#!/usr/bin/env python3
"""
MiniMax MCP Search Skill - 使用 mcporter 调用 MiniMax MCP
"""

import os
import sys
import json
import argparse
import subprocess

def run_mcporter(command):
    """执行 mcporter 命令"""
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=60
    )
    return result.stdout, result.stderr, result.returncode

def web_search(query):
    """网络搜索"""
    if not query:
        return {"error": "请提供搜索关键词"}
    
    cmd = f'mcporter call minimax.web_search query:"{query}"'
    stdout, stderr, code = run_mcporter(cmd)
    
    if code != 0:
        return {"error": f"搜索失败: {stderr}"}
    
    try:
        # 解析 JSON 结果
        result = json.loads(stdout)
        
        # 格式化输出
        output = {"results": [], "status": "success"}
        
        if "organic" in result:
            for item in result["organic"][:10]:
                output["results"].append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")[:200],
                    "date": item.get("date", "")
                })
        
        return output
    except:
        return {"raw": stdout, "status": "success"}

def understand_image(image_path, prompt="请描述这张图片的内容"):
    """图像理解"""
    if not image_path:
        return {"error": "请提供图片路径"}
    
    # 处理本地路径
    image_source = image_path
    if not image_path.startswith("http"):
        # 转换为绝对路径
        abs_path = os.path.abspath(os.path.expanduser(image_path))
        image_source = abs_path
    
    cmd = f'mcporter call minimax.understand_image prompt:"{prompt}" image_source:"{image_source}"'
    stdout, stderr, code = run_mcporter(cmd)
    
    if code != 0:
        return {"error": f"图片分析失败: {stderr}"}
    
    return {"description": stdout.strip(), "status": "success", "image": image_source}

def main():
    parser = argparse.ArgumentParser(description="MiniMax MCP Search Skill")
    parser.add_argument("--tool", choices=["web_search", "understand_image"], required=True)
    parser.add_argument("--query", help="搜索关键词")
    parser.add_argument("--prompt", help="图片分析要求")
    parser.add_argument("--image", help="图片路径或URL")
    
    args = parser.parse_args()
    
    if args.tool == "web_search":
        if not args.query:
            print(json.dumps({"error": "请提供搜索关键词 --query"}, ensure_ascii=False))
            sys.exit(1)
        result = web_search(args.query)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.tool == "understand_image":
        if not args.image:
            print(json.dumps({"error": "请提供图片路径 --image"}, ensure_ascii=False))
            sys.exit(1)
        result = understand_image(args.image, args.prompt or "请描述这张图片的内容")
        print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
