---
name: dockerfile-optimizer
description: Analyze Dockerfiles for size, build speed, and security — generate
  optimized versions.
---


# Dockerfile Optimizer

Analyze and optimize Dockerfiles for smaller images, faster builds, and better security.

## Instructions

1. **Read the Dockerfile**: Accept file path or pasted content. Parse all stages.

2. **Check best practices and flag issues**:

   | Check | Issue | Fix |
   |-------|-------|-----|
   | Base image | Uses `:latest` tag | Pin specific version: `node:20-alpine` |
   | Layer count | Multiple separate `RUN` commands | Combine with `&&` |
   | Cache order | Frequently-changing files copied early | Copy dependency files first, then source |
   | User | Runs as root | Add `USER node` or `USER appuser` |
   | COPY vs ADD | Uses `ADD` for plain files | Use `COPY` (ADD only for tar extraction) |
   | Multi-stage | Single stage with build tools in final image | Use multi-stage build |
   | Cleanup | Package cache left in image | Add `rm -rf /var/lib/apt/lists/*` in same RUN |
   | .dockerignore | Missing or incomplete | Generate one |
   | Secrets | Hardcoded tokens/passwords | Use build args or secrets mount |

3. **Size optimization reference**:
   | Base Image | Size | Alternative | Size |
   |-----------|------|-------------|------|
   | `node:20` | ~1 GB | `node:20-alpine` | ~130 MB |
   | `python:3.12` | ~1 GB | `python:3.12-slim` | ~150 MB |
   | `ubuntu:22.04` | ~77 MB | `debian:12-slim` | ~52 MB |
   | Any | varies | `gcr.io/distroless/*` | minimal |

4. **Generate optimized Dockerfile**: Output improved version with comments explaining each change.

5. **Estimate savings**: Report approximate layer reduction and size improvement.

## Security Checks

- 🔴 Hardcoded secrets or ENV with credentials
- 🔴 Running as root without USER instruction
- 🟡 Unnecessary EXPOSE ports
- 🟡 Writable filesystem (consider `--read-only` at runtime)
- 🟡 No HEALTHCHECK instruction

## Edge Cases

- **Multi-stage builds**: Analyze each stage independently
- **Build args**: Ensure `ARG` values don't leak secrets into image layers
- **Platform-specific**: Note if Alpine may cause issues (musl vs glibc)

## Requirements

- No dependencies — static analysis of Dockerfile text
- No API keys needed
