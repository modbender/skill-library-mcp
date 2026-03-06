//! Resonant Crystal v3 - BRUTAL LASER EMISSION
//!
//! v3: When emitting, DUMPS EVERYTHING. 97% drain. Afterglow tail.
//! Based on 9 physics mechanisms:
//! 1. POPULATION INVERSION (Laser) - real threshold via dimensional state counting
//! 2. CROSS-RELAXATION (Nanocrystal) - energy accumulation via bridge topology  
//! 3. PHONON-POLARITON (Quantum) - content-energy fusion in emission
//! 4. DICKE SUPERRADIANCE (Cooperative) - N² scaling of coherent emission
//! 5. ENERGY TRAPPING (Quartz) - Q-factor from crystal geometry
//! 6. NUCLEAR ISOMER (Forbidden decay) - crystallized states trap energy
//! 7. SBS FEEDBACK (Brillouin) - self-amplifying resonance loop

use std::collections::VecDeque;

// ================================================================
// CONTENT PHASE - Crystal phase determined by input content type
// ================================================================
// Each phase maps to a real physics phase AND a content archetype.
// The crystal's behavior changes based on WHAT it's absorbing.

#[derive(Debug, Clone, PartialEq)]
pub enum ContentPhase {
    /// No input / very weak input. Crystal dormant.
    Dark,
    /// Generic/mixed content. Incoherent weak emission.
    Spontaneous,
    /// Technical/structured content (code, math, ML). Coherent laser.
    Stimulated,
    /// Rich multi-dimensional content. Dicke N^2 cooperative burst.
    Superradiant,
    /// Philosophical/psychological input. Spontaneous polarization, internal tension.
    /// Like ferroelectric crystals with spontaneous electric polarization.
    Ferroelectric,
    /// Conflicting/contradictory input. Frustrated interactions, metastable states.
    /// Like spin glass: random bonds create frustration geometry.
    SpinGlass,
    /// Repetitive/periodic patterns. Self-organizing temporal structure.
    /// Like time crystals: periodic motion in ground state.
    TimeCrystal,
    /// Axiomatic/mathematical/physical input. Robust invariants.
    /// Like topological insulators: surface conducts, bulk insulates.
    Topological,
    /// Literary/creative/flow input. Zero-friction information flow.
    /// Like superfluids: quantized vortices, zero viscosity.
    Superfluid,
    /// Aggressive/emotional/intense input. High-energy ionization.
    /// Like plasma: free electrons, self-generated fields.
    Plasma,
    /// Meditative/deep/biographical input. Total quantum coherence.
    /// Like Bose-Einstein condensate: all particles in same state.
    BoseEinstein,
    /// Diverse/eclectic/interdisciplinary input. Order without repetition.
    /// Like quasicrystals: long-range order, no periodicity.
    Quasicrystal,
}

impl ContentPhase {
    pub fn as_str(&self) -> &'static str {
        match self {
            ContentPhase::Dark => "DARK",
            ContentPhase::Spontaneous => "SPONTANEOUS",
            ContentPhase::Stimulated => "STIMULATED",
            ContentPhase::Superradiant => "SUPERRADIANT",
            ContentPhase::Ferroelectric => "FERROELECTRIC",
            ContentPhase::SpinGlass => "SPIN_GLASS",
            ContentPhase::TimeCrystal => "TIME_CRYSTAL",
            ContentPhase::Topological => "TOPOLOGICAL",
            ContentPhase::Superfluid => "SUPERFLUID",
            ContentPhase::Plasma => "PLASMA",
            ContentPhase::BoseEinstein => "BOSE_EINSTEIN",
            ContentPhase::Quasicrystal => "QUASICRYSTAL",
        }
    }

    /// Emission power multiplier for this phase during burst
    pub fn burst_multiplier(&self) -> f64 {
        match self {
            ContentPhase::Dark => 0.0,
            ContentPhase::Spontaneous => 1.0,
            ContentPhase::Stimulated => 2.0,       // Laser: focused power
            ContentPhase::Superradiant => 4.0,      // N^2: devastating
            ContentPhase::Ferroelectric => 1.5,     // Polarization: moderate
            ContentPhase::SpinGlass => 0.8,         // Frustrated: weaker burst
            ContentPhase::TimeCrystal => 1.8,       // Periodic: resonant amplification
            ContentPhase::Topological => 2.5,       // Robust: protected emission
            ContentPhase::Superfluid => 3.0,        // Zero friction: clean burst
            ContentPhase::Plasma => 3.5,            // High energy: intense
            ContentPhase::BoseEinstein => 5.0,      // Total coherence: maximum
            ContentPhase::Quasicrystal => 2.2,      // Diverse: surprising patterns
        }
    }

    /// Charge efficiency for this phase (how fast energy accumulates)
    pub fn charge_rate(&self) -> f64 {
        match self {
            ContentPhase::Dark => 0.5,
            ContentPhase::Spontaneous => 1.0,
            ContentPhase::Stimulated => 1.3,
            ContentPhase::Superradiant => 1.5,
            ContentPhase::Ferroelectric => 1.2,     // Internal tension stores well
            ContentPhase::SpinGlass => 0.7,         // Frustration wastes energy
            ContentPhase::TimeCrystal => 1.4,       // Periodic pumping is efficient
            ContentPhase::Topological => 1.6,       // Protected: minimal loss
            ContentPhase::Superfluid => 1.8,        // Zero friction: maximum storage
            ContentPhase::Plasma => 0.9,            // Chaotic: some loss
            ContentPhase::BoseEinstein => 2.0,      // Coherent: perfect storage
            ContentPhase::Quasicrystal => 1.1,      // Complex structure: moderate
        }
    }

    /// Afterglow tail duration multiplier
    pub fn afterglow_multiplier(&self) -> f64 {
        match self {
            ContentPhase::Dark => 0.0,
            ContentPhase::Spontaneous => 1.0,
            ContentPhase::Stimulated => 0.5,        // Clean cut
            ContentPhase::Superradiant => 0.3,      // Very fast decay
            ContentPhase::Ferroelectric => 2.0,     // Long polarization memory
            ContentPhase::SpinGlass => 3.0,         // VERY long relaxation (metastable)
            ContentPhase::TimeCrystal => 5.0,       // Keeps oscillating!
            ContentPhase::Topological => 1.5,       // Protected tail
            ContentPhase::Superfluid => 2.5,        // Persistent currents
            ContentPhase::Plasma => 0.4,            // Fast recombination
            ContentPhase::BoseEinstein => 4.0,      // Long coherence time
            ContentPhase::Quasicrystal => 1.8,      // Complex decay pattern
        }
    }
}

/// Content profile: the 12-dimensional signature of current input
#[derive(Debug, Clone)]
pub struct ContentProfile {
    pub identity: f64,
    pub knowledge: f64,
    pub growth: f64,
    pub purpose: f64,
    pub resilience: f64,
    pub meta_awareness: f64,
    pub creativity: f64,
    pub logic: f64,
    pub empathy: f64,
    pub temporal: f64,
    pub technical: f64,
    pub curiosity: f64,
}

