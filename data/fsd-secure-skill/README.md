# FSD Secure Skill (Camera-Only)

This skill simulates a "Highest Safety" autonomous driving agent that relies solely on visual data from cameras.

## Safety Architecture
1.  **Dual-Pass Verification**: Every frame is analyzed by two independent systems:
    -   **Pass 1**: Deep Neural Network (simulated) for high-level object detection.
    -   **Pass 2**: Heuristic/Classical CV (simulated) for low-level edge/obstacle verification.
    -   **Requirement**: Both must verify a clear path.
2.  **Temporal Consistency**: The agent will **never** accelerate unless the path has been verified clear for **3 consecutive frames**. This prevents "flickering" false positives.
3.  **Strict Confidence**: Neural network confidence must exceed **99%**.

## Usage

Run the simulation:
```bash
python3 scripts/fsd_agent.py
```

The output will show the frame-by-frame analysis and the "Emergency Stop" triggers if any safety check fails.

## Publishing
```bash
clawhub publish
```
