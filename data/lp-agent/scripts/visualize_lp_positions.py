#!/usr/bin/env python3
"""
Generate an interactive HTML dashboard from LP position events (RangePositionUpdate table).

Groups ADD/REMOVE events by position_address to show complete position lifecycle.
Drill down on individual positions to see details.

Usage:
    python visualize_lp_positions.py --pair <trading_pair> [--connector NAME] [--hours N] [--db <path>] [--output <path>] [--no-open]

Examples:
    python visualize_lp_positions.py --pair SOL-USDC              # all connectors for SOL-USDC
    python visualize_lp_positions.py --pair SOL-USDC --connector orca/clmm   # orca only
    python visualize_lp_positions.py --pair SOL-USDC --hours 12   # last 12 hours
    python visualize_lp_positions.py --pair SOL-USDC --connector orca/clmm --hours 6
    python visualize_lp_positions.py --pair SOL-USDC --db data/my.sqlite
    python visualize_lp_positions.py --pair SOL-USDC --output report.html
"""

import argparse
import json
import os
import sqlite3
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def find_db_with_lp_positions(data_dir: str = "data") -> str:
    """Find database with RangePositionUpdate data, prioritizing by row count."""
    data_path = Path(data_dir)
    if not data_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    candidates = []
    for db_file in data_path.glob("*.sqlite"):
        try:
            conn = sqlite3.connect(str(db_file))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='RangePositionUpdate'")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*) FROM RangePositionUpdate")
                count = cursor.fetchone()[0]
                if count > 0:
                    candidates.append((str(db_file), count))
            conn.close()
        except Exception:
            continue

    if not candidates:
        raise FileNotFoundError(f"No database with RangePositionUpdate data found in {data_dir}")

    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0][0]


def get_table_columns(cursor) -> set:
    """Get column names from RangePositionUpdate table."""
    cursor.execute("PRAGMA table_info(RangePositionUpdate)")
    return {row[1] for row in cursor.fetchall()}


