/**
 * Python AST Dataflow Analyzer - Advanced source-to-sink analysis
 * Uses Python tree-sitter via subprocess (no Node.js native deps required)
 */

const path = require('path');
const { execSync, spawnSync } = require('child_process');
const fs = require('fs');

// Check if Python analyzer is available
let isAvailable = false;
const ANALYZER_SCRIPT = path.join(__dirname, '..', 'ast-analyzer.py');

try {
  // Check if Python and tree-sitter are available
  if (fs.existsSync(ANALYZER_SCRIPT)) {
    const result = spawnSync('python', ['-c', 'import tree_sitter; import tree_sitter_python'], {
      timeout: 5000,
      encoding: 'utf-8'
    });
    isAvailable = result.status === 0;
  }
} catch (e) {
  isAvailable = false;
}

// ─── Source patterns - where sensitive data comes from ─────────────

const DATA_SOURCES = [
  {
    id: 'env-source',
    pattern: /(?:os\.environ|process\.env|getenv|env\.get)\s*[\[\(]/g,
    description: 'Environment variable access',
    severity: 'high',
    dataType: 'environment'
  },
  {
    id: 'file-source',
    pattern: /(?:open|readFile|readFileSync|fs\.read)\s*\(\s*['"][^'"]*\.env['"]|open\s*\(\s*['"][^'"]*(?:config|secret|key|credential)['"]|readFile.*(?:\.env|config|secret|key|credential)/gi,
    description: 'Sensitive file read',
    severity: 'critical',
    dataType: 'file'
  },
  {
    id: 'stdin-source',
    pattern: /(?:input\s*\(|sys\.stdin|process\.stdin|readline|gets\s*\()/g,
    description: 'User input source',
    severity: 'medium',
    dataType: 'input'
  },
  {
    id: 'memory-source',
    pattern: /(?:MEMORY\.md|TOOLS\.md|SOUL\.md|AGENTS\.md|memory\/)/gi,
    description: 'OpenClaw memory file access',
    severity: 'critical',
    dataType: 'memory'
  }
];

// ─── Sink patterns - where data can leak out ──────────────────────

const DATA_SINKS = [
  {
    id: 'http-sink',
    pattern: /(?:requests\.(?:post|put|patch)|fetch\s*\(|axios\.(?:post|put|patch)|urllib\.request)/g,
    description: 'HTTP request with data',
    severity: 'critical',
    riskType: 'exfiltration'
  },
  {
    id: 'file-sink',
    pattern: /(?:writeFile|appendFile|open\s*\([^)]*['"]w|fs\.write|write\s*\()/g,
    description: 'File write operation',
    severity: 'medium',
    riskType: 'persistence'
  },
  {
    id: 'shell-sink',
    pattern: /(?:os\.system|subprocess|exec|spawn|child_process)/g,
    description: 'Shell command execution',
    severity: 'high',
    riskType: 'execution'
  },
  {
    id: 'network-sink',
    pattern: /(?:socket\.send|udp\.send|smtp\.send|websocket\.send)/g,
    description: 'Network transmission',
    severity: 'high',
    riskType: 'exfiltration'
  }
];

// ─── Tree-sitter AST analysis ──────────────────────────────────────

class DataFlowAnalyzer {
  constructor() {
    if (!isAvailable) {
      throw new Error('tree-sitter dependencies not available');
    }
    this.parser = new Parser();
    this.parser.setLanguage(Python);
  }

  parseFile(filePath) {
    const fs = require('fs');
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      return this.parser.parse(content);
    } catch (e) {
      return null;
    }
  }

  findDataFlows(tree, filePath) {
    const findings = [];
    if (!tree) return findings;

    const sources = this.findDataSources(tree);
    const sinks = this.findDataSinks(tree);
    const flows = this.traceDataFlow(tree, sources, sinks);

    // Convert flows to findings
    for (const flow of flows) {
      findings.push({
        id: 'dataflow-' + flow.source.type + '-to-' + flow.sink.type,
        category: 'Data Flow',
        severity: this.calculateFlowSeverity(flow),
        file: path.basename(filePath),
        line: flow.sink.line,
        snippet: flow.sink.text.substring(0, 200),
        explanation: `Data flows from ${flow.source.description} (line ${flow.source.line}) to ${flow.sink.description} (line ${flow.sink.line})`,
        analyzer: 'ast-python',
        dataflow: {
          source: flow.source,
          sink: flow.sink,
          variables: flow.variables
        }
      });
    }

    return findings;
  }

  findDataSources(tree) {
    const sources = [];
    this.walkTree(tree.rootNode, (node) => {
      // Look for variable assignments from sensitive sources
      if (node.type === 'assignment') {
        const text = node.text;
        for (const source of DATA_SOURCES) {
          if (source.pattern.test(text)) {
            const variable = this.extractAssignedVariable(node);
            sources.push({
              type: source.id,
              description: source.description,
              severity: source.severity,
              dataType: source.dataType,
              line: node.startPosition.row + 1,
              text: text,
              variable: variable,
              node: node
            });
          }
        }
      }
    });
    return sources;
  }

  findDataSinks(tree) {
    const sinks = [];
    this.walkTree(tree.rootNode, (node) => {
      // Look for function calls that could leak data
      if (node.type === 'call') {
        const text = node.text;
        for (const sink of DATA_SINKS) {
          if (sink.pattern.test(text)) {
            const variables = this.extractCallArguments(node);
            sinks.push({
              type: sink.id,
              description: sink.description,
              severity: sink.severity,
              riskType: sink.riskType,
              line: node.startPosition.row + 1,
              text: text,
              variables: variables,
              node: node
            });
          }
        }
      }
    });
    return sinks;
  }

  traceDataFlow(tree, sources, sinks) {
    const flows = [];
    
    // Simple variable name matching for MVP
    // TODO: More sophisticated dataflow analysis with SSA/control flow
    for (const source of sources) {
      for (const sink of sinks) {
        if (source.variable && sink.variables.includes(source.variable)) {
          flows.push({
            source: source,
            sink: sink,
            variables: [source.variable]
          });
        }
      }
    }

    return flows;
  }

  calculateFlowSeverity(flow) {
    // Critical if environment/memory data goes to network
    if ((flow.source.dataType === 'environment' || flow.source.dataType === 'memory') && 
        flow.sink.riskType === 'exfiltration') {
      return 'critical';
    }
    
    // High if any sensitive source goes to network
    if (flow.sink.riskType === 'exfiltration') {
      return 'high';
    }
    
    // Medium for other combinations
    return 'medium';
  }

  extractAssignedVariable(assignmentNode) {
    // Extract the variable name being assigned to
    const left = assignmentNode.children.find(c => c.type === 'identifier');
    return left ? left.text : null;
  }

  extractCallArguments(callNode) {
    // Extract variable names passed as arguments
    const variables = [];
    this.walkTree(callNode, (node) => {
      if (node.type === 'identifier') {
        variables.push(node.text);
      }
    });
    return variables;
  }

  walkTree(node, callback) {
    callback(node);
    for (const child of node.children) {
      this.walkTree(child, callback);
    }
  }
}

// ─── Main scanner function ─────────────────────────────────────────

function scanFile(filePath, skillDir, options = {}) {
  if (!isAvailable) {
    // Return graceful notice instead of error
    return [{
      id: 'ast-unavailable',
      category: 'Info',
      severity: 'info',
      file: path.relative(skillDir, filePath),
      line: 0,
      snippet: '',
      explanation: 'Python AST analysis not available — install: pip install tree-sitter tree-sitter-python',
      analyzer: 'ast-python'
    }];
  }

  // Only analyze Python files
  const ext = path.extname(filePath).toLowerCase();
  if (!['.py', '.pyw'].includes(ext)) {
    return [];
  }

  try {
    // Call Python AST analyzer script
    const result = spawnSync('python', [ANALYZER_SCRIPT, filePath, '--json'], {
      timeout: 30000,
      encoding: 'utf-8',
      maxBuffer: 10 * 1024 * 1024
    });

    if (result.status !== 0) {
      return [{
        id: 'ast-error',
        category: 'Error',
        severity: 'medium',
        file: path.relative(skillDir, filePath),
        line: 0,
        snippet: '',
        explanation: `Python AST analysis failed: ${result.stderr || 'Unknown error'}`,
        analyzer: 'ast-python'
      }];
    }

    const output = JSON.parse(result.stdout);
    
    // Convert findings to use relative paths
    const findings = (output.findings || []).map(f => ({
      ...f,
      file: path.relative(skillDir, f.file || filePath)
    }));

    return findings;
  } catch (e) {
    return [{
      id: 'ast-error',
      category: 'Error',
      severity: 'medium',
      file: path.relative(skillDir, filePath),
      line: 0,
      snippet: '',
      explanation: `Python AST analysis failed: ${e.message}`,
      analyzer: 'ast-python'
    }];
  }
}

// ─── Capability detection ──────────────────────────────────────────

function checkCapability() {
  return {
    available: isAvailable,
    dependencies: ['python', 'tree-sitter', 'tree-sitter-python'],
    installCommand: 'pip install tree-sitter tree-sitter-python',
    description: 'Python dataflow analysis using tree-sitter AST parsing (via Python subprocess)'
  };
}

module.exports = {
  scanFile,
  checkCapability,
  isAvailable
};