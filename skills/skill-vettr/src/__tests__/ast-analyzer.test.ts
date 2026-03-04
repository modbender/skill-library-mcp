import { describe, it, before } from 'node:test';
import assert from 'node:assert/strict';
import { AstAnalyzer } from '../analyzers/ast-analyzer.js';

describe('AstAnalyzer', () => {
  const analyzer = new AstAnalyzer();

  before(async () => {
    await analyzer.init();
  });

  describe('WASM artifact verification', () => {
    it('exposes REQUIRED_WASM_PATHS as a static readonly array', () => {
      assert.ok(Array.isArray(AstAnalyzer.REQUIRED_WASM_PATHS));
      assert.ok(AstAnalyzer.REQUIRED_WASM_PATHS.length > 0);
      for (const p of AstAnalyzer.REQUIRED_WASM_PATHS) {
        assert.ok(p.endsWith('.wasm'), `Expected .wasm extension: ${p}`);
      }
    });

    it('throws descriptive error when WASM files are missing', async () => {
      const fresh = new AstAnalyzer();
      const original = AstAnalyzer.REQUIRED_WASM_PATHS;

      // Temporarily override with a non-existent WASM path
      const fakePaths = ['nonexistent-pkg/missing.wasm'];
      Object.defineProperty(AstAnalyzer, 'REQUIRED_WASM_PATHS', {
        value: fakePaths,
        configurable: true,
      });

      try {
        await assert.rejects(() => fresh.init(), (err: Error) => {
          assert.ok(err.message.includes('Missing required WASM artifacts'));
          assert.ok(err.message.includes('npm install'));
          assert.ok(err.message.includes('nonexistent-pkg/missing.wasm'));
          return true;
        });
      } finally {
        // Restore original paths
        Object.defineProperty(AstAnalyzer, 'REQUIRED_WASM_PATHS', {
          value: original,
          configurable: true,
        });
      }
    });
  });

  describe('eval detection', () => {
    it('detects eval() calls', () => {
      const findings = analyzer.analyze('test.js', 'eval("code")', '.js');
      assert.ok(findings.some((f) => f.message.includes('eval()')));
    });

    it('detects new Function()', () => {
      const findings = analyzer.analyze('test.js', 'new Function("return 1")', '.js');
      assert.ok(findings.some((f) => f.message.includes('Function()')));
    });

    it('does not flag eval as a string', () => {
      const findings = analyzer.analyze('test.js', 'const name = "eval";', '.js');
      // The string "eval" alone shouldn't trigger the call_expression rule
      const evalFindings = findings.filter((f) => f.message.includes('eval()'));
      assert.equal(evalFindings.length, 0);
    });
  });

  describe('shell injection detection', () => {
    it('detects exec() with string argument', () => {
      const findings = analyzer.analyze('test.js', 'exec("ls -la")', '.js');
      assert.ok(findings.some((f) => f.category === 'SHELL_INJECTION'));
    });

    it('detects execSync()', () => {
      const findings = analyzer.analyze('test.js', 'execSync("whoami")', '.js');
      assert.ok(findings.some((f) => f.message.includes('execSync')));
    });

    it('detects child_process import', () => {
      const findings = analyzer.analyze('test.js', 'import { exec } from "child_process";', '.js');
      assert.ok(findings.some((f) => f.message.includes('child_process')));
    });

    it('detects child_process require', () => {
      const findings = analyzer.analyze('test.js', 'const cp = require("child_process");', '.js');
      assert.ok(findings.some((f) => f.message.includes('child_process')));
    });

    it('detects spawn with shell', () => {
      const findings = analyzer.analyze('test.js', 'spawn("bash", ["-c", cmd])', '.js');
      assert.ok(findings.some((f) => f.message.includes('spawn')));
    });
  });

  describe('VM module detection', () => {
    it('detects vm.runInThisContext', () => {
      const findings = analyzer.analyze('test.js', 'vm.runInThisContext(code)', '.js');
      assert.ok(findings.some((f) => f.message.includes('vm module')));
    });

    it('detects vm.compileFunction', () => {
      const findings = analyzer.analyze('test.js', 'vm.compileFunction(src)', '.js');
      assert.ok(findings.some((f) => f.message.includes('vm module')));
    });
  });

  describe('dynamic require detection', () => {
    it('detects require with variable', () => {
      const findings = analyzer.analyze('test.js', 'const m = require(moduleName)', '.js');
      assert.ok(findings.some((f) => f.message.includes('Dynamic require')));
    });

    it('detects require with template string', () => {
      const findings = analyzer.analyze('test.js', 'require(`./modules/${name}`)', '.js');
      assert.ok(findings.some((f) => f.message.includes('Dynamic require')));
    });

    it('does not flag require with string literal', () => {
      const findings = analyzer.analyze('test.js', 'require("lodash")', '.js');
      const dynamicFindings = findings.filter((f) => f.message.includes('Dynamic require'));
      assert.equal(dynamicFindings.length, 0);
    });
  });

  describe('prototype pollution detection', () => {
    it('detects __proto__ assignment', () => {
      const findings = analyzer.analyze('test.js', 'obj.__proto__ = malicious', '.js');
      assert.ok(findings.some((f) => f.message.includes('__proto__')));
    });
  });

  describe('TypeScript support', () => {
    it('analyses .ts files', () => {
      const code = 'const fn = eval("return 1");\n';
      const findings = analyzer.analyze('test.ts', code, '.ts');
      assert.ok(findings.some((f) => f.message.includes('eval()')));
    });
  });

  describe('network call extraction', () => {
    it('extracts fetch URLs', () => {
      const calls = analyzer.extractNetworkCalls(
        'test.js',
        'fetch("https://api.example.com/data")',
        '.js',
      );
      assert.equal(calls.length, 1);
      assert.equal(calls[0]?.url, 'https://api.example.com/data');
    });

    it('ignores non-URL fetch arguments', () => {
      const calls = analyzer.extractNetworkCalls('test.js', 'fetch(someVariable)', '.js');
      assert.equal(calls.length, 0);
    });

    it('ignores non-http URLs', () => {
      const calls = analyzer.extractNetworkCalls('test.js', 'fetch("file:///etc/passwd")', '.js');
      assert.equal(calls.length, 0);
    });
  });

  describe('safe code', () => {
    it('produces no findings for clean code', () => {
      const code = `
        const add = (a: number, b: number) => a + b;
        console.log(add(1, 2));
        export default add;
      `;
      const findings = analyzer.analyze('test.ts', code, '.ts');
      // process.env access (INFO) might still fire from console.log,
      // but there should be no CRITICAL/WARNING findings
      const serious = findings.filter((f) => f.severity !== 'INFO');
      assert.equal(serious.length, 0);
    });
  });
});
