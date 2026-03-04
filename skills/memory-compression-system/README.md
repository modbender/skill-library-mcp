# Memory Compression System

Integrated memory management and extreme context compression for OpenClaw.

## Quick Installation

```bash
# Install via ClawHub
openclaw skill install memory-compression-system
```

## Features

- **Three compression formats**: Base64, Binary, Ultra-Compact
- **Automatic scheduling**: Compression every 6 hours
- **Search functionality**: Unified search across all memory
- **Backup system**: Automatic backups before operations
- **Health monitoring**: Built-in health checks

## Basic Usage

```bash
# Check status
./scripts/status.sh

# Manual compression
./scripts/compress.sh --format ultra

# Search memory
./scripts/search.sh "keyword"

# View logs
./scripts/logs.sh
```

## Documentation

Full documentation available in `SKILL.md`.

## Support

For issues and questions:
1. Check `logs/` directory
2. Run `./scripts/health.sh`
3. Review `examples/troubleshooting.md`

## License

MIT License