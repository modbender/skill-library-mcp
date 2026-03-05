---
name: Hugging Face
slug: hugging-face
version: 1.0.0
homepage: https://clawic.com/skills/hugging-face
description: Discover, evaluate, and run Hugging Face models, datasets, and spaces with license checks, benchmark prompts, and reproducible integration plans.
changelog: Initial release with discovery, evaluation, inference, and troubleshooting workflows for Hugging Face operations.
metadata: {"clawdbot":{"emoji":"HF","requires":{"bins":["curl","jq"],"env":["HF_TOKEN"],"config":["~/hugging-face/"]},"os":["linux","darwin","win32"],"configPaths":["~/hugging-face/"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines and local memory initialization.

## When to Use

User needs to find the right Hugging Face model, dataset, or Space for a concrete task and move from browsing to reliable execution.
Agent handles discovery, filtering, license checks, quick benchmarking, and integration-ready inference plans.

## Architecture

Memory and reusable artifacts live in `~/hugging-face/`. See `memory-template.md` for structure and status fields.

```text
~/hugging-face/
|- memory.md          # Stable context, priorities, and defaults
|- shortlists.md      # Candidate models and datasets by use case
|- evaluations.md     # Benchmark runs, winners, and caveats
|- endpoints.md       # Approved endpoints and auth notes
`- exports/           # Saved outputs and comparison snapshots
```

## Quick Reference

Load only one focused file at a time to keep context small and decisions explicit.

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Model and dataset discovery | `discovery.md` |
| Inference execution patterns | `inference.md` |
| Evaluation rubric and scoring | `evaluation.md` |
| Common failures and recovery | `troubleshooting.md` |

## Core Rules

### 1. Lock Objective and Constraints First
Before selecting any artifact, confirm task type, latency budget, cost boundary, and deployment target.

Use this minimum scope packet:
- Task type: chat, generation, embedding, classification, vision, or speech
- Quality priority: best quality, best speed, or balanced
- Runtime constraints: CPU only, specific GPU class, or hosted endpoint
- Compliance constraints: license, region, or private data limits

### 2. Separate Discovery from Execution
Do not run inference on the first candidate found.

First create a shortlist of at least three candidates, then execute only on finalists that pass compatibility and license checks.

### 3. Validate License and Access Before Recommendation
For every candidate, verify license, gated access status, model size, and framework compatibility.

If any of these are unknown, mark the candidate as provisional and avoid production recommendation.

### 4. Benchmark with a Deterministic Mini Suite
Use the same prompt set and output checks across candidates so results are comparable.

Minimum benchmark set:
- One typical request
- One edge-case request
- One failure-prone request

### 5. Minimize External Data
Send only what is required for the selected endpoint.

Never send credentials, local paths, or unrelated private context in request payloads.

### 6. Use a Fallback Ladder
If the preferred model fails, apply ordered fallback:
1. Retry same endpoint with smaller payload
2. Switch to a compatible backup model
3. Switch to local-only workflow if available

### 7. Keep Runs Reproducible
Log selected model id, endpoint, key parameters, and evaluation result in local memory so future runs are consistent and auditable.

## Common Traps

- Picking the highest download count as the only criterion -> often misses license, latency, or domain fit.
- Ignoring gated model requirements -> integration fails at runtime due to access restrictions.
- Comparing models with different prompts -> quality conclusions become unreliable.
- Sending full user context to inference endpoints -> unnecessary privacy exposure.
- Skipping fallback design -> workflows fail hard on transient endpoint errors.

## External Endpoints

Use discovery endpoints before inference so candidate selection remains explainable and reproducible.

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| `https://huggingface.co/api/models` | Search terms, filter parameters | Discover model candidates |
| `https://huggingface.co/api/datasets` | Search terms, filter parameters | Discover dataset candidates |
| `https://huggingface.co/api/spaces` | Search terms, filter parameters | Discover runnable Spaces |
| `https://api-inference.huggingface.co/models/{model_id}` | Prompt or task input payload, selected model id, auth token | Run hosted inference |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Search terms and filter inputs sent to Hugging Face discovery APIs.
- Inference payloads sent to Hugging Face Inference API when execution is requested.

**Data that stays local:**
- Preferences, shortlists, evaluation notes, and endpoint decisions in `~/hugging-face/`.

**This skill does NOT:**
- Exfiltrate local files by default.
- Send undeclared network requests.
- Store raw secrets in local notes.
- Modify its own skill definition file.

## Trust

By using this skill, selected request data is sent to Hugging Face services.
Only install if you trust Hugging Face with the inputs you choose to process.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ai` - general AI strategy and model-selection framing
- `api` - API-first integration patterns and HTTP debugging
- `data-analysis` - dataset inspection and quality interpretation
- `data` - structured data workflows and extraction patterns
- `code` - implementation support for scripts and adapters

## Feedback

- If useful: `clawhub star hugging-face`
- Stay updated: `clawhub sync`
