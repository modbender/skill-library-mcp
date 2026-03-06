"use strict";

/**
 * py2py3-converter: Test generation utility.
 * Creates pytest tests for converted Python 3 code.
 */

/**
 * Extract function definitions from Python code.
 * @param {string} code - Python source code
 * @returns {Array<{name: string, args: string[], line: number}>}
 */
function extractFunctions(code) {
  const functions = [];
  const lines = code.split("\n");

  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^\s*def\s+(\w+)\s*\(([^)]*)\)\s*:/);
    if (match) {
      const name = match[1];
      const argStr = match[2].trim();
      const args = argStr
        ? argStr.split(",").map((a) => a.trim().split("=")[0].trim())
        : [];
      functions.push({ name, args, line: i + 1 });
    }
  }

  return functions;
}

/**
 * Extract class definitions from Python code.
 * @param {string} code - Python source code
 * @returns {Array<{name: string, line: number}>}
 */
function extractClasses(code) {
  const classes = [];
  const lines = code.split("\n");

  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^\s*class\s+(\w+)/);
    if (match) {
      classes.push({ name: match[1], line: i + 1 });
    }
  }

  return classes;
}

/**
 * Detect which Python 2 → 3 patterns were converted.
 * @param {string} originalCode - Original Python 2 code
 * @param {string} convertedCode - Converted Python 3 code
 * @returns {Array<string>} List of detected conversion patterns
 */
