import fs from 'node:fs';
import { profilePaths, readJson } from './_lib.mjs';

// Actions
// - read: list/search/get message
// - draft: create/update draft
// - send: send mail / reply / forward

export function loadPolicy(profile) {
  const { cfgPath } = profilePaths(profile);
  const cfg = readJson(cfgPath);
  const policy = cfg.policy || { allow: ['read'], requireConfirm: ['send'] };
  return { cfg, policy };
}

export function assertAllowed(profile, action) {
  const { policy } = loadPolicy(profile);
  const allow = new Set(policy.allow || []);
  if (!allow.has(action)) {
    throw new Error(`Policy blocks action="${action}" for profile=${profile}. Update profile policy or re-run setup.`);
  }
}

export function needsConfirm(profile, action) {
  const { policy } = loadPolicy(profile);
  const req = new Set(policy.requireConfirm || []);
  return req.has(action);
}

export function writePolicy(profile, patch) {
  const { cfgPath } = profilePaths(profile);
  const cfg = readJson(cfgPath);
  cfg.policy = { ...(cfg.policy || {}), ...patch };
  fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 2) + '\n', 'utf8');
}
