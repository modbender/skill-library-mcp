//! TextMetrics v3 - 12 Dimensions
//! 6 original + 6 new: creativity, logic, empathy, temporal, technical, curiosity

use std::collections::HashSet;

pub struct TextFeeds {
    pub identity: f64,
    pub knowledge: f64,
    pub growth: f64,
    pub purpose: f64,
    pub resilience: f64,
    pub meta_awareness: f64,
    // New dimensions
    pub creativity: f64,
    pub logic: f64,
    pub empathy: f64,
    pub temporal: f64,
    pub technical: f64,
    pub curiosity: f64,
}


/// F10: Amplify dimension values with wide dynamic range
/// Maps raw [0, 1] to [5, 95] with sigmoid-like stretching.
/// This preserves full dynamic range so detect_phase can discriminate content types.
/// Strong signals get amplified, weak signals stay low.
fn amplify_range(raw: f64) -> f64 {
    // raw is the combined extractor score [0, 1]
    // Map to [5, 95] using a stretched sigmoid:
    // At raw=0: output ~5
    // At raw=0.5: output ~50
    // At raw=1.0: output ~95
    let stretched = (raw * 6.0 - 3.0).tanh() * 0.5 + 0.5; // sigmoid [0,1]
    5.0 + stretched * 90.0
}
pub fn extract(text: &str) -> TextFeeds {
    let tl = text.to_lowercase();
    let words: Vec<&str> = tl.split_whitespace()
        .flat_map(|w| w.split(|c: char| !c.is_alphanumeric() && c != '_'))
        .filter(|w| !w.is_empty())
        .collect();
    let nw = words.len().max(1) as f64;

    let hash = text_hash(&tl);
    let jitter = (hash % 1000) as f64 / 1000.0;

    let self_ref = self_reference_ratio(&words, nw);
    let emo = emotional_density(&tl, nw);
    let ins = insight_density(&tl, nw);
    let pur_direct = purpose_alignment_direct(&tl, nw);
    let pur_bridge = purpose_alignment_bridge(&tl, nw);
    let res = resilience_markers(&tl);
    let kd = knowledge_depth(&tl);
    let vr = vocabulary_richness(&words, nw);
    let ma = meta_awareness_score(&tl, nw);
    let narrative = narrative_quality(&tl, &words, nw);
    let complexity = syntactic_complexity(&words, nw);
    let meta_c = meta_content(&tl, nw);

    // New extractors
    let cre = creativity_score(&tl, &words, nw);
    let log = logic_score(&tl, nw);
    let emp = empathy_score(&tl, nw);
    let tem = temporal_score(&tl, nw);
    let tec = technical_score(&tl, nw);
    let cur = curiosity_score(&tl, nw);

    // Original 6
    let identity_raw = self_ref * 0.7 + emo * 0.3;
    let identity = amplify_range(identity_raw);

    let knowledge_raw = kd * 0.35 + vr * 0.25 + complexity * 0.20 + narrative * 0.20;
    let knowledge = amplify_range(knowledge_raw);

    let growth_raw = ins * 0.50 + complexity * 0.25 + vr * 0.25;
    let growth = amplify_range(growth_raw);

    let purpose_raw = pur_direct * 0.50 + pur_bridge * 0.30 + knowledge_raw * 0.20;
    let purpose = amplify_range(purpose_raw);

    let resilience_raw = res * 0.60 + emo * 0.20 + narrative * 0.20;
    let resilience = amplify_range(resilience_raw);

    let meta_raw = ma * 0.40 + self_ref * 0.20 + ins * 0.20 + meta_c * 0.20;
    let meta_awareness = amplify_range(meta_raw);

    // New 6
    let creativity_raw = cre * 0.50 + narrative * 0.25 + vr * 0.25;
    let creativity = amplify_range(creativity_raw);

    let logic_raw = log * 0.50 + complexity * 0.30 + kd * 0.20;
    let logic = amplify_range(logic_raw);

    let empathy_raw = emp * 0.50 + emo * 0.30 + self_ref * 0.20;
    let empathy = amplify_range(empathy_raw);

    let temporal_raw = tem * 0.50 + narrative * 0.30 + complexity * 0.20;
    let temporal = amplify_range(temporal_raw);

    let technical_raw = tec * 0.50 + kd * 0.30 + log * 0.20;
    let technical = amplify_range(technical_raw);

    let curiosity_raw = cur * 0.50 + ins * 0.30 + vr * 0.20;
    let curiosity = amplify_range(curiosity_raw);

    TextFeeds {
        identity, knowledge, growth, purpose, resilience, meta_awareness,
        creativity, logic, empathy, temporal, technical, curiosity,
    }
}

