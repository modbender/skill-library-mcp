"use strict";

const { convert, generateReport } = require("../scripts/converter");
const { generateTests, extractFunctions, extractClasses, detectConversions } = require("../scripts/test-generator");

let passed = 0;
let failed = 0;
const failures = [];

function assert(condition, message) {
  if (!condition) {
    failed++;
    failures.push(message);
    console.log(`  FAIL: ${message}`);
  } else {
    passed++;
    console.log(`  PASS: ${message}`);
  }
}

function assertIncludes(haystack, needle, message) {
  assert(haystack.includes(needle), message + ` (expected to find "${needle}")`);
}

function assertNotIncludes(haystack, needle, message) {
  assert(!haystack.includes(needle), message + ` (expected NOT to find "${needle}")`);
}

function assertEqual(actual, expected, message) {
  assert(actual === expected, message + ` (expected: ${JSON.stringify(expected)}, got: ${JSON.stringify(actual)})`);
}

// ========== Print Statement Tests ==========
console.log("\n--- Print Statement Conversion ---");

(function testSimplePrint() {
  const result = convert('print "hello"');
  assertIncludes(result.convertedCode, 'print("hello")', "Simple print converts to function call");
})();

(function testMultiValuePrint() {
  const result = convert('print "a", "b", "c"');
  assertIncludes(result.convertedCode, 'print("a", "b", "c")', "Multi-value print converts correctly");
})();

(function testPrintStderr() {
  const result = convert('print >> sys.stderr, "error"');
  assertIncludes(result.convertedCode, 'print("error", file=sys.stderr)', "print >> stderr converts to file= kwarg");
})();

(function testPrintAlreadyFunction() {
  const result = convert('print("already a function")');
  assertIncludes(result.convertedCode, 'print("already a function")', "print() call remains unchanged");
})();

(function testBarePrint() {
  const result = convert('print');
  assertIncludes(result.convertedCode, 'print()', "Bare print converts to print()");
})();

// ========== Built-in Replacement Tests ==========
console.log("\n--- Built-in Replacements ---");

(function testRawInput() {
  const result = convert('name = raw_input("Enter: ")');
  assertIncludes(result.convertedCode, 'input("Enter: ")', "raw_input() converts to input()");
  assertNotIncludes(result.convertedCode, 'raw_input', "raw_input should not remain");
})();

(function testXrange() {
  const result = convert('for i in xrange(10): pass');
  assertIncludes(result.convertedCode, 'range(10)', "xrange() converts to range()");
  assertNotIncludes(result.convertedCode, 'xrange', "xrange should not remain");
})();

(function testUnicode() {
  const result = convert('s = unicode("hello")');
  assertIncludes(result.convertedCode, 'str("hello")', "unicode() converts to str()");
})();

(function testBasestring() {
  const result = convert('isinstance(x, basestring)');
  assertIncludes(result.convertedCode, 'isinstance(x, str)', "basestring converts to str");
})();

(function testLong() {
  const result = convert('n = long(42)');
  assertIncludes(result.convertedCode, 'int(42)', "long() converts to int()");
})();

// ========== Dictionary Tests ==========
console.log("\n--- Dictionary Method Conversion ---");

(function testHasKey() {
  const result = convert('if d.has_key("x"): pass');
  assertIncludes(result.convertedCode, '"x" in d', "has_key() converts to 'in' operator");
})();

(function testIteritems() {
  const result = convert('for k, v in d.iteritems(): pass');
  assertIncludes(result.convertedCode, 'd.items()', ".iteritems() converts to .items()");
})();

(function testItervalues() {
  const result = convert('for v in d.itervalues(): pass');
  assertIncludes(result.convertedCode, 'd.values()', ".itervalues() converts to .values()");
})();

(function testIterkeys() {
  const result = convert('for k in d.iterkeys(): pass');
  assertIncludes(result.convertedCode, 'd.keys()', ".iterkeys() converts to .keys()");
})();

// ========== Exception Handling Tests ==========
console.log("\n--- Exception Handling ---");

(function testExceptComma() {
  const result = convert('    except ValueError, e:');
  assertIncludes(result.convertedCode, 'except ValueError as e:', "except comma converts to 'as'");
})();

(function testRaiseComma() {
  const result = convert('    raise TypeError, "bad type"');
  assertIncludes(result.convertedCode, 'raise TypeError("bad type")', "raise comma converts to call syntax");
})();

// ========== Import Tests ==========
console.log("\n--- Import Conversion ---");

(function testFutureImportRemoval() {
  const result = convert('from __future__ import print_function');
  assertNotIncludes(result.convertedCode, 'from __future__', "__future__ import is removed");
})();

(function testUrllib2Import() {
  const result = convert('import urllib2');
  assertIncludes(result.convertedCode, 'import urllib.request', "urllib2 converts to urllib.request");
})();

(function testConfigParserImport() {
  const result = convert('import ConfigParser');
  assertIncludes(result.convertedCode, 'import configparser', "ConfigParser converts to configparser");
})();

(function testStringIOImport() {
  const result = convert('import StringIO');
  assertIncludes(result.convertedCode, 'import io', "StringIO converts to io");
})();

