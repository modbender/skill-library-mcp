# Pet Me Master 👻💜

Interactive Aavegotchi petting via Bankr. Daily kinship ritual for bonding with your gotchis.

## Quick Start

### Setup

1. **Install Bankr skill** and configure API key at `~/.openclaw/skills/bankr/config.json`

2. **Create config:**
   ```bash
   mkdir -p ~/.openclaw/workspace/skills/pet-me-master
   cat > ~/.openclaw/workspace/skills/pet-me-master/config.json << 'EOF'
   {
     "contractAddress": "0xA99c4B08201F2913Db8D28e71d020c4298F29dBF",
     "rpcUrl": "https://mainnet.base.org",
     "chainId": 8453,
     "gotchiIds": ["9638"],
     "streakTracking": true
   }
   EOF
   ```

3. **Edit your gotchi IDs:**
   ```bash
   nano ~/.openclaw/workspace/skills/pet-me-master/config.json
   # Add your gotchi IDs to the "gotchiIds" array
   ```

4. **Verify dependencies:**
   ```bash
   cast --version  # Foundry (for on-chain reads)
   jq --version    # JSON parser
   ```

### Usage

Ask AAI:
- **"Pet my gotchi"** - Check & pet if ready (first gotchi)
- **"Pet all my gotchis"** - Batch pet all ready gotchis ⭐
- **"Pet status"** - Show all gotchis + timers
- **"When can I pet?"** - Next available time
- **"Pet gotchi #9638"** - Pet specific gotchi

## How It Works

```
You → AAI → Check on-chain cooldown → Build transaction → Bankr signs & submits → ✅ Petted!
```

**Security:** All transactions signed remotely by Bankr. No private keys used.

## Philosophy

**Less automation, more connection.**

This isn't about setting-and-forgetting. It's about checking in on your gotchis daily, like a Tamagotchi. The ritual matters.

## Optional: Auto-Reminders

Set up daily reminders with optional automatic fallback petting:

```
"Remind me to pet my gotchi in 12 hours, and if I don't respond within 1 hour, automatically pet them"
```

This combines the **ritual of interactive petting** with the **safety of automation** — best of both worlds! 💜

## Files

- `SKILL.md` - Full documentation
- `config.json` - Your gotchi IDs
- `scripts/check-cooldown.sh` - Query on-chain cooldown
- `scripts/pet-via-bankr.sh` - Execute via Bankr (secure)
- `scripts/pet-status.sh` - Show all gotchis status
- `scripts/auto-pet-fallback.sh` - Optional auto-pet after reminder

## Support

- GitHub: https://github.com/aaigotchi/pet-me-master
- Base Contract: 0xA99c4B08201F2913Db8D28e71d020c4298F29dBF
- ClawHub: https://clawhub.com/skills/pet-me-master

---

**Made with 💜 by AAI 👻**

LFGOTCHi! 🦞🚀

## v2.0.0 - Self-Perpetuating Automation (NEW!)

**The automation now schedules itself infinitely!**

After each pet (manual or auto-fallback), the system automatically creates the NEXT reminder cycle. No more one-time reminders that need manual re-setup!

### How It Works

```
Pet gotchis → Schedule next reminder (12h 5m later)
              ↓
Reminder fires → Wait 1h for response
              ↓
Auto-pet fallback → Schedule NEXT cycle
              ↓
Repeat forever! ♾️
```

### New Scripts

- `init-automation.sh` - Start the infinite cycle (run once)
- `schedule-next-reminder.sh` - Calculate next reminder times  
- `pet-all-and-reschedule.sh` - Pet + reschedule wrapper

### Setup (One-Time)

1. Pet your gotchis once (manually or via "pet all")
2. Run: `bash ~/.openclaw/workspace/skills/pet-me-master/scripts/init-automation.sh`
3. That's it! The system will now run forever.

The agent will create three cron jobs for each cycle:
- Reminder (12h 5m after pet)
- Fallback (1h after reminder)
- Reschedule (1min after fallback) - creates next cycle

**True set-it-and-forget-it automation!** 🦞💜
