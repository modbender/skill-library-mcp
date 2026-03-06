import { getDb } from './db.js'; // For internal use, but actually di

/**
 * List all voice profiles.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @returns {Array} Array of profile objects.
 */
export function listProfiles(db) {
  return db.prepare('SELECT * FROM voice_profiles ORDER BY name').all();
}

/**
 * Add a new voice profile.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} name - Profile name.
 * @param {string} voiceId - ElevenLabs voice ID.
 * @param {string} [settingsJson='{}'] - JSON settings.
 * @throws {Error} If name exists or invalid JSON.
 */
export function addProfile(db, name, voiceId, settingsJson = '{}') {
  const existing = db.prepare('SELECT id FROM voice_profiles WHERE name = ?').get(name);
  if (existing) {
    throw new Error(`Profile ${name} already exists`);
  }
  let settings;
  try {
    settings = JSON.parse(settingsJson);
  } catch (e) {
    throw new Error('Invalid settings JSON');
  }
  const stmt = db.prepare('INSERT INTO voice_profiles (name, elevenlabs_voice_id, settings_json) VALUES (?, ?, ?)');
  stmt.run(name, voiceId, settingsJson);
}

/**
 * Set default voice profile.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @param {string} name - Profile name.
 * @throws {Error} If profile not found.
 */
export function setDefaultProfile(db, name) {
  const profile = db.prepare('SELECT id FROM voice_profiles WHERE name = ?').get(name);
  if (!profile) {
    throw new Error(`Profile ${name} not found`);
  }
  const upsertStmt = db.prepare('INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)');
  upsertStmt.run('default_voice_profile', name);
}

/**
 * Get the default voice profile name.
 * @param {import('better-sqlite3').Database} db - The database instance.
 * @returns {string|null} Default profile name or null.
 */
export function getDefaultProfile(db) {
  const row = db.prepare('SELECT value FROM config WHERE key = ?').get('default_voice_profile');
  return row ? row.value : null;
}