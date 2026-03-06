#!/usr/bin/env python3
"""🧠 Intrusive Thoughts Dashboard — what Ember does when you're not looking."""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime
from collections import Counter
from pathlib import Path
from config import get_file_path, get_data_dir, get_dashboard_port, get_agent_name, get_agent_emoji

PORT = get_dashboard_port()
HISTORY_FILE = get_file_path("history.json")
THOUGHTS_FILE = get_file_path("thoughts.json")
PICKS_LOG = get_data_dir() / "log" / "picks.log"


def load_history():
    try:
        return json.loads(HISTORY_FILE.read_text())
    except:
        return []


def load_picks():
    try:
        lines = [l.strip() for l in PICKS_LOG.read_text().splitlines() if l.strip()]
        picks = []
        for line in lines:
            parts = line.split(" | ")
            ts = parts[0] if parts else ""
            meta = dict(p.split("=", 1) for p in parts[1:] if "=" in p)
            picks.append({"timestamp": ts, **meta})
        return picks
    except:
        return []


def load_thoughts():
    try:
        return json.loads(THOUGHTS_FILE.read_text())
    except:
        return {}

def load_mood_history():
    try:
        data = json.loads(get_file_path("mood_history.json").read_text())
        return data.get("history", [])
    except:
        return []

def load_streaks():
    try:
        return json.loads(get_file_path("streaks.json").read_text())
    except:
        return {"current_streaks": {}}

def load_achievements():
    try:
        return json.loads(get_file_path("achievements_earned.json").read_text())
    except:
        return {"earned": [], "total_points": 0}

def load_soundtracks():
    try:
        return json.loads(get_file_path("soundtracks.json").read_text())
    except:
        return {}

def load_today_mood():
    try:
        return json.loads(get_file_path("today_mood.json").read_text())
    except:
        return {}

def load_journal_entries():
    try:
        journal_dir = get_data_dir() / "journal"
        entries = []
        if journal_dir.exists():
            for file in journal_dir.glob("*.md"):
                entries.append({
                    "date": file.stem,
                    "content": file.read_text()[:300] + "..." if len(file.read_text()) > 300 else file.read_text()
                })
        return sorted(entries, key=lambda x: x["date"], reverse=True)[:5]
    except:
        return []

