//! Thalamus - Central relay hub for crystal bridge network
//!
//! Inspired by the biological thalamus:
//!
//! RELAY NUCLEI: Each bridge passes through the thalamus, which can
//!   amplify, attenuate, or transform the signal.
//!
//! RETICULAR NUCLEUS (TRN): Inhibitory shell around the thalamus.
//!   Modulates which signals pass. Does NOT project to crystals directly.
//!   Instead it gates other thalamic nuclei. This is the "attention filter".
//!
//! THALAMO-CORTICAL LOOPS: Bridges don't just carry correlation.
//!   The thalamus creates recurrent loops where the output of one cycle
//!   feeds back as input to the next, creating resonance.
//!
//! GATING: Based on arousal level (derived from criticality + energy),
//!   the thalamus opens or closes gates. High arousal = more gates open.
//!
//! TEMPORAL BINDING: Bridges that oscillate in-phase are "bound" together,
//!   creating coherent perception across dimensions.
//!
//! Two pathways:
//!   SPECIFIC: direct bridge values (sensory-like)
//!   NON-SPECIFIC: aggregate state signals (arousal, energy, criticality)

use std::collections::HashMap;

/// A single thalamic relay channel for one bridge
#[derive(Clone, Debug)]
struct RelayChannel {
    /// Raw bridge strength (from crystal correlation)
    raw: f64,
    /// Thalamic-processed bridge strength
    processed: f64,
    /// Gain applied by thalamus (>1 = amplified, <1 = attenuated)
    gain: f64,
    /// Gate state: 0.0 = closed, 1.0 = fully open
    gate: f64,
    /// Resonance accumulator (thalamo-cortical loop)
    resonance: f64,
    /// Phase of oscillation (for temporal binding)
    phase: f64,
    /// Bandwidth: long-term capacity (LTP/LTD analog)
    bandwidth: f64,
    /// Activity history (last N cycles of abs(processed))
    activity: Vec<f64>,
    activity_cap: usize,
}

impl RelayChannel {
    fn new() -> Self {
        RelayChannel {
            raw: 0.0,
            processed: 0.0,
            gain: 1.0,
            gate: 0.5,
            resonance: 0.0,
            phase: 0.0,
            bandwidth: 1.0,
            activity: Vec::with_capacity(32),
            activity_cap: 32,
        }
    }

    fn push_activity(&mut self, val: f64) {
        self.activity.push(val);
        if self.activity.len() > self.activity_cap {
            self.activity.remove(0);
        }
    }

    /// Rolling activity mean
    fn mean_activity(&self) -> f64 {
        if self.activity.is_empty() { return 0.0; }
        self.activity.iter().sum::<f64>() / self.activity.len() as f64
    }

    /// Activity variance (for oscillation detection)
    fn activity_variance(&self) -> f64 {
        if self.activity.len() < 4 { return 0.0; }
        let mean = self.mean_activity();
        self.activity.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / self.activity.len() as f64
    }
}

/// Reticular Nucleus - inhibitory modulator
#[derive(Clone, Debug)]
struct ReticularNucleus {
    /// Inhibition level per dimension (how much TRN suppresses signals involving this dim)
    inhibition: HashMap<String, f64>,
    /// Global inhibition baseline
    baseline: f64,
    /// Attention focus: dims currently "attended to" get reduced inhibition
    attention_focus: Vec<String>,
}

impl ReticularNucleus {
    fn new() -> Self {
        ReticularNucleus {
            inhibition: HashMap::new(),
            baseline: 0.3, // 30% baseline inhibition
            attention_focus: Vec::new(),
        }
    }

