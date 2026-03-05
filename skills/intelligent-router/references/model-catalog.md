# Model Selection Guide

This guide helps you evaluate and select LLM models for each tier in the intelligent router system. Rather than prescribing specific models, it teaches you how to assess models for your own setup.

## Understanding the Tier System

### SIMPLE Tier — Efficiency First

**Purpose:** High-frequency, low-complexity operations where speed and cost matter more than sophistication.

**Ideal characteristics:**
- **Cost:** Under $0.50/M input tokens
- **Speed:** Fast response times (< 2 seconds)
- **Reliability:** Consistent output for routine tasks
- **Context:** 8K-32K context window sufficient

**Good for:**
- Status checks and monitoring
- API calls with minimal processing
- Simple summarization
- Data extraction and filtering
- Heartbeat operations

**Not good for:**
- Complex reasoning
- Creative writing
- Multi-step logic
- Code generation

**How to evaluate:**
Test your candidate model on these tasks:
```
Task: "Summarize this JSON: {simple_status_object}"
Task: "Extract error messages from this log"
Task: "Check if this API response indicates success"
```

If it handles these reliably without overthinking, it's SIMPLE tier material.

**Common model types:**
- Small parameter models (< 10B parameters)
- Distilled versions of larger models
- Provider "mini" or "fast" variants
- Local models optimized for speed

---

### MEDIUM Tier — Balanced Capability

**Purpose:** General-purpose work requiring moderate intelligence — the workhorse tier.

**Ideal characteristics:**
- **Cost:** $0.50-$3.00/M input tokens
- **Capabilities:** Good at code, reasoning, and analysis
- **Context:** 32K-128K context window
- **Quality:** Reliable output, minimal hallucination

**Good for:**
- Code fixes and refactoring
- Research and documentation
- Data analysis
- Testing and validation
- General Q&A

**Not good for:**
- Complex architecture decisions
- Security-critical operations
- Novel algorithm design
- Multi-file system builds

**How to evaluate:**
Test your candidate model on these tasks:
```
Task: "Fix the bug in this 20-line Python function"
Task: "Research and summarize recent developments in [topic]"
Task: "Review this code for obvious issues"
```

If it produces competent, correct results most of the time, it's MEDIUM tier material.

**Common model types:**
- Mid-size models (10B-70B parameters)
- Code-specialized models
- General-purpose frontier models from previous generations
- Cost-optimized variants of premium models

---

### COMPLEX Tier — High Quality

**Purpose:** Sophisticated work requiring deep reasoning, creativity, or technical expertise.

**Ideal characteristics:**
- **Cost:** $3.00-$5.00/M input tokens (quality justifies cost)
- **Capabilities:** Excellent code, strong reasoning, creative problem-solving
- **Context:** 100K+ context window
- **Quality:** Reliable on hard problems, minimal supervision needed

**Good for:**
- Feature development (multi-file)
- Complex debugging
- Architectural design
- Algorithm development
- Technical writing

**Not good for:**
- Routine monitoring (overkill)
- Simple repetitive tasks (wasteful)
- High-frequency operations (too expensive)

**How to evaluate:**
Test your candidate model on these tasks:
```
Task: "Design a caching layer for this API with Redis"
Task: "Debug this race condition in concurrent code"
Task: "Implement a new authentication flow with JWT"
```

If it produces production-quality results with minimal revision, it's COMPLEX tier material.

**Common model types:**
- Current-generation frontier models
- Large parameter models (70B-200B+)
- Models with extended reasoning capabilities
- Specialized code generation models

---

### CRITICAL Tier — Best Available

**Purpose:** High-stakes operations where failure has serious consequences.

**Ideal characteristics:**
- **Cost:** Secondary to quality and reliability
- **Capabilities:** State-of-the-art across all dimensions
- **Context:** Large context (200K-1M+) for thorough analysis
- **Quality:** Exceptional accuracy, careful reasoning, safety-aware

**Good for:**
- Security audits
- Production deployments
- Financial analysis
- Legal document review
- High-stakes decision support

**Not good for:**
- Routine operations (expensive overkill)
- Development/testing (use COMPLEX instead)
- High-volume tasks (cost prohibitive)

**How to evaluate:**
Test your candidate model on these tasks:
```
Task: "Audit this authentication code for security vulnerabilities"
Task: "Review this database migration for potential issues"
Task: "Analyze this financial data for compliance"
```

If it identifies subtle issues and provides thorough, careful analysis, it's CRITICAL tier material.

