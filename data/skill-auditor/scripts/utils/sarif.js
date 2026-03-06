/**
 * SARIF Output Generator - GitHub Code Scanning compatible format
 * Converts skill-auditor findings to SARIF 2.1.0 format
 */

// ─── SARIF Schema constants ────────────────────────────────────────

const SARIF_VERSION = '2.1.0';
const SCHEMA_URI = 'https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json';

// Map our severity levels to SARIF levels
const SEVERITY_MAP = {
  'critical': 'error',
  'high': 'error', 
  'medium': 'warning',
  'low': 'note',
  'info': 'note'
};

// Map categories to SARIF security severity levels
const SECURITY_SEVERITY_MAP = {
  'critical': 9.0,
  'high': 7.0,
  'medium': 5.0,
  'low': 3.0,
  'info': 1.0
};

// ─── SARIF Generator ───────────────────────────────────────────────

class SarifGenerator {
  constructor(toolName = 'skill-auditor', toolVersion = '2.0.0') {
    this.toolName = toolName;
    this.toolVersion = toolVersion;
  }

  generateSarif(report) {
    const sarif = {
      $schema: SCHEMA_URI,
      version: SARIF_VERSION,
      runs: [
        {
          tool: this.generateToolInfo(),
          results: this.convertFindings(report.findings),
          artifacts: this.generateArtifacts(report),
          invocations: [this.generateInvocation(report)]
        }
      ]
    };

    return sarif;
  }

  generateToolInfo() {
    return {
      driver: {
        name: this.toolName,
        version: this.toolVersion,
        informationUri: 'https://github.com/RubenAQuispe/clawd/tree/main/skills/skill-auditor',
        shortDescription: {
          text: 'Security scanner for OpenClaw skills'
        },
        fullDescription: {
          text: 'Static analysis security scanner that audits skills for vulnerabilities, prompt injection, data exfiltration, obfuscation, and other threats with context-aware intent matching.'
        },
        semanticVersion: this.toolVersion,
        rules: this.generateRules()
      }
    };
  }

  generateRules() {
    // Generate SARIF rule definitions from our patterns and analyzers
    const rules = [];
    
    // Common rule categories
    const ruleCategories = {
      'path-traversal': {
        id: 'path-traversal',
        shortDescription: { text: 'Path traversal vulnerability' },
        fullDescription: { text: 'Code attempts to access files outside the skill directory using path traversal sequences' },
        defaultConfiguration: { level: 'error' },
        properties: { 
          category: 'security',
          tags: ['security', 'file-access', 'path-traversal']
        }
      },
      'prompt-injection': {
        id: 'prompt-injection',
        shortDescription: { text: 'Prompt injection attempt' },
        fullDescription: { text: 'Code contains patterns that attempt to manipulate AI agent instructions or behavior' },
        defaultConfiguration: { level: 'error' },
        properties: {
          category: 'security', 
          tags: ['security', 'prompt-injection', 'ai-safety']
        }
      },
      'data-exfiltration': {
        id: 'data-exfiltration',
        shortDescription: { text: 'Potential data exfiltration' },
        fullDescription: { text: 'Code patterns suggest potential unauthorized data transmission or collection' },
        defaultConfiguration: { level: 'error' },
        properties: {
          category: 'security',
          tags: ['security', 'exfiltration', 'privacy']
        }
      },
      'shell-execution': {
        id: 'shell-execution', 
        shortDescription: { text: 'Shell command execution' },
        fullDescription: { text: 'Code executes system shell commands which could be used maliciously' },
        defaultConfiguration: { level: 'warning' },
        properties: {
          category: 'security',
          tags: ['security', 'execution', 'shell']
        }
      },
      'sensitive-file-access': {
        id: 'sensitive-file-access',
        shortDescription: { text: 'Sensitive file access' },
        fullDescription: { text: 'Code accesses sensitive system or configuration files' },
        defaultConfiguration: { level: 'error' },
        properties: {
          category: 'security',
          tags: ['security', 'file-access', 'sensitive']
        }
      }
    };

    // Add rules based on categories we use
    Object.values(ruleCategories).forEach(rule => rules.push(rule));

    return rules;
  }

  convertFindings(findings) {
    return findings.map((finding, index) => this.convertFinding(finding, index));
  }

