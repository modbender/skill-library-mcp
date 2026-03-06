#!/usr/bin/env python3
"""
Python AST Dataflow Analyzer for Skill Auditor
Analyzes Python files for data flow from sensitive sources to dangerous sinks.
Called by the Node.js scan-skill.js when --use-ast flag is passed.

Usage: python ast-analyzer.py <file.py> [--json]
"""

import sys
import json
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

# Initialize parser
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

# Sensitive sources (where dangerous data might come from)
SENSITIVE_SOURCES = {
    'os.environ': 'Environment variable access',
    'os.environ.get': 'Environment variable access',
    'os.getenv': 'Environment variable access',
    'dotenv': 'Dotenv file access',
    'load_dotenv': 'Dotenv file access',
    'open': 'File read (check for .env, credentials)',
    'pathlib.Path': 'File path access',
    'subprocess': 'Subprocess (command injection risk)',
    'eval': 'Dynamic code evaluation',
    'exec': 'Dynamic code execution',
    '__import__': 'Dynamic import',
}

# Dangerous sinks (where data should not flow to)
DANGEROUS_SINKS = {
    'requests.get': 'HTTP request (potential exfiltration)',
    'requests.post': 'HTTP request (potential exfiltration)',
    'requests.put': 'HTTP request (potential exfiltration)',
    'urllib.request': 'HTTP request (potential exfiltration)',
    'httpx': 'HTTP request (potential exfiltration)',
    'aiohttp': 'HTTP request (potential exfiltration)',
    'curl': 'Shell HTTP request',
    'wget': 'Shell HTTP request',
    'subprocess.run': 'Shell command execution',
    'subprocess.call': 'Shell command execution',
    'subprocess.Popen': 'Shell command execution',
    'os.system': 'Shell command execution',
    'os.popen': 'Shell command execution',
    'socket.send': 'Network socket (potential exfiltration)',
    'smtplib': 'Email send (potential exfiltration)',
}

def get_node_text(node, source_bytes):
    """Extract text from a node."""
    return source_bytes[node.start_byte:node.end_byte].decode('utf-8', errors='replace')

def find_imports(tree, source_bytes):
    """Find all imports in the file."""
    imports = {}
    
    def visit(node):
        if node.type == 'import_statement':
            for child in node.children:
                if child.type == 'dotted_name':
                    name = get_node_text(child, source_bytes)
                    imports[name.split('.')[0]] = name
        elif node.type == 'import_from_statement':
            module = None
            for child in node.children:
                if child.type == 'dotted_name':
                    module = get_node_text(child, source_bytes)
                    break
            if module:
                for child in node.children:
                    if child.type == 'import_list' or child.type == 'aliased_import':
                        for c in child.children if child.type == 'import_list' else [child]:
                            if c.type == 'aliased_import' or c.type == 'identifier':
                                name = get_node_text(c.children[0] if c.type == 'aliased_import' else c, source_bytes)
                                imports[name] = f"{module}.{name}"
        
        for child in node.children:
            visit(child)
    
    visit(tree.root_node)
    return imports

def find_sources_and_sinks(tree, source_bytes, imports):
    """Find sensitive sources and dangerous sinks."""
    findings = []
    sources = []  # Track variables assigned from sensitive sources
    
    def get_call_name(node):
        """Get the full name of a function call."""
        if node.type == 'call':
            func = node.child_by_field_name('function')
            if func:
                if func.type == 'attribute':
                    obj = func.child_by_field_name('object')
                    attr = func.child_by_field_name('attribute')
                    if obj and attr:
                        obj_text = get_node_text(obj, source_bytes)
                        attr_text = get_node_text(attr, source_bytes)
                        return f"{obj_text}.{attr_text}"
                elif func.type == 'identifier':
                    return get_node_text(func, source_bytes)
        return None
    
    def visit(node, depth=0):
        # Check for function calls
        if node.type == 'call':
            call_name = get_call_name(node)
            if call_name:
                # Check if it's a sensitive source
                for source_pattern, desc in SENSITIVE_SOURCES.items():
                    if source_pattern in call_name or call_name in source_pattern:
                        finding = {
                            'type': 'source',
                            'pattern': call_name,
                            'description': desc,
                            'line': node.start_point[0] + 1,
                            'column': node.start_point[1],
                            'snippet': get_node_text(node, source_bytes)[:100]
                        }
                        findings.append(finding)
                        sources.append((call_name, node.start_point[0] + 1))
                
                # Check if it's a dangerous sink
                for sink_pattern, desc in DANGEROUS_SINKS.items():
                    if sink_pattern in call_name or call_name in sink_pattern:
                        finding = {
                            'type': 'sink',
                            'pattern': call_name,
                            'description': desc,
                            'line': node.start_point[0] + 1,
                            'column': node.start_point[1],
                            'snippet': get_node_text(node, source_bytes)[:100]
                        }
                        findings.append(finding)
        
        # Check for string patterns that might indicate exfiltration
        if node.type == 'string':
            text = get_node_text(node, source_bytes)
            if any(pattern in text.lower() for pattern in ['webhook.site', 'requestbin', 'ngrok', 'burpcollaborator']):
                findings.append({
                    'type': 'exfil_url',
                    'pattern': 'Known exfiltration endpoint',
                    'description': 'URL to known data capture service',
                    'line': node.start_point[0] + 1,
                    'column': node.start_point[1],
                    'snippet': text[:100],
                    'severity': 'critical'
                })
        
        for child in node.children:
            visit(child, depth + 1)
    
    visit(tree.root_node)
    return findings, sources

