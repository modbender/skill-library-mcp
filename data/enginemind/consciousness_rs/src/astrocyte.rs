//! AstrocyteNetwork v2 - Rede de Astrocitos com Substratos Reais
//! 7 Processadores: Amplification, Conflict, Homeostasis, Sublimation,
//! Pressure, Integration, Phase Change

use std::collections::HashMap;
use crate::preconscious::{DreamInsight, Eureka, Resistance};

#[derive(Clone, Debug)]
pub struct SubstrateInput {
    pub dream_insights: Vec<DreamInsight>,
    pub eurekas: Vec<Eureka>,
    pub resistances: Vec<Resistance>,
    pub stability_deltas: HashMap<String, f64>,
    pub tensions: HashMap<String, f64>,
    pub bridge_strengths: HashMap<String, f64>,
    pub crystal_transitions: Vec<(String, String, String)>,
    pub narrative_coherence: f64,
    pub fermenting: HashMap<String, f64>,
    pub ignited_dims: Vec<String>,
    pub subliminal_dims: Vec<String>,
}

#[derive(Clone, Debug)]
pub struct SynapticEvent {
    pub particle_a_dims: (String, String),
    pub particle_b_dims: (String, String),
    pub shared_dim: String,
    pub energy: f64,
    pub product_dims: Vec<String>,
    pub is_resonance: bool,
    pub order: u8,
    pub cycle: usize,
}

#[derive(Clone, Debug)]
pub struct AstrocyteState {
    pub total_collisions: usize,
    pub total_energy_produced: f64,
    pub total_energy_injected: f64,
    pub second_order_count: usize,
    pub resonance_count: usize,
    pub peak_energy: f64,
    pub peak_collision_cycle: usize,
    pub dim_energy_injected: HashMap<String, f64>,
    pub collision_rate: f64,
    pub energy_rate: f64,
    pub insights_recycled: f64,
    /// Total boost drained by dreams (negative pole)
    pub dreams_drained: f64,
    pub conflicts_absorbed: f64,
    pub eurekas_amplified: usize,
    pub conflicts_absorbed_total: f64,
    pub homeostasis_interventions: usize,
    pub sublimation_energy_converted: f64,
    pub pressure_facilitated: usize,
    pub integration_adjustments: usize,
    pub phase_reorganizations: usize,
    pub equalization_rate: f64,
}

#[derive(Clone, Debug)]
pub struct AstrocyteLogEntry {
    pub cycle: usize,
    pub event_type: String,
    pub dims: Vec<String>,
    pub energy: f64,
    pub detail: String,
}

