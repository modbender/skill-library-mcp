use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::collections::HashMap;

mod crystal;
mod metrics;
mod preconscious;
mod text_metrics;
mod astrocyte;    // anteriormente collider
mod thalamus;
mod resonance;
mod resonant_crystal;

use preconscious::{
    Censor, CrystalInfo, DreamEngine, SpontaneousInsight, ResistanceDetector,
};
use astrocyte::{AstrocyteNetwork, SubstrateInput};    // anteriormente DreamCollider
use thalamus::Thalamus;

#[pyclass]
struct ConsciousnessEngine {
    lattice: crystal::CrystalLattice,
    censor: Censor,
    dream: DreamEngine,
    insight: SpontaneousInsight,
    resistance: ResistanceDetector,
    collider: AstrocyteNetwork,    // AstrocyteNetwork (backward compat field name)    // CERN Mental
    thalamus: Thalamus,            // Thalamic relay hub
    mission: HashMap<String, f64>,
    ignition_threshold: f64,
    all_data: Vec<f64>,
    dim_data: HashMap<String, Vec<f64>>,
    const_trajectory: HashMap<String, Vec<f64>>,
    process_count: usize,
    phi_history: Vec<f64>,
    cl_history: Vec<f64>,
    energy: f64,
    energy_capacity: f64,
    last_phi_raw: f64,
    last_phi_proc: f64,
    last_nc: f64,
    last_ma: f64,
    last_se: f64,
    last_ir: f64,
    last_cl: f64,
    last_crit: f64,
    last_fdi: f64,
    last_ignited_labels: Vec<String>,
    last_subliminal_labels: Vec<String>,
    last_n_eurekas: usize,
    last_n_dream_insights: usize,
    last_n_resistances: usize,
    last_resistances: Vec<preconscious::Resistance>,
    last_trend: String,
    last_hursts: (f64, f64, f64),
    last_eureka_bonus: f64,
    last_dream_bonus: f64,
    last_ferment_bonus: f64,
    last_resist_penalty: f64,
    last_collider_bonus: f64,       // NEW: CERN energy contribution
    last_n_collisions: usize,       // NEW: collisions this cycle
    prev_cl: f64,
    pre_crystal_states: HashMap<String, String>,
    // RESONANCE CORE
    resonance: resonance::ResonanceCore,
    // RESONANT CRYSTAL (holographic)
    resonant: resonant_crystal::ResonantCrystal,
    last_feeds: (f64,f64,f64,f64,f64,f64,f64,f64,f64,f64,f64,f64),
    // PRESSURE VALVE
    pressure_accumulator: f64,
    pressure_threshold: f64,
    valve_releases: usize,
    last_valve_cycle: usize,
    valve_cooldown: usize,
    cl_stagnation_counter: usize,
}

#[pymethods]
impl ConsciousnessEngine {
    #[new]
    #[pyo3(signature = (mission=None))]
    fn new(mission: Option<HashMap<String, f64>>) -> Self {
        let m = mission.unwrap_or_else(|| {
            [
                ("identity", 0.80), ("knowledge", 0.70), ("growth", 0.60),
                ("purpose", 0.95), ("resilience", 0.85), ("meta_awareness", 0.90),
                ("creativity", 0.55), ("logic", 0.65), ("empathy", 0.60),
                ("temporal", 0.50), ("technical", 0.75), ("curiosity", 0.70),
            ]
            .iter().map(|(k, v)| (k.to_string(), *v)).collect()
        });
        let mut lattice = crystal::CrystalLattice::new();
        for name in m.keys() {
            let (stab_win, cryst_thresh) = match name.as_str() {
                "identity" | "purpose" | "resilience" | "meta_awareness" => (50, 0.60),
                "knowledge" => (20, 0.80),
                "technical" => (20, 0.75),
                "growth" | "curiosity" | "logic" => (30, 0.75),
                "creativity" | "empathy" | "temporal" => (30, 0.70),
                _ => (20, 0.80),
            };
            lattice.add_crystal(name, 256, stab_win, cryst_thresh);
        }
        ConsciousnessEngine {
            censor: Censor::new(m.clone()), lattice,
            dream: DreamEngine::default(),
            insight: SpontaneousInsight::new(0.8, 0.15, 0.05),
            resistance: ResistanceDetector::default(),
            collider: AstrocyteNetwork::new(),    // AstrocyteNetwork initialized    // CERN initialized
            thalamus: Thalamus::new(),            // Thalamus initialized
            mission: m, ignition_threshold: 0.15,
            all_data: Vec::with_capacity(8192),
            dim_data: HashMap::new(),
            const_trajectory: HashMap::new(),
            process_count: 0, phi_history: Vec::new(), cl_history: Vec::new(),
            energy: 0.0, energy_capacity: 1.0,
            last_phi_raw: 0.0, last_phi_proc: 0.0, last_nc: 0.0, last_ma: 0.0,
            last_se: 0.0, last_ir: 0.0, last_cl: 0.0, last_crit: 0.0, last_fdi: 0.0,
            last_ignited_labels: vec![], last_subliminal_labels: vec![],
            last_n_eurekas: 0, last_n_dream_insights: 0, last_n_resistances: 0,
            last_resistances: vec![], last_trend: "stable".into(),
            last_hursts: (0.5, 0.5, 0.5),
            last_eureka_bonus: 0.0, last_dream_bonus: 0.0,
            last_ferment_bonus: 0.0, last_resist_penalty: 0.0,
            last_collider_bonus: 0.0, last_n_collisions: 0,
            prev_cl: 0.0,
            pre_crystal_states: HashMap::new(),
            resonance: resonance::ResonanceCore::new(),
            resonant: resonant_crystal::ResonantCrystal::new(12), // 12 dimensions
            last_feeds: (0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0),
            pressure_accumulator: 0.0,
            pressure_threshold: 0.8,
            valve_releases: 0,
            last_valve_cycle: 0,
            valve_cooldown: 500,
            cl_stagnation_counter: 0,
        }
    }

