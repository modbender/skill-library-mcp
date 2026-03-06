---
author: "@canbirlik"
dependencies:
  python:
  - playwright
description: A visual, human-like web browser for OpenClaw agents.Supports reading,screenshots, and visible mode.
emoji: 🌐
name: claw-browser
platforms:
- darwin
- linux
- win32
---

# 🌐 Claw Browser Skill

This skill gives the agent **"Eyes"** to browse the web using a real
Chromium browser.

Unlike simple HTTP requests, `claw-browser`:

-   Renders JavaScript
-   Handles dynamic content
-   Loads SPA applications
-   Takes real screenshots
-   Can run in visible (non-headless) mode

------------------------------------------------------------------------

# 🛠️ Installation & Setup (READ FIRST)

⚠️ **Before using this tool, the agent MUST set up the Python
environment and download browser binaries.**

If `venv` does not exist, run this setup command block automatically:

``` bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download Chromium binaries (CRITICAL STEP)
playwright install chromium
```

> ⚠️ The `playwright install chromium` step is **CRITICAL**.\
> Without it, the browser will NOT launch.

------------------------------------------------------------------------

# 🔧 Tools & Usage

## `browser.py`

### Arguments

  -----------------------------------------------------------------------
  Argument                            Description
  ----------------------------------- -----------------------------------
  `--url`                             The website to visit (**Required**)

  `--action`                          Action to perform: `read` or
                                      `screenshot`

  `--visible`                         (Optional) Runs the browser in
                                      visible mode (NOT headless). Use if
                                      the user wants to *see* the
                                      browser.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 🚀 Execution Examples

⚠️ Always activate the virtual environment first.

------------------------------------------------------------------------

## 1️⃣ Read a Page (Headless - Default)

``` bash
source venv/bin/activate && python browser.py --url "https://github.com/trending" --action read
```

------------------------------------------------------------------------

## 2️⃣ Take a Screenshot of a News Site

``` bash
source venv/bin/activate && python browser.py --url "https://news.ycombinator.com" --action screenshot
```

This saves:

    evidence.png

------------------------------------------------------------------------

## 3️⃣ Visible Mode (Shows Browser UI - Great for Demos)

``` bash
source venv/bin/activate && python browser.py --url "https://google.com" --action read --visible
```

This will launch a real Chromium window on screen.

------------------------------------------------------------------------

## 4️⃣ Visible Mode (WSL / Linux Fix) ⭐️

**Use this if you get "Missing X server" or "Display not found" errors:**

```bash
export DISPLAY=:0 && source venv/bin/activate && python browser.py --url "[https://google.com](https://google.com)" --action read --visible
```
This sets the `DISPLAY` variable so the browser can open on your screen.

------------------------------------------------------------------------

# 🧠 When Should the Agent Use This Skill?

Use `claw-browser` when:

-   The page requires JavaScript rendering
-   The site is dynamic (React, Vue, Angular, etc.)
-   Screenshots are required
-   The user explicitly asks to "open" or "see" a website
-   Traditional HTTP requests fail

------------------------------------------------------------------------

# ⚡ Summary

`claw-browser` transforms your OpenClaw agent from a simple API caller
into a **real browser-powered assistant** with visual capabilities.

It enables:

-   Dynamic page interaction
-   Visual verification
-   Demo-ready browsing
-   Real-world automation

------------------------------------------------------------------------

Made with ❤️ by @canbirlik
