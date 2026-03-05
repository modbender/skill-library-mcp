# Wavelet World Model Skill for OpenClaw

This skill enables an OpenClaw agent to build a multi-resolution "world model" of an environment or system state using Discrete Wavelet Transforms (DWT).

## Features

- **Multi-resolution State Encoding**: Captures both slow trends and fast perturbations in the environment.
- **Dimensionality Reduction**: Compresses state history while preserving critical temporal-spatial transitions.
- **Predictive Foundation**: Provides a robust, denoised state representation that can be fed into downstream RL or predictive neural networks.

## Installation

### Local Install (Development)
If you have the OpenClaw CLI installed:
```bash
openclaw skill install ./wavelet-world-model-skill
```

## Usage

Once installed, you can ask OpenClaw:
> "Generate a wavelet world model from my current state data"
> "Run the wavelet-model skill"

## Publishing to ClawHub

To share this skill:

1.  **Login to ClawHub**:
    ```bash
    clawhub login
    ```

2.  **Publish the Skill**:
    Navigate to the skill directory and run:
    ```bash
    clawhub publish
    ```