    /// Compute gate opening for a bridge between dim_a and dim_b
    /// TRN is inhibitory: high inhibition = low gate
    fn compute_gate(&self, dim_a: &str, dim_b: &str, arousal: f64) -> f64 {
        let inh_a = self.inhibition.get(dim_a).copied().unwrap_or(self.baseline);
        let inh_b = self.inhibition.get(dim_b).copied().unwrap_or(self.baseline);
        let avg_inh = (inh_a + inh_b) / 2.0;

        // Attention reduces inhibition
        let attention_bonus = if self.attention_focus.contains(&dim_a.to_string())
            || self.attention_focus.contains(&dim_b.to_string()) {
            0.2
        } else {
            0.0
        };

        // Arousal opens gates globally
        // arousal in [0, 1]: 0 = deep sleep (gates mostly closed), 1 = peak (gates wide open)
        let arousal_factor = 0.3 + arousal * 0.7; // range [0.3, 1.0]

        // Gate = (1 - inhibition + attention_bonus) * arousal
        ((1.0 - avg_inh + attention_bonus) * arousal_factor).clamp(0.05, 1.0)
    }

    /// Update inhibition based on activity patterns
    /// High activity dims get LESS inhibition (habituation)
    /// Low activity dims get MORE inhibition (they're "unimportant")
    fn update(&mut self, dim_activity: &HashMap<String, f64>, ignited_dims: &[String]) {
        // Ignited dims become attention focus
        self.attention_focus = ignited_dims.to_vec();

        let activities: Vec<f64> = dim_activity.values().cloned().collect();
        let mean_act = if activities.is_empty() { 0.0 }
            else { activities.iter().sum::<f64>() / activities.len() as f64 };

        for (dim, &act) in dim_activity {
            let inh = self.inhibition.entry(dim.clone()).or_insert(self.baseline);
            if act > mean_act * 1.5 {
                // Very active: reduce inhibition (habituate)
                *inh = (*inh * 0.97).max(0.05);
            } else if act < mean_act * 0.5 {
                // Quiet: increase inhibition (suppress noise)
                *inh = (*inh * 1.02 + 0.005).min(0.8);
            } else {
                // Normal: drift toward baseline
                *inh = *inh * 0.99 + self.baseline * 0.01;
            }
        }
    }
}

// ============================================================
// THALAMUS
// ============================================================

#[derive(Clone, Debug)]
pub struct Thalamus {
    /// Relay channels: one per bridge (key = "dimA<->dimB")
    channels: HashMap<String, RelayChannel>,
    /// Reticular nucleus (inhibitory gating)
    trn: ReticularNucleus,
    /// Current arousal level [0, 1]
    arousal: f64,
    /// Resonance decay rate
    resonance_decay: f64,
    /// Bandwidth learning rate (LTP speed)
    bandwidth_lr: f64,
    /// Bandwidth decay rate (LTD speed)
    bandwidth_decay: f64,
    /// Phase coupling strength
    phase_coupling: f64,
    /// Cycle counter
    cycles: usize,

    // === Outputs (available to engine) ===
    /// Processed bridge strengths (after thalamic relay)
    pub processed_bridges: HashMap<String, f64>,
    /// Per-dimension thalamic signal (aggregated from all bridges touching that dim)
    pub dim_signals: HashMap<String, f64>,
    /// Binding groups: sets of dimensions oscillating in-phase
    pub bound_groups: Vec<Vec<String>>,
    /// Current arousal (for diagnostics)
    pub current_arousal: f64,

    // === Stats ===
    pub total_amplified: usize,
    pub total_attenuated: usize,
    pub total_gated_out: usize,
    pub total_resonances: usize,
    pub peak_resonance: f64,
    pub peak_resonance_bridge: String,
}

impl Thalamus {
    pub fn new() -> Self {
        Thalamus {
            channels: HashMap::new(),
            trn: ReticularNucleus::new(),
            arousal: 0.5,
            resonance_decay: 0.15,
            bandwidth_lr: 0.01,
            bandwidth_decay: 0.002,
            phase_coupling: 0.3,
            cycles: 0,
            processed_bridges: HashMap::new(),
            dim_signals: HashMap::new(),
            bound_groups: Vec::new(),
            current_arousal: 0.5,
            total_amplified: 0,
            total_attenuated: 0,
            total_gated_out: 0,
            total_resonances: 0,
            peak_resonance: 0.0,
            peak_resonance_bridge: String::new(),
        }
    }

