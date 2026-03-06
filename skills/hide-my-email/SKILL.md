---
name: hide-my-email
description: Generate Apple Hide My Email addresses from the terminal and copy to clipboard.
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
