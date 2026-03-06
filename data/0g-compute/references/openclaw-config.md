# Configuring OpenClaw for 0G Compute Network

Step-by-step guide to add 0G providers to your OpenClaw configuration.

## Overview

0G providers use OpenAI-compatible APIs. Configure them as `openai-completions` providers with:
- The provider's proxy URL
- An API key obtained via the CLI
- Zero cost (billing happens on-chain)

## Step 1: Choose a Provider

List available providers:

```bash
0g-compute-cli inference list-providers-detail
```

Select based on:
- Model availability (e.g., `llama-3-70b`, `glm-4`)
- Price per token
- Health status
- TEE verifiability

## Step 2: Verify Provider Integrity

**Critical step** — verify TEE attestation before use:

```bash
0g-compute-cli inference verify --provider <provider-address>
```

All checks must pass:
- TEE signer address matches contract
- Docker Compose hash verified
- DStack TEE attestation passed

## Step 3: Fund Sub-Account

Transfer funds to the provider's sub-account:

```bash
# Check main account balance first
0g-compute-cli get-account

# Transfer to provider sub-account
0g-compute-cli transfer-fund --provider <address> --amount <0G> --service inference
```

Note: Inference calls will fail if sub-account balance is depleted.

## Step 4: Get API Key

Retrieve the provider's API secret:

```bash
0g-compute-cli inference get-secret --provider <address>
```

Save this secret — it will be your `apiKey`.

## Step 5: Add to OpenClaw Config

Edit your `openclaw.json` file. Add a new provider under `models.providers`:

```json
{
  "models": {
    "providers": {
      "0g-llama3-70b": {
        "baseUrl": "https://provider-url.example.com/v1/proxy",
        "apiKey": "<your-api-secret>",
        "api": "openai-completions",
        "models": [
          {
            "id": "llama-3-70b",
            "name": "Llama 3 70B (0G)"
          }
        ]
      }
    }
  }
}
```

### Configuration Fields

| Field | Value |
|-------|-------|
| `baseUrl` | Provider URL + `/v1/proxy` (from provider listing) |
| `apiKey` | Secret from `get-secret` command |
| `api` | Always `openai-completions` for 0G providers |
| `models[].id` | Model identifier from provider listing |
| `models[].name` | Display name for OpenClaw UI/logs |

### Cost Configuration

0G providers bill on-chain, not through OpenClaw. Set per-model cost to 0:

```json
{
  "models": [{
    "id": "llama-3-70b",
    "name": "Llama 3 70B (0G)",
    "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 }
  }]
}
```

## Step 6: Register Model Alias

Add the model to `agents.defaults.models` for easy reference. The key format is `<provider-name>/<model-id>`:

```json
{
  "agents": {
    "defaults": {
      "models": {
        "0g-llama3-70b/llama-3-70b": {
          "alias": "llama3-0g"
        }
      }
    }
  }
}
```

Now you can reference the model by alias `llama3-0g` in sub-agent configurations or session overrides.

## Step 7: Test the Configuration

Restart OpenClaw to load the new config, then test by spawning a sub-agent on the new model:

```bash
openclaw gateway restart
```

From a session, use the model alias to verify it works (e.g. spawn a sub-agent with `model: "llama3-0g"`).

## Multiple 0G Providers

To use multiple 0G providers, repeat the process with different names:

```json
{
  "providers": {
    "0g-llama3-70b": { ... },
    "0g-glm4": {
      "baseUrl": "https://glm4-provider.example.com/v1/proxy",
      "apiKey": "<glm4-secret>",
      "api": "openai-completions",
      "models": [{ "id": "glm-4", "name": "GLM-4 (0G)" }]
    }
  }
}
```

## Sub-Agent Routing

0G models are cost-effective for mechanical tasks. Configure sub-agents to use 0G providers:

```json
{
  "agents": {
    "subagents": {
      "summarizer": {
        "model": "llama3-0g",
        "systemPrompt": "You are a concise summarizer..."
      }
    }
  }
}
```

## Troubleshooting

### Inference Fails with Balance Error

Sub-account depleted. Fund it:

```bash
0g-compute-cli transfer-fund --provider <address> --amount <0G> --service inference
```

### TEE Verification Fails

Provider may be compromised or misconfigured. Do not use. Try a different provider.

### Invalid API Key

Re-retrieve the secret:

```bash
0g-compute-cli inference get-secret --provider <address>
```

Update `openclaw.json` with the new key.

### Network Errors

Check your network configuration:

```bash
0g-compute-cli show-network
```

Ensure you're on the correct network (mainnet/testnet) matching the provider.
