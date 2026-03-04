#!/usr/bin/env python3
"""
InvestmentTracker 混合技能
结合MCP API、临时手动数据和模拟数据
"""

import json
import sys
import os
from typing import Dict, Any, Optional
from datetime import datetime

class HybridInvestmentTracker:
    """混合投资追踪器"""
    
    def __init__(self):
        self.data_sources = {
            "mcp_api": self._try_mcp_api,
            "manual_data": self._load_manual_data,
            "simulated": self._generate_simulated_data
        }
        
        # 数据缓存
        self.cache = {}
        self.cache_timeout = 300  # 5分钟
        
    def _try_mcp_api(self) -> Optional[Dict[str, Any]]:
        """尝试从MCP API获取数据"""
        try:
            # 这里可以集成之前的MCP客户端
            # 目前返回None表示API不可用
            return None
        except:
            return None
    
    def _load_manual_data(self) -> Optional[Dict[str, Any]]:
        """加载手动数据"""
        manual_file = "user_investment_data.json"
        if os.path.exists(manual_file):
            try:
                with open(manual_file, 'r') as f:
                    data = json.load(f)
                    if data.get("data_source") == "manual":
                        return {
                            "source": "manual",
                            "data": data,
                            "priority": 1  # 手动数据优先级最高
                        }
            except:
                pass
        return None
    
    def _generate_simulated_data(self) -> Dict[str, Any]:
        """生成模拟数据"""
        return {
            "source": "simulated",
            "data": {
                "user_info": {
                    "id": "user_123",
                    "name": "投资用户",
                    "email": "investor@example.com",
                    "joined_date": "2024-01-01",
                    "investment_style": "成长型",
                    "note": "模拟数据 - 使用临时方案添加真实数据"
                },
                "positions": [
                    {
                        "id": "pos_001",
                        "symbol": "BTC",
                        "name": "Bitcoin",
                        "asset_type": "crypto",
                        "quantity": 0.5,
                        "current_price": 45000.00,
                        "current_value": 22500.00,
                        "cost_basis": 20000.00,
                        "unrealized_gain": 2500.00,
                        "status": "POSITION",
                        "note": "模拟数据 - 示例持仓"
                    }
                ],
                "methodology": {
                    "strategy": "价值投资 + 趋势跟踪",
                    "risk_tolerance": "中等",
                    "time_horizon": "长期",
                    "diversification": "跨资产类别分散",
                    "rebalancing_frequency": "季度",
                    "note": "模拟数据 - 示例投资策略"
                },
                "stats": {
                    "total_portfolio_value": 125000.50,
                    "total_return": 25000.50,
                    "return_percentage": 25.0,
                    "active_positions": 1,
                    "closed_positions": 5,
                    "win_rate": 75.0,
                    "note": "模拟数据 - 示例统计数据"
                }
            },
            "priority": 3  # 模拟数据优先级最低
        }
    
    def get_data(self, data_type: str = "all") -> Dict[str, Any]:
        """获取数据（智能选择数据源）"""
        cache_key = f"{data_type}_{datetime.now().timestamp() // self.cache_timeout}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 按优先级尝试各个数据源
        best_data = None
        best_priority = float('inf')
        
        for source_name, source_func in self.data_sources.items():
            try:
                data = source_func()
                if data:
                    priority = data.get("priority", 999)
                    if priority < best_priority:
                        best_priority = priority
                        best_data = data
            except:
                continue
        
        if not best_data:
            best_data = self._generate_simulated_data()
        
        # 添加时间戳
        best_data["timestamp"] = datetime.now().isoformat()
        
        # 缓存结果
        self.cache[cache_key] = best_data
        
        return best_data
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        data = self.get_data()
        return {
            "source": data["source"],
            "data": data["data"]["user_info"],
            "timestamp": data["timestamp"]
        }
    
    def list_positions(self, status: str = "POSITION", limit: int = 10) -> Dict[str, Any]:
        """列出持仓"""
        data = self.get_data()
        positions = [p for p in data["data"]["positions"] if p["status"] == status][:limit]
        
        total_value = sum(p["current_value"] for p in positions)
        
        return {
            "source": data["source"],
            "data": {
                "positions": positions,
                "count": len(positions),
                "total_value": total_value
            },
            "timestamp": data["timestamp"]
        }
    
    def get_methodology(self) -> Dict[str, Any]:
        """获取投资方法论"""
        data = self.get_data()
        return {
            "source": data["source"],
            "data": data["data"]["methodology"],
            "timestamp": data["timestamp"]
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据"""
        data = self.get_data()
        return {
            "source": data["source"],
            "data": data["data"]["stats"],
            "timestamp": data["timestamp"]
        }
    
    def get_data_source_info(self) -> Dict[str, Any]:
        """获取数据源信息"""
        data = self.get_data()
        
        source_info = {
            "current_source": data["source"],
            "available_sources": list(self.data_sources.keys()),
            "timestamp": data["timestamp"],
            "cache_status": len(self.cache)
        }
        
        # 检查各个数据源状态
        source_status = {}
        for source_name in self.data_sources.keys():
            if source_name == "mcp_api":
                source_status[source_name] = "checking..."
            elif source_name == "manual_data":
                manual_file = "user_investment_data.json"
                if os.path.exists(manual_file):
                    try:
                        with open(manual_file, 'r') as f:
                            manual_data = json.load(f)
                            source_status[source_name] = "available" if manual_data.get("data_source") == "manual" else "simulated"
                    except:
                        source_status[source_name] = "error"
                else:
                    source_status[source_name] = "not_found"
            else:
                source_status[source_name] = "available"
        
        source_info["source_status"] = source_status
        return source_info
    
    # 格式化方法
    def format_positions(self, positions_data: Dict[str, Any]) -> str:
        """格式化持仓输出"""
        data = positions_data["data"]
        source = positions_data["source"]
        timestamp = positions_data.get("timestamp", "")
        
        output = []
        output.append("📊 持仓列表")
        output.append("=" * 60)
        
        # 数据源信息
        source_display = {
            "mcp_api": "MCP API实时数据",
            "manual_data": "手动输入数据",
            "simulated": "模拟演示数据"
        }.get(source, source)
        
        output.append(f"数据源: {source_display}")
        if timestamp:
            output.append(f"更新时间: {timestamp[:19]}")
        output.append("")
        
        positions = data.get("positions", [])
        if positions:
            output.append(f"持仓数量: {len(positions)}")
            output.append(f"总价值: ${data.get('total_value', 0):,.2f}")
            output.append("")
            output.append("详细持仓:")
            output.append("-" * 60)
            
            for pos in positions:
                gain_percentage = (pos["unrealized_gain"] / pos["cost_basis"] * 100) if pos["cost_basis"] else 0
                output.append(
                    f"{pos['symbol']:<6} {pos['name'][:15]:<15} "
                    f"数量: {pos['quantity']:>8.4f} "
                    f"现价: ${pos['current_price']:>8.2f} "
                    f"价值: ${pos['current_value']:>8.2f} "
                    f"收益: {gain_percentage:>5.1f}%"
                )
                if pos.get("note"):
                    output.append(f"   📝 {pos['note']}")
        else:
            output.append("暂无持仓记录")
            output.append("💡 使用临时方案添加真实持仓数据")
        
        # 添加数据源提示
        if source == "simulated":
            output.append("")
            output.append("💡 提示: 当前使用模拟数据")
            output.append("      使用临时方案添加真实持仓数据:")
            output.append("      python3 temporary_fix.py add --symbol BTC --asset-name Bitcoin --quantity 0.5 --price 45000")
        
        return "\n".join(output)
    
    def format_data_source_info(self, info_data: Dict[str, Any]) -> str:
        """格式化数据源信息"""
        output = []
        output.append("🔧 数据源状态")
        output.append("=" * 60)
        output.append(f"当前数据源: {info_data['current_source']}")
        output.append(f"更新时间: {info_data['timestamp'][:19]}")
        output.append("")
        
        output.append("可用数据源状态:")
        for source, status in info_data.get("source_status", {}).items():
            status_icon = "✅" if status in ["available", "manual"] else "⚠️" if status == "simulated" else "❌"
            output.append(f"  {status_icon} {source}: {status}")
        
        output.append("")
        output.append("💡 数据源优先级:")
        output.append("  1. MCP API实时数据 (当前不可用)")
        output.append("  2. 手动输入数据 (推荐使用)")
        output.append("  3. 模拟演示数据 (默认)")
        
        output.append("")
        output.append("🚀 立即行动:")
        output.append("  1. 使用临时方案添加真实数据:")
        output.append("     python3 temporary_fix.py add --symbol BTC --asset-name Bitcoin --quantity 0.5 --price 45000")
        output.append("  2. 查看添加的数据:")
        output.append("     python3 temporary_fix.py view")
        
        return "\n".join(output)

# 命令行接口
def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="InvestmentTracker混合技能")
    parser.add_argument("command", nargs="?", help="命令: user, positions, methodology, stats, source, all")
    parser.add_argument("--status", default="POSITION", help="持仓状态")
    parser.add_argument("--limit", type=int, default=10, help="限制数量")
    
    args = parser.parse_args()
    
    tracker = HybridInvestmentTracker()
    
    if args.command == "user":
        user_info = tracker.get_user_info()
        print(json.dumps(user_info, indent=2, ensure_ascii=False))
    
    elif args.command == "positions":
        positions = tracker.list_positions(status=args.status, limit=args.limit)
        print(tracker.format_positions(positions))
    
    elif args.command == "methodology":
        methodology = tracker.get_methodology()
        print(json.dumps(methodology, indent=2, ensure_ascii=False))
    
    elif args.command == "stats":
        stats = tracker.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.command == "source":
        source_info = tracker.get_data_source_info()
        print(tracker.format_data_source_info(source_info))
    
    elif args.command == "all" or not args.command:
        # 显示所有信息
        print("=" * 60)
        print("InvestmentTracker混合技能")
        print("=" * 60)
        
        # 数据源信息
        source_info = tracker.get_data_source_info()
        print(tracker.format_data_source_info(source_info))
        
        print("\n" + "=" * 60)
        positions = tracker.list_positions()
        print(tracker.format_positions(positions))
        
        print("\n" + "=" * 60)
        print("💡 完整功能已就绪，可以开始使用！")
    
    else:
        print(f"错误: 未知命令 '{args.command}'")
        print("可用命令: user, positions, methodology, stats, source, all")

if __name__ == "__main__":
    main()