import fs from 'node:fs';
import path from 'node:path';
import { Command } from 'commander';
import { DB_PATH, openDb, nowIso } from './db.js';
import { colors } from './colors.js';
import { factsToMarkdown } from './format.js';
import { extractFactsFromFile, wasAlreadyExtracted, logExtraction } from './extract.js';
import { runTestSuites } from './test-runner.js';
import { UserError } from './errors.js';

const DEFAULT_LIMIT = 100;
const VALID_SCOPES = new Set(['global', 'project', 'conversation']);
const VALID_TIERS = new Set(['working', 'long-term']);
const VALID_SOURCE_TYPES = new Set(['manual', 'inferred', 'user_said', 'tool_output']);
const VALID_RELATION_TYPES = new Set(['related_to', 'part_of', 'decided_by', 'owned_by', 'replaced_by']);

function parseConfidence(value) {
  const n = Number(value);
  if (Number.isNaN(n) || n < 0 || n > 1) {
    throw new UserError('Confidence must be a number between 0 and 1');
  }
  return n;
}

function parseLimit(value) {
  const n = Number.parseInt(value, 10);
  if (!Number.isInteger(n) || n <= 0) {
    throw new UserError('Limit must be a positive integer');
  }
  return n;
}

function parseDate(value) {
  const d = new Date(value);
  if (Number.isNaN(d.valueOf())) {
    throw new UserError('Invalid date. Use ISO format like 2025-01-01T00:00:00Z');
  }
  return d.toISOString();
}

function parseScope(value) {
  if (!VALID_SCOPES.has(value)) {
    throw new UserError('Scope must be one of: global, project, conversation');
  }
  return value;
}

function parseTier(value) {
  if (!VALID_TIERS.has(value)) {
    throw new UserError('Tier must be one of: working, long-term');
  }
  return value;
}

function parseSourceType(value) {
  if (!VALID_SOURCE_TYPES.has(value)) {
    throw new UserError('Source type must be one of: manual, inferred, user_said, tool_output');
  }
  return value;
}

function parseRelationType(value) {
  if (!VALID_RELATION_TYPES.has(value)) {
    throw new UserError(`Relation type must be one of: ${[...VALID_RELATION_TYPES].join(', ')}`);
  }
  return value;
}

function parseDurationMs(value) {
  const match = String(value).trim().toLowerCase().match(/^(\d+)([smhdw])$/);
  if (!match) {
    throw new UserError('TTL must be a compact duration like 30m, 24h, 7d');
  }

  const amount = Number.parseInt(match[1], 10);
  if (!Number.isInteger(amount) || amount <= 0) {
    throw new UserError('TTL duration amount must be a positive integer');
  }

  const unit = match[2];
  const multipliers = {
    s: 1000,
    m: 60 * 1000,
    h: 60 * 60 * 1000,
    d: 24 * 60 * 60 * 1000,
    w: 7 * 24 * 60 * 60 * 1000
  };

  return amount * multipliers[unit];
}

function ttlToExpiresAt(ttl) {
  if (!ttl) {
    return null;
  }
  return new Date(Date.now() + parseDurationMs(ttl)).toISOString();
}

function formatDuration(ms) {
  const abs = Math.max(0, Math.floor(ms / 1000));
  const units = [
    { size: 86400, label: 'd' },
    { size: 3600, label: 'h' },
    { size: 60, label: 'm' },
    { size: 1, label: 's' }
  ];

  for (const unit of units) {
    if (abs >= unit.size) {
      return `${Math.floor(abs / unit.size)}${unit.label}`;
    }
  }
  return '0s';
}

function expiresLabel(expiresAt) {
  if (!expiresAt) {
    return 'no ttl';
  }

  const delta = new Date(expiresAt).valueOf() - Date.now();
  if (!Number.isFinite(delta)) {
    return 'invalid ttl';
  }

  if (delta <= 0) {
    return `expired ${formatDuration(-delta)} ago`;
  }
  return `expires in ${formatDuration(delta)}`;
}

function printFact(fact) {
  const conf = typeof fact.confidence === 'number' ? fact.confidence.toFixed(2) : '1.00';
  const source = fact.source ? ` source=${fact.source}` : '';
  const meta = ` confidence=${conf} scope=${fact.scope ?? 'global'} tier=${fact.tier ?? 'long-term'} source_type=${fact.source_type ?? 'manual'} ttl=${expiresLabel(fact.expires_at)}`;
  console.log(`${colors.bold(`${fact.category}/${fact.key}`)} = ${fact.value}${colors.dim(` [${meta}${source}]`)}`);
}

function projectTag(slug) {
  return `[project:${slug}]`;
}

function withProjectTag(source, project) {
  if (!project) {
    return source ?? null;
  }
  const tag = projectTag(project);
  const base = source ? String(source).trim() : '';
  if (base.includes(tag)) {
    return base;
  }
  return base ? `${base} ${tag}` : tag;
}

function upsertFact(db, {
  category,
  key,
  value,
  source = null,
  confidence = 1.0,
  scope = 'global',
  tier = 'long-term',
  expires_at: expiresAt = null,
  last_verified: lastVerified = null,
  source_type: sourceType = 'manual'
}) {
  const ts = nowIso();

  // Check for existing fact — log change if value differs
  const existing = db.prepare('SELECT id, value FROM facts WHERE category = ? AND key = ?').get(category, key);
  if (existing && existing.value !== value) {
    db.prepare(`
      INSERT INTO changelog (fact_id, category, key, old_value, new_value, change_type, source, created)
      VALUES (?, ?, ?, ?, ?, 'updated', ?, ?)
    `).run(existing.id, category, key, existing.value, value, source, ts);
  }

  const stmt = db.prepare(`
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
  `);

  const changeType = existing ? 'updated' : 'inserted';

  stmt.run({
    category,
    key,
    value,
    source,
    confidence,
    created: ts,
    updated: ts,
    scope,
    tier,
    expires_at: expiresAt,
    last_verified: lastVerified,
    source_type: sourceType
  });

  // Log insertion to changelog too
  if (!existing) {
    const newFact = db.prepare('SELECT id FROM facts WHERE category = ? AND key = ?').get(category, key);
    if (newFact) {
      db.prepare(`
        INSERT INTO changelog (fact_id, category, key, old_value, new_value, change_type, source, created)
        VALUES (?, ?, ?, NULL, ?, 'created', ?, ?)
      `).run(newFact.id, category, key, value, source, ts);
    }
  }

  return changeType;
}

function requireFile(filePath) {
  if (!fs.existsSync(filePath)) {
    throw new UserError(`File not found: ${filePath}`);
  }
}

function requireDirectory(dirPath) {
  if (!fs.existsSync(dirPath)) {
    throw new UserError(`Directory not found: ${dirPath}`);
  }
  if (!fs.statSync(dirPath).isDirectory()) {
    throw new UserError(`Not a directory: ${dirPath}`);
  }
}

function toSummaryKey(date = new Date()) {
  const pad = (n) => String(n).padStart(2, '0');
  return `summary.${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}-${pad(date.getHours())}-${pad(date.getMinutes())}`;
}

function hasSessionSummary(summary) {
  return (
    summary.decisions.length > 0 ||
    summary.open_questions.length > 0 ||
    summary.action_items.length > 0 ||
    summary.topics.length > 0
  );
}

function globToRegex(glob) {
  const escaped = String(glob).replace(/[.+^${}()|[\]\\]/g, '\\$&');
  const regexPattern = `^${escaped.replace(/\*/g, '.*').replace(/\?/g, '.').replace(/\//g, '[/\\\\]')}$`;
  return new RegExp(regexPattern, 'i');
}

function listFilesRecursive(rootDir, pattern, sinceIso = null) {
  const matcher = globToRegex(pattern);
  const out = [];
  const stack = [rootDir];

  while (stack.length > 0) {
    const current = stack.pop();
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const fullPath = path.join(current, entry.name);
      if (entry.isDirectory()) {
        stack.push(fullPath);
        continue;
      }
      if (!entry.isFile()) {
        continue;
      }
      const rel = path.relative(rootDir, fullPath);
      if (!matcher.test(rel) && !matcher.test(entry.name)) {
        continue;
      }
      if (sinceIso) {
        const stat = fs.statSync(fullPath);
        if (stat.mtime.toISOString() <= sinceIso) {
          continue;
        }
      }
      out.push(fullPath);
    }
  }

  out.sort((a, b) => a.localeCompare(b));
  return out;
}

