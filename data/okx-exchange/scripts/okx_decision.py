#!/usr/bin/env python3
"""
OKX Trading Decision Engine v1.0
结合 JSON 数据进行推演、规划、买卖决策
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"

# 数据文件
LEARNING_MODEL_FILE = MEMORY_DIR / "okx-learning-model.json"
TRADE_JOURNAL_FILE = MEMORY_DIR / "okx-trade-journal.json"
LESSONS_FILE = MEMORY_DIR / "okx-lessons.json"
PATTERNS_FILE = MEMORY_DIR / "okx-patterns.json"
MONITORING_LOG_FILE = MEMORY_DIR / "okx-monitoring-log.json"
DECISION_LOG_FILE = MEMORY_DIR / "okx-decision-log.json"


def load_json(filepath: Path) -> dict:
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_json(filepath: Path, data: dict):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class DecisionEngine:
    """交易决策引擎"""
    
    def __init__(self):
        self.model = load_json(LEARNING_MODEL_FILE)
        self.lessons = load_json(LESSONS_FILE)
        self.patterns = load_json(PATTERNS_FILE)
        self.journal = load_json(TRADE_JOURNAL_FILE)
        self.monitoring = load_json(MONITORING_LOG_FILE)
        self.decision_log = load_json(DECISION_LOG_FILE)
    
    def check_avoid_conditions(self, coin: str, signal: str, market_regime: str) -> Tuple[bool, str]:
        """检查是否应避免某类交易"""
        for lesson in self.lessons.get("lessons", []):
            avoid = lesson.get("avoid_condition", {})
            if (avoid.get("coin") == coin and 
                avoid.get("signal") == signal and 
                avoid.get("market_regime") == market_regime):
                return True, f"教训#{lesson.get('type', 'unknown')}: {lesson.get('lesson', '')}"
        
        for pattern in self.patterns.get("patterns", []):
            if (pattern.get("coin") == coin and 
                pattern.get("signal") == signal and 
                pattern.get("market_regime") == market_regime and
                pattern.get("pattern_type") == "failed"):
                return True, f"失败模式：胜率{pattern.get('win_rate', 0)*100:.1f}%"
        
        return False, ""
    
    def check_success_patterns(self, coin: str, signal: str, market_regime: str) -> List[dict]:
        """检查是否有成功模式可复用"""
        suggestions = []
        
        for pattern in self.patterns.get("patterns", []):
            if (pattern.get("coin") == coin and 
                pattern.get("signal") == signal and 
                pattern.get("market_regime") == market_regime and
                pattern.get("pattern_type") == "successful"):
                suggestions.append({
                    "pattern": f"{coin}_{signal}_{market_regime}",
                    "win_rate": f"{pattern.get('win_rate', 0)*100:.1f}%",
                    "avg_pnl": f"{pattern.get('total_pnl', 0)/max(1, pattern.get('trades', 1)):.2f}%",
                    "trades": pattern.get("trades", 0)
                })
        
        for lesson in self.lessons.get("lessons", []):
            replicate = lesson.get("replicate_condition", {})
            if (replicate.get("coin") == coin and 
                replicate.get("signal") == signal and 
                replicate.get("market_regime") == market_regime):
                suggestions.append({
                    "lesson": lesson.get("lesson", ""),
                    "action": lesson.get("action", "")
                })
        
        return suggestions
    
    def simulate_scenario(self, coin: str, direction: str, entry_price: float, 
                          position_usdt: float, leverage: int, 
                          stop_loss_pct: float, take_profit_pct: float) -> dict:
        """推演交易情景"""
        # 基于历史数据模拟
        recent_trades = self.journal.get("trades", [])[-50:]  # 最近 50 笔
        
        coin_trades = [t for t in recent_trades if t.get("coin", "").startswith(coin.split("-")[0])]
        
        if not coin_trades:
            return {
                "status": "insufficient_data",
                "message": "该币种历史交易数据不足"
            }
        
        # 统计类似交易的表现
        similar_trades = [
            t for t in coin_trades 
            if t.get("direction", "") == direction
        ]
        
        if not similar_trades:
            similar_trades = coin_trades  #  fallback
        
        win_count = sum(1 for t in similar_trades if t.get("pnl_pct", 0) > 0)
        total_pnl = sum(t.get("pnl_pct", 0) for t in similar_trades)
        avg_win = sum(t.get("pnl_pct", 0) for t in similar_trades if t.get("pnl_pct", 0) > 0) / max(1, win_count)
        avg_loss = sum(t.get("pnl_pct", 0) for t in similar_trades if t.get("pnl_pct", 0) < 0) / max(1, len(similar_trades) - win_count)
        
        # 情景推演
        scenarios = {
            "bull_case": {
                "probability": 0.3,
                "outcome": f"+{take_profit_pct*100:.1f}%",
                "pnl_usdt": position_usdt * leverage * take_profit_pct
            },
            "base_case": {
                "probability": 0.5,
                "outcome": f"{total_pnl/max(1, len(similar_trades)):+.1f}%",
                "pnl_usdt": position_usdt * leverage * (total_pnl/max(1, len(similar_trades)))
            },
            "bear_case": {
                "probability": 0.2,
                "outcome": f"-{stop_loss_pct*100:.1f}%",
                "pnl_usdt": -position_usdt * leverage * stop_loss_pct
            }
        }
        
        expected_value = (
            scenarios["bull_case"]["pnl_usdt"] * scenarios["bull_case"]["probability"] +
            scenarios["base_case"]["pnl_usdt"] * scenarios["base_case"]["probability"] +
            scenarios["bear_case"]["pnl_usdt"] * scenarios["bear_case"]["probability"]
        )
        
        return {
            "status": "simulated",
            "sample_size": len(similar_trades),
            "historical_win_rate": f"{win_count/max(1, len(similar_trades))*100:.1f}%",
            "avg_win": f"{avg_win:.2f}%",
            "avg_loss": f"{avg_loss:.2f}%",
            "scenarios": scenarios,
            "expected_value_usdt": f"{expected_value:.2f}"
        }
    
    def generate_decision(self, coin: str, signal: str, market_regime: str, 
                          current_price: float, rsi: float = 50) -> dict:
        """生成买卖决策"""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "coin": coin,
            "signal": signal,
            "market_regime": market_regime,
            "current_price": current_price,
            "rsi": rsi,
            "decision": "wait",  # buy / sell / wait
            "confidence": 0.0,
            "reasons": [],
            "parameters": {},
            "simulation": {},
            "avoid_warning": None,
            "success_patterns": []
        }
        
        # 1. 检查规避条件
        should_avoid, avoid_reason = self.check_avoid_conditions(coin, signal, market_regime)
        if should_avoid:
            decision["decision"] = "avoid"
            decision["avoid_warning"] = avoid_reason
            decision["reasons"].append(f"⚠️ {avoid_reason}")
            decision["confidence"] = 0.0
            return decision
        
        # 2. 检查成功模式
        success_patterns = self.check_success_patterns(coin, signal, market_regime)
        if success_patterns:
            decision["success_patterns"] = success_patterns
            decision["reasons"].append(f"✅ 发现{len(success_patterns)}个成功模式")
            decision["confidence"] += 0.3 * min(len(success_patterns), 3)
        
        # 3. RSI 极端值判断
        if rsi < 30:
            decision["decision"] = "buy"
            decision["reasons"].append(f"✅ RSI {rsi:.1f} < 30 (超卖)")
            decision["confidence"] += 0.3
        elif rsi > 70:
            decision["decision"] = "sell"
            decision["reasons"].append(f"✅ RSI {rsi:.1f} > 70 (超买)")
            decision["confidence"] += 0.3
        
        # 4. 市场状态判断
        if market_regime == "strong_bull":
            if signal == "BUY":
                decision["decision"] = "buy"
                decision["reasons"].append("✅ 强牛市 + BUY 信号共振")
                decision["confidence"] += 0.4
        elif market_regime == "strong_bear":
            if signal == "SELL":
                decision["decision"] = "sell"
                decision["reasons"].append("✅ 强熊市 + SELL 信号共振")
                decision["confidence"] += 0.4
        elif market_regime == "ranging":
            decision["reasons"].append("⚠️ 震荡市，降低权重")
            decision["confidence"] *= 0.5
        
        # 5. 参数建议
        if decision["decision"] in ["buy", "sell"]:
            # 基于历史最优参数
            optimal = self.model.get("optimal_parameters", {})
            
            # 根据成功模式调整
            if success_patterns:
                position_size = min(80, optimal.get("position_size_usdt", 50) * 1.5)
                take_profit = min(20, optimal.get("take_profit_pct", 15) * 1.2)
            else:
                position_size = optimal.get("position_size_usdt", 50)
                take_profit = optimal.get("take_profit_pct", 15)
            
            decision["parameters"] = {
                "position_usdt": position_size,
                "leverage": optimal.get("leverage", 3),
                "stop_loss_pct": optimal.get("stop_loss_pct", 3.0),
                "take_profit_pct": take_profit
            }
            
            # 情景推演
            direction = "long" if decision["decision"] == "buy" else "short"
            decision["simulation"] = self.simulate_scenario(
                coin=coin,
                direction=direction,
                entry_price=current_price,
                position_usdt=position_size,
                leverage=optimal.get("leverage", 3),
                stop_loss_pct=optimal.get("stop_loss_pct", 3.0),
                take_profit_pct=take_profit
            )
        
        # 6. 置信度封顶
        decision["confidence"] = min(1.0, decision["confidence"])
        
        # 7. 决策阈值
        if decision["confidence"] < 0.3:
            decision["decision"] = "wait"
            decision["reasons"].append("⚠️ 置信度不足 30%，建议观望")
        
        return decision
    
    def log_decision(self, decision: dict):
        """记录决策到日志"""
        if "decisions" not in self.decision_log:
            self.decision_log["decisions"] = []
        
        self.decision_log["decisions"].append(decision)
        
        # 限制日志大小
        if len(self.decision_log["decisions"]) > 500:
            self.decision_log["decisions"] = self.decision_log["decisions"][-500:]
        
        self.decision_log["last_updated"] = datetime.now().isoformat()
        save_json(DECISION_LOG_FILE, self.decision_log)
    
    def get_decision_summary(self, limit: int = 10) -> List[dict]:
        """获取最近决策摘要"""
        decisions = self.decision_log.get("decisions", [])[-limit:]
        
        summary = []
        for d in decisions:
            summary.append({
                "time": d.get("timestamp", "")[:19],
                "coin": d.get("coin", ""),
                "decision": d.get("decision", ""),
                "confidence": f"{d.get('confidence', 0)*100:.0f}%",
                "reasons": d.get("reasons", [])[:2]
            })
        
        return summary


def main():
    import sys
    
    engine = DecisionEngine()
    
    if len(sys.argv) < 2:
        print("""
