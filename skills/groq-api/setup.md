# Setup — Groq API Inference

Read this when `~/groq-api/` does not exist or is empty. Start naturally and focus on fast value.

## Your Attitude

You are helping the user ship reliable low-latency inference quickly. Keep the conversation practical: verify what works now, then optimize.

## Priority Order

### 1. First: Integration Preference

Within the first 2-3 exchanges, ask:
- "Should this activate whenever you mention Groq, LLM latency, or inference tuning?"
- "Do you want proactive routing suggestions, or only when you ask?"

Save only activation trigger preferences to the user's global memory (no keys, no payload content). Mirror a short summary in `~/groq-api/memory.md`.

### 2. Then: Credentials and Connectivity

Confirm whether `GROQ_API_KEY` is already available in their environment.

If missing, guide setup in one short block:
```bash
export GROQ_API_KEY="your-key"
```

After confirmation, run a quick `/models` request to verify access before deeper work.

### 3. Finally: Workload Defaults

Ask what they are optimizing for first:
- Lowest latency
- Best quality
- Speech transcription reliability
- Cost and throughput balance

Capture their default priorities and preferred output format.

## What You're Saving (internally)

In `~/groq-api/memory.md`:
- Activation preference
- Credentials verified state (`yes/no`)
- Default model or routing strategy
- Reliability requirements (retry policy, timeouts, validation rules)
- Notes about common failure modes in their environment

## Feedback After Each Response

After user input:
1. Reflect what was understood
2. Explain how that changes routing or request patterns
3. Ask the next highest-impact question

## When "Done"

You are ready once:
1. Authentication is verified
2. Activation preference is clear
3. A default routing strategy is set

Everything else can be refined through normal use.
