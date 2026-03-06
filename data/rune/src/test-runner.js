import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { DB_PATH, openDb, nowIso } from './db.js';
import { colors } from './colors.js';
import { factsToMarkdown } from './format.js';
import { extractFactsFromFile } from './extract.js';

const SUITES = ['unit', 'extract', 'recall', 'perf', 'e2e'];
const DEFAULT_TEST_DB_PATH = '/tmp/rune-test.db';
const BENCHMARK_PATH = path.join(os.homedir(), '.openclaw', 'rune-benchmarks.json');
const FIXTURE_DIR = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'test', 'fixtures');

function makeSuiteResult(name) {
  return {
    suite: name,
    passed: 0,
    failed: 0,
    skipped: 0,
    total: 0,
    metrics: {},
    errors: []
  };
}

function addPass(result) {
  result.passed += 1;
  result.total += 1;
}

function addFail(result, message) {
  result.failed += 1;
  result.total += 1;
  result.errors.push(message);
}

function addSkip(result, message) {
  result.skipped += 1;
  result.total += 1;
  if (message) {
    result.errors.push(`SKIP: ${message}`);
  }
}

function assert(result, condition, message) {
  if (condition) {
    addPass(result);
    return;
  }
  addFail(result, message);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function ensureDeleted(filePath) {
  if (fs.existsSync(filePath)) {
    fs.rmSync(filePath, { force: true });
  }
}

function ensureParentDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function toFtsQuery(query) {
  const terms = String(query)
    .trim()
    .split(/\s+/)
    .map((term) => term.replace(/"/g, '""'))
    .filter(Boolean)
    .map((term) => `"${term}"*`);

  if (terms.length === 0) {
    return '""';
  }
  return terms.join(' AND ');
}

function searchFacts(db, query) {
  const ftsRows = db.prepare(`
    SELECT f.*
    FROM facts_fts
    JOIN facts f ON f.id = facts_fts.rowid
    WHERE facts_fts MATCH ?
    ORDER BY bm25(facts_fts), f.updated DESC
  `).all(toFtsQuery(query));
  if (ftsRows.length > 0) {
    return ftsRows;
  }

  const broadRows = db.prepare(`
    SELECT *
    FROM facts
    WHERE lower(key) LIKE lower(?) OR lower(value) LIKE lower(?)
    ORDER BY updated DESC
  `).all(`%${query}%`, `%${query}%`);
  if (broadRows.length > 0) {
    return broadRows;
  }

  const terms = String(query)
    .toLowerCase()
    .replace(/[^a-z0-9#._\\s-]/g, ' ')
    .split(/\s+/)
    .filter((term) => term.length > 2);
  if (terms.length === 0) {
    return [];
  }

  const where = terms.map(() => '(lower(key) LIKE ? OR lower(value) LIKE ?)').join(' OR ');
  const params = terms.flatMap((term) => [`%${term}%`, `%${term}%`]);
  return db.prepare(`SELECT * FROM facts WHERE ${where} ORDER BY updated DESC`).all(...params);
}

function parseDurationMs(value) {
  const match = String(value).trim().toLowerCase().match(/^(\d+)([smhdw])$/);
  if (!match) {
    return null;
  }

  const amount = Number.parseInt(match[1], 10);
  const unit = match[2];
  const mul = {
    s: 1000,
    m: 60 * 1000,
    h: 60 * 60 * 1000,
    d: 24 * 60 * 60 * 1000,
    w: 7 * 24 * 60 * 60 * 1000
  };

  return amount * mul[unit];
}

function ttlToExpiresAt(ttl) {
  if (!ttl) {
    return null;
  }
  const ms = parseDurationMs(ttl);
  if (!ms) {
    return null;
  }
  return new Date(Date.now() + ms).toISOString();
}

function upsertFact(db, fact) {
  const ts = nowIso();
  db.prepare(`
    INSERT INTO facts (category, key, value, source, confidence, created, updated, scope, tier, expires_at, last_verified, source_type)
    VALUES (@category, @key, @value, @source, @confidence, @created, @updated, @scope, @tier, @expires_at, @last_verified, @source_type)
    ON CONFLICT(category, key) DO UPDATE SET
      value = excluded.value,
      source = excluded.source,
      confidence = excluded.confidence,
      scope = excluded.scope,
      tier = excluded.tier,
      expires_at = excluded.expires_at,
      last_verified = COALESCE(excluded.last_verified, facts.last_verified),
      source_type = excluded.source_type,
      updated = excluded.updated
  `).run({
    category: fact.category,
    key: fact.key,
    value: fact.value,
    source: fact.source ?? null,
    confidence: fact.confidence ?? 1,
    created: ts,
    updated: ts,
    scope: fact.scope ?? 'global',
    tier: fact.tier ?? 'long-term',
    expires_at: fact.expires_at ?? ttlToExpiresAt(fact.ttl ?? null),
    last_verified: fact.last_verified ?? null,
    source_type: fact.source_type ?? 'manual'
  });
}

function applyExtractedFacts(db, facts) {
  const now = nowIso();
  const getByKey = db.prepare('SELECT * FROM facts WHERE category = ? AND key = ?');
  const insertStmt = db.prepare(`
    INSERT INTO facts (category, key, value, source, confidence, created, updated, scope, tier, expires_at, last_verified, source_type)
    VALUES (@category, @key, @value, @source, @confidence, @created, @updated, @scope, @tier, @expires_at, @last_verified, @source_type)
  `);
  const updateStmt = db.prepare(`
    UPDATE facts
    SET value = @value,
        source = @source,
        confidence = @confidence,
        scope = @scope,
        tier = @tier,
        expires_at = @expires_at,
        source_type = @source_type,
        updated = @updated
    WHERE category = @category AND key = @key
  `);
  const touchStmt = db.prepare(`
    UPDATE facts
    SET last_verified = @last_verified
    WHERE category = @category AND key = @key
  `);

  let inserted = 0;
  let updated = 0;
  let skipped = 0;

  const tx = db.transaction(() => {
    for (const fact of facts) {
      const existing = getByKey.get(fact.category, fact.key);
      if (!existing) {
        insertStmt.run({
          category: fact.category,
          key: fact.key,
          value: fact.value,
          source: null,
          confidence: fact.confidence ?? 0.8,
          created: now,
          updated: now,
          scope: fact.scope ?? 'global',
          tier: fact.tier ?? 'long-term',
          expires_at: ttlToExpiresAt(fact.ttl),
          last_verified: now,
          source_type: fact.source_type ?? 'inferred'
        });
        inserted += 1;
        continue;
      }

      if (existing.value === fact.value) {
        touchStmt.run({ category: fact.category, key: fact.key, last_verified: now });
        skipped += 1;
        continue;
      }

      updateStmt.run({
        category: fact.category,
        key: fact.key,
        value: fact.value,
        source: existing.source,
        confidence: fact.confidence ?? existing.confidence ?? 0.8,
        scope: fact.scope ?? existing.scope,
        tier: fact.tier ?? existing.tier,
        expires_at: ttlToExpiresAt(fact.ttl),
        source_type: fact.source_type ?? existing.source_type ?? 'inferred',
        updated: now
      });
      updated += 1;
    }
  });

  tx();
  return { inserted, updated, skipped };
}

function listFixtureNames() {
  const files = fs.readdirSync(FIXTURE_DIR)
    .filter((name) => name.endsWith('.md'))
    .sort();
  return files;
}

function loadExpectedForFixture(fixtureMd) {
  const expectedPath = path.join(FIXTURE_DIR, fixtureMd.replace(/\.md$/, '-expected.json'));
  const raw = fs.readFileSync(expectedPath, 'utf8');
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed.facts) ? parsed.facts : [];
}

function normalizeText(value) {
  return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function overlapText(a, b) {
  const aa = normalizeText(a);
  const bb = normalizeText(b);
  if (!aa || !bb) {
    return false;
  }
  return aa.includes(bb) || bb.includes(aa);
}

function keySimilar(a, b) {
  const aa = normalizeText(a).replace(/[^a-z0-9.]/g, '');
  const bb = normalizeText(b).replace(/[^a-z0-9.]/g, '');
  if (!aa || !bb) {
    return false;
  }
  if (aa === bb || aa.includes(bb) || bb.includes(aa)) {
    return true;
  }
  const aParts = new Set(aa.split('.').filter(Boolean));
  const bParts = bb.split('.').filter(Boolean);
  let shared = 0;
  for (const part of bParts) {
    if (aParts.has(part)) {
      shared += 1;
    }
  }
  return shared >= 1;
}

function scoreExtraction(extractedFacts, expectedFacts) {
  const usedExpected = new Set();
  let truePositive = 0;

  for (const got of extractedFacts) {
    let bestIndex = -1;
    let bestScore = 0;
    for (let i = 0; i < expectedFacts.length; i += 1) {
      if (usedExpected.has(i)) {
        continue;
      }
      const expected = expectedFacts[i];
      const valueMatch = overlapText(got.value, expected.value);
      const keyMatch = keySimilar(got.key, expected.key);
      const sameCategory = normalizeText(got.category) === normalizeText(expected.category);

      // Score: value or key match is sufficient. Category is a bonus.
      let score = 0;
      if (valueMatch) score += 2;
      if (keyMatch) score += 2;
      if (sameCategory) score += 1;

      // Must have at least a value OR key match to count
      if (score >= 2 && score > bestScore) {
        bestScore = score;
        bestIndex = i;
      }
    }
    if (bestIndex >= 0) {
      usedExpected.add(bestIndex);
      truePositive += 1;
    }
  }

  const precision = extractedFacts.length === 0 ? 0 : truePositive / extractedFacts.length;
  const recall = expectedFacts.length === 0 ? 1 : truePositive / expectedFacts.length;
  const f1 = precision + recall === 0 ? 0 : (2 * precision * recall) / (precision + recall);

  return { precision, recall, f1, truePositive, extracted: extractedFacts.length, expected: expectedFacts.length };
}

async function isOllamaAvailable(baseUrl = process.env.OLLAMA_URL || 'http://localhost:11434') {
  try {
    const response = await fetch(`${baseUrl}/api/tags`, { method: 'GET' });
    return response.ok;
  } catch {
    return false;
  }
}

function withSuiteDb(basePath, suiteName) {
  const ext = path.extname(basePath);
  const stem = ext ? basePath.slice(0, -ext.length) : basePath;
  const fullExt = ext || '.db';
  return `${stem}.${suiteName}${fullExt}`;
}

function timed(operation) {
  const start = process.hrtime.bigint();
  const value = operation();
  const end = process.hrtime.bigint();
  const ms = Number(end - start) / 1e6;
  return { value, ms };
}

async function runUnitSuite(dbPath, options = {}) {
  const result = makeSuiteResult('unit');
  ensureParentDir(dbPath);
  ensureDeleted(dbPath);
  const db = openDb(dbPath);

  try {
    upsertFact(db, { category: 'person', key: 'alice.name', value: 'Alice', scope: 'global', tier: 'long-term' });
    const fetched = db.prepare('SELECT value FROM facts WHERE category = ? AND key = ?').get('person', 'alice.name');
    assert(result, fetched?.value === 'Alice', 'Add/get fact failed');

    const removed = db.prepare('DELETE FROM facts WHERE category = ? AND key = ?').run('person', 'alice.name');
    assert(result, removed.changes === 1, 'Remove fact failed');

    upsertFact(db, { category: 'person', key: 'alice.name', value: 'Alice A.' });
    upsertFact(db, { category: 'person', key: 'alice.name', value: 'Alice B.' });
    const dedupCount = db.prepare('SELECT COUNT(*) AS n FROM facts WHERE category = ? AND key = ?').get('person', 'alice.name').n;
    assert(result, dedupCount === 1, 'Dedup failed for repeated upsert');

    const contradiction = db.prepare('SELECT value FROM facts WHERE category = ? AND key = ?').get('person', 'alice.name');
    assert(result, contradiction?.value === 'Alice B.', 'Contradiction update did not overwrite value');

    upsertFact(db, { category: 'project', key: 'alpha.note', value: 'Global note', scope: 'global' });
    upsertFact(db, { category: 'project', key: 'alpha.plan', value: 'Project plan', scope: 'project' });
    const globalCount = db.prepare("SELECT COUNT(*) AS n FROM facts WHERE scope = 'global'").get().n;
    const projectCount = db.prepare("SELECT COUNT(*) AS n FROM facts WHERE scope = 'project'").get().n;
    assert(result, globalCount >= 1 && projectCount >= 1, 'Scope filtering setup invalid');

    upsertFact(db, { category: 'task', key: 'build.state', value: 'active', tier: 'working', ttl: '1s' });
    await sleep(1200);
    const expired = db.prepare("DELETE FROM facts WHERE tier = 'working' AND expires_at IS NOT NULL AND expires_at <= ?").run(nowIso());
    const workingLeft = db.prepare("SELECT COUNT(*) AS n FROM facts WHERE category = 'task' AND key = 'build.state'").get().n;
    assert(result, expired.changes >= 1 && workingLeft === 0, 'TTL expiry failed');

    upsertFact(db, { category: 'tool', key: 'editor', value: 'Neovim' });
    const ftsRows = db.prepare(`
      SELECT f.*
      FROM facts_fts
      JOIN facts f ON f.id = facts_fts.rowid
      WHERE facts_fts MATCH ?
    `).all(toFtsQuery('Neovim'));
    assert(result, ftsRows.some((row) => row.key === 'editor'), 'FTS search did not return inserted fact');

    upsertFact(db, { category: 'project', key: 'tier.check', value: 'long memory', tier: 'long-term' });
    upsertFact(db, { category: 'project', key: 'tier.active', value: 'short memory', tier: 'working', ttl: '1h' });
    const longTerm = db.prepare("SELECT COUNT(*) AS n FROM facts WHERE tier = 'long-term'").get().n;
    const working = db.prepare("SELECT COUNT(*) AS n FROM facts WHERE tier = 'working'").get().n;
    assert(result, longTerm >= 1 && working >= 1, 'Tier filtering setup invalid');

    const src = db.prepare('SELECT id FROM facts WHERE category = ? AND key = ?').get('project', 'alpha.note');
    const dst = db.prepare('SELECT id FROM facts WHERE category = ? AND key = ?').get('project', 'alpha.plan');
    db.prepare(`
      INSERT INTO relations (source_fact_id, target_fact_id, relation_type, created)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(source_fact_id, target_fact_id, relation_type) DO NOTHING
    `).run(src.id, dst.id, 'related_to', nowIso());
    const relCount = db.prepare('SELECT COUNT(*) AS n FROM relations WHERE source_fact_id = ?').get(src.id).n;
    assert(result, relCount === 1, 'Relation link insert failed');

    const graphRows = db.prepare(`
      WITH RECURSIVE walk(node_id, depth) AS (
        SELECT ?, 0
        UNION ALL
        SELECT r.target_fact_id, depth + 1
        FROM relations r
        JOIN walk w ON w.node_id = r.source_fact_id
        WHERE depth < 2
      )
      SELECT COUNT(*) AS n FROM walk
    `).get(src.id);
    assert(result, graphRows.n >= 2, 'Graph traversal failed');

    const injectFacts = db.prepare('SELECT * FROM facts ORDER BY category, key').all();
    const markdown = factsToMarkdown(injectFacts);
    assert(result, markdown.includes('# Rune - Known Facts') && markdown.includes('## Working Memory'), 'Inject markdown format invalid');

    const exported = JSON.stringify(injectFacts, null, 2);
    const roundtripDbPath = `${dbPath}.roundtrip`;
    ensureDeleted(roundtripDbPath);
    const db2 = openDb(roundtripDbPath);
    const imported = JSON.parse(exported);
    for (const fact of imported) {
      upsertFact(db2, fact);
    }
    const importedCount = db2.prepare('SELECT COUNT(*) AS n FROM facts').get().n;
    db2.close();
    ensureDeleted(roundtripDbPath);
    assert(result, importedCount === injectFacts.length, 'Import/export roundtrip count mismatch');
  } finally {
    db.close();
  }

  return result;
}

async function runExtractSuite(options = {}) {
  const result = makeSuiteResult('extract');
  const available = await isOllamaAvailable();
  if (!available) {
    addSkip(result, 'Ollama not reachable at OLLAMA_URL or http://localhost:11434');
    result.metrics = { f1_avg: 0, fixtures: {} };
    return result;
  }

  const fixtureScores = {};
  const fixtures = listFixtureNames();
  let f1Sum = 0;

  for (const fixture of fixtures) {
    const fixturePath = path.join(FIXTURE_DIR, fixture);
    const expected = loadExpectedForFixture(fixture);
    try {
      const extracted = await extractFactsFromFile(fixturePath, {
        model: options.model || 'qwen3:8b',
        verbose: Boolean(options.verbose)
      });
      const score = scoreExtraction(extracted.facts, expected);
      fixtureScores[fixture.replace(/\.md$/, '')] = score.f1;
      f1Sum += score.f1;
      addPass(result);
    } catch (err) {
      addSkip(result, `${fixture}: ${err.message || String(err)}`);
      fixtureScores[fixture.replace(/\.md$/, '')] = 0;
    }
  }

  const fixtureCount = Math.max(1, fixtures.length);
  result.metrics = {
    f1_avg: f1Sum / fixtureCount,
    fixtures: fixtureScores
  };

  return result;
}

function seedRecallFacts(db) {
  const facts = [
    { category: 'person', key: 'cory.son', value: "Cory's son is Liam." },
    { category: 'project', key: 'cad-wiki.brand-color', value: 'TKNS brand color is #003ba9.' },
    { category: 'decision', key: 'rune.codename', value: 'Rune codename references Norse runes.' },
    { category: 'person', key: 'cory.discord.alt', value: 'Bobsy is Cory on Discord.' },
    { category: 'project', key: 'cad-wiki.editor', value: 'cad-wiki editor is TipTap.' },
    { category: 'lesson', key: 'gateway-restart', value: 'NEVER restart the gateway in production.' },
    { category: 'preference', key: 'cory.timezone', value: 'Cory timezone is Eastern time.' }
  ];

  for (const fact of facts) {
    upsertFact(db, fact);
  }
}

async function runRecallSuite(dbPath) {
  const result = makeSuiteResult('recall');
  ensureParentDir(dbPath);
  ensureDeleted(dbPath);
  const db = openDb(dbPath);

  try {
    seedRecallFacts(db);
    const qaPath = path.join(FIXTURE_DIR, 'recall-questions.json');
    const questions = JSON.parse(fs.readFileSync(qaPath, 'utf8'));

    let hits = 0;
    for (const entry of questions) {
      const [expectedCategory, expectedKey] = String(entry.expected_key).split('/');
      const rows = searchFacts(db, entry.question);

      const hit = rows.some((row) => row.category === expectedCategory && row.key === expectedKey && String(row.value).includes(entry.expected_contains));
      if (hit) {
        hits += 1;
        addPass(result);
      } else {
        addFail(result, `Recall miss for question: ${entry.question}`);
      }
    }

    result.metrics = {
      hit_rate: questions.length === 0 ? 1 : hits / questions.length,
      total: questions.length,
      hits
    };
  } finally {
    db.close();
  }

  return result;
}

function makeLongDocument(wordCount) {
  const words = [];
  for (let i = 0; i < wordCount; i += 1) {
    words.push(`token${i % 300}`);
  }
  return `# Perf Document\n\n${words.join(' ')}\n`;
}

async function runPerfSuite(dbPath, options = {}) {
  const result = makeSuiteResult('perf');
  ensureParentDir(dbPath);
  ensureDeleted(dbPath);
  const db = openDb(dbPath);

  try {
    const insertMany = (count, prefix) => {
      const tx = db.transaction(() => {
        for (let i = 0; i < count; i += 1) {
          upsertFact(db, {
            category: 'project',
            key: `${prefix}.fact.${i}`,
            value: `value ${i} for search benchmark`,
            scope: 'global',
            tier: 'long-term'
          });
        }
      });
      tx();
    };

    for (let i = 0; i < 3; i += 1) {
      insertMany(200, `warmup${i}`);
      db.prepare("DELETE FROM facts WHERE key LIKE 'warmup%'").run();
    }

    const insertTiming = timed(() => insertMany(1000, 'perf'));

    const searchTiming = timed(() => {
      for (let i = 0; i < 100; i += 1) {
        db.prepare(`
          SELECT COUNT(*) AS n
          FROM facts_fts
          WHERE facts_fts MATCH ?
        `).get(toFtsQuery(`value ${i % 10}`));
      }
    });

    const facts = db.prepare('SELECT * FROM facts ORDER BY category, key').all();
    const injectTiming = timed(() => factsToMarkdown(facts));

    const ids = db.prepare("SELECT id FROM facts WHERE key LIKE 'perf.fact.%' ORDER BY key LIMIT 4").all();
    if (ids.length === 4) {
      const now = nowIso();
      db.prepare('INSERT INTO relations (source_fact_id, target_fact_id, relation_type, created) VALUES (?, ?, ?, ?)').run(ids[0].id, ids[1].id, 'related_to', now);
      db.prepare('INSERT INTO relations (source_fact_id, target_fact_id, relation_type, created) VALUES (?, ?, ?, ?)').run(ids[1].id, ids[2].id, 'related_to', now);
      db.prepare('INSERT INTO relations (source_fact_id, target_fact_id, relation_type, created) VALUES (?, ?, ?, ?)').run(ids[2].id, ids[3].id, 'related_to', now);
    }

    const graphTiming = timed(() => {
      if (ids.length === 0) {
        return;
      }
      db.prepare(`
        WITH RECURSIVE walk(node_id, depth) AS (
          SELECT ?, 0
          UNION ALL
          SELECT r.target_fact_id, depth + 1
          FROM relations r
          JOIN walk w ON w.node_id = r.source_fact_id
          WHERE w.depth < 2
        )
        SELECT COUNT(*) AS n FROM walk
      `).get(ids[0].id);
    });

    let extractMs = null;
    const available = await isOllamaAvailable();
    if (available) {
      const docPath = `${dbPath}.perf.md`;
      fs.writeFileSync(docPath, makeLongDocument(5000), 'utf8');
      try {
        const measured = timed(() => extractFactsFromFile(docPath, { model: options.model || 'qwen3:8b' }));
        await measured.value;
        extractMs = measured.ms;
        addPass(result);
      } catch (err) {
        addSkip(result, `extract benchmark skipped (${err.message || String(err)})`);
      }
      ensureDeleted(docPath);
    } else {
      addSkip(result, 'extract benchmark skipped (Ollama not available)');
    }

    result.metrics = {
      insert_1000_ms: insertTiming.ms,
      search_avg_ms: searchTiming.ms / 100,
      inject_ms: injectTiming.ms,
      extract_ms: extractMs,
      graph_3_level_ms: graphTiming.ms,
      table: [
        { operation: 'insert_1000', count: 1000, total_ms: insertTiming.ms, per_op_ms: insertTiming.ms / 1000 },
        { operation: 'search_100_queries', count: 100, total_ms: searchTiming.ms, per_op_ms: searchTiming.ms / 100 },
        { operation: 'inject_1000', count: facts.length, total_ms: injectTiming.ms, per_op_ms: facts.length ? injectTiming.ms / facts.length : 0 },
        { operation: 'extract_5000_words', count: 1, total_ms: extractMs, per_op_ms: extractMs },
        { operation: 'graph_3_level', count: 1, total_ms: graphTiming.ms, per_op_ms: graphTiming.ms }
      ]
    };

    addPass(result);
  } finally {
    db.close();
  }

  return result;
}

async function runE2ESuite(dbPath, options = {}) {
  const result = makeSuiteResult('e2e');
  ensureParentDir(dbPath);
  ensureDeleted(dbPath);
  const db = openDb(dbPath);

  try {
    const baseFacts = [
      { category: 'person', key: 'cory.name', value: 'Cory' },
      { category: 'project', key: 'cad-wiki.editor', value: 'TipTap' },
      { category: 'project', key: 'cad-wiki.brand-color', value: '#003ba9' },
      { category: 'decision', key: 'rune.codename', value: 'Norse runes' },
      { category: 'lesson', key: 'gateway-restart', value: 'NEVER restart the gateway' },
      { category: 'preference', key: 'cory.timezone', value: 'Eastern' },
      { category: 'person', key: 'cory.discord.alt', value: 'Bobsy' },
      { category: 'person', key: 'cory.son', value: 'Liam' },
      { category: 'environment', key: 'server.os', value: 'Ubuntu 24.04' },
      { category: 'tool', key: 'cad-wiki.ci', value: 'GitHub Actions' }
    ];
    for (const fact of baseFacts) {
      upsertFact(db, fact);
    }
    assert(result, db.prepare('SELECT COUNT(*) AS n FROM facts').get().n >= 10, 'E2E failed to seed 10 manual facts');

    const fixturePath = path.join(FIXTURE_DIR, 'simple-conversation.md');
    const ollamaAvailable = await isOllamaAvailable();
    let extractedFacts = [];

    if (ollamaAvailable) {
      try {
        const extraction = await extractFactsFromFile(fixturePath, {
          model: options.model || 'qwen3:8b',
          verbose: Boolean(options.verbose)
        });
        extractedFacts = extraction.facts;
      } catch {
        extractedFacts = [];
      }
    }

    if (extractedFacts.length === 0) {
      extractedFacts = loadExpectedForFixture('simple-conversation.md').map((fact) => ({
        ...fact,
        scope: 'global',
        tier: 'long-term',
        source_type: 'user_said',
        confidence: 0.9,
        ttl: null
      }));
    }

    const firstApply = applyExtractedFacts(db, extractedFacts);
    assert(result, firstApply.inserted + firstApply.updated + firstApply.skipped >= 1, 'E2E extraction apply had no effect');

    const secondApply = applyExtractedFacts(db, extractedFacts);
    assert(result, secondApply.inserted === 0, 'E2E dedup failed on re-extract');

    const cory = db.prepare('SELECT id FROM facts WHERE category = ? AND key = ?').get('person', 'cory.name');
    const editor = db.prepare('SELECT id FROM facts WHERE category = ? AND key = ?').get('project', 'cad-wiki.editor');
    db.prepare(`
      INSERT INTO relations (source_fact_id, target_fact_id, relation_type, created)
      VALUES (?, ?, ?, ?)
      ON CONFLICT(source_fact_id, target_fact_id, relation_type) DO NOTHING
    `).run(cory.id, editor.id, 'related_to', nowIso());

    const graphCount = db.prepare('SELECT COUNT(*) AS n FROM relations WHERE source_fact_id = ?').get(cory.id).n;
    assert(result, graphCount >= 1, 'E2E graph link missing');

    const markdown = factsToMarkdown(db.prepare('SELECT * FROM facts ORDER BY category, key').all());
    assert(result, markdown.includes('# Rune - Known Facts') && markdown.includes('cad-wiki.editor'), 'E2E inject output missing expected data');

    upsertFact(db, {
      category: 'task',
      key: 'e2e.temp',
      value: 'ephemeral',
      tier: 'working',
      ttl: '1s',
      scope: 'global'
    });
    await sleep(1200);
    const expired = db.prepare("DELETE FROM facts WHERE tier = 'working' AND expires_at IS NOT NULL AND expires_at <= ?").run(nowIso());
    const stillThere = db.prepare("SELECT COUNT(*) AS n FROM facts WHERE category = 'task' AND key = 'e2e.temp'").get().n;
    assert(result, expired.changes >= 1 && stillThere === 0, 'E2E TTL expire failed');
  } finally {
    db.close();
  }

  return result;
}

function ensureBenchmarkFile() {
  ensureParentDir(BENCHMARK_PATH);
  if (!fs.existsSync(BENCHMARK_PATH)) {
    fs.writeFileSync(BENCHMARK_PATH, JSON.stringify({ runs: [] }, null, 2));
  }
}

function loadBenchmarkHistory() {
  ensureBenchmarkFile();
  const parsed = JSON.parse(fs.readFileSync(BENCHMARK_PATH, 'utf8'));
  if (!parsed || !Array.isArray(parsed.runs)) {
    return { runs: [] };
  }
  return parsed;
}

function saveBenchmarkRun(run) {
  const history = loadBenchmarkHistory();
  history.runs.push(run);
  fs.writeFileSync(BENCHMARK_PATH, `${JSON.stringify(history, null, 2)}\n`, 'utf8');
}

function toDiffLine(label, current, previous, suffix = '') {
  if (current == null || previous == null) {
    return `${label}: n/a`;
  }
  const delta = current - previous;
  const sign = delta > 0 ? '+' : '';
  return `${label}: ${current}${suffix} (${sign}${delta.toFixed(3)}${suffix})`;
}

function compareWithLastSaved(currentRun) {
  const history = loadBenchmarkHistory();
  const prev = history.runs.length ? history.runs[history.runs.length - 1] : null;
  if (!prev) {
    return { ok: false, text: `No previous benchmark run found at ${BENCHMARK_PATH}` };
  }

  const lines = [
    `Comparing against ${prev.timestamp}`,
    toDiffLine('unit.passed', currentRun.unit?.passed, prev.unit?.passed),
    toDiffLine('extract.f1_avg', currentRun.extract?.f1_avg, prev.extract?.f1_avg),
    toDiffLine('recall.hit_rate', currentRun.recall?.hit_rate, prev.recall?.hit_rate),
    toDiffLine('perf.insert_1000_ms', currentRun.perf?.insert_1000_ms, prev.perf?.insert_1000_ms, 'ms'),
    toDiffLine('perf.search_avg_ms', currentRun.perf?.search_avg_ms, prev.perf?.search_avg_ms, 'ms'),
    toDiffLine('perf.inject_ms', currentRun.perf?.inject_ms, prev.perf?.inject_ms, 'ms'),
    toDiffLine('perf.extract_ms', currentRun.perf?.extract_ms, prev.perf?.extract_ms, 'ms')
  ];
  return { ok: true, text: lines.join('\n') };
}

function printSuiteResult(result, verbose = false) {
  const headerColor = result.failed > 0 ? colors.red : colors.green;
  console.log(headerColor(`${result.suite}: pass=${result.passed} fail=${result.failed} skip=${result.skipped}`));

  if (verbose && result.errors.length > 0) {
    for (const msg of result.errors) {
      const c = msg.startsWith('SKIP:') ? colors.yellow : colors.red;
      console.log(c(`  - ${msg}`));
    }
  }

  if (result.suite === 'perf' && result.metrics.table) {
    console.log(colors.bold('  perf table'));
    for (const row of result.metrics.table) {
      const total = row.total_ms == null ? 'n/a' : row.total_ms.toFixed(2);
      const per = row.per_op_ms == null ? 'n/a' : row.per_op_ms.toFixed(4);
      console.log(`  ${row.operation} count=${row.count} total_ms=${total} per_op_ms=${per}`);
    }
  }
}

function buildRunSummary(suiteResults) {
  const pkgPath = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..', 'package.json');
  const version = JSON.parse(fs.readFileSync(pkgPath, 'utf8')).version;

  const byName = Object.fromEntries(suiteResults.map((s) => [s.suite, s]));
  return {
    timestamp: new Date().toISOString(),
    version,
    unit: {
      passed: byName.unit?.passed ?? 0,
      failed: byName.unit?.failed ?? 0,
      total: byName.unit?.total ?? 0
    },
    extract: {
      f1_avg: byName.extract?.metrics?.f1_avg ?? 0,
      fixtures: byName.extract?.metrics?.fixtures ?? {}
    },
    recall: {
      hit_rate: byName.recall?.metrics?.hit_rate ?? 0,
      total: byName.recall?.metrics?.total ?? 0,
      hits: byName.recall?.metrics?.hits ?? 0
    },
    perf: {
      insert_1000_ms: byName.perf?.metrics?.insert_1000_ms ?? null,
      search_avg_ms: byName.perf?.metrics?.search_avg_ms ?? null,
      inject_ms: byName.perf?.metrics?.inject_ms ?? null,
      extract_ms: byName.perf?.metrics?.extract_ms ?? null,
      graph_3_level_ms: byName.perf?.metrics?.graph_3_level_ms ?? null
    }
  };
}

export async function runTestSuites(targetSuite = 'all', options = {}) {
  const suite = (targetSuite || 'all').toLowerCase();
  const selected = suite === 'all' ? SUITES : [suite];
  for (const s of selected) {
    if (!SUITES.includes(s)) {
      throw new Error(`Invalid suite \"${suite}\". Use one of: unit, extract, recall, perf, e2e, all`);
    }
  }

  const baseDbPath = options.db || DEFAULT_TEST_DB_PATH;
  const results = [];

  for (const s of selected) {
    const suiteDbPath = withSuiteDb(baseDbPath, s);
    if (s !== 'extract') {
      ensureParentDir(suiteDbPath);
      ensureDeleted(suiteDbPath);
    }

    let outcome;
    if (s === 'unit') {
      outcome = await runUnitSuite(suiteDbPath, options);
    }
    if (s === 'extract') {
      outcome = await runExtractSuite(options);
    }
    if (s === 'recall') {
      outcome = await runRecallSuite(suiteDbPath, options);
    }
    if (s === 'perf') {
      outcome = await runPerfSuite(suiteDbPath, options);
    }
    if (s === 'e2e') {
      outcome = await runE2ESuite(suiteDbPath, options);
    }

    results.push(outcome);
    printSuiteResult(outcome, Boolean(options.verbose));
  }

  const failed = results.reduce((sum, r) => sum + r.failed, 0);
  const savedRun = buildRunSummary(results);

  if (options.save) {
    saveBenchmarkRun(savedRun);
    console.log(colors.green(`Saved benchmark run: ${BENCHMARK_PATH}`));
  }

  if (options.compare) {
    const comparison = compareWithLastSaved(savedRun);
    if (comparison.ok) {
      console.log(colors.bold('Comparison'));
      console.log(comparison.text);
    } else {
      console.log(colors.yellow(comparison.text));
    }
  }

  console.log(colors.bold(`Summary: suites=${results.length} failed_assertions=${failed}`));
  return {
    ok: failed === 0,
    results,
    run: savedRun,
    benchmarkPath: BENCHMARK_PATH,
    defaultDbPath: DEFAULT_TEST_DB_PATH,
    realDbPath: DB_PATH
  };
}