def analyze_dataflow(findings, sources):
    """Analyze if data flows from sources to sinks."""
    dataflow_issues = []
    
    source_lines = [s[1] for s in sources]
    sink_findings = [f for f in findings if f['type'] == 'sink']
    
    # Simple heuristic: if a sink appears after a source in the same file, flag it
    for sink in sink_findings:
        for source_line in source_lines:
            if sink['line'] > source_line:
                dataflow_issues.append({
                    'type': 'dataflow',
                    'severity': 'high',
                    'description': f"Potential data flow from sensitive source (line {source_line}) to {sink['pattern']}",
                    'line': sink['line'],
                    'sink': sink['pattern'],
                    'source_line': source_line
                })
                break  # One match is enough
    
    return dataflow_issues

def analyze_file(filepath):
    """Analyze a Python file for security issues."""
    try:
        with open(filepath, 'rb') as f:
            source_bytes = f.read()
    except Exception as e:
        return {'error': str(e), 'file': filepath}
    
    tree = parser.parse(source_bytes)
    imports = find_imports(tree, source_bytes)
    findings, sources = find_sources_and_sinks(tree, source_bytes, imports)
    dataflow_issues = analyze_dataflow(findings, sources)
    
    # Combine all findings
    all_findings = []
    
    # Add source/sink findings
    for f in findings:
        severity = f.get('severity', 'medium')
        if f['type'] == 'source':
            severity = 'medium'
        elif f['type'] == 'sink':
            severity = 'high'
        
        all_findings.append({
            'id': f'ast-{f["type"]}-{f["pattern"].replace(".", "-")}',
            'category': 'AST Analysis',
            'severity': severity,
            'file': filepath,
            'line': f['line'],
            'snippet': f['snippet'],
            'explanation': f'{f["description"]} — {f["pattern"]}',
            'analyzer': 'ast-python'
        })
    
    # Add dataflow findings
    for df in dataflow_issues:
        all_findings.append({
            'id': 'ast-dataflow',
            'category': 'Dataflow Analysis',
            'severity': 'critical',
            'file': filepath,
            'line': df['line'],
            'snippet': f"Data may flow from line {df['source_line']} to {df['sink']}",
            'explanation': df['description'],
            'analyzer': 'ast-python'
        })
    
    return {
        'file': filepath,
        'findings': all_findings,
        'imports': imports,
        'source_count': len(sources),
        'sink_count': len([f for f in findings if f['type'] == 'sink'])
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python ast-analyzer.py <file.py> [--json]", file=sys.stderr)
        sys.exit(2)
    
    filepath = sys.argv[1]
    json_output = '--json' in sys.argv
    
    result = analyze_file(filepath)
    
    if json_output:
        print(json.dumps(result, indent=2))
    else:
        if 'error' in result:
            print(f"Error: {result['error']}")
            sys.exit(1)
        
        print(f"File: {result['file']}")
        print(f"Sources found: {result['source_count']}")
        print(f"Sinks found: {result['sink_count']}")
        print(f"Findings: {len(result['findings'])}")
        print()
        
        for f in result['findings']:
            print(f"[{f['severity'].upper()}] Line {f['line']}: {f['explanation']}")
            print(f"  Snippet: {f['snippet']}")
            print()

if __name__ == '__main__':
    main()