def query_positions(db_path: str, connector: Optional[str] = None, trading_pair: Optional[str] = None, lookback_hours: Optional[float] = None) -> list[dict]:
    """Query LP position events and group by position_address."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get available columns
    available_cols = get_table_columns(cursor)

    # Build query
    base_cols = ["id", "hb_id", "timestamp", "tx_hash", "trade_fee",
                 "config_file_path", "order_action", "trading_pair", "position_address",
                 "lower_price", "upper_price", "mid_price", "base_amount", "quote_amount",
                 "base_fee", "quote_fee"]
    optional_cols = ["market", "position_rent", "position_rent_refunded", "trade_fee_in_quote"]

    select_cols = [c for c in base_cols if c in available_cols]
    for col in optional_cols:
        if col in available_cols:
            select_cols.append(col)

    query = f"SELECT {', '.join(select_cols)} FROM RangePositionUpdate WHERE 1=1"
    params = []

    if connector and "market" in available_cols:
        query += " AND market = ?"
        params.append(connector)

    if trading_pair:
        query += " AND trading_pair = ?"
        params.append(trading_pair)

    if lookback_hours:
        # timestamp is in milliseconds
        cutoff_ms = int((time.time() - lookback_hours * 3600) * 1000)
        query += " AND timestamp >= ?"
        params.append(cutoff_ms)

    query += " ORDER BY timestamp ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return []

    # Convert to list of dicts
    events = []
    for row in rows:
        event = dict(zip(select_cols, row))
        # Convert timestamp from ms to seconds
        if event.get("timestamp"):
            event["timestamp_ms"] = event["timestamp"]
            event["timestamp"] = event["timestamp"] / 1000
        events.append(event)

    # Group events by position_address
    positions_map = {}
    for event in events:
        pos_addr = event.get("position_address") or "unknown"
        if pos_addr not in positions_map:
            positions_map[pos_addr] = {"address": pos_addr, "events": []}
        positions_map[pos_addr]["events"].append(event)

    # Build position records
    positions = []
    for pos_addr, pos_data in positions_map.items():
        events = pos_data["events"]
        add_event = next((e for e in events if e.get("order_action") == "ADD"), None)
        remove_event = next((e for e in events if e.get("order_action") == "REMOVE"), None)

        if not add_event:
            continue  # Skip positions without ADD event

        # Calculate PnL
        add_base = _float(add_event.get("base_amount"))
        add_quote = _float(add_event.get("quote_amount"))
        add_price = _float(add_event.get("mid_price"))
        add_value = add_base * add_price + add_quote if add_price else add_quote

        remove_base = _float(remove_event.get("base_amount")) if remove_event else 0
        remove_quote = _float(remove_event.get("quote_amount")) if remove_event else 0
        remove_price = _float(remove_event.get("mid_price")) if remove_event else add_price
        remove_value = remove_base * remove_price + remove_quote if remove_price else remove_quote

        base_fee = _float(remove_event.get("base_fee")) if remove_event else 0
        quote_fee = _float(remove_event.get("quote_fee")) if remove_event else 0
        fees_quote = base_fee * remove_price + quote_fee if remove_price else quote_fee

        # IL = (remove_value - add_value) without fees
        # PnL = IL + fees
        il = remove_value - add_value if remove_event else 0
        pnl = il + fees_quote

        # Rent
        rent_paid = _float(add_event.get("position_rent", 0))
        rent_refunded = _float(remove_event.get("position_rent_refunded", 0)) if remove_event else 0

        # Transaction fees (in quote currency)
        add_tx_fee = _float(add_event.get("trade_fee_in_quote", 0))
        remove_tx_fee = _float(remove_event.get("trade_fee_in_quote", 0)) if remove_event else 0
        total_tx_fee = add_tx_fee + remove_tx_fee

        # Duration
        add_ts = add_event.get("timestamp", 0)
        remove_ts = remove_event.get("timestamp", 0) if remove_event else 0
        duration = int(remove_ts - add_ts) if remove_ts > add_ts else 0

        # Determine status
        status = "CLOSED" if remove_event else "OPEN"

        positions.append({
            "address": pos_addr,
            "trading_pair": add_event.get("trading_pair", ""),
            "connector": add_event.get("market", ""),
            "config_file": add_event.get("config_file_path", ""),

            # Timing
            "add_ts": add_ts,
            "add_datetime": datetime.fromtimestamp(add_ts).strftime("%Y-%m-%d %H:%M:%S") if add_ts else "",
            "remove_ts": remove_ts,
            "remove_datetime": datetime.fromtimestamp(remove_ts).strftime("%Y-%m-%d %H:%M:%S") if remove_ts else "",
            "duration": duration,
            "status": status,

            # Price bounds
            "lower_price": _float(add_event.get("lower_price")),
            "upper_price": _float(add_event.get("upper_price")),
            "add_price": add_price,
            "remove_price": remove_price,

            # Amounts at ADD
            "add_base": add_base,
            "add_quote": add_quote,
            "add_value": add_value,

            # Amounts at REMOVE
            "remove_base": remove_base,
            "remove_quote": remove_quote,
            "remove_value": remove_value,

            # Fees
            "base_fee": base_fee,
            "quote_fee": quote_fee,
            "fees_quote": fees_quote,

            # PnL
            "il": il,
            "pnl": pnl,
            "pnl_pct": (pnl / add_value * 100) if add_value > 0 else 0,

            # Rent & tx fees
            "rent_paid": rent_paid,
            "rent_refunded": rent_refunded,
            "tx_fee_quote": total_tx_fee,

            # TX hashes
            "add_tx": add_event.get("tx_hash", ""),
            "remove_tx": remove_event.get("tx_hash", "") if remove_event else "",

            # Raw events for detail view
            "events": events,
        })

    # Sort by add timestamp (newest first)
    positions.sort(key=lambda p: p["add_ts"], reverse=True)

    return positions


# ---------------------------------------------------------------------------
# Transform to chart data
# ---------------------------------------------------------------------------

def positions_to_chart_data(positions: list[dict]) -> list[dict]:
    """Convert position records into chart-ready JSON."""
    # Sort chronologically for cumulative calculation
    sorted_positions = sorted(positions, key=lambda p: p["add_ts"])

    cum_pnl = 0.0
    cum_fees = 0.0
    records = []

    for idx, p in enumerate(sorted_positions):
        pnl = p["pnl"]
        fees = p["fees_quote"]

        # Only add to cumulative if position is closed
        if p["status"] == "CLOSED":
            cum_pnl += pnl
            cum_fees += fees

        # Determine side: BUY if more quote (expecting to buy base), SELL if more base
        # Compare quote value vs base value at time of ADD
        add_base_value = p["add_base"] * p["add_price"] if p["add_price"] else 0
        side = "BUY" if p["add_quote"] > add_base_value else "SELL"

        records.append({
            "idx": idx,
            "address": p["address"],
            "trading_pair": p["trading_pair"],
            "connector": p["connector"],
            "side": side,

            # Timing
            "add_ts": p["add_datetime"].replace(" ", "T") if p["add_datetime"] else "",
            "remove_ts": p["remove_datetime"].replace(" ", "T") if p["remove_datetime"] else "",
            "dur": p["duration"],
            "status": p["status"],

            # Prices
            "lower": round(p["lower_price"], 6),
            "upper": round(p["upper_price"], 6),
            "add_price": round(p["add_price"], 6),
            "remove_price": round(p["remove_price"], 6),

            # Amounts
            "add_base": round(p["add_base"], 6),
            "add_quote": round(p["add_quote"], 6),
            "add_value": round(p["add_value"], 4),
            "remove_base": round(p["remove_base"], 6),
            "remove_quote": round(p["remove_quote"], 6),
            "remove_value": round(p["remove_value"], 4),

            # Fees
            "base_fee": round(p["base_fee"], 6),
            "quote_fee": round(p["quote_fee"], 6),
            "fees": round(fees, 6),
            "cum_fees": round(cum_fees, 6),

            # PnL
            "il": round(p["il"], 6),
            "pnl": round(pnl, 6),
            "pnl_pct": round(p["pnl_pct"], 4),
            "cum_pnl": round(cum_pnl, 6),

            # Rent & tx fees
            "rent_paid": round(p["rent_paid"], 6),
            "rent_refunded": round(p["rent_refunded"], 6),
            "tx_fee_quote": round(p["tx_fee_quote"], 6),

            # TX
            "add_tx": p["add_tx"],
            "remove_tx": p["remove_tx"],
        })

    return records


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def generate_html(chart_data: list[dict], meta: dict) -> str:
    """Build a self-contained HTML file with the dashboard."""
    data_json = json.dumps(chart_data)
    meta_json = json.dumps(meta)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>LP Positions Dashboard — {meta.get("trading_pair", "")}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0f1019; color: #e8eaed; font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace; }}
  #root {{ min-height: 100vh; }}
</style>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
<script src="https://cdnjs.cloudflare.com/ajax/libs/react/18.2.0/umd/react.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/18.2.0/umd/react-dom.production.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prop-types/15.8.1/prop-types.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/recharts/2.12.7/Recharts.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/babel-standalone/7.23.9/babel.min.js"></script>
</head>
<body>
<div id="root"></div>
<script>
  window.__LP_DATA__ = {data_json};
  window.__LP_META__ = {meta_json};
</script>
<script type="text/babel">
{DASHBOARD_JSX}
</script>
</body>
</html>"""