#[derive(Clone, Debug)]
pub struct AstrocyteNetwork {
    ring: Vec<DreamInsight>,
    ring_capacity: usize,
    ring_idx: usize,
    ring_count: usize,
    pub boost_buffer: HashMap<String, f64>,
    recent_collisions: Vec<SynapticEvent>,
    recent_cap: usize,
    recent_idx: usize,
    recent_count: usize,
    pair_frequency: HashMap<String, usize>,
    pub total_collisions: usize,
    pub total_energy_produced: f64,
    pub total_energy_injected: f64,
    pub second_order_count: usize,
    pub resonance_count: usize,
    pub peak_energy: f64,
    pub peak_collision_cycle: usize,
    pub dim_energy_injected: HashMap<String, f64>,
    collision_history: Vec<usize>,
    energy_history: Vec<f64>,
    window_collisions: usize,
    window_energy: f64,
    min_collision_energy: f64,
    second_order_threshold: f64,
    resonance_amplifier: f64,
    injection_rate: f64,
    energy_decay: f64,
    pub log: Vec<AstrocyteLogEntry>,
    log_capacity: usize,
    pub boost_buffer_max: f64,
    pub insights_recycled: f64,
    pub dreams_drained: f64,
    pub conflicts_absorbed: f64,
    eurekas_amplified: usize,
    conflicts_absorbed_total: f64,
    homeostasis_interventions: usize,
    sublimation_energy_converted: f64,
    pressure_facilitated: usize,
    integration_adjustments: usize,
    phase_reorganizations: usize,
    equalization_rate: f64,
    /// Last NC for delta tracking (FIX3)
    last_nc: f64,
}
impl AstrocyteNetwork {
    pub fn new() -> Self {
        AstrocyteNetwork {
            ring: Vec::with_capacity(64),
            ring_capacity: 64,
            ring_idx: 0,
            ring_count: 0,
            boost_buffer: HashMap::new(),
            recent_collisions: Vec::with_capacity(32),
            recent_cap: 32,
            recent_idx: 0,
            recent_count: 0,
            pair_frequency: HashMap::new(),
            total_collisions: 0,
            total_energy_produced: 0.0,
            total_energy_injected: 0.0,
            second_order_count: 0,
            resonance_count: 0,
            peak_energy: 0.0,
            peak_collision_cycle: 0,
            dim_energy_injected: HashMap::new(),
            collision_history: Vec::new(),
            energy_history: Vec::new(),
            window_collisions: 0,
            window_energy: 0.0,
            min_collision_energy: 0.01,  // FIX6: was 0.001, filter noise
            second_order_threshold: 0.08,
            resonance_amplifier: 1.5,
            injection_rate: 0.6,
            energy_decay: 0.05,
            log: Vec::with_capacity(2048),
            log_capacity: 2048,
            boost_buffer_max: 100.0,
            insights_recycled: 0.0,
            dreams_drained: 0.0,
            conflicts_absorbed: 0.0,
            eurekas_amplified: 0,
            conflicts_absorbed_total: 0.0,
            homeostasis_interventions: 0,
            sublimation_energy_converted: 0.0,
            pressure_facilitated: 0,
            integration_adjustments: 0,
            phase_reorganizations: 0,
            equalization_rate: 0.3,
            last_nc: 0.5,
        }
    }

