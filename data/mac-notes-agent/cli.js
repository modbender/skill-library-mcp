#!/usr/bin/env node

// Mac Notes Agent CLI
// Node.js bridge to Apple Notes via AppleScript (osascript)
// Supports: add, list, get, update, append, delete, search

const { execFileSync } = require('child_process');

function runOsascript(script) {
  try {
    const result = execFileSync('osascript', ['-e', script], {
      encoding: 'utf8',
      maxBuffer: 10 * 1024 * 1024,
    });
    return result.trim();
  } catch (err) {
    const msg = err.stderr ? err.stderr.toString() : err.message;
    console.error(JSON.stringify({ status: 'error', error: msg }));
    process.exit(1);
  }
}

function jsonOut(obj) {
  process.stdout.write(JSON.stringify(obj, null, 2) + '\n');
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const key = a.slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith('--')) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    } else {
      args._.push(a);
    }
  }
  return args;
}

function requireArg(args, name) {
  if (!args[name]) {
    console.error(JSON.stringify({ status: 'error', error: `Missing required argument --${name}` }));
    process.exit(1);
  }
}

function esc(str) {
  return String(str).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
}

// AppleScript helpers

function scriptEnsureFolder(folderName) {
  return `
    tell application "Notes"
      set defaultAcc to default account
      set targetFolder to folder "${esc(folderName)}" of defaultAcc
    end tell
  `;
}

function scriptEnsureFolderCreate(folderName) {
  return `
    tell application "Notes"
      set defaultAcc to default account
      set folderNames to name of folders of defaultAcc
      if folderNames does not contain "${esc(folderName)}" then
        make new folder at defaultAcc with properties {name:"${esc(folderName)}"}
      end if
      set targetFolder to folder "${esc(folderName)}" of defaultAcc
    end tell
  `;
}

function commandAdd(args) {
  requireArg(args, 'title');
  requireArg(args, 'body');
  const title = esc(args.title);
  const rawBody = args.body;
  // Interpret literal "\\n" sequences as real newlines, then render as simple HTML
  const normalized = String(rawBody).replace(/\\n/g, '\n');
  const htmlBody = `<div>${normalized.replace(/\r?\n/g, '<br>')}</div>`;
  const body = esc(htmlBody);
  const folder = args.folder ? esc(args.folder) : null;

  const script = folder
    ? `
      tell application "Notes"
        set defaultAcc to default account
        set folderNames to name of folders of defaultAcc
        if folderNames does not contain "${folder}" then
          make new folder at defaultAcc with properties {name:"${folder}"}
        end if
        set targetFolder to folder "${folder}" of defaultAcc
        set newNote to make new note at targetFolder with properties {name:"${title}", body:"${body}"}
        set cDate to creation date of newNote as string
      end tell
      return cDate
    `
    : `
      tell application "Notes"
        set defaultAcc to default account
        set newNote to make new note at defaultAcc with properties {name:"${title}", body:"${body}"}
        set cDate to creation date of newNote as string
      end tell
      return cDate
    `;

  const creationDateStr = runOsascript(script);
  const id = `${folder || 'default'}::${creationDateStr}::${args.title}`;
  jsonOut({ status: 'ok', id, title: args.title, folder: args.folder || 'default', creationDate: creationDateStr });
}

