#!/usr/bin/env node
// scripts/status.js – Health check, stats overview, social pulse
const { initSchema, getState } = require('../lib/db');
const path = require('path');
const fs = require('fs');

function main() {
  const db = initSchema();
  const dbPath = path.resolve(__dirname, '..', 'data', 'secondmind.db');

  let dbSize = '?';
  try { dbSize = (fs.statSync(dbPath).size / 1024).toFixed(1); } catch {}

  console.log('🧠 SecondMind Status\n');
  console.log(`Database: ${dbPath} (${dbSize} KB)`);

  // Buffer
  const b = db.prepare(`
    SELECT COUNT(*) as total,
           SUM(CASE WHEN processed=0 THEN 1 ELSE 0 END) as unprocessed,
           COALESCE(SUM(token_count), 0) as tokens
    FROM shortterm_buffer
  `).get();
  console.log(`\n📥 Buffer: ${b.total} total, ${b.unprocessed || 0} unprocessed, ${b.tokens} tokens`);

  // Knowledge
  const k = db.prepare(`
    SELECT category, COUNT(*) as c FROM knowledge_entries
    GROUP BY category ORDER BY c DESC
  `).all();
  console.log(`\n📚 Knowledge: ${k.reduce((s, x) => s + x.c, 0)} entries`);
  for (const x of k) console.log(`   ${x.category}: ${x.c}`);

  // Archive
  const a = db.prepare('SELECT COUNT(*) as c FROM longterm_archive').get();
  console.log(`\n🗄️  Archive: ${a.c} entries`);

  // Proposals
  const p = db.prepare(`
    SELECT status, COUNT(*) as c FROM proposals
    GROUP BY status ORDER BY c DESC
  `).all();
  console.log(`\n💡 Proposals: ${p.reduce((s, x) => s + x.c, 0)} total`);
  for (const x of p) console.log(`   ${x.status}: ${x.c}`);

  // Projects
  try {
    const proj = db.prepare(`
      SELECT status, COUNT(*) as c FROM projects
      GROUP BY status ORDER BY c DESC
    `).all();
    if (proj.length > 0) {
      console.log(`\n📦 Projects: ${proj.reduce((s, x) => s + x.c, 0)} total`);
      for (const x of proj) console.log(`   ${x.status}: ${x.c}`);
    }
  } catch { /* table might not exist yet */ }

  // === SOZIALE INTELLIGENZ ===
  try {
    const emoCount = db.prepare('SELECT COUNT(*) as c FROM social_context').get();
    const evtCount = db.prepare('SELECT COUNT(*) as c FROM social_events').get();

    if (emoCount.c > 0 || evtCount.c > 0) {
      console.log(`\n🎭 Soziale Intelligenz:`);
      console.log(`   Emotionen erfasst: ${emoCount.c}`);
      console.log(`   Events/Termine: ${evtCount.c}`);

      const moods = db.prepare(`
        SELECT mood, COUNT(*) as c FROM social_context
        WHERE detected_at > datetime('now', '-7 days')
        GROUP BY mood ORDER BY c DESC LIMIT 5
      `).all();
      if (moods.length > 0) {
        const mi = {
          frustration:'😤', excitement:'🎉', worry:'😰', celebration:'🥳',
          stress:'😫', curiosity:'🤔', boredom:'😴', gratitude:'🙏'
        };
        console.log('   Stimmung (7d): ' +
          moods.map(m => `${mi[m.mood]||'❓'}${m.mood}(${m.c})`).join(' '));
      }

      try {
        const stale = db.prepare('SELECT COUNT(*) as c FROM v_stale_frustrations WHERE days_ago > 3').get();
        if (stale.c > 0) console.log(`   ⚠️  ${stale.c} ungelöste Frustration(en) > 3 Tage`);
      } catch {}

      try {
        const upcoming = db.prepare('SELECT person, event_type, description, days_until FROM v_upcoming_events').all();
        if (upcoming.length > 0) {
          console.log('   📅 Anstehend:');
          for (const e of upcoming)
            console.log(`      ${e.person}: ${e.description || e.event_type} (${e.days_until}d)`);
        }
      } catch {}
    }
  } catch { /* social tables may not exist on first run */ }

  // Last runs
  console.log('\n⏰ Letzte Läufe:');
  for (const key of ['last_ingest', 'last_consolidate', 'last_archive', 'last_initiative']) {
    const val = getState(key);
    console.log(`   ${key.replace('last_', '').padEnd(12)}: ${val || 'nie'}`);
  }
}
main();
