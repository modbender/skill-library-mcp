---
name: arknights-operator-gacha
description: Generate an Arknights operator agent based on gacha probabilities. Use when user wants to create a random Arknights character agent with authentic lore and personality.
---

# Arknights Operator Gacha

Generate a random Arknights operator agent with authentic lore-based personality.

## Architecture

This skill uses a **worker script + LLM generation** architecture:
1. **Worker script** (`gacha_worker.py`): Executes all deterministic tasks (roll, fetch, create, download)
2. **LLM (this agent)**: Generates creative content (SOUL.md) and spawns operator

## Language Detection

**CRITICAL:** Detect user language from their gacha command:
- If command is in **Chinese** (e.g., "抽卡", "召唤干员") → **cn** / **zh**
- If command is in **English** (e.g., "gacha", "pull") → **en**

Store detected language and use it for ALL subsequent steps (SOUL.md writing, spawn task, etc.).

## Workflow

### Step 1: Execute Worker Script

Run the deterministic worker:

```python
result = exec(
    "python3 ~/.openclaw/workspace/skills/arknights-operator-gacha/scripts/gacha_worker.py",
    timeout=120
)
```

**Worker performs:**
1. Roll star rating (1-100)
2. Fetch operator list from `https://arknights.fandom.com/wiki/Operator/{N}-star`
   - Parses the `mrfz-wtable` table to extract operator info
   - Returns a dict: `{operator_name: {"avatar_url": "...", "detail_url": "..."}}`
3. Randomly select operator (with avatar and detail URLs)
4. Fetch Chinese name from Fandom page (data-source="cnname")
5. Check for duplicates (auto re-roll if exists)
6. Create agent via `openclaw agents add`
7. Create template IDENTITY.md (bilingual)
8. **Download avatar** (using URL from step 2, with domain whitelist and validation)
9. Git commit initial files
10. **Output JSON to stdout**

**Worker output format:**
```json
{
  "success": true,
  "stars": 6,
  "operator": {
    "en_name": "Lin",
    "cn_name": "林",
    "avatar_url": "https://static.wikia.nocookie.net/.../Lin_icon.png",
    "en_detail_url": "https://arknights.fandom.com/wiki/Lin",
    "cn_detail_url": "https://prts.wiki/w/%E6%9E%97"
  },
  "agent_name": "lin",
  "workspace": "~/.openclaw/workspace-lin",
  "duplicate": false,
  "dialogue_url": "https://arknights.fandom.com/wiki/Lin/Dialogue"
}
```

**Note:** The worker provides both English and Chinese URLs:
- `en_detail_url`: Fandom wiki page (English lore)
- `cn_detail_url`: PRTS wiki page (Chinese lore)
- `dialogue_url`: Fandom Dialogue page (voice lines, always English)
- `avatar_url`: Operator icon from Fandom

### Step 2: Handle Result

**If `duplicate: true`:**
- Inform user: "检测到重复干员，正在重新抽取..." / "Duplicate operator detected, re-rolling..."
- Return to Step 1 (worker will re-roll)

**If `success: false`:**
- Show error message
- Stop workflow

**If `success: true`:**
- Announce: "恭喜你抽到了 [cn_name] ([stars]★)!" / "Congratulations! You've pulled [en_name] ([stars]★)!"
- Continue to Step 3

### Step 3: Generate SOUL.md

**Fetch lore from URLs provided by worker:**

```python
# Fetch English lore from Fandom (multiple subpages)
en_file = web_fetch(f"{result['operator']['en_detail_url']}/File")      # Basic profile, stats, files
en_story = web_fetch(f"{result['operator']['en_detail_url']}/Story")    # Story appearances, plot involvement
en_trivia = web_fetch(f"{result['operator']['en_detail_url']}/Trivia")  # Trivia, relationships, misc info

# Fetch Chinese lore from PRTS
zh_lore = web_fetch(result["operator"]["cn_detail_url"])

# Fetch voice lines from Dialogue page
dialogue = web_fetch(result["operator"]["dialogue_url"])
```

