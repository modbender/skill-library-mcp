---
name: memory-compression-system
description: Integrated memory management and extreme context compression for OpenClaw. Combines memory management, compression, search, and automation in one unified skill.
version: 3.0.0
author: tenx (@Safetbear)
tags: [memory, compression, automation, optimization, search]
---

# Memory Compression System v3.0

**Integrated memory management and extreme context compression** for OpenClaw. Combines the best features of memory management and extreme compression into a single, streamlined skill with automatic scheduling.

## Quick Start

```bash
# Install skill
openclaw skill install memory-compression-system

# Enable automatic compression (runs every 6 hours)
scripts/enable.sh

# Check status
scripts/status.sh

# Manual compression
scripts/compress.sh --format ultra

# Search memory
scripts/search.sh "keyword"
```

## Features

### 1. Integrated Memory Management
- **Automatic compression**: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **Smart cleanup**: Daily cleanup of old files
- **Search functionality**: Unified search across all memory files
- **Backup system**: Automatic backups before compression

### 2. Three Compression Formats
- **Base64 Compact (B64C)**: Universal compatibility, ~40% reduction
- **Custom Binary (CBIN)**: Optimized binary, ~70% reduction  
- **Ultra Compact (UCMP)**: Extreme compression, ~85% reduction, target ~150 tokens

### 3. Automated Scheduling
- **Single cron job**: No overlapping schedules
- **Configurable**: Adjust frequency and timing
- **Reliable**: Built-in error recovery and logging
- **Efficient**: Minimal resource usage

### 4. Search & Retrieval
- **Unified search**: Across all memory formats
- **Fast indexing**: Real-time search updates
- **Context aware**: Understands compressed formats
- **Export options**: Search results in multiple formats

### 5. ClawHub Ready
- **Standard structure**: Compatible with ClawHub
- **Easy installation**: One-command setup
- **Health checks**: Built-in monitoring
- **Documentation**: Comprehensive guides

## Installation

### Via ClawHub (Recommended)
```bash
openclaw skill search memory-compression-system
openclaw skill install memory-compression-system
```

### Manual Installation
```bash
cd /home/node/.openclaw/workspace/skills
git clone [repository-url] memory-compression-system
cd memory-compression-system
scripts/install.sh
```

## Usage

### Basic Operations
```bash
# Enable automatic compression
scripts/enable.sh

# Disable automatic compression  
scripts/disable.sh

# Check system status
scripts/status.sh

# Run health check
scripts/health.sh
```

### Compression Operations
```bash
# Compress with auto format selection
scripts/compress.sh

# Compress to specific format
scripts/compress.sh --format base64
scripts/compress.sh --format binary
scripts/compress.sh --format ultra

# Decompress files
scripts/decompress.sh [filename]

# List compressed files
scripts/list.sh
```

### Search Operations
```bash
# Search across all memory
scripts/search.sh "keyword"

# Search with filters
scripts/search.sh "keyword" --format ultra --date 2026-02-15

# Export search results
scripts/search.sh "keyword" --export json

# View search history
scripts/search-history.sh
```

### Management Operations
```bash
# Cleanup old files
scripts/cleanup.sh --days 30

# Backup system
scripts/backup.sh

# Restore from backup
scripts/restore.sh [backup-file]

# View logs
scripts/logs.sh

# Performance metrics
scripts/metrics.sh
```

## Configuration

### Main Configuration File
Edit `config/default.conf`:
```bash
# Compression settings
COMPRESSION_ENABLED=true
DEFAULT_FORMAT=ultra
RETENTION_DAYS=30
MAX_COMPRESSED_FILES=100

# Cron schedule (UTC)
CRON_SCHEDULE="0 */6 * * *"  # Every 6 hours
CLEANUP_SCHEDULE="0 4 * * *" # Daily at 04:00

# Search settings
SEARCH_ENABLED=true
SEARCH_INDEX_AUTO_UPDATE=true
SEARCH_HISTORY_SIZE=1000

# Performance settings
MAX_MEMORY_MB=100
MAX_PROCESSING_TIME_SEC=300
```

### Environment Variables
```bash
export MEMORY_COMPRESSION_DEBUG=1  # Enable debug mode
export MEMORY_COMPRESSION_QUIET=0  # Disable quiet mode
export MEMORY_COMPRESSION_TEST=0   # Enable test mode
```

## Compression Formats

### Format 1: Base64 Compact (B64C)
```
VERSION:3.0
FORMAT:B64C
TIMESTAMP:2026-02-15T14:55:00Z
SIZE:1024
CHECKSUM:crc32
DATA:<base64_encoded>
```

**Features**:
- Human readable
- Easy debugging
- Universal compatibility
- CRC32 integrity check

### Format 2: Custom Binary (CBIN)
```
[Magic:CBIN][Version:3][Flags:1][Size:4][Dictionary:var][Data:var][Checksum:2]
```

**Features**:
- Optimized binary format
- Shared string dictionary
- Huffman encoding
- CRC16 integrity check

### Format 3: Ultra Compact (UCMP)
Target: ~150 tokens for complete context

**Features**:
- Extreme compression (~85% reduction)
- 3-letter abbreviations
- Bit packing
- Delta encoding
- String interning

## Automatic Scheduling

### Compression Schedule
- **Every 6 hours**: 00:00, 06:00, 12:00, 18:00 UTC
- **Operations**:
  1. Backup current memory
  2. Compress with optimal format
  3. Update search index
  4. Cleanup old files
  5. Log results