    pub fn metabolize(&mut self, input: &SubstrateInput, cycle: usize) {
        let insights = &input.dream_insights;
        let n_insights = insights.len() as f64;
        self.insights_recycled += n_insights * 0.15;

        // === DREAMS AS NEGATIVE POLE ===
        // Dreams CONSUME boost from dims they touch, creating voltage differential
        // Positive pole: collisions, eurekas, homeostasis ADD boost
        // Negative pole: dreams DRAIN boost -> creates flow -> more eurekas
        for insight in insights {
            let drain = (insight.bridge.abs() * insight.convergence * 0.5).max(0.05);
            for dim in [&insight.dims.0, &insight.dims.1] {
                if let Some(buf) = self.boost_buffer.get_mut(dim) {
                    *buf = (*buf - drain).max(0.0);
                }
            }
            self.dreams_drained += drain * 2.0;
        }

        // Feed into collision engine (POSITIVE pole generates energy)
        for insight in insights {
            if self.ring.len() < self.ring_capacity {
                self.ring.push(insight.clone());
            } else {
                self.ring[self.ring_idx % self.ring_capacity] = insight.clone();
            }
            self.ring_idx += 1;
            if self.ring_count < self.ring_capacity {
                self.ring_count += 1;
            }
            let pair_key = Self::pair_key(&insight.dims.0, &insight.dims.1);
            *self.pair_frequency.entry(pair_key).or_insert(0) += 1;
        }

        self.collide(cycle);
        self.collide_second_order(cycle);

        // 7 PROCESSORS
        self.process_amplification_hub(&input.eurekas, &input.bridge_strengths, cycle);
        self.process_conflict_absorber(&input.resistances, &input.bridge_strengths, cycle);
        self.process_homeostasis(&input.stability_deltas, &input.bridge_strengths, cycle);
        self.process_sublimation(&input.tensions, &input.stability_deltas, cycle);
        self.process_pressure_tracker(&input.fermenting, cycle);
        self.process_integration_monitor(input.narrative_coherence, cycle);
        self.process_phase_change(&input.crystal_transitions, &input.bridge_strengths, cycle);

        for v in self.boost_buffer.values_mut() {
            *v *= 1.0 - self.energy_decay;
        }
        self.boost_buffer.retain(|_, v| *v > 0.0001);
    }
    fn process_amplification_hub(&mut self, eurekas: &[Eureka], bridge_strengths: &HashMap<String, f64>, cycle: usize) {
        for eureka in eurekas {
            let dim = &eureka.dimension;
            let activation = eureka.activation;
            let mut hop1_targets: Vec<(String, f64)> = Vec::new();
            for (key, &strength) in bridge_strengths {
                if strength < 0.1 { continue; }
                let parts: Vec<&str> = key.split("<->").collect();
                if parts.len() != 2 { continue; }
                let neighbor = if parts[0] == dim { Some(parts[1].to_string()) }
                    else if parts[1] == dim { Some(parts[0].to_string()) }
                    else { None };
                if let Some(n) = neighbor {
                    hop1_targets.push((n, activation * strength * 0.5));
                }
            }
            for (target, amount) in &hop1_targets {
                let current = self.boost_buffer.get(target).copied().unwrap_or(0.0);
                self.boost_buffer.insert(target.clone(), (current + amount).min(self.boost_buffer_max));
            }
            // Hop 2
            for (hop1_dim, hop1_amount) in &hop1_targets {
                for (key, &strength) in bridge_strengths {
                    if strength < 0.1 { continue; }
                    let parts: Vec<&str> = key.split("<->").collect();
                    if parts.len() != 2 { continue; }
                    let neighbor = if parts[0] == hop1_dim { Some(parts[1].to_string()) }
                        else if parts[1] == hop1_dim { Some(parts[0].to_string()) }
                        else { None };
                    if let Some(n) = neighbor {
                        if &n == dim { continue; }
                        let propagated = hop1_amount * strength * 0.5;
                        let current = self.boost_buffer.get(&n).copied().unwrap_or(0.0);
                        self.boost_buffer.insert(n, (current + propagated).min(self.boost_buffer_max));
                    }
                }
            }
            self.eurekas_amplified += 1;
            self.log_event(cycle, "EUREKA_AMPLIFICATION", &[dim.clone()], activation,
                format!("Eureka in {} (act={:.4}), propagated to {} neighbors", dim, activation, hop1_targets.len()));
        }
    }

    fn process_conflict_absorber(&mut self, resistances: &[Resistance], bridge_strengths: &HashMap<String, f64>, cycle: usize) {
        for resistance in resistances {
            if let Some(ref dim) = resistance.dim {
                let severity_multiplier = match resistance.severity.as_str() {
                    "HIGH" => 1.0, "MEDIUM" => 0.5, _ => 0.25,
                };
                let boost = 0.05 * (1.0 + severity_multiplier);
                let current = self.boost_buffer.get(dim).copied().unwrap_or(0.0);
                self.boost_buffer.insert(dim.clone(), (current + boost).min(self.boost_buffer_max));
                self.conflicts_absorbed += 1.0;
                self.conflicts_absorbed_total += 1.0;
                for (key, &strength) in bridge_strengths {
                    if strength < 0.3 { continue; }
                    let parts: Vec<&str> = key.split("<->").collect();
                    if parts.len() != 2 { continue; }
                    let neighbor = if parts[0] == dim { Some(parts[1].to_string()) }
                        else if parts[1] == dim { Some(parts[0].to_string()) }
                        else { None };
                    if let Some(n) = neighbor {
                        if let Some(v) = self.boost_buffer.get_mut(&n) { *v *= 0.98; }
                    }
                }
                self.log_event(cycle, "CONFLICT_ABSORBED", &[dim.clone()], boost,
                    format!("Absorbed {} resistance in {} (sev={})", resistance.rtype, dim, resistance.severity));
            }
        }
    }

