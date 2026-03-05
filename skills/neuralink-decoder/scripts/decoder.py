#!/usr/bin/env python3
import numpy as np
import random
import time
import sys

# =========================================================================
# NEURALINK DECODER SKILL
# Simulates Motor Cortex Spiking -> Decodes Cursor Velocity
# =========================================================================

class NeuralSimulator:
    """
    Simulates a population of neurons in the Motor Cortex (M1).
    Uses 'Cosine Tuning' model: Firing Rate ~ Base + Mod * cos(theta - preferred_dir)
    """
    def __init__(self, num_neurons=64):
        self.num_neurons = num_neurons
        # Assign random preferred directions [0, 2pi] for each neuron
        self.preferred_dirs = np.random.uniform(0, 2*np.pi, num_neurons)
        self.base_rate = 10.0 # Hz
        self.modulation = 20.0 # Hz

    def generate_spikes(self, velocity_vector, dt=0.05):
        """
        Generates spike counts for a given time bin 'dt' based on movement velocity.
        velocity_vector: (vx, vy)
        """
        vx, vy = velocity_vector
        speed = np.sqrt(vx**2 + vy**2)
        move_dir = np.arctan2(vy, vx)

        spike_counts = []
        if speed < 0.1:
            # Baseline activity if not moving
            rates = np.full(self.num_neurons, self.base_rate)
        else:
            # Cosine tuning
            rates = self.base_rate + self.modulation * np.cos(self.preferred_dirs - move_dir)
            # Add noise (Poisson-like variability)
        
        rates = np.maximum(rates, 0) # Ensure non-negative
        
        for r in rates:
            # Number of spikes in this bin = Rate * dt + Noise
            count = np.random.poisson(r * dt)
            spike_counts.append(count)
            
        return np.array(spike_counts)

class BCIDecoder:
    """
    Decodes neural activity into velocity.
    In a real system, this is trained via Ridge Regression or Kalman Filter.
    Here, we approximate the inverse of the tuning model for simulation.
    """
    def __init__(self, simulator):
        # We cheat slightly by knowing the preferred directions to construct a perfect population vector decoder
        self.preferred_dirs = simulator.preferred_dirs
        self.num_neurons = simulator.num_neurons

    def decode(self, spike_counts):
        """
        Population Vector Algorithm: Sum of (SpikeCount * PreferredDirectionVector)
        """
        # Normalize counts (subtract baseline estimate)
        baseline_count = 10.0 * 0.05 # roughly base_rate * dt
        rates = spike_counts - baseline_count
        
        # Weighted sum of direction vectors
        vx_est = 0.0
        vy_est = 0.0
        
        for i in range(self.num_neurons):
            w = rates[i]
            vx_est += w * np.cos(self.preferred_dirs[i])
            vy_est += w * np.sin(self.preferred_dirs[i])
            
        # Scale factor (gain) - empirically tuned
        gain = 0.5 
        return np.array([vx_est * gain, vy_est * gain])

def run_simulation():
    print("Initializing Neuralink BCI Simulator...")
    sim = NeuralSimulator(num_neurons=64)
    decoder = BCIDecoder(sim)
    
    print("Subject is thinking: 'Move Cursor Right' (Target: [1.0, 0.0])")
    target_velocity = np.array([1.0, 0.0])
    
    cursor_pos = np.array([0.0, 0.0])
    dt = 0.1 # 100ms bins
    
    print(f"{'TIME':<8} | {'NEURAL SPIKES (Sum)':<20} | {'DECODED VELOCITY':<25} | {'CURSOR POS':<20}")
    print("-" * 85)
    
    for t in range(20):
        # 1. Brain generates spikes based on intention
        spikes = sim.generate_spikes(target_velocity, dt)
        total_spikes = np.sum(spikes)
        
        # 2. BCI Decodes spikes
        vel_est = decoder.decode(spikes)
        
        # 3. Update Cursor
        cursor_pos += vel_est * dt
        
        # Output
        v_str = f"[{vel_est[0]:.2f}, {vel_est[1]:.2f}]"
        p_str = f"[{cursor_pos[0]:.2f}, {cursor_pos[1]:.2f}]"
        print(f"{t*dt:<8.1f} | {total_spikes:<20} | {v_str:<25} | {p_str:<20}")
        
        time.sleep(0.1)
        
    print("-" * 85)
    # Check accuracy
    final_dir = np.arctan2(cursor_pos[1], cursor_pos[0])
    expected_dir = 0.0
    error = abs(final_dir - expected_dir)
    print(f"Angle Error: {error:.4f} rad")
    if error < 0.5:
        print("SUCCESS: Cursor moved in the intended direction.")
    else:
        print("FAIL: Decoding was inaccurate.")

if __name__ == "__main__":
    run_simulation()
