---
name: clawsay
description: Display a message in a speech bubble spoken by an ASCII lobster.
license: MIT
---

# Clawsay

Display a message in a speech bubble with an ASCII art lobster, like `cowsay` but with a lobster.

## Usage

When the user wants to display a message with the lobster, run the script using `uv`. Ensure `cd` to the script directory:

```
cd scripts && uv run clawsay.py <message>
```

The lobster will be colored red and the message will appear in a speech bubble above it.

## Example

```
uv run python scripts/clawsay.py "Hello from the deep!"
```
