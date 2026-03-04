#!/usr/bin/env python3
"""
Generate an interactive HTML dashboard for a single LP executor.

Fetches from the Hummingbot REST API by executor ID — no SQLite needed.
Optionally overlays 5m KuCoin price candles for major pairs.

Usage:
    python scripts/visualize_lp_executor.py --id <executor_id>
    python scripts/visualize_lp_executor.py --id <executor_id> --output report.html
    python scripts/visualize_lp_executor.py --id <executor_id> --no-open

Examples:
    python scripts/visualize_lp_executor.py --id ryUBCGfuBgmDL5bPggxmVFbQzu7McBE1hXs2yRymiob
    python scripts/visualize_lp_executor.py --id 5w7GcMkZZVMDke4LjfqTVDsHVV7SVTF4pmL5TjbcYN8Z --output /tmp/sol_usdc.html
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.request
import urllib.error
import webbrowser
from datetime import datetime

# ---------------------------------------------------------------------------
# Auth / config  (HUMMINGBOT_API_URL / API_USER / API_PASS — same as other lp-agent scripts)
# ---------------------------------------------------------------------------

def load_env():
    """Load environment from .env files (first found wins)."""
    for path in [".env", os.path.expanduser("~/.hummingbot/.env"), os.path.expanduser("~/.env")]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


def get_api_config():
    """Get API configuration from environment."""
    load_env()
    return {
        "url":      os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000"),
        "user":     os.environ.get("API_USER", "admin"),
        "password": os.environ.get("API_PASS", "admin"),
    }


def make_auth_header(cfg):
    creds = base64.b64encode(f"{cfg['user']}:{cfg['password']}".encode()).decode()
    return f"Basic {creds}"


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def api_get(url, hdrs, timeout=30):
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}") from e


def api_post(url, payload, hdrs, timeout=30):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data,
                                  headers={**hdrs, "Content-Type": "application/json"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode(errors='replace')}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Connection error: {e.reason}") from e


def fetch_executor(base_url, hdrs, executor_id):
    raw = api_get(f"{base_url}/executors/{executor_id}", hdrs)
    if isinstance(raw, dict) and "data" in raw:
        data = raw["data"]
        return (data[0] if isinstance(data, list) and data else data) or None
    return raw


def fetch_candles(base_url, hdrs, trading_pair, start_time, end_time, interval="5m"):
    """Fetch KuCoin candles. Returns list or None. Skips exotic/pump pairs."""
    kucoin_pair = trading_pair.replace("USDC", "USDT").replace("usdc", "usdt")
    base_tok = kucoin_pair.split("-")[0]
    if len(base_tok) > 10 or base_tok.lower().endswith("pump"):
        print(f"  Skipping candle fetch — exotic pair: {kucoin_pair}")
        return None
    try:
        result = api_post(
            f"{base_url}/market-data/historical-candles",
            {"connector_name": "kucoin", "trading_pair": kucoin_pair,
             "interval": interval, "start_time": int(start_time), "end_time": int(end_time)},
            hdrs, timeout=20,
        )
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            for k in ("candles", "data", "ohlcv"):
                if k in result and isinstance(result[k], list):
                    return result[k]
        return None
    except Exception as e:
        print(f"  Warning: candle fetch failed for {kucoin_pair}: {e}")
        return None


# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------

def _f(v, d=None):
    if v is None or v == "":
        return d
    try:
        return float(v)
    except (ValueError, TypeError):
        return d


def _s(v, d=""):
    return str(v) if v is not None else d


def parse_ts(s):
    if not s:
        return None
    try:
        import calendar
        clean = str(s).replace("+00:00", "").replace("Z", "")
        if "." in clean:
            p = clean.split(".")
            clean = p[0] + "." + p[1][:6]
        dt = datetime.fromisoformat(clean)
        return calendar.timegm(dt.timetuple()) + dt.microsecond / 1e6
    except Exception:
        return None


def fmt_dur(s):
    if s is None or s <= 0:
        return "—"
    s = int(s)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m {s % 60}s"
    return f"{s // 3600}h {(s % 3600) // 60}m"


def fmt_ts(ts):
    if ts is None:
        return "—"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)


def status_color(status):
    return {
        "TERMINATED": "#4ecdc4", "COMPLETE": "#4ecdc4",
        "RUNNING": "#f0c644",    "ACTIVE": "#f0c644",
        "SHUTTING_DOWN": "#f0a644",
        "FAILED": "#e85d75",
    }.get(status, "#8b8fa3")


def pnl_col(v):
    return "#4ecdc4" if (v or 0) >= 0 else "#e85d75"


# ---------------------------------------------------------------------------
# HTML builder
# ---------------------------------------------------------------------------

DARK_CSS = """
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0d1117; color:#e8eaed; font-family:'JetBrains Mono','Fira Code',Consolas,monospace; font-size:12px; }
  .container { max-width:1200px; margin:0 auto; padding:24px 20px; }
  h1 { font-size:22px; font-weight:700; color:#4ecdc4; margin-bottom:4px; }
  .subtitle { font-size:11px; color:#6b7084; margin-bottom:24px; font-family:monospace; }
  .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr)); gap:10px; margin-bottom:24px; }
  .kpi-card { background:#161b27; border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:14px 16px; }
  .kpi-label { font-size:10px; color:#6b7084; text-transform:uppercase; letter-spacing:.06em; margin-bottom:6px; }
  .kpi-value { font-size:20px; font-weight:700; }
  .kpi-sub { font-size:10px; color:#555870; margin-top:4px; }
  .layout { display:grid; grid-template-columns:1fr 340px; gap:24px; }
  @media (max-width:900px) { .layout { grid-template-columns:1fr; } }
  .section-title { font-size:11px; font-weight:600; color:#8b8fa3; text-transform:uppercase; letter-spacing:.08em; margin:24px 0 12px; }
  .chart-wrap { background:#161b27; border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:16px; margin-bottom:20px; }
  .chart-container { position:relative; }
  .summary-table { background:#161b27; border:1px solid rgba(255,255,255,0.06); border-radius:10px; overflow:hidden; width:100%; }
  .summary-table td { padding:7px 12px; font-size:11px; border-bottom:1px solid rgba(255,255,255,0.03); }
  .summary-table tr:last-child td { border-bottom:none; }
  .summary-table tr:hover td { background:rgba(255,255,255,0.02); }
  .footer { font-size:10px; color:#3a3d50; text-align:center; margin-top:32px; padding-bottom:16px; }
  a { color:#7c6df0; text-decoration:none; }
  a:hover { text-decoration:underline; }
"""


def build_html(ex, candles):
    cfg = ex.get("config") or {}
    ci  = ex.get("custom_info") or {}

    eid        = _s(ex.get("executor_id") or ex.get("id"))
    pair       = _s(ex.get("trading_pair"))
    connector  = _s(ex.get("connector_name"))
    status     = _s(ex.get("status"))
    close_type = _s(ex.get("close_type"))
    account    = _s(ex.get("account_name"))
    controller = _s(ex.get("controller_id"))
    err_count  = ex.get("error_count", 0)

    created_ts = parse_ts(ex.get("created_at"))
    close_ts   = _f(ex.get("close_timestamp")) or parse_ts(ex.get("closed_at"))
    duration   = round(close_ts - created_ts, 1) if created_ts and close_ts and close_ts > created_ts else None

    pnl        = _f(ex.get("net_pnl_quote"), 0)
    pnl_pct    = _f(ex.get("net_pnl_pct"), 0)
    filled     = _f(ex.get("filled_amount_quote"), 0)

    # Config (deployment params)
    pool_addr  = _s(cfg.get("pool_address"))
    lower_cfg  = _f(cfg.get("lower_price"))
    upper_cfg  = _f(cfg.get("upper_price"))
    base_cfg   = _f(cfg.get("base_amount"))
    quote_cfg  = _f(cfg.get("quote_amount"))
    side_val   = cfg.get("side")
    offset_pct = _f(cfg.get("position_offset_pct"))
    auto_above = cfg.get("auto_close_above_range_seconds")
    auto_below = cfg.get("auto_close_below_range_seconds")
    keep_pos   = cfg.get("keep_position")

    side_map   = {0: "0 — BOTH", 1: "1 — BUY (quote-only)", 2: "2 — SELL (base-only)"}
    side_str   = side_map.get(side_val, str(side_val) if side_val is not None else "—")

    # custom_info (live / final state)
    state        = _s(ci.get("state"))
    pos_addr     = _s(ci.get("position_address"))
    cur_price    = _f(ci.get("current_price"))
    lower_actual = _f(ci.get("lower_price"))
    upper_actual = _f(ci.get("upper_price"))
    base_cur     = _f(ci.get("base_amount"))
    quote_cur    = _f(ci.get("quote_amount"))
    base_fee     = _f(ci.get("base_fee"))
    quote_fee    = _f(ci.get("quote_fee"))
    fees_earned  = _f(ci.get("fees_earned_quote"), 0)
    total_value  = _f(ci.get("total_value_quote"))
    unreal_pnl   = _f(ci.get("unrealized_pnl_quote"))
    pos_rent     = _f(ci.get("position_rent"))
    rent_ref     = _f(ci.get("position_rent_refunded"))
    tx_fee       = _f(ci.get("tx_fee"))
    oor_sec      = _f(ci.get("out_of_range_seconds"))
    max_retry    = ci.get("max_retries_reached")
    init_base    = _f(ci.get("initial_base_amount"))
    init_quote   = _f(ci.get("initial_quote_amount"))

    sc         = status_color(status)
    pc         = pnl_col(pnl)
    dur_str    = fmt_dur(duration)
    oor_str    = fmt_dur(oor_sec)
    lp_lower   = lower_cfg if lower_cfg is not None else lower_actual
    lp_upper   = upper_cfg if upper_cfg is not None else upper_actual

    # Solscan links
    pool_link = (
        f'<a href="https://solscan.io/account/{pool_addr}" target="_blank" '
        f'style="font-family:monospace;font-size:9px;word-break:break-all;">{pool_addr}</a>'
        if pool_addr else "—"
    )
    pos_link = (
        f'<a href="https://solscan.io/account/{pos_addr}" target="_blank" '
        f'style="font-family:monospace;font-size:9px;word-break:break-all;">{pos_addr}</a>'
        if pos_addr else "—"
    )

    # ---- Price chart ----
    price_section_html = ""
    price_chart_js     = ""
    if candles:
        cd = []
        for c in candles:
            if isinstance(c, list) and len(c) >= 5:
                ts_c, close_c = _f(c[0]), _f(c[4])
                if ts_c and close_c:
                    cd.append((ts_c, close_c))
            elif isinstance(c, dict):
                ts_c  = _f(c.get("timestamp") or c.get("ts") or c.get("open_time"))
                close_c = _f(c.get("close") or c.get("c"))
                if ts_c and close_c:
                    cd.append((ts_c, close_c))
        cd.sort()

        if cd:
            labels  = [datetime.fromtimestamp(t).strftime("%H:%M") for t, _ in cd]
            closes  = [v for _, v in cd]

            lp_lo_js = round(lp_lower, 8) if lp_lower is not None else "null"
            lp_hi_js = round(lp_upper, 8) if lp_upper is not None else "null"

            # Find index closest to open/close timestamps
            open_idx = close_idx = "null"
            if created_ts:
                for i, (t, _) in enumerate(cd):
                    if t >= created_ts:
                        open_idx = i; break
            if close_ts:
                for i, (t, _) in reversed(list(enumerate(cd))):
                    if t <= close_ts:
                        close_idx = i; break

            price_section_html = """
  <div class="section-title">Price Chart — 5m Candles (KuCoin) with LP Range</div>
  <div class="chart-wrap"><div class="chart-container" style="height:280px;">
    <canvas id="priceChart"></canvas>
  </div></div>"""

            price_chart_js = f"""
(function() {{
  const labels = {json.dumps(labels)};
  const closes = {json.dumps(closes)};
  const lo = {lp_lo_js}, hi = {lp_hi_js};
  const openIdx = {open_idx}, closeIdx = {close_idx};

  const ds = [{{
    label:'Close Price', data:closes,
    borderColor:'#f0c644', backgroundColor:'rgba(240,198,68,0.06)',
    borderWidth:2, pointRadius:0, fill:false, tension:0.1, order:1,
  }}];
  if (lo !== null) ds.push({{
    label:'LP Lower', data:closes.map(()=>lo),
    borderColor:'rgba(78,205,196,0.7)', borderWidth:1.5, borderDash:[5,5],
    pointRadius:0, fill:false, order:2,
  }});
  if (hi !== null) ds.push({{
    label:'LP Upper', data:closes.map(()=>hi),
    borderColor:'rgba(232,93,117,0.7)', borderWidth:1.5, borderDash:[5,5],
    pointRadius:0, fill:false, order:3,
  }});
  if (lo !== null && hi !== null) ds.push({{
    label:'LP Range', data:closes.map(()=>hi),
    borderColor:'transparent', backgroundColor:'rgba(124,109,240,0.07)',
    fill:1, pointRadius:0, order:4,
  }});
  if (openIdx !== null) ds.push({{
    label:'Open', data:closes.map((v,i)=>i===openIdx?v:null),
    borderColor:'#4ecdc4', backgroundColor:'#4ecdc4',
    pointRadius:closes.map((_,i)=>i===openIdx?8:0),
    pointStyle:'triangle', showLine:false, order:0,
  }});
  if (closeIdx !== null) ds.push({{
    label:'Close', data:closes.map((v,i)=>i===closeIdx?v:null),
    borderColor:'#e85d75', backgroundColor:'#e85d75',
    pointRadius:closes.map((_,i)=>i===closeIdx?8:0),
    pointStyle:'rectRot', showLine:false, order:0,
  }});

  new Chart(document.getElementById('priceChart').getContext('2d'), {{
    type:'line', data:{{labels, datasets:ds}},
    options:{{
      maintainAspectRatio:false,
      plugins:{{
        legend:{{display:true, labels:{{color:'#6b7084',font:{{size:10}},boxWidth:18,
          filter:(i)=>i.text!=='LP Range'}}}},
        tooltip:{{mode:'index', intersect:false,
          callbacks:{{label:(c)=>c.parsed.y!=null?` ${{c.dataset.label}}: ${{c.parsed.y.toFixed(6)}}`:null}}}}
      }},
      scales:{{
        x:{{ticks:{{color:'#6b7084',font:{{size:9}},maxTicksLimit:12}},grid:{{color:'rgba(255,255,255,0.04)'}}}},
        y:{{ticks:{{color:'#6b7084',font:{{size:10}},callback:(v)=>v.toFixed(4)}},grid:{{color:'rgba(255,255,255,0.06)'}}}}
      }}
    }}
  }});
}})();"""

    # ---- Balance chart ----
    balance_html = balance_js = ""
    if init_base is not None and base_cur is not None:
        balance_html = """
  <div class="section-title">Token Balance — Initial vs Final</div>
  <div class="chart-wrap"><div class="chart-container" style="height:190px;">
    <canvas id="balChart"></canvas>
  </div></div>"""
        balance_js = f"""
(function() {{
  new Chart(document.getElementById('balChart').getContext('2d'), {{
    type:'bar',
    data:{{
      labels:{json.dumps(['Base (initial)','Base (final)','Quote (initial)','Quote (final)'])},
      datasets:[{{
        label:'Amount',
        data:{json.dumps([round(init_base,8), round(base_cur,8), round(init_quote or 0,8), round(quote_cur or 0,8)])},
        backgroundColor:['rgba(78,205,196,0.4)','rgba(78,205,196,0.85)','rgba(124,109,240,0.4)','rgba(124,109,240,0.85)'],
        borderRadius:4,
      }}]
    }},
    options:{{
      maintainAspectRatio:false,
      plugins:{{legend:{{display:false}},
        tooltip:{{callbacks:{{label:(c)=>` ${{c.parsed.y.toFixed(8)}}`}}}}
      }},
      scales:{{
        x:{{ticks:{{color:'#6b7084',font:{{size:10}}}},grid:{{color:'rgba(255,255,255,0.04)'}}}},
        y:{{ticks:{{color:'#6b7084',font:{{size:10}}}},grid:{{color:'rgba(255,255,255,0.06)'}}}}
      }}
    }}
  }});
}})();"""

    # ---- PnL breakdown chart ----
    il = pnl - fees_earned
    pnl_bkd_labels = json.dumps(["Fees Earned", "IL / Price Impact", "Net PnL"])
    pnl_bkd_data   = json.dumps([round(fees_earned, 8), round(il, 8), round(pnl, 8)])
    pnl_bkd_colors = json.dumps([
        "rgba(124,109,240,0.85)",
        "rgba(232,93,117,0.85)" if il < 0 else "rgba(78,205,196,0.85)",
        "rgba(78,205,196,0.85)" if pnl >= 0 else "rgba(232,93,117,0.85)",
    ])

    # ---- Summary table ----
    def row(label, value, color="#e8eaed"):
        return (f'<tr><td style="color:#6b7084;font-size:10px;width:46%">{label}</td>'
                f'<td style="text-align:right;color:{color};font-weight:500;">{value}</td></tr>')

    def sep():
        return '<tr><td colspan="2" style="padding:3px 0;border-bottom:1px solid rgba(255,255,255,0.06);"></td></tr>'

    d = lambda v, fmt=".8g": (f"{v:{fmt}}" if v is not None else "—")

    table_rows = "".join([
        row("Executor ID", f'<span style="font-family:monospace;font-size:9px;">{eid}</span>'),
        row("Account", account),
        row("Controller", controller or "—"),
        row("Connector", connector),
        row("Trading Pair", pair, "#e8eaed"),
        sep(),
        row("Status",
            f'<span style="padding:2px 8px;border-radius:8px;background:{sc}22;font-size:9px;">{status}</span>'),
        row("Close Type", close_type or "—"),
        row("State", state or "—"),
        row("Errors", str(err_count), "#e85d75" if err_count else "#e8eaed"),
        sep(),
        row("Created", fmt_ts(created_ts)),
        row("Closed",  fmt_ts(close_ts)),
        row("Duration", dur_str),
        row("Out of Range", oor_str),
        sep(),
        row("Net PnL",        f"{pnl:+.8f}", pc),
        row("Net PnL %",      f"{pnl_pct * 100:+.4f}%", pc),
        row("Unrealized PnL", d(unreal_pnl), pnl_col(unreal_pnl)),
        row("Fees Earned",    d(fees_earned, ".8f"), "#7c6df0"),
        row("Base Fee",       d(base_fee)),
        row("Quote Fee",      d(quote_fee)),
        row("Total Value",    d(total_value)),
        row("Filled Amount",  f"${filled:.4f}"),
        sep(),
        row("Side", side_str),
        row("LP Lower (config)",  d(lower_cfg)),
        row("LP Upper (config)",  d(upper_cfg)),
        row("LP Lower (actual)",  d(lower_actual)),
        row("LP Upper (actual)",  d(upper_actual)),
        row("Current Price",      d(cur_price)),
        row("Position Offset %",  f"{offset_pct:.4f}%" if offset_pct is not None else "—"),
        sep(),
        row("Initial Base",   d(init_base, ".8f")),
        row("Initial Quote",  d(init_quote, ".8f")),
        row("Base (final)",   d(base_cur, ".8f")),
        row("Quote (final)",  d(quote_cur, ".8f")),
        sep(),
        row("Position Rent",    f"{pos_rent:.8f} SOL" if pos_rent is not None else "—", "#e85d75"),
        row("Rent Refunded",    f"{rent_ref:.8f} SOL" if rent_ref is not None else "—", "#4ecdc4"),
        row("TX Fee",           f"{tx_fee:.8f} SOL" if tx_fee is not None else "—"),
        row("Max Retries Hit",  "yes" if max_retry else ("no" if max_retry is not None else "—"),
            "#e85d75" if max_retry else "#e8eaed"),
        sep(),
        row("Auto Close Above", f"{auto_above}s" if auto_above is not None else "—"),
        row("Auto Close Below", f"{auto_below}s" if auto_below is not None else "—"),
        row("Keep Position",    "yes" if keep_pos else ("no" if keep_pos is not None else "—")),
        sep(),
        row("Pool Address",     pool_link),
        row("Position Address", pos_link),
    ])

    lower_disp = f"{lp_lower:.6g}" if lp_lower is not None else "—"
    upper_disp = f"{lp_upper:.6g}" if lp_upper is not None else "—"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>LP Executor — {pair}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"></script>
<style>{DARK_CSS}</style>
</head>
<body>
<div class="container">
  <h1>{pair} — LP Executor</h1>
  <div class="subtitle">ID: {eid} · {connector} · {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>

  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Status</div>
      <div class="kpi-value" style="color:{sc};font-size:14px;">{status}</div>
      <div class="kpi-sub">{close_type or state}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Net PnL</div>
      <div class="kpi-value" style="color:{pc};">{pnl:+.6f}</div>
      <div class="kpi-sub">{pnl_pct * 100:+.4f}%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Fees Earned</div>
      <div class="kpi-value" style="color:#7c6df0;">{fees_earned:.6f}</div>
      <div class="kpi-sub">quote currency</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Duration</div>
      <div class="kpi-value" style="color:#e8eaed;font-size:15px;">{dur_str}</div>
      <div class="kpi-sub">OOR: {oor_str}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">LP Range</div>
      <div class="kpi-value" style="font-size:12px;color:#e8eaed;">{lower_disp} – {upper_disp}</div>
      <div class="kpi-sub">side {side_str.split('—')[0].strip()}</div>
    </div>
  </div>

  <div class="layout">
    <div>
      {price_section_html}
      {balance_html}
      <div class="section-title">PnL Breakdown</div>
      <div class="chart-wrap"><div class="chart-container" style="height:190px;">
        <canvas id="pnlChart"></canvas>
      </div></div>
    </div>
    <div>
      <div class="section-title">Position Summary</div>
      <table class="summary-table"><tbody>{table_rows}</tbody></table>
    </div>
  </div>

  <div class="footer">Hummingbot LP Executor · {eid[:16]}… · {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
</div>
<script>
{price_chart_js}
{balance_js}
(function() {{
  new Chart(document.getElementById('pnlChart').getContext('2d'), {{
    type:'bar',
    data:{{
      labels:{pnl_bkd_labels},
      datasets:[{{
        label:'Quote', data:{pnl_bkd_data},
        backgroundColor:{pnl_bkd_colors}, borderColor:{pnl_bkd_colors},
        borderWidth:1, borderRadius:4,
      }}]
    }},
    options:{{
      maintainAspectRatio:false, indexAxis:'y',
      plugins:{{legend:{{display:false}},
        tooltip:{{callbacks:{{label:(c)=>` ${{c.parsed.x.toFixed(8)}}`}}}}
      }},
      scales:{{
        x:{{ticks:{{color:'#6b7084',font:{{size:10}},callback:(v)=>v.toFixed(6)}},grid:{{color:'rgba(255,255,255,0.06)'}}}},
        y:{{ticks:{{color:'#8b8fa3',font:{{size:11}}}},grid:{{color:'rgba(255,255,255,0.03)'}}}}
      }}
    }}
  }});
}})();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Visualize a single LP executor as an HTML dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--id", dest="executor_id", required=True,
                        help="Executor ID")
    parser.add_argument("--output", "-o",
                        help="Output HTML path (default: data/lp_executor_<id[:10]>_<ts>.html)")
    parser.add_argument("--no-open", action="store_true",
                        help="Don't auto-open in browser")
    args = parser.parse_args()

    cfg  = get_api_config()
    hdrs = {"Authorization": make_auth_header(cfg)}

    print(f"Fetching executor {args.executor_id} from {cfg['url']} ...")
    try:
        ex = fetch_executor(cfg["url"], hdrs, args.executor_id)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not ex:
        print("Executor not found.", file=sys.stderr)
        return 1

    pair       = _s(ex.get("trading_pair"))
    created_ts = parse_ts(ex.get("created_at"))
    close_ts   = _f(ex.get("close_timestamp")) or parse_ts(ex.get("closed_at"))

    # Fetch candles
    candles = None
    if pair and created_ts:
        end = close_ts if close_ts else int(time.time()) + 300
        print(f"Fetching 5m candles for {pair} from KuCoin ...")
        candles = fetch_candles(cfg["url"], hdrs, pair,
                                start_time=created_ts - 300,
                                end_time=end + 300)
        if candles:
            print(f"  {len(candles)} candles loaded.")
        else:
            print("  No candles — price chart skipped.")

    print("Building dashboard ...")
    html = build_html(ex, candles)

    output_path = args.output
    if not output_path:
        os.makedirs("data", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/lp_executor_{args.executor_id[:10]}_{ts}.html"

    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(html)
    print(f"Dashboard written to: {output_path}")

    if not args.no_open:
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
        print("Opened in browser.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
