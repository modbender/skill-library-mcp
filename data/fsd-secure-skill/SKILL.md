---
name: fsd-secure
description: Full Self-Driving agent with highest safety standards (Camera-Only, Redundant Checks).
author: tempguest
version: 0.1.0
license: MIT
---

# FSD Secure Skill

This skill implements a **Camera-Only Full Self-Driving** agent designed for maximum safety.
It runs in a simulated environment and uses **Dual-Pass Analysis** to verify clear paths.

## Safety Features
- **Dual-Pass Verification**: Two independent algorithms must agree the path is clear.
- **Temporal Consistency**: Requires 3 consecutive safe frames before acceleration.
- **Fail-Safe**: Any uncertainty triggers an immediate Emergency Stop.

## Commands

- `drive`: Start the autonomous driving simulation.