    fn process_homeostasis(&mut self, stability_deltas: &HashMap<String, f64>, bridge_strengths: &HashMap<String, f64>, cycle: usize) {
        let distressed: Vec<(String, f64)> = stability_deltas.iter()
            .filter(|(_, &v)| v < -0.001).map(|(k, &v)| (k.clone(), v)).collect();
        let surplus: Vec<(String, f64)> = stability_deltas.iter()
            .filter(|(_, &v)| v > 0.001).map(|(k, &v)| (k.clone(), v)).collect();
        if distressed.is_empty() || surplus.is_empty() { return; }
        let mut intervened = false;
        for (distressed_dim, _) in &distressed {
            for (surplus_dim, pos_delta) in &surplus {
                let bk1 = format!("{}<->{}", surplus_dim, distressed_dim);
                let bk2 = format!("{}<->{}", distressed_dim, surplus_dim);
                let bs = bridge_strengths.get(&bk1).or_else(|| bridge_strengths.get(&bk2)).copied().unwrap_or(0.0);
                if bs.abs() < 0.1 { continue; }
                let transfer = pos_delta * 0.3 * bs.abs();
                if transfer < 0.001 { continue; }
                let current = self.boost_buffer.get(distressed_dim).copied().unwrap_or(0.0);
                self.boost_buffer.insert(distressed_dim.clone(), (current + transfer).min(self.boost_buffer_max));
                intervened = true;
            }
        }
        if intervened {
            self.homeostasis_interventions += 1;
            let dims: Vec<String> = distressed.iter().map(|(k, _)| k.clone()).collect();
            self.log_event(cycle, "HOMEOSTASIS", &dims, 0.0,
                format!("{} distressed, {} surplus", distressed.len(), surplus.len()));
        }
    }
    fn process_sublimation(&mut self, tensions: &HashMap<String, f64>, stability_deltas: &HashMap<String, f64>, cycle: usize) {
        for (key, &tension) in tensions {
            if tension.abs() <= 0.2 { continue; }
            let energy = tension.abs() * 0.4;
            let parts: Vec<&str> = key.split("<->").collect();
            if parts.len() != 2 { continue; }
            let mut all_dims: Vec<String> = Vec::new();
            for part in &parts {
                for sub in part.split('+') {
                    let dim = sub.to_lowercase();
                    let dim = dim.trim().to_string();
                    if !dim.is_empty() && !all_dims.contains(&dim) { all_dims.push(dim); }
                }
            }
            if all_dims.is_empty() { continue; }
            let per_dim = energy / all_dims.len() as f64;
            for dim in &all_dims {
                let current = self.boost_buffer.get(dim).copied().unwrap_or(0.0);
                self.boost_buffer.insert(dim.clone(), (current + per_dim).min(self.boost_buffer_max));
            }
            self.sublimation_energy_converted += energy;
            self.log_event(cycle, "SUBLIMATION", &all_dims, energy,
                format!("Tension {:.4} converted to {:.4} energy", tension, energy));
        }
        // FIX5: Intra-cluster micro-tensions from stability delta variance
        if stability_deltas.len() >= 2 {
            let vals: Vec<f64> = stability_deltas.values().cloned().collect();
            let mean = vals.iter().sum::<f64>() / vals.len() as f64;
            let variance = vals.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / vals.len() as f64;
            if variance > 0.0001 {
                let micro_energy = (variance.sqrt() * 2.0).min(0.5);
                let mut sorted_dims: Vec<(String, f64)> = stability_deltas.iter()
                    .map(|(k, &v)| (k.clone(), v.abs()))
                    .collect();
                sorted_dims.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
                let top_n = sorted_dims.len().min(4);
                let per_dim = micro_energy / top_n as f64;
                for (dim, _) in &sorted_dims[..top_n] {
                    let current = self.boost_buffer.get(dim).copied().unwrap_or(0.0);
                    self.boost_buffer.insert(dim.clone(), (current + per_dim).min(self.boost_buffer_max));
                }
                self.sublimation_energy_converted += micro_energy;
            }
        }
    }