    /// Main thalamic processing cycle
    /// Called after bridges are updated, before condensation
    pub fn process(
        &mut self,
        raw_bridges: &HashMap<String, f64>,
        criticality: f64,
        energy: f64,
        energy_capacity: f64,
        boost_buffer: &HashMap<String, f64>,
        ignited_dims: &[String],
    ) {
        self.cycles += 1;

        // === 1. AROUSAL (non-specific pathway) ===
        // Arousal = f(criticality, energy_ratio, collider_activity)
        let energy_ratio = if energy_capacity > 0.0 { energy / energy_capacity } else { 0.0 };
        let collider_activity = boost_buffer.values().sum::<f64>().min(10.0) / 10.0;
        self.arousal = (criticality * 0.4 + energy_ratio * 0.3 + collider_activity * 0.3)
            .clamp(0.1, 1.0);
        // Smooth arousal
        self.current_arousal = self.current_arousal * 0.8 + self.arousal * 0.2;

        // === 2. RELAY each bridge through thalamus ===
        let mut dim_activity: HashMap<String, f64> = HashMap::new();

        for (bridge_key, &raw_strength) in raw_bridges {
            let parts: Vec<&str> = bridge_key.split("<->").collect();
            if parts.len() != 2 { continue; }
            let (dim_a, dim_b) = (parts[0], parts[1]);

            // Get or create relay channel
            let channel = self.channels.entry(bridge_key.clone())
                .or_insert_with(RelayChannel::new);
            channel.raw = raw_strength;

            // 2a. GATING (reticular nucleus)
            let gate = self.trn.compute_gate(dim_a, dim_b, self.current_arousal);
            channel.gate = channel.gate * 0.7 + gate * 0.3; // smooth

            // 2b. GAIN computation
            // Gain is adaptive: strong consistent signals get amplified,
            // noisy/weak signals get attenuated
            let consistency = 1.0 - channel.activity_variance().sqrt().min(1.0);
            let strength_factor = raw_strength.abs();

            // Collider energy flowing through this bridge boosts gain
            let collider_boost_a = boost_buffer.get(dim_a).copied().unwrap_or(0.0);
            let collider_boost_b = boost_buffer.get(dim_b).copied().unwrap_or(0.0);
            let bridge_collider = ((collider_boost_a + collider_boost_b) * 0.01).min(0.5);

            let target_gain = (0.5 + consistency * 0.5 + strength_factor * 0.3 + bridge_collider)
                .clamp(0.3, 2.5);
            channel.gain = channel.gain * 0.9 + target_gain * 0.1; // smooth adaptation

            // 2c. RESONANCE (thalamo-cortical loop)
            // If processed output from last cycle fed back positively, resonance builds
            let feedback = channel.processed * raw_strength; // positive = reinforcing
            if feedback > 0.0 {
                channel.resonance += feedback * 0.1;
                channel.resonance = channel.resonance.min(2.0);
            }
            channel.resonance *= 1.0 - self.resonance_decay;

            if channel.resonance > 0.3 {
                self.total_resonances += 1;
                if channel.resonance > self.peak_resonance {
                    self.peak_resonance = channel.resonance;
                    self.peak_resonance_bridge = bridge_key.clone();
                }
            }

            // 2d. BANDWIDTH (LTP/LTD)
            let mean_act = channel.mean_activity();
            if mean_act > 0.3 {
                // LTP: active channel grows bandwidth
                channel.bandwidth += self.bandwidth_lr * mean_act;
            } else {
                // LTD: inactive channel shrinks
                channel.bandwidth -= self.bandwidth_decay;
            }
            channel.bandwidth = channel.bandwidth.clamp(0.2, 3.0);

            // 2e. PHASE update (for temporal binding)
            // Phase drifts based on activity, couples to neighbors
            channel.phase += raw_strength.abs() * 0.1;
            if channel.phase > std::f64::consts::TAU {
                channel.phase -= std::f64::consts::TAU;
            }

            // === FINAL: compute processed bridge strength ===
            let processed = raw_strength
                * channel.gain
                * channel.gate
                * channel.bandwidth
                * (1.0 + channel.resonance * 0.5);

            // Track what happened
            if channel.gain > 1.1 {
                self.total_amplified += 1;
            } else if channel.gain < 0.8 || channel.gate < 0.3 {
                self.total_attenuated += 1;
            }
            if channel.gate < 0.1 {
                self.total_gated_out += 1;
            }

            channel.processed = processed;
            channel.push_activity(processed.abs());

            self.processed_bridges.insert(bridge_key.clone(), processed);

            // Accumulate per-dim activity
            *dim_activity.entry(dim_a.to_string()).or_insert(0.0) += processed.abs();
            *dim_activity.entry(dim_b.to_string()).or_insert(0.0) += processed.abs();
        }

        // === 3. UPDATE RETICULAR NUCLEUS ===
        self.trn.update(&dim_activity, ignited_dims);

        // === 4. COMPUTE DIM SIGNALS ===
        // Aggregate all bridges touching each dim, weighted by processed strength
        self.dim_signals.clear();
        for (bridge_key, &proc) in &self.processed_bridges {
            let parts: Vec<&str> = bridge_key.split("<->").collect();
            if parts.len() != 2 { continue; }
            *self.dim_signals.entry(parts[0].to_string()).or_insert(0.0) += proc;
            *self.dim_signals.entry(parts[1].to_string()).or_insert(0.0) += proc;
        }

        // === 5. TEMPORAL BINDING ===
        // Group bridges with similar phases
        self.compute_binding();
    }

