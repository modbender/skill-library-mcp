const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;

// Paths
const STORIES_FILE = path.join(__dirname, '..', 'newsletter-today.json');
const INTERESTS_FILE = path.join(__dirname, '..', 'newsletter-interests.json');
const READING_LIST_FILE = path.join(__dirname, '..', 'reading-list.md');
const NOTES_FILE = path.join(__dirname, '..', 'newsletter-notes.json');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// GET / — serve SPA
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// GET /api/today — return today's stories
app.get('/api/today', (req, res) => {
  try {
    if (!fs.existsSync(STORIES_FILE)) {
      return res.status(404).json({ error: 'No stories file found. Run the newsletter digest first.' });
    }
    const data = JSON.parse(fs.readFileSync(STORIES_FILE, 'utf8'));
    // Strip bodies from list response — fetched on demand via /api/story/:id
    const light = { ...data, stories: data.stories.map(s => ({ ...s, hasBody: !!(s.body), body: undefined })) };
    res.json(light);
  } catch (err) {
    console.error('Error reading stories:', err);
    res.status(500).json({ error: 'Failed to read stories file.' });
  }
});

// GET /api/story/:id — fetch single story body on demand
app.get('/api/story/:id', (req, res) => {
  try {
    if (!fs.existsSync(STORIES_FILE)) {
      return res.status(404).json({ error: 'No stories file.' });
    }
    const data = JSON.parse(fs.readFileSync(STORIES_FILE, 'utf8'));
    const story = data.stories.find(s => s.id === req.params.id);
    if (!story) return res.status(404).json({ error: 'Story not found.' });
    res.json({ id: story.id, body: story.body || '' });
  } catch (err) {
    res.status(500).json({ error: 'Failed to read story.' });
  }
});

// POST /api/vote — record up/down vote
app.post('/api/vote', (req, res) => {
  const { storyId, vote } = req.body;
  if (!storyId || !['up', 'down', 'open'].includes(vote)) {
    return res.status(400).json({ error: 'storyId and vote ("up", "down", or "open") required.' });
  }

  try {
    const interests = readInterests();

    if (vote === 'open') {
      // Soft signal — cap at 1 per story per session to avoid noise
      const alreadyOpened = interests.signals.some(
        s => s.storyId === storyId && s.vote === 'open'
      );
      if (alreadyOpened) return res.json({ ok: true, storyId, vote, skipped: true });
    } else {
      // Hard vote — replace any previous up/down for this story
      interests.signals = interests.signals.filter(
        s => !(s.storyId === storyId && ['up', 'down'].includes(s.vote))
      );
    }

    interests.signals.push({ storyId, vote, ts: new Date().toISOString() });
    writeInterests(interests);
    res.json({ ok: true, storyId, vote });
  } catch (err) {
    console.error('Error writing vote:', err);
    res.status(500).json({ error: 'Failed to record vote.' });
  }
});

// POST /api/save — save to reading list
app.post('/api/save', (req, res) => {
  const { storyId, note } = req.body;
  if (!storyId) {
    return res.status(400).json({ error: 'storyId required.' });
  }

  try {
    // Find story details
    let story = null;
    if (fs.existsSync(STORIES_FILE)) {
      const data = JSON.parse(fs.readFileSync(STORIES_FILE, 'utf8'));
      story = data.stories.find(s => s.id === storyId);
    }

    // Append to reading-list.md
    const ts = new Date().toISOString();
    const date = ts.slice(0, 10);
    const safeHeadline = escapeMarkdown(story ? story.headline : storyId);
    const safeSource = escapeMarkdown(story ? story.source : 'Unknown');
    const safeId = escapeMarkdown(storyId);
    const safeNote = note ? escapeMarkdown(note) : '';
    const safeGmailUrl = sanitizeUrl(story?.gmailUrl);

    let entry = `\n## ${safeHeadline}\n`;
    entry += `- **Date saved:** ${date}\n`;
    entry += `- **Source:** ${safeSource}\n`;
    if (safeGmailUrl) entry += `- **Link:** [Open in Gmail](${safeGmailUrl})\n`;
    if (safeNote) entry += `- **Note:** ${safeNote}\n`;
    entry += `- **ID:** ${safeId}\n`;

    fs.appendFileSync(READING_LIST_FILE, entry);

    // Also add a save signal to interests
    const interests = readInterests();
    interests.signals = interests.signals.filter(s => !(s.storyId === storyId && s.vote === 'save'));
    interests.signals.push({ storyId, vote: 'save', ts, note: note || null });
    writeInterests(interests);

    res.json({ ok: true, storyId });
  } catch (err) {
    console.error('Error saving story:', err);
    res.status(500).json({ error: 'Failed to save story.' });
  }
});

// GET /api/notes — return all saved notes
app.get('/api/notes', (req, res) => {
  try {
    const notes = readNotes();
    res.json(notes);
  } catch (err) {
    res.status(500).json({ error: 'Failed to read notes.' });
  }
});

// POST /api/note — save or update a note for a story
app.post('/api/note', (req, res) => {
  const { storyId, note } = req.body;
  if (!storyId) return res.status(400).json({ error: 'storyId required.' });

  try {
    const notes = readNotes();
    if (note && note.trim()) {
      notes[storyId] = { note: note.trim(), ts: new Date().toISOString() };
    } else {
      delete notes[storyId]; // empty note = delete
    }
    writeNotes(notes);
    res.json({ ok: true, storyId });
  } catch (err) {
    console.error('Error saving note:', err);
    res.status(500).json({ error: 'Failed to save note.' });
  }
});

// Helpers
function readNotes() {
  if (!fs.existsSync(NOTES_FILE)) return {};
  return JSON.parse(fs.readFileSync(NOTES_FILE, 'utf8'));
}

function writeNotes(data) {
  fs.writeFileSync(NOTES_FILE, JSON.stringify(data, null, 2));
}

function readInterests() {
  if (!fs.existsSync(INTERESTS_FILE)) {
    return { version: 1, topics: {}, signals: [], sources: {} };
  }
  return JSON.parse(fs.readFileSync(INTERESTS_FILE, 'utf8'));
}

function writeInterests(data) {
  fs.writeFileSync(INTERESTS_FILE, JSON.stringify(data, null, 2));
}

function escapeMarkdown(input) {
  return String(input || '')
    .replace(/\\/g, '\\\\')
    .replace(/([`*_{}[\]()#+\-.!|>])/g, '\\$1')
    .replace(/[\r\n]+/g, ' ')
    .trim();
}

function sanitizeUrl(url) {
  if (!url) return null;
  try {
    const u = new URL(String(url));
    if (u.protocol !== 'https:' && u.protocol !== 'http:') return null;
    return u.toString();
  } catch {
    return null;
  }
}

// Start server
app.listen(PORT, () => {
  console.log(`📰 Newsletter Reader running at http://localhost:${PORT}`);
  console.log(`   Stories: ${STORIES_FILE}`);
  console.log(`   Interests: ${INTERESTS_FILE}`);
});