### Cleanup Schedule
- **Daily at 04:00 UTC**
- **Operations**:
  1. Remove files older than RETENTION_DAYS
  2. Archive logs
  3. Optimize search index
  4. Update statistics

### Health Check Schedule
- **Integrated with OpenClaw health checks**
- **Operations**:
  1. Check compression status
  2. Verify file integrity
  3. Monitor resource usage
  4. Report issues

## Search System

### Search Index
- **Real-time updates**: Index updates after each compression
- **Multiple formats**: Searches across all compression formats
- **Fast retrieval**: Optimized for speed
- **Context aware**: Understands compressed content

### Search Features
```bash
# Basic search
scripts/search.sh "compression"

# Advanced search
scripts/search.sh "compression ratio" --format ultra --after 2026-02-01

# Export results
scripts/search.sh "test" --export csv --output results.csv

# Search history
scripts/search.sh --history
```

### Search Index Structure
```json
{
  "version": "3.0",
  "last_updated": "2026-02-15T18:00:00Z",
  "files": [
    {
      "filename": "memory_20260215_180000.ultra",
      "format": "ultra",
      "size": 256,
      "original_size": 1024,
      "ratio": 0.25,
      "keywords": ["compression", "memory", "test"],
      "timestamp": "2026-02-15T18:00:00Z"
    }
  ]
}
```

## Error Handling & Recovery

### Automatic Recovery
- **Backup system**: Automatic backups before operations
- **Transaction logs**: All operations logged
- **Rollback capability**: Automatic rollback on failure
- **Error notifications**: Alerts for critical issues

### Manual Recovery
```bash
# Check error logs
scripts/logs.sh --error

# Restore from backup
scripts/restore.sh latest

# Repair search index
scripts/repair-index.sh

# Reset system
scripts/reset.sh --safe
```

### Common Issues & Solutions

**Issue**: Compression fails
**Solution**: Check disk space and run `scripts/repair.sh`

**Issue**: Search not working
**Solution**: Rebuild index with `scripts/rebuild-index.sh`

**Issue**: Cron job not running
**Solution**: Check with `scripts/status.sh --cron`

**Issue**: Performance degradation
**Solution**: Run `scripts/cleanup.sh --aggressive`

## Monitoring & Logging

### Log Files
- `logs/compression.log`: Compression operations
- `logs/search.log`: Search operations
- `logs/error.log`: Error messages
- `logs/performance.log`: Performance metrics
- `logs/cron.log`: Cron job execution

### Status Monitoring
```bash
# Basic status
scripts/status.sh

# Detailed health check
scripts/health.sh

# Performance metrics
scripts/metrics.sh

# System information
scripts/info.sh
```

### Alert System
- **Email alerts**: For critical errors (if configured)
- **Telegram notifications**: For important events
- **Log monitoring**: Automatic log analysis
- **Performance alerts**: For resource issues

## Testing

### Test Suite
```bash
cd test
./run-tests.sh
```

### Test Coverage
- **Unit tests**: Format encoding/decoding
- **Integration tests**: Full system integration
- **Performance tests**: Speed and memory usage
- **Error tests**: Failure scenarios
- **Cron tests**: Automatic scheduling

### Manual Testing
```bash
# Test compression
scripts/test-compression.sh

# Test search
scripts/test-search.sh

# Test cron job
scripts/test-cron.sh

# Test error handling
scripts/test-errors.sh
```

## Performance

### Compression Performance
- **Base64**: < 50ms for 10KB
- **Binary**: < 100ms for 10KB
- **Ultra**: < 200ms for 10KB
- **Target ratio**: 75-90% reduction

### Search Performance
- **Indexing**: < 100ms per file
- **Search**: < 50ms for 1000 files
- **Memory**: < 10MB for index
- **Updates**: Real-time

### Resource Usage
- **CPU**: Minimal impact
- **Memory**: < 50MB peak
- **Disk**: Configurable retention
- **Network**: Local only

## Updates & Maintenance

### Update Procedure
```bash
# Update via ClawHub
openclaw skill update memory-compression-system

# Manual update
scripts/update.sh

# Check for updates
scripts/check-updates.sh
```

### Backup Recommendations
- **Regular backups**: Weekly backups of `data/` directory
- **Export search index**: Monthly export of search index
- **Archive logs**: Monthly log archiving
- **Configuration backup**: Backup `config/` after changes

### Version History
- **3.0.0**: Integrated memory-compression-system (current)
- **2.0.0**: Extreme context compression skill
- **1.0.0**: Memory manager skill

## Contributing

### Development Setup
```bash
# Clone repository
git clone [repo-url]

# Install dependencies
npm install

# Run tests
npm test

# Build package
npm run build
```

### Code Standards
- **Bash scripts**: Follow Google Bash Style Guide
- **JavaScript**: Follow Standard JS style
- **Documentation**: Keep SKILL.md updated
- **Testing**: Add tests for new features

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit pull request

## Support

### Documentation
- **SKILL.md**: This file
- **README.md**: User documentation
- **examples/**: Usage examples
- **test/**: Test examples

### Troubleshooting
1. Check `logs/` directory
2. Run `scripts/diagnose.sh`
3. Review `examples/troubleshooting.md`
4. Contact maintainer if needed

### Community
- **ClawHub**: Skill repository
- **Discord**: OpenClaw community
- **GitHub**: Issue tracker
- **Documentation**: OpenClaw docs

## License

MIT License - See LICENSE file for details.

---

**Note**: This skill is designed for OpenClaw context optimization. Always maintain backups of important data and test in a safe environment before production use.