import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, rmSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import {
  DEFAULT_ENTITIES,
  REJECT_WORDS,
  isValidEntity,
  loadEntitiesFromDb,
  addEntityToDb,
  mergeConfigEntities,
} from '../lib/entities.js';
import { ensureTables } from '../lib/sqlite.js';

test('isValidEntity: accepts valid known entity', () => {
  const entities = new Set(['kevin', 'config']);
  assert.equal(isValidEntity('kevin', entities), true);
});

test('isValidEntity: rejects unknown entity', () => {
  const entities = new Set(['kevin', 'config']);
  assert.equal(isValidEntity('unknown', entities), false);
});

test('isValidEntity: rejects empty string', () => {
  const entities = new Set(['kevin']);
  assert.equal(isValidEntity('', entities), false);
});

test('isValidEntity: rejects too long entity', () => {
  const entities = new Set(['kevin']);
  const longName = 'a'.repeat(61);
  assert.equal(isValidEntity(longName, entities), false);
});

test('isValidEntity: case insensitive matching', () => {
  const entities = new Set(['config']);
  assert.equal(isValidEntity('CONFIG', entities), true);
  assert.equal(isValidEntity('Config', entities), true);
  assert.equal(isValidEntity('config', entities), true);
});

test('isValidEntity: dotted path accepted when base is known', () => {
  const entities = new Set(['kevin']);
  assert.equal(isValidEntity('Kevin.preference', entities), true);
  assert.equal(isValidEntity('kevin.trading_build_mission', entities), true);
});

test('isValidEntity: PascalCase multi-word auto-accept', () => {
  const entities = new Set();
  assert.equal(isValidEntity('TradingSystem', entities), true);
  assert.equal(isValidEntity('MemoryPlugin', entities), true);
  assert.equal(isValidEntity('LilyMemory', entities), true);
});

test('isValidEntity: PascalCase single word rejected', () => {
  const entities = new Set();
  assert.equal(isValidEntity('Trading', entities), false);
  assert.equal(isValidEntity('Memory', entities), false);
});

test('isValidEntity: PascalCase must have lowercase after first uppercase', () => {
  const entities = new Set();
  assert.equal(isValidEntity('ALLCAPS', entities), false);
  assert.equal(isValidEntity('TestCase', entities), true);
});

test('isValidEntity: starts with uppercase then lowercase then uppercase', () => {
  const entities = new Set();
  assert.equal(isValidEntity('TestCase', entities), true);
  assert.equal(isValidEntity('TE', entities), false);
  assert.equal(isValidEntity('Te', entities), false);
});

test('isValidEntity: REJECT_WORDS - Still', () => {
  const entities = new Set();
  assert.equal(isValidEntity('Still', entities), false);
  assert.equal(isValidEntity('still', entities), false);
});

test('isValidEntity: REJECT_WORDS - Just', () => {
  const entities = new Set();
  assert.equal(isValidEntity('Just', entities), false);
});

test('isValidEntity: REJECT_WORDS - Also', () => {
  const entities = new Set();
  assert.equal(isValidEntity('Also', entities), false);
});

test('isValidEntity: REJECT_WORDS - Would', () => {
  const entities = new Set();
  assert.equal(isValidEntity('Would', entities), false);
});

test('isValidEntity: REJECT_WORDS - Each', () => {
  const entities = new Set();
  assert.equal(isValidEntity('Each', entities), false);
});

test('isValidEntity: starts with number rejected', () => {
  const entities = new Set();
  assert.equal(isValidEntity('123test', entities), false);
  assert.equal(isValidEntity('5entity', entities), false);
});

test('isValidEntity: starts with http rejected', () => {
  const entities = new Set();
  assert.equal(isValidEntity('http://example.com', entities), false);
  assert.equal(isValidEntity('https://test.com', entities), false);
  assert.equal(isValidEntity('HTTP', entities), false);
});

test('isValidEntity: runtime entities accepted', () => {
  const entities = new Set(['melanie', 'rose']);
  assert.equal(isValidEntity('melanie', entities), true);
  assert.equal(isValidEntity('Melanie', entities), true);
  assert.equal(isValidEntity('rose', entities), true);
});

