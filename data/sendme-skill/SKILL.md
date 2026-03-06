---
name: sendme
description: >-
  Send and receive files peer-to-peer using the sendme protocol from iroh.computer.
  Use when the user wants to share files, transfer files between machines, send
  files to someone, or receive files using a sendme ticket. Supports files and
  folders of any size with resumable downloads, integrity verification, and
  direct peer-to-peer connections without servers.
metadata:
  openclaw:
    requires:
      anyBins: [sendme]
    install:
      - kind: brew
        formula: sendme
        bins: [sendme]
---

# Sendme

Peer-to-peer file transfer using [iroh](https://www.iroh.computer/sendme). No server uploads — files stream directly between machines via encrypted connections with automatic NAT traversal.


## Installation

If `sendme` is not installed:

```bash
brew install sendme
```

Alternatively, install via Cargo: `cargo install sendme`

## Sending Files

```bash
sendme send <path>
```

- Accepts a file or directory path
- Outputs a **ticket** — a long base32-encoded string the recipient needs
- The process stays running until interrupted with Ctrl+C — the sender must remain online for the recipient to download
- Present the ticket to the user and instruct them to share it with their recipient

Example:

```bash
sendme send ~/Documents/report.pdf
# Outputs: sendme receive blobaa...  (the ticket)
```

For directories, sendme bundles the entire folder recursively.

### Non-Interactive / Headless Environments

`sendme` requires a TTY — it enables raw terminal mode for interactive features. In non-interactive environments (scripts, Docker, CI, agents), it will fail with:

```
Failed to enable raw mode: No such device or address
```

**Use the Python PTY wrapper** to provide a PTY and extract the ticket programmatically. This uses `os.execvp()` to invoke `sendme` directly without shell interpretation, avoiding shell injection risks:

```python
import os, pty, select, signal, sys

def sendme_send(path):
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp("sendme", ["sendme", "send", path])
    output = b""
    ticket = None
    while True:
        ready, _, _ = select.select([fd], [], [], 0.5)
        if ready:
            try:
                chunk = os.read(fd, 4096)
                if not chunk:
                    break
                output += chunk
                for line in output.decode(errors="replace").split("\n"):
                    if "sendme receive blob" in line:
                        ticket = line.strip().replace("sendme receive ", "")
                        print(ticket)
                        sys.stdout.flush()
            except OSError:
                break
        elif ticket:
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                break
    try:
        os.kill(pid, signal.SIGTERM)
        os.waitpid(pid, 0)
    except (ProcessLookupError, ChildProcessError):
        pass
    return ticket
```

## Receiving Files

```bash
sendme receive <ticket>
```

- Downloads the file/folder to the current directory
- Uses temporary `.sendme-*` directories during download, then moves atomically
- Automatically verifies integrity via blake3 hashing
- Resumes interrupted downloads automatically

Example:

```bash
sendme receive blobaafy...
```

## Key Details

- **Connection**: Direct peer-to-peer with TLS encryption. Falls back to relay servers if direct connection fails.
- **Resumable**: Interrupted downloads continue from where they left off.
- **Integrity**: All data is blake3-verified during streaming.
- **Speed**: Saturates connections up to 4Gbps.
- **No size limit**: Works with files and folders of any size.
- **Sender must stay online**: The `sendme send` process must keep running until the recipient completes the download.
