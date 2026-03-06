# OpenAI Codex docs summary (from developers.openai.com/codex)

Reviewed pages:
- https://developers.openai.com/codex
- https://developers.openai.com/codex/cli
- https://developers.openai.com/codex/quickstart

## Confirmed points

- Codex is OpenAI's coding agent for software development.
- Codex can write code, understand unfamiliar codebases, review code, debug/fix issues, and automate repetitive engineering tasks.
- Codex CLI runs locally in terminal and can read/change/run code in selected directory.
- Install command: `npm i -g @openai/codex`
- Run command: `codex`
- One-shot scripting path is supported via `codex exec`.
- First run requires sign-in (ChatGPT account or API key).
- CLI docs mention interactive mode, model/reasoning controls, image input, local review, web search, Codex Cloud tasks, MCP, approval modes.

## Operational implication for OpenClaw

When OpenClaw invokes Codex:
1. set `workdir` to target repo,
2. keep `pty:true`,
3. choose foreground/background mode per task length,
4. stream/check logs for verifiable completion.
