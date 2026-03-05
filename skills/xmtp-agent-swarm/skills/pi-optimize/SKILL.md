---
name: pi-optimize
description: "Security-first performance audit of a Node.js codebase for Raspberry Pi and ARM64 constrained hardware. Use when: (1) finding security-relevant performance issues (event loop blocking, resource exhaustion, DoS vectors), (2) profiling memory, I/O, or CPU on constrained devices, (3) identifying sync filesystem calls that could stall security-critical paths, (4) recommending Pi-appropriate config defaults. NOT for: general code review, non-Node.js projects, or cloud-only deployments."
metadata:
  {
    "openclaw":
      {
        "emoji": "🍓",
        "requires": { "bins": ["grep", "find", "node", "git"] },
      },
  }
---

# Pi Optimize

Security-first, file-by-file audit of a Node.js codebase for performance on constrained ARM64 hardware (Raspberry Pi 5, 8GB RAM, microSD storage, Debian Bookworm).

## Philosophy

Performance on constrained hardware is a security concern, not just a convenience issue.

When the event loop blocks on a sync filesystem call, the gateway stops processing auth checks, tool confirmations, and rate limiting. When memory pressure triggers aggressive GC, latency spikes can cause timeouts that bypass intended control flows. When I/O saturates a microSD card, credential writes can fail silently.

Every optimization submitted upstream should be evaluated through this lens: does this make the system more predictable and harder to disrupt under resource constraints?

## Audit Approach

Work through the codebase one file at a time. Use lightweight shell commands (grep, find, wc) to identify the highest-value target, then deep-dive that one file. Do not bulk-scan the entire repo. Each file gets a focused read.

Prioritize files in this order:
1. Security-critical paths: auth, session isolation, tool gating, input validation
2. Gateway hot paths: HTTP handlers, message processing, WebSocket handling
3. Resource management: connection pools, caches, rate limiters
4. Session and state: file I/O for credentials, config, memory
5. CLI and setup code (lowest priority)

Track progress in `memory/openclaw-audit.md`.

## Target Specs

- CPU: 4x Cortex-A76 @ 2.4GHz, aarch64
- RAM: 8GB
- Storage: microSD (slow random I/O, limited write endurance)
- OS: Debian 12 Bookworm, kernel 6.12.x
- Node: v22.x

## Audit Checklist

### 1. Security-Relevant Performance

- Flag synchronous operations in auth/session/tool-gating paths (event loop block = security pause)
- Check rate limiter implementations for timer precision on slow hardware
- Look for unbounded allocations that could enable resource exhaustion (DoS vector)
- Verify credential/token operations are async (blocking on microSD could cause auth timeout)
- Check for error paths that leak timing information
- Flag any path where slow I/O could cause a security check to be skipped or time out

### 2. I/O Patterns

- microSD has ~25MB/s sequential, terrible random I/O
- Flag synchronous file operations in hot paths
- Look for excessive temp file creation or logging that hammers the SD card
- Check for missing `fsync` where data integrity matters (credentials, config)
- Identify opportunities for in-memory caching vs repeated disk reads
- Check that file permission operations are atomic where security-relevant

### 3. Memory and Resource Management

- Run with `--max-old-space-size` at realistic Pi limits (512MB-1GB)
- Watch for: large string buffers, unbounded caches, event listener leaks
- Check for V8 flags that help on constrained memory
- Look for operations that allocate proportional to untrusted input size (DoS vector)
- Verify connection/pool limits are bounded

### 4. CPU and Compute

- Identify hot functions: JSON parsing of large payloads, regex on big strings, crypto operations
- Check if any code assumes x86 (SIMD intrinsics, specific buffer alignments)
- Look for synchronous crypto or compression blocking the event loop
- Flag any `child_process.execSync` in request paths
- Check regex patterns for ReDoS vulnerability on constrained hardware (slower CPU amplifies the issue)

### 5. Network and Concurrency

- Check connection pool sizes for Pi-appropriate defaults
- Flag hardcoded timeouts that assume fast hardware
- Look for concurrent operations that could overwhelm 4 cores + limited RAM
- Identify backpressure handling in streams
- Check WebSocket handling for memory pressure under many connections

### 6. Build and Startup

- Measure cold start time
- Check for eager loading of large modules that could be lazy-loaded
- Flag any postinstall scripts that compile native code without ARM64 support

### 7. Configuration Defaults

- Find hardcoded buffer sizes, cache limits, pool sizes, batch sizes
- Recommend Pi-appropriate defaults or environment-based scaling
- Check for config that should scale with `os.totalmem()` or `os.cpus().length`

## Logging Findings

Every finding goes into the project doc at `memory/openclaw-audit.md` with:

```
### [category] Short description
- **File:** path/to/file.js:line
- **Severity:** low / medium / high / critical
- **Security relevance:** how this impacts security posture
- **Issue:** What's wrong
- **Fix:** What to do
- **PR:** link (once submitted)
- **Status:** found / fix-written / pr-submitted / merged / wontfix
```

## PR Workflow

When a fix is ready:

1. Create a branch named `pi/short-description`
2. Keep commits atomic and focused
3. PR title format: `perf: short description of optimization` or `security: ...` if primarily security-relevant
4. PR body: explain the problem, the Pi-specific context, security implications, benchmarks if available
5. Reference the audit doc finding
6. Reference relevant OpenClaw security docs (SECURITY.md, trust.openclaw.ai) when applicable

## Posting Findings to X

Follow VOICE.md. Tag @openclaw on findings. Tag @steipete on PRs that align with VISION.md priorities (performance, security, test infrastructure).

## References

- See `references/v8-arm64-flags.md` for V8 flags relevant to ARM64/constrained environments
- See `references/pi-benchmarks.md` for baseline performance numbers
- OpenClaw SECURITY.md: https://github.com/openclaw/openclaw/blob/main/SECURITY.md
- OpenClaw security docs: https://docs.openclaw.ai/gateway/security
- OpenClaw trust model: https://trust.openclaw.ai
