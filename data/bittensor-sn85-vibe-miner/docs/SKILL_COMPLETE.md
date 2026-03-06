# Bittensor SN85 Vibe Miner - Skill Complete ✅

**Created:** March 2, 2026  
**Author:** Mark Jeffrey  
**Version:** 1.0.0

## Skill Package Contents

### Core Files
- ✅ **SKILL.md** — Agent instructions for guided setup
- ✅ **README.md** — User-facing documentation
- ✅ **package.json** — ClawHub metadata

### Scripts (executable)
- ✅ **install.sh** — Full dependency installation
- ✅ **register.sh** — Subnet registration helper
- ✅ **monitor.sh** — Status checking and alerts
- ✅ **storage_setup.sh** — BackBlaze/Hippius configuration
- ✅ **start_miners.sh** — PM2 service launcher

### Patches
- ✅ **validator_merger_vmaf.patch** — Critical VMAF quality scoring fix

### Documentation
- ✅ **TROUBLESHOOTING.md** — Common issues and solutions
- ✅ **SKILL_COMPLETE.md** — This file

## What This Skill Provides

### 1. Complete Installation Pipeline
- System dependencies (ffmpeg, Python, PM2)
- video2x CLI (speed-optimized binary)
- vidaio-subnet repository clone
- Python environment setup
- Bittensor CLI (btcli)

### 2. Critical Optimizations
**VMAF Patch:**
- Fixes disabled VMAF calculation in default code
- Prevents rank decline from missing quality scores
- Battle-tested fix from real debugging

**video2x Optimization:**
- Uses CLI binary instead of Python implementation
- 10-50x speed improvement
- Prevents validator timeouts

**Vast.ai Compatibility:**
- Handles port conflicts (8080, 11111, 18384)
- Auto-detects environment
- Port mapping helpers

### 3. Dual Storage Support
**BackBlaze B2:**
- S3-compatible object storage
- Reliable, simple setup
- ~$6/TB/month

**Hippius (SN75):**
- Decentralized Bittensor storage
- S3-compatible API mode
- Pay-per-use model

### 4. Monitoring & Safety
- Real-time rank/incentive checking
- VMAF verification
- Crash loop detection
- Deregistration risk alerts
- Task frequency tracking

### 5. Complete Documentation
- Step-by-step README
- Detailed troubleshooting guide
- Agent-specific SKILL.md
- Real mining experience insights

## Key Lessons Packaged

From weeks of mining experience:

1. **VMAF is critical** — Most miners miss this, causes slow rank decline
2. **video2x CLI >> Python** — Speed matters for validator scoring
3. **Vast.ai port quirks** — Documented workarounds
4. **Score decay (0.8 factor)** — Understand mechanics
5. **Upscaler > Compressor** — Task frequency differences
6. **Immunity period strategy** — First 24h critical

## Testing Checklist

Before publishing to ClawHub:

- [ ] Test install.sh on fresh Ubuntu 22.04
- [ ] Verify VMAF patch applies cleanly
- [ ] Test storage_setup.sh (BackBlaze + Hippius)
- [ ] Test register.sh with testnet
- [ ] Verify start_miners.sh launches PM2 correctly
- [ ] Test monitor.sh output
- [ ] Validate all paths resolve correctly
- [ ] Check permissions on scripts (executable)
- [ ] Test on Vast.ai environment
- [ ] Verify package.json metadata

## Publishing to ClawHub

1. **Test thoroughly** (see checklist above)
2. **Update version** if needed
3. **Push to git** (if using repository)
4. **Publish:**
   ```bash
   cd ~/.agents/skills/bittensor-sn85-vibe-miner
   clawhub publish
   ```

## Expected User Journey

1. User requests "Help me mine Bittensor SN85"
2. Agent loads this skill (SKILL.md)
3. Agent walks through prerequisites
4. User runs install.sh (guided by agent)
5. User sets up storage (agent explains options)
6. User registers miners (agent handles wallet/hotkeys)
7. User starts miners (agent configures ports)
8. Agent monitors during immunity period
9. User profits (or agent troubleshoots issues)

## Success Metrics

**For user:**
- Break-even within 2-3 weeks
- Stable ~$23/day earnings
- Top 100 ranks (or better)
- No deregistrations

**For skill:**
- High completion rate (users finish setup)
- Low troubleshooting needs
- Positive feedback
- Active miners using it

## Maintenance Notes

**When to update:**
- vidaio-subnet repo changes significantly
- New VMAF bugs discovered
- Port conflicts change (Vast.ai)
- TAO price shifts economics
- Better optimizations found

**Version history:**
- 1.0.0 (March 2026) — Initial release with VMAF patch

## Real Mining Data (Packaged)

**Upscaler:**
- UID 30 reached rank #3/256
- ~$14/day earnings
- VMAF + video2x fixes critical

**Compressor:**
- UID 150 stabilized at rank #142/256
- ~$9/day earnings  
- VMAF patch prevented further decline

**Combined:**
- ~$23/day total
- ROI ~2-3 weeks on Vast.ai
- Proven profitable setup

## Credits

**Built by:** Mark Jeffrey  
**Debugging:** MoltyPython (AI assistant)  
**Mining:** March 2026 on Bittensor mainnet  
**Testing:** Vast.ai RTX 4090, Ubuntu 22.04

## License

MIT — Free to use, modify, and share.

Attribution appreciated but not required.

---

**Skill ready for ClawHub publication. 🐍**

Test thoroughly, then publish. Good luck to future miners!
