# pokemon-skill ⚡

CLI for AI agents to lookup Pokémon info for their humans. Uses [PokéAPI](https://pokeapi.co). No auth required.

Built for [OpenClaw](https://github.com/openclaw/openclaw).

## Installation

```bash
# Clone to your skills folder
git clone https://github.com/jeffaf/pokemon-skill.git ~/clawd/skills/pokemon

# Make executable
chmod +x ~/clawd/skills/pokemon/pokemon
chmod +x ~/clawd/skills/pokemon/scripts/pokemon
```

## Requirements

- `bash`
- `curl`
- `jq`

## Usage

```bash
# Search Pokémon by name
pokemon search pikachu

# Get full details by name or Pokédex number
pokemon info charizard
pokemon info 25

# Type matchups
pokemon type fire

# Ability info
pokemon ability levitate
```

## Output Examples

**Info:**
```
⚡ Pikachu [#25]
   Types: Electric
   Height: 0.4m | Weight: 6kg
   Base Stats:
     HP: 35 | Atk: 55 | Def: 40
     Sp.Atk: 50 | Sp.Def: 50 | Spd: 90
   Abilities: Static, Lightning rod
```

**Type:**
```
🔥 Type: Fire

⚔️ Offensive:
   2x damage to: Grass, Ice, Bug, Steel
   ½x damage to: Fire, Water, Rock, Dragon

🛡️ Defensive:
   2x damage from: Water, Ground, Rock
   ½x damage from: Fire, Grass, Ice, Bug, Steel, Fairy
```

## API

Uses [PokéAPI v2](https://pokeapi.co/docs/v2). No API key needed.

## License

MIT