**Common model types:**
- Flagship frontier models (the "flagship" from each major provider)
- Models with extended thinking/reasoning modes
- Large context models (500K-1M+ tokens)
- Models marketed for enterprise/production use

---

## Capability Matrix

Different tiers need different capabilities. Use this matrix to match models to requirements:

| Capability | SIMPLE | MEDIUM | COMPLEX | CRITICAL |
|------------|--------|--------|---------|----------|
| **Text comprehension** | ✓ Basic | ✓✓ Good | ✓✓✓ Excellent | ✓✓✓ Excellent |
| **Code generation** | ✗ Limited | ✓✓ Good | ✓✓✓ Excellent | ✓✓✓ Excellent |
| **Reasoning** | ✓ Basic | ✓✓ Moderate | ✓✓✓ Deep | ✓✓✓ Deep + careful |
| **Vision** | ✗ Optional | ✓ Helpful | ✓✓ Useful | ✓✓ Important |
| **Function calling** | ✗ Rare | ✓ Useful | ✓✓ Important | ✓✓✓ Critical |
| **Context window** | 8K-32K | 32K-128K | 100K-200K | 200K-1M |
| **Extended thinking** | ✗ Not needed | ✗ Wasteful | ✓ Beneficial | ✓✓ Valuable |

**Key:**
- ✓ = Basic/sufficient
- ✓✓ = Good/recommended
- ✓✓✓ = Excellent/required
- ✗ = Not needed/wasteful

---

## Provider Landscape

Understanding different providers helps you build a well-rounded model portfolio.

### Major Cloud Providers

**Anthropic (Claude)**
- **Strengths:** Excellent reasoning, code quality, safety-focused
- **Tiers:** Haiku (SIMPLE/MEDIUM), Sonnet (COMPLEX), Opus (CRITICAL)
- **Cost range:** $0.25-$15/M input
- **Best for:** General purpose, code, careful reasoning

**OpenAI (GPT)**
- **Strengths:** Broad capabilities, function calling, good ecosystem
- **Tiers:** GPT-4o Mini (MEDIUM), GPT-4o (COMPLEX), o1/o3 (CRITICAL)
- **Cost range:** $0.15-$15/M input
- **Best for:** Function calling, multimodal tasks, integrations

**Google (Gemini)**
- **Strengths:** Large context windows, multimodal, good at code
- **Tiers:** Flash (MEDIUM), Pro (COMPLEX), Ultra (CRITICAL)
- **Cost range:** $0.075-$7/M input
- **Best for:** Long documents, multimodal tasks, context-heavy work

**Meta (Llama)**
- **Strengths:** Open weights, customizable, cost-effective
- **Tiers:** Llama 3.3 70B (MEDIUM/COMPLEX)
- **Cost range:** Free (self-hosted) or $0.40-$0.80/M via providers
- **Best for:** Cost optimization, self-hosting, customization

### Specialized Providers

**DeepSeek**
- **Strengths:** Excellent at code, math, reasoning
- **Cost:** Very competitive ($0.14-$0.55/M typically)
- **Best for:** Code-heavy workloads

**Cohere**
- **Strengths:** Optimized for retrieval, enterprise features
- **Best for:** RAG applications, search, embeddings

**Mistral**
- **Strengths:** European provider, open models, good performance
- **Best for:** Code, general purpose, privacy-conscious deployments

### Local/Self-Hosted

**Ollama**
- **Strengths:** Free, private, no API costs
- **Models:** Llama, Qwen, Mistral, etc.
- **Best for:** SIMPLE tier, development, privacy-sensitive tasks
- **Trade-off:** Slower, requires hardware, limited context

---

## Cost-Quality Trade-offs

Understanding when to spend more (or less) on model quality:

### When Cheaper is Smarter

- **High volume:** Running thousands of similar tasks daily
- **Well-defined:** Task has clear success criteria
- **Low stakes:** Mistakes are easily caught and fixed
- **Redundant:** Multiple checks/retries are acceptable
- **Examples:** Heartbeat monitoring, status checks, log parsing

### When Premium is Worth It

- **Low volume:** One-off or infrequent tasks
- **Ill-defined:** Task requires judgment and interpretation
- **High stakes:** Mistakes have serious consequences
- **One-shot:** No opportunity for retries or refinement
- **Examples:** Security audits, production code, financial analysis

### The Retry Paradox

**Key insight:** Sometimes the "expensive" model is cheaper overall.

