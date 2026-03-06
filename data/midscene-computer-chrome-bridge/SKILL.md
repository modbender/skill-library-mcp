---
name: Chrome Bridge Automation
description: |
  Vision-driven browser automation using Midscene Bridge mode. Operates entirely from screenshots — no DOM or accessibility labels required. Can interact with all visible elements on screen regardless of technology stack.

  This mode connects to the user's desktop Chrome browser via the Midscene Chrome Extension, preserving cookies, sessions, and login state.

  Use this skill when the user wants to:
  - Browse, navigate, or open web pages in the user's own Chrome browser
  - Interact with pages that require login sessions, cookies, or existing browser state
  - Scrape, extract, or collect data from websites using the user's real browser
  - Fill out forms, click buttons, or interact with web elements
  - Verify, validate, or test frontend UI behavior
  - Take screenshots of web pages
  - Automate multi-step web workflows
  - Check website content or appearance

  Powered by Midscene.js (https://midscenejs.com)
allowed-tools:
  - Bash
---

# Chrome Bridge Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **Never run midscene commands in the background.** Each command must run synchronously so you can read its output (especially screenshots) before deciding the next action. Background execution breaks the screenshot-analyze-act loop.
> 2. **Run only one midscene command at a time.** Wait for the previous command to finish, read the screenshot, then decide the next action. Never chain multiple commands together.
> 3. **Allow enough time for each command to complete.** Midscene commands involve AI inference and screen interaction, which can take longer than typical shell commands. A typical command needs about 1 minute; complex `act` commands may need even longer.

Automate the user's real Chrome browser via the Midscene Chrome Extension (Bridge mode), preserving cookies, sessions, and login state. You (the AI agent) act as the brain, deciding which actions to take based on screenshots.

## Command Format

**CRITICAL — Every command MUST follow this EXACT format. Do NOT modify the command prefix.**

```
npx @midscene/web@1 --bridge <subcommand> [args]
```

- `--bridge` flag is **MANDATORY** here — it activates Bridge mode to connect to the user's desktop Chrome browser

## Prerequisites

The user has already prepared Chrome and the Midscene Extension. Do NOT check browser or extension status before connecting — just connect directly.

Midscene requires models with strong visual grounding capabilities. The following environment variables must be configured — either as system environment variables or in a `.env` file in the current working directory (Midscene loads `.env` automatically):

```bash
MIDSCENE_MODEL_API_KEY="your-api-key"
MIDSCENE_MODEL_NAME="model-name"
MIDSCENE_MODEL_BASE_URL="https://..."
MIDSCENE_MODEL_FAMILY="family-identifier"
```

Example: Gemini (Gemini-3-Flash)

```bash
MIDSCENE_MODEL_API_KEY="your-google-api-key"
MIDSCENE_MODEL_NAME="gemini-3-flash"
MIDSCENE_MODEL_BASE_URL="https://generativelanguage.googleapis.com/v1beta/openai/"
MIDSCENE_MODEL_FAMILY="gemini"
```

Example: Qwen3-VL

```bash
MIDSCENE_MODEL_API_KEY="your-openrouter-api-key"
MIDSCENE_MODEL_NAME="qwen/qwen3-vl-235b-a22b-instruct"
MIDSCENE_MODEL_BASE_URL="https://openrouter.ai/api/v1"
MIDSCENE_MODEL_FAMILY="qwen3-vl"
```

Example: Doubao Seed 1.6

```bash
MIDSCENE_MODEL_API_KEY="your-doubao-api-key"
MIDSCENE_MODEL_NAME="doubao-seed-1-6-250615"
MIDSCENE_MODEL_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"
MIDSCENE_MODEL_FAMILY="doubao-vision"
```

Commonly used models: Doubao Seed 1.6, Qwen3-VL, Zhipu GLM-4.6V, Gemini-3-Pro, Gemini-3-Flash.

If the model is not configured, ask the user to set it up. See [Model Configuration](https://midscenejs.com/model-common-config) for supported providers.

## Commands

### Connect to a Web Page

```bash
npx @midscene/web@1 --bridge connect --url https://example.com
```

### Take Screenshot

```bash
npx @midscene/web@1 --bridge take_screenshot
```

After taking a screenshot, read the saved image file to understand the current page state before deciding the next action.

### Perform Action

Use `act` to interact with the page and get the result. It autonomously handles all UI interactions internally — clicking, typing, scrolling, hovering, waiting, and navigating — so you should give it complex, high-level tasks as a whole rather than breaking them into small steps. Describe **what you want to do and the desired effect** in natural language:

```bash
# specific instructions
npx @midscene/web@1 --bridge act --prompt "click the Login button and fill in the email field with 'user@example.com'"
npx @midscene/web@1 --bridge act --prompt "scroll down and click the Submit button"

# or target-driven instructions
npx @midscene/web@1 --bridge act --prompt "click the country dropdown and select Japan"
```

### Disconnect

```bash
npx @midscene/web@1 --bridge disconnect
```

## Workflow Pattern

Since CLI commands are stateless between invocations, follow this pattern:

1. **Connect** to a URL to establish a session
2. **Take screenshot** to see the current state, make sure the page is loaded.
3. **Execute action** using `act` to perform the desired action or target-driven instructions.
4. **Disconnect** when done

## Best Practices

1. **Always connect first**: Navigate to the target URL with `connect --url` before any interaction.
2. **Be specific about UI elements**: Instead of `"the button"`, say `"the blue Submit button in the contact form"`.
3. **Use natural language**: Describe what you see on the page, not CSS selectors. Say `"the red Buy Now button"` instead of `"#buy-btn"`.
4. **Handle loading states**: After navigation or actions that trigger page loads, take a screenshot to verify the page has loaded.
5. **Disconnect when done**: Always disconnect to free resources.
6. **Never run in background**: Every midscene command must run synchronously — background execution breaks the screenshot-analyze-act loop.
7. **Batch related operations into a single `act` command**: When performing consecutive operations within the same page, combine them into one `act` prompt instead of splitting them into separate commands. For example, "fill in the email and password fields, then click the Login button" should be a single `act` call, not three. This reduces round-trips, avoids unnecessary screenshot-analyze cycles, and is significantly faster.
8. **Summarize report files after completion**: After finishing the automation task, collect and summarize all report files (screenshots, logs, output files, etc.) for the user. Present a clear summary of what was accomplished, what files were generated, and where they are located, making it easy for the user to review the results.

**Example — Dropdown selection:**

```bash
npx @midscene/web@1 --bridge act --prompt "click the country dropdown and select Japan"
npx @midscene/web@1 --bridge take_screenshot
```

**Example — Form interaction:**

```bash
npx @midscene/web@1 --bridge act --prompt "fill in the email field with 'user@example.com' and the password field with 'pass123', then click the Log In button"
npx @midscene/web@1 --bridge take_screenshot
```

## Troubleshooting

### Bridge Mode Connection Failures
- Ask user to check if Chrome is open with the Midscene Extension installed and enabled.
- The Midscene Extension can be installed from the Chrome Web Store: https://chromewebstore.google.com/detail/midscenejs/gbldofcpkknbggpkmbdaefngejllnief
- Check that the 'bridge mode' indicator in the extension shows "Listening" status.
- See the [Bridge Mode documentation](https://midscenejs.com/bridge-mode-by-chrome-extension.html).

### Timeouts
- Web pages may take time to load. After connecting, take a screenshot to verify readiness before interacting.
- For slow pages, wait briefly between steps.

### Screenshots Not Displaying
- The screenshot path is an absolute path to a local file. Use the Read tool to view it.