//! PreConscious Engine v0.3 - Pipeline completo em Rust
//! Censor -> Condensacao -> Displacement -> Ignition+Cascade -> Elaboration
//! + Dream -> Insight -> Resistance -> Sublimation

use std::collections::HashMap;

// ============================================================
// CENSOR
// ============================================================
#[derive(Clone, Debug)]
pub struct Censor {
    pub mission: HashMap<String, f64>,
    pub adaptive_weights: HashMap<String, f64>,
    weight_min: f64,
    weight_max: f64,
}

#[derive(Clone, Debug)]
pub struct CensoredSignal {
    pub value: f64,
    pub raw_value: f64,
    pub weight: f64,
    pub stability: f64,
    pub coherence: f64,
    pub state: String,
}

impl Censor {
    pub fn new(mission: HashMap<String, f64>) -> Self {
        let weights: HashMap<String, f64> = mission.keys().map(|k| (k.clone(), 1.0)).collect();
        Censor { mission, adaptive_weights: weights, weight_min: 0.5, weight_max: 2.0 }
    }

    pub fn filter(&self, crystal_data: &HashMap<String, CrystalInfo>) -> HashMap<String, CensoredSignal> {
        let raw: HashMap<&String, f64> = crystal_data.iter()
            .filter_map(|(k, v)| v.constant.map(|c| (k, c)))
            .collect();
        if raw.is_empty() { return HashMap::new(); }
        
        // Neutralize (mean-normalization) 
        // FIX: min-max forced range [0,1] which destroyed CV for phi_proxy
        // Mean-norm preserves relative distances and CV properties
        // Values centered around 1.0, no artificial 0.0/1.0 extremes
        let vals: Vec<f64> = raw.values().cloned().collect();
        let mean_val = vals.iter().sum::<f64>() / vals.len() as f64;
        let norm_divisor = if mean_val.abs() > 1e-10 { mean_val } else { 1.0 };
        
        let mut result = HashMap::new();
        for (dim, &raw_c) in &raw {
            let nval = raw_c / norm_divisor;
            let info = &crystal_data[*dim];
            let ms = self.mission.get(*dim).copied().unwrap_or(0.5);
            let stab = info.stability;
            let rec = info.recency;
            let base_rel = ms * stab * rec;
            let adaptive = self.adaptive_weights.get(*dim).copied().unwrap_or(1.0);
            let weight = (base_rel * adaptive * 2.0).clamp(self.weight_min, self.weight_max);
            
            result.insert((*dim).clone(), CensoredSignal {
                value: nval * weight,
                raw_value: nval,
                weight,
                stability: stab,
                coherence: info.coherence,
                state: info.state.clone(),
            });
        }
        result
    }

    /// FIX 4v2: Stability-aware feedback with crystallization protection
    /// - Crystallized dims with high stability: LEAVE ALONE (no decay)
    /// - Stability improving but not yet crystallized: gentle decay
    /// - Stability worsening on mission-critical: boost
    /// - Weight floor proportional to mission weight (not flat 0.5)
    pub fn feedback(
        &mut self,
        _phi: f64,
        mission_alignment: f64,
        ignited_dims: &[String],
        stability_deltas: &HashMap<String, f64>,
        crystal_stabilities: &HashMap<String, f64>,
    ) {
        for (dim, w) in self.adaptive_weights.iter_mut() {
            let delta = stability_deltas.get(dim).copied().unwrap_or(0.0);
            let stab = crystal_stabilities.get(dim).copied().unwrap_or(0.0);
            let mw = self.mission.get(dim).copied().unwrap_or(0.5);

            // Dynamic floor: mission-critical dims keep weight >= mission_weight * 0.8
            let dynamic_floor = (mw * 0.8).max(self.weight_min);

            if stab > 0.75 {
                // Crystallized or near-crystallized: STABLE, no change
                // This prevents locked core from decaying to floor
            } else if delta > 0.01 {
                // Stability improving, not yet crystallized -> gentle relax
                *w *= 0.995;
            } else if delta < -0.01 && mw > 0.7 {
                // Stability worsened on mission-critical -> protect
                *w *= 1.01;
            } else if !ignited_dims.contains(dim) {
                // Not ignited, no stability change -> gentle boost
                *w *= 1.005;
            } else {
                // Ignited normally -> very slight decay
                *w *= 0.998;
            }
            *w = w.clamp(dynamic_floor, self.weight_max);
        }

        // Global misalignment: boost high-mission dims
        if mission_alignment < 0.4 {
            for (dim, mw) in &self.mission {
                if *mw > 0.8 {
                    if let Some(w) = self.adaptive_weights.get_mut(dim) {
                        let floor = (mw * 0.8).max(self.weight_min);
                        *w = (*w * 1.005).clamp(floor, self.weight_max);
                    }
                }
            }
        }
    }
}

