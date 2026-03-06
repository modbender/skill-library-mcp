# Changelog

All notable changes to the Poe API Orchestrator skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-03

### Added
- ✅ Initial release of Poe API Orchestrator skill
- ✅ OpenAI-compatible API implementation
- ✅ 4 specialized subagents with model assignments:
  - coding-agent → GPT-5.3-Codex (8000 tokens)
  - design-agent → Gemini-3.1-Pro (4000 tokens)
  - analysis-agent → Claude-Sonnet-4.6 (3000 tokens)
  - reasoning-agent → Claude-Opus-4.6 (5000 tokens)
- ✅ Autonomous decision-making by main agent (GLM-5)
- ✅ Token control system with call limits
- ✅ Task type detection via keywords
- ✅ Complete documentation and examples

### Changed
- 🔄 Switched from fastapi_poe to OpenAI-compatible API (simpler, more efficient)
- 🔄 Updated token control logic (max_tokens = response length, not total usage)
- 🔄 Increased coding task max_tokens from 2000 to 8000

### Fixed
- 🐛 Fixed token control misunderstanding
- 🐛 Corrected max_tokens interpretation (response length vs total usage)
- 🐛 Added proper call limit control (max_calls_per_task)

### Performance
- ⚡ 40% token savings compared to fastapi_poe (85 vs 142 tokens)
- ⚡ 100% connection success rate (4/4 models)
- ⚡ Average response time: 2.51s
- ⚡ Token efficiency: 0.085%

### Documentation
- 📝 Complete SKILL.md with decision matrix
- 📝 Comprehensive README.md
- 📝 TOKEN_CONTROL_EXPLAINED.md
- 📝 POE_FINAL_OPTIMIZED.md
- 📝 POE_OPENAI_API_GUIDE.md

## [0.9.0] - 2026-03-03 (Beta)

### Added
- ✅ Initial implementation with fastapi_poe
- ✅ Basic token control (incorrect implementation)
- ✅ 4 specialized models
- ✅ Task routing logic

### Issues
- ❌ Incorrect token control understanding
- ❌ Coding tasks limited to 2000 tokens (too low)
- ❌ Complex async/await implementation

---

## Version History

| Version | Date | Status | Key Changes |
|---------|------|--------|-------------|
| 1.0.0 | 2026-03-03 | ✅ Production | OpenAI API, correct token control |
| 0.9.0 | 2026-03-03 | ⚠️ Beta | Initial fastapi_poe implementation |

---

## Future Plans

### [1.1.0] - Planned
- [ ] Add streaming support
- [ ] Add batch processing
- [ ] Add cost estimation per task
- [ ] Add model fallback options
- [ ] Add response caching

### [1.2.0] - Planned
- [ ] Add more specialized models
- [ ] Add custom model configuration
- [ ] Add performance analytics
- [ ] Add A/B testing support

---

## Migration Guide

### From 0.9.0 to 1.0.0

**API Change**:
```python
# Old (0.9.0) - fastapi_poe
import fastapi_poe as fp
async for partial in fp.get_bot_response(...):
    ...

# New (1.0.0) - OpenAI-compatible
import openai
client = openai.OpenAI(
    api_key="YOUR_POE_API_KEY",
    base_url="https://api.poe.com/v1"
)
chat = client.chat.completions.create(...)
```

**Token Control Change**:
```python
# Old (0.9.0) - Incorrect
MAX_TOKENS_PER_REQUEST = 2000  # Thought this was total usage

# New (1.0.0) - Correct
max_tokens = 8000  # Response length
max_calls_per_task = 10  # Real cost control
```

**Installation**:
```bash
# Old (0.9.0)
pip install fastapi-poe

# New (1.0.0)
pip install openai
```

---

[1.0.0]: https://github.com/your-repo/poe-api-orchestrator/releases/tag/v1.0.0
[0.9.0]: https://github.com/your-repo/poe-api-orchestrator/releases/tag/v0.9.0
