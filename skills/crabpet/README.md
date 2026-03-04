# 🦞 CrabPet — AI Pet for OpenClaw

Your OpenClaw lobster isn't just a tool anymore — it's a companion.

**CrabPet** is an OpenClaw Skill that turns your AI usage into a virtual pet experience. A pixel lobster lives alongside your agent, growing and evolving based on how you actually use OpenClaw. No extra effort needed — just keep chatting, and your pet grows.

## How It Works

CrabPet reads your existing OpenClaw memory logs (`memory/YYYY-MM-DD.md`) and calculates:

- **XP & Level** — more conversations = more growth
- **Personality** — what you use AI for shapes who your pet becomes
- **Mood** — how recently you've been active affects your pet's behavior
- **Achievements** — milestones unlock badges and bragging rights

Every pet is unique because every user's AI habits are different.

## Personalities

| Your behavior | Pet becomes |
|--------------|-------------|
| Mostly coding | 🔧 Tech Nerd — glasses, tiny laptop |
| Mostly writing | 📝 Literary Crab — scarf, thought bubbles |
| Data analysis | 📊 Scholar Crab — graduation cap |
| Design work | 🎨 Creative Crab — beret, palette |
| Heavy daily use | ⚡ Grinder Crab — headband, lightning |

Personalities are blended — you might be 70% coder + 20% writer + 10% analyst.

## What Happens When You're Away

Your pet never dies, but it does react:

- **0 days**: Working happily at its desk ✨
- **1-3 days**: Yawning, looking around for you 😴
- **3-7 days**: On the couch eating snacks, getting rounder 🛋️
- **7-14 days**: Asleep with cobwebs forming 🕸️
- **14-30 days**: Covered in dust, lights off 🏚️
- **30+ days**: Frozen solid... but blinks sometimes ❄️

When you come back, your pet wakes up with a welcome animation!

## Install

```bash
clawhub install crabpet
```

Or manually:

```bash
cd ~/.openclaw/workspace/skills/
git clone https://github.com/YOUR_USERNAME/crabpet.git
```

Restart your OpenClaw gateway after installing.

## Usage

Just talk to your OpenClaw agent naturally:

- "How is my pet?" — shows current status
- "Show me my pet card" — generates a shareable pixel art card
- "What achievements do I have?" — lists unlocked badges
- "What's my pet's personality?" — detailed personality breakdown
- "Give me a pet summary" — daily summary of pet activity

## Requirements

- OpenClaw (any version with memory/ directory)
- Python 3.8+
- Optional: Pillow (`pip install Pillow`) for PNG pet card generation

## Web Visualization

Open `web/index.html` in a browser to see your pet rendered as an animated pixel art Canvas. You can load your `pet_state.json` file or try the built-in demo mode.

## Pet Card

Generate a shareable card showing your pet's stats:

```
╔══════════════════════════════════╗
║       🦞 CRABPET CARD 🦞        ║
╠══════════════════════════════════╣
║   Name: Alex Jr.                 ║
║   Level: 15                      ║
║   Type: 🔧 技术宅                ║
║   Mood: ✨ 精力充沛              ║
║   Streak: 15 days                ║
║                                  ║
║   clawhub install crabpet        ║
╚══════════════════════════════════╝
```

With Pillow installed, you get a pixel art PNG instead — perfect for sharing on social media.

## File Structure

```
crabpet/
├── SKILL.md                 # OpenClaw skill definition
├── README.md                # This file
├── scripts/
│   └── pet_engine.py        # Core engine (XP, personality, mood, card gen)
├── references/
│   └── personality.md       # Personality system documentation
├── sprites/                 # Pixel art sprite data (JSON)
│   ├── body/                # Body sprites for each growth stage
│   ├── face/                # Face expressions (happy, sleepy, bored, excited)
│   ├── accessories/         # Personality-based accessories
│   ├── effects/             # Visual effects (sparkle, zzz, cobweb, ice, dust)
│   └── scenes/              # Background scenes (desk, sofa, bed)
├── web/
│   └── index.html           # Canvas-based pet visualization
├── tests/
│   └── test_pet_engine.py   # Unit tests
├── data/
│   └── pet_state.json       # Your pet's saved state (auto-generated)
└── output/
    └── pet_card.png          # Generated pet cards (auto-generated)
```

## Contributing

Contributions welcome! Some ideas:

- **New personalities** — add keyword sets for more AI usage patterns
- **Pixel art sprites** — design crab variations for different states
- **Web UI** — Canvas-based live pet visualization
- **More achievements** — creative milestone ideas
- **Localization** — translate personality labels and messages

## License

MIT

---

*Made with 🦞 by an OpenClaw enthusiast. Your lobster deserves a life beyond the terminal.*
