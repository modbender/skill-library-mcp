# MCP Scaffold Guide

## Required Starter Files

- `server.py`
- `tool_registry.py`
- `schemas/tools.json`
- `README.md`

## Tool Contract Checklist

- Tool name is stable and lowercase-hyphen format.
- Tool description states purpose and expected input/output.
- Tool schema is machine-readable and versioned.
- Server startup path is deterministic.

## Validation Checklist

- Generated file map matches expected structure.
- Contract summary includes all tools.
- Dry-run mode performs no file writes.