(function testReduceImport() {
  const result = convert('total = reduce(lambda a, b: a + b, [1, 2])');
  assertIncludes(result.convertedCode, 'from functools import reduce', "reduce() triggers functools import");
})();

// ========== Report Generation Tests ==========
console.log("\n--- Report Generation ---");

(function testEmptyReport() {
  const report = generateReport([]);
  assertIncludes(report, "No issues found", "Empty issues produces clean report");
})();

(function testReportWithIssues() {
  const issues = [
    { type: "info", line: 1, message: "test info" },
    { type: "warning", line: 2, message: "test warning" },
    { type: "error", line: 3, message: "test error" },
  ];
  const report = generateReport(issues);
  assertIncludes(report, "Errors (1)", "Report shows error count");
  assertIncludes(report, "Warnings (1)", "Report shows warning count");
  assertIncludes(report, "Info (1)", "Report shows info count");
})();

// ========== Test Generator Tests ==========
console.log("\n--- Test Generator ---");

(function testExtractFunctions() {
  const code = 'def foo(x, y):\n    return x + y\ndef bar():\n    pass';
  const funcs = extractFunctions(code);
  assertEqual(funcs.length, 2, "Extracts correct number of functions");
  assertEqual(funcs[0].name, "foo", "First function name is correct");
  assertEqual(funcs[0].args.length, 2, "First function has correct arg count");
  assertEqual(funcs[1].name, "bar", "Second function name is correct");
})();

(function testExtractClasses() {
  const code = 'class Foo:\n    pass\nclass Bar(Foo):\n    pass';
  const classes = extractClasses(code);
  assertEqual(classes.length, 2, "Extracts correct number of classes");
  assertEqual(classes[0].name, "Foo", "First class name is correct");
  assertEqual(classes[1].name, "Bar", "Second class name is correct");
})();

(function testDetectConversions() {
  const original = 'print "hello"\nraw_input()\nxrange(10)\nunicode("x")\nd.has_key("k")\nd.iteritems()';
  const converted = 'print("hello")\ninput()\nrange(10)\nstr("x")\n"k" in d\nd.items()';
  const patterns = detectConversions(original, converted);
  assert(patterns.includes("print_statement"), "Detects print statement conversion");
  assert(patterns.includes("raw_input"), "Detects raw_input conversion");
  assert(patterns.includes("xrange"), "Detects xrange conversion");
  assert(patterns.includes("unicode"), "Detects unicode conversion");
  assert(patterns.includes("has_key"), "Detects has_key conversion");
  assert(patterns.includes("iteritems"), "Detects iteritems conversion");
})();

(function testGenerateTestsOutput() {
  const original = 'print "hello"\ndef greet(): pass';
  const result = convert(original);
  const tests = generateTests(original, result.convertedCode);
  assertIncludes(tests, "def test_syntax_is_valid_python3", "Generated tests include syntax check");
  assertIncludes(tests, "def test_greet_exists", "Generated tests include function existence check");
})();

// ========== Full Integration Test ==========
console.log("\n--- Full Integration ---");

(function testFullSampleConversion() {
  const fs = require("fs");
  const path = require("path");
  const samplePath = path.join(__dirname, "..", "assets", "sample-py2-code.py");
  const expectedPath = path.join(__dirname, "..", "assets", "expected-py3-output.py");
  const sample = fs.readFileSync(samplePath, "utf-8");
  const expected = fs.readFileSync(expectedPath, "utf-8");

  const result = convert(sample);

  // Verify key conversions happened
  assertNotIncludes(result.convertedCode, "from __future__", "No __future__ imports remain");
  assertIncludes(result.convertedCode, "import urllib.request", "urllib2 converted");
  assertIncludes(result.convertedCode, "import configparser", "ConfigParser converted");
  assertIncludes(result.convertedCode, "import io", "StringIO converted");
  assertIncludes(result.convertedCode, 'print("Hello, World!")', "Print statements converted");
  assertIncludes(result.convertedCode, "input(", "raw_input converted");
  assertIncludes(result.convertedCode, "range(10)", "xrange converted");
  assertIncludes(result.convertedCode, "str(", "unicode converted");
  assertIncludes(result.convertedCode, "isinstance(greeting, str)", "basestring converted");
  assertIncludes(result.convertedCode, '"a" in my_dict', "has_key converted");
  assertIncludes(result.convertedCode, ".items()", "iteritems converted");
  assertIncludes(result.convertedCode, ".values()", "itervalues converted");
  assertIncludes(result.convertedCode, "except ZeroDivisionError as e:", "except syntax converted");
  assertIncludes(result.convertedCode, 'raise ValueError("x must be non-negative")', "raise syntax converted");
  assertIncludes(result.convertedCode, "from functools import reduce", "functools import added");

  // Verify no errors
  const errors = result.issues.filter((i) => i.type === "error");
  assertEqual(errors.length, 0, "No conversion errors on sample file");

  // Verify issues were generated
  assert(result.issues.length > 0, "Conversion issues were reported");
})();

// ========== Summary ==========
console.log("\n============================");
console.log(`Results: ${passed} passed, ${failed} failed`);

if (failures.length > 0) {
  console.log("\nFailures:");
  failures.forEach((f) => console.log(`  - ${f}`));
  process.exit(1);
}

console.log("\nAll tests passed!");
process.exit(0);
