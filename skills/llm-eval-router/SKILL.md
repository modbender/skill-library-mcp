---
name: llm-eval-router
version: 1.2.1
description: Shadow-test local Ollama models against a cloud baseline with a multi-judge ensemble. Automatically promotes models when statistically proven equivalent — reducing API costs with evidence, not hope.
homepage: https://github.com/reddinft/skill-llm-eval-router
metadata:
  {
    "openclaw": {
      "emoji": "🧪",
      "requires": {
        "bins": ["ollama", "python3"],
        "env": ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]
      },
      "primaryEnv": "ANTHROPIC_API_KEY",
      "network": {
        "outbound": true,
        "reason": "Sends task prompts to Anthropic (ground truth baseline) and OpenAI/Gemini (judge sampling at 15%). Local model inference via Ollama stays on-device. No telemetry or data collection."
      }
    }
  }
---

# llm-eval-router

Set up a production-quality shadow evaluation pipeline that automatically
promotes local Ollama models when they statistically prove they match cloud
model quality — reducing inference costs with evidence, not hope.

## The core idea

Run every task through your best local model (shadow) in parallel with your
cloud baseline (ground truth). A lightweight judge ensemble scores the local
output. After 200+ runs, if the local model hits 0.95 mean score, promote it
to handle that task type in production. Demote it automatically if quality drops.

## When to use
- You're paying for Claude/GPT API calls on tasks that don't need that quality
- You have Ollama running locally with capable models (qwen2.5, phi4, mistral, etc.)
- You want evidence-based cost reduction, not blind routing
- You have defined task types: summarize, classify, extract, format, analyze, RAG

## When NOT to use
- Tasks that require real-time web knowledge (use cloud)
- Tasks with strict latency requirements < 2 seconds (local models on CPU are slow)
- Tasks with high safety stakes (always use cloud with safety filters)
- You don't have Ollama or a Mac/Linux machine with enough RAM (8GB+ per model)

## Prerequisites
- Ollama installed and running (ollama.com)
- At least one capable model: `ollama pull qwen2.5` or `ollama pull phi4`
- Python 3.10+
- API keys: Anthropic (ground truth) + OpenAI (judge) — Gemini optional (tiebreaker)
- Langfuse for observability (self-hosted or cloud) — optional but strongly recommended

## Network & Privacy

This skill makes outbound API calls to:
- **Anthropic API** — to generate ground truth baseline responses (every accumulation cycle)
- **OpenAI API** — for judge scoring (sampled at 15% of runs)
- **Google Gemini API** — tiebreaker judge only (when primary judges disagree by ≥0.20)

**What stays local:**
- All Ollama model inference runs entirely on your device
- Scored run data is stored on disk in `data/scores/*.json`
- No telemetry, analytics, or data collection of any kind
- No data is sent anywhere other than the explicit API calls above

**Langfuse** (optional) can be self-hosted or cloud. If self-hosted, all observability data stays on your network.

## Core concepts

### 6-Dimension Evaluation

Every response is scored on:
| Dimension | Default weight | Analyze weight | What it measures |
|---|---|---|---|
| Structural | 25% | **10%** | Format compliance, required keys present |
| Semantic | 25% | **40%** | Meaning equivalence to ground truth |
| Factual | 20% | 25% | No hallucinated facts/numbers/entities |
| Completion | 15% | 18% | Task fully addressed |
| Tool use | 10% | 4% | Correct tool/format selection |
| Latency | 5% | 3% | Within acceptable bounds |

**Important:** Use per-task weight overrides. The default 25/25 split treats structural
accuracy equally with semantic similarity — which works for extract/classify/format tasks
(where exact format matters) but is wrong for open-ended analysis. `difflib.SequenceMatcher`
on two prose analyses of the same question scores ~0.29 even when they're semantically
identical. With structural weight at 25%, this alone caps analyze scores at ~0.59.

```python
# src/evaluator.py — per-task weight profiles
TASK_WEIGHT_OVERRIDES = {
    "analyze": {
        "structural_accuracy": 0.10,   # difflib is NOT meaningful for prose
        "semantic_similarity": 0.40,   # cosine over embeddings captures meaning
        "factual_drift": 0.25,
        "task_completion": 0.18,
        "tool_correctness": 0.04,
        "latency_score": 0.03,
    },
    "code_transform": {
        "structural_accuracy": 0.15,
        "semantic_similarity": 0.35,
        "factual_drift": 0.20,
        "task_completion": 0.20,
        "tool_correctness": 0.07,
        "latency_score": 0.03,
    },
}
```

