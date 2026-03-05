# Bittensor Subnet 85 "Vibe Miner" 🐍

**by Mark Jeffrey**

Complete turnkey setup for mining Bittensor Subnet 85 (VidAIo) — video upscaling and compression with GPU acceleration.

## What Is This?

SN85 pays miners in TAO for processing video:
- **Upscaling**: SD→HD, HD→4K using AI (RealESRGAN)
- **Compression**: High-quality compression with AV1/HEVC codecs

This skill packages **real mining experience** from March 2026, including critical bug fixes and optimizations that took days of debugging to discover.

## Expected Earnings

**Live data (March 2026):**
- Upscaler: ~$14/day (top 5% miners)
- Compressor: ~$9/day (top 65% miners)
- **Combined: ~$23/day** (~$690/month)

*At current TAO price (~$205). Varies with network conditions.*

## What You Need

1. **NVIDIA GPU** — RTX 3090/4090 recommended
   - Needs NVENC hardware encoding
   - Vast.ai RTX 4090: ~$0.30/hr (~$216/month)

2. **TAO Wallet** — 1-2 τ minimum (~$200-400)
   - Registration costs: ~0.13 τ per miner
   - Need buffer for immunity period

3. **Storage** — BackBlaze B2 or Hippius
   - B2: ~$6/TB/month (recommended)
   - Hippius: Decentralized (SN75), pay-per-use

4. **Linux** — Ubuntu 22.04+ recommended
   - Works on Vast.ai, bare metal, or cloud

## Quick Start

### 1. Install Dependencies

```bash
cd ~/.agents/skills/bittensor-sn85-vibe-miner
chmod +x scripts/*.sh
./scripts/install.sh
```

This installs:
- Python 3.10, ffmpeg, video2x
- PM2 process manager
- vidaio-subnet repository
- Critical VMAF patch

### 2. Set Up Storage

```bash
./scripts/storage_setup.sh
```

Choose BackBlaze B2 (easiest) or Hippius (decentralized).

### 3. Register Miners

```bash
./scripts/register.sh
```

Creates wallet, hotkeys, and registers on SN85.

**Cost:** ~0.13 τ per miner (~0.26 τ for both)

### 4. Configure & Start

Edit config files with your UIDs and storage credentials, then start miners with PM2.

### 5. Monitor

```bash
export UPSCALER_UID=<your_uid>
export COMPRESSOR_UID=<your_uid>
./scripts/monitor.sh
```

Watch ranks, incentives, and task completion during immunity period (first 24h).

## Critical Optimizations Included

This skill includes fixes that **most miners miss**:

### 1. VMAF Quality Scoring (CRITICAL)
**Bug:** Default code skips VMAF calculation  
**Impact:** Validators score you low → rank decline → deregistration  
**Fix:** Patch in `patches/validator_merger_vmaf.patch`

Without this, you'll slowly drop in rank despite completing tasks.

### 2. video2x Speed Optimization
**Bug:** Python implementation takes 17+ minutes per video  
**Impact:** Validator timeout (60s) → all tasks fail  
**Fix:** Use video2x CLI binary (10-50x faster)

Critical for upscaler to compete with top miners.

### 3. Vast.ai Port Conflicts
**Issue:** Ports 8080, 11111, 18384 occupied by Vast.ai services  
**Fix:** Use alternative ports (8384, 1111) for miners

Prevents axon binding failures.

## File Structure

```
bittensor-sn85-vibe-miner/
├── SKILL.md              # Agent instructions
├── README.md             # This file
├── scripts/
│   ├── install.sh        # Full installation
│   ├── register.sh       # Subnet registration
│   ├── monitor.sh        # Status checking
│   └── storage_setup.sh  # Storage configuration
├── patches/
│   └── validator_merger_vmaf.patch  # VMAF fix
└── configs/
    ├── miner_upscaler.json     # Upscaler config
    └── miner_compressor.json   # Compressor config
```

## Economics

**Investment:**
- GPU rental: ~$216/month (Vast.ai RTX 4090)
- Registration: ~$52 (0.26 τ for both miners)
- Storage: ~$6/month (BackBlaze B2)
- **Total monthly:** ~$274

**Revenue:**
- Expected: ~$690/month
- **Net profit:** ~$416/month
- **ROI:** ~2-3 weeks to break even

*Based on March 2026 data. Past performance ≠ future results.*

## Troubleshooting

### Compressor crash loop
- Check Python syntax in validator_merger.py
- Verify VMAF patch applied: `grep "calculate_full_video_vmaf" services/compress/validator_merger.py`
- Look for port conflicts

### Low incentive scores
- Check VMAF is running: `pm2 logs video-compressor | grep "Calculating final video VMAF"`
- Verify GPU encoding works: `nvidia-smi`
- Test axon connectivity: `curl http://<your_ip>:<port>`

### Deregistration risk
- Incentive < 0.002 = danger zone
- Upscaler has priority (better task frequency)
- Monitor closely during immunity period (first 24h)

### No tasks received
- Verify port mapping correct (Vast.ai)
- Check axon registered: `btcli subnet list --netuid 85`
- Upscaler gets tasks every 30-60min, compressor every 1-2h

## Safety

- ⚠️ **Irreversible:** Registration fees are non-refundable
- 🔒 **Security:** Keep wallet mnemonics offline and secure
- 📊 **Monitor:** Watch closely during immunity period
- 💰 **Capital:** Only invest what you can afford to lose

## Background

This skill was built from real mining experience (March 2026):
- Debugged VMAF bug causing rank decline (#28 → #164)
- Optimized upscaler (jumped to #3 rank)
- Survived 7 registration attempts before finding winning setup
- Documented every pitfall for the community

## Support

**Built by:** Mark Jeffrey (@markjeffrey on X)  
**Tested on:** Vast.ai RTX 4090, Ubuntu 22.04  
**Last updated:** March 2026

All optimizations are battle-tested. Use at your own risk.

## License

MIT — Free to use, modify, share. Attribution appreciated.

---

**Ready to mine?** Start with `./scripts/install.sh` and follow the prompts.

Questions? Check SKILL.md for detailed agent instructions.
