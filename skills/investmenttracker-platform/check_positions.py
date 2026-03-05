#!/usr/bin/env python3
"""
使用真实API密钥检查持仓数据
"""

import json
import os
import sys
import subprocess
import time
from typing import Dict, Any, List, Optional

def send_mcp_request(api_url: str, headers: Dict[str, str], method: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """发送MCP请求"""
    # 构建JSON-RPC请求
    request = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": int(time.time() * 1000)
    }
    
    # 构建curl命令
    header_args = []
    for key, value in headers.items():
        header_args.append(f"-H")
        header_args.append(f"{key}: {value}")
    
    cmd = [
        "curl", "-s", "-N", "-X", "POST",
        api_url,
        *header_args,
        "-d", json.dumps(request)
    ]
    
    print(f"发送请求到: {api_url}")
    print(f"命令: {' '.join(cmd[:10])}...")
    
    try:
        # 执行curl命令
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"请求失败: {result.stderr}")
            return None
        
        # 解析响应
        response = json.loads(result.stdout)
        return response
        
    except subprocess.TimeoutExpired:
        print("请求超时")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"原始响应: {result.stdout[:200] if 'result' in locals() else '无响应'}")
        return None
    except Exception as e:
        print(f"请求异常: {e}")
        return None

def get_positions(api_url: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """获取持仓列表"""
    return send_mcp_request(api_url, headers, "tools/call", {
        "name": "positions_list_v1",
        "arguments": {
            "status": "POSITION",
            "limit": 20
        }
    })

def get_user_info(api_url: str, headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """获取用户信息"""
    return send_mcp_request(api_url, headers, "tools/call", {
        "name": "whoami_v1",
        "arguments": {}
    })

def format_positions(positions_data: Dict[str, Any]) -> str:
    """格式化持仓数据"""
    if not positions_data or "result" not in positions_data:
        return "持仓数据: 获取失败或数据为空"
    
    result = positions_data["result"]
    
    output = []
    output.append("📊 持仓列表 (真实数据)")
    output.append("=" * 60)
    
    if not result or "items" not in result or not result["items"]:
        output.append("暂无持仓")
    else:
        positions = result["items"]
        output.append(f"持仓数量: {len(positions)}")
        output.append("=" * 60)
        
        for i, pos in enumerate(positions, 1):
            output.append(f"{i}. {pos.get('symbol', 'N/A')} - {pos.get('name', 'N/A')}")
            output.append(f"   类型: {pos.get('asset_type', 'N/A')}")
            output.append(f"   数量: {pos.get('quantity', 0):,.4f}")
            output.append(f"   当前价格: ${pos.get('current_price', 0):,.2f}")
            output.append(f"   当前价值: ${pos.get('current_value', 0):,.2f}")
            output.append(f"   成本基础: ${pos.get('cost_basis', 0):,.2f}")
            output.append(f"   未实现收益: ${pos.get('unrealized_gain', 0):,.2f}")
            output.append(f"   状态: {pos.get('status', 'N/A')}")
            if i < len(positions):
                output.append("-" * 40)
    
    return "\n".join(output)

def format_user_info(user_data: Dict[str, Any]) -> str:
    """格式化用户信息"""
    if not user_data or "result" not in user_data:
        return "用户信息: 获取失败"
    
    result = user_data["result"]
    
    output = []
    output.append("👤 用户信息")
    output.append("-" * 40)
    
    if result:
        output.append(f"ID: {result.get('id', 'N/A')}")
        output.append(f"名称: {result.get('name', 'N/A')}")
        output.append(f"邮箱: {result.get('email', 'N/A')}")
        output.append(f"加入日期: {result.get('joined_date', 'N/A')}")
        output.append(f"投资风格: {result.get('investment_style', 'N/A')}")
    else:
        output.append("数据为空")
    
    return "\n".join(output)

def main():
    """主函数"""
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "real_config.json")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"配置文件不存在: {config_path}")
        return
    
    mcp_config = config.get("mcpServers", {}).get("investmenttracker", {})
    api_url = mcp_config.get("url", "")
    headers = mcp_config.get("headers", {})
    
    print("=" * 60)
    print("InvestmentTracker 真实数据查询")
    print(f"API URL: {api_url}")
    print("=" * 60)
    print()
    
    # 获取用户信息
    print("获取用户信息...")
    user_info = get_user_info(api_url, headers)
    if user_info:
        print(format_user_info(user_info))
    else:
        print("用户信息获取失败")
    print()
    
    # 获取持仓数据
    print("获取持仓数据...")
    positions = get_positions(api_url, headers)
    if positions:
        print(format_positions(positions))
        
        # 计算总价值
        if positions.get("result") and positions["result"].get("items"):
            total_value = sum(pos.get("current_value", 0) for pos in positions["result"]["items"])
            total_gain = sum(pos.get("unrealized_gain", 0) for pos in positions["result"]["items"])
            print()
            print("📈 持仓汇总")
            print("-" * 40)
            print(f"持仓总价值: ${total_value:,.2f}")
            print(f"总未实现收益: ${total_gain:,.2f}")
            print(f"持仓数量: {len(positions['result']['items'])}")
    else:
        print("持仓数据获取失败")
    
    print()
    print("=" * 60)
    print("查询完成")

if __name__ == "__main__":
    main()