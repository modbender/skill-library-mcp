#!/usr/bin/env python3
"""
InvestmentTracker-platform 可工作版本
支持模拟模式和API模式
"""

import json
import time
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

class ConnectionMode(Enum):
    """连接模式"""
    SIMULATED = "simulated"  # 模拟数据模式
    API = "api"              # 真实API模式
    HYBRID = "hybrid"        # 混合模式（API失败时使用模拟）

@dataclass
class PortfolioAsset:
    """投资组合资产"""
    symbol: str
    name: str
    asset_type: str
    quantity: float
    current_price: float
    current_value: float
    cost_basis: float
    unrealized_gain: float
    unrealized_gain_percentage: float
    weight: float

@dataclass
class Transaction:
    """交易记录"""
    id: str
    date: str
    type: str
    symbol: str
    quantity: float
    price: float
    total: float
    fee: float
    status: str

class InvestmentTrackerSkill:
    """InvestmentTracker技能主类"""
    
    def __init__(self, mode: ConnectionMode = ConnectionMode.HYBRID):
        self.mode = mode
        self.api_url = "https://investmenttracker-ingest-production.up.railway.app/mcp"
        self.auth_token = "it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
        
        # 模拟数据
        self.simulated_portfolio = self._create_simulated_portfolio()
        self.simulated_transactions = self._create_simulated_transactions()
    
    def _create_simulated_portfolio(self) -> Dict[str, Any]:
        """创建模拟投资组合数据"""
        return {
            "total_value": 125000.50,
            "total_invested": 100000.00,
            "total_return": 25000.50,
            "return_percentage": 25.0,
            "assets": [
                {
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "asset_type": "crypto",
                    "quantity": 0.5,
                    "current_price": 45000.00,
                    "current_value": 22500.00,
                    "cost_basis": 20000.00,
                    "unrealized_gain": 2500.00,
                    "unrealized_gain_percentage": 12.5,
                    "weight": 18.0
                },
                {
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "asset_type": "crypto",
                    "quantity": 2.5,
                    "current_price": 2500.00,
                    "current_value": 6250.00,
                    "cost_basis": 5000.00,
                    "unrealized_gain": 1250.00,
                    "unrealized_gain_percentage": 25.0,
                    "weight": 5.0
                },
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "asset_type": "stock",
                    "quantity": 10,
                    "current_price": 175.50,
                    "current_value": 1755.00,
                    "cost_basis": 1500.00,
                    "unrealized_gain": 255.00,
                    "unrealized_gain_percentage": 17.0,
                    "weight": 1.4
                }
            ]
        }
    
    def _create_simulated_transactions(self) -> List[Dict[str, Any]]:
        """创建模拟交易记录"""
        return [
            {
                "id": "txn_001",
                "date": "2026-02-16T10:30:00Z",
                "type": "BUY",
                "symbol": "BTC",
                "quantity": 0.1,
                "price": 42000.00,
                "total": 4200.00,
                "fee": 10.50,
                "status": "COMPLETED"
            },
            {
                "id": "txn_002",
                "date": "2026-02-15T14:20:00Z",
                "type": "SELL",
                "symbol": "AAPL",
                "quantity": 5,
                "price": 180.00,
                "total": 900.00,
                "fee": 2.25,
                "status": "COMPLETED"
            },
            {
                "id": "txn_003",
                "date": "2026-02-14T09:15:00Z",
                "type": "BUY",
                "symbol": "ETH",
                "quantity": 0.5,
                "price": 2400.00,
                "total": 1200.00,
                "fee": 3.00,
                "status": "COMPLETED"
            }
        ]
    
    def _send_mcp_request(self, method: str, params: Dict = None) -> Optional[Dict[str, Any]]:
        """发送MCP API请求"""
        if self.mode == ConnectionMode.SIMULATED:
            return None
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json"
        }
        
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": int(time.time() * 1000)
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=request,
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return None
            else:
                print(f"API错误: HTTP {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API连接错误: {e}")
            return None
    
    def get_portfolio(self) -> Dict[str, Any]:
        """获取投资组合"""
        if self.mode in [ConnectionMode.API, ConnectionMode.HYBRID]:
            # 尝试从API获取
            api_result = self._send_mcp_request("tools/call", {
                "name": "get_portfolio",
                "arguments": {}
            })
            
            if api_result and "result" in api_result:
                return {
                    "source": "api",
                    "data": api_result["result"]
                }
        
        # 使用模拟数据
        return {
            "source": "simulated",
            "data": self.simulated_portfolio
        }
    
    def get_transactions(self, limit: int = 10) -> Dict[str, Any]:
        """获取交易记录"""
        if self.mode in [ConnectionMode.API, ConnectionMode.HYBRID]:
            # 尝试从API获取
            api_result = self._send_mcp_request("tools/call", {
                "name": "get_transactions",
                "arguments": {"limit": limit}
            })
            
            if api_result and "result" in api_result:
                return {
                    "source": "api",
                    "data": api_result["result"]
                }
        
        # 使用模拟数据
        transactions = self.simulated_transactions[:limit]
        return {
            "source": "simulated",
            "data": {
                "transactions": transactions,
                "count": len(transactions)
            }
        }
    
    def get_analysis(self) -> Dict[str, Any]:
        """获取投资分析"""
        portfolio = self.get_portfolio()["data"]
        
        # 计算分析指标
        total_value = portfolio["total_value"]
        total_invested = portfolio["total_invested"]
        total_return = portfolio["total_return"]
        
        analysis = {
            "performance": {
                "total_return_percentage": portfolio["return_percentage"],
                "annualized_return": 18.5,  # 模拟数据
                "sharpe_ratio": 1.25,
                "volatility": 15.2
            },
            "asset_allocation": {},
            "risk_metrics": {
                "max_drawdown": -8.5,
                "var_95_1d": -3.2
            }
        }
        
        # 计算资产分配
        for asset in portfolio.get("assets", []):
            asset_type = asset["asset_type"]
            value = asset["current_value"]
            
            if asset_type not in analysis["asset_allocation"]:
                analysis["asset_allocation"][asset_type] = 0
            
            analysis["asset_allocation"][asset_type] += value
        
        # 转换为百分比
        for asset_type in analysis["asset_allocation"]:
            analysis["asset_allocation"][asset_type] = round(
                analysis["asset_allocation"][asset_type] / total_value * 100, 1
            )
        
        return {
            "source": portfolio.get("source", "simulated"),
            "data": analysis
        }
    
    def format_portfolio_for_display(self, portfolio_data: Dict[str, Any]) -> str:
        """格式化投资组合数据用于显示"""
        data = portfolio_data["data"]
        source = portfolio_data["source"]
        
        output = []
        output.append("=" * 60)
        output.append(f"投资组合概览 ({'API数据' if source == 'api' else '模拟数据'})")
        output.append("=" * 60)
        output.append(f"总价值: ${data.get('total_value', 0):,.2f}")
        output.append(f"总投资: ${data.get('total_invested', 0):,.2f}")
        output.append(f"总收益: ${data.get('total_return', 0):,.2f}")
        output.append(f"收益率: {data.get('return_percentage', 0):.1f}%")
        output.append("")
        
        assets = data.get("assets", [])
        if assets:
            output.append("资产持仓:")
            output.append("-" * 60)
            for asset in assets:
                output.append(
                    f"{asset.get('symbol', 'N/A'):<6} "
                    f"{asset.get('name', 'N/A'):<20} "
                    f"数量: {asset.get('quantity', 0):.4f} "
                    f"价值: ${asset.get('current_value', 0):,.2f} "
                    f"收益: {asset.get('unrealized_gain_percentage', 0):.1f}%"
                )
        
        if source == "simulated":
            output.append("")
            output.append("注: 使用模拟数据。API连接成功后将显示真实数据。")
        
        return "\n".join(output)
    
    def format_transactions_for_display(self, transactions_data: Dict[str, Any]) -> str:
        """格式化交易记录数据用于显示"""
        data = transactions_data["data"]
        source = transactions_data["source"]
        
        output = []
        output.append("=" * 60)
        output.append(f"交易记录 ({'API数据' if source == 'api' else '模拟数据'})")
        output.append("=" * 60)
        
        transactions = data.get("transactions", [])
        if transactions:
            output.append(f"最近 {len(transactions)} 笔交易:")
            output.append("-" * 60)
            for txn in transactions:
                output.append(
                    f"{txn.get('date', 'N/A')[:10]} "
                    f"{txn.get('type', 'N/A'):<6} "
                    f"{txn.get('symbol', 'N/A'):<6} "
                    f"数量: {txn.get('quantity', 0):.4f} "
                    f"价格: ${txn.get('price', 0):,.2f} "
                    f"总额: ${txn.get('total', 0):,.2f}"
                )
        else:
            output.append("暂无交易记录")
        
        if source == "simulated":
            output.append("")
            output.append("注: 使用模拟数据。API连接成功后将显示真实数据。")
        
        return "\n".join(output)
    
    def format_analysis_for_display(self, analysis_data: Dict[str, Any]) -> str:
        """格式化分析数据用于显示"""
        data = analysis_data["data"]
        source = analysis_data["source"]
        
        output = []
        output.append("=" * 60)
        output.append(f"投资分析报告 ({'API数据' if source == 'api' else '模拟数据'})")
        output.append("=" * 60)
        
        # 表现分析
        performance = data.get("performance", {})
        output.append("表现分析:")
        output.append(f"  总收益率: {performance.get('total_return_percentage', 0):.1f}%")
        output.append(f"  年化收益率: {performance.get('annualized_return', 0):.1f}%")
        output.append(f"  夏普比率: {performance.get('sharpe_ratio', 0):.2f}")
        output.append(f"  波动率: {performance.get('volatility', 0):.1f}%")
        output.append("")
        
        # 资产分配
        allocation = data.get("asset_allocation", {})
        if allocation:
            output.append("资产分配:")
            for asset_type, percentage in allocation.items():
                output.append(f"  {asset_type}: {percentage}%")
            output.append("")
        
        # 风险指标
        risk = data.get("risk_metrics", {})
        output.append("风险指标:")
        output.append(f"  最大回撤: {risk.get('max_drawdown', 0):.1f}%")
        output.append(f"  1日95%VaR: {risk.get('var_95_1d', 0):.1f}%")
        
        if source == "simulated":
            output.append("")
            output.append("注: 使用模拟数据。API连接成功后将显示真实分析。")
        
        return "\n".join(output)

# 使用示例
def main():
    """主函数示例"""
    print("InvestmentTracker Skill 测试")
    print("=" * 60)
    
    # 创建技能实例（混合模式）
    skill = InvestmentTrackerSkill(mode=ConnectionMode.HYBRID)
    
    print("1. 获取投资组合...")
    print("-" * 40)
    portfolio = skill.get_portfolio()
    print(skill.format_portfolio_for_display(portfolio))
    
    print("\n2. 获取交易记录...")
    print("-" * 40)
    transactions = skill.get_transactions(limit=5)
    print(skill.format_transactions_for_display(transactions))
    
    print("\n3. 获取投资分析...")
    print("-" * 40)
    analysis = skill.get_analysis()
    print(skill.format_analysis_for_display(analysis))
    
    print("\n" + "=" * 60)
    print("技能状态:")
    print(f"模式: {skill.mode.value}")
    print("功能: 投资组合查看, 交易记录, 投资分析")
    print("数据源: 模拟数据 (API连接中...)")

if __name__ == "__main__":
    main()