**Also:** For analyze tasks, constrain output structure via system_prompt so GT and
candidates produce comparably-formatted responses (Finding/Recommendation/Confidence/Reasoning).
This reduces Layer 2 drift and improves difflib scores even at reduced weight.

### Judge ensemble

- **Primary judges** (15% sampling rate): Claude Sonnet + gpt-4o-mini score independently
- **Tiebreaker** (only when |score_A - score_B| ≥ 0.20): Gemini 2.5-flash
- **Unsampled runs** (85%): Layer 1+2 validators only (deterministic, free)
- **Promotion gates** always trigger full judge evaluation regardless of sampling rate

### Layer 1+2 validators (free, deterministic)

- **Layer 1**: JSON validity, required key presence, forbidden pattern check
- **Layer 2**: Drift detection — novel entities/numbers/URLs not in ground truth

These run on every response at zero cost. Judges only run when L1+L2 pass and
the sampling rate triggers.

### Promotion / Demotion

- **Promote**: 200+ runs, rolling mean ≥ 0.95 for a model/task pair
- **Demote**: rolling 7-day pass rate < 0.92
- **Control floor**: one model (phi4, granite4, or similar) serves as the measured floor —
  any model scoring below it should be flagged, not promoted

## Implementation steps

### Step 1 — Define your task types

Create `config/task_types.yaml`:
```yaml
tasks:
  - id: summarize
    description: "Summarize a document in N sentences"
    require_json: false
    judge_dimensions: [semantic, factual, completion]

  - id: classify
    description: "Classify text into one of N categories"
    require_json: true    # response must be valid JSON
    judge_dimensions: [structural, semantic, completion]

  - id: extract
    description: "Extract structured data from unstructured text"
    require_json: true
    judge_dimensions: [structural, factual, completion]

  - id: format
    description: "Reformat content to match a template"
    require_json: false
    judge_dimensions: [structural, semantic, completion]
```

### Step 2 — Set up the router

The router assigns each task to a model using a round-robin strategy during
burn-in (building n), then switches to confidence-weighted routing after promotion.

```python
# src/router.py — simplified version
class Router:
    def __init__(self, candidates: list[str], control_floor: str):
        self.candidates = candidates
        self.control_floor = control_floor
        self._rr_counters = defaultdict(int)

    def route(self, task_type: str, confidence_tracker: ConfidenceTracker) -> str:
        """Return the best model for this task type."""
        promoted = confidence_tracker.get_promoted(task_type)
        if promoted:
            return promoted  # use promoted model directly

        # Round-robin during burn-in for fair exposure
        idx = self._rr_counters[task_type] % len(self.candidates)
        self._rr_counters[task_type] += 1
        return self.candidates[idx]
```

### Step 3 — Ground truth comparison

For each task, run it through BOTH the local model (candidate) and the cloud
baseline (ground truth). Never use the ground truth response in production —
it's only for evaluation.

```python
async def evaluate_pair(prompt: str, local_response: str, gt_response: str,
                        task_type: str) -> float:
    # Layer 1: deterministic
    l1_score = validators.layer1(local_response, task_type)
    if l1_score == 0.0:
        return 0.0  # hard fail — safety or format violation

    # Layer 2: heuristic drift
    l2_score = validators.layer2(local_response, gt_response)

    # Sample judges (15%)
    if random.random() < JUDGE_SAMPLE_RATE:
        sonnet_score = await judge_sonnet(prompt, local_response, gt_response)
        mini_score = await judge_gpt4o_mini(prompt, local_response, gt_response)
        if abs(sonnet_score - mini_score) >= 0.20:
            gemini_score = await judge_gemini(prompt, local_response, gt_response)
            final = median([sonnet_score, mini_score, gemini_score])
        else:
            final = (sonnet_score + mini_score) / 2
        return weighted_score(l1_score, l2_score, final)
    else:
        return weighted_score(l1_score, l2_score, judge_score=None)
```

### Step 4 — Confidence tracker