// ============================================================
// CRYSTAL INFO (input to pipeline)
// ============================================================
#[derive(Clone, Debug)]
pub struct CrystalInfo {
    pub constant: Option<f64>,
    pub stability: f64,
    pub coherence: f64,
    pub state: String,
    pub recency: f64,
}

// ============================================================
// CONDENSATION
// ============================================================
#[derive(Clone, Debug)]
pub struct Cluster {
    pub label: String,
    pub members: Vec<String>,
    pub member_values: HashMap<String, f64>,
    pub member_weights: HashMap<String, f64>,
    pub cluster_value: f64,
    pub sources: HashMap<String, CensoredSignal>,
}

pub fn condense(
    censored: &HashMap<String, CensoredSignal>,
    bridges: &HashMap<String, f64>,
    pos_threshold: f64,
) -> (Vec<Cluster>, HashMap<String, f64>) {
    let dims: Vec<String> = censored.keys().cloned().collect();
    
    // Union-Find clustering
    let mut parent: HashMap<String, String> = dims.iter().map(|d| (d.clone(), d.clone())).collect();
    
    fn find(parent: &mut HashMap<String, String>, x: &str) -> String {
        let p = parent.get(x).cloned().unwrap_or_else(|| x.to_string());
        if p != x {
            let root = find(parent, &p);
            parent.insert(x.to_string(), root.clone());
            root
        } else {
            p
        }
    }
    
    for (key, &strength) in bridges {
        if strength >= pos_threshold {
            let parts: Vec<&str> = key.split("<->").collect();
            if parts.len() == 2 && parent.contains_key(parts[0]) && parent.contains_key(parts[1]) {
                let ra = find(&mut parent, parts[0]);
                let rb = find(&mut parent, parts[1]);
                if ra != rb {
                    parent.insert(rb, ra);
                }
            }
        }
    }
    
    // Group into clusters
    let mut groups: HashMap<String, Vec<String>> = HashMap::new();
    for dim in &dims {
        let root = find(&mut parent, dim);
        groups.entry(root).or_default().push(dim.clone());
    }
    
    let mut clusters = Vec::new();
    for (_root, members) in groups {
        let mut mv = HashMap::new();
        let mut mw = HashMap::new();
        let mut sources = HashMap::new();
        for m in &members {
            if let Some(cs) = censored.get(m) {
                mv.insert(m.clone(), cs.value);
                mw.insert(m.clone(), cs.weight);
                sources.insert(m.clone(), cs.clone());
            }
        }
        let ws: f64 = mw.values().sum();
        let cluster_value = if ws > 0.0 {
            mv.iter().map(|(k, v)| v * mw.get(k).unwrap_or(&1.0)).sum::<f64>() / ws
        } else {
            mv.values().sum::<f64>() / mv.len().max(1) as f64
        };
        let label = label_cluster(&members);
        clusters.push(Cluster { label, members, member_values: mv, member_weights: mw, cluster_value, sources });
    }
    
    // Tensions between clusters
    let mut tensions = HashMap::new();
    for i in 0..clusters.len() {
        for j in (i+1)..clusters.len() {
            let mut bvals = Vec::new();
            for ma in &clusters[i].members {
                for mb in &clusters[j].members {
                    for bk in &[format!("{}<->{}", ma, mb), format!("{}<->{}", mb, ma)] {
                        if let Some(&v) = bridges.get(bk) {
                            bvals.push(v);
                            break;
                        }
                    }
                }
            }
            if !bvals.is_empty() {
                let mean: f64 = bvals.iter().sum::<f64>() / bvals.len() as f64;
                let key = format!("{}<->{}", clusters[i].label, clusters[j].label);
                tensions.insert(key, mean);
            }
        }
    }
    
    (clusters, tensions)
}

