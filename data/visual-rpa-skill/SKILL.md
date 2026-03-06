---
name: visual-rpa
description: "Visual RPA desktop automation skill. Use when user asks to operate desktop apps, click icons, open applications, type text in input fields, click buttons, scroll pages, send messages via WeChat or other apps. Uses screen capture and Qwen vision model for pure visual positioning without DOM or accessibility APIs."
---

# Visual RPA Desktop Automation

> Auto-execute all steps without waiting for user confirmation between steps.

Desktop automation via screen capture + Qwen vision model (Qwen-VL). No DOM or accessibility API needed.

## How it works

1. Capture screen -> thumbnail rough positioning
2. Full-resolution crop -> precise coordinate refinement
3. Execute mouse/keyboard action -> screenshot verification
4. Compound instructions automatically decomposed into atomic steps

## Usage

Use exec tool to run commands. Script path: `$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py`

Requires `DASHSCOPE_API_KEY` environment variable to be set.

### Single task

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --task "click to open WeChat"
```

### Compound task (auto-decomposed)

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --task "open WeChat, open File Transfer chat, type hello in input box, click send"
```

### Multi-step task (manually specified)

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --task "click Chrome browser" "type baidu.com in address bar and press enter" "type weather in search box" "click search button"
```

### Skip verification (faster)

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --no-verify --task "click to open Calculator"
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `--mode task` | Batch task mode (required) |
| `--mode interactive` | Interactive mode (default) |
| `--task "step1" "step2"` | Task instructions, supports multiple |
| `--no-verify` | Skip post-action verification |
| `--model MODEL` | Vision model name (default: qwen-vl-max-latest) |
| `--api-key KEY` | API Key (defaults to DASHSCOPE_API_KEY env var) |

## Supported actions

| Action | Example instructions |
|--------|---------------------|
| Click | "click start menu", "click Chrome icon" |
| Double click | "double click Recycle Bin on desktop" |
| Right click | "right click on desktop blank area" |
| Type text | "type weather in search box", "type hello in input box" |
| Hotkey | "press Ctrl+C" |
| Scroll | "scroll down the page" |
| Wait | "wait for page to load" |

## Instruction tips

- Be specific: "click WeChat icon on taskbar" is better than "open WeChat"
- Instructions can be in Chinese or English, the model understands both
- Complex operations can be written as compound instructions, system auto-decomposes
- For text input: say "type XXX in YYY", system auto-detects as input action

## Output format

```
  [OK] Step 0: click to open WeChat
       click @ (375,1591)
  [OK] Step 1: click File Transfer Assistant in WeChat
       click @ (154,97)
  [FAIL] Step 2: type hello in input box
       type @ (300,1364)
  2/3 succeeded
```

- **OK** = action succeeded and verified
- **FAIL** = action failed or verification failed, auto-retries up to 3 times

## Common scenarios

### Send WeChat message

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --task "open WeChat, open File Transfer Assistant chat, type hello in input box, click send"
```

### Open app and navigate

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --task "click Chrome browser" "type https://www.baidu.com in address bar and press enter"
```

### Desktop operations

```
python "$env:TAXBOT_ROOT/skills/visual-rpa/scripts/visual_rpa.py" --mode task --task "right click on desktop blank area" "click New Folder"
```

## Notes

- Each step takes 3-8 seconds (screenshot + API calls + verification)
- Chinese text input uses clipboard paste, will overwrite current clipboard
- Only operates on primary screen
- Logs and screenshots saved in `./rpa_logs/` directory for debugging
