#!/usr/bin/env node
/**
 * Session State Tracker - CLI
 *
 * Commands:
 *   session-state show       - Display current state
 *   session-state set <key> <value> - Set a field
 *   session-state refresh    - Rediscover state from sessions
 *   session-state clear      - Reset to empty
 *
 * SECURITY MANIFEST:
 *   Environment variables accessed: OPENCLAW_WORKSPACE (optional)
 *   External endpoints called: none
 *   Local files read: SESSION_STATE.md
 *   Local files written: SESSION_STATE.md
 *
 * Note: 'refresh' requires the memory_search tool, which is available when
 * running under OpenClaw exec or when the memory_search environment is set up.
 */

const { readState, writeState, discoverFromSessions } = require('./state');

async function show() {
  const state = await readState();
  if (!state) {
    console.log('SESSION_STATE.md does not exist or is empty.');
    return;
  }
  console.log('--- SESSION STATE ---');
  for (const [key, value] of Object.entries(state)) {
    if (key === 'body' || key === 'updated') continue;
    if (Array.isArray(value)) {
      console.log(`${key}:`);
      value.forEach(v => console.log(`  - ${v}`));
    } else {
      console.log(`${key}: ${value}`);
    }
  }
  if (state.updated) {
    console.log(`\nupdated: ${state.updated}`);
  }
  if (state.body) {
    console.log('\n--- Context ---');
    console.log(state.body);
  }
}

async function setField(key, value) {
  const updates = { [key]: value };
  await writeState(updates);
  console.log(`Set ${key} = ${value}`);
}

async function refresh(memorySearch) {
  if (!memorySearch) {
    console.error('memory_search tool is not available. Ensure session transcript indexing is enabled.');
    process.exit(1);
  }
  const discovered = await discoverFromSessions(memorySearch);
  await writeState(discovered);
  console.log('SESSION_STATE.md refreshed from session transcripts.');
  console.log(`Project: ${discovered.project}`);
  console.log(`Task: ${discovered.task}`);
}

async function clear() {
  await writeState({
    project: '',
    task: '',
    status: '',
    last_action: '',
    next_steps: [],
    updated: new Date().toISOString(),
    body: ''
  });
  console.log('SESSION_STATE.md cleared.');
}

// Main CLI entry
const args = process.argv.slice(2);
const command = args[0];

switch (command) {
  case 'show':
    show().catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
    break;
  case 'set':
    if (args.length < 3) {
      console.error('Usage: session-state set <key> <value>');
      process.exit(1);
    }
    const key = args[1];
    const value = args.slice(2).join(' ');
    setField(key, value).catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
    break;
  case 'refresh':
    // memorySearch will be injected by OpenClaw when running as a tool.
    // When run standalone, this will fail; that's okay.
    refresh(global.__memory_search__).catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
    break;
  case 'clear':
    clear().catch(err => {
      console.error('Error:', err.message);
      process.exit(1);
    });
    break;
  default:
    console.log(`
Session State Tracker CLI

Commands:
  show               Display current SESSION_STATE.md contents
  set <key> <value>  Set a field (e.g., "session-state set task 'Implement login'")
  refresh            Rediscover state from session transcripts (requires memory_search)
  clear              Reset SESSION_STATE.md to empty

Note: When run as an OpenClaw tool, the `refresh` command automatically has access to memory_search.
When run standalone (node scripts/cli.js), refresh will not work.
`);
}