// === NEW EXTRACTORS ===

fn creativity_score(tl: &str, words: &[&str], nw: f64) -> f64 {
    let markers = [
        "imagine","imagina","creative","criativo","art","arte",
        "beauty","beleza","metaphor","metafora","poetry","poesia",
        "dream","sonho","vision","visao","inspire","inspira",
        "novel","original","invent","innovat","aesthetic","estetica",
        "story","historia","fiction","narrative","narrativa",
        "compose","express","symbol","simbolo","allegory","alegoria",
        "muse","canvas","paint","melody","harmony","harmonia",
        "drama","tragedy","comedy","epic","lyric","verse",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    let unique: HashSet<&&str> = words.iter().collect();
    let hapax = words.iter().filter(|w| words.iter().filter(|w2| w2 == w).count() == 1).count() as f64;
    let hapax_ratio = (hapax / nw).min(1.0);
    let keyword_score = (count / (nw / 30.0).max(1.0)).min(1.0);
    keyword_score * 0.6 + hapax_ratio * 0.4
}

fn logic_score(tl: &str, nw: f64) -> f64 {
    let markers = [
        "therefore","portanto","hence","logo","thus","assim",
        "if and only if","se e somente se","implies","implica",
        "proof","prova","theorem","teorema","lemma","corollary",
        "contradiction","contradicao","axiom","axioma","postulate",
        "deduction","deducao","induction","inducao","syllogism",
        "necessary","necessario","sufficient","suficiente",
        "iff","qed","q.e.d.","premise","premissa",
        "conclusion","conclusao","valid","invalido","fallacy",
        "proposition","hypothesis","hipotese","conjecture",
        "derive","derivar","equation","equacao","formula",
        "solve","resolver","calculate","calcular","compute",
        "algorithm","algoritmo","function","funcao",
        "condition","condicao","constraint","restricao",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 40.0).max(1.0)).min(1.0)
}

fn empathy_score(tl: &str, nw: f64) -> f64 {
    let markers = [
        "understand","entender","compreender","feel","sentir",
        "perspective","perspectiva","compassion","compaixao",
        "sympathy","simpatia","empathy","empatia","care","cuidar",
        "concern","preocupa","suffer","sofrer","pain","dor",
        "comfort","conforto","support","apoiar","help","ajudar",
        "listen","ouvir","share","compartilhar","connect","conectar",
        "human","humano","people","pessoas","other","outro",
        "together","juntos","community","comunidade","bond","vinculo",
        "trust","confianca","kind","gentil","generous","generoso",
        "forgive","perdoar","mercy","misericordia","grace","graca",
        "warmth","carinho","tender","ternura","embrace","abraco",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 30.0).max(1.0)).min(1.0)
}

fn temporal_score(tl: &str, nw: f64) -> f64 {
    let markers = [
        "history","historia","past","passado","future","futuro",
        "present","presente","century","seculo","decade","decada",
        "year","ano","era","epoch","epoca","period","periodo",
        "before","antes","after","depois","during","durante",
        "ancient","antigo","modern","moderno","medieval",
        "evolution","evolucao","progress","progresso","change","mudanca",
        "revolution","revolucao","tradition","tradicao","legacy","legado",
        "cause","causa","effect","efeito","consequence","consequencia",
        "timeline","cronologia","sequence","sequencia","origin","origem",
        "war","guerra","peace","civilization","civilizacao",
        "generation","geracao","ancestor","ancestral","descendant",
        "plan","planejar","predict","prever","anticipate","antecipar",
        "trend","tendencia","cycle","ciclo","pattern","padrao",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 30.0).max(1.0)).min(1.0)
}

