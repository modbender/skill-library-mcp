# Freeride OpenCode Skill

> ⚠️ **Para funcionar, são necessárias duas API keys:**
> - **OpenCode Zen API key** - Para modelos OpenCode (MiniMax M2.1, Kimi K2.5, GLM 4.7, GPT 5 Nano)
> - **OpenRouter API key** - Para modelos OpenRouter (Trinity Large e outros)

## Descrição

Configure modelos free do OpenCode Zen com fallbacks inteligentes para otimizar custos mantendo confiabilidade.

## Quick Start

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free",
          "opencode/kimi-k2.5-free"
        ]
      }
    }
  }
}
```

## Documentação Completa

Veja [SKILL.md](SKILL.md) para documentação detalhada.

## Modelos Disponíveis

| Modelo | Provider | ID | Posição |
|--------|----------|-----|---------|
| MiniMax M2.1 | OpenCode | `opencode/minimax-m2.1-free` | Primary |
| Trinity Large | OpenRouter | `openrouter/arcee-ai/trinity-large-preview:free` | Fallback 1 |
| Kimi K2.5 | OpenCode | `opencode/kimi-k2.5-free` | Fallback 2 |

## Versão

1.2.0