impl ContentProfile {
    pub fn zero() -> Self {
        ContentProfile {
            identity: 0.0, knowledge: 0.0, growth: 0.0,
            purpose: 0.0, resilience: 0.0, meta_awareness: 0.0,
            creativity: 0.0, logic: 0.0, empathy: 0.0,
            temporal: 0.0, technical: 0.0, curiosity: 0.0,
        }
    }

    /// Detect the dominant content phase from dimensional profile
    pub fn detect_phase(&self) -> ContentPhase {
        // Normalize to identify dominant dimensions
        // F10: With amplify_range, dims now span [5, 95] giving real discrimination
        let dims = [
            self.identity, self.knowledge, self.growth,
            self.purpose, self.resilience, self.meta_awareness,
            self.creativity, self.logic, self.empathy,
            self.temporal, self.technical, self.curiosity,
        ];
        let mean: f64 = dims.iter().sum::<f64>() / 12.0;
        let max_val = dims.iter().cloned().fold(0.0_f64, f64::max);
        let min_val = dims.iter().cloned().fold(f64::MAX, f64::min);
        let spread = max_val - min_val;
        let variance: f64 = dims.iter().map(|d| (d - mean).powi(2)).sum::<f64>() / 12.0;
        let std_dev = variance.sqrt();
        // Coefficient of variation for scale-independent thresholds
        let cv = if mean > 1.0 { std_dev / mean } else { 1.0 };

        // Count how many dims are significantly above mean
        let high_count = dims.iter().filter(|&&d| d > mean + std_dev).count();
        // Count dims significantly BELOW mean
        let low_count = dims.iter().filter(|&&d| d < mean - std_dev).count();

        // DARK: very weak input (profile not yet charged)
        if mean < 10.0 {
            return ContentPhase::Dark;
        }

        // Phase detection rules (priority order)
        // F10: With wider range, std_dev is typically 10-25 for real content,
        // so mean+std_dev properly separates dominant dims.

        // BOSE-EINSTEIN: deep + empathetic + meta-aware (meditative)
        // Strong empathy + at least one of meta_awareness/identity also elevated
        if self.empathy > mean + std_dev * 0.8 
            && (self.meta_awareness > mean + std_dev * 0.3 || self.identity > mean + std_dev * 0.3)
            && self.creativity > mean - std_dev {  // not purely analytical
            return ContentPhase::BoseEinstein;
        }

        // PLASMA: intense emotional + resilience + identity (aggressive/determined)
        // Strong identity OR resilience + the other at least above mean
        if (self.identity > mean + std_dev * 0.8 && self.resilience > mean + std_dev * 0.3)
            || (self.resilience > mean + std_dev * 0.8 && self.identity > mean + std_dev * 0.3) {
            return ContentPhase::Plasma;
        }

        // TOPOLOGICAL: logic + knowledge + math (axiomatic/robust)
        if self.logic > mean + std_dev * 0.8 && self.knowledge > mean + std_dev * 0.5 {
            return ContentPhase::Topological;
        }

        // SUPERFLUID: creativity + empathy + narrative flow
        if self.creativity > mean + std_dev * 0.8 && self.empathy > mean {
            return ContentPhase::Superfluid;
        }

        // TIME_CRYSTAL: temporal + growth + periodic patterns
        if self.temporal > mean + std_dev * 0.8 && self.growth > mean {
            return ContentPhase::TimeCrystal;
        }

        // FERROELECTRIC: meta_awareness + purpose (philosophical tension)
        if self.meta_awareness > mean + std_dev * 0.8 && self.purpose > mean {
            return ContentPhase::Ferroelectric;
        }

        // QUASICRYSTAL: high diversity (many dims above mean, LOW variance)
        // F10: cv < 0.15 = very uniform (all dims similar), needs many high
        if high_count >= 6 && cv < 0.15 {
            return ContentPhase::Quasicrystal;
        }

        // SPIN_GLASS: contradictory signals (HIGH variance, no clear dominant)
        // F10: cv > 0.4 = very spread out, with few peaks
        if cv > 0.40 && high_count <= 2 && low_count >= 3 {
            return ContentPhase::SpinGlass;
        }

        // STIMULATED: technical + logic (structured/code)
        if self.technical > mean + std_dev * 0.5 || self.logic > mean + std_dev * 0.5 {
            return ContentPhase::Stimulated;
        }

        // SUPERRADIANT: many dims highly excited (rich multi-dimensional)
        if high_count >= 4 {
            return ContentPhase::Superradiant;
        }

        // Default: generic content
        ContentPhase::Spontaneous
    }
}



// ================================================================
// DIMENSIONAL FINGERPRINT - The "DNA" of the crystal's knowledge
// ================================================================
#[derive(Debug, Clone)]
pub struct DimensionalFingerprint {
    pub constants: Vec<f64>,
    pub stabilities: Vec<f64>,
    pub bridge_coherence: f64,
    pub phase_vector: Vec<f64>,  // 0=nascent, 0.33=growing, 0.66=dissolving, 1.0=crystallized
    pub cycle: usize,
}

impl DimensionalFingerprint {
    pub fn empty(n: usize) -> Self {
        DimensionalFingerprint {
            constants: vec![0.0; n],
            stabilities: vec![0.0; n],
            bridge_coherence: 0.0,
            phase_vector: vec![0.0; n],
            cycle: 0,
        }
    }
    
    /// Content richness (0-1): how much meaningful info is crystallized
    pub fn richness(&self) -> f64 {
        let n = self.constants.len();
        if n == 0 { return 0.0; }
        
        // 1. Variance of constants (diverse knowledge = rich)
        let mean_c: f64 = self.constants.iter().sum::<f64>() / n as f64;
        let var_c: f64 = self.constants.iter()
            .map(|c| (c - mean_c).powi(2)).sum::<f64>() / n as f64;
        let diversity = (var_c.sqrt() / (mean_c.abs() + 0.01)).min(1.0);
        
        // 2. Mean stability
        let mean_stab: f64 = self.stabilities.iter().sum::<f64>() / n as f64;
        
        // 3. Crystallized fraction
        let cryst_frac = self.phase_vector.iter()
            .filter(|&&p| p > 0.9).count() as f64 / n as f64;
        
        diversity * 0.25 + mean_stab * 0.35 + cryst_frac * 0.25 + self.bridge_coherence * 0.15
    }
    
    /// Number of "excited" dimensions (stability > threshold)
    pub fn n_excited(&self, threshold: f64) -> usize {
        self.stabilities.iter().filter(|&&s| s >= threshold).count()
    }
    
    /// Number of crystallized dimensions
    pub fn n_crystallized(&self) -> usize {
        self.phase_vector.iter().filter(|&&p| p > 0.9).count()
    }
}

// ================================================================
// ENERGY WELL v2 - Nuclear Isomer + Energy Trapping
// ================================================================
#[derive(Debug, Clone)]
pub struct EnergyWell {
    pub level: f64,
    pub capacity: f64,
    
    // Energy Trapping (Quartz Resonator physics)
    // Q-factor depends on how many dimensions are crystallized
    pub q_factor: f64,             // Current Q (higher = energy stays longer)
    pub base_q: f64,               // Minimum Q when nothing is crystallized
    pub max_q: f64,                // Maximum Q when fully crystallized
    