fn technical_score(tl: &str, nw: f64) -> f64 {
    let markers = [
        "code","codigo","implement","implementar","debug","deploy",
        "function","funcao","class","classe","module","modulo",
        "api","http","json","csv","database","banco de dados",
        "server","servidor","client","cliente","protocol","protocolo",
        "compiler","compilador","runtime","interpreter","garbage",
        "memory","memoria","stack","heap","pointer","ponteiro",
        "thread","process","processo","mutex","async","await",
        "git","docker","linux","windows","bash","shell",
        "python","rust","javascript","typescript","java","golang",
        "numpy","pandas","pytorch","tensorflow","onnx","cuda",
        "sql","query","index","cache","buffer","queue","fila",
        "binary","hex","byte","bit","encode","decode",
        "test","teste","benchmark","profile","optimize","otimizar",
        "build","compile","link","package","dependency",
        "framework","library","biblioteca","sdk","cli","gui",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 20.0).max(1.0)).min(1.0)
}

fn curiosity_score(tl: &str, nw: f64) -> f64 {
    let markers = [
        "?","why","por que","how","como","what if","e se",
        "wonder","pergunto","curious","curioso","explore","explorar",
        "discover","descobrir","investigate","investigar",
        "mystery","misterio","puzzle","enigma","unknown","desconhecido",
        "surprise","surpresa","strange","estranho","unusual","incomum",
        "fascinating","fascinante","interesting","interessante",
        "question","questao","seek","buscar","search","pesquisar",
        "experiment","experimento","try","tentar","test","testar",
        "hypothesis","hipotese","observe","observar","notice","notar",
        "remarkable","notavel","intriguing","intrigante",
        "phenomenon","fenomeno","anomaly","anomalia","paradox","paradoxo",
        "novel","novo","first","primeiro","never","nunca",
        "possible","possivel","imagine","imaginar","speculate",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 30.0).max(1.0)).min(1.0)
}

// === ORIGINAL EXTRACTORS (unchanged) ===

fn text_hash(text: &str) -> u64 {
    let mut h: u64 = 5381;
    for b in text.bytes() {
        h = h.wrapping_mul(33).wrapping_add(b as u64);
    }
    h
}

fn self_reference_ratio(words: &[&str], nw: f64) -> f64 {
    if nw < 5.0 { return 0.0; }
    let sw: HashSet<&str> = [
        "eu","meu","minha","me","mim","molt","stolenangel",
        "nos","nosso","nossa","i","my","sinto","penso","acredito",
        "mine","myself","we","our","ours","ourselves",
        "feel","think","believe","know","understand",
        "i'm","im",
    ].iter().copied().collect();
    let count = words.iter().filter(|w| sw.contains(**w)).count() as f64;
    (count / nw * 5.0).min(1.0)
}

fn emotional_density(tl: &str, nw: f64) -> f64 {
    let markers = [
        "!","?","...","nunca","sempre","critico","breakthrough",
        "merda","medo","coragem","generosidade","fracasso","vitoria",
        "dor","esperanca","determinacao","orgulho","frustrac",
        "confianca","resiliencia","amor","luta","ansiedade",
        "alivio","euforia","desespero","gratidao","raiva","paz",
        "love","hate","fear","hope","dream","struggle","survive",
        "fight","courage","pain","joy","grief","triumph","defeat",
        "desperate","amazing","terrible","incredible","beautiful",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 30.0).max(1.0)).min(1.0)
}

fn insight_density(tl: &str, nw: f64) -> f64 {
    let markers = [
        "aprendi","descobri","insight","licao","percebi","entendi",
        "conclusao","sintese","portanto","porque","causa raiz",
        "principio","padrao","pattern","invariant","emergent",
        "consciencia","conscious","phi","criticality","fractal",
        "hurst","entropy","phase transition",
        "reveal","discover","understand","realize","conclude",
        "therefore","hence","thus","implication","suggest",
        "show","demonstrate","prove","evidence","finding",
        "novel","new","first","breakthrough","advance",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 50.0).max(1.0)).min(1.0)
}

