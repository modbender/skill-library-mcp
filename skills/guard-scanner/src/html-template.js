/**
 * guard-scanner — HTML Report Template
 * Dark Glassmorphism + Conic-gradient Risk Gauges
 * Zero dependencies. Pure CSS animations.
 */

'use strict';

function generateHTML(version, stats, findings) {
    const safetyRate = stats.scanned > 0 ? Math.round(((stats.clean + stats.low) / stats.scanned) * 100) : 100;

    // ── Risk gauge (conic-gradient donut) ──
    const riskGauge = (risk) => {
        const angle = (risk / 100) * 360;
        const color = risk >= 80 ? '#ef4444' : risk >= 30 ? '#f59e0b' : '#22c55e';
        return `<div class="risk-gauge" style="--risk-angle:${angle}deg;--risk-color:${color}"><span class="risk-val">${risk}</span></div>`;
    };

    // ── Aggregate severity + category counts ──
    const sevCounts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };
    const catCounts = {};
    for (const sr of findings) {
        for (const f of sr.findings) {
            sevCounts[f.severity] = (sevCounts[f.severity] || 0) + 1;
            catCounts[f.cat] = (catCounts[f.cat] || 0) + 1;
        }
    }
    const total = Object.values(sevCounts).reduce((a, b) => a + b, 0);

    // ── Severity distribution bars ──
    const sevColors = { CRITICAL: '#ef4444', HIGH: '#f97316', MEDIUM: '#eab308', LOW: '#22c55e' };
    const sevBars = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'].map(s => {
        const c = sevCounts[s], pct = total > 0 ? ((c / total) * 100).toFixed(1) : 0;
        return `<div class="bar-row"><span class="bar-label" style="color:${sevColors[s]}">${s}</span><div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:${sevColors[s]}"></div></div><span class="bar-ct">${c}</span></div>`;
    }).join('\n');

    // ── Top 8 categories ──
    const topCats = Object.entries(catCounts).sort((a, b) => b[1] - a[1]).slice(0, 8);
    const catBars = topCats.map(([cat, c]) => {
        const pct = total > 0 ? ((c / total) * 100).toFixed(0) : 0;
        return `<div class="bar-row"><span class="bar-label cat-lbl">${cat}</span><div class="bar-track"><div class="bar-fill cat-fill" style="width:${pct}%"></div></div><span class="bar-ct">${c}</span></div>`;
    }).join('\n');

    // ── Skill cards ──
    let cards = '';
    for (const sr of findings) {
        const vc = sr.verdict === 'MALICIOUS' ? 'mal' : sr.verdict === 'SUSPICIOUS' ? 'sus' : sr.verdict === 'LOW RISK' ? 'low' : 'ok';
        const icon = sr.verdict === 'MALICIOUS' ? '💀' : sr.verdict === 'SUSPICIOUS' ? '⚡' : sr.verdict === 'LOW RISK' ? '⚠️' : '✅';
        const rows = sr.findings.map(f => {
            const sc = f.severity.toLowerCase();
            return `<tr class="f-row"><td><span class="pill ${sc}">${f.severity}</span></td><td class="mono dim">${f.cat}</td><td>${f.desc}</td><td class="mono muted">${f.file}${f.line ? ':' + f.line : ''}</td></tr>`;
        }).join('\n');

        cards += `
<details class="card card-${vc}" ${(vc === 'mal' || vc === 'sus') ? 'open' : ''}>
  <summary class="card-head">
    <div class="card-info"><span class="card-icon">${icon}</span><span class="card-name">${sr.skill}</span><span class="v-pill v-${vc}">${sr.verdict}</span></div>
    ${riskGauge(sr.risk)}
  </summary>
  <div class="card-body">
    <table class="ftable"><thead><tr><th>Severity</th><th>Category</th><th>Description</th><th>Location</th></tr></thead><tbody>${rows}</tbody></table>
  </div>
</details>`;
    }

    // ── Full HTML ──
    return `<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>guard-scanner v${version} — Security Report</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* ===== Tokens ===== */
:root{
  --bg:#06070d;--sf:rgba(15,18,35,.7);--cd:rgba(20,24,50,.55);--ch:rgba(28,33,65,.65);
  --bdr:rgba(100,120,255,.08);--glow:rgba(100,140,255,.15);
  --t1:#e8eaf6;--t2:#8b92b3;--t3:#5a6180;
  --blue:#6c8cff;--purple:#a78bfa;--cyan:#22d3ee;--green:#22c55e;--yellow:#eab308;--orange:#f97316;--red:#ef4444;
  --sans:'Inter',system-ui,-apple-system,sans-serif;--mono:'JetBrains Mono','SF Mono',monospace;
  --r:12px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:var(--sans);background:var(--bg);color:var(--t1);min-height:100vh;overflow-x:hidden;line-height:1.6}

/* ===== Ambient BG ===== */
body::before{content:'';position:fixed;inset:0;z-index:-1;
  background:radial-gradient(ellipse 80% 60% at 20% 10%,rgba(108,140,255,.08) 0%,transparent 50%),
  radial-gradient(ellipse 60% 50% at 80% 90%,rgba(167,139,250,.06) 0%,transparent 50%),
  radial-gradient(ellipse 50% 40% at 50% 50%,rgba(34,211,238,.04) 0%,transparent 50%);
  animation:pulse 12s ease-in-out infinite alternate}
@keyframes pulse{0%{opacity:.6;transform:scale(1)}100%{opacity:1;transform:scale(1.05)}}

.wrap{max-width:1200px;margin:0 auto;padding:32px 24px}

/* ===== Header ===== */
.hdr{text-align:center;margin-bottom:36px;animation:fadeD .6s ease-out}
.hdr h1{font-size:2.2em;font-weight:800;letter-spacing:-.03em;
  background:linear-gradient(135deg,var(--blue),var(--purple),var(--cyan));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.hdr .sub{color:var(--t2);font-size:.95em;margin-top:4px}
.hdr .ts{color:var(--t3);font-family:var(--mono);font-size:.78em;margin-top:2px}

/* ===== Stat Grid ===== */
.sg{display:grid;grid-template-columns:repeat(auto-fit,minmax(155px,1fr));gap:14px;margin-bottom:28px;animation:fadeU .7s ease-out}
.sc{background:var(--cd);backdrop-filter:blur(20px) saturate(1.5);-webkit-backdrop-filter:blur(20px) saturate(1.5);
  border:1px solid var(--bdr);border-radius:var(--r);padding:18px;text-align:center;
  transition:all .3s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden}
.sc::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,transparent,var(--ac,var(--blue)),transparent);opacity:0;transition:opacity .3s}
.sc:hover{transform:translateY(-3px);border-color:var(--glow)}.sc:hover::before{opacity:1}
.sn{font-size:2.2em;font-weight:800;letter-spacing:-.04em;line-height:1.1}
.sl{color:var(--t2);font-size:.78em;font-weight:500;margin-top:3px;text-transform:uppercase;letter-spacing:.06em}
.sc.g{--ac:var(--green)}.sc.g .sn{color:var(--green)}
.sc.l{--ac:#86efac}.sc.l .sn{color:#86efac}
.sc.s{--ac:var(--yellow)}.sc.s .sn{color:var(--yellow)}
.sc.m{--ac:var(--red)}.sc.m .sn{color:var(--red)}
.sc.r{--ac:var(--cyan)}.sc.r .sn{color:var(--cyan)}

/* ===== Analysis Panels ===== */
.ag{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-bottom:28px;animation:fadeU .8s ease-out}
@media(max-width:768px){.ag{grid-template-columns:1fr}}
.pn{background:var(--cd);backdrop-filter:blur(20px) saturate(1.5);-webkit-backdrop-filter:blur(20px) saturate(1.5);
  border:1px solid var(--bdr);border-radius:var(--r);padding:22px}
.pn h2{font-size:.88em;font-weight:600;color:var(--t2);text-transform:uppercase;letter-spacing:.08em;margin-bottom:14px}

/* Bars */
.bar-row{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.bar-label{font-family:var(--mono);font-size:.72em;font-weight:600;width:68px;text-align:right}
.cat-lbl{font-family:var(--sans);font-weight:500;color:var(--t2);width:110px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bar-track{flex:1;height:5px;background:rgba(255,255,255,.04);border-radius:3px;overflow:hidden}
.bar-fill{height:100%;border-radius:3px;transition:width 1.2s cubic-bezier(.4,0,.2,1)}
.cat-fill{background:linear-gradient(90deg,var(--blue),var(--purple))}
.bar-ct{font-family:var(--mono);font-size:.76em;color:var(--t3);width:28px}

/* ===== Skill Cards ===== */
.sec-title{font-size:1.05em;font-weight:700;margin-bottom:14px}
.card{background:var(--cd);backdrop-filter:blur(16px) saturate(1.4);-webkit-backdrop-filter:blur(16px) saturate(1.4);
  border:1px solid var(--bdr);border-radius:var(--r);margin-bottom:10px;overflow:hidden;
  transition:all .3s ease;animation:fadeU .5s ease-out both}
.card:hover{border-color:var(--glow)}
.card-mal{border-left:3px solid var(--red)}
.card-sus{border-left:3px solid var(--yellow)}
.card-low{border-left:3px solid #86efac}
.card-ok{border-left:3px solid var(--green)}

.card-head{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;cursor:pointer;list-style:none}
.card-head::-webkit-details-marker{display:none}
.card-info{display:flex;align-items:center;gap:8px;flex:1;min-width:0}
.card-icon{font-size:1.15em}
.card-name{font-weight:600;font-size:.92em;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.v-pill{font-family:var(--mono);font-size:.66em;font-weight:600;padding:2px 7px;border-radius:4px;letter-spacing:.04em}
.v-mal{background:rgba(239,68,68,.15);color:var(--red)}
.v-sus{background:rgba(234,179,8,.15);color:var(--yellow)}
.v-low{background:rgba(134,239,172,.15);color:#86efac}
.v-ok{background:rgba(34,197,94,.15);color:var(--green)}

/* Risk Gauge */
.risk-gauge{width:44px;height:44px;border-radius:50%;flex-shrink:0;display:flex;align-items:center;justify-content:center;position:relative;
  background:conic-gradient(var(--risk-color) 0deg,var(--risk-color) var(--risk-angle),rgba(255,255,255,.05) var(--risk-angle),rgba(255,255,255,.05) 360deg)}
.risk-gauge::after{content:'';position:absolute;inset:5px;border-radius:50%;background:var(--bg)}
.risk-val{position:relative;z-index:1;font-family:var(--mono);font-size:.68em;font-weight:700}

/* Findings Table */
.card-body{padding:0 18px 14px}
.ftable{width:100%;border-collapse:collapse;font-size:.82em}
.ftable th{text-align:left;font-size:.72em;font-weight:600;color:var(--t3);text-transform:uppercase;letter-spacing:.06em;padding:7px 9px;border-bottom:1px solid rgba(255,255,255,.04)}
.ftable td{padding:7px 9px;border-bottom:1px solid rgba(255,255,255,.025)}
.f-row{transition:background .2s}.f-row:hover{background:rgba(255,255,255,.02)}
.pill{font-family:var(--mono);font-size:.7em;font-weight:600;padding:2px 5px;border-radius:3px;letter-spacing:.03em}
.critical{background:rgba(239,68,68,.15);color:var(--red)}
.high{background:rgba(249,115,22,.15);color:var(--orange)}
.medium{background:rgba(234,179,8,.15);color:var(--yellow)}
.low{background:rgba(34,197,94,.15);color:var(--green)}
.mono{font-family:var(--mono);font-size:.9em}
.dim{color:var(--t2)}.muted{color:var(--t3);white-space:nowrap}

/* Empty */
.empty{text-align:center;padding:48px 20px;background:var(--cd);backdrop-filter:blur(20px);border:1px solid var(--bdr);border-radius:var(--r)}
.empty .ei{font-size:2.8em;margin-bottom:10px}
.empty p{color:var(--green);font-size:1.05em;font-weight:600}
.empty .es{color:var(--t3);font-size:.82em;margin-top:3px}

/* Footer */
.ft{text-align:center;margin-top:40px;padding-top:20px;border-top:1px solid rgba(255,255,255,.04);color:var(--t3);font-size:.78em}
.ft a{color:var(--blue);text-decoration:none}.ft a:hover{text-decoration:underline}

/* Animations */
@keyframes fadeD{from{opacity:0;transform:translateY(-18px)}to{opacity:1;transform:translateY(0)}}
@keyframes fadeU{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}

/* Responsive */
@media(max-width:640px){
  .sg{grid-template-columns:repeat(2,1fr)}.sn{font-size:1.7em}.hdr h1{font-size:1.5em}
  .ftable{font-size:.74em}
}

/* Print */
@media print{
  body{background:#fff;color:#111}body::before{display:none}
  .sc,.pn,.card{background:#f8f8f8;backdrop-filter:none;border-color:#ddd}
  .sn{color:#111!important}.card{break-inside:avoid}
}
</style></head><body>
<div class="wrap">
<div class="hdr">
  <h1>🛡️ guard-scanner v${version}</h1>
  <div class="sub">Security Scan Report</div>
  <div class="ts">${new Date().toISOString()}</div>
</div>

<div class="sg">
  <div class="sc"><div class="sn">${stats.scanned}</div><div class="sl">Scanned</div></div>
  <div class="sc g"><div class="sn">${stats.clean}</div><div class="sl">Clean</div></div>
  <div class="sc l"><div class="sn">${stats.low}</div><div class="sl">Low Risk</div></div>
  <div class="sc s"><div class="sn">${stats.suspicious}</div><div class="sl">Suspicious</div></div>
  <div class="sc m"><div class="sn">${stats.malicious}</div><div class="sl">Malicious</div></div>
  <div class="sc r"><div class="sn">${safetyRate}%</div><div class="sl">Safety Rate</div></div>
</div>

${total > 0 ? `<div class="ag">
  <div class="pn"><h2>Severity Distribution</h2>${sevBars}</div>
  <div class="pn"><h2>Top Categories</h2>${catBars}</div>
</div>` : ''}

<div>
  <div class="sec-title">Skill Analysis</div>
  ${cards || `<div class="empty"><div class="ei">✅</div><p>All Clear — No Threats Detected</p><div class="es">${stats.scanned} skill(s) scanned, 0 findings</div></div>`}
</div>

<div class="ft">
  guard-scanner v${version} &mdash; Zero dependencies. Zero compromises. 🛡️<br>
  Built by <a href="https://github.com/koatora20">Guava 🍈 &amp; Dee</a>
</div>
</div>
</body></html>`;
}

module.exports = { generateHTML };
