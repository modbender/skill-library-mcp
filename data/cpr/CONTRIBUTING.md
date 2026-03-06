# Contributing to CPR

**Thank you for helping make AI communication better for everyone.**

CPR is a community-driven project. Your feedback, testing, and contributions directly improve the framework for thousands of AI developers and users.

---

## How to Contribute

### 🐛 Report Issues

Found a personality type that doesn't fit? Drift pattern we missed? Documentation that's confusing?

**Use these templates:**

#### Bug Report: Drift Detection Failure
```markdown
**Personality Type:** [Direct/Minimal, Warm/Supportive, Professional, Casual, or Hybrid]

**Drift Pattern Observed:**
[What drift behavior occurred? Quote the AI response.]

**Expected Behavior:**
[What should have happened according to your baseline?]

**Baseline Definition:**
[Link to your baseline config or paste relevant sections]

**Frequency:**
[How often does this occur? Once? Consistently?]

**Model:**
[Claude Opus, GPT-4o, Grok, etc.]
```

#### Feature Request: Missing Pattern/Personality
```markdown
**Use Case:**
[What are you trying to do? Customer support? Technical docs? Creative?]

**Current Limitation:**
[What doesn't work with existing personality types?]

**Proposed Solution:**
[What would solve this? New personality type? Pattern addition? Calibration guide?]

**Why This Matters:**
[Who else would benefit? How common is this use case?]
```

#### Documentation Confusion
```markdown
**Which File:**
[BASELINE_TEMPLATE.md, RESTORATION_FRAMEWORK.md, etc.]

**Which Section:**
[Step number, section name, or line number]

**What's Unclear:**
[Specific question or confusion]

**Suggested Improvement:**
[How could we explain this better?]
```

---

### 🔧 Submit Improvements

**What We Need Most:**

1. **Additional Personality Examples**
   - Real baseline definitions from different use cases
   - Before/after examples showing CPR in action
   - Edge case personalities (hybrid blends, unusual styles)

2. **Model-Specific Calibration Data**
   - Drift thresholds for new models (GPT-5, Claude 5, etc.)
   - Platform quirks (ChatGPT web, Claude.ai, Gemini)
   - Model personality baselines

3. **Cross-Cultural Adaptations**
   - Translation of patterns to other languages
   - Cultural communication norm differences
   - Validation that patterns work internationally

4. **Tooling**
   - Automated baseline validation scripts
   - Drift scoring calculators
   - Message log analyzers

**Contribution Guidelines:**

#### Documentation Standards
- **Examples over theory:** Show before/after, not just concepts
- **Quantify when possible:** "Once per 10 messages" not "sometimes"
- **Test your additions:** Run through validation scenarios
- **Cite sources:** If referencing research, link it

#### Code Standards (If Adding Tooling)
- **Language-agnostic when possible:** Python preferred, but shell/JS acceptable
- **No external dependencies** unless absolutely necessary
- **Include usage examples** in comments
- **Test on multiple models** if model-specific

#### Pull Request Process
1. **Fork the repo** (GitHub/ClawHub)
2. **Create feature branch** (`feature/hybrid-personality-guide` or `fix/validation-step-7`)
3. **Make changes** following standards above
4. **Test thoroughly** (run through scenarios, validate with real AI)
5. **Submit PR** with clear description of what changed and why
6. **Respond to review** within 7 days (or we'll assume abandoned)

**Review Timeline:**
- Minor fixes (typos, clarifications): 1-2 days
- New examples/sections: 3-5 days
- New personality types: 5-7 days (requires validation)
- Major methodology changes: 7-14 days (requires community discussion)

---

### 🧪 Test and Document

**Most valuable contribution:** Use CPR, document what happens, share results.

#### Metrics Template

Before implementing CPR, capture baseline metrics:

```yaml
before_cpr:
  personality_type: [your self-assessment]
  model: [Claude Opus, GPT-4o, etc.]
  use_case: [customer support, technical docs, etc.]
  
  metrics:
    avg_response_length: [X sentences or Y words]
    validation_frequency: [once per N messages]
    user_satisfaction: [subjective 1-10 scale]
    drift_incidents: [times you noticed drift per week]
    
  sample_responses: |
    [Paste 3-5 typical responses before CPR]
```

After implementing CPR (20-30 interactions):

```yaml
after_cpr:
  personality_type: [validated archetype from Step 7]
  
  metrics:
    avg_response_length: [X sentences or Y words]
    validation_frequency: [once per N messages]
    user_satisfaction: [subjective 1-10 scale]
    drift_incidents: [times you noticed drift per week]
    
  sample_responses: |
    [Paste 3-5 typical responses after CPR]
    
  improvements:
    - [What got better?]
    - [What stayed the same?]
    - [What got worse (if anything)?]
    
  surprises:
    - [Anything unexpected?]
```

**Where to share:** Open an issue with title "Case Study: [Your Use Case]" and paste your results. We'll add to CASE_STUDIES.md (with your permission).

---

## Roadmap & Priorities

### ✅ Completed (V2.0)
- Universal drift separation
- 4 personality archetypes + hybrid support
- Baseline validation protocol
- Boundary precision testing
- Test validation across 8+ models
- Open-source documentation

### 🚧 In Progress
- Community case studies (collecting)
- Platform-specific guides (ChatGPT web, Claude.ai)
- Contribution tooling (this file!)

### 📋 Planned (V2.1+)
- **High Priority:**
  - Simplified CPR for consumer platforms (ChatGPT instructions field)
  - Automated baseline validation tool
  - Internationalization framework
  
- **Medium Priority:**
  - Drift scoring calculator
  - Additional personality archetype examples
  - Video walkthrough (5-min setup demo)
  
- **Low Priority (Community-Driven):**
  - Multi-language translations
  - Cross-cultural calibration guides
  - Integration templates for popular platforms

**Want to work on something from the roadmap?** Open an issue titled "RFC: [Feature Name]" and describe your approach. We'll discuss before you invest time building.

---

## Community Standards

### Code of Conduct (Short Version)

1. **Be respectful:** Critique ideas, not people
2. **Be constructive:** "This doesn't work" → "This doesn't work because X, maybe try Y"
3. **Be patient:** Maintainers are human, reviews take time
4. **Be honest:** Report failures, not just successes (failures help us improve)

**Zero tolerance for:** Harassment, discrimination, spam, self-promotion without contribution.

**Full Code of Conduct:** [Link to standard CoC if on GitHub]

### Credit & Attribution

- **Contributors:** All merged PRs get credit in CONTRIBUTORS.md
- **Case studies:** Attributed unless you request anonymity
- **Derived works:** MIT license allows commercial use, just credit CPR and link back

---

## Questions?

- 💬 **Discord:** https://discord.com/invite/clawd (OpenClaw community, #cpr channel)
- 🐦 **Twitter:** https://x.com/TheShadowyRose (DMs open for quick questions)
- 🐛 **Issues:** GitHub/ClawHub issue tracker (for bugs/features)

---

## Thank You

Every contribution — bug report, example, test result, typo fix — makes CPR better for the entire AI community.

**You're not just improving a tool. You're raising the standard for AI communication.**

— The CPR Team  
February 2026
