#!/usr/bin/env python3
"""
内容优化器 - 优化生成的书籍内容质量
"""

import re
import json
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ContentOptimizer:
    """内容优化器"""

    def __init__(self):
        self.citation_formats = {
            "apa": self._format_apa_citation,
            "mla": self._format_mla_citation,
            "chicago": self._format_chicago_citation,
            "harvard": self._format_harvard_citation
        }

    def optimize_content(self, content: str, content_type: str = "chapter") -> str:
        """
        优化内容质量

        Args:
            content: 原始内容
            content_type: 内容类型（chapter, section, paragraph等）

        Returns:
            str: 优化后的内容
        """
        # 1. 语法和风格优化
        content = self._optimize_grammar_and_style(content)
        
        # 2. 格式规范化
        content = self._normalize_formatting(content)
        
        # 3. 引用格式化
        content = self._format_citations(content)
        
        # 4. 公式验证和格式化
        content = self._validate_and_format_equations(content)
        
        # 5. 代码块语法高亮标记
        content = self._add_code_language_tags(content)
        
        return content

    def _optimize_grammar_and_style(self, content: str) -> str:
        """优化语法和风格"""
        # 修正常见的语法错误
        content = re.sub(r'\s+', ' ', content)  # 合并多个空格为单个空格
        content = re.sub(r'(\w)\.(\w)', r'\1. \2', content)  # 确保句号后有空格
        content = re.sub(r'(\w),(\w)', r'\1, \2', content)  # 确保逗号后有空格
        
        # 修正标题格式
        lines = content.split('\n')
        optimized_lines = []
        for line in lines:
            # 检查是否为标题行
            if line.strip().startswith('#'):
                # 确保标题后有空行
                optimized_lines.append(line)
                if len(optimized_lines) > 0 and optimized_lines[-1] != '':
                    optimized_lines.append('')
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)

    def _normalize_formatting(self, content: str) -> str:
        """规范化格式"""
        # 标准化标题层级
        content = re.sub(r'^#{6,}', '##', content, flags=re.MULTILINE)  # 将过多的标题层级降级
        content = re.sub(r'^#{1}', '#', content, flags=re.MULTILINE)  # 保留一级标题
        
        # 确保列表格式一致
        content = re.sub(r'^\s*[*+-]\s+', '- ', content, flags=re.MULTILINE)  # 统一无序列表标记
        
        return content

    def _format_citations(self, content: str) -> str:
        """格式化引用"""
        # 查找引用标记，如 [1], [Smith et al., 2020], [Author, Year] 等
        citation_pattern = r'\[([^]]+)\]'
        
        def replace_citation(match):
            citation_text = match.group(1)
            # 这里可以实现具体的引用格式化逻辑
            # 为简化，暂时返回原文
            return f'[{citation_text}]'
        
        return re.sub(citation_pattern, replace_citation, content)

    def _validate_and_format_equations(self, content: str) -> str:
        """验证和格式化方程式"""
        # 确保LaTeX公式格式正确
        # 匹配 $$...$$ 或 $...$ 形式的公式
        content = re.sub(r'\$\$(.*?)\$\$', r'\n$$\n\1\n$$\n', content, flags=re.DOTALL)
        content = re.sub(r'\$(.*?)\$', r'$\1$', content)
        
        return content

    def _add_code_language_tags(self, content: str) -> str:
        """为代码块添加语言标签"""
        # 简单的代码语言检测和标记
        # 这里使用简单的启发式方法，实际应用中可能需要更复杂的检测逻辑
        lines = content.split('\n')
        optimized_content = []
        in_code_block = False
        code_block_start_idx = -1
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if line.strip() == '```':
                if not in_code_block:
                    # 代码块开始
                    in_code_block = True
                    code_block_start_idx = i
                else:
                    # 代码块结束
                    in_code_block = False
                    
                    # 检查代码块内容并尝试确定语言
                    if code_block_start_idx + 1 < len(lines) and i > code_block_start_idx + 1:
                        # 获取代码块内容
                        code_content = '\n'.join(lines[code_block_start_idx+1:i])
                        
                        # 简单的语言检测
                        lang = self._detect_code_language(code_content)
                        
                        if lang:
                            # 在代码块开始标记后插入语言标识
                            lines[code_block_start_idx] = f'```{lang}'
                    
                    optimized_content.append(lines[i])
                i += 1
                continue
            
            optimized_content.append(line)
            i += 1
        
        return '\n'.join(optimized_content)

    def _detect_code_language(self, code_content: str) -> Optional[str]:
        """检测代码语言"""
        code_content_lower = code_content.lower()
        
        # 检测常见语言的关键字
        language_keywords = {
            'python': ['def ', 'import ', 'class ', 'print(', 'lambda '],
            'javascript': ['function', 'const ', 'let ', 'var ', 'console.log'],
            'java': ['public class', 'private ', 'import ', 'System.out'],
            'cpp': ['#include', 'using namespace', 'cout <<', 'cin >>'],
            'html': ['<html>', '<body>', '<div', '</'],
            'css': ['{', '}', 'margin:', 'padding:'],
            'sql': ['SELECT', 'FROM', 'WHERE', 'INSERT INTO'],
            'bash': ['#!/bin/bash', 'echo ', 'cd ', 'ls ', 'mkdir '],
            'markdown': ['#', '*', '**', '[', '](']
        }
        
        scores = {}
        for lang, keywords in language_keywords.items():
            score = sum(1 for keyword in keywords if keyword.lower() in code_content_lower)
            scores[lang] = score
        
        # 返回得分最高的语言
        if scores:
            best_lang = max(scores, key=scores.get)
            if scores[best_lang] > 0:  # 只有在找到至少一个关键字时才返回语言
                return best_lang
        
        return None

    def _format_apa_citation(self, citation: str) -> str:
        """格式化APA引用"""
        # APA格式示例: (Author, Year)
        return f"({citation})"

    def _format_mla_citation(self, citation: str) -> str:
        """格式化MLA引用"""
        # MLA格式示例: (Author Page)
        return f"({citation})"

    def _format_chicago_citation(self, citation: str) -> str:
        """格式化Chicago引用"""
        # Chicago格式示例: (Author Year)
        return f"({citation})"

    def _format_harvard_citation(self, citation: str) -> str:
        """格式化Harvard引用"""
        # Harvard格式示例: (Author, Year)
        return f"({citation})"

    def add_multimedia_elements(self, content: str, multimedia_data: Dict) -> str:
        """
        添加多媒体元素（公式、图表、表格、代码等）

        Args:
            content: 原始内容
            multimedia_data: 多媒体数据字典

        Returns:
            str: 添加多媒体元素后的内容
        """
        # 添加数学公式
        if 'formulas' in multimedia_data and multimedia_data['formulas']:
            content += "\n\n## 数学公式\n\n"
            for i, formula in enumerate(multimedia_data['formulas']):
                content += f"$$\n{formula}\n$$\n\n"

        # 添加代码示例
        if 'code_snippets' in multimedia_data and multimedia_data['code_snippets']:
            content += "\n\n## 代码示例\n\n"
            for snippet in multimedia_data['code_snippets']:
                lang = snippet.get('language', 'python')
                code = snippet.get('code', '')
                content += f"```{lang}\n{code}\n```\n\n"

        # 添加表格
        if 'tables' in multimedia_data and multimedia_data['tables']:
            content += "\n\n## 表格\n\n"
            for table in multimedia_data['tables']:
                title = table.get('title', '表格')
                content += f"**{title}**\n\n"
                
                # 简单的表格表示
                if 'rows' in table:
                    for row in table['rows']:
                        content += "| " + " | ".join(str(cell) for cell in row) + " |\n"
                    content += "\n"

        # 添加图表描述
        if 'figures' in multimedia_data and multimedia_data['figures']:
            content += "\n\n## 图表\n\n"
            for figure in multimedia_data['figures']:
                caption = figure.get('caption', '图表')
                description = figure.get('description', '')
                content += f"**{caption}**: {description}\n\n"

        return content

    def validate_content_quality(self, content: str) -> Dict[str, any]:
        """
        验证内容质量

        Args:
            content: 待验证的内容

        Returns:
            Dict: 验证结果
        """
        result = {
            'word_count': len(content.split()),
            'character_count': len(content),
            'sentence_count': len(re.split(r'[.!?]+', content)),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
            'has_headings': bool(re.search(r'^#+\s', content, re.MULTILINE)),
            'has_lists': bool(re.search(r'^\s*[-*+]\s|^(\d+\. )', content, re.MULTILINE)),
            'has_code_blocks': '```' in content,
            'has_equations': '$$' in content or '$' in content,
            'readability_score': self._calculate_readability_score(content)
        }
        
        return result

    def _calculate_readability_score(self, content: str) -> float:
        """计算可读性分数（简化版）"""
        words = content.split()
        sentences = re.split(r'[.!?]+', content)
        sentences = [s for s in sentences if s.strip()]  # 移除空句子
        
        if not words or not sentences:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        # 简化的可读性计算
        score = max(0, min(100, 204.8 - 1.015 * avg_sentence_length))
        return round(score, 2)


def main():
    """测试函数"""
    import argparse

    parser = argparse.ArgumentParser(description="内容优化器测试")
    parser.add_argument("content", nargs='?', help="要优化的内容")
    parser.add_argument("--file", help="包含内容的文件路径")

    args = parser.parse_args()

    optimizer = ContentOptimizer()

    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            content = f.read()
    elif args.content:
        content = args.content
    else:
        content = """
        # 第一章 引言
        本章将介绍相关内容.这是第一段内容.这是第二句话。
        - 列表项1
        - 列表项2
        代码块如下:
        ```
        print("Hello, world!")
        ```
        这里有一个公式 $E=mc^2$ 和另一个 $$\\int_0^\\infty e^{-x^2} dx$$
        """

    print("原始内容:")
    print(content)
    print("\n" + "="*50 + "\n")

    optimized = optimizer.optimize_content(content)
    print("优化后内容:")
    print(optimized)

    quality = optimizer.validate_content_quality(optimized)
    print("\n内容质量评估:")
    for key, value in quality.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()