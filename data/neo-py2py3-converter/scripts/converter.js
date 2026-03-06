"use strict";

/**
 * py2py3-converter: Core conversion engine.
 * Transforms Python 2 source code into Python 3 syntax.
 */

/**
 * All conversion rules applied to the source code.
 * Each rule has a name, a transform function, and produces issues.
 */
const IMPORT_MAP = {
  urllib2: "urllib.request",
  urlparse: "urllib.parse",
  ConfigParser: "configparser",
  Queue: "queue",
  StringIO: "io",
  cPickle: "pickle",
  HTMLParser: "html.parser",
  httplib: "http.client",
  thread: "_thread",
};

const FUTURE_IMPORTS = [
  "print_function",
  "unicode_literals",
  "absolute_import",
  "division",
];

/**
 * Convert Python 2 code to Python 3.
 * @param {string} code - Python 2 source code
 * @param {object} [options] - Conversion options
 * @param {boolean} [options.keepWarnings=true] - Include warnings in output
 * @returns {{ convertedCode: string, issues: Array<{type: string, line: number, message: string}> }}
 */
function convert(code, options) {
  options = Object.assign({ keepWarnings: true }, options || {});

  const issues = [];
  let lines = code.split("\n");
  let needsFunctoolsImport = false;
  let hasFunctoolsImport = false;

  // Check if functools is already imported
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*(?:from\s+functools\s+import|import\s+functools)/.test(lines[i])) {
      hasFunctoolsImport = true;
      break;
    }
  }

  // Process each line
  const converted = [];
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    const lineNum = i + 1;
    const indent = line.match(/^(\s*)/)[1];
    const trimmed = line.trimStart();

    // Skip empty lines and comments
    if (trimmed === "" || trimmed.startsWith("#")) {
      converted.push(line);
      continue;
    }

    // --- Remove __future__ imports ---
    const futureMatch = trimmed.match(
      /^from\s+__future__\s+import\s+(.+)$/
    );
    if (futureMatch) {
      const imports = futureMatch[1].split(",").map((s) => s.trim());
      const remaining = imports.filter(
        (imp) => !FUTURE_IMPORTS.includes(imp)
      );
      if (remaining.length === 0) {
        issues.push({
          type: "info",
          line: lineNum,
          message: `Removed __future__ import: ${futureMatch[1]}`,
        });
        // Skip line entirely
        continue;
      } else {
        line =
          indent +
          "from __future__ import " +
          remaining.join(", ");
        issues.push({
          type: "info",
          line: lineNum,
          message: `Removed some __future__ imports, kept: ${remaining.join(", ")}`,
        });
      }
    }

    // --- Module import remapping ---
    const importMatch = trimmed.match(/^import\s+(\w+)$/);
    if (importMatch && IMPORT_MAP[importMatch[1]]) {
      const oldMod = importMatch[1];
      const newMod = IMPORT_MAP[oldMod];
      line = indent + "import " + newMod;
      issues.push({
        type: "info",
        line: lineNum,
        message: `Replaced import ${oldMod} with ${newMod}`,
      });
      converted.push(line);
      continue;
    }

    const fromImportMatch = trimmed.match(
      /^from\s+(\w+)\s+import\s+(.+)$/
    );
    if (
      fromImportMatch &&
      IMPORT_MAP[fromImportMatch[1]] &&
      !trimmed.startsWith("from __future__")
    ) {
      const oldMod = fromImportMatch[1];
      const newMod = IMPORT_MAP[oldMod];
      line = indent + "from " + newMod + " import " + fromImportMatch[2];
      issues.push({
        type: "info",
        line: lineNum,
        message: `Replaced from ${oldMod} import with from ${newMod} import`,
      });
      converted.push(line);
      continue;
    }

    // --- Print statement conversion ---
    line = convertPrintStatements(line, indent, trimmed, lineNum, issues);

    // --- raw_input → input ---
    if (/\braw_input\s*\(/.test(line)) {
      line = line.replace(/\braw_input\s*\(/g, "input(");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced raw_input() with input()",
      });
    }

    // --- xrange → range ---
    if (/\bxrange\s*\(/.test(line)) {
      line = line.replace(/\bxrange\s*\(/g, "range(");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced xrange() with range()",
      });
    }

    // --- unicode() → str() ---
    if (/\bunicode\s*\(/.test(line)) {
      line = line.replace(/\bunicode\s*\(/g, "str(");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced unicode() with str()",
      });
    }

    // --- basestring → str ---
    if (/\bbasestring\b/.test(line)) {
      line = line.replace(/\bbasestring\b/g, "str");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced basestring with str",
      });
    }

    // --- long() → int() / long type → int ---
    if (/\blong\s*\(/.test(line)) {
      line = line.replace(/\blong\s*\(/g, "int(");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced long() with int()",
      });
    }

    // --- dict.has_key(k) → k in dict ---
    const hasKeyMatch = line.match(/(\w+)\.has_key\(([^)]+)\)/);
    if (hasKeyMatch) {
      line = line.replace(
        /(\w+)\.has_key\(([^)]+)\)/g,
        (_, dictName, key) => `${key} in ${dictName}`
      );
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced dict.has_key(k) with k in dict",
      });
    }

    // --- dict.iteritems() → dict.items() ---
    if (/\.iteritems\s*\(\s*\)/.test(line)) {
      line = line.replace(/\.iteritems\s*\(\s*\)/g, ".items()");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced .iteritems() with .items()",
      });
    }

    // --- dict.itervalues() → dict.values() ---
    if (/\.itervalues\s*\(\s*\)/.test(line)) {
      line = line.replace(/\.itervalues\s*\(\s*\)/g, ".values()");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced .itervalues() with .values()",
      });
    }

    // --- dict.iterkeys() → dict.keys() ---
    if (/\.iterkeys\s*\(\s*\)/.test(line)) {
      line = line.replace(/\.iterkeys\s*\(\s*\)/g, ".keys()");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced .iterkeys() with .keys()",
      });
    }

    // --- except Exception, e → except Exception as e ---
    const exceptMatch = line.match(
      /^(\s*except\s+\w+(?:\.\w+)*)\s*,\s*(\w+)\s*:/
    );
    if (exceptMatch) {
      line = exceptMatch[1] + " as " + exceptMatch[2] + ":";
      issues.push({
        type: "info",
        line: lineNum,
        message: "Replaced comma-style except with 'as' keyword",
      });
    }

    // --- raise Type, "msg" → raise Type("msg") ---
    const raiseMatch = line.match(
      /^(\s*raise\s+)(\w+(?:\.\w+)*)\s*,\s*(.+)$/
    );
    if (raiseMatch) {
      line = raiseMatch[1] + raiseMatch[2] + "(" + raiseMatch[3] + ")";
      issues.push({
        type: "info",
        line: lineNum,
        message: "Converted raise statement to Python 3 syntax",
      });
    }

    // --- standalone reduce() → functools.reduce() ---
    if (/(?<!\w)reduce\s*\(/.test(line) && !/functools\.reduce/.test(line)) {
      // Check if this is a standalone reduce call (not method call)
      if (!/\.\s*reduce\s*\(/.test(line)) {
        needsFunctoolsImport = true;
        issues.push({
          type: "info",
          line: lineNum,
          message: "reduce() requires functools import in Python 3",
        });
      }
    }

    // --- u"string" prefix removal ---
    if (/\bu(['"])/.test(line)) {
      line = line.replace(/\bu(['"])/g, "$1");
      issues.push({
        type: "info",
        line: lineNum,
        message: "Removed u prefix from string literal (default in Python 3)",
      });
    }

    converted.push(line);
  }

  // Insert functools import if needed
  let result = converted;
  if (needsFunctoolsImport && !hasFunctoolsImport) {
    result = insertFunctoolsImport(converted);
    issues.push({
      type: "info",
      line: 1,
      message: "Added 'from functools import reduce' for Python 3 compatibility",
    });
  }

  // Filter issues based on options
  let finalIssues = issues;
  if (!options.keepWarnings) {
    finalIssues = issues.filter((i) => i.type !== "warning");
  }

  return {
    convertedCode: result.join("\n"),
    issues: finalIssues,
  };
}

/**
 * Convert Python 2 print statements to Python 3 print() calls.
 */
function convertPrintStatements(line, indent, trimmed, lineNum, issues) {
  // Already a function call: print(...) - leave as is
  if (/^\s*print\s*\(/.test(line)) {
    return line;
  }

  // print >> sys.stderr, "msg" → print("msg", file=sys.stderr)
  const printStderrMatch = trimmed.match(
    /^print\s*>>\s*([\w.]+)\s*,\s*(.+)$/
  );
  if (printStderrMatch) {
    const target = printStderrMatch[1];
    const content = printStderrMatch[2];
    issues.push({
      type: "info",
      line: lineNum,
      message: `Converted print >> ${target} to print(..., file=${target})`,
    });
    return indent + "print(" + content + ", file=" + target + ")";
  }

  // print "a", (trailing comma = no newline) → print("a", end=" ")
  const printTrailingComma = trimmed.match(/^print\s+(.+),\s*$/);
  if (printTrailingComma) {
    const content = printTrailingComma[1];
    issues.push({
      type: "info",
      line: lineNum,
      message: "Converted print with trailing comma to print(..., end=\" \")",
    });
    return indent + "print(" + content + ', end=" ")';
  }

  // print "value" or print "a", "b"
  const printMatch = trimmed.match(/^print\s+(.+)$/);
  if (printMatch) {
    const content = printMatch[1];
    issues.push({
      type: "info",
      line: lineNum,
      message: "Converted print statement to function call",
    });
    return indent + "print(" + content + ")";
  }

  // Bare print (no arguments)
  if (/^\s*print\s*$/.test(line)) {
    issues.push({
      type: "info",
      line: lineNum,
      message: "Converted bare print statement to print()",
    });
    return indent + "print()";
  }

  return line;
}

/**
 * Insert 'from functools import reduce' at the correct position in the file.
 */
function insertFunctoolsImport(lines) {
  // Find the last import line
  let lastImportIndex = -1;
  for (let i = 0; i < lines.length; i++) {
    if (/^\s*(import\s|from\s)/.test(lines[i])) {
      lastImportIndex = i;
    }
  }

  const importLine = "from functools import reduce";

  if (lastImportIndex >= 0) {
    // Insert after last import
    lines.splice(lastImportIndex + 1, 0, importLine);
  } else {
    // No imports found, insert at beginning (after shebang/encoding if present)
    let insertAt = 0;
    for (let i = 0; i < Math.min(lines.length, 3); i++) {
      if (lines[i].startsWith("#!") || lines[i].startsWith("# -*-")) {
        insertAt = i + 1;
      }
    }
    lines.splice(insertAt, 0, importLine);
  }

  return lines;
}

/**
 * Generate a compatibility report from issues.
 * @param {Array} issues - Array of issue objects
 * @returns {string} Formatted report
 */
function generateReport(issues) {
  if (issues.length === 0) {
    return "No issues found. Code appears to be Python 3 compatible.";
  }

  const errors = issues.filter((i) => i.type === "error");
  const warnings = issues.filter((i) => i.type === "warning");
  const infos = issues.filter((i) => i.type === "info");

  let report = "=== Conversion Report ===\n\n";

  if (errors.length > 0) {
    report += `Errors (${errors.length}):\n`;
    errors.forEach((e) => {
      report += `  Line ${e.line}: ${e.message}\n`;
    });
    report += "\n";
  }

  if (warnings.length > 0) {
    report += `Warnings (${warnings.length}):\n`;
    warnings.forEach((w) => {
      report += `  Line ${w.line}: ${w.message}\n`;
    });
    report += "\n";
  }

  if (infos.length > 0) {
    report += `Info (${infos.length}):\n`;
    infos.forEach((info) => {
      report += `  Line ${info.line}: ${info.message}\n`;
    });
    report += "\n";
  }

  report += `Total: ${errors.length} errors, ${warnings.length} warnings, ${infos.length} info\n`;

  return report;
}

module.exports = { convert, generateReport };
