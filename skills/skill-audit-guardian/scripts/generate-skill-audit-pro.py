#!/usr/bin/env python3
import glob
import html
import os
import re
from datetime import datetime

OUT = "/Users/gascomp/Desktop/skill-audit-pro.html"


def classify(snippet: str):
    s = snippet.lower()
    hits = []

    if re.search(r"\brm\s+-rf\b|\blaunchctl\b|\bcrontab\b|\bnc\s+-e\b", s):
        hits.append(("critical", "Dangerous system command pattern", "This can delete files, create persistence, or execute shell payloads. Could be malware behavior."))

    if re.search(r"~/.ssh|id_rsa|private key|authorization:|api[_-]?key|token", s):
        hits.append(("high", "Credential or secret-related pattern", "This references credentials/tokens. Could be legitimate auth handling, but also possible key theft/exfil path."))

    if re.search(r"\bcurl\b|\bwget\b|http://|https://|\bscp\b|\brsync\b", s):
        hits.append(("medium", "Network or data transfer pattern", "This reaches external endpoints or transfers data. Normal for API skills, but can also exfiltrate data."))

    if re.search(r"\bbash\s+-c\b|\bpython\s+-c\b|eval\(|child_process|subprocess|chmod\s+\+x", s):
        hits.append(("high", "Dynamic code/command execution", "Executes commands dynamically. Powerful but risky, often used in loaders or hidden execution chains."))

    # Benign documentation hints
    benign_doc = bool(re.search(r"part of|homepage:|website:|readme|template|docs", s))

    if not hits:
        if benign_doc:
            return "low", "Likely documentation text", "This looks like docs/content text, not executable behavior.", "likely-benign"
        return "low", "Low-risk text match", "No strong malicious indicator in this line.", "likely-benign"

    # pick top severity
    order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    top = sorted(hits, key=lambda x: order[x[0]], reverse=True)[0]
    sev = top[0]
    reason = "; ".join(dict.fromkeys(h[1] for h in hits))
    plain = " ".join(dict.fromkeys(h[2] for h in hits))

    if benign_doc and sev in ("medium", "high"):
        verdict = "review-manually"
        plain += " Note: this line may still be documentation/example text, so verify context before concluding malware."
    elif sev == "critical":
        verdict = "suspected-malware"
    elif sev == "high":
        verdict = "high-risk"
    else:
        verdict = "needs-review"

    return sev, reason, plain, verdict


def badge_class(risk):
    return {
        "SAFE": "safe",
        "CAUTION": "caution",
        "REMOVE": "remove",
    }.get(risk, "unknown")

entries = []
for report in sorted(glob.glob('/tmp/skill-audit/*/report.md')):
    txt = open(report, encoding='utf-8', errors='ignore').read()
    risk = re.search(r"- Risk: \*\*(.+?)\*\*", txt)
    score = re.search(r"- Score: (\d+)", txt)
    zipm = re.search(r"- ZIP: (.+)", txt)
    flags = re.search(r"- Flags: (.+)", txt)

    risk = risk.group(1) if risk else "UNKNOWN"
    score = score.group(1) if score else "?"
    zip_name = os.path.basename(zipm.group(1)) if zipm else os.path.basename(os.path.dirname(report))
    flags = flags.group(1) if flags else "none"

    suspicious_path = os.path.join(os.path.dirname(report), 'suspicious.txt')
    lines = []
    if os.path.exists(suspicious_path):
        for raw in open(suspicious_path, encoding='utf-8', errors='ignore'):
            raw = raw.rstrip('\n')
            if not raw:
                continue
            m = re.match(r'^(.*?):(\d+):(.*)$', raw)
            if m:
                fpath, lno, snippet = m.group(1), m.group(2), m.group(3).strip()
            else:
                fpath, lno, snippet = raw, '?', ''
            sev, reason, plain, verdict = classify(snippet)
            lines.append({
                'file': fpath,
                'line': lno,
                'snippet': snippet,
                'sev': sev,
                'reason': reason,
                'plain': plain,
                'verdict': verdict,
            })

    # Overall plain-English explanation per skill
    if risk == 'SAFE':
        overall = "No strong harmful behavior patterns were found. Some matches may be normal network/docs text."
    elif risk == 'CAUTION':
        overall = "This skill contains patterns that are common in legit integrations (API/network/auth), but they can also be abused. Review before trusting with real keys."
    elif risk == 'REMOVE':
        overall = "This skill triggered stacked high-risk signals (e.g., dynamic execution + credential/network/system patterns). Treat as suspected malware until manual deep review clears it."
    else:
        overall = "Risk could not be determined confidently."

    entries.append({
        'zip': zip_name,
        'risk': risk,
        'score': score,
        'flags': flags,
        'overall': overall,
        'lines': lines,
    })

