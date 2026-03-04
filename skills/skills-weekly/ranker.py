"""
ranker.py — Trending Velocity Calculator (v5)

Two-track ranking system:
  MOVERS   — established skills ranked by installs_all_time delta (cumulative growth)
  ROCKETS  — new skills (<30 days) ranked by growth + velocity with recency bonus

Uses installs_all_time (monotonically increasing counter) instead of
installs_current (gauge that oscillates near zero for established skills).

Cold-start handling: when only 1 snapshot exists, uses age-normalized proxy
(average daily rate * 7) instead of raw cumulative totals. This prevents
the rankings from being a popularity contest and reduces day-2 cliff.
"""

import storage
from datetime import datetime, timezone, timedelta


# --- MOVER scoring weights ---
W_IAT_DELTA = 0.35       # installs_all_time delta (primary trending signal)
W_DOWNLOADS_DELTA = 0.15  # Download growth (secondary)
W_PCT_INCREASE = 0.25     # Relative velocity (breakout detection)
W_STARS = 0.15            # Stars as quality signal
W_STARS_DELTA = 0.10      # Star growth (community momentum)

# Normalisation caps (calibrated for weekly deltas, not cumulative)
MAX_IAT_DELTA = 500       # installs_all_time weekly growth
MAX_DOWNLOADS_DELTA = 5000
MAX_PCT = 200.0
MAX_STARS = 1000
MAX_STARS_DELTA = 50

# Author diversity: max entries per author in top N
MAX_PER_AUTHOR = 3


def _skill_age_days(skill: dict) -> int:
    """Return skill age in days from created_at, or 365 if unknown."""
    created_ms = skill.get("created_at", 0)
    if not created_ms:
        return 365
    created = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
    return max((datetime.now(timezone.utc) - created).days, 1)


def _mover_score(vel: dict, stars: int) -> float:
    """Composite score for established skills (30+ days old)."""
    iat_delta = vel.get("installs_all_time_delta", vel.get("installs_delta", 0))
    iat_norm = min(max(iat_delta, 0), MAX_IAT_DELTA) / MAX_IAT_DELTA
    dl_norm = min(max(vel["downloads_delta"], 0), MAX_DOWNLOADS_DELTA) / MAX_DOWNLOADS_DELTA
    pct = vel.get("pct_increase", 0.0)
    pct_norm = min(max(pct, 0), MAX_PCT) / MAX_PCT if pct >= 0 else 0.0
    stars_norm = min(stars, MAX_STARS) / MAX_STARS
    stars_d_norm = min(max(vel.get("stars_delta", 0), 0), MAX_STARS_DELTA) / MAX_STARS_DELTA

    return (
        W_IAT_DELTA * iat_norm
        + W_DOWNLOADS_DELTA * dl_norm
        + W_PCT_INCREASE * pct_norm
        + W_STARS * stars_norm
        + W_STARS_DELTA * stars_d_norm
    )


def _rocket_score(skill: dict, vel: dict) -> float:
    """Score for new skills (<30 days). Uses velocity when available, recency bonus applied."""
    age_days = _skill_age_days(skill)
    recency_bonus = 1 + (1 / (1 + age_days))  # day 0 = 2x, day 7 = 1.125x

    snaps = vel.get("snapshots_used", 0)

    if snaps >= 2:
        # Real velocity data available — use it
        iat_delta = vel.get("installs_all_time_delta", 0)
        dl_delta = vel.get("downloads_delta", 0)
        stars = vel.get("latest_stars", skill.get("stars", 0))
        iat_norm = min(max(iat_delta, 0), 100) / 100
        dl_norm = min(max(dl_delta, 0), 1000) / 1000
        stars_norm = min(stars, 50) / 50
    else:
        # Cold start: use age-normalized average weekly rate
        iat = skill.get("installs_all_time", skill.get("installs_current", 0))
        dl = skill.get("downloads", 0)
        stars = skill.get("stars", 0)
        weekly_rate_iat = iat / age_days * 7
        weekly_rate_dl = dl / age_days * 7
        iat_norm = min(weekly_rate_iat, 100) / 100
        dl_norm = min(weekly_rate_dl, 1000) / 1000
        stars_norm = min(stars, 50) / 50

    raw = 0.40 * iat_norm + 0.30 * dl_norm + 0.30 * stars_norm
    return raw * recency_bonus


def _is_new(skill: dict, days: int = 30) -> bool:
    """Check if skill was created within the last N days."""
    created_ms = skill.get("created_at", 0)
    if not created_ms:
        return False
    created = datetime.fromtimestamp(created_ms / 1000, tz=timezone.utc)
    return (datetime.now(timezone.utc) - created).days < days


