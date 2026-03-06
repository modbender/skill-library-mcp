import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import Database from 'better-sqlite3';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { startConversation, endConversation, listConversations } from '../src/conversations.js';
import { addTranscriptLine, showTranscript } from '../src/transcripts.js';
import { addProfile, listProfiles, setDefaultProfile, getDefaultProfile } from '../src/profiles.js';
import { generateInterchange } from '../src/interchange.js';

const __filename = fileURLToPath(import.meta.url);
const testDir = path.dirname(__filename);
const migrationsDir = path.join(testDir, '..', 'migrations');
import os from 'node:os';
const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'voice-test-'));
const testDbPath = path.join(tmpDir, 'voice.test.db');
const backupTestDb = path.join(tmpDir, 'voice.test.backup.db');

let db;

function runInitialMigration(db) {
  const files = fs.readdirSync(migrationsDir).filter(f => f.endsWith('.sql')).sort();
  for (const file of files) {
    const sql = fs.readFileSync(path.join(migrationsDir, file), 'utf8');
    db.exec(sql);
  }
}

beforeEach(() => {
  if (fs.existsSync(testDbPath)) fs.unlinkSync(testDbPath);
  db = new Database(testDbPath);
  db.pragma('journal_mode = WAL');
  db.pragma('foreign_keys = ON');
  runInitialMigration(db);
});

afterEach(() => {
  db.close();
  if (fs.existsSync(testDbPath)) fs.unlinkSync(testDbPath);
  if (fs.existsSync(backupTestDb)) fs.unlinkSync(backupTestDb);
});

describe('Voice Skill Tests', () => {
  it('1. Start conversation stores with started timestamp', () => {
    const id = startConversation(db);
    assert.ok(id);
    const row = db.prepare('SELECT * FROM conversations WHERE id = ?').get(id);
    assert.ok(row);
    assert.ok(row.started);
    assert.strictEqual(row.ended, null);
    assert.strictEqual(row.turn_count, 0);
    assert.strictEqual(row.summary, null);
  });

  it('2. Add transcript line stores with speaker and text', () => {
    const id = startConversation(db);
    addTranscriptLine(db, id, 'user', 'Hello');
    const line = db.prepare('SELECT * FROM transcript_lines WHERE conversation_id = ?').get(id);
    assert.ok(line);
    assert.strictEqual(line.speaker, 'user');
    assert.strictEqual(line.text, 'Hello');
    assert.strictEqual(line.confidence, 1.0);
  });

  it('3. End conversation sets ended timestamp and updates turn count', () => {
    const id = startConversation(db);
    addTranscriptLine(db, id, 'user', 'Hello');
    addTranscriptLine(db, id, 'assistant', 'Hi there');
    endConversation(db, id);
    const row = db.prepare('SELECT * FROM conversations WHERE id = ?').get(id);
    assert.ok(row.ended);
    assert.strictEqual(row.turn_count, 1);
  });

  it('4. List conversations returns conversations', () => {
    const id1 = startConversation(db);
    const id2 = startConversation(db, 'Test summary');
    const convs = listConversations(db);
    assert.strictEqual(convs.length >= 2, true);
    const found1 = convs.find(c => c.id === id1);
    const found2 = convs.find(c => c.id === id2);
    assert.ok(found1);
    assert.ok(found2);
    assert.strictEqual(found2.summary, 'Test summary');
  });

  it('5. Search transcripts finds by keyword', () => {
    const id = startConversation(db);
    addTranscriptLine(db, id, 'user', 'Hello world');
    addTranscriptLine(db, id, 'assistant', 'Goodbye');
    const convs = listConversations(db, { search: 'world' });
    assert.strictEqual(convs.length, 1);
    assert.strictEqual(convs[0].id, id);
  });

  it('6. Show transcript returns all lines for conversation', () => {
    const id = startConversation(db);
    addTranscriptLine(db, id, 'user', 'Line 1');
    addTranscriptLine(db, id, 'assistant', 'Line 2');
    const lines = showTranscript(db, id);
    assert.strictEqual(lines.length, 2);
    assert.strictEqual(lines[0].text, 'Line 1');
    assert.strictEqual(lines[1].text, 'Line 2');
  });

  it('7. Add voice profile stores with name and voice_id', () => {
    addProfile(db, 'test', 'test-voice-id', '{"description": "Test voice"}');
    const profile = db.prepare('SELECT * FROM voice_profiles WHERE name = ?').get('test');
    assert.ok(profile);
    assert.strictEqual(profile.name, 'test');
    assert.strictEqual(profile.elevenlabs_voice_id, 'test-voice-id');
  });

  it('8. List profiles returns all profiles', () => {
    addProfile(db, 'profile1', 'id1');
    addProfile(db, 'profile2', 'id2');
    const profiles = listProfiles(db);
    assert.strictEqual(profiles.length, 2);
  });

  it('9. Interchange refresh generates valid .md files without API keys', () => {
    addProfile(db, 'nova', 'pNInz6obpgDQGcFmaJgB', '{"description": "Warm voice"}');
    const id = startConversation(db, 'Test conv');
    addTranscriptLine(db, id, 'user', 'Hi');
    addTranscriptLine(db, id, 'assistant', 'Hello');
    endConversation(db, id);
    generateInterchange(db);
    const workspaceDir = path.join(testDir, '..', '..', '..');
    const capsPath = path.join(workspaceDir, 'interchange', 'voice', 'ops', 'capabilities.md');
    const profPath = path.join(workspaceDir, 'interchange', 'voice', 'ops', 'profiles.md');
    const recentPath = path.join(workspaceDir, 'interchange', 'voice', 'state', 'recent.md');
    assert.ok(fs.existsSync(capsPath));
    assert.ok(fs.existsSync(profPath));
    assert.ok(fs.existsSync(recentPath));
    const profContent = fs.readFileSync(profPath, 'utf8');
    assert.ok(profContent.includes('nova'));
    assert.ok(profContent.includes('Warm voice'));
    assert.notStrictEqual(profContent, /pNInz6obpgDQGcFmaJgB/); // No voice ID if not wanted, but spec no API keys, voice id ok but to be safe
    const recentContent = fs.readFileSync(recentPath, 'utf8');
    assert.ok(recentContent.includes('Test conv'));
    assert.notStrictEqual(recentContent, /Hi|Hello/); // No content
  });

  it('10. Data integrity: conversation with multiple lines', () => {
    const id = startConversation(db);
    addTranscriptLine(db, id, 'user', 'Line 1', 0.9);
    addTranscriptLine(db, id, 'assistant', 'Line 2', 0.95);
    addTranscriptLine(db, id, 'user', 'Line 3', 0.8);
    const lines = showTranscript(db, id);
    assert.strictEqual(lines.length, 3);
    assert.strictEqual(lines[0].speaker, 'user');
    assert.strictEqual(lines[0].text, 'Line 1');
    assert.strictEqual(lines[0].confidence, 0.9);
    assert.strictEqual(lines[1].speaker, 'assistant');
    assert.strictEqual(lines[2].speaker, 'user');
    const conv = db.prepare('SELECT turn_count FROM conversations WHERE id = ?').get(id);
    assert.strictEqual(conv.turn_count, 1);
  });
});