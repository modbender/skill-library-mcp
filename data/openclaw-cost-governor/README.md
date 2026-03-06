# Cost Governor - Installation & Setup

Pre-flight cost control for OpenClaw subagent spawns. Prevents surprise API bills.

## Quick Install

```bash
# Via ClawHub (when published)
clawhub install cost-governor

# Or manual install
cd ~/.openclaw/workspace/skills
# Download from ClawHub or extract package
```

## First-Time Setup

1. **Create tracking file:**
```bash
mkdir -p ~/.openclaw/workspace/notes
cat > ~/.openclaw/workspace/notes/cost-tracking.md << 'EOF'
# Cost Tracking Log

## Multipliers
- Creative: 7.5x
- Research: 3x
- Technical: 2x
- Simple: 1.5x

| Date | Task | Model | Est. | Actual | Ratio | Notes |
|------|------|-------|------|--------|-------|-------|
EOF
```

2. **Set daily budget (optional):**
```bash
echo "DAILY_BUDGET=20.00" >> ~/.openclaw/workspace/.env
```

3. **Test it:**
Ask your agent: "Estimate cost for researching passive income on Opus"

## Usage

The skill activates automatically when:
- You ask to spawn a subagent
- You request a cost estimate
- Daily cron runs (if configured)

### Manual Cost Check

```
You: "How much would it cost to spawn a research agent on Opus?"
Agent: [reads SKILL.md, estimates using multipliers]
Agent: "Research task on Opus, ~3K tokens: $3.50 estimated (3x multiplier)"
```

### Pre-Flight Gate

```
You: "Research the best passive income methods"
Agent: "Estimated cost: $3.50 (Opus, research, 3x multiplier). Approve?"
You: "Yes"
Agent: [spawns, logs to cost-tracking.md]
```

## Configuration

### Adjust Multipliers

Edit `~/.openclaw/workspace/notes/cost-tracking.md`:

```markdown
## Multipliers
- Creative: 10x    # Your creative tasks run long
- Research: 2.5x   # You scope research tightly
```

Agent reads this file on each cost check.

### Set Budget Alert

Add to workspace `.env`:
```bash
DAILY_BUDGET=50.00
WEEKLY_BUDGET=300.00
```

Agent will warn when approaching limits.

## Integration with Cron (Optional)

Daily spend summary at 6 PM:

```bash
openclaw cron add \
  --name "Daily Cost Report" \
  --schedule "0 18 * * *" \
  --task "Read notes/cost-tracking.md, summarize today's spend, compare to budget"
```

## Troubleshooting

**Estimates are way off?**
- Check your multipliers in cost-tracking.md
- Log actual costs for 5-10 tasks, calculate average ratio
- Update multipliers accordingly

**Agent ignores the skill?**
- Ensure SKILL.md is in `skills/cost-governor/`
- Check skill is enabled: `ls ~/.openclaw/workspace/skills/`

**Need to bypass gate?**
- Say "proceed without cost check" (still logs)
- Or reduce approval threshold in SKILL.md (not recommended)

## Examples

### Example 1: Cheap Task (Auto-Approved)

```
You: "Quick lookup: What's the capital of France?"
Agent: [estimates $0.05, auto-approves, spawns on Haiku]
```

### Example 2: Expensive Task (Gated)

```
You: "Write a 10-chapter novel outline with character arcs"
Agent: "Estimated $15.00 (Creative task, Opus, 10K tokens, 7.5x multiplier). This is expensive. Approve, or switch to Sonnet ($2.00)?"
You: "Switch to Sonnet"
Agent: [spawns on Sonnet, logs both estimates]
```

### Example 3: Daily Summary

```markdown
## Daily Spend — 2026-02-21
| Task | Model | Est. | Actual | Ratio |
|------|-------|------|--------|-------|
| PassiveIncomeResearch | Opus | $3.50 | $4.20 | 1.2x |
| AIHardwareResearch | Sonnet | $0.80 | $0.65 | 0.8x |
| QuickLookup | Haiku | $0.05 | $0.03 | 0.6x |

**Total:** $4.35 est / $4.88 actual  
**Budget:** $15.12 remaining / $20.00 daily
```

## Contributing

Found a better multiplier? Submit a PR with your cost-tracking.md data.

## License

MIT - Free to use, modify, distribute.

## Credits

Created by the OpenClaw community. Inspired by Reddit post: "I woke up to a $340 API bill."

Don't let it happen to you.