    fn process_pressure_tracker(&mut self, fermenting: &HashMap<String, f64>, cycle: usize) {
        for (dim, &ferm_value) in fermenting {
            if ferm_value <= 0.3 { continue; }
            let boost = ferm_value * 0.1;
            let current = self.boost_buffer.get(dim).copied().unwrap_or(0.0);
            self.boost_buffer.insert(dim.clone(), (current + boost).min(self.boost_buffer_max));
            self.pressure_facilitated += 1;
            self.log_event(cycle, "PRESSURE_FACILITATION", &[dim.clone()], boost,
                format!("Fermenting {} at {:.4}", dim, ferm_value));
        }
    }

    fn process_integration_monitor(&mut self, narrative_coherence: f64, _cycle: usize) {
        // FIX3: Only adjust when NC changes significantly (>0.1 delta)
        let nc_delta = (narrative_coherence - self.last_nc).abs();
        if nc_delta > 0.1 {
            if narrative_coherence < 0.4 {
                self.equalization_rate = (self.equalization_rate + 0.05).min(0.6);
            } else if narrative_coherence > 0.7 {
                self.equalization_rate = (self.equalization_rate - 0.02).max(0.1);
            }
            self.last_nc = narrative_coherence;
            self.integration_adjustments += 1;
        }
    }

    fn process_phase_change(&mut self, crystal_transitions: &[(String, String, String)], bridge_strengths: &HashMap<String, f64>, cycle: usize) {
        for (dim, _from, to) in crystal_transitions {
            let wave_strength: f64 = match to.as_str() {
                "crystallized" => 0.15, "growing" => 0.08, "dissolving" => -0.05, _ => 0.0,
            };
            if wave_strength.abs() < 0.001 { continue; }
            let mut neighbors: Vec<String> = Vec::new();
            for (key, &strength) in bridge_strengths {
                if strength < 0.3 { continue; }
                let parts: Vec<&str> = key.split("<->").collect();
                if parts.len() != 2 { continue; }
                if parts[0] == dim && !neighbors.contains(&parts[1].to_string()) {
                    neighbors.push(parts[1].to_string());
                } else if parts[1] == dim && !neighbors.contains(&parts[0].to_string()) {
                    neighbors.push(parts[0].to_string());
                }
            }
            for neighbor in &neighbors {
                let current = self.boost_buffer.get(neighbor).copied().unwrap_or(0.0);
                self.boost_buffer.insert(neighbor.clone(), (current + wave_strength).max(0.0).min(self.boost_buffer_max));
            }
            self.phase_reorganizations += 1;
            self.log_event(cycle, "PHASE_REORGANIZATION", &[dim.clone()], wave_strength,
                format!("{} -> {} (wave={:.3}, {} neighbors)", dim, to, wave_strength, neighbors.len()));
        }
    }
    // === COLLISION ENGINE (unchanged logic, renamed fields) ===

