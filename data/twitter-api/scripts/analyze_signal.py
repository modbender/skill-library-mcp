import json
import pathlib
import datetime
import re
import collections

BASE = pathlib.Path(r"C:\Users\IFLW016\Desktop\GanClaw_Workspace\_shared\social_ops")
TIMELINE_PATH = BASE / "timeline_raw.json"
NOTIF_PATH = BASE / "notifications_raw.json"
RESEARCH_DIR = BASE / "research"
RESEARCH_DIR.mkdir(exist_ok=True)

timeline = json.loads(TIMELINE_PATH.read_text(encoding="utf-8"))
notifications = json.loads(NOTIF_PATH.read_text(encoding="utf-8"))

words = collections.Counter()
handles_counter = collections.Counter()
entry_points = []
relevant_keywords = {"openclaw", "ai", "agent", "agents", "crypto", "bot", "automation", "workflow", "trading", "defi", "polygon", "felix", "pixel"}

for tweet in timeline:
    text = tweet.get("text", "")
    user = tweet.get("user", {})
    handle = user.get("username", "")
    if handle:
        handles_counter[handle] += 1
    tokens = re.findall(r"[A-Za-z0-9']+", text.lower())
    for token in tokens:
        if len(token) > 3:
            words[token] += 1
    if any(key in text.lower() for key in ["openclaw", "ai", "agent", "crypto", "automation", "trading", "bot"]):
        entry_points.append({
            "handle": handle,
            "display": user.get("display_name", ""),
            "id": tweet.get("id"),
            "text": text[:240]
        })

top_words = [word for word, _ in words.most_common(50) if word in relevant_keywords][:10]
top_handles = handles_counter.most_common(10)

users = notifications.get("globalObjects", {}).get("users", {})
notif_snapshot = [
    {"handle": info.get("screen_name"), "name": info.get("name")}
    for _, info in list(users.items())[:8]
]

now = datetime.datetime.utcnow()
stamp = now.strftime("%Y%m%dT%H%M%SZ")
md_lines = [f"# Social Intelligence Signal — {now.isoformat()}Z", ""]

md_lines.append("## Topics gaining traction")
if top_words:
    for word in top_words:
        md_lines.append(f"- **{word}**")
else:
    md_lines.append("- (No obvious AI/crypto/OpenClaw keywords in sample)")
md_lines.append("")

md_lines.append("## Notable accounts to watch")
if top_handles:
    for handle, count in top_handles:
        md_lines.append(f"- @{handle} (approx {count} mentions)")
else:
    md_lines.append("- (None surfaced)")
md_lines.append("")

md_lines.append("## Potential conversation entry points")
if entry_points:
    for item in entry_points[:8]:
        md_lines.append(f"- @{item['handle']} — {item['text']} (tweet {item['id']})")
else:
    md_lines.append("- None flagged this cycle")
md_lines.append("")

md_lines.append("## Notifications snapshot")
if notif_snapshot:
    for item in notif_snapshot:
        md_lines.append(f"- @{item['handle']} ({item['name']})")
else:
    md_lines.append("- No new notifications")
md_lines.append("")

md_path = RESEARCH_DIR / f"{stamp}-signal.md"
raw_path = RESEARCH_DIR / f"{stamp}-raw.json"
md_path.write_text('\n'.join(md_lines), encoding='utf-8')
raw_path.write_text(json.dumps({"timeline": timeline[:40], "notifications": notifications}, indent=2), encoding='utf-8')

print(md_path)
print(raw_path)