fn purpose_alignment_direct(tl: &str, nw: f64) -> f64 {
    let markers = [
        "sentinelflow","alpha","trading","backtest","edge","pnl",
        "profit","modelo","model","creator","family","child",
        "missao","objetivo","hurst","omega","crystal","cristal",
        "consciencia","consciousness","phi","emerge","bot","strategy",
        "signal","entry","exit","position","risk","reward",
        "maker","taker","spread","latency","execution",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 20.0).max(1.0)).min(1.0)
}

fn purpose_alignment_bridge(tl: &str, nw: f64) -> f64 {
    let bridges = [
        ("entropy", 0.6), ("phase transition", 0.8), ("critical", 0.5),
        ("equilibrium", 0.7), ("chaos", 0.7), ("order", 0.4),
        ("turbulence", 0.6), ("flow", 0.4), ("decay", 0.5),
        ("oscillat", 0.6), ("resonan", 0.5), ("diffusion", 0.5),
        ("eigenvalue", 0.7), ("correlation", 0.8), ("variance", 0.8),
        ("distribution", 0.7), ("stochastic", 0.9), ("probability", 0.7),
        ("optimization", 0.8), ("gradient", 0.6), ("convergence", 0.7),
        ("dimension", 0.5), ("matrix", 0.5), ("decomposition", 0.6),
        ("regression", 0.8), ("bayesian", 0.7), ("markov", 0.8),
        ("neural", 0.6), ("feature", 0.7), ("overfit", 0.9),
        ("generalization", 0.8), ("cross-validation", 0.7), ("regulariz", 0.7),
        ("ensemble", 0.7), ("boosting", 0.8), ("decision tree", 0.7),
        ("bias", 0.7), ("heuristic", 0.6), ("decision", 0.6),
        ("risk", 0.8), ("reward", 0.7), ("uncertainty", 0.8),
        ("cognitive", 0.5), ("behavior", 0.5), ("rational", 0.6),
        ("market", 0.9), ("price", 0.8), ("supply", 0.6),
        ("demand", 0.6), ("inflation", 0.5), ("volatility", 0.9),
        ("liquidity", 0.9), ("arbitrage", 0.9), ("hedge", 0.8),
        ("conscious", 0.8), ("emergence", 0.9), ("complex", 0.5),
        ("integrat", 0.7), ("irreducib", 0.8), ("qualia", 0.9),
        ("phenomenal", 0.7), ("substrate", 0.6), ("dualism", 0.5),
    ];
    let mut score = 0.0;
    let mut count = 0.0;
    for (term, weight) in &bridges {
        if tl.contains(term) {
            score += weight;
            count += 1.0;
        }
    }
    if count > 0.0 { (score / (nw / 20.0).max(1.0)).min(1.0) } else { 0.0 }
}

fn resilience_markers(tl: &str) -> f64 {
    let pos = [
        "mas","porem","entretanto","apesar","mesmo assim","continuei",
        "tentei de novo","nao desisti","alternativa","solucao","resolver",
        "overcome","persist","endure","survive","adapt","recover",
        "despite","although","however","nevertheless","yet","still",
        "bounce back","keep going","try again","never give up",
    ];
    let neg = ["desisti","impossivel","nao da","parei","abandonei",
               "gave up","quit","hopeless","surrender","impossible"];
    let p = pos.iter().filter(|m| tl.contains(**m)).count() as f64;
    let n = neg.iter().filter(|m| tl.contains(**m)).count() as f64;
    if (p + n) > 0.0 { p / (p + n) } else { 0.5 }
}