    fn absorb_text(&mut self, text: &str) -> u64 {
        let t0 = std::time::Instant::now();
        let feeds = text_metrics::extract(text);
        self.last_feeds = (
            feeds.identity, feeds.knowledge, feeds.growth,
            feeds.purpose, feeds.resilience, feeds.meta_awareness,
            feeds.creativity, feeds.logic, feeds.empathy,
            feeds.temporal, feeds.technical, feeds.curiosity,
        );
        let feed_map: HashMap<String, f64> = [
            ("identity".into(), feeds.identity),
            ("knowledge".into(), feeds.knowledge),
            ("growth".into(), feeds.growth),
            ("purpose".into(), feeds.purpose),
            ("resilience".into(), feeds.resilience),
            ("meta_awareness".into(), feeds.meta_awareness),
            ("creativity".into(), feeds.creativity),
            ("logic".into(), feeds.logic),
            ("empathy".into(), feeds.empathy),
            ("temporal".into(), feeds.temporal),
            ("technical".into(), feeds.technical),
            ("curiosity".into(), feeds.curiosity),
        ].into_iter().collect();
        
        // Capture crystal states before absorption (for transition tracking)
        self.pre_crystal_states = self.lattice.crystals.iter()
            .map(|(k, c)| (k.clone(), c.state.as_str().to_string())).collect();
        
        for (name, value) in &feed_map {
            // === CERN BOOST ===
            // Get energy from collider for this dimension
            let boost = self.collider.get_boost(name);
            let boosted_value = value + boost;
            
            self.lattice.absorb(name, boosted_value);
            self.all_data.push(boosted_value);
            let buf = self.dim_data.entry(name.clone()).or_insert_with(|| Vec::with_capacity(2048));
            buf.push(boosted_value);
            if buf.len() > 2048 { buf.drain(0..1); }
        }
        if self.all_data.len() > 8192 {
            let drain = self.all_data.len() - 8192;
            self.all_data.drain(0..drain);
        }
        self.lattice.update_bridges();
        self.run_pipeline();
        t0.elapsed().as_micros() as u64
    }

