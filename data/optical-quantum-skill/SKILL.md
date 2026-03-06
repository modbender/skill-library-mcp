---
name: optical-quantum-kernel
description: Simulates a quantum kernel using optical fiber storage and linear optics.
author: tempguest
version: 0.1.0
license: MIT
---

# Optical Quantum Kernel Skill

This skill simulates a photonic quantum computer that uses optical fibers for storage and linear optics for computation.
It calculates the quantum kernel (similarity) between two data vectors by encoding them into optical phases, passing them through simulated fibers (with loss), and interfering them.

## Security Features
- **Resource Bounding**: Capped at 8 modes to prevent resource exhaustion.
- **Input Validation**: Strict checks on input vector dimensions and limits.
- **Physics-Based Constraints**: Includes attenuation and phase noise for realism.

## Commands

- `simulate`: Run the quantum kernel simulation on two input vectors.
