---
name: youtube-summary
description: Summarize YouTube videos into structured Markdown with youtube2md, including chaptered notes, timestamp links, and key takeaways. Use when the user provides one or more YouTube URLs and asks for summaries, study notes, language-specific summaries, transcript extraction, or machine-readable JSON output.
env:
  - name: OPENAI_API_KEY
    required: false
    description: Enables full summarization mode. When set, transcript content is sent to OpenAI. Omit to use extract-only mode with local summarization.
---

# YouTube Summary (youtube2md)

Use the official `youtube2md` CLI behavior from the repository.

## Runtime + security prerequisites

- Require **Node.js 18+**.
- Require preinstalled `youtube2md` on PATH.
  - Recommended pinned install: `npm i -g youtube2md@1.0.1`
- Require **python3** for transcript text preparation (`prepare.py`) in extract mode.
- Default runner uses local `youtube2md` executable only.
- Runtime npm execution (`npx`) is intentionally not supported in this skill.
- The `YOUTUBE2MD_BIN` environment variable override is rejected by the runner.
- `OPENAI_API_KEY` enables full summarization mode; transcript/content may be sent to OpenAI through youtube2md’s workflow.
  - For sensitive content, omit `OPENAI_API_KEY` and use extract mode.
- In sensitive environments, audit the upstream `youtube2md` package and dependencies before installation or version bumps.

See `references/security.md` before first-time install/enable.

## Workflow

1. Validate input
   - Accept `youtube.com` and `youtu.be` URLs.
   - If URLs are missing, ask for one URL per line.

2. Choose mode
   - **Full mode**: generates Markdown.
     - Use when `OPENAI_API_KEY` is available and external API use is acceptable.
   - **Extract mode** (`--extract-only`): outputs transcript JSON and prepares transcript text (`.txt`).
     - Use when API key is unavailable or when transcript-only output is requested.
   - Prefer a **no-error path**: check key first and run extract directly when key is missing.

3. Run converter
   - Preferred runner script:
     - `scripts/run_youtube2md.sh <url> full [output_md_path] [language] [model]`
       - If `OPENAI_API_KEY` is missing, runner auto-falls back to extract mode by default.
     - `scripts/run_youtube2md.sh <url> extract [output_json_path]`
   - Optional machine-readable CLI output:
     - `YOUTUBE2MD_JSON=1 scripts/run_youtube2md.sh <url> full`
     - `YOUTUBE2MD_JSON=1 scripts/run_youtube2md.sh <url> extract`
   - Runtime controls:
     - Use only locally installed `youtube2md` executable.
     - Do not use runtime npm execution (`npx`) for this skill.
   - Direct CLI equivalent:
     - `youtube2md --url <url> [--out <path>] [--lang <language>] [--model <model>]`
     - Add `--extract-only` for transcript-only mode.

4. Verify output
   - Full mode: Markdown file exists and is non-empty.
   - Extract mode: JSON file exists and is non-empty.
   - Extract mode: prepared TXT file exists and is non-empty.
   - If using `--json`, parse `ok: true/false` and handle error `code`.

5. Respond to the user
   - Follow `references/output-format.md` as the default response shape.
   - Follow `references/summarization-behavior.md` for source policy and chapter/takeaway density.
   - Do **not** include generated local file path(s) in normal user-facing replies.
   - Share file paths only when explicitly requested by the user (e.g., debugging/export workflows).
   - **Summary source policy:**
     - Full mode succeeded → use youtube2md Markdown output as the summary source.
     - Non-full mode (extract) → use prepared `.txt` transcript text as the summary source.
   - Keep user-facing flow smooth: if key is missing, use extract output and summarize from `.txt` without surfacing avoidable tool-error noise.

## Multi-video requests

- Process URLs sequentially.
- Return per-video summary results (omit local file paths unless requested).
- If any fail, report successful items first, then failures with fixes.

## Built-in behavior to trust

- Default output paths:
  - Full mode: `./summaries/<video_id>.md`
  - Extract mode: `./summaries/<video_id>.json`
  - Local runner post-process (extract): `./summaries/<video_id>.txt` via `prepare.py`

## Packaging hygiene

- Do not publish generated outputs (e.g., `summaries/*.json`, `summaries/*.txt`) inside the skill folder.
- Keep only source files (`SKILL.md`, `scripts/`, `references/`, helpers) in release artifacts.

## Resources

- CLI runner: `scripts/run_youtube2md.sh`
- Transcript text prep: `prepare.py`
- Output guidance: `references/output-format.md`
- Behavior reference: `references/summarization-behavior.md`
- Security/install notes: `references/security.md`
- Troubleshooting and error codes: `references/troubleshooting.md`
