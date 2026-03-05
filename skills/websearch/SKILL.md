# WebSearch (SearXNG)

Search the web using a local SearXNG instance.

## What this skill does
This skill performs a web search by executing a local `websearch` command,
which queries a self-hosted SearXNG instance and returns search results.

It is designed to give OpenClaw access to up-to-date information without
using paid search APIs.

## Inputs
- **query** (string, required)  
  The search query to look up on the web.

## Outputs
- **results** (string)  
  Raw results returned by SearXNG (JSON or text, depending on configuration).

## Requirements
- `/usr/local/bin/websearch` must exist and be executable.
- A running SearXNG instance accessible from the host.

## Security
This skill runs inside OpenClaw’s sandboxed exec environment.
No network access is granted beyond what the host allows.

## Example
Search for recent Linux kernel releases:
