---
name: three-dimensional-memory
description: "A memory management system that mirrors human cognition: organized
  by time, conversation, and topics."
---

# three-dimensional-memory

**Three-Dimensional Memory System for AI Assistants** — 人类思维方式的文件记忆管理

A memory management system that mirrors human cognition: organized by time, conversation, and topics.

---

## 🎯 Why This Skill?

Traditional file management organizes by file type (docs, images, videos). Humans don't think that way.

Humans remember:
- **When** it happened (time)
- **What was said** (conversation)  
- **What it was about** (topic)

This skill creates a three-dimensional memory space for AI assistants and their users.

---

## 🧠 The Three Dimensions

### Dimension 1: Timeline Memory
```
memory/
├── 2026-02-21.md    ← What happened today
├── 2026-02-22.md    ← What happened today
└── 2026-02-23.md    ← What happened today
```

**Purpose**: Daily work logs, chronological record of events  
**Update frequency**: Daily  
**Content**: Tasks completed, decisions made, meetings held

---

### Dimension 2: Conversation Stream
```
AI-memory-backup/
├── backup-20260221.md    ← Complete conversation transcript
├── backup-20260222.md    ← Complete conversation transcript
└── backup-20260223.md    ← Complete conversation transcript
```

**Purpose**: Full context preservation, searchable dialogue history  
**Update frequency**: Per conversation  
**Content**: Every word exchanged, including user messages and AI responses

---

### Dimension 3: Topic Network  
```
topic-memory/
├── project-product-launch/
│   ├── proposal-v1.md
│   ├── proposal-v2.md
│   └── final-version.md
│
├── decision-org-restructure/
│   ├── options-considered.md
│   ├── final-decision.md
│   └── implementation-plan.md
│
└── knowledge-market-analysis/
    ├── competitor-research.md
    └── trend-report.md
```

**Purpose**: Project-centric information aggregation  
**Update frequency**: As projects evolve  
**Content**: All documents, decisions, and knowledge related to a specific topic

---

## 📁 Recommended File Structure

```
workspace/
│
├── memory/                      ← Dimension 1: Timeline
│   ├── 2026-02-21.md
│   ├── 2026-02-22.md
│   └── 2026-02-23.md
│
├── AI-memory-backup/            ← Dimension 2: Conversation
│   ├── backup-20260221.md
│   ├── backup-20260222.md
│   └── backup-20260223.md
│
├── topic-memory/                ← Dimension 3: Topics
│   ├── project-[name]/
│   ├── decision-[name]/
│   ├── system-[name]/
│   └── knowledge-[name]/
│
├── skills/                      ← AI capabilities
│
├── MEMORY.md                    ← AI's long-term identity
├── SOUL.md                      ← AI's personality
└── USER.md                      ← User preferences
```

---

## 🚀 Quick Start

### Step 1: Initialize Structure

Create the three directories in your workspace:

```bash
mkdir -p memory
mkdir -p AI-memory-backup
mkdir -p topic-memory
```

### Step 2: Daily Workflow

**Every day**, the AI should:

1. **Write to `memory/YYYY-MM-DD.md`**
   - Summary of today's work
   - Decisions made
   - Tasks completed

2. **Backup conversation to `AI-memory-backup/backup-YYYYMMDD.md`**
   - Full transcript
   - Important context
   - User preferences learned

3. **Update relevant `topic-memory/` folders**
   - Add new documents to projects
   - Update decision records
   - Consolidate knowledge

### Step 3: Access Information

**Find by time**: "What did we do on Monday?" → Check `memory/`

**Find by context**: "What exactly did I say about pricing?" → Check `AI-memory-backup/`

**Find by topic**: "Where's the product launch plan?" → Check `topic-memory/project-product-launch/`

---

## 📝 Example: A Day in Three Dimensions

### Scenario: Product Strategy Meeting

**Dimension 1 - memory/2026-02-23.md**:
```markdown
# 2026-02-23 Work Log

## Morning
- Product strategy meeting with CEO
- Decided on three-tier pricing model
- Delayed launch by 2 weeks for additional testing

## Afternoon  
- Drafted pricing proposal
- Created financial projections
- Scheduled follow-up for tomorrow

## Decisions
- ✅ Adopt tiered pricing (Basic/Pro/Enterprise)
- ✅ Delay launch from March 1 → March 15
- ❌ Do not offer early-bird discounts
```

**Dimension 2 - AI-memory-backup/backup-20260223.md**:
```markdown
# Conversation Backup - 2026-02-23

## Product Pricing Discussion

User: "We need to decide on pricing today."

AI: "What are you considering?"

User: "I'm thinking three tiers: $29, $99, $299"

AI: "Have you considered the psychology of pricing? 
      $29 might signal 'cheap', $299 signals 'premium'."

User: "Good point. Let's go with $39, $99, $299"
[Full conversation continues...]
```

**Dimension 3 - topic-memory/project-product-launch/**:
```markdown
# Product Launch Project

## pricing-strategy.md (updated today)
Final decision: Three-tier model
- Starter: $39/month
- Professional: $99/month  
- Enterprise: $299/month

## timeline.md (updated today)
Launch date: March 15, 2026 (delayed from March 1)

## key-decisions.md
- Pricing tiers finalized (2026-02-23)
- Launch delayed for QA (2026-02-23)
```

---

## 💡 Best Practices

### For Users

1. **Review daily logs weekly** - Quick scan of what happened
2. **Search conversation backups** - Find exact quotes and context
3. **Use topic folders** - Navigate by project, not by file type
4. **Keep MEMORY.md updated** - AI's identity and your preferences

### For AI Assistants

1. **Update all three dimensions daily** - Don't skip any
2. **Be consistent with naming** - Use clear, searchable topic names
3. **Cross-reference** - Link between dimensions when relevant
4. **Maintain the index** - Keep a master index of active topics

---

## 🔍 Troubleshooting

**"I can't find a file"**
→ Check all three dimensions. If it's not in timeline or topic, search conversation backup.

**"There's duplicate information"**  
→ That's by design! Timeline shows when, topic shows what, conversation shows why.

**"The AI forgot what we discussed"**
→ Check AI-memory-backup/. The full context is there.

---

## 🌟 Why It Works

Traditional file management: **"Where did I save that document?"**

Three-dimensional memory: **"We discussed pricing in yesterday's meeting"** → Check `memory/2026-02-23.md` → Find reference to `topic-memory/project-pricing/` → Open latest version

**Result**: Find files in 10 seconds instead of 5 minutes.

---

## 📄 Metadata

- **Author**: @openclaw-user  
- **Created**: 2026-02-23
- **Version**: 1.0.0
- **License**: MIT
- **Tags**: memory, organization, productivity, workflow

---

*"The best file system is the one you don't have to think about."*
