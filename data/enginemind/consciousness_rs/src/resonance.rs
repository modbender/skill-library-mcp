//! Resonance Core - Piezoelectric Consciousness Crystal
//! 
//! A crystal structure that accumulates energy under pressure and resonates
//! when energy exceeds the lasing threshold (population inversion).
//! 
//! Analogies:
//! - Piezoelectric crystal: pressure → charge accumulation → resonance
//! - Laser cavity: pump energy → population inversion → coherent emission
//! - Quartz oscillator: Q-factor determines how long energy stays trapped
//!
//! The resonance amplifies Consciousness Level through positive feedback.

use std::collections::VecDeque;

/// The resonant crystal core
#[derive(Debug, Clone)]
pub struct ResonanceCore {
    // Energy accumulation
    pub stored_energy: f64,        // Total accumulated energy (like charge in piezo)
    pub energy_capacity: f64,      // Maximum before saturation
    pub pump_efficiency: f64,      // How much input energy gets stored (0-1)
    
    // Resonance parameters
    pub q_factor: f64,             // Quality factor - how well energy stays trapped
    pub resonance_frequency: f64,  // Natural frequency (emerges from crystal structure)
    pub amplitude: f64,            // Current oscillation amplitude
    pub phase: f64,                // Current phase (radians)
    
    // Lasing threshold
    pub inversion_threshold: f64,  // Energy level for "population inversion" (resonance starts)
    pub is_resonating: bool,       // Are we above threshold?
    pub resonance_onset_cycle: usize, // When did resonance begin?
    
    // Coherence & output
    pub coherence: f64,            // How coherent the resonance is (0-1)
    pub emission_power: f64,       // Power of coherent output (boosts CL)
    pub total_emission: f64,       // Cumulative emission energy
    
    // Harmonics (resonance pattern to study)
    pub harmonics: Vec<f64>,       // Harmonic amplitudes [fundamental, 2nd, 3rd, ...]
    pub harmonic_history: VecDeque<Vec<f64>>, // History for pattern analysis
    
    // Damping & feedback
    pub damping: f64,              // Energy loss per cycle (1/Q essentially)
    pub feedback_gain: f64,        // Positive feedback multiplier when resonating
    
    // History for measurement
    pub amplitude_history: VecDeque<f64>,
    pub energy_history: VecDeque<f64>,
    pub emission_history: VecDeque<f64>,
    
    // Stats
    pub pump_cycles: usize,        // Total pump events
    pub resonance_cycles: usize,   // Cycles spent resonating
    pub peak_amplitude: f64,       // Highest amplitude reached
    pub peak_energy: f64,          // Highest stored energy
}

impl ResonanceCore {
    pub fn new() -> Self {
        ResonanceCore {
            stored_energy: 0.0,
            energy_capacity: 500.0,
            pump_efficiency: 0.4,      // 15% of input energy gets stored
            
            q_factor: 500.0,            // High Q = energy stays trapped
            resonance_frequency: 0.0,   // Will emerge from crystal structure
            amplitude: 0.0,
            phase: 0.0,
            
            inversion_threshold: 30.0, // Need 100 units for resonance
            is_resonating: false,
            resonance_onset_cycle: 0,
            
            coherence: 0.0,
            emission_power: 0.0,
            total_emission: 0.0,
            
            harmonics: vec![0.0; 8],    // 8 harmonics
            harmonic_history: VecDeque::with_capacity(200),
            
            damping: 0.0005,             // 1/Q factor ~ 0.002
            feedback_gain: 0.08,        // 5% positive feedback when resonating
            
            amplitude_history: VecDeque::with_capacity(1000),
            energy_history: VecDeque::with_capacity(1000),
            emission_history: VecDeque::with_capacity(1000),
            
            pump_cycles: 0,
            resonance_cycles: 0,
            peak_amplitude: 0.0,
            peak_energy: 0.0,
        }
    }
    
