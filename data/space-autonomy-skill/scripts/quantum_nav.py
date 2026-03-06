#!/usr/bin/env python3
import numpy as np
import argparse
import sys
import math

class OpticalQuantumSimulator:
    """
    Simulates optical fiber storage and linear optics interactions.
    Reused from optical-quantum-skill for portability.
    """
    def __init__(self, num_modes=2, fiber_length_km=1.0, attenuation_db_km=0.2):
        if num_modes > 8: raise ValueError("Resource Limit Exceeded")
        self.num_modes = num_modes
        self.state = np.zeros(num_modes, dtype=complex)
        self.fiber_length = fiber_length_km
        self.attenuation = attenuation_db_km

    def encode_phase(self, data_vector):
        # Assume input data is in [0, 1] range
        # Map 0 -> 0, 1 -> PI/2 to avoid phase ambiguity in sine response
        phases = np.array(data_vector) * (np.pi / 2)
        for i, phase in enumerate(phases):
            self.state[i] = np.exp(1j * phase)

    def evolve(self):
        # Fiber Attenuation
        trans = 10 ** (-self.attenuation * self.fiber_length / 10)
        amp_damping = np.sqrt(trans)
        # Phase Noise
        drift = np.random.normal(0, 0.05, self.num_modes) # Reduced noise for high-grade space optics
        
        damping = np.diag([amp_damping] * self.num_modes)
        phasing = np.diag(np.exp(1j * drift))
        self.state = phasing @ damping @ self.state

    def interfere(self):
        # 50:50 BS for 2 modes
        bs = (1/np.sqrt(2)) * np.array([[1, 1j], [1j, 1]])
        if self.num_modes == 2:
            self.state = bs @ self.state

    def measure(self):
        return np.abs(self.state)**2

def compute_kernel(vec_a, vec_b):
    """Computes similarity using the optical simulator."""
    sim = OpticalQuantumSimulator(num_modes=2)
    kernel_sum = 0
    # simplified element-wise comparison for robustness
    for i in range(min(len(vec_a), len(vec_b))):
        sim.state[0] = np.exp(1j * vec_a[i])
        sim.state[1] = np.exp(1j * vec_b[i])
        sim.evolve()
        sim.interfere()
        intensities = sim.measure()
        # Heuristic: Destructive interference at port 2 implies similarity?
        # Let's use a standard visibility metric.
        # If phases are equal, port 1 -> bright, port 2 -> dark (depending on BS phase)
        # We assume standard BS where equal inputs -> port 0 activates.
        diff = intensities[0] - intensities[1]
        
        # Derived physics: diff = 2 * sin(phi_a - phi_b)
        # We want Kernel = 1 when diff = 0 (identical phases)
        # We use a linear decay based on the interference contrast
        # Range of diff is [-2, 2].
        similarity = 1.0 - (0.5 * np.abs(diff))
        kernel_sum += similarity
    return kernel_sum / len(vec_a)


class QuantumAutonomyAgent:
    def __init__(self):
        # Knowledge Base: Known terrain signatures (normalized vectors)
        self.signatures = {
            "SAFE_FLAT": [0.1, 0.1, 0.1],
            "HAZARD_ROCK": [0.8, 0.9, 0.7],
            "HAZARD_VOID": [0.0, 0.0, 0.0]
        }
        self.safety_threshold = 0.85 # High confidence required

    def classify_terrain(self, sensor_input):
        print(f"Agent identifying terrain signature: {sensor_input}")
        
        scores = {}
        for terrain, sig in self.signatures.items():
            # Redundancy: Run 3 times and average to average out optical noise
            k_vals = []
            for _ in range(3):
                k = compute_kernel(sensor_input, sig)
                k_vals.append(k)
            scores[terrain] = np.mean(k_vals)
            
        return scores

    def decide_action(self, sensor_input):
        scores = self.classify_terrain(sensor_input)
        best_match = max(scores, key=scores.get)
        confidence = scores[best_match]
        
        print("\n--- Quantum Kernel Analysis ---")
        for t, s in scores.items():
            print(f"  {t}: {s:.4f}")
            
        print(f"\nBest Match: {best_match} (Confidence: {confidence:.4f})")

        # SAFETY FAILSAFE
        if confidence < self.safety_threshold:
            return ">>> TRIGGERING FAILSAFE: SAFE MODE (UNCERTAIN TERRAIN) <<<"
        
        if "SAFE" in best_match:
            return f"Action: PROCEED (Terrain is {best_match})"
        else:
            return f"Action: AVOID / HALT (Detected {best_match})"

def main():
    parser = argparse.ArgumentParser(description="Space Autonomy Agent")
    parser.add_argument("sensor_data", type=str, help="Sensor vector (e.g., '0.1,0.2,0.1')")
    args = parser.parse_args()

    try:
        input_vec = [float(x) for x in args.sensor_data.split(",")]
        agent = QuantumAutonomyAgent()
        sys.stdout.flush()
        
        decision = agent.decide_action(input_vec)
        print("\n" + "="*40)
        print(f"DECISION: {decision}")
        print("="*40)

    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
