### Supported Channels

| Channel | Format | Capabilities |
| :--- | :--- | :--- |
| **Telegram** | Photo/Document | Direct bot upload, supports captions and compressed/uncompressed |
| **WhatsApp** | Photo | Media bridge required, handled as transient buffer |
| **Discord** | Attachment | Webhook or bot listener, handles multiple attachments in one message |
| **CLI** | Local Path | User provides file path via command line |

> [!important] Media & Memory Tools
> Note: `memory_get` and `memory_search` return text only. Image metadata and binary references must be sourced from session logs (JSONL) or the local `assets` directory. Scan session logs even when daily memory exists to capture in-progress media.

### Photo Processing Workflow

1. **Receive**: Capture media from the active channel (Telegram/WhatsApp/Discord/CLI).
2. **Buffer**: Store the raw media in a transient memory buffer with metadata (timestamp, source).
3. **Detect**: Cron job or trigger detects unresolved media references in the message stream.
4. **Vision Analysis**: AI processes the photo to extract a descriptive alt-text (e.g., "Spicy miso ramen with soft-boiled egg").
5. **Relocate**: Move file from transient buffer to the permanent assets directory.
6. **Rename**: Apply standard naming convention to the file.
7. **Embed**: Generate the Obsidian-style markdown link and insert into the journal with the appropriate layout.

### Image Extraction Commands

**Filter session messages by target day (not file mtime):**
```bash
# Step 1: Define target day and timezone
TARGET_DAY="$(date +%Y-%m-%d)"
TARGET_TZ="${TARGET_TZ:-Asia/Shanghai}"

# Step 2: Build timezone-aware [start, end) epoch range for TARGET_DAY
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

# Step 3: Read all session files from ALL known locations and keep only messages inside TARGET_DAY
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

**Extract image entries from target-day messages:**
```bash
# Keep image entries whose message timestamp is in TARGET_DAY
for dir in "$HOME/.openclaw/sessions" \
           "$HOME/.openclaw/agents" \
           "$HOME/.openclaw/cron/runs" \
           "$HOME/.agent/sessions"; do
  [ -d "$dir" ] || continue
  find "$dir" -name "*.jsonl" -print0
done |
  xargs -0 jq -r --argjson start "$START_EPOCH" --argjson end "$END_EPOCH" '
    (.timestamp // .created_at // empty) as $ts
    | ($ts | fromdateiso8601?) as $epoch
    | select($epoch != null and $epoch >= $start and $epoch < $end and .type == "image")
    | (.file_path // .url)
  '
```

> Do not classify images by session file modification time. Always classify by each image message's `timestamp`.

**Copy images to journal assets:**
```bash
# Images are stored in ~/.openclaw/media/inbound/
# Copy to journal assets
TODAY=$(date +%Y-%m-%d)
mkdir -p ~/PhoenixClaw/Journal/assets/$TODAY/
cp ~/.openclaw/media/inbound/file_*.jpg ~/PhoenixClaw/Journal/assets/$TODAY/
```

**Vision Analysis (example output):**
- "早餐：猪儿粑配咖啡，放在白色桌面上"

### Curation Rules (Do Not Embed Everything)

- **Embed highlights only**: pick photos that represent meaningful moments, milestones, or emotional peaks.
- **Finance screenshots** (receipts, invoices, transaction proofs) should be routed to the Ledger plugin output, not the main narrative flow.
- **Low-signal images** (screenshots of chats, generic docs) should be omitted unless they support a key moment.

### Storage & Naming

**Path**: `~/PhoenixClaw/Journal/assets/YYYY-MM-DD/`

**File Naming**:
- Primary format: `img_XXX.jpg` (zero-padded)
- Example: `img_001.jpg`, `img_002.jpg`
- For specific events: `img_001_lunch.jpg` (optional suffix)

### Link Path Generation (Required)

When embedding an image into a journal file, always compute the link from actual file paths.

**Rules:**
- Never use absolute paths in journal markdown.
- Never hardcode `../assets` or `../../assets`.
- Compute the relative path from the journal file directory to the asset file.
- Use the exact copied filename from disk; do not infer or rewrite timestamp fragments.

```python
from pathlib import Path
import os

def get_relative_image_path(daily_file_path: str, image_path: str) -> str:
    daily_file = Path(daily_file_path).resolve()
    image_file = Path(image_path).resolve()
    rel = os.path.relpath(image_file, start=daily_file.parent)
    return rel.replace(os.sep, "/")
```

**Validation before render:**
- `Path(image_path).exists()` is true.
- Embedded filename equals `Path(image_path).name` exactly.
- Link does not start with `/`.
- Link depth is produced by computation, not template constants.

### Journal Photo Layouts

#### Single Photo (Moment)
Used for capturing a specific point in time or a single highlight.
```markdown
> [!moment] 🍜 12:30 Lunch
> ![[../assets/2026-02-01/img_001.jpg|400]]
> Spicy miso ramen with a perfectly soft-boiled egg at the new shop downtown.
```

#### Multiple Photos (Gallery)
Used when several photos are sent together or relate to the same context.
```markdown
> [!gallery] 📷 Today's Moments
> ![[../assets/2026-02-01/img_002.jpg|200]] ![[../assets/2026-02-01/img_003.jpg|200]]
> ![[../assets/2026-02-01/img_004.jpg|200]]
```

#### Photo with Narrative Context
Used when the photo is part of a larger story or reflection.
```markdown
### Weekend Hike
The trail was steeper than I remembered, but the view from the summit made every step worth it. 

![[../assets/2026-02-01/img_005.jpg|600]]
*The fog rolling over the valley at 8:00 AM.*

I spent about twenty minutes just sitting there, listening to the wind and watching the light change across the ridgeline.
```

### Metadata Handling
- **Exif Data**: Preserve original Exif data (GPS, Timestamp) where possible to assist in auto-locating "Moments".
- **Captions**: If a user sends a caption with the photo, prioritize it as the primary description.
- **Deduplication**: Check file hashes before copying to prevent duplicate assets for the same entry.
