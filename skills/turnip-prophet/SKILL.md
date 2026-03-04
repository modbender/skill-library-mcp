---
name: turnip-prophet
description: Predict Animal Crossing New Horizons turnip prices using the game's exact algorithm. Use when a user asks about turnip prices, ACNH turnips, stalk market, turnip predictions, when to sell turnips, or bell profit from turnips.
repository: https://github.com/nicholasjackson/openclaw-turnip-profit
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3", "jq"] },
        "install":
          [
            {
              "id": "python-deps",
              "kind": "shell",
              "label": "Install Python dependencies (matplotlib)",
              "command": "pip3 install matplotlib"
            },
            {
              "id": "jq-debian",
              "kind": "shell",
              "label": "Install jq (Debian/Ubuntu)",
              "command": "sudo apt-get update && sudo apt-get install -y jq",
              "when": "debian"
            },
            {
              "id": "jq-macos",
              "kind": "shell",
              "label": "Install jq (macOS)",
              "command": "brew install jq",
              "when": "darwin"
            }
          ]
      }
  }
---

# Turnip Prophet - Animal Crossing Turnip Price Predictor

Predicts Animal Crossing: New Horizons turnip prices using the game's actual algorithm.

## ⚠️ IMPORTANT: Always Read Memory First!

**Before doing ANYTHING**, read the weekly data file:
```
memory/turnip-week.json
```
This contains the buy price, previous pattern, and all known prices for the current week. **Do not ask the user for data you already have.** Only ask for new/missing prices.

When the user gives a new price, **update `memory/turnip-week.json` immediately** with the new value before running the prediction.

### Weekly Data Format (`memory/turnip-week.json`)
```json
{
  "week_start": "2026-02-15",
  "buy_price": 96,
  "previous_pattern": 1,
  "prices": [84, 81, 78, null, null, null, null, null, null, null, null, null],
  "labels": ["Mon AM", "Mon PM", "Tue AM", "Tue PM", "Wed AM", "Wed PM", "Thu AM", "Thu PM", "Fri AM", "Fri PM", "Sat AM", "Sat PM"]
}
```

On Sundays, create a fresh file with the new buy price and reset prices to all nulls.

## Triggers

Activate when user mentions:
- "turnip prices" or "turnip price"
- "ACNH turnips" or "Animal Crossing turnips"
- "stalk market"
- "turnip prophet" or "turnip prediction"
- "bell profit" with context of turnips
- Any question about when to sell turnips in Animal Crossing

## Privacy & Data Storage

This skill stores local configuration data **only on your machine** in `memory/turnip-config.json`. No data is sent to external servers.

**What gets stored (if you enable reminders):**
- Channel name (telegram/whatsapp/discord/signal)
- Your user ID on that channel
- OpenClaw binary path
- Setup timestamp

**Why:** These values are needed so the cron reminders can send messages to the correct place without hard-coded values.

**Where:** Stored locally in the skill's memory directory on your OpenClaw instance. Not shared, not uploaded, not visible to anyone else.

**How to disable/reset:**
```bash
rm ~/.openclaw/workspace/skills/turnip-prophet/memory/turnip-config.json
```

**Removing cron entries:**
```bash
# Edit crontab and remove the turnip-prophet lines
crontab -e
```

**Important:** You must explicitly confirm the setup flow before any config is saved. Declining the setup offer means nothing is stored.

## Credentials & Permissions

**The skill itself does not request or store any API keys or credentials.**

However, **if you enable cron reminders**, the installed cron jobs will:
- Use your local `openclaw` CLI binary
- Send messages using your existing OpenClaw configuration and credentials
- Operate with whatever permissions your OpenClaw instance has

**What this means:**
- Automated reminders will be sent **as you**, using your OpenClaw identity
- The cron jobs require OpenClaw to be running and properly configured
- Messages are sent through your configured channels (Telegram/WhatsApp/etc.) using your bot tokens or API credentials

**You are granting permission for:**
- Automated message sending on your behalf
- Using your existing messaging channel credentials
- Running scheduled tasks that invoke `openclaw gateway call message.send`

If you're uncomfortable with automated messaging using your credentials, **do not enable the cron reminders**. The core prediction feature works fine without them.

## Daily Reminders (Optional)

On first use, offer to set up daily reminders with an interactive flow:

### Interactive Setup Flow (Agent Instructions)

**On first trigger (when user asks about turnips for the first time):**

1. **Check if already configured:**
   ```bash
   test -f memory/turnip-config.json && echo "configured" || echo "not configured"
   ```

