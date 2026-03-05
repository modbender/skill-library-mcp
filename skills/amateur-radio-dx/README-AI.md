# 🤖 AI-Enhanced DX Monitor

AI-powered propagation prediction and DXCC filtering for ham-radio-dx!

## New Features

✨ **Propagation Prediction** - ML-based scoring of spot workability  
🎯 **DXCC Filtering** - Only show DX you actually need  
📊 **Smart Scoring** - Combines rarity, workability, and your needs  
🚨 **Priority Alerts** - High-score spots flagged automatically  
⚙️ **Personalized** - Configured for your QTH, power, antenna  

---

## Quick Start

### 1. Setup (First Time)

```bash
cd /Users/awalker/clawd/skills/ham-radio-dx
python3 dx-ai-enhanced.py setup
```

**Prompts:**
- Your callsign: `W5???`
- Grid square: `EM12`
- TX power: `100`
- Needed DXCC: `VP8,VK0,3Y0,ZL,VK,ZS,P5,BS7`

This creates `dx-ai-config.json` with your station details.

### 2. Watch for Workable DX

```bash
python3 dx-ai-enhanced.py watch
```

**Output:**
```
🤖 AI-Enhanced DX Monitor
============================================================
📍 QTH: Fort Worth, TX (EM12)
📡 Station: 100W
🎯 Needed DXCC: VP8, VK0, 3Y0, ZL, VK...
⚡ Min Workability: 50%
============================================================

☀️  Solar: SFI=150 A=10 K=2 (fair)

🎯 Top Workable DX (sorted by score):

Score  Call         Band   Mode   Dist     Work%  Status
----------------------------------------------------------------------
0.92   VP8/G3XYZ    40m    CW     9234km    87%   🔥 📡
0.85   ZL2ABC       20m    FT8    11450km   82%   🔥 📡
0.78   VK6DX        17m    FT4    14230km   76%   🔥
0.65   ZS1ABC       15m    SSB    13100km   61%   
0.55   K1XYZ        20m    CW      2100km   70%   ✓

Legend: 🔥 = Needed  ✓ = Already worked  📡 = Excellent propagation

🚨 HIGH PRIORITY ALERTS:
   📻 VP8/G3XYZ on 40m CW - 87% workable, 9234km - NEEDED!
   📻 ZL2ABC on 20m FT8 - 82% workable, 11450km - NEEDED!
```

---

## How It Works

### Propagation Prediction

For each DX spot, the AI calculates:

1. **Distance Factor**  
   - Compares path distance to band's optimal range
   - 20m sweet spot: 1000-8000km
   - 40m sweet spot: 0-3000km
   - etc.

2. **Solar Condition Factor**  
   - Higher bands (10m, 12m, 15m) need good solar flux
   - Mid bands (20m, 17m, 30m) work in most conditions
   - Lower bands (40m, 80m, 160m) less solar-dependent

3. **Mode Factor**  
   - FT8/FT4: 1.0 (works in poor conditions)
   - CW: 0.9 (very efficient)
   - SSB: 0.7 (needs better conditions)

**Workability Score** = Distance × Solar × Mode  
Range: 0.0 (impossible) to 1.0 (excellent)

### DXCC Filtering

- Checks each spot's prefix against your **needed** list
- Filters out spots below minimum workability threshold
- Prioritizes rare + workable combinations

### Smart Scoring

**Total Score** = (Rarity × 0.4) + (Workability × 0.5) + Needed Bonus

- **Rarity:**  
  - 1.0 = Most wanted (VP8, VK0, 3Y0, etc.)
  - 0.8 = Rare (ZL, VK, ZS)
  - 0.6 = Needed but common
  - 0.3 = Already worked

- **Workability:** 0.0-1.0 from propagation model

- **Needed Bonus:** +0.3 if on your needed list

Spots sorted by total score (best first).

---

## Configuration

Edit `dx-ai-config.json`:

```json
{
  "operator": {
    "callsign": "W5???",
    "qth": {
      "grid": "EM12",
      "latitude": 32.7555,
      "longitude": -97.3308,
      "location": "Fort Worth, TX"
    },
    "station": {
      "power": 100,
      "antenna": "compromise (power line constraints)",
      "modes": ["FT8", "FT4", "CW", "SSB"]
    }
  },
  "preferences": {
    "priority_modes": ["FT8", "FT4"],
    "priority_bands": ["20m", "17m", "15m"],
    "min_workability_score": 0.5,
    "alert_threshold": 0.7
  },
  "needed_dxcc": ["VP8", "VK0", "3Y0", "FT5", "P5", "BS7", "ZL", "VK", "ZS"],
  "worked_dxcc": []
}
```

