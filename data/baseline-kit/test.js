import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { auditConfig, generateProfile, runCli } from './src/index.js';

const secure = JSON.parse(
  fs.readFileSync(new URL('./fixtures/secure-openclaw.json', import.meta.url), 'utf8')
);
const insecure = JSON.parse(
  fs.readFileSync(new URL('./fixtures/insecure-openclaw.json', import.meta.url), 'utf8')
);

const profile = generateProfile('enterprise');
assert.equal(profile.gateway.bind, '127.0.0.1');
assert.equal(profile.logging.audit, true);

const secureReport = auditConfig(secure, 'secure');
assert.equal(secureReport.summary.high, 0);

const insecureReport = auditConfig(insecure, 'insecure');
assert.equal(insecureReport.summary.high > 0, true);
assert.equal(insecureReport.findings.some((f) => f.id === 'NET_EXPOSURE'), true);

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'baseline-kit-'));
const generatedPath = path.join(tmpDir, 'openclaw.json');
const codeGenerate = await runCli(['generate', '--profile', 'team', '--out', generatedPath]);
assert.equal(codeGenerate, 0);
assert.equal(fs.existsSync(generatedPath), true);

const codeAudit = await runCli(['audit', '--config', generatedPath, '--format', 'json']);
assert.equal(codeAudit, 0);

const missingCode = await runCli(['audit', '--config', path.join(tmpDir, 'missing.json')]);
assert.equal(missingCode, 1);

console.log('baseline-kit tests passed');
