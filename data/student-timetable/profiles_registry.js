const fs = require('fs');
const path = require('path');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function normalizeToken(s) {
  return String(s || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

const GENERIC_ALIASES = new Set([
  'me', 'myself', 'self',
  'kid', 'child', 'son', 'daughter', 'boy', 'girl',
  'older', 'younger', 'big', 'small',
  'primary', 'secondary'
]);

const RESERVED_WORDS = new Set(['all', 'everyone']);

function loadProfilesRegistry(workspaceRoot) {
  const registryPath = path.join(workspaceRoot, 'schedules', 'profiles', 'registry.json');
  if (!fs.existsSync(registryPath)) {
    return { version: 1, dataRoot: 'schedules/profiles', profiles: [], _path: registryPath };
  }

  const data = readJson(registryPath);
  const profiles = Array.isArray(data && data.profiles) ? data.profiles : [];
  const version = typeof (data && data.version) === 'number' ? data.version : 1;
  const dataRoot = (data && data.dataRoot) ? String(data.dataRoot) : 'schedules/profiles';
  return { version, dataRoot, profiles, _path: registryPath };
}

function findSelfProfile(registry) {
  return (registry.profiles || []).find(p => p && p.type === 'self') || null;
}

function resolveProfile(registry, rawIdent, opts = {}) {
  const ident = normalizeToken(rawIdent);
  const allowDefaultToSelf = !!opts.allowDefaultToSelf;

  if (!ident) {
    if (allowDefaultToSelf) {
      const self = findSelfProfile(registry);
      if (self) {
        return { ok: true, profile: self, reason: 'default_to_self' };
      }
    }
    return { ok: false, reason: 'missing', candidates: registry.profiles || [] };
  }

  if (RESERVED_WORDS.has(ident)) {
    return { ok: false, reason: 'reserved', candidates: registry.profiles || [] };
  }

  if (GENERIC_ALIASES.has(ident)) {
    return { ok: false, reason: 'generic_alias', candidates: registry.profiles || [] };
  }

  const profiles = registry.profiles || [];

  const byId = profiles.filter(p => normalizeToken(p && p.profile_id) === ident);
  if (byId.length === 1) return { ok: true, profile: byId[0], reason: 'profile_id' };
  if (byId.length > 1) return { ok: false, reason: 'ambiguous', candidates: byId };

  const byName = profiles.filter(p => normalizeToken(p && p.display_name) === ident);
  if (byName.length === 1) return { ok: true, profile: byName[0], reason: 'display_name' };
  if (byName.length > 1) return { ok: false, reason: 'ambiguous', candidates: byName };

  const byAlias = profiles.filter(p => {
    const aliases = Array.isArray(p && p.aliases) ? p.aliases : [];
    return aliases.some(a => normalizeToken(a) === ident);
  });
  if (byAlias.length === 1) return { ok: true, profile: byAlias[0], reason: 'alias' };
  if (byAlias.length > 1) return { ok: false, reason: 'ambiguous', candidates: byAlias };

  return { ok: false, reason: 'unmatched', candidates: profiles };
}

function clarifyProfileMessage(result) {
  const candidates = (result && result.candidates) ? result.candidates : [];
  const names = candidates
    .map(p => {
      const disp = p && p.display_name ? String(p.display_name) : '';
      const id = p && p.profile_id ? String(p.profile_id) : '';
      if (disp && id && disp.toLowerCase() !== id.toLowerCase()) return `${disp} (${id})`;
      return disp || id;
    })
    .filter(Boolean);

  let hint = '';
  if (names.length) {
    hint = `Available profiles: ${names.join(', ')}.`;
  } else {
    hint = 'No profiles found in schedules/profiles/registry.json.';
  }

  if (result && result.reason === 'generic_alias') {
    return `Which profile did you mean? Generic aliases like "${String(result.input || '').trim()}" require clarification. ${hint}`;
  }

  if (result && result.reason === 'reserved') {
    return `"${String(result.input || '').trim()}" is reserved; please choose a specific profile. ${hint}`;
  }

  return `Which profile? Please pass --profile <id|name|alias>. ${hint}`;
}

module.exports = {
  loadProfilesRegistry,
  resolveProfile,
  clarifyProfileMessage,
  GENERIC_ALIASES,
  RESERVED_WORDS,
  normalizeToken
};
