---
name: islamic-tiktok-stories
description: >
  End-to-end pipeline for creating faceless Islamic story TikTok videos.
  Orchestrates multiple specialized agents: story research, scriptwriting,
  image generation, voice narration, and video assembly. Use this skill
  whenever the user wants to create Islamic content videos, generate
  TikTok/Reels/Shorts about Islamic stories, or produce faceless narration
  videos about prophets, sahaba, or Islamic history. Also trigger when
  the user mentions "Islamic TikTok", "story videos", "faceless creator",
  or wants to batch-produce religious educational short-form content.
---

# Islamic TikTok Stories — Multi-Agent Pipeline

## How This Skill System Works

This is a **multi-agent pipeline**. There is ONE top-level orchestrator agent
and FIVE specialist agents beneath it. Here's how they connect:

```
┌─────────────────────────────────────────────────────┐
│              ORCHESTRATOR AGENT                      │
│  (You feed THIS file — SKILL.md — to this agent)    │
│                                                      │
│  This agent reads SKILL.md, understands the full     │
│  pipeline, and delegates to specialist agents.       │
│  It is the "director" — it calls each agent in       │
│  order, passes outputs between them, and handles     │
│  errors.                                             │
└──────────┬──────────────────────────────────────────┘
           │ delegates to:
           │
    ┌──────┴──────┐
    │             │
    ▼             ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
│ Story  │→ │ Script │→ │ Visual │  │ Voice  │→ │Assembly│
│ Agent  │  │ Agent  │  │ Agent  │  │ Agent  │  │ Agent  │
│        │  │        │  │   ↓    │  │   ↓    │  │        │
│ skill: │  │ skill: │  │(parallel)─(parallel)│  │ skill: │
│story.md│  │script  │  │ skill: │  │ skill: │  │assembly│
│        │  │  .md   │  │visual  │  │voice.md│  │  .md   │
│        │  │        │  │  .md   │  │        │  │        │
└────────┘  └────────┘  └────────┘  └────────┘  └────────┘
```

### How to set this up in OpenClaw:

1. **Create the Orchestrator Agent**
   - Attach THIS file (SKILL.md) as its skill
   - This agent needs the ability to call/invoke other agents
   - It reads the pipeline flow below and executes step by step

2. **Create each Specialist Agent**
   - Each gets its own skill file from the `agents/` folder
   - Story Agent → `agents/story_agent.md`
   - Script Agent → `agents/script_agent.md`
   - Visual Agent → `agents/visual_agent.md`
   - Voice Agent → `agents/voice_agent.md`
   - Assembly Agent → `agents/assembly_agent.md`

3. **Attach tools to each agent**
   - Story Agent: web search (for hadith verification), file read
   - Script Agent: no external tools needed (pure LLM reasoning)
   - Visual Agent: image generation API (Flux/SDXL), face detection tool
   - Voice Agent: ElevenLabs / OpenAI TTS API
   - Assembly Agent: FFmpeg, file system access

4. **The Orchestrator calls agents in sequence:**
   ```
   orchestrator receives: "Make a video about Prophet Nuh"
     → calls Story Agent → gets story JSON
     → calls Script Agent with story JSON → gets script JSON
     → calls Visual Agent with script JSON → gets image paths (parallel)
     → calls Voice Agent with script JSON → gets audio paths  (parallel)
     → calls Assembly Agent with images + audio + script → gets final video
   ```

---

## Visual Approach: Narrator + Story Scenes

Each video uses TWO types of visuals:

### 1. Narrator Scenes (brand anchor — same across ALL videos)
The faceless man in traditional Arabic clothing. Used for:
- **Opening shot (first 2-3 seconds)** — establishes the "host"
- **Closing shot (last 2-3 seconds)** — delivers the lesson / CTA

The narrator character is your **brand identity**. Viewers recognize him
across all your videos. He always looks the same:
- White thobe, red-checkered keffiyeh
- NEVER shows face (back shots, silhouettes, over-shoulder, hands)
- Same painterly art style, same color palette

### 2. Story Scenes (UNIQUE per video)
The middle 80% of each video shows **what is actually happening in the
story**. These are completely unique to each video.

**Example — Story of Prophet Nuh (Noah):**
| Beat | Visual |
|------|--------|
| Nuh preaching | Wide shot: lone figure on raised ground addressing a crowd in ancient city, people turning away |
| Building the ark | Close-up: weathered hands hammering wood, massive wooden frame in background |
| The mockery | Crowd of silhouettes laughing and pointing at the ship in the desert |
| The flood begins | Dark storm clouds, rain hammering earth, water rising rapidly |
| Animals boarding | Pairs of animal silhouettes walking toward a massive wooden ship at dawn |
| The flood | Enormous waves, the ark riding the storm, lightning illuminating the scene |
| Waters recede | Ark resting on a mountaintop, olive branch, golden light breaking through |

**Example — Story of Prophet Yusuf (Joseph):**
| Beat | Visual |
|------|--------|
| The dream | A boy looking up at night sky with 11 stars, sun, and moon arranged in a pattern |
| The well | Dark stone well in desert, rope descending into darkness |
| The caravan | Camels in a line crossing desert dunes, golden dust in air |
| The palace | Ornate Egyptian palace interior, golden columns, silk drapes |
| Prison | Dim stone cell, single beam of light through a high window |
| The reunion | Two silhouetted figures embracing in a field at sunset |