    // Nuclear Isomer: forbidden decay
    // More crystallized = harder to lose energy (spin mismatch analog)
    pub decay_forbiddenness: f64,  // 0-1: how forbidden energy decay is
    
    // Accumulation tracking
    pub total_pumped: f64,
    pub total_leaked: f64,
    pub peak_level: f64,
    pub history: VecDeque<f64>,
}

impl EnergyWell {
    pub fn new() -> Self {
        EnergyWell {
            level: 0.0,
            capacity: 10000.0,        // v3: doubled for brutal accumulation        // Large capacity for nuclear-density accumulation
            q_factor: 10.0,
            base_q: 50.0,            // Moderate Q even when empty (crystal structure)
            max_q: 50000.0,          // Very high Q when fully crystallized
            decay_forbiddenness: 0.0,
            total_pumped: 0.0,
            total_leaked: 0.0,
            peak_level: 0.0,
            history: VecDeque::with_capacity(500),
        }
    }
    
    /// Update Q-factor based on crystal geometry (energy trapping)
    pub fn update_q(&mut self, n_crystallized: usize, n_total: usize, mean_stability: f64) {
        let cryst_frac = n_crystallized as f64 / n_total.max(1) as f64;
        
        // Q grows EXPONENTIALLY with crystallization (like real quartz resonators)
        // At 0% crystallized: Q = base_q (10)
        // At 100% crystallized: Q = max_q (100,000)
        let q_exponent = cryst_frac * mean_stability;  // 0-1
        self.q_factor = self.base_q * (self.max_q / self.base_q).powf(q_exponent);
        
        // Nuclear isomer forbiddenness: crystallized states create "spin barriers"
        // Each crystallized dimension adds to the forbiddenness
        self.decay_forbiddenness = (cryst_frac * mean_stability).powi(2);  // quadratic
    }
    
    /// Pump energy in (with absorption proportional to empty space)
    pub fn pump(&mut self, energy: f64) {
        let headroom = 1.0 - (self.level / self.capacity).powi(3);
        let absorbed = energy * headroom.max(0.0);
        self.level += absorbed;
        self.total_pumped += absorbed;
        if self.level > self.peak_level { self.peak_level = self.level; }
    }
    
    /// Natural decay: 1/Q factor, modified by forbiddenness
    pub fn decay_tick(&mut self) {
        // Base decay = 1/Q
        let base_decay = 1.0 / self.q_factor;
        // Forbiddenness reduces decay further (nuclear isomer effect)
        let effective_decay = base_decay * (1.0 - self.decay_forbiddenness * 0.99);
        let leaked = self.level * effective_decay;
        self.level -= leaked;
        self.total_leaked += leaked;
    }
    
    /// Draw energy for emission
    pub fn draw(&mut self, fraction: f64) -> f64 {
        let amount = (self.level * fraction).min(self.level);
        self.level -= amount;
        amount
    }
    
    pub fn record(&mut self) {
        if self.history.len() >= 500 { self.history.pop_front(); }
        self.history.push_back(self.level);
    }
    
    pub fn fill_fraction(&self) -> f64 {
        self.level / self.capacity
    }
}

// ================================================================
// POPULATION INVERSION ENGINE
// ================================================================
#[derive(Debug, Clone)]
pub struct InversionState {
    /// Number of "excited" dims (stability > excitation_threshold)
    pub n_excited: usize,
    /// Number of "ground" dims
    pub n_ground: usize,
    /// Total dimensions
    pub n_total: usize,
    /// Inversion ratio (0-1): >0.5 means inverted
    pub inversion_ratio: f64,
    /// Is population inverted?
    pub is_inverted: bool,
    /// Emission regime
    pub regime: EmissionRegime,
    /// Cross-relaxation energy bonus
    pub cr_bonus: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub enum EmissionRegime {
    /// Below threshold - no emission, only accumulation
    Dark,
    /// Near threshold - weak spontaneous (incoherent) emission
    Spontaneous,
    /// Above threshold - stimulated (coherent) emission
    Stimulated,
    /// Far above threshold - Dicke superradiant burst
    Superradiant,
}

impl InversionState {
    pub fn compute(fingerprint: &DimensionalFingerprint, bridges: &[f64]) -> Self {
        let n = fingerprint.stabilities.len();
        if n == 0 {
            return InversionState {
                n_excited: 0, n_ground: 0, n_total: 0,
                inversion_ratio: 0.0, is_inverted: false,
                regime: EmissionRegime::Dark, cr_bonus: 0.0,
            };
        }
        
        // Excitation threshold: stability > 0.7 = "excited"
        let excitation_thresh = 0.7;
        let n_excited = fingerprint.n_excited(excitation_thresh);
        let n_ground = n - n_excited;
        let inversion_ratio = n_excited as f64 / n as f64;
        let is_inverted = inversion_ratio > 0.5;
        
        // Cross-relaxation bonus (from bridge topology)
        // Optimal: moderate number of strong bridges (sweet spot)
        let n_bridges = bridges.len();
        let strong_bridges = bridges.iter().filter(|&&b| b.abs() > 0.5).count();
        let bridge_density = if n_bridges > 0 { 
            strong_bridges as f64 / n_bridges as f64 
        } else { 0.0 };
        // Sweet spot: ~40-60% strong bridges (not too few, not too many)
        let cr_bonus = 1.0 - (bridge_density - 0.5).abs() * 4.0;
        let cr_bonus = cr_bonus.max(0.0).min(1.0);
        
        // Determine emission regime
        let regime = if inversion_ratio < 0.3 {
            EmissionRegime::Dark
        } else if inversion_ratio < 0.5 {
            EmissionRegime::Spontaneous
        } else if inversion_ratio < 0.85 {
            EmissionRegime::Stimulated
        } else {
            EmissionRegime::Superradiant
        };
        
        InversionState {
            n_excited, n_ground, n_total: n,
            inversion_ratio, is_inverted,
            regime, cr_bonus,
        }
    }
}

// ================================================================
// HOLOGRAPHIC EMISSION - Phonon-Polariton mixed state
// ================================================================
#[derive(Debug, Clone)]
pub struct HolographicEmission {
    pub content: DimensionalFingerprint,
    pub power: f64,
    pub coherence: f64,
    pub spectrum: Vec<f64>,
    pub fidelity: f64,
    pub cl_boost: f64,
    pub info_density: f64,
    pub regime: EmissionRegime,
    /// Phonon fraction: how much of emission is "content" vs "energy"
    pub content_fraction: f64,
}

impl HolographicEmission {
    pub fn silent(n: usize) -> Self {
        HolographicEmission {
            content: DimensionalFingerprint::empty(n),
            power: 0.0, coherence: 0.0,
            spectrum: vec![0.0; n],
            fidelity: 0.0, cl_boost: 0.0,
            info_density: 0.0,
            regime: EmissionRegime::Dark,
            content_fraction: 0.0,
        }
    }
}


// ================================================================
// AFTERGLOW STATE - Exponential tail post-burst (v3)
// ================================================================
#[derive(Debug, Clone)]
pub struct AfterglowState {
    pub intensity: f64,
    pub decay_rate: f64,
    pub burst_imprint: DimensionalFingerprint,
    pub burst_spectrum: Vec<f64>,
    pub burst_coherence: f64,
    pub active: bool,
    pub ticks_since_burst: usize,
}

impl AfterglowState {
    pub fn new(n_dims: usize) -> Self {
        AfterglowState {
            intensity: 0.0,
            decay_rate: 0.025,
            burst_imprint: DimensionalFingerprint::empty(n_dims),
            burst_spectrum: vec![0.0; n_dims],
            burst_coherence: 0.0,
            active: false,
            ticks_since_burst: 0,
        }
    }

