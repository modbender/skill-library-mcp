---
name: excretion-tracker
description: "Track bathroom events (pee/poop) via chat: start time, duration, color, pain, and Bristol stool scale. Generates weekly summaries and optional constipation reminders when no poop occurs past a threshold (default 24h, user-configurable). Use for urination/defecation logging, bowel/bladder trends, stool form tracking, diarrhea/constipation monitoring. Search keywords: bathroom tracker, toilet log, BM tracker, stool tracker, poop tracker, pee tracker. Triggers: poop, pee, bowel movement, stool, urination, bathroom log, toilet log, constipation, diarrhea, Bristol, night pee (nocturia)."
---

# Excretion Tracker（排泄记录）

This skill is **chat-only**: always log via the bundled CLI and store data locally.

## 0) Safety / scope
- No medical diagnosis.
- If the user reports **blood in stool/urine**, **severe pain**, **fever**, or symptoms lasting >24–48h, recommend professional medical advice.

## 1) What to collect (required vs optional)

### New: Attempt (no output)
If the user reports **abdominal pain / urge** and **no pee/poop produced** (e.g., “蹲了20分钟都没有产出”), log an `attempt` event with:
- start time
- duration
- pain
- intent: poop | pee | unknown
- notes

Do not force color/Bristol when there was no output.

### Required for every log
- `type`: pee | poop | attempt (no output)
- `start_at`: timestamp (default: now)
- `duration_sec`: integer (if unknown, ask)
- `pain`: 0–3 (0 none, 1 mild, 2 moderate, 3 severe)

### Color requirement
- For `pee` and `poop`: color is required
- For `attempt` (no output): color is not required

### Poop-only
- `bristol`: 1–7 (ask if poop)

### Optional
- `notes`: short free text

## 2) Bristol stool scale (what it is)

Bristol（布里斯托大便分类）把便便形态分为 1–7：
- 1–2：偏干硬（便秘倾向）
- 3–4：相对正常
- 5–7：偏稀（腹泻倾向）

If user doesn’t know, ask 1 question:
- “更像：1/2（很硬成颗粒） 3/4（成形） 5/6/7（软烂到水样）？”

See details: `references/bristol.md`.

## 3) Color options (display to user in Chinese; English in Title Case)

### Pee color
- Clear（透明）
- Pale Yellow（浅黄）
- Yellow（黄色）
- Dark Yellow（深黄）
- Amber（琥珀色）
- Red（红）
- Brown（褐）
- Other（其他）

### Poop color
- Normal Brown（正常棕）
- Light Brown（浅棕）
- Yellow（黄）
- Green（绿）
- Black（黑）
- Red（红）
- Pale（偏浅/灰白）
- Other（其他）

Internal storage can still use snake_case enums, but never show snake_case to the user.
## 4) Chat-only flow (includes optional card feedback)

When the user says they went to the bathroom:

1) Determine `type` (pee/poop). If unclear, ask.
2) Ask only missing required fields **in the user's language** (Chinese).
   - If you need to show any English options, format them in **Title Case** (no underscores).
3) Ask for:
   - start time (if not specified)
   - duration (minutes/seconds)
   - color
   - pain (0–3)
   - for poop: bristol (1–7)
4) Log the event via CLI: `excretion log ...`.
5) **Optional visual card (SOP):**
   - Detect whether `nano-banana-pro` is installed.
   - If installed: follow `references/card_sop.md` to generate a consistent cute 3:4 card using **nano-banana-pro** and send it.
   - If not installed: **skip silently** (no extra questions).

Note: This skill intentionally ships **no image-generation scripts**. The agent should execute the SOP by invoking `nano-banana-pro` when available.
If user says “刚刚/刚才” → use now.
If user provides duration like “2分钟” → convert to seconds.

## 5) Commands to run

- Log pee:
  - `excretion log pee --start-at "..." --duration-sec 60 --color yellow --pain 0 --notes "..."`

- Log poop:
  - `excretion log poop --start-at "..." --duration-sec 180 --color normal_brown --pain 1 --bristol 4 --notes "..."`

- Show weekly summary:
  - `excretion week`

- Set reminder threshold (hours):
  - `excretion config set poop_remind_hours 24`

## 6) Weekly summary (what to send)

Include:
- Poop frequency + avg interval
- Bristol distribution (counts)
- Poop pain average
- Pee frequency (day vs night)
- Red-flag events count (blood/pain>=3)
- “Not medical advice” note

## 7) Files
- CLI: `scripts/excretion.py`
- Bristol reference: `references/bristol.md`
- (Optional) Card generation SOP: `references/card_sop.md` (uses `nano-banana-pro` if installed; otherwise skip)
