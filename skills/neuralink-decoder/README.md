# Neuralink Decoder Skill

This skill demonstrates a **Brain-Computer Interface (BCI)**.
It simulates neural activity from the Motor Cortex and decodes it to control a virtual cursor.

## How it Works
1.  **Neural Simulation**: Uses a "Cosine Tuning" model to generate spike counts for 64 simulated neurons based on a movement intention (e.g., "Move Right").
2.  **Decoding**: Uses a **Population Vector** algorithm to aggregate the spiking activity and reconstruct the velocity vector.
3.  **Result**: The cursor moves in the direction of the user's intent.

## Usage

Run the BCI loop:
```bash
python3 scripts/decoder.py
```

## Publishing
```bash
clawhub publish
```
