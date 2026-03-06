//! Consciousness Metrics - Phi, Criticality, FDI, Hurst
//! Computacoes numericas pesadas que beneficiam de Rust.

use std::collections::HashMap;

/// Phi proxy (IIT): integrated information via CV + irreducibility
pub fn phi_proxy(constants: &HashMap<String, f64>) -> f64 {
    let vals: Vec<f64> = constants.values().cloned().collect();
    let n = vals.len();
    if n < 2 { return 0.0; }
    
    let mean = vals.iter().sum::<f64>() / n as f64;
    if mean.abs() < 1e-10 { return 0.0; }
    
    let std = (vals.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / n as f64).sqrt();
    let cv = std / mean.abs();
    let integration = (1.0 - cv).max(0.0);
    
    // Irreducibility: min loss when removing each part
    let mut losses = Vec::with_capacity(n);
    for i in 0..n {
        let reduced: Vec<f64> = vals.iter().enumerate()
            .filter(|&(j, _)| j != i)
            .map(|(_, &v)| v)
            .collect();
        if reduced.is_empty() { continue; }
        let rm = reduced.iter().sum::<f64>() / reduced.len() as f64;
        if rm.abs() < 1e-10 { losses.push(integration); continue; }
        let rs = (reduced.iter().map(|v| (v - rm).powi(2)).sum::<f64>() / reduced.len() as f64).sqrt();
        let rcv = rs / rm.abs();
        let ri = (1.0 - rcv).max(0.0);
        losses.push((integration - ri).abs());
    }
    
    let irreducibility = losses.iter().cloned().fold(f64::MAX, f64::min).min(1.0);
    (integration * (1.0 + irreducibility)).clamp(0.0, 2.0)
}

/// Criticality v2 (SOC): consciousness at edge of chaos
/// FIX E: State component only; run_pipeline adds continuous components
pub fn criticality(states: &HashMap<String, String>) -> f64 {
    let n = states.len();
    if n == 0 { return 0.0; }
    let mut counts: HashMap<&str, usize> = HashMap::new();
    for s in states.values() {
        *counts.entry(s.as_str()).or_insert(0) += 1;
    }
    let n_states = counts.len();
    let diversity_bonus: f64 = match n_states {
        1 => 0.15, 2 => 0.50, 3 => 0.80, _ => 1.00,
    };
    let edge_bonus = if counts.contains_key("growing") && counts.contains_key("crystallized") {
        0.2
    } else if counts.contains_key("nascent") && counts.contains_key("crystallized") {
        0.1
    } else {
        0.0
    };
    (diversity_bonus * 0.5 + edge_bonus).clamp(0.0_f64, 1.0_f64)
}

/// Continuous criticality from crystal properties
/// A mature (all-crystallized) system can still be at edge of chaos
/// if crystals have diverse stabilities, coherences, tensions
pub fn criticality_continuous(
    stabilities: &[f64], coherences: &[f64], constants: &[f64],
    bridges: &HashMap<String, f64>, state_component: f64,
) -> f64 {
    if stabilities.len() < 2 { return state_component; }
    // C1: Stability variance (30%)
    let sm: f64 = stabilities.iter().sum::<f64>() / stabilities.len() as f64;
    let ss = (stabilities.iter().map(|s| (s-sm).powi(2)).sum::<f64>() / stabilities.len() as f64).sqrt();
    let scv = if sm > 1e-10 { ss/sm } else { 0.0 };
    let sd = (scv * 10.0).min(1.0);
    // C2: Bridge tension (25%)
    let bt = if !bridges.is_empty() {
        let w = bridges.values().filter(|&&b| b.abs() < 0.3).count();
        let neg = bridges.values().filter(|&&b| b < -0.1).count();
        ((w + neg * 2) as f64 / bridges.len() as f64).min(1.0)
    } else { 0.5 };
    // C3: Coherence spread (20%)
    let cm: f64 = coherences.iter().sum::<f64>() / coherences.len() as f64;
    let cs = (coherences.iter().map(|c| (c-cm).powi(2)).sum::<f64>() / coherences.len() as f64).sqrt();
    let ccv = if cm > 1e-10 { cs/cm } else { 0.0 };
    let csp = (ccv * 5.0).min(1.0);
    // C4: Constant diversity (15%)
    let km: f64 = constants.iter().sum::<f64>() / constants.len() as f64;
    let ks = (constants.iter().map(|c| (c-km).powi(2)).sum::<f64>() / constants.len() as f64).sqrt();
    let kcv = if km > 1e-10 { ks/km } else { 0.0 };
    let kd = (kcv * 3.0).min(1.0);
    // C5: State-based (10%)
    (sd*0.30 + bt*0.25 + csp*0.20 + kd*0.15 + state_component*0.10).clamp(0.0, 1.0)
}

