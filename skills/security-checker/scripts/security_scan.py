#!/usr/bin/env python3
"""
Security scanner for Python scripts before publishing
Checks for:
- Dangerous imports (os.system, subprocess, etc.)
- Hardcoded secrets/tokens
- File operations outside workspace
- Network calls
"""

import re
import sys
from pathlib import Path

# Patterns that might indicate security issues
DANGEROUS_IMPORTS = [
    r'import\s+os\b',
    r'from\s+os\s+import',
    r'import\s+subprocess\b',
    r'from\s+subprocess\s+import',
    r'import\s+shutil\b',
    r'from\s+shutil\s+import',
    r'import\s+socket\b',
    r'from\s+socket\s+import',
    r'import\s+urllib\b',
    r'from\s+urllib\s+import',
    r'import\s+requests\b',
]

DANGEROUS_FUNCTIONS = [
    r'\bos\.system\s*\(',
    r'\bsubprocess\.call\s*\(',
    r'\bsubprocess\.run\s*\(',
    r'\bsubprocess\.Popen\s*\(',
    r'\beval\s*\(',
    r'\bexec\s*\(',
]

SECRET_PATTERNS = [
    r'api[_-]?key\s*=\s*["\']([^"\']{20,})["\']',
    r'token\s*=\s*["\']([^"\']{20,})["\']',
    r'password\s*=\s*["\']([^"\']{8,})["\']',
    r'secret\s*=\s*["\']([^"\']{8,})["\']',
    r'private[_-]?key\s*=\s*["\']([^"\']{20,})["\']',
    r'clh_[A-Za-z0-9_]{30,}',  # ClawHub tokens
    r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',  # JWT-like tokens
]

FILE_PATTERNS = [
    r'\bopen\s*\([^)]*["\']\s*[/\\]',  # Absolute paths
    r'\bPath\s*\([^)]*\.\.',  # Parent directory traversal
    r'\.write_text\s*\(',  # File write operations
    r'\.write_bytes\s*\(',  # Binary file write
    r'\bopen\s*\([^)]*["\'].*["\'].*\b["\']w',  # Open for writing
]

def scan_file(filepath):
    """Scan a single Python file for security issues."""
    issues = []
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [f"ERROR: Could not read file: {e}"]
    
    # Check dangerous imports
    for pattern in DANGEROUS_IMPORTS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"⚠️  Line {line_num}: Dangerous import: {match.group()}")
    
    # Check dangerous functions
    for pattern in DANGEROUS_FUNCTIONS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"⚠️  Line {line_num}: Dangerous function: {match.group()}")
    
    # Check for hardcoded secrets
    for pattern in SECRET_PATTERNS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            # Don't show the actual secret
            issues.append(f"🔴 Line {line_num}: Possible hardcoded secret detected")
    
    # Check file operations
    for pattern in FILE_PATTERNS:
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues.append(f"⚠️  Line {line_num}: Potentially unsafe file operation: {match.group()}")
    
    return issues

def scan_directory(directory):
    """Scan all Python files in a directory."""
    issues = []
    directory = Path(directory)
    
    for py_file in directory.rglob('*.py'):
        print(f"\n🔍 Scanning: {py_file.relative_to(directory)}")
        file_issues = scan_file(py_file)
        
        if file_issues:
            issues.append((str(py_file.relative_to(directory)), file_issues))
            for issue in file_issues:
                print(f"  {issue}")
        else:
            print("  ✅ No issues found")
    
    return issues

def main():
    if len(sys.argv) < 2:
        print("Security Scanner - Scan Python code before publishing")
        print("\nUsage: security_scan.py <file_or_directory>")
        print("\nChecks for:")
        print("  • Dangerous imports (os, subprocess, etc.)")
        print("  • Dangerous functions (eval, exec, system)")
        print("  • Hardcoded secrets/tokens")
        print("  • Unsafe file operations")
        return
    
    target = Path(sys.argv[1])
    
    print(f"\n🔒 Security Scan: {target}")
    print("=" * 60)
    
    if target.is_file():
        issues = scan_file(target)
        if issues:
            print(f"\n⚠️  Found {len(issues)} issue(s):\n")
            for issue in issues:
                print(issue)
        else:
            print("\n✅ No security issues found")
    elif target.is_dir():
        all_issues = scan_directory(target)
        total_issues = sum(len(file_issues) for _, file_issues in all_issues)
        
        print("\n" + "=" * 60)
        if total_issues > 0:
            print(f"\n⚠️  Found {total_issues} total issue(s) across {len(all_issues)} file(s)")
        else:
            print("\n✅ All clear - No security issues found")
    else:
        print(f"Error: {target} is not a valid file or directory")

if __name__ == "__main__":
    main()
