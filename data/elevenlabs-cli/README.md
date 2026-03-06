<h1 align="center">ElevenLabs CLI Skill</h1>

<p align="center">
  AI-agent skill package for operating <code>elevenlabs-cli</code> effectively.
</p>

<p align="center">
  <a href="https://github.com/hongkongkiwi/elevenlabs-cli">
    <img src="https://img.shields.io/badge/upstream-elevenlabs--cli-black?style=for-the-badge&logo=github" alt="Upstream CLI" />
  </a>
  <a href="https://github.com/hongkongkiwi/elevenlabs-cli-skill/blob/main/SKILL.md">
    <img src="https://img.shields.io/badge/skill-SKILL.md-2D7FF9?style=for-the-badge" alt="Skill Spec" />
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/license-MIT-3DA639?style=for-the-badge" alt="MIT License" />
  </a>
</p>

> [!WARNING]
> ElevenLabs CLI is community-built and not an official ElevenLabs release.

## Purpose

This skill helps AI agents safely and quickly perform common ElevenLabs workflows:

- Text-to-speech generation
- Speech-to-text transcription
- Voice cloning and voice management
- Sound effects and audio isolation
- Dubbing and conversation/agent operations
- MCP server setup and tool filtering

## Install

### ClawHub

```bash
clawhub install elevenlabs-cli
```

### Manual

Copy `SKILL.md` into your agent skills directory.

## Requirements

```bash
export ELEVENLABS_API_KEY="your-api-key"
```

Get a key from [ElevenLabs API Settings](https://elevenlabs.io/app/settings/api-keys).

## Using the Skill

1. Install and configure `elevenlabs-cli`.
2. Load this skill in your AI client.
3. Ask for outcomes (for example: "generate narration from this script", "transcribe this call", "set up MCP with read-only tools").

## Security Notes

- Your API key is used for ElevenLabs API calls only.
- Content you process (text/audio) is sent to ElevenLabs for the requested operation.
- Prefer read-only or restricted tool modes (`--read-only`, `--disable-admin`) when exposing MCP tools to autonomous agents.

## Related Repositories

| Repository | Purpose | README |
| --- | --- | --- |
| [hongkongkiwi/elevenlabs-cli](https://github.com/hongkongkiwi/elevenlabs-cli) | Main CLI source and docs | [Open](https://github.com/hongkongkiwi/elevenlabs-cli/blob/main/README.md) |
| [hongkongkiwi/homebrew-elevenlabs-cli](https://github.com/hongkongkiwi/homebrew-elevenlabs-cli) | Homebrew tap | [Open](https://github.com/hongkongkiwi/homebrew-elevenlabs-cli/blob/main/README.md) |
| [hongkongkiwi/scoop-elevenlabs-cli](https://github.com/hongkongkiwi/scoop-elevenlabs-cli) | Scoop bucket | [Open](https://github.com/hongkongkiwi/scoop-elevenlabs-cli/blob/main/README.md) |
| [hongkongkiwi/action-elevenlabs-cli](https://github.com/hongkongkiwi/action-elevenlabs-cli) | GitHub Actions integration | [Open](https://github.com/hongkongkiwi/action-elevenlabs-cli/blob/main/README.md) |

## License

MIT.