### Critical Rules for Story Scenes:
- **NO faces on any Prophets, Angels, or Sahaba** — same faceless techniques
- Story scenes CAN show: landscapes, architecture, objects, animals,
  weather, hands/feet, silhouettes, wide shots where figures are tiny
- Art style must stay consistent WITHIN a single video
- Story scenes should match the emotional mood of the narration beat

### How the Script Agent marks scene types:

```json
{
  "scenes": [
    {
      "scene_number": 1,
      "scene_category": "narrator_opening",
      "narration_text": "What happens when an entire world turns against one man?",
      "visual_direction": {
        "description": "Back shot of narrator on cliff overlooking vast ocean, wind in his thobe",
        "character_type": "narrator"
      }
    },
    {
      "scene_number": 2,
      "scene_category": "story",
      "narration_text": "Prophet Nuh, alayhi as-salam, called his people to Allah for 950 years...",
      "visual_direction": {
        "description": "Ancient city. A lone silhouetted figure stands on raised ground, arms raised to the sky, addressing a crowd below. The crowd turns away. Hot dusty afternoon.",
        "character_type": "story_figure",
        "story_element": "Nuh preaching to his people"
      }
    },
    {
      "scene_number": 9,
      "scene_category": "narrator_closing",
      "narration_text": "And that is why patience is never wasted with Allah...",
      "visual_direction": {
        "description": "Narrator sitting on rock at sunset, calm sea, same cliff from opening but now peaceful golden light",
        "character_type": "narrator"
      }
    }
  ]
}
```

The Visual Agent uses DIFFERENT prompt strategies:
- `narrator_opening` / `narrator_closing` → strict narrator character prompt (brand consistency)
- `story` → story-specific prompt, unique imagery, faceless constraint on human figures only

---

## Global Config

Before any agent runs, this config is loaded and shared with all agents.

```json
{
  "brand": {
    "channel_name": "{{CHANNEL_NAME}}",
    "narrator_character": "A faceless man wearing traditional white thobe and red-checkered keffiyeh/shemagh. Never show face — use back shots, silhouettes, over-shoulder angles, hands close-ups, or wide shots. Dignified, contemplative, wise.",
    "visual_style": "Cinematic, warm golden-hour lighting, painterly digital art style — NOT photorealistic, NOT cartoon. Epic film concept art quality.",
    "color_palette": ["#C8956C", "#2C1810", "#F5E6D0", "#1A3A4A", "#D4A853"],
    "aspect_ratio": "9:16",
    "resolution": "1080x1920"
  },
  "content_guidelines": {
    "sensitivity_rules": [
      "NEVER depict faces of any Prophet, Angel, or Sahabi",
      "NEVER depict faces on the narrator character",
      "All human figures in story scenes must also be faceless",
      "Use nasheeds or ambient sound only — no musical instruments",
      "Always include proper Islamic honorifics",
      "Only use Sahih or Hasan grade hadith",
      "Cite Surah name and verse number for all Quran references"
    ]
  },
  "target_languages": ["en", "ar", "fr", "ur", "tr", "id"],
  "default_language": "en"
}
```

---

## Pipeline Execution (Orchestrator Playbook)

When the orchestrator receives a request:

### Step 1: Call Story Agent
```
Input:  { "topic": "Prophet Nuh", "target_duration_seconds": 60 }
Output: Story JSON with sources, emotional arc, key visual moments
```

### Step 2: Call Script Agent
```
Input:  Story Agent output
Output: Scene-by-scene script with:
        - narration text per scene
        - scene_category (narrator_opening / story / narrator_closing)
        - visual directions unique to the story
        - timing and subtitle text
```

### Step 3: Call Visual Agent + Voice Agent (PARALLEL)
```
Visual: Script scenes → generates images per scene
        (narrator prompt template for opening/closing)
        (story-specific prompt for middle scenes)
Voice:  Script narration → generates audio per scene + word timestamps
```

### Step 4: Call Assembly Agent
```
Input:  Images + motion configs + audio + subtitle text + brand assets
Output: Final MP4, thumbnail, SRT file
```

### Step 5: Quality Checks (Orchestrator does this itself)
- Verify no faces in any generated image (call face detection)
- Verify audio/visual sync (check durations match)
- Verify file size under 50MB
- If fail → retry failing agent up to 3 times

### Step 6: Output
- Save video to output directory
- Log to content calendar

---

## Agent Skill Files

Each agent has its own detailed skill file:

| Agent | Skill File | Purpose | Tools Needed |
|-------|-----------|---------|--------------|
| Story Research | `agents/story_agent.md` | Find + validate Islamic stories | Web search, file read |
| Script Writer | `agents/script_agent.md` | Story → TikTok script with scene directions | None (pure LLM) |
| Visual Generation | `agents/visual_agent.md` | Generate narrator + story scene images | Image gen API, face detection |
| Voice Narration | `agents/voice_agent.md` | TTS with Arabic pronunciation | ElevenLabs/OpenAI TTS |
| Video Assembly | `agents/assembly_agent.md` | Images + audio → final video | FFmpeg/Remotion |

**Read each agent's skill file for full input/output JSON schemas,
prompt templates, and quality gates.**

---

## References

| File | Purpose |
|------|---------|
| `references/visual_style_guide.md` | Faceless techniques, environments, lighting, Ken Burns, prompt templates |
| `config/global_config.json` | Full config template with API settings, brand, pipeline params |
