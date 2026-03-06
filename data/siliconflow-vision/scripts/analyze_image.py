#!/usr/bin/env python3
"""
图片识别与分析脚本
支持多服务商：SiliconFlow、OpenAI、Anthropic
智能渐进方案：默认快速模型，必要时切换
"""
import sys

# 强制 UTF-8 编码输出（解决 Windows gbk 问题）
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

import argparse
import base64
import json
import os
import sys
from pathlib import Path

# 使用 requests 库（更稳定的 HTTP 客户端）
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import warnings
    warnings.warn("requests 库未安装，将使用 urllib，但可能存在 SSL 兼容性问题")

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# 支持的服务商配置
PROVIDERS = {
    "siliconflow": {
        "name": "SiliconFlow",
        "api_base": "https://api.siliconflow.cn/v1",
        "api_key_name": "SILICONFLOW_API_KEY",
        "models": {
            "fast": "deepseek-ai/deepseek-vl2",
            "smart": "Qwen/Qwen2.5-VL-72B-Instruct",
            "balanced": "deepseek-ai/deepseek-vl2-turbo",
        },
        "default_model": "fast",
    },
    "openai": {
        "name": "OpenAI",
        "api_base": "https://api.openai.com/v1",
        "api_key_name": "OPENAI_API_KEY",
        "models": {
            "fast": "gpt-4o",
            "smart": "gpt-4o",
            "balanced": "gpt-4o",
        },
        "default_model": "fast",
    },
    "anthropic": {
        "name": "Anthropic",
        "api_base": None,  # Claude API 格式不同
        "api_key_name": "ANTHROPIC_API_KEY",
        "models": {
            "fast": "claude-sonnet-4-20250514",
            "smart": "claude-opus-4-20250514",
            "balanced": "claude-sonnet-4-20250514",
        },
        "default_model": "fast",
    },
}

DEFAULT_MODEL = "fast"

# 默认提示词 - 优化版（来自 siliconflow-vision）
DEFAULT_PROMPT = """请仔细识别这张图片，输出以下内容：

【图片类型】
截图/照片/表情包/聊天记录/海报/漫画/其他

【清晰文字】
提取图片中所有能看清的文字，逐字完整复制，不要改写，不要遗漏

【画面元素】
列出图片中包含的人物、物品、图标、头像、装饰等（简单列出即可）

【整体布局】
图片的结构分布，例如：上下结构、左右结构、多栏布局等

【风格】
简约/搞笑/暗黑/可爱/正式/复古/潮流/其他（简述即可）

【其他】
任何值得注意的视觉元素或细节

**重要原则**：
- 只做客观识别，不做分析解读
- 只做简单描述，不过度思考
- 文字必须完整准确
- 让主模型负责思考分析"""

SHORT_PROMPT = """简要分析这张图片：
- 类型：
- 主体：
- 主要文字：
- 核心信息："""


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "config" / "default.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_api_config(provider=None):
    """获取 API 配置"""
    config = load_config()
    
    # 优先使用指定的服务商，其次使用配置文件
    use_provider = provider or config.get("provider", "siliconflow")
    
    if use_provider not in PROVIDERS:
        return None, None, None, None
    
    provider_config = PROVIDERS[use_provider]
    
    # 优先从配置文件读取，其次从环境变量
    api_key = config.get("api_key") or os.environ.get(provider_config["api_key_name"])
    model = config.get("model", provider_config["default_model"])
    api_base = config.get("api_base", provider_config["api_base"])
    
    return use_provider, provider_config["name"], api_key, model, api_base


