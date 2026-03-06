#!/usr/bin/env python3
"""
InvestmentTracker-platform Skill 修复版本
支持新的mcpServers配置格式
"""

import json
import time
import sys
import os
from typing import Dict, Any, List, Optional
from enum import Enum
import subprocess

class ConnectionMode(Enum):
    """连接模式"""
    API = "api"              # 真实API模式
    SIMULATED = "simulated"  # 模拟数据模式
    HYBRID = "hybrid"        # 混合模式

class InvestmentTrackerSkill:
    """InvestmentTracker技能主类（修复版本）"""
    
    def __init__(self, mode: ConnectionMode = ConnectionMode.HYBRID):
        self.mode = mode
        
        # 加载配置
        self.config = self._load_config()
        
        # 从配置获取MCP服务器信息
        self.mcp_config = self.config.get("mcpServers", {}).get("investmenttracker", {})
        self.api_url = self.mcp_config.get("url", "")
        self.headers = self.mcp_config.get("headers", {})
        
        # 模拟数据
        self.simulated_data = self._create_simulated_data()
        
        print(f"配置加载成功: URL={self.api_url}")
        print(f"Headers: {self.headers}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                print(f"配置文件加载成功: {config_path}")
                return config
        except FileNotFoundError:
            print(f"配置文件不存在: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"配置文件JSON解析错误: {e}")
            return {}
    
    def _create_simulated_data(self) -> Dict[str, Any]:
        """创建模拟数据"""
        return {
            "user": {
                "id": "sim_user_001",
                "name": "模拟用户",
                "email": "simulated@example.com",
                "joined_date": "2024-01-01",
                "investment_style": "成长型"
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
                    "status": "POSITION"
                },
                {
                    "id": "pos_002",
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "asset_type": "crypto",
                    "quantity": 2.0,
                    "current_price": 2500.00,
                    "current_value": 5000.00,
                    "cost_basis": 4000.00,
                    "unrealized_gain": 1000.00,
                    "status": "POSITION"
                }
            ],
            "methodology": {
                "strategy": "价值投资 + 趋势跟踪",
                "risk_tolerance": "中等",
                "time_horizon": "长期",
                "diversification": "跨资产类别分散",
                "rebalancing_frequency": "季度"
            },
            "stats": {
                "total_portfolio_value": 125000.50,
                "total_return": 25000.50,
                "return_percentage": 25.0,
                "active_positions": 3,
                "closed_positions": 12,
                "win_rate": 75.0
            }
        }
    
    def _send_mcp_request(self, method: str, params: Dict = None) -> Optional[Dict[str, Any]]:
        """发送MCP请求（使用curl处理SSE）"""
        if self.mode == ConnectionMode.SIMULATED:
            return None
        
        if not self.api_url:
            print("API URL未配置，使用模拟数据")
            return None
        
        request_id = int(time.time() * 1000)
        request = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": request_id
        }
        
        # 保存请求到临时文件
        request_file = f"/tmp/mcp_request_{request_id}.json"
        with open(request_file, 'w') as f:
            json.dump(request, f)
        
        # 构建curl命令
        cmd = ['curl', '-s', '-N', '-X', 'POST']
        
        # 添加headers
        for key, value in self.headers.items():
            cmd.extend(['-H', f'{key}: {value}'])
        
        # 添加请求数据
        cmd.extend(['--data-binary', f'@{request_file}', self.api_url])
        
        print(f"发送请求到: {self.api_url}")
        print(f"命令: {' '.join(cmd[:10])}...")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"curl命令失败: {result.stderr}")
                return None
            
            # 解析SSE响应
            for line in result.stdout.split('\n'):
                if line.startswith('data: '):
                    try:
                        event_data = json.loads(line[6:])
                        return event_data
                    except json.JSONDecodeError as e:
                        print(f"JSON解析错误: {e}")
                        continue
            
            return None
            
        except subprocess.TimeoutExpired:
            print("请求超时")
            return None
        except Exception as e:
            print(f"请求异常: {e}")
            return None
        finally:
            # 清理临时文件
            if os.path.exists(request_file):
                os.remove(request_file)
    
    def get_user_info(self) -> Dict[str, Any]:
        """获取用户信息"""
        if self.mode == ConnectionMode.SIMULATED:
            return {"source": "simulated", "data": self.simulated_data["user"]}
        
        # 尝试API
        result = self._send_mcp_request("tools/call", {
            "name": "whoami_v1",
            "arguments": {}
        })
        
        if result and "result" in result:
            return {"source": "api", "data": result["result"]}
        
        # API失败，根据模式决定
        if self.mode == ConnectionMode.API:
            return {"source": "api_error", "data": None}
        else:
            return {"source": "simulated", "data": self.simulated_data["user"]}
    
    def list_positions(self, status: str = "POSITION", limit: int = 10) -> Dict[str, Any]:
        """列出持仓"""
        if self.mode == ConnectionMode.SIMULATED:
            positions = [p for p in self.simulated_data["positions"] if p["status"] == status]
            return {"source": "simulated", "data": {"positions": positions[:limit], "count": len(positions)}}
        
        # 尝试API
        result = self._send_mcp_request("tools/call", {
            "name": "positions_list_v1",
            "arguments": {
                "status": status,
                "limit": limit
            }
        })
        
        if result and "result" in result:
            return {"source": "api", "data": result["result"]}
        
        # API失败，根据模式决定
        if self.mode == ConnectionMode.API:
            return {"source": "api_error", "data": None}
        else:
            positions = [p for p in self.simulated_data["positions"] if p["status"] == status]
            return {"source": "simulated", "data": {"positions": positions[:limit], "count": len(positions)}}
    
    def get_methodology(self) -> Dict[str, Any]:
        """获取投资方法论"""
        if self.mode == ConnectionMode.SIMULATED:
            return {"source": "simulated", "data": self.simulated_data["methodology"]}
        
        # 尝试API
        result = self._send_mcp_request("tools/call", {
            "name": "methodology_get_v1",
            "arguments": {}
        })
        
        if result and "result" in result:
            return {"source": "api", "data": result["result"]}
        
        # API失败，根据模式决定
        if self.mode == ConnectionMode.API:
            return {"source": "api_error", "data": None}
        else:
            return {"source": "simulated", "data": self.simulated_data["methodology"]}
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计数据"""
        if self.mode == ConnectionMode.SIMULATED:
            return {"source": "simulated", "data": self.simulated_data["stats"]}
        
        # 尝试API
        result = self._send_mcp_request("tools/call", {
            "name": "stats_quick_v1",
            "arguments": {}
        })
        
        if result and "result" in result:
            return {"source": "api", "data": result["result"]}
        
        # API失败，根据模式决定
        if self.mode == ConnectionMode.API:
            return {"source": "api_error", "data": None}
        else:
            return {"source": "simulated", "data": self.simulated_data["stats"]}
    
    def format_user_info(self, user_data: Dict[str, Any]) -> str:
        """格式化用户信息"""
        if not user_data or "data" not in user_data:
            return "用户信息: 获取失败"
        
        data = user_data["data"]
        source = user_data.get("source", "unknown")
        
        output = []
        output.append(f"👤 用户信息 (来源: {source})")
        output.append("-" * 40)
        
        if data:
            output.append(f"ID: {data.get('id', 'N/A')}")
            output.append(f"名称: {data.get('name', 'N/A')}")
            output.append(f"邮箱: {data.get('email', 'N/A')}")
            output.append(f"加入日期: {data.get('joined_date', 'N/A')}")
            output.append(f"投资风格: {data.get('investment_style', 'N/A')}")
        else:
            output.append("数据为空")
        
        return "\n".join(output)
    
    def format_positions(self, positions_data: Dict[str, Any]) -> str:
        """格式化持仓列表"""
        if not positions_data or "data" not in positions_data:
            return "持仓列表: 获取失败"
        
        data = positions_data["data"]
        source = positions_data.get("source", "unknown")
        
        output = []
        output.append(f"📊 持仓列表 (来源: {source})")
        output.append("=" * 60)
        
        if not data or "items" not in data or not data["items"]:
            output.append("暂无持仓")
        else:
            positions = data["items"]
            output.append(f"持仓数量: {len(positions)}")
            output.append("=" * 60)
            
            for i, pos in enumerate(positions, 1):
                output.append(f"{i}. {pos.get('code', 'N/A')} - {pos.get('name', 'N/A')}")
                output.append(f"   持仓状态: {pos.get('status', 'N/A')}")
                output.append(f"   货币: {pos.get('currency', 'N/A')}")
                output.append(f"   数量: {pos.get('quantity', 'N/A')}")
                output.append(f"   买入日期: {pos.get('buy_date', 'N/A')}")
                output.append(f"   投资组合: {pos.get('portfolio', 'N/A')}")
                output.append(f"   最后更新: {pos.get('source_updated_at', 'N/A')}")
                output.append()
        
        return "\n".join(output)
    
    def format_methodology(self, methodology_data: Dict[str, Any]) -> str:
        """格式化投资方法论"""
        if not methodology_data or "data" not in methodology_data:
            return "投资方法论: 获取失败"
        
        data = methodology_data["data"]
        source = methodology_data.get("source", "unknown")
        
        output = []
        output.append(f"📈 投资方法论 (来源: {source})")
        output.append("-" * 40)
        
        if data:
            output.append(f"策略: {data.get('strategy', 'N/A')}")
            output.append(f"风险承受能力: {data.get('risk_tolerance', 'N/A')}")
            output.append(f"投资期限: {data.get('time_horizon', 'N/A')}")
            output.append(f"分散化: {data.get('diversification', 'N/A')}")
            output.append(f"再平衡频率: {data.get('rebalance_frequency', 'N/A')}")
        else:
            output.append("数据为空")
        
        return "\n".join(output)
    
    def format_stats(self, stats_data: Dict[str, Any]) -> str:
        """格式化统计数据"""
        if not stats_data or "data" not in stats_data:
            return "投资统计数据: 获取失败"
        
        data = stats_data["data"]
        source = stats_data.get("source", "unknown")
        
        output = []
        output.append(f"📊 投资统计数据 (来源: {source})")
        output.append("-" * 40)
        
        if data:
            total_value = data.get("total_value", 0)
            total_gain = data.get("total_gain", 0)
            return_rate = data.get("return_rate", 0)
            
            output.append(f"投资组合总价值: ${total_value:,.2f}")
            output.append(f"总收益: ${total_gain:,.2f}")
            output.append(f"收益率: {return_rate:.2f}%")
            output.append(f"活跃持仓: {data.get('active_positions', 0)}")
            output.append(f"已平仓持仓: {data.get('closed_positions', 0)}")
            output.append(f"胜率: {data.get('win_rate', 0):.2f}%")
        else:
            output.append("数据为空")
        
        return "\n".join(output)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="InvestmentTracker Skill")
    parser.add_argument("command", nargs="?", default="all", 
                       choices=["all", "user", "positions", "methodology", "stats", "help"],
                       help="命令: all, user, positions, methodology, stats, help")
    parser.add_argument("--mode", default="hybrid",
                       choices=["api", "simulated", "hybrid"],
                       help="连接模式: api, simulated, hybrid")
    parser.add_argument("--status", default="POSITION",
                       choices=["POSITION", "CLOSE"],
                       help="持仓状态: POSITION, CLOSE")
    parser.add_argument("--limit", type=int, default=10,
                       help="持仓数量限制")
    
    args = parser.parse_args()
    
    # 设置连接模式
    mode_map = {
        "api": ConnectionMode.API,
        "simulated": ConnectionMode.SIMULATED,
        "hybrid": ConnectionMode.HYBRID
    }
    mode = mode_map.get(args.mode, ConnectionMode.HYBRID)
    
    # 创建技能实例
    skill = InvestmentTrackerSkill(mode=mode)
    
    if args.command == "help":
        parser.print_help()
        return
    
    print("=" * 60)
    print("InvestmentTracker Skill")
    print(f"模式: {args.mode}")
    print("=" * 60)
    
    if args.command == "all" or args.command == "user":
        user_info = skill.get_user_info()
        print(skill.format_user_info(user_info))
        print()
    
    if args.command == "all" or args.command == "positions":
        positions = skill.list_positions(status=args.status, limit=args.limit)
        print(skill.format_positions(positions))
        print()
    
    if args.command == "all" or args.command == "methodology":
        methodology = skill.get_methodology()
        print(skill.format_methodology(methodology))
        print()
    
    if args.command == "all" or args.command == "stats":
        stats = skill.get_stats()
        print(skill.format_stats(stats))
        print()

if __name__ == "__main__":
    main()