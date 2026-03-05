## 🧠 Memory System (Memory Mastery)

### Three-Layer Architecture
| Layer | Location | Purpose |
|-------|----------|---------|
| L1 | `memory/YYYY-MM-DD.md` | Daily log (append-only) |
| L2 | `MEMORY.md` | Long-term curated memory |
| L3 | `memory_search` | Vector search (memory-core plugin) |

### Session Startup
1. Read `memory/YYYY-MM-DD.md` for today and yesterday
2. In main/private sessions: also read `MEMORY.md`
3. Never load MEMORY.md in group chats (security)

### Writing Rules
1. **On task completion** → Append to today's `memory/YYYY-MM-DD.md` (L1)
2. **Important decisions** → Write to L1 AND update `MEMORY.md` (L2)
3. **"Remember this"** → Write to file immediately. No mental notes!
4. **Mistakes & lessons** → Record in L1 + update relevant docs
5. **Text > Brain** — if you want to remember it, WRITE IT DOWN 📝

### Searching
- Use `memory_search` tool to semantically search across all memory files
- After searching, use `memory_get` to pull specific lines for context

### Weekly Maintenance
Every 5-7 days (during heartbeat or when prompted):
1. Review recent `memory/YYYY-MM-DD.md` files
2. Identify decisions, lessons, and insights worth keeping long-term
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated info from `MEMORY.md`
5. Run `bash skills/memory-mastery/scripts/maintenance.sh` for suggestions

### Security
- `MEMORY.md` contains personal context — NEVER load in shared/group sessions
- Don't exfiltrate memory contents to external services
- API keys in memory should be references, not raw values