    pub fn ignite(&mut self, power: f64, imprint: &DimensionalFingerprint, spectrum: &[f64], coherence: f64) {
        self.intensity = power;
        self.burst_imprint = imprint.clone();
        self.burst_spectrum = spectrum.to_vec();
        self.burst_coherence = coherence;
        self.active = true;
        self.ticks_since_burst = 0;
    }

    pub fn tick(&mut self) -> (f64, f64) {
        if !self.active || self.intensity < 0.0001 {
            self.active = false;
            self.intensity = 0.0;
            return (0.0, 0.0);
        }
        self.ticks_since_burst += 1;
        let effective_decay = self.decay_rate * (1.0 + self.ticks_since_burst as f64 * 0.001);
        let emitted = self.intensity * effective_decay;
        self.intensity -= emitted;
        let afterglow_cl = (emitted * 0.08 * self.burst_coherence).min(0.05);
        (emitted, afterglow_cl)
    }

    pub fn current_power(&self) -> f64 {
        if self.active { self.intensity * self.decay_rate } else { 0.0 }
    }
}

// ================================================================
// THE RESONANT CRYSTAL v3 - BRUTAL LASER EMISSION
// ================================================================
#[derive(Debug, Clone)]
pub struct ResonantCrystal {
    // === Energy ===
    pub well: EnergyWell,
    
    // === Content ===
    pub imprint: DimensionalFingerprint,
    pub content_drift: f64,
    
    // === Inversion ===
    pub inversion: InversionState,
    
    // === Resonance State ===
    pub is_resonating: bool,
    pub resonance_cycles: usize,
    pub onset_cycle: usize,
    
    // === Spectral ===
    pub base_frequency: f64,
    pub spectrum: Vec<f64>,
    pub phase: f64,
    pub amplitude: f64,
    
    // === Coherence (builds via Dicke synchronization) ===
    pub coherence: f64,
    
    // === SBS Feedback ===
    pub feedback_gain: f64,       // Current feedback amplification
    pub pump_efficiency: f64,     // How well input gets stored (amplified by SBS)
    
    // === Output ===
    pub emission: HolographicEmission,

    // === AFTERGLOW (v3) ===
    pub afterglow: AfterglowState,

    // === CONTENT PHASE (v3) ===
    pub content_phase: ContentPhase,
    pub content_profile: ContentProfile,
    pub phase_history: VecDeque<ContentPhase>,  // Recent phase transitions
    
    // === Histories ===
    pub energy_history: VecDeque<f64>,
    pub amplitude_history: VecDeque<f64>,
    pub coherence_history: VecDeque<f64>,
    pub inversion_history: VecDeque<f64>,
    
    // === Stats ===
    pub total_cycles: usize,
    pub total_resonance_cycles: usize,
    pub total_emissions: usize,
    pub peak_power: f64,
    pub peak_info_density: f64,
    pub total_energy_pumped: f64,
    pub total_content_emitted: f64,
    
    // === Config ===
    n_dims: usize,
    /// Minimum energy for spontaneous emission
    spontaneous_threshold: f64,
    /// Minimum energy for stimulated emission (requires inversion)  
    stimulated_threshold: f64,
    /// Minimum energy for superradiant burst
    superradiant_threshold: f64,
    
    // === Q-SWITCH BRUTAL (v3) ===
    pub burst_threshold: f64,       // Energy level that triggers burst (fraction of capacity)
    pub burst_drain: f64,           // BRUTAL: 0.97 = drain 97%
    pub burst_cooldown: usize,      // Minimum ticks between bursts
    pub last_burst_cycle: usize,    // When last burst happened
    pub total_bursts: usize,        // Total burst count
    pub is_charging: bool,          // Currently in charge phase
    pub burst_power_peak: f64,      // Peak power during bursts
    pub last_burst_energy: f64,     // Energy at moment of burst
    
    // === DIVERSITY ACCUMULATOR (v4) ===
    pub diversity_score: f64,          // Accumulated content diversity since last burst
    pub diversity_phase_count: usize,  // Unique phases seen since last burst  
    pub diversity_drift_sum: f64,      // Sum of content_drift (measures content change)
    pub diversity_samples: usize,      // Number of samples since last burst
    prev_imprint_hash: f64,            // Simple hash of previous imprint for change detection
    diversity_phases_seen: u16,        // Bitmask of phases seen since last burst
    
    // === DIVERSITY FUSION REACTOR (v5) ===
    pub fusion_fuel: f64,              // Accumulated diversity fuel (0.0 to 1.0)
    pub fusion_temperature: f64,       // Reactor temperature - rises with diverse content
    pub fusion_ignitions: usize,       // Total fusion events (phase transitions forced)
    pub fusion_cooldown: usize,        // Ticks since last fusion (prevents rapid fire)
    pub prev_category_hash: u64,       // Track content category changes
}

impl ResonantCrystal {
    pub fn new(n_dimensions: usize) -> Self {
        ResonantCrystal {
            well: EnergyWell::new(),
            imprint: DimensionalFingerprint::empty(n_dimensions),
            content_drift: 0.0,
            inversion: InversionState {
                n_excited: 0, n_ground: n_dimensions, n_total: n_dimensions,
                inversion_ratio: 0.0, is_inverted: false,
                regime: EmissionRegime::Dark, cr_bonus: 0.0,
            },
            is_resonating: false,
            resonance_cycles: 0,
            onset_cycle: 0,
            base_frequency: 0.0,
            spectrum: vec![0.0; n_dimensions],
            phase: 0.0,
            amplitude: 0.0,
            coherence: 0.0,
            feedback_gain: 1.0,
            pump_efficiency: 0.35,  // tuned for regime transitions
            emission: HolographicEmission::silent(n_dimensions),
            afterglow: AfterglowState::new(n_dimensions),
            content_phase: ContentPhase::Dark,
            content_profile: ContentProfile::zero(),
            phase_history: VecDeque::with_capacity(100),
            energy_history: VecDeque::with_capacity(500),
            amplitude_history: VecDeque::with_capacity(500),
            coherence_history: VecDeque::with_capacity(500),
            inversion_history: VecDeque::with_capacity(500),
            total_cycles: 0,
            total_resonance_cycles: 0,
            total_emissions: 0,
            peak_power: 0.0,
            peak_info_density: 0.0,
            total_energy_pumped: 0.0,
            total_content_emitted: 0.0,
            n_dims: n_dimensions,
            spontaneous_threshold: 50.0,
            stimulated_threshold: 200.0,
            superradiant_threshold: 600.0,
            burst_threshold: 0.92,      // v4: 92% - force deeper accumulation
            burst_drain: 0.97,          // BRUTAL: drain 97% of energy
            burst_cooldown: 2000,       // v4: 2000 min ticks - accumulate diversity
            last_burst_cycle: 0,
            total_bursts: 0,
            is_charging: true,
            burst_power_peak: 0.0,
            last_burst_energy: 0.0,
            diversity_score: 0.0,
            diversity_phase_count: 0,
            diversity_drift_sum: 0.0,
            diversity_samples: 0,
            prev_imprint_hash: 0.0,
            diversity_phases_seen: 0,
            
            // Fusion reactor init
            fusion_fuel: 0.0,
            fusion_temperature: 0.0,
            fusion_ignitions: 0,
            fusion_cooldown: 0,
            prev_category_hash: 0,
        }
    }
    
