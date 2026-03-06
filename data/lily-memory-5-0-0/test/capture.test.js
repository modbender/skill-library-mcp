import { describe, test, before, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import { ensureTables, sqliteQuery } from '../lib/sqlite.js';
import { captureFromMessages } from '../lib/capture.js';

const runtimeEntities = new Set(['kevin', 'config', 'system', 'note', 'project']);

function makeDb() {
  const dir = mkdtempSync(join(tmpdir(), 'capture-test-'));
  const dbPath = join(dir, 'test.db');
  ensureTables(dbPath);
  return { dbPath, dir };
}

function silentLogger() {
  // no-op logger to suppress output during tests
  return () => {};
}

describe('captureFromMessages', () => {
  test('captures fact from message with valid entity', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'user', content: 'Kevin prefers TypeScript for all new backend projects' }
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      assert.ok(result.stored >= 1, 'should store at least one fact');
      const rows = sqliteQuery(dbPath, "SELECT * FROM decisions WHERE entity = 'Kevin'");
      assert.ok(rows.length >= 1, 'should have a row for Kevin entity');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('assigns ttl_class=stable and importance=0.75 for user messages', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'user', content: 'Kevin prefers TypeScript for all new backend projects' }
      ];
      captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      const rows = sqliteQuery(dbPath, "SELECT ttl_class, importance FROM decisions WHERE entity = 'Kevin'");
      assert.ok(rows.length >= 1, 'should have a row');
      assert.equal(rows[0].ttl_class, 'stable');
      assert.equal(Number(rows[0].importance), 0.75);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('assigns ttl_class=active and importance=0.6 for assistant messages', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'assistant', content: 'The cache backend is configured as Redis for distributed session storage' }
      ];
      captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      const rows = sqliteQuery(dbPath, "SELECT ttl_class, importance FROM decisions WHERE entity = 'config'");
      assert.ok(rows.length >= 1, 'should have a row for config entity');
      assert.equal(rows[0].ttl_class, 'active');
      assert.equal(Number(rows[0].importance), 0.6);
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('updates existing fact when entity+key already exists', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages1 = [
        { role: 'user', content: 'Kevin prefers TypeScript for all new backend projects' }
      ];
      captureFromMessages(dbPath, messages1, 10, runtimeEntities, silentLogger());
      const rowsBefore = sqliteQuery(dbPath, "SELECT fact_value FROM decisions WHERE entity = 'Kevin' AND fact_key = 'preference'");
      assert.ok(rowsBefore.length >= 1, 'should have initial fact');

      // Now update with a different value for same entity+key
      const messages2 = [
        { role: 'user', content: 'Kevin prefers Go for all new backend services and systems' }
      ];
      captureFromMessages(dbPath, messages2, 10, runtimeEntities, silentLogger());
      const rowsAfter = sqliteQuery(dbPath, "SELECT fact_value FROM decisions WHERE entity = 'Kevin' AND fact_key = 'preference'");
      assert.equal(rowsAfter.length, 1, 'should still have exactly one fact (updated not duplicated)');
      assert.ok(rowsAfter[0].fact_value !== rowsBefore[0].fact_value, 'fact_value should have changed');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('respects maxCapture limit', () => {
    const { dbPath, dir } = makeDb();
    try {
      // Provide multiple messages each with extractable facts, limit to 1
      const messages = [
        { role: 'user', content: 'Kevin prefers TypeScript for all new backend projects' },
        { role: 'user', content: 'Note: always enable strict mode for TypeScript backend projects' },
        { role: 'user', content: 'project: preferred_language = TypeScript for all new backend work' }
      ];
      const result = captureFromMessages(dbPath, messages, 1, runtimeEntities, silentLogger());
      assert.equal(result.stored, 1, 'should store at most 1 fact');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('skips messages containing <lily-memory> injected context', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'user', content: '<lily-memory>Kevin prefers TypeScript for all new backend projects</lily-memory>' }
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      assert.equal(result.stored, 0, 'should skip injected context messages');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('skips messages shorter than 30 chars', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'user', content: 'Kevin prefers TS' } // 16 chars
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      assert.equal(result.stored, 0, 'should skip short messages');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('skips messages longer than 5000 chars', () => {
    const { dbPath, dir } = makeDb();
    try {
      const longText = 'Kevin prefers TypeScript. ' + 'x'.repeat(4976); // > 5000 chars
      const messages = [
        { role: 'user', content: longText }
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      assert.equal(result.stored, 0, 'should skip messages longer than 5000 chars');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('returns newDecisionIds for new insertions', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'user', content: 'Kevin prefers TypeScript for all new backend projects' }
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      assert.ok(result.newDecisionIds.length >= 1, 'should return newDecisionIds');
      const entry = result.newDecisionIds[0];
      assert.ok(typeof entry.id === 'string' && entry.id.length > 0, 'id should be a non-empty string');
      assert.ok(typeof entry.text === 'string' && entry.text.length > 0, 'text should be a non-empty string');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('returns stored count matching actual insertions', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        { role: 'user', content: 'Kevin prefers TypeScript for all new backend projects' },
        { role: 'assistant', content: 'The primary model is set to gemini-2.5-pro for inference tasks' }
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      const rows = sqliteQuery(dbPath, "SELECT id FROM decisions WHERE category = 'auto-capture'");
      assert.equal(result.stored, rows.length, 'stored count should match rows in DB');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });

  test('handles array content blocks in messages', () => {
    const { dbPath, dir } = makeDb();
    try {
      const messages = [
        {
          role: 'user',
          content: [
            { type: 'text', text: 'Kevin prefers TypeScript for all new backend projects' }
          ]
        }
      ];
      const result = captureFromMessages(dbPath, messages, 10, runtimeEntities, silentLogger());
      assert.ok(result.stored >= 1, 'should capture from array content blocks');
    } finally {
      rmSync(dir, { recursive: true, force: true });
    }
  });
});
