//! Crystal Engine v2 - Inconsciente com Identity Lock
//! Ring buffer com rolling stats, bridges por correlacao, estados de fase.
//! FIX 1: Core Identity Lock - cristais core preservam baseline
//! FIX 2: Stability window diferenciada por cristal
//! FIX 3: Crystallization threshold variavel por cristal

use std::collections::HashMap;

#[derive(Clone, Debug, PartialEq)]
pub enum CrystalState {
    Nascent,
    Growing,
    Crystallized,
    Dissolving,
}

impl CrystalState {
    pub fn as_str(&self) -> &'static str {
        match self {
            CrystalState::Nascent => "nascent",
            CrystalState::Growing => "growing",
            CrystalState::Crystallized => "crystallized",
            CrystalState::Dissolving => "dissolving",
        }
    }
}

#[derive(Clone, Debug)]
pub struct Crystal {
    pub name: String,
    buffer: Vec<f64>,
    buf_idx: usize,
    buf_count: usize,
    buf_size: usize,
    pub constant: Option<f64>,
    pub stability: f64,
    pub coherence: f64,
    pub state: CrystalState,
    pub absorptions: usize,
    pub transitions: usize,
    stability_window: usize,
    crystallization_threshold: f64,
    // Rolling stats
    running_sum: f64,
    running_sq_sum: f64,
    // FIX 1: Identity Lock
    baseline_mean: Option<f64>,
    baseline_locked: bool,
    baseline_blend: f64, // 0.0-1.0, how much baseline vs new (0.7 = 70% baseline)
    // Track stability delta for censor feedback
    pub prev_stability: f64,
}

impl Crystal {
    pub fn new(name: &str, buf_size: usize, stability_window: usize, cryst_thresh: f64) -> Self {
        Crystal {
            name: name.to_string(),
            buffer: vec![0.0; buf_size],
            buf_idx: 0,
            buf_count: 0,
            buf_size,
            constant: None,
            stability: 0.0,
            coherence: 0.0,
            state: CrystalState::Nascent,
            absorptions: 0,
            transitions: 0,
            stability_window,
            crystallization_threshold: cryst_thresh,
            running_sum: 0.0,
            running_sq_sum: 0.0,
            // FIX 1
            baseline_mean: None,
            baseline_locked: false,
            baseline_blend: 0.5, // FIX C2: was 0.7, reduced to allow locked dims to grow more
            prev_stability: 0.0,
        }
    }

    /// FIX 1: Lock the current mean as baseline identity anchor
    pub fn lock_baseline(&mut self) {
        if let Some(mean) = self.constant {
            self.baseline_mean = Some(mean);
            self.baseline_locked = true;
        }
    }

    /// FIX 1: Unlock baseline (for recalibration)
    pub fn unlock_baseline(&mut self) {
        self.baseline_locked = false;
    }

    pub fn is_locked(&self) -> bool {
        self.baseline_locked
    }

    pub fn absorb(&mut self, value: f64) {
        // FIX 1: If baseline locked, blend value toward baseline
        let effective_value = if self.baseline_locked {
            if let Some(base) = self.baseline_mean {
                // Blend: 70% baseline + 30% new value
                // This prevents diverse content from destabilizing core identity
                base * self.baseline_blend + value * (1.0 - self.baseline_blend)
            } else {
                value
            }
        } else {
            value
        };

        // Save prev stability for delta tracking (FIX 4)
        self.prev_stability = self.stability;

        // Remove old value from running stats if buffer full
        if self.buf_count >= self.buf_size {
            let old = self.buffer[self.buf_idx % self.buf_size];
            self.running_sum -= old;
            self.running_sq_sum -= old * old;
        }

        // Insert new value
        self.buffer[self.buf_idx % self.buf_size] = effective_value;
        self.running_sum += effective_value;
        self.running_sq_sum += effective_value * effective_value;
        self.buf_idx += 1;
        if self.buf_count < self.buf_size {
            self.buf_count += 1;
        }
        self.absorptions += 1;

        // Update constant and stability
        if self.buf_count >= 2 {
            let n = self.buf_count as f64;
            let mean = self.running_sum / n;
            let var = (self.running_sq_sum / n) - mean * mean;
            let _std = if var > 0.0 { var.sqrt() } else { 0.0 };

            self.constant = Some(mean);

            // Stability from recent window (FIX 2: window size varies per crystal)
            let window = self.stability_window.min(self.buf_count);
            if window >= 2 {
                let start = if self.buf_count >= self.buf_size {
                    (self.buf_idx + self.buf_size - window) % self.buf_size
                } else {
                    self.buf_count - window
                };
                let mut w_sum = 0.0;
                let mut w_sq = 0.0;
                for i in 0..window {
                    let idx = (start + i) % self.buf_size;
                    let v = self.buffer[idx];
                    w_sum += v;
                    w_sq += v * v;
                }
                let wn = window as f64;
                let w_mean = w_sum / wn;
                let w_var = (w_sq / wn) - w_mean * w_mean;
                let w_std = if w_var > 0.0 { w_var.sqrt() } else { 0.0 };
                let cv = if w_mean.abs() > 1e-10 { w_std / w_mean.abs() } else { 1.0 };
                self.stability = (1.0 - cv).max(0.0).min(1.0);
            }

            // State transitions (FIX 5: minimum absorptions + gradual decay)
            // A crystal should NOT crystallize in <10 cycles (audit fix)
            let old_state = self.state.clone();
            let min_absorptions_for_cryst = 10usize;
            if self.stability >= self.crystallization_threshold && self.absorptions >= min_absorptions_for_cryst {
                self.state = CrystalState::Crystallized;
            } else if self.stability >= 0.4 && self.absorptions >= 5 {
                self.state = CrystalState::Growing;
            } else if self.absorptions > 15 && self.stability < 0.25 {
                self.state = CrystalState::Dissolving;
            } else {
                self.state = CrystalState::Nascent;
            }
            if old_state != self.state {
                self.transitions += 1;
            }
        }
    }

