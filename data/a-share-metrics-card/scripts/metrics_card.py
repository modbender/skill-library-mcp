#!/usr/bin/env python3
"""Generate a simple A-share metrics card using AkShare.

Usage:
  python metrics_card.py --symbol 600406 [--name 国电南瑞] [--out <path>]

Notes:
- This script intentionally focuses on a small, robust subset of metrics.
- AkShare APIs can change; keep the script defensive.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path


def _now_iso() -> str:
    return dt.datetime.now().astimezone().isoformat(timespec="seconds")


def _safe_str(x) -> str:
    if x is None:
        return ""
    return str(x)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", required=True, help="6-digit A-share code, e.g., 600406")
    ap.add_argument("--name", default="", help="Chinese name (optional)")
    ap.add_argument("--out", default="", help="Output markdown path")
    args = ap.parse_args()

    symbol = args.symbol.strip()
    name = args.name.strip()

    out_path = Path(args.out) if args.out else Path("notes/stocks/cards") / f"{symbol}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Lazy import so arg parsing works even if deps missing.
    import akshare as ak

    lines: list[str] = []
    lines.append(f"# 股票体检卡：{symbol}{(' ' + name) if name else ''}")
    lines.append("")
    lines.append(f"- 生成时间：{_now_iso()}")
    lines.append(f"- 数据源：AkShare {ak.__version__}")
    lines.append("")

    # 1) Quote (prefer Eastmoney push2 stock/get: lightweight and tends to work even when clist is blocked)
    quote_note = ""
    try:
        from curl_cffi import requests as creq

        market_prefix = "1" if symbol.startswith("6") else "0"  # 1=SH, 0=SZ (covers 0/3)
        secid = f"{market_prefix}.{symbol}"
        url = "https://push2.eastmoney.com/api/qt/stock/get"
        params = {
            "secid": secid,
            "fields": "f58,f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f59",
        }
        def _get_with_retry(url, params, tries=3):
            last_err = None
            for i in range(tries):
                try:
                    # small backoff: 0s, 1s, 2s
                    if i:
                        import time
                        time.sleep(i)
                    return creq.get(url, params=params, timeout=20, impersonate="chrome")
                except Exception as e:
                    last_err = e
            raise last_err  # type: ignore

        r = _get_with_retry(url, params, tries=3)
        j = r.json()
        d = (j or {}).get("data") or {}

        # Field hints (best-effort):
        # f58 name, f43 last, f44 high, f45 low, f46 open, f47 volume, f48 amount
        if d:
            if not name:
                name = _safe_str(d.get("f58"))
            # Prices are usually scaled by 100 (e.g., 2833 => 28.33). Make it human-friendly.
            def p(x):
                try:
                    return f"{float(x)/100:.2f}" if x is not None else ""
                except Exception:
                    return _safe_str(x)

            last = d.get("f43")
            high = d.get("f44")
            low = d.get("f45")
            open_ = d.get("f46")
            vol = d.get("f47")
            amt = d.get("f48")

            lines.append("## 行情概览（来自 Eastmoney push2）")
            lines.append(f"- 最新价：{p(last)}")
            lines.append(f"- 开盘/最高/最低：{p(open_)} / {p(high)} / {p(low)}")
            lines.append(f"- 成交量：{_safe_str(vol)}")
            lines.append(f"- 成交额：{_safe_str(amt)}")
            lines.append("")
        else:
            # Fallback: try AkShare spot table (heavier; may also fail on some hosts)
            try:
                df = ak.stock_zh_a_spot_em()
                row = df[df["代码"].astype(str) == symbol].head(1)
                if not row.empty:
                    if not name:
                        name = _safe_str(row.iloc[0].get("名称"))
                    last = row.iloc[0].get("最新价")
                    chg = row.iloc[0].get("涨跌幅")
                    amount = row.iloc[0].get("成交额")
                    lines.append("## 行情概览（Fallback：AkShare spot 表）")
                    lines.append(f"- 最新价：{_safe_str(last)}")
                    lines.append(f"- 涨跌幅：{_safe_str(chg)}")
                    lines.append(f"- 成交额：{_safe_str(amount)}")
                    lines.append("")
                else:
                    quote_note = "接口返回空 data；fallback 也未匹配到代码。"
            except Exception as e2:
                quote_note = f"接口返回空 data；fallback 失败：{e2!s}"
    except Exception as e:
        quote_note = f"行情拉取失败：{e!s}"

    if quote_note:
        lines.append("## 行情概览")
        lines.append(f"- 备注：{quote_note}")
        lines.append("")

    # 2) Financial/valuation indicators
    # NOTE: AkShare indicator interfaces are sometimes unstable; keep best-effort and do not fail the whole card.
    ind_note = ""
    try:
        # Try a known Eastmoney-based indicator endpoint in AkShare (may fail depending on upstream changes)
        dfi = None
        try:
            dfi = ak.stock_financial_analysis_indicator_em(symbol=symbol)
        except Exception as e1:
            # Some AkShare versions raise internal NoneType issues; fall back.
            dfi = None
            ind_note = f"财务分析指标接口异常（将fallback）：{e1!s}"

        if dfi is not None and hasattr(dfi, "empty") and (not dfi.empty):
            tail = dfi.tail(1)
            lines.append("## 财务分析指标（近一期，AkShare）")
            for col in ["净资产收益率(ROE)", "销售毛利率", "资产负债率", "每股收益(EPS)"]:
                if col in tail.columns:
                    lines.append(f"- {col}: {_safe_str(tail.iloc[0][col])}")
            lines.append("")
        else:
            # Fallback to another indicator function (may return empty depending on upstream)
            try:
                df2 = ak.stock_financial_analysis_indicator(symbol=symbol)
                if df2 is not None and hasattr(df2, "empty") and (not df2.empty):
                    tail = df2.tail(1)
                    lines.append("## 财务分析指标（近一期，AkShare fallback）")
                    # Print first few available columns to avoid key mismatch across sources
                    cols = [c for c in tail.columns[:8]]
                    for c in cols:
                        lines.append(f"- {c}: {_safe_str(tail.iloc[0][c])}")
                    lines.append("")
                else:
                    if not ind_note:
                        ind_note = "财务分析指标接口返回空（可能被限流/网络不通/上游变动）。"
            except Exception as e2:
                if not ind_note:
                    ind_note = f"财务分析指标拉取失败：{e2!s}"
    except Exception as e:
        if not ind_note:
            ind_note = f"财务分析指标拉取失败：{e!s}"

    if ind_note:
        lines.append("## 财务分析指标")
        lines.append(f"- 备注：{ind_note}")
        lines.append("")

    lines.append("## 下一步建议（学习向）")
    lines.append("- 核实公司行业属性与主营（避免只看代码/概念）。")
    lines.append("- 对照三张表：利润表（毛利/净利）、资产负债表（负债结构）、现金流量表（经营现金流）。")
    lines.append("- 记录你关心的 3 个指标口径（例如：PE_TTM、ROE、经营现金流）。")
    lines.append("")
    lines.append("## 读卡指南（给新手）")
    lines.append("1) 先看‘公司做什么’：主营/行业位置，不要只看题材。")
    lines.append("2) 再看‘赚不赚钱 & 赚得稳不稳’：ROE、毛利率/净利率的趋势。")
    lines.append("3) 最后看‘钱是不是真进兜里’：经营现金流是否匹配利润。")
    lines.append("4) 所有指标都要问：数据口径是什么？报告期是哪天？")

    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