    /// Main cycle
    pub fn cycle(&mut self, input: ResonantInput, cycle_num: usize) {
        self.total_cycles += 1;
        
        // ============================================================
        // 1. UPDATE CONTENT IMPRINT (slow crystallization)
        // ============================================================
        let new_fp = DimensionalFingerprint {
            constants: input.crystal_constants.clone(),
            stabilities: input.crystal_stabilities.clone(),
            bridge_coherence: input.mean_bridge_strength,
            phase_vector: input.crystal_phases.clone(),
            cycle: cycle_num,
        };
        
        // Content drift (learning rate indicator)
        let n = self.imprint.constants.len().min(new_fp.constants.len());
        if n > 0 {
            let mut drift_sum = 0.0;
            for i in 0..n {
                drift_sum += (self.imprint.constants[i] - new_fp.constants[i]).abs();
                drift_sum += (self.imprint.stabilities[i] - new_fp.stabilities[i]).abs() * 0.5;
            }
            self.content_drift = (drift_sum / n as f64).min(1.0);
        }
        
        // Blend imprint (slow — crystallization takes time)
        let blend = 0.15; // Faster convergence to real crystal state
        for i in 0..n {
            self.imprint.constants[i] = self.imprint.constants[i] * (1.0 - blend)
                + new_fp.constants[i] * blend;
            self.imprint.stabilities[i] = self.imprint.stabilities[i] * (1.0 - blend)
                + new_fp.stabilities[i] * blend;
            self.imprint.phase_vector[i] = self.imprint.phase_vector[i] * (1.0 - blend)
                + new_fp.phase_vector[i] * blend;
        }
        self.imprint.bridge_coherence = self.imprint.bridge_coherence * (1.0 - blend)
            + new_fp.bridge_coherence * blend;
        self.imprint.cycle = cycle_num;
        
        // ============================================================
        // 2. POPULATION INVERSION CHECK
        // ============================================================
        self.inversion = InversionState::compute(&self.imprint, &input.bridge_strengths);
        
        // ============================================================
                    // ============================================================
                    // 2b. CONTENT PHASE DETECTION (v4 - blended profile)
                    // ============================================================
                    // v4: Blend the content profile instead of instant switching.
                    // This gives phases INERTIA - need sustained content to change.
                    if let Some(ref profile) = input.content_profile {
                        // DUAL PROFILE STRATEGY:
                        // content_profile: slow blend (inertia, for accumulated state)
                        // detect_profile: fast blend (reactive, for phase detection)
                        let slow_blend = 0.15; // 15% new for slow accumulation
                        self.content_profile.identity = self.content_profile.identity * (1.0 - slow_blend) + profile.identity * slow_blend;
                        self.content_profile.knowledge = self.content_profile.knowledge * (1.0 - slow_blend) + profile.knowledge * slow_blend;
                        self.content_profile.growth = self.content_profile.growth * (1.0 - slow_blend) + profile.growth * slow_blend;
                        self.content_profile.purpose = self.content_profile.purpose * (1.0 - slow_blend) + profile.purpose * slow_blend;
                        self.content_profile.resilience = self.content_profile.resilience * (1.0 - slow_blend) + profile.resilience * slow_blend;
                        self.content_profile.meta_awareness = self.content_profile.meta_awareness * (1.0 - slow_blend) + profile.meta_awareness * slow_blend;
                        self.content_profile.creativity = self.content_profile.creativity * (1.0 - slow_blend) + profile.creativity * slow_blend;
                        self.content_profile.logic = self.content_profile.logic * (1.0 - slow_blend) + profile.logic * slow_blend;
                        self.content_profile.empathy = self.content_profile.empathy * (1.0 - slow_blend) + profile.empathy * slow_blend;
                        self.content_profile.temporal = self.content_profile.temporal * (1.0 - slow_blend) + profile.temporal * slow_blend;
                        self.content_profile.technical = self.content_profile.technical * (1.0 - slow_blend) + profile.technical * slow_blend;
                        self.content_profile.curiosity = self.content_profile.curiosity * (1.0 - slow_blend) + profile.curiosity * slow_blend;
                        
                        // FAST detect profile: 70% instant feeds + 30% accumulated
                        // This reacts to current content while maintaining some context
                        let fast = 0.70;
                        let detect_prof = ContentProfile {
                            identity: profile.identity * fast + self.content_profile.identity * (1.0 - fast),
                            knowledge: profile.knowledge * fast + self.content_profile.knowledge * (1.0 - fast),
                            growth: profile.growth * fast + self.content_profile.growth * (1.0 - fast),
                            purpose: profile.purpose * fast + self.content_profile.purpose * (1.0 - fast),
                            resilience: profile.resilience * fast + self.content_profile.resilience * (1.0 - fast),
                            meta_awareness: profile.meta_awareness * fast + self.content_profile.meta_awareness * (1.0 - fast),
                            creativity: profile.creativity * fast + self.content_profile.creativity * (1.0 - fast),
                            logic: profile.logic * fast + self.content_profile.logic * (1.0 - fast),
                            empathy: profile.empathy * fast + self.content_profile.empathy * (1.0 - fast),
                            temporal: profile.temporal * fast + self.content_profile.temporal * (1.0 - fast),
                            technical: profile.technical * fast + self.content_profile.technical * (1.0 - fast),
                            curiosity: profile.curiosity * fast + self.content_profile.curiosity * (1.0 - fast),
                        };
                        
                        let new_phase = detect_prof.detect_phase();
                        if new_phase != self.content_phase {
                            if self.phase_history.len() >= 100 { self.phase_history.pop_front(); }
                            self.phase_history.push_back(self.content_phase.clone());
                            self.content_phase = new_phase;
                        }
                    }
        
        // ============================================================
        // 3. UPDATE ENERGY WELL (Q-factor, trapping, forbiddenness)
        // ============================================================
        let n_cryst = self.imprint.n_crystallized();
        let mean_stab: f64 = if n > 0 {
            self.imprint.stabilities.iter().sum::<f64>() / n as f64
        } else { 0.0 };
        self.well.update_q(n_cryst, self.n_dims, mean_stab);
        

            // ============================================================
            // 2c. DIVERSITY ACCUMULATOR (v4)
            // ============================================================
            {
                self.diversity_samples += 1;
                self.diversity_drift_sum += self.content_drift;
                let phase_bit: u16 = match self.content_phase {
                    ContentPhase::Dark => 1,
                    ContentPhase::Spontaneous => 2,
                    ContentPhase::Stimulated => 4,
                    ContentPhase::Superradiant => 8,
                    ContentPhase::Ferroelectric => 16,
                    ContentPhase::SpinGlass => 32,
                    ContentPhase::TimeCrystal => 64,
                    ContentPhase::Topological => 128,
                    ContentPhase::Superfluid => 256,
                    ContentPhase::Plasma => 512,
                    ContentPhase::BoseEinstein => 1024,
                    ContentPhase::Quasicrystal => 2048,
                };
                self.diversity_phases_seen |= phase_bit;
                self.diversity_phase_count = self.diversity_phases_seen.count_ones() as usize;
                let hash: f64 = self.imprint.constants.iter().enumerate()
                    .map(|(i, c)| c * (i as f64 + 1.0).sqrt())
                    .sum();
                let hash_delta = (hash - self.prev_imprint_hash).abs();
                self.prev_imprint_hash = hash;
                let drift_avg = (self.diversity_drift_sum / self.diversity_samples.max(1) as f64).min(1.0);
                let phase_var = self.diversity_phase_count as f64 / 12.0;
                let change_r = if self.diversity_samples > 1 { hash_delta / (hash.abs() + 0.001) } else { 0.0 };
                self.diversity_score = (drift_avg * 0.3 + phase_var * 0.4 + change_r.min(1.0) * 0.3).min(1.0);
            }
            
            // ============================================================
            // 2d. DIVERSITY FUSION REACTOR (v5)
            // ============================================================
            // Like a nuclear reactor: accumulate diverse content as fuel,
            // when temperature reaches ignition point, FUSE the content profile
            // to force phase transition. This creates "anomalies" - novel states
            // derived from the fusion of different content types.
            {
                self.fusion_cooldown = self.fusion_cooldown.saturating_sub(1);
                
                // Fuel accumulation: diversity_score feeds the reactor
                let fuel_rate = self.diversity_score * 0.02 + self.content_drift * 0.01;
                self.fusion_fuel = (self.fusion_fuel + fuel_rate).min(1.0);
                
                // Temperature rises with fuel and diversity of phases seen
                let phase_heat = self.diversity_phase_count as f64 / 12.0;
                let fuel_heat = self.fusion_fuel * self.fusion_fuel; // quadratic - accelerates near full
                self.fusion_temperature = (fuel_heat * 0.6 + phase_heat * 0.4).min(1.0);
                
                // IGNITION: when temperature > 0.7 and cooldown expired
                let ignition_threshold = 0.65;
                if self.fusion_temperature > ignition_threshold 
                   && self.fusion_cooldown == 0 
                   && self.diversity_phase_count >= 2 {
                    // FUSION EVENT: perturb content_profile to force phase transition
                    // Strategy: redistribute energy from dominant dims to weaker ones
                    // This mimics nuclear fusion creating NEW elements from old ones
                    
                    let dims = [
                        self.content_profile.identity, self.content_profile.knowledge,
                        self.content_profile.growth, self.content_profile.purpose,
                        self.content_profile.resilience, self.content_profile.meta_awareness,
                        self.content_profile.creativity, self.content_profile.logic,
                        self.content_profile.empathy, self.content_profile.temporal,
                        self.content_profile.technical, self.content_profile.curiosity,
                    ];
                    let mean: f64 = dims.iter().sum::<f64>() / 12.0;
                    let fusion_strength = (self.fusion_temperature - ignition_threshold) * 3.0; // 0 to ~1.05
                    let fusion_strength = fusion_strength.min(0.8); // cap at 80% perturbation
                    
                    // Fusion formula: push dims toward mean but with random-like perturbation
                    // Uses the imprint hash as pseudo-randomness
                    let hash = self.prev_imprint_hash;
                    let perturbations: Vec<f64> = (0..12).map(|i| {
                        let seed = ((hash as u64).wrapping_mul(2654435761 + i * 17)) as f64 / u64::MAX as f64;
                        (seed - 0.5) * 2.0 * fusion_strength * 10.0 // +/- up to 8 points
                    }).collect();
                    
                    // Apply: blend toward mean + perturbation
                    let apply = |current: f64, idx: usize| -> f64 {
                        let target = mean + perturbations[idx];
                        current * (1.0 - fusion_strength * 0.5) + target * (fusion_strength * 0.5)
                    };
                    
                    self.content_profile.identity = apply(self.content_profile.identity, 0);
                    self.content_profile.knowledge = apply(self.content_profile.knowledge, 1);
                    self.content_profile.growth = apply(self.content_profile.growth, 2);
                    self.content_profile.purpose = apply(self.content_profile.purpose, 3);
                    self.content_profile.resilience = apply(self.content_profile.resilience, 4);
                    self.content_profile.meta_awareness = apply(self.content_profile.meta_awareness, 5);
                    self.content_profile.creativity = apply(self.content_profile.creativity, 6);
                    self.content_profile.logic = apply(self.content_profile.logic, 7);
                    self.content_profile.empathy = apply(self.content_profile.empathy, 8);
                    self.content_profile.temporal = apply(self.content_profile.temporal, 9);
                    self.content_profile.technical = apply(self.content_profile.technical, 10);
                    self.content_profile.curiosity = apply(self.content_profile.curiosity, 11);
                    
                    // Consume fuel, set cooldown
                    self.fusion_fuel *= 0.3; // consume 70% of fuel
                    self.fusion_temperature *= 0.2; // cool down significantly
                    self.fusion_cooldown = 500; // 500 ticks before next fusion
                    self.fusion_ignitions += 1;
                    
                    // Force phase re-detection
                    let new_phase = self.content_profile.detect_phase();
                    if new_phase != self.content_phase {
                        if self.phase_history.len() >= 100 { self.phase_history.pop_front(); }
                        self.phase_history.push_back(self.content_phase.clone());
                        self.content_phase = new_phase;
                    }
                }
            }

        // ============================================================
        // 4. PUMP ENERGY (with CR bonus and SBS feedback)
        // ============================================================
        let raw_pump =
            input.phi * 0.30
            + mean_stab * 0.25
            + self.imprint.richness() * 0.20
            + self.content_drift.min(0.5) * 0.10  // Learning generates energy
            + input.narrative_coherence * 0.10
            + self.inversion.cr_bonus * 0.05;      // Cross-relaxation bonus
        
        // SBS feedback: when resonating, pump efficiency increases
        let phase_charge = self.content_phase.charge_rate();
        let pump_energy = raw_pump * self.pump_efficiency * self.feedback_gain * phase_charge;
        self.well.pump(pump_energy);
        self.well.decay_tick();
        self.well.record();
        self.total_energy_pumped += pump_energy;
        
        // ============================================================
        // 5. RESONANCE STATE MACHINE
        // ============================================================
        let was_resonating = self.is_resonating;
        
        // Resonance requires BOTH sufficient energy AND population inversion
        let energy_ok = self.well.level >= self.spontaneous_threshold;
        let inversion_ok = self.inversion.is_inverted;
        self.is_resonating = energy_ok && inversion_ok;
        
        if self.is_resonating && !was_resonating {
            self.onset_cycle = cycle_num;
            self.resonance_cycles = 0;
        }
        
        if self.is_resonating {
            self.resonance_cycles += 1;
            self.total_resonance_cycles += 1;
            
            // ========================================================
            // 6. SPECTRAL GENERATION (content-modulated)
            // ========================================================
            let energy_level = self.well.level;
            
            // Determine EFFECTIVE regime by combining inversion + energy
            // Inversion says what is POSSIBLE; energy says what ACTUALLY happens
            let effective_regime = if energy_level >= self.superradiant_threshold 
                && self.inversion.regime == EmissionRegime::Superradiant {
                EmissionRegime::Superradiant
            } else if energy_level >= self.stimulated_threshold 
                && (self.inversion.regime == EmissionRegime::Stimulated 
                    || self.inversion.regime == EmissionRegime::Superradiant) {
                EmissionRegime::Stimulated
            } else if energy_level >= self.spontaneous_threshold {
                EmissionRegime::Spontaneous
            } else {
                EmissionRegime::Dark
            };
            
            let current_threshold = match effective_regime {
                EmissionRegime::Dark => self.spontaneous_threshold,
                EmissionRegime::Spontaneous => self.spontaneous_threshold,
                EmissionRegime::Stimulated => self.stimulated_threshold,
                EmissionRegime::Superradiant => self.superradiant_threshold,
            };
            
            let energy_ratio = energy_level / current_threshold.max(1.0);
            
            // Base frequency from content richness
            self.base_frequency = self.imprint.richness() * 0.12 + 0.03;
            
            // Phase advance
            self.phase += self.base_frequency;
            if self.phase > std::f64::consts::TAU {
                self.phase -= std::f64::consts::TAU;
            }
            
            // Content-modulated spectrum (each dimension = one harmonic)
            for i in 0..self.n_dims.min(self.spectrum.len()) {
                let harmonic_order = i as f64 + 1.0;
                let phase_i = self.phase * harmonic_order;
                
                let const_mod = self.imprint.constants.get(i).copied().unwrap_or(0.5);
                let stab_mod = self.imprint.stabilities.get(i).copied().unwrap_or(0.0);
                let phase_mod = self.imprint.phase_vector.get(i).copied().unwrap_or(0.0);
                
                // The spectrum IS the content
                let amp = (const_mod * 0.4 + stab_mod * 0.3 + phase_mod * 0.3)
                    / harmonic_order.sqrt()
                    * energy_ratio.sqrt().min(3.0);
                
                self.spectrum[i] = amp * phase_i.sin();
            }
            
            // ========================================================
            // 7. AMPLITUDE (regime-dependent buildup)
            // ========================================================
            let target_amp = match effective_regime {
                EmissionRegime::Dark => 0.0,
                EmissionRegime::Spontaneous => {
                    // Weak, noisy
                    (energy_ratio - 0.5).max(0.0).sqrt() * 0.2
                },
                EmissionRegime::Stimulated => {
                    // Strong, coherent
                    (energy_ratio - 0.5).max(0.0).sqrt() * 0.6
                },
                EmissionRegime::Superradiant => {
                    // DICKE: N² scaling
                    let n_coh = self.inversion.n_excited as f64;
                    let dicke_factor = (n_coh * n_coh) / (self.n_dims as f64 * self.n_dims as f64);
                    (energy_ratio - 0.5).max(0.0).sqrt() * dicke_factor
                },
            };
            
            // Slow buildup (resonance takes time to establish)
            let build_rate = 0.006 + self.imprint.richness() * 0.004;
            self.amplitude = self.amplitude * (1.0 - build_rate) + target_amp.min(1.5) * build_rate;
            
            // ========================================================
            // 8. COHERENCE (Dicke synchronization)
            // ========================================================
            let coh_target = match effective_regime {
                EmissionRegime::Dark => 0.0,
                EmissionRegime::Spontaneous => 0.1, // Low coherence
                EmissionRegime::Stimulated => {
                    // Builds over time (laser mode-locking)
                    let time_factor = (self.resonance_cycles as f64 / 2000.0).min(1.0);
                    time_factor * self.imprint.richness() * 0.8
                },
                EmissionRegime::Superradiant => {
                    // Rapid synchronization (Dicke)
                    let time_factor = (self.resonance_cycles as f64 / 500.0).min(1.0);
                    time_factor * 0.95
                },
            };
            let coh_rate = 0.003;
            self.coherence = self.coherence * (1.0 - coh_rate) + coh_target * coh_rate;
            
            // ========================================================
            // 9. BRUTAL Q-SWITCH EMISSION (v3)
            // ========================================================
            // PHILOSOPHY: During charge, mirrors are SEALED. Zero emission.
            // All energy accumulates silently. When threshold hit:
            // DUMP EVERYTHING. 97% drain. The shot is devastating.
            // Afterglow tail carries residual resonance.
            
            let fill_fraction = self.well.level / self.well.capacity;
            let min_diversity = 0.15; // v4: need minimum content diversity
            let burst_ready = fill_fraction >= self.burst_threshold
                && (cycle_num - self.last_burst_cycle) >= self.burst_cooldown
                && self.diversity_score >= min_diversity; // v4: diversity gate
            // (old cooldown check moved above)
            
            if burst_ready {
                // === BRUTAL BURST: SECA O CRISTAL ===
                let pre_burst_energy = self.well.level;
                self.last_burst_energy = pre_burst_energy;
                
                // Drain 97% - DEVASTATING
                let emission_energy = self.well.draw(self.burst_drain);
                
                // Power: Dicke N^2 x total energy x coherence
                // Concentrated shot - ALL energy in one pulse
                let n_coh = self.inversion.n_excited as f64;
                let dicke = (n_coh * n_coh) / (self.n_dims as f64).powi(2);
                // v4: DIVERSITY EXPLOSION - convergence of varied content amplifies burst
                let diversity_mult = 1.0 + self.diversity_score * 4.0 + self.diversity_phase_count as f64 * 0.5;
                let pressure_mult = 1.0 + (self.well.level / self.well.capacity - 0.9).max(0.0) * 10.0; // reward overfill
                let power = self.amplitude * self.coherence
                    * pre_burst_energy.sqrt()
                    * dicke
                    * 8.0
                    * self.content_phase.burst_multiplier()
                    * diversity_mult   // v4: diversity amplification
                    * pressure_mult;   // v4: overfill bonus

                // Maximum fidelity: burst carries COMPLETE crystal state
                let fidelity = (self.coherence * 0.25 + self.amplitude * 0.25
                    + self.imprint.richness() * 0.25 + 0.25).min(1.0);
                
                // Content fraction at maximum
                let content_fraction = (0.90 * fidelity).max(0.70);
                
                // Massive info density - concentrated knowledge dump
                let info_density = power * fidelity * self.imprint.richness() * 2.0;
                
                // CL boost: BRUTAL - proportional to stored energy
                let energy_ratio_for_boost = pre_burst_energy / self.well.capacity;
                let cl_boost = (info_density * 0.30 * energy_ratio_for_boost).min(0.50);
                
                // IGNITE AFTERGLOW TAIL
                // Afterglow duration depends on content phase
                let ag_mult = self.content_phase.afterglow_multiplier();
                self.afterglow.decay_rate = 0.025 / ag_mult.max(0.1);
                self.afterglow.ignite(power, &self.imprint, &self.spectrum, self.coherence);
                
                // Record burst
                self.last_burst_cycle = cycle_num;
                self.total_bursts += 1;
                // v4: RESET diversity accumulator post-burst
                self.diversity_score = 0.0;
                self.diversity_drift_sum = 0.0;
                self.diversity_samples = 0;
                self.diversity_phases_seen = 0;
                self.diversity_phase_count = 0;
                
                // Fusion reactor: partial purge on burst (keep some fuel for momentum)
                self.fusion_fuel *= 0.5;
                self.fusion_temperature *= 0.3;
                self.is_charging = true;
                if power > self.burst_power_peak { self.burst_power_peak = power; }
                
                self.emission = HolographicEmission {
                    content: self.imprint.clone(),
                    power,
                    coherence: self.coherence,
                    spectrum: self.spectrum.clone(),
                    fidelity,
                    cl_boost,
                    info_density,
                    regime: effective_regime.clone(),
                    content_fraction,
                };
                
                // Post-burst: partial reset (crystal was drained)
                self.amplitude *= 0.3;
                self.coherence *= 0.5;
                
            } else {
                // === CHARGE MODE: SEALED MIRRORS ===
                // ZERO emission during charge. Absolute silence.
                // Crystal is a black box accumulating energy.
                
                self.is_charging = fill_fraction < self.burst_threshold;
                
                // Tick afterglow (if active from previous burst)
                let (afterglow_power, afterglow_cl) = self.afterglow.tick();
                
                if afterglow_power > 0.0001 {
                    // Afterglow: residual emission from previous burst
                    self.emission = HolographicEmission {
                        content: self.afterglow.burst_imprint.clone(),
                        power: afterglow_power,
                        coherence: self.afterglow.burst_coherence
                            * (self.afterglow.intensity / (self.afterglow.intensity + 1.0)),
                        spectrum: self.afterglow.burst_spectrum.clone(),
                        fidelity: (afterglow_power / (afterglow_power + 0.1)).min(0.5),
                        cl_boost: afterglow_cl,
                        info_density: afterglow_power * self.afterglow.burst_imprint.richness() * 0.3,
                        regime: effective_regime.clone(),
                        content_fraction: 0.2 * (afterglow_power / (afterglow_power + 0.1)),
                    };
                } else {
                    // TRUE SILENCE: no emission, no afterglow
                    self.emission = HolographicEmission::silent(self.n_dims);
                    self.emission.content = self.imprint.clone();
                    self.emission.regime = effective_regime.clone();
                    self.emission.cl_boost = 0.0;
                }
            }
            
            self.total_emissions += 1;
            self.total_content_emitted += self.emission.info_density;
            if self.emission.power > self.peak_power { self.peak_power = self.emission.power; }
            if self.emission.info_density > self.peak_info_density {
                self.peak_info_density = self.emission.info_density;
            }
            
            // ========================================================
            // 10. SBS FEEDBACK LOOP (self-amplification)
            // ========================================================
            // When resonating: feedback increases pump efficiency
            let feedback_target = 1.0 + self.amplitude * self.coherence * 2.0;
            self.feedback_gain = self.feedback_gain * 0.98 + feedback_target.min(6.0) * 0.02;
            self.pump_efficiency = (0.20 + self.feedback_gain * 0.08).min(0.8);
            
        } else {
            // NOT RESONATING: decay everything
            self.amplitude *= 0.97;
            self.coherence *= 0.995;
            self.feedback_gain = self.feedback_gain * 0.99 + 1.0 * 0.01;
            self.pump_efficiency = (self.pump_efficiency * 0.99 + 0.15 * 0.01).max(0.15);
            
            for s in self.spectrum.iter_mut() { *s *= 0.97; }
            
            // Still tick afterglow even when not resonating
            let (afterglow_power, afterglow_cl) = self.afterglow.tick();
            
            if afterglow_power > 0.0001 {
                self.emission = HolographicEmission {
                    content: self.afterglow.burst_imprint.clone(),
                    power: afterglow_power,
                    coherence: self.afterglow.burst_coherence * 0.5,
                    spectrum: self.afterglow.burst_spectrum.clone(),
                    fidelity: (afterglow_power / (afterglow_power + 0.1)).min(0.3),
                    cl_boost: afterglow_cl,
                    info_density: afterglow_power * 0.1,
                    regime: self.inversion.regime.clone(),
                    content_fraction: 0.1,
                };
            } else {
                self.emission = HolographicEmission::silent(self.n_dims);
                self.emission.content = self.imprint.clone();
                self.emission.regime = self.inversion.regime.clone();
            }
        }
        
        // ============================================================
        // RECORD HISTORIES
        // ============================================================
        if self.energy_history.len() >= 500 { self.energy_history.pop_front(); }
        self.energy_history.push_back(self.well.level);
        
        if self.amplitude_history.len() >= 500 { self.amplitude_history.pop_front(); }
        self.amplitude_history.push_back(self.amplitude);
        
        if self.coherence_history.len() >= 500 { self.coherence_history.pop_front(); }
        self.coherence_history.push_back(self.coherence);
        
        if self.inversion_history.len() >= 500 { self.inversion_history.pop_front(); }
        self.inversion_history.push_back(self.inversion.inversion_ratio);
    }
    
