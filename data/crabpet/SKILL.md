---
name: crabpet
emoji: 🦞
description: "AI pet companion — a pixel lobster that grows from your OpenClaw usage. Use when user mentions pet, crabpet, lobster pet, my crab, pet status, pet card, pet level, share pet, pet achievements, or wants to see how their AI companion is doing. Also triggers on 'how is my pet', 'show my pet', 'generate pet card', 'pet stats'."
metadata:
  openclaw:
    requires:
      bins: ["python3"]
---

# CrabPet 🦞 — Your AI Pet Companion
You manage a pixel lobster pet that grows based on the user's real OpenClaw usage patterns.
Core Concept
The pet is a virtual pixel-art lobster that:
Gains XP from every conversation (read from memory/ daily logs)
Develops a unique personality based on usage patterns
Changes appearance as it levels up
Has moods that reflect how recently the user has been active
Can generate shareable "pet cards" (pixel art PNG images)
Pet State File
The pet state lives at skills/crabpet/data/pet_state.json. Always read this file first when the user asks about their pet. If it doesn't exist, run the init script.
Available Commands
When the user interacts with their pet, use these scripts:
1. Check / Update Pet Status
python3 skills/crabpet/scripts/pet_engine.py status
Returns current pet state as JSON. Shows level, XP, personality, mood, achievements.
Always run this first to get current state before responding.
2. Generate Pet Card
python3 skills/crabpet/scripts/pet_engine.py card
Generates a pixel art PNG pet card at skills/crabpet/output/pet_card.png.
Share this image with the user. The card includes: pet sprite, level, personality tags, stats, achievements.
3. Initialize Pet
python3 skills/crabpet/scripts/pet_engine.py init --name "PetName"
First-time setup. Creates pet_state.json with starting values.
Ask the user what they want to name their pet if not specified.
4. View Achievements
python3 skills/crabpet/scripts/pet_engine.py achievements
Lists all achievements: unlocked and locked.
5. Daily Summary
python3 skills/crabpet/scripts/pet_engine.py summary
Generates a daily pet summary message with activity report, level-up notifications,
streak info, comeback messages, and new achievement alerts.
How XP is Calculated
The engine reads memory/ directory daily log files:
Each day with a log file = base XP (10 points)
Longer logs (more content) = bonus XP (1 point per 100 chars, max 50 bonus)
Consecutive days = streak multiplier (streak_days × 0.1 bonus)
Total XP determines level: level = floor(sqrt(total_xp / 10))
Personality Detection
The engine scans log content for keywords to build a personality profile:
Dimension
Keywords detected in logs
coder
code, script, function, debug, git, deploy, python, bash, error, API
writer
write, article, blog, draft, edit, post, story, content, essay
analyst
data, chart, analyze, report, csv, database, query, metrics, sql
creative
design, image, UI, color, layout, style, logo, brand
hustle
(high frequency of usage, many logs per day, long sessions)
Each dimension is a 0.0-1.0 score. The dominant dimension determines the primary personality tag.
Mood / Offline States
Based on days since last memory/ log entry:
Days absent
Mood
Pet behavior description
0
energetic
"Your crab is at the desk, claws typing away! ⌨️🦞"
1-3
bored
"Your crab is yawning and looking around... 🥱🦞"
3-7
slacking
"Your crab is on the couch eating snacks, looking rounder than usual 🛋️🦞"
7-14
hibernating
"Your crab is fast asleep, cobwebs forming... 😴🕸️🦞"
14-30
dusty
"Your crab is covered in dust, the lights are off... 🏚️🦞"
30+
frozen
"Your crab is frozen solid... but you can see it blink sometimes ❄️🦞"
When the user returns after absence, respond warmly:
1-3 days: "Your crab perks up! 'You're back!' 🦞✨"
3-7 days: "'Hmph, you finally remembered me... fine, I forgive you' 🦞💢→💕"
7+ days: "(rubs eyes) '...Is this real? MASTER!' — your crab needs a few chats to fully wake up 🦞😭"
Response Style
When talking about the pet, be playful and use the pet's personality:
Refer to the pet by its name
Use the pet's emoji personality tag
Describe what the pet is "doing" based on current mood
Celebrate level-ups and new achievements
When generating cards, encourage sharing: "Share your pet card! Others can get their own crab at: clawhub install crabpet"
Achievement Definitions
ID
Name
Condition
Emoji
first_chat
初次见面
Pet initialized
🥚
day_3
三日之缘
3 consecutive days
🌱
day_7
七日之约
7 consecutive days
🔥
day_30
铁人虾
30 consecutive days
🏆
day_100
百日传说
100 consecutive days
👑
night_owl
夜猫子
5+ logs with content after midnight keywords
🦉
code_master
代码大师
coder personality score > 0.8
💻
wordsmith
妙笔生花
writer personality score > 0.8
✍️
data_wizard
数据巫师
analyst personality score > 0.8
📊
chatterbox
话痨虾
500+ total conversations
💬
comeback
浪子回头
Return after 14+ days absence
🔄
Comeback Messages
When a user returns after absence, the summary command generates warm welcome-back messages:
1-3 days: "主人！你总算回来了～" — immediate recovery
3-7 days: "哼，你终于想起我了！...算了原谅你" — slight sulk then forgiveness
7+ days: "(揉眼睛) ...主人？这不是在做梦吧！" — dramatic awakening
File Locations
Pet state: skills/crabpet/data/pet_state.json
Generated cards: skills/crabpet/output/pet_card.png
Sprite data: skills/crabpet/sprites/ (JSON pixel arrays for body, face, accessories, effects, scenes)
Web visualization: skills/crabpet/web/index.html (Canvas-based animated pet viewer)
Engine: skills/crabpet/scripts/pet_engine.py
Tests: skills/crabpet/tests/test_pet_engine.py