#!/usr/bin/env node
import { Command } from 'commander';
import { getDb } from './db.js';
import { startConversation, endConversation, listConversations } from './conversations.js';
import { addTranscriptLine, showTranscript } from './transcripts.js';
import { listProfiles, addProfile, setDefaultProfile, getDefaultProfile } from './profiles.js';
import { backupDb, restoreDb } from './backup.js';
import { generateInterchange } from './interchange.js';

const program = new Command();
program.name('voice').description('OpenClaw Voice Skill CLI').version('1.0.0');

// --- Transcript commands ---
const transcript = program.command('transcript').description('Transcript management');

transcript.command('list')
  .description('List conversations')
  .option('--today', 'Filter by today')
  .option('--search <query>', 'Search in transcripts')
  .action((opts) => {
    const db = getDb();
    const convs = listConversations(db, { today: !!opts.today, search: opts.search || null });
    if (!convs.length) { console.log('No conversations found.'); return; }
    convs.forEach(c => {
      const status = c.ended ? 'ended' : 'ongoing';
      console.log(`${c.id}: ${c.started} (${status}) | Turns: ${c.turn_count} | Summary: ${c.summary || 'None'}`);
    });
  });

transcript.command('show')
  .argument('<conversation-id>', 'Conversation ID')
  .description('Show transcript')
  .action((id) => {
    const db = getDb();
    const lines = showTranscript(db, id);
    if (!lines.length) { console.log('No transcript lines found.'); return; }
    lines.forEach(l => console.log(`[${l.timestamp}] ${l.speaker.toUpperCase()}: ${l.text} (confidence: ${l.confidence})`));
  });

transcript.command('add')
  .argument('<conversation-id>', 'Conversation ID')
  .requiredOption('--speaker <type>', 'Speaker: user or assistant')
  .requiredOption('--text <text>', 'Text content')
  .option('--confidence <number>', 'Confidence score', '1.0')
  .description('Add transcript line')
  .action((id, opts) => {
    const db = getDb();
    addTranscriptLine(db, id, opts.speaker, opts.text, parseFloat(opts.confidence));
    console.log('Transcript line added.');
  });

// --- Conversation commands ---
const conversation = program.command('conversation').description('Conversation management');

conversation.command('start')
  .option('--summary <text>', 'Initial summary')
  .description('Start new conversation')
  .action((opts) => {
    const db = getDb();
    const id = startConversation(db, opts.summary || null);
    console.log(`New conversation started: ${id}`);
  });

conversation.command('end')
  .argument('<conversation-id>', 'Conversation ID')
  .option('--summary <text>', 'Final summary')
  .description('End conversation')
  .action((id, opts) => {
    const db = getDb();
    endConversation(db, id, opts.summary || null);
    console.log('Conversation ended.');
  });

// --- Profile commands ---
const profile = program.command('profile').description('Voice profile management');

profile.command('list')
  .description('List profiles')
  .action(() => {
    const db = getDb();
    const defaultName = getDefaultProfile(db);
    const profiles = listProfiles(db);
    if (!profiles.length) { console.log('No profiles found.'); return; }
    profiles.forEach(p => {
      const tag = defaultName === p.name ? ' (default)' : '';
      console.log(`${p.name}${tag}: ${p.elevenlabs_voice_id}`);
    });
  });

profile.command('add')
  .argument('<name>', 'Profile name')
  .requiredOption('--voice-id <id>', 'ElevenLabs voice ID')
  .option('--settings <json>', 'Settings JSON', '{}')
  .description('Add profile')
  .action((name, opts) => {
    const db = getDb();
    addProfile(db, name, opts.voiceId, opts.settings);
    console.log(`Profile ${name} added.`);
  });

profile.command('default')
  .argument('<name>', 'Profile name')
  .description('Set default profile')
  .action((name) => {
    const db = getDb();
    setDefaultProfile(db, name);
    console.log(`Default profile set to ${name}.`);
  });

// --- Utilities ---
program.command('refresh')
  .description('Refresh interchange files')
  .action(() => { generateInterchange(); console.log('Interchange files refreshed.'); });

program.command('backup')
  .option('--output <path>', 'Output path')
  .description('Backup database')
  .action(async (opts) => {
    const db = getDb();
    try { const p = await backupDb(db, opts.output || null); console.log(`Backup created: ${p}`); }
    catch (e) { console.error('Backup failed:', e.message); process.exit(1); }
  });

program.command('restore')
  .argument('<backup-file>', 'Backup file path')
  .description('Restore from backup')
  .action(async (file) => {
    try { await restoreDb(file); console.log('Database restored.'); }
    catch (e) { console.error('Restore failed:', e.message); process.exit(1); }
  });

program.parse();
