---
name: dakboard
description: Manage DAKboard screens, devices, and push custom display data.
author: Kristopher Clark
homepage: https://github.com/krisclarkdev/dakboard-skill
files: ["scripts/*"]
metadata:
  clawdbot:
    requires:
      env:
        - DAKBOARD_API_KEY
---

# DAKboard Skill

This skill provides a command-line interface to interact with the DAKboard API. It allows for comprehensive management of devices and screens, and enables pushing custom data for dynamic displays.

## Setup

Before using this skill, you must set your DAKboard API key as an environment variable.

```bash
export DAKBOARD_API_KEY="your_api_key_here"
```

The primary tool for this skill is the Python script located at `scripts/dakboard.py`.

## Available Commands

### 1. List Devices
Retrieves a list of all DAKboard devices (e.g., Raspberry Pis) linked to your account. This is useful for finding the `device_id` needed for other commands.

**Usage:**
```bash
python3 scripts/dakboard.py devices
```

### 2. List Screens
Retrieves a list of all available screen layouts (e.g., "Big Monthly", "Two Column"). This is used to find the `screen_id` needed to change a device's display.

**Usage:**
```bash
python3 scripts/dakboard.py screens
```

### 3. Update Device Screen
Changes the screen layout currently being displayed on a specific device.

**Usage:**
```bash
# Usage: update-device <device_id> <screen_id>
python3 scripts/dakboard.py update-device "dev_0c3e1405a961" "scr_709367acf3d4"
```

### 4. Push Metric
Pushes a single, named data point to a "DAKboard Metrics" block. This is ideal for displaying real-time data like sensor readings or statistics.

**Usage:**
```bash
# Usage: metric <key> <value>
python3 scripts/dakboard.py metric "indoor_temp" "72.5"
```

### 5. Push Fetch Data
Pushes a complete JSON object to a "Fetch" block on a screen. This is for displaying more complex, structured data.

**Usage:**
```bash
# Usage: fetch '<json_string>'
python3 scripts/dakboard.py fetch '{"tasks": ["Buy milk", "Walk the dog"], "priority": "high"}'
```

## Security & Privacy

### External Endpoints
| URL | Data Sent | Purpose |
| :--- | :--- | :--- |
| `https://dakboard.com/api/` | API Key, Device IDs, Screen IDs, Metrics Data | Used to interact with the DAKboard API to list and update devices, and push metrics/fetch data to custom blocks. |

### Data Handling
Only data provided as arguments to the skill commands (such as messages or metrics to be displayed on the DAKboard) and your `DAKBOARD_API_KEY` are sent to `dakboard.com`. No local files are read or written.

### Model Invocation Note
This skill is designed to be autonomously invoked by the OpenClaw agent when requested by the user. You can opt-out of autonomous invocation by disabling this skill.

### Trust Statement
By using this skill, data sent is limited to the arguments provided and sent directly to `dakboard.com`. Only install this skill if you trust DAKboard with the information you choose to display.