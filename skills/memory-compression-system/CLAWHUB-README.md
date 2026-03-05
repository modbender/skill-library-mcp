# Memory Compression System v3.0.0

**Integrated memory management and extreme context compression for OpenClaw**

## 🚀 Quick Start

```bash
# Install via ClawHub
openclaw skill install memory-compression-system

# Or manual installation
cd /home/node/.openclaw/workspace/skills
git clone [repository-url] memory-compression-system
cd memory-compression-system
./scripts/install.sh
./scripts/enable.sh
```

## ✨ Features

- **Three compression formats**: Base64, Binary, Ultra-Compact (85%+ reduction)
- **Automatic scheduling**: Compression every 6 hours
- **Integrated search**: Unified search across all memory formats
- **Smart cleanup**: Automatic retention management
- **Health monitoring**: Built-in health checks and alerts
- **ClawHub ready**: Standard skill structure

## 📊 Performance

- **Ultra compression**: ~85% size reduction
- **Fast processing**: < 1 second for 10KB context
- **Low resource usage**: < 10MB memory, minimal CPU
- **Reliable**: Automatic backups and error recovery

## 🛠️ Usage

```bash
# Check status
./scripts/status.sh

# Manual compression
./scripts/compress.sh --format ultra

# Search memory
./scripts/search.sh "keyword"

# Cleanup old files
./scripts/cleanup.sh --days 30
```

## ⚙️ Configuration

Edit `config/default.conf`:
```bash
# Compression settings
COMPRESSION_ENABLED=true
DEFAULT_FORMAT=ultra
RETENTION_DAYS=30

# Automation
COMPRESSION_SCHEDULE="0 */6 * * *"  # Every 6 hours
CLEANUP_SCHEDULE="0 4 * * *"       # Daily at 04:00
```

## 📁 File Structure

```
memory-compression-system/
├── SKILL.md              # Full documentation
├── README.md             # User guide
├── package.json          # Node.js package
├── scripts/              # Executable scripts
│   ├── install.sh        # Installation
│   ├── enable.sh         # Enable system
│   ├── disable.sh        # Disable system
│   ├── status.sh         # Check status
│   ├── compress.sh       # Compression
│   ├── cleanup.sh        # Cleanup
│   └── search.sh         # Search
├── config/               # Configuration
├── data/                 # Data storage
├── logs/                 # Log files
├── test/                 # Test suite
└── examples/             # Usage examples
```

## 🔧 Requirements

- OpenClaw 1.0+
- Bash 4.0+
- Node.js 14+ (optional, for advanced features)
- Basic Unix utilities

## 📈 Compression Formats

1. **Base64 Compact (B64C)**: Universal compatibility, ~40% reduction
2. **Custom Binary (CBIN)**: Optimized binary, ~70% reduction
3. **Ultra Compact (UCMP)**: Extreme compression, ~85% reduction

## 🎯 Use Cases

- **Context optimization**: Reduce OpenClaw context size
- **Memory management**: Organize and compress memory files
- **Search & retrieval**: Fast search across compressed memory
- **Automation**: Scheduled compression and cleanup
- **Backup**: Automatic backups before operations

## 🚨 Safety Features

- **Automatic backups**: Before every compression
- **Integrity checks**: CRC32 checksums for all formats
- **Error recovery**: Automatic rollback on failure
- **Transaction logs**: All operations logged
- **Dry run mode**: Test before making changes

## 📊 Monitoring

```bash
# Check system health
./scripts/health.sh

# View logs
./scripts/logs.sh

# Performance metrics
./scripts/metrics.sh

# System information
./scripts/info.sh
```

## 🔄 Automation

The system automatically:
1. **Compresses memory** every 6 hours
2. **Cleans up old files** daily
3. **Updates search index** after each compression
4. **Monitors health** hourly
5. **Sends alerts** for critical issues

## 🧪 Testing

```bash
# Run test suite
cd test && ./run-tests.sh

# Test compression
./scripts/compress.sh --test

# Test cleanup
./scripts/cleanup.sh --dry-run

# Test search
./scripts/search.sh --test
```

## 📚 Documentation

- **SKILL.md**: Complete skill documentation
- **README.md**: User guide
- **examples/**: Usage examples
- **test/**: Test examples

## 🆘 Support

1. Check `logs/` directory for errors
2. Run `./scripts/health.sh` for diagnostics
3. Review `examples/troubleshooting.md`
4. Contact maintainer if needed

## 📄 License

MIT License - See LICENSE file for details.

---

**Maintainer**: tenx (@Safetbear)  
**Version**: 3.0.0  
**Last Updated**: 2026-02-15  
**ClawHub ID**: memory-compression-system