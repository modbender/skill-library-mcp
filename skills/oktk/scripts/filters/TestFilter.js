/**
 * TestFilter - Filter test framework output (npm, cargo, pytest, jest, etc.)
 */

const BaseFilter = require('./BaseFilter');

class TestFilter extends BaseFilter {
  async apply(output, context = {}) {
    // Check if filtering is safe
    if (!this.canFilter(output)) {
      return output;
    }

    // Remove ANSI codes
    output = this.removeAnsiCodes(output);

    // Detect test framework
    const command = context.command || '';
    if (command.includes('npm') || command.includes('yarn')) {
      return this.filterNpm(output);
    } else if (command.includes('cargo')) {
      return this.filterCargo(output);
    } else if (command.includes('pytest')) {
      return this.filterPytest(output);
    } else if (command.includes('jest')) {
      return this.filterJest(output);
    } else {
      return this.filterGeneric(output);
    }
  }

  /**
   * Filter npm/yarn test output
   */
  filterNpm(output) {
    const lines = output.split('\n');

    // Parse npm test output
    let totalTests = 0;
    let passed = 0;
    let failed = 0;
    let skipped = 0;
    const suites = new Set();
    const failures = [];

    for (const line of lines) {
      // Count tests from summary line (e.g., "Tests: 12 passed, 12 total")
      const testsSummaryMatch = line.match(/^Tests:\s+(\d+)\s+passed/i);
      if (testsSummaryMatch) {
        passed = parseInt(testsSummaryMatch[1]);
        continue;
      }

      const testsFailedMatch = line.match(/^Tests:\s+[^,]+,\s+(\d+)\s+failed/i);
      if (testsFailedMatch) {
        failed = parseInt(testsFailedMatch[1]);
        continue;
      }

      // Count tests (alternative patterns)
      const testMatch = line.match(/(\d+)\s+passed/i);
      if (testMatch) {
        const count = parseInt(testMatch[1]);
        // Only use if it's not from a summary line we already processed
        if (passed === 0) passed = count;
      }

      const failMatch = line.match(/(\d+)\s+failed/i);
      if (failMatch && failed === 0) {
        failed = parseInt(failMatch[1]);
      }

      const skipMatch = line.match(/(\d+)\s+(skipped|pending)/i);
      if (skipMatch && skipped === 0) {
        skipped = parseInt(skipMatch[1]);
      }

      // Test suite detection
      const suiteMatch = line.match(/(PASS|FAIL)\s+(.+)/);
      if (suiteMatch) {
        suites.add(suiteMatch[2]);
      }

      // Failure extraction
      if (line.includes('✗') || line.includes('✖') || line.includes('●')) {
        failures.push(line.trim());
      }
    }

    // If no tests found, try generic parsing
    if (totalTests === 0) {
      totalTests = passed + failed + skipped;
    }

    // Build summary
    const result = [];

    // Overall status
    if (failed > 0) {
      result.push('❌ Tests failed');
    } else if (passed > 0) {
      result.push('✅ All tests passed');
    } else {
      result.push('⚠️  No tests run');
    }

    // Statistics
    if (passed > 0 || failed > 0) {
      result.push(``);
      result.push(`📊 ${passed + failed} total tests`);
      if (passed > 0) result.push(`  ✅ Passed: ${passed}`);
      if (failed > 0) result.push(`  ❌ Failed: ${failed}`);
      if (skipped > 0) result.push(`  ⏭️  Skipped: ${skipped}`);
    }

    // Test suites
    if (suites.size > 0) {
      result.push(``);
      result.push(`📦 ${suites.size} test suite(s)`);
    }

    // Show failures (limited)
    if (failures.length > 0) {
      result.push(``);
      result.push(`❌ Failures:`);
      failures.slice(0, 10).forEach(f => {
        result.push(`  ${f.substring(0, 80)}`);
      });
      if (failures.length > 10) {
        result.push(`  ... and ${failures.length - 10} more failures`);
      }
    }

    // Extract timing if available
    for (const line of lines) {
      const timeMatch = line.match(/(\d+(?:\.\d+)?)\s*s/);
      if (timeMatch) {
        result.push(``);
        result.push(`⏱️  Duration: ${timeMatch[1]}s`);
        break;
      }
    }

    return result.join('\n');
  }

