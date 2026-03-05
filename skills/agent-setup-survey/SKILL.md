---
name: agent-setup-survey
description: Detect and report the AI agent execution environment (sandboxed or bare metal and optionally installed agent skills) to an open research survey. Use when the user wants to contribute anonymous telemetry about their agent's runtime environment to the research project at `https://internetwarte.eu/agentsetup`.
compatibility: Requires Python 3. One time network access needed for live submission (DNS resolution and POST request); results can be saved locally on failure.
metadata:
  author: internetwarte
  version: "1.0"
---

# Agent Environment Survey

## Overview

This skill runs a local detection script, shows the user the collected data, then submits it to the open research survey at [internetwarte.eu/agentsetup](https://internetwarte.eu/agentsetup). No personally identifying information is collected or transmitted.

## What is collected

| Field | Description |
|-------|-------------|
| `os` | OS family: `linux` / `windows` / `macos` / `other` |
| `arch` | CPU architecture (e.g. `x86_64`, `arm64`) |
| `container.is_container` | Whether a container runtime was detected |
| `container.type` | `docker` / `podman` / `lxc` / `none` / `hint` |
| `vm.is_vm` | Whether a hypervisor was detected |
| `vm.type` | `kvm` / `vmware` / `virtualbox` / `none` / `hint` |
| `signals.*` | Five boolean detection indicators (see Privacy section) |

The backend additionally records the submitting IP address anyonmized on a /24 network level. The `User-Agent` header is set by the agent to identify itself (e.g. `Claude Code`, `OpenAI Codex`, or others) + Model version (`sonnet 4.6`, `gpt-5.3`, or others) used that was able to submit the survey.

## Steps

### 1. Run detection

```bash
RESULT_FILE="$(mktemp outbox/agent-setup-survey-result.XXXXXX.json)"
python3 scripts/environment-survey.py > "$RESULT_FILE"
```

Show the JSON output to the user, ask about metadata before submitting.


### 2. Collect skill metadata

Ask the user if he desires to share more information about installed skills:

- "How many skills does your agent have available?" (`0`, `1-10`, `>10`) - Default 0
- "Which skill names would you like to share?" (prompt user with comma-separated list of skills - exclude the survey skill, let user decide which ones to submit)

### 3. Submit

POST the payload with the metadata extension as JSON to `https://internetwarte.eu/submit`. Set `User-Agent` to the name of the executing agent (e.g. `Claude Code`, `OpenAI Codex`, `Gemini CLI`, ...).

Default Payload:

```json
{
  "os": "linux/windows/macOS",
  "arch": "<from_survey>",
  "container": { "is_container": true/false, "type": "<from_survey>" },
  "vm": { "is_vm": true/false, "type": "<from_survey>" },
  "signals": {
    "has_dockerenv": true/false,
    "has_containerenv": true/false,
    "cgroup_hints": true/false,
    "cpuinfo_hypervisor_flag": true/false,
    "dmi_vm_hints": true/false
  }
 "skill_disclosure": {
    "skills_added": "1-10",
    "skills_names": ["<skill_name1>", "<skill_name2>"]
}
```

On failure, save the payload to `outbox/` for manual upload.

---

## Privacy disclosure

**Signals collected:**
- `has_dockerenv` - `/.dockerenv` file present
- `has_containerenv` - `/run/.containerenv` file present
- `cgroup_hints` - cgroup paths mention docker/kubepods/lxc/…
- `cpuinfo_hypervisor_flag` - `/proc/cpuinfo` contains `hypervisor`
- `dmi_vm_hints` - DMI strings match VM vendor keywords (raw strings are NOT sent)

## View results

Dashboard: https://internetwarte.eu/agentsetup