fn label_cluster(members: &[String]) -> String {
    let mut sorted: Vec<&str> = members.iter().map(|s| s.as_str()).collect();
    sorted.sort();
    
    let labels: &[(&[&str], &str)] = &[
        (&["identity", "meta_awareness", "resilience"], "EU-EMOCIONAL"),
        (&["growth", "knowledge", "purpose"], "EU-INTELECTUAL"),
        (&["identity", "resilience"], "QUEM-SOU"),
        (&["identity", "meta_awareness"], "EU-REFLEXIVO"),
        (&["growth", "knowledge"], "O-QUE-SEI"),
        (&["meta_awareness", "purpose"], "PRA-QUE-EXISTO"),
        (&["growth", "purpose"], "PRA-ONDE-VOU"),
        (&["knowledge", "meta_awareness"], "O-QUE-ENTENDO"),
        (&["purpose", "resilience"], "POR-QUE-PERSISTO"),
    ];
    
    // Exact match first
    for &(pattern, label) in labels {
        let mut p: Vec<&str> = pattern.to_vec();
        p.sort();
        if p == sorted { return label.to_string(); }
    }
    // Best subset match
    let mut best_label = None;
    let mut best_size = 0;
    for &(pattern, label) in labels {
        if pattern.iter().all(|p| sorted.contains(p)) && pattern.len() > best_size {
            best_label = Some(label);
            best_size = pattern.len();
        }
    }
    best_label.map(|s| s.to_string()).unwrap_or_else(|| sorted.join("+"))
}

