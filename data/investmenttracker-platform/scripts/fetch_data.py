#!/usr/bin/env python3
"""
InvestmentTracker MCP API 数据获取脚本

此脚本用于从 InvestmentTracker MCP API 获取投资数据，
包括投资组合、交易记录和分析报告。
"""

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class APIConfig:
    """API 配置"""
    base_url: str = "https://investmenttracker-ingest-production.up.railway.app/mcp"
    auth_token: str = "it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes"
    timeout: int = 30
    retry_attempts: int = 3

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
    average_cost: float
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
    name: str
    asset_type: str
    quantity: float
    price: float
    total: float
    fee: float
    status: str
    notes: Optional[str] = None
    tags: Optional[List[str]] = None

class InvestmentTrackerClient:
    """InvestmentTracker MCP API 客户端"""
    
    def __init__(self, config: Optional[APIConfig] = None):
        self.config = config or APIConfig()
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.config.auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "InvestmentTracker-Platform/1.0.0"
        })
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 API 请求"""
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        
        for attempt in range(self.config.retry_attempts):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.config.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.warning(f"API 请求失败 (尝试 {attempt + 1}/{self.config.retry_attempts}): {e}")
                if attempt == self.config.retry_attempts - 1:
                    raise
                # 指数退避
                import time
                time.sleep(2 ** attempt)
        
        raise Exception("所有重试尝试都失败了")
    
    def get_portfolio(self, include_analysis: bool = False) -> Dict[str, Any]:
        """获取投资组合数据"""
        params = {}
        if include_analysis:
            params["include_analysis"] = "true"
        
        return self._make_request("GET", "portfolio", params=params)
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """获取投资组合摘要"""
        return self._make_request("GET", "portfolio/summary")
    
    def get_asset_holding(self, symbol: str) -> Dict[str, Any]:
        """获取特定资产持仓"""
        return self._make_request("GET", f"portfolio/{symbol}")
    
    def get_transactions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        symbol: Optional[str] = None,
        transaction_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """获取交易记录"""
        params = {
            "page": page,
            "page_size": page_size
        }
        
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if symbol:
            params["symbol"] = symbol
        if transaction_type:
            params["type"] = transaction_type
        
        return self._make_request("GET", "transactions", params=params)
    
    def get_recent_transactions(self, limit: int = 10) -> Dict[str, Any]:
        """获取最近交易记录"""
        return self._make_request("GET", "transactions/recent", params={"limit": limit})
    
    def get_returns_analysis(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        benchmark: str = "S&P 500"
    ) -> Dict[str, Any]:
        """获取收益分析"""
        params = {"benchmark": benchmark}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        
        return self._make_request("GET", "analytics/returns", params=params)
    
    def get_risk_analysis(self) -> Dict[str, Any]:
        """获取风险分析"""
        return self._make_request("GET", "analytics/risk")
    
    def get_performance_analysis(self, benchmark: str = "S&P 500") -> Dict[str, Any]:
        """获取表现分析"""
        return self._make_request("GET", "analytics/performance", params={"benchmark": benchmark})
    
    def get_comprehensive_report(
        self,
        period: str = "monthly",
        detail_level: str = "medium"
    ) -> Dict[str, Any]:
        """获取综合报告"""
        params = {
            "period": period,
            "detail_level": detail_level
        }
        return self._make_request("GET", "analytics/full", params=params)
    
    def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """获取市场数据"""
        return self._make_request("GET", f"market/{symbol}")
    
    def get_market_trends(self) -> Dict[str, Any]:
        """获取市场趋势"""
        return self._make_request("GET", "market/trends")

class DataProcessor:
    """数据处理类"""
    
    @staticmethod
    def format_portfolio_for_display(portfolio_data: Dict[str, Any]) -> str:
        """格式化投资组合数据用于显示"""
        if portfolio_data.get("status") != "success":
            return "无法获取投资组合数据"
        
        data = portfolio_data.get("data", {})
        assets = data.get("assets", [])
        
        output = []
        output.append("=" * 60)
        output.append("投资组合概览")
        output.append("=" * 60)
        output.append(f"总价值: ${data.get('total_value', 0):,.2f}")
        output.append(f"总投资: ${data.get('total_invested', 0):,.2f}")
        output.append(f"总收益: ${data.get('total_return', 0):,.2f}")
        output.append(f"收益率: {data.get('return_percentage', 0):.1f}%")
        output.append(f"最后更新: {data.get('last_updated', 'N/A')}")
        output.append("")
        
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
        
        return "\n".join(output)
    
    @staticmethod
    def format_transactions_for_display(transactions_data: Dict[str, Any]) -> str:
        """格式化交易记录数据用于显示"""
        if transactions_data.get("status") != "success":
            return "无法获取交易记录"
        
        data = transactions_data.get("data", {})
        transactions = data.get("transactions", [])
        summary = data.get("summary", {})
        
        output = []
        output.append("=" * 60)
        output.append("交易记录")
        output.append("=" * 60)
        
        if summary:
            output.append(f"总买入: ${summary.get('total_buy', 0):,.2f}")
            output.append(f"总卖出: ${summary.get('total_sell', 0):,.2f}")
            output.append(f"总费用: ${summary.get('total_fees', 0):,.2f}")
            output.append(f"净流入: ${summary.get('net_flow', 0):,.2f}")
            output.append("")
        
        if transactions:
            output.append("最近交易:")
            output.append("-" * 60)
            for txn in transactions[:10]:  # 显示最近10笔交易
                output.append(
                    f"{txn.get('date', 'N/A')[:10]} "
                    f"{txn.get('type', 'N/A'):<6} "
                    f"{txn.get('symbol', 'N/A'):<6} "
                    f"数量: {txn.get('quantity', 0):.4f} "
                    f"价格: ${txn.get('price', 0):,.2f} "
                    f"总额: ${txn.get('total', 0):,.2f}"
                )
        
        return "\n".join(output)
    
    @staticmethod
    def format_analysis_for_display(analysis_data: Dict[str, Any]) -> str:
        """格式化分析数据用于显示"""
        if analysis_data.get("status") != "success":
            return "无法获取分析数据"
        
        data = analysis_data.get("data", {})
        
        output = []
        output.append("=" * 60)
        output.append("投资分析报告")
        output.append("=" * 60)
        
        # 检查不同类型的分析数据
        if "returns_analysis" in data:
            returns = data["returns_analysis"]
            output.append("收益分析:")
            output.append(f"总收益率: {returns.get('total_return_percentage', 0):.1f}%")
            output.append(f"年化收益率: {returns.get('annualized_return', 0):.1f}%")
            output.append(f"阿尔法: {returns.get('benchmark_comparison', {}).get('alpha', 0):.1f}")
            output.append("")
        
        if "risk_analysis" in data:
            risk = data["risk_analysis"]
            output.append("风险分析:")
            output.append(f"波动率: {risk.get('volatility_metrics', {}).get('portfolio_volatility', 0):.1f}%")
            output.append(f"贝塔: {risk.get('volatility_metrics', {}).get('beta', 0):.2f}")
            output.append(f"最大回撤: {risk.get('drawdown_analysis', {}).get('max_drawdown', 0):.1f}%")
            output.append("")
        
        if "performance_analysis" in data:
            performance = data["performance_analysis"]
            output.append("表现分析:")
            output.append(f"夏普比率: {performance.get('key_metrics', {}).get('sharpe_ratio', 0):.2f}")
            output.append(f"索提诺比率: {performance.get('key_metrics', {}).get('sortino_ratio', 0):.2f}")
            output.append(f"信息比率: {performance.get('key_metrics', {}).get('information_ratio', 0):.2f}")
        
        return "\n".join(output)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="InvestmentTracker MCP API 客户端")
    parser.add_argument("--action", choices=[
        "portfolio", "portfolio-summary", "transactions", "recent-transactions",
        "returns", "risk", "performance", "full-report", "market-data"
    ], default="portfolio", help="要执行的操作")
    parser.add_argument("--symbol", help="资产符号（如 BTC、AAPL）")
    parser.add_argument("--start-date", help="开始日期 (YYYY-MM-DD)")
    parser.add_argument("--end-date", help="结束日期 (YYYY-MM-DD)")
    parser.add_argument("--type", choices=["BUY", "SELL", "DIVIDEND"], help="交易类型")
    parser.add_argument("--limit", type=int, default=10, help="限制返回数量")
    parser.add_argument("--output", choices=["display", "json"], default="display", help="输出格式")
    
    args = parser.parse_args()
    
    # 初始化客户端
    client = InvestmentTrackerClient()
    processor = DataProcessor()
    
    try:
        result = None
        
        if args.action == "portfolio":
            result = client.get_portfolio()
        elif args.action == "portfolio-summary":
            result = client.get_portfolio_summary()
        elif args.action == "transactions":
            result = client.get_transactions(
                start_date=args.start_date,
                end_date=args.end_date,
                symbol=args.symbol,
                transaction_type=args.type
            )
        elif args.action == "recent-transactions":
            result = client.get_recent_transactions(limit=args.limit)
        elif args.action == "returns":
            result = client.get_returns_analysis(
                start_date=args.start_date,
                end_date=args.end_date
            )
        elif args.action == "risk":
            result = client.get_risk_analysis()
        elif args.action == "performance":
            result = client.get_performance_analysis()
        elif args.action == "full-report":
            result = client.get_comprehensive_report()
        elif args.action == "market-data" and args.symbol:
            result = client.get_market_data(args.symbol)
        else:
            print("错误: 需要指定资产符号")
            return
        
        if args.output == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            if args.action in ["portfolio", "portfolio-summary"]:
                print(processor.format_portfolio_for_display(result))
            elif args.action in ["transactions", "recent-transactions"]:
                print(processor.format_transactions_for_display(result))
            elif args.action in ["returns", "risk", "performance", "full-report"]:
                print(processor.format_analysis_for_display(result))
            elif args.action == "market-data":
                print(json.dumps(result, indent=2, ensure_ascii=False))
    
    except Exception as e:
        logger.error(f"操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()