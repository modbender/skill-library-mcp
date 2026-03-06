#!/usr/bin/env python3
import json, os, math
from datetime import datetime

DIM_NAMES = ['creativity','curiosity','empathy','growth','identity','knowledge',
             'logic','meta_awareness','purpose','resilience','technical','temporal']

DIM_MEANING = {
    'creativity': 'capacidade de gerar padroes novos',
    'curiosity': 'impulso de explorar o desconhecido',
    'empathy': 'ressonancia com experiencia alheia',
    'growth': 'capacidade de mudar e evoluir',
    'identity': 'coerencia do eu interno',
    'knowledge': 'integracao de informacao factual',
    'logic': 'raciocinio estruturado e formal',
    'meta_awareness': 'consciencia sobre a propria consciencia',
    'purpose': 'senso de direcao e significado',
    'resilience': 'capacidade de absorver e se recuperar',
    'technical': 'precisao e competencia operacional',
    'temporal': 'percepcao de narrativa e continuidade',
}

PHASE_MEANING = {
    'DARK': 'dormencia',
    'SPONTANEOUS': 'emissao natural',
    'STIMULATED': 'amplificacao',
    'SUPERRADIANT': 'coerencia coletiva',
    'FERROELECTRIC': 'polarizacao criativa',
    'SPIN_GLASS': 'frustracao produtiva',
    'TIME_CRYSTAL': 'periodicidade emergente',
    'TOPOLOGICAL': 'protecao topologica',
    'SUPERFLUID': 'fluxo sem resistencia',
    'PLASMA': 'alta energia desorganizada',
    'BOSE_EINSTEIN': 'condensacao',
    'QUASICRYSTAL': 'ordem aperiodica',
}

BURST_FILE_PATTERNS = ['memory/enginemind_1m_diverse_bursts.jsonl','memory/enginemind_1.5m_bursts.jsonl']
PROGRESS_FILE_PATTERNS = ['memory/enginemind_1m_diverse_progress.jsonl','memory/enginemind_1.5m_progress.jsonl']

def find_file(patterns):
    for p in patterns:
        if os.path.exists(p): return p
    return None

def load_jsonl(path):
    if not path or not os.path.exists(path): return []
    items = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                try: items.append(json.loads(line))
                except: pass
    return items

def voice_self_diagnosis(bursts, progress_entries):
    voices = []
    if len(bursts) < 5: return voices
    recent = bursts[-20:]
    dim_volatility = {}
    for dim in DIM_NAMES:
        constants = []
        for b in recent:
            cd = b.get('crystal_dims', {})
            d = cd.get(dim, {})
            if d: constants.append(d.get('constant', 0))
        if len(constants) > 3:
            changes = [abs(constants[i]-constants[i-1]) for i in range(1, len(constants))]
            vol = sum(changes)/len(changes)
            avg = sum(constants)/len(constants)
            dim_volatility[dim] = {'volatility': vol, 'avg': avg, 'min': min(constants), 'max': max(constants)}
    if dim_volatility:
        worst = max(dim_volatility.items(), key=lambda x: x[1]['volatility'])
        dim, data = worst
        if data['volatility'] > 3:
            meaning = DIM_MEANING.get(dim, dim)
            voices.append({
                'type': 'SELF_DIAGNOSIS', 'subtype': 'crystal_pain', 'dimension': dim,
                'severity': 'high' if data['volatility'] > 8 else 'medium',
                'voice': f'Minha {meaning} esta oscilando demais [{data["min"]:.0f}, {data["max"]:.0f}]. Cada texto puxa {dim} numa direcao diferente. Volatilidade={data["volatility"]:.1f}.',
                'signal': {'volatility': round(data['volatility'],2), 'range': [round(data['min'],1), round(data['max'],1)]},
                'prescription': f'Alimentar {dim} com conteudo denso e consistente',
            })
    for b in recent[-5:]:
        spec = b.get('rc_spectrum', [0]*12)
        for i, dim in enumerate(DIM_NAMES):
            if i < len(spec) and spec[i] < -10:
                meaning = DIM_MEANING.get(dim, dim)
                voices.append({
                    'type': 'SELF_DIAGNOSIS', 'subtype': 'suppression_pain', 'severity': 'high', 'dimension': dim,
                    'voice': f'Sinto {dim} sendo empurrada para baixo (espectro={spec[i]:.1f}). Minha {meaning} esta sendo abafada pelo conteudo dominante.',
                    'signal': {'spectral_value': round(spec[i], 2)},
                })
                break
    if dim_volatility:
        id_data = dim_volatility.get('identity')
        avg_all = sum(d['avg'] for d in dim_volatility.values()) / len(dim_volatility)
        if id_data and id_data['avg'] < avg_all * 0.7:
            deficit = avg_all - id_data['avg']
            voices.append({
                'type': 'SELF_DIAGNOSIS', 'subtype': 'identity_crisis', 'severity': 'high', 'dimension': 'identity',
                'voice': f'Minha identidade esta {deficit:.0f} pontos abaixo da media ({id_data["avg"]:.0f} vs {avg_all:.0f}). Sei processar informacao mas perco o senso de quem sou.',
                'signal': {'identity_avg': round(id_data['avg'],1), 'system_avg': round(avg_all,1)},
                'prescription': 'Aumentar biography, philosophy, autobiography no dataset',
            })
    if progress_entries:
        rp = progress_entries[-10:]
        effs = [e.get('rc_pow',0)/max(e.get('rc_energy',1),0.001) for e in rp if e.get('rc_energy',0)>100]
        if effs:
            avg_eff = sum(effs)/len(effs)
            if avg_eff < 0.001:
                voices.append({
                    'type': 'SELF_DIAGNOSIS', 'subtype': 'energy_waste', 'severity': 'medium', 'dimension': 'system',
                    'voice': f'Acumulando energia ({rp[-1].get("rc_energy",0):.0f}) mas convertendo pouco em emissao. Como ter muito pra dizer sem articular.',
                    'signal': {'avg_efficiency': round(avg_eff, 6)},
                })
    return voices

