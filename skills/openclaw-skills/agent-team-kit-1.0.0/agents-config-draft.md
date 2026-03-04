# Agent Config Draft

## Agents to Rebuild

1. **Scout** 🔍
   - Role: Discovery (find opportunities)
   - Model: anthropic/claude-sonnet-4-5

2. **Sage** 🦉
   - Role: Architecture (from opportunities → specs)
   - Model: anthropic/claude-sonnet-4-5

3. **Pixel** 🎨
   - Role: Design (visuals, branding)
   - Model: anthropic/claude-sonnet-4-5

4. **Link** 🔗
   - Role: Build (code, MVP construction)
   - Model: anthropic/claude-sonnet-4-5

5. **Spark** ✨
   - Role: Distribution (content, announcements)
   - Model: anthropic/claude-sonnet-4-5

6. **Echo** 📝
   - Role: Documentation (write docs, guides, blogs)
   - Model: anthropic/claude-sonnet-4-5

7. **Rhythm** 🥁
   - Role: Backlog/Grooming (ops/triage)
   - Model: anthropic/claude-sonnet-4-5

8. **Harmony** 🤝
   - Role: Health/Morale (team vibes, audits)
   - Model: anthropic/claude-sonnet-4-5

---

## Test Plan
- **Testing sequence:** One at a time
- **Verify model**: Sonnet for all agents
- **Ensure work proceeds:** Use `HEARTBEAT.md` loop tasks to validate role functions

---

## Next Steps
- Enable config for seamless spawning.
- Test roles sequentially (start with Scout, validate tools + outputs).
- Document fixes.