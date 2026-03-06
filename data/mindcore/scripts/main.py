"""
main.py — Biomimetic Mind Engine — Entry Point
Phase 1 MVP: Complete five-layer pipeline demo

Usage:
    python3 main.py
"""

import time
import json
import numpy as np
from datetime import datetime
from engine.engine_loop import MindEngine
from engine.config import TOTAL_LAYER0_NODES, SENSOR_STATE_PATH, SHORT_TERM_MEMORY_PATH


def print_header():
    print()
    print("=" * 70)
    print("  🧠 Biomimetic Mind Engine — Live Five-Layer Pipeline Demo")
    print("  Biomimetic Mind Engine — Full 5-Layer Pipeline Demo")
    print("=" * 70)
    print()


def print_tick(result: dict):
    """格式化打印每个 tick 的Status。"""
    t = result["tick"]
    ts = result["timestamp"][:19]
    l0 = result["layer0"]
    l1 = result["layer1"]
    l2 = result["layer2"]
    l3 = result["layer3"]
    l4 = result["layer4"]

    # Separator
    print(f"{'─' * 70}")
    print(f"  ⏱  Tick {t:03d} | {ts} | 🌙 Circadian: {l0['circadian']:.3f}")

    # Layer 1
    if l1["active_count"] > 0:
        sensors_str = ", ".join([f"{s[0]}={s[1]}" for s in l1["active_sensors"]])
        print(f"  📡 L1 Sensors | {l1['active_count']} active | {sensors_str}")
        print(f"  💭 Mood    | mood_valence = {l1['mood_valence']:+.4f}")
    else:
        print(f"  📡 L1 Sensors | 静默 (无active)")

    # Layer 2
    if l2["fired_count"] > 0:
        impulse_str = ", ".join(l2["fired"][:3])
        print(f"  ⚡ L2 Impulses | {l2['fired_count']} fired | {impulse_str}")
    else:
        membrane = l2["membrane"]
        print(f"  ⚡ L2 Impulses | Silent | Max membrane potential: {membrane['max_potential']:.3f} | near threshold: {membrane['num_near_threshold']}")

    # Layer 3
    if l3["winner_count"] > 0:
        winner_str = " + ".join(l3["winners"])
        print(f"  🧬 L3 Personality | Winners: {winner_str} (从 {l3['candidates']} candidates)")
    else:
        print(f"  🧬 L3 Personality | No impulses passed gate")

    # Layer 4
    if l4.get("should_speak"):
        intensity = l4["intensity_level"]["level_name"]
        primary = l4["impulses"][0]["name"] if l4["impulses"] else "?"
        print(f"  📢 L4 Output | ⚠️  Action! | Intensity: {intensity.upper()} | Impulse: {primary}")
        if l4.get("system_prompt_injection"):
            # Only print first two lines
            lines = l4["system_prompt_injection"].split("\n")[:3]
            for line in lines:
                print(f"  │ {line}")
    else:
        print(f"  📢 L4 Output | 😶 Silent (nothing to say)")


def on_speak(output: dict):
    """Callback when AI decides to speak."""
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║  🗣️  AI decided to speak!                         ║")
    intensity = output["intensity_level"]["level_name"]
    name = output["impulses"][0]["name"] if output["impulses"] else "?"
    print(f"  ║  Impulse: {name:<35s}  ║")
    print(f"  ║  Intensity: {intensity:<35s}  ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()


def main():
    print_header()

    # ── Scenario Setup：模拟"深夜 + 缺觉 + neglected3 hours" ──
    print("[📝 Scenario Setup]")
    print("  active传感器: sleep_deprived=1, late_night=1, eye_fatigue=1")
    print("  社交Status:   last_interaction_time = 3 hours前")
    print("  Mood底色:   mood_valence = -0.4 (轻度负面)")
    print()

    # Modify Sensor_State.json
    with open(SENSOR_STATE_PATH, "r", encoding="utf-8") as f:
        sensor = json.load(f)
    sensor["body"]["sleep_deprived"] = 1
    sensor["body"]["eye_fatigue"] = 1
    sensor["environment"]["late_night"] = 1
    sensor["social"]["last_interaction_time"] = time.time() - 3 * 3600
    with open(SENSOR_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(sensor, f, ensure_ascii=False, indent=4)

    # Modify ShortTermMemory.json
    with open(SHORT_TERM_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "mood_valence": -0.4,
            "unresolved_events": [
                {"type": "neglected", "time": time.time() - 3600, "is_unresolved": True}
            ]
        }, f, ensure_ascii=False, indent=2)

    # ── Initialize engine ──
    engine = MindEngine(enable_circadian=True, save_outputs=True)

    # ── Run 20 ticks ──
    num_ticks = 20
    print(f"[🚀 Start] 运行 {num_ticks} ticks (每 tick 0.5s Accelerated demo)\n")

    spoke_ticks = []

    for i in range(num_ticks):
        result = engine.tick()
        print_tick(result)

        if result["layer4"].get("should_speak"):
            on_speak(result["layer4"])
            spoke_ticks.append(result["tick"])

        time.sleep(0.5)  # Accelerated demo

    # ── Summary ──
    print()
    print("=" * 70)
    summary = engine.get_summary()
    print(f"  ✅ Demo complete")
    print(f"  📊 Total ticks: {summary['total_ticks']}")
    print(f"  ⚡ 总Impulsefired: {summary['total_impulse_fires']}")
    print(f"  🗣️  Times spoke: {len(spoke_ticks)}")
    if spoke_ticks:
        print(f"  📢 Spoke at ticks: {spoke_ticks}")
    print(f"  🧬 Personality profile: {summary['personality_profile']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