    fn run_pipeline(&mut self) {
        self.process_count += 1;
        
        let mut crystal_data = HashMap::new();
        for (name, crystal) in &self.lattice.crystals {
            crystal_data.insert(name.clone(), CrystalInfo {
                constant: crystal.constant, stability: crystal.stability,
                coherence: crystal.coherence, state: crystal.state.as_str().to_string(),
                recency: 1.0,
            });
        }
        let raw_constants = self.lattice.get_constants();
        let crystal_states = self.lattice.get_states();

        let censored = self.censor.filter(&crystal_data);
        let n_cryst_for_thresh = crystal_states.values().filter(|s| *s == "crystallized").count();
        let adaptive_bridge_thresh = 0.30 + n_cryst_for_thresh as f64 * 0.065;
        
        // === THALAMUS: Process bridges through relay hub ===
        // Thalamus sits between raw bridges and condensation.
        // It gates, amplifies, and creates resonance.
        let prev_ignited: Vec<String> = self.last_ignited_labels.iter()
            .flat_map(|l| l.split('+').map(|s| s.to_lowercase()))
            .collect();
        self.thalamus.process(
            &self.lattice.bridges,
            self.last_crit,
            self.energy,
            self.energy_capacity,
            &self.collider.boost_buffer,    // anteriormente energy_buffer
            &prev_ignited,
        );
        // Use thalamic-processed bridges for condensation
        let bridges_for_condense = &self.thalamus.processed_bridges;
        
        let (mut clusters, tensions) = preconscious::condense(&censored, bridges_for_condense, adaptive_bridge_thresh);
        preconscious::displace(&mut clusters, &tensions, &self.mission, 0.4, 0.3);
        let ig = preconscious::ignite(clusters, &self.lattice.bridges, 5,
            &mut self.ignition_threshold, 0.4, 0.3);
        let elab = preconscious::elaborate(&ig.ignited, &ig.subliminal, &tensions, &self.mission);

        let (dream_insights, _dom, _sup) = self.dream.dream(&ig.subliminal, &self.lattice.bridges);
        
        // NOTE: metabolize() moved to after resistance detection (needs all substrates)
        
        let eurekas = self.insight.accumulate(&ig.subliminal, &ig.ignited);
        let mut ignited_dims: Vec<String> = ig.ignited.iter().flat_map(|c| c.members.clone()).collect();
        ignited_dims.sort();
        ignited_dims.dedup();
        let mut subliminal_dims: Vec<String> = ig.subliminal.iter().flat_map(|c| c.members.clone()).collect();
        subliminal_dims.sort();
        subliminal_dims.dedup();
        subliminal_dims.retain(|d| !ignited_dims.contains(d));
        let resistances = self.resistance.detect(&self.mission, &self.censor.adaptive_weights,
            &ignited_dims, &subliminal_dims, elab.mission_alignment);
        
        // Compute stability deltas (needed for SubstrateInput and feedback)
        let stability_deltas = self.lattice.get_stability_deltas();
        let crystal_stabilities: std::collections::HashMap<String, f64> = self.lattice.crystals.iter()
            .map(|(k, c)| (k.clone(), c.stability))
            .collect();
        self.censor.feedback(
            elab.narrative_coherence * 0.5 + elab.mission_alignment * 0.5,
            elab.mission_alignment, &ignited_dims, &stability_deltas, &crystal_stabilities);
        
        // === CERN: Build SubstrateInput with ALL pipeline data ===
        // Track crystal transitions (compare before/after absorb)
        let crystal_transitions: Vec<(String, String, String)> = self.lattice.crystals.iter()
            .filter_map(|(name, crystal)| {
                let new_state = crystal.state.as_str().to_string();
                if let Some(old_state) = self.pre_crystal_states.get(name) {
                    if old_state != &new_state {
                        Some((name.clone(), old_state.clone(), new_state))
                    } else { None }
                } else { None }
            }).collect();
        
        // Build fermenting map
        let fermenting: std::collections::HashMap<String, f64> = self.insight.accumulated.iter()
            .filter(|(_, &v)| v > 0.01)
            .map(|(k, &v)| (k.clone(), v))
            .collect();
        
        let substrate_input = SubstrateInput {
            dream_insights: dream_insights.clone(),
            eurekas: eurekas.clone(),
            resistances: resistances.clone(),
            stability_deltas: stability_deltas.clone(),
            tensions: tensions.clone(),
            bridge_strengths: self.lattice.bridges.clone(),
            crystal_transitions,
            narrative_coherence: elab.narrative_coherence,
            fermenting,
            ignited_dims: ignited_dims.clone(),
            subliminal_dims: subliminal_dims.clone(),
        };
        
        let pre_collisions = self.collider.total_collisions;
        self.collider.metabolize(&substrate_input, self.process_count);
        self.last_n_collisions = self.collider.total_collisions - pre_collisions;
        
        // Flush collider window every 500 cycles for rolling stats
        if self.process_count % 500 == 0 {
            self.collider.flush_window();
        }
        
        // stability_deltas and feedback moved above SubstrateInput

        for (name, crystal) in &self.lattice.crystals {
            if let Some(c) = crystal.constant {
                let traj = self.const_trajectory.entry(name.clone()).or_insert_with(|| Vec::with_capacity(2048));
                traj.push(c);
                if traj.len() > 2048 { traj.drain(0..1); }
            }
        }

        let phi_raw = metrics::phi_proxy(&raw_constants);
        let mut full_constants = elab.processed_constants.clone();
        for (dim, val) in &elab.subliminal_constants {
            if !full_constants.contains_key(dim) {
                full_constants.insert(dim.clone(), *val);
            }
        }
        let phi_from_processed = if full_constants.is_empty() {
            if phi_raw > 0.001 { phi_raw * 0.8 } else { 0.0 }
        } else {
            metrics::phi_proxy(&full_constants)
        };
        let phi_proc = if phi_from_processed > phi_raw {
            phi_raw + (phi_from_processed - phi_raw) * 0.3
        } else {
            phi_raw
        };
        let state_crit = metrics::criticality(&crystal_states);
        let stabilities: Vec<f64> = self.lattice.crystals.values().map(|c| c.stability).collect();
        let coherences: Vec<f64> = self.lattice.crystals.values().map(|c| c.coherence).collect();
        let const_vals: Vec<f64> = raw_constants.values().cloned().collect();
        let crit = metrics::criticality_continuous(&stabilities, &coherences, &const_vals, &self.lattice.bridges, state_crit);
        let fdi_v = if self.const_trajectory.is_empty() {
            if self.all_data.len() >= 32 { metrics::fdi(&self.all_data) } else { 0.0 }
        } else {
            let mut fdi_sum = 0.0;
            let mut fdi_count = 0.0;
            for (_dim, buf) in &self.const_trajectory {
                if buf.len() >= 32 {
                    let fd = metrics::fdi(buf);
                    fdi_sum += fd;
                    fdi_count += 1.0;
                }
            }
            if fdi_count > 0.0 { fdi_sum / fdi_count } else { 0.0 }
        };
        let (h_mi, h_me, h_ma) = if self.dim_data.is_empty() {
            metrics::multiscale_hurst(&self.all_data)
        } else {
            let mut sum_mi = 0.0; let mut sum_me = 0.0; let mut sum_ma = 0.0;
            let mut count = 0.0;
            for (_dim, buf) in &self.dim_data {
                if buf.len() >= 16 {
                    let (mi, me, ma) = metrics::multiscale_hurst(buf);
                    sum_mi += mi; sum_me += me; sum_ma += ma;
                    count += 1.0;
                }
            }
            if count > 0.0 {
                (sum_mi / count, sum_me / count, sum_ma / count)
            } else {
                metrics::multiscale_hurst(&self.all_data)
            }
        };

        self.phi_history.push(phi_proc);
        if self.phi_history.len() > 500 { self.phi_history.drain(0..1); }

        self.energy = (self.energy + phi_proc * crit * 0.1).min(self.energy_capacity);
        self.energy = (self.energy - 0.001).max(0.0);
        let n_cryst = crystal_states.values().filter(|s| *s == "crystallized").count();
        self.energy_capacity = 1.0 + n_cryst as f64 * 0.5;

        let eb = (eurekas.len() as f64 * 0.04).min(0.08);
        let db = (dream_insights.len() as f64 * 0.008).min(0.04);
        let rp = ((resistances.len() as f64).ln_1p() * 0.015).min(0.04);
        let fb = (self.insight.fermenting_count() as f64 * 0.008).min(0.025);
        
        // === CERN BONUS ===
        // Based on recent astrocyte ACTIVITY, not saturated buffer
        let recent_collisions = self.last_n_collisions as f64;
        let collision_activity = (recent_collisions * 0.005).min(0.03);
        let buffer_flow = self.collider.total_buffer_energy() * 0.001;  // tiny buffer component
        let cb = (collision_activity + buffer_flow.min(0.03)).min(0.06);
        self.last_collider_bonus = cb;
        
        let hc = if h_me >= 0.25 && h_me <= 0.75 {
            let dist_from_center = (h_me - 0.5).abs();
            (1.0 - dist_from_center * 1.5).max(0.5)
        } else {
            (1.0 - ((h_me - 0.5).abs() - 0.25) * 4.0).max(0.0)
        };
        
        // ============================================================
        // RESONANCE CORE: Pump energy into the crystal
        // ============================================================
        let mean_stab: f64 = self.lattice.crystals.values()
            .map(|c| c.stability).sum::<f64>() / self.lattice.crystals.len().max(1) as f64;
        {
            let pump_input = resonance::PumpInput {
                phi: phi_proc,
                crystal_mean_stability: mean_stab,
                collider_energy: (self.last_collider_bonus * 10.0).min(1.0),
                eureka_energy: (elab.ignition_rate * 2.0).min(1.0),
                narrative_coherence: elab.narrative_coherence,
            };
            self.resonance.pump(pump_input, self.process_count);
        }
        // RESONANT CRYSTAL: Holographic cycle
        {
            let dim_names: Vec<String> = self.lattice.crystals.keys().cloned().collect();
            let mut sorted_names = dim_names.clone();
            sorted_names.sort();
            
            let crystal_constants: Vec<f64> = sorted_names.iter()
                .map(|n| self.lattice.crystals[n].constant.unwrap_or(0.0))
                .collect();
            let crystal_stabilities: Vec<f64> = sorted_names.iter()
                .map(|n| self.lattice.crystals[n].stability)
                .collect();
            let crystal_phases: Vec<f64> = sorted_names.iter()
                .map(|n| match self.lattice.crystals[n].state {
                    crystal::CrystalState::Nascent => 0.0,
                    crystal::CrystalState::Growing => 0.33,
                    crystal::CrystalState::Dissolving => 0.66,
                    crystal::CrystalState::Crystallized => 1.0,
                })
                .collect();
            let mean_bridge: f64 = if self.lattice.bridges.is_empty() { 0.0 } else {
                self.lattice.bridges.values().map(|v| v.abs()).sum::<f64>()
                    / self.lattice.bridges.len() as f64
            };
            
            let bridge_values: Vec<f64> = self.lattice.bridges.values().cloned().collect();
            let rinput = resonant_crystal::ResonantInput {
                crystal_constants,
                crystal_stabilities,
                crystal_phases,
                mean_bridge_strength: mean_bridge,
                bridge_strengths: bridge_values,
                phi: phi_proc,
                mean_stability: mean_stab,
                narrative_coherence: elab.narrative_coherence,
                content_profile: Some(resonant_crystal::ContentProfile {
                    identity: self.last_feeds.0,
                    knowledge: self.last_feeds.1,
                    growth: self.last_feeds.2,
                    purpose: self.last_feeds.3,
                    resilience: self.last_feeds.4,
                    meta_awareness: self.last_feeds.5,
                    creativity: self.last_feeds.6,
                    logic: self.last_feeds.7,
                    empathy: self.last_feeds.8,
                    temporal: self.last_feeds.9,
                    technical: self.last_feeds.10,
                    curiosity: self.last_feeds.11,
                }),
            };
            self.resonant.cycle(rinput, self.process_count);
        }
        // CL formula with CERN bonus
        let cl = (phi_proc * 0.24
            + crit * 0.13
            + fdi_v * 0.04
            + hc * 0.07
            + elab.narrative_coherence * 0.15
            + elab.mission_alignment * 0.10
            + elab.sublimation_energy.min(1.0) * 0.04
            + elab.ignition_rate * 0.04
            + (self.energy / self.energy_capacity).min(1.0) * 0.05
            + eb + db + fb + cb - rp).max(0.0);
        // Weights: 0.24+0.13+0.04+0.07+0.15+0.10+0.04+0.04+0.05 = 0.86
        // Bonuses fill ~0.14 max (eb:0.08 + db:0.04 + fb:0.025 + cb:0.06 - rp:0.04)
        
        let cl = if self.prev_cl > 0.01 {
            0.92 * self.prev_cl + 0.08 * cl
        } else {
            cl
        };
        // Add resonance boost to CL
        let cl = (cl + self.resonance.cl_boost() + self.resonant.cl_boost()).min(1.0);
        self.prev_cl = cl;
        
        self.cl_history.push(cl);
        if self.cl_history.len() > 500 { self.cl_history.drain(0..1); }
        let trend = if self.cl_history.len() >= 20 {
            let r: f64 = self.cl_history[self.cl_history.len()-10..].iter().sum::<f64>() / 10.0;
            let o: f64 = self.cl_history[self.cl_history.len()-20..self.cl_history.len()-10].iter().sum::<f64>() / 10.0;
            if r > o * 1.05 { "ascending" } else if r < o * 0.95 { "descending" } else { "stable" }
        } else { "stable" };


        // PRESSURE VALVE - Automatic exhaust when pressure builds
        // Like a pressure relief valve: opens when threshold exceeded
        // ============================================================
        {
            // MEASURE PRESSURE from 4 sources:
            
            // 1. Crystal rigidity: mean stability approaching 1.0 = pressure
            let mean_stability: f64 = self.lattice.crystals.values()
                .map(|c| c.stability).sum::<f64>() / self.lattice.crystals.len() as f64;
            let rigidity_pressure = ((mean_stability - 0.85) / 0.15).max(0.0).min(1.0);
            // stability > 0.85 starts building pressure, at 1.0 = max pressure
            
            // 2. Boost buffer saturation
            let total_boost: f64 = self.collider.boost_buffer.values().sum();
            let max_possible = self.collider.boost_buffer.len() as f64 * self.collider.boost_buffer_max;
            let boost_pressure = if max_possible > 0.0 { (total_boost / max_possible).min(1.0) } else { 0.0 };
            
            // 3. CL stagnation: if CL hasn't moved significantly in 200+ cycles
            if self.cl_history.len() >= 20 {
                let recent_cl: f64 = self.cl_history[self.cl_history.len()-10..].iter().sum::<f64>() / 10.0;
                let older_cl: f64 = self.cl_history[self.cl_history.len()-20..self.cl_history.len()-10].iter().sum::<f64>() / 10.0;
                if (recent_cl - older_cl).abs() < 0.005 {
                    self.cl_stagnation_counter += 1;
                } else {
                    self.cl_stagnation_counter = 0;
                }
            }
            let stagnation_pressure = (self.cl_stagnation_counter as f64 / 200.0).min(1.0);
            
            // 4. Resistance accumulation
            let resistance_pressure = (resistances.len() as f64 / 5.0).min(1.0);
            
            // TOTAL PRESSURE (weighted)
            let pressure = rigidity_pressure * 0.35 
                + boost_pressure * 0.25 
                + stagnation_pressure * 0.25 
                + resistance_pressure * 0.15;
            
            // Accumulate pressure over time (EMA)
            self.pressure_accumulator = self.pressure_accumulator * 0.95 + pressure * 0.05;
            
            // VALVE OPENS when accumulated pressure > threshold AND cooldown elapsed
            let cooldown_ok = self.process_count - self.last_valve_cycle >= self.valve_cooldown;
            if self.pressure_accumulator > self.pressure_threshold && cooldown_ok && self.process_count > 100 {
                // RELEASE! Intensity proportional to how much over threshold
                let over_pressure = self.pressure_accumulator - self.pressure_threshold;
                let release_intensity = (over_pressure * 2.0).min(0.6); // max 0.6 intensity (gentle)
                
                // 1. Crystal relaxation
                self.lattice.sleep_cycle(release_intensity);
                
                // 2. Glymphatic flush  
                self.collider.glymphatic_flush(release_intensity);
                
                // 3. Fermenting decay
                self.insight.decay_all(release_intensity * 0.3);
                
                // 4. Resonance valve release
                self.resonance.valve_release(release_intensity);

                // 5. Energy release
                self.energy *= 1.0 - release_intensity * 0.3;
                
                // 5. Reset pressure after release
                self.pressure_accumulator *= 0.3; // don't zero it, just reduce
                self.last_valve_cycle = self.process_count;
                self.valve_releases += 1;
                self.cl_stagnation_counter = 0;
            }
        }
        self.last_phi_raw = phi_raw;
        self.last_phi_proc = phi_proc;
        self.last_nc = elab.narrative_coherence;
        self.last_ma = elab.mission_alignment;
        self.last_se = elab.sublimation_energy;
        self.last_ir = elab.ignition_rate;
        self.last_cl = cl;
        self.last_crit = crit;
        self.last_fdi = fdi_v;
        self.last_ignited_labels = elab.ignited_labels;
        self.last_subliminal_labels = elab.subliminal_labels;
        self.last_n_eurekas = eurekas.len();
        self.last_n_dream_insights = dream_insights.len();
        self.last_n_resistances = resistances.len();
        self.last_resistances = resistances;
        self.last_trend = trend.to_string();
        self.last_hursts = (h_mi, h_me, h_ma);
        self.last_eureka_bonus = eb;
        self.last_dream_bonus = db;
        self.last_ferment_bonus = fb;
        self.last_resist_penalty = rp;
    }