counts = {}
for e in entries:
    counts[e['risk']] = counts.get(e['risk'], 0) + 1

css = """
:root{--bg:#0b1020;--panel:#111831;--panel2:#0f1730;--text:#e8ecff;--muted:#9aa4c7;--safe:#16a34a;--caution:#f59e0b;--remove:#ef4444;--chip:#1b2447}
*{box-sizing:border-box} body{margin:0;background:linear-gradient(180deg,#0b1020,#0f1730);color:var(--text);font:14px/1.45 Inter,ui-sans-serif,system-ui}
.wrap{max-width:1200px;margin:24px auto;padding:0 16px}
.h1{font-size:30px;font-weight:800;margin:0 0 4px}.sub{color:var(--muted);margin-bottom:16px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:14px}
.card{background:var(--panel);border:1px solid #22305f;border-radius:14px;padding:12px}
.num{font-size:24px;font-weight:800}.label{color:var(--muted);font-size:12px}
.toolbar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-bottom:14px}
.btn{border:1px solid #2a3a74;background:var(--chip);color:var(--text);padding:8px 12px;border-radius:999px;cursor:pointer;font-weight:700}
.btn.active{outline:2px solid #8ca5ff}
.search{margin-left:auto;min-width:280px;background:var(--panel);border:1px solid #2a3a74;color:var(--text);padding:10px 12px;border-radius:10px}
.list{display:flex;flex-direction:column;gap:12px}
.item{background:var(--panel);border:1px solid #25366d;border-radius:14px;overflow:hidden}
.head{display:grid;grid-template-columns:1fr auto auto;gap:10px;align-items:center;padding:12px 14px;cursor:pointer}
.name{font-weight:700;word-break:break-word}.badge{padding:3px 10px;border-radius:999px;font-size:12px;font-weight:800}
.safe{background:color-mix(in srgb, var(--safe) 25%, transparent);color:#7dffa6;border:1px solid #2ea463}
.caution{background:color-mix(in srgb, var(--caution) 25%, transparent);color:#ffd27a;border:1px solid #d48b00}
.remove{background:color-mix(in srgb, var(--remove) 25%, transparent);color:#ff9b9b;border:1px solid #d83b3b}
.unknown{background:#334155;color:#dbeafe;border:1px solid #64748b}
.score{color:#c6d2ff}
.body{display:none;padding:0 14px 14px}
.item.open .body{display:block}
.overall{background:#0f1730;border:1px solid #24315e;border-radius:10px;padding:10px;margin-bottom:10px}
table{width:100%;border-collapse:collapse}
th,td{border:1px solid #24315e;padding:8px;vertical-align:top;font-size:12px}
th{background:#111b38}
.sev-critical{color:#ff8f8f;font-weight:700}
.sev-high{color:#ffd27a;font-weight:700}
.sev-medium{color:#ffe6a3;font-weight:700}
.sev-low{color:#b8c4f2;font-weight:700}
.verdict-suspected-malware{color:#ff8f8f;font-weight:700}
.verdict-high-risk{color:#ffd27a;font-weight:700}
.verdict-needs-review{color:#ffe6a3;font-weight:700}
.verdict-review-manually{color:#fcd34d;font-weight:700}
.verdict-likely-benign{color:#86efac;font-weight:700}
@media (max-width:900px){.stats{grid-template-columns:repeat(2,1fr)}.head{grid-template-columns:1fr auto}.search{margin-left:0;min-width:unset;flex:1}}
"""