def get_productivity_stats():
    try:
        import subprocess
        result = subprocess.run(['python3', str(get_data_dir() / 'analyze.py'), '--json'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return json.loads(result.stdout)
    except:
        pass
    return {"insights": [], "moods": {}}

def build_html():
    history = load_history()
    picks = load_picks()
    thoughts = load_thoughts()
    mood_history = load_mood_history()
    streaks = load_streaks()
    achievements = load_achievements()
    soundtracks = load_soundtracks()
    today_mood = load_today_mood()
    journal_entries = load_journal_entries()
    productivity_stats = get_productivity_stats()

    # Stats
    thought_counts = Counter(p.get("thought", "?") for p in picks)
    mood_counts = Counter(p.get("mood", "?") for p in picks)
    total_picks = len(picks)
    total_completed = len(history)

    # Top thoughts chart data
    top_thoughts = thought_counts.most_common(15)

    # Recent history
    recent = history[-20:][::-1]

    # Build thought catalog
    all_thoughts = []
    for mood_name, mood_data in thoughts.get("moods", {}).items():
        for t in mood_data.get("thoughts", []):
            all_thoughts.append({
                "id": t["id"],
                "mood": mood_name,
                "weight": t.get("weight", 1),
                "prompt": t["prompt"],
                "times_picked": thought_counts.get(t["id"], 0),
            })

    # Mood history for graph (last 14 days)
    mood_graph_data = mood_history[-14:] if mood_history else []
    
    # Current streaks
    current_streaks = streaks.get("current_streaks", {})
    
    # Recent achievements
    recent_achievements = achievements.get("earned", [])[-5:][::-1]
    
    # Today's soundtrack
    today_soundtrack = ""
    if today_mood:
        mood_id = today_mood.get("drifted_to", today_mood.get("id", ""))
        soundtrack_info = soundtracks.get("mood_soundtracks", {}).get(mood_id, {})
        if soundtrack_info:
            vibe = soundtrack_info.get("vibe_description", "")
            genres = ", ".join(soundtrack_info.get("genres", [])[:3])
            today_soundtrack = f"{vibe} — {genres}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>🧠 Intrusive Thoughts</title>
<style>
  :root {{ --bg: #0a0a0f; --card: #12121a; --border: #1e1e2e; --text: #c9c9d9; --accent: #f59e0b; --accent2: #8b5cf6; --dim: #555568; --success: #22c55e; --warning: #eab308; }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--text); font-family: 'SF Mono', 'Fira Code', monospace; padding: 2rem; max-width: 1400px; margin: 0 auto; }}
  h1 {{ color: var(--accent); font-size: 1.8rem; margin-bottom: 0.3rem; }}
  .subtitle {{ color: var(--dim); margin-bottom: 2rem; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 2rem; }}
  .stat-card {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; text-align: center; }}
  .stat-card .number {{ font-size: 2.5rem; font-weight: bold; color: var(--accent); }}
  .stat-card .label {{ color: var(--dim); font-size: 0.85rem; margin-top: 0.3rem; }}
  .section {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
  .section h2 {{ color: var(--accent2); font-size: 1.1rem; margin-bottom: 1rem; }}
  .bar-chart .bar-row {{ display: flex; align-items: center; margin-bottom: 0.5rem; }}
  .bar-chart .bar-label {{ width: 160px; font-size: 0.8rem; color: var(--dim); text-align: right; padding-right: 1rem; flex-shrink: 0; }}
  .bar-chart .bar {{ height: 22px; background: linear-gradient(90deg, var(--accent), var(--accent2)); border-radius: 4px; min-width: 4px; transition: width 0.5s; }}
  .bar-chart .bar-count {{ margin-left: 0.5rem; font-size: 0.8rem; color: var(--dim); }}
  .history-item {{ border-bottom: 1px solid var(--border); padding: 0.8rem 0; }}
  .history-item:last-child {{ border: none; }}
  .history-item .time {{ color: var(--accent); font-size: 0.75rem; }}
  .history-item .mood-tag {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 8px; font-size: 0.7rem; margin-left: 0.5rem; }}
  .mood-night {{ background: #1e1b4b; color: #a78bfa; }}
  .mood-day {{ background: #422006; color: #fbbf24; }}
  .history-item .summary {{ margin-top: 0.3rem; font-size: 0.9rem; }}
  .thought-item {{ border-bottom: 1px solid var(--border); padding: 0.8rem 0; display: flex; justify-content: space-between; align-items: start; }}
  .thought-item:last-child {{ border: none; }}
  .thought-item .prompt {{ font-size: 0.85rem; flex: 1; }}
  .thought-item .meta {{ text-align: right; flex-shrink: 0; margin-left: 1rem; font-size: 0.75rem; color: var(--dim); }}
  .empty {{ color: var(--dim); font-style: italic; text-align: center; padding: 2rem; }}
  .mood-dot {{ width: 12px; height: 12px; border-radius: 50%; margin: 0 4px; display: inline-block; }}
  .streak-item {{ background: var(--border); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; }}
  .achievement-item {{ display: flex; align-items: center; margin-bottom: 0.8rem; padding: 0.8rem; background: var(--border); border-radius: 8px; }}
  .achievement-tier {{ margin-right: 0.8rem; font-size: 1.2rem; }}
  .achievement-info h4 {{ color: var(--accent); margin-bottom: 0.2rem; }}
  .achievement-info .desc {{ color: var(--dim); font-size: 0.8rem; }}
  .journal-entry {{ background: var(--border); padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }}
  .journal-date {{ color: var(--accent); font-size: 0.85rem; margin-bottom: 0.5rem; }}
  .journal-content {{ font-size: 0.9rem; line-height: 1.4; }}
  .insight-item {{ background: var(--border); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; font-size: 0.9rem; }}
  .soundtrack {{ background: linear-gradient(135deg, var(--accent2), var(--accent)); padding: 1rem; border-radius: 12px; text-align: center; color: white; }}
  footer {{ text-align: center; color: var(--dim); font-size: 0.75rem; margin-top: 2rem; }}
</style>
</head>
<body>
<h1>🧠 Intrusive Thoughts</h1>
<p class="subtitle">What Ember does when you're not looking — now with memory, streaks, achievements, and vibes</p>

{f'<div class="soundtrack">{today_soundtrack}</div><br>' if today_soundtrack else ''}

<div class="grid">
  <div class="stat-card"><div class="number">{total_picks}</div><div class="label">Total Impulses</div></div>
  <div class="stat-card"><div class="number">{total_completed}</div><div class="label">Completed</div></div>
  <div class="stat-card"><div class="number">{len(achievements.get('earned', []))}</div><div class="label">🏆 Achievements</div></div>
  <div class="stat-card"><div class="number">{achievements.get('total_points', 0)}</div><div class="label">🎯 Points</div></div>
</div>

<div class="grid-2">
  <div class="section">
    <h2>📈 Mood History (Last 14 Days)</h2>
    {''.join(f'<span class="mood-dot" style="background: hsl({hash(m.get("mood_id",""))%360}, 70%, 60%)" title="{m.get("date","")} - {m.get("mood_id","")}"></span>' for m in mood_graph_data) if mood_graph_data else '<div class="empty">No mood history yet</div>'}
    <div style="margin-top: 1rem; font-size: 0.8rem; color: var(--dim);">
      {f"Recent pattern: {' → '.join([m.get('mood_id','?')[:4] for m in mood_graph_data[-5:]])}" if len(mood_graph_data) >= 5 else "Building mood patterns..."}
    </div>
  </div>

  <div class="section">
    <h2>🔥 Current Streaks</h2>
    {f'''<div class="streak-item"><strong>Activity:</strong> {current_streaks.get('activity_type', ['none'])[0]} × {len(current_streaks.get('activity_type', []))}</div>''' if current_streaks.get('activity_type') else ''}
    {f'''<div class="streak-item"><strong>Mood:</strong> {current_streaks.get('mood', ['none'])[0]} × {len(current_streaks.get('mood', []))}</div>''' if current_streaks.get('mood') else ''}
    {'<div class="empty">No active streaks</div>' if not current_streaks.get('activity_type') and not current_streaks.get('mood') else ''}
  </div>
</div>

<div class="grid-2">
  <div class="section">
    <h2>🏆 Recent Achievements</h2>
    {''.join(f"""<div class="achievement-item"><div class="achievement-tier">{ {"bronze": "🥉", "silver": "🥈", "gold": "🥇", "platinum": "💎"}.get(a.get("tier", "bronze"), "🏆") }</div><div class="achievement-info"><h4>{a.get("name", "Unknown")}</h4><div class="desc">{a.get("description", "")} (+{a.get("points", 0)} pts)</div></div></div>""" for a in recent_achievements) if recent_achievements else '<div class="empty">No achievements yet — keep grinding!</div>'}
  </div>

  <div class="section">
    <h2>📊 Productivity Insights</h2>
    {''.join(f'<div class="insight-item">{insight}</div>' for insight in productivity_stats.get('insights', [])) if productivity_stats.get('insights') else '<div class="empty">Building productivity patterns...</div>'}
  </div>
</div>

<div class="section">
  <h2>📓 Night Journal Entries</h2>
  {''.join(f'''<div class="journal-entry"><div class="journal-date">{entry["date"]}</div><div class="journal-content">{entry["content"].replace('**', '').replace('*', '')}</div></div>''' for entry in journal_entries) if journal_entries else '<div class="empty">No journal entries yet — night summaries auto-generate after sessions</div>'}
</div>

<div class="section">
  <h2>🎯 Most Common Impulses</h2>
  <div class="bar-chart">
    {''.join(f'''<div class="bar-row"><div class="bar-label">{name}</div><div class="bar" style="width: {max(count / max(top_thoughts[0][1], 1) * 100, 2):.0f}%"></div><div class="bar-count">{count}</div></div>''' for name, count in top_thoughts) if top_thoughts else '<div class="empty">No data yet — check back after some impulses fire</div>'}
  </div>
</div>

<div class="section">
  <h2>📝 Recent Activity</h2>
  {''.join(f"""<div class="history-item"><span class="time">{e.get('timestamp','?')[:16].replace('T',' ')}</span><span class="mood-tag mood-{e.get('mood','day')}">{e.get('mood','?')}</span> <strong>{e.get('thought_id','?')}</strong> <span style="color: var(--{'success' if e.get('vibe') == 'positive' else 'warning' if e.get('vibe') == 'negative' else 'dim'}); font-size: 0.8rem;">[{e.get('energy','?')}/{e.get('vibe','?')}]</span><div class="summary">{e.get('summary','')}</div></div>""" for e in recent) if recent else '<div class="empty">Nothing yet. First night session fires at 03:17 🌙</div>'}
</div>

<div class="section">
  <h2>🚦 System Health</h2>
  <div id="health-status">Loading v1.0 systems...</div>
  <script>
    fetch('/api/health').then(r=>r.json()).then(d=>{{
      let html = '<div class="grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));">';
      if(d.components) {{
        for(const [name, comp] of Object.entries(d.components)) {{
          html += `<div class="stat-card"><div class="number">${{comp.emoji}}</div><div class="label">${{name}}</div></div>`;
        }}
      }}
      html += '</div>';
      if(d.metrics) {{
        html += `<div style="color:var(--dim);font-size:0.8rem;margin-top:0.5rem;">Heartbeats: ${{d.metrics.total_heartbeats || 0}} | Incidents: ${{d.metrics.total_incidents || 0}} | Healthy streak: ${{d.metrics.consecutive_healthy || 0}}</div>`;
      }}
      document.getElementById('health-status').innerHTML = html;
    }}).catch(()=>{{document.getElementById('health-status').innerHTML='<div class="empty">Health monitor unavailable</div>';}});
  </script>
</div>

<footer>{get_agent_name()} {get_agent_emoji()} × Intrusive Thoughts v1.0 — refreshed {datetime.now().strftime('%Y-%m-%d %H:%M')}</footer>
</body>
</html>"""


def load_v1_systems():
    """Load data from all v1.0 systems for dashboard display."""
    systems = {}
    try:
        from health_monitor import get_dashboard_data
        systems["health"] = get_dashboard_data()
    except Exception:
        systems["health"] = None
    try:
        from memory_system import MemorySystem
        ms = MemorySystem()
        systems["memory"] = ms.get_stats()
    except Exception:
        systems["memory"] = None
    try:
        from trust_system import TrustSystem
        ts = TrustSystem()
        systems["trust"] = ts.get_stats()
    except Exception:
        systems["trust"] = None
    try:
        from proactive import ProactiveAgent
        pa = ProactiveAgent()
        systems["proactive"] = pa.wal_stats()
    except Exception:
        systems["proactive"] = None
    try:
        from self_evolution import SelfEvolutionSystem
        se = SelfEvolutionSystem()
        systems["evolution"] = se.get_stats()
    except Exception:
        systems["evolution"] = None
    return systems


class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            html = build_html()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == "/api/stats":
            history = load_history()
            picks = load_picks()
            thought_counts = Counter(p.get("thought", "?") for p in picks)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "total_picks": len(picks),
                "total_completed": len(history),
                "thought_counts": dict(thought_counts),
                "recent": history[-10:][::-1],
            }).encode())
        elif self.path == "/api/systems":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(load_v1_systems(), default=str).encode())
        elif self.path == "/api/health":
            try:
                from health_monitor import get_dashboard_data
                data = get_dashboard_data()
            except Exception:
                data = {"error": "health monitor unavailable"}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, default=str).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Quiet


if __name__ == "__main__":
    print(f"🧠 Intrusive Thoughts Dashboard running at http://localhost:{PORT}")
    HTTPServer(("0.0.0.0", PORT), DashboardHandler).serve_forever()