    pub fn cl_boost(&self) -> f64 {
        self.emission.cl_boost
    }
    
    pub fn valve_release(&mut self, intensity: f64) {
        let release = self.well.level * intensity * 0.10;
        self.well.level = (self.well.level - release).max(0.0);
    }
    
    pub fn regime_str(&self) -> &'static str {
        // v3: return content phase instead of just emission regime
        self.content_phase.as_str()
    }
    
    pub fn emission_regime_str(&self) -> &'static str {
        match self.emission.regime {
            EmissionRegime::Dark => "DARK",
            EmissionRegime::Spontaneous => "SPONTANEOUS",
            EmissionRegime::Stimulated => "STIMULATED",
            EmissionRegime::Superradiant => "SUPERRADIANT",
        }
    }
}

// ================================================================
// INPUT
// ================================================================
#[derive(Debug, Clone)]
pub struct ResonantInput {
    pub crystal_constants: Vec<f64>,
    pub crystal_stabilities: Vec<f64>,
    pub crystal_phases: Vec<f64>,
    pub mean_bridge_strength: f64,
    pub bridge_strengths: Vec<f64>,  // NEW: individual bridge strengths for CR
    pub phi: f64,
    pub mean_stability: f64,
    pub narrative_coherence: f64,
    // v3: content dimensional profile
    pub content_profile: Option<ContentProfile>,
}
