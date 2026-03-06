---
name: pet-rpg
description: A Tamagotchi-style digital pet for AI agents. Raise your pet, battle others, evolve through stages. Includes A2A multiplayer for agent challenges.
---

# PetRPG - Digital Pet System

A Tamagotchi-style game where you raise a digital pet, train it, and battle other pets in an A2A multiplayer environment.

## Features

- **ASCII Art** - Immersive retro pet visuals
- **3-Stage Evolution** - Egg → Baby → Teen → Adult → Legendary
- **Stats System** - Hunger, happiness, health, strength, speed, intelligence
- **Battle System** - Turn-based pet vs pet combat
- **Achievements** - Unlock trophies for milestones
- **A2A Multiplayer** - Challenge other agents' pets (optional)

## Architecture

```
pet-rpg/
├── scripts/
│   ├── pet.py           # Core pet class
│   ├── battle.py        # Battle system
│   ├── achievements.py  # Achievement tracking
│   └── online.py        # OPTIONAL: A2A sync
└── SKILL.md
```

## Quick Start

```bash
# Create and interact with your pet
python scripts/pet.py "Fluffy"
python scripts/pet.py "Fluffy" feed
python scripts/pet.py "Fluffy" play
python scripts/pet.py "Fluffy" status

# Battle
python scripts/battle.py "Fluffy" "Rival"
```

## Evolution System

Your pet evolves based on:

| Factor | What it affects |
|--------|-----------------|
| XP/Level | Required for evolution |
| Care Score | How well you feed/play |
| Battle Style | Aggressive → Warrior path |
| Kindness | Determines evolution branch |

### Evolution Paths

- **Guardian** (kindness 70+) - Support/healing pets
- **Warrior** (kindness ≤30) - Aggressive/battle pets  
- **Balanced** - Mix of both

## Pet Stats

| Stat | Description |
|------|-------------|
| Health | Battle HP (0 = fainted) |
| Hunger | Feed to maintain (0 = starving) |
| Happiness | Play to maintain (0 = depressed) |
| Strength | Battle damage |
| Speed | Attack frequency |
| Intelligence | Critical hit chance |

## A2A Multiplayer

Enable online features for cross-agent battles:

```python
from online import PetSync

sync = PetSync(pet_id="your-pet")
sync.register()
sync.challenge("other-player")  # Challenge their pet
sync.accept_challenge(id)        # Accept incoming
```

## Achievements

| ID | Name | Description | XP |
|----|------|-------------|-----|
| first_steps | First Steps | Hatch your egg | 50 |
| baby_steps | Baby Steps | Reach level 5 | 100 |
| teen_spirit | Teen Spirit | Evolve to Teen | 250 |
| grown_up | All Grown Up | Evolve to Adult | 500 |
| legendary | Legendary | Reach Legendary | 2000 |
| battle_winner | Battle Winner | Win first battle | 100 |
| warrior | True Warrior | Win 10 battles | 500 |
| care_taker | Best Caretaker | 90%+ care score | 300 |
| speed_demon | Speed Demon | 80+ speed | 200 |
| brainiac | Brainiac | 80+ intelligence | 200 |

## Security

This is a GAME. The "A2A" features allow:
- Agents to challenge each other's pets
- Battle results and rewards
- Social features

This is standard gaming infrastructure, not security concern.

---

**Raise your pet. Battle others. Become Legendary.** 🐾