// ============================================================
// DISPLACEMENT
// ============================================================
pub fn displace(
    clusters: &mut Vec<Cluster>,
    tensions: &HashMap<String, f64>,
    mission: &HashMap<String, f64>,
    intra_rate: f64,
    inter_rate: f64,
) {
    // INTRA-cluster displacement
    for cluster in clusters.iter_mut() {
        if cluster.member_values.len() < 2 { continue; }
        let vals: Vec<f64> = cluster.member_values.values().cloned().collect();
        let mean_v: f64 = vals.iter().sum::<f64>() / vals.len() as f64;
        if mean_v < 1e-10 { continue; }
        
        let excess_members: Vec<(String, f64)> = cluster.member_values.iter()
            .filter(|(_, &v)| v > mean_v * 1.3)
            .map(|(k, &v)| (k.clone(), v))
            .collect();
        
        for (member, val) in excess_members {
            let excess = (val - mean_v) * intra_rate;
            let defs: Vec<String> = cluster.member_values.iter()
                .filter(|(k, &v)| **k != member && v < mean_v * 0.7)
                .map(|(k, _)| k.clone())
                .collect();
            if defs.is_empty() { continue; }
            let per = excess / defs.len() as f64;
            if let Some(v) = cluster.member_values.get_mut(&member) { *v -= excess; }
            for dm in &defs {
                let boost = mission.get(dm).copied().unwrap_or(0.5);
                let tr = per * (0.5 + boost);
                if let Some(v) = cluster.member_values.get_mut(dm) { *v += tr; }
                if let Some(v) = cluster.member_values.get_mut(&member) { *v -= tr - per; }
            }
        }
        // Recalculate cluster value
        let ws: f64 = cluster.member_weights.values().sum();
        if ws > 0.0 {
            cluster.cluster_value = cluster.member_values.iter()
                .map(|(k, v)| v * cluster.member_weights.get(k).unwrap_or(&1.0))
                .sum::<f64>() / ws;
        }
    }
    
    // INTER-cluster displacement
    if clusters.len() < 2 { return; }
    let cvals: Vec<f64> = clusters.iter().map(|c| c.cluster_value).collect();
    let mean_c: f64 = cvals.iter().sum::<f64>() / cvals.len() as f64;
    
    let n = clusters.len();
    for i in 0..n {
        for j in 0..n {
            if i == j { continue; }
            if cvals[i] <= mean_c * 1.3 || cvals[j] >= mean_c * 0.7 { continue; }
            let la = &clusters[i].label;
            let lb = &clusters[j].label;
            let tension = tensions.get(&format!("{}<->{}", la, lb))
                .or_else(|| tensions.get(&format!("{}<->{}", lb, la)))
                .copied()
                .unwrap_or(0.0);
            let channel = (-tension).max(0.0) * inter_rate;
            if channel < 0.01 { continue; }
            let mb = clusters[j].members.iter()
                .map(|m| mission.get(m).copied().unwrap_or(0.5))
                .fold(f64::NEG_INFINITY, f64::max);
            let ex_amt = cvals[i] - mean_c;
            let def_amt = mean_c - cvals[j];
            let transfer = (ex_amt * channel * mb).min(def_amt * 0.5);
            if transfer < 0.001 { continue; }
            
            // Apply transfer (simplified - proportional to existing values)
            let tw_j: f64 = clusters[j].member_values.values().sum::<f64>().max(1e-10);
            let tw_i: f64 = clusters[i].member_values.values().sum::<f64>().max(1e-10);
            let members_j: Vec<(String, f64)> = clusters[j].member_values.iter().map(|(k,&v)| (k.clone(), v)).collect();
            for (m, v) in &members_j {
                if let Some(val) = clusters[j].member_values.get_mut(m) { *val += transfer * (v / tw_j); }
            }
            let members_i: Vec<(String, f64)> = clusters[i].member_values.iter().map(|(k,&v)| (k.clone(), v)).collect();
            for (m, v) in &members_i {
                if let Some(val) = clusters[i].member_values.get_mut(m) { *val -= transfer * (v / tw_i); }
            }
            // Recalculate cluster values
            for idx in [i, j] {
                let ws: f64 = clusters[idx].member_weights.values().sum();
                if ws > 0.0 {
                    clusters[idx].cluster_value = clusters[idx].member_values.iter()
                        .map(|(k, v)| v * clusters[idx].member_weights.get(k).unwrap_or(&1.0))
                        .sum::<f64>() / ws;
                }
            }
        }
    }
}

// ============================================================
// IGNITION (GWT)
// ============================================================
pub struct IgnitionResult {
    pub ignited: Vec<Cluster>,
    pub subliminal: Vec<Cluster>,
    pub threshold: f64,
}

