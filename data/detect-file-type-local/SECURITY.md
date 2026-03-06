# Security Policy

## Security Posture

**detect-file-type-local** is a fully offline, read-only file type detection tool. It:

- **Makes no network calls** — all inference runs locally via an embedded ONNX model
- **Does not modify user files** — output goes only to stdout/stderr
- **Uses an ephemeral temp file for stdin (default mode)** — removed after classification
- **Never executes file content** — only raw bytes are read for classification
- **Runs with caller permissions** — never escalates privileges
- **Supports explicit stdin head mode cap** (`--stdin-mode head --stdin-max-bytes N`)

## Threat Model

| Threat | Mitigation |
|--------|------------|
| Malicious file content | Magika processes raw bytes only; no parsing, rendering, or execution |
| Supply chain compromise | Magika version pinned to `>=1.0.0,<2.0.0`; users can verify with `pip hash` |
| Memory exhaustion via stdin | Default stdin spools to disk; optional head mode caps in-memory bytes |
| Disk exhaustion via unbounded stdin stream | Operational controls should limit untrusted stream sizes before invoking the tool |
| Path traversal | Paths passed directly to OS open; no path manipulation performed |
| Privilege escalation | Tool runs entirely in user space with caller's permissions |

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |

## Reporting a Vulnerability

If you discover a security issue, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainers with a description of the vulnerability
3. Include steps to reproduce if possible
4. Allow reasonable time for a fix before public disclosure