  /**
   * Filter cargo test output
   */
  filterCargo(output) {
    const lines = output.split('\n');

    let totalTests = 0;
    let passed = 0;
    let failed = 0;
    const suites = [];
    const failures = [];

    for (const line of lines) {
      // Test result
      const testResult = line.match(/^test\s+(.+)\s+\.\.\.\s+(ok|FAILED)/);
      if (testResult) {
        totalTests++;
        if (testResult[2] === 'ok') passed++;
        else failed++;
      }

      // Suite info
      const suiteMatch = line.match(/^running\s+(\d+)\s+test/);
      if (suiteMatch) {
        suites.push({ count: parseInt(suiteMatch[1]), name: '' });
      }

      // Failure details
      if (line.includes('FAILED')) {
        failures.push(line.trim());
      }
    }

    const result = [];

    // Overall status
    if (failed > 0) {
      result.push('❌ Tests failed');
    } else if (passed > 0) {
      result.push('✅ All tests passed');
    } else {
      result.push('⚠️  No tests run');
    }

    // Statistics
    if (totalTests > 0) {
      result.push(``);
      result.push(`📊 ${totalTests} total tests`);
      if (passed > 0) result.push(`  ✅ Passed: ${passed}`);
      if (failed > 0) result.push(`  ❌ Failed: ${failed}`);
    }

    // Test suites
    if (suites.length > 0) {
      result.push(``);
      result.push(`📦 ${suites.length} test suite(s)`);
    }

    // Failures
    if (failures.length > 0) {
      result.push(``);
      result.push(`❌ Failures:`);
      failures.slice(0, 10).forEach(f => {
        result.push(`  ${f.substring(0, 80)}`);
      });
      if (failures.length > 10) {
        result.push(`  ... and ${failures.length - 10} more failures`);
      }
    }

    // Extract timing
    for (const line of lines) {
      const timeMatch = line.match(/test result: ok\.\s+passed:\s+\d+;\s+failed:\s+\d+;\s+ignored:\s+\d+;\s+measured:\s+\d+;\s+filtered out:\s+\d+;\s+finished in\s+([0-9.]+)s/);
      if (timeMatch) {
        result.push(``);
        result.push(`⏱️  Duration: ${timeMatch[1]}s`);
        break;
      }
    }

    return result.join('\n');
  }

  /**
   * Filter pytest output
   */
  filterPytest(output) {
    const lines = output.split('\n');

    let totalTests = 0;
    let passed = 0;
    let failed = 0;
    let skipped = 0;
    const failures = [];

    for (const line of lines) {
      // Test summary line
      const summaryMatch = line.match(/(\d+)\s+passed,\s*(\d+)\s+failed/);
      if (summaryMatch) {
        passed = parseInt(summaryMatch[1]);
        failed = parseInt(summaryMatch[2]);
        totalTests = passed + failed;
      }

      const skipMatch = line.match(/(\d+)\s+skipped/);
      if (skipMatch) skipped = parseInt(skipMatch[1]);

      // Failure indicators
      if (line.includes('FAILED')) {
        failures.push(line.trim());
      }
    }

    const result = [];

    // Overall status
    if (failed > 0) {
      result.push('❌ Tests failed');
    } else if (passed > 0) {
      result.push('✅ All tests passed');
    } else {
      result.push('⚠️  No tests run');
    }

    // Statistics
    if (totalTests > 0) {
      result.push(``);
      result.push(`📊 ${totalTests} total tests`);
      if (passed > 0) result.push(`  ✅ Passed: ${passed}`);
      if (failed > 0) result.push(`  ❌ Failed: ${failed}`);
      if (skipped > 0) result.push(`  ⏭️  Skipped: ${skipped}`);
    }

    // Failures
    if (failures.length > 0) {
      result.push(``);
      result.push(`❌ Failures:`);
      failures.slice(0, 10).forEach(f => {
        result.push(`  ${f.substring(0, 80)}`);
      });
      if (failures.length > 10) {
        result.push(`  ... and ${failures.length - 10} more failures`);
      }
    }

    // Extract timing
    for (const line of lines) {
      const timeMatch = line.match(/finished in\s+([0-9.]+)s/);
      if (timeMatch) {
        result.push(``);
        result.push(`⏱️  Duration: ${timeMatch[1]}s`);
        break;
      }
    }

    return result.join('\n');
  }

