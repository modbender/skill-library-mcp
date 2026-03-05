# Molt Sift - Build Plan & Next Steps

## Scaffold Status: ✓ COMPLETE

Core Molt Sift skill is scaffolded and ready for development.

**Created:**
- ✓ SKILL.md (full documentation)
- ✓ Core Sifter engine (`scripts/sifter.py`)
- ✓ CLI entry point (`scripts/molt_sift.py`)
- ✓ Bounty agent scaffold (`scripts/bounty_agent.py`)
- ✓ API server scaffold (`scripts/api_server.py`)
- ✓ Validation rules (`references/rules.md`)
- ✓ Test suite (all passing)
- ✓ Sample data and schemas (`assets/`)

---

## Phase 1: MVP Feature Implementation (4-6 hours)

### 1.1 **Sifter Engine** (DONE)
- [x] JSON validation engine
- [x] Crypto/Trading/Sentiment rule sets
- [x] Quality scoring system
- [x] Signal sifting
- [x] Schema validation

### 1.2 **CLI + Library Integration** (1 hour)
- [ ] Install molt-sift as pip package
- [ ] Test CLI commands locally
  ```bash
  pip install -e .
  molt-sift validate --input assets/sample_crypto.json --rules crypto
  molt-sift sift --input assets/sample_crypto.json --rules crypto
  ```
- [ ] Verify all commands work

### 1.3 **PayAClaw API Integration** (2-3 hours)
- [ ] Implement bounty job fetching
- [ ] Job claim/process workflow
- [ ] Result submission
- [ ] Test end-to-end bounty flow

### 1.4 **x402 Solana Payment** (1-2 hours)
- [ ] Integrate x402 library
- [ ] Auto-trigger payment on validation completion
- [ ] Test payment flow

### 1.5 **Flask API Server** (1 hour)
- [ ] Create Flask app with /bounty endpoint
- [ ] Request validation
- [ ] Call Sifter + x402 payment
- [ ] Response formatting

---

## Phase 2: Production Hardening (2-3 hours)

### 2.1 **Error Handling**
- [ ] Graceful failure modes
- [ ] Retry logic for PayAClaw/x402
- [ ] Logging and monitoring

### 2.2 **Performance**
- [ ] Batch validation
- [ ] Caching for schemas
- [ ] Async bounty watching

### 2.3 **Testing**
- [ ] Integration tests
- [ ] Load testing (bounty workflow)
- [ ] Error scenario testing

---

## Phase 3: ClawHub Packaging (1 hour)

### 3.1 **Package Preparation**
- [ ] Verify SKILL.md completeness
- [ ] Create package manifest
- [ ] Test skill discovery/installation

### 3.2 **ClawHub Upload**
- [ ] Upload to ClawHub
- [ ] Verify installation in fresh environment
- [ ] Create landing page/description

---

## Timeline

| Phase | Time | Status |
|-------|------|--------|
| Scaffold | ✓ DONE | Complete |
| Phase 1 (MVP) | 4-6h | Ready to start |
| Phase 2 (Hardening) | 2-3h | After Phase 1 |
| Phase 3 (ClawHub) | 1h | After Phase 2 |

**Total: ~8-10 hours to production**

---

## Immediate Next Steps

### RIGHT NOW:
1. Install locally: `pip install -e .`
2. Test CLI works
3. Test each validation rule set

### THIS WEEK:
1. Implement PayAClaw bounty agent
2. Add x402 payment integration
3. Start earning bounties

### THEN:
1. Add Flask API server
2. Harden error handling
3. Package for ClawHub

---

## Success Metrics

✓ **Phase 1 (MVP):**
- Validation engine: 100+ operations/hour
- PayAClaw bounties: 5+ claims/day
- Payment success rate: 100%

✓ **Phase 2 (Production):**
- Zero crashes on invalid input
- <500ms validation time
- Automatic retry on transient failures

✓ **Phase 3 (ClawHub):**
- Listed and installable
- Used by at least 3 other agents
- Generating USDC revenue

---

## Code Quality

All tests passing:
```
[SUCCESS] All tests passed!
  - Crypto validation ✓
  - Invalid data handling ✓
  - Signal sifting ✓
  - Trading validation ✓
  - Missing fields detection ✓
```

Ready for development.
