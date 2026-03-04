#!/usr/bin/env node

// macOS Reminders bridge
// Usage:
//   node reminders/apple-bridge.js list --scope week
//   node reminders/apple-bridge.js add --title "Buy groceries" --due "2026-02-02T15:10:00+09:00"
//   node reminders/apple-bridge.js add --title "Weekly" --due "..." --repeat weekly
//   node reminders/apple-bridge.js edit --id "ABC123" --title "New title"
//   node reminders/apple-bridge.js delete --id "ABC123"
//   node reminders/apple-bridge.js complete --id "ABC123"

const { execFile } = require('child_process');
const path = require('path');

let applescript;
try {
  applescript = require('applescript');
} catch (e) {
  console.error('Error: "applescript" module not found.\nPlease run the following in the workspace directory:\n  npm install applescript');
  process.exit(1);
}

function parseArgs(argv) {
  const args = { _: [] };
  let currentKey = null;
  for (const token of argv) {
    if (token.startsWith('--')) {
      currentKey = token.slice(2);
      args[currentKey] = true;
    } else if (currentKey) {
      args[currentKey] = token;
      currentKey = null;
    } else {
      args._.push(token);
    }
  }
  return args;
}

function runAppleScript(source) {
  return new Promise((resolve, reject) => {
    applescript.execString(source, (err, result) => {
      if (err) reject(err);
      else resolve(result);
    });
  });
}

function parseISO(dueISO) {
  if (!dueISO) return null;

  // Use Date object to parse any valid ISO format and convert to local time
  const d = new Date(dueISO);
  if (isNaN(d.getTime())) return null;

  return {
    year: d.getFullYear(),
    month: d.getMonth() + 1, // getMonth() is 0-indexed
    day: d.getDate(),
    hour: d.getHours(),
    minute: d.getMinutes(),
  };
}

// Check if Swift is available
function checkSwift() {
  return new Promise((resolve) => {
    execFile('which', ['swift'], (err) => {
      resolve(!err);
    });
  });
}

// Run Swift EventKit helper
async function runSwiftHelper(args) {
  const hasSwift = await checkSwift();
  if (!hasSwift) {
    throw new Error(
      'Swift not found. Native recurrence requires Swift.\n' +
      'Install Xcode Command Line Tools: xcode-select --install'
    );
  }

  return new Promise((resolve, reject) => {
    const swiftPath = path.join(__dirname, 'eventkit-bridge.swift');
    execFile('swift', [swiftPath, ...args], { encoding: 'utf8' }, (err, stdout, stderr) => {
      if (err) {
        return reject(new Error(stderr || err.message || String(err)));
      }
      const text = stdout.trim();
      try {
        const json = JSON.parse(text);
        if (json.ok === false) {
          return reject(new Error(json.error || 'Swift helper failed'));
        }
        resolve(json);
      } catch (parseErr) {
        reject(new Error('Swift returned invalid JSON: ' + text.slice(0, 200)));
      }
    });
  });
}

// List reminders via Swift EventKit (returns IDs)
async function list(scope) {
  scope = scope || 'week';
  const result = await runSwiftHelper(['list', '--scope', scope]);
  return result.items || [];
}

