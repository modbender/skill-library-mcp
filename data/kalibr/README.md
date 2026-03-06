# @kalibr/openclaw

Ship agents that fix themselves. This plugin connects [OpenClaw](https://docs.openclaw.ai) to [Kalibr](https://kalibr.systems) — so your agents learn what's working in production and route around failures, degradations, and cost spikes before they impact users.

## How It Works

This plugin creates a closed feedback loop between OpenClaw and Kalibr:

**Observe** — Hooks into every LLM call (`llm_input`/`llm_output`) and agent run completion (`agent_end`). Captures which model was used, token counts, and whether the run succeeded or failed. Reports this telemetry to Kalibr via `reportOutcome()`.

**Route** — Before each agent run, calls Kalibr's `decide()` API. Kalibr uses Thompson Sampling over historical outcomes to pick the best execution path (model + tool + parameters). The plugin returns `modelOverride`/`providerOverride` to OpenClaw, which applies it to the run. 90% of traffic goes to the best-performing path. 10% explores alternatives to detect changes.

**Adapt** — As outcomes flow in, Kalibr's routing policy updates automatically. If a model degrades — provider outage, quality regression, rate limits — Kalibr detects the drop in success rate and routes around it before users notice.

OpenClaw's `modelOverride` gives you a steering wheel. Kalibr gives you a driver.

## What You Get

- **Agents that fix themselves** — Kalibr learns from real outcomes and reroutes automatically
- **Graceful degradation** — if Kalibr is unreachable, OpenClaw uses its default model. Agent runs are never blocked.
- **Zero-config telemetry** — token usage, success/failure, and duration captured automatically from hooks
- **Provider inference** — works with Anthropic, OpenAI, Google, Mistral, Meta, Cohere, and DeepSeek models out of the box

## Quick Start

**Telemetry only** (install, set API key, done):
```bash
openclaw plugins install @kalibr/openclaw
openclaw config set plugins.entries.kalibr.config.apiKey "your-api-key"
openclaw gateway restart
```

Kalibr immediately starts learning from your agent runs.

**Telemetry + routing** (add one config flag):
```jsonc
// ~/.openclaw/openclaw.json
{
  plugins: {
    entries: {
      kalibr: {
        enabled: true,
        config: {
          apiKey: "${KALIBR_API_KEY}",
          tenantId: "your-tenant-id",
          defaultGoal: "openclaw_agent_run",
          enableRouting: true,
        },
      },
    },
  },
}
```

Now Kalibr picks the best execution path for each agent run based on what's actually working.

## Configuration

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| apiKey | string | required | Kalibr API key |
| tenantId | string | — | Kalibr tenant ID |
| apiUrl | string | https://kalibr-intelligence.fly.dev | Intelligence service URL |
| defaultGoal | string | openclaw_agent_run | Goal identifier for routing and outcome reporting |
| enabled | boolean | true | Enable/disable the plugin |
| enableRouting | boolean | false | Use Kalibr decide() to override model selection before each agent run |
| captureLlmTelemetry | boolean | true | Capture LLM input/output telemetry |
| captureOutcomes | boolean | true | Report agent run outcomes |

## How Routing Works

When `enableRouting` is true, the plugin registers a `before_agent_start` hook — the only modifying hook in OpenClaw's plugin system (sequential execution, merged results, higher-priority plugins win via first-defined-wins).

Before each agent run:
1. Plugin calls `decide(goal)` against Kalibr's intelligence service
2. Kalibr returns a `DecideResponse` with model_id, confidence, exploration flag, and success_rate
3. Plugin maps model_id to OpenClaw format — via explicit lookup, slash-format passthrough, or provider inference from model name patterns
4. Plugin returns `{ modelOverride, providerOverride }` to OpenClaw

If anything fails — SDK not initialized, `decide()` throws, unknown model — the plugin returns `{}` and OpenClaw uses its default model.

## Parameter Injection (v0.2)

When `enableRouting` is true, the plugin also registers a `before_tool_call` hook. Kalibr's `decide()` response can include a `params` object alongside model_id. If present, these parameters are merged into tool call arguments — decision params take precedence over the tool's existing params on conflict.

Tool names are captured for telemetry regardless of whether routing is enabled. Every `before_tool_call` invocation records the tool name, which is included in the `reportOutcome()` metadata as `toolsCalled` and `toolCallCount`. The first tool called in a session is also sent as `toolId`.

The `before_tool_call` hook cannot redirect tool calls to different tools — only OpenClaw's `before_agent_start` can override the model. If the decision's `tool_id` differs from the current tool, the plugin logs an informational message and proceeds with parameter injection.

## OpenClaw Hooks

- `before_model_resolve` — execution path override (primary hook)
- `before_prompt_build` — context injection
- `before_tool_call` — parameter injection + tool telemetry
- `before_agent_start` — legacy fallback

## Verification

```bash
openclaw plugins list
openclaw plugins doctor
openclaw kalibr          # CLI status
/kalibr                  # Slash command in chat
```

## Roadmap

- **v0.1** — Telemetry + Routing
- **v0.2** — Parameter injection via before_tool_call, tool telemetry (current)
- **v0.3** — Exploration tuning, multi-goal policies, per-task routing, cost constraints

## Links

- [Kalibr](https://kalibr.systems)
- [Kalibr Docs](https://kalibr.systems/docs)
- [OpenClaw](https://docs.openclaw.ai)
- [OpenClaw Plugin Docs](https://docs.openclaw.ai/plugins)
- [ClawHub Skill](https://clawhub-skills.com/skills/kalibr)
- [SKILL.md](https://kalibr.systems/skill.md)

## License

MIT
