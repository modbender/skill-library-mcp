# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-02-17

### Initial Release

Renamed from `openclaw-memory-qdrant` to `openclaw-semantic-memory` to better reflect the plugin's core functionality.

#### Features

- **Semantic Search**: Local vector search using Transformers.js embeddings
- **Disk Persistence**: Memories saved to `~/.openclaw-memory/` by default
- **Custom Storage Path**: Configure custom storage directory
- **Auto Capture**: Optional automatic conversation recording with PII protection
- **Auto Recall**: Automatic injection of relevant memories into conversations
- **Multiple Storage Backends**:
  - In-memory mode (default, with optional disk persistence)
  - External Qdrant server support
- **Privacy Protection**: PII detection and filtering by default
- **Zero Configuration**: Works out of the box with sensible defaults

#### Configuration Options

- `persistToDisk` (default: true) - Save memories to disk
- `storagePath` (optional) - Custom storage directory
- `autoCapture` (default: false) - Auto-record conversations
- `allowPIICapture` (default: false) - Allow PII capture
- `autoRecall` (default: true) - Auto-inject memories
- `qdrantUrl` (optional) - External Qdrant server
- `maxMemorySize` (default: 1000) - Max memories in memory mode

#### Migration from openclaw-memory-qdrant

This is a renamed version of `openclaw-memory-qdrant` v1.0.15. All features and functionality remain the same. To migrate:

1. Uninstall old plugin: `clawhub uninstall memory-qdrant`
2. Install new plugin: `clawhub install semantic-memory`
3. Update your config from `memory-qdrant` to `semantic-memory`

Your existing data in `~/.openclaw-memory/` will be automatically used by the new plugin.