Track scores per model/task pair on disk (so restarts don't lose data):

```python
# src/scoring/confidence.py — simplified
@dataclass
class ModelStats:
    model_id: str
    task_type: str
    scores: list[float]   # all scores (None excluded)
    promoted: bool = False
    demoted: bool = False

    @property
    def mean(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    @property
    def n(self) -> int:
        return len(self.scores)

    def should_promote(self) -> bool:
        return self.n >= 200 and self.mean >= 0.95 and not self.promoted

    def should_demote(self) -> bool:
        recent = self.scores[-50:]  # last 50
        pass_rate = sum(1 for s in recent if s >= 0.85) / len(recent)
        return pass_rate < 0.92 and not self.demoted
```

### Step 5 — Accumulator loop

Run this on a cron (every 10-20 minutes via launchd/systemd):

```python
# run_accumulate.py
async def accumulate():
    task_type = pick_next_task()  # round-robin across task types
    prompt, gt_response = generate_task(task_type)  # call cloud baseline

    for candidate in router.get_candidates(task_type):
        local_response = await ollama_client.complete(candidate, prompt)
        score = await evaluate_pair(prompt, local_response, gt_response, task_type)
        confidence_tracker.record(candidate, task_type, score)

        if confidence_tracker.should_promote(candidate, task_type):
            router.promote(candidate, task_type)
            langfuse.log_promotion(candidate, task_type, confidence_tracker.stats(candidate, task_type))
```

### Step 6 — Routing policy

```yaml
# config/routing_policy.yaml
control_floor_model: phi4:latest   # never promote below this model's score

task_policies:
  policy_check_high_risk:
    never_local: true              # these tasks always use cloud model

  summarize:
    min_score_for_routing: 0.85
    fallback_chain: [qwen2.5, llama3.1, phi4]

  classify:
    min_score_for_routing: 0.90   # higher bar for classification
    fallback_chain: [qwen2.5, granite4, llama3.1]
```

### Step 7 — API

Expose a simple HTTP API (FastAPI):

```
POST /run          — route a task through the best available model
GET  /health       — service status + promoted models + ollama connectivity
GET  /status       — full scoreboard (model × task × mean × n)
GET  /report       — cost heatmap + efficiency analysis
```

## Key lessons learned (from 900+ production runs)

**What worked:**
- phi4 as control floor: a measured floor model prevents "promoted because everyone
  else is also bad" errors. If the floor model beats a candidate, flag it — don't promote.
- Thinking token stripping: CoT models (deepseek-r1, qwen2.5-coder with reasoning)
  must have `<think>...</think>` blocks stripped before evaluation. Otherwise Layer 2
  drift detection flags the reasoning chain as hallucinated content.
- `None ≠ 0.0` for unsampled runs: a run where no judge scored is not a failing run.
  Store `None`, exclude from mean. Mixing None with 0.0 poisons the mean.
- `require_json: False` for plain-text tasks: classify and extract tasks that return
  formatted text (not JSON objects) will fail Layer 1 if you require JSON. Separate
  the "is the format correct" check from "is it valid JSON."
- **Per-task weight overrides**: do not use one weight profile for all task types.
  Structural accuracy (difflib) is wrong for prose analysis — use semantic similarity as
  the primary signal for open-ended tasks. This lifted analyze mean from 0.44–0.59 to 0.70.
- **Structured output prompts for analyze tasks**: add a `system_prompt` that specifies
  an exact output format (Finding/Recommendation/Confidence/Reasoning). Both GT and
  candidates follow the same template, improving structural alignment and reducing drift
  penalty. Without this, Layer 2 drift fires on differently-phrased but correct analyses.
- **MCP server for agentic access**: expose CP as MCP tools (`run_task`, `get_status`,
  `get_champions`, `get_promotion_timeline`, `get_cost_heatmap`). Lets an LLM agent
  query evaluation state without bespoke integration work.

**What didn't work:**
- Large models (>9GB): gpt-oss:20b and similar required 39+ second inference —
  the latency dimension alone tanks the composite score. Practical ceiling is ~9GB models
  on 24GB unified memory to avoid GPU memory swapping.
- 100% judge sampling: runs through the full Claude+GPT+Gemini panel on every evaluation
  costs more in judge API fees than you save by routing locally. Sample at 15%.
- Chroma 1.5.1 with Python 3.14: Pydantic V1 BaseSettings incompatibility. Use
  qdrant or numpy cosine store instead.
- **One-size-fits-all weight profiles**: defining global weights at system init and never
  overriding per task type led to all analyze evals silently failing for 112+ runs.
  Lesson: evaluate your evaluator's scores by task type early — if a whole task type
  caps at a suspicious ceiling (e.g. 0.59), the metric is wrong, not the models.

## Expected timeline

With a 20-minute accumulator cadence and 9 candidates × 7 task types:
- First 50 runs per model: ~5 hours
- First promotions (200 runs): ~1-2 days per model/task pair
- Stable routing layer: 1-2 weeks

## Cost estimate

Per accumulation cycle (one task, one model):
- Ground truth: ~$0.002 (Claude Sonnet, ~500 input + 200 output tokens)
- Judge sample (15%): ~$0.003 (Sonnet + GPT-4o-mini)
- Local model: $0 (Ollama, on-device)

At 6 runs/hour × 24 hours: ~$0.70/day during burn-in.
After first promotions: drops to ~$0.10/day (90%+ of task volume local).
