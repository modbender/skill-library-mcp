---
name: material-report
description: Analyze ad material videos and produce a markdown report with framework, material traits, and acquisition keywords, then propose new material production frameworks and detailed storyboard tables. Use when users provide a video asset and want analysis plus new creative guidance for performance ads.
---

# Material Report

## Quick Start
- Request or confirm: video path, category/vertical, target platform.
- Duration spec: keep the new material duration roughly consistent with the original video unless the user explicitly requests otherwise.
- Analyze the provided video and output a markdown report.

## Workflow
1. Verify the video file exists and read basic metadata (duration, resolution, fps).
2. Before extracting frames, check whether frame images already exist. If they do, reuse them directly.
3. If frame extraction is needed, use ffmpeg to extract frames. Save all frame images in a folder named after the video (same base name) under the current working directory. If permissions prevent this, ask the user to grant access; do not change the output path.
4. If ffmpeg is not available on the user's machine, prompt the user to install ffmpeg (do not provide installation instructions in this skill) or provide an existing frame image folder path.
5. Extract the original framework as ordered stages (opening hook, problem, turning points, resolution, ending/CTA).
   - Hook identification: prioritize the first 0-5 seconds and any large on-screen headline, abrupt visual change, or explicit "attention" phrasing. If the hook is ambiguous, state multiple candidates and pick the strongest with a brief rationale.
6. Summarize material traits (format, tempo, overlays, UI density, meme usage, etc.).
7. List acquisition keywords (concise, actionable, aligned to content and visual tactics).
8. Create at least one new material framework. For the "different direction" variant, choose the best-performing direction based on your judgment, without being constrained by the original material. Do not deviate from the same category/vertical and target platform.
9. Provide a detailed storyboard table for the new framework with time ranges, on-screen action, copy, and visual effects.
10. Deliver the report in markdown in the response.
11. If the user does not specify category/vertical, first ask for it; then proceed with a best-effort inference and label it clearly as an assumption in the report.

## Output Template (Markdown)
- Load references/report_template.md and follow its structure

## Notes
- Match the user's language and tone.
- Keep the storyboard single-level lists and clear time ranges.
- If the user requests a same-framework version, keep the structure identical and only change content details.
