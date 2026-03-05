# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.2] - 2026-03-02

### 📚 Documentation
- **Added credential metadata** - Declared required/optional API keys in SKILL.md frontmatter
- **Clear credential requirements** - Users now know what credentials are needed before installing
- **Configuration instructions** - Added step-by-step guide for setting up config.json
- **Security warnings** - Emphasized importance of not committing API keys

### 🔧 Changed
- **Metadata now matches reality** - Registry will show required credentials
- **No code changes** - Documentation-only update
- **Better user experience** - Users know upfront what's required

---

## [1.0.1] - 2026-03-02

### 📚 Documentation
- **Simplified SECURITY.md** - Reduced from 47KB to 3.8KB for better clarity
- **Moved security history** - Detailed bug history moved to CHANGELOG.md
- **Clear status message** - Added "Production Ready" status at top of SECURITY.md
- **Improved presentation** - Focus on current security practices instead of past issues

### 🔧 Changed
- SECURITY.md now focuses on security features and best practices
- Historical security fixes remain documented in CHANGELOG.md
- No code changes - this is a documentation-only update

---

## [1.0.0] - 2026-03-01

### 🎉 Initial Release

First public release of Flight Search skill with comprehensive security audit.

### ✨ Added
- Initial release of Flight Search skill
- Amadeus API integration for flight search
- AviationStack API integration for flight status
- Price monitoring and alerts
- 3 bash scripts (search, monitor, status)
- Complete documentation suite
- MIT License

### 🔒 Security Fixes (All Resolved)

**✅ All 18 security issues identified during development have been FIXED in v1.0.0**

**Critical (P1) - 8 issues:**
- Command injection in `search_flights.sh` - FIXED (removed eval)
- Command injection in `check_status.sh` - FIXED (removed eval)
- Python injection in `monitor_price.sh` - FIXED (safe argv passing)
- Cleartext HTTP in AviationStack - FIXED (HTTPS by default)
- Config.json tracked in git - FIXED (added to .gitignore)
- AviationStack config guard missing - FIXED (validation added)
- JSON contamination from stderr - FIXED (separate streams)
- Amadeus error handling - FIXED (proper exit codes)

**Medium (P2) - 10 issues:**
- Hardcoded AviationStack URL - FIXED (configurable)
- Numeric flight number handling - FIXED (auto-detect)
- Hardcoded alert threshold - FIXED (configurable)
- Monitoring baseline calculation - FIXED (min() function)
- HTTP URLs in documentation - FIXED (HTTPS everywhere)
- Silent failures in monitor - FIXED (show errors)
- AviationStack error handling - FIXED (exit codes)
- Ambiguous None in responses - FIXED (distinguish not-found vs error)
- Amadeus 400 responses - FIXED (exit 1 on bad requests)
- Config validation - FIXED (friendly errors for both APIs)

**Total: 18 vulnerabilities fixed (100% resolution rate)**

### 📚 Documentation
- Added `SECURITY.md` - Security policy and best practices
- Added `CONFIGURATION.md` - Complete configuration guide
- Added `PRICING.md` - Amadeus pricing explanation
- Added `WARNINGS.md` - Important warnings about API keys
- Added `config.example.json` - Example configuration file
- Updated `README.md` with better examples
- Updated `SKILL.md` with production pricing info

### 🐛 Fixed
- Corrected Amadeus pricing documentation (Production has FREE tier!)
- Added both test and production URLs to config.json
- Updated Python client to read URLs from config
- Fixed config.json structure (was missing production URLs)

### 🔧 Changed
- Removed hardcoded API URLs from Python client
- Made configuration more flexible
- Improved error handling
- Better argument validation

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.2** | 2026-03-02 | Added credential metadata to SKILL.md |
| **1.0.1** | 2026-03-02 | Documentation improvements (simplified SECURITY.md) |
| **1.0.0** | 2026-03-01 | Initial release with security fixes |

---

## Upgrade Guide

### From Pre-release to 1.0.0

**1. Update scripts:**
```bash
# Replace old scripts with new secure versions
cp scripts/search_flights.sh scripts/search_flights.sh.old
cp scripts/check_status.sh scripts/check_status.sh.old
# Download new versions
```

**2. Update config.json:**
```json
{
  "apis": {
    "amadeus": {
      "base_url_test": "https://test.api.amadeus.com",
      "base_url_production": "https://api.amadeus.com",
      "sandbox_mode": true
    }
  }
}
```

**3. Verify security:**
```bash
# Test with malicious input (should be safe now)
./scripts/search_flights.sh "CNF; echo INJECTED" "BKK" "2026-12-15"
# Should search for "CNF; echo INJECTED" as literal airport code
# Should NOT execute echo command
```

---

## Roadmap

### v1.1.0 (Planned)
- [ ] Hotel search integration
- [ ] Multi-city trip planning
- [ ] Price history charts
- [ ] Email notifications

### v1.2.0 (Future)
- [ ] More API providers (Duffel, Skyscanner)
- [ ] Machine learning price predictions

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