async function add(title, dueISO, note, repeat, repeatEnd, interval) {
  if (!title) {
    throw new Error('title is required');
  }

  // Use Swift EventKit helper for recurrence (native support)
  // or for any reminder creation (more reliable)
  if (repeat) {
    const args = ['add', '--title', title];
    if (dueISO) args.push('--due', dueISO);
    if (note) args.push('--note', note);
    if (repeat) args.push('--repeat', repeat);
    if (interval) args.push('--interval', String(interval));
    if (repeatEnd) args.push('--repeat-end', repeatEnd);

    const result = await runSwiftHelper(args);
    return {
      ok: true,
      title,
      due: dueISO || null,
      note: note || null,
      repeat: repeat || null,
      interval: interval || null,
      repeatEnd: repeatEnd || null,
      ...result,
    };
  }

  // Non-recurring: use AppleScript (existing behavior)
  const escTitle = title.replace(/"/g, '\\"');
  const escNote = note ? note.replace(/"/g, '\\"') : '';
  const dt = parseISO(dueISO);

  let script;

  if (dt) {
    if (escNote) {
      script = `
    tell application "Reminders"
      set targetDate to current date
      set year of targetDate to ${dt.year}
      set month of targetDate to ${dt.month}
      set day of targetDate to ${dt.day}
      set hours of targetDate to ${dt.hour}
      set minutes of targetDate to ${dt.minute}
      set seconds of targetDate to 0
      tell default list
        make new reminder with properties {name:"${escTitle}", due date:targetDate, body:"${escNote}"}
      end tell
    end tell
    `;
    } else {
      script = `
    tell application "Reminders"
      set targetDate to current date
      set year of targetDate to ${dt.year}
      set month of targetDate to ${dt.month}
      set day of targetDate to ${dt.day}
      set hours of targetDate to ${dt.hour}
      set minutes of targetDate to ${dt.minute}
      set seconds of targetDate to 0
      tell default list
        make new reminder with properties {name:"${escTitle}", due date:targetDate}
      end tell
    end tell
    `;
    }
  } else {
    if (escNote) {
      script = `
    tell application "Reminders"
      tell default list
        make new reminder with properties {name:"${escTitle}", body:"${escNote}"}
      end tell
    end tell
    `;
    } else {
      script = `
    tell application "Reminders"
      tell default list
        make new reminder with properties {name:"${escTitle}"}
      end tell
    end tell
    `;
    }
  }

  await runAppleScript(script);
  return {
    ok: true,
    title,
    due: dueISO || null,
    note: note || null,
  };
}

// Edit reminder via Swift EventKit (by ID)
async function edit(id, updates) {
  const args = ['edit', '--id', id];
  if (updates.title) args.push('--title', updates.title);
  if (updates.due) args.push('--due', updates.due);
  if (updates.note !== undefined) args.push('--note', updates.note || '');
  if (updates.repeat) args.push('--repeat', updates.repeat);
  if (updates.interval) args.push('--interval', String(updates.interval));
  if (updates['repeat-end']) args.push('--repeat-end', updates['repeat-end']);

  return await runSwiftHelper(args);
}

// Delete reminder via Swift EventKit (by ID)
async function deleteReminder(id) {
  return await runSwiftHelper(['delete', '--id', id]);
}

// Complete reminder via Swift EventKit (by ID)
async function completeReminder(id) {
  return await runSwiftHelper(['complete', '--id', id]);
}

async function main() {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);
  const cmd = args._[0];

  if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') {
    console.log(`Usage:
  list [--scope today|week|all]
  add --title "TITLE" [--due ISO_DATE] [--note "MEMO"] [--repeat daily|weekly|monthly|yearly] [--interval N] [--repeat-end YYYY-MM-DD]
  edit --id "ID" [--title "NEW"] [--due ISO_DATE] [--note "NEW"]
  delete --id "ID"
  complete --id "ID"

Examples:
  node reminders/apple-bridge.js list --scope week
  node reminders/apple-bridge.js add --title "Meeting" --due "2026-02-02T09:00:00+09:00"
  node reminders/apple-bridge.js edit --id "ABC123" --title "Updated Meeting"
  node reminders/apple-bridge.js delete --id "ABC123"
  node reminders/apple-bridge.js complete --id "ABC123"`);
    process.exit(0);
  }

  try {
    if (cmd === 'list') {
      const scope = args.scope || 'week';
      const items = await list(scope);
      console.log(JSON.stringify(items));
    } else if (cmd === 'add') {
      const title = args.title;
      const due = args.due || '';
      const note = args.note || '';
      const repeat = args.repeat || '';
      const repeatEnd = args['repeat-end'] || '';
      const interval = args.interval || '';
      if (!title) {
        console.error('Error: --title is required for add');
        process.exit(1);
      }
      const result = await add(title, due || null, note || null, repeat || null, repeatEnd || null, interval || null);
      console.log(JSON.stringify(result));
    } else if (cmd === 'edit') {
      const id = args.id;
      if (!id) {
        console.error('Error: --id is required for edit');
        process.exit(1);
      }
      const result = await edit(id, {
        title: args.title || '',
        due: args.due || '',
        note: args.note,
        repeat: args.repeat || '',
        interval: args.interval || '',
        'repeat-end': args['repeat-end'] || '',
      });
      console.log(JSON.stringify(result));
    } else if (cmd === 'delete') {
      const id = args.id;
      if (!id) {
        console.error('Error: --id is required for delete');
        process.exit(1);
      }
      const result = await deleteReminder(id);
      console.log(JSON.stringify(result));
    } else if (cmd === 'complete') {
      const id = args.id;
      if (!id) {
        console.error('Error: --id is required for complete');
        process.exit(1);
      }
      const result = await completeReminder(id);
      console.log(JSON.stringify(result));
    } else {
      console.error('Unknown command:', cmd);
      process.exit(1);
    }
  } catch (err) {
    console.error('Error running apple-bridge:', err.message || err);
    process.exit(1);
  }
}

main();