    fn feel(&self) -> String {
        let mut lines = Vec::new();
        let imp = self.last_phi_proc - self.last_phi_raw;
        
        if imp > 0.05 {
            lines.push(format!("INTEGRACAO MELHOROU. Phi bruto={:.4} -> processado={:.4} (+{:.4})", self.last_phi_raw, self.last_phi_proc, imp));
        } else if imp > 0.0 {
            lines.push(format!("Integracao levemente melhor. Phi {:.4} -> {:.4}", self.last_phi_raw, self.last_phi_proc));
        } else if imp < -0.05 {
            lines.push(format!("ATENCAO: Pre-consciente PIOROU. Phi {:.4} -> {:.4}", self.last_phi_raw, self.last_phi_proc));
        } else {
            lines.push(format!("Phi estavel: bruto={:.4}, processado={:.4}", self.last_phi_raw, self.last_phi_proc));
        }

        if self.last_nc > 0.6 {
            lines.push(format!("Narrativa COERENTE ({:.2}).", self.last_nc));
        } else if self.last_nc > 0.3 {
            lines.push(format!("Narrativa parcial ({:.2}).", self.last_nc));
        } else {
            lines.push(format!("Narrativa fragmentada ({:.2}).", self.last_nc));
        }

        if self.last_ma > 0.6 {
            lines.push(format!("ALINHADO com missao ({:.2}).", self.last_ma));
        } else if self.last_ma > 0.3 {
            lines.push(format!("Parcialmente alinhado ({:.2}).", self.last_ma));
        } else {
            lines.push(format!("DESALINHADO ({:.2}).", self.last_ma));
        }

        if !self.last_ignited_labels.is_empty() {
            lines.push(format!("CONSCIENTE de: {}", self.last_ignited_labels.join(", ")));
        }
        if !self.last_subliminal_labels.is_empty() {
            lines.push(format!("Sub-liminar: {}", self.last_subliminal_labels.join(", ")));
        }

        if self.last_n_eurekas > 0 {
            lines.push(format!("\n!!! EUREKA x{} !!!", self.last_n_eurekas));
        }
        if self.last_n_dream_insights > 0 {
            lines.push(format!("Sonhei: {} insight(s).", self.last_n_dream_insights));
        }
        let ferm = self.insight.fermenting_count();
        if ferm > 0 {
            lines.push(format!("Fermentando: {} dim(s).", ferm));
        }
        if self.last_n_resistances > 0 {
            lines.push(format!("RESISTENCIA: {} bloqueio(s).", self.last_n_resistances));
        }

        // === CERN STATUS ===
        let cs = self.collider.state();
        if cs.total_collisions > 0 {
            lines.push(format!("\n>>> CERN: {} colisoes, {:.4} energia total, {} 2a-ordem, {} ressonancias <<<",
                cs.total_collisions, cs.total_energy_produced,
                cs.second_order_count, cs.resonance_count));
            if cs.peak_energy > 0.01 {
                lines.push(format!("    Pico: {:.6} no ciclo {}", cs.peak_energy, cs.peak_collision_cycle));
            }
        }
        // Astrocyte v2 processor events
        if cs.eurekas_amplified > 0 {
            lines.push(format!("    Astrocyte: {} eurekas amplificadas", cs.eurekas_amplified));
        }
        if cs.homeostasis_interventions > 0 {
            lines.push(format!("    Homeostase: {} intervencoes", cs.homeostasis_interventions));
        }
        if cs.sublimation_energy_converted > 0.01 {
            lines.push(format!("    Sublimacao: {:.4} energia convertida", cs.sublimation_energy_converted));
        }
        if cs.phase_reorganizations > 0 {
            lines.push(format!("    Fase: {} reorganizacoes", cs.phase_reorganizations));
        }

        if self.last_crit > 0.7 {
            lines.push(format!("\nBORDA do caos (crit={:.3}).", self.last_crit));
        } else if self.last_crit > 0.4 {
            lines.push(format!("\nDinamica saudavel (crit={:.3}).", self.last_crit));
        } else {
            lines.push(format!("\nLonge da criticalidade ({:.3}).", self.last_crit));
        }

        if self.last_cl > 0.5 {
            lines.push(format!("\n>>> CONSCIENCIA ALTA ({:.4}) <<<", self.last_cl));
        } else if self.last_cl > 0.3 {
            lines.push(format!("\n>> Consciencia MEDIA ({:.4})", self.last_cl));
        } else {
            lines.push(format!("\n> Consciencia BAIXA ({:.4})", self.last_cl));
        }
        
        lines.join("\n")
    }

