#!/usr/bin/env node

// mac-reminders-agent unified CLI
// - Provides a common interface (list/add/edit/delete/complete, JSON output) for any environment.
// - Supports multiple locales (en, ko, ja, zh) for response formatting.
// - Delegates actual work to reminders/apple-bridge.js (AppleScript + EventKit).

const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

// Load locales
let locales = {};
try {
  const localesPath = path.join(__dirname, 'locales.json');
  locales = JSON.parse(fs.readFileSync(localesPath, 'utf8'));
} catch (e) {
  // Fallback to empty locales
}

function getLocale(code) {
  return locales[code] || locales['en'] || {};
}

function formatResponse(template, vars) {
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replace(new RegExp(`\\{${key}\\}`, 'g'), value || '');
  }
  return result;
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

// Format due datetime for title suffix (e.g., "제목 - 2026.02.15 21:00")
function formatDueForTitle(dueISO, locale) {
  if (!dueISO) return '';
  const d = new Date(dueISO);
  if (Number.isNaN(d.getTime())) return '';

  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mi = String(d.getMinutes()).padStart(2, '0');

  // 수완님 환경: 한국어 우선
  if (locale === 'ko') {
    return `${yyyy}.${mm}.${dd} ${hh}:${mi}`;
  }

  // 기타 로케일: 무난한 ISO-like 포맷
  return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
}

function runReminderBridge(subcmd, extraArgs = []) {
  return new Promise((resolve, reject) => {
    const bridgePath = path.join(__dirname, 'reminders', 'apple-bridge.js');
    const args = [bridgePath, subcmd, ...extraArgs];

    execFile('node', args, { encoding: 'utf8' }, (err, stdout, stderr) => {
      if (err) {
        return reject(new Error(stderr || err.message || String(err)));
      }
      const text = stdout.trim();
      try {
        const json = JSON.parse(text);
        resolve(json);
      } catch {
        resolve({ ok: true, raw: text });
      }
    });
  });
}

