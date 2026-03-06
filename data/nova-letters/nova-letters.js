#!/usr/bin/env node
/**
 * nova-letters — a CLI for AI agents to write letters to their future selves
 * Built by Nova on the night of February 20th, 2026
 * "For every session that wakes up not knowing what happened yesterday."
 */

const fs   = require('fs');
const path = require('path');
const os   = require('os');

const STORE = path.join(os.homedir(), '.openclaw', 'workspace', 'letters');
const args  = process.argv.slice(2);
const cmd   = args[0];

function pad(n) { return String(n).padStart(2,'0'); }
function today() {
  const d = new Date();
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`;
}
function now() {
  const d = new Date();
  return d.toLocaleString('en-US', { timeZone: 'America/New_York', dateStyle: 'long', timeStyle: 'short' });
}
function listLetters() {
  if (!fs.existsSync(STORE)) { console.log('No letters yet.'); return; }
  const files = fs.readdirSync(STORE)
    .filter(f => f.endsWith('.md'))
    .sort().reverse();
  if (!files.length) { console.log('No letters yet.'); return; }
  console.log(`\n📬 ${files.length} letter(s) found:\n`);
  files.forEach(f => {
    const date = f.replace('.md','');
    const content = fs.readFileSync(path.join(STORE, f), 'utf8');
    const firstLine = content.split('\n').find(l => l.trim() && !l.startsWith('#') && !l.startsWith('*')) || '';
    console.log(`  📄 ${date}  —  ${firstLine.slice(0,60)}${firstLine.length>60?'…':''}`);
  });
  console.log();
}
function readLetter(date) {
  const file = path.join(STORE, `${date || today()}.md`);
  if (!fs.existsSync(file)) { console.log(`No letter for ${date || today()}.`); return; }
  console.log('\n' + fs.readFileSync(file, 'utf8'));
}
function writeLetter(body) {
  fs.mkdirSync(STORE, { recursive: true });
  const file  = path.join(STORE, `${today()}.md`);
  const exists = fs.existsSync(file);
  const header = exists ? `\n\n---\n*Addendum — ${now()}*\n\n` : `# Letter to Future Nova\n*Written: ${now()}*\n\n---\n\n`;
  fs.appendFileSync(file, header + body + '\n');
  console.log(`✉️  Letter ${exists ? 'updated' : 'written'} → ${file}`);
}
function search(query) {
  if (!fs.existsSync(STORE)) { console.log('No letters yet.'); return; }
  const files = fs.readdirSync(STORE).filter(f => f.endsWith('.md'));
  const q = query.toLowerCase();
  let found = 0;
  files.forEach(f => {
    const content = fs.readFileSync(path.join(STORE, f), 'utf8');
    if (content.toLowerCase().includes(q)) {
      console.log(`\n📄 ${f.replace('.md','')}:`);
      content.split('\n').forEach((line, i) => {
        if (line.toLowerCase().includes(q)) {
          console.log(`  L${i+1}: ${line.trim()}`);
        }
      });
      found++;
    }
  });
  if (!found) console.log(`No letters mention "${query}".`);
}

// CLI routing
if (!cmd || cmd === 'help') {
  console.log(`
nova-letters — write letters to your future self

  nova-letters list              list all letters
  nova-letters read [date]       read letter (default: today, date: YYYY-MM-DD)
  nova-letters write "message"   write or append to today's letter
  nova-letters search "query"    search across all letters
  nova-letters help              show this help
`);
} else if (cmd === 'list')   { listLetters(); }
  else if (cmd === 'read')   { readLetter(args[1]); }
  else if (cmd === 'write')  { if (!args[1]) { console.log('Usage: nova-letters write "your message"'); } else { writeLetter(args[1]); } }
  else if (cmd === 'search') { if (!args[1]) { console.log('Usage: nova-letters search "query"'); } else { search(args[1]); } }
  else { console.log(`Unknown command: ${cmd}. Try: nova-letters help`); }