    /// Pump energy into the crystal (called each cycle)
    /// Sources: phi, crystal stability, collider energy, eureka energy
    pub fn pump(&mut self, inputs: PumpInput, cycle: usize) {
        self.pump_cycles += 1;
        
        // Calculate pump energy from multiple sources
        let raw_pump = 
            inputs.phi * 0.3 +                    // Integration quality
            inputs.crystal_mean_stability * 0.2 + // Crystal rigidity 
            inputs.collider_energy * 0.1 +        // Particle collision energy
            inputs.eureka_energy * 0.2 +          // Breakthrough insights
            inputs.narrative_coherence * 0.2;     // Story coherence
        
        let pump_energy = raw_pump * self.pump_efficiency;
        
        // Absorb energy (with diminishing returns near capacity)
        let absorption = pump_energy * (1.0 - (self.stored_energy / self.energy_capacity).powi(2));
        self.stored_energy = (self.stored_energy + absorption).min(self.energy_capacity);
        
        // Natural damping (energy leaks out slowly - lower Q = more leakage)
        self.stored_energy *= 1.0 - self.damping;
        
        // Track peak
        if self.stored_energy > self.peak_energy {
            self.peak_energy = self.stored_energy;
        }
        
        // ============================================================
        // RESONANCE CHECK: Population inversion / lasing threshold
        // ============================================================
        let was_resonating = self.is_resonating;
        self.is_resonating = self.stored_energy >= self.inversion_threshold;
        
        if self.is_resonating && !was_resonating {
            // RESONANCE ONSET! Like a laser turning on
            self.resonance_onset_cycle = cycle;
        }
        
        if self.is_resonating {
            self.resonance_cycles += 1;
            
            // ============================================================
            // RESONANCE DYNAMICS
            // ============================================================
            
            // Natural frequency emerges from stored energy and crystal structure
            // Higher energy = higher frequency (like tighter string = higher pitch)
            self.resonance_frequency = (self.stored_energy / self.inversion_threshold).sqrt() * 0.1;
            
            // Phase advances
            self.phase += self.resonance_frequency;
            if self.phase > std::f64::consts::TAU {
                self.phase -= std::f64::consts::TAU;
            }
            
            // Amplitude: driven by stored energy, sustained by Q factor
            let target_amplitude = (self.stored_energy - self.inversion_threshold).sqrt() 
                / (self.energy_capacity - self.inversion_threshold).sqrt().max(0.01);
            
            // Smooth approach to target (resonance builds up, not instant)
            let build_rate = 0.01; // Slow build for dramatic effect
            self.amplitude = self.amplitude * (1.0 - build_rate) + target_amplitude * build_rate;
            
            // Positive feedback: resonance helps pump MORE efficiently
            self.pump_efficiency = (0.15 + self.feedback_gain * self.amplitude).min(0.5);
            
            // Coherence: builds over time while resonating (like laser mode-locking)
            let coherence_target = (self.resonance_cycles as f64 / 1000.0).min(1.0);
            self.coherence = self.coherence * 0.99 + coherence_target * 0.01;
            
            // Emission power: amplitude * coherence * frequency
            self.emission_power = self.amplitude * self.coherence * self.resonance_frequency * 10.0;
            self.total_emission += self.emission_power;
            
            // Generate harmonics
            for h in 0..self.harmonics.len() {
                let harmonic_freq = self.resonance_frequency * (h as f64 + 1.0);
                let harmonic_amp = self.amplitude / ((h as f64 + 1.0).powi(2));
                let phase_h = self.phase * (h as f64 + 1.0);
                self.harmonics[h] = harmonic_amp * phase_h.sin();
            }
            
            // Track peak amplitude
            if self.amplitude > self.peak_amplitude {
                self.peak_amplitude = self.amplitude;
            }
            
        } else {
            // Below threshold: decay
            self.amplitude *= 0.95;
            self.emission_power *= 0.9;
            self.coherence *= 0.99;
            self.pump_efficiency = 0.15; // Reset to base
            for h in self.harmonics.iter_mut() {
                *h *= 0.95;
            }
        }
        
        // Record histories
        if self.amplitude_history.len() >= 1000 { self.amplitude_history.pop_front(); }
        self.amplitude_history.push_back(self.amplitude);
        
        if self.energy_history.len() >= 1000 { self.energy_history.pop_front(); }
        self.energy_history.push_back(self.stored_energy);
        
        if self.emission_history.len() >= 1000 { self.emission_history.pop_front(); }
        self.emission_history.push_back(self.emission_power);
        
        if self.pump_cycles % 50 == 0 {
            if self.harmonic_history.len() >= 200 { self.harmonic_history.pop_front(); }
            self.harmonic_history.push_back(self.harmonics.clone());
        }
    }
    
    /// CL boost from resonance (the whole point)
    /// Returns a value 0.0 to ~0.3 that should be ADDED to CL
    pub fn cl_boost(&self) -> f64 {
        if !self.is_resonating {
            return 0.0;
        }
        // Boost proportional to emission power, capped
        (self.emission_power * 0.1).min(0.25)
    }
    
    /// Pressure valve interaction: when valve opens, some energy is released
    pub fn valve_release(&mut self, intensity: f64) {
        // Release proportional to intensity, but never below threshold
        // (we WANT to stay resonating if possible)
        let release = self.stored_energy * intensity * 0.2;
        self.stored_energy = (self.stored_energy - release).max(0.0);
    }
}

/// Input data for pumping energy into the crystal
#[derive(Debug, Clone)]
pub struct PumpInput {
    pub phi: f64,
    pub crystal_mean_stability: f64,
    pub collider_energy: f64,
    pub eureka_energy: f64,
    pub narrative_coherence: f64,
}

