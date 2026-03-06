#!/usr/bin/env python3
"""
Grok Twitter Search - 优化版
1. 精简 prompt 减少 input tokens
2. 正确的 xAI Responses API 格式
3. 调用后报告 token 消耗
"""

import os
import sys
import json
import argparse
import httpx

# 全局复用 HTTP 客户端
_http_client = None

def get_client(proxy: str = None) -> httpx.Client:
    """获取或初始化全局 HTTP Client"""
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(proxy=proxy, timeout=httpx.Timeout(15.0, read=60.0))
    return _http_client

def format_tweet(tweet: dict) -> dict:
    """提取并格式化推文原生数据"""
    try:
        author = tweet.get("author", {})
        return {
            "author": f"@{author.get('handle', 'unknown').lstrip('@')}",
            "content": tweet.get("content", ""),
            "timestamp": tweet.get("timestamp", ""),
            "likes": tweet.get("engagement", {}).get("likes", 0),
            "retweets": tweet.get("engagement", {}).get("reposts", 0),
            "url": f"https://x.com/i/status/{tweet.get('id')}"
        }
    except (KeyError, TypeError, ValueError) as e:
        print(f"[Warn] 格式化单条推文数据异常: {e}", file=sys.stderr)
        return {}

def search_twitter(
    query: str, 
    api_key: str, 
    api_base: str = "https://api.x.ai/v1", 
    max_results: int = 10,
    proxy: str = None,
    analyze: bool = False
) -> dict:
    """调用 xAI API，使用原生工具返回机制"""
    
    url = f"{api_base.rstrip('/')}/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 模型选择：只有 reasoning 模型支持 x_search 工具
    model = "grok-4-1-fast-reasoning"
    
    # 精简的 payload，减少 input tokens
    # 关键：不要加 system message，直接让模型调用工具
    payload = {
        "model": model,
        "input": f"Search Twitter for: {query}. Return up to {max_results} tweets.",
        "tools": [{"type": "x_search"}],
        "temperature": 0.0  # 降低随机性，更确定性的输出
    }

    try:
        client = get_client(proxy)
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # 初始化结果
        result = {
            "status": "success",
            "query": query,
            "tweets": [],
            "model_used": model,
            "usage": {},
            "cost_report": ""
        }
        
        # 提取 usage 信息
        usage = data.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0) or (input_tokens + output_tokens)
        x_search_calls = usage.get("x_search_calls", 0)
        
        result["usage"] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "x_search_calls": x_search_calls
        }
        
        # 生成成本报告
        # 根据 xAI 定价：$0.20/百万 input tokens, $0.50/百万 output tokens
        input_cost = (input_tokens / 1_000_000) * 0.20
        output_cost = (output_tokens / 1_000_000) * 0.50
        total_cost = input_cost + output_cost
        
        result["cost_report"] = (
            f"📊 Token 消耗报告:\n"
            f"   Input tokens:  {input_tokens:,}\n"
            f"   Output tokens: {output_tokens:,}\n"
            f"   Total tokens:  {total_tokens:,}\n"
            f"   X Search calls: {x_search_calls}\n"
            f"   💰 预估成本: ${total_cost:.4f} (${total_cost*1000:.2f}/千次)"
        )
        
        # 解析推文数据
        tweets = []
        output_list = data.get("output", [])
        
        for item in output_list:
            if isinstance(item, dict):
                # 策略 1: 直接包含 author 和 id 的工具返回
                if item.get("author") and item.get("id"):
                    tweet_data = format_tweet(item)
                    if tweet_data:
                        tweets.append(tweet_data)
                
                # 策略 2: 从 message content 中解析
                elif item.get("type") == "message":
                    content_list = item.get("content", [])
                    for c in content_list:
                        if c.get("type") == "output_text":
                            text = c.get("text", "")
                            # 尝试找到 JSON 数组
                            try:
                                # 查找方括号包裹的内容
                                start = text.find("[")
                                end = text.rfind("]")
                                if start != -1 and end != -1:
                                    parsed = json.loads(text[start:end+1])
                                    if isinstance(parsed, list):
                                        for t in parsed:
                                            if isinstance(t, dict):
                                                tweet_data = format_tweet(t)
                                                if tweet_data:
                                                    tweets.append(tweet_data)
                            except json.JSONDecodeError:
                                pass
        
        result["tweets"] = tweets[:max_results]
        
        # 打印 token 消耗报告到 stderr（OpenClaw 可以看到）
        print(result["cost_report"], file=sys.stderr)
        
        return result

    except httpx.HTTPStatusError as e:
        error_msg = f"API 错误: {e.response.status_code} - {e.response.text[:200]}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {"status": "error", "message": error_msg}
    except httpx.RequestError as e:
        error_msg = f"网络/代理错误: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"未知错误: {e}"
        print(f"❌ {error_msg}", file=sys.stderr)
        return {"status": "error", "message": error_msg}

def run_interactive_mode(api_key: str, default_proxy: str):
    """纯数字菜单交互模式"""
    while True:
        print("\n" + "="*40)
        print("  🐦 Grok Twitter 搜索")
        print("="*40)
        print(f"当前代理: {default_proxy or '直连'}")
        print("1. 极速检索")
        print("2. 深度分析")
        print("0. 退出")
        print("="*40)
        
        try:
            choice = input("请选择: ").strip()
            if choice == '0':
                break
            elif choice in ('1', '2'):
                query = input("\n搜索关键词: ").strip()
                if not query:
                    continue
                
                print(f"\n🔍 搜索中...")
                res = search_twitter(
                    query=query, 
                    api_key=api_key, 
                    proxy=default_proxy, 
                    analyze=(choice == '2')
                )
                
                # 打印结果（不含 cost_report，因为已经打印过了）
                output = {k: v for k, v in res.items() if k != "cost_report"}
                print(json.dumps(output, ensure_ascii=False, indent=2))
            else:
                print("[!] 无效输入")
        except KeyboardInterrupt:
            print("\n👋 再见")
            break
        except Exception as e:
            print(f"\n[!] 错误: {e}")

def main():
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="Grok Twitter Search")
        parser.add_argument("--query", required=True, help="搜索查询")
        parser.add_argument("--api-key", help="Grok API Key")
        parser.add_argument("--api-base", default="https://api.x.ai/v1")
        parser.add_argument("--max-results", type=int, default=10)
        parser.add_argument("--proxy", help="SOCKS5 代理")
        parser.add_argument("--analyze", action="store_true", help="启用推理模式")
        
        args = parser.parse_args()
        
        api_key = args.api_key or os.environ.get("GROK_API_KEY")
        if not api_key:
            print(json.dumps({"status": "error", "message": "缺少 API Key"}))
            sys.exit(1)
            
        proxy = args.proxy or os.environ.get("SOCKS5_PROXY")
        
        result = search_twitter(
            args.query, api_key, args.api_base, 
            args.max_results, proxy, args.analyze
        )
        
        # 输出结果（stdout 给 OpenClaw）
        output = {k: v for k, v in result.items() if k != "cost_report"}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        api_key = os.environ.get("GROK_API_KEY")
        if not api_key:
            print("[!] 未设置 GROK_API_KEY")
            sys.exit(1)
        proxy = os.environ.get("SOCKS5_PROXY")
        run_interactive_mode(api_key, proxy)

if __name__ == "__main__":
    main()