    /// Stability delta since last absorb (FIX 4: for censor feedback)
    pub fn stability_delta(&self) -> f64 {
        self.stability - self.prev_stability
    }

    /// Get last N values from ring buffer
    pub fn last_n(&self, n: usize) -> Vec<f64> {
        let count = n.min(self.buf_count);
        let mut result = Vec::with_capacity(count);
        for i in 0..count {
            let idx = if self.buf_count >= self.buf_size {
                (self.buf_idx + self.buf_size - count + i) % self.buf_size
            } else {
                self.buf_count - count + i
            };
            result.push(self.buffer[idx]);
        }
        result
    }

    /// EXHAUST: Relax crystal tension - allow constant to drift
    /// Returns the amount of stress released
    pub fn exhaust_relax(&mut self, intensity: f64) -> f64 {
        let stress = 0.0_f64;
        
        // 1. Stability decay - let it breathe
        let stability_drop = self.stability * intensity * 0.15;  // drop 15% of stability at full intensity
        self.stability = (self.stability - stability_drop).max(0.1);
        
        // 2. If locked, temporarily widen the blend (allow more new data influence)
        // This is the key: during "sleep", locked crystals can shift
        if self.baseline_locked {
            // Temporarily reduce baseline influence (0.5 -> 0.3 during sleep)
            // After re-lock, it goes back to 0.5
            self.baseline_blend = (self.baseline_blend - intensity * 0.2).max(0.2);
        }
        
        // 3. State can regress: crystallized -> growing during heavy exhaust
        if intensity > 0.5 && self.state == CrystalState::Crystallized {
            // Only regress if stability actually dropped below threshold
            if self.stability < self.crystallization_threshold {
                self.state = CrystalState::Growing;
                self.transitions += 1;
            }
        }
        
        stability_drop
    }
    
    /// EXHAUST: Re-anchor after sleep - restore baseline blend
    pub fn exhaust_reanchor(&mut self) {
        if self.baseline_locked {
            // Restore normal blend, but UPDATE baseline to current mean
            // This is the "learning during sleep" - baseline shifts
            if let Some(current) = self.constant {
                if let Some(base) = self.baseline_mean {
                    // Shift baseline 10% toward current (consolidation)
                    self.baseline_mean = Some(base * 0.9 + current * 0.1);
                }
            }
            self.baseline_blend = 0.5;  // restore normal blend
        }
    }

/// Bridge between two crystals
#[derive(Clone, Debug)]
pub struct Bridge {
    pub a: String,
    pub b: String,
    pub strength: f64,
}

/// Crystal Lattice - collection of crystals with bridges
#[derive(Clone, Debug)]
pub struct CrystalLattice {
    pub crystals: HashMap<String, Crystal>,
    pub bridges: HashMap<String, f64>,
}

impl CrystalLattice {
    pub fn new() -> Self {
        CrystalLattice {
            crystals: HashMap::new(),
            bridges: HashMap::new(),
        }
    }

    pub fn add_crystal(&mut self, name: &str, buf_size: usize, stability_window: usize, cryst_thresh: f64) {
        self.crystals.insert(name.to_string(), Crystal::new(name, buf_size, stability_window, cryst_thresh));
    }