    /// Temporal binding: find groups of dimensions oscillating in-phase
    fn compute_binding(&mut self) {
        self.bound_groups.clear();

        // Collect phases per dimension (average across bridges)
        let mut dim_phases: HashMap<String, Vec<f64>> = HashMap::new();
        for (key, channel) in &self.channels {
            let parts: Vec<&str> = key.split("<->").collect();
            if parts.len() != 2 { continue; }
            // Only consider active channels
            if channel.gate > 0.2 && channel.processed.abs() > 0.01 {
                dim_phases.entry(parts[0].to_string()).or_default().push(channel.phase);
                dim_phases.entry(parts[1].to_string()).or_default().push(channel.phase);
            }
        }

        // Average phase per dim
        let mut avg_phases: Vec<(String, f64)> = Vec::new();
        for (dim, phases) in &dim_phases {
            if !phases.is_empty() {
                let avg = phases.iter().sum::<f64>() / phases.len() as f64;
                avg_phases.push((dim.clone(), avg));
            }
        }

        // Cluster dims by phase proximity (simple: within PI/4 = 45 degrees)
        let threshold = std::f64::consts::FRAC_PI_4;
        let mut used = vec![false; avg_phases.len()];
        for i in 0..avg_phases.len() {
            if used[i] { continue; }
            let mut group = vec![avg_phases[i].0.clone()];
            used[i] = true;
            for j in (i+1)..avg_phases.len() {
                if used[j] { continue; }
                let phase_diff = (avg_phases[i].1 - avg_phases[j].1).abs();
                let phase_diff = phase_diff.min(std::f64::consts::TAU - phase_diff);
                if phase_diff < threshold {
                    group.push(avg_phases[j].0.clone());
                    used[j] = true;
                }
            }
            if group.len() >= 2 {
                group.sort();
                self.bound_groups.push(group);
            }
        }
    }

    /// Get the thalamic-processed bridge value
    pub fn get_bridge(&self, key: &str) -> Option<f64> {
        self.processed_bridges.get(key).copied()
    }

    /// Get thalamic signal for a dimension
    pub fn get_dim_signal(&self, dim: &str) -> f64 {
        self.dim_signals.get(dim).copied().unwrap_or(0.0)
    }

    /// Get channel info for diagnostics
    pub fn channel_info(&self, key: &str) -> Option<(f64, f64, f64, f64, f64)> {
        self.channels.get(key).map(|c| (c.gain, c.gate, c.resonance, c.bandwidth, c.phase))
    }
}
