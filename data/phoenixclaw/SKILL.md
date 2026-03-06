---
name: phoenixclaw
description: |
  Passive journaling skill that scans daily conversations via cron to generate
  markdown journals using semantic understanding.

  Use when:
  - User requests journaling ("Show me my journal", "What did I do today?")
  - User asks for pattern analysis ("Analyze my patterns", "How am I doing?")
  - User requests summaries ("Generate weekly/monthly summary")
metadata:
  version: 0.0.15
---

# PhoenixClaw: Zero-Tag Passive Journaling

PhoenixClaw automatically distills daily conversations into meaningful reflections using semantic intelligence.

Automatically identifies journal-worthy moments, patterns, and growth opportunities.

## 🛠️ Core Workflow

> [!critical] **MANDATORY: Complete Workflow Execution**
> This 9-step workflow MUST be executed in full regardless of invocation method:
> - **Cron execution** (10 PM nightly)
> - **Manual invocation** ("Show me my journal", "Generate today's journal", etc.)
> - **Regeneration requests** ("Regenerate my journal", "Update today's entry")
> 
> **Never skip steps.** Partial execution causes:
> - Missing images (session logs not scanned)
> - Missing finance data (Ledger plugin not triggered)
> - Incomplete journals (plugins not executed)

PhoenixClaw follows a structured pipeline to ensure consistency and depth:

1. **User Configuration:** Check for `~/.phoenixclaw/config.yaml`. If missing, initiate the onboarding flow defined in `references/user-config.md`.
2. **Context Retrieval:** 
   - **Scan memory files (NEW):** Read `memory/YYYY-MM-DD.md` and `memory/YYYY-MM-DD-*.md` files for manually recorded daily reflections. These files contain personal thoughts, emotions, and context that users explicitly ask the AI to remember via commands like "记一下" (remember this). **CRITICAL**: Do not skip these files - they contain explicit user reflections that session logs may miss.
   - **Scan session logs:** Call `memory_get` for the current day's memory, then **CRITICAL: Scan ALL raw session logs and filter by message timestamp**. Session files are often split across multiple files. Do NOT classify images by session file `mtime`:
      ```bash
      # Read all session logs from ALL known OpenClaw locations, then filter by per-message timestamp
      # Use timezone-aware epoch range to avoid UTC/local-day mismatches.
      TARGET_DAY="$(date +%Y-%m-%d)"
      TARGET_TZ="${TARGET_TZ:-Asia/Shanghai}"
      read START_EPOCH END_EPOCH < <(
        python3 - <<'PY' "$TARGET_DAY" "$TARGET_TZ"
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys

day, tz = sys.argv[1], sys.argv[2]
start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=ZoneInfo(tz))
end = start + timedelta(days=1)
print(int(start.timestamp()), int(end.timestamp()))
PY
      )

      for dir in "$HOME/.openclaw/sessions" \
                 "$HOME/.openclaw/agents" \
                 "$HOME/.openclaw/cron/runs" \
                 "$HOME/.agent/sessions"; do
        [ -d "$dir" ] || continue
        find "$dir" -name "*.jsonl" -print0
      done |
        xargs -0 jq -cr --argjson start "$START_EPOCH" --argjson end "$END_EPOCH" '
          (.timestamp // .created_at // empty) as $ts
          | ($ts | fromdateiso8601?) as $epoch
          | select($epoch != null and $epoch >= $start and $epoch < $end)
        '
      ```
      Read **all matching files** regardless of their numeric naming (e.g., file_22, file_23 may be earlier in name but still contain today's messages).
    - **EXTRACT IMAGES FROM SESSION LOGS**: Session logs contain `type: "image"` entries with file paths. You MUST:
      1. Find all image entries (e.g., `"type":"image"`)
      2. Keep only entries where message `timestamp` is in the target date range
      3. Extract the `file_path` or `url` fields
      4. Copy files into `assets/YYYY-MM-DD/`
      5. Rename with descriptive names when possible
    - **Why session logs are mandatory**: `memory_get` returns **text only**. Image metadata, photo references, and media attachments are **only available in session logs**. Skipping session logs = missing all photos.
    - **Activity signal quality**: Do not treat heartbeat/cron system noise as user activity. Extract user/assistant conversational content and media events first, then classify moments.
    - **FILTER HEARTBEAT MESSAGES (CRITICAL)**: Session logs contain system heartbeat messages that MUST be excluded from journaling. When scanning messages, SKIP any message matching these criteria:
      1. **User heartbeat prompts**: Messages containing "Read HEARTBEAT.md" AND "reply HEARTBEAT_OK"
      2. **Assistant heartbeat responses**: Messages containing ONLY "HEARTBEAT_OK" (with optional leading/trailing whitespace)
      3. **Cron system messages**: Messages with role "system" or "cron" containing job execution summaries (e.g., "Cron job completed", "A cron job")
      
      Example jq filter to exclude heartbeats:
      ```jq
      # Exclude heartbeat messages
      | select(
          (.message.content? | type == "array" and 
            (.message.content | map(.text?) | join("") | 
              test("Read HEARTBEAT\.md"; "i") | not))
          and
          (.message.content? | type == "array" and 
            (.message.content | map(.text?) | join("") | 
              test("^\\s*HEARTBEAT_OK\\s*$"; "i") | not))
        )
      ```
    - **Edge case - Midnight boundary**: For late-night activity that spans midnight, expand the **timestamp** range to include spillover windows (for example, previous day 23:00-24:00) and still filter per-message by `timestamp`.
   - **Merge sources:** Combine content from both memory files and session logs. Memory files capture explicit user reflections; session logs capture conversational flow and media. Use both to build complete context.
   - **Fallback:** If memory is sparse, reconstruct context from session logs, then update memory so future runs use the enriched memory. Incorporate historical context via `memory_search` (skip if embeddings unavailable)

3. **Moment Identification:** Identify "journal-worthy" content: critical decisions, emotional shifts, milestones, or shared media. See `references/media-handling.md` for photo processing. This step generates the `moments` data structure that plugins depend on.
   **Image Processing (CRITICAL)**:
   - For each extracted image, generate descriptive alt-text via Vision Analysis
   - Categorize images (food, selfie, screenshot, document, etc.)
   
   **Filter Finance Screenshots (NEW)**:
   Payment screenshots (WeChat Pay, Alipay, etc.) should NOT be included in the journal narrative. These are tool images, not life moments.
   
   Detection criteria (check any):
   1. **OCR keywords**: "支付成功", "支付完成", "微信支付", "支付宝", "订单号", "交易单号", "¥" + amount
   2. **Context clues**: Image sent with nearby text containing "记账", "支付", "付款", "转账"
   3. **Visual patterns**: Standard payment app UI layouts (green WeChat, blue Alipay)
   
   Handling rules:
   - Mark as `finance_screenshot` type
   - Route to Ledger plugin (if enabled) for transaction recording
   - **EXCLUDE from journal main narrative** unless explicitly described as part of a life moment (e.g., "今天请朋友吃饭" with payment screenshot)
   - Never include raw payment screenshots in daily journal images section
   
   - Match images to moments (e.g., breakfast photo → breakfast moment)
   - Store image metadata with moments for journal embedding
4. **Pattern Recognition:** Detect recurring themes, mood fluctuations, and energy levels. Map these to growth opportunities using `references/skill-recommendations.md`.

5. **Plugin Execution:** Execute all registered plugins at their declared hook points. See `references/plugin-protocol.md` for the complete plugin lifecycle:
   - `pre-analysis` → before conversation analysis
   - `post-moment-analysis` → **Ledger and other primary plugins execute here**
   - `post-pattern-analysis` → after patterns detected
   - `journal-generation` → plugins inject custom sections
   - `post-journal` → after journal complete


6. **Journal Generation:** Synthesize the day's events into a beautiful Markdown file using `assets/daily-template.md`. Follow the visual guidelines in `references/visual-design.md`. **Include all plugin-generated sections** at their declared `section_order` positions.
   - **Embed curated images only**, not every image. Prioritize highlights and moments.
   - **Route finance screenshots to Ledger** sections (receipts, invoices, transaction proofs).
   - Use Obsidian format from `references/media-handling.md` with descriptive captions.
   - **Generate image links from filesystem truth**: compute the image path relative to the current journal file directory. Never output absolute paths.
   - **Do not hardcode path depth** (`../` or `../../`): calculate dynamically from `daily_file_path` and `image_path`.
   - **Use copied filename as source of truth**: if asset file is `image_124917_2.jpg`, the link must reference that exact filename.

7. **Timeline Integration:** If significant events occurred, append them to the master index in `timeline.md` using the format from `assets/timeline-template.md` and `references/obsidian-format.md`.

8. **Growth Mapping:** Update `growth-map.md` (based on `assets/growth-map-template.md`) if new behavioral patterns or skill interests are detected.

9. **Profile Evolution:** Update the long-term user profile (`profile.md`) to reflect the latest observations on values, goals, and personality traits. See `references/profile-evolution.md` and `assets/profile-template.md`.

## ⏰ Cron & Passive Operation
PhoenixClaw is designed to run without user intervention. It utilizes OpenClaw's built-in cron system to trigger its analysis daily at 10:00 PM local time (0 22 * * *).
- Setup details can be found in `references/cron-setup.md`.
- **Mode:** Primarily Passive. The AI proactively summarizes the day's activities without being asked.

### Rolling Journal Window (NEW)
To solve the 22:00-24:00 content loss issue, PhoenixClaw now supports a **rolling journal window** mechanism:

**Problem**: Fixed 24-hour window (00:00-22:00) misses content between 22:00-24:00 when journal is generated at 22:00.

**Solution**: `scripts/rolling-journal.js` scans from **last journal time → now** instead of fixed daily boundaries.

**Features**:
- Configurable schedule hour (default: 22:00, customizable via `~/.phoenixclaw/config.yaml`)
- Rolling window: No content loss even if generation time varies
- Backward compatible with existing `late-night-supplement.js`

**Configuration** (`~/.phoenixclaw/config.yaml`):
```yaml
schedule:
  hour: 22        # Journal generation time
  minute: 0
  rolling_window: true   # Enable rolling window (recommended)
```

**Usage**:
```bash
# Default: generate from last journal to now
node scripts/rolling-journal.js

# Specific date
node scripts/rolling-journal.js 2026-02-12
```

## 💬 Explicit Triggers

While passive by design, users can interact with PhoenixClaw directly using these phrases:
- *"Show me my journal for today/yesterday."*
- *"What did I accomplish today?"*
- *"Analyze my mood patterns over the last week."*
- *"Generate my weekly/monthly summary."*
- *"How am I doing on my personal goals?"*
- *"Regenerate my journal."* / *"重新生成日记"*

> [!warning] **Manual Invocation = Full Pipeline**
> When users request journal generation/regeneration, you MUST execute the **complete 9-step Core Workflow** above. This ensures:
> - **Photos are included** (via session log scanning)
> - **Ledger plugin runs** (via `post-moment-analysis` hook)
> - **All plugins execute** (at their respective hook points)
> 
> **Common mistakes to avoid:**
> - ❌ Only calling `memory_get` (misses photos)
> - ❌ Skipping moment identification (plugins never trigger)
> - ❌ Generating journal directly without plugin sections

## 📚 Documentation Reference
### References (`references/`)
- `user-config.md`: Initial onboarding and persistence settings.
- `cron-setup.md`: Technical configuration for nightly automation.
- `plugin-protocol.md`: Plugin architecture, hook points, and integration protocol.
- `media-handling.md`: Strategies for extracting meaning from photos and rich media.
- `session-day-audit.js`: Diagnostic utility for verifying target-day message coverage across session logs.
- `visual-design.md`: Layout principles for readability and aesthetics.
- `obsidian-format.md`: Ensuring compatibility with Obsidian and other PKM tools.
- `profile-evolution.md`: How the system maintains a long-term user identity.
- `skill-recommendations.md`: Logic for suggesting new skills based on journal insights.

### Assets (`assets/`)
- `daily-template.md`: The blueprint for daily journal entries.
- `weekly-template.md`: The blueprint for high-level weekly summaries.
- `profile-template.md`: Structure for the `profile.md` persistent identity file.
- `timeline-template.md`: Structure for the `timeline.md` chronological index.
- `growth-map-template.md`: Structure for the `growth-map.md` thematic index.

---
