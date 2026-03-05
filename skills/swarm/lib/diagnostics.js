/**
 * Swarm Diagnostics
 * System checks, test runner, and machine profiling
 */

const os = require('os');
const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');

const CONFIG_DIR = path.join(os.homedir(), '.config', 'clawdbot');

/**
 * Collect machine profile
 */
function getMachineProfile() {
  const cpus = os.cpus();
  const totalMem = os.totalmem();
  const freeMem = os.freemem();
  
  // Detect if running in container
  const isDocker = fs.existsSync('/.dockerenv');
  const isWSL = os.release().toLowerCase().includes('microsoft');
  
  // Check Node.js version
  const nodeVersion = process.version;
  const nodeMajor = parseInt(nodeVersion.slice(1).split('.')[0], 10);
  
  // Optimal worker count based on resources
  // Rule: min(CPU cores * 2, available_mem_gb / 0.1, 50)
  const memGb = freeMem / 1024 / 1024 / 1024;
  const optimalWorkers = Math.max(2, Math.min(
    cpus.length * 2,
    Math.floor(memGb / 0.1),
    50
  ));
  
  return {
    os: {
      platform: os.platform(),
      release: os.release(),
      arch: os.arch(),
      isDocker,
      isWSL,
    },
    cpu: {
      cores: cpus.length,
      model: cpus[0]?.model || 'unknown',
    },
    memory: {
      totalGb: Math.round(totalMem / 1024 / 1024 / 1024 * 10) / 10,
      freeGb: Math.round(freeMem / 1024 / 1024 / 1024 * 10) / 10,
      usedPercent: Math.round((1 - freeMem / totalMem) * 100),
    },
    node: {
      version: nodeVersion,
      major: nodeMajor,
      supported: nodeMajor >= 18,
    },
    recommendations: {
      optimalWorkers,
      maxConcurrentApi: Math.min(optimalWorkers, 20),
    },
  };
}

/**
 * Check for required dependencies
 */
function checkDependencies() {
  const issues = [];
  const resolved = [];
  
  // Check Node.js version
  const nodeMajor = parseInt(process.version.slice(1).split('.')[0], 10);
  if (nodeMajor < 18) {
    issues.push({
      type: 'node_version',
      severity: 'error',
      message: `Node.js ${process.version} is not supported. Requires v18+`,
      fix: 'Update Node.js: https://nodejs.org/',
    });
  } else {
    resolved.push('Node.js version OK');
  }
  
  // Check if lib files exist
  const libPath = path.join(__dirname);
  const requiredFiles = ['index.js', 'dispatcher.js', 'events.js', 'display.js'];
  
  for (const file of requiredFiles) {
    if (!fs.existsSync(path.join(libPath, file))) {
      issues.push({
        type: 'missing_file',
        severity: 'error',
        message: `Missing required file: lib/${file}`,
        fix: 'Reinstall the package: npm install @clawdbot/node-scaling',
      });
    }
  }
  
  if (issues.filter(i => i.type === 'missing_file').length === 0) {
    resolved.push('All lib files present');
  }
  
  // Check config directory
  if (!fs.existsSync(CONFIG_DIR)) {
    issues.push({
      type: 'no_config_dir',
      severity: 'warning',
      message: `Config directory doesn't exist: ${CONFIG_DIR}`,
      fix: `Create it: mkdir -p ${CONFIG_DIR}`,
      autoFix: () => fs.mkdirSync(CONFIG_DIR, { recursive: true }),
    });
  } else {
    resolved.push('Config directory exists');
  }
  
  return { issues, resolved };
}

/**
 * Check API key configuration
 */
function checkApiKeys() {
  const issues = [];
  const resolved = [];
  const providers = ['gemini', 'openai', 'anthropic', 'groq'];
  const envVars = {
    gemini: 'GEMINI_API_KEY',
    openai: 'OPENAI_API_KEY',
    anthropic: 'ANTHROPIC_API_KEY',
    groq: 'GROQ_API_KEY',
  };
  
  let hasAnyKey = false;
  
  for (const provider of providers) {
    // Check environment variable
    if (process.env[envVars[provider]]) {
      resolved.push(`${provider}: Found in environment (${envVars[provider]})`);
      hasAnyKey = true;
      continue;
    }
    
    // Check key file
    const keyFile = path.join(CONFIG_DIR, `${provider}-key.txt`);
    if (fs.existsSync(keyFile)) {
      const key = fs.readFileSync(keyFile, 'utf8').trim();
      if (key.length > 10) {
        resolved.push(`${provider}: Found in ${keyFile}`);
        hasAnyKey = true;
        continue;
      }
    }
  }
  
  if (!hasAnyKey) {
    issues.push({
      type: 'no_api_key',
      severity: 'error',
      message: 'No API key configured for any provider',
      fix: 'Run setup: node bin/setup.js OR set GEMINI_API_KEY environment variable',
    });
  }
  
  return { issues, resolved, hasAnyKey };
}