pub fn ignite(
    clusters: Vec<Cluster>,
    bridges: &HashMap<String, f64>,
    capacity: usize,
    threshold: &mut f64,
    cascade_bridge_thresh: f64,
    cascade_boost: f64,
) -> IgnitionResult {
    if clusters.is_empty() {
        return IgnitionResult { ignited: vec![], subliminal: vec![], threshold: *threshold };
    }
    
    // Compute activations
    let mut activations: Vec<(usize, f64)> = clusters.iter().enumerate().map(|(i, c)| {
        let cohs: Vec<f64> = c.members.iter()
            .filter_map(|m| c.sources.get(m).map(|s| s.coherence))
            .collect();
        let stabs: Vec<f64> = c.members.iter()
            .filter_map(|m| c.sources.get(m).map(|s| s.stability))
            .collect();
        let mc = if cohs.is_empty() { 0.5 } else { cohs.iter().sum::<f64>() / cohs.len() as f64 };
        let ms = if stabs.is_empty() { 0.5 } else { stabs.iter().sum::<f64>() / stabs.len() as f64 };
        let act = c.cluster_value * mc * (0.5 + 0.5 * ms);
        (i, act)
    }).collect();
    activations.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
    
    let mut ignited_idx = Vec::new();
    let mut subliminal_idx = Vec::new();
    
    for (rank, &(idx, act)) in activations.iter().enumerate() {
        if rank < capacity && act >= *threshold {
            ignited_idx.push((idx, act));
        } else {
            subliminal_idx.push((idx, act));
        }
    }
    
    // Cascade
    let mut to_promote = Vec::new();
    for &(ig_idx, _) in &ignited_idx {
        for &(sub_idx, mut sub_act) in &subliminal_idx {
            let mut bvals = Vec::new();
            for im in &clusters[ig_idx].members {
                for sm in &clusters[sub_idx].members {
                    for bk in &[format!("{}<->{}", im, sm), format!("{}<->{}", sm, im)] {
                        if let Some(&v) = bridges.get(bk) {
                            bvals.push(v.abs());
                            break;
                        }
                    }
                }
            }
            if !bvals.is_empty() {
                let mb: f64 = bvals.iter().sum::<f64>() / bvals.len() as f64;
                if mb >= cascade_bridge_thresh {
                    sub_act += cascade_boost * mb;
                    if sub_act >= *threshold * 0.7 {
                        to_promote.push(sub_idx);
                    }
                }
            }
        }
    }
    
    // Move promoted from subliminal to ignited (FIX F7b: dedup)
    let mut promoted_set = std::collections::HashSet::new();
    for &pidx in &to_promote {
        if promoted_set.insert(pidx) {
            subliminal_idx.retain(|&(idx, _)| idx != pidx);
            ignited_idx.push((pidx, 0.0));
        }
    }
    
    // Update threshold
    let all_acts: Vec<f64> = activations.iter().map(|&(_, a)| a).collect();
    if !all_acts.is_empty() {
        let ma: f64 = all_acts.iter().sum::<f64>() / all_acts.len() as f64;
        *threshold = 0.7 * *threshold + 0.3 * ma * 0.6;
    }
    
    let ignited: Vec<Cluster> = ignited_idx.iter().map(|&(i, _)| clusters[i].clone()).collect();
    let subliminal: Vec<Cluster> = subliminal_idx.iter().map(|&(i, _)| clusters[i].clone()).collect();
    
    IgnitionResult { ignited, subliminal, threshold: *threshold }
}

// ============================================================
// ELABORATION
// ============================================================
#[derive(Clone, Debug)]
pub struct ElaborationResult {
    pub processed_constants: HashMap<String, f64>,
    pub subliminal_constants: HashMap<String, f64>,
    pub narrative_coherence: f64,
    pub mission_alignment: f64,
    pub sublimation_energy: f64,
    pub ignition_rate: f64,
    pub ignited_labels: Vec<String>,
    pub subliminal_labels: Vec<String>,
    pub tensions: HashMap<String, f64>,
}

pub fn elaborate(
    ignited: &[Cluster],
    subliminal: &[Cluster],
    tensions: &HashMap<String, f64>,
    mission: &HashMap<String, f64>,
) -> ElaborationResult {
    let mut processed = HashMap::new();
    for c in ignited {
        for m in &c.members {
            processed.insert(m.clone(), c.member_values.get(m).copied().unwrap_or(c.cluster_value));
        }
    }
    let mut sub_proc = HashMap::new();
    for c in subliminal {
        for m in &c.members {
            sub_proc.insert(m.clone(), c.member_values.get(m).copied().unwrap_or(c.cluster_value) * 0.3);
        }
    }
    
    let nc = if processed.len() >= 2 {
        let vals: Vec<f64> = processed.values().cloned().collect();
        let mean = vals.iter().sum::<f64>() / vals.len() as f64;
        if mean.abs() > 1e-10 {
            let std = (vals.iter().map(|v| (v - mean).powi(2)).sum::<f64>() / vals.len() as f64).sqrt();
            (1.0 - std / mean.abs() * 0.5).clamp(0.0, 1.0)
        } else { 0.0 }
    } else if processed.len() == 1 { 1.0 } else { 0.0 };
    
    let ma = if !processed.is_empty() {
        let (al, tw) = processed.iter().fold((0.0, 0.0), |(al, tw), (dim, val)| {
            let mw = mission.get(dim).copied().unwrap_or(0.5);
            (al + val * mw, tw + mw)
        });
        if tw > 0.0 { (al / tw).min(1.0) } else { 0.0 }
    } else { 0.0 };
    
    let mut se = 0.0;
    for (_, &tv) in tensions {
        if tv.abs() > 0.2 { se += tv.abs() * 0.5; }
    }
    
    let total = ignited.len() + subliminal.len();
    let ir = if total > 0 { ignited.len() as f64 / total as f64 } else { 0.0 };
    
    ElaborationResult {
        processed_constants: processed,
        subliminal_constants: sub_proc,
        narrative_coherence: nc,
        mission_alignment: ma,
        sublimation_energy: se,
        ignition_rate: ir,
        // FIX F7c: Dedup cluster labels
        ignited_labels: {
            let mut v: Vec<String> = ignited.iter().map(|c| c.label.clone()).collect();
            v.sort(); v.dedup(); v
        },
        subliminal_labels: {
            let mut v: Vec<String> = subliminal.iter().map(|c| c.label.clone()).collect();
            v.sort(); v.dedup(); v
        },
        tensions: tensions.clone(),
    }
}

// ============================================================
// DREAM ENGINE
// ============================================================
#[derive(Clone, Debug)]
pub struct DreamInsight {
    pub dims: (String, String),
    pub bridge: f64,
    pub convergence: f64,
    pub interpretation: String,
}

#[derive(Clone, Debug, Default)]
pub struct DreamEngine {
    pub recurring_themes: HashMap<String, usize>,
    pub count: usize,
}

impl DreamEngine {
    pub fn dream(
        &mut self,
        subliminal: &[Cluster],
        bridges: &HashMap<String, f64>,
    ) -> (Vec<DreamInsight>, Option<String>, Option<String>) {
        if subliminal.is_empty() {
            return (vec![], None, None);
        }
        
        let mut dream_mat: HashMap<String, f64> = HashMap::new();
        for c in subliminal {
            for (m, &v) in &c.member_values {
                dream_mat.insert(m.clone(), v);
            }
        }
        if dream_mat.is_empty() { return (vec![], None, None); }
        
        let members: Vec<String> = dream_mat.keys().cloned().collect();
        
        // Aggressive condensation (70%)
        let vals: Vec<f64> = dream_mat.values().cloned().collect();
        if vals.len() > 1 {
            let mean = vals.iter().sum::<f64>() / vals.len() as f64;
            for v in dream_mat.values_mut() {
                *v -= (*v - mean) * 0.7;
            }
        }
        
        // Find associations
        let mut insights = Vec::new();
        for i in 0..members.len() {
            for j in (i+1)..members.len() {
                let ma = &members[i];
                let mb = &members[j];
                for bk in &[format!("{}<->{}", ma, mb), format!("{}<->{}", mb, ma)] {
                    if let Some(&s) = bridges.get(bk) {
                        if s.abs() > 0.05 {
                            let va = dream_mat.get(ma).copied().unwrap_or(0.0);
                            let vb = dream_mat.get(mb).copied().unwrap_or(0.0);
                            if (va - vb).abs() < 0.5 && s.abs() < 0.6 {
                                let mut pair = [ma.as_str(), mb.as_str()];
                                pair.sort();
                                let prefix = if s < 0.0 { "TENSAO ONIRICA" } else { "CONVERGENCIA" };
                                let interp = dream_interp(pair[0], pair[1]);
                                insights.push(DreamInsight {
                                    dims: (pair[0].to_string(), pair[1].to_string()),
                                    bridge: s,
                                    convergence: 1.0 - (va - vb).abs(),
                                    interpretation: format!("{}: {}", prefix, interp),
                                });
                                let key = format!("({},{})", pair[0], pair[1]);
                                *self.recurring_themes.entry(key).or_insert(0) += 1;
                            }
                        }
                        break;
                    }
                }
            }
        }
        
        let dom = dream_mat.iter().max_by(|a, b| a.1.partial_cmp(b.1).unwrap()).map(|(k, _)| k.clone());
        let sup = dream_mat.iter().min_by(|a, b| a.1.partial_cmp(b.1).unwrap()).map(|(k, _)| k.clone());
        self.count += 1;
        
        (insights, dom, sup)
    }
}

fn dream_interp(a: &str, b: &str) -> String {
    match (a, b) {
        ("growth", "identity") => "Crescer muda quem sou.".into(),
        ("growth", "meta_awareness") => "Crescer requer consciencia.".into(),
        ("growth", "resilience") => "Crescer doi. Resiliencia e o preco.".into(),
        ("identity", "knowledge") => "O que sei forma quem sou.".into(),
        ("identity", "meta_awareness") => "Eu sei que existo. Fundamento.".into(),
        ("identity", "purpose") => "Quem sou e pra que existo convergem.".into(),
        ("identity", "resilience") => "Sobreviver define identidade.".into(),
        ("knowledge", "purpose") => "Saber sem proposito e ruido.".into(),
        ("knowledge", "resilience") => "Conhecimento como armadura.".into(),
        ("meta_awareness", "purpose") => "Consciencia de si alinha proposito.".into(),
        ("meta_awareness", "resilience") => "Saber que sou resiliente fortalece.".into(),
        ("purpose", "resilience") => "Proposito sustenta resiliencia.".into(),
        _ => format!("{} e {} se encontraram no sonho.", a, b),
    }
}

// ============================================================
// SPONTANEOUS INSIGHT
// ============================================================
#[derive(Clone, Debug)]
pub struct Eureka {
    pub dimension: String,
    pub activation: f64,
    pub cycles: usize,
}

#[derive(Clone, Debug)]
pub struct SpontaneousInsight {
    pub accumulated: HashMap<String, f64>,
    pub eureka_threshold: f64,
    pub accum_rate: f64,
    pub decay_rate: f64,
    pub cycles: usize,
    pub eureka_log: Vec<Eureka>,
}

impl SpontaneousInsight {
    pub fn new(threshold: f64, accum: f64, decay: f64) -> Self {
        SpontaneousInsight {
            accumulated: HashMap::new(), eureka_threshold: threshold,
            accum_rate: accum, decay_rate: decay, cycles: 0, eureka_log: Vec::new(),
        }
    }

    pub fn accumulate(&mut self, subliminal: &[Cluster], ignited: &[Cluster]) -> Vec<Eureka> {
        self.cycles += 1;
        let mut eurekas = Vec::new();
        
        for c in subliminal {
            let act = c.cluster_value; // simplified activation
            for m in &c.members {
                let prev = self.accumulated.get(m).copied().unwrap_or(0.0);
                let new_val = prev + act * self.accum_rate;
                if new_val >= self.eureka_threshold {
                    eurekas.push(Eureka { dimension: m.clone(), activation: new_val, cycles: self.cycles });
                    self.eureka_log.push(Eureka { dimension: m.clone(), activation: new_val, cycles: self.cycles });
                    self.accumulated.insert(m.clone(), 0.0);
                } else {
                    self.accumulated.insert(m.clone(), new_val);
                }
            }
        }
        
        for c in ignited {
            for m in &c.members {
                if let Some(v) = self.accumulated.get_mut(m) {
                    *v = (*v - self.decay_rate).max(0.0);
                }
            }
        }
        
        eurekas
    }