2. **If NOT configured, offer setup:**
   > "Want daily turnip reminders? I can ping you:
   > • Sunday 8am: Check Daisy Mae's price
   > • Mon-Sat noon + 8pm: Check Nook's prices  
   > • Saturday 9:45pm: Final warning
   > 
   > Reply 'yes' to set up, or 'no' to skip."

3. **If user says yes, auto-detect config:**
   - **Channel:** Extract from inbound context JSON `"channel"` field (telegram/whatsapp/discord/signal)
   - **Target ID:** Extract from inbound context JSON `"sender_id"` field
   - **OpenClaw path:** Run `which openclaw` or use `/usr/local/bin/openclaw`
   - **Skill dir:** Use the absolute path to this skill's directory

4. **If auto-detection fails:**
   - Ask user for missing values explicitly
   - Validate before proceeding

**Store config in `memory/turnip-config.json`:**
```json
{
  "channel": "telegram",
  "target": "8577655544",
  "openclaw_bin": "/usr/local/bin/openclaw",
  "skill_dir": "/home/user/.openclaw/workspace/skills/turnip-prophet",
  "configured_at": "2026-02-23T10:30:00Z"
}
```

**Generate and show cron entries:**
Show the user exactly what will be added, with their specific values. Example:
```bash
# Turnip Prophet reminders for telegram:8577655544
0 8 * * 0 /usr/local/bin/openclaw gateway call message.send --params '{"channel":"telegram","target":"8577655544","message":"🔔 Sunday! Check Daisy Mae'\''s turnip price (90-110 bells) and buy your turnips 🥬"}' 2>&1 | logger -t turnip-prophet
0 12 * * 1-6 /usr/local/bin/openclaw gateway call message.send --params '{"channel":"telegram","target":"8577655544","message":"🔔 Time to check Nook'\''s Cranny turnip prices!"}' 2>&1 | logger -t turnip-prophet
0 20 * * 1-6 /usr/local/bin/openclaw gateway call message.send --params '{"channel":"telegram","target":"8577655544","message":"🔔 Evening price check: Check Nook'\''s Cranny!"}' 2>&1 | logger -t turnip-prophet
45 21 * * 6 /usr/local/bin/openclaw gateway call message.send --params '{"channel":"telegram","target":"8577655544","message":"⏰ FINAL CALL: Turnips expire at 10 PM! Sell now or they'\''ll rot 🗑️"}' 2>&1 | logger -t turnip-prophet
```

Replace channel/target with detected values. Escape single quotes properly.

**Show user what will be stored (before confirmation):**
```
This will save:
• Channel: telegram
• User ID: 8577655544
• Location: memory/turnip-config.json (local only)

This data is stored locally on your machine and is needed so cron reminders can send messages to you.
You can delete the config file anytime with: rm memory/turnip-config.json

Continue? Reply 'confirm' to proceed, or 'cancel' to skip.
```

**On confirmation:**
1. Write config to `memory/turnip-config.json`
2. Generate a safe install command and show it to the user:
   ```bash
   # Save the cron entries to a temp file
   cat > /tmp/turnip-cron-$$.txt <<'TURNIP_EOF'
   [generated entries]
   TURNIP_EOF
   
   # Review the file
   cat /tmp/turnip-cron-$$.txt
   
   # If it looks good, install:
   (crontab -l 2>/dev/null; cat /tmp/turnip-cron-$$.txt) | crontab -
   ```
3. Ask user to run the commands and confirm when done
4. Reply: "✅ Reminders configured. You'll only get pings for missing data. Check `crontab -l` to verify installation. To remove: `rm memory/turnip-config.json` and remove the cron entries."

**On rejection/cancel:**
- Reply: "No problem. No data was stored. You can set this up anytime by asking about turnip prices again."

### Cron Handler (scripts/cron_handler.sh)

The cron script reads from `memory/turnip-config.json` for channel/target:

```bash
CONFIG_FILE="$SKILL_DIR/memory/turnip-config.json"
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Config not found: $CONFIG_FILE" >&2
    exit 1
fi

CHANNEL=$(jq -r '.channel' "$CONFIG_FILE")
TARGET=$(jq -r '.target' "$CONFIG_FILE")
OPENCLAW_BIN=$(jq -r '.openclaw_bin' "$CONFIG_FILE")
```

**Event types:**

**sunday-daisy:**
- Check if `memory/turnip-week.json` has a buy_price for current week
- If missing: Send reminder "🔔 Sunday! Check Daisy Mae's turnip price (90-110 bells) and buy your turnips 🥬"
- If already set: Stay silent

