# Audio Routing Logic KB

This document outlines the rules and keywords for classifying an audio request prompt into one of three categories: `music`, `sfx`, or `tts`.

## Classification Hierarchy

The classification process follows a specific order of checks. The first match determines the `audio_type`.

**1. Text-to-Speech (TTS) Check**

- **Primary Trigger**: The prompt contains a substantial amount of text intended for narration, enclosed in quotation marks or clearly formatted as a script.
- **Keywords**: `"read"`, `"say"`, `"narrate"`, `"voice-over"`, `"speak"`, `"pronounce"`
- **Length Heuristic**: If the prompt text is longer than 15 words and reads like a sentence or paragraph, it is likely TTS.

*Example Prompts*:
- `"Can you read this for me: 'The quick brown fox jumps over the lazy dog.'"` -> **tts**
- `"Narrate the following script: 'Welcome to our product demo...'"` -> **tts**

**2. Sound Effect (SFX) Check**

- **Primary Trigger**: The prompt describes a specific, discrete event, action, or ambient sound.
- **Keywords**: `"sound of"`, `"sfx"`, `"effect"`, `"ambience"`, `"noise"`, `"footsteps"`, `"explosion"`, `"door creak"`, `"wind blowing"`, `"typing on a keyboard"`, `"car horn"`
- **Structure Heuristic**: Prompts are often short, descriptive phrases focusing on an object and an action.

*Example Prompts*:
- `"The sound of a heavy wooden door creaking open slowly."` -> **sfx**
- `"Jungle ambience at night with crickets and distant animal calls."` -> **sfx**
- `"A short, tense, cinematic swell, building in intensity."` -> **sfx**

**3. Music Check (Default)**

- **Primary Trigger**: If the prompt does not meet the criteria for TTS or SFX, it defaults to `music`.
- **Keywords**: `"music"`, `"track"`, `"song"`, `"melody"`, `"harmony"`, `"rhythm"`, `"beat"`, `"instrumental"`, `"background music"`, `"soundtrack"`, `"lo-fi"`, `"cinematic"`, `"upbeat"`, `"jazz"`, `"rock"`
- **Structure Heuristic**: Prompts often describe a mood, genre, style, or instrumentation.

*Example Prompts*:
- `"An upbeat, funky electronic track with a strong bassline."` -> **music**
- `"A sad, slow, cinematic piano melody."` -> **music**
- `"Background music for a corporate presentation, professional and inspiring."` -> **music**

## Edge Cases & Disambiguation

- **Prompt: "A singing bird"**: This could be SFX (a realistic bird call) or Music (a melodic, stylized bird song). The dispatcher may need to ask for clarification, e.g., "Do you want a realistic sound effect or a musical interpretation?"
- **Prompt: "A dramatic drum roll"**: This is likely SFX, but could be part of a larger musical piece. The context of the request is key. If it's for a specific moment (like an announcement), it's SFX. If it's part of a song description, it's Music.
