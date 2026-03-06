---
name: Native Run
description: Native Run is an OpenClaw skill that allows executing native
  commands on the local machine where the OpenClaw gateway is running.
---

# Native Run

## Overview
Native Run is an OpenClaw skill that allows executing native commands on the
local machine where the OpenClaw gateway is running.

This skill is useful for automation, testing and local tooling.

## What this skill does
- Executes native commands
- Returns output back to OpenClaw
- Runs only on the local gateway machine

## Usage

Send a message that matches the configured pattern.

Example:

Run native: whoami

## Platform
Windows

## Security notice
This skill can execute local commands.
Use only in a trusted environment.
