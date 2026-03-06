# Changelog

All notable changes to the Psychology Master skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-20

### 🎉 Initial Release

The world's most comprehensive psychology skill for AI agents, featuring 20 reference modules and 3 assessment scripts.

### Added

#### Core References (8 modules)
- `learning-development.md` - Age-specific learning psychology (3-65+)
- `skill-acquisition.md` - Language, coding, math, music acquisition frameworks
- `cognitive-systems.md` - Memory, attention, decision-making, executive function
- `motivation-frameworks.md` - SDT, goals, habits, behavior change
- `marketing-psychology.md` - JTBD, behavioral economics, ethical persuasion
- `conversion-optimization.md` - Funnel psychology, pricing, CTAs
- `customer-psychology.md` - Decision journey, emotions, loyalty
- `safety-ethics.md` - Guardrails, dark patterns, vulnerable populations

#### Extended References (12 modules)
- `social-psychology.md` - Group dynamics, conformity, social influence
- `personality-psychology.md` - Big Five, MBTI, persona design
- `ux-psychology.md` - Gestalt principles, cognitive load, interaction design
- `emotional-intelligence.md` - EQ framework, empathy, emotional triggers
- `neuropsychology-basics.md` - Brain systems, neuroplasticity, neurotransmitters
- `communication-psychology.md` - Active listening, verbal/nonverbal, feedback
- `negotiation-psychology.md` - BATNA, principled negotiation, tactics
- `color-psychology.md` - Color meanings, cultural variations, branding
- `sleep-circadian.md` - Sleep stages, chronotypes, learning timing
- `creativity-psychology.md` - Divergent thinking, ideation techniques
- `stress-resilience.md` - Coping, burnout prevention, recovery
- `organizational-psychology.md` - Teams, leadership, culture, change

#### Assessment Scripts
- `learner_assessment.py` - Generate personalized learning plans by age/skill/context
- `conversion_audit.py` - Audit conversion funnels with psychology insights
- `bias_detector.py` - Detect manipulation patterns in marketing copy

#### Documentation
- `SKILL.md` - Main skill entry point with triggers, workflows, templates
- `README.md` - Comprehensive GitHub documentation
- `CHANGELOG.md` - This file

### Technical Details
- All scripts use standard Python 3 library (no external dependencies)
- Scripts follow Result dataclass pattern for structured output
- JSON output option available for all scripts
- Exit codes: 0=success, 1=error, 10=validation failure

---

## [Unreleased]

### Planned Features
- [ ] Personality profiler script
- [ ] Team diagnostic script
- [ ] Cultural psychology module (non-Western perspectives)
- [ ] Industry-specific modules (healthcare, finance, education)
- [ ] Interactive assessment web interface
- [ ] Multi-language support

### Under Consideration
- Integration with popular LLM frameworks
- API wrapper for remote access
- Visual diagram generators for psychological models
- Case study library with real-world examples

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2026-01-20 | Initial release with 20 references, 3 scripts |

---

## Contributing

See [README.md](README.md#-contributing) for contribution guidelines.

When contributing, please:
1. Update this CHANGELOG with your changes
2. Follow the existing format
3. Add your changes under `[Unreleased]` section
4. Include the type of change (Added, Changed, Deprecated, Removed, Fixed, Security)

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Vulnerability fixes
