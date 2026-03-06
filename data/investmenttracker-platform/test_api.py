#!/usr/bin/env python3
"""
测试 InvestmentTracker MCP API 连接
"""

import json
import requests
import sys

def test_api_connection():
    """测试API连接和JSON响应"""
    url = "https://investmenttracker-ingest-production.up.railway.app/mcp"
    headers = {
        "Authorization": "Bearer it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes",
        "Content-Type": "application/json"
    }
    
    print("测试 InvestmentTracker MCP API 连接...")
    print(f"URL: {url}")
    
    try:
        # 首先测试根端点
        print("\n1. 测试根端点...")
        response = requests.get(url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应大小: {len(response.text)} 字符")
        
        # 尝试解析JSON
        try:
            data = response.json()
            print("✓ JSON解析成功")
            print(f"响应结构: {type(data)}")
            if isinstance(data, dict):
                print(f"键: {list(data.keys())}")
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {e}")
            print(f"响应前100字符: {response.text[:100]}")
            print(f"响应后100字符: {response.text[-100:]}")
            
            # 检查可能的格式问题
            if '"' in response.text:
                quote_count = response.text.count('"')
                print(f"引号数量: {quote_count} (应该是偶数)")
            
            # 检查换行符
            newline_count = response.text.count('\n')
            print(f"换行符数量: {newline_count}")
        
        # 测试特定端点
        print("\n2. 测试投资组合端点...")
        portfolio_url = f"{url}/portfolio"
        response = requests.get(portfolio_url, headers=headers, timeout=30)
        print(f"状态码: {response.status_code}")
        print(f"响应大小: {len(response.text)} 字符")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ 投资组合JSON解析成功")
                
                # 检查响应结构
                if isinstance(data, dict):
                    print(f"状态: {data.get('status', 'N/A')}")
                    if 'data' in data:
                        data_part = data['data']
                        if isinstance(data_part, dict):
                            print(f"总价值: ${data_part.get('total_value', 0):,.2f}")
                            assets = data_part.get('assets', [])
                            print(f"资产数量: {len(assets)}")
            except json.JSONDecodeError as e:
                print(f"✗ 投资组合JSON解析失败: {e}")
                print(f"错误位置: 第{e.lineno}行, 第{e.colno}列")
                print(f"错误片段: {response.text[max(0, e.pos-50):e.pos+50]}")
        
        # 测试交易记录端点
        print("\n3. 测试交易记录端点...")
        transactions_url = f"{url}/transactions/recent"
        response = requests.get(transactions_url, headers=headers, timeout=30, params={"limit": 5})
        print(f"状态码: {response.status_code}")
        print(f"响应大小: {len(response.text)} 字符")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("✓ 交易记录JSON解析成功")
            except json.JSONDecodeError as e:
                print(f"✗ 交易记录JSON解析失败: {e}")
        
        print("\n4. 检查常见问题...")
        # 检查响应编码
        print(f"响应编码: {response.encoding}")
        
        # 检查内容类型
        content_type = response.headers.get('content-type', '')
        print(f"内容类型: {content_type}")
        
        if 'application/json' not in content_type:
            print("⚠️ 警告: 响应内容类型不是JSON")
        
        # 检查响应头
        print("\n响应头信息:")
        for key, value in response.headers.items():
            if key.lower() in ['content-length', 'content-type', 'server', 'date']:
                print(f"  {key}: {value}")
        
    except requests.exceptions.RequestException as e:
        print(f"✗ 请求失败: {e}")
        return False
    
    return True

def check_json_syntax(json_string):
    """检查JSON语法"""
    print("\n检查JSON语法...")
    
    # 检查基本语法
    if not json_string.strip():
        print("✗ JSON字符串为空")
        return False
    
    # 检查括号平衡
    open_braces = json_string.count('{')
    close_braces = json_string.count('}')
    open_brackets = json_string.count('[')
    close_brackets = json_string.count(']')
    
    print(f"大括号: {open_braces} 开, {close_braces} 闭")
    print(f"方括号: {open_brackets} 开, {close_brackets} 闭")
    
    if open_braces != close_braces:
        print(f"⚠️ 大括号不平衡: 差 {abs(open_braces - close_braces)}")
    
    if open_brackets != close_brackets:
        print(f"⚠️ 方括号不平衡: 差 {abs(open_brackets - close_brackets)}")
    
    # 检查引号
    double_quotes = json_string.count('"')
    single_quotes = json_string.count("'")
    
    print(f"双引号: {double_quotes}")
    print(f"单引号: {single_quotes}")
    
    if double_quotes % 2 != 0:
        print("⚠️ 双引号数量不是偶数")
    
    # 尝试解析
    try:
        data = json.loads(json_string)
        print("✓ JSON语法正确")
        return True
    except json.JSONDecodeError as e:
        print(f"✗ JSON语法错误: {e}")
        print(f"错误位置: {e.pos} (第{e.lineno}行, 第{e.colno}列)")
        
        # 显示错误附近的上下文
        start = max(0, e.pos - 50)
        end = min(len(json_string), e.pos + 50)
        print(f"错误上下文: ...{json_string[start:end]}...")
        
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("InvestmentTracker MCP API 测试工具")
    print("=" * 60)
    
    success = test_api_connection()
    
    if not success:
        print("\n⚠️ API连接测试失败")
        print("\n建议的解决方案:")
        print("1. 检查网络连接")
        print("2. 验证API密钥是否正确")
        print("3. 检查API端点是否可用")
        print("4. 查看API文档了解正确的使用方式")
        print("5. 联系API提供商获取支持")
    
    # 如果有命令行参数，检查特定的JSON字符串
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_content = f.read()
            check_json_syntax(json_content)
        except FileNotFoundError:
            print(f"文件未找到: {json_file}")
        except Exception as e:
            print(f"读取文件失败: {e}")