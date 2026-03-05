# Security Manifest — solid-agent-storage

## Network Access

- **Default target**: `https://crawlout.io` (Interition's hosted Solid server)
- **Configurable**: The Skill contacts whatever server is set in `SOLID_SERVER_URL`. If you point it at a remote server, credentials and tokens will be exchanged with that server. **Only use a server you control and trust.**
- **No other network calls**: The Skill does not contact analytics endpoints, third-party APIs, or any server other than the configured Solid server
- **No telemetry**: Nothing is reported back to Interition or any other party

## File System Scope

- **Credentials**: `~/.interition/agents/{name}/credentials.enc` — encrypted agent credentials
- **No other files**: The Skill does not read or write files outside `~/.interition/`

## Credentials Handling

- **Encrypted at rest**: AES-256-GCM encryption with PBKDF2 key derivation (100,000 iterations, SHA-256, random 32-byte salt per file)
- **Passphrase-protected**: Requires `INTERITION_PASSPHRASE` environment variable
- **File permissions**: Credentials files are set to `0600` (owner read/write only) as defence in depth
- **Never logged**: Credentials, tokens, and passphrases are never written to stdout or log files
- **Session-only key**: The decryption key exists only in process memory for the duration of a single command

## Encryption Details

| Parameter | Value |
|-----------|-------|
| Algorithm | AES-256-GCM |
| Key derivation | PBKDF2 |
| PBKDF2 iterations | 100,000 |
| PBKDF2 hash | SHA-256 |
| Salt length | 32 bytes (random per file) |
| IV length | 16 bytes (random per encryption) |
| Auth tag | 16 bytes (GCM authentication tag) |

## Process Execution

- **Only spawns**: `node` (to run compiled TypeScript CLI commands)
- **No shell expansion**: Shell scripts use `set -euo pipefail` and pass arguments safely via `"$@"`
- **No eval or dynamic code**: No `eval()`, `Function()`, or dynamic `import()` in any code path

## Dependencies

- **Zero runtime dependencies**: Uses only Node.js built-in modules (`crypto`, `fs`, `path`, `os`)
- **Build-time only**: TypeScript compiler and Vitest (test framework) are devDependencies
