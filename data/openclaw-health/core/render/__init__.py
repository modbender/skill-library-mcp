from typing import Any, Dict, Optional


def _fmt_maybe(value, suffix: str = "") -> str:
    return f"{value}{suffix}" if value is not None else "-"


def _round_maybe(value: Any, ndigits: int) -> Optional[float]:
    if isinstance(value, (int, float)):
        return round(float(value), ndigits)
    return None


def _fmt_sleep_duration(total_seconds: Any) -> str:
    if not isinstance(total_seconds, (int, float)):
        return "-"
    sec = int(total_seconds)
    h = sec // 3600
    m = (sec % 3600) // 60
    return f"{h}h{m:02d}m"


def to_markdown(norm: Dict[str, Any]) -> str:
    m = norm.get("metrics", {})
    sleep = m.get("sleep", {})
    lines = []
    lines.append(f"### Daily Health – {norm.get('date')}")
    lines.append("")

    # Sleep
    lines.append(f"- Sleep: {_fmt_sleep_duration(sleep.get('total_seconds'))} (score {_fmt_maybe(sleep.get('score'))})")

    # Readiness
    lines.append(f"- Readiness: {_fmt_maybe(m.get('readiness', {}).get('score'))}")

    # Activity
    act = m.get("activity", {})
    lines.append(
        f"- Activity: steps {_fmt_maybe(act.get('steps'))}, calories {_fmt_maybe(act.get('calories'))}, minutes {_fmt_maybe(act.get('minutes'))}"
    )

    # Biometrics (rounded)
    lines.append(f"- Resting HR: {_fmt_maybe(m.get('resting_hr'), ' bpm')}")
    lines.append(f"- HRV (RMSSD): {_fmt_maybe(_round_maybe(m.get('hrv_rmssd'), 1), ' ms')}")
    lines.append(f"- Respiratory Rate: {_fmt_maybe(_round_maybe(m.get('respiratory_rate'), 1), ' bpm')}")
    lines.append(f"- SpO2: {_fmt_maybe(_round_maybe(m.get('spo2'), 1), '%')}")

    # Body
    wkg = m.get("weight_kg")
    if isinstance(wkg, (int, float)):
        wlb = round(float(wkg) * 2.2046226218, 1)
        lines.append(f"- Weight: {wlb} lb ({round(float(wkg), 2)} kg)")
    else:
        lines.append(f"- Weight: {_fmt_maybe(wkg, ' kg')}")
    lines.append(f"- Body Fat: {_fmt_maybe(_round_maybe(m.get('body_fat_percent'), 1), '%')}")

    lines.append("")

    # Sources summary
    srcs = ", ".join(sorted(norm.get("sources", {}).keys())) or "-"
    lines.append(f"_sources: {srcs}_")
    return "\n".join(lines)

