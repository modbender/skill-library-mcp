#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw中文工具包集成模块
提供与OpenClaw工具的直接集成
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chinese_tools import ChineseToolkit

class OpenClawChineseIntegration:
    """OpenClaw中文工具包集成类"""
    
    def __init__(self):
        """初始化"""
        self.toolkit = ChineseToolkit()
        self.cache = {}
        
    def process_command(self, command: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理OpenClaw命令
        
        Args:
            command: 命令名称
            args: 命令参数
            
        Returns:
            处理结果
        """
        try:
            if command == "segment":
                return self._handle_segment(args)
            elif command == "translate":
                return self._handle_translate(args)
            elif command == "ocr":
                return self._handle_ocr(args)
            elif command == "pinyin":
                return self._handle_pinyin(args)
            elif command == "stats":
                return self._handle_stats(args)
            elif command == "summary":
                return self._handle_summary(args)
            elif command == "keywords":
                return self._handle_keywords(args)
            elif command == "convert":
                return self._handle_convert(args)
            else:
                return {
                    "success": False,
                    "error": f"未知命令: {command}",
                    "available_commands": [
                        "segment", "translate", "ocr", "pinyin",
                        "stats", "summary", "keywords", "convert"
                    ]
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command,
                "args": args
            }
    
    def _handle_segment(self, args: Dict) -> Dict:
        """处理分词命令"""
        text = args.get("text", "")
        cut_all = args.get("cut_all", False)
        use_paddle = args.get("use_paddle", False)
        
        segments = self.toolkit.segment(text, cut_all, use_paddle)
        
        return {
            "success": True,
            "command": "segment",
            "text": text,
            "segments": segments,
            "segment_count": len(segments)
        }
    
    def _handle_translate(self, args: Dict) -> Dict:
        """处理翻译命令"""
        text = args.get("text", "")
        from_lang = args.get("from", "zh")
        to_lang = args.get("to", "en")
        engine = args.get("engine", "baidu")
        
        translated = self.toolkit.translate(text, from_lang, to_lang, engine)
        
        return {
            "success": True,
            "command": "translate",
            "original": text,
            "translated": translated,
            "from_lang": from_lang,
            "to_lang": to_lang,
            "engine": engine
        }
    
    def _handle_ocr(self, args: Dict) -> Dict:
        """处理OCR命令"""
        image_path = args.get("image_path", "")
        language = args.get("language", "chi_sim")
        
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"图片文件不存在: {image_path}"
            }
        
        text = self.toolkit.ocr_image(image_path, language)
        
        return {
            "success": True,
            "command": "ocr",
            "image_path": image_path,
            "language": language,
            "text": text,
            "text_length": len(text)
        }
    
    def _handle_pinyin(self, args: Dict) -> Dict:
        """处理拼音命令"""
        text = args.get("text", "")
        style = args.get("style", "normal")
        
        pinyin = self.toolkit.to_pinyin(text, style)
        
        return {
            "success": True,
            "command": "pinyin",
            "text": text,
            "pinyin": pinyin,
            "style": style
        }
    
    def _handle_stats(self, args: Dict) -> Dict:
        """处理统计命令"""
        text = args.get("text", "")
        
        stats = self.toolkit.get_text_statistics(text)
        
        return {
            "success": True,
            "command": "stats",
            "text": text,
            "statistics": stats
        }
    
    def _handle_summary(self, args: Dict) -> Dict:
        """处理摘要命令"""
        text = args.get("text", "")
        max_length = args.get("max_length", 200)
        
        summary = self.toolkit.text_summary(text, max_length)
        
        return {
            "success": True,
            "command": "summary",
            "original_length": len(text),
            "summary_length": len(summary),
            "summary": summary,
            "max_length": max_length
        }
    
    def _handle_keywords(self, args: Dict) -> Dict:
        """处理关键词命令"""
        text = args.get("text", "")
        top_k = args.get("top_k", 10)
        with_weight = args.get("with_weight", False)
        
        keywords = self.toolkit.extract_keywords(text, top_k, with_weight)
        
        return {
            "success": True,
            "command": "keywords",
            "text": text,
            "keywords": keywords,
            "top_k": top_k,
            "with_weight": with_weight
        }
    
    def _handle_convert(self, args: Dict) -> Dict:
        """处理转换命令"""
        text = args.get("text", "")
        direction = args.get("direction", "s2t")  # s2t: 简转繁, t2s: 繁转简
        
        converted = self.toolkit.convert_traditional(text, direction)
        
        return {
            "success": True,
            "command": "convert",
            "original": text,
            "converted": converted,
            "direction": direction
        }
    
    def batch_process(self, commands: List[Dict]) -> List[Dict]:
        """
        批量处理命令
        
        Args:
            commands: 命令列表，每个元素包含command和args
            
        Returns:
            处理结果列表
        """
        results = []
        for cmd in commands:
            result = self.process_command(cmd["command"], cmd.get("args", {}))
            results.append(result)
        return results


# ========== 命令行接口 ==========

def main():
    """命令行入口点"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OpenClaw中文工具包集成接口')
    parser.add_argument('--command', '-c', required=True, help='命令名称')
    parser.add_argument('--args', '-a', type=json.loads, default='{}', help='JSON格式的参数')
    parser.add_argument('--output', '-o', choices=['json', 'text'], default='json', help='输出格式')
    
    args = parser.parse_args()
    
    # 初始化集成
    integration = OpenClawChineseIntegration()
    
    # 处理命令
    result = integration.process_command(args.command, args.args)
    
    # 输出结果
    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 文本格式输出
        if result.get("success"):
            print(f"✅ 命令执行成功: {args.command}")
            for key, value in result.items():
                if key not in ["success", "command"]:
                    if isinstance(value, (list, dict)):
                        print(f"  {key}: {json.dumps(value, ensure_ascii=False)}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print(f"❌ 命令执行失败: {args.command}")
            print(f"   错误: {result.get('error', '未知错误')}")


# ========== OpenClaw工具直接调用示例 ==========

def openclaw_tool_example():
    """OpenClaw工具调用示例"""
    integration = OpenClawChineseIntegration()
    
    # 示例1: 分词
    print("示例1: 中文分词")
    result = integration.process_command("segment", {
        "text": "今天天气真好，我们一起去公园散步吧。",
        "cut_all": False
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    
    # 示例2: 翻译
    print("示例2: 中英翻译")
    result = integration.process_command("translate", {
        "text": "你好，世界",
        "from": "zh",
        "to": "en",
        "engine": "google"
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print()
    
    # 示例3: 文本统计
    print("示例3: 文本统计")
    result = integration.process_command("stats", {
        "text": "OpenClaw中文工具包提供了丰富的中文处理功能。"
    })
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    return integration


if __name__ == '__main__':
    # 如果直接运行，显示示例
    if len(sys.argv) == 1:
        print("🎯 OpenClaw中文工具包集成接口")
        print("=" * 50)
        print("使用方法:")
        print("  python openclaw_integration.py --command <命令> --args '{\"参数\": \"值\"}'")
        print()
        print("可用命令:")
        print("  segment    - 中文分词")
        print("  translate  - 文本翻译")
        print("  ocr        - OCR识别")
        print("  pinyin     - 拼音转换")
        print("  stats      - 文本统计")
        print("  summary    - 文本摘要")
        print("  keywords   - 关键词提取")
        print("  convert    - 简繁转换")
        print()
        print("示例:")
        print('  python openclaw_integration.py --command segment --args \'{"text": "今天天气真好"}\'')
        print()
        print("运行示例:")
        openclaw_tool_example()
    else:
        main()