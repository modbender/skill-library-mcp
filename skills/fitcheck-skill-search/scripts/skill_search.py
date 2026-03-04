#!/usr/bin/env python3
"""Skill Search V1.1 - Advanced skill discovery."""
import os, re, sys, json, argparse
from pathlib import Path
from typing import List, Tuple, Dict

sys.path.insert(0, str(Path(__file__).parent))
from embeddings import index_all_skills, load_index, semantic_search, INDEX_DIR

SKILL_DIRS = [
    "/usr/local/lib/node_modules/openclaw/skills",
    os.path.expanduser("~/.openclaw/workspace/skills"),
]

def parse_skill_md(skill_path: Path) -> Tuple[str, str, str, List[str]]:
    name = skill_path.parent.name
    desc = "(no description)"
    triggers = []
    try:
        content = skill_path.read_text(encoding='utf-8', errors='ignore')
        if content.startswith('---'):
            end = re.search(r'\n---\s*\n', content[3:])
            if end:
                fm = content[3:3+end.start()]
                nm = re.search(r'^name:\s*(.+)$', fm, re.M)
                if nm: name = nm.group(1).strip().strip('"\'')
                dm = re.search(r'^description:\s*(.+?)(?=\n\w+:|\Z)', fm, re.M|re.S)
                if dm: desc = re.sub(r'\s+', ' ', dm.group(1).strip().strip('"\'').replace('\n',' '))
                tm = re.search(r'triggers?:\s*\n((?:^\s*- .+\n?)+)', fm, re.M)
                if tm:
                    triggers = [l.strip('- ').strip('"\'') for l in tm.group(1).strip().split('\n') if l.strip().startswith('-')]
    except: pass
    return name, desc, str(skill_path.parent), triggers

def find_all_skills() -> List[Tuple[str, str, str, List[str]]]:
    skills, seen = [], set()
    for sd in SKILL_DIRS:
        if not os.path.isdir(sd): continue
        for it in sorted(os.listdir(sd)):
            if it.startswith('.'): continue
            sp = Path(sd) / it / "SKILL.md"
            if sp.exists() and it not in seen:
                seen.add(it)
                skills.append(parse_skill_md(sp) + (it,))
    return sorted(skills, key=lambda x: x[0].lower())

def keyword_search(query: str, top_k: int = 10) -> List[Tuple]:
    ql = query.lower()
    qw = set(ql.split())
    results = []
    for name, desc, loc, triggers, folder in find_all_skills():
        nl, dl, tl = name.lower(), desc.lower(), ' '.join(triggers).lower()
        score, matched = 0, []
        if ql == nl: score, matched = 20, ['exact']
        elif ql in nl: score, matched = 10, ['name']
        for w in qw:
            if w in nl: score += 5
            if w in dl: score += 2
            if w in tl: score += 3
        if score > 0: results.append((name, desc, folder, loc, triggers, score, matched))
    results.sort(key=lambda x: (-x[5], x[0].lower()))
    return results[:top_k]