function commandList(args) {
  const folder = args.folder ? esc(args.folder) : null;
  const limit = args.limit ? parseInt(args.limit, 10) : 100;

  const script = folder
    ? `
      set output to ""
      tell application "Notes"
        set defaultAcc to default account
        set targetFolder to folder "${folder}" of defaultAcc
        set noteList to notes of targetFolder
        repeat with n in noteList
          set t to name of n
          set cDate to creation date of n as string
          set output to output & "${folder}||" & cDate & "||" & t & linefeed
        end repeat
      end tell
      return output
    `
    : `
      set output to ""
      tell application "Notes"
        set defaultAcc to default account
        set allFolders to folders of defaultAcc
        repeat with f in allFolders
          set fname to name of f
          set noteList to notes of f
          repeat with n in noteList
            set t to name of n
            set cDate to creation date of n as string
            set output to output & fname & "||" & cDate & "||" & t & linefeed
          end repeat
        end repeat
      end tell
      return output
    `;

  const raw = runOsascript(script);
  const lines = raw.split(/\r?\n/).filter(Boolean);
  const notes = lines.slice(0, limit).map((line) => {
    const [folderName, cDate, title] = line.split('||');
    return {
      id: `${folderName || 'default'}::${cDate}::${title}`,
      folder: folderName || 'default',
      title,
      creationDate: cDate,
    };
  });
  jsonOut(notes);
}

function scriptFindNoteByFolderTitle(folderName, title) {
  return `
    tell application "Notes"
      set defaultAcc to default account
      set targetFolder to folder "${esc(folderName)}" of defaultAcc
      set noteList to notes of targetFolder
      repeat with n in noteList
        if (name of n) is equal to "${esc(title)}" then
          return {n, creation date of n as string}
        end if
      end repeat
    end tell
    return {missing}
  `;
}

function commandGet(args) {
  if (!args.id && !(args.folder && args.title)) {
    console.error(
      JSON.stringify({
        status: 'error',
        error: 'Provide either --id or (--folder and --title) to locate a note',
      }),
    );
    process.exit(1);
  }

  let folderName, title;
  if (args.id) {
    const parts = String(args.id).split('::');
    folderName = parts[0];
    title = parts.slice(2).join('::');
  } else {
    folderName = args.folder;
    title = args.title;
  }

  const script = `
    tell application "Notes"
      set defaultAcc to default account
      set targetFolder to folder "${esc(folderName)}" of defaultAcc
      set noteList to notes of targetFolder
      repeat with n in noteList
        if (name of n) is equal to "${esc(title)}" then
          set cDate to creation date of n as string
          set theBody to body of n as string
          return cDate & "||" & theBody
        end if
      end repeat
    end tell
    return ""
  `;

  const raw = runOsascript(script);
  if (!raw) {
    jsonOut({ status: 'not_found', folder: folderName, title });
    return;
  }
  const [cDate, body] = raw.split('||');
  jsonOut({
    status: 'ok',
    folder: folderName,
    title,
    creationDate: cDate,
    body,
  });
}

function commandUpdateOrAppend(args, mode) {
  if (!args.id && !(args.folder && args.title)) {
    console.error(
      JSON.stringify({
        status: 'error',
        error: 'Provide either --id or (--folder and --title) to locate a note',
      }),
    );
    process.exit(1);
  }
  requireArg(args, 'body');

  let folderName, title;
  if (args.id) {
    const parts = String(args.id).split('::');
    folderName = parts[0];
    title = parts.slice(2).join('::');
  } else {
    folderName = args.folder;
    title = args.title;
  }

  const rawBody = args.body;
  // Interpret literal "\\n" sequences as real newlines, then render as simple HTML
  const normalized = String(rawBody).replace(/\\n/g, '\n');
  const newBody = esc(`<div>${normalized.replace(/\r?\n/g, '<br>')}</div>`);

  const script = mode === 'append'
    ? `
      tell application "Notes"
        set defaultAcc to default account
        set targetFolder to folder "${esc(folderName)}" of defaultAcc
        set noteList to notes of targetFolder
        repeat with n in noteList
          if (name of n) is equal to "${esc(title)}" then
            set oldBody to body of n as string
            set body of n to oldBody & "${newBody}"
            return "ok"
          end if
        end repeat
      end tell
      return "not_found"
    `
    : `
      tell application "Notes"
        set defaultAcc to default account
        set targetFolder to folder "${esc(folderName)}" of defaultAcc
        set noteList to notes of targetFolder
        repeat with n in noteList
          if (name of n) is equal to "${esc(title)}" then
            set body of n to "${newBody}"
            return "ok"
          end if
        end repeat
      end tell
      return "not_found"
    `;

  const result = runOsascript(script);
  if (result === 'ok') {
    jsonOut({ status: 'ok', folder: folderName, title, mode });
  } else {
    jsonOut({ status: 'not_found', folder: folderName, title });
  }
}

