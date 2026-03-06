# References

## Anthropic's Complete Guide to Building Skills for Claude (January 2026)

The foundational reference for this skill's design principles, progressive disclosure patterns, quality scoring rubric, and testing methodology.

**Source:** https://claude.com/blog/complete-guide-to-building-skills-for-claude  
**PDF:** https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf?hsLang=en

This guide covers:
- Skill architecture (frontmatter, SKILL.md body, linked files)
- Progressive disclosure for token efficiency
- Composability and portability principles
- Testing with self-play and evaluation
- Use case categories and trigger design
- Security considerations for skill content

All core design principles in this skill's SKILL.md are derived from or inspired by this guide.

## Multi-Agent Architecture Pattern

The Designer/Reviewer/Tester pattern used in this skill is original design inspired by software engineering peer review and QA practices. Key principle: **builders don't evaluate their own work**. This pattern enforces separation of concerns where:
- Designer: creative work (artifact generation)
- Reviewer: critical evaluation (quality scoring, gap analysis)
- Tester: empirical validation (self-play, trigger testing)

This architecture is not derived from academic literature but from established software engineering practices around code review, QA testing, and separation of duties.