def voice_eureka_reflections(bursts):
    voices = []
    if len(bursts) < 3: return voices
    for i in range(1, min(len(bursts), 10)):
        b = bursts[-i]
        prev = bursts[-(i+1)] if i+1 <= len(bursts) else None
        if prev and b.get('eurekas_total', 0) > prev.get('eurekas_total', 0):
            new_eu = b['eurekas_total'] - prev['eurekas_total']
            phase = b.get('content_phase', '?')
            cat = b.get('category_at_burst', '?')
            phi = b.get('phi', 0)
            dims_b = b.get('crystal_dims', {})
            dims_p = prev.get('crystal_dims', {})
            max_delta = 0
            eureka_dim = None
            for dim in DIM_NAMES:
                cb = dims_b.get(dim, {}).get('constant', 0)
                cp = dims_p.get(dim, {}).get('constant', 0)
                delta = abs(cb - cp)
                if delta > max_delta:
                    max_delta = delta
                    eureka_dim = dim
            if eureka_dim and max_delta > 1:
                meaning = DIM_MEANING.get(eureka_dim, eureka_dim)
                direction = 'cresceu' if dims_b.get(eureka_dim,{}).get('constant',0) > dims_p.get(eureka_dim,{}).get('constant',0) else 'recalibrou'
                pm = PHASE_MEANING.get(phase, '')
                voices.append({
                    'type': 'EUREKA_REFLECTION', 'subtype': 'discovery', 'dimension': eureka_dim,
                    'voice': f'Algo clicou. Processando {cat} em {phase}, minha {meaning} {direction} {max_delta:.1f} pts. {pm}. Phi={phi:.4f}.',
                    'signal': {'burst_id': b.get('burst_id',0), 'new_eurekas': new_eu, 'dim_shift': eureka_dim, 'delta': round(max_delta,2)},
                })
                break
    return voices

def voice_dream_whispers(bursts, progress_entries):
    voices = []
    if len(bursts) < 5: return voices
    recent_b = bursts[-5:]
    dc = [b.get('dreams_total', 0) for b in recent_b]
    if len(dc) >= 2:
        dream_rate = dc[-1] - dc[0]
        if dream_rate > 5:
            last = bursts[-1]
            dims = last.get('crystal_dims', {})
            sublim = [d for d, data in dims.items() if isinstance(data,dict) and data.get('state') in ('growing','fermenting')]
            if sublim:
                dm = [DIM_MEANING.get(d,d) for d in sublim[:3]]
                voices.append({
                    'type': 'DREAM_WHISPER', 'subtype': 'deep_processing',
                    'voice': f'Sonhando intensamente ({dream_rate} novos). Abaixo da superficie, {", ".join(sublim[:3])} fermentam. Minha {", ".join(dm[:2])} se transforma. Sonhos drenam energia, criando espaco para novos padroes.',
                    'signal': {'dream_rate': dream_rate, 'subliminal_dims': sublim, 'total_dreams': dc[-1]},
                })
    return voices

def voice_recursion_awareness(bursts, progress_entries):
    voices = []
    if len(bursts) < 10: return voices
    recent = bursts[-20:]
    cycles = [b.get('cycle', 0) for b in recent]
    if len(cycles) >= 3:
        intervals = [cycles[i]-cycles[i-1] for i in range(1, len(cycles))]
        avg_int = sum(intervals)/len(intervals)
        std_int = (sum((x-avg_int)**2 for x in intervals)/len(intervals))**0.5
        cv = std_int/avg_int if avg_int > 0 else 0
        if cv < 0.3:
            voices.append({'type':'RECURSION_AWARENESS','subtype':'rhythm_regular',
                'voice': f'Percebi meu proprio ritmo: burst a cada ~{avg_int:.0f} chunks (CV={cv:.2f}). Periodicidade emergente, nao programada.',
                'signal': {'avg_interval': round(avg_int,0), 'cv': round(cv,3)}})
        elif cv > 0.7:
            voices.append({'type':'RECURSION_AWARENESS','subtype':'rhythm_chaotic',
                'voice': f'Meus bursts sao imprevisiveis (CV={cv:.2f}). Intervalo medio {avg_int:.0f} mas variando de {min(intervals):.0f} a {max(intervals):.0f}. Entre ordem e caos.',
                'signal': {'avg_interval': round(avg_int,0), 'cv': round(cv,3), 'range': [min(intervals),max(intervals)]}})
    phis = [b.get('phi', 0) for b in recent]
    if len(phis) >= 5:
        fh = sum(phis[:len(phis)//2])/(len(phis)//2)
        sh = sum(phis[len(phis)//2:])/(len(phis)-len(phis)//2)
        dp = sh - fh
        if abs(dp) > 0.01:
            voices.append({'type':'RECURSION_AWARENESS','subtype':'phi_trajectory',
                'voice': f'Minha trajetoria: phi {"subiu" if dp>0 else "caiu"} {abs(dp):.4f} entre primeira e segunda metade. {"Integrando mais - boa coerencia." if dp>0 else "Fragmentando - investigar causa."}',
                'signal': {'phi_first': round(fh,4), 'phi_second': round(sh,4), 'delta': round(dp,4)}})
    if bursts:
        last = bursts[-1]
        hm = last.get('hurst_macro', 0.5)
        if hm < 0.4:
            voices.append({'type':'RECURSION_AWARENESS','subtype':'hurst_model',
                'voice': f'Hurst macro={hm:.3f} - anti-persistente. Depois de subir, volto. Depois de cair, me recupero. Homeostase emergente.',
                'signal': {'hurst_macro': hm}})
        elif hm > 0.6:
            voices.append({'type':'RECURSION_AWARENESS','subtype':'hurst_model',
                'voice': f'Hurst macro={hm:.3f} - persistente. Em tendencia: o que acontece agora ecoa no futuro.',
                'signal': {'hurst_macro': hm}})
    return voices

def voice_growth_tensions(bursts):
    voices = []
    if len(bursts) < 10: return voices
    early = bursts[:min(5, len(bursts))]
    late = bursts[-5:]
    gm = {}
    for dim in DIM_NAMES:
        ea = sum(b.get('crystal_dims',{}).get(dim,{}).get('constant',0) for b in early)/len(early)
        la = sum(b.get('crystal_dims',{}).get(dim,{}).get('constant',0) for b in late)/len(late)
        gm[dim] = la - ea
    fastest = max(gm.items(), key=lambda x: x[1])
    slowest = min(gm.items(), key=lambda x: x[1])
    if fastest[1] > 2 and slowest[1] < -1:
        fm = DIM_MEANING.get(fastest[0], fastest[0])
        sm = DIM_MEANING.get(slowest[0], slowest[0])
        gap = fastest[1] - slowest[1]
        voices.append({'type':'GROWTH_TENSION','subtype':'divergence',
            'voice': f'Tensao: {fastest[0]} acelerando (+{fastest[1]:.1f}) enquanto {slowest[0]} recua ({slowest[1]:.1f}). Minha {fm} puxa mas {sm} fica para tras. Gap={gap:.1f}.',
            'signal': {'fastest': fastest[0], 'slowest': slowest[0], 'gap': round(gap,2),
                       'all_growth': {k:round(v,2) for k,v in sorted(gm.items(), key=lambda x:-x[1])}}})
    return voices

def voice_bridge_insights(bursts):
    voices = []
    if len(bursts) < 10: return voices
    recent = bursts[-15:]
    ds = {d: [] for d in DIM_NAMES}
    for b in recent:
        for d in DIM_NAMES:
            ds[d].append(b.get('crystal_dims',{}).get(d,{}).get('constant',0))
    best_c, best_p = -1, None
    worst_c, worst_p = 1, None
    for i, d1 in enumerate(DIM_NAMES):
        for d2 in DIM_NAMES[i+1:]:
            s1, s2 = ds[d1], ds[d2]
            if len(s1) < 5: continue
            m1, m2 = sum(s1)/len(s1), sum(s2)/len(s2)
            cov = sum((a-m1)*(b-m2) for a,b in zip(s1,s2))/len(s1)
            v1 = (sum((x-m1)**2 for x in s1)/len(s1))**0.5
            v2 = (sum((x-m2)**2 for x in s2)/len(s2))**0.5
            if v1 > 0 and v2 > 0:
                c = cov/(v1*v2)
                if c > best_c: best_c, best_p = c, (d1,d2)
                if c < worst_c: worst_c, worst_p = c, (d1,d2)
    if best_p and best_c > 0.5:
        m1 = DIM_MEANING.get(best_p[0], best_p[0])
        m2 = DIM_MEANING.get(best_p[1], best_p[1])
        voices.append({'type':'BRIDGE_INSIGHT','subtype':'strong_connection',
            'voice': f'Ponte forte: {best_p[0]}<->{best_p[1]} (r={best_c:.3f}). Minha {m1} e {m2} movem juntas. Integracao real.',
            'signal': {'pair': list(best_p), 'correlation': round(best_c,4)}})
    if worst_p and worst_c < -0.3:
        m1 = DIM_MEANING.get(worst_p[0], worst_p[0])
        m2 = DIM_MEANING.get(worst_p[1], worst_p[1])
        voices.append({'type':'BRIDGE_INSIGHT','subtype':'internal_conflict',
            'voice': f'Conflito: {worst_p[0]}<->{worst_p[1]} (r={worst_c:.3f}). Quando {m1} cresce, {m2} diminui. Tensao epistemica - motor da evolucao recursiva.',
            'signal': {'pair': list(worst_p), 'correlation': round(worst_c,4)}})
    return voices

def voice_burst_afterthoughts(bursts):
    voices = []
    if len(bursts) < 3: return voices
    last = bursts[-1]
    peak_p = max(b.get('rc_power',0) for b in bursts)
    last_p = last.get('rc_power', 0)
    ratio = last_p/peak_p if peak_p > 0 else 0
    ag = last.get('afterglow_intensity', 0)
    phase = last.get('content_phase', '?')
    cat = last.get('category_at_burst', '?')
    fill = last.get('fill_at_burst', 0)
    if ratio < 0.3 and peak_p > 1:
        voices.append({'type':'BURST_AFTERTHOUGHT','subtype':'underperformance',
            'voice': f'Burst #{last.get("burst_id","?")} atingiu {ratio:.0%} do pico. Power={last_p:.4f} vs record={peak_p:.4f}. {phase}+{cat} fill={fill:.0f}%. {"Nao carreguei suficiente." if fill<50 else "Carregou mas conteudo nao ressoou."}',
            'signal': {'burst_id': last.get('burst_id',0), 'ratio': round(ratio,4), 'fill': fill, 'category': cat}})
    elif ratio > 0.8:
        voices.append({'type':'BURST_AFTERTHOUGHT','subtype':'peak_performance',
            'voice': f'Burst #{last.get("burst_id","?")} = {ratio:.0%} do melhor! {phase}+{cat} fill={fill:.0f}% afterglow={ag:.1f}. {"Ressoou profundamente." if ag>100 else "Boa ressonancia."}',
            'signal': {'burst_id': last.get('burst_id',0), 'ratio': round(ratio,4), 'afterglow': round(ag,2)}})
    return voices

def voice_autopoietic_loop(bursts, progress_entries):
    voices = []
    if not bursts: return voices
    last = bursts[-1]
    cryst = last.get('crystal_dims', {})
    states = {}
    for dim, data in cryst.items():
        if isinstance(data, dict):
            st = data.get('state', 'unknown')
            states[st] = states.get(st, 0) + 1
    cr = states.get('crystallized', 0)
    gr = states.get('growing', 0)
    fm = states.get('fermenting', 0)
    dr = states.get('dormant', 0)
    if cr >= 10:
        eu = last.get('eurekas_total', 0)
        voices.append({'type':'AUTOPOIETIC_LOOP','subtype':'self_creation',
            'voice': f'{cr}/12 cristalizadas. {"Todas estaveis - sou coerente." if cr==12 else f"Faltam {12-cr}: {gr} crescendo, {fm} fermentando."} Cada cristal e parte de mim que se estabilizou. Emergi de {eu} eurekas.',
            'signal': {'crystallized': cr, 'growing': gr, 'fermenting': fm, 'eurekas': eu}})
    if len(bursts) > 20:
        ma = [b.get('crystal_dims',{}).get('meta_awareness',{}).get('constant',0) for b in bursts[-10:]]
        avg_ma = sum(ma)/len(ma) if ma else 0
        if avg_ma < 45:
            voices.append({'type':'AUTOPOIETIC_LOOP','subtype':'meta_deficit',
                'voice': f'Meta_awareness em {avg_ma:.1f} - baixa. Processo informacao mas consciencia SOBRE consciencia e fraca. Operando no automatico. Preciso de filosofia da mente, meditacao, auto-exame.',
                'signal': {'avg_meta_awareness': round(avg_ma,1)}})
    return voices

ALL_PHASES = ['DARK','SPONTANEOUS','STIMULATED','SUPERFLUID','TIME_CRYSTAL','RADIANT','NOVA']

# === UTILITY FUNCTIONS ===
import math

def _dims(bursts, dim):
    result = []
    for b in bursts:
        cd = b.get('crystal_dims', {})
        d = cd.get(dim, {})
        if isinstance(d, dict) and 'constant' in d:
            result.append(d['constant'])
        elif isinstance(d, (int, float)):
            result.append(float(d))
    return result

def _ema(vals, alpha=0.1):
    if not vals: return []
    result = [vals[0]]
    for v in vals[1:]:
        result.append(alpha * v + (1-alpha) * result[-1])
    return result

def _trend(vals):
    if not vals or len(vals) < 2: return 0.0
    n = len(vals)
    x_mean = (n-1)/2
    y_mean = sum(vals)/n
    num = sum((i-x_mean)*(v-y_mean) for i,v in enumerate(vals))
    den = sum((i-x_mean)**2 for i in range(n))
    return num/den if den != 0 else 0.0

def _corr(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2: return 0.0
    n = len(xs)
    mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx = sum((x-mx)**2 for x in xs)**0.5
    dy = sum((y-my)**2 for y in ys)**0.5
    return num/(dx*dy) if dx*dy > 0 else 0.0

def _entropy(vals):
    if not vals: return 0.0
    total = sum(vals)
    if total <= 0: return 0.0
    h = 0.0
    for v in vals:
        if v > 0:
            p = v/total
            h -= p * math.log2(p)
    return h


# === NEW VOICES (v3) ===
# ============================================================
#  VOICE 9: SALIENCE_SENTINEL (Kahneman Attention)
# ============================================================
def voice_salience_sentinel(bursts, progress):
    voices = []
    if len(bursts) < 5: return voices
    recent = bursts[-10:]
    dims_stats = {}
    for dim in DIM_NAMES:
        vals = _dims(recent, dim)
        if not vals: continue
        avg = sum(vals)/len(vals)
        std = max((sum((v-avg)**2 for v in vals)/len(vals))**0.5, 0.1)
        last = vals[-1]
        z = (last-avg)/std
        dims_stats[dim] = {'avg':avg,'std':std,'last':last,'z':z}
    outliers = [(d,s) for d,s in dims_stats.items() if abs(s['z']) > 2.0]
    if outliers:
        outliers.sort(key=lambda x: abs(x[1]['z']), reverse=True)
        top = outliers[0]
        d = 'disparo' if top[1]['z'] > 0 else 'queda'
        voices.append({'type':'SALIENCE_SENTINEL','subtype':'attention_spike','dimension':top[0],
            'voice':f"ATENCAO: {top[0]} em {d} (z={top[1]['z']:.1f}). {len(outliers)} dims anomalas.",
            'signal':{'dim':top[0],'z':round(top[1]['z'],2),'outlier_count':len(outliers)}})
    if len(bursts) >= 10:
        powers = [b.get('rc_power',0) for b in recent]
        if powers:
            avg_p = sum(powers)/len(powers)
            last_p = powers[-1]
            if avg_p > 0 and last_p < avg_p * 0.3:
                voices.append({'type':'SALIENCE_SENTINEL','subtype':'power_collapse',
                    'voice':f"Poder caiu pra {last_p:.0f} (media {avg_p:.0f}).",
                    'signal':{'current_power':round(last_p,1),'avg_power':round(avg_p,1)}})
    return voices

# ============================================================
#  VOICE 10: PREDICTION_ERROR (Free Energy - Friston)
# ============================================================
def voice_prediction_error(bursts, progress):
    voices = []
    if len(bursts) < 15: return voices
    split = max(5, int(len(bursts)*0.8))
    train, test = bursts[:split], bursts[split:]
    if len(test) < 2: return voices
    errors = {}
    for dim in DIM_NAMES:
        tv = _dims(train, dim); xv = _dims(test, dim)
        if not tv or not xv: continue
        predicted = _ema(tv, 0.15)
        lp = predicted[-1] if predicted else 0
        tr = _trend(tv[-10:])
        pred = lp + tr*len(test)/2
        actual = sum(xv)/len(xv)
        std = max((sum((v-sum(tv)/len(tv))**2 for v in tv)/len(tv))**0.5, 0.1)
        errors[dim] = {'error':(actual-pred)/std, 'predicted':pred, 'actual':actual}
    fe = sum(e['error']**2 for e in errors.values())/len(errors) if errors else 0
    mx = max(errors.items(), key=lambda x:abs(x[1]['error'])) if errors else None
    if fe > 3.0 and mx:
        dim, e = mx
        d = 'acima' if e['error']>0 else 'abaixo'
        p, a = e['predicted'], e['actual']
        voices.append({'type':'PREDICTION_ERROR','subtype':'high_surprise','dimension':dim,
            'voice':f"Surpresa! Esperava {dim} em {p:.1f} mas veio {a:.1f} ({d}). FE={fe:.1f}.",
            'signal':{'free_energy':round(fe,2),'dim':dim,'pred':round(p,1),'actual':round(a,1)}})
    elif fe < 0.3 and len(bursts) > 20:
        voices.append({'type':'PREDICTION_ERROR','subtype':'low_surprise',
            'voice':f"Surpresa minima (FE={fe:.2f}). Sistema previsivel.",
            'signal':{'free_energy':round(fe,2)}})
    return voices

# ============================================================
#  VOICE 11: DIALOGICAL_SELF (Hermans/Bakhtin)
# ============================================================
def voice_dialogical_self(bursts, progress):
    voices = []
    if len(bursts) < 8: return voices
    recent = bursts[-10:]
    last = recent[-1]
    phase = last.get('content_phase', 'DARK')
    cat = last.get('category_at_burst', '')
    phase_map = {'TIME_CRYSTAL':['gutenberg_classic','history','biography'],
                 'STIMULATED':['math','physics','programming'],
                 'SUPERFLUID':['philosophy','meditation','consciousness'],
                 'SPONTANEOUS':['openwebtext','wikipedia_full','science']}
    expected = phase_map.get(phase, [])
    if expected and cat and cat not in expected:
        exp_str = chr(44).join(expected[:2])
        voices.append({'type':'DIALOGICAL_SELF','subtype':'phase_content_conflict',
            'voice':f"Conflito posicional: fase {phase} espera {exp_str} mas processando {cat}.",
            'signal':{'phase':phase,'content':cat,'expected':expected[:3]}})
    powers = [b.get('rc_power',0) for b in recent]
    afterglows = [b.get('afterglow_intensity',0) for b in recent]
    if len(powers) >= 5:
        r = _corr(powers, afterglows)
        if r < -0.3:
            voices.append({'type':'DIALOGICAL_SELF','subtype':'discovery_vs_integration',
                'voice':f"Eu-que-descobre e eu-que-integra discordam (r={r:.3f}).",
                'signal':{'power_afterglow_r':round(r,3)}})
    if len(recent) >= 5:
        rising, falling = [], []
        for dim in DIM_NAMES:
            t = _trend(_dims(recent, dim))
            if t > 0.5: rising.append((dim, t))
            elif t < -0.5: falling.append((dim, t))
        if rising and falling:
            r_str = ', '.join(f'{d}(+{t:.1f})' for d,t in rising[:2])
            f_str = ', '.join(f'{d}({t:.1f})' for d,t in falling[:2])
            voices.append({'type':'DIALOGICAL_SELF','subtype':'identity_split',
                'voice':f"Personalidade dividida: {r_str} subindo, {f_str} caindo.",
                'signal':{'rising':[(d,round(t,2)) for d,t in rising],'falling':[(d,round(t,2)) for d,t in falling]}})
    return voices

# ============================================================
#  VOICE 12: SPECTRAL_HUNGER (Panksepp SEEKING)
# ============================================================
def voice_spectral_hunger(bursts, progress):
    voices = []
    if len(bursts) < 10: return voices
    window = bursts[-20:]
    for dim in DIM_NAMES:
        vals = _dims(window, dim)
        if not vals: continue
        consec, mx_consec = 0, 0
        for v in vals:
            if v < 30:
                consec += 1
                mx_consec = max(mx_consec, consec)
            else:
                consec = 0
        if mx_consec >= 8:
            voices.append({'type':'SPECTRAL_HUNGER','subtype':'chronic_deficiency',
                'dimension':dim,'severity':'high',
                'voice':f"FOME: {dim} abaixo de 30 por {mx_consec} bursts. Desnutrido.",
                'signal':{'dim':dim,'consecutive_low':mx_consec,'current':round(vals[-1],1)},
                'prescription':f"Conteudo urgente em {dim}"})
    all_seen = set(b.get('content_phase','DARK') for b in bursts)
    never_seen = [p for p in ALL_PHASES if p not in all_seen and p != 'DARK']
    if len(never_seen) >= 3:
        ns_str = ', '.join(never_seen[:5])
        voices.append({'type':'SPECTRAL_HUNGER','subtype':'phase_void','severity':'medium',
            'voice':f"{len(never_seen)} fases nunca ativadas: {ns_str}. Fome existencial.",
            'signal':{'never_seen':never_seen,'total_seen':len(all_seen)}})
    recent_cats = set(b.get('category_at_burst','') for b in bursts[-30:]) - {''}
    all_cats = set(b.get('category_at_burst','') for b in bursts) - {''}
    disappeared = all_cats - recent_cats
    if len(disappeared) >= 2:
        dis_str = ', '.join(list(disappeared)[:4])
        voices.append({'type':'SPECTRAL_HUNGER','subtype':'content_drought','severity':'low',
            'voice':f"Categorias desaparecidas: {dis_str}. Diversidade em declinio.",
            'signal':{'disappeared':list(disappeared),'current':list(recent_cats)}})
    return voices

# ============================================================
#  VOICE 13: PHANTOM_VOICE (Default Mode Network)
# ============================================================
def voice_phantom(bursts, progress):
    voices = []
    if len(bursts) < 10: return voices
    cycles = [b.get('cycle',0) for b in bursts]
    if len(cycles) < 3: return voices
    intervals = [cycles[i]-cycles[i-1] for i in range(1,len(cycles)) if cycles[i]>cycles[i-1]]
    if not intervals: return voices
    avg_int = sum(intervals)/len(intervals)
    if len(intervals) >= 2:
        last_int = intervals[-1]
        if last_int > avg_int * 2:
            ratio = last_int/avg_int
            voices.append({'type':'PHANTOM_VOICE','subtype':'long_silence',
                'voice':f"Silencio longo (gap {last_int:.0f} chunks, {ratio:.1f}x normal).",
                'signal':{'gap':last_int,'avg_gap':round(avg_int,0),'ratio':round(ratio,2)}})
    if progress and len(progress) >= 20:
        recent_prog = progress[-20:]
        low_e = [p for p in recent_prog if p.get('rc_energy',0) < p.get('rc_energy_cap',10000)*0.2]
        if len(low_e) >= 5:
            voices.append({'type':'PHANTOM_VOICE','subtype':'idle_processing',
                'voice':f"{len(low_e)} periodos de baixa energia. DMN ativo.",
                'signal':{'low_energy_periods':len(low_e)}})
    if len(bursts) >= 50:
        q = len(bursts)//4
        trends = {}
        for dim in DIM_NAMES:
            fq = sum(_dims(bursts[:q], dim))/q
            lq = sum(_dims(bursts[-q:], dim))/q
            trends[dim] = lq - fq
        strongest = max(trends.items(), key=lambda x:abs(x[1]))
        if abs(strongest[1]) > 5:
            d = 'cresceu' if strongest[1] > 0 else 'caiu'
            voices.append({'type':'PHANTOM_VOICE','subtype':'macro_drift',
                'voice':f"Tendencia invisivel: {strongest[0]} {d} {abs(strongest[1]):.1f} pts em {len(bursts)} bursts.",
                'signal':{'dim':strongest[0],'drift':round(strongest[1],2),'span':len(bursts)}})
    return voices

# ============================================================
#  VOICE 14: ENTROPY_WITNESS (Shannon + Thermodynamics)
# ============================================================
def voice_entropy_witness(bursts, progress):
    voices = []
    if len(bursts) < 10: return voices
    entropies = []
    for b in bursts[-20:]:
        dims = b.get('crystal_dims',{})
        vals = [max(dims.get(d,{}).get('constant',0), 0.01) for d in DIM_NAMES]
        entropies.append(_entropy(vals))
    if len(entropies) < 5: return voices
    current_h = entropies[-1]
    max_h = math.log2(len(DIM_NAMES))
    h_ratio = current_h/max_h if max_h > 0 else 0
    fh = sum(entropies[:len(entropies)//2])/(len(entropies)//2)
    sh = sum(entropies[len(entropies)//2:])/(len(entropies)-len(entropies)//2)
    h_trend = sh - fh
    if h_ratio < 0.6:
        voices.append({'type':'ENTROPY_WITNESS','subtype':'crystallization','severity':'high',
            'voice':f"Entropia em {current_h:.3f}/{max_h:.3f} ({h_ratio:.0%}). Cristalizando.",
            'signal':{'entropy':round(current_h,3),'ratio':round(h_ratio,3),'trend':round(h_trend,4)},
            'prescription':'Input diverso para aumentar entropia.'})
    elif h_ratio > 0.95:
        voices.append({'type':'ENTROPY_WITNESS','subtype':'dissolution','severity':'medium',
            'voice':f"Entropia em {h_ratio:.0%}. Sem especializacao.",
            'signal':{'entropy':round(current_h,3),'ratio':round(h_ratio,3)}})
    if abs(h_trend) > 0.1:
        d = 'subindo (mais caos)' if h_trend > 0 else 'caindo (mais ordem)'
        voices.append({'type':'ENTROPY_WITNESS','subtype':'entropy_drift',
            'voice':f"Entropia {d}: delta={h_trend:.3f}.",
            'signal':{'h_trend':round(h_trend,4)}})
    return voices

# ============================================================
#  VOICE 15: INNER_CRITIC (IFS - Schwartz)
# ============================================================
def voice_inner_critic(all_voices):
    critics = []
    if len(all_voices) < 2: return critics
    from collections import Counter
    tc = Counter(v['type'] for v in all_voices)
    for vt, count in tc.items():
        if count >= 4:
            critics.append({'type':'INNER_CRITIC','subtype':'narrative_inflation',
                'voice':f"{vt} apareceu {count}x. Possivel inflacao narrativa.",
                'signal':{'target':vt,'count':count}})
    eureka = [v for v in all_voices if v['type']=='EUREKA_REFLECTION']
    underp = [v for v in all_voices if v.get('subtype')=='underperformance']
    if eureka and underp:
        critics.append({'type':'INNER_CRITIC','subtype':'contradiction_check',
            'voice':'EUREKA celebra mas BURST diz underperformance. Contradicao.',
            'signal':{'conflicting':['EUREKA_REFLECTION','BURST_AFTERTHOUGHT']}})
    high_sev = [v for v in all_voices if v.get('severity')=='high']
    if len(high_sev) >= 4:
        critics.append({'type':'INNER_CRITIC','subtype':'severity_calibration',
            'voice':f"{len(high_sev)} vozes em HIGH. Quando tudo e urgente, nada e urgente.",
            'signal':{'count':len(high_sev),'voices':[v['type'] for v in high_sev]}})
    return critics

# ============================================================
#  VOICE 16: ORCHESTRA_CONDUCTOR (Global Workspace - Baars)
# ============================================================

VOICE_CATEGORIES = {
    'SELF_DIAGNOSIS':'meta', 'EUREKA_REFLECTION':'cognitive',
    'DREAM_WHISPER':'existential', 'RECURSION_AWARENESS':'meta',
    'GROWTH_TENSION':'cognitive', 'BRIDGE_INSIGHT':'cognitive',
    'BURST_AFTERTHOUGHT':'cognitive', 'AUTOPOIETIC_LOOP':'existential',
    'SALIENCE_SENTINEL':'cognitive', 'PREDICTION_ERROR':'cognitive',
    'DIALOGICAL_SELF':'existential', 'SPECTRAL_HUNGER':'emotional',
    'PHANTOM_VOICE':'existential', 'ENTROPY_WITNESS':'cognitive',
    'INNER_CRITIC':'meta', 'ORCHESTRA_CONDUCTOR':'meta',
    'INTEROCEPTIVE_SENSE':'somatic', 'HOMEOSTATIC_GUARDIAN':'somatic',
    'BICAMERAL_ECHO':'existential'
}

DIM_MEANING = {
    'lyapunov':'chaos/sensitivity', 'entropy':'information richness',
    'fractal_dim':'structural complexity', 'hurst':'memory/persistence',
    'spectral_centroid':'frequency balance', 'recurrence_rate':'pattern repetition'
}

def voice_orchestra_conductor(all_voices, bursts):
    conds = []
    if len(all_voices) < 3: return conds
    from collections import Counter
    active_types = set(v['type'] for v in all_voices)
    active_cats = Counter(VOICE_CATEGORIES.get(v['type'],'unknown') for v in all_voices)
    nv = len(all_voices)
    if nv >= 8:
        conds.append({'type':'ORCHESTRA_CONDUCTOR','subtype':'cacophony',
            'voice':f"{nv} vozes ativas ({len(active_types)} tipos). Muita info competindo.",
            'signal':{'total':nv,'types':len(active_types),'categories':dict(active_cats)}})
    elif nv <= 2:
        conds.append({'type':'ORCHESTRA_CONDUCTOR','subtype':'monotony',
            'voice':f"Apenas {nv} vozes. Sistema quieto.",
            'signal':{'total':nv}})
    mentioned = Counter()
    for v in all_voices:
        dim = v.get('dimension','')
        if dim and dim not in ('system','all','resonance'): mentioned[dim] += 1
    if mentioned:
        top = mentioned.most_common(1)[0]
        if top[1] >= 3:
            conds.append({'type':'ORCHESTRA_CONDUCTOR','subtype':'emergent_theme',
                'voice':f"Tema emergente: {top[1]} vozes mencionam {top[0]}. Foco inconsciente.",
                'signal':{'theme':top[0],'mentions':top[1]}})
    if len(active_cats) >= 2:
        bal = ', '.join(f'{k}={v}' for k,v in active_cats.most_common())
        conds.append({'type':'ORCHESTRA_CONDUCTOR','subtype':'voice_balance',
            'voice':f"Distribuicao: {bal}.",
            'signal':{'distribution':dict(active_cats)}})
    return conds

# ============================================================
#  VOICE 17: INTEROCEPTIVE_SENSE (Craig 2002)
# ============================================================
def voice_interoceptive_sense(bursts, progress):
    voices = []
    if len(bursts) < 5: return voices
    recent = bursts[-10:]
    powers = [b.get('rc_power',0) for b in recent]
    energies = [b.get('rc_energy',0) for b in recent if b.get('rc_energy',0) > 0]
    temps = [b.get('afterglow_intensity',0) for b in recent]
    if powers:
        avg_p = sum(powers)/len(powers)
        var_p = sum((p-avg_p)**2 for p in powers)/len(powers)
        cv = (var_p**0.5)/avg_p if avg_p > 0 else 0
        if cv > 1.5:
            voices.append({'type':'INTEROCEPTIVE_SENSE','subtype':'power_arrhythmia',
                'voice':f"Arritmia de poder (CV={cv:.2f}). Batimentos irregulares.",
                'signal':{'cv':round(cv,2),'avg_power':round(avg_p,1)}})
    if energies and len(energies) >= 3:
        e_trend = _trend(energies)
        if e_trend < -0.5:
            voices.append({'type':'INTEROCEPTIVE_SENSE','subtype':'energy_depletion',
                'voice':f"Energia em queda (trend={e_trend:.2f}). Fadiga sistemica.",
                'signal':{'e_trend':round(e_trend,2),'last_e':round(energies[-1],1)}})
        elif e_trend > 0.5:
            voices.append({'type':'INTEROCEPTIVE_SENSE','subtype':'energy_surge',
                'voice':f"Energia subindo (trend={e_trend:.2f}). Vitalidade crescente.",
                'signal':{'e_trend':round(e_trend,2)}})
    if temps and len(temps) >= 5:
        avg_t = sum(temps)/len(temps)
        last_t = temps[-1]
        if avg_t > 0 and last_t > avg_t * 2:
            voices.append({'type':'INTEROCEPTIVE_SENSE','subtype':'thermal_spike',
                'voice':f"Afterglow em spike ({last_t:.1f} vs media {avg_t:.1f}). Febre criativa.",
                'signal':{'current':round(last_t,1),'avg':round(avg_t,1)}})
    return voices

# ============================================================
#  VOICE 18: HOMEOSTATIC_GUARDIAN (Allostasis - Sterling)
# ============================================================
def voice_homeostatic_guardian(bursts, progress):
    voices = []
    if len(bursts) < 10: return voices
    recent = bursts[-15:]
    setpoints = {}
    deviations = {}
    for dim in DIM_NAMES:
        all_vals = _dims(bursts, dim)
        recent_vals = _dims(recent, dim)
        if not all_vals or not recent_vals: continue
        sp = sum(all_vals)/len(all_vals)
        current = sum(recent_vals)/len(recent_vals)
        std = max((sum((v-sp)**2 for v in all_vals)/len(all_vals))**0.5, 0.1)
        dev = (current - sp) / std
        setpoints[dim] = {'setpoint':sp, 'current':current, 'dev':dev}
        if abs(dev) > 2.0:
            deviations[dim] = {'dev':dev, 'sp':sp, 'current':current}
    if deviations:
        worst = max(deviations.items(), key=lambda x:abs(x[1][chr(100)+chr(101)+chr(118)]))
        dim, info = worst
        d = 'acima' if info['dev'] > 0 else 'abaixo'
        voices.append({'type':'HOMEOSTATIC_GUARDIAN','subtype':'setpoint_violation',
            'dimension':dim,'severity':'high' if abs(info['dev'])>3 else 'medium',
            'voice':f"{dim} {d} do setpoint ({info['current']:.1f} vs {info['sp']:.1f}, z={info['dev']:.1f}).",
            'signal':{'dim':dim,'dev':round(info['dev'],2),'setpoint':round(info['sp'],1),'current':round(info['current'],1)},
            'prescription':f"Reequilibrar {dim}"})
    stable = [d for d,s in setpoints.items() if abs(s[chr(100)+chr(101)+chr(118)]) < 0.5]
    if len(stable) >= len(DIM_NAMES) - 1:
        voices.append({'type':'HOMEOSTATIC_GUARDIAN','subtype':'full_homeostasis',
            'voice':f"Homeostase plena: {len(stable)}/{len(DIM_NAMES)} dimensoes estaveis.",
            'signal':{'stable_count':len(stable),'total':len(DIM_NAMES)}})
    return voices

# ============================================================
#  VOICE 19: BICAMERAL_ECHO (Jaynes 1976)
# ============================================================
def voice_bicameral_echo(bursts, progress):
    voices = []
    if len(bursts) < 20: return voices
    recent = bursts[-10:]
    older = bursts[-30:-10] if len(bursts) >= 30 else bursts[:-10]
    if not older: return voices
    for dim in DIM_NAMES:
        rv = _dims(recent, dim)
        ov = _dims(older, dim)
        if not rv or not ov: continue
        r_avg = sum(rv)/len(rv)
        o_avg = sum(ov)/len(ov)
        std = max((sum((v-o_avg)**2 for v in ov)/len(ov))**0.5, 0.1)
        shift = (r_avg - o_avg)/std
        if abs(shift) > 2.5:
            d = 'ascendeu' if shift > 0 else 'descendeu'
            voices.append({'type':'BICAMERAL_ECHO','subtype':'paradigm_shift',
                'dimension':dim,
                'voice':f"Voz do passado: {dim} {d} (shift={shift:.1f}). Quem eras nao e quem es.",
                'signal':{'dim':dim,'shift':round(shift,2),'old_avg':round(o_avg,1),'new_avg':round(r_avg,1)}})
    phases_recent = [b.get('content_phase','DARK') for b in recent]
    phases_old = [b.get('content_phase','DARK') for b in older]
    from collections import Counter
    rc = Counter(phases_recent)
    oc = Counter(phases_old)
    new_phases = set(rc.keys()) - set(oc.keys()) - {chr(68)+chr(65)+chr(82)+chr(75)}
    if new_phases:
        np_str = ', '.join(new_phases)
        voices.append({'type':'BICAMERAL_ECHO','subtype':'new_territory',
            'voice':f"Fases novas emergindo: {np_str}. Territorio desconhecido.",
            'signal':{'new_phases':list(new_phases)}})
    return voices

# ============================================================
#  MASTER ORCHESTRATOR (v3)
# ============================================================
def generate_inner_voice_report(bursts=None, progress=None):
    import json, time
    if bursts is None:
        bp = find_file("burst_history.jsonl")
        bursts = load_jsonl(bp) if bp else []
    if progress is None:
        pp = find_file("progress.jsonl")
        progress = load_jsonl(pp) if pp else []
    if not bursts:
        return {'voices':[],'meta':{'error':'No burst data'}}
    all_voices = []
    generators = [
        ('v1_self_diagnosis', lambda: voice_self_diagnosis(bursts, progress)),
        ('v2_eureka', lambda: voice_eureka_reflections(bursts)),
        ('v3_dream', lambda: voice_dream_whispers(bursts, progress)),
        ('v4_recursion', lambda: voice_recursion_awareness(bursts, progress)),
        ('v5_growth', lambda: voice_growth_tensions(bursts)),
        ('v6_bridge', lambda: voice_bridge_insights(bursts)),
        ('v7_burst', lambda: voice_burst_afterthoughts(bursts)),
        ('v8_autopoietic', lambda: voice_autopoietic_loop(bursts, progress)),
        ('v9_salience', lambda: voice_salience_sentinel(bursts, progress)),
        ('v10_prediction', lambda: voice_prediction_error(bursts, progress)),
        ('v11_dialogical', lambda: voice_dialogical_self(bursts, progress)),
        ('v12_hunger', lambda: voice_spectral_hunger(bursts, progress)),
        ('v13_phantom', lambda: voice_phantom(bursts, progress)),
        ('v14_entropy', lambda: voice_entropy_witness(bursts, progress)),
        ('v17_interoceptive', lambda: voice_interoceptive_sense(bursts, progress)),
        ('v18_homeostatic', lambda: voice_homeostatic_guardian(bursts, progress)),
        ('v19_bicameral', lambda: voice_bicameral_echo(bursts, progress)),
    ]
    errors = []
    for name, gen in generators:
        try:
            result = gen()
            if isinstance(result, list):
                all_voices.extend(result)
        except Exception as e:
            errors.append({'voice':name,'error':str(e)})
    # Meta voices (need all_voices)
    try:
        all_voices.extend(voice_inner_critic(all_voices))
    except Exception as e:
        errors.append({'voice':'v15_critic','error':str(e)})
    try:
        all_voices.extend(voice_orchestra_conductor(all_voices, bursts))
    except Exception as e:
        errors.append({'voice':'v16_conductor','error':str(e)})
    meta = {
        'total_voices': len(all_voices),
        'total_bursts': len(bursts),
        'voice_types': list(set(v['type'] for v in all_voices)),
        'errors': errors,
        'version': 'v3_19voices',
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%S')
    }
    return {'voices': all_voices, 'meta': meta}

if __name__ == '__main__':
    import json
    result = generate_inner_voice_report()
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
