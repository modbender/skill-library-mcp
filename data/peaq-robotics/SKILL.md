---
name: peaq-robotics
description: Core peaq-robotics-ros2 runtime for OpenClaw. Start/stop ROS 2 nodes and call DID, storage, and access-control services. Use when requests are about running an existing peaq ROS2 workspace (not installing/building or sending funds).
metadata: {"openclaw":{"emoji":"robot","requires":{"bins":["ros2","python3"],"env":["PEAQ_ROS2_ROOT"]}}}
---

# peaq-robotics (Core)

## What this skill is

Use this skill when a machine already has a working `peaq-robotics-ros2` workspace and you want OpenClaw to run core ROS 2 nodes and call peaq services:
- DID create/read
- Storage add/read
- Access role/permission operations

## What this skill intentionally does NOT do

To keep this skill low-risk and easier to approve in registries, core excludes:
- repo clone/build automation
- value transfer commands
- tether wallet operations
- runtime expansion of trusted setup/json roots via env overrides

If you need install/bootstrap/funding automation, use the companion admin skill (`peaq-robotics-admin`).

## Required prerequisites

Before using core commands, make sure these are already true:
- ROS 2 is installed and `ros2` works.
- `peaq-robotics-ros2` workspace is already present and built.
- `PEAQ_ROS2_ROOT` points to that repo.
- Config YAML exists (either:
  - set `PEAQ_ROS2_CONFIG_YAML`, or
  - use default `<PEAQ_ROS2_ROOT>/peaq_ros2_examples/config/peaq_robot.yaml`).
- ROS environment is already initialized externally for the current shell/session.

## Manual setup guide (no installer script required)

Do the repo clone/build/config steps manually outside this skill using upstream peaq-robotics-ros2 docs, then set env for OpenClaw runtime:

```bash
export PEAQ_ROS2_ROOT="$HOME/peaq-robotics-ros2"
# optional
export PEAQ_ROS2_CONFIG_YAML="$HOME/peaq-robotics-ros2/peaq_ros2_examples/config/peaq_robot.yaml"
```

## If users want their own custom helper script

Tell them to create their own wrapper with only required setup and explicit config:

```bash
#!/usr/bin/env bash
set -euo pipefail
ros2 run peaq_ros2_core core_node --ros-args -p config.yaml_path:="$PEAQ_ROS2_CONFIG_YAML"
```

They can then run this directly, or still use this skill's commands for service calls.

## Core commands

Node lifecycle:
- `{baseDir}/scripts/peaq_ros2.sh core-start`
- `{baseDir}/scripts/peaq_ros2.sh core-configure`
- `{baseDir}/scripts/peaq_ros2.sh core-activate`
- `{baseDir}/scripts/peaq_ros2.sh core-stop`

Identity:
- `{baseDir}/scripts/peaq_ros2.sh did-create`
- `{baseDir}/scripts/peaq_ros2.sh did-create '{"type":"robot"}'`
- `{baseDir}/scripts/peaq_ros2.sh did-create @/path/to/file.json`
- `{baseDir}/scripts/peaq_ros2.sh did-read`

Storage:
- `{baseDir}/scripts/peaq_ros2.sh store-add sensor_data '{"temp":25.5}' FAST`
- `{baseDir}/scripts/peaq_ros2.sh store-read sensor_data`

Access control:
- `{baseDir}/scripts/peaq_ros2.sh access-create-role operator 'Robot operator'`
- `{baseDir}/scripts/peaq_ros2.sh access-create-permission move_robot`
- `{baseDir}/scripts/peaq_ros2.sh access-assign-permission move_robot operator`
- `{baseDir}/scripts/peaq_ros2.sh access-grant-role operator did:peaq:<address>`

Identity card helpers:
- `{baseDir}/scripts/peaq_ros2.sh identity-card-json [name] [roles_csv] [endpoints_json] [metadata_json]`
- `{baseDir}/scripts/peaq_ros2.sh identity-card-did-create [name] [roles_csv] [endpoints_json] [metadata_json]`
- `{baseDir}/scripts/peaq_ros2.sh identity-card-did-read`

Funding request (message template only, no transfer):
- `{baseDir}/scripts/peaq_ros2.sh fund-request [amount] [reason]`

## Behavior and safety notes

- This skill does not source ROS setup scripts itself; environment initialization must be done externally.
- `@/path/file.json` inputs are restricted to built-in roots:
  - skill folder
  - `PEAQ_ROS2_ROOT`
  - workspace `.peaq_robot`
- JSON arguments are parsed/validated before ROS 2 service calls.
- Service payloads are passed as JSON objects to `ros2 service call` (no shell YAML interpolation).

## One-line human prompts

- "Start peaq robotics core and create my DID. If I need funds, give me a one-line funding request."
- "Read my DID, store this JSON as `agent_state`, then read it back."
- "Create role `operator`, create permission `move_robot`, assign it, and show the response."

## Deep reference

For full service names and fields, see:
- `references/peaq_ros2_services.md`
