---
name: bing-wallpaper
description: Use when users need to fetch the daily Bing wallpaper.
---

# Bing Wallpaper Skill

This skill helps AI agents fetch the daily Bing wallpaper from the 60s API, which provides the latest Bing homepage background image.

## When to Use This Skill

Use this skill when users:
- Ask for today's Bing wallpaper
- Request a beautiful daily background image

## How to Use

Execute the associated `scripts/wallpaper.sh` script to fetch the Bing wallpaper.

```bash
./scripts/wallpaper.sh [encoding]
```

### Options

- `--encoding, -e <format>`: Optional. Specifies the output response format. Valid options are `text`, `json`, `image`, and `markdown`. 

### Return Values

The script securely calls the 60s Bing wallpaper API and outputs the response to `stdout`. Depending on the `encoding` parameter, the response could be a JSON string, plain text, markdown, or binary image data.

### Usage Examples

```bash
# Get Bing wallpaper using default API encoding
./scripts/wallpaper.sh

# Get Bing wallpaper in JSON format
./scripts/wallpaper.sh --encoding json

# Get Bing wallpaper in plain text format (simplified usage)
./scripts/wallpaper.sh text

# Get Bing wallpaper in markdown format
./scripts/wallpaper.sh -e markdown

# Get Bing wallpaper as an image
./scripts/wallpaper.sh image
```

## Response Format

The return values differ based on the `encoding` parameter:

1. **Default & Recommended (`--encoding markdown`)**
   - **When to use:** By default for standard wallpaper inquiries.
   - **Why:** Returns a brief description of the wallpaper along with the image link in an easy-to-read markdown format.

2. **Just the Link (`--encoding text`)**
   - **When to use:** When the user only wants the image link.
   - **Why:** Returns exactly the raw image link and nothing else.

3. **Structured Data (`--encoding json`)**
   - **When to use:** When you need the wallpaper description and link in a structured JSON format.
   - **Why:** Useful for parsing the response to extract specific fields programmatically.

4. **Direct Image (`--encoding image`)**
   - **When to use:** When the user specifically requests the image file itself.
