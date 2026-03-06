import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { installSkill, rollbackSkill, runCli, validatePolicyFile } from './src/index.js';

const tmpRoot = fs.mkdtempSync(path.join(os.tmpdir(), 'safe-install-'));
const storePath = path.join(tmpRoot, 'store');
const policyPath = path.join(tmpRoot, 'policy.json');

const policy = {
  defaultAction: 'allow',
  blockedPatterns: [],
  allowedSources: [],
  forceRequiredForAvoid: true
};
fs.writeFileSync(policyPath, JSON.stringify(policy, null, 2));

const safeSkill = new URL('./fixtures/safe-skill', import.meta.url).pathname;
const avoidSkill = new URL('./fixtures/avoid-skill', import.meta.url).pathname;
const cautionSkill = new URL('./fixtures/caution-skill', import.meta.url).pathname;

const safeResult = await installSkill(safeSkill, {
  config: policyPath,
  store: storePath,
  yes: true
});
assert.equal(safeResult.code, 0);
assert.equal(safeResult.data.install.skill, 'safe-skill-fixture');

const avoidBlocked = await installSkill(avoidSkill, {
  config: policyPath,
  store: storePath
});
assert.equal(avoidBlocked.code, 2);

const avoidForced = await installSkill(avoidSkill, {
  config: policyPath,
  store: storePath,
  force: true,
  yes: true
});
assert.equal(avoidForced.code, 0);

const cautionBlocked = await installSkill(cautionSkill, {
  config: policyPath,
  store: storePath
});
assert.equal(cautionBlocked.code, 2);

const cautionApproved = await installSkill(cautionSkill, {
  config: policyPath,
  store: storePath,
  yes: true
});
assert.equal(cautionApproved.code, 0);

const safeSkillV2 = path.join(tmpRoot, 'safe-skill-v2');
fs.cpSync(safeSkill, safeSkillV2, { recursive: true });
const pkgPath = path.join(safeSkillV2, 'package.json');
const pkg = JSON.parse(fs.readFileSync(pkgPath, 'utf8'));
pkg.version = '1.0.1';
fs.writeFileSync(pkgPath, JSON.stringify(pkg, null, 2));

const safeV2Install = await installSkill(safeSkillV2, {
  config: policyPath,
  store: storePath,
  yes: true
});
assert.equal(safeV2Install.code, 0);

const rollback = rollbackSkill('safe-skill-fixture', { store: storePath });
assert.equal(rollback.code, 0);

const policyValidation = validatePolicyFile(policyPath);
assert.equal(policyValidation.code, 0);

const missingPolicyValidation = validatePolicyFile(path.join(tmpRoot, 'missing-policy.json'));
assert.equal(missingPolicyValidation.code, 1);

const historyCode = await runCli(['history', '--format', 'json', '--store', storePath]);
assert.equal(historyCode, 0);

console.log('safe-install tests passed');
