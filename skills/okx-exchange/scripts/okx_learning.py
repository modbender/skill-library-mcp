#!/usr/bin/env python3
"""
OKX Trading Learning System v2.0
自我学习、参数优化、市场状态识别、数据压缩、经验提炼
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import hashlib

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
LEARNING_MODEL_FILE = MEMORY_DIR / "okx-learning-model.json"
TRADE_JOURNAL_FILE = MEMORY_DIR / "okx-trade-journal.json"
MONITORING_LOG_FILE = MEMORY_DIR / "okx-monitoring-log.json"
LESSONS_FILE = MEMORY_DIR / "okx-lessons.json"
PATTERNS_FILE = MEMORY_DIR / "okx-patterns.json"
PREFERENCES_FILE = MEMORY_DIR / "okx-trading-preferences.json"

# 数据保留策略
MAX_TRADES_IN_MEMORY = 1000  # 内存中保留最多 1000 笔交易
MAX_MONITORING_SESSIONS = 100  # 最多 100 个监控会话
COMPRESS_AFTER_DAYS = 7  # 7 天后压缩归档
DELETE_AFTER_DAYS = 90  # 90 天后删除

# 经验提炼阈值
MIN_TRADES_FOR_PATTERN = 10  # 至少 10 笔交易才识别模式
MIN_WIN_RATE_FOR_PATTERN = 0.6  # 胜率 60%+ 才视为成功模式
MAX_LOSS_RATE_FOR_PATTERN = 0.3  # 亏损率 30%-才视为失败模式


def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _init_model(model: dict) -> dict:
    """Initialize model structure if missing (first run or new file)."""
    model.setdefault("performance_stats", {
        "total_trades": 0, "winning_trades": 0, "losing_trades": 0,
        "win_rate": 0.0, "total_pnl_usdt": 0.0,
    })
    model.setdefault("coin_performance", {})
    model.setdefault("lessons_learned", [])
    model.setdefault("optimal_parameters", {
        "stop_loss_pct": 3.0, "take_profit_pct": 15.0,
        "position_size_usdt": 50, "leverage": 3,
    })
    return model


def record_trade(trade_data):
    """记录交易并更新学习模型（带数据压缩）"""
    journal = load_json(TRADE_JOURNAL_FILE)
    model = _init_model(load_json(LEARNING_MODEL_FILE))
    lessons = load_json(LESSONS_FILE)
    patterns = load_json(PATTERNS_FILE)
    
    # 添加交易记录
    trade_record = {
        "id": generate_trade_id(trade_data),
        "timestamp": datetime.now().isoformat(),
        **trade_data
    }
    
    if "trades" not in journal:
        journal["trades"] = []
    journal["trades"].append(trade_record)
    journal["last_updated"] = datetime.now().isoformat()
    
    # 数据压缩检查
    journal = compress_trade_journal(journal)
    save_json(TRADE_JOURNAL_FILE, journal)
    
    # 更新统计数据
    update_model_stats(model, trade_data)
    save_json(LEARNING_MODEL_FILE, model)
    
    # 提炼经验教训
    lesson = extract_lesson(trade_data)
    if lesson:
        if "lessons" not in lessons:
            lessons["lessons"] = []
        lessons["lessons"].append(lesson)
        lessons["last_updated"] = datetime.now().isoformat()
        save_json(LESSONS_FILE, lessons)
    
    # 更新模式识别
    update_patterns(patterns, trade_data)
    save_json(PATTERNS_FILE, patterns)
    
    return model


def generate_trade_id(trade_data):
    """生成唯一交易 ID"""
    content = f"{trade_data.get('coin', '')}{trade_data.get('timestamp', '')}{trade_data.get('entry_price', 0)}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def compress_trade_journal(journal):
    """压缩交易记录，保留最近 N 笔，归档旧数据"""
    trades = journal.get("trades", [])
    
    if len(trades) <= MAX_TRADES_IN_MEMORY:
        return journal
    
    # 分离新旧数据
    recent_trades = trades[-MAX_TRADES_IN_MEMORY:]
    old_trades = trades[:-MAX_TRADES_IN_MEMORY]
    
    # 压缩旧数据为统计摘要
    if "compressed_stats" not in journal:
        journal["compressed_stats"] = []
    
    compressed = {
        "period_start": old_trades[0].get("timestamp"),
        "period_end": old_trades[-1].get("timestamp"),
        "total_trades": len(old_trades),
        "winning_trades": sum(1 for t in old_trades if t.get("pnl_pct", 0) > 0),
        "losing_trades": sum(1 for t in old_trades if t.get("pnl_pct", 0) < 0),
        "total_pnl_usdt": sum(t.get("pnl_usdt", 0) for t in old_trades),
        "avg_win_pct": sum(t.get("pnl_pct", 0) for t in old_trades if t.get("pnl_pct", 0) > 0) / max(1, sum(1 for t in old_trades if t.get("pnl_pct", 0) > 0)),
        "avg_loss_pct": sum(t.get("pnl_pct", 0) for t in old_trades if t.get("pnl_pct", 0) < 0) / max(1, sum(1 for t in old_trades if t.get("pnl_pct", 0) < 0)),
        "compressed_at": datetime.now().isoformat()
    }
    journal["compressed_stats"].append(compressed)
    
    # 保留最近交易
    journal["trades"] = recent_trades
    
    return journal


def extract_lesson(trade_data):
    """从单笔交易提炼经验教训"""
    pnl_pct = trade_data.get("pnl_pct", 0)
    coin = trade_data.get("coin", "UNKNOWN")
    hold_time = trade_data.get("hold_time_hours", 0)
    signal_type = trade_data.get("signal_type", "unknown")
    market_regime = trade_data.get("market_regime", "unknown")
    
    lesson = None
    
    # 大额亏损教训
    if pnl_pct < -5:
        lesson = {
            "type": "large_loss",
            "severity": "high" if pnl_pct < -10 else "medium",
            "coin": coin,
            "pnl_pct": pnl_pct,
            "signal_type": signal_type,
            "market_regime": market_regime,
            "timestamp": datetime.now().isoformat(),
            "lesson": f"在{market_regime}市场使用{signal_type}信号亏损{pnl_pct:.1f}%",
            "action": f"收紧{coin}止损或减少该信号权重",
            "avoid_condition": {
                "coin": coin,
                "signal": signal_type,
                "market_regime": market_regime
            }
        }
    
    # 大额盈利经验
    elif pnl_pct > 10:
        lesson = {
            "type": "large_win",
            "coin": coin,
            "pnl_pct": pnl_pct,
            "signal_type": signal_type,
            "market_regime": market_regime,
            "timestamp": datetime.now().isoformat(),
            "lesson": f"在{market_regime}市场使用{signal_type}信号盈利{pnl_pct:.1f}%",
            "action": f"增加{coin}在该市场状态下的仓位",
            "replicate_condition": {
                "coin": coin,
                "signal": signal_type,
                "market_regime": market_regime
            }
        }
    
    # 快速止盈经验
    elif hold_time < 1 and pnl_pct > 5:
        lesson = {
            "type": "quick_win",
            "coin": coin,
            "pnl_pct": pnl_pct,
            "hold_time": hold_time,
            "timestamp": datetime.now().isoformat(),
            "lesson": f"{coin} 快速盈利{pnl_pct:.1f}% (持仓{hold_time:.1f}h)",
            "action": "该币种适合短线策略"
        }
    
    # 止损正确经验
    elif -3.5 < pnl_pct < -2.5:
        lesson = {
            "type": "good_stop",
            "coin": coin,
            "pnl_pct": pnl_pct,
            "timestamp": datetime.now().isoformat(),
            "lesson": f"{coin} 止损执行正确 (亏损{pnl_pct:.1f}%)",
            "action": "止损参数合理，继续保持"
        }
    
    return lesson


def update_patterns(patterns, trade_data):
    """更新交易模式识别"""
    if "patterns" not in patterns:
        patterns["patterns"] = []
    
    coin = trade_data.get("coin", "UNKNOWN")
    signal = trade_data.get("signal_type", "unknown")
    regime = trade_data.get("market_regime", "unknown")
    pnl = trade_data.get("pnl_pct", 0)
    
    # 查找或创建模式
    pattern_key = f"{coin}_{signal}_{regime}"
    existing_pattern = None
    for p in patterns["patterns"]:
        if p.get("key") == pattern_key:
            existing_pattern = p
            break
    
    if not existing_pattern:
        existing_pattern = {
            "key": pattern_key,
            "coin": coin,
            "signal": signal,
            "market_regime": regime,
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "total_pnl": 0,
            "created_at": datetime.now().isoformat()
        }
        patterns["patterns"].append(existing_pattern)
    
    # 更新模式统计
    existing_pattern["trades"] += 1
    existing_pattern["total_pnl"] += pnl
    if pnl > 0:
        existing_pattern["wins"] += 1
    elif pnl < 0:
        existing_pattern["losses"] += 1
    
    # 计算胜率
    existing_pattern["win_rate"] = existing_pattern["wins"] / existing_pattern["trades"]
    
    # 标记模式类型
    if existing_pattern["trades"] >= MIN_TRADES_FOR_PATTERN:
        if existing_pattern["win_rate"] >= MIN_WIN_RATE_FOR_PATTERN:
            existing_pattern["pattern_type"] = "successful"
        elif existing_pattern["win_rate"] <= MAX_LOSS_RATE_FOR_PATTERN:
            existing_pattern["pattern_type"] = "failed"
        else:
            existing_pattern["pattern_type"] = "neutral"
    
    patterns["last_updated"] = datetime.now().isoformat()


def update_model_stats(model, trade):
    """更新模型统计"""
    stats = model["performance_stats"]
    pnl_pct = trade.get("pnl_pct", 0)
    coin = trade.get("coin", "UNKNOWN")
    
    stats["total_trades"] += 1
    
    if pnl_pct > 0:
        stats["winning_trades"] += 1
    elif pnl_pct < 0:
        stats["losing_trades"] += 1
    
    # 胜率
    if stats["total_trades"] > 0:
        stats["win_rate"] = stats["winning_trades"] / stats["total_trades"] * 100
    
    # 平均盈亏
    stats["total_pnl_usdt"] += trade.get("pnl_usdt", 0)
    
    # 更新币种表现
    if coin not in model["coin_performance"]:
        model["coin_performance"][coin] = {
            "trades": 0, "wins": 0, "losses": 0, "total_pnl": 0
        }
    model["coin_performance"][coin]["trades"] += 1
    if pnl_pct > 0:
        model["coin_performance"][coin]["wins"] += 1
    elif pnl_pct < 0:
        model["coin_performance"][coin]["losses"] += 1
    model["coin_performance"][coin]["total_pnl"] += pnl_pct
    
    # 学习教训
    if pnl_pct < -5:  # 大额亏损
        lesson = {
            "type": "large_loss",
            "coin": coin,
            "pnl_pct": pnl_pct,
            "timestamp": datetime.now().isoformat(),
            "suggestion": f"考虑收紧 {coin} 的止损或降低仓位"
        }
        model["lessons_learned"].append(lesson)
    elif pnl_pct > 10:  # 大额盈利
        lesson = {
            "type": "large_win",
            "coin": coin,
            "pnl_pct": pnl_pct,
            "timestamp": datetime.now().isoformat(),
            "suggestion": f"{coin} 策略有效，可适当增加仓位"
        }
        model["lessons_learned"].append(lesson)


def get_lessons_summary():
    """获取经验教训总结"""
    lessons = load_json(LESSONS_FILE)
    patterns = load_json(PATTERNS_FILE)
    
    summary = {
        "total_lessons": len(lessons.get("lessons", [])),
        "avoid_conditions": [],
        "replicate_conditions": [],
        "successful_patterns": [],
        "failed_patterns": []
    }
    
    # 提取规避条件
    for lesson in lessons.get("lessons", []):
        if lesson.get("type") == "large_loss" and lesson.get("avoid_condition"):
            summary["avoid_conditions"].append({
                "condition": lesson["avoid_condition"],
                "reason": lesson["lesson"],
                "action": lesson["action"]
            })
        
        # 提取复制条件
        if lesson.get("type") == "large_win" and lesson.get("replicate_condition"):
            summary["replicate_conditions"].append({
                "condition": lesson["replicate_condition"],
                "reason": lesson["lesson"],
                "action": lesson["action"]
            })
    
    # 提取成功/失败模式
    for pattern in patterns.get("patterns", []):
        if pattern.get("pattern_type") == "successful":
            summary["successful_patterns"].append({
                "coin": pattern["coin"],
                "signal": pattern["signal"],
                "market_regime": pattern["market_regime"],
                "win_rate": f"{pattern['win_rate']*100:.1f}%",
                "trades": pattern["trades"],
                "avg_pnl": f"{pattern['total_pnl']/pattern['trades']:.2f}%"
            })
        elif pattern.get("pattern_type") == "failed":
            summary["failed_patterns"].append({
                "coin": pattern["coin"],
                "signal": pattern["signal"],
                "market_regime": pattern["market_regime"],
                "win_rate": f"{pattern['win_rate']*100:.1f}%",
                "trades": pattern["trades"],
                "avg_pnl": f"{pattern['total_pnl']/pattern['trades']:.2f}%"
            })
    
    return summary


def should_avoid_trade(coin, signal, market_regime):
    """检查是否应该避免某类交易"""
    lessons = load_json(LESSONS_FILE)
    patterns = load_json(PATTERNS_FILE)
    
    # 检查规避条件
    for lesson in lessons.get("lessons", []):
        avoid = lesson.get("avoid_condition", {})
        if (avoid.get("coin") == coin and
            avoid.get("signal") == signal and
            avoid.get("market_regime") == market_regime):
            return True, f"避免：{lesson['lesson']}"
    
    # 检查失败模式
    for pattern in patterns.get("patterns", []):
        if (pattern.get("coin") == coin and
            pattern.get("signal") == signal and
            pattern.get("market_regime") == market_regime and
            pattern.get("pattern_type") == "failed"):
            return True, f"失败模式：胜率{pattern.get('win_rate', 0)*100:.1f}%"
    
    return False, None


def get_optimal_conditions(coin, signal, market_regime):
    """获取最佳交易条件"""
    lessons = load_json(LESSONS_FILE)
    patterns = load_json(PATTERNS_FILE)
    
    suggestions = []
    
    # 检查复制条件
    for lesson in lessons.get("lessons", []):
        replicate = lesson.get("replicate_condition", {})
        if (replicate.get("coin") == coin and
            replicate.get("signal") == signal and
            replicate.get("market_regime") == market_regime):
            suggestions.append({
                "type": "replicate",
                "reason": lesson["lesson"],
                "action": lesson["action"]
            })
    
    # 检查成功模式
    for pattern in patterns.get("patterns", []):
        if (pattern.get("coin") == coin and
            pattern.get("signal") == signal and
            pattern.get("market_regime") == market_regime and
            pattern.get("pattern_type") == "successful"):
            suggestions.append({
                "type": "successful_pattern",
                "win_rate": f"{pattern['win_rate']*100:.1f}%",
                "avg_pnl": f"{pattern['total_pnl']/pattern['trades']:.2f}%",
                "trades": pattern["trades"]
            })
    
    return suggestions


def cleanup_old_data():
    """清理过期数据"""
    cutoff_date = datetime.now() - timedelta(days=DELETE_AFTER_DAYS)
    
    # 清理交易日志
    journal = load_json(TRADE_JOURNAL_FILE)
    if "trades" in journal:
        original_count = len(journal["trades"])
        journal["trades"] = [
            t for t in journal["trades"]
            if datetime.fromisoformat(t.get("timestamp", "2000-01-01")) > cutoff_date
        ]
        if len(journal["trades"]) < original_count:
            save_json(TRADE_JOURNAL_FILE, journal)
            return f"清理了 {original_count - len(journal['trades'])} 笔过期交易记录"
    
    return "无需清理"


def analyze_and_optimize():
    """分析历史数据并优化参数"""
    journal = load_json(TRADE_JOURNAL_FILE)
    model = load_json(LEARNING_MODEL_FILE)
    lessons = load_json(LESSONS_FILE)
    patterns = load_json(PATTERNS_FILE)
    
    trades = journal.get("trades", [])
    if len(trades) < 5:
        return {
            "status": "insufficient_data",
            "message": "需要至少 5 笔交易才能优化参数",
            "current_trades": len(trades)
        }
    
    # 分析最佳参数组合
    winning_trades = [t for t in trades if t.get("pnl_pct", 0) > 0]
    losing_trades = [t for t in trades if t.get("pnl_pct", 0) < 0]
    
    # 计算平均持仓时间
    if winning_trades:
        avg_hold = sum(t.get("hold_time_hours", 0) for t in winning_trades) / len(winning_trades)
    else:
        avg_hold = 0
    
    # 参数优化建议
    suggestions = []
    
    # 胜率过低 → 收紧止损
    if model["performance_stats"]["win_rate"] < 40:
        suggestions.append({
            "param": "stop_loss_pct",
            "current": model["optimal_parameters"]["stop_loss_pct"],
            "suggested": 2.0,
            "reason": f"胜率仅{model['performance_stats']['win_rate']:.1f}%，建议收紧止损"
        })
    
    # 平均盈利高 → 放宽止盈
    if winning_trades:
        avg_win = sum(t.get("pnl_pct", 0) for t in winning_trades) / len(winning_trades)
        if avg_win > 8:
            suggestions.append({
                "param": "take_profit_pct",
                "current": model["optimal_parameters"]["take_profit_pct"],
                "suggested": 20.0,
                "reason": f"平均盈利{avg_win:.1f}%，可尝试更高止盈"
            })
    
    # 币种表现分析
    worst_coin = None
    worst_rate = 100
    for coin, perf in model["coin_performance"].items():
        if perf["trades"] >= 3:
            rate = perf["wins"] / perf["trades"] * 100
            if rate < worst_rate:
                worst_rate = rate
                worst_coin = coin
    
    if worst_coin and worst_rate < 30:
        suggestions.append({
            "param": f"avoid_coin",
            "value": worst_coin,
            "reason": f"{worst_coin} 胜率仅{worst_rate:.1f}%，建议减少交易"
        })
    
    return {
        "status": "optimized",
        "total_trades": len(trades),
        "win_rate": model["performance_stats"]["win_rate"],
        "suggestions": suggestions
    }


def identify_market_regime(monitoring_data):
    """识别当前市场状态"""
    if not monitoring_data:
        return "unknown"
    
    # 分析最近的信号
    recent_signals = monitoring_data[-20:] if len(monitoring_data) >= 20 else monitoring_data
    
    sell_count = sum(1 for d in recent_signals if d.get("signal") == "SELL")
    buy_count = sum(1 for d in recent_signals if d.get("signal") == "BUY")
    
    sell_ratio = sell_count / len(recent_signals) if recent_signals else 0
    
    if sell_ratio > 0.8:
        return "strong_bear"  # 强烈看跌
    elif sell_ratio > 0.6:
        return "weak_bear"    # 弱势看跌
    elif sell_ratio < 0.2:
        return "strong_bull"  # 强烈看涨
    elif sell_ratio < 0.4:
        return "weak_bull"    # 弱势看涨
    else:
        return "ranging"      # 震荡


def get_adaptive_parameters(market_regime):
    """根据市场状态返回自适应参数"""
    base_params = {
        "strong_bull": {
            "position_size": 80, "leverage": 5, "stop_loss": 4.0, "take_profit": 20.0,
            "strategy": "trend_follow_long"
        },
        "weak_bull": {
            "position_size": 50, "leverage": 3, "stop_loss": 3.0, "take_profit": 15.0,
            "strategy": "cautious_long"
        },
        "ranging": {
            "position_size": 30, "leverage": 2, "stop_loss": 2.0, "take_profit": 8.0,
            "strategy": "mean_reversion"
        },
        "weak_bear": {
            "position_size": 40, "leverage": 3, "stop_loss": 3.0, "take_profit": 12.0,
            "strategy": "cautious_short"
        },
        "strong_bear": {
            "position_size": 60, "leverage": 4, "stop_loss": 4.0, "take_profit": 18.0,
            "strategy": "trend_follow_short"
        }
    }
    
    return base_params.get(market_regime, base_params["ranging"])


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python okx_learning.py <command> [args]")
        print("""
