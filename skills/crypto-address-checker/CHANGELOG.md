# Changelog

All notable changes to the Crypto Scam Detector will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-20

### 🚀 Major Changes

This is a **complete architecture rewrite** with breaking changes.

### Added
- **Database-first architecture** - All checks now query local SQLite database
- **Instant checks** - Results in <5ms (no external API calls during checks)
- **Background sync worker** - `sync_worker.py` for Etherscan data collection
- **Transaction message analysis** - Decodes hex data and analyzes for suspicious content
- **Auto-queue system** - Unknown addresses automatically added to sync queue
- **Convenience script** - `check_address.sh` for auto-sync checking
- **Deep scam detection** - Detects "Lazarus", exploit references, phishing keywords
- **Database statistics** - `--stats` flag shows database metrics
- **Comprehensive documentation** - DATABASE_ARCHITECTURE.md with technical details
- **Encrypted key storage** - Secure API key storage with AES-256

### Changed
- **Main command** changed from `crypto_check.py` to `crypto_check_db.py`
- **Architecture** moved from direct API calls to database + background worker
- **Check latency** improved from 2-5 seconds to <5ms
- **Rate limits** eliminated for user checks (only worker hits API)
- **Risk scoring** algorithm enhanced with message analysis

### Fixed
- ✅ **False negatives** - Now detects scams missed in v1.1.3
- ✅ **Missing transaction analysis** - Full hex message decoding
- ✅ **No suspicious keyword detection** - Comprehensive keyword list
- ✅ **Hacking group references** - Detects Lazarus, Orbit Bridge, etc.
- ✅ **Private key phishing** - Identifies seed phrase scams

### Breaking Changes
- `crypto_check.py` is replaced by `crypto_check_db.py`
- Requires initial database setup (automatic on first run)
- Background worker must be run to populate database
- MCP server (`mcp_server.py`) deprecated in favor of database mode

### Migration Guide

**From v1.x to v2.0:**

1. Update the skill:
   ```bash
   clawhub update crypto-scam-detector
   ```

2. Install dependencies:
   ```bash
   bash install.sh
   ```

3. Setup API key:
   ```bash
   ./setup.sh
   ```

4. Run initial sync for addresses you care about:
   ```bash
   python3 sync_worker.py --add-address 0x...
   python3 sync_worker.py --max-jobs 1
   ```

5. Setup cron for background sync:
   ```bash
   */10 * * * * cd ~/.openclaw/workspace/skills/crypto-scam-detector && source venv/bin/activate && ETHERSCAN_API_KEY="key" python3 sync_worker.py --max-jobs 30
   ```

6. Use new checker:
   ```bash
   python3 crypto_check_db.py 0x...
   ```

### Performance
- Check speed: 2-5s → <5ms (500-1000x faster)
- API calls per check: 4 → 0 (eliminated)
- Database size: ~1KB per address
- Sync time: ~2s per address (4 API calls)

### Test Results

Address `0x098B716B8Aaf21512996dC57EB0615e2383E2f96`:

**v1.1.3 Result:**
- Risk: 0/100 (false negative)
- Missed: Lazarus references, exploit messages

**v2.0.0 Result:**
- Risk: 100/100 (correct)
- Detected: 5 suspicious transactions
- Found: Lazarus Vanguard, Orbit Bridge Hacker, private key phishing

## [1.1.3] - 2026-02-20

### Added
- No-server architecture
- Encrypted API key storage
- Better OpenClaw integration

### Changed
- Removed MCP server requirement
- Direct command-line execution

## [1.0.0] - 2026-02-19

### Added
- Initial release
- MCP server architecture
- Basic scam detection
- ChainAbuse API integration
- Local scam database
- Risk scoring (0-100)
- Multi-source verification

### Features
- Known scam address detection
- Pattern analysis
- Contract verification checks
- Balance and transaction count fetching

---

## Upgrade Recommendations

- **v1.x users:** Upgrade to v2.0 for instant checks and deep analysis
- **Production deployments:** Test v2.0 in staging before production
- **API key users:** Re-configure with `./setup.sh` or environment variable
- **Cron users:** Update cron jobs to use new `sync_worker.py` script

## Support

- **Issues:** https://github.com/trustclaw/crypto-scam-detector/issues
- **ClawHub:** https://clawhub.com/crypto-scam-detector
- **Discord:** https://discord.com/invite/clawd