test('isValidEntity: default entities always accepted', () => {
  const entities = new Set(['config', 'system', 'note', 'project']);
  assert.equal(isValidEntity('config', entities), true);
  assert.equal(isValidEntity('system', entities), true);
  assert.equal(isValidEntity('note', entities), true);
  assert.equal(isValidEntity('project', entities), true);
});

test('loadEntitiesFromDb: returns names from DB', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'entities-test-'));
  const dbPath = join(tmpDir, 'test.db');

  try {
    ensureTables(dbPath);
    addEntityToDb(dbPath, 'kevin', 'test');
    addEntityToDb(dbPath, 'lily', 'test');

    const entities = loadEntitiesFromDb(dbPath);
    assert.equal(entities.length, 2);
    assert.ok(entities.includes('kevin'));
    assert.ok(entities.includes('lily'));
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('loadEntitiesFromDb: returns empty array for empty table', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'entities-test-'));
  const dbPath = join(tmpDir, 'test.db');

  try {
    ensureTables(dbPath);
    const entities = loadEntitiesFromDb(dbPath);
    assert.equal(entities.length, 0);
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('addEntityToDb: inserts new entity successfully', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'entities-test-'));
  const dbPath = join(tmpDir, 'test.db');

  try {
    ensureTables(dbPath);
    const result = addEntityToDb(dbPath, 'kevin', 'runtime');
    assert.equal(result, true);

    const entities = loadEntitiesFromDb(dbPath);
    assert.equal(entities.length, 1);
    assert.equal(entities[0], 'kevin');
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('addEntityToDb: duplicate insert does not fail (OR IGNORE)', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'entities-test-'));
  const dbPath = join(tmpDir, 'test.db');

  try {
    ensureTables(dbPath);
    const result1 = addEntityToDb(dbPath, 'kevin', 'runtime');
    const result2 = addEntityToDb(dbPath, 'kevin', 'config');

    assert.equal(result1, true);
    assert.equal(result2, true);

    const entities = loadEntitiesFromDb(dbPath);
    assert.equal(entities.length, 1);
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('addEntityToDb: invalid name rejected - contains spaces', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'entities-test-'));
  const dbPath = join(tmpDir, 'test.db');

  try {
    ensureTables(dbPath);
    const result = addEntityToDb(dbPath, 'kevin smith', 'runtime');
    assert.equal(result, false);
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('addEntityToDb: invalid name rejected - special chars', () => {
  const tmpDir = mkdtempSync(join(tmpdir(), 'entities-test-'));
  const dbPath = join(tmpDir, 'test.db');

  try {
    ensureTables(dbPath);
    const result = addEntityToDb(dbPath, 'kevin@test', 'runtime');
    assert.equal(result, false);
  } finally {
    rmSync(tmpDir, { recursive: true, force: true });
  }
});

test('mergeConfigEntities: unions defaults + config + db, all lowercase, no duplicates', () => {
  const configEntities = ['Kevin', 'Lily', 'OpenClaw'];
  const dbEntities = ['lily', 'rose', 'christine'];

  const merged = mergeConfigEntities(configEntities, dbEntities);

  // Should include defaults
  assert.ok(merged.has('config'));
  assert.ok(merged.has('system'));
  assert.ok(merged.has('note'));
  assert.ok(merged.has('project'));

  // Should include config (lowercased)
  assert.ok(merged.has('kevin'));
  assert.ok(merged.has('lily'));
  assert.ok(merged.has('openclaw'));

  // Should include db
  assert.ok(merged.has('rose'));
  assert.ok(merged.has('christine'));

  // Should not have duplicates (lily appears in both config and db)
  const allValues = Array.from(merged);
  const lilyCount = allValues.filter(e => e === 'lily').length;
  assert.equal(lilyCount, 1);

  // Total unique count: 4 defaults + 3 config + 3 db - 1 overlap (lily) = 9
  assert.equal(merged.size, 9);
});
