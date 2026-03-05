# Security Policy

## Supported Versions

This project contains no background services or runtime daemons.
It only provides OpenClaw skill scripts.

## Reporting a Vulnerability

If you discover a security issue, please open an issue.

## Security Design

- No dynamic code execution
- No subprocess spawning
- No shell injection
- No remote code download
- No hidden processes
- No data persistence

This project acts as a thin wrapper around 12306 MCP interface.