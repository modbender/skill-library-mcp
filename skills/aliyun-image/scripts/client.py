#!/usr/bin/env python3
"""
阿里云百炼图像生成与编辑 API 客户端

使用方法:
    # 文生图
    python client.py generate "提示词" [--size 1920*1080] [--max]

    # 图像编辑
    python client.py edit "图像URL" "编辑指令" [-n 2] [--size 1536*1024] [--max]

    # 多图融合
    python client.py edit "图1URL,图2URL,图3URL" "编辑指令" [-n 1]

    # 图像翻译
    python client.py translate "图像URL" --source en --target zh [--domain "电商客服"] [--sensitives "敏感词1,敏感词2"]

    # 下载图像
    python client.py download "图像URL" [保存路径]
"""

import argparse
import base64
import os
import sys
import time
from typing import List, Optional

import requests

# API 配置
API_BASE = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
TRANSLATE_API = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis"
TASK_API = "https://dashscope.aliyuncs.com/api/v1/tasks"

# 默认配置
DEFAULT_NEGATIVE_PROMPT = "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节"


class AliyunImageClient:
    """阿里云百炼图像API客户端"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量或传入 api_key 参数")

    def _request(self, payload: dict) -> dict:
        """发送API请求"""
        resp = requests.post(
            API_BASE,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            },
            json=payload,
            timeout=120
        )
        result = resp.json()

        if "code" in result:
            raise Exception(f"[{result['code']}] {result.get('message', 'Unknown error')}")

        return result

    def generate(
        self,
        prompt: str,
        size: str = "1664*928",
        negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
        prompt_extend: bool = True,
        watermark: bool = False,
        use_max: bool = False
    ) -> str:
        """
        文生图

        Args:
            prompt: 正向提示词
            size: 输出分辨率
            negative_prompt: 反向提示词
            prompt_extend: 是否开启提示词智能改写
            watermark: 是否添加水印
            use_max: 是否使用Max模型

        Returns:
            生成图像的URL
        """
        model = "qwen-image-max" if use_max else "qwen-image-plus"

        payload = {
            "model": model,
            "input": {
                "messages": [{
                    "role": "user",
                    "content": [{"text": prompt}]
                }]
            },
            "parameters": {
                "negative_prompt": negative_prompt,
                "prompt_extend": prompt_extend,
                "watermark": watermark,
                "size": size
            }
        }

        result = self._request(payload)
        return result["output"]["choices"][0]["message"]["content"][0]["image"]

    def edit(
        self,
        images: List[str],
        instruction: str,
        n: int = 1,
        size: Optional[str] = None,
        negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
        prompt_extend: bool = True,
        watermark: bool = False,
        use_max: bool = False
    ) -> List[str]:
        """
        图像编辑

        Args:
            images: 图像URL列表（1-3张）
            instruction: 编辑指令
            n: 输出图像数量（1-6）
            size: 输出分辨率
            negative_prompt: 反向提示词
            prompt_extend: 是否开启提示词智能改写
            watermark: 是否添加水印
            use_max: 是否使用Max模型

        Returns:
            生成图像的URL列表
        """
        model = "qwen-image-edit-max" if use_max else "qwen-image-edit-plus"

        # 构建content
        content = []
        for img in images:
            # 支持本地文件
            if os.path.exists(img):
                with open(img, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                content.append({"image": f"data:image/jpeg;base64,{b64}"})
            else:
                content.append({"image": img})

        content.append({"text": instruction})

        payload = {
            "model": model,
            "input": {
                "messages": [{
                    "role": "user",
                    "content": content
                }]
            },
            "parameters": {
                "n": n,
                "negative_prompt": negative_prompt,
                "prompt_extend": prompt_extend,
                "watermark": watermark
            }
        }

        if size:
            payload["parameters"]["size"] = size

        result = self._request(payload)
        return [c["image"] for c in result["output"]["choices"][0]["message"]["content"]]

    @staticmethod
    def download(url: str, save_path: str) -> str:
        """
        下载图像

        Args:
            url: 图像URL
            save_path: 保存路径

        Returns:
            保存的文件路径
        """
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()

        with open(save_path, "wb") as f:
            f.write(resp.content)

        return os.path.abspath(save_path)

    def translate(
        self,
        image_url: str,
        source_lang: str = "auto",
        target_lang: str = "zh",
        domain_hint: Optional[str] = None,
        sensitives: Optional[List[str]] = None,
        terminologies: Optional[List[dict]] = None,
        skip_img_segment: bool = False,
        poll_interval: int = 3
    ) -> str:
        """
        图像翻译

        Args:
            image_url: 输入图像URL
            source_lang: 源语种，默认自动检测
            target_lang: 目标语种，默认中文
            domain_hint: 领域提示（英文）
            sensitives: 敏感词列表
            terminologies: 术语定义列表 [{"src": "源词", "tgt": "目标词"}]
            skip_img_segment: 是否翻译主体文字
            poll_interval: 轮询间隔（秒）

        Returns:
            翻译后图像的URL
        """
        # 构建请求体
        payload = {
            "model": "qwen-mt-image",
            "input": {
                "image_url": image_url,
                "source_lang": source_lang,
                "target_lang": target_lang
            }
        }

        # 添加可选参数
        ext = {}
        if domain_hint:
            ext["domainHint"] = domain_hint
        if sensitives:
            ext["sensitives"] = sensitives
        if terminologies:
            ext["terminologies"] = terminologies
        if skip_img_segment:
            ext["config"] = {"skipImgSegment": True}

        if ext:
            payload["input"]["ext"] = ext

        # 创建任务
        resp = requests.post(
            TRANSLATE_API,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "X-DashScope-Async": "enable"
            },
            json=payload,
            timeout=30
        )
        result = resp.json()

        if "code" in result:
            raise Exception(f"[{result['code']}] {result.get('message', 'Unknown error')}")

        task_id = result["output"]["task_id"]

        # 轮询查询结果
        while True:
            time.sleep(poll_interval)
            resp = requests.get(
                f"{TASK_API}/{task_id}",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            result = resp.json()
            status = result["output"]["task_status"]

            if status == "SUCCEEDED":
                return result["output"]["image_url"]
            elif status == "FAILED":
                raise Exception(f"任务失败: {result['output'].get('message', 'Unknown error')}")
            elif status in ("PENDING", "RUNNING"):
                continue
            else:
                raise Exception(f"未知状态: {status}")


def main():
    parser = argparse.ArgumentParser(description="阿里云百炼图像API客户端")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 文生图命令
    gen_parser = subparsers.add_parser("generate", help="文生图")
    gen_parser.add_argument("prompt", help="提示词")
    gen_parser.add_argument("--size", default="1664*928", help="输出分辨率")
    gen_parser.add_argument("--max", action="store_true", help="使用Max模型")
    gen_parser.add_argument("--no-extend", action="store_true", help="关闭提示词智能改写")

    # 图像编辑命令
    edit_parser = subparsers.add_parser("edit", help="图像编辑")
    edit_parser.add_argument("images", help="图像URL，多个用逗号分隔")
    edit_parser.add_argument("instruction", help="编辑指令")
    edit_parser.add_argument("-n", type=int, default=1, help="输出数量")
    edit_parser.add_argument("--size", help="输出分辨率")
    edit_parser.add_argument("--max", action="store_true", help="使用Max模型")

    # 图像翻译命令
    trans_parser = subparsers.add_parser("translate", help="图像翻译")
    trans_parser.add_argument("image", help="图像URL")
    trans_parser.add_argument("--source", "-s", default="auto", help="源语种（默认auto自动检测）")
    trans_parser.add_argument("--target", "-t", default="zh", help="目标语种（默认zh中文）")
    trans_parser.add_argument("--domain", "-d", help="领域提示（英文描述）")
    trans_parser.add_argument("--sensitives", help="敏感词，多个用逗号分隔")
    trans_parser.add_argument("--terms", help="术语定义，格式：源词1:目标词1,源词2:目标词2")
    trans_parser.add_argument("--skip-segment", action="store_true", help="翻译主体上的文字")

    # 下载命令
    dl_parser = subparsers.add_parser("download", help="下载图像")
    dl_parser.add_argument("url", help="图像URL")
    dl_parser.add_argument("path", nargs="?", default="output.png", help="保存路径")

    args = parser.parse_args()
    client = AliyunImageClient()

    if args.command == "generate":
        print(f"正在生成图像...")
        url = client.generate(
            prompt=args.prompt,
            size=args.size,
            use_max=args.max,
            prompt_extend=not args.no_extend
        )
        print(f"图像URL: {url}")
        print("注意：URL有效期24小时")

    elif args.command == "edit":
        images = [img.strip() for img in args.images.split(",")]
        print(f"正在编辑图像（输入{len(images)}张，输出{args.n}张）...")
        urls = client.edit(
            images=images,
            instruction=args.instruction,
            n=args.n,
            size=args.size,
            use_max=args.max
        )
        for i, url in enumerate(urls):
            print(f"图像 {i+1}: {url}")
        print("注意：URL有效期24小时")

    elif args.command == "translate":
        # 解析敏感词
        sensitives = None
        if args.sensitives:
            sensitives = [s.strip() for s in args.sensitives.split(",")]

        # 解析术语定义
        terminologies = None
        if args.terms:
            terminologies = []
            for term in args.terms.split(","):
                if ":" in term:
                    src, tgt = term.split(":", 1)
                    terminologies.append({"src": src.strip(), "tgt": tgt.strip()})

        print(f"正在翻译图像 ({args.source} -> {args.target})...")
        url = client.translate(
            image_url=args.image,
            source_lang=args.source,
            target_lang=args.target,
            domain_hint=args.domain,
            sensitives=sensitives,
            terminologies=terminologies,
            skip_img_segment=args.skip_segment
        )
        print(f"翻译结果: {url}")
        print("注意：URL有效期24小时")

    elif args.command == "download":
        path = client.download(args.url, args.path)
        print(f"已保存到: {path}")


if __name__ == "__main__":
    main()
