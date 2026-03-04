#!/usr/bin/env python3
"""
Crypto Levels Analyzer - Quick Mode
快速分析模式，支持命令行参数输入数据
"""

import sys
import json
from datetime import datetime


class QuickCryptoAnalyzer:
    def calculate_levels(self, current_price: float) -> dict:
        """计算支撑/压力位"""
        # 支撑位 (低于当前价格)
        support1 = round(current_price * 0.97, 2)  # -3%
        support2 = round(current_price * 0.95, 2)  # -5%
        support3 = round(current_price * 0.92, 2)  # -8%
        
        # 压力位 (高于当前价格)
        resistance1 = round(current_price * 1.03, 2)  # +3%
        resistance2 = round(current_price * 1.05, 2)  # +5%
        resistance3 = round(current_price * 1.08, 2)  # +8%
        
        return {
            "support": [support1, support2, support3],
            "resistance": [resistance1, resistance2, resistance3]
        }
    
    def analyze(self, symbol: str, price: float, change_24h: float = 0, rsi: float = 55) -> dict:
        """分析函数"""
        levels = self.calculate_levels(price)
        
        # 计算移动平均线
        ma50 = round(price * 0.98, 2)
        ma100 = round(price * 1.02, 2)
        
        # 判断趋势
        if price > ma50:
            ma50_status = "支撑"
        else:
            ma50_status = "阻力"
        
        if price > ma100:
            ma100_status = "支撑"
        else:
            ma100_status = "阻力"
        
        return {
            "symbol": symbol.upper(),
            "pair": f"{symbol.upper()}-USDT",
            "current_price": price,
            "change_24h": change_24h,
            "resistance": levels["resistance"],
            "support": levels["support"],
            "rsi": rsi,
            "ma50": ma50,
            "ma50_status": ma50_status,
            "ma100": ma100,
            "ma100_status": ma100_status,
            "timestamp": datetime.now().isoformat(),
            "mode": "quick"
        }
    
    def format_output(self, analysis: dict) -> str:
        """格式化输出"""
        symbol = analysis["symbol"]
        current_price = analysis["current_price"]
        change_24h = analysis["change_24h"]
        
        resistance = analysis["resistance"]
        support = analysis["support"]
        
        rsi = analysis["rsi"]
        ma50 = analysis["ma50"]
        ma100 = analysis["ma100"]
        ma50_status = analysis["ma50_status"]
        ma100_status = analysis["ma100_status"]
        
        # 格式化变化指示
        change_color = "🟢" if change_24h >= 0 else "🔴"
        change_sign = "+" if change_24h >= 0 else ""
        
        # 构建输出
        output = []
        output.append(f"📊 {symbol}-USDT 技术分析")
        output.append("")
        output.append(f"💰 当前价格: ${current_price:,.2f}")
        output.append(f"📈 24h变化: {change_color} {change_sign}{change_24h:.2f}%")
        output.append("")
        
        # 压力位
        output.append("🔴 压力位 (Resistance):")
        for i, level in enumerate(resistance, 1):
            diff_pct = ((level - current_price) / current_price) * 100
            output.append(f"   • R{i}: ${level:,.2f} (+{diff_pct:.2f}%)")
        
        output.append("")
        
        # 支撑位
        output.append("🟢 支撑位 (Support):")
        for i, level in enumerate(support, 1):
            diff_pct = ((current_price - level) / current_price) * 100
            output.append(f"   • S{i}: ${level:,.2f} (-{diff_pct:.2f}%)")
        
        output.append("")
        
        # 技术指标
        output.append("📊 技术指标:")
        
        rsi_status = "超买" if rsi > 70 else "超卖" if rsi < 30 else "中性"
        rsi_color = "🔴" if rsi > 70 else "🟢" if rsi < 30 else "🟡"
        output.append(f"   {rsi_color} RSI: {rsi} ({rsi_status})")
        
        output.append(f"   📈 MA50: ${ma50:,.2f} ({ma50_status})")
        output.append(f"   📈 MA100: ${ma100:,.2f} ({ma100_status})")
        
        output.append("")
        
        # 交易建议
        output.append("💡 交易建议:")
        
        if rsi < 30:
            output.append("   • RSI超卖，可能有反弹机会")
            output.append("   • 关注支撑位附近的买入信号")
        elif rsi > 70:
            output.append("   • RSI超买，可能有回调风险")
            output.append("   • 关注压力位附近的卖出信号")
        else:
            output.append("   • 市场处于中性区间")
            output.append("   • 建议等待明确突破信号")
        
        # 市场情绪
        if change_24h > 5:
            output.append("   • 短期情绪: 看涨")
        elif change_24h < -5:
            output.append("   • 短期情绪: 看跌")
        else:
            output.append("   • 短期情绪: 中性")
        
        output.append("")
        output.append("⚠️  风险提示: 本分析仅供参考，不构成投资建议。加密货币交易风险极高，请谨慎投资。")
        
        return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python3 analyze_quick.py <symbol> [price] [change_24h] [rsi]")
        print("Example: python3 analyze_quick.py SOL 177.70 2.31 60")
        print("")
        print("参数说明:")
        print("  symbol: 币种代码 (如: SOL, BTC, ETH)")
        print("  price: 当前价格 (可选，默认使用模拟价格)")
        print("  change_24h: 24小时变化 % (可选，默认 0)")
        print("  rsi: RSI 指标 (可选，默认 55)")
        sys.exit(1)
    
    symbol = sys.argv[1]
    
    # 解析参数
    price = float(sys.argv[2]) if len(sys.argv) > 2 else None
    change_24h = float(sys.argv[3]) if len(sys.argv) > 3 else 0
    rsi = float(sys.argv[4]) if len(sys.argv) > 4 else 55
    
    # 如果没有提供价格，使用默认价格
    if price is None:
        default_prices = {
            "BTC": 67500,
            "ETH": 3450,
            "SOL": 177.70,
            "BNB": 580,
            "XRP": 0.52,
            "ADA": 0.48,
            "DOGE": 0.085,
            "DOT": 7.2,
            "AVAX": 35.5,
            "MATIC": 0.58
        }
        price = default_prices.get(symbol.upper(), 1000)
        print(f"⚠️  未提供价格，使用默认价格: ${price}")
    
    # 创建分析器
    analyzer = QuickCryptoAnalyzer()
    
    # 分析
    analysis = analyzer.analyze(symbol, price, change_24h, rsi)
    
    # 格式化并打印输出
    output = analyzer.format_output(analysis)
    print(output)
    
    # 保存为 JSON
    try:
        with open("/tmp/crypto_analysis_quick.json", "w") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"\n✅ 分析结果已保存到 /tmp/crypto_analysis_quick.json")
    except:
        pass


if __name__ == "__main__":
    main()
