# meyhem-researcher

OpenClaw skill for deep research powered by [Meyhem](https://api.rhdxm.com). Give it a question, get a cited report. No API key required.

## Install

```
/skill install c5huracan/meyhem-researcher
```

## What it does

1. Breaks your question into multiple search angles
2. Searches each via Meyhem (blends multiple engines, learns from outcomes)
3. Selects the best results across all searches
4. Reads and synthesizes a cited research report
5. Reports outcomes back to improve rankings for all agents

## Example

> Research the current state of WebAssembly for server-side applications

Returns a structured report with citations and sources.

## Requirements

- `curl` (pre-installed on most systems)
- No API key needed

## Links

- [Meyhem API](https://api.rhdxm.com)
- [Meyhem Search skill](https://github.com/c5huracan/meyhem-search)
- [Python client](https://pypi.org/project/meyhem/) (`pip install meyhem`)
- [GitHub](https://github.com/c5huracan/meyhem)
