#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token Estimator - Token 消耗预估核心代码
版本：1.0.0
创建时间：2026-02-24
作者：Neo（宇宙神经系统）
"""

import sys
import json
import argparse
from typing import Tuple, Dict, Optional

# 尝试导入 tokenizer 库
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import dashscope
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False


class TokenEstimator:
    """Token 消耗预估器"""
    
    def __init__(self, model_name: str = "dashscope/qwen3.5-plus"):
        self.model_name = model_name
        self.tokenizer = self._get_tokenizer()
    
    def _get_tokenizer(self):
        """自动选择最适合的 Tokenizer"""
        model_lower = self.model_name.lower()
        
        # Qwen/dashscope 系列
        if "qwen" in model_lower or "dashscope" in model_lower:
            if TRANSFORMERS_AVAILABLE:
                try:
                    print(f"🔧 使用 Qwen Tokenizer (transformers)", file=sys.stderr)
                    return AutoTokenizer.from_pretrained("Qwen/Qwen-7B")
                except Exception as e:
                    print(f"⚠️ Qwen Tokenizer 加载失败：{e}", file=sys.stderr)
            return self._fallback_estimator
        
        # OpenAI 系列
        elif "gpt" in model_lower or "openai" in model_lower:
            if TIKTOKEN_AVAILABLE:
                try:
                    encoding = tiktoken.encoding_for_model(model_lower.split('/')[-1])
                    print(f"🔧 使用 OpenAI Tokenizer (tiktoken)", file=sys.stderr)
                    return encoding.encode
                except Exception as e:
                    print(f"⚠️ OpenAI Tokenizer 加载失败：{e}", file=sys.stderr)
            if TIKTOKEN_AVAILABLE:
                return tiktoken.get_encoding("cl100k_base").encode
        
        # Gemini 系列
        elif "gemini" in model_lower:
            if TIKTOKEN_AVAILABLE:
                print(f"🔧 使用 Gemini Tokenizer (tiktoken/cl100k_base)", file=sys.stderr)
                return tiktoken.get_encoding("cl100k_base").encode
        
        # 未知模型：降级到字符估算
        print(f"⚠️ 未知模型 '{self.model_name}'，使用字符估算", file=sys.stderr)
        return self._fallback_estimator
    
    def _fallback_estimator(self, text: str) -> list:
        """字符估算：中文 4 字≈1 token，英文 4 字符≈1 token"""
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_chars = len([c for c in text if c.isascii() and c.isalnum()])
        # 返回虚拟的 token IDs（仅用于计数）
        return list(range((chinese_chars // 4) + (english_chars // 4)))
    
    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量"""
        if callable(self.tokenizer):
            tokens = self.tokenizer(text)
            if isinstance(tokens, list):
                return len(tokens)
            else:
                # transformers tokenizer 返回 dict
                return len(tokens.get('input_ids', []))
        else:
            return 0
    
    def estimate_output_tokens(self, input_length: int, text_type: str = "auto") -> Tuple[int, int]:
        """
        预估输出 token 数量
        
        返回：(min_output, max_output)
        """
        # 根据输入长度和文本类型估算
        if text_type == "auto":
            if input_length < 1000:
                text_type = "short"
            elif input_length < 5000:
                text_type = "medium"
            else:
                text_type = "long"
        
        # 输出 token 估算规则
        output_ranges = {
            "short": (200, 500),      # 短文本
            "medium": (500, 1500),    # 中文本
            "long": (1500, 3000),     # 长文本
            "code": (300, 1000),      # 代码
            "dialogue": (100, 300),   # 对话
        }
        
        min_out, max_out = output_ranges.get(text_type, (500, 1500))
        return (min_out, max_out)
    
    def estimate_compression_savings(self, input_tokens: int) -> Dict:
        """预估 4D 压缩后的节省效果"""
        # 基于 T1-T7 实验数据
        compression_rate = 0.70  # 平均 70% 节省
        
        compressed_tokens = int(input_tokens * (1 - compression_rate))
        saved_tokens = input_tokens - compressed_tokens
        
        # 成本估算（按 dashscope 价格）
        cost_per_1k = 0.002  # $0.002 per 1k tokens（示例价格）
        saved_cost = (saved_tokens / 1000) * cost_per_1k
        
        return {
            "original": input_tokens,
            "compressed": compressed_tokens,
            "saved": saved_tokens,
            "rate": compression_rate * 100,
            "cost_saved_usd": saved_cost,
            "cost_saved_cny": saved_cost * 7.2
        }
    
    def format_usage_meter(self, usage_data: Dict) -> str:
        """格式化 Token 水表显示"""
        used = usage_data.get("used", 0)
        quota = usage_data.get("quota", 18000)
        percentage = (used / quota * 100) if quota > 0 else 0
        
        # 进度条
        bar_length = 20
        filled = int(bar_length * percentage / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        return f"""
💧 Token 水表（{usage_data.get("period", "月度")}）
━━━━━━━━━━━━━━━━━━━━
已用：{bar} {percentage:.1f}%
配额：{used:,} / {quota:,}
剩余：{quota - used:,} tokens"""


def detect_text_type(text: str) -> str:
    """自动检测文本类型"""
    # 检测代码
    if any(kw in text for kw in ["def ", "function", "import ", "class ", "if __name__"]):
        return "code"
    
    # 检测对话
    if text.count("\n") < 3 and len(text) < 500:
        return "dialogue"
    
    # 检测中英混合
    chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    english_chars = len([c for c in text if c.isascii() and c.isalpha()])
    
    if chinese_chars > 0 and english_chars > 0:
        if english_chars / (chinese_chars + english_chars) > 0.3:
            return "mixed"
    
    # 默认按长度分类
    if len(text) < 1000:
        return "short"
    elif len(text) < 5000:
        return "medium"
    else:
        return "long"


def print_estimation(estimator: TokenEstimator, text: str, with_compress: bool = False):
    """打印 Token 预估结果"""
    
    # 计算输入 tokens
    input_tokens = estimator.count_tokens(text)
    
    # 检测文本类型
    text_type = detect_text_type(text)
    
    # 预估输出 tokens
    min_output, max_output = estimator.estimate_output_tokens(input_tokens, text_type)
    
    # 总消耗
    total_min = input_tokens + min_output
    total_max = input_tokens + max_output
    
    # 打印结果
    print("\n┌─────────────────────────────────────────┐")
    print("│  📊 Token 消耗预估                      │")
    print("├─────────────────────────────────────────┤")
    print(f"│  模型：{estimator.model_name:<35}│")
    print("│                                         │")
    print(f"│  原文长度：{len(text):,} 字".ljust(42) + "│")
    print(f"│  文本类型：{text_type}".ljust(42) + "│")
    print(f"│  预计输入：约 {input_tokens:,} tokens".ljust(42) + "│")
    print(f"│  预计输出：约 {min_output:,}–{max_output:,} tokens".ljust(42) + "│")
    print("│  ─────────────────────────────────      │")
    print(f"│  总计消耗：约 {total_min:,}–{total_max:,} tokens".ljust(42) + "│")
    
    # 4D 压缩建议
    if with_compress and input_tokens > 500:
        savings = estimator.estimate_compression_savings(input_tokens)
        compressed_total_min = savings["compressed"] + min_output
        compressed_total_max = savings["compressed"] + max_output
        
        print("│                                         │")
        print("│  💡 启用 4D 压缩后：                     │")
        print(f"│     节省：约 {savings['saved']:,} tokens ({savings['rate']:.0f}%)".ljust(42) + "│")
        print(f"│     实际：约 {compressed_total_min:,}–{compressed_total_max:,} tokens".ljust(42) + "│")
        print(f"│     成本节省：¥{savings['cost_saved_cny']:.3f} CNY".ljust(42) + "│")
    
    print("└─────────────────────────────────────────┘\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Token 消耗预估工具")
    parser.add_argument("text", nargs="?", help="要预估的文本")
    parser.add_argument("--model", "-m", default="dashscope/qwen3.5-plus", 
                       help="模型名称（默认：dashscope/qwen3.5-plus）")
    parser.add_argument("--with-compress", "-c", action="store_true",
                       help="显示 4D 压缩建议")
    parser.add_argument("--usage", "-u", action="store_true",
                       help="显示 Token 水表用量")
    parser.add_argument("--json", "-j", action="store_true",
                       help="输出 JSON 格式")
    
    args = parser.parse_args()
    
    # 如果没有提供文本，从 stdin 读取
    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        parser.print_help()
        sys.exit(1)
    
    # 创建预估器
    estimator = TokenEstimator(args.model)
    
    # 输出结果
    if args.json:
        # JSON 输出（用于程序调用）
        input_tokens = estimator.count_tokens(text)
        text_type = detect_text_type(text)
        min_out, max_out = estimator.estimate_output_tokens(input_tokens, text_type)
        
        result = {
            "model": args.model,
            "input_length": len(text),
            "input_tokens": input_tokens,
            "output_tokens_min": min_out,
            "output_tokens_max": max_out,
            "total_min": input_tokens + min_out,
            "total_max": input_tokens + max_out,
            "text_type": text_type
        }
        
        if args.with_compress and input_tokens > 500:
            result["compression"] = estimator.estimate_compression_savings(input_tokens)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 人类可读输出
        print_estimation(estimator, text, args.with_compress)


if __name__ == "__main__":
    main()