def hybrid_search(query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
    kw = {r[0]: r[5] for r in keyword_search(query, 20)}
    sem = semantic_search(query, 20)
    sm = {s.get('name'): sim for s, sim in sem}
    all_skills = load_index()
    if not all_skills: return sem[:top_k]
    km = max(kw.values()) if kw else 1
    combined = []
    for sk in all_skills:
        name = sk.get('name', '')
        ks = kw.get(name, 0) / km if km > 0 else 0
        ss = sm.get(name, 0)
        cs = (ks * 0.5) + (ss * 0.5)
        if cs > 0.1: combined.append((sk, cs))
    combined.sort(key=lambda x: x[1], reverse=True)
    return combined[:top_k]

def task_match(query: str) -> str:
    if not load_index(): index_all_skills()
    r = hybrid_search(query, 5)
    if not r: return "No skills found."
    lines = [f"Recommended for '{query}':\n"]
    for i, (sk, sc) in enumerate(r, 1):
        name = sk.get('name', 'Unknown')
        desc = sk.get('description', '')[:80]
        trig = sk.get('triggers', [])
        conf = "High" if sc >= 0.7 else "Medium" if sc >= 0.4 else "Low"
        lines.append(f"{i}. {name}")
        lines.append(f"   {desc}{'...' if len(desc) >= 80 else ''}")
        if trig: lines.append(f"   Triggers: {', '.join(trig[:3])}")
        lines.append(f"   Confidence: {conf} ({sc:.2f})")
        lines.append("")
    return "\n".join(lines)

def list_skills(show_locs: bool = False) -> str:
    skills = find_all_skills()
    lines = [f"Skills ({len(skills)} total):\n"]
    for name, desc, loc, triggers, folder in skills:
        lines.append(f"• {name}")
        lines.append(f"  {desc[:60]}{'...' if len(desc) > 60 else ''}")
        if triggers: lines.append(f"  Triggers: {', '.join(triggers[:3])}")
        if show_locs: lines.append(f"  Location: {loc}")
        lines.append("")
    return "\n".join(lines)

def fmt_kw(results: List[Tuple]) -> str:
    if not results: return "No skills found."
    lines = []
    for i, (name, desc, folder, loc, trig, score, matched) in enumerate(results, 1):
        lines.append(f"{i}. {name} (score: {score})")
        lines.append(f"   {desc[:70]}{'...' if len(desc) > 70 else ''}")
        if trig: lines.append(f"   Triggers: {', '.join(trig[:3])}")
        lines.append("")
    return "\n".join(lines)

def fmt_sem(results: List[Tuple[Dict, float]]) -> str:
    if not results: return "No skills found."
    lines = []
    for i, (sk, sc) in enumerate(results, 1):
        lines.append(f"{i}. {sk.get('name', 'Unknown')} (sim: {sc:.3f})")
        lines.append(f"   {sk.get('description', '')[:70]}{'...'}")
        trig = sk.get('triggers', [])
        if trig: lines.append(f"   Triggers: {', '.join(trig[:3])}")
        lines.append("")
    return "\n".join(lines)

def main():
    p = argparse.ArgumentParser(description="Skill Search V1.1")
    p.add_argument('--json', action='store_true')
    sub = p.add_subparsers(dest='cmd')
    
    sub.add_parser('index', help='Build index')
    lg = sub.add_parser('list', help='List skills')
    lg.add_argument('--location', action='store_true')
    
    kw = sub.add_parser('keyword', help='Keyword search')
    kw.add_argument('query', nargs='+')
    kw.add_argument('-k', type=int, default=10)
    
    sm = sub.add_parser('semantic', help='Semantic search')
    sm.add_argument('query', nargs='+')
    sm.add_argument('-k', type=int, default=5)
    
    hb = sub.add_parser('hybrid', help='Hybrid search')
    hb.add_argument('query', nargs='+')
    hb.add_argument('-k', type=int, default=5)
    
    sg = sub.add_parser('suggest', help='AI task matching')
    sg.add_argument('query', nargs='+')
    
    a = p.parse_args()
    if not a.cmd:
        p.print_help()
        return
    
    if a.cmd == 'index':
        r = index_all_skills()
        print(f"Indexed {r['count']} skills")
    elif a.cmd == 'list':
        print(list_skills(a.location))
    elif a.cmd == 'keyword':
        print(fmt_kw(keyword_search(' '.join(a.query), a.k)))
    elif a.cmd == 'semantic':
        if not load_index():
            print("Building index...")
            index_all_skills()
        print(fmt_sem(semantic_search(' '.join(a.query), a.k)))
    elif a.cmd == 'hybrid':
        print(task_match(' '.join(a.query)))
    elif a.cmd == 'suggest':
        print(task_match(' '.join(a.query)))

if __name__ == '__main__':
    main()
