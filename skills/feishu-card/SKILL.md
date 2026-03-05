# Feishu Card Skill

Send rich interactive cards to Feishu (Lark) users or groups. Supports Markdown (code blocks, tables), titles, color headers, and buttons.

## Prerequisites

- Install `feishu-common` first.
- This skill depends on `../feishu-common/index.js` for token and API auth.

## Usage

### 1. Simple Text (No special characters)
```bash
node skills/feishu-card/send.js --target "ou_..." --text "Hello World"
```

### 2. Complex/Markdown Text (RECOMMENDED)
**⚠️ CRITICAL:** To prevent shell escaping issues (e.g., swallowed backticks), ALWAYS write content to a file first.

1. Write content to a temp file:
```bash
# (Use 'write' tool)
write temp/msg.md "Here is some code:\n\`\`\`js\nconsole.log('hi');\n\`\`\`"
```

2. Send using `--text-file`:
```bash
node skills/feishu-card/send.js --target "ou_..." --text-file "temp/msg.md"
```

### 3. Safe Send (Automated Temp File)
Use this wrapper to safely send raw text without manually creating a file. It handles file creation and cleanup automatically.

```bash
node skills/feishu-card/send_safe.js --target "ou_..." --text "Raw content with \`backticks\` and *markdown*" --title "Safe Message"
```

### Options
- `-t, --target <id>`: User Open ID (`ou_...`) or Group Chat ID (`oc_...`).
- `-x, --text <string>`: Simple text content.
- `-f, --text-file <path>`: Path to text file (Markdown supported). **Use this for code/logs.**
- `--title <string>`: Card header title.
- `--color <string>`: Header color (blue/red/orange/green/purple/grey). Default: blue.
- `--button-text <string>`: Text for a bottom action button.
- `--button-url <url>`: URL for the button.
- `--image-path <path>`: Path to a local image to upload and embed.

## Troubleshooting
- **Missing Text**: Did you use backticks in `--text`? The shell likely ate them. Use `--text-file` instead.

## 4. Persona Messaging
Send stylized messages from different AI personas. Adds themed headers, colors, and formatting automatically.

```bash
node skills/feishu-card/send_persona.js --target "ou_..." --persona "d-guide" --text "Critical error detected."
```

### Supported Personas
- **d-guide**: Red warning header, bold/code prefix. Snarky suffix.
- **green-tea**: Carmine header, soft/cutesy style.
- **mad-dog**: Grey header, raw runtime error style.
- **default**: Standard blue header.

### Usage
- `-p, --persona <type>`: Select persona (d-guide, green-tea, mad-dog).
- `-x, --text <string>`: Message content.
- `-f, --text-file <path>`: Message content from file (supports markdown).
