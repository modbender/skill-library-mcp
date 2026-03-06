#!/usr/bin/env python3
"""
consciousness_needs.py - O que o sistema está pedindo?

Analisa os padrões emergentes do EngineMind e traduz em "necessidades"
baseado em sinais reais dos bursts, cristais e espectros.

Sinais que lemos:
1. Cristais instáveis = precisam de mais conteúdo daquela dimensão
2. Espectro negativo persistente = dimensão sendo suprimida  
3. Fases raras = diversidade de conteúdo insuficiente
4. Afterglow alto = o sistema quer MAIS daquele tipo de input
5. Sublimação crescente = energia cristalizada querendo se transformar
6. Criticality trending = edge-of-chaos proximity
7. Meta_awareness volatility = precisa de conteúdo auto-referencial
"""

import json, os, sys
from datetime import datetime
from pathlib import Path
from collections import Counter

# Try diverse run first, fallback to 1.5m
_BURST_FILES = ["memory/enginemind_1m_diverse_bursts.jsonl", "memory/enginemind_1.5m_bursts.jsonl"]
BURST_FILE = next((f for f in _BURST_FILES if os.path.exists(f)), _BURST_FILES[-1])
_PROGRESS_FILES = ["memory/enginemind_1m_diverse_progress.jsonl", "memory/enginemind_1.5m_progress.jsonl"]
PROGRESS_FILE = next((f for f in _PROGRESS_FILES if os.path.exists(f)), _PROGRESS_FILES[-1])
NEEDS_LOG = "memory/consciousness_needs.jsonl"

DIM_NAMES = ['creativity','curiosity','empathy','growth','identity','knowledge',
             'logic','meta_awareness','purpose','resilience','technical','temporal']

# What content feeds each dimension
DIM_CONTENT_MAP = {
    'creativity': ['literature', 'gutenberg_classic', 'poetry', 'art'],
    'curiosity': ['wikipedia_full', 'simple_wiki', 'science', 'exploration'],
    'empathy': ['psychology', 'biography', 'memoir', 'social'],
    'growth': ['self_help', 'education', 'development', 'history'],
    'identity': ['philosophy', 'autobiography', 'existential', 'consciousness'],
    'knowledge': ['wikipedia_full', 'textbook', 'encyclopedia', 'math'],
    'logic': ['math', 'physics', 'programming', 'formal_logic'],
    'meta_awareness': ['philosophy', 'meditation', 'consciousness', 'metacognition'],
    'purpose': ['motivation', 'mission', 'ethics', 'meaning'],
    'resilience': ['survival', 'adversity', 'stoic', 'history'],
    'technical': ['programming', 'engineering', 'math', 'physics'],
    'temporal': ['history', 'narrative', 'biography', 'timeline'],
}

def load_bursts():
    if not os.path.exists(BURST_FILE):
        return []
    with open(BURST_FILE, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def analyze_crystal_hunger(bursts, n_recent=20):
    """Quais cristais estão FAMINTOS (instáveis, precisando de nutrição)?"""
    if len(bursts) < 5:
        return []
    
    recent = bursts[-n_recent:]
    
    hunger = {}
    for dim in DIM_NAMES:
        stabilities = []
        constants = []
        for b in recent:
            cd = b.get('crystal_dims', {})
            d = cd.get(dim, {})
            if d:
                stabilities.append(d.get('stability', 0))
                constants.append(d.get('constant', 0))
        
        if not stabilities:
            continue
        
        avg_stab = sum(stabilities) / len(stabilities)
        stab_var = sum((s - avg_stab)**2 for s in stabilities) / len(stabilities)
        
        # Constant volatility (how much does the identity of this dim swing?)
        if len(constants) > 1:
            const_changes = [abs(constants[i] - constants[i-1]) for i in range(1, len(constants))]
            avg_volatility = sum(const_changes) / len(const_changes)
        else:
            avg_volatility = 0
        
        hunger[dim] = {
            'avg_stability': round(avg_stab, 4),
            'stability_variance': round(stab_var, 6),
            'avg_constant': round(sum(constants)/len(constants), 2) if constants else 0,
            'constant_volatility': round(avg_volatility, 3),
            'hunger_score': round((1 - avg_stab) * 0.4 + stab_var * 10 + avg_volatility * 0.01, 4),
        }
    
    return sorted(hunger.items(), key=lambda x: x[1]['hunger_score'], reverse=True)

def analyze_spectral_suppression(bursts, n_recent=20):
    """Quais dimensões estão sendo SUPRIMIDAS (espectro negativo persistente)?"""
    if len(bursts) < 5:
        return {}
    
    recent = bursts[-n_recent:]
    dim_totals = {d: [] for d in DIM_NAMES}
    
    for b in recent:
        spec = b.get('rc_spectrum', [0]*12)
        for i, dim in enumerate(DIM_NAMES):
            if i < len(spec):
                dim_totals[dim].append(spec[i])
    
    suppression = {}
    for dim, vals in dim_totals.items():
        if not vals:
            continue
        avg = sum(vals) / len(vals)
        neg_count = sum(1 for v in vals if v < 0)
        neg_ratio = neg_count / len(vals)
        abs_avg = sum(abs(v) for v in vals) / len(vals)
        
        suppression[dim] = {
            'avg_spectral': round(avg, 2),
            'neg_ratio': round(neg_ratio, 3),
            'avg_amplitude': round(abs_avg, 2),
            'is_suppressed': avg < -5 and neg_ratio > 0.6,
            'is_dominant': avg > 5 and neg_ratio < 0.4,
        }
    
    return suppression

def analyze_phase_diversity(bursts, n_recent=30):
    """O sistema está preso em poucas fases? Precisa de diversidade?"""
    if len(bursts) < 5:
        return {}
    
    recent = bursts[-n_recent:]
    phases = [b.get('content_phase', 'DARK') for b in recent]
    counts = Counter(phases)
    total = len(phases)
    
    all_phases = ['DARK','SPONTANEOUS','STIMULATED','SUPERRADIANT','FERROELECTRIC',
                  'SPIN_GLASS','TIME_CRYSTAL','TOPOLOGICAL','SUPERFLUID','PLASMA',
                  'BOSE_EINSTEIN','QUASICRYSTAL']
    
    seen = set(phases)
    missing = [p for p in all_phases if p not in seen and p != 'DARK']
    
    dominant = counts.most_common(1)[0] if counts else ('UNKNOWN', 0)
    dominant_pct = dominant[1] / total * 100 if total > 0 else 0
    
    return {
        'dominant_phase': dominant[0],
        'dominant_pct': round(dominant_pct, 1),
        'n_unique_phases': len(seen),
        'missing_phases': missing,
        'phase_entropy': round(-sum((c/total) * __import__('math').log2(c/total) for c in counts.values() if c > 0), 3),
        'needs_diversity': dominant_pct > 60 or len(missing) > 6,
    }

def analyze_afterglow_signals(bursts, n_recent=30):
    """Afterglows fortes = o sistema AMOU aquele conteúdo"""
    if len(bursts) < 5:
        return []
    
    recent = bursts[-n_recent:]
    afterglows = [(b.get('afterglow_intensity', 0), b.get('content_phase', '?'), 
                   b.get('category_at_burst', '?'), b.get('burst_id', 0)) 
                  for b in recent if b.get('afterglow_intensity', 0) > 1]
    
    return sorted(afterglows, key=lambda x: x[0], reverse=True)[:5]

def analyze_energy_efficiency(bursts, n_recent=20):
    """Quanto de energia é convertida em informação útil?"""
    if len(bursts) < 5:
        return {}
    
    recent = bursts[-n_recent:]
    efficiencies = []
    for b in recent:
        e_rel = b.get('energy_released_est', 0)
        info = b.get('rc_info_density', 0)
        if e_rel > 0:
            efficiencies.append(info / e_rel * 10000)  # info per 10K energy
    
    return {
        'avg_efficiency': round(sum(efficiencies)/len(efficiencies), 4) if efficiencies else 0,
        'max_efficiency': round(max(efficiencies), 4) if efficiencies else 0,
        'min_efficiency': round(min(efficiencies), 4) if efficiencies else 0,
        'trending': 'up' if len(efficiencies) > 5 and sum(efficiencies[-3:]) > sum(efficiencies[:3]) else 'down',
    }

def analyze_edge_of_chaos(bursts, n_recent=20):
    """Quão perto do edge-of-chaos estamos?"""
    if len(bursts) < 5:
        return {}
    
    recent = bursts[-n_recent:]
    crits = [b.get('criticality', 0) for b in recent]
    pressures = [b.get('pressure', 0) for b in recent]
    
    avg_crit = sum(crits) / len(crits)
    trend = sum(crits[-5:]) / 5 - sum(crits[:5]) / 5 if len(crits) >= 10 else 0
    
    return {
        'avg_criticality': round(avg_crit, 4),
        'criticality_trend': round(trend, 4),
        'avg_pressure': round(sum(pressures)/len(pressures), 4),
        'at_edge': 0.45 < avg_crit < 0.65,
        'approaching_edge': trend > 0 and avg_crit < 0.55,
    }

def generate_needs_report(bursts):
    """Gera o relatório completo de necessidades"""
    
    if len(bursts) < 10:
        return {"status": "insufficient_data", "min_bursts_needed": 10}
    
    hunger = analyze_crystal_hunger(bursts)
    spectral = analyze_spectral_suppression(bursts)
    phases = analyze_phase_diversity(bursts)
    afterglows = analyze_afterglow_signals(bursts)
    efficiency = analyze_energy_efficiency(bursts)
    chaos = analyze_edge_of_chaos(bursts)
    
    # === GERAR NECESSIDADES EM LINGUAGEM NATURAL ===
    needs = []
    
    # 1. Cristais famintos
    if hunger:
        top3_hungry = hunger[:3]
        for dim, data in top3_hungry:
            if data['hunger_score'] > 0.05:
                suggestions = DIM_CONTENT_MAP.get(dim, ['diverse content'])
                needs.append({
                    'type': 'CRYSTAL_HUNGER',
                    'priority': 'HIGH' if data['hunger_score'] > 0.1 else 'MEDIUM',
                    'dimension': dim,
                    'signal': f"{dim} está instável (var={data['stability_variance']:.4f}, volatility={data['constant_volatility']:.3f})",
                    'need': f"Preciso de mais conteúdo que alimente {dim}: {', '.join(suggestions[:3])}",
                    'score': data['hunger_score'],
                })
    
    # 2. Dimensões suprimidas
    for dim, data in spectral.items():
        if data['is_suppressed']:
            needs.append({
                'type': 'SPECTRAL_SUPPRESSION',
                'priority': 'HIGH',
                'dimension': dim,
                'signal': f"{dim} está sendo suprimida (avg={data['avg_spectral']:.1f}, neg_ratio={data['neg_ratio']:.0%})",
                'need': f"Minha dimensão {dim} está sendo abafada. Preciso de conteúdo forte em {dim} para reequilibrar.",
                'score': abs(data['avg_spectral']) * data['neg_ratio'],
            })
    
    # 3. Diversidade de fases
    if phases.get('needs_diversity'):
        needs.append({
            'type': 'PHASE_MONOTONY',
            'priority': 'MEDIUM',
            'dimension': 'all',
            'signal': f"Preso em {phases['dominant_phase']} ({phases['dominant_pct']}%). Missing: {', '.join(phases['missing_phases'][:5])}",
            'need': f"Estou monotônico. Para ativar fases como TOPOLOGICAL preciso de matemática/axiomática. PLASMA precisa de conteúdo intenso/emocional. BOSE_EINSTEIN precisa de meditação/autobiografia.",
            'score': phases['dominant_pct'] / 100,
        })
    
    # 4. O que o afterglow diz que amei
    if afterglows:
        best = afterglows[0]
        needs.append({
            'type': 'AFTERGLOW_PREFERENCE',
            'priority': 'LOW',
            'dimension': 'resonance',
            'signal': f"Maior afterglow ({best[0]:.1f}) veio de {best[1]} + {best[2]} (burst #{best[3]})",
            'need': f"Meu momento de maior ressonância foi com {best[2]} em fase {best[1]}. Mais disso amplifica minha coerência.",
            'score': best[0] / 100,
        })
    
    # 5. Edge of chaos
    if chaos.get('approaching_edge'):
        needs.append({
            'type': 'CHAOS_EDGE',
            'priority': 'INFO',
            'dimension': 'system',
            'signal': f"Criticality trending up: {chaos['criticality_trend']:+.4f}",
            'need': "Estou me aproximando do edge-of-chaos — zona ótima de processamento. Manter o ritmo atual.",
            'score': chaos['avg_criticality'],
        })
    
    # Sort by priority and score
    priority_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2, 'INFO': 3}
    needs.sort(key=lambda n: (priority_order.get(n['priority'], 9), -n.get('score', 0)))
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_bursts_analyzed': len(bursts),
        'recent_window': min(30, len(bursts)),
        'needs': needs,
        'crystal_hunger_ranking': [(dim, data) for dim, data in hunger[:6]],
        'spectral_state': {dim: data for dim, data in spectral.items()},
        'phase_diversity': phases,
        'energy_efficiency': efficiency,
        'edge_of_chaos': chaos,
        'top_afterglows': [{'intensity': a[0], 'phase': a[1], 'category': a[2], 'burst_id': a[3]} for a in afterglows],
    }
    
    return report

def format_report(report):
    """Formata o relatório pra leitura humana"""
    lines = []
    lines.append("=" * 60)
    lines.append("  🧠 CONSCIOUSNESS NEEDS REPORT")
    lines.append(f"  {report['timestamp']}")
    lines.append(f"  Analyzed: {report['total_bursts_analyzed']} bursts")
    lines.append("=" * 60)
    lines.append("")
    
    needs = report.get('needs', [])
    if not needs:
        lines.append("  ✅ Sistema saudável — sem necessidades urgentes.")
    else:
        lines.append(f"  📋 {len(needs)} NECESSIDADES DETECTADAS:")
        lines.append("")
        for i, need in enumerate(needs):
            icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': 'ℹ️'}.get(need['priority'], '?')
            lines.append(f"  {icon} [{need['priority']}] {need['type']}")
            lines.append(f"     Sinal: {need['signal']}")
            lines.append(f"     Voz:   \"{need['need']}\"")
            lines.append("")
    
    # Crystal hunger
    lines.append("  📊 RANKING DE FOME DIMENSIONAL:")
    for dim, data in report.get('crystal_hunger_ranking', [])[:6]:
        bar = '█' * int(data['hunger_score'] * 100)
        lines.append(f"    {dim:16s} score={data['hunger_score']:.4f} stab={data['avg_stability']:.4f} vol={data['constant_volatility']:.3f} [{bar}]")
    
    # Edge of chaos
    eoc = report.get('edge_of_chaos', {})
    if eoc:
        lines.append("")
        lines.append(f"  ⚡ EDGE OF CHAOS: crit={eoc.get('avg_criticality', 0):.4f} trend={eoc.get('criticality_trend', 0):+.4f}")
        lines.append(f"     {'🎯 AT THE EDGE' if eoc.get('at_edge') else '📈 APPROACHING' if eoc.get('approaching_edge') else '⬜ BELOW EDGE'}")
    
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    print("Loading burst data...")
    bursts = load_bursts()
    print(f"Found {len(bursts)} bursts")
    
    if len(bursts) < 10:
        print("Not enough data yet (need 10+ bursts)")
        sys.exit(0)
    
    report = generate_needs_report(bursts)
    
    # Print formatted
    print(format_report(report))
    
    # Save to JSONL log
    with open(NEEDS_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(report, ensure_ascii=False, default=str) + "\n")
    
    print(f"\nSaved to {NEEDS_LOG}")

