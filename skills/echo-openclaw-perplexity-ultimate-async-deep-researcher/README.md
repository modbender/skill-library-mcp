# Echo - OpenClaw Perplexity Ultimate Async Deep Researcher

A high-performance, autonomous research skill for the OpenClaw framework. This skill empowers your AI Agent to break down complex research tasks and fetch raw data from multiple sources concurrently using the Perplexity Search API.

Built by HolyGrass.

## 🚀 Key Features

- **Blazing Fast Concurrency:** Utilizes `AsyncPerplexity` to execute up to 5 sub-queries simultaneously, drastically reducing the time your Agent spends waiting for web results.
- **Zero-Config Dependency Injection:** The Agent automatically detects and installs the required Perplexity Python SDK on its first run via the internal Python tool. No manual `pip install` required for the end-user.
- **LLM Context Optimization:** Requests "raw data" (snippets, URLs) capped at 2048 tokens per page to reduce payload size and protect your LLM context window.
- **Fault Tolerance:** Built-in error handling ensures that if one search query fails or hits a rate limit, the rest of the research data still returns successfully.

## 🛠 Installation

Create a new directory in your OpenClaw skills folder:

```bash
mkdir -p ~/.openclaw/skills/echo-perplexity-ultimate-async-researcher
```

Copy the provided `SKILL.md` into this new directory.

Reload your OpenClaw environment to register the new skill.

## ⚙️ Configuration

This skill requires a Perplexity API key to function. Expose it to your OpenClaw execution environment:

```bash
export PERPLEXITY_API_KEY="your_api_key_here"
```

You can generate an API key from the Perplexity API Platform.

## 🧠 How It Works (The Agent Workflow)

When a user triggers a research prompt, for example, "Research the latest advancements in solid-state batteries in 2026", the Agent follows a strict 3-stage pipeline:

1. **Query Formulation:** Break the prompt down into 3 to 5 hyper-specific search queries.
2. **Execution:** Execute the built-in asynchronous Python script, replacing placeholder queries with its own, then read the raw JSON output from stdout.
3. **Synthesis & Citation:** Synthesize the JSON into a cohesive Markdown report with inline hyperlink citations.

## ⚠️ Notes on Runtime

- If OpenClaw is running in a sandboxed container, `pip install` requires network egress and a writable environment. Prefer pre-installing dependencies in the sandbox image if installs fail.
- If you want OpenClaw to hide this skill when the API key is missing, keep the `metadata.openclaw.requires.env` gate in `SKILL.md`.

## 📄 License

MIT License. Feel free to fork and modify!
