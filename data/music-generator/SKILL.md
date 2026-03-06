---
name: music-generator
description: Generates music from a structured Composition Plan. Use this skill to execute music generation after a prompt or plan has been designed. It validates the output quality and retries on failure.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🎵"
    tags: ["music", "generation", "ai", "audio"]
---

# Music Generator

This skill takes a structured `Composition Plan` and generates a high-quality audio file using an AI music model. It's designed to be the execution engine in a music creation workflow, ensuring the final output matches the creative design specifications.

## When to Use

- **After a `Composition Plan` is created**: This skill is the logical next step once you have a detailed JSON plan for the music.
- **To execute music generation**: When the goal is to produce the final audio file based on a prompt or design.

**Avoid using this skill if:**
- The `Composition Plan` has not been created or is incomplete.
- You only need to design the music, not generate it (use a `music-design` or `prompt-generation` skill for that).

## Core Principles

- **Specification-Driven**: Generation parameters must strictly match the design specifications in the `Composition Plan`.
- **Duration Precision**: The output audio's duration must be validated against the target length with a tight tolerance.
- **Quality First**: The skill will automatically retry generation if the output quality does not meet the defined standards.

## Workflow

1.  **Load Composition Plan**: The skill starts by loading the `Composition Plan` JSON file.
2.  **Set Generation Parameters**: It consults the `music-generation-kb.md` to configure parameters for the generation API call, including:
    *   `duration_ms`: Total duration, precisely matching the target (e.g., video length).
    *   `output_format`: `WAV` for production, `MP3` for delivery.
    *   `instrumental`: Set to `true` to ensure no vocals are generated.
3.  **Execute Generation**: It calls the music generation model's API, passing the `Composition Plan` and configured parameters.
4.  **Quality Validation (QV)**: After generation, it performs a rigorous quality check based on `music-generation-kb.md`:
    *   **Duration Match**: Is the audio length within ±0.5 seconds of the target?
    *   **Style Consistency**: Does the music match the `positive_global_styles` and avoid the `negative_global_styles`?
    *   **Audio Fidelity**: Is the audio free of distortion, clipping, and noise?
    *   **Transitions**: Are the transitions between sections smooth and natural?
5.  **Error Handling & Retry**: If the QV fails, the skill will:
    *   Log the reason for failure.
    *   Attempt to regenerate up to 3 times, potentially with slight adjustments to the plan.
    *   Escalate for manual review if all retries fail.
6.  **Output Audio File**: Once a generation passes QV, the skill outputs the final, validated audio file (`music_file`).

## References

- **[music-generation-kb.md](references/music-generation-kb.md)**: This knowledge base file defines the API specifications, `Composition Plan` schema, and detailed quality validation standards.