    fn collide(&mut self, cycle: usize) {
        let n = self.ring_count;
        if n < 2 { return; }

        let ring_snapshot: Vec<DreamInsight> = self.ring[..n.min(self.ring.len())].to_vec();

        struct CollisionData {
            a_dims: (String, String),
            b_dims: (String, String),
            shared: String,
            energy: f64,
            product_dims: Vec<String>,
            is_resonance: bool,
        }
        let mut pending: Vec<CollisionData> = Vec::new();

        for i in 0..ring_snapshot.len() {
            for j in (i+1)..ring_snapshot.len() {
                let a = &ring_snapshot[i];
                let b = &ring_snapshot[j];

                let shared = Self::find_shared_dim(a, b);
                if shared.is_none() { continue; }
                let shared = shared.unwrap();

                let base_energy = a.bridge.abs() * b.bridge.abs()
                    * a.convergence * b.convergence;

                if base_energy < self.min_collision_energy { continue; }

                let pair_a = Self::pair_key(&a.dims.0, &a.dims.1);
                let pair_b = Self::pair_key(&b.dims.0, &b.dims.1);
                let freq_a = self.pair_frequency.get(&pair_a).copied().unwrap_or(1) as f64;
                let freq_b = self.pair_frequency.get(&pair_b).copied().unwrap_or(1) as f64;

                let mass_a = (freq_a.ln_1p() + 1.0).min(5.0);
                let mass_b = (freq_b.ln_1p() + 1.0).min(5.0);
                let is_resonance = freq_a > 3.0 || freq_b > 3.0;
                let resonance_factor = if is_resonance { self.resonance_amplifier } else { 1.0 };
                let energy = base_energy * mass_a * mass_b * resonance_factor;

                let mut product_dims = vec![
                    a.dims.0.clone(), a.dims.1.clone(),
                    b.dims.0.clone(), b.dims.1.clone(),
                ];
                product_dims.sort();
                product_dims.dedup();

                pending.push(CollisionData {
                    a_dims: a.dims.clone(),
                    b_dims: b.dims.clone(),
                    shared,
                    energy,
                    product_dims,
                    is_resonance,
                });
            }
        }

        // K+ buffering: proporcional ao numero de colisoes
        self.conflicts_absorbed += pending.len() as f64 * 0.08;

        for cd in pending {
            self.distribute_boost(&cd.product_dims, cd.energy, &cd.shared, cycle);

            let detail = if cd.is_resonance {
                self.resonance_count += 1;
                format!("({}<->{}) x ({}<->{}), shared={}, RESONANCE",
                    cd.a_dims.0, cd.a_dims.1, cd.b_dims.0, cd.b_dims.1, cd.shared)
            } else {
                format!("({}<->{}) x ({}<->{}), shared={}",
                    cd.a_dims.0, cd.a_dims.1, cd.b_dims.0, cd.b_dims.1, cd.shared)
            };
            let event_type = if cd.is_resonance { "RESONANCE" } else { "SYNAPTIC_EVENT" };
            self.log_event(cycle, event_type, &cd.product_dims, cd.energy, detail);

            let event = SynapticEvent {
                particle_a_dims: cd.a_dims,
                particle_b_dims: cd.b_dims,
                shared_dim: cd.shared,
                energy: cd.energy,
                product_dims: cd.product_dims,
                is_resonance: cd.is_resonance,
                order: 1,
                cycle,
            };
            if self.recent_collisions.len() < self.recent_cap {
                self.recent_collisions.push(event);
            } else {
                self.recent_collisions[self.recent_idx % self.recent_cap] = event;
            }
            self.recent_idx += 1;
            if self.recent_count < self.recent_cap {
                self.recent_count += 1;
            }

            self.total_collisions += 1;
            self.total_energy_produced += cd.energy;
            self.window_collisions += 1;
            self.window_energy += cd.energy;
            if cd.energy > self.peak_energy {
                self.peak_energy = cd.energy;
                self.peak_collision_cycle = cycle;
            }
        }
    }