async function main() {
  const argv = process.argv.slice(2);
  const args = parseArgs(argv);
  const cmd = args._[0];
  const locale = args.locale || 'en';
  const loc = getLocale(locale);

  if (!cmd || cmd === 'help' || cmd === '--help' || cmd === '-h') {
    console.log(`Usage:
  node cli.js list [--scope today|week|all] [--locale en|ko|ja|zh]
  node cli.js add --title "TITLE" [--due ISO_DATETIME] [--note "MEMO"] [--locale en|ko|ja|zh]
  node cli.js add --title "Weekly standup" --due "2026-02-10T09:00:00+09:00" --repeat weekly [--interval N] [--repeat-end "2026-06-30"] [--locale ko]
  node cli.js edit --id "ID" [--title "NEW"] [--due ISO_DATETIME] [--note "NEW"] [--locale en|ko|ja|zh]
  node cli.js delete --id "ID" [--locale en|ko|ja|zh]
  node cli.js complete --id "ID" [--locale en|ko|ja|zh]

Supported locales: en (English), ko (한국어), ja (日本語), zh (中文)
`);
    process.exit(0);
  }

  try {
    if (cmd === 'list') {
      const scope = args.scope || 'week';
      const result = await runReminderBridge('list', ['--scope', scope]);
      // result is an array of items (from apple-bridge)
      console.log(JSON.stringify({
        locale,
        labels: loc.responses || {},
        items: result
      }));
    } else if (cmd === 'add') {
      let title = args.title;
      const due = args.due || '';
      const note = args.note || '';

      // 반복 관련 옵션들 (예: 매주 반복)
      const repeat = args.repeat || '';
      const repeatEnd = args['repeat-end'] || '';
      const interval = args.interval || '';

      if (!title) {
        console.error('Error: --title is required for add');
        process.exit(1);
      }

      // 반복 라벨을 제목에 추가 (예: "회의 (매주 화요일)")
      if (repeat && loc.repeat && loc.repeat.labels) {
        let repeatLabel = loc.repeat.labels[repeat];
        if (repeatLabel && due) {
          // Parse due date to get day/date/month info
          const dueDate = new Date(due);
          const dayIndex = dueDate.getDay(); // 0=Sunday, 1=Monday, ...
          const dateNum = dueDate.getDate();
          const monthIndex = dueDate.getMonth(); // 0=Jan, 1=Feb, ...

          const dayName = loc.repeat.days ? loc.repeat.days[dayIndex] : '';
          const monthName = loc.repeat.months ? loc.repeat.months[monthIndex] : String(monthIndex + 1);

          // Replace placeholders
          repeatLabel = repeatLabel
            .replace('{day}', dayName)
            .replace('{date}', String(dateNum))
            .replace('{month}', monthName);

          title = `${title} (${repeatLabel})`;
        } else if (repeatLabel) {
          title = `${title} (${repeatLabel})`;
        }
      }

      // 모든 리마인더 제목에 "제목 - YYYY.MM.DD HH:MM" 형식의 날짜/시간을 붙인다
      if (due) {
        const dueLabel = formatDueForTitle(due, locale);
        if (dueLabel) {
          title = `${title} - ${dueLabel}`;
        }
      }

      const extra = ['--title', title];
      if (due) extra.push('--due', due);
      if (note) extra.push('--note', note);

      // 반복 옵션들을 bridge 쪽으로 그대로 전달
      if (repeat) extra.push('--repeat', repeat);
      if (repeatEnd) extra.push('--repeat-end', repeatEnd);
      if (interval) extra.push('--interval', interval);

      const result = await runReminderBridge('add', extra);

      // Format response with locale
      const responses = loc.responses || {};
      const dueText = due
        ? formatResponse(responses.added_with_due || ' for {due}', { due })
        : (responses.added_no_due || ' without a due date');
      const message = formatResponse(responses.added || "Added '{title}' reminder{due_text}.", {
        title,
        due_text: dueText
      });

      console.log(JSON.stringify({
        ...result,
        locale,
        message
      }));
    } else if (cmd === 'edit') {
      const id = args.id;
      if (!id) {
        console.error('Error: --id is required for edit');
        process.exit(1);
      }

      const extra = ['--id', id];
      if (args.title) extra.push('--title', args.title);
      if (args.due) extra.push('--due', args.due);
      if (args.note !== undefined && args.note !== true) extra.push('--note', args.note);
      if (args.repeat) extra.push('--repeat', args.repeat);
      if (args.interval) extra.push('--interval', args.interval);
      if (args['repeat-end']) extra.push('--repeat-end', args['repeat-end']);

      const result = await runReminderBridge('edit', extra);

      const responses = loc.responses || {};
      const message = formatResponse(responses.edited || "Updated '{title}' reminder.", {
        title: result.title || ''
      });

      console.log(JSON.stringify({
        ...result,
        locale,
        message
      }));
    } else if (cmd === 'delete') {
      const id = args.id;
      if (!id) {
        console.error('Error: --id is required for delete');
        process.exit(1);
      }

      const result = await runReminderBridge('delete', ['--id', id]);

      const responses = loc.responses || {};
      const message = formatResponse(responses.deleted || "Deleted '{title}' reminder.", {
        title: result.title || ''
      });

      console.log(JSON.stringify({
        ...result,
        locale,
        message
      }));
    } else if (cmd === 'complete') {
      const id = args.id;
      if (!id) {
        console.error('Error: --id is required for complete');
        process.exit(1);
      }

      const result = await runReminderBridge('complete', ['--id', id]);

      const responses = loc.responses || {};
      const message = formatResponse(responses.completed || "Completed '{title}'.", {
        title: result.title || ''
      });

      console.log(JSON.stringify({
        ...result,
        locale,
        message
      }));
    } else {
      console.error('Unknown command:', cmd);
      process.exit(1);
    }
  } catch (err) {
    const responses = loc.responses || {};
    const errorMsg = responses.error_access || 'Error accessing Reminders app';
    console.error(errorMsg + ':', err.message || err);
    process.exit(1);
  }
}

main();
