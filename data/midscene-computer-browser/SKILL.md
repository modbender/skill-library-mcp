---
name: Browser Automation
description: |
  Vision-driven browser automation using Midscene. Operates entirely from screenshots — no DOM or accessibility labels required. Can interact with all visible elements on screen regardless of technology stack.

  Opens a new browser tab for each target URL via Puppeteer (headless Chrome).

  Use this skill when the user wants to:
  - Browse, navigate, or open web pages
  - Scrape, extract, or collect data from websites
  - Fill out forms, click buttons, or interact with web elements
  - Verify, validate, or test frontend UI behavior
  - Take screenshots of web pages
  - Automate multi-step web workflows
  - Run browser automation or check website content


  Powered by Midscene.js (https://midscenejs.com)
allowed-tools:
  - Bash
---

# Browser Automation

> **CRITICAL RULES — VIOLATIONS WILL BREAK THE WORKFLOW:**
>
> 1. **Never run midscene commands in the background.** Each command must run synchronously so you can read its output (especially screenshots) before deciding the next action. Background execution breaks the screenshot-analyze-act loop.
> 2. **Run only one midscene command at a time.** Wait for the previous command to finish, read the screenshot, then decide the next action. Never chain multiple commands together.
> 3. **Allow enough time for each command to complete.** Midscene commands involve AI inference and screen interaction, which can take longer than typical shell commands. A typical command needs about 1 minute; complex `act` commands may need even longer.

Automate web browsing using `npx @midscene/web@1`. Launches a headless Chrome via Puppeteer that **persists across CLI calls** — no session loss between commands. Each CLI command maps directly to an MCP tool — you (the AI agent) act as the brain, deciding which actions to take based on screenshots.

## When to Use

Use this skill when:
- The user wants to browse or navigate to a specific URL
- You need to scrape, extract, or collect data from websites
- You want to verify or test frontend UI behavior
- The user wants screenshots of web pages

If you need to preserve login sessions or work with the user's existing browser tabs, use the **Chrome Bridge Automation** skill instead.

## Prerequisites

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
npx @midscene/web@1 connect --url https://example.com
```

### Take Screenshot

```bash
npx @midscene/web@1 take_screenshot
```

After taking a screenshot, read the saved image file to understand the current page state before deciding the next action.

### Perform Action

Use `act` to interact with the page and get the result. It autonomously handles all UI interactions internally — clicking, typing, scrolling, hovering, waiting, and navigating — so you should give it complex, high-level tasks as a whole rather than breaking them into small steps. Describe **what you want to do and the desired effect** in natural language:

```bash
# specific instructions
npx @midscene/web@1 act --prompt "click the Login button and fill in the email field with 'user@example.com'"
npx @midscene/web@1 act --prompt "scroll down and click the Submit button"

# or target-driven instructions
npx @midscene/web@1 act --prompt "click the country dropdown and select Japan"
```

### Disconnect

Disconnect from the page but keep the browser running:

```bash
npx @midscene/web@1 disconnect
```

### Close Browser

Close the browser completely when finished:

```bash
npx @midscene/web@1 close
```

## Workflow Pattern

The browser **persists across CLI calls** via a background Chrome process. Follow this pattern:

1. **Connect** to a URL to open a new tab
2. **Take screenshot** to see the current state, make sure the page is loaded.
3. **Execute action** using `act` to perform the desired action or target-driven instructions.
4. **Close** the browser when done (or **disconnect** to keep it for later)

## Best Practices

1. **Always connect first**: Navigate to the target URL with `connect --url` before any interaction.
2. **Be specific about UI elements**: Instead of `"the button"`, say `"the blue Submit button in the contact form"`.
3. **Use natural language**: Describe what you see on the page, not CSS selectors. Say `"the red Buy Now button"` instead of `"#buy-btn"`.
4. **Handle loading states**: After navigation or actions that trigger page loads, take a screenshot to verify the page has loaded.
5. **Close when done**: Use `close` to shut down the browser and free resources.
6. **Never run in background**: Every midscene command must run synchronously — background execution breaks the screenshot-analyze-act loop.
7. **Batch related operations into a single `act` command**: When performing consecutive operations within the same page, combine them into one `act` prompt instead of splitting them into separate commands. For example, "fill in the email and password fields, then click the Login button" should be a single `act` call, not three. This reduces round-trips, avoids unnecessary screenshot-analyze cycles, and is significantly faster.
8. **Summarize report files after completion**: After finishing the automation task, collect and summarize all report files (screenshots, logs, output files, etc.) for the user. Present a clear summary of what was accomplished, what files were generated, and where they are located, making it easy for the user to review the results.

**Example — Dropdown selection:**

```bash
npx @midscene/web@1 act --prompt "click the country dropdown and select Japan"
npx @midscene/web@1 take_screenshot
```

**Example — Form interaction:**

```bash
npx @midscene/web@1 act --prompt "fill in the email field with 'user@example.com' and the password field with 'pass123', then click the Log In button"
npx @midscene/web@1 take_screenshot
```

## Troubleshooting

### Connection Failures
- Ensure Chrome/Chromium is installed on the system (Puppeteer downloads its own by default).
- Check that no firewall blocks local Chrome debugging ports.

### API Key Errors
- Check `.env` file contains `MIDSCENE_MODEL_API_KEY=<your-key>`.
- Verify the key is valid for the configured model provider.

### Timeouts
- Web pages may take time to load. After connecting, take a screenshot to verify readiness before interacting.
- For slow pages, wait briefly between steps.

### Screenshots Not Displaying
- The screenshot path is an absolute path to a local file. Use the Read tool to view it.