def encode_image(image_path: str) -> str:
    """将图片编码为 Base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def compress_image(image_path: str, max_size: int = 1024) -> str:
    """压缩图片（可选）"""
    try:
        from PIL import Image
        import io

        img = Image.open(image_path)
        img.thumbnail((max_size, max_size))
        
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except ImportError:
        return encode_image(image_path)


def analyze_with_siliconflow(api_key: str, image_path: str, question: str, model: str) -> str:
    """使用 SiliconFlow API 分析图片"""
    # 获取图片数据
    if image_path.startswith(("http://", "https://")):
        image_url = image_path
        image_data = None
    else:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        image_data = encode_image(image_path)
        image_url = None

    # 构建图片内容
    if image_url:
        image_content = {"type": "image_url", "image_url": {"url": image_url}}
    else:
        mime_type = f"image/{Path(image_path).suffix[1:]}" if Path(image_path).suffix else "image/jpeg"
        image_content = {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}

    # 构建消息
    messages = [
        {
            "role": "user",
            "content": [image_content, {"type": "text", "text": question}]
        }
    ]

    # 发送请求 - 优先使用 requests（更稳定）
    url = "https://api.siliconflow.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.7
    }

    # 优先使用 requests 库
    if HAS_REQUESTS:
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=180)
            if resp.status_code == 200:
                result = resp.json()
                return result["choices"][0]["message"]["content"]
            else:
                return f"错误: HTTP {resp.status_code} - {resp.text[:200]}"
        except Exception as e:
            return f"错误: {e}"
    
    # 回退到 urllib
    print("[WARN] 回退到 urllib 库...", file=sys.stderr)
    req = Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    
    try:
        with urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except (URLError, HTTPError) as e:
        return f"错误: {e}"


def analyze_with_openai(api_key: str, image_path: str, question: str, model: str) -> str:
    """使用 OpenAI API 分析图片"""
    # 获取图片数据
    if image_path.startswith(("http://", "https://")):
        image_url = image_path
    else:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"图片文件不存在: {image_path}")
        image_url = f"data:image/jpeg;base64,{encode_image(image_path)}"

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]
        }
    ]

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.7
    }

    req = Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    
    try:
        with urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except (URLError, HTTPError) as e:
        return f"错误: {e}"


def analyze_image(
    image_path: str,
    question: str = None,
    model: str = None,
    provider: str = None,
    short: bool = False,
) -> str:
    """分析图片的主函数"""
    # 获取配置
    provider_name, provider_full_name, api_key, model_name, api_base = get_api_config(provider)
    
    if not api_key:
        return "错误: 未找到 API Key，请检查配置文件或环境变量"
    
    # 确定提示词
    prompt = SHORT_PROMPT if short else (question or DEFAULT_PROMPT)
    
    # 确定模型
    actual_model = PROVIDERS[provider_name]["models"].get(model or model_name, model or model_name)
    
    # 打印信息
    print(f"[INFO] 服务商: {provider_full_name}", file=sys.stderr)
    print(f"[INFO] 模型: {actual_model}", file=sys.stderr)
    print(f"[INFO] 图片: {image_path}", file=sys.stderr)
    
    # 调用对应服务商
    if provider_name == "siliconflow":
        return analyze_with_siliconflow(api_key, image_path, prompt, actual_model)
    elif provider_name == "openai":
        return analyze_with_openai(api_key, image_path, prompt, actual_model)
    else:
        return f"错误: 不支持的服务商 {provider_name}，目前支持 siliconflow 和 openai"


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="图片识别与分析 - 多服务商支持")
    parser.add_argument("image", help="图片路径或 URL")
    parser.add_argument("-q", "--question", default=None, help="自定义问题")
    parser.add_argument("-m", "--model", default=None, 
                       help="模型选择: fast(快速), smart(聪明), balanced(平衡)")
    parser.add_argument("-s", "--short", action="store_true", help="简短模式")
    parser.add_argument("-p", "--provider", choices=["siliconflow", "openai", "anthropic"],
                       help="指定服务商")
    parser.add_argument("-c", "--compress", action="store_true", help="压缩图片")
    
    args = parser.parse_args()
    
    result = analyze_image(
        image_path=args.image,
        question=args.question,
        model=args.model,
        provider=args.provider,
        short=args.short,
    )
    
    print(result)


if __name__ == "__main__":
    main()
