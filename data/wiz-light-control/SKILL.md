---
name: wiz-light-control
description: Controls Wiz smart bulbs (turn on/off, RGB colors, disco mode) via local WiFi.
author: "@canbirlik"
emoji: "💡"
platforms:
  - darwin
  - linux
  - win32
dependencies:
  python:
    - pywizlight
---

# Wiz Light Control Skill

This skill allows the agent to control physical Wiz smart lights on the local network. 

⚠️ **IMPORTANT CONFIGURATION:**
The IP address `192.168.1.109` used in examples is a placeholder. You **MUST** find the actual Local IP address of the Wiz Bulb on the network before running commands.

## 🛠️ Installation & Setup (READ FIRST)

**Before running the script for the first time, you MUST set up the Python environment.**
The agent should verify if `venv` exists. If not, run this setup command block automatically:

```bash
# 1. Create Virtual Environment and Install Dependencies
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```
## Tools & Usage

### `wiz.py`

The main script to interact with the light.

**Arguments:**
- `--ip`: The IP address of the bulb (Required).
- `--action`: The command to execute. Options: `on`, `off`, `color`, `disco`.
- `--r`, `--g`, `--b`: Red, Green, Blue values (0-255) (Used for `color` action).
- `--duration`: Duration in seconds (Used for `disco` action).

**Example Prompts:**
- "Turn on the disco mode in my room for 30 seconds."
- "Turn off the light."
- "Change the light color to red."

**Execution Examples:**

```bash
# 1. Turn on Disco Mode (Check IP first!)
python wiz.py --ip 192.168.1.109 --action disco --duration 60

# 2. Turn OFF
python wiz.py --ip 192.168.1.109 --action off

# 3. Turn ON
python wiz.py --ip 192.168.1.109 --action on

# 4. Set specific color (e.g., Red)
python wiz.py --ip 192.168.1.109 --action color --r 255 --g 0 --b 0