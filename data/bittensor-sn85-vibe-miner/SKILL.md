---
name: Bittensor Subnet 85 "Vibe Miner" Skill
description: "Guides users through setting up profitable video processing miners
  on Bittensor Subnet 85:"
---

# Bittensor Subnet 85 "Vibe Miner" Skill

**Author:** Mark Jeffrey  
**Description:** Complete automated setup for mining Bittensor Subnet 85 (VidAIo) — video upscaling and compression mining with GPU acceleration.

## What This Skill Does

Guides users through setting up profitable video processing miners on Bittensor Subnet 85:
- **Upscaler miner** — Upscale SD→HD, HD→4K using RealESRGAN (video2x)
- **Compressor miner** — High-quality video compression with AV1/HEVC
- **Storage setup** — BackBlaze B2 or Hippius decentralized storage
- **Monitoring** — Rank tracking, incentive monitoring, health checks
- **Optimizations** — Includes critical patches for VMAF quality scoring and video2x speed

## Prerequisites

**Required:**
1. **NVIDIA GPU** — RTX 3090/4090 recommended (needs NVENC hardware encoding)
2. **TAO Wallet** — 1-2 τ minimum (≈$200-400 at current prices)
3. **Storage** — BackBlaze B2 account OR Hippius access
4. **Linux** — Ubuntu 22.04+ recommended
5. **Skills** — Basic command line, SSH access if using Vast.ai

**Recommended Platform:**
- **Vast.ai** — Rent RTX 4090 for ~$0.30/hr (~$216/month)
- **Alternative** — Own hardware or other GPU cloud providers

## Expected Returns

Based on live mining data (March 2026):
- **Upscaler earnings:** ~$14/day (top 5% miners)
- **Compressor earnings:** ~$9/day (top 65% miners)
- **Combined:** ~$23/day (~$690/month)
- **Break-even:** ~2-3 weeks on Vast.ai rental

*Returns vary with TAO price, network competition, and subnet emissions.*

## How to Use This Skill

Agent will guide you through:
1. Creating/importing TAO wallet
2. Setting up GPU instance (Vast.ai or bare metal)
3. Configuring storage (BackBlaze or Hippius)
4. Installing dependencies and mining software
5. Registering on subnet (costs ~0.13 τ per miner)
6. Starting miners and monitoring performance

## What Makes This Different

**Includes hard-won optimizations:**
- ✅ **VMAF quality scoring** — Critical patch that many miners miss (causes rank decline)
- ✅ **video2x speed optimization** — 10-50x faster than default Python implementation
- ✅ **Vast.ai port workarounds** — Handles occupied ports (8080, 11111, 18384)
- ✅ **Score decay awareness** — 0.8 decay factor, strategies to maintain rank
- ✅ **Dual miner setup** — Both upscaler + compressor for maximum earnings

## Agent Instructions

When user requests SN85 mining setup:

### Phase 1: Prerequisites Check
1. Verify GPU availability (query user about Vast.ai vs own hardware)
2. Check TAO wallet exists (`btcli wallet list`)
3. Verify wallet balance (need 1-2 τ minimum)
4. Confirm storage choice (BackBlaze B2 or Hippius)

### Phase 2: Environment Setup
1. If Vast.ai: Guide through instance creation (RTX 4090, Ubuntu 22.04, Docker)
2. If bare metal: Verify NVIDIA drivers, CUDA, docker/PM2
3. Clone vidaio-subnet repository
4. Install dependencies (use `scripts/install.sh`)

### Phase 3: Storage Configuration
1. If BackBlaze: Guide through B2 bucket creation, save credentials
2. If Hippius: Set up using hippius skill, configure S3-compatible endpoint
3. Update miner configs with storage credentials

### Phase 4: Apply Patches
1. Apply VMAF calculation patch (`patches/validator_merger_vmaf.patch`)
2. Verify video2x installation (should use CLI, not Python)
3. Test GPU encoding (NVENC support)

### Phase 5: Registration
1. Create hotkeys if needed (`btcli wallet new_hotkey`)
2. Register upscaler on SN85 (costs 0.13 τ)
3. Register compressor on SN85 (costs 0.13 τ)
4. Configure port mappings (Vast.ai: map internal→external)

### Phase 6: Start Miners
1. Launch PM2 services (upscaler, compressor, workers)
2. Verify axon connectivity
3. Wait for first tasks (upscaler should receive within 30-60min)

### Phase 7: Monitor
1. Check incentive/rank with `scripts/monitor.sh`
2. Verify VMAF calculation in logs (look for "🎯 Calculating final video VMAF")
3. Alert if crash loops detected
4. Track earnings over immunity period (7200 blocks ≈ 24h)

## Key Files

- **SKILL.md** — This file
- **scripts/install.sh** — Full dependency installation
- **scripts/register.sh** — Subnet registration helper
- **scripts/monitor.sh** — Status checking and alerts
- **scripts/storage_setup.sh** — BackBlaze/Hippius configuration
- **patches/validator_merger_vmaf.patch** — Critical quality scoring fix
- **configs/miner_upscaler.json** — Upscaler configuration template
- **configs/miner_compressor.json** — Compressor configuration template

## Troubleshooting

**Compressor crash loops:**
- Check for Python syntax errors in validator_merger.py
- Verify VMAF patch applied correctly
- Look for port conflicts

**Low incentive scores:**
- Verify VMAF calculation is running (check logs for "🎯 Calculating")
- Ensure GPU encoding is working (NVENC)
- Check network connectivity (axon reachable)

**Deregistration risk:**
- Monitor incentive (if below 0.002, at risk)
- Upscaler has priority (better task frequency)
- Consider running upscaler only if capital limited

## Safety Notes

- **Test on testnet first** if unsure
- **Start with one miner** to verify setup before registering second
- **Monitor closely** during immunity period (first 24h)
- **Backups** — Keep wallet mnemonics secure and offline
- **Costs** — Registration is non-refundable, calculate ROI before committing

## Support

This skill packages real mining experience from March 2026. All optimizations are battle-tested.

**Common issues solved:**
- VMAF calculation disabled by default (causes rank decline)
- video2x Python implementation too slow (causes validator timeouts)
- Vast.ai port conflicts (8080, 11111, 18384 occupied)
- Score decay mechanics (0.8 factor, need frequent validator pings)

---

**Ready to mine?** Agent will walk you through each step. Have your TAO wallet and GPU ready.