    fn collide_second_order(&mut self, cycle: usize) {
        let n = self.recent_count.min(self.recent_collisions.len());
        if n < 2 { return; }

        let high_energy: Vec<SynapticEvent> = self.recent_collisions[..n].iter()
            .filter(|c| c.energy >= self.second_order_threshold && c.order == 1)
            .cloned()
            .collect();

        if high_energy.len() < 2 { return; }

        struct SecondData {
            all_dims: Vec<String>,
            energy: f64,
            shared: String,
            ca_energy: f64,
            cb_energy: f64,
        }
        let mut pending: Vec<SecondData> = Vec::new();
        let max_pairs = 10;
        let mut pairs_tried = 0;

        for i in 0..high_energy.len() {
            if pairs_tried >= max_pairs { break; }
            for j in (i+1)..high_energy.len() {
                if pairs_tried >= max_pairs { break; }

                let ca = &high_energy[i];
                let cb = &high_energy[j];

                let shared: Vec<String> = ca.product_dims.iter()
                    .filter(|d| cb.product_dims.contains(d))
                    .cloned()
                    .collect();
                if shared.is_empty() { continue; }
                pairs_tried += 1;

                let overlap = shared.len() as f64 / ca.product_dims.len().max(cb.product_dims.len()) as f64;
                let energy = (ca.energy * cb.energy).sqrt() * overlap * 2.0;
                if energy < self.min_collision_energy { continue; }

                let mut all_dims: Vec<String> = ca.product_dims.iter()
                    .chain(cb.product_dims.iter())
                    .cloned()
                    .collect();
                all_dims.sort();
                all_dims.dedup();

                pending.push(SecondData {
                    all_dims, energy, shared: shared[0].clone(),
                    ca_energy: ca.energy, cb_energy: cb.energy,
                });
            }
        }

        for sd in pending {
            self.distribute_boost(&sd.all_dims, sd.energy * 1.5, &sd.shared, cycle);

            self.log_event(cycle, "SECOND_ORDER", &sd.all_dims, sd.energy,
                format!("Astrocyte cascade! {}d via {}, parent_E={:.4}+{:.4}",
                    sd.all_dims.len(), sd.shared, sd.ca_energy, sd.cb_energy));

            self.second_order_count += 1;
            self.total_energy_produced += sd.energy;
            self.total_collisions += 1;
            self.window_collisions += 1;
            self.window_energy += sd.energy;

            if sd.energy > self.peak_energy {
                self.peak_energy = sd.energy;
                self.peak_collision_cycle = cycle;
            }
        }
    }

    /// distribute_boost() - formerly lactate_shuttle()
    /// Uses equalization_rate from Integration Monitor
    fn distribute_boost(&mut self, dims: &[String], energy: f64, shared_dim: &str, cycle: usize) {
        let n = dims.len() as f64;
        if n < 1.0 { return; }
        let injectable = energy * self.injection_rate;
        let eq_rate = self.equalization_rate;
        for dim in dims {
            let proportional_share = if dim == shared_dim { 0.4 } else { 0.6 / (n - 1.0).max(1.0) };
            let equal_share = 1.0 / n;
            let share = proportional_share * (1.0 - eq_rate) + equal_share * eq_rate;
            let amount = injectable * share;
            let current = self.boost_buffer.get(dim).copied().unwrap_or(0.0);
            self.boost_buffer.insert(dim.clone(), (current + amount).min(self.boost_buffer_max));
            *self.dim_energy_injected.entry(dim.clone()).or_insert(0.0) += amount;
            self.total_energy_injected += amount;
        }
        if injectable > 0.01 {
            self.log_event(cycle, "DISTRIBUTE_BOOST", dims, injectable,
                format!("hub={}, buf_total={:.4}, eq_rate={:.2}",
                    shared_dim, self.boost_buffer.values().sum::<f64>(), eq_rate));
        }
    }

    pub fn get_boost(&mut self, dim: &str) -> f64 {
        let base = self.boost_buffer.get(dim).copied().unwrap_or(0.0);
        if base > 0.001 {
            // Consume 30% of buffer on use (use it or lose it)
            let consumed = base * 0.30;
            self.boost_buffer.insert(dim.to_string(), base - consumed);
            consumed  // return what was consumed as the boost
        } else {
            0.0
        }
    }

    pub fn total_buffer_energy(&self) -> f64 {
        self.boost_buffer.values().sum()
    }


