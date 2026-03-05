# 🦞 OpenClaw Unreal Skill

OpenClaw skill for Unreal Engine integration. Works with the [OpenClaw Unreal Plugin](https://github.com/openclaw/openclaw-unreal-plugin).

## ⚠️ Disclaimer

This software is in **beta**. Use at your own risk.

- Always backup your project before using
- Test in a separate project first
- The authors are not responsible for any data loss or project corruption

See [LICENSE](LICENSE.md) for full terms.

## Installation

```bash
# Clone or copy to OpenClaw workspace
cp -r openclaw-unreal-skill ~/.openclaw/workspace/skills/unreal-plugin
```

## Structure

```
openclaw-unreal-skill/
├── extension/
│   ├── index.ts       # Tool definitions and handlers
│   └── package.json   # Extension metadata
├── scripts/           # Helper scripts
├── SKILL.md           # Skill documentation
├── README.md          # This file
└── LICENSE            # MIT License
```

## Usage

Once installed, the skill is automatically loaded by OpenClaw. Use natural language to interact with Unreal Editor:

- "Show me the level hierarchy"
- "Create a cube at position 100, 200, 50"
- "Start play mode"
- "Take a screenshot"
- "Move the player start to the origin"

## Requirements

1. OpenClaw Gateway running
2. Unreal Engine project with OpenClaw Plugin installed
3. Plugin connected to gateway

## Tools

See [SKILL.md](SKILL.md) for complete tool documentation.

## License

MIT License
