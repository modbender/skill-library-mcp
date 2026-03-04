import os
import re
import sqlite3
from datetime import datetime, timedelta

try:
    from html2image import Html2Image
    from PIL import Image
except Exception:
    print("[!] Missing dependencies: install requirements.txt first (pip install -r requirements.txt)")
    raise

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "calorie_data.db")
WORKSPACE_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))
USER_MD_PATH = os.getenv('CALORIE_VIS_USER_MD', os.path.join(WORKSPACE_DIR, 'USER.md'))


def parse_user_md():
    if not os.path.exists(USER_MD_PATH):
        return None
    with open(USER_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    info = {}
    h = re.search(r"身高[:：]\s*(\d+)", content)
    w = re.search(r"体重[:：]\s*(\d+(?:\.\d+)?)", content)
    a = re.search(r"年龄[:：]\s*(\d+)", content)
    g = re.search(r"性别[:：]\s*(男|女)", content)
    if h:
        info["height"] = float(h.group(1))
    if w:
        info["weight"] = float(w.group(1))
    if a:
        info["age"] = int(a.group(1))
    if g:
        info["gender"] = "male" if "男" in g.group(1) else "female"
    return info if len(info) >= 4 else None


def _calc_goal(c):
    c.execute("SELECT value FROM config WHERE key = 'daily_goal'")
    row = c.fetchone()
    if row and row[0]:
        return int(row[0])

    profile = parse_user_md()
    if profile:
        if profile["gender"] == "male":
            bmr = 10 * profile["weight"] + 6.25 * profile["height"] - 5 * profile["age"] + 5
        else:
            bmr = 10 * profile["weight"] + 6.25 * profile["height"] - 5 * profile["age"] - 161
        return int(bmr * 1.2)

    return 2000


def ensure_tables(c):
    c.execute('''CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        food_name TEXT,
        calories INTEGER,
        protein INTEGER,
        photo_path TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')


def get_data_extended():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ensure_tables(c)

    now = datetime.now()
    today = now.strftime("%Y-%m-%d")

    c.execute("SELECT SUM(calories), SUM(protein) FROM entries WHERE date = ?", (today,))
    row = c.fetchone()
    consumed = row[0] or 0
    protein = row[1] or 0

    c.execute("SELECT food_name, calories FROM entries WHERE date = ? ORDER BY created_at DESC", (today,))
    items = c.fetchall()

    goal = _calc_goal(c)

    c.execute("SELECT date, SUM(calories) FROM entries GROUP BY date ORDER BY date DESC LIMIT 35")
    rows = c.fetchall()
    conn.close()

    day_map = {d: (v or 0) for d, v in rows}

    # Week: current week starts from Sunday
    sunday_offset = (now.weekday() + 1) % 7
    week_start = now - timedelta(days=sunday_offset)
    week_dates = [(week_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    week_labels = [datetime.strptime(d, "%Y-%m-%d").strftime("%m/%d") for d in week_dates]
    week_values = [day_map.get(d, 0) for d in week_dates]

    # Month: from day 1 to today
    month_start = now.replace(day=1)
    month_days = (now - month_start).days + 1
    month_dates = [(month_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(month_days)]
    month_values = [day_map.get(d, 0) for d in month_dates]

    return consumed, protein, goal, items, week_dates, week_labels, week_values, month_values, today


def generate_image():
    consumed, protein, goal, items, week_dates, week_labels, week_values, month_values, today = get_data_extended()

    progress_percent = min(100, (consumed / goal) * 100) if goal > 0 else 0
    max_week = max(max(week_values), goal, 1)
    max_month = max(max(month_values) if month_values else 0, goal, 1)

    target_carb = (goal * 0.4) / 4
    target_pro = (goal * 0.3) / 4
    target_fat = (goal * 0.3) / 9
    cur_carb = consumed * 0.45 / 4
    cur_fat = consumed * 0.25 / 9

    # Week bars
    week_bar_html = ""
    for d, lbl, v in zip(week_dates, week_labels, week_values):
        is_future = d > today
        color = "#cbd5e1" if is_future else "#48bb78"
        h_pct = 0 if is_future else (v / max_week * 100)
        text = "-" if is_future else str(int(v))
        week_bar_html += (
            f'<div class="bar-item">'
            f'<div style="font-size:10px;color:#64748b;font-weight:700">{text}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="height:{h_pct:.1f}%;background:{color};"></div></div>'
            f'<div class="bar-label">{lbl}</div>'
            f"</div>"
        )

    # Month line (with padding to avoid point clipping)
    svg_w, svg_h = 620, 140
    marker_r = 3.5
    pad = marker_r + 1.5

    def map_y(v):
        usable = max(svg_h - 2 * pad, 1)
        return pad + (1 - (v / max_month)) * usable

    points = []
    n = len(month_values)
    if n <= 1:
        points = [(0, map_y(month_values[0] if n == 1 else 0))]
    else:
        for i, v in enumerate(month_values):
            x = (i / (n - 1)) * svg_w
            points.append((x, map_y(v)))

    month_line_points = " ".join([f"{x:.1f},{y:.1f}" for x, y in points])
    month_area_points = f"0,{svg_h-pad:.1f} {month_line_points} {svg_w:.1f},{svg_h-pad:.1f}" if month_line_points else ""
    month_markers = "".join([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{marker_r}" fill="#16a34a" />' for x, y in points])

    week_goal_y = 14 + max(0, min(120, 120 - (goal / max_week * 120)))
    month_goal_y = max(0, min(140, 140 - (goal / max_month * 140)))

    month_svg = f'''<svg width="100%" height="140" viewBox="0 0 {svg_w} {svg_h}" preserveAspectRatio="none" style="position:absolute;left:0;right:0;bottom:0;z-index:6;overflow:visible;">
      <polygon points="{month_area_points}" fill="#22c55e" fill-opacity="0.20" />
      <polyline points="{month_line_points}" fill="none" stroke="#16a34a" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" />
      {month_markers}
    </svg>'''

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
html, body {{ margin:0; width:100%; height:100%; }}
body {{ background:#f0f2f5; box-sizing:border-box; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }}
.frame {{ width:1200px; height:675px; position:relative; box-sizing:border-box; }}
.container {{ position:absolute; left:18px; top:27px; width:1164px; height:620px; display:flex; background:white; border-radius:64px; box-shadow:0 8px 18px rgba(0,0,0,.06); overflow:hidden; }}
.container::after {{ content:""; position:absolute; inset:0; border:4px solid #c9d8ed; border-radius:64px; pointer-events:none; z-index:50; }}
.left-panel {{ width:380px; padding:30px; border-right:1px solid #edf2f7; display:flex; flex-direction:column; box-sizing:border-box; }}
.main-circle-container {{ position:relative; width:170px; height:170px; margin:0 auto 20px; }}
.progress-ring {{ transform:rotate(-90deg); transform-origin:50% 50%; }}
.circle-inner-content {{ position:absolute; inset:0; display:flex; flex-direction:column; justify-content:center; align-items:center; }}
.inner-label {{ font-size:14px; color:#718096; }}
.inner-value {{ font-size:42px; font-weight:800; color:#1a202c; }}
.inner-sub {{ font-size:12px; color:#a0aec0; margin-top:2px; }}
.macro-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin-bottom:25px; }}
.macro-item {{ text-align:center; }}
.macro-label {{ font-size:12px; color:#718096; margin-bottom:5px; font-weight:600; }}
.macro-bar-bg {{ height:6px; background:#edf2f7; border-radius:3px; overflow:hidden; margin-bottom:6px; }}
.macro-bar-fill {{ height:100%; border-radius:3px; }}
.food-list {{ flex:1; overflow:hidden; }}
.food-item {{ display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #f7fafc; }}
.food-name {{ font-weight:600; font-size:14px; color:#4a5568; }}
.food-cal {{ color:#718096; font-size:13px; font-weight:700; }}
.right-panel {{ flex:1; padding:40px; display:flex; flex-direction:column; gap:30px; box-sizing:border-box; min-height:0; }}
.chart-box {{ flex:1; display:flex; flex-direction:column; min-height:0; }}
.chart-title {{ font-size:18px; font-weight:700; color:#2d3748; margin-bottom:15px; }}
.chart-content {{ flex:1; position:relative; border-left:2px solid #edf2f7; border-bottom:2px solid #edf2f7; min-height:0; }}
.goal-line {{ position:absolute; left:0; right:0; border-top:2px dashed #fc8181; z-index:10; display:flex; justify-content:flex-end; }}
.goal-label {{ color:#fc8181; font-size:10px; font-weight:700; padding-right:5px; margin-top:-15px; background:rgba(255,255,255,.6); }}
.week-plot {{ position:absolute; left:15px; right:15px; bottom:8px; height:148px; }}
.bar-container {{ display:flex; align-items:stretch; height:100%; gap:12px; }}
.bar-item {{ flex:1; display:grid; grid-template-rows:14px 120px 14px; align-items:center; justify-items:center; }}
.bar-track {{ width:72%; height:120px; background:#e9eef5; border-radius:6px; position:relative; overflow:hidden; }}
.bar-fill {{ position:absolute; left:0; right:0; bottom:0; border-radius:6px 6px 0 0; }}
.bar-label {{ font-size:10px; color:#a0aec0; }}
.month-plot {{ position:absolute; left:0; right:0; bottom:2px; height:140px; z-index:6; }}
.month-line-wrap {{ position:absolute; inset:0; z-index:6; }}
</style>
</head>
<body>
<div class="frame"><div class="container">
  <div class="left-panel">
    <div class="main-circle-container">
      <svg width="170" height="170" class="progress-ring">
        <circle stroke="#edf2f7" stroke-width="12" fill="transparent" r="75" cx="85" cy="85" />
        <circle stroke="#48bb78" stroke-width="12" stroke-linecap="round" fill="transparent" r="75" cx="85" cy="85" stroke-dasharray="471.2" stroke-dashoffset="{471.2 * (1 - progress_percent / 100)}" />
      </svg>
      <div class="circle-inner-content">
        <div class="inner-label">Diet Intake</div><div class="inner-value">{int(consumed)}</div><div class="inner-sub">Goal {goal} kcal</div>
      </div>
    </div>
    <div class="macro-grid">
      <div class="macro-item"><div class="macro-label">Carbs</div><div class="macro-bar-bg"><div class="macro-bar-fill" style="width:{min(100,(cur_carb/target_carb)*100)}%;background:#63b3ed;"></div></div><div style="font-size:10px;">{int(cur_carb)}g/{int(target_carb)}g</div></div>
      <div class="macro-item"><div class="macro-label">Protein</div><div class="macro-bar-bg"><div class="macro-bar-fill" style="width:{min(100,(protein/target_pro)*100)}%;background:#f6ad55;"></div></div><div style="font-size:10px;">{int(protein)}g/{int(target_pro)}g</div></div>
      <div class="macro-item"><div class="macro-label">Fat</div><div class="macro-bar-bg"><div class="macro-bar-fill" style="width:{min(100,(cur_fat/target_fat)*100)}%;background:#fc8181;"></div></div><div style="font-size:10px;">{int(cur_fat)}g/{int(target_fat)}g</div></div>
    </div>
    <div class="food-list">{"".join([f'<div class="food-item"><div class="food-name">{n}</div><div class="food-cal">{k} kcal</div></div>' for n,k in items[:5]])}</div>
  </div>
  <div class="right-panel">
    <div class="chart-box"><div class="chart-title">Weekly Calorie Intake (kcal)</div><div class="chart-content"><div class="week-plot"><div class="goal-line" style="top:{week_goal_y:.1f}px;"><div class="goal-label">BUDGET {goal}</div></div><div class="bar-container">{week_bar_html}</div></div></div></div>
    <div class="chart-box"><div class="chart-title">Monthly Calorie Trend (kcal)</div><div class="chart-content"><div class="month-plot"><div class="goal-line" style="top:{month_goal_y:.1f}px;"></div><div class="month-line-wrap">{month_svg}</div></div></div></div>
  </div>
</div></div>
</body>
</html>
"""

    out = os.path.join(BASE_DIR, "daily_report.png")
    raw = os.path.join(BASE_DIR, "daily_report_raw.png")

    hti = Html2Image(output_path=BASE_DIR)
    hti.screenshot(html_str=html, save_as="daily_report_raw.png", size=(1200, 900))

    img = Image.open(raw)
    w, h = img.size
    px = img.load()
    bg = px[0, 0]

    threshold = 5
    top, bottom, left, right = h, 0, w, 0
    for y in range(h):
        for x in range(w):
            p = px[x, y]
            if any(abs(p[i] - bg[i]) > threshold for i in range(3)):
                top, bottom = min(top, y), max(bottom, y)
                left, right = min(left, x), max(right, x)

    left, right = max(0, left - 10), min(w, right + 10)
    top, bottom = max(0, top - 16), min(h, bottom + 16)
    img.crop((left, top, right, bottom)).save(out)

    try:
        os.remove(raw)
    except Exception:
        pass

    print(f"IMAGE_PATH:{out}")


if __name__ == "__main__":
    generate_image()