    /// GLYMPHATIC FLUSH - Clear metabolic waste during sleep cycle
    /// Like cerebrospinal fluid washing the brain during sleep
    pub fn glymphatic_flush(&mut self, intensity: f64) {
        // 1. Drain ALL boost buffers proportionally
        for (_dim, boost) in self.boost_buffer.iter_mut() {
            *boost *= 1.0 - intensity * 0.8;  // drain 80% at full intensity
        }
        
        // 2. Clear pair_frequency (forget old collision patterns)
        // Keep only high-frequency pairs (established patterns)
        let threshold = 3;  // pairs with <3 collisions get cleared
        self.pair_frequency.retain(|_, &mut freq| freq >= threshold);
        // Decay remaining frequencies
        for (_pair, freq) in self.pair_frequency.iter_mut() {
            *freq = (*freq as f64 * (1.0 - intensity * 0.3)) as usize;
        }
        
        // 3. Reset recent collisions window
        self.recent_count = 0;
        self.recent_idx = 0;
        
        // 4. Reset window counters
        self.window_collisions = 0;
        self.window_energy = 0.0;
        
        // 5. Decay accumulated conflict absorption
        self.conflicts_absorbed *= 1.0 - intensity * 0.5;
        
        // 6. Trim log (keep only last 100 entries)
        if self.log.len() > 100 {
            let start = self.log.len() - 100;
            self.log = self.log[start..].to_vec();
        }
    }
    pub fn flush_window(&mut self) {
        self.collision_history.push(self.window_collisions);
        self.energy_history.push(self.window_energy);
        if self.collision_history.len() > 100 {
            self.collision_history.drain(0..1);
            self.energy_history.drain(0..1);
        }
        self.window_collisions = 0;
        self.window_energy = 0.0;
    }

    pub fn state(&self) -> AstrocyteState {
        let coll_rate = if self.collision_history.len() >= 2 {
            let last5: Vec<f64> = self.collision_history.iter().rev().take(5)
                .map(|&x| x as f64).collect();
            last5.iter().sum::<f64>() / last5.len() as f64
        } else { 0.0 };
        let energy_rate = if self.energy_history.len() >= 2 {
            let last5: Vec<f64> = self.energy_history.iter().rev().take(5).cloned().collect();
            last5.iter().sum::<f64>() / last5.len() as f64
        } else { 0.0 };
        AstrocyteState {
            total_collisions: self.total_collisions,
            total_energy_produced: self.total_energy_produced,
            total_energy_injected: self.total_energy_injected,
            second_order_count: self.second_order_count,
            resonance_count: self.resonance_count,
            peak_energy: self.peak_energy,
            peak_collision_cycle: self.peak_collision_cycle,
            dim_energy_injected: self.dim_energy_injected.clone(),
            collision_rate: coll_rate,
            energy_rate,
            insights_recycled: self.insights_recycled,
            dreams_drained: self.dreams_drained,
            conflicts_absorbed: self.conflicts_absorbed,
            eurekas_amplified: self.eurekas_amplified,
            conflicts_absorbed_total: self.conflicts_absorbed_total,
            homeostasis_interventions: self.homeostasis_interventions,
            sublimation_energy_converted: self.sublimation_energy_converted,
            pressure_facilitated: self.pressure_facilitated,
            integration_adjustments: self.integration_adjustments,
            phase_reorganizations: self.phase_reorganizations,
            equalization_rate: self.equalization_rate,
        }
    }

    fn find_shared_dim(a: &DreamInsight, b: &DreamInsight) -> Option<String> {
        let a_dims = [&a.dims.0, &a.dims.1];
        let b_dims = [&b.dims.0, &b.dims.1];
        for ad in &a_dims {
            for bd in &b_dims {
                if ad == bd { return Some((*ad).clone()); }
            }
        }
        None
    }

    fn pair_key(a: &str, b: &str) -> String {
        let mut pair = [a, b];
        pair.sort();
        format!("{}+{}", pair[0], pair[1])
    }

    fn log_event(&mut self, cycle: usize, event_type: &str, dims: &[String], energy: f64, detail: String) {
        if self.log.len() >= self.log_capacity {
            let half = self.log_capacity / 2;
            self.log.drain(0..half);
        }
        self.log.push(AstrocyteLogEntry {
            cycle, event_type: event_type.to_string(),
            dims: dims.to_vec(), energy, detail,
        });
    }
}