**daily-check:**
- Determine which price slot is currently active (Mon AM/PM through Sat PM)
- Check if that slot is filled in `memory/turnip-week.json`
- If missing: Send reminder "🔔 [Day] [AM/PM]: Check Nook's Cranny turnip prices!"
- If already filled: Stay silent

**saturday-final:**
- Check how many prices are still null
- If any missing OR no buy_price: Send "⏰ FINAL CALL: Turnips expire at 10 PM! Sell now or they'll rot 🗑️"
- If all prices known: "⏰ Last chance to sell turnips tonight!"

Send via: `"$OPENCLAW_BIN" gateway call message.send --params "{\"channel\":\"$CHANNEL\",\"target\":\"$TARGET\",\"message\":\"...\"}"`

## How It Works

The skill uses a Python implementation of the actual ACNH turnip price algorithm to predict future prices based on:
- Your Sunday buy price (90-110 bells)
- Any known sell prices from this week
- Previous week's pattern (if known)

There are 4 price patterns:
- **Pattern 0 (Fluctuating)**: High-low-high-low-high waves
- **Pattern 1 (Large Spike)**: Decreasing then massive spike (up to 6x)
- **Pattern 2 (Decreasing)**: Consistently declining (bad week)
- **Pattern 3 (Small Spike)**: Decreasing then moderate spike (up to 2x)

## Usage Instructions

When triggered:

1. **Read `memory/turnip-week.json`** — get all known data
2. **Update the file** if the user provided a new price
3. **Run the prediction** with all known data
4. **Generate a chart** and send it with the prediction summary

### Running the Prediction

```bash
echo '{"buy_price": 96, "prices": [84, 81, 78, null, null, null, null, null, null, null, null, null], "previous_pattern": 1}' | python3 scripts/turnip_predict.py
```

- `prices` array: [Mon AM, Mon PM, Tue AM, Tue PM, Wed AM, Wed PM, Thu AM, Thu PM, Fri AM, Fri PM, Sat AM, Sat PM]
- Use `null` for unknown prices

### Generating the Chart

After running the prediction, generate a chart image:

```bash
python3 scripts/generate_chart.py <buy_price> '<known_json>' '<mins_json>' '<maxs_json>' /tmp/turnip-chart.png
```

- `buy_price`: Sunday buy price (integer)
- `known_json`: array of 12 values, `null` for unknown (from `memory/turnip-week.json` prices)
- `mins_json`: array of 12 min values from the prediction output
- `maxs_json`: array of 12 max values from the prediction output
- All script paths are relative to the skill directory: `skills/turnip-prophet/`

Then send the chart image via the message tool with a caption containing the prediction summary.

**Always include the chart with every prediction update.**

## Presenting Results

Send the chart image via message tool, then reply with a conversational analysis. Don't be robotic — have a personality about it.

**Format:**
1. Chart image with brief caption (buy price, known prices)
2. Text reply with:
   - **Pattern odds** as a bullet list with emoji reactions (😬🤞🚀💀 etc.)
   - **Brief colour commentary** — what the data actually means in plain English
   - **"My take:"** — a specific, opinionated recommendation for what to do next (which price to check, when to sell, when to hold)

**Example:**
```
Pattern odds:
📉 Decreasing: 84.7% 😬
📈 Large Spike: 15.1% 🤞
📊 Small Spike: 0.1%

Not great. Three consecutive drops is strongly pointing to a decreasing week. But there's still a 15% chance of a large spike hiding — if it happens, it'd be Wed-Fri with prices up to 576 bells.

My take: Check the Tuesday PM price. If it drops again, this week is almost certainly a bust — sell and cut your losses. If it jumps up, the spike is on. 🎰
```

Be direct, be opinionated, skip patterns with 0% probability.

## Pattern Descriptions for Users

- **Fluctuating (0)**: Prices go up and down in waves — sell when above 120-130
- **Large Spike (1)**: Prices drop then SPIKE huge (400-600 bells) — wait for it!
- **Decreasing (2)**: Prices keep falling all week — sell ASAP to cut losses
- **Small Spike (3)**: Prices drop then small bump (150-200) — sell during the bump

## Error Handling

If the script fails or returns an error:
- Explain what went wrong in simple terms
- Ask user to double-check their input data
- Suggest they try again with corrected information

## Notes

- Predictions are probabilistic, not guaranteed
- The algorithm matches the actual game code
- More known prices = better predictions
- Sunday buy price is required
- Previous week's pattern helps but isn't required