/// Fractal Dimension Index (Higuchi method)
pub fn fdi(data: &[f64]) -> f64 {
    let n = data.len();
    if n < 32 { return 0.0; }
    
    let k_max = 16.min(n / 4);
    let mut l_vals = Vec::new();
    
    for k in 1..=k_max {
        let mut lk_vals = Vec::new();
        for m in 1..=k {
            let mut idx = m - 1;
            let mut seg_diffs = Vec::new();
            while idx + k < n {
                seg_diffs.push((data[idx + k] - data[idx]).abs());
                idx += k;
            }
            if seg_diffs.is_empty() { continue; }
            let norm = (n - 1) as f64 / (k * seg_diffs.len() * k) as f64;
            let sum: f64 = seg_diffs.iter().sum();
            lk_vals.push(sum * norm);
        }
        if !lk_vals.is_empty() {
            let mean_lk: f64 = lk_vals.iter().sum::<f64>() / lk_vals.len() as f64;
            l_vals.push((mean_lk + 1e-10).ln());
        }
    }
    
    if l_vals.len() < 2 { return 0.0; }
    
    let log_k: Vec<f64> = (1..=l_vals.len()).map(|k| -(k as f64).ln()).collect();
    let slope = linear_slope(&log_k, &l_vals);
    let fd = slope.clamp(1.0, 2.0);
    
    {
        // FIX E9b: Linear FDI - fd=1.5 ideal, fd=2.0 still valuable (0.2 floor)
        // Philosophical: high fd = active information processing, not pathological
        if fd <= 1.5 {
            ((fd - 0.7) / 0.6).clamp(0.0, 1.0)
        } else {
            (1.0 - (fd - 1.5) * 1.2).max(0.25)
        }
    }
}

/// Quick Hurst exponent via R/S analysis
pub fn hurst(data: &[f64]) -> f64 {
    let n = data.len();
    if n < 16 { return 0.5; }
    
    let scales = [8usize, 16, 32, 64];
    let mut log_scales = Vec::new();
    let mut log_rs = Vec::new();
    
    for &scale in &scales {
        if scale > n / 2 { break; }
        let mut rs_list = Vec::new();
        let blocks = n / scale;
        for i in 0..blocks {
            let block = &data[i * scale..(i + 1) * scale];
            if block.len() < 2 { continue; }
            let mean: f64 = block.iter().sum::<f64>() / block.len() as f64;
            
            let mut cumdev = Vec::with_capacity(block.len() - 1);
            let mut cum = 0.0;
            for j in 1..block.len() {
                cum += (block[j] - block[j-1]) - (block.iter().skip(1).zip(block.iter()).map(|(a, b)| a - b).sum::<f64>() / (block.len() - 1) as f64);
                cumdev.push(cum);
            }
            
            // Simpler: use returns
            let rets: Vec<f64> = (1..block.len()).map(|j| block[j] - block[j-1]).collect();
            if rets.is_empty() { continue; }
            let ret_mean: f64 = rets.iter().sum::<f64>() / rets.len() as f64;
            let mut devs = Vec::with_capacity(rets.len());
            let mut cs = 0.0;
            for r in &rets {
                cs += r - ret_mean;
                devs.push(cs);
            }
            let r = devs.iter().cloned().fold(f64::NEG_INFINITY, f64::max)
                  - devs.iter().cloned().fold(f64::INFINITY, f64::min);
            let s = std_dev(&rets);
            if s > 1e-10 {
                rs_list.push(r / s);
            }
        }
        if !rs_list.is_empty() {
            let mean_rs: f64 = rs_list.iter().sum::<f64>() / rs_list.len() as f64;
            log_scales.push((scale as f64).ln());
            log_rs.push(mean_rs.ln());
        }
    }
    
    if log_scales.len() < 2 { return 0.5; }
    linear_slope(&log_scales, &log_rs).clamp(0.01, 0.99)
}

/// Multiscale Hurst (micro=16, meso=64, macro=128)
pub fn multiscale_hurst(data: &[f64]) -> (f64, f64, f64) {
    let n = data.len();
    let micro = if n >= 16 { hurst(&data[n.saturating_sub(16)..]) } else { 0.5 };
    let meso = if n >= 64 { hurst(&data[n.saturating_sub(64)..]) } else { 0.5 };
    let macro_h = if n >= 128 { hurst(&data[n.saturating_sub(128)..]) } else { 0.5 };
    (micro, meso, macro_h)
}

// Helpers
fn linear_slope(x: &[f64], y: &[f64]) -> f64 {
    let n = x.len() as f64;
    if n < 2.0 { return 0.0; }
    let sx: f64 = x.iter().sum();
    let sy: f64 = y.iter().sum();
    let sxy: f64 = x.iter().zip(y.iter()).map(|(a, b)| a * b).sum();
    let sx2: f64 = x.iter().map(|a| a * a).sum();
    let denom = n * sx2 - sx * sx;
    if denom.abs() < 1e-15 { 0.0 } else { (n * sxy - sx * sy) / denom }
}

fn std_dev(data: &[f64]) -> f64 {
    let n = data.len() as f64;
    if n < 2.0 { return 0.0; }
    let mean = data.iter().sum::<f64>() / n;
    let var = data.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / (n - 1.0);
    var.sqrt()
}