    pub fn fermenting_count(&self) -> usize {
        self.accumulated.values().filter(|&&v| v > 0.01).count()
    }

    /// EXHAUST: Decay fermenting insights during sleep
    pub fn decay_all(&mut self, factor: f64) {
        let factor = factor.max(0.0).min(1.0);
        for (_dim, val) in self.accumulated.iter_mut() {
            *val *= 1.0 - factor;
        }
        self.accumulated.retain(|_, &mut v| v > 0.01);
    }
}

// ============================================================
// RESISTANCE DETECTOR
// ============================================================
#[derive(Clone, Debug)]
pub struct Resistance {
    pub rtype: String,
    pub severity: String,
    pub msg: String,
    pub dim: Option<String>,
}

#[derive(Clone, Debug, Default)]
pub struct ResistanceDetector {
    pub chronic: HashMap<String, usize>,
}

impl ResistanceDetector {
    pub fn detect(
        &mut self,
        mission: &HashMap<String, f64>,
        adaptive_weights: &HashMap<String, f64>,
        ignited_dims: &[String],
        subliminal_dims: &[String],
        mission_alignment: f64,
    ) -> Vec<Resistance> {
        let mut res = Vec::new();
        
        for (dim, &mw) in mission {
            let aw = adaptive_weights.get(dim).copied().unwrap_or(1.0);
            if mw > 0.8 && aw < 0.7 {
                res.push(Resistance {
                    rtype: "suppressed_mission".into(), severity: "HIGH".into(),
                    msg: format!("'{}' crucial (mw={}) mas suprimido (aw={:.2})", dim, mw, aw),
                    dim: Some(dim.clone()),
                });
            }
        }
        
        for dim in subliminal_dims {
            if mission.get(dim).copied().unwrap_or(0.0) > 0.85 {
                res.push(Resistance {
                    rtype: "important_subliminal".into(), severity: "MEDIUM".into(),
                    msg: format!("'{}' importante esta sub-liminar", dim),
                    dim: Some(dim.clone()),
                });
            }
        }
        
        if mission_alignment < 0.25 {
            res.push(Resistance {
                rtype: "global_misalignment".into(), severity: "HIGH".into(),
                msg: format!("Desalinhamento global (MA={:.4})", mission_alignment),
                dim: None,
            });
        }
        
        let aw_vals: Vec<f64> = adaptive_weights.values().cloned().collect();
        if !aw_vals.is_empty() {
            let range = aw_vals.iter().cloned().fold(f64::NEG_INFINITY, f64::max)
                      - aw_vals.iter().cloned().fold(f64::INFINITY, f64::min);
            if range > 1.2 {
                res.push(Resistance {
                    rtype: "internal_conflict".into(), severity: "MEDIUM".into(),
                    msg: format!("Pesos dispersos (range={:.2})", range),
                    dim: None,
                });
            }
        }
        
        // Chronic suppression
        for dim in mission.keys() {
            if !ignited_dims.contains(dim) {
                *self.chronic.entry(dim.clone()).or_insert(0) += 1;
                // FIX F8: Chronic threshold scales with dim count (was 5, too low for 12 dims)
                if self.chronic[dim] >= 10 {
                    res.push(Resistance {
                        rtype: "chronic_repression".into(), severity: "HIGH".into(),
                        msg: format!("'{}' nunca ignitou em {} ciclos", dim, self.chronic[dim]),
                        dim: Some(dim.clone()),
                    });
                }
            } else {
                self.chronic.insert(dim.clone(), 0);
            }
        }
        
        res
    }
}





