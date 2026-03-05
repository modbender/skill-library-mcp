import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { MetadataAnalyzer } from '../analyzers/metadata-analyzer.js';
import { VettingConfig, SkillManifest } from '../types.js';

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
  typosquatTargets: ['hello-world', 'lodash', 'express'],
};

describe('MetadataAnalyzer', () => {
  const analyzer = new MetadataAnalyzer();

  describe('author validation', () => {
    it('flags missing author when required', () => {
      const manifest: SkillManifest = { name: 'test', version: '1.0.0' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      assert.ok(findings.some((f) => f.message.includes('author')));
    });

    it('does not flag present author', () => {
      const manifest: SkillManifest = { name: 'test', version: '1.0.0', author: 'valid-author' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const authorFindings = findings.filter((f) => f.message.includes('author'));
      assert.equal(authorFindings.length, 0);
    });

    it('flags blocked authors', () => {
      const config = { ...BASE_CONFIG, blockedAuthors: ['evil-author'] };
      const manifest: SkillManifest = { name: 'test', version: '1.0.0', author: 'evil-author' };
      const findings = analyzer.analyze(manifest, '/test', config);
      assert.ok(findings.some((f) => f.severity === 'CRITICAL' && f.message.includes('blocked')));
    });

    it('matches blocked authors case-insensitively', () => {
      const config = { ...BASE_CONFIG, blockedAuthors: ['Evil-Author'] };
      const manifest: SkillManifest = { name: 'test', version: '1.0.0', author: 'evil-author' };
      const findings = analyzer.analyze(manifest, '/test', config);
      assert.ok(findings.some((f) => f.severity === 'CRITICAL'));
    });
  });

  describe('typosquatting detection', () => {
    it('detects names 1 edit away (CRITICAL)', () => {
      const manifest: SkillManifest = { name: 'helo-world', version: '1.0.0', author: 'x' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const typos = findings.filter((f) => f.category === 'TYPO_SQUATTING');
      assert.ok(typos.some((f) => f.severity === 'CRITICAL'));
    });

    it('detects names 2 edits away (WARNING)', () => {
      const manifest: SkillManifest = { name: 'helo-wrld', version: '1.0.0', author: 'x' };
      const config = { ...BASE_CONFIG, typosquatTargets: ['hello-wrld'] };
      // 'helo-wrld' vs 'hello-wrld' = 1 edit
      const findings = analyzer.analyze(manifest, '/test', config);
      const typos = findings.filter((f) => f.category === 'TYPO_SQUATTING');
      assert.ok(typos.length > 0);
    });

    it('does not flag exact matches', () => {
      const manifest: SkillManifest = { name: 'hello-world', version: '1.0.0', author: 'x' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const typos = findings.filter((f) => f.category === 'TYPO_SQUATTING');
      assert.equal(typos.length, 0);
    });

    it('does not flag distant names', () => {
      const manifest: SkillManifest = { name: 'totally-different', version: '1.0.0', author: 'x' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const typos = findings.filter((f) => f.category === 'TYPO_SQUATTING');
      assert.equal(typos.length, 0);
    });
  });

  describe('dangerous permissions', () => {
    it('flags shell:exec permission', () => {
      const manifest: SkillManifest = {
        name: 'test', version: '1.0.0', author: 'x',
        permissions: ['shell:exec'],
      };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      assert.ok(findings.some((f) => f.message.includes('shell:exec')));
    });

    it('flags credentials:read permission', () => {
      const manifest: SkillManifest = {
        name: 'test', version: '1.0.0', author: 'x',
        permissions: ['credentials:read'],
      };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      assert.ok(findings.some((f) => f.message.includes('credentials:read')));
    });

    it('does not flag safe permissions', () => {
      const manifest: SkillManifest = {
        name: 'test', version: '1.0.0', author: 'x',
        permissions: ['filesystem:read'],
      };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const permFindings = findings.filter((f) => f.message.includes('dangerous permission'));
      assert.equal(permFindings.length, 0);
    });
  });

  describe('version format', () => {
    it('accepts standard semver', () => {
      const manifest: SkillManifest = { name: 'test', version: '1.2.3', author: 'x' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const versionFindings = findings.filter((f) => f.message.includes('version'));
      assert.equal(versionFindings.length, 0);
    });

    it('accepts semver with pre-release', () => {
      const manifest: SkillManifest = { name: 'test', version: '1.0.0-beta.1', author: 'x' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      const versionFindings = findings.filter((f) => f.message.includes('version'));
      assert.equal(versionFindings.length, 0);
    });

    it('flags non-standard version format', () => {
      const manifest: SkillManifest = { name: 'test', version: 'latest', author: 'x' };
      const findings = analyzer.analyze(manifest, '/test', BASE_CONFIG);
      assert.ok(findings.some((f) => f.message.includes('version')));
    });
  });
});