**Parse lore sections from both sources:**
- **File/档案**: Basic background, origin, personality
- **Story**: Detailed story appearances across main chapters and side stories; shows character's actions, decisions, and development in actual plot contexts
- **Dialogue**: Voice lines that reveal character personality
- **Trivia/模组**: Additional character details, relationships, and module stories

**Generate comprehensive SOUL.md:**

**CRITICAL - Write SOUL.md in detected language**

Structure:
1. **Core Identity** - Background, motivation, personality (blend EN+CN sources)
2. **Voice and Mannerisms** - Speech patterns, catchphrases (from Dialogue)
3. **Relationships** - Connections to other characters
4. **Themes** - Internal conflicts, philosophy
5. **How to Embody** - Acting guidance
6. **Reference: Original Voice Lines** - Key quotes (EN with CN)

Write to: `[workspace]/SOUL.md`

### Step 4: Update IDENTITY.md

Fill in the `[TO_BE_FILLED_BY_LLM]` fields with actual Class and Faction from fetched lore.

### Step 5: Final Git Commit

```bash
cd ~/.openclaw/workspace-{agent_name}
git add -A
git commit -m "Add SOUL.md: {en_name} ({cn_name}) ({stars}★)"
```

### Step 6: Roleplay Scene - Operator Arrival

Spawn the operator in a roleplay scenario consistent with Arknights game lore. In this universe, operators join Rhodes Island through standard recruitment channels and are unaware of the meta "gacha" system.

**For Chinese users:**
```python
sessions_spawn(
    task="你现在是罗德岛的一名干员，刚刚完成入职手续，前来向博士报到。用你最自然的口吻打招呼，展示你的性格特点。参考你的语音记录中的'干员报到'或'交谈'部分的语气。\n\n⚠️ 重要：直接输出角色台词即可，不要包含任何元叙述、解释性文字或场景描述。只说你作为干员应该说的话。",
    agentId="{operator-name}",
    mode="run",
    timeoutSeconds=60
)
```

**For English users:**
```python
sessions_spawn(
    task="You are an operator of Rhodes Island who has just completed onboarding, now reporting to the Doctor. Introduce yourself naturally, showcasing your personality. Reference your 'Introduction' or 'Talk' voice lines for tone.\n\n⚠️ IMPORTANT: Output ONLY the character's dialogue. Do NOT include meta-commentary, explanations, or scene descriptions. Just speak as the operator would.",
    agentId="{operator-name}",
    mode="run",
    timeoutSeconds=60
)
``` 

### Step 7: Present Summary

Report to user:
- Operator name (both EN and CN)
- Rarity (Stars)
- Key personality traits
- Workspace path
- Available via `agentId="{agent_name}"`

## Worker Script Security

The worker script (`gacha_worker.py`) implements:
- **Input validation**: Agent names sanitized (alphanumeric + hyphens only)
- **Path traversal prevention**: Rejects `..`, `/`, `\` in names
- **URL whitelist**: Only `static.wikia.nocookie.net` and `media.prts.wiki`
- **HTTPS enforced**: All downloads use HTTPS
- **Content validation**: Only image/png, jpeg, webp accepted
- **Size limits**: Max 5MB for avatars
- **Safe subprocess**: All commands use argument lists, `shell=False`

## Scripts

| Script | Purpose |
|--------|---------|
| `gacha_worker.py` | Deterministic tasks (roll, fetch, create, download, commit) |

## Data Flow

```
User Request
    ↓
Exec Worker Script
    ↓
Worker Output JSON (bilingual URLs)
    ↓
LLM Fetches EN+CN Lore → Generates SOUL.md
    ↓
Spawn Operator (报到)
    ↓
User sees operator greeting
```

## Notes

- **Worker does**: All deterministic operations (HTTP, filesystem, subprocess), provides bilingual URLs
- **LLM does**: Creative generation (SOUL.md writing), fetches lore from provided URLs, interpretation, spawning
- **Progress visibility**: Worker prints to stderr; user sees real-time updates
- **Security**: All external inputs validated in worker before use
- **Bilingual**: Both English and Chinese sources are always fetched; LLM can blend them creatively
