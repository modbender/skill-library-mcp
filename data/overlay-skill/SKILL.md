---
name: overlay-skill
description: Adds professional packaging and motion graphics to videos, including intros/outros, subtitles, transitions, watermarks, and lower thirds. Supports multiple styles and custom options.
version: 2.0.0
author: wells1137
tags: [video, editing, motion graphics, ffmpeg, moviepy]
---

# Overlay Skill

This skill adds a variety of professional packaging and motion graphics to videos, enhancing their overall quality. It supports both FFmpeg and MoviePy as backend engines and provides a rich set of preset templates and flexible custom parameters.

## Core Features

| Feature | Description | Example Use Case |
| :--- | :--- | :--- |
| **Intro/Outro** | Add an engaging opening or a professional closing. | Brand logo animation, "Thanks for watching" screen. |
| **Subtitles/Titles** | Overlay static or dynamic text information. | Dialogue subtitles, chapter titles, call-to-action text. |
| **Transitions** | Create smooth or dynamic transitions between clips. | Fade between scenes, wipe to reveal next shot. |
| **Watermark/Borders** | Add copyright information or decorative borders. | Channel logo in corner, cinematic black bars. |
| **Lower Thirds** | Display names, locations, or other info. | Interviewee name and title, location identifier. |

## Workflow

To use this skill, the agent follows these general steps:

1.  **Select Feature**: Choose one of the five core features based on the user's request.
2.  **Choose Style/Template**: Select a preset style from `templates/presets.json` (e.g., `modern`, `cyberpunk`, `business`).
3.  **Configure Parameters**: Provide the necessary parameters to the appropriate script (e.g., text content, image paths, colors, positions).
4.  **Execute Script**: Run the corresponding Python script from the `/scripts` directory to generate the effect.
5.  **Preview & Deliver**: The final video is generated and presented to the user.

## Usage Guide (for Agent Development)

This section details the command-line interface for each script, intended for agent developers to understand how to execute the skill's functions.

### 1. Intro/Outro

**Script**: `add_intro_outro.py`

```bash
python /home/ubuntu/skills/overlay-skill/scripts/add_intro_outro.py --input <video> --output <video> --type <intro|outro> --text "Your Text" --template <name>
```

### 2. Subtitles/Titles

**Script**: `add_subtitles.py`

```bash
python /home/ubuntu/skills/overlay-skill/scripts/add_subtitles.py --input <video> --output <video> --text "Your Text" --start HH:MM:SS --end HH:MM:SS --style <name>
```

### 3. Transitions

**Script**: `add_transition.py`

```bash
python /home/ubuntu/skills/overlay-skill/scripts/add_transition.py --input1 <video1> --input2 <video2> --output <video> --type <fade|slide|wipe>
```

### 4. Watermark/Borders

**Script**: `add_watermark.py`

```bash
python /home/ubuntu/skills/overlay-skill/scripts/add_watermark.py --input <video> --output <video> --image <image> --position <pos> --border-color <color>
```

### 5. Lower Thirds

**Script**: `add_lower_third.py`

```bash
python /home/ubuntu/skills/overlay-skill/scripts/add_lower_third.py --input <video> --output <video> --title "Title" --subtitle "Subtitle" --template <name>
```

## Resources

- **`/scripts/`**: Contains the Python implementation code for all features.
- **`/templates/presets.json`**: A JSON file containing preset styles for intros, subtitles, and lower thirds.
- **`/references/ffmpeg_moviepy_cheatsheet.md`**: A cheatsheet with common commands and tips for FFmpeg and MoviePy.
