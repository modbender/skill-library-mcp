---
name: hide-my-email
description: Generate Apple Hide My Email addresses from the terminal and copy to clipboard.
version: "1.0.1"
homepage: https://github.com/manikal/hide-my-email
metadata:
  openclaw:
    emoji: "\U+1F4E7"
    os: ["macos"]
    requires:
      bins: ["hme"]
    install:
      - id: git
        kind: shell
        command: "git clone --depth=1 https://github.com/manikal/hide-my-email.git ~/.hme && chmod +x ~/.hme/hme && echo 'export PATH=\"$HOME/.hme/bin:$PATH\"' >> ~/.zshrc && echo 'Installed. Restart your shell, then run: hme \"Test\"'"
        label: "Install hme (git clone, recommended)"
      - id: curl
        kind: shell
        command: "curl -fsSL https://raw.githubusercontent.com/manikal/hide-my-email/v1.0.1/install.sh | sh"
        label: "Install hme (curl, pinned to v1.0.1)"
---

# Hide My Email CLI

Generate Apple iCloud+ "Hide My Email" addresses from the terminal. The generated address is automatically copied to your clipboard.

## Usage

```bash
hme <label> [note]
```

- **label** (required): A name for the address (e.g. the service you're signing up for)
- **note** (optional): A description or reminder for the address

## Examples

```bash
# Create an address labeled "Twitter"
hme "Twitter"

# Create an address with a note
hme "Shopping" "For online orders"
```

## Output

On success, prints the masked email and copies the full address to clipboard:

```
✓ abc****@icloud.com (copied to clipboard)
```

On failure, prints an error message to stderr and exits non-zero.

## Requirements

- macOS with an iCloud+ subscription
- System Settings accessibility permissions granted to your terminal app
