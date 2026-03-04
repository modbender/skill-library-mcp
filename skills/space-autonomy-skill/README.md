# Space Autonomy Quantum Skill

This skill simulates an autonomous agent for diverse space environments. It relies on **Optical Quantum Kernels** to classify terrain based on sensor data.

## Safety First
Space is unforgiving. This agent implements a **"Highest Safety"** protocol:
1.  **Failsafe Threshold**: If the quantum classifier's confidence is below `0.85`, the agent immediately triggers **SAFE MODE**.
2.  **Redundancy**: Every classification is computed 3 times and averaged to mitigate quantum/optical noise.
3.  **Default to Halt**: If a hazard is detected OR if the terrain is unknown, the agent stops.

## How it Works
The agent compares real-time sensor inputs against a "Knowledge Base" (Safe Ground, Rocks, Voids) using a simulated optical quantum computer.
- **High Kernel Value** -> High Similarity -> Confident Classification.
- **Low Kernel Value** -> Low Similarity -> Unknown Terrain -> Safe Mode.

## Usage

Simulate a sensor reading (vector of 3 values):

# Case 1: Clear, safe terrain (matches 'SAFE_FLAT')
```bash
python3 scripts/quantum_nav.py "0.1,0.12,0.1"
# Expected: Action: PROCEED
```

# Case 2: Hazardous Rock (matches 'HAZARD_ROCK')
```bash
python3 scripts/quantum_nav.py "0.8,0.9,0.7"
# Expected: Action: AVOID / HALT
```

# Case 3: Unknown/Ambiguous Signal
```bash
python3 scripts/quantum_nav.py "0.5,0.5,0.5"
# Expected: >>> TRIGGERING FAILSAFE: SAFE MODE <<<
```

## Publishing
```bash
clawhub publish
```
