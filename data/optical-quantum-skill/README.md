# Optical Quantum Kernel Simulation

This skill simulates a "Quantum Kernel Trick" using a physics-based model of an optical quantum computer.

## The Physics Model
1.  **Optical Fiber Storage**: The quantum state (photons) travels through optical fibers.
    -   **Loop**: Storage is simulated as a fiber loop.
    -   **Loss**: Attenuation ($0.2 dB/km$) reduces the signal amplitude.
    -   **Noise**: Random phase drift simulates thermal fluctuations in the fiber.
2.  **Linear Optics**: 
    -   **Encoding**: Data is mapped to the phase of optical modes.
    -   **Computation**: A 50:50 Beam Splitter interferes the modes.
3.  **Measurement**: Photodetectors measure the intensity at the output ports to estimate the kernel (similarity).

## Security Features
- **Bounded Resources**: The simulation acts as a "Sandbox", strictly creating only up to 8 optical modes/qubits. This prevents Denial of Service (DoS) via memory exhaustion.
- **Input Sanitization**: Verifies that inputs are valid numerical vectors before processing.

## Usage

Calculate the kernel (similarity) between two vectors:

```bash
python3 scripts/optical_kernel.py "0.5,1.2" "0.5,1.2"
# Expected: High kernel value (~1.0)
```

Orthogonal/Different vectors:
```bash
python3 scripts/optical_kernel.py "0.1,0.2" "0.9,0.8"
# Expected: Lower kernel value
```

## Publishing to ClawHub

To publish this skill:
```bash
clawhub publish
```