function applyExtractedFacts(db, facts) {
  const now = nowIso();
  const getByKey = db.prepare('SELECT * FROM facts WHERE category = ? AND key = ?');
  const insertStmt = db.prepare(`
    INSERT INTO facts (category, key, value, source, confidence, created, updated, scope, tier, expires_at, last_verified, source_type)
    VALUES (@category, @key, @value, @source, @confidence, @created, @updated, @scope, @tier, @expires_at, @last_verified, @source_type)
  `);
  const updateChangedStmt = db.prepare(`
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
  const touchVerifiedStmt = db.prepare(`
    UPDATE facts
    SET last_verified = @last_verified
    WHERE category = @category AND key = @key
  `);

  let inserted = 0;
  let updated = 0;
  let skipped = 0;

  const tx = db.transaction((items) => {
    for (const fact of items) {
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
        touchVerifiedStmt.run({
          category: fact.category,
          key: fact.key,
          last_verified: now
        });
        skipped += 1;
        continue;
      }

      updateChangedStmt.run({
        category: fact.category,
        key: fact.key,
        value: fact.value,
        source: existing.source ?? null,
        confidence: fact.confidence ?? existing.confidence ?? 0.8,
        scope: fact.scope ?? existing.scope ?? 'global',
        tier: fact.tier ?? existing.tier ?? 'long-term',
        expires_at: ttlToExpiresAt(fact.ttl),
        source_type: fact.source_type ?? existing.source_type ?? 'inferred',
        updated: now
      });
      updated += 1;
    }
  });

  tx(facts);
  return { inserted, updated, skipped };
}

function storeSessionSummary(db, summary) {
  if (!hasSessionSummary(summary)) {
    return null;
  }
  const key = toSummaryKey();
  upsertFact(db, {
    category: 'session',
    key,
    value: JSON.stringify(summary),
    scope: 'global',
    tier: 'long-term',
    source_type: 'inferred',
    confidence: 0.9
  });
  return key;
}

async function runExtractOne(file, options) {
  const startMs = Date.now();
  const content = fs.readFileSync(file, 'utf8');

  // Skip files already extracted (unless --force)
  if (!options.dryRun && !options.force) {
    const db = openDb();
    const already = wasAlreadyExtracted(db, file, content);
    db.close();
    if (already) {
      if (options.verbose) {
        console.log(colors.dim(`${file}: already extracted (use --force to re-extract)`));
      }
      return { facts: 0, inserted: 0, updated: 0, skipped: 0, summaryStored: false, skippedFile: true };
    }
  }

  let extraction;
  try {
    extraction = await extractFactsFromFile(file, {
      engine: options.engine,
      model: options.model,
      verbose: Boolean(options.verbose)
    });
  } catch (err) {
    const durationMs = Date.now() - startMs;
    // Log failed extraction so we can debug
    if (!options.dryRun) {
      const db = openDb();
      logExtraction(db, {
        filePath: file, content, engine: options.engine || 'auto',
        model: options.model || 'default', facts: 0, inserted: 0,
        updated: 0, skipped: 0, durationMs, status: 'error',
        error: err.message || String(err)
      });
      db.close();
    }
    throw err;
  }

  const durationMs = Date.now() - startMs;

  if (extraction.facts.length === 0 && !hasSessionSummary(extraction.session_summary)) {
    console.log(colors.yellow(`${file}: no useful extraction output`));
    if (!options.dryRun) {
      const db = openDb();
      logExtraction(db, {
        filePath: file, content, engine: extraction.engine,
        model: options.model || 'default', facts: 0, inserted: 0,
        updated: 0, skipped: 0, durationMs, status: 'empty'
      });
      db.close();
    }
    return { facts: 0, inserted: 0, updated: 0, skipped: 0, summaryStored: false };
  }

  if (options.dryRun) {
    console.log(colors.bold(file));
    for (const fact of extraction.facts) {
      console.log(`${fact.category}/${fact.key} = ${fact.value} [scope=${fact.scope} tier=${fact.tier} source_type=${fact.source_type} confidence=${fact.confidence.toFixed(2)} ttl=${fact.ttl ?? 'none'}]`);
    }
    if (hasSessionSummary(extraction.session_summary)) {
      console.log(colors.dim(`session_summary decisions=${extraction.session_summary.decisions.length} open_questions=${extraction.session_summary.open_questions.length} action_items=${extraction.session_summary.action_items.length} topics=${extraction.session_summary.topics.length}`));
    }
    console.log(colors.dim(`${extraction.facts.length} fact(s) extracted in ${(durationMs/1000).toFixed(1)}s [${extraction.engine}]${extraction.chunks > 1 ? ` across ${extraction.chunks} chunk(s)` : ''}`));
    return {
      facts: extraction.facts.length,
      inserted: 0,
      updated: 0,
      skipped: 0,
      summaryStored: hasSessionSummary(extraction.session_summary)
    };
  }

  const db = openDb();
  const result = applyExtractedFacts(db, extraction.facts);
  const summaryKey = storeSessionSummary(db, extraction.session_summary);

  logExtraction(db, {
    filePath: file, content, engine: extraction.engine,
    model: options.model || 'default', facts: extraction.facts.length,
    inserted: result.inserted, updated: result.updated,
    skipped: result.skipped, durationMs, status: 'ok'
  });
  db.close();

  const changedMsg = `inserted=${result.inserted} updated=${result.updated} skipped=${result.skipped}`;
  const summaryMsg = summaryKey ? ` summary=${summaryKey}` : '';
  const timeMsg = ` (${(durationMs/1000).toFixed(1)}s ${extraction.engine})`;
  console.log(colors.green(`${file}: extracted=${extraction.facts.length} ${changedMsg}${summaryMsg}${timeMsg}`));
  return {
    facts: extraction.facts.length,
    inserted: result.inserted,
    updated: result.updated,
    skipped: result.skipped,
    summaryStored: Boolean(summaryKey)
  };
}

function printSimpleList(facts) {
  for (const fact of facts) {
    printFact(fact);
  }
  console.log(colors.dim(`${facts.length} fact(s)`));
}

function parseFactRef(input) {
  const trimmed = String(input).trim();
  const slash = trimmed.indexOf('/');
  if (slash <= 0 || slash === trimmed.length - 1) {
    throw new UserError(`Invalid fact reference: ${input}. Expected category/key`);
  }

  return {
    category: trimmed.slice(0, slash),
    key: trimmed.slice(slash + 1)
  };
}

function getFactByRef(db, input) {
  const ref = parseFactRef(input);
  const row = db.prepare('SELECT * FROM facts WHERE category = ? AND key = ?').get(ref.category, ref.key);
  if (!row) {
    throw new UserError(`Fact not found: ${ref.category}/${ref.key}`);
  }
  return row;
}

function toFtsQuery(query) {
  const terms = String(query)
    .trim()
    .split(/\s+/)
    .map((term) => term.replace(/"/g, '""'))
    .filter(Boolean)
    .map((term) => `"${term}"*`);

  if (terms.length === 0) {
    throw new UserError('Search query cannot be empty');
  }
  return terms.join(' AND ');
}

export function runCli(argv) {
  const program = new Command();

  program
    .name('rune')
    .description('Persistent fact-based memory for Brokkr')
    .version('1.0.0');

  program.command('add <category> <key> <value>')
    .description('Add or update a fact')
    .option('--source <source>', 'Fact source')
    .option('--confidence <n>', 'Confidence score (0-1)', parseConfidence, 1.0)
    .option('--scope <scope>', 'Fact scope: global|project|conversation', parseScope, 'global')
    .option('--tier <tier>', 'Memory tier: working|long-term', parseTier, 'long-term')
    .option('--ttl <duration>', 'Auto-expire duration (e.g., 24h, 7d, 30m)')
    .option('--source-type <type>', 'manual|inferred|user_said|tool_output', parseSourceType, 'manual')
    .option('--project <slug>', 'Shortcut: sets scope=project and tags source with project name')
    .action((category, key, value, options) => {
      const db = openDb();
      const scope = options.project ? 'project' : options.scope;
      const source = withProjectTag(options.source ?? null, options.project ?? null);
      const expiresAt = ttlToExpiresAt(options.ttl ?? null);

      upsertFact(db, {
        category,
        key,
        value,
        source,
        confidence: options.confidence,
        scope,
        tier: options.tier,
        expires_at: expiresAt,
        source_type: options.sourceType
      });

      db.close();
      console.log(colors.green('Fact saved'));
    });

  program.command('get <category> [key]')
    .description('Get facts by category or specific key')
    .action((category, key) => {
      const db = openDb();
      let rows;
      if (key) {
        rows = db.prepare('SELECT * FROM facts WHERE category = ? AND key = ?').all(category, key);
      } else {
        rows = db.prepare('SELECT * FROM facts WHERE category = ? ORDER BY key').all(category);
      }
      db.close();

      if (rows.length === 0) {
        throw new UserError('No matching facts found', 2);
      }
      printSimpleList(rows);
    });

  program.command('search <query>')
    .description('Search facts using FTS5 index')
    .action((query) => {
      const db = openDb();
      const ftsQuery = toFtsQuery(query);
      let rows = db.prepare(`
        SELECT f.*
        FROM facts_fts
        JOIN facts f ON f.id = facts_fts.rowid
        WHERE facts_fts MATCH ?
        ORDER BY bm25(facts_fts), f.updated DESC
      `).all(ftsQuery);

      if (rows.length === 0) {
        rows = db.prepare(`
          SELECT * FROM facts
          WHERE lower(key) LIKE lower(?) OR lower(value) LIKE lower(?)
          ORDER BY updated DESC
        `).all(`%${query}%`, `%${query}%`);
      }

      db.close();

      if (rows.length === 0) {
        throw new UserError('No matching facts found', 2);
      }
      printSimpleList(rows);
    });

  program.command('score <message>')
    .description('Score all facts for relevance to a message/query (Phase 4: Adaptive Context)')
    .option('--engine <engine>', 'Scoring engine: ollama (default), anthropic, openai', 'ollama')
    .option('--model <model>', 'Model for scoring')
    .option('--limit <n>', 'Max facts to return', '50')
    .option('--threshold <score>', 'Min relevance score (0-1)', '0.3')
    .option('--json', 'Output as JSON')
    .action(async (message, options) => {
      const db = openDb();
      const limit = parseInt(options.limit, 10) || 50;
      const threshold = parseFloat(options.threshold) || 0.3;
      
      // Get all facts
      const allFacts = db.prepare('SELECT * FROM facts ORDER BY updated DESC').all();
      if (allFacts.length === 0) {
        console.log(colors.yellow('No facts to score'));
        db.close();
        return;
      }

      try {
        const { scoreFactsForRelevance } = await import('./relevance.js');
        const scoredFacts = await scoreFactsForRelevance(message, allFacts, {
          engine: options.engine,
          model: options.model,
          limit,
          threshold
        });

        if (options.json) {
          console.log(JSON.stringify(scoredFacts, null, 2));
          db.close();
          return;
        }

        console.log(colors.bold(`🎯 Relevance: "${message}"`));
        console.log('');
        
        for (const item of scoredFacts) {
          const score = item.relevance_score.toFixed(3);
          const color = item.relevance_score > 0.7 ? colors.green : item.relevance_score > 0.5 ? colors.yellow : colors.dim;
          console.log(`${color(score)} ${item.category}/${item.key} = ${item.value}`);
        }
        
        console.log('');
        console.log(colors.dim(`${scoredFacts.length} fact(s) above ${threshold} threshold`));
        
      } catch (err) {
        console.log(colors.red(`Scoring failed: ${err.message}`));
      }
      
      db.close();
    });

  program.command('budget <message>')
    .description('Generate context within strict token budget (Phase 4: T-028)')
    .option('--engine <engine>', 'Scoring engine', 'ollama')
    .option('--model <model>', 'Model for scoring')
    .option('--tokens <n>', 'Token budget (approximate)', '500')
    .option('--threshold <score>', 'Min relevance score (0-1)', '0.5')
    .action(async (message, options) => {
      try {
        const tokenBudget = parseInt(options.tokens, 10) || 500;
        const threshold = parseFloat(options.threshold) || 0.5;
        
        const { openDb } = await import('./db.js');
        const { scoreFactsForRelevance } = await import('./relevance.js');
        
        const db = openDb();
        const allFacts = db.prepare('SELECT * FROM facts ORDER BY updated DESC').all();
        db.close();
        
        if (allFacts.length === 0) {
          console.log(colors.yellow('No facts to budget'));
          return;
        }

        // Score all facts
        const scoredFacts = await scoreFactsForRelevance(message, allFacts, {
          engine: options.engine,
          model: options.model,
          limit: 100,  // Get many candidates
          threshold: 0.1  // Low threshold for candidates
        });

        // Budget selection: estimate tokens per fact (~15-25 tokens avg)
        const AVG_TOKENS_PER_FACT = 20;
        const headerTokens = 50;  // "# Dynamic Context" etc
        const availableTokens = tokenBudget - headerTokens;
        const maxFacts = Math.floor(availableTokens / AVG_TOKENS_PER_FACT);
        
        // Select top facts within budget, respect threshold
        const selectedFacts = scoredFacts
          .filter(f => f.relevance_score >= threshold)
          .slice(0, Math.max(1, maxFacts));  // At least 1 fact if any pass threshold
        
        if (selectedFacts.length === 0) {
          console.log(colors.yellow(`No facts above threshold ${threshold}`));
          return;
        }

        // Generate context
        let context = '# Dynamic Context\n\n';
        const grouped = {};
        for (const fact of selectedFacts) {
          if (!grouped[fact.category]) grouped[fact.category] = [];
          grouped[fact.category].push(fact);
        }

        for (const [category, facts] of Object.entries(grouped)) {
          context += `## ${category}\n`;
          for (const fact of facts) {
            context += `- ${fact.key}: ${fact.value}\n`;
          }
          context += '\n';
        }

        const actualTokens = Math.round(context.length / 3.5);  // Rough token estimate
        context += `*${selectedFacts.length} fact(s), ~${actualTokens}/${tokenBudget} tokens*\n`;
        
        console.log(context);
        
        if (actualTokens > tokenBudget) {
          console.log(colors.yellow(`Warning: Exceeded budget by ${actualTokens - tokenBudget} tokens`));
        }
        
      } catch (err) {
        console.log(colors.red(`Budget generation failed: ${err.message}`));
      }
    });

  program.command('context <message>')
    .description('Generate dynamic context injection for a message (Phase 4: T-025)')
    .option('--engine <engine>', 'Scoring engine: ollama (default), anthropic, openai', 'ollama')
    .option('--model <model>', 'Model for scoring')
    .option('--budget <n>', 'Max facts to include (context budget)', '15')
    .option('--threshold <score>', 'Min relevance score (0-1)', '0.4')
    .option('--output <file>', 'Write to file instead of stdout')
    .action(async (message, options) => {
      try {
        const { generateDynamicContext } = await import('./relevance.js');
        
        const contextMd = await generateDynamicContext(message, {
          engine: options.engine,
          model: options.model,
          contextBudget: parseInt(options.budget, 10) || 15,
          threshold: parseFloat(options.threshold) || 0.4
        });

        if (options.output) {
          const fs = await import('fs');
          fs.writeFileSync(options.output, contextMd);
          console.log(colors.green(`Context written to ${options.output}`));
        } else {
          console.log(contextMd);
        }
        
      } catch (err) {
        console.log(colors.red(`Context generation failed: ${err.message}`));
      }
    });

  program.command('proactive <message>')
    .description('Proactive memory - volunteer relevant context unprompted (Phase 5: T-031)')
    .option('--engine <engine>', 'Scoring engine', 'ollama')
    .option('--model <model>', 'Model for scoring') 
    .option('--style <style>', 'Response style: summary, tips, warnings, context', 'context')
    .option('--quiet', 'Return empty if no strong matches (relevance < 0.7)')
    .action(async (message, options) => {
      try {
        const { generateProactiveMemory } = await import('./proactive.js');
        
        const response = await generateProactiveMemory(message, {
          engine: options.engine,
          model: options.model,
          style: options.style,
          quietMode: options.quiet
        });

        if (response.trim()) {
          console.log(response);
        } else if (!options.quiet) {
          console.log(colors.dim('(No proactive context available)'));
        }
        
      } catch (err) {
        console.log(colors.red(`Proactive memory failed: ${err.message}`));
      }
    });

  program.command('remember <query>')
    .description('Search memory with trigger phrases like "remember when" (Phase 5: T-032)')  
    .option('--limit <n>', 'Max results to return', '10')
    .option('--days <n>', 'Search within N days', '30')
    .option('--json', 'Output as JSON')
    .action((query, options) => {
      const db = openDb();
      const limit = parseInt(options.limit, 10) || 10;
      const daysBack = parseInt(options.days, 10) || 30;
      const cutoffDate = new Date(Date.now() - daysBack * 24 * 60 * 60 * 1000).toISOString();
      
      // Multi-source search for memory patterns
      const results = {
        facts: [],
        events: [],
        changes: []
      };
      
      // FTS search in facts
      const ftsQuery = toFtsQuery(query);
      try {
        results.facts = db.prepare(`
          SELECT f.*, bm25(facts_fts) as rank
          FROM facts_fts
          JOIN facts f ON f.id = facts_fts.rowid  
          WHERE facts_fts MATCH ? AND f.updated > ?
          ORDER BY bm25(facts_fts)
          LIMIT ?
        `).all(ftsQuery, cutoffDate, limit);
      } catch {
        // Fallback to LIKE search
        results.facts = db.prepare(`
          SELECT * FROM facts
          WHERE (LOWER(key) LIKE ? OR LOWER(value) LIKE ?) AND updated > ?
          ORDER BY updated DESC LIMIT ?
        `).all(`%${query.toLowerCase()}%`, `%${query.toLowerCase()}%`, cutoffDate, limit);
      }
      
      // Search performance events
      results.events = db.prepare(`
        SELECT * FROM performance_log
        WHERE LOWER(detail) LIKE ? AND created > ?
        ORDER BY created DESC LIMIT ?
      `).all(`%${query.toLowerCase()}%`, cutoffDate, Math.floor(limit / 2));
      
      // Search changelog
      results.changes = db.prepare(`
        SELECT * FROM changelog
        WHERE (LOWER(key) LIKE ? OR LOWER(old_value) LIKE ? OR LOWER(new_value) LIKE ?) 
              AND created > ?
        ORDER BY created DESC LIMIT ?
      `).all(`%${query.toLowerCase()}%`, `%${query.toLowerCase()}%`, `%${query.toLowerCase()}%`, cutoffDate, Math.floor(limit / 2));
      
      db.close();
      
      if (options.json) {
        console.log(JSON.stringify(results, null, 2));
        return;
      }
      
      const total = results.facts.length + results.events.length + results.changes.length;
      if (total === 0) {
        console.log(colors.yellow(`No memories found for "${query}" in the last ${daysBack} days`));
        return;
      }
      
      console.log(colors.bold(`🧠 Remember: "${query}"`));
      console.log('');
      
      if (results.facts.length > 0) {
        console.log(colors.bold('Facts:'));
        results.facts.forEach(f => {
          console.log(`  ${f.category}/${f.key}: ${f.value}`);
          console.log(colors.dim(`    (${f.updated.substring(0, 10)})`));
        });
        console.log('');
      }
      
      if (results.events.length > 0) {
        console.log(colors.bold('Events:'));
        results.events.forEach(e => {
          const icon = e.event_type === 'mistake' ? '❌' : e.event_type === 'success' ? '✅' : '📝';
          console.log(`  ${icon} ${e.event_type}: ${e.detail}`);
          console.log(colors.dim(`    (${e.created.substring(0, 10)})`));
        });
        console.log('');
      }
      
      if (results.changes.length > 0) {
        console.log(colors.bold('Changes:'));
        results.changes.forEach(c => {
          console.log(`  ~ ${c.key}: ${c.old_value} → ${c.new_value}`);
          console.log(colors.dim(`    (${c.created.substring(0, 10)})`));
        });
        console.log('');
      }
      
      console.log(colors.dim(`${total} result(s) from last ${daysBack} days`));
    });

  program.command('session-style <message>')
    .description('Detect interaction style for adaptive responses (Phase 5: T-029)')
    .option('--save', 'Save to session metadata store')
    .option('--session-id <id>', 'Session identifier')
    .action(async (message, options) => {
      try {
        const { detectInteractionStyle, saveSessionMetadata } = await import('./session-intel.js');
        
        const analysis = detectInteractionStyle(message);
        
        console.log(colors.bold(`🎭 Style Analysis: "${message}"`));
        console.log('');
        console.log(`**Primary Style:** ${analysis.primary}`);
        console.log(`**Confidence:** ${analysis.confidence.toFixed(2)}`);
        console.log(`**Indicators:** ${analysis.indicators.join(', ')}`);
        
        if (analysis.mood) {
          console.log(`**Mood:** ${analysis.mood}`);
        }
        
        if (analysis.urgency) {
          console.log(`**Urgency:** ${analysis.urgency}`);
        }
        
        if (options.save) {
          const sessionId = options.sessionId || 'default';
          saveSessionMetadata(sessionId, {
            style: analysis.primary,
            confidence: analysis.confidence,
            mood: analysis.mood,
            urgency: analysis.urgency,
            message: message.substring(0, 100)  // First 100 chars for reference
          });
          console.log(colors.green(`\nSaved to session ${sessionId}`));
        }
        
      } catch (err) {
        console.log(colors.red(`Style detection failed: ${err.message}`));
      }
    });

  program.command('session-patterns [sessionId]')
    .description('Analyze session patterns and behavior (Phase 5: T-033)')
    .option('--days <n>', 'Look back N days', '30')
    .option('--json', 'Output as JSON')
    .action(async (sessionId = 'default', options) => {
      try {
        const { getSessionPatterns } = await import('./session-intel.js');
        
        const analysis = getSessionPatterns(sessionId, parseInt(options.days, 10) || 30);
        
        if (options.json) {
          console.log(JSON.stringify(analysis, null, 2));
          return;
        }
        
        console.log(colors.bold(`📊 Session Patterns: ${sessionId}`));
        console.log('');
        
        if (analysis.patterns.session_count === 0) {
          console.log(colors.yellow('No session data found'));
          return;
        }
        
        console.log(colors.bold('Patterns:'));
        console.log(`  Preferred Style: ${analysis.patterns.preferred_style}`);
        console.log(`  Common Moods: ${analysis.patterns.common_moods.join(', ') || 'none detected'}`);
        console.log(`  Frequent Topics: ${analysis.patterns.frequent_topics.join(', ') || 'none detected'}`);
        console.log(`  Session Count: ${analysis.patterns.session_count}`);
        console.log('');
        
        if (analysis.insights.length > 0) {
          console.log(colors.bold('Insights:'));
          analysis.insights.forEach(insight => {
            console.log(`  • ${insight}`);
          });
        }
        
      } catch (err) {
        console.log(colors.red(`Pattern analysis failed: ${err.message}`));
      }
    });

  program.command('project-state [project]')
    .description('Track and manage project states (Phase 6: T-034)')
    .option('--set-phase <phase>', 'Set project phase (planning, building, testing, deploying, complete)')
    .option('--set-task <task>', 'Set active task')
    .option('--add-blocker <blocker>', 'Add a blocker')
    .option('--resolve-blocker <id>', 'Mark blocker as resolved')
    .option('--next-steps <steps>', 'Set next steps')
    .option('--list-all', 'List all projects')
    .option('--json', 'Output as JSON')
    .action(async (project, options) => {
      try {
        const { getProjectState, updateProjectState, listAllProjects } = await import('./autopilot.js');
        
        if (options.listAll) {
          const projects = listAllProjects();
          
          if (options.json) {
            console.log(JSON.stringify(projects, null, 2));
            return;
          }
          
          console.log(colors.bold('📋 All Projects'));
          console.log('');
          
          if (projects.length === 0) {
            console.log(colors.yellow('No projects found'));
            return;
          }
          
          projects.forEach(proj => {
            console.log(colors.bold(`${proj.name}`));
            console.log(`  Phase: ${proj.phase}`);
            console.log(`  Active Task: ${proj.active_task || 'none'}`);
            console.log(`  Blockers: ${proj.blockers || 0}`);
            console.log(`  Updated: ${proj.updated.substring(0, 10)}`);
            console.log('');
          });
          
          return;
        }
        
        if (!project) {
          console.log(colors.red('Project name required (or use --list-all)'));
          return;
        }
        
        // Handle updates
        const updates = {};
        if (options.setPhase) updates.phase = options.setPhase;
        if (options.setTask) updates.active_task = options.setTask;
        if (options.nextSteps) updates.next_steps = options.nextSteps;
        
        if (Object.keys(updates).length > 0) {
          updateProjectState(project, updates);
          console.log(colors.green(`Updated ${project}`));
        }
        
        // Handle blockers
        if (options.addBlocker) {
          updateProjectState(project, { add_blocker: options.addBlocker });
          console.log(colors.yellow(`Added blocker to ${project}`));
        }
        
        if (options.resolveBlocker) {
          updateProjectState(project, { resolve_blocker: parseInt(options.resolveBlocker) });
          console.log(colors.green(`Resolved blocker for ${project}`));
        }
        
        // Show current state
        const state = getProjectState(project);
        
        if (options.json) {
          console.log(JSON.stringify(state, null, 2));
          return;
        }
        
        console.log(colors.bold(`📊 Project: ${project}`));
        console.log('');
        console.log(`Phase: ${state.phase}`);
        console.log(`Active Task: ${state.active_task || 'none'}`);
        console.log(`Next Steps: ${state.next_steps || 'none'}`);
        console.log(`Blockers: ${state.blockers?.length || 0}`);
        
        if (state.blockers && state.blockers.length > 0) {
          console.log('');
          console.log(colors.bold('Blockers:'));
          state.blockers.forEach((blocker, idx) => {
            console.log(`  ${idx + 1}. ${blocker.description} (${blocker.created.substring(0, 10)})`);
          });
        }
        
        console.log('');
        console.log(`Last Updated: ${state.updated}`);
        
      } catch (err) {
        console.log(colors.red(`Project state failed: ${err.message}`));
      }
    });

  program.command('next-task')
    .description('Smart task picker - what should I work on next? (Phase 6: T-036)')
    .option('--skip-blocked', 'Skip projects with active blockers', false)
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      try {
        const { getNextTask } = await import('./autopilot.js');
        
        const nextTask = getNextTask({ skipBlocked: options.skipBlocked });
        
        if (!nextTask) {
          console.log(colors.yellow('No unblocked tasks found'));
          return;
        }
        
        if (options.json) {
          console.log(JSON.stringify(nextTask, null, 2));
          return;
        }
        
        console.log(colors.bold('🎯 Recommended Next Task'));
        console.log('');
        console.log(colors.bold(`Project: ${nextTask.name}`));
        console.log(`Phase: ${nextTask.phase}`);
        console.log(`Priority: ${nextTask.priority}`);
        console.log(`Active Task: ${nextTask.active_task || 'none'}`);
        console.log(`Next Steps: ${nextTask.next_steps || 'none'}`);
        console.log(`Score: ${nextTask.score?.toFixed(1) || 'N/A'}`);
        
        if (nextTask.last_activity) {
          const daysSince = Math.floor((Date.now() - new Date(nextTask.last_activity).getTime()) / (1000 * 60 * 60 * 24));
          console.log(`Last Activity: ${daysSince} day(s) ago`);
        }
        
      } catch (err) {
        console.log(colors.red(`Task picker failed: ${err.message}`));
      }
    });

  program.command('stuck-projects')
    .description('Detect projects blocked too long (Phase 6: T-037)')
    .option('--hours <n>', 'Consider stuck after N hours', '48')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      try {
        const { detectStuckProjects } = await import('./autopilot.js');
        
        const hours = parseInt(options.hours, 10) || 48;
        const stuckProjects = detectStuckProjects(hours);
        
        if (options.json) {
          console.log(JSON.stringify(stuckProjects, null, 2));
          return;
        }
        
        if (stuckProjects.length === 0) {
          console.log(colors.green(`No projects stuck longer than ${hours} hours`));
          return;
        }
        
        console.log(colors.bold(`🚨 Projects Stuck > ${hours}h`));
        console.log('');
        
        stuckProjects.forEach(project => {
          const stuckDays = Math.floor((Date.now() - new Date(project.oldest_blocker).getTime()) / (1000 * 60 * 60 * 24));
          console.log(colors.red(`${project.name}`));
          console.log(`  Blocked for: ${stuckDays} day(s)`);
          console.log(`  Phase: ${project.phase}`);
          console.log(`  Blockers: ${project.blocker_count}`);
          console.log('');
        });
        
        console.log(colors.yellow('💡 These projects may need intervention'));
        
      } catch (err) {
        console.log(colors.red(`Stuck detection failed: ${err.message}`));
      }
    });

  program.command('notify <message>')
    .description('Smart notification classification and routing (Phase 7: T-039)')
    .option('--channel <channel>', 'Target channel (dm, discord, system)', 'dm')
    .option('--force-send', 'Send immediately regardless of timing')
    .option('--dry-run', 'Classify only, don\'t send')
    .option('--context <text>', 'Additional context for classification')
    .action(async (message, options) => {
      try {
        const { classifyNotification, routeNotification } = await import('./notifications.js');
        
        const classification = await classifyNotification(message, {
          context: options.context,
          channel: options.channel
        });
        
        if (options.dryRun) {
          console.log(colors.bold('📋 Notification Classification'));
          console.log('');
          console.log(`**Priority:** ${classification.priority}`);
          console.log(`**Category:** ${classification.category}`);
          console.log(`**Urgency:** ${classification.urgency}`);
          console.log(`**Send Now:** ${classification.sendNow ? 'Yes' : 'No'}`);
          console.log(`**Channel:** ${classification.suggestedChannel}`);
          console.log(`**Reasoning:** ${classification.reasoning}`);
          
          if (classification.holdUntil) {
            console.log(`**Hold Until:** ${classification.holdUntil}`);
          }
          
          return;
        }
        
        // Route the notification
        const result = await routeNotification(message, classification, {
          forceSend: options.forceSend,
          targetChannel: options.channel
        });
        
        if (result.sent) {
          console.log(colors.green(`✅ Sent ${classification.priority} notification via ${result.channel}`));
        } else {
          console.log(colors.yellow(`🕐 Queued ${classification.priority} notification (${result.reason})`));
        }
        
      } catch (err) {
        console.log(colors.red(`Notification failed: ${err.message}`));
      }
    });

  program.command('pending-notifications')
    .description('Show queued notifications waiting for good timing (Phase 7: T-040)')
    .option('--send-all', 'Send all pending notifications now')
    .option('--json', 'Output as JSON')
    .action(async (options) => {
      try {
        const { getPendingNotifications, sendPendingNotifications } = await import('./notifications.js');
        
        const pending = getPendingNotifications();
        
        if (options.sendAll && pending.length > 0) {
          const results = await sendPendingNotifications();
          console.log(colors.green(`Sent ${results.sent} notification(s), ${results.held} still pending`));
          return;
        }
        
        if (options.json) {
          console.log(JSON.stringify(pending, null, 2));
          return;
        }
        
        if (pending.length === 0) {
          console.log(colors.green('No pending notifications'));
          return;
        }
        
        console.log(colors.bold(`📬 ${pending.length} Pending Notification(s)`));
        console.log('');
        
        pending.forEach((notif, idx) => {
          const icon = notif.priority === 'critical' ? '🚨' : notif.priority === 'high' ? '⚠️' : '📋';
          console.log(`${icon} **${notif.priority}** (${notif.category})`);
          console.log(`   ${notif.message.substring(0, 80)}${notif.message.length > 80 ? '...' : ''}`);
          console.log(`   Hold until: ${notif.hold_until || 'good timing'}`);
          console.log(`   Age: ${Math.floor((Date.now() - new Date(notif.created).getTime()) / (1000 * 60))}m`);
          console.log('');
        });
        
      } catch (err) {
        console.log(colors.red(`Pending notifications failed: ${err.message}`));
      }
    });

  program.command('digest')
    .description('Generate daily summary of everything while away (Phase 7: T-042)')
    .option('--days <n>', 'Look back N days', '1')
    .option('--format <fmt>', 'Output format: markdown, text, json', 'markdown')
    .option('--send', 'Send digest via notifications')
    .option('--channel <ch>', 'Channel for sending', 'dm')
    .action(async (options) => {
      try {
        const { generateDigest } = await import('./notifications.js');
        
        const days = parseInt(options.days, 10) || 1;
        const digest = await generateDigest(days, {
          format: options.format,
          includeMetrics: true
        });
        
        if (options.send) {
          const { routeNotification } = await import('./notifications.js');
          
          await routeNotification(digest.content, {
            priority: 'medium',
            category: 'system', 
            suggestedChannel: options.channel,
            sendNow: true
          });
          
          console.log(colors.green(`Digest sent via ${options.channel}`));
        } else {
          console.log(digest.content);
        }
        
      } catch (err) {
        console.log(colors.red(`Digest generation failed: ${err.message}`));
      }
    });

  program.command('batch-send')
    .description('Send batched low-priority notifications (Phase 7: T-043)')
    .option('--category <cat>', 'Send only specific category')
    .option('--force', 'Send all pending regardless of timing')
    .option('--max <n>', 'Max notifications to send', '10')
    .action(async (options) => {
      try {
        const { batchSendNotifications } = await import('./notifications.js');
        
        const result = await batchSendNotifications({
          category: options.category,
          force: options.force,
          maxCount: parseInt(options.max, 10) || 10
        });
        
        if (result.batched > 0) {
          console.log(colors.green(`📦 Sent batch: ${result.batched} notifications in ${result.messages} message(s)`));
        } else {
          console.log(colors.yellow('No notifications ready for batching'));
        }
        
        if (result.held > 0) {
          console.log(colors.dim(`${result.held} notifications still pending`));
        }
        
      } catch (err) {
        console.log(colors.red(`Batch send failed: ${err.message}`));
      }
    });

  program.command('self-review')
    .description('Weekly self-improvement review (Phase 8: T-048)')
    .option('--days <n>', 'Review period in days', '7')
    .option('--auto-inject', 'Automatically promote top lessons to context')
    .option('--save', 'Save review insights to facts')
    .action(async (options) => {
      try {
        const { generateSelfReview, analyzePatterns } = await import('./self-improvement.js');
        
        const days = parseInt(options.days, 10) || 7;
        const review = await generateSelfReview(days, {
          autoInject: options.autoInject,
          save: options.save
        });
        
        console.log(review.content);
        
        if (review.improvements > 0) {
          console.log('');
          console.log(colors.green(`✅ Made ${review.improvements} improvement(s)`));
        }
        
        if (review.patterns.length > 0) {
          console.log('');
          console.log(colors.yellow('🔍 Patterns detected:'));
          review.patterns.forEach(pattern => {
            console.log(`  • ${pattern.description} (${pattern.frequency}x)`);
          });
        }
        
      } catch (err) {
        console.log(colors.red(`Self-review failed: ${err.message}`));
      }
    });

  program.command('pattern-analysis')
    .description('Detect repetitive mistakes and behaviors (Phase 8: T-045)')
    .option('--days <n>', 'Analysis period in days', '30')
    .option('--min-frequency <n>', 'Minimum pattern frequency', '2')
    .option('--escalate', 'Auto-escalate critical patterns')
    .action(async (options) => {
      try {
        const { analyzePatterns, escalatePatterns } = await import('./self-improvement.js');
        
        const days = parseInt(options.days, 10) || 30;
        const minFreq = parseInt(options.minFrequency, 10) || 2;
        
        const patterns = await analyzePatterns(days, { minFrequency: minFreq });
        
        if (patterns.length === 0) {
          console.log(colors.green('No significant patterns detected'));
          return;
        }
        
        console.log(colors.bold(`🔍 Pattern Analysis (${days} days)`));
        console.log('');
        
        patterns.forEach(pattern => {
          const icon = pattern.severity === 'critical' ? '🚨' : 
                      pattern.severity === 'warning' ? '⚠️' : '📊';
          
          console.log(`${icon} **${pattern.type}** (${pattern.frequency}x)`);
          console.log(`   ${pattern.description}`);
          console.log(`   Trend: ${pattern.trend || 'stable'}`);
          
          if (pattern.suggestions) {
            console.log(`   💡 ${pattern.suggestions}`);
          }
          console.log('');
        });
        
        if (options.escalate) {
          const escalated = escalatePatterns(patterns);
          if (escalated.length > 0) {
            console.log(colors.red(`🚨 Escalated ${escalated.length} critical pattern(s)`));
          }
        }
        
      } catch (err) {
        console.log(colors.red(`Pattern analysis failed: ${err.message}`));
      }
    });

  program.command('skill-usage')
    .description('Track which skills are used vs neglected (Phase 8: T-047)')
    .option('--days <n>', 'Analysis period in days', '30')
    .option('--suggest', 'Suggest underused skills')
    .action(async (options) => {
      try {
        const { analyzeSkillUsage } = await import('./self-improvement.js');
        
        const days = parseInt(options.days, 10) || 30;
        const analysis = await analyzeSkillUsage(days, {
          suggest: options.suggest
        });
        
        console.log(colors.bold(`🛠️ Skill Usage Analysis (${days} days)`));
        console.log('');
        
        if (analysis.used.length > 0) {
          console.log(colors.bold('✅ Most Used Skills:'));
          analysis.used.slice(0, 10).forEach((skill, idx) => {
            console.log(`  ${idx + 1}. ${skill.skill} (${skill.count}x)`);
          });
          console.log('');
        }
        
        if (analysis.neglected.length > 0) {
          console.log(colors.bold('⚠️ Neglected Skills:'));
          analysis.neglected.slice(0, 5).forEach(skill => {
            console.log(`  • ${skill.skill} (last used: ${skill.lastUsed || 'never'})`);
          });
          console.log('');
        }
        
        if (options.suggest && analysis.suggestions.length > 0) {
          console.log(colors.bold('💡 Suggestions:'));
          analysis.suggestions.forEach(suggestion => {
            console.log(`  • ${suggestion}`);
          });
        }
        
      } catch (err) {
        console.log(colors.red(`Skill usage analysis failed: ${err.message}`));
      }
    });

  program.command('consolidate')
    .description('Memory consolidation - merge, compress, prioritize facts (Phase 9: T-049)')
    .option('--dry-run', 'Show what would be consolidated without changes')
    .option('--similarity-threshold <n>', 'Similarity threshold for merging (0.0-1.0)', '0.8')
    .option('--compress-long', 'Compress facts longer than 200 chars')
    .option('--auto-prioritize', 'Auto-prioritize by access patterns')
    .action(async (options) => {
      try {
        const { consolidateMemory } = await import('./advanced-memory.js');
        
        const result = await consolidateMemory({
          dryRun: options.dryRun,
          similarityThreshold: parseFloat(options.similarityThreshold) || 0.8,
          compressLong: options.compressLong,
          autoPrioritize: options.autoPrioritize
        });
        
        if (options.dryRun) {
          console.log(colors.bold('🔍 Consolidation Preview (Dry Run)'));
          console.log('');
          
          if (result.merges.length > 0) {
            console.log(colors.bold('Potential Merges:'));
            result.merges.forEach((merge, idx) => {
              console.log(`${idx + 1}. Merge ${merge.sources.length} similar facts:`);
              console.log(`   Key: ${merge.newKey}`);
              console.log(`   Value: ${merge.newValue.substring(0, 100)}...`);
              console.log('');
            });
          }
          
          if (result.compressions.length > 0) {
            console.log(colors.bold('Potential Compressions:'));
            result.compressions.forEach((comp, idx) => {
              console.log(`${idx + 1}. ${comp.key}: ${comp.oldLength} → ${comp.newLength} chars`);
            });
            console.log('');
          }
        } else {
          console.log(colors.green(`✅ Consolidation complete:`));
          console.log(`   • ${result.merged} fact(s) merged`);
          console.log(`   • ${result.compressed} fact(s) compressed`);
          console.log(`   • ${result.prioritized} fact(s) re-prioritized`);
          console.log(`   • Freed ${result.spaceSaved} characters`);
        }
        
      } catch (err) {
        console.log(colors.red(`Consolidation failed: ${err.message}`));
      }
    });

  program.command('forget')
    .description('Apply forgetting curve - reduce confidence and prune unused facts (Phase 9: T-050)')
    .option('--dry-run', 'Show what would be forgotten without changes')
    .option('--decay-rate <n>', 'Confidence decay rate per day', '0.05')
    .option('--prune-threshold <n>', 'Confidence threshold for pruning', '0.1')
    .option('--grace-days <n>', 'Grace period before decay starts', '30')
    .action(async (options) => {
      try {
        const { applyForgettingCurve } = await import('./advanced-memory.js');
        
        const result = await applyForgettingCurve({
          dryRun: options.dryRun,
          decayRate: parseFloat(options.decayRate) || 0.05,
          pruneThreshold: parseFloat(options.pruneThreshold) || 0.1,
          graceDays: parseInt(options.graceDays, 10) || 30
        });
        
        if (options.dryRun) {
          console.log(colors.bold('🧠 Forgetting Curve Preview (Dry Run)'));
          console.log('');
          
          if (result.toDecay.length > 0) {
            console.log(colors.bold('Facts with Reduced Confidence:'));
            result.toDecay.slice(0, 10).forEach(fact => {
              console.log(`   ${fact.key}: ${fact.oldConfidence.toFixed(3)} → ${fact.newConfidence.toFixed(3)}`);
            });
            if (result.toDecay.length > 10) {
              console.log(`   ...and ${result.toDecay.length - 10} more`);
            }
            console.log('');
          }
          
          if (result.toPrune.length > 0) {
            console.log(colors.bold('Facts to Archive (Low Confidence):'));
            result.toPrune.forEach(fact => {
              console.log(`   ${fact.key}: confidence ${fact.confidence.toFixed(3)} (unused for ${fact.daysSinceAccess} days)`);
            });
            console.log('');
          }
        } else {
          console.log(colors.green(`✅ Forgetting curve applied:`));
          console.log(`   • ${result.decayed} fact(s) had confidence reduced`);
          console.log(`   • ${result.archived} fact(s) archived to forgetting_archive`);
          console.log(`   • Average confidence change: ${result.avgDecay.toFixed(3)}`);
        }
        
      } catch (err) {
        console.log(colors.red(`Forgetting curve failed: ${err.message}`));
      }
    });

  program.command('temporal <query>')
    .description('Temporal queries - "what were we working on last Tuesday?" (Phase 9: T-051)')
    .option('--json', 'Output as JSON')
    .option('--limit <n>', 'Max results to return', '20')
    .action(async (query, options) => {
      try {
        const { executeTemporalQuery } = await import('./advanced-memory.js');
        
        const result = await executeTemporalQuery(query, {
          limit: parseInt(options.limit, 10) || 20
        });
        
        if (options.json) {
          console.log(JSON.stringify(result, null, 2));
          return;
        }
        
        console.log(colors.bold(`⏰ Temporal Query: "${query}"`));
        console.log('');
        
        if (!result.timeframe) {
          console.log(colors.yellow('Could not parse timeframe from query'));
          return;
        }
        
        console.log(`**Timeframe:** ${result.timeframe.description}`);
        console.log(`**Period:** ${result.timeframe.startDate} to ${result.timeframe.endDate}`);
        console.log('');
        
        if (result.facts.length > 0) {
          console.log(colors.bold('📋 Facts from that period:'));
          result.facts.forEach(fact => {
            console.log(`   ${fact.category}/${fact.key}: ${fact.value}`);
            console.log(colors.dim(`   (${fact.updated.substring(0, 10)})`));
          });
          console.log('');
        }
        
        if (result.events.length > 0) {
          console.log(colors.bold('📊 Events from that period:'));
          result.events.forEach(event => {
            const icon = event.event_type === 'success' ? '✅' : event.event_type === 'mistake' ? '❌' : '📝';
            console.log(`   ${icon} ${event.detail}`);
            console.log(colors.dim(`   (${event.created.substring(0, 10)})`));
          });
          console.log('');
        }
        
        if (result.projects.length > 0) {
          console.log(colors.bold('🚧 Projects active then:'));
          result.projects.forEach(project => {
            console.log(`   ${project.name}: ${project.phase} (${project.active_task || 'no active task'})`);
          });
          console.log('');
        }
        
        console.log(colors.dim(`${result.facts.length} fact(s), ${result.events.length} event(s), ${result.projects.length} project(s)`));
        
      } catch (err) {
        console.log(colors.red(`Temporal query failed: ${err.message}`));
      }
    });

  program.command('cross-session')
    .description('Cross-session reasoning - detect patterns across all sessions (Phase 9: T-052)')
    .option('--days <n>', 'Analysis period in days', '90')
    .option('--pattern-type <type>', 'Focus on specific pattern type')
    .option('--min-sessions <n>', 'Minimum sessions for pattern', '3')
    .action(async (options) => {
      try {
        const { analyzeCrossSessionPatterns } = await import('./advanced-memory.js');
        
        const result = await analyzeCrossSessionPatterns({
          days: parseInt(options.days, 10) || 90,
          patternType: options.patternType,
          minSessions: parseInt(options.minSessions, 10) || 3
        });
        
        console.log(colors.bold(`🔄 Cross-Session Pattern Analysis (${options.days} days)`));
        console.log('');
        
        if (result.sessionPatterns.length > 0) {
          console.log(colors.bold('📊 Session Patterns:'));
          result.sessionPatterns.forEach((pattern, idx) => {
            console.log(`${idx + 1}. **${pattern.trigger}** → **${pattern.outcome}**`);
            console.log(`   Frequency: ${pattern.frequency} sessions`);
            console.log(`   Confidence: ${(pattern.confidence * 100).toFixed(1)}%`);
            console.log(`   Example: ${pattern.example}`);
            console.log('');
          });
        }
        
        if (result.behaviorPatterns.length > 0) {
          console.log(colors.bold('🎯 Behavior Patterns:'));
          result.behaviorPatterns.forEach(pattern => {
            console.log(`   • ${pattern.description}`);
            console.log(`     Observed in ${pattern.sessionCount} session(s)`);
          });
          console.log('');
        }
        
        if (result.insights.length > 0) {
          console.log(colors.bold('💡 Cross-Session Insights:'));
          result.insights.forEach(insight => {
            console.log(`   • ${insight}`);
          });
        }
        
      } catch (err) {
        console.log(colors.red(`Cross-session analysis failed: ${err.message}`));
      }
    });

  program.command('decision-changelog [decision]')
    .description('Full audit trail of decision changes (Phase 9: T-053)')
    .option('--limit <n>', 'Max entries to show', '20')
    .option('--json', 'Output as JSON')
    .action(async (decision, options) => {
      try {
        const { getDecisionChangelog } = await import('./advanced-memory.js');
        
        const result = await getDecisionChangelog(decision, {
          limit: parseInt(options.limit, 10) || 20
        });
        
        if (options.json) {
          console.log(JSON.stringify(result, null, 2));
          return;
        }
        
        if (decision) {
          console.log(colors.bold(`📜 Decision History: "${decision}"`));
        } else {
          console.log(colors.bold('📜 All Decision Changes'));
        }
        console.log('');
        
        if (result.changes.length === 0) {
          console.log(colors.yellow('No decision changes found'));
          return;
        }
        
        result.changes.forEach((change, idx) => {
          const icon = change.change_type === 'created' ? '🆕' : 
                      change.change_type === 'updated' ? '📝' : 
                      change.change_type === 'contradicted' ? '🔄' : '❓';
          
          console.log(`${icon} **${change.key}** (${change.created.substring(0, 10)})`);
          
          if (change.change_type === 'created') {
            console.log(`   Initial: ${change.new_value}`);
          } else if (change.change_type === 'updated' || change.change_type === 'contradicted') {
            console.log(`   From: ${change.old_value}`);
            console.log(`   To: ${change.new_value}`);
          }
          
          if (change.source) {
            console.log(colors.dim(`   Source: ${change.source}`));
          }
          
          console.log('');
        });
        
        console.log(colors.dim(`${result.changes.length} change(s) shown`));
        
      } catch (err) {
        console.log(colors.red(`Decision changelog failed: ${err.message}`));
      }
    });

  program.command('recall <topic>')
    .description('Smart recall — pull all relevant context for a topic (facts, decisions, lessons, people, history)')
    .option('--json', 'Output as JSON for programmatic use')
    .option('--limit <n>', 'Max facts per section', '10')
    .action((topic, options) => {
      const db = openDb();
      const q = topic.toLowerCase();
      const limit = parseInt(options.limit, 10) || 10;

      // FTS search
      const ftsQuery = toFtsQuery(topic);
      let ftsResults = [];
      try {
        ftsResults = db.prepare(`
          SELECT f.*, bm25(facts_fts) as rank
          FROM facts_fts
          JOIN facts f ON f.id = facts_fts.rowid
          WHERE facts_fts MATCH ?
          ORDER BY bm25(facts_fts)
          LIMIT ?
        `).all(ftsQuery, limit * 3);
      } catch { /* FTS query might fail on special chars */ }

      // Fuzzy fallback
      const fuzzyResults = db.prepare(`
        SELECT * FROM facts
        WHERE LOWER(key) LIKE ? OR LOWER(value) LIKE ?
        ORDER BY updated DESC
        LIMIT ?
      `).all(`%${q}%`, `%${q}%`, limit * 3);

      // Merge and dedup
      const seen = new Set();
      const allFacts = [];
      for (const f of [...ftsResults, ...fuzzyResults]) {
        if (!seen.has(f.id)) {
          seen.add(f.id);
          allFacts.push(f);
        }
      }

      // Categorize
      const facts = allFacts.filter(f => !['decision', 'lesson', 'session'].includes(f.category)).slice(0, limit);
      const decisions = allFacts.filter(f => f.category === 'decision').slice(0, 5);
      const lessons = allFacts.filter(f => f.category === 'lesson').slice(0, 5);
      const people = allFacts.filter(f => f.category === 'person').slice(0, 5);

      // Get recent performance events
      const perfEvents = db.prepare(`
        SELECT * FROM performance_log
        WHERE LOWER(detail) LIKE ? OR LOWER(category) LIKE ?
        ORDER BY created DESC LIMIT 5
      `).all(`%${q}%`, `%${q}%`);

      // Get changelog
      const changes = db.prepare(`
        SELECT * FROM changelog
        WHERE LOWER(key) LIKE ? OR LOWER(old_value) LIKE ? OR LOWER(new_value) LIKE ?
        ORDER BY created DESC LIMIT 5
      `).all(`%${q}%`, `%${q}%`, `%${q}%`);

      if (options.json) {
        console.log(JSON.stringify({ topic, facts, decisions, lessons, people, events: perfEvents, changes }, null, 2));
        db.close();
        return;
      }

      const total = facts.length + decisions.length + lessons.length + people.length;
      if (total === 0 && perfEvents.length === 0 && changes.length === 0) {
        console.log(colors.yellow(`Nothing found for "${topic}"`));
        db.close();
        return;
      }

      console.log(colors.bold(`🧠 Recall: "${topic}"`));
      console.log('');

      if (facts.length > 0) {
        console.log(colors.bold('Facts:'));
        for (const f of facts) {
          console.log(`  ${f.category}/${f.key} = ${f.value}`);
        }
        console.log('');
      }

      if (decisions.length > 0) {
        console.log(colors.bold('Decisions:'));
        for (const d of decisions) {
          console.log(`  ⚖️  ${d.key}: ${d.value}`);
        }
        console.log('');
      }

      if (lessons.length > 0) {
        console.log(colors.bold('Lessons:'));
        for (const l of lessons) {
          console.log(`  💡 ${l.key}: ${l.value}`);
        }
        console.log('');
      }

      if (people.length > 0) {
        console.log(colors.bold('People:'));
        for (const p of people) {
          console.log(`  👤 ${p.key}: ${p.value}`);
        }
        console.log('');
      }

      if (perfEvents.length > 0) {
        console.log(colors.bold('Past Events:'));
        for (const e of perfEvents) {
          const icon = e.event_type === 'mistake' ? '❌' : e.event_type === 'success' ? '✅' : '📝';
          console.log(`  ${icon} ${e.event_type}: ${e.detail}`);
        }
        console.log('');
      }

      if (changes.length > 0) {
        console.log(colors.bold('Changes:'));
        for (const c of changes) {
          if (c.change_type === 'updated') {
            console.log(`  ~ ${c.key}: ${c.old_value} → ${c.new_value}`);
          }
        }
        console.log('');
      }

      console.log(colors.dim(`${total} fact(s) + ${perfEvents.length} event(s) + ${changes.length} change(s)`));
      db.close();
    });

  program.command('list')
    .description('List facts with optional filters')
    .option('--category <cat>', 'Filter category')
    .option('--scope <scope>', 'Filter by scope', parseScope)
    .option('--tier <tier>', 'Filter by tier', parseTier)
    .option('--limit <n>', 'Limit number of rows', parseLimit, DEFAULT_LIMIT)
    .option('--recent', 'Sort by most recently updated')
    .action((options) => {
      const db = openDb();
      const where = [];
      const params = [];

      if (options.category) {
        where.push('category = ?');
        params.push(options.category);
      }
      if (options.scope) {
        where.push('scope = ?');
        params.push(options.scope);
      }
      if (options.tier) {
        where.push('tier = ?');
        params.push(options.tier);
      }

      const whereSql = where.length ? `WHERE ${where.join(' AND ')}` : '';
      const orderSql = options.recent ? 'ORDER BY updated DESC' : 'ORDER BY category, key';
      const sql = `SELECT * FROM facts ${whereSql} ${orderSql} LIMIT ?`;
      const rows = db.prepare(sql).all(...params, options.limit);
      db.close();

      if (rows.length === 0) {
        throw new UserError('No facts found', 2);
      }
      printSimpleList(rows);
    });

  program.command('remove <category> <key>')
    .description('Delete a specific fact')
    .action((category, key) => {
      const db = openDb();
      const res = db.prepare('DELETE FROM facts WHERE category = ? AND key = ?').run(category, key);
      db.close();

      if (res.changes === 0) {
        throw new UserError('No matching fact to remove', 2);
      }
      console.log(colors.green('Fact removed'));
    });

  program.command('link <from> <to>')
    .description('Link two facts with a relation')
    .option('--type <relation_type>', 'related_to|part_of|decided_by|owned_by|replaced_by', parseRelationType, 'related_to')
    .action((from, to, options) => {
      const db = openDb();
      const fromFact = getFactByRef(db, from);
      const toFact = getFactByRef(db, to);

      db.prepare(`
        INSERT INTO relations (source_fact_id, target_fact_id, relation_type, created)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(source_fact_id, target_fact_id, relation_type) DO NOTHING
      `).run(fromFact.id, toFact.id, options.type, nowIso());

      db.close();
      console.log(colors.green(`Linked ${fromFact.category}/${fromFact.key} -> ${toFact.category}/${toFact.key} (${options.type})`));
    });

  program.command('graph <fact>')
    .description('Show a fact and connected facts')
    .action((factRef) => {
      const db = openDb();
      const root = getFactByRef(db, factRef);
      const rows = db.prepare(`
        SELECT r.relation_type, 'outgoing' AS direction, t.category, t.key, t.value
        FROM relations r
        JOIN facts t ON t.id = r.target_fact_id
        WHERE r.source_fact_id = ?
        UNION ALL
        SELECT r.relation_type, 'incoming' AS direction, s.category, s.key, s.value
        FROM relations r
        JOIN facts s ON s.id = r.source_fact_id
        WHERE r.target_fact_id = ?
        ORDER BY relation_type, direction, category, key
      `).all(root.id, root.id);
      db.close();

      console.log(colors.bold(`${root.category}/${root.key}`));
      console.log(root.value);

      if (rows.length === 0) {
        console.log(colors.dim('No relations'));
        return;
      }

      for (const row of rows) {
        const arrow = row.direction === 'outgoing' ? '->' : '<-';
        console.log(`${arrow} (${row.relation_type}) ${row.category}/${row.key}: ${row.value}`);
      }
    });

  program.command('who [query]')
    .description('People directory — look up a person or list all known people')
    .option('--list', 'List all known people')
    .option('--alias <alias> <canonical>', 'Create an alias for a person')
    .option('--json', 'Output as JSON')
    .action((query, options) => {
      const db = openDb();

      // Get all person facts
      const allPersonFacts = db.prepare("SELECT * FROM facts WHERE category = 'person' ORDER BY key").all();

      if (options.list || !query) {
        // Group by person name (first segment of key)
        const people = new Map();
        for (const fact of allPersonFacts) {
          const person = fact.key.split('.')[0];
          if (!people.has(person)) people.set(person, []);
          people.get(person).push(fact);
        }

        if (people.size === 0) {
          console.log(colors.yellow('No people in memory'));
          db.close();
          return;
        }

        if (options.json) {
          const out = {};
          for (const [name, facts] of people) {
            out[name] = Object.fromEntries(facts.map(f => [f.key.replace(name + '.', ''), f.value]));
          }
          console.log(JSON.stringify(out, null, 2));
          db.close();
          return;
        }

        console.log(colors.bold(`Known People (${people.size})`));
        console.log('');
        for (const [name, facts] of people) {
          const nameFact = facts.find(f => f.key === name + '.name' || f.key === name + '.relationship');
          const label = nameFact ? nameFact.value : name;
          const attrCount = facts.length;
          const lastUpdated = facts.reduce((latest, f) => f.updated > latest ? f.updated : latest, '');
          console.log(`  ${colors.bold(name.toUpperCase())} — ${label} (${attrCount} facts, updated ${lastUpdated.split('T')[0]})`);
        }
        db.close();
        return;
      }

      // Fuzzy search for a person
      const q = query.toLowerCase();

      // Check aliases first
      const aliasFact = allPersonFacts.find(f =>
        f.key.endsWith('.alias') && f.value.toLowerCase() === q
      );
      const resolvedQuery = aliasFact ? aliasFact.key.split('.')[0] : q;

      // Find matching person — prioritize exact name match, then fuzzy
      const matched = new Map();
      // Pass 1: exact name prefix match
      for (const fact of allPersonFacts) {
        const person = fact.key.split('.')[0];
        if (person.toLowerCase() === resolvedQuery) {
          if (!matched.has(person)) matched.set(person, []);
        }
      }
      // Pass 2: if no exact match, try fuzzy (value/key contains query)
      if (matched.size === 0) {
        for (const fact of allPersonFacts) {
          const person = fact.key.split('.')[0];
          const keyMatch = person.toLowerCase().includes(resolvedQuery);
          const valueMatch = fact.value.toLowerCase().includes(resolvedQuery);
          if (keyMatch || valueMatch) {
            if (!matched.has(person)) matched.set(person, []);
          }
        }
      }

      // Now collect ALL facts for matched people
      for (const person of matched.keys()) {
        const personFacts = allPersonFacts.filter(f => f.key.startsWith(person + '.'));
        matched.set(person, personFacts);
      }

      if (matched.size === 0) {
        console.log(colors.yellow(`No person matching "${query}"`));
        db.close();
        return;
      }

      // Get relations per person
      function getRelationsForFacts(db, factIds) {
        if (factIds.length === 0) return [];
        const placeholders = factIds.map(() => '?').join(',');
        return db.prepare(`
          SELECT DISTINCT f.*, r.relation_type
          FROM relations r
          JOIN facts f ON (
            CASE WHEN r.source_fact_id IN (${placeholders})
              THEN f.id = r.target_fact_id
              ELSE f.id = r.source_fact_id
            END
          )
          WHERE r.source_fact_id IN (${placeholders}) OR r.target_fact_id IN (${placeholders})
        `).all(...factIds, ...factIds, ...factIds);
      }

      if (options.json) {
        const out = {};
        for (const [name, facts] of matched) {
          const personRelations = getRelationsForFacts(db, facts.map(f => f.id));
          out[name] = {
            attributes: Object.fromEntries(facts.map(f => [f.key.replace(name + '.', ''), f.value])),
            relations: personRelations.map(rf => ({ type: rf.relation_type, category: rf.category, key: rf.key, value: rf.value }))
          };
        }
        console.log(JSON.stringify(out, null, 2));
        db.close();
        return;
      }

      // Render profile cards
      for (const [name, facts] of matched) {
        const personRelations = getRelationsForFacts(db, facts.map(f => f.id));
        const width = 50;
        const border = '═'.repeat(width - 2);
        const pad = (text) => text + ' '.repeat(Math.max(0, width - text.length - 4));

        console.log(`╔${border}╗`);
        console.log(`║  ${pad(colors.bold(name.toUpperCase()))}║`);
        console.log(`╠${border}╣`);

        for (const fact of facts) {
          const attr = fact.key.replace(name + '.', '');
          const line = `${attr}: ${fact.value}`;
          const truncated = line.length > width - 6 ? line.slice(0, width - 9) + '...' : line;
          console.log(`║  ${pad(truncated)}║`);
        }

        if (personRelations.length > 0) {
          console.log(`║${' '.repeat(width - 2)}║`);
          console.log(`║  ${pad(colors.dim('Related:'))}║`);
          for (const rf of personRelations.slice(0, 5)) {
            const line = `• ${rf.category}/${rf.key}: ${rf.value}`;
            const truncated = line.length > width - 6 ? line.slice(0, width - 9) + '...' : line;
            console.log(`║  ${pad(truncated)}║`);
          }
        }

        const lastUpdated = facts.reduce((latest, f) => f.updated > latest ? f.updated : latest, '');
        console.log(`║${' '.repeat(width - 2)}║`);
        console.log(`║  ${pad(colors.dim(`Last updated: ${lastUpdated.split('T')[0]}`))}║`);
        console.log(`╚${border}╝`);
        console.log('');
      }

      db.close();
    });

  program.command('working')
    .description('List all working memory facts and TTL status')
    .action(() => {
      const db = openDb();
      const rows = db.prepare(`
        SELECT *
        FROM facts
        WHERE tier = 'working'
        ORDER BY CASE WHEN expires_at IS NULL THEN 1 ELSE 0 END, expires_at ASC, updated DESC
      `).all();
      db.close();

      if (rows.length === 0) {
        throw new UserError('No working-memory facts found', 2);
      }

      for (const fact of rows) {
        console.log(`${colors.bold(`${fact.category}/${fact.key}`)} = ${fact.value} ${colors.dim(`[${expiresLabel(fact.expires_at)}]`)}`);
      }
      console.log(colors.dim(`${rows.length} fact(s)`));
    });

  program.command('expire')
    .description('Prune facts whose TTL has expired')
    .action(() => {
      const db = openDb();
      const res = db.prepare("DELETE FROM facts WHERE tier = 'working' AND expires_at IS NOT NULL AND expires_at <= ?").run(nowIso());
      db.close();

      console.log(colors.green(`Expired ${res.changes} fact(s)`));
    });

  program.command('inject')
    .description('Generate markdown for LLM injection')
    .option('--max <n>', 'Maximum facts', parseLimit, DEFAULT_LIMIT)
    .option('--scope <scope>', 'Filter by scope', parseScope)
    .option('--project <slug>', 'Inject global + project-scoped facts tagged for this project')
    .option('--include-working', 'Include working memory (default is long-term only)')
    .option('--output <file>', 'Write markdown to file')
    .action((options) => {
      const db = openDb();
      const where = ['(expires_at IS NULL OR expires_at > ?)'];
      const params = [nowIso()];

      if (options.scope) {
        where.push('scope = ?');
        params.push(options.scope);
      }

      if (!options.includeWorking) {
        where.push("tier = 'long-term'");
      }

      if (options.project) {
        where.push(`(scope = 'global' OR (scope = 'project' AND source LIKE ?))`);
        params.push(`%${projectTag(options.project)}%`);
      }

      const sql = `
        SELECT * FROM facts
        WHERE ${where.join(' AND ')}
        ORDER BY CASE WHEN tier = 'working' THEN 0 ELSE 1 END, updated DESC
        LIMIT ?
      `;
      const rows = db.prepare(sql).all(...params, options.max);
      db.close();

      const markdown = factsToMarkdown(rows);
      if (options.output) {
        fs.writeFileSync(options.output, markdown, 'utf8');
        console.log(colors.green(`Wrote ${rows.length} fact(s) to ${options.output}`));
      } else {
        process.stdout.write(markdown);
      }
    });

  program.command('extract <file>')
    .description('Extract facts and session summary from a markdown file')
    .option('--dry-run', 'Print extracted facts without writing')
    .option('--engine <engine>', 'Extraction engine: anthropic, openai, ollama, or auto (default: auto)', 'auto')
    .option('--model <model>', 'Model name (default depends on engine)')
    .option('--force', 'Re-extract even if file was already processed')
    .option('--verbose', 'Show extraction prompt and raw model response')
    .action(async (file, options) => {
      requireFile(file);
      const res = await runExtractOne(file, options);
      if (!options.dryRun) {
        console.log(colors.green(`Stored ${res.facts} extracted fact(s)`));
      }
    });

  program.command('extract-all <directory>')
    .description('Batch extract facts from markdown files in a directory')
    .option('--pattern <glob>', 'File pattern', '*.md')
    .option('--since <date>', 'Only process files modified after date (ISO)')
    .option('--dry-run', 'Print extracted facts without writing')
    .option('--engine <engine>', 'Extraction engine: anthropic, openai, ollama, or auto (default: auto)', 'auto')
    .option('--model <model>', 'Model name (default depends on engine)')
    .option('--force', 'Re-extract even if files were already processed')
    .option('--verbose', 'Show extraction prompt and raw model response')
    .action(async (directory, options) => {
      requireDirectory(directory);
      const sinceIso = options.since ? parseDate(options.since) : null;
      const files = listFilesRecursive(directory, options.pattern, sinceIso);
      if (files.length === 0) {
        console.log(colors.yellow('No files matched'));
        return;
      }

      let totalFacts = 0;
      let totalInserted = 0;
      let totalUpdated = 0;
      let totalSkipped = 0;
      let totalSummaries = 0;
      let totalSkippedFiles = 0;
      for (const file of files) {
        try {
          const res = await runExtractOne(file, options);
          totalFacts += res.facts;
          totalInserted += res.inserted;
          totalUpdated += res.updated;
          totalSkipped += res.skipped;
          totalSummaries += res.summaryStored ? 1 : 0;
          if (res.skippedFile) totalSkippedFiles += 1;
        } catch (err) {
          console.log(colors.red(`${file}: ${err.message || String(err)}`));
        }
      }

      const header = options.dryRun ? 'Batch dry-run complete' : 'Batch extract complete';
      const processed = files.length - totalSkippedFiles;
      const counts = `files=${files.length} processed=${processed} skipped_unchanged=${totalSkippedFiles} facts=${totalFacts} inserted=${totalInserted} updated=${totalUpdated} skipped=${totalSkipped} summaries=${totalSummaries}`;
      console.log(colors.green(`${header}: ${counts}`));
    });

  program.command('import <file>')
    .description('Import facts from JSON file')
    .action((file) => {
      requireFile(file);
      let data;
      try {
        data = JSON.parse(fs.readFileSync(file, 'utf8'));
      } catch {
        throw new UserError('Import file is not valid JSON');
      }
      if (!Array.isArray(data)) {
        throw new UserError('Import JSON must be an array of facts');
      }

      const clean = [];
      for (const item of data) {
        if (!item || typeof item !== 'object') {
          continue;
        }

        const {
          category,
          key,
          value,
          source = null,
          confidence = 1.0,
          scope = 'global',
          tier = 'long-term',
          ttl = null,
          expires_at: expiresAt = null,
          source_type: sourceType = 'manual'
        } = item;

        if (
          typeof category !== 'string' || !category.trim() ||
          typeof key !== 'string' || !key.trim() ||
          typeof value !== 'string' || !value.trim()
        ) {
          continue;
        }

        const conf = Number(confidence);
        if (!Number.isFinite(conf) || conf < 0 || conf > 1) {
          continue;
        }

        if (!VALID_SCOPES.has(scope) || !VALID_TIERS.has(tier) || !VALID_SOURCE_TYPES.has(sourceType)) {
          continue;
        }

        let finalExpiresAt = null;
        try {
          if (ttl != null) {
            finalExpiresAt = ttlToExpiresAt(String(ttl));
          } else if (expiresAt != null) {
            finalExpiresAt = parseDate(String(expiresAt));
          }
        } catch {
          continue;
        }

        clean.push({
          category: category.trim(),
          key: key.trim(),
          value: value.trim(),
          source: source == null ? null : String(source),
          confidence: conf,
          scope,
          tier,
          expires_at: finalExpiresAt,
          source_type: sourceType
        });
      }

      if (clean.length === 0) {
        throw new UserError('No valid facts found in import file');
      }

      const db = openDb();
      const tx = db.transaction((items) => {
        for (const fact of items) {
          upsertFact(db, fact);
        }
      });
      tx(clean);
      db.close();
      console.log(colors.green(`Imported ${clean.length} fact(s)`));
    });

  program.command('export')
    .description('Export all facts')
    .option('--format <fmt>', 'Export format: json or md', 'json')
    .action((options) => {
      if (!['json', 'md'].includes(options.format)) {
        throw new UserError('Format must be json or md');
      }
      const db = openDb();
      const rows = db.prepare('SELECT * FROM facts ORDER BY category, key').all();
      db.close();

      if (options.format === 'json') {
        process.stdout.write(`${JSON.stringify(rows, null, 2)}\n`);
        return;
      }
      process.stdout.write(factsToMarkdown(rows));
    });

  program.command('why <query>')
    .description('Look up why a decision was made — searches decisions, lessons, and changelog')
    .action((query, options) => {
      const db = openDb();
      const q = query.toLowerCase();

      // Search decisions
      const decisions = db.prepare(
        "SELECT * FROM facts WHERE category IN ('decision', 'lesson') AND (LOWER(key) LIKE ? OR LOWER(value) LIKE ?) ORDER BY updated DESC"
      ).all(`%${q}%`, `%${q}%`);

      // Search changelog for related changes
      const changes = db.prepare(
        "SELECT * FROM changelog WHERE LOWER(key) LIKE ? OR LOWER(old_value) LIKE ? OR LOWER(new_value) LIKE ? ORDER BY created DESC LIMIT 10"
      ).all(`%${q}%`, `%${q}%`, `%${q}%`);

      if (decisions.length === 0 && changes.length === 0) {
        console.log(colors.yellow(`No decisions or history found for "${query}"`));
        db.close();
        return;
      }

      if (decisions.length > 0) {
        console.log(colors.bold(`Decisions & Lessons (${decisions.length})`));
        console.log('');
        for (const d of decisions) {
          const icon = d.category === 'decision' ? '⚖️' : '💡';
          const date = d.updated.split('T')[0];
          const source = d.source ? ` (source: ${d.source})` : '';
          console.log(`${icon}  ${colors.bold(d.key)}`);
          console.log(`   ${d.value}`);
          console.log(colors.dim(`   ${date} | ${d.scope} | confidence ${d.confidence.toFixed(2)}${source}`));
          console.log('');
        }
      }

      if (changes.length > 0) {
        console.log(colors.bold(`Change History (${changes.length})`));
        for (const c of changes) {
          const date = c.created.split('T')[0];
          if (c.change_type === 'created') {
            console.log(`${colors.green('+')} ${colors.dim(date)} ${c.category}/${c.key} = ${c.new_value}`);
          } else {
            console.log(`${colors.yellow('~')} ${colors.dim(date)} ${c.category}/${c.key}: ${colors.red(c.old_value)} → ${colors.green(c.new_value)}`);
          }
        }
      }

      db.close();
    });

  program.command('history [key]')
    .description('Show change history for a fact or all recent changes')
    .option('--limit <n>', 'Max entries to show', '20')
    .action((key, options) => {
      const db = openDb();
      const limit = parseInt(options.limit, 10) || 20;
      let rows;
      if (key) {
        rows = db.prepare('SELECT * FROM changelog WHERE key LIKE ? ORDER BY created DESC LIMIT ?').all(`%${key}%`, limit);
      } else {
        rows = db.prepare('SELECT * FROM changelog ORDER BY created DESC LIMIT ?').all(limit);
      }
      if (rows.length === 0) {
        console.log(colors.yellow('No change history found'));
        db.close();
        return;
      }
      for (const row of rows) {
        const date = row.created.split('T')[0];
        if (row.change_type === 'created') {
          console.log(`${colors.green('+')} ${colors.dim(date)} ${row.category}/${row.key} = ${row.new_value}`);
        } else {
          console.log(`${colors.yellow('~')} ${colors.dim(date)} ${row.category}/${row.key}: ${colors.red(row.old_value)} → ${colors.green(row.new_value)}`);
        }
      }
      console.log(colors.dim(`\n${rows.length} change(s)`));
      db.close();
    });

  program.command('log <type> <detail>')
    .description('Log a performance event (mistake, success, skill-used, forgot, pattern)')
    .option('--severity <level>', 'Severity: info, warning, error', 'info')
    .option('--category <cat>', 'Category for grouping')
    .action((type, detail, options) => {
      const validTypes = ['mistake', 'success', 'skill-used', 'forgot', 'pattern', 'lesson', 'feedback'];
      if (!validTypes.includes(type)) {
        console.log(colors.red(`Invalid type. Use: ${validTypes.join(', ')}`));
        return;
      }
      const db = openDb();
      db.prepare(`
        INSERT INTO performance_log (event_type, category, detail, severity, created)
        VALUES (?, ?, ?, ?, datetime('now'))
      `).run(type, options.category || null, detail, options.severity);
      db.close();
      console.log(colors.green(`Logged: ${type} — ${detail}`));
    });

  program.command('review')
    .description('Self-review: show performance patterns, recurring mistakes, skill gaps')
    .option('--days <n>', 'Look back N days', '7')
    .action((options) => {
      const db = openDb();
      const days = parseInt(options.days, 10) || 7;
      const since = new Date(Date.now() - days * 86400000).toISOString();

      // Get all events in window
      const events = db.prepare(
        "SELECT * FROM performance_log WHERE created >= ? ORDER BY created DESC"
      ).all(since);

      // Count by type
      const typeCounts = {};
      for (const e of events) {
        typeCounts[e.event_type] = (typeCounts[e.event_type] || 0) + 1;
      }

      // Find recurring patterns (same detail appearing 2+)
      const detailCounts = {};
      for (const e of events) {
        const key = `${e.event_type}:${e.detail}`;
        detailCounts[key] = (detailCounts[key] || 0) + 1;
      }
      const recurring = Object.entries(detailCounts).filter(([, c]) => c >= 2).sort((a, b) => b[1] - a[1]);

      // Get fact changes in window
      const factChanges = db.prepare(
        "SELECT change_type, COUNT(*) as n FROM changelog WHERE created >= ? GROUP BY change_type"
      ).all(since);

      // Get extraction stats
      const extractions = db.prepare(
        "SELECT COUNT(*) as n, SUM(facts_extracted) as total_facts, AVG(duration_ms) as avg_ms FROM extraction_log WHERE created >= ?"
      ).get(since);

      console.log(colors.bold(`Self-Review — Last ${days} Days`));
      console.log('');

      if (Object.keys(typeCounts).length > 0) {
        console.log(colors.bold('Performance Events:'));
        for (const [type, count] of Object.entries(typeCounts).sort((a, b) => b[1] - a[1])) {
          const icon = type === 'mistake' ? '❌' : type === 'success' ? '✅' : type === 'forgot' ? '🧠' : type === 'skill-used' ? '🔧' : '📝';
          console.log(`  ${icon} ${type}: ${count}`);
        }
        console.log('');
      }

      if (recurring.length > 0) {
        console.log(colors.bold('⚠️  Recurring Patterns:'));
        for (const [key, count] of recurring.slice(0, 5)) {
          console.log(`  ${count}x — ${key}`);
        }
        console.log('');
      }

      if (factChanges.length > 0) {
        console.log(colors.bold('Fact Changes:'));
        for (const row of factChanges) {
          console.log(`  ${row.change_type}: ${row.n}`);
        }
        console.log('');
      }

      if (extractions && extractions.n > 0) {
        console.log(colors.bold('Extractions:'));
        console.log(`  Runs: ${extractions.n} | Facts: ${extractions.total_facts || 0} | Avg: ${Math.round(extractions.avg_ms || 0)}ms`);
        console.log('');
      }

      if (events.length === 0 && factChanges.length === 0) {
        console.log(colors.yellow('No activity logged yet. Use "rune log" to track events.'));
      }

      // Top lessons from facts
      const lessons = db.prepare(
        "SELECT key, value FROM facts WHERE category = 'lesson' ORDER BY updated DESC LIMIT 5"
      ).all();
      if (lessons.length > 0) {
        console.log(colors.bold('Top Lessons:'));
        for (const l of lessons) {
          console.log(`  💡 ${l.key}: ${l.value}`);
        }
      }

      db.close();
    });

  program.command('stats')
    .description('Show memory stats')
    .action(() => {
      const db = openDb();
      const total = db.prepare('SELECT COUNT(*) AS n FROM facts').get().n;
      const byCategory = db.prepare('SELECT category, COUNT(*) AS n FROM facts GROUP BY category ORDER BY category').all();
      const byScope = db.prepare('SELECT scope, COUNT(*) AS n FROM facts GROUP BY scope ORDER BY scope').all();
      const byTier = db.prepare('SELECT tier, COUNT(*) AS n FROM facts GROUP BY tier ORDER BY tier').all();
      const latest = db.prepare('SELECT MAX(updated) AS last_updated FROM facts').get().last_updated;
      db.close();

      let dbSize = 0;
      if (fs.existsSync(DB_PATH)) {
        dbSize = fs.statSync(DB_PATH).size;
      }

      console.log(`${colors.bold('DB:')} ${DB_PATH}`);
      console.log(`${colors.bold('Total facts:')} ${total}`);
      console.log(`${colors.bold('DB size:')} ${dbSize} bytes`);
      console.log(`${colors.bold('Last updated:')} ${latest ?? 'n/a'}`);
      console.log(colors.bold('By category:'));
      for (const row of byCategory) {
        console.log(`- ${row.category}: ${row.n}`);
      }
      console.log(colors.bold('By scope:'));
      for (const row of byScope) {
        console.log(`- ${row.scope}: ${row.n}`);
      }
      console.log(colors.bold('By tier:'));
      for (const row of byTier) {
        console.log(`- ${row.tier}: ${row.n}`);
      }
    });

  program.command('prune')
    .description('Remove old and/or low-confidence facts')
    .option('--before <date>', 'Delete facts updated before this ISO date')
    .option('--confidence-below <n>', 'Delete facts with confidence below n')
    .action((options) => {
      if (!options.before && options.confidenceBelow == null) {
        throw new UserError('Provide at least one filter: --before or --confidence-below');
      }

      const where = [];
      const params = [];
      if (options.before) {
        where.push('updated < ?');
        params.push(parseDate(options.before));
      }
      if (options.confidenceBelow != null) {
        const conf = parseConfidence(options.confidenceBelow);
        where.push('confidence < ?');
        params.push(conf);
      }

      const db = openDb();
      const res = db.prepare(`DELETE FROM facts WHERE ${where.join(' AND ')}`).run(...params);
      db.close();

      console.log(colors.green(`Pruned ${res.changes} fact(s)`));
    });

  program.command('test [suite]')
    .description('Run test and benchmark suites (unit, extract, recall, perf, e2e, all)')
    .option('--save', 'Save results to benchmark history')
    .option('--compare', 'Compare current results against last saved run')
    .option('--verbose', 'Show detailed suite output')
    .option('--db <path>', 'Use alternate base DB path for test suites', '/tmp/rune-test.db')
    .option('--model <model>', 'Ollama model for extraction benchmarks', 'qwen3:8b')
    .action(async (suite = 'all', options) => {
      const outcome = await runTestSuites(suite, options);
      if (!outcome.ok) {
        process.exitCode = 1;
      }
    });

  program.configureOutput({
    outputError: (str, write) => write(colors.red(str))
  });

  const fatal = (err) => {
    if (err instanceof UserError) {
      console.error(colors.red(`Error: ${err.message}`));
      process.exit(err.exitCode ?? 1);
    }
    console.error(colors.red(`Error: ${err.message || 'Unknown error'}`));
    process.exit(1);
  };

  program.parseAsync(argv).catch(fatal);
}
