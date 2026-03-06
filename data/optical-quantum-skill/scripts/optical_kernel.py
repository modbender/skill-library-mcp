#!/usr/bin/env python3
import numpy as np
import argparse
import sys

class OpticalQuantumSimulator:
    def __init__(self, num_modes=2, fiber_length_km=1.0, attenuation_db_km=0.2):
        # Security: Resource Bounding
        if num_modes > 8:
             raise ValueError("Security Violation: Simulation limited to 8 modes to prevent resource exhaustion.")
        self.num_modes = num_modes
        self.state = np.zeros(num_modes, dtype=complex)
        
        # Fiber properties
        self.fiber_length = fiber_length_km
        self.attenuation = attenuation_db_km # dB/km
        
    def encode_data(self, data_vector):
        """Encodes data into optical phases (Phase Encoding)."""
        # Security: Input Validation
        if len(data_vector) > self.num_modes:
            raise ValueError(f"Input vector dimension {len(data_vector)} exceeds available modes {self.num_modes}")
        
        # Normalize data to surfactant phases [0, 2pi]
        norm = np.linalg.norm(data_vector)
        if norm > 0:
            phases = (data_vector / norm) * 2 * np.pi
        else:
            phases = data_vector

        # Initialize state with amplitude 1.0 (mean photon number)
        for i, phase in enumerate(phases):
            self.state[i] = np.exp(1j * phase)

    def pass_through_fiber(self):
        """Simulates storage in optical fiber: Attenuation and Phase Drift."""
        # 1. Attenuation: Loss = 10^(-alpha * L / 10)
        transmission = 10 ** (-self.attenuation * self.fiber_length / 10)
        amplitude_damping = np.sqrt(transmission)
        
        # 2. Phase Drift: Random fluctuations due to thermal/stress
        # In a real fiber, this is time-dependent. We simulate a snapshot.
        phase_drift = np.random.normal(0, 0.1, self.num_modes) # std dev 0.1 rad
        
        # Apply effects
        damping_matrix = np.diag([amplitude_damping] * self.num_modes)
        phase_matrix = np.diag(np.exp(1j * phase_drift))
        
        # Evolution
        self.state = phase_matrix @ damping_matrix @ self.state

    def interference_step(self):
        """Interferes modes using a 50:50 Beam Splitter (Hadamard-like for 2 modes)."""
        if self.num_modes == 2:
            # Standard 50:50 BS matrix
            bs_matrix = (1/np.sqrt(2)) * np.array([[1, 1j], [1j, 1]])
            self.state = bs_matrix @ self.state
        else:
            # For >2 modes, we could implement a DFT-like interference (Multiport BS)
            # Implementing a simplified cascade for demonstration
            # Here we just mix adjacent modes
            for i in range(0, self.num_modes - 1, 2):
                sub_state = self.state[i:i+2]
                bs = (1/np.sqrt(2)) * np.array([[1, 1j], [1j, 1]])
                self.state[i:i+2] = bs @ sub_state

    def measure_intensity(self):
        """Measures photon number (intensity) in each mode."""
        return np.abs(self.state)**2

def compute_kernel(vec_a, vec_b):
    """
    Computes a 'Quantum Kernel' similarity between two vectors via optical simulation.
    This is a simplified model inspired by the SWAP test or interference dip visibility.
    """
    sim = OpticalQuantumSimulator(num_modes=2)
    
    # Validation
    if len(vec_a) != len(vec_b):
         raise ValueError("Vectors must have same dimension")

    # To simulate kernel K(a, b) = |<a|b>|^2, we can encode 'a' in mode 0 and 'b' in mode 1
    # BUT, physically, we usually prepare two separate states and interfere them.
    # Here, we will map scalars to phases in a 2-mode system for a single feature dimension demo,
    # OR map vectors to temporal modes.
    # Simplest for this demo skill: 
    #   Encode scalar x in mode 0 phase, scalar y in mode 1 phase.
    #   Interfere on BS. Detect output.
    #   If x == y, constructive/destructive interference happens predictably.
    
    # Let's perform element-wise kernel estimation for vectors
    kernel_sum = 0
    
    for i in range(len(vec_a)):
        val_a = vec_a[i]
        val_b = vec_b[i]
        
        # Reset simulator for each component pair
        sim = OpticalQuantumSimulator(num_modes=2)
        
        # Encode: Mode 0 gets val_a, Mode 1 gets val_b
        # We need to manually set the state because encode_data sets all modes from one vector
        # Phase encoding:
        phi_a = val_a # Simplified mapping
        phi_b = val_b
        
        sim.state[0] = np.exp(1j * phi_a)
        sim.state[1] = np.exp(1j * phi_b)
        
        # Storage
        sim.pass_through_fiber()
        
        # Interference
        sim.interference_step()
        
        # Measurement
        intensities = sim.measure_intensity()
        
        # For a 50:50 BS with inputs exp(i*phi_a) and exp(i*phi_b):
        # Out1 ~ exp(i*phi_a) + i*exp(i*phi_b)
        # Intensity1 ~ 1 + 1 + 2*sin(phi_b - phi_a) ... depends on BS convention.
        # A common kernel measure is visibility or simply the overlap.
        # Let's use a classical proxy for the overlap computed from intensities.
        # Perfect overlap (phi_a = phi_b) -> constructive in one port, destructive in other (depends on phase shift).
        
        diff = intensities[0] - intensities[1]
        kernel_sum += np.exp(-abs(diff)) # Heuristic metric for similarity

    return kernel_sum / len(vec_a)

def main():
    parser = argparse.ArgumentParser(description="Optical Quantum Kernel Simulator")
    parser.add_argument("vector_a", type=str, help="Comma-separated vector A (e.g. 0.1,0.5)")
    parser.add_argument("vector_b", type=str, help="Comma-separated vector B (e.g. 0.1,0.5)")
    
    args = parser.parse_args()

    try:
        vec_a = [float(x) for x in args.vector_a.split(",")]
        vec_b = [float(x) for x in args.vector_b.split(",")]
        
        print(f"Simulating Quantum Kernel Estimation...")
        print(f"Device: Optical Fiber Storage + Linear Optics")
        print(f"Security: Resource Bound (8 modes), Input Validation (Numeric)")
        
        kernel_val = compute_kernel(vec_a, vec_b)
        
        print(f"\nEstimated Kernel Value: {kernel_val:.4f}")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