/**
 * Run test suite and return results
 */
async function runTests(options = {}) {
  const { skipE2e = false, timeout = 60000 } = options;
  const testDir = path.join(__dirname, '..', 'test');
  
  const results = {
    unit: { passed: 0, failed: 0, skipped: false, error: null },
    integration: { passed: 0, failed: 0, skipped: false, error: null },
    e2e: { passed: 0, failed: 0, skipped: false, error: null },
  };
  
  // Helper to run a test file and parse output
  async function runTestFile(name, file, env = {}) {
    return new Promise((resolve) => {
      const testPath = path.join(testDir, file);
      
      if (!fs.existsSync(testPath)) {
        resolve({ passed: 0, failed: 0, skipped: true, error: 'Test file not found' });
        return;
      }
      
      let output = '';
      const proc = spawn('node', [testPath], {
        env: { ...process.env, ...env },
        timeout,
      });
      
      proc.stdout.on('data', (data) => { output += data.toString(); });
      proc.stderr.on('data', (data) => { output += data.toString(); });
      
      proc.on('close', (code) => {
        // Parse output for pass/fail counts
        const passMatch = output.match(/(\d+) passed/);
        const failMatch = output.match(/(\d+) failed/);
        const skippedMatch = output.includes('Skipping') || output.includes('skipped');
        
        resolve({
          passed: passMatch ? parseInt(passMatch[1], 10) : 0,
          failed: failMatch ? parseInt(failMatch[1], 10) : 0,
          skipped: skippedMatch,
          error: code !== 0 && !skippedMatch ? `Exit code ${code}` : null,
          output: options.verbose ? output : undefined,
        });
      });
      
      proc.on('error', (err) => {
        resolve({ passed: 0, failed: 0, skipped: false, error: err.message });
      });
    });
  }
  
  // Run unit tests (always)
  results.unit = await runTestFile('unit', 'unit.test.js');
  
  // Run integration tests (always)
  results.integration = await runTestFile('integration', 'integration.test.js');
  
  // Run E2E tests (if not skipped and API key available)
  if (skipE2e) {
    results.e2e = { passed: 0, failed: 0, skipped: true, error: null };
  } else {
    const apiCheck = checkApiKeys();
    if (!apiCheck.hasAnyKey) {
      results.e2e = { passed: 0, failed: 0, skipped: true, error: 'No API key' };
    } else {
      // Find an API key to use
      let env = {};
      if (process.env.GEMINI_API_KEY) {
        env.GEMINI_API_KEY = process.env.GEMINI_API_KEY;
      } else {
        const keyFile = path.join(CONFIG_DIR, 'gemini-key.txt');
        if (fs.existsSync(keyFile)) {
          env.GEMINI_API_KEY = fs.readFileSync(keyFile, 'utf8').trim();
        }
      }
      results.e2e = await runTestFile('e2e', 'e2e.test.js', env);
    }
  }
  
  return results;
}

/**
 * Generate full diagnostic report
 */