### Tuning Parameters

**min_workability_score** (0.0-1.0):  
- 0.3 = Show everything (lots of spots)
- 0.5 = Moderate (balanced)
- 0.7 = Only excellent conditions

**alert_threshold** (0.0-1.0):  
- 0.6 = Many alerts
- 0.7 = High priority only (recommended)
- 0.8 = Ultra rare + excellent propagation

---

## Integration with OpenClaw

### Add to TOOLS.md

```markdown
## Ham Radio DX Monitor

**AI-Enhanced mode:**
```bash
cd skills/ham-radio-dx && python3 dx-ai-enhanced.py watch
```

**Your station:**
- Callsign: W5???
- QTH: Fort Worth, TX (EM12)
- Power: 100W
- Needed DXCC: VP8, VK0, 3Y0, ZL, VK, ZS, P5, BS7
```

### Cron Job for Alerts

```bash
# Check every 30 minutes, alert on high-priority spots
*/30 * * * * cd /Users/awalker/clawd/skills/ham-radio-dx && \
  python3 dx-ai-enhanced.py watch 2>&1 | \
  grep "🚨 HIGH PRIORITY" && \
  # Send Telegram notification via OpenClaw
```

---

## Future Enhancements

**Next Steps:**
1. ✅ Propagation prediction (DONE)
2. ✅ DXCC filtering (DONE)
3. ⏳ Real solar data API integration
4. ⏳ ML model trained on historical QSO data
5. ⏳ Logbook integration (auto-populate worked_dxcc)
6. ⏳ FT8 PSK Reporter integration
7. ⏳ Auto-alerts to Telegram/Discord

**Production ML Model:**
- Train on millions of QSOs from LOTW/ClubLog
- Learn actual propagation patterns vs. predicted
- Personalize to your QTH, antenna, power
- → 90%+ accuracy predicting workability

**Integration Ideas:**
- WSJT-X UDP monitoring for FT8 alerts
- Auto-log to QRZ/LOTW when you work spotted DX
- Web dashboard showing propagation forecasts
- Mobile app with push notifications

---

## Example Use Cases

### Morning DX Check
```bash
python3 dx-ai-enhanced.py watch
```
See what rare DX is workable right now.

### Contest Preparation
```bash
# Lower threshold to see more multipliers
# Edit config: "min_workability_score": 0.3
python3 dx-ai-enhanced.py watch
```

### Chase Specific DXCC
```bash
# Edit dx-ai-config.json, set needed_dxcc to just what you want
# "needed_dxcc": ["VP8", "3Y0"]
python3 dx-ai-enhanced.py watch
```

### FT8 Mode Only
```bash
# Will prioritize FT8 spots and score them higher
# Already configured in preferences.priority_modes
python3 dx-ai-enhanced.py watch
```

---

## Troubleshooting

**"Config file not found"**
```bash
python3 dx-ai-enhanced.py setup
```

**"No workable DX spots"**
- Lower `min_workability_score` in config (try 0.3)
- Check again in 15-30 minutes
- Best DX often at sunrise/sunset

**Scoring seems wrong**
- Check your QTH lat/lon in config
- Verify power/antenna settings
- DX location database is simplified (production would use callbook API)

**Want to see all spots (no filtering)**
- Set `min_workability_score: 0.0`
- Set `needed_dxcc: []` (empty list)

---

## Technical Notes

**Propagation Model:**
Current implementation uses simplified rule-based model. For production:
- ML model trained on historical propagation data
- Real-time ionosonde data
- Path loss calculations
- Mode-specific signal requirements

**DXCC Prefix Extraction:**
Simplified algorithm. Production would use:
- Full callsign prefix database
- Country files from ARRL/DXCC
- Handle special prefixes (/P, /M, /Maritime, etc.)

**Solar Data:**
Placeholder currently returns moderate conditions. Production:
- Integrate with NOAA Space Weather API
- Real-time SFI, A/K indices
- Aurora alerts
- Solar flux forecasting

---

73 and good DX! 📻🤖