DASHBOARD_JSX = r"""
const { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ComposedChart, Line, ReferenceArea } = Recharts;

const DATA = window.__LP_DATA__;
const META = window.__LP_META__;

const fmt = (n, d = 4) => n?.toFixed(d) ?? "—";
const fmtTime = (ts) => {
  if (!ts) return "";
  const d = new Date(ts);
  return d.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
};
const fmtDateTime = (iso) => iso ? iso.replace("T", " ") : "—";
const fmtDuration = (s) => {
  if (!s) return "0s";
  if (s < 60) return `${s}s`;
  if (s < 3600) return `${Math.floor(s/60)}m ${s%60}s`;
  return `${Math.floor(s/3600)}h ${Math.floor((s%3600)/60)}m`;
};
const shortenAddr = (addr) => addr ? `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}` : "—";

function StatCard({ label, value, sub, accent }) {
  return React.createElement("div", {
    style: {
      background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)",
      borderRadius: 10, padding: "14px 18px", minWidth: 0,
    }
  },
    React.createElement("div", {
      style: { fontSize: 11, color: "#8b8fa3", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 6 }
    }, label),
    React.createElement("div", {
      style: { fontSize: 22, fontWeight: 600, color: accent || "#e8eaed" }
    }, value),
    sub && React.createElement("div", { style: { fontSize: 11, color: "#6b7084", marginTop: 4 } }, sub)
  );
}

function SectionTitle({ children }) {
  return React.createElement("h3", {
    style: {
      fontSize: 13, fontWeight: 600, color: "#8b8fa3", textTransform: "uppercase",
      letterSpacing: "0.08em", margin: "32px 0 14px",
    }
  }, children);
}

function DetailRow({ label, value, color, mono }) {
  const e = React.createElement;
  return e("div", { style: { display: "flex", justifyContent: "space-between", padding: "4px 0", borderBottom: "1px solid rgba(255,255,255,0.03)" } },
    e("span", { style: { color: "#6b7084", fontSize: 11 } }, label),
    e("span", { style: { color: color || "#e8eaed", fontSize: 11, fontWeight: 500, fontFamily: mono ? "monospace" : "inherit", wordBreak: mono ? "break-all" : "normal" } }, value)
  );
}

function PositionDetail({ position, onClose }) {
  const e = React.createElement;
  if (!position) return null;

  const d = position;
  const pnlColor = d.pnl >= 0 ? "#4ecdc4" : "#e85d75";

  return e("div", {
    style: {
      position: "fixed", top: 0, right: 0, width: 420, height: "100vh",
      background: "#12141f", borderLeft: "1px solid rgba(255,255,255,0.08)",
      overflowY: "auto", zIndex: 1000, boxShadow: "-4px 0 20px rgba(0,0,0,0.3)",
    }
  },
    // Header
    e("div", { style: { padding: "16px 20px", borderBottom: "1px solid rgba(255,255,255,0.06)", display: "flex", alignItems: "center", justifyContent: "space-between", position: "sticky", top: 0, background: "#12141f", zIndex: 1 } },
      e("div", null,
        e("div", { style: { fontSize: 14, fontWeight: 600, color: "#e8eaed" } }, `Position #${d.idx + 1}`),
        e("div", { style: { fontSize: 10, color: "#555870", marginTop: 2, fontFamily: "monospace" } }, shortenAddr(d.address))
      ),
      e("button", {
        onClick: onClose,
        style: { background: "none", border: "none", color: "#6b7084", fontSize: 20, cursor: "pointer", padding: "4px 8px" }
      }, "×")
    ),

    // Content
    e("div", { style: { padding: "16px 20px" } },
      // Trading pair and connector prominent
      e("div", { style: { marginBottom: 16 } },
        e("div", { style: { fontSize: 20, fontWeight: 700, color: "#4ecdc4", marginBottom: 4 } }, d.trading_pair),
        e("div", { style: { fontSize: 12, color: "#8b8fa3" } }, d.connector || "Unknown connector"),
      ),
      // Status badges
      e("div", { style: { display: "flex", gap: 8, marginBottom: 16 } },
        e("span", { style: { fontSize: 10, padding: "3px 10px", borderRadius: 12, background: d.status === "CLOSED" ? "rgba(78,205,196,0.1)" : "rgba(240,198,68,0.1)", color: d.status === "CLOSED" ? "#4ecdc4" : "#f0c644" } }, d.status),
        e("span", { style: { fontSize: 10, padding: "3px 10px", borderRadius: 12, background: d.side === "BUY" ? "rgba(78,205,196,0.15)" : "rgba(232,93,117,0.15)", color: d.side === "BUY" ? "#4ecdc4" : "#e85d75" } }, d.side),
      ),

      // PnL highlight
      e("div", { style: { background: "rgba(255,255,255,0.02)", borderRadius: 10, padding: "16px", marginBottom: 16, textAlign: "center" } },
        e("div", { style: { fontSize: 11, color: "#6b7084", marginBottom: 4 } }, "Net PnL"),
        e("div", { style: { fontSize: 28, fontWeight: 700, color: pnlColor } }, `$${fmt(d.pnl, 6)}`),
        e("div", { style: { fontSize: 12, color: pnlColor, marginTop: 4 } }, `${fmt(d.pnl_pct, 4)}%`)
      ),

      // Timing section
      e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8, marginTop: 16 } }, "TIMING"),
      e(DetailRow, { label: "Opened", value: fmtDateTime(d.add_ts) }),
      e(DetailRow, { label: "Closed", value: d.remove_ts ? fmtDateTime(d.remove_ts) : "Still open" }),
      e(DetailRow, { label: "Duration", value: fmtDuration(d.dur) }),

      // Price section
      e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8, marginTop: 20 } }, "PRICE BOUNDS"),
      e(DetailRow, { label: "Lower Price", value: fmt(d.lower, 6) }),
      e(DetailRow, { label: "Upper Price", value: fmt(d.upper, 6) }),
      e(DetailRow, { label: "Price at ADD", value: fmt(d.add_price, 6) }),
      e(DetailRow, { label: "Price at REMOVE", value: d.remove_ts ? fmt(d.remove_price, 6) : "—" }),

      // ADD LIQUIDITY section
      e("div", { style: { fontSize: 11, fontWeight: 600, color: "#4ecdc4", marginBottom: 8, marginTop: 20, display: "flex", alignItems: "center", justifyContent: "space-between" } },
        e("span", null, "ADD LIQUIDITY"),
        d.add_tx && e("a", {
          href: `https://solscan.io/tx/${d.add_tx}`,
          target: "_blank",
          rel: "noopener noreferrer",
          style: { fontSize: 10, color: "#7c6df0", textDecoration: "none" }
        }, "View TX ↗")
      ),
      e(DetailRow, { label: "Base Amount", value: fmt(d.add_base, 6) }),
      e(DetailRow, { label: "Quote Amount", value: fmt(d.add_quote, 6) }),
      e(DetailRow, { label: "Total Value", value: `$${fmt(d.add_value, 4)}` }),
      e(DetailRow, { label: "Price", value: fmt(d.add_price, 6) }),

      // REMOVE LIQUIDITY section
      d.status === "CLOSED" && e("div", null,
        e("div", { style: { fontSize: 11, fontWeight: 600, color: "#e85d75", marginBottom: 8, marginTop: 20, display: "flex", alignItems: "center", justifyContent: "space-between" } },
          e("span", null, "REMOVE LIQUIDITY"),
          d.remove_tx && e("a", {
            href: `https://solscan.io/tx/${d.remove_tx}`,
            target: "_blank",
            rel: "noopener noreferrer",
            style: { fontSize: 10, color: "#7c6df0", textDecoration: "none" }
          }, "View TX ↗")
        ),
        e(DetailRow, { label: "Base Amount", value: fmt(d.remove_base, 6) }),
        e(DetailRow, { label: "Quote Amount", value: fmt(d.remove_quote, 6) }),
        e(DetailRow, { label: "Total Value", value: `$${fmt(d.remove_value, 4)}` }),
        e(DetailRow, { label: "Price", value: fmt(d.remove_price, 6) }),
      ),

      // Fees section
      e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8, marginTop: 20 } }, "FEES EARNED"),
      e(DetailRow, { label: "Base Fee", value: fmt(d.base_fee, 6) }),
      e(DetailRow, { label: "Quote Fee", value: fmt(d.quote_fee, 6) }),
      e(DetailRow, { label: "Total Fees (Quote)", value: `$${fmt(d.fees, 6)}`, color: "#7c6df0" }),

      // PnL breakdown
      e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8, marginTop: 20 } }, "PNL BREAKDOWN"),
      e(DetailRow, { label: "IL (value change)", value: `$${fmt(d.il, 6)}`, color: d.il >= 0 ? "#4ecdc4" : "#e85d75" }),
      e(DetailRow, { label: "Fees Earned", value: `$${fmt(d.fees, 6)}`, color: "#7c6df0" }),
      e(DetailRow, { label: "Net PnL", value: `$${fmt(d.pnl, 6)}`, color: pnlColor }),

      // Rent & tx fee section
      (d.rent_paid > 0 || d.rent_refunded > 0 || d.tx_fee_quote > 0) && e("div", null,
        e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8, marginTop: 20 } }, "RENT & TX FEES"),
        e(DetailRow, { label: "Rent Paid", value: `${fmt(d.rent_paid, 6)} SOL`, color: "#e85d75" }),
        e(DetailRow, { label: "Rent Refunded", value: `${fmt(d.rent_refunded, 6)} SOL`, color: "#4ecdc4" }),
        d.tx_fee_quote > 0 && e(DetailRow, { label: "Transaction Fees", value: `$${fmt(d.tx_fee_quote, 6)}`, color: "#f0c644" }),
      ),

      // Cumulative at close
      d.status === "CLOSED" && e("div", null,
        e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8, marginTop: 20 } }, "CUMULATIVE AT CLOSE"),
        e(DetailRow, { label: "Cumulative PnL", value: `$${fmt(d.cum_pnl, 6)}`, color: d.cum_pnl >= 0 ? "#4ecdc4" : "#e85d75" }),
        e(DetailRow, { label: "Cumulative Fees", value: `$${fmt(d.cum_fees, 6)}`, color: "#7c6df0" }),
      ),

      // Position address
      e("div", { style: { marginTop: 20 } },
        e("div", { style: { fontSize: 11, fontWeight: 600, color: "#8b8fa3", marginBottom: 8 } }, "POSITION ADDRESS"),
        e("div", { style: { fontSize: 10, color: "#555870", fontFamily: "monospace", wordBreak: "break-all" } }, d.address)
      ),
    )
  );
}

function PositionTable({ data, selectedIdx, onSelect }) {
  const e = React.createElement;
  const [sortKey, setSortKey] = React.useState("idx");
  const [sortDir, setSortDir] = React.useState(-1);  // Newest first
  const [filterStatus, setFilterStatus] = React.useState("all");
  const [filterSide, setFilterSide] = React.useState("all");
  const [filterConnector, setFilterConnector] = React.useState("all");

  // Get unique connectors from data
  const connectors = React.useMemo(() => {
    const set = new Set(data.map(d => d.connector).filter(Boolean));
    return Array.from(set).sort();
  }, [data]);

  const filtered = React.useMemo(() => {
    let result = [...data];
    if (filterStatus !== "all") result = result.filter(d => d.status === filterStatus);
    if (filterSide !== "all") result = result.filter(d => d.side === filterSide);
    if (filterConnector !== "all") result = result.filter(d => d.connector === filterConnector);
    result.sort((a, b) => (a[sortKey] > b[sortKey] ? 1 : -1) * sortDir);
    return result;
  }, [data, filterStatus, filterSide, filterConnector, sortKey, sortDir]);

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(-sortDir);
    else { setSortKey(key); setSortDir(1); }
  };

  const thStyle = { padding: "8px 6px", textAlign: "left", fontSize: 10, color: "#6b7084", cursor: "pointer", userSelect: "none", borderBottom: "1px solid rgba(255,255,255,0.06)" };
  const tdStyle = { padding: "8px 6px", fontSize: 11, borderBottom: "1px solid rgba(255,255,255,0.03)" };

  const sortIcon = (key) => sortKey === key ? (sortDir === 1 ? " ↑" : " ↓") : "";

  const filterBtn = (value, label, currentFilter, setFilter) => e("button", {
    onClick: () => setFilter(value),
    style: {
      fontSize: 9, padding: "3px 8px", borderRadius: 10, cursor: "pointer", fontFamily: "inherit",
      border: `1px solid ${currentFilter === value ? "#4ecdc4" : "rgba(255,255,255,0.08)"}`,
      background: currentFilter === value ? "rgba(78,205,196,0.12)" : "transparent",
      color: currentFilter === value ? "#4ecdc4" : "#6b7084", marginRight: 4,
    }
  }, label);

  return e("div", null,
    // Filters
    e("div", { style: { display: "flex", gap: 16, marginBottom: 12, flexWrap: "wrap" } },
      connectors.length > 1 && e("div", { style: { display: "flex", alignItems: "center", gap: 4 } },
        e("span", { style: { fontSize: 10, color: "#555870", marginRight: 4 } }, "Connector:"),
        filterBtn("all", "All", filterConnector, setFilterConnector),
        ...connectors.map(c => filterBtn(c, c.split("/")[0], filterConnector, setFilterConnector))
      ),
      e("div", { style: { display: "flex", alignItems: "center", gap: 4 } },
        e("span", { style: { fontSize: 10, color: "#555870", marginRight: 4 } }, "Side:"),
        filterBtn("all", "All", filterSide, setFilterSide),
        filterBtn("BUY", "Buy", filterSide, setFilterSide),
        filterBtn("SELL", "Sell", filterSide, setFilterSide),
      ),
      e("div", { style: { display: "flex", alignItems: "center", gap: 4 } },
        e("span", { style: { fontSize: 10, color: "#555870", marginRight: 4 } }, "Status:"),
        filterBtn("all", "All", filterStatus, setFilterStatus),
        filterBtn("CLOSED", "Closed", filterStatus, setFilterStatus),
        filterBtn("OPEN", "Open", filterStatus, setFilterStatus),
      ),
      e("span", { style: { fontSize: 10, color: "#555870", marginLeft: "auto" } }, `${filtered.length} positions`)
    ),

    // Table
    e("div", { style: { overflowX: "auto", background: "rgba(255,255,255,0.02)", borderRadius: 10, border: "1px solid rgba(255,255,255,0.05)" } },
      e("table", { style: { width: "100%", borderCollapse: "collapse", minWidth: 900 } },
        e("thead", null,
          e("tr", null,
            e("th", { style: thStyle, onClick: () => handleSort("idx") }, "#" + sortIcon("idx")),
            e("th", { style: thStyle, onClick: () => handleSort("side") }, "Side" + sortIcon("side")),
            e("th", { style: thStyle, onClick: () => handleSort("connector") }, "Connector" + sortIcon("connector")),
            e("th", { style: thStyle, onClick: () => handleSort("add_ts") }, "Opened" + sortIcon("add_ts")),
            e("th", { style: thStyle, onClick: () => handleSort("dur") }, "Duration" + sortIcon("dur")),
            e("th", { style: thStyle, onClick: () => handleSort("add_value") }, "Value" + sortIcon("add_value")),
            e("th", { style: thStyle, onClick: () => handleSort("pnl") }, "PnL" + sortIcon("pnl")),
            e("th", { style: thStyle, onClick: () => handleSort("pnl_pct") }, "PnL %" + sortIcon("pnl_pct")),
            e("th", { style: thStyle, onClick: () => handleSort("fees") }, "Fees" + sortIcon("fees")),
            e("th", { style: thStyle }, "Status"),
          )
        ),
        e("tbody", null,
          ...filtered.map(d => e("tr", {
            key: d.idx,
            onClick: () => onSelect(d.idx),
            style: {
              cursor: "pointer",
              background: selectedIdx === d.idx ? "rgba(78,205,196,0.08)" : "transparent",
              transition: "background 0.15s",
            },
            onMouseEnter: (ev) => ev.currentTarget.style.background = selectedIdx === d.idx ? "rgba(78,205,196,0.12)" : "rgba(255,255,255,0.02)",
            onMouseLeave: (ev) => ev.currentTarget.style.background = selectedIdx === d.idx ? "rgba(78,205,196,0.08)" : "transparent",
          },
            e("td", { style: { ...tdStyle, color: "#8b8fa3" } }, d.idx + 1),
            e("td", { style: { ...tdStyle, color: d.side === "BUY" ? "#4ecdc4" : "#e85d75", fontWeight: 500 } }, d.side),
            e("td", { style: { ...tdStyle, fontSize: 10 } }, d.connector ? d.connector.split("/")[0] : "—"),
            e("td", { style: { ...tdStyle, fontFamily: "monospace", fontSize: 10 } }, fmtDateTime(d.add_ts)),
            e("td", { style: tdStyle }, fmtDuration(d.dur)),
            e("td", { style: tdStyle }, `$${fmt(d.add_value, 2)}`),
            e("td", { style: { ...tdStyle, color: d.pnl >= 0 ? "#4ecdc4" : "#e85d75", fontWeight: 500 } }, `$${fmt(d.pnl, 4)}`),
            e("td", { style: { ...tdStyle, color: d.pnl_pct >= 0 ? "#4ecdc4" : "#e85d75" } }, `${fmt(d.pnl_pct, 3)}%`),
            e("td", { style: { ...tdStyle, color: "#7c6df0" } }, `$${fmt(d.fees, 4)}`),
            e("td", { style: tdStyle },
              e("span", { style: { fontSize: 9, padding: "2px 6px", borderRadius: 8, background: d.status === "CLOSED" ? "rgba(78,205,196,0.1)" : "rgba(240,198,68,0.1)", color: d.status === "CLOSED" ? "#4ecdc4" : "#f0c644" } }, d.status)
            ),
          ))
        )
      )
    )
  );
}

// Custom chart component for position ranges with price line
function PositionRangeChart({ data, onSelectPosition, tradingPair }) {
  const e = React.createElement;
  const containerRef = React.useRef(null);
  const [dimensions, setDimensions] = React.useState({ width: 0, height: 400 });

  React.useEffect(() => {
    if (containerRef.current) {
      const resizeObserver = new ResizeObserver(entries => {
        for (let entry of entries) {
          setDimensions({ width: entry.contentRect.width, height: 400 });
        }
      });
      resizeObserver.observe(containerRef.current);
      return () => resizeObserver.disconnect();
    }
  }, []);

  const { width, height } = dimensions;
  const margin = { top: 20, right: 60, bottom: 40, left: 70 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Compute time and price domains
  const { minTime, maxTime, minPrice, maxPrice, pricePoints } = React.useMemo(() => {
    if (!data.length) return { minTime: 0, maxTime: 1, minPrice: 0, maxPrice: 1, pricePoints: [] };

    let minT = Infinity, maxT = -Infinity;
    let minP = Infinity, maxP = -Infinity;
    const points = [];

    data.forEach(d => {
      const addTs = new Date(d.add_ts).getTime();
      const removeTs = d.remove_ts ? new Date(d.remove_ts).getTime() : Date.now();

      minT = Math.min(minT, addTs);
      maxT = Math.max(maxT, removeTs);
      minP = Math.min(minP, d.lower, d.add_price);
      maxP = Math.max(maxP, d.upper, d.add_price);

      // Add price points for the line
      points.push({ time: addTs, price: d.add_price });
      if (d.remove_ts && d.remove_price) {
        points.push({ time: removeTs, price: d.remove_price });
        minP = Math.min(minP, d.remove_price);
        maxP = Math.max(maxP, d.remove_price);
      }
    });

    // Sort price points by time
    points.sort((a, b) => a.time - b.time);

    // Add padding to price range
    const priceRange = maxP - minP;
    minP -= priceRange * 0.05;
    maxP += priceRange * 0.05;

    return { minTime: minT, maxTime: maxT, minPrice: minP, maxPrice: maxP, pricePoints: points };
  }, [data]);

  // Scale functions
  const xScale = (t) => margin.left + ((t - minTime) / (maxTime - minTime)) * innerWidth;
  const yScale = (p) => margin.top + innerHeight - ((p - minPrice) / (maxPrice - minPrice)) * innerHeight;

  // Generate Y axis ticks
  const yTicks = React.useMemo(() => {
    const ticks = [];
    const range = maxPrice - minPrice;
    const step = range / 5;
    for (let i = 0; i <= 5; i++) {
      ticks.push(minPrice + step * i);
    }
    return ticks;
  }, [minPrice, maxPrice]);

  // Generate X axis ticks
  const xTicks = React.useMemo(() => {
    const ticks = [];
    const range = maxTime - minTime;
    const step = range / 6;
    for (let i = 0; i <= 6; i++) {
      ticks.push(minTime + step * i);
    }
    return ticks;
  }, [minTime, maxTime]);

  // Build price line path
  const pricePath = React.useMemo(() => {
    if (pricePoints.length < 2) return "";
    return pricePoints.map((p, i) =>
      `${i === 0 ? "M" : "L"} ${xScale(p.time)} ${yScale(p.price)}`
    ).join(" ");
  }, [pricePoints, xScale, yScale]);

  if (width === 0) {
    return e("div", { ref: containerRef, style: { width: "100%", height: 400 } });
  }

  return e("div", { ref: containerRef, style: { width: "100%", height: 400, background: "rgba(255,255,255,0.02)", borderRadius: 10, border: "1px solid rgba(255,255,255,0.05)" } },
    e("svg", { width, height, style: { display: "block" } },
      // Grid lines
      ...yTicks.map((tick, i) => e("line", {
        key: `y-${i}`,
        x1: margin.left,
        y1: yScale(tick),
        x2: width - margin.right,
        y2: yScale(tick),
        stroke: "rgba(255,255,255,0.04)",
        strokeDasharray: "3,3"
      })),
      ...xTicks.map((tick, i) => e("line", {
        key: `x-${i}`,
        x1: xScale(tick),
        y1: margin.top,
        x2: xScale(tick),
        y2: height - margin.bottom,
        stroke: "rgba(255,255,255,0.04)",
        strokeDasharray: "3,3"
      })),

      // Position range bars
      ...data.map((d, i) => {
        const addTs = new Date(d.add_ts).getTime();
        const removeTs = d.remove_ts ? new Date(d.remove_ts).getTime() : Date.now();
        const x1 = xScale(addTs);
        const x2 = xScale(removeTs);
        const y1 = yScale(d.upper);
        const y2 = yScale(d.lower);
        const fillColor = d.side === "BUY" ? "rgba(78,205,196,0.25)" : "rgba(232,93,117,0.25)";
        const strokeColor = d.side === "BUY" ? "#4ecdc4" : "#e85d75";

        return e("rect", {
          key: `pos-${i}`,
          x: x1,
          y: y1,
          width: Math.max(x2 - x1, 2),
          height: Math.max(y2 - y1, 1),
          fill: fillColor,
          stroke: strokeColor,
          strokeWidth: 1,
          strokeOpacity: 0.5,
          cursor: "pointer",
          onClick: () => onSelectPosition(d.idx),
        });
      }),

      // Price line
      e("path", {
        d: pricePath,
        fill: "none",
        stroke: "#f0c644",
        strokeWidth: 2,
        strokeLinejoin: "round",
        strokeLinecap: "round",
      }),

      // Price dots at position open/close
      ...pricePoints.map((p, i) => e("circle", {
        key: `dot-${i}`,
        cx: xScale(p.time),
        cy: yScale(p.price),
        r: 3,
        fill: "#f0c644",
      })),

      // Y axis
      e("line", { x1: margin.left, y1: margin.top, x2: margin.left, y2: height - margin.bottom, stroke: "rgba(255,255,255,0.1)" }),
      ...yTicks.map((tick, i) => e("text", {
        key: `yl-${i}`,
        x: margin.left - 8,
        y: yScale(tick),
        fill: "#555870",
        fontSize: 10,
        textAnchor: "end",
        dominantBaseline: "middle",
      }, tick.toFixed(tick > 100 ? 0 : tick > 1 ? 2 : 4))),

      // X axis
      e("line", { x1: margin.left, y1: height - margin.bottom, x2: width - margin.right, y2: height - margin.bottom, stroke: "rgba(255,255,255,0.1)" }),
      ...xTicks.map((tick, i) => e("text", {
        key: `xl-${i}`,
        x: xScale(tick),
        y: height - margin.bottom + 16,
        fill: "#555870",
        fontSize: 10,
        textAnchor: "middle",
      }, fmtTime(tick))),

      // Y axis label
      e("text", {
        x: 14,
        y: height / 2,
        fill: "#6b7084",
        fontSize: 11,
        textAnchor: "middle",
        transform: `rotate(-90, 14, ${height / 2})`,
      }, `${tradingPair} Price`),

      // Legend
      e("line", { x1: width - margin.right - 200, y1: margin.top + 6, x2: width - margin.right - 180, y2: margin.top + 6, stroke: "#f0c644", strokeWidth: 2 }),
      e("text", { x: width - margin.right - 175, y: margin.top + 9, fill: "#8b8fa3", fontSize: 10 }, `${tradingPair} Price`),
      e("rect", { x: width - margin.right - 95, y: margin.top, width: 12, height: 12, fill: "rgba(78,205,196,0.25)", stroke: "#4ecdc4", strokeWidth: 1 }),
      e("text", { x: width - margin.right - 78, y: margin.top + 9, fill: "#8b8fa3", fontSize: 10 }, "Buy"),
      e("rect", { x: width - margin.right - 40, y: margin.top, width: 12, height: 12, fill: "rgba(232,93,117,0.25)", stroke: "#e85d75", strokeWidth: 1 }),
      e("text", { x: width - margin.right - 23, y: margin.top + 9, fill: "#8b8fa3", fontSize: 10 }, "Sell"),
    )
  );
}

function App() {
  const [selectedIdx, setSelectedIdx] = React.useState(null);
  const [activeTab, setActiveTab] = React.useState("chart");
  const [showOpen, setShowOpen] = React.useState(false);
  const [filterConnector, setFilterConnector] = React.useState("all");

  // Get unique connectors
  const connectors = React.useMemo(() => {
    const set = new Set(DATA.map(d => d.connector).filter(Boolean));
    return Array.from(set).sort();
  }, []);

  // Filter by connector first
  const filteredData = React.useMemo(() => {
    if (filterConnector === "all") return DATA;
    return DATA.filter(d => d.connector === filterConnector);
  }, [filterConnector]);

  const closedPositions = React.useMemo(() => filteredData.filter(d => d.status === "CLOSED"), [filteredData]);
  const openPositions = React.useMemo(() => filteredData.filter(d => d.status === "OPEN"), [filteredData]);
  const chartData = React.useMemo(() => showOpen ? filteredData : closedPositions, [showOpen, filteredData, closedPositions]);

  const stats = React.useMemo(() => {
    const closed = closedPositions;
    const totalPnl = closed.reduce((s, d) => s + d.pnl, 0);
    const totalFees = closed.reduce((s, d) => s + d.fees, 0);
    const totalIL = closed.reduce((s, d) => s + d.il, 0);
    const totalValue = closed.reduce((s, d) => s + d.add_value, 0);
    const profitable = closed.filter(d => d.pnl > 0).length;
    const losing = closed.filter(d => d.pnl < 0).length;
    const totalRent = DATA.reduce((s, d) => s + d.rent_paid, 0);
    const maxPnl = closed.length ? Math.max(...closed.map(d => d.pnl)) : 0;
    const minPnl = closed.length ? Math.min(...closed.map(d => d.pnl)) : 0;
    const avgDur = closed.length ? closed.reduce((s, d) => s + d.dur, 0) / closed.length : 0;
    return { totalPnl, totalFees, totalIL, totalValue, profitable, losing, totalRent, maxPnl, minPnl, avgDur };
  }, [closedPositions]);

  const selectedPosition = selectedIdx !== null ? DATA[selectedIdx] : null;

  const e = React.createElement;

  const tabBtn = (v, label) => e("button", {
    key: v, onClick: () => setActiveTab(v),
    style: {
      fontSize: 11, padding: "8px 20px", cursor: "pointer", fontFamily: "inherit",
      border: "none", borderBottom: activeTab === v ? "2px solid #4ecdc4" : "2px solid transparent",
      background: "transparent",
      color: activeTab === v ? "#e8eaed" : "#6b7084",
      fontWeight: activeTab === v ? 600 : 400,
    }
  }, label);

  const firstTs = DATA.length ? DATA[DATA.length - 1]?.add_ts?.replace("T", " ").substring(0, 16) : "";
  const lastTs = DATA.length ? DATA[0]?.add_ts?.replace("T", " ").substring(0, 16) : "";

  return e("div", { style: { paddingRight: selectedPosition ? 420 : 0, transition: "padding-right 0.2s" } },
    e("div", { style: { padding: "28px 24px", maxWidth: 1200, margin: "0 auto" } },
      // Header
      e("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 } },
        e("div", null,
          e("h1", { style: { fontSize: 28, fontWeight: 700, margin: 0, color: "#4ecdc4" } }, META.trading_pair),
          e("div", { style: { fontSize: 12, color: "#6b7084", marginTop: 4 } }, "LP Positions"),
        ),
        e("div", { style: { display: "flex", alignItems: "center", gap: 8 } },
          e("span", { style: { fontSize: 11, color: "#6b7084" } }, "Connector:"),
          e("select", {
            value: filterConnector,
            onChange: (ev) => setFilterConnector(ev.target.value),
            style: {
              fontSize: 11, padding: "6px 10px", borderRadius: 6, cursor: "pointer",
              background: "#1a1c2e", border: "1px solid rgba(255,255,255,0.1)",
              color: "#e8eaed", fontFamily: "inherit",
            }
          },
            e("option", { value: "all" }, "All Connectors"),
            ...connectors.map(c => e("option", { key: c, value: c }, c))
          )
        )
      ),
      e("div", { style: { fontSize: 11, color: "#555870", marginBottom: 16 } },
        `${firstTs} → ${lastTs} · ${filteredData.length} positions (${closedPositions.length} closed, ${openPositions.length} open)`
      ),

      // KPI cards
      e("div", { style: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 10, marginBottom: 24 } },
        e(StatCard, { label: "Positions", value: `${closedPositions.length}`, sub: openPositions.length > 0 ? `${openPositions.length} open` : "all closed", accent: "#e8eaed" }),
        e(StatCard, { label: "Total PnL", value: `$${fmt(stats.totalPnl, 4)}`, sub: `${fmt(stats.totalPnl / Math.max(stats.totalValue, 1) * 100, 2)}% return`, accent: stats.totalPnl >= 0 ? "#4ecdc4" : "#e85d75" }),
        e(StatCard, { label: "Fees Earned", value: `$${fmt(stats.totalFees, 4)}`, sub: `${fmt(stats.totalFees / Math.max(stats.totalValue, 1) * 10000, 1)} bps`, accent: "#7c6df0" }),
        e(StatCard, { label: "Avg Duration", value: fmtDuration(Math.round(stats.avgDur)), sub: "per position", accent: "#e8eaed" }),
      ),

      // Tab navigation
      e("div", { style: { display: "flex", gap: 0, borderBottom: "1px solid rgba(255,255,255,0.06)", marginBottom: 24 } },
        tabBtn("chart", "Range Chart"),
        tabBtn("positions", "Positions"),
      ),

      // Chart tab
      activeTab === "chart" && e("div", null,
        e("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", margin: "32px 0 14px" } },
          e("h3", { style: { fontSize: 13, fontWeight: 600, color: "#8b8fa3", textTransform: "uppercase", letterSpacing: "0.08em", margin: 0 } }, "Position Ranges & Price"),
          openPositions.length > 0 && e("label", { style: { display: "flex", alignItems: "center", gap: 6, cursor: "pointer", fontSize: 11, color: "#6b7084" } },
            e("input", {
              type: "checkbox",
              checked: showOpen,
              onChange: (ev) => setShowOpen(ev.target.checked),
              style: { cursor: "pointer" }
            }),
            `Show open (${openPositions.length})`
          )
        ),
        e(PositionRangeChart, { data: chartData, onSelectPosition: setSelectedIdx, tradingPair: META.trading_pair }),
      ),

      // Positions tab
      activeTab === "positions" && e("div", null,
        e(SectionTitle, null, "All Positions"),
        e(PositionTable, { data: DATA, selectedIdx, onSelect: setSelectedIdx }),
      ),

      e("div", { style: { fontSize: 10, color: "#3a3d50", textAlign: "center", marginTop: 32, paddingBottom: 16 } },
        `${META.trading_pair || "All Pairs"} · ${DATA.length} positions · ${META.db_name || ""}`
      ),
    ),

    // Detail panel
    selectedPosition && e(PositionDetail, { position: selectedPosition, onClose: () => setSelectedIdx(null) }),
  );
}

ReactDOM.render(React.createElement(App), document.getElementById("root"));
"""


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _float(v) -> float:
    if v is None or v == "":
        return 0.0
    try:
        return float(v)
    except (ValueError, TypeError):
        return 0.0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Visualize LP position events as an interactive HTML dashboard.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--pair", "-p", required=True, help="Trading pair (e.g., SOL-USDC) - required for IL calculation")
    parser.add_argument("--connector", "-c", help="Filter by connector (e.g., orca/clmm, meteora/clmm)")
    parser.add_argument("--hours", "-H", type=float, help="Lookback period in hours (e.g., 24 for last 24 hours)")
    parser.add_argument("--db", help="Path to SQLite database (default: auto-detect)")
    parser.add_argument("--output", "-o", help="Output HTML path (default: data/lp_positions_<pair>_dashboard.html)")
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open in browser")

    args = parser.parse_args()

    # Find database
    if args.db:
        db_path = args.db
    else:
        db_path = find_db_with_lp_positions()
    print(f"Using database: {db_path}")

    # Query positions
    positions = query_positions(db_path, args.connector, args.pair, args.hours)
    if not positions:
        filters = []
        if args.connector:
            filters.append(f"connector={args.connector}")
        if args.pair:
            filters.append(f"pair={args.pair}")
        if args.hours:
            filters.append(f"last {args.hours}h")
        filter_str = f" ({', '.join(filters)})" if filters else ""
        print(f"No positions found{filter_str}")
        return 1

    filter_parts = []
    if args.connector:
        filter_parts.append(args.connector)
    if args.hours:
        filter_parts.append(f"last {args.hours}h")
    filter_str = f" ({', '.join(filter_parts)})" if filter_parts else ""
    print(f"Loaded {len(positions)} positions{filter_str}")

    # Build metadata
    meta = {
        "trading_pair": args.pair,
        "connector": args.connector,  # None if not specified (show all connectors)
        "db_name": Path(db_path).name,
        "lookback_hours": args.hours,
    }

    # Transform and generate
    chart_data = positions_to_chart_data(positions)
    html = generate_html(chart_data, meta)

    # Write output
    if args.output:
        output_path = args.output
    else:
        os.makedirs("data", exist_ok=True)
        parts = []
        if args.connector:
            parts.append(args.connector.replace("/", "_"))
        if args.pair:
            parts.append(args.pair)
        suffix = f"_{'_'.join(parts)}" if parts else ""
        output_path = f"data/lp_positions{suffix}_dashboard.html"

    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard written to: {output_path}")

    if not args.no_open:
        abs_path = os.path.abspath(output_path)
        webbrowser.open(f"file://{abs_path}")
        print("Opened in browser")

    return 0


if __name__ == "__main__":
    exit(main())
