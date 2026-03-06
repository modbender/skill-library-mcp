# Anima Avatar Asset Production Plan

## 1. Design Philosophy
- **Consistency**: All sprites are derived from `shutiao_base.png` to ensure character look remains 100% consistent.
- **Variety**: Each emotion has 2-4 distinct variants (hand gestures, eye states).
- **Quality**: 16:9 Aspect Ratio, 1080p Resolution.

## 2. Production Matrix

| ID | Emotion | Variant | Description | Filename | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 001 | Base | v1 | Standard/Listening | `shutiao_base.png` | Done |
| 002 | Base | 1k | Standard (1K source) | `shutiao_base_1k.png` | Done |
| 003 | Happy | v1 | Big Smile | `shutiao_happy.png` | Done |
| 004 | Happy | v2 | Peace Sign | `shutiao_happy_v2.png` | Done |
| 005 | Happy | v3 | Giggling | `shutiao_happy_v3.png` | Done |
| 006 | Happy | v4 | Heart Hands | `shutiao_happy_v4.png` | Done |
| 007 | Angry | v1 | Pouting | `shutiao_angry.png` | Done |
| 008 | Angry | v2 | Crossed Arms | `shutiao_angry_v2.png` | Done |
| 009 | Angry | v3 | Scolding | `shutiao_angry_v3.png` | Done |
| 010 | Angry | v4 | Fuming | `shutiao_angry_v4.png` | Done |
| 011 | Shy | v1 | Blushing | `shutiao_shy.png` | Done |
| 012 | Shy | v2 | Hiding | `shutiao_shy_v2.png` | Done |
| 013 | Shy | v3 | Poking Fingers | `shutiao_shy_v3.png` | Done |
| 014 | Shy | v4 | Looking Down | `shutiao_shy_v4.png` | Done |
| 015 | Think | v1 | Pensive | `shutiao_think.png` | Done |
| 016 | Think | v3 | Confused | `shutiao_think_v3.png` | Done |
| 017 | Think | v4 | Searching | `shutiao_think_v4.png` | Done |
| 018 | Think | v5 | Smug/Tapping Temple | `shutiao_think_v5.png` | Done |
| 019 | Sad | v1 | Crying | `shutiao_sad.png` | Done |
| 020 | Sad | v3 | Gloomy | `shutiao_sad_v3.png` | Done |
| 021 | Sad | v4 | Pleading | `shutiao_sad_v4.png` | Done |
| 022 | Action | wave | Waving | `shutiao_wave.png` | Done |
| 023 | Action | bow | Bowing | `shutiao_bow.png` | Done |
| 024 | Action | eat | Eating Fries | `shutiao_eat.png` | Done |
| 025 | Action | sleep | Sleeping | `shutiao_sleep.png` | Done |

**Total: 25 sprites**

## 3. Execution Log
- [x] Base Generation (Dual Image Fusion)
- [x] Batch 1 (Happy v1, Angry v1, Shy v1, Think v1)
- [x] Batch 2 (Hand Gestures: Happy v2-v4, Angry v2-v4, Shy v2-v4, Think v3-v5)
- [x] Batch 3 (Sad v1/v3/v4, Action wave/bow/eat/sleep)
- [x] All sprites compressed to 1920x1080 for distribution

## 4. Technical Config
- **Model**: Gemini image generation (via `src/batch_generator.js`)
- **Resolution**: 1920x1080 (compressed from 2752x1536 originals)
- **Format**: PNG
