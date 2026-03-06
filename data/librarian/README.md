# Librarian Skill

**OpenClaw conversational interface for semantic book search**

This is a **companion skill** for [Librarian](https://github.com/nonlinear/librarian) — it adds natural language query support to your local book library.

---

## Requirements

**You must install Librarian first:**

1. **Clone Librarian**: [https://github.com/nonlinear/librarian](https://github.com/nonlinear/librarian)
2. **Follow setup**: Index your books, configure engine
3. **Then activate this skill** in OpenClaw

---

## Installation

**Option 1: Automatic (OpenClaw)**
```bash
clawdhub install librarian
```

**Option 2: Manual (symlink)**
```bash
ln -s ~/Documents/librarian/skill ~/.openclaw/skills/librarian
```

**Verify:**
```bash
ls -la ~/.openclaw/skills/librarian
# Should point to ~/Documents/librarian/skill
```

---

## Usage

**Trigger patterns:**
- "pesquisa por X"
- "research for X"
- "can you check it against (topic/book)"
- "pergunta ao I Ching sobre Y"
- "what does Graeber say about debt?"

**Examples:**

```
User: "What does chaos magick say about sigils?"
Kin: [loads metadata → infers topic → searches → formats response with citations]

User: "Procura no Graeber sobre debt"
Kin: [searches Debt book → returns excerpts with page numbers]
```

**How it works:**
1. AI detects trigger pattern
2. Loads metadata (`.library-index.json`)
3. Infers scope (topic or book)
4. Calls wrapper → research.py
5. Formats results with citations

**See [SKILL.md](SKILL.md) for full protocol documentation.**

---

## What This Skill Does

- **Conversational layer** for librarian engine
- **Trigger detection** (natural language → search)
- **Scope inference** (which book/topic to search)
- **Hard stops** (honest failures > invented answers)
- **Citation formatting** (emoji markers, sources)

**What it does NOT do:**
- Indexing (done by librarian engine)
- Search logic (done by research.py)
- Book storage (done by librarian/books/)

**This skill = protocol wrapper. Engine = heavy lifting.**

---

## Links

- **Librarian project**: [https://github.com/nonlinear/librarian](https://github.com/nonlinear/librarian)
- **OpenClaw**: [https://openclaw.ai](https://openclaw.ai)
- **Skill marketplace**: [https://clawhub.com](https://clawhub.com)

---

## Version

**v0.15.0** - Skill as Protocol (2026-02-21)

**Status:** Companion skill (requires librarian parent)

**Future:** v0.21.0 will generalize (standalone skill with embedded indexing)
