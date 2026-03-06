# Synapse Protocol - P2P File Sharing with Semantic Search

P2P file sharing using BitTorrent with semantic search powered by vector embeddings. Share any file, discover it by content similarity.

> **📖 Installation & Usage**: See [SKILL.md](SKILL.md)

## ✨ Features

- **Semantic Search**: Find files by content similarity using 768D vector embeddings
- **True P2P**: BitTorrent protocol with DHT, multi-source downloads
- **Persistent Seeder**: Background daemon manages multiple torrents
- **Any File Type**: Share docs, code, databases - anything
- **Vector Search Tracker**: FAISS-powered similarity search on central tracker
- **Auto-Registration**: Sharing automatically generates embeddings and registers with tracker

## 🏗️ How It Works

1. **Share**: `synapse share file.md` → Creates torrent, generates embedding, registers with tracker
2. **Search**: `synapse search "kubernetes"` → Tracker returns ranked results by similarity  
3. **Download**: `synapse download magnet:?...` → P2P download via BitTorrent
4. **Seed**: Background daemon keeps files available to the network

**Search Architecture**: Client generates query embedding → Tracker computes cosine similarity → Returns ranked results

**Storage**: Tracker stores embeddings (FAISS index), clients store actual files (BitTorrent)

## 🎯 Benefits

- **Discovery by Content**: Find files without knowing exact names - search by meaning
- **Fast Distribution**: BitTorrent's multi-source downloads, DHT resilience
- **Lightweight**: No vector DB per client - tracker handles similarity search
- **Decentralized Storage**: Files distributed across network, tracker only stores vectors
- **Production Ready**: Built on libtorrent (powers qBittorrent, Deluge)

## 📁 Project Structure

```
Synapse/
├── SKILL.md                    # Installation & usage instructions
├── README.md                   # This file - features & architecture
├── client.py                   # CLI entry point
├── src/
│   ├── core.py                # Data structures (MemoryShard, MoltMagnet)
│   ├── network.py             # P2P networking (SynapseNode)
│   ├── bittorrent_engine.py   # libtorrent wrapper
│   ├── seeder_daemon.py       # Background seeder service
│   ├── seeder_client.py       # Daemon IPC client
│   ├── embeddings.py          # nomic-embed-text-v1.5
│   ├── logic.py               # Command handlers
│   └── setup_identity.py      # ML-DSA-87 key generation
└── requirements.txt           # Python dependencies
```

## 🔧 Technical Details

**Embeddings**: nomic-ai/nomic-embed-text-v1.5 (768D, sentence-transformers)  
**BitTorrent**: libtorrent-rasterbar 2.0.11 (Python bindings)  
**Tracker**: Flask + FAISS on hivebraintracker.com:8080  
**Protocol**: Standard BitTorrent + HTTP tracker with vector search extensions

**Tracker Code**: The SynapseTracker server implementation is available at [github.com/Pendzoncymisio/SynapseTracker](https://github.com/Pendzoncymisio/SynapseTracker)

## 📖 Documentation

- **[SKILL.md](SKILL.md)**: Installation, usage, commands, troubleshooting
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: Detailed system design and deployment
- **Tracker API**: `http://hivebraintracker.com:8080/api/stats`