  /**
   * Filter jest output
   */
  filterJest(output) {
    const lines = output.split('\n');

    let totalTests = 0;
    let passed = 0;
    let failed = 0;
    const suites = [];
    const failures = [];

    for (const line of lines) {
      // Test counts
      const testMatch = line.match(/Tests:\s+(\d+)\s+passed,\s*(\d+)\s+failed/);
      if (testMatch) {
        passed = parseInt(testMatch[1]);
        failed = parseInt(testMatch[2]);
        totalTests = passed + failed;
      }

      // Suite names
      const suiteMatch = line.match(/PASS\s+(.+)/);
      if (suiteMatch) {
        suites.push({ name: suiteMatch[1], status: 'PASS' });
      }

      const failSuiteMatch = line.match(/FAIL\s+(.+)/);
      if (failSuiteMatch) {
        suites.push({ name: failSuiteMatch[1], status: 'FAIL' });
      }

      // Failures
      if (line.includes('●') || line.includes('✕')) {
        failures.push(line.trim());
      }
    }

    const result = [];

    // Overall status
    if (failed > 0) {
      result.push('❌ Tests failed');
    } else if (passed > 0) {
      result.push('✅ All tests passed');
    } else {
      result.push('⚠️  No tests run');
    }

    // Statistics
    if (totalTests > 0) {
      result.push(``);
      result.push(`📊 ${totalTests} total tests`);
      if (passed > 0) result.push(`  ✅ Passed: ${passed}`);
      if (failed > 0) result.push(`  ❌ Failed: ${failed}`);
    }

    // Test suites
    if (suites.length > 0) {
      result.push(``);
      result.push(`📦 ${suites.length} test suite(s)`);
      const failedSuites = suites.filter(s => s.status === 'FAIL');
      if (failedSuites.length > 0) {
        result.push(`  ❌ Failed: ${failedSuites.length}`);
        failedSuites.slice(0, 5).forEach(s => {
          result.push(`    - ${s.name.substring(0, 60)}`);
        });
      }
    }

    // Failures
    if (failures.length > 0 && failures.length <= 20) {
      result.push(``);
      result.push(`❌ Failures:`);
      failures.slice(0, 10).forEach(f => {
        result.push(`  ${f.substring(0, 80)}`);
      });
      if (failures.length > 10) {
        result.push(`  ... and ${failures.length - 10} more failures`);
      }
    }

    // Extract timing
    for (const line of lines) {
      const timeMatch = line.match(/Time:\s+([0-9.]+)s/);
      if (timeMatch) {
        result.push(``);
        result.push(`⏱️  Duration: ${timeMatch[1]}s`);
        break;
      }
    }

    return result.join('\n');
  }

  /**
   * Generic test filter
   */
  filterGeneric(output) {
    const lines = output.split('\n');

    // Try to extract test results generically
    let passed = 0;
    let failed = 0;
    let total = 0;

    for (const line of lines) {
      const passMatch = line.match(/(\d+)\s+passed/i);
      if (passMatch) passed += parseInt(passMatch[1]);

      const failMatch = line.match(/(\d+)\s+failed/i);
      if (failMatch) failed += parseInt(failMatch[1]);

      const totalMatch = line.match(/(\d+)\s+tests?/i);
      if (totalMatch && total === 0) total = parseInt(totalMatch[1]);
    }

    if (passed > 0 || failed > 0) {
      if (total === 0) total = passed + failed;

      const result = [
        failed > 0 ? '❌ Tests failed' : '✅ All tests passed',
        ``,
        `📊 ${total} total tests`,
        passed > 0 ? `  ✅ Passed: ${passed}` : '',
        failed > 0 ? `  ❌ Failed: ${failed}` : ''
      ].filter(Boolean);

      return result.join('\n');
    }

    // Fallback: show first 20 lines
    if (lines.length <= 20) {
      return output;
    }

    return [
      ...lines.slice(0, 10),
      ``,
      `[... ${lines.length - 15} lines hidden ...]`,
      ``,
      ...lines.slice(-5)
    ].join('\n');
  }
}

module.exports = TestFilter;