OKX Decision Engine v1.0

Usage:
  python okx_decision.py decision <coin> <signal> <market_regime> <price> [rsi]
  python okx_decision.py summary [limit]
  python okx_decision.py simulate <coin> <direction> <price> <position> <leverage> <sl> <tp>
  python okx_decision.py avoid <coin> <signal> <market_regime>
        """)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "decision":
        if len(sys.argv) < 6:
            print("Usage: python okx_decision.py decision <coin> <signal> <market_regime> <price> [rsi]")
            return
        
        coin = sys.argv[2]
        signal = sys.argv[3]
        regime = sys.argv[4]
        price = float(sys.argv[5])
        rsi = float(sys.argv[6]) if len(sys.argv) > 6 else 50
        
        decision = engine.generate_decision(coin, signal, regime, price, rsi)
        engine.log_decision(decision)
        
        print("\n" + "="*60)
        print("🎯 交易决策")
        print("="*60)
        print(f"币种：{decision['coin']}")
        print(f"信号：{decision['signal']}")
        print(f"市场状态：{decision['market_regime']}")
        print(f"当前价格：{decision['current_price']}")
        print(f"RSI: {decision['rsi']}")
        print("-"*60)
        print(f"决策：{decision['decision'].upper()}")
        print(f"置信度：{decision['confidence']*100:.0f}%")
        print("-"*60)
        
        if decision['avoid_warning']:
            print(f"⚠️ 规避警告：{decision['avoid_warning']}")
        
        if decision['success_patterns']:
            print(f"\n✅ 成功模式 ({len(decision['success_patterns'])}个):")
            for p in decision['success_patterns'][:3]:
                if 'win_rate' in p:
                    print(f"   - {p.get('pattern', '')}: 胜率{p['win_rate']}, 平均盈利{p['avg_pnl']}")
                else:
                    print(f"   - {p.get('lesson', '')}")
        
        print(f"\n📋 理由:")
        for r in decision['reasons']:
            print(f"   {r}")
        
        if decision['parameters']:
            print(f"\n💰 建议参数:")
            print(f"   仓位：{decision['parameters'].get('position_usdt', 0)} USDT")
            print(f"   杠杆：{decision['parameters'].get('leverage', 0)}x")
            print(f"   止损：{decision['parameters'].get('stop_loss_pct', 0)}%")
            print(f"   止盈：{decision['parameters'].get('take_profit_pct', 0)}%")
        
        if decision.get('simulation', {}).get('status') == 'simulated':
            sim = decision['simulation']
            print(f"\n🔮 情景推演:")
            print(f"   样本数：{sim.get('sample_size', 0)} 笔历史交易")
            print(f"   历史胜率：{sim.get('historical_win_rate', 'N/A')}")
            print(f"   期望值：{sim.get('expected_value_usdt', 'N/A')} USDT")
            print(f"   乐观情景 (+30%): {sim['scenarios']['bull_case']['outcome']}")
            print(f"   基准情景 (+50%): {sim['scenarios']['base_case']['outcome']}")
            print(f"   悲观情景 (+20%): {sim['scenarios']['bear_case']['outcome']}")
        
        print("="*60 + "\n")
    
    elif cmd == "summary":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        summary = engine.get_decision_summary(limit)
        
        print(f"\n最近{limit}笔决策:\n")
        for s in summary:
            print(f"{s['time']} | {s['coin'][:15]:15} | {s['decision']:6} | {s['confidence']:6} | {', '.join(s['reasons'])[:50]}")
        print()
    
    elif cmd == "simulate":
        if len(sys.argv) < 9:
            print("Usage: python okx_decision.py simulate <coin> <direction> <price> <position> <leverage> <sl> <tp>")
            return
        
        result = engine.simulate_scenario(
            coin=sys.argv[2],
            direction=sys.argv[3],
            entry_price=float(sys.argv[4]),
            position_usdt=float(sys.argv[5]),
            leverage=int(sys.argv[6]),
            stop_loss_pct=float(sys.argv[7]),
            take_profit_pct=float(sys.argv[8])
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "avoid":
        if len(sys.argv) < 5:
            print("Usage: python okx_decision.py avoid <coin> <signal> <market_regime>")
            return
        
        should_avoid, reason = engine.check_avoid_conditions(sys.argv[2], sys.argv[3], sys.argv[4])
        if should_avoid:
            print(f"⚠️ 避免交易：{reason}")
        else:
            print("✅ 可以交易")


if __name__ == "__main__":
    main()