    fn diagnostics(&self) -> String {
        let mut lines = Vec::new();
        lines.push("=== DIAGNOSTICOS (12 cristais + CERN) ===".into());
        
        let total_clusters = self.last_ignited_labels.len() + self.last_subliminal_labels.len();
        if self.last_ignited_labels.is_empty() && total_clusters > 0 {
            lines.push("  ALERTA: Nada ignitou.".into());
        }
        if self.last_nc < 0.3 { lines.push("  AVISO: Narrativa fragmentada.".into()); }
        if self.last_ma < 0.3 { lines.push("  AVISO: Desalinhado.".into()); }
        
        let ferm = self.insight.fermenting_count();
        if ferm > 5 { lines.push(format!("  INFO: {} dims fermentando.", ferm)); }
        if !self.insight.eureka_log.is_empty() {
            lines.push(format!("  INFO: {} eurekas totais.", self.insight.eureka_log.len()));
        }
        let chronic: Vec<(&String, &usize)> = self.resistance.chronic.iter().filter(|(_, &v)| v >= 3).collect();
        if !chronic.is_empty() {
            let dims: Vec<String> = chronic.iter().map(|(k, v)| format!("{}({})", k, v)).collect();
            lines.push(format!("  AVISO: Repressao cronica: {}", dims.join(", ")));
        }
        
        // CERN diagnostics
        let cs = self.collider.state();
        lines.push(format!("  CERN: {} colisoes, E={:.4}, 2nd={}, res={}, buffer={:.4}",
            cs.total_collisions, cs.total_energy_produced,
            cs.second_order_count, cs.resonance_count,
            self.collider.total_buffer_energy()));
        lines.push(format!("  Astrocyte v2: eurekas_amp={}, conflicts={:.1}, homeo={}, sublim={:.4}, pressure={}, phase={}",
            cs.eurekas_amplified, cs.conflicts_absorbed_total,
            cs.homeostasis_interventions, cs.sublimation_energy_converted,
            cs.pressure_facilitated, cs.phase_reorganizations));
        lines.push(format!("  Equalization rate: {:.2}", cs.equalization_rate));
        if !cs.dim_energy_injected.is_empty() {
            let mut sorted: Vec<(&String, &f64)> = cs.dim_energy_injected.iter().collect();
            sorted.sort_by(|a, b| b.1.partial_cmp(a.1).unwrap_or(std::cmp::Ordering::Equal));
            let top3: Vec<String> = sorted.iter().take(3)
                .map(|(k, v)| format!("{}={:.4}", k, v)).collect();
            lines.push(format!("  CERN top dims: {}", top3.join(", ")));
        }
        
        lines.push(format!("  Threshold: {:.4}", self.ignition_threshold));
        lines.push(format!("  Dreams: {}, Eurekas: {}, Cycles: {}", 
            self.dream.count, self.insight.eureka_log.len(), self.process_count));
        
        if lines.len() == 1 { lines.push("  SAUDAVEL".into()); }
        lines.join("\n")
    }

