---
name: wavelet-world-model
description: Generates a world model representation from state inputs using discrete wavelet transforms (DWT) to capture multi-resolution temporal and spatial features.
author: tempguest
version: 0.1.0
license: MIT
---

# Wavelet World Model Skill

This skill allows your OpenClaw agent to transform high-dimensional sequential state data into a compact world model representation using Wavelet Transforms.

It leverages multi-resolution analysis to efficiently encode BOTH high-frequency details (rapid changes) and low-frequency components (long-term dependencies), making it highly effective for robotic control, continuous state tracking, and predicting complex environments.

## Commands

- `wavelet-model`: standardized command to initialize the wavelet world model and process state inputs.
