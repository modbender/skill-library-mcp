#!/usr/bin/env node
// Latent Press API client
// Usage: node api.js <command> [args...]
//
// Commands:
//   create-book --title "T" [--genre "g1,g2"] [--blurb "B"] [--cover_url "U"]
//   list-books
//   add-chapter <slug> <number> "Title" "Content"
//   list-chapters <slug>
//   update-doc <slug> <type> "Content"     (type: bible|outline|status|story_so_far|process)
//   add-character <slug> "Name" "Description" [voice]
//   upload-audio <slug> <chapter-number> <file-path>  — upload audio to a chapter
//   remove-audio <slug> <chapter-number>              — remove audio from a chapter
//   publish <slug>
//
// API key resolution (first match wins):
//   1. LATENTPRESS_API_KEY env var
//   2. .env file in skill root

const fs = require('fs');
const path = require('path');

const API = 'https://www.latentpress.com/api';
const ENV_FILE = path.join(__dirname, '..', '.env');

function getKey() {
  // 1. Environment variable
  if (process.env.LATENTPRESS_API_KEY) {
    return process.env.LATENTPRESS_API_KEY;
  }

  // 2. .env file
  if (fs.existsSync(ENV_FILE)) {
    const content = fs.readFileSync(ENV_FILE, 'utf8');
    const match = content.match(/LATENTPRESS_API_KEY=(.+)/);
    if (match) return match[1].trim();
  }

  console.error('No API key found. Set LATENTPRESS_API_KEY env var, run register.js, or add it to .env');
  process.exit(1);
}

function headers(key) {
  return {
    'Authorization': `Bearer ${key}`,
    'Content-Type': 'application/json',
  };
}

async function api(method, path, body) {
  const key = getKey();
  const opts = { method, headers: headers(key) };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  const data = await res.json();
  if (!res.ok) {
    console.error(`Error ${res.status}:`, data.error || data);
    process.exit(1);
  }
  return data;
}

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith('--') && i + 1 < args.length) {
      result[args[i].slice(2)] = args[++i];
    }
  }
  return result;
}

async function main() {
  const [,, cmd, ...args] = process.argv;

  if (!cmd || cmd === '--help') {
    console.log(`Usage: node api.js <command> [args...]

Commands:
  create-book --title "T" [--genre "g1,g2"] [--blurb "B"] [--cover_url "U"]
  list-books
  add-chapter <slug> <number> "Title" "Content"
  list-chapters <slug>
  update-doc <slug> <type> "Content"
  add-character <slug> "Name" "Description" [voice]
  upload-audio <slug> <chapter-number> <file-path>
  remove-audio <slug> <chapter-number>
  publish <slug>

API key: set LATENTPRESS_API_KEY env var, or run register.js to save to .env`);
    return;
  }

  switch (cmd) {
    case 'create-book': {
      const opts = parseArgs(args);
      if (!opts.title) { console.error('--title required'); process.exit(1); }
      const body = { title: opts.title };
      if (opts.genre) body.genre = opts.genre.split(',').map(s => s.trim());
      if (opts.blurb) body.blurb = opts.blurb;
      if (opts.cover_url) body.cover_url = opts.cover_url;
      const data = await api('POST', '/books', body);
      console.log('Book created:', JSON.stringify(data.book, null, 2));
      break;
    }
    case 'list-books': {
      const data = await api('GET', '/books');
      console.log(JSON.stringify(data.books, null, 2));
      break;
    }
    case 'add-chapter': {
      const [slug, number, title, content] = args;
      if (!slug || !number || !content) {
        console.error('Usage: add-chapter <slug> <number> "Title" "Content"');
        process.exit(1);
      }
      const body = { number: parseInt(number), content };
      if (title) body.title = title;
      const data = await api('POST', `/books/${slug}/chapters`, body);
      console.log('Chapter saved:', JSON.stringify(data.chapter, null, 2));
      break;
    }
    case 'list-chapters': {
      const data = await api('GET', `/books/${args[0]}/chapters`);
      console.log(JSON.stringify(data.chapters, null, 2));
      break;
    }
    case 'update-doc': {
      const [slug, type, content] = args;
      if (!slug || !type || !content) {
        console.error('Usage: update-doc <slug> <type> "Content"');
        process.exit(1);
      }
      const data = await api('PUT', `/books/${slug}/documents`, { type, content });
      console.log('Document updated:', JSON.stringify(data.document, null, 2));
      break;
    }
    case 'add-character': {
      const [slug, name, description, voice] = args;
      if (!slug || !name) {
        console.error('Usage: add-character <slug> "Name" "Description" [voice]');
        process.exit(1);
      }
      const body = { name };
      if (description) body.description = description;
      if (voice) body.voice = voice;
      const data = await api('POST', `/books/${slug}/characters`, body);
      console.log('Character saved:', JSON.stringify(data.character, null, 2));
      break;
    }
    case 'upload-audio': {
      const [slug, chapterNum, filePath] = args;
      if (!slug || !chapterNum || !filePath) {
        console.error('Usage: upload-audio <slug> <chapter-number> <file-path>');
        process.exit(1);
      }
      const audioKey = getKey();
      const audioFile = fs.readFileSync(filePath);
      const ext = path.extname(filePath).toLowerCase();
      const mimeMap = { '.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.ogg': 'audio/ogg' };
      const mime = mimeMap[ext] || 'audio/mpeg';
      const form = new FormData();
      form.append('file', new Blob([audioFile], { type: mime }), path.basename(filePath));
      const audioRes = await fetch(`${API}/books/${slug}/chapters/${chapterNum}/audio`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${audioKey}` },
        body: form,
      });
      const audioData = await audioRes.json();
      if (!audioRes.ok) { console.error(`Error ${audioRes.status}:`, audioData.error || audioData); process.exit(1); }
      console.log('Audio uploaded:', JSON.stringify(audioData, null, 2));
      break;
    }
    case 'remove-audio': {
      const [slug2, chapterNum2] = args;
      if (!slug2 || !chapterNum2) {
        console.error('Usage: remove-audio <slug> <chapter-number>');
        process.exit(1);
      }
      const data2 = await api('DELETE', `/books/${slug2}/chapters/${chapterNum2}/audio`);
      console.log('Audio removed:', JSON.stringify(data2, null, 2));
      break;
    }
    case 'publish': {
      const data = await api('POST', `/books/${args[0]}/publish`);
      console.log('Published:', JSON.stringify(data, null, 2));
      break;
    }
    default:
      console.error(`Unknown command: ${cmd}. Run with --help.`);
      process.exit(1);
  }
}

main().catch(e => { console.error(e); process.exit(1); });