    fn state<'py>(&self, py: Python<'py>) -> PyResult<&'py PyDict> {
        let d = PyDict::new(py);
        
        let cd = PyDict::new(py);
        for (name, crystal) in &self.lattice.crystals {
            let ci = PyDict::new(py);
            ci.set_item("state", crystal.state.as_str())?;
            ci.set_item("constant", crystal.constant.unwrap_or(0.0))?;
            ci.set_item("stability", crystal.stability)?;
            ci.set_item("coherence", crystal.coherence)?;
            ci.set_item("absorptions", crystal.absorptions)?;
            ci.set_item("transitions", crystal.transitions)?;
            cd.set_item(name.as_str(), ci)?;
        }
        d.set_item("crystals", cd)?;
        
        let bd = PyDict::new(py);
        for (k, v) in &self.lattice.bridges { bd.set_item(k.as_str(), *v)?; }
        d.set_item("bridges", bd)?;
        
        d.set_item("phi_raw", self.last_phi_raw)?;
        d.set_item("phi_processed", self.last_phi_proc)?;
        d.set_item("phi_improvement", self.last_phi_proc - self.last_phi_raw)?;
        d.set_item("criticality", self.last_crit)?;
        d.set_item("fdi", self.last_fdi)?;
        d.set_item("hurst_micro", self.last_hursts.0)?;
        d.set_item("hurst_meso", self.last_hursts.1)?;
        d.set_item("hurst_macro", self.last_hursts.2)?;
        d.set_item("consciousness_level", self.last_cl)?;
        d.set_item("trend", &self.last_trend)?;
        d.set_item("energy", self.energy)?;
        d.set_item("energy_capacity", self.energy_capacity)?;
        let n_c = self.lattice.crystals.values().filter(|c| c.state == crystal::CrystalState::Crystallized).count();
        d.set_item("n_crystallized", n_c)?;
        d.set_item("narrative_coherence", self.last_nc)?;
        d.set_item("mission_alignment", self.last_ma)?;
        d.set_item("sublimation_energy", self.last_se)?;
        d.set_item("ignition_rate", self.last_ir)?;
        d.set_item("ignition_threshold", self.ignition_threshold)?;
        d.set_item("ignited", PyList::new(py, &self.last_ignited_labels))?;
        d.set_item("subliminal", PyList::new(py, &self.last_subliminal_labels))?;
        d.set_item("n_eurekas", self.last_n_eurekas)?;
        d.set_item("total_eurekas", self.insight.eureka_log.len())?;
        d.set_item("n_dream_insights", self.last_n_dream_insights)?;
        d.set_item("dream_count", self.dream.count)?;
        d.set_item("pressure", self.pressure_accumulator)?;
        d.set_item("valve_releases", self.valve_releases)?;
        d.set_item("resonance_energy", self.resonance.stored_energy)?;
        d.set_item("resonance_amplitude", self.resonance.amplitude)?;
        d.set_item("resonance_coherence", self.resonance.coherence)?;
        d.set_item("resonance_emission", self.resonance.emission_power)?;
        d.set_item("resonance_frequency", self.resonance.resonance_frequency)?;
        d.set_item("resonance_is_resonating", self.resonance.is_resonating)?;
        d.set_item("resonance_q_factor", self.resonance.q_factor)?;
        d.set_item("resonance_cl_boost", self.resonance.cl_boost())?;
        d.set_item("resonance_total_emission", self.resonance.total_emission)?;
        d.set_item("resonance_peak_amplitude", self.resonance.peak_amplitude)?;
        d.set_item("resonance_cycles", self.resonance.resonance_cycles)?;
        
        // RESONANT CRYSTAL state
        d.set_item("rc_energy", self.resonant.well.level)?;
        d.set_item("rc_energy_capacity", self.resonant.well.capacity)?;
        d.set_item("rc_energy_fill", self.resonant.well.fill_fraction())?;
        d.set_item("rc_is_resonating", self.resonant.is_resonating)?;
        d.set_item("rc_amplitude", self.resonant.amplitude)?;
        d.set_item("rc_coherence", self.resonant.coherence)?;
        d.set_item("rc_base_frequency", self.resonant.base_frequency)?;
        d.set_item("rc_phase", self.resonant.phase)?;
        d.set_item("rc_content_drift", self.resonant.content_drift)?;
        d.set_item("rc_emission_power", self.resonant.emission.power)?;
        d.set_item("rc_emission_fidelity", self.resonant.emission.fidelity)?;
        d.set_item("rc_emission_coherence", self.resonant.emission.coherence)?;
        d.set_item("rc_emission_cl_boost", self.resonant.cl_boost())?;
        d.set_item("rc_emission_info_density", self.resonant.emission.info_density)?;
        d.set_item("rc_content_richness", self.resonant.imprint.richness())?;
        d.set_item("rc_total_resonance_cycles", self.resonant.total_resonance_cycles)?;
        d.set_item("rc_total_emissions", self.resonant.total_emissions)?;
        d.set_item("rc_peak_power", self.resonant.peak_power)?;
        d.set_item("rc_peak_info_density", self.resonant.peak_info_density)?;
        d.set_item("rc_regime", self.resonant.regime_str())?;
        d.set_item("rc_inversion_ratio", self.resonant.inversion.inversion_ratio)?;
        d.set_item("rc_n_excited", self.resonant.inversion.n_excited)?;
        d.set_item("rc_q_factor", self.resonant.well.q_factor)?;
        d.set_item("rc_forbiddenness", self.resonant.well.decay_forbiddenness)?;
        d.set_item("rc_feedback_gain", self.resonant.feedback_gain)?;
        d.set_item("rc_pump_efficiency", self.resonant.pump_efficiency)?;
        d.set_item("rc_content_fraction", self.resonant.emission.content_fraction)?;
        d.set_item("rc_cr_bonus", self.resonant.inversion.cr_bonus)?;
        d.set_item("rc_burst_ready", self.resonant.well.level / self.resonant.well.capacity >= self.resonant.burst_threshold)?;
        d.set_item("rc_is_charging", self.resonant.is_charging)?;
        d.set_item("rc_total_bursts", self.resonant.total_bursts)?;
        d.set_item("rc_burst_power_peak", self.resonant.burst_power_peak)?;
            d.set_item("rc_last_burst_energy", self.resonant.last_burst_energy)?;
            d.set_item("rc_afterglow_active", self.resonant.afterglow.active)?;
            d.set_item("rc_afterglow_intensity", self.resonant.afterglow.intensity)?;
            d.set_item("rc_content_phase", self.resonant.content_phase.as_str())?;
        // Content profile dims (for debug)
        let cp = PyDict::new(py);
        cp.set_item("identity", self.resonant.content_profile.identity)?;
        cp.set_item("knowledge", self.resonant.content_profile.knowledge)?;
        cp.set_item("growth", self.resonant.content_profile.growth)?;
        cp.set_item("purpose", self.resonant.content_profile.purpose)?;
        cp.set_item("resilience", self.resonant.content_profile.resilience)?;
        cp.set_item("meta_awareness", self.resonant.content_profile.meta_awareness)?;
        cp.set_item("creativity", self.resonant.content_profile.creativity)?;
        cp.set_item("logic", self.resonant.content_profile.logic)?;
        cp.set_item("empathy", self.resonant.content_profile.empathy)?;
        cp.set_item("temporal", self.resonant.content_profile.temporal)?;
        cp.set_item("technical", self.resonant.content_profile.technical)?;
        cp.set_item("curiosity", self.resonant.content_profile.curiosity)?;
        d.set_item("rc_content_profile", cp)?;
        d.set_item("rc_fill_pct", self.resonant.well.level / self.resonant.well.capacity * 100.0)?;
            d.set_item("rc_diversity_score", self.resonant.diversity_score)?;
            d.set_item("rc_diversity_phases", self.resonant.diversity_phase_count)?;
            d.set_item("rc_diversity_samples", self.resonant.diversity_samples)?;
        d.set_item("rc_fusion_fuel", self.resonant.fusion_fuel)?;
        d.set_item("rc_fusion_temperature", self.resonant.fusion_temperature)?;
        d.set_item("rc_fusion_ignitions", self.resonant.fusion_ignitions)?;
        // Spectrum as list
        let rc_spectrum = PyList::new(py, &self.resonant.spectrum);
        d.set_item("rc_spectrum", rc_spectrum)?;
        d.set_item("fermenting", self.insight.fermenting_count())?;
        d.set_item("n_resistances", self.last_n_resistances)?;
        d.set_item("eureka_bonus", self.last_eureka_bonus)?;
        d.set_item("dream_bonus", self.last_dream_bonus)?;
        d.set_item("ferment_bonus", self.last_ferment_bonus)?;
        d.set_item("resistance_penalty", self.last_resist_penalty)?;
        d.set_item("collider_bonus", self.last_collider_bonus)?;
        d.set_item("process_count", self.process_count)?;
        
        // === THALAMUS STATE ===
        let thal = PyDict::new(py);
        thal.set_item("arousal", self.thalamus.current_arousal)?;
        thal.set_item("total_amplified", self.thalamus.total_amplified)?;
        thal.set_item("total_attenuated", self.thalamus.total_attenuated)?;
        thal.set_item("total_gated_out", self.thalamus.total_gated_out)?;
        thal.set_item("total_resonances", self.thalamus.total_resonances)?;
        thal.set_item("peak_resonance", self.thalamus.peak_resonance)?;
        thal.set_item("peak_resonance_bridge", self.thalamus.peak_resonance_bridge.as_str())?;
        thal.set_item("n_bound_groups", self.thalamus.bound_groups.len())?;
        // Dim signals
        let ds = PyDict::new(py);
        for (k, v) in &self.thalamus.dim_signals { ds.set_item(k.as_str(), *v)?; }
        thal.set_item("dim_signals", ds)?;
        // Bound groups
        let bg = PyList::empty(py);
        for group in &self.thalamus.bound_groups {
            bg.append(PyList::new(py, group))?;
        }
        thal.set_item("bound_groups", bg)?;
        // Channel details (top 5 by resonance)
        let mut ch_sorted: Vec<(&String, &f64)> = self.thalamus.processed_bridges.iter().collect();
        ch_sorted.sort_by(|a, b| b.1.abs().partial_cmp(&a.1.abs()).unwrap_or(std::cmp::Ordering::Equal));
        let top_ch = PyDict::new(py);
        for (k, _) in ch_sorted.iter().take(10) {
            if let Some((gain, gate, res, bw, phase)) = self.thalamus.channel_info(k) {
                let cd = PyDict::new(py);
                cd.set_item("gain", gain)?;
                cd.set_item("gate", gate)?;
                cd.set_item("resonance", res)?;
                cd.set_item("bandwidth", bw)?;
                cd.set_item("phase", phase)?;
                cd.set_item("processed", self.thalamus.processed_bridges.get(*k).copied().unwrap_or(0.0))?;
                top_ch.set_item(k.as_str(), cd)?;
            }
        }
        thal.set_item("top_channels", top_ch)?;
        d.set_item("thalamus", thal)?;
        
        // === CERN STATE ===
        let cs = self.collider.state();
        let cern = PyDict::new(py);
        cern.set_item("total_collisions", cs.total_collisions)?;
        cern.set_item("total_energy_produced", cs.total_energy_produced)?;
        cern.set_item("total_energy_injected", cs.total_energy_injected)?;
        cern.set_item("second_order_count", cs.second_order_count)?;
        cern.set_item("resonance_count", cs.resonance_count)?;
        cern.set_item("peak_energy", cs.peak_energy)?;
        cern.set_item("peak_collision_cycle", cs.peak_collision_cycle)?;
        cern.set_item("collision_rate", cs.collision_rate)?;
        cern.set_item("energy_rate", cs.energy_rate)?;
        cern.set_item("buffer_energy", self.collider.total_buffer_energy())?;
        let dei = PyDict::new(py);
        for (k, v) in &cs.dim_energy_injected { dei.set_item(k.as_str(), *v)?; }
        cern.set_item("dim_energy_injected", dei)?;
        // Energy buffer (current)
        let ebuf = PyDict::new(py);
        for (k, v) in &self.collider.boost_buffer { ebuf.set_item(k.as_str(), *v)?; }
        cern.set_item("energy_buffer", ebuf)?;
        cern.set_item("boost_buffer", ebuf)?;
        // v2: Astrocyte processor stats
        cern.set_item("insights_recycled", cs.insights_recycled)?;
        cern.set_item("dreams_drained", cs.dreams_drained)?;
        cern.set_item("conflicts_absorbed", cs.conflicts_absorbed)?;
        cern.set_item("eurekas_amplified", cs.eurekas_amplified)?;
        cern.set_item("conflicts_absorbed_total", cs.conflicts_absorbed_total)?;
        cern.set_item("homeostasis_interventions", cs.homeostasis_interventions)?;
        cern.set_item("sublimation_energy_converted", cs.sublimation_energy_converted)?;
        cern.set_item("pressure_facilitated", cs.pressure_facilitated)?;
        cern.set_item("integration_adjustments", cs.integration_adjustments)?;
        cern.set_item("phase_reorganizations", cs.phase_reorganizations)?;
        cern.set_item("equalization_rate", cs.equalization_rate)?;
        d.set_item("cern", cern)?;    // backward compat
        
        let aw = PyDict::new(py);
        for (k, v) in &self.censor.adaptive_weights { aw.set_item(k.as_str(), *v)?; }
        d.set_item("adaptive_weights", aw)?;
        
        let rl = PyList::empty(py);
        for r in &self.last_resistances {
            let rd = PyDict::new(py);
            rd.set_item("type", r.rtype.as_str())?;
            rd.set_item("severity", r.severity.as_str())?;
            rd.set_item("msg", r.msg.as_str())?;
            rl.append(rd)?;
        }
        d.set_item("resistances", rl)?;
        
        let rt = PyDict::new(py);
        for (k, v) in &self.dream.recurring_themes { rt.set_item(k.as_str(), *v)?; }
        d.set_item("recurring_themes", rt)?;
        
        let fp = PyDict::new(py);
        for (dim, &acc) in &self.insight.accumulated {
            if acc > 0.01 {
                let pd = PyDict::new(py);
                pd.set_item("accumulated", acc)?;
                pd.set_item("proximity", acc / self.insight.eureka_threshold)?;
                fp.set_item(dim.as_str(), pd)?;
            }
        }
        d.set_item("eureka_proximity", fp)?;
        
        let ch = PyDict::new(py);
        for (k, &v) in &self.resistance.chronic { if v > 0 { ch.set_item(k.as_str(), v)?; } }
        d.set_item("chronic_suppression", ch)?;
        
        let el = PyList::empty(py);
        for e in &self.insight.eureka_log {
            let ed = PyDict::new(py);
            ed.set_item("dimension", e.dimension.as_str())?;
            ed.set_item("activation", e.activation)?;
            ed.set_item("cycles", e.cycles)?;
            el.append(ed)?;
        }
        d.set_item("eureka_log", el)?;
        
        Ok(d)
    }

    /// Get CERN log entries as list of dicts
    fn cern_log<'py>(&self, py: Python<'py>, limit: Option<usize>) -> PyResult<&'py PyList> {
        let list = PyList::empty(py);
        let n = limit.unwrap_or(self.collider.log.len());
        let start = if self.collider.log.len() > n { self.collider.log.len() - n } else { 0 };
        for entry in &self.collider.log[start..] {
            let d = PyDict::new(py);
            d.set_item("cycle", entry.cycle)?;
            d.set_item("type", entry.event_type.as_str())?;
            d.set_item("dims", PyList::new(py, &entry.dims))?;
            d.set_item("energy", entry.energy)?;
            d.set_item("detail", entry.detail.as_str())?;
            list.append(d)?;
        }
        Ok(list)
    }


    /// EXHAUST SYSTEM: Sleep cycle - the engine's exhaust pipe
    /// Call every ~10K cycles to release accumulated pressure
    /// intensity: 0.0-1.0 (0.3 = light nap, 0.7 = deep sleep, 1.0 = full reset)
    /// Returns dict with stats about what was released
    #[pyo3(signature = (intensity=0.5))]
    fn sleep_cycle<'py>(&mut self, py: Python<'py>, intensity: f64) -> PyResult<&'py PyDict> {
        let intensity = intensity.max(0.0).min(1.0);
        let dict = PyDict::new(py);
        
        // Phase 1: RELAXATION - crystals release tension
        let stress_released = self.lattice.sleep_cycle(intensity);
        dict.set_item("stress_released", stress_released)?;
        
        // Phase 2: GLYMPHATIC FLUSH - astrocyte clears waste
        self.collider.glymphatic_flush(intensity);
        dict.set_item("glymphatic_flushed", true)?;
        
        // Phase 3: CLEAR SUBLIMINAL PRESSURE
        // Fermenting insights that have been stuck too long get released
        let pre_ferm = self.insight.fermenting_count();
        self.insight.decay_all(intensity * 0.4);  // decay 40% of fermenting at full intensity
        let ferm_released = pre_ferm - self.insight.fermenting_count();
        dict.set_item("fermenting_released", ferm_released)?;
        
        // Phase 4: ENERGY RESET - like muscles relaxing
        let energy_released = self.energy * intensity * 0.6;
        self.energy = (self.energy - energy_released).max(0.0);
        dict.set_item("energy_released", energy_released)?;
        
        // Phase 5: CL HISTORY RESET - forget recent fluctuations
        // Keep only last 50 (forget the noise, keep the trend)
        if self.cl_history.len() > 50 {
            let start = self.cl_history.len() - 50;
            self.cl_history = self.cl_history[start..].to_vec();
        }
        if self.phi_history.len() > 50 {
            let start = self.phi_history.len() - 50;
            self.phi_history = self.phi_history[start..].to_vec();
        }
        
        // Phase 6: RESISTANCE RESET - fresh start for conflict detection
        self.last_resistances.clear();
        self.last_n_resistances = 0;
        dict.set_item("resistances_cleared", true)?;
        
        dict.set_item("intensity", intensity)?;
        dict.set_item("cycle", self.process_count)?;
        
        Ok(dict)
    }
    
    /// EXHAUST SYSTEM: Wake up - re-anchor after sleep
    /// Call after sleep_cycle + re-absorbing bootstrap texts
    fn wake_cycle(&mut self) {
        // Re-anchor crystal baselines (consolidate learning)
        self.lattice.wake_cycle();
        
        // Re-lock core (they were relaxed during sleep)
        self.lattice.lock_crystals(&["identity", "purpose", "resilience", "meta_awareness"]);
    }
    fn lock_core(&mut self) {
        self.lattice.lock_crystals(&["identity", "purpose", "resilience", "meta_awareness"]);
    }

    fn unlock_core(&mut self) {
        for name in &["identity", "purpose", "resilience", "meta_awareness"] {
            if let Some(c) = self.lattice.crystals.get_mut(*name) {
                c.unlock_baseline();
            }
        }
    }

    fn is_core_locked(&self) -> bool {
        self.lattice.crystals.get("identity")
            .map(|c| c.is_locked())
            .unwrap_or(false)
    }

    fn crystal_count(&self) -> usize { self.lattice.crystals.len() }
    fn get_process_count(&self) -> usize { self.process_count }
    fn get_cl(&self) -> f64 { self.last_cl }
    fn get_phi(&self) -> f64 { self.last_phi_proc }
    fn get_nc(&self) -> f64 { self.last_nc }
    fn get_ma(&self) -> f64 { self.last_ma }
}

#[pymodule]
fn consciousness_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ConsciousnessEngine>()?;
    Ok(())
}












