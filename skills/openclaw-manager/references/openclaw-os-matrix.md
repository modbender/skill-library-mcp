# OpenClaw OS Matrix

Use this matrix to adapt commands and caveats for each platform.

| OS | Supported Path | Key Notes |
|---|---|---|
| macOS | local + hosted CLI workflows | Prefer Homebrew package installs where available; verify shell path exports. |
| Linux | local + hosted CLI workflows | Prefer distro package manager + systemd for daemonized local workflows. |
| Windows (WSL2) | local (inside WSL2) + hosted CLI workflows | Run OpenClaw tooling inside WSL2 Linux environment; avoid mixed host/WSL path assumptions. |

## Command Adaptation Guidance
1. Normalize path assumptions before writing state/config files.
2. Keep provider CLIs installed in the same environment where commands run.
3. For Windows users, require explicit confirmation that terminal is WSL2 before local install steps.

## OS-Specific Verification
- Confirm CLI binaries resolve (`which`/`command -v`) in active shell.
- Confirm state directory read/write behavior.
- Confirm restart behavior and local process persistence approach.

## Hard Stops
- Platform mismatch between declared OS and active execution environment.
- State path not writable in selected OS runtime.
- Required CLI missing and no secure install path chosen.
