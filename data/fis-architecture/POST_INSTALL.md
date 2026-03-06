# Post-Installation Setup

> **FIS 3.2 is ready to use immediately — no complex setup required!**

---

## What's Different in 3.2?

**FIS 3.2 requires no initialization.**

Unlike FIS 3.1 which needed:
- ❌ Initialization scripts
- ❌ Registry files
- ❌ Python path setup
- ❌ Complex directory structures

FIS 3.2 only needs:
- ✅ Ticket files (create as needed)
- ✅ Knowledge files (drop into `knowledge/`)

---

## Quick Verification

Check if your shared hub exists:

```bash
ls ~/.openclaw/fis-hub/tickets/
# Should show: active/  completed/
```

If not, create the minimal structure:

```bash
mkdir -p ~/.openclaw/fis-hub/{tickets/active,tickets/completed,knowledge,results,.fis3.1}
echo '{}' > ~/.openclaw/fis-hub/.fis3.1/notifications.json
```

---

## Your First Ticket

```bash
# Create a task ticket
cat > ~/.openclaw/fis-hub/tickets/active/TASK_FIRST.json << 'EOF'
{
  "ticket_id": "TASK_FIRST",
  "agent_id": "worker-001",
  "parent": "cybermao",
  "role": "worker",
  "task": "My first FIS task",
  "status": "active",
  "created_at": "2026-02-19T21:00:00",
  "timeout_minutes": 60
}
EOF

# View it
cat ~/.openclaw/fis-hub/tickets/active/TASK_FIRST.json

# Complete and archive
mv ~/.openclaw/fis-hub/tickets/active/TASK_FIRST.json \
   ~/.openclaw/fis-hub/tickets/completed/
```

✅ **That's it!** No Python imports, no registries, no setup.

---

## Optional: Generate Badge

For visual identity:

```bash
cd ~/.openclaw/workspace/skills/fis-architecture/lib
python3 badge_generator_v7.py
# Follow prompts
```

---

## What About Content/Knowledge?

Use **QMD** — it's already integrated with OpenClaw:

```bash
# Search for knowledge
mcporter call 'exa.web_search_exa(query: "your topic", numResults: 5)'

# Or add knowledge
echo "# My Knowledge" > ~/.openclaw/fis-hub/knowledge/my-notes.md
# QMD will index it automatically
```

---

## No Configuration Needed

| Feature | FIS 3.1 | FIS 3.2 |
|---------|---------|---------|
| Setup | `python3 init_fis31.py` | None |
| Registry files | Required | Not needed |
| Python imports | Required | Optional |
| Skill discovery | Custom registry | QMD |
| Memory queries | Custom manager | QMD |

---

## Next Steps

- Read [AGENT_GUIDE.md](./AGENT_GUIDE.md) — When to use SubAgents
- Read [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) — Command cheat sheet
- Create your first real ticket

---

*FIS 3.2.0-lite — Ready when you are 🐱⚡*
