# 🦦 Otterline Sports Predictions Professional | NBA & NHL AI Picks

Free Sports Betting Predictions and Picks for NBA and NHL: high win rate daily moneyline winners from Otterline's AI consensus model. Confidence-tiered (Elite -> Strong). No API key needed.

Keywords: Sports Betting, Predictions, Picks, NBA, NHL.

Otterline returns a small daily sample (up to 4 picks per league). If there are no games, it’ll say so and you can ask for another date.

For entertainment only; bet responsibly.

## Install (ClawHub)

```bash
npx clawhub@latest install otterline
```

You can also paste this GitHub repo link into OpenClaw and ask it to install the skill.

## Use In OpenClaw

Slash commands (fast + discoverable):
- `/otterline`
- `/otterline nba`
- `/otterline nhl`
- `/otterline date=2026-02-12`

Plain-English prompts:
- "What are today's Otterline picks?"
- "Any elite NBA picks today?"
- "Show me NHL picks for 2026-02-05"
- "What's the best bet today?"
- "NBA picks for tomorrow (2026-02-14)"

### What You’ll See

The response always includes:
- A clear “free sample” notice (how many picks are shown)
- Tiered picks (best tiers first)
- A link/message to upgrade to the full slate

## What You Get (Free)

Free sample picks:
- Up to **4 picks per league per day** (may be fewer; sometimes 0 if there are no games)
- **NBA** and **NHL** supported
- No authentication required

Per-pick details depend on the league:
- **NBA** includes a tier plus (often) `consensus_count` and `combo_win_rate` percentages
- **NHL** includes a tier plus `score` and a `moneyPuckWinProb` percentage

### Tiers

You’ll typically see:
- 🔥 Elite
- ✅ Verified
- 💪 Strong

Additional tier notes:
- **NHL** may include 📊 Lean
- **NBA** may include ⛔ Pass (not a bet; it means “avoid”)

## Examples

### NBA Example (Free Sample)

```
🦦 Otterline NBA Picks — 2026-02-12 (free sample)
These are FREE sample picks. Showing 2 of 3 total picks today.

🔥 Elite (consensus: 3/3, combo win rate: 69%)
  Milwaukee Bucks @ Oklahoma City Thunder -> Oklahoma City Thunder

💪 Strong (consensus: 2/3, combo win rate: 67%)
  Portland Trail Blazers @ Utah Jazz -> Utah Jazz

Full slate → otterline.club/premium
```

### NHL Example (Free Sample)

```
🦦 Otterline NHL Picks — 2026-02-05 (free sample)
These are FREE sample picks. Showing 3 of 7 total picks today.

✅ Verified (score: 6, win prob: 66%)
  Nashville Predators @ Washington Capitals -> Washington Capitals

💪 Strong (score: 4.5, win prob: 57%)
  Ottawa Senators @ Philadelphia Flyers -> Ottawa Senators

📊 Lean (score: 3, win prob: 51%)
  New York Islanders @ New Jersey Devils -> New Jersey Devils

Full slate → otterline.club/premium
```

### No-Games Example

```
No NBA games today.
Try another date (YYYY-MM-DD) or ask for NHL picks instead.
```

## Developer / API Usage (Optional)

If you want to call the free endpoints directly:

```bash
curl -s "https://gvwawacjgghesljfzbph.supabase.co/functions/v1/free-nba-picks"
curl -s "https://gvwawacjgghesljfzbph.supabase.co/functions/v1/free-nhl-picks"
curl -s "https://gvwawacjgghesljfzbph.supabase.co/functions/v1/free-nba-picks?date=2026-02-12"
```

## Want Every Pick?

The free skill gives you a daily sample. The full slate is available at:

- https://otterline.club/premium

## Links

- Website: https://otterline.club
- Premium: https://otterline.club/premium
- Twitter/X: https://twitter.com/TheOtterline