**Example calculation:**
- **Cheap model:** $0.0005 per task, 70% success rate → avg $0.00071 per success (with retries)
- **Premium model:** $0.0050 per task, 98% success rate → $0.0051 per success
- **If time has value:** Premium model wins (no retry delays)

**Rule of thumb:** For critical tasks, calculate: `(cost per attempt) / (success rate)` to find true cost.

---

## Benchmarking Your Models

To properly assign tiers, benchmark candidates on representative tasks.

### SIMPLE Tier Benchmark Suite

```
1. Status check: "Parse this JSON and report the status field"
2. Summarization: "Summarize these 5 log entries in one sentence each"
3. Extraction: "Extract all error codes from this output"
4. Comparison: "Is value A greater than value B?"
5. Simple classification: "Is this message urgent, normal, or low priority?"
```

**Passing criteria:** ≥95% accuracy, <3s response time, no overthinking

### MEDIUM Tier Benchmark Suite

```
1. Code fix: "Fix the bug in this 30-line function"
2. Research: "Summarize recent developments in [technical topic]"
3. Analysis: "Identify performance bottlenecks in this code"
4. Documentation: "Write API documentation for this function"
5. Testing: "Generate unit tests for this module"
```

**Passing criteria:** ≥85% quality, good code understanding, reasonable cost

### COMPLEX Tier Benchmark Suite

```
1. Feature build: "Implement a caching layer with Redis"
2. Debugging: "Find and fix this race condition"
3. Architecture: "Design a microservices split for this monolith"
4. Algorithm: "Implement an efficient solution to [problem]"
5. Refactoring: "Refactor this module for better maintainability"
```

**Passing criteria:** Production-quality output, minimal revision needed, handles edge cases

### CRITICAL Tier Benchmark Suite

```
1. Security: "Audit this authentication flow for vulnerabilities"
2. Production: "Review this deployment script for risks"
3. Financial: "Analyze this transaction log for anomalies"
4. Compliance: "Check this code for GDPR compliance issues"
5. Architecture review: "Evaluate this system design for scalability and security"
```

**Passing criteria:** Exceptional thoroughness, identifies subtle issues, provides detailed reasoning

---

## Building Your Model Portfolio

**Ideal portfolio structure:**

1. **One reliable SIMPLE tier model** for high-frequency tasks
   - Optimize for cost and speed
   - Consider local/self-hosted if volume is very high

2. **One or two MEDIUM tier models** for everyday work
   - Balance cost and capability
   - Consider one code-specialized, one general-purpose

3. **One strong COMPLEX tier model** for sophisticated work
   - Current-generation frontier model
   - Excellent code and reasoning capabilities

4. **One CRITICAL tier model** (can be same as COMPLEX)
   - Best available quality
   - Use sparingly, only for high-stakes work

**Budget-conscious portfolio:**
- SIMPLE: Local Ollama model (free)
- MEDIUM: GPT-4o Mini or Gemini Flash ($0.15-$0.30/M)
- COMPLEX: Claude Sonnet or GPT-4o ($3-$5/M)
- CRITICAL: Use COMPLEX tier model, add extended thinking mode

**Performance-focused portfolio:**
- SIMPLE: GPT-4o Mini ($0.15/M)
- MEDIUM: Claude Sonnet ($3/M)
- COMPLEX: Claude Sonnet with thinking ($3-$9/M effective)
- CRITICAL: Claude Opus or GPT o1 ($15-$30/M)

---

## Updating Your Configuration

Model capabilities and pricing change frequently. Review quarterly:

1. **Check for new models** from your providers
2. **Review pricing changes** (often trending downward)
3. **Re-benchmark existing models** against new options
4. **Adjust tier assignments** if model capabilities have improved
5. **Update cost estimates** in your `config.json`

**Resources for updates:**
- Provider pricing pages
- Model release announcements
- Benchmark leaderboards (HumanEval, MMLU, etc.)
- Community discussions and reviews

---

## Summary: Model Selection Checklist

**For each model you're considering:**

- [ ] Identify which tier(s) it fits best
- [ ] Verify current pricing (input/output per million tokens)
- [ ] Check context window size
- [ ] List supported capabilities (vision, function-calling, etc.)
- [ ] Run benchmark tasks for target tier
- [ ] Document any limitations or quirks
- [ ] Add to `config.json` with appropriate metadata
- [ ] Validate with `python scripts/router.py health`

**Remember:** The "best" model configuration depends on your specific workload, budget, and quality requirements. Start conservative, measure results, and adjust based on real-world performance.