Commands:
  record <json>      - 记录交易
  status             - 显示学习状态
  analyze            - 分析并优化参数
  lessons            - 显示经验教训总结
  patterns           - 显示识别的交易模式
  check <coin> <signal> <regime> - 检查是否应避免某类交易
  cleanup            - 清理过期数据
  compress           - 手动压缩数据
        """)
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "record":
        trade_data = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
        result = record_trade(trade_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "status":
        model = load_json(LEARNING_MODEL_FILE)
        print(json.dumps(model.get("performance_stats", {}), indent=2, ensure_ascii=False))
    
    elif cmd == "analyze":
        result = analyze_and_optimize()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "lessons":
        result = get_lessons_summary()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "patterns":
        patterns = load_json(PATTERNS_FILE)
        print(json.dumps(patterns.get("patterns", []), indent=2, ensure_ascii=False))
    
    elif cmd == "check":
        if len(sys.argv) < 5:
            print("Usage: python okx_learning.py check <coin> <signal> <market_regime>")
            sys.exit(1)
        coin, signal, regime = sys.argv[2], sys.argv[3], sys.argv[4]
        should_avoid, reason = should_avoid_trade(coin, signal, regime)
        if should_avoid:
            print(f"⚠️ 避免交易：{reason}")
        else:
            print("✅ 可以交易")
            suggestions = get_optimal_conditions(coin, signal, regime)
            if suggestions:
                print("建议:")
                for s in suggestions:
                    print(f"  - {s}")
    
    elif cmd == "cleanup":
        result = cleanup_old_data()
        print(result)
    
    elif cmd == "compress":
        journal = load_json(TRADE_JOURNAL_FILE)
        journal = compress_trade_journal(journal)
        save_json(TRADE_JOURNAL_FILE, journal)
        print("数据压缩完成")
        print(json.dumps(journal.get("compressed_stats", []), indent=2, ensure_ascii=False))