    pub fn absorb(&mut self, name: &str, value: f64) -> bool {
        if let Some(crystal) = self.crystals.get_mut(name) {
            crystal.absorb(value);
            true
        } else {
            false
        }
    }

    /// FIX 1: Lock baseline for specified crystals
    pub fn lock_crystals(&mut self, names: &[&str]) {
        for name in names {
            if let Some(crystal) = self.crystals.get_mut(*name) {
                crystal.lock_baseline();
            }
        }
    }

    /// FIX 4: Get stability deltas for censor feedback
    pub fn get_stability_deltas(&self) -> HashMap<String, f64> {
        self.crystals.iter()
            .map(|(k, c)| (k.clone(), c.stability_delta()))
            .collect()
    }

    /// Update all bridges using correlation of recent values
    pub fn update_bridges(&mut self) {
        let names: Vec<String> = self.crystals.keys().cloned().collect();
        let window = 20;

        // Collect recent values for each crystal
        let mut recent: HashMap<String, Vec<f64>> = HashMap::new();
        for name in &names {
            if let Some(c) = self.crystals.get(name) {
                recent.insert(name.clone(), c.last_n(window));
            }
        }

        // Compute pairwise correlation
        for i in 0..names.len() {
            for j in (i+1)..names.len() {
                let a = &names[i];
                let b = &names[j];
                if let (Some(va), Some(vb)) = (recent.get(a), recent.get(b)) {
                    let n = va.len().min(vb.len());
                    if n >= 4 {
                        let strength = pearson_corr(&va[..n], &vb[..n]);
                        let key = format!("{}<->{}", a, b);
                        self.bridges.insert(key, strength);
                    }
                }
            }
        }

        // Update coherence for each crystal
        for name in &names {
            let mut total = 0.0;
            let mut count = 0;
            for (key, &val) in &self.bridges {
                if key.contains(name.as_str()) {
                    total += val.abs();
                    count += 1;
                }
            }
            if let Some(c) = self.crystals.get_mut(name) {
                c.coherence = if count > 0 { total / count as f64 } else { 0.0 };
            }
        }
    }


    /// EXHAUST SYSTEM: Sleep cycle for the whole lattice
    /// Returns total stress released
    pub fn sleep_cycle(&mut self, intensity: f64) -> f64 {
        let mut total_stress = 0.0;
        
        // Phase 1: Relax all crystals
        for (_name, crystal) in self.crystals.iter_mut() {
            total_stress += crystal.exhaust_relax(intensity);
        }
        
        // Phase 2: Decay bridges (forget weak connections)
        let weak_bridges: Vec<String> = self.bridges.iter()
            .filter(|(_, &v)| v.abs() < 0.3)  // weak bridges
            .map(|(k, _)| k.clone())
            .collect();
        for key in weak_bridges {
            if let Some(v) = self.bridges.get_mut(&key) {
                *v *= 1.0 - intensity * 0.5;  // decay 50% at full intensity
            }
        }
        
        // Phase 3: Strengthen strong bridges (consolidation)
        for (_key, v) in self.bridges.iter_mut() {
            if v.abs() > 0.6 {
                // Strong bridges get slightly stronger (capped at 1.0)
                *v = (*v * (1.0 + intensity * 0.1)).min(1.0).max(-1.0);
            }
        }
        
        total_stress
    }
    
    /// EXHAUST: Re-anchor all crystals after sleep
    pub fn wake_cycle(&mut self) {
        for (_name, crystal) in self.crystals.iter_mut() {
            crystal.exhaust_reanchor();
        }
    }
    pub fn get_constants(&self) -> HashMap<String, f64> {
        let mut result = HashMap::new();
        for (name, crystal) in &self.crystals {
            if let Some(c) = crystal.constant {
                result.insert(name.clone(), c);
            }
        }
        result
    }

    pub fn get_states(&self) -> HashMap<String, String> {
        self.crystals.iter()
            .map(|(k, v)| (k.clone(), v.state.as_str().to_string()))
            .collect()
    }
}

fn pearson_corr(a: &[f64], b: &[f64]) -> f64 {
    let n = a.len() as f64;
    if n < 2.0 { return 0.0; }
    let mean_a: f64 = a.iter().sum::<f64>() / n;
    let mean_b: f64 = b.iter().sum::<f64>() / n;
    let mut cov = 0.0;
    let mut var_a = 0.0;
    let mut var_b = 0.0;
    for i in 0..a.len() {
        let da = a[i] - mean_a;
        let db = b[i] - mean_b;
        cov += da * db;
        var_a += da * da;
        var_b += db * db;
    }
    let denom = (var_a * var_b).sqrt();
    if denom < 1e-15 { 0.0 } else { (cov / denom).clamp(-1.0, 1.0) }
}