async function runDiagnostics(options = {}) {
  const report = {
    timestamp: new Date().toISOString(),
    machine: getMachineProfile(),
    dependencies: checkDependencies(),
    apiKeys: checkApiKeys(),
    tests: null,
    status: 'unknown',
    issues: [],
    recommendations: [],
  };
  
  // Run tests if requested
  if (options.runTests !== false) {
    report.tests = await runTests({
      skipE2e: options.skipE2e,
      verbose: options.verbose,
    });
  }
  
  // Collect all issues
  report.issues = [
    ...report.dependencies.issues,
    ...report.apiKeys.issues,
  ];
  
  // Add test failures as issues
  if (report.tests) {
    if (report.tests.unit.failed > 0) {
      report.issues.push({
        type: 'test_failure',
        severity: 'error',
        message: `Unit tests failed: ${report.tests.unit.failed} failures`,
        fix: 'Run `npm run test:unit` to see details',
      });
    }
    if (report.tests.integration.failed > 0) {
      report.issues.push({
        type: 'test_failure',
        severity: 'error',
        message: `Integration tests failed: ${report.tests.integration.failed} failures`,
        fix: 'Run `npm run test:integration` to see details',
      });
    }
    if (report.tests.e2e.failed > 0) {
      report.issues.push({
        type: 'test_failure',
        severity: 'warning',
        message: `E2E tests failed: ${report.tests.e2e.failed} failures`,
        fix: 'Check API key and run `npm run test:e2e` to see details',
      });
    }
  }
  
  // Generate recommendations
  const { recommendations } = report.machine;
  report.recommendations.push(
    `Optimal worker count for this machine: ${recommendations.optimalWorkers}`,
    `Max concurrent API calls: ${recommendations.maxConcurrentApi}`
  );
  
  if (report.machine.memory.freeGb < 1) {
    report.recommendations.push('Low memory detected - consider reducing max workers');
  }
  
  if (report.machine.os.isDocker) {
    report.recommendations.push('Running in Docker - ensure sufficient memory limits are set');
  }
  
  // Determine overall status
  const errors = report.issues.filter(i => i.severity === 'error');
  const warnings = report.issues.filter(i => i.severity === 'warning');
  
  if (errors.length > 0) {
    report.status = 'error';
  } else if (warnings.length > 0) {
    report.status = 'warning';
  } else {
    report.status = 'ok';
  }
  
  return report;
}

/**
 * Print diagnostic report to console
 */
function printReport(report) {
  console.log('\n🔍 SWARM DIAGNOSTICS REPORT');
  console.log('═'.repeat(50));
  
  // Machine info
  console.log('\n📊 Machine Profile');
  console.log(`   OS: ${report.machine.os.platform} ${report.machine.os.arch}`);
  console.log(`   CPU: ${report.machine.cpu.cores} cores (${report.machine.cpu.model.substring(0, 40)})`);
  console.log(`   Memory: ${report.machine.memory.freeGb}GB free / ${report.machine.memory.totalGb}GB total`);
  console.log(`   Node.js: ${report.machine.node.version}`);
  
  if (report.machine.os.isDocker) console.log('   ⚠️  Running in Docker');
  if (report.machine.os.isWSL) console.log('   ℹ️  Running in WSL');
  
  // Test results
  if (report.tests) {
    console.log('\n🧪 Test Results');
    const t = report.tests;
    console.log(`   Unit:        ${t.unit.skipped ? '⏭️  Skipped' : t.unit.failed > 0 ? `❌ ${t.unit.passed}/${t.unit.passed + t.unit.failed}` : `✅ ${t.unit.passed} passed`}`);
    console.log(`   Integration: ${t.integration.skipped ? '⏭️  Skipped' : t.integration.failed > 0 ? `❌ ${t.integration.passed}/${t.integration.passed + t.integration.failed}` : `✅ ${t.integration.passed} passed`}`);
    console.log(`   E2E:         ${t.e2e.skipped ? '⏭️  Skipped (no API key)' : t.e2e.failed > 0 ? `❌ ${t.e2e.passed}/${t.e2e.passed + t.e2e.failed}` : `✅ ${t.e2e.passed} passed`}`);
  }
  
  // Issues
  if (report.issues.length > 0) {
    console.log('\n⚠️  Issues Found');
    for (const issue of report.issues) {
      const icon = issue.severity === 'error' ? '❌' : '⚠️';
      console.log(`   ${icon} ${issue.message}`);
      if (issue.fix) {
        console.log(`      Fix: ${issue.fix}`);
      }
    }
  }
  
  // Recommendations
  console.log('\n💡 Recommendations');
  for (const rec of report.recommendations) {
    console.log(`   • ${rec}`);
  }
  
  // Status
  console.log('\n' + '─'.repeat(50));
  if (report.status === 'ok') {
    console.log('✅ Status: All checks passed!\n');
  } else if (report.status === 'warning') {
    console.log('⚠️  Status: Warnings found (Swarm should still work)\n');
  } else {
    console.log('❌ Status: Errors found (Swarm may not work correctly)\n');
  }
}

module.exports = {
  getMachineProfile,
  checkDependencies,
  checkApiKeys,
  runTests,
  runDiagnostics,
  printReport,
};