html_parts = []
html_parts.append("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
html_parts.append("<title>Skill Audit Pro</title><style>" + css + "</style></head><body><div class='wrap'>")
html_parts.append("<h1 class='h1'>Skill Audit Dashboard</h1>")
html_parts.append(f"<div class='sub'>Generated {html.escape(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}. Click a skill to see plain-English reasoning behind each flagged line.</div>")
html_parts.append(
    f"<div class='stats'>"
    f"<div class='card'><div class='num'>{len(entries)}</div><div class='label'>Total Skills</div></div>"
    f"<div class='card'><div class='num' style='color:#7dffa6'>{counts.get('SAFE',0)}</div><div class='label'>SAFE</div></div>"
    f"<div class='card'><div class='num' style='color:#ffd27a'>{counts.get('CAUTION',0)}</div><div class='label'>CAUTION</div></div>"
    f"<div class='card'><div class='num' style='color:#ff9b9b'>{counts.get('REMOVE',0)}</div><div class='label'>REMOVE</div></div>"
    f"</div>"
)

html_parts.append("""
<div class='toolbar'>
  <button class='btn active' data-filter='ALL'>All</button>
  <button class='btn' data-filter='SAFE'>SAFE</button>
  <button class='btn' data-filter='CAUTION'>CAUTION</button>
  <button class='btn' data-filter='REMOVE'>REMOVE</button>
  <input id='q' class='search' placeholder='Search skill name / flags / reasons...' />
</div>
<div class='list' id='list'>
""")

for e in sorted(entries, key=lambda x: ({'REMOVE':0,'CAUTION':1,'SAFE':2}.get(x['risk'],3), x['zip'].lower())):
    b = badge_class(e['risk'])
    keyword_blob = (e['zip'] + " " + e['flags'] + " " + e['overall'] + " " + " ".join(l['reason'] for l in e['lines'][:50])).lower()

    rows = []
    for l in e['lines'][:80]:
        sev_cls = f"sev-{l['sev']}"
        verdict_cls = f"verdict-{l['verdict']}"
        rows.append(
            "<tr>"
            f"<td class='{sev_cls}'>{html.escape(l['sev'])}</td>"
            f"<td><code>{html.escape(l['file'])}:{html.escape(l['line'])}</code></td>"
            f"<td>{html.escape(l['snippet'])}</td>"
            f"<td>{html.escape(l['reason'])}</td>"
            f"<td>{html.escape(l['plain'])}</td>"
            f"<td class='{verdict_cls}'>{html.escape(l['verdict'])}</td>"
            "</tr>"
        )

    if not rows:
        rows.append("<tr><td colspan='6'>No suspicious lines captured for this skill.</td></tr>")

    html_parts.append(
        f"<div class='item' data-risk='{html.escape(e['risk'])}' data-name='{html.escape(keyword_blob)}'>"
        f"<div class='head' onclick='toggleItem(this.parentElement)'>"
        f"<div class='name'>{html.escape(e['zip'])}<div class='score'>Score {html.escape(str(e['score']))} · Flags: {html.escape(e['flags'])}</div></div>"
        f"<div><span class='badge {b}'>{html.escape(e['risk'])}</span></div>"
        f"<div class='score'>Click to expand</div>"
        f"</div>"
        f"<div class='body'>"
        f"<div class='overall'><b>Why this result:</b> {html.escape(e['overall'])}</div>"
        f"<table><thead><tr><th>Severity</th><th>File:Line</th><th>Code/Text snippet</th><th>What scanner saw</th><th>Plain-English explanation</th><th>Verdict</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
        f"</div></div>"
    )

html_parts.append("</div>")
html_parts.append("""
<script>
let current='ALL';
const btns=[...document.querySelectorAll('.btn[data-filter]')];
function apply(){
  const q=document.getElementById('q').value.trim().toLowerCase();
  document.querySelectorAll('.item').forEach(it=>{
    const risk=it.dataset.risk;
    const text=it.dataset.name;
    const okRisk=(current==='ALL'||risk===current);
    const okQ=(!q||text.includes(q));
    it.style.display=(okRisk&&okQ)?'':'none';
  });
}
btns.forEach(b=>b.onclick=()=>{current=b.dataset.filter;btns.forEach(x=>x.classList.remove('active'));b.classList.add('active');apply();});
document.getElementById('q').addEventListener('input',apply);
function toggleItem(el){el.classList.toggle('open');}
window.toggleItem=toggleItem;
apply();
</script>
""")
html_parts.append("</div></body></html>")

open(OUT, 'w', encoding='utf-8').write(''.join(html_parts))
print(OUT)
