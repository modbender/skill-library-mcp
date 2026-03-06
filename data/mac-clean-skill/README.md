# Mac Cleanup Skill for OpenClaw

This skill allows your OpenClaw agent to perform system maintenance on your MacBook Pro.

## Features

- **Empty Trash**: Permanently deletes files in `~/.Trash`.
- **Clear Caches**: Removes files in `~/Library/Caches` older than 7 days.
- **Clean Downloads**: Deletes files in `~/Downloads` older than 30 days.

## Installation

Since this is a local skill, you need to point OpenClaw to this directory or publish it to ClawHub.

### Local Install (Development)
If you have the OpenClaw CLI installed:
```bash
openclaw skill install ./mac-cleanup-skill
```

## Usage

Once installed, you can ask OpenClaw:
> "Clean up my mac"
> "Run the cleanup skill"

By default, the script runs in **DRY RUN** mode to prevent accidental data loss. To actually delete files, you need to modify the command execution to pass the `--force` flag or run the script manually.

## Publishing to ClawHub

To share this skill with the community (or yourself on other devices):

1.  **Login to ClawHub**:
    ```bash
    clawhub login
    ```

2.  **Publish the Skill**:
    Navigate to the skill directory and run:
    ```bash
    clawhub publish
    ```

## Security Note

This skill deletes files. Review `scripts/cleanup.py` before running with `--force`.
