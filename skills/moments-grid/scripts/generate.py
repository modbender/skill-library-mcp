#!/usr/bin/env python3
"""
朋友圈4宫格卡片生成 Skill
输入主题，自动生成文案+4张卡片图片
"""
import argparse
import os
import subprocess
import tempfile
import json
import requests

from pathlib import Path

# 技能根目录
SKILL_DIR = Path(__file__).parent

# MiniMax API 配置
MINIMAX_API_KEY = "sk-cp-qF0H7zzHFfGnFUYEu_UC9q77Gt51T16M698NWthaRh4KumX_ZzIyR3vOP8D2Hg-c1mMj_DGkMfXfZfBOM_eRYWwZC7VCGqJObJYihEDw7poGgZAftQeVCUQ"
MINIMAX_BASE_URL = "https://api.minimaxi.com/anthropic/v1"

def generate_copy_and_prompts(topic: str) -> dict:
    """调用 MiniMax API 生成文案和图片内容"""
    import httpx
    
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = """你是一个朋友圈文案高手。根据用户给定的主题，生成：
1. 一段朋友圈文案（带 emoji 符号，分类列举风格，每行都要换行）
2. 4个卡片内容（每个卡片包含标题和3个要点）

参考格式：
💪 {主题}：
▪️ 新陈代谢变慢
▪️ 更要注重饮食
▪️ 控制热量摄入

❌ 饮食误区：
▪️ 暴饮暴食
▪️ 高油高盐外卖
▪️ 奶茶饮料不断

✅ 健康习惯：
▪️ 早餐要吃好
▪️ 晚餐七分饱
▪️ 戒掉宵夜

💚 坚持就是胜利：
▪️ 控制饮食
▪️ 保持身材
▪️ 健康是美

#中年健康 #健康饮食 #保持身材

输出格式化为 JSON：
{
  "copy": "朋友圈文案（每行用\\n换行）",
  "cards": [
    {"title": "卡片标题1", "points": ["要点1", "要点2", "要点3"]},
    {"title": "卡片标题2", "points": ["要点1", "要点2", "要点3"]},
    {"title": "卡片标题3", "points": ["要点1", "要点2", "要点3"]},
    {"title": "卡片标题4", "points": ["要点1", "要点2", "要点3"]}
  ]
}

要求：
- 文案用 emoji + 分类列举格式
- 每个分类之间用空行分隔
- 每个分类3个要点，用 ▪️ 符号
- 最后带话题标签"""

    payload = {
        "model": "MiniMax-M2.5",
        "max_tokens": 1000,
        "system": system_prompt,
        "messages": [
            {"role": "user", "content": f"主题：{topic}"}
        ]
    }
    
    response = requests.post(
        f"{MINIMAX_BASE_URL}/messages",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        raise Exception(f"API error: {response.status_code}")
    
    result = response.json()
    
    # 找到 text 类型的 content
    content = ""
    for item in result.get("content", []):
        if item.get("type") == "text":
            text = item.get("text", "")
            # 提取 JSON 部分（可能包含在 ```json ... ``` 中）
            import re
            # 先找 ```json ... ``` 块
            match = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                content = match.group(1)
                break
            # 再试直接找 JSON 对象
            match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
            if match:
                content = match.group()
                break
    
    if not content:
        raise Exception("No JSON content found in response")
    
    # 清理 content
    content = content.replace('\\n', '\n')
    # 移除无效的控制字符
    import re
    content = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', content)
    
    return json.loads(content)
    
    # 解析 JSON
    return json.loads(content)

def generate_card_image(content: str, output_path: str, bg_color: str = "#667eea", topic: str = ""):
    """使用 playwright 生成卡片图片"""
    from playwright.sync_api import sync_playwright
    
    # 将 \n 转换为真正的换行
    content = content.replace('\\n', '\n')
    lines = content.strip().split('\n')
    header = lines[0] if lines else ""
    body_lines = lines[1:] if len(lines) > 1 else []
    
    # 处理换行
    body_html = ''
    for line in body_lines:
        if line.strip():
            body_html += f'<div><span class="bullet">✓</span> {line}</div>'
    
    topic_text = topic if topic else "#话题"
    
    # 提取序号
    import re
    num_match = re.match(r'^(\d+)[.、\s]', header)
    num = num_match.group(1) if num_match else ""
    header_clean = re.sub(r'^(\d+)[.、\s]', '', header)
    
    # 标题图标
    icons = {"1": "🔧", "2": "📦", "3": "✨", "4": "✅"}
    title_icon = icons.get(num, "📌")
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: 600px;
            height: 600px;
            background: linear-gradient(135deg, {bg_color} 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Segoe UI', Roboto, sans-serif;
        }}
        .card {{
            width: 540px;
            height: 540px;
            background: white;
            border-radius: 16px;
            padding: 32px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            border: 3px solid white;
            display: flex;
            flex-direction: column;
            position: relative;
        }}
        .title-section {{
            text-align: center;
            padding-bottom: 20px;
            margin-bottom: 20px;
            border-bottom: 2px dashed #e0e0e0;
            position: relative;
        }}
        .title-section::after {{
            content: '';
            position: absolute;
            bottom: -6px;
            left: 50%;
            transform: translateX(-50%);
            width: 30px;
            height: 12px;
            background: white;
            border-left: 2px solid {bg_color};
            border-right: 2px solid {bg_color};
        }}
        .title-icon {{
            font-size: 44px;
            display: block;
            margin-bottom: 12px;
        }}
        .card-header {{
            font-size: 26px;
            font-weight: 600;
            color: #1a1a1a;
            line-height: 1.4;
        }}
        .card-body {{
            flex: 1;
            font-size: 19px;
            color: #4a4a4a;
            line-height: 2.6;
            padding-top: 8px;
        }}
        .card-body div {{
            margin-bottom: 18px;
            display: flex;
            align-items: flex-start;
        }}
        .bullet {{
            background: {bg_color};
            color: white;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            display: inline-flex;
            justify-content: center;
            align-items: center;
            font-size: 12px;
            margin-right: 10px;
            flex-shrink: 0;
            margin-top: 3px;
        }}
        .card-footer {{
            margin-top: auto;
            padding-top: 16px;
            border-top: 3px solid #f0f0f0;
            text-align: center;
        }}
        .topic-tags {{
            display: flex;
            gap: 8px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .topic-tag {{
            background: {bg_color};
            color: white;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 500;
        }}
    </style>
</head>
<body>
    <div class="card">
        <div class="title-section">
            <span class="title-icon">{title_icon}</span>
            <div class="card-header">{header_clean}</div>
        </div>
        <div class="card-body">{body_html}</div>
        <div class="card-footer">
            <div class="topic-tags">{topic_text}</div>
        </div>
    </div>
</body>
</html>"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 600, 'height': 600})
        page.set_content(html_template)
        page.screenshot(path=output_path, full_page=True)
        browser.close()

def main():
    parser = argparse.ArgumentParser(description="朋友圈4宫格卡片生成")
    parser.add_argument("--topic", required=True, help="主题方向")
    parser.add_argument("--bg", default="#4CAF50", help="背景色")
    args = parser.parse_args()
    
    output_dir = tempfile.mkdtemp(prefix="moments_grid_")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"📱 主题: {args.topic}")
    print("📝 生成文案和卡片内容...")
    
    # 生成文案和内容
    result = generate_copy_and_prompts(args.topic)
    
    copy = result["copy"]
    
    # 处理文案换行：优化排版
    import re
    # 每个要点符号后加换行
    copy = copy.replace('▪️', '\n▪️')
    # 清理多余的换行
    copy = re.sub(r'\n+', '\n', copy)
    # 在话题前加空行
    copy = re.sub(r'(#\w+)', r'\n\n\1', copy)
    # 清理多余空行
    copy = re.sub(r'\n{3,}', '\n\n', copy)
    
    # 随机颜色
    import random
    all_colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0", "#E91E63", "#00BCD4", "#FF5722", "#607D8B"]
    colors = random.sample(all_colors, 4)
    
    cards = result["cards"]
    
    # 提取话题标签
    import re
    topics = re.findall(r'#(\w+)', copy)
    # 多个标签分行显示
    if topics:
        topic_text = " ".join([f"<span class='topic-tag'>#{t}</span>" for t in topics[:3]])
    else:
        topic_text = f"<span class='topic-tag'>#{topic}</span>"
    
    print(f"\n{'='*50}")
    print("📝 朋友圈文案：")
    print(f"{'='*50}")
    print(copy)
    print(f"\n{'='*50}")
    
    # 生成4张卡片（不同颜色）
    for i, card in enumerate(cards):
        title = card["title"]
        points = card["points"]
        content = f"{title}\n" + "\n".join(points)
        
        output_path = os.path.join(output_dir, f"card_{i+1}.png")
        generate_card_image(content, output_path, colors[i], topic_text)
        print(f"✅ 第 {i+1} 张卡片完成")
    
    # 保存文案
    with open(os.path.join(output_dir, "copy.txt"), "w", encoding="utf-8") as f:
        f.write(copy)
    
    print(f"\n🎉 完成！")

if __name__ == "__main__":
    main()