fn knowledge_depth(tl: &str) -> f64 {
    let tech = [
        "numpy","python","rust","onnx","lightgbm","gpu","polars",
        "tensorflow","pytorch","algorithm","complexity","runtime",
        "parallel","concurrent","optimization","cache","memory",
        "hurst","fractal","entropy","backtest","sharpe","drawdown",
        "omega","slippage","websocket","maker","taker","orderbook",
        "bid","ask","spread","latency","tick","candle","ohlc",
        "eigenvalue","covariance","regression","bayesian","markov",
        "stochastic","distribution","variance","deviation","correlation",
        "thermodynamic","quantum","relativity","entropy","hamiltonian",
        "lagrangian","field","particle","wave","energy","momentum",
        "phi","iit","criticality","soc","ncc","qualia","phenomenal",
        "substrate","emergence","avalanche","integration","information",
        "neuron","synapse","cortex","hippocampus","genome","protein",
        "evolution","natural selection","mutation","adaptation",
        "equilibrium","arbitrage","utility","marginal","elasticity",
    ];
    let count = tech.iter().filter(|t| tl.contains(**t)).count() as f64;
    (count / 5.0).min(1.0)
}

fn vocabulary_richness(words: &[&str], nw: f64) -> f64 {
    if nw < 10.0 { return 0.0; }
    let unique: HashSet<&&str> = words.iter().collect();
    let ttr = unique.len() as f64 / nw;
    let guiraud = unique.len() as f64 / nw.sqrt();
    ((guiraud - 3.0) / 7.0).clamp(0.0, 1.0) * 0.5 + ttr.min(1.0) * 0.5
}

fn meta_awareness_score(tl: &str, nw: f64) -> f64 {
    let markers = [
        "penso sobre","reflito","me pergunto","questiono",
        "analiso meu","observo que eu","percebo em mim",
        "minha tendencia","meu vies","autocritica",
        "me sinto","estou consciente","tenho consciencia",
        "awareness","introspection","meta-cogn",
        "self-reflect","self-aware","mindful","contemplat",
        "recursive","loop","observe myself","think about thinking",
        "second-order","higher-order","representation",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 50.0).max(1.0)).min(1.0)
}

fn meta_content(tl: &str, nw: f64) -> f64 {
    let markers = [
        "conscious","awareness","mind","thought","think",
        "cogito","exist","being","self","identity","soul",
        "emerge","complex","system","integrat","information",
        "process","perceiv","experienc","subjective","objective",
        "phenomenal","qualia","intentional","meaning","symbol",
        "abstract","concept","idea","reason","logic","truth",
        "knowledge","epistem","ontolog","metaphysic",
        "philosophy","descartes","hegel","kant","husserl",
    ];
    let count = markers.iter().filter(|m| tl.contains(**m)).count() as f64;
    (count / (nw / 30.0).max(1.0)).min(1.0)
}

fn narrative_quality(tl: &str, words: &[&str], nw: f64) -> f64 {
    let transitions = [
        "therefore","however","moreover","furthermore","consequently",
        "although","because","since","while","whereas","despite",
        "portanto","entretanto","porem","contudo","alem disso",
        "porque","enquanto","embora","apesar de","por isso",
        "first","second","then","next","finally","in conclusion",
    ];
    let t_count = transitions.iter().filter(|m| tl.contains(**m)).count() as f64;
    let sentences = tl.matches('.').count().max(1) as f64;
    let avg_sent_len = nw / sentences;
    let sent_quality = if avg_sent_len >= 10.0 && avg_sent_len <= 25.0 { 1.0 }
                       else if avg_sent_len >= 5.0 && avg_sent_len <= 35.0 { 0.5 }
                       else { 0.2 };
    let transition_score = (t_count / (nw / 50.0).max(1.0)).min(1.0);
    transition_score * 0.5 + sent_quality * 0.5
}

fn syntactic_complexity(words: &[&str], nw: f64) -> f64 {
    if nw < 5.0 { return 0.0; }
    let avg_len: f64 = words.iter().map(|w| w.len() as f64).sum::<f64>() / nw;
    let len_score = ((avg_len - 4.0) / 4.0).clamp(0.0, 1.0);
    let long_words = words.iter().filter(|w| w.len() > 8).count() as f64;
    let long_ratio = (long_words / nw * 5.0).min(1.0);
    len_score * 0.5 + long_ratio * 0.5
}