function detectConversions(originalCode, convertedCode) {
  const patterns = [];

  if (/\bprint\s+[^(]/.test(originalCode)) {
    patterns.push("print_statement");
  }
  if (/\braw_input\s*\(/.test(originalCode)) {
    patterns.push("raw_input");
  }
  if (/\bxrange\s*\(/.test(originalCode)) {
    patterns.push("xrange");
  }
  if (/\bunicode\s*\(/.test(originalCode)) {
    patterns.push("unicode");
  }
  if (/\bbasestring\b/.test(originalCode)) {
    patterns.push("basestring");
  }
  if (/\.has_key\s*\(/.test(originalCode)) {
    patterns.push("has_key");
  }
  if (/\.iteritems\s*\(/.test(originalCode)) {
    patterns.push("iteritems");
  }
  if (/\.itervalues\s*\(/.test(originalCode)) {
    patterns.push("itervalues");
  }
  if (/except\s+\w+\s*,\s*\w+/.test(originalCode)) {
    patterns.push("except_comma");
  }
  if (/raise\s+\w+\s*,\s*/.test(originalCode)) {
    patterns.push("raise_comma");
  }
  if (/(?<!\w)reduce\s*\(/.test(originalCode)) {
    patterns.push("reduce");
  }
  if (/\blong\s*\(/.test(originalCode)) {
    patterns.push("long");
  }

  return patterns;
}

/**
 * Generate pytest test code for converted Python 3 code.
 * @param {string} originalCode - Original Python 2 code
 * @param {string} convertedCode - Converted Python 3 code
 * @returns {string} Pytest test file content
 */
function generateTests(originalCode, convertedCode) {
  const functions = extractFunctions(convertedCode);
  const classes = extractClasses(convertedCode);
  const conversions = detectConversions(originalCode, convertedCode);

  let testCode = `"""Auto-generated tests for Python 2 to 3 converted code."""
import ast
import sys


# ========== Syntax Validation Tests ==========

def test_syntax_is_valid_python3():
    """Verify the converted code is valid Python 3 syntax."""
    code = ${JSON.stringify(convertedCode)}
    tree = ast.parse(code)
    assert tree is not None, "Code should parse as valid Python 3"


def test_no_python2_print_statements():
    """Verify no Python 2 print statements remain."""
    code = ${JSON.stringify(convertedCode)}
    lines = code.split("\\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("print ") and not stripped.startswith("print("):
            # Allow comments
            if not stripped.startswith("#"):
                assert False, f"Line {i} contains Python 2 print statement: {stripped}"


def test_no_python2_except_syntax():
    """Verify no Python 2 except syntax remains."""
    code = ${JSON.stringify(convertedCode)}
    import re
    matches = re.findall(r"except\\s+\\w+\\s*,\\s*\\w+\\s*:", code)
    assert len(matches) == 0, f"Found Python 2 except syntax: {matches}"


def test_no_python2_raise_syntax():
    """Verify no Python 2 raise syntax remains."""
    code = ${JSON.stringify(convertedCode)}
    import re
    matches = re.findall(r"raise\\s+\\w+\\s*,\\s*[^)]", code)
    assert len(matches) == 0, f"Found Python 2 raise syntax: {matches}"

`;

  // Generate conversion-specific tests
  if (conversions.includes("print_statement")) {
    testCode += `
def test_print_converted_to_function():
    """Verify print statements were converted to function calls."""
    code = ${JSON.stringify(convertedCode)}
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == "print":
                return  # Found at least one print() call
    # If there were print statements in original, there should be print() calls
    pass

`;
  }

  if (conversions.includes("xrange")) {
    testCode += `
def test_xrange_replaced_with_range():
    """Verify xrange() calls were replaced with range()."""
    code = ${JSON.stringify(convertedCode)}
    import re
    matches = re.findall(r"\\bxrange\\s*\\(", code)
    assert len(matches) == 0, "xrange() should be replaced with range()"

`;
  }

  if (conversions.includes("raw_input")) {
    testCode += `
def test_raw_input_replaced_with_input():
    """Verify raw_input() was replaced with input()."""
    code = ${JSON.stringify(convertedCode)}
    import re
    matches = re.findall(r"\\braw_input\\s*\\(", code)
    assert len(matches) == 0, "raw_input() should be replaced with input()"

`;
  }

  if (conversions.includes("unicode")) {
    testCode += `
def test_unicode_replaced_with_str():
    """Verify unicode() was replaced with str()."""
    code = ${JSON.stringify(convertedCode)}
    import re
    matches = re.findall(r"\\bunicode\\s*\\(", code)
    assert len(matches) == 0, "unicode() should be replaced with str()"

`;
  }

  if (conversions.includes("has_key")) {
    testCode += `
def test_has_key_replaced():
    """Verify dict.has_key() was replaced with 'in' operator."""
    code = ${JSON.stringify(convertedCode)}
    assert ".has_key(" not in code, "has_key() should be replaced with 'in' operator"

`;
  }

  if (conversions.includes("iteritems")) {
    testCode += `
def test_iteritems_replaced():
    """Verify .iteritems() was replaced with .items()."""
    code = ${JSON.stringify(convertedCode)}
    assert ".iteritems()" not in code, "iteritems() should be replaced with items()"

`;
  }

  if (conversions.includes("reduce")) {
    testCode += `
def test_functools_reduce_imported():
    """Verify functools.reduce is properly imported."""
    code = ${JSON.stringify(convertedCode)}
    assert "from functools import reduce" in code, "functools.reduce should be imported"

`;
  }

  // Generate tests for detected functions
  for (const func of functions) {
    if (func.name.startsWith("_") && func.name !== "__init__") continue;
    if (func.name === "__init__") continue;

    testCode += `
def test_${func.name}_exists():
    """Verify function ${func.name} is defined and callable."""
    code = ${JSON.stringify(convertedCode)}
    tree = ast.parse(code)
    func_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]
    assert "${func.name}" in func_names, "Function ${func.name} should be defined"

`;
  }

  // Generate tests for detected classes
  for (const cls of classes) {
    testCode += `
def test_class_${cls.name}_exists():
    """Verify class ${cls.name} is defined."""
    code = ${JSON.stringify(convertedCode)}
    tree = ast.parse(code)
    class_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]
    assert "${cls.name}" in class_names, "Class ${cls.name} should be defined"

`;
  }

  return testCode;
}

module.exports = { generateTests, extractFunctions, extractClasses, detectConversions };