  convertFinding(finding, index) {
    const severity = finding.severity || 'medium';
    const sarifLevel = SEVERITY_MAP[severity];
    const securitySeverity = SECURITY_SEVERITY_MAP[severity];

    const result = {
      ruleId: this.mapFindingToRuleId(finding),
      ruleIndex: 0, // Simplified for MVP
      level: sarifLevel,
      message: {
        text: finding.explanation || finding.description
      },
      locations: [
        {
          physicalLocation: {
            artifactLocation: {
              uri: finding.file,
              uriBaseId: 'SRCROOT'
            },
            region: {
              startLine: finding.line || 1,
              startColumn: 1,
              snippet: {
                text: finding.snippet || ''
              }
            }
          }
        }
      ],
      properties: {
        category: finding.category,
        severity: severity,
        analyzer: finding.analyzer || 'static',
        securitySeverity: securitySeverity
      }
    };

    // Add additional properties based on finding type
    if (finding.match) {
      result.properties.match = finding.match;
    }

    if (finding.intentMatch !== undefined) {
      result.properties.intentMatch = finding.intentMatch;
      result.properties.originalSeverity = finding.originalSeverity;
    }

    if (finding.llmAnalysis) {
      result.properties.llmAnalysis = finding.llmAnalysis;
    }

    if (finding.virustotal) {
      result.properties.virustotal = {
        hash: finding.virustotal.hash,
        status: finding.virustotal.status,
        engines: finding.virustotal.engines,
        positives: finding.virustotal.positives,
        permalink: finding.virustotal.permalink
      };
    }

    if (finding.dataflow) {
      result.properties.dataflow = finding.dataflow;
      result.codeFlows = [this.generateCodeFlow(finding.dataflow)];
    }

    return result;
  }

  mapFindingToRuleId(finding) {
    // Map finding categories to SARIF rule IDs
    const categoryMap = {
      'Path Traversal': 'path-traversal',
      'Prompt Injection': 'prompt-injection', 
      'Data Exfiltration': 'data-exfiltration',
      'Shell Execution': 'shell-execution',
      'Sensitive File Access': 'sensitive-file-access',
      'File Access': 'sensitive-file-access',
      'Network': 'network-access',
      'Obfuscation': 'obfuscation',
      'Persistence': 'persistence',
      'Privilege Escalation': 'privilege-escalation'
    };

    return categoryMap[finding.category] || 'unknown-pattern';
  }

  generateCodeFlow(dataflow) {
    if (!dataflow.source || !dataflow.sink) return null;

    return {
      threadFlows: [
        {
          locations: [
            {
              location: {
                physicalLocation: {
                  region: { startLine: dataflow.source.line }
                },
                message: { text: `Data source: ${dataflow.source.description}` }
              }
            },
            {
              location: {
                physicalLocation: {
                  region: { startLine: dataflow.sink.line }
                },
                message: { text: `Data sink: ${dataflow.sink.description}` }
              }
            }
          ]
        }
      ]
    };
  }

  generateArtifacts(report) {
    const artifacts = [];
    const fileSet = new Set();

    // Collect unique files from findings
    for (const finding of report.findings) {
      if (finding.file && !fileSet.has(finding.file)) {
        fileSet.add(finding.file);
        artifacts.push({
          location: {
            uri: finding.file,
            uriBaseId: 'SRCROOT'
          },
          length: -1, // Unknown
          roles: ['analysisTarget']
        });
      }
    }

    return artifacts;
  }

  generateInvocation(report) {
    return {
      executionSuccessful: true,
      startTimeUtc: report.scan.timestamp,
      endTimeUtc: report.scan.timestamp, // Simplified
      machine: require('os').hostname(),
      workingDirectory: {
        uri: report.skill.directory,
        uriBaseId: 'SRCROOT'
      }
    };
  }
}

// ─── Main export functions ─────────────────────────────────────────

function generateSarif(report, options = {}) {
  const generator = new SarifGenerator(
    options.toolName || 'skill-auditor',
    options.toolVersion || '2.0.0'
  );
  
  return generator.generateSarif(report);
}

function formatSarif(sarifData) {
  return JSON.stringify(sarifData, null, 2);
}

// Calculate exit code for CI/CD integration
function calculateExitCode(report, options = {}) {
  if (!options.failOnFindings) return 0;
  
  // Count non-info findings
  const significantFindings = report.findings.filter(f => 
    f.severity && !['info', 'low'].includes(f.severity)
  );
  
  return significantFindings.length > 0 ? 1 : 0;
}

module.exports = {
  generateSarif,
  formatSarif,
  calculateExitCode,
  SarifGenerator
};