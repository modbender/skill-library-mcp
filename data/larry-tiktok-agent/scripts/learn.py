#!/usr/bin/env python3
"""
Larry — Self-Learning Loop
Analysiert Performance-Daten und optimiert Hook-Formeln.
Läuft täglich nach dem Stats-Check.
"""
import json
from pathlib import Path
from collections import defaultdict

LARRY_DIR = Path(__file__).parent.parent

def analyze_and_learn():
    """Analysiert Performance und gibt Learnings aus"""
    log_file = LARRY_DIR / "logs" / "performance.json"
    if not log_file.exists():
        print("Noch keine Performance-Daten vorhanden.")
        return

    with open(log_file) as f:
        posts = json.load(f)

    if len(posts) < 3:
        print(f"Erst {len(posts)} Posts — brauche mehr Daten für Learnings.")
        return

    # Hooks nach Views sortieren
    posts_with_views = [p for p in posts if p.get("views", 0) > 0]
    if not posts_with_views:
        print("Noch keine Views-Daten.")
        return

    posts_with_views.sort(key=lambda x: x.get("views", 0), reverse=True)

    print("\n📊 LARRY'S LEARNINGS\n" + "="*40)

    # Top-Performer
    print("\n🏆 TOP HOOKS (nach Views):")
    for i, p in enumerate(posts_with_views[:5], 1):
        print(f"  {i}. {p['hook'][:60]}")
        print(f"     👁 {p['views']:,} | ❤️ {p['likes']:,} | 💬 {p['comments']:,} | 🔄 {p['shares']:,}")

    # Flops
    flops = sorted(posts_with_views, key=lambda x: x.get("views", 0))[:3]
    print("\n❌ FLOPS (vermeiden):")
    for p in flops:
        print(f"  - {p['hook'][:60]} ({p['views']:,} Views)")

    # Hook-Muster-Analyse
    print("\n🔍 HOOK-MUSTER:")
    patterns = defaultdict(list)
    for p in posts_with_views:
        hook = p["hook"].lower()
        if "fehler" in hook or "mistake" in hook:
            patterns["fehler-hooks"].append(p["views"])
        elif hook.startswith("die ") or hook.startswith("das "):
            patterns["die/das-hooks"].append(p["views"])
        elif "warum" in hook or "wieso" in hook:
            patterns["warum-hooks"].append(p["views"])
        elif "?" in hook:
            patterns["frage-hooks"].append(p["views"])
        else:
            patterns["andere"].append(p["views"])

    for pattern, views_list in sorted(patterns.items(), key=lambda x: sum(x[1])/len(x[1]), reverse=True):
        avg = sum(views_list) / len(views_list)
        print(f"  {pattern}: Ø {avg:,.0f} Views ({len(views_list)} Posts)")

    # Empfehlung
    best_pattern = max(patterns.items(), key=lambda x: sum(x[1])/len(x[1]) if x[1] else 0)
    print(f"\n💡 EMPFEHLUNG: Mehr '{best_pattern[0]}' verwenden!")

    # Savings report
    print(f"\n📈 GESAMT: {len(posts)} Posts | {sum(p.get('views',0) for p in posts):,} Views total")

    return {
        "top_hooks": [p["hook"] for p in posts_with_views[:3]],
        "avoid_hooks": [p["hook"] for p in flops],
        "best_pattern": best_pattern[0]
    }

if __name__ == "__main__":
    analyze_and_learn()