def _apply_author_diversity(ranked: list[dict], max_per: int, total: int) -> list[dict]:
    """Cap entries per author in the top list to ensure diversity."""
    result = []
    author_count: dict[str, int] = {}
    for skill in ranked:
        if len(result) >= total:
            break
        author = (skill.get("author") or "").lower()
        if not author:
            result.append(skill)
            continue
        count = author_count.get(author, 0)
        if count < max_per:
            result.append(skill)
            author_count[author] = count + 1
    return result


def rank(skills: list[dict], db_days: int = 7, top_n: int = 10) -> list[dict]:
    """
    Rank skills by trending velocity using two-track system.

    Returns top_n MOVERS (author-diversified) plus up to 5 ROCKETS (new skills <30 days).
    """
    velocity_map = {v["slug"]: v for v in storage.get_all_velocities(days=db_days)}

    movers = []
    rockets = []

    for skill in skills:
        slug = skill["slug"]
        vel = velocity_map.get(slug, {
            "slug": slug,
            "installs_delta": 0,
            "installs_all_time_delta": 0,
            "downloads_delta": 0,
            "pct_increase": 0.0,
            "latest_installs": skill.get("installs_current", 0),
            "latest_installs_all_time": skill.get("installs_all_time", 0),
            "latest_downloads": skill.get("downloads", 0),
            "latest_stars": skill.get("stars", 0),
            "stars_delta": 0,
            "snapshots_used": 0,
        })

        snaps = vel.get("snapshots_used", 0)

        # Cold-start proxy: age-normalized weekly estimate instead of raw cumulative
        if snaps <= 1:
            age_days = _skill_age_days(skill)
            iat_raw = skill.get("installs_all_time", skill.get("installs_current", 0))
            dl_raw = skill.get("downloads", 0)
            vel["installs_all_time_delta"] = round(iat_raw / age_days * 7)
            vel["downloads_delta"] = round(dl_raw / age_days * 7)
            vel["pct_increase"] = -1.0  # sentinel: "no data"

        stars = vel.get("latest_stars", skill.get("stars", 0))

        if _is_new(skill, days=30):
            score = _rocket_score(skill, vel)
            rockets.append({
                **skill,
                "_score": round(score, 4),
                "_track": "rocket",
                "_installs_delta": vel.get("installs_all_time_delta", 0),
                "_downloads_delta": vel["downloads_delta"],
                "_stars_delta": vel.get("stars_delta", 0),
                "_pct_increase": vel["pct_increase"],
                "_snapshots_used": snaps,
                "_cold_start": snaps <= 1,
            })
        else:
            score = _mover_score(vel, stars)
            movers.append({
                **skill,
                "_score": round(score, 4),
                "_track": "mover",
                "_installs_delta": vel.get("installs_all_time_delta", 0),
                "_downloads_delta": vel["downloads_delta"],
                "_stars_delta": vel.get("stars_delta", 0),
                "_pct_increase": vel["pct_increase"],
                "_snapshots_used": snaps,
                "_cold_start": snaps <= 1,
            })

    movers.sort(key=lambda s: s["_score"], reverse=True)
    rockets.sort(key=lambda s: s["_score"], reverse=True)

    # Author diversity: prevent one author from dominating the list
    top_movers = _apply_author_diversity(movers, MAX_PER_AUTHOR, top_n)
    top_rockets = rockets[:5]

    def _safe(text: str) -> str:
        return text.encode("ascii", errors="replace").decode("ascii")

    print(f"[RANKER] {len(movers)} movers, {len(rockets)} rockets")
    print(f"[RANKER] Top {len(top_movers)} movers:")
    for i, s in enumerate(top_movers, 1):
        hist = f"({s['_snapshots_used']}d)" if s["_snapshots_used"] > 1 else "(est)"
        print(
            f"  #{i} {_safe(s['display_name'])} score={s['_score']} "
            f"iat_delta=+{s['_installs_delta']} dl_delta=+{s['_downloads_delta']} "
            f"stars={s.get('stars', 0)} {hist}"
        )

    if top_rockets:
        print(f"[RANKER] Top {len(top_rockets)} rockets (new <30d):")
        for i, s in enumerate(top_rockets, 1):
            age = "new"
            if s.get("created_at"):
                age_d = (datetime.now(timezone.utc) - datetime.fromtimestamp(s["created_at"] / 1000, tz=timezone.utc)).days
                age = f"{age_d}d old"
            print(f"  #{i} {_safe(s['display_name'])} score={s['_score']} {age}")

    return top_movers, top_rockets