function commandDelete(args) {
  if (!args.id && !(args.folder && args.title)) {
    console.error(
      JSON.stringify({
        status: 'error',
        error: 'Provide either --id or (--folder and --title) to locate a note',
      }),
    );
    process.exit(1);
  }

  let folderName, title;
  if (args.id) {
    const parts = String(args.id).split('::');
    folderName = parts[0];
    title = parts.slice(2).join('::');
  } else {
    folderName = args.folder;
    title = args.title;
  }

  const script = `
    tell application "Notes"
      set defaultAcc to default account
      set targetFolder to folder "${esc(folderName)}" of defaultAcc
      set noteList to notes of targetFolder
      repeat with n in noteList
        if (name of n) is equal to "${esc(title)}" then
          delete n
          return "ok"
        end if
      end repeat
    end tell
    return "not_found"
  `;

  const result = runOsascript(script);
  if (result === 'ok') {
    jsonOut({ status: 'ok', deleted: { folder: folderName, title } });
  } else {
    jsonOut({ status: 'not_found', folder: folderName, title });
  }
}

function commandSearch(args) {
  requireArg(args, 'query');
  const query = args.query.toLowerCase();
  const folder = args.folder ? esc(args.folder) : null;
  const limit = args.limit ? parseInt(args.limit, 10) : 50;

  const script = folder
    ? `
      set output to ""
      tell application "Notes"
        set defaultAcc to default account
        set targetFolder to folder "${folder}" of defaultAcc
        set noteList to notes of targetFolder
        repeat with n in noteList
          set t to name of n
          set cDate to creation date of n as string
          set b to body of n as string
          set output to output & "${folder}||" & cDate & "||" & t & "||" & b & linefeed
        end repeat
      end tell
      return output
    `
    : `
      set output to ""
      tell application "Notes"
        set defaultAcc to default account
        set allFolders to folders of defaultAcc
        repeat with f in allFolders
          set fname to name of f
          set noteList to notes of f
          repeat with n in noteList
            set t to name of n
            set cDate to creation date of n as string
            set b to body of n as string
            set output to output & fname & "||" & cDate & "||" & t & "||" & b & linefeed
          end repeat
        end repeat
      end tell
      return output
    `;

  const raw = runOsascript(script);
  const lines = raw.split(/\r?\n/).filter(Boolean);
  const results = [];

  for (const line of lines) {
    if (results.length >= limit) break;
    const [folderName, cDate, title, body] = line.split('||');
    const hay = (title + '\n' + body).toLowerCase();
    if (hay.includes(query)) {
      results.push({
        id: `${folderName || 'default'}::${cDate}::${title}`,
        folder: folderName || 'default',
        title,
        creationDate: cDate,
        snippet: body ? body.slice(0, 200) : '',
      });
    }
  }

  jsonOut(results);
}

function main() {
  const args = parseArgs(process.argv);
  const [command] = args._;

  switch (command) {
    case 'add':
      return commandAdd(args);
    case 'list':
      return commandList(args);
    case 'get':
      return commandGet(args);
    case 'update':
      return commandUpdateOrAppend(args, 'update');
    case 'append':
      return commandUpdateOrAppend(args, 'append');
    case 'delete':
      return commandDelete(args);
    case 'search':
      return commandSearch(args);
    default:
      console.error(
        JSON.stringify({
          status: 'error',
          error:
            'Usage: node cli.js <add|list|get|update|append|delete|search> [--folder F] [--title T] [--body B]',
        }),
      );
      process.exit(1);
  }
}

if (require.main === module) {
  main();
}
