CREATE TABLE conversations (
  id TEXT PRIMARY KEY,
  started TEXT DEFAULT (datetime('now')),
  ended TEXT,
  turn_count INTEGER DEFAULT 0,
  summary TEXT
);

CREATE TABLE transcript_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  conversation_id TEXT REFERENCES conversations(id),
  speaker TEXT NOT NULL CHECK(speaker IN ('user','assistant')),
  text TEXT NOT NULL,
  timestamp TEXT DEFAULT (datetime('now')),
  confidence REAL
);

CREATE TABLE voice_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  elevenlabs_voice_id TEXT,
  settings_json TEXT DEFAULT '{}'
);

CREATE TABLE config (
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE INDEX idx_transcript_conversation ON transcript_lines(conversation_id);
CREATE INDEX idx_transcript_timestamp ON transcript_lines(timestamp);
CREATE INDEX idx_profiles_name ON voice_profiles(name);