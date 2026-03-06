#!/usr/bin/env python3
"""
智能写书主程序 - 根据提示词生成书籍大纲并逐级扩写内容
"""

import os
import sys
import json
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

# 尝试导入依赖，如果失败则提供替代方案
try:
    import openai
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# 导入内容优化器
try:
    from .content_optimizer import ContentOptimizer
    HAS_CONTENT_OPTIMIZER = True
except ImportError:
    HAS_CONTENT_OPTIMIZER = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/book_writer.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class BookOutline:
    """书籍大纲数据结构"""
    title: str
    subtitle: Optional[str]
    chapters: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@dataclass
class ChapterContent:
    """章节内容数据结构"""
    chapter_number: int
    title: str
    sections: List[Dict[str, Any]]
    content: str
    formulas: List[str]
    figures: List[Dict[str, str]]
    tables: List[Dict[str, Any]]
    code_snippets: List[Dict[str, str]]
    references: List[str]

@dataclass
class Book:
    """整本书的数据结构"""
    title: str
    outline: BookOutline
    chapters: List[ChapterContent]
    metadata: Dict[str, Any]

class BookWriter:
    """智能写书主类"""

    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化写书器

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.client = None
        self.content_optimizer = None
        
        # 初始化OpenAI客户端
        self._initialize_openai_client()
        
        # 初始化内容优化器
        self._initialize_content_optimizer()

        # 创建输出目录
        self.output_dir = self.config.get("storage", {}).get("output_dir", "generated_books")
        self.temp_dir = self.config.get("storage", {}).get("temp_dir", "temp_files")
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.temp_dir).mkdir(parents=True, exist_ok=True)

        logger.info(f"写书器初始化完成，输出目录: {self.output_dir}")

    def _load_config(self, config_path: str) -> Dict:
        """加载配置文件"""
        if not os.path.exists(config_path):
            logger.warning(f"配置文件 {config_path} 不存在，使用默认配置")
            return {}

        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {config_path}")
            return config or {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return {}

    def _initialize_openai_client(self):
        """初始化OpenAI客户端"""
        if not HAS_OPENAI:
            logger.warning("OpenAI库未安装，将使用模拟模式")
            return

        openai_config = self.config.get("openai", {})
        api_key = os.environ.get("OPENAI_API_KEY") or openai_config.get("api_key")

        if not api_key:
            logger.warning("OpenAI API密钥未设置，将使用模拟模式")
            return

        try:
            self.client = OpenAI(api_key=api_key)
            logger.info("OpenAI客户端初始化成功")
        except Exception as e:
            logger.error(f"OpenAI客户端初始化失败: {e}")

    def _initialize_content_optimizer(self):
        """初始化内容优化器"""
        if HAS_CONTENT_OPTIMIZER:
            try:
                self.content_optimizer = ContentOptimizer()
                logger.info("内容优化器初始化成功")
            except Exception as e:
                logger.error(f"内容优化器初始化失败: {e}")
                self.content_optimizer = None

    def generate_outline(self, prompt: str, max_chapters: Optional[int] = None) -> BookOutline:
        """
        根据提示词生成书籍大纲

        Args:
            prompt: 书籍主题提示词
            max_chapters: 最大章节数

        Returns:
            BookOutline: 生成的书籍大纲
        """
        logger.info(f"开始生成书籍大纲: {prompt}")

        # 使用默认值或配置值
        if max_chapters is None:
            max_chapters = self.config.get("defaults", {}).get("max_chapters", 10)

        # 构造请求
        outline_prompt = f"""
        请为以下主题生成一本结构完整的书籍大纲：
        主题: {prompt}

        要求：
        1. 生成不超过{max_chapters}章的大纲
        2. 每章包含3-5个小节
        3. 为每章和每节提供简要描述
        4. 考虑目标读者为{self.config.get('content', {}).get('target_audience', 'general')}
        5. 内容风格应为{self.config.get('content', {}).get('writing_style', 'informative')}

        请以JSON格式返回，结构如下：
        {{
            "title": "书籍标题",
            "subtitle": "副标题（可选）",
            "chapters": [
                {{
                    "chapter_number": 1,
                    "title": "第一章标题",
                    "description": "章节简介",
                    "sections": [
                        {{
                            "section_number": 1,
                            "title": "第一节标题",
                            "description": "小节简介"
                        }}
                    ]
                }}
            ],
            "metadata": {{
                "topic": "{prompt}",
                "target_audience": "{self.config.get('content', {}).get('target_audience', 'general')}",
                "writing_style": "{self.config.get('content', {}).get('writing_style', 'informative')}"
            }}
        }}
        """

        if self.client:
            # 使用真实的OpenAI API
            try:
                response = self.client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[{"role": "user", "content": outline_prompt}],
                    temperature=self.config.get("openai", {}).get("temperature", 0.7),
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 2000)
                )
                
                response_text = response.choices[0].message.content
                logger.info(f"OpenAI响应: {response_text[:200]}...")
            except Exception as e:
                logger.error(f"OpenAI API调用失败: {e}")
                response_text = self._generate_outline_mock(prompt, max_chapters)  # 使用模拟数据
        else:
            # 使用模拟模式
            response_text = self._generate_outline_mock(prompt, max_chapters)

        # 解析响应
        try:
            # 尝试提取JSON部分
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                outline_data = json.loads(json_str)
                
                # 创建BookOutline对象
                outline = BookOutline(
                    title=outline_data.get("title", "未命名书籍"),
                    subtitle=outline_data.get("subtitle"),
                    chapters=outline_data.get("chapters", []),
                    metadata=outline_data.get("metadata", {})
                )
                
                logger.info(f"大纲生成成功，共{len(outline.chapters)}章")
                return outline
            else:
                logger.error("未能从响应中提取JSON数据")
                # 返回一个基本的大纲
                return self._create_basic_outline(prompt, max_chapters)
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            logger.error(f"响应内容: {response_text}")
            return self._create_basic_outline(prompt, max_chapters)

    def _generate_outline_mock(self, prompt: str, max_chapters: int) -> str:
        """模拟生成大纲（用于测试或无API密钥时）"""
        logger.info(f"使用模拟模式生成大纲: {prompt}")
        
        # 创建一个模拟的JSON响应
        mock_outline = {
            "title": f"{prompt} - 完整指南",
            "subtitle": f"深入理解{prompt}的核心概念与应用",
            "chapters": [],
            "metadata": {
                "topic": prompt,
                "target_audience": self.config.get('content', {}).get('target_audience', 'general'),
                "writing_style": self.config.get('content', {}).get('writing_style', 'informative')
            }
        }
        
        for i in range(1, min(max_chapters, 5) + 1):  # 限制为最多5章以保持简洁
            chapter = {
                "chapter_number": i,
                "title": f"第{i}章 {prompt}基础",
                "description": f"介绍{prompt}的基本概念和原理",
                "sections": []
            }
            
            for j in range(1, 4):  # 每章3个小节
                section_title = f"{chapter['title']}的小节{j}"
                chapter["sections"].append({
                    "section_number": j,
                    "title": section_title,
                    "description": f"探讨{section_title}的相关内容"
                })
            
            mock_outline["chapters"].append(chapter)
        
        return json.dumps(mock_outline, ensure_ascii=False, indent=2)

    def _create_basic_outline(self, prompt: str, max_chapters: int) -> BookOutline:
        """创建基本大纲（当JSON解析失败时）"""
        logger.warning("创建基本大纲结构")
        
        chapters = []
        for i in range(1, min(max_chapters, 5) + 1):
            chapters.append({
                "chapter_number": i,
                "title": f"第{i}章",
                "description": f"关于{prompt}的第{i}部分内容",
                "sections": [{
                    "section_number": 1,
                    "title": "引言",
                    "description": "本章引言"
                }, {
                    "section_number": 2,
                    "title": "主要内容",
                    "description": "本章主要内容"
                }, {
                    "section_number": 3,
                    "title": "总结",
                    "description": "本章总结"
                }]
            })
        
        return BookOutline(
            title=f"{prompt}指南",
            subtitle=f"关于{prompt}的全面介绍",
            chapters=chapters,
            metadata={
                "topic": prompt,
                "target_audience": self.config.get('content', {}).get('target_audience', 'general'),
                "writing_style": self.config.get('content', {}).get('writing_style', 'informative')
            }
        )

    def expand_chapter(self, chapter_data: Dict, chapter_index: int) -> ChapterContent:
        """
        扩写单个章节

        Args:
            chapter_data: 章节数据
            chapter_index: 章节索引

        Returns:
            ChapterContent: 扩写后的章节内容
        """
        logger.info(f"开始扩写章节: {chapter_data['title']}")

        # 构造扩写提示
        expand_prompt = f"""
        请详细扩写以下章节内容：
        章节标题: {chapter_data['title']}
        章节描述: {chapter_data['description']}
        
        该章节包含以下小节：
        {chr(10).join([f"- {sec['title']}: {sec['description']}" for sec in chapter_data['sections']])}
        
        要求：
        1. 写作长度为{self.config.get('defaults', {}).get('content_length', 'medium')}
        2. 包含适当的标题层级结构
        3. 如适用，添加相关的数学公式、代码示例、图表描述或表格
        4. 保持{self.config.get('content', {}).get('writing_style', 'informative')}的写作风格
        5. 如适用，包含相关引用和参考文献
        
        请返回内容，包含：
        - 主要内容文本
        - 数学公式列表（如果有）
        - 代码示例列表（如果有）
        - 图表描述列表（如果有）
        - 表格数据列表（如果有）
        - 参考文献列表（如果有）
        """

        if self.client:
            # 使用真实的OpenAI API
            try:
                response = self.client.chat.completions.create(
                    model=self.config.get("openai", {}).get("model", "gpt-4o"),
                    messages=[{"role": "user", "content": expand_prompt}],
                    temperature=self.config.get("openai", {}).get("temperature", 0.7),
                    max_tokens=self.config.get("openai", {}).get("max_tokens", 3000)
                )
                
                content = response.choices[0].message.content
            except Exception as e:
                logger.error(f"OpenAI API调用失败: {e}")
                content = self._expand_chapter_mock(chapter_data, chapter_index)  # 使用模拟数据
        else:
            # 使用模拟模式
            content = self._expand_chapter_mock(chapter_data, chapter_index)

        # 解析内容，提取各种元素
        chapter_content = self._parse_expanded_content(content, chapter_data, chapter_index)
        
        logger.info(f"章节扩写完成: {chapter_data['title']}")
        return chapter_content

    def _expand_chapter_mock(self, chapter_data: Dict, chapter_index: int) -> str:
        """模拟扩写章节内容"""
        logger.info(f"使用模拟模式扩写章节: {chapter_data['title']}")
        
        return f"""
# {chapter_data['title']}

## 章节概述

本章将详细介绍{chapter_data['title']}的相关内容。我们将从基本概念入手，逐步深入探讨其核心原理和实际应用。

## 主要内容

{chapter_data['description']}

在这一部分，我们将：

1. 介绍基本定义和概念
2. 探讨核心原理
3. 分析实际应用场景

## 小节内容

"""

    def _parse_expanded_content(self, content: str, chapter_data: Dict, chapter_index: int) -> ChapterContent:
        """解析扩写后的内容，提取各种元素"""
        # 提取数学公式（LaTeX格式）
        formula_pattern = r'\$\$(.*?)\$\$|\$(.*?)\$'
        formulas = re.findall(formula_pattern, content, re.DOTALL)
        formulas = [item[0] if item[0] else item[1] for item in formulas if item[0] or item[1]]

        # 提取代码块
        code_pattern = r'```(\w*)\n(.*?)```'
        code_matches = re.findall(code_pattern, content, re.DOTALL)
        code_snippets = [{"language": lang, "code": code.strip()} for lang, code in code_matches]

        # 提取图表描述（简单模式）
        figure_pattern = r'图\d+[:：]\s*(.*?)(?:\n|$)'
        figures = [{"caption": cap.strip(), "description": cap.strip()} for cap in re.findall(figure_pattern, content)]

        # 提取表格（简单模式）
        table_pattern = r'表\d+[:：]\s*(.*?)(?:\n|$)'
        tables = [{"title": tbl.strip(), "description": tbl.strip()} for tbl in re.findall(table_pattern, content)]

        # 提取参考文献
        ref_patterns = [
            r'\[(\d+)\].*?',
            r'(?:参考文献|References).*?\n((?:.*?\n)*?)\n\n',
            r'\[([^\]]+)\]'
        ]
        references = []
        for pat in ref_patterns:
            refs = re.findall(pat, content)
            references.extend(refs)

        return ChapterContent(
            chapter_number=chapter_index,
            title=chapter_data['title'],
            sections=chapter_data['sections'],
            content=content,
            formulas=formulas,
            figures=figures,
            tables=tables,
            code_snippets=code_snippets,
            references=list(set(references))  # 去重
        )

    def expand_book(self, outline: BookOutline, max_chapters: Optional[int] = None) -> Book:
        """
        扩写整本书

        Args:
            outline: 书籍大纲
            max_chapters: 最大扩写章节数

        Returns:
            Book: 扩写后的书籍
        """
        logger.info(f"开始扩写整本书: {outline.title}")

        if max_chapters is None:
            max_chapters = self.config.get("defaults", {}).get("max_chapters", 3)  # 默认只扩写3章

        chapters_to_expand = outline.chapters[:max_chapters]
        expanded_chapters = []

        for i, chapter_data in enumerate(chapters_to_expand):
            logger.info(f"正在扩写第{i+1}/{len(chapters_to_expand)}章")
            chapter_content = self.expand_chapter(chapter_data, i+1)
            expanded_chapters.append(chapter_content)

        book = Book(
            title=outline.title,
            outline=outline,
            chapters=expanded_chapters,
            metadata=outline.metadata
        )

        logger.info(f"书籍扩写完成，共{len(expanded_chapters)}章")
        return book

    def save_book(self, book: Book, output_path: str):
        """
        保存书籍到文件

        Args:
            book: 书籍对象
            output_path: 输出路径
        """
        output_dir = Path(self.output_dir) / output_path
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存完整书籍数据
        book_data = {
            "title": book.title,
            "outline": asdict(book.outline),
            "chapters": [asdict(chapter) for chapter in book.chapters],
            "metadata": book.metadata
        }

        with open(output_dir / "book.json", 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

        # 为每一章创建单独的文件
        for chapter in book.chapters:
            chapter_file = output_dir / f"chapter_{chapter.chapter_number:02d}.md"
            with open(chapter_file, 'w', encoding='utf-8') as f:
                f.write(f"# {chapter.title}\n\n")
                f.write(chapter.content)
                
                # 添加公式
                if chapter.formulas:
                    f.write("\n## 数学公式\n\n")
                    for i, formula in enumerate(chapter.formulas):
                        f.write(f"$$\n{formula}\n$$\n\n")
                
                # 添加代码
                if chapter.code_snippets:
                    f.write("\n## 代码示例\n\n")
                    for snippet in chapter.code_snippets:
                        f.write(f"```{snippet['language']}\n{snippet['code']}\n```\n\n")
                
                # 添加图表
                if chapter.figures:
                    f.write("\n## 图表\n\n")
                    for figure in chapter.figures:
                        f.write(f"图: {figure['caption']}\n\n")
                
                # 添加表格
                if chapter.tables:
                    f.write("\n## 表格\n\n")
                    for table in chapter.tables:
                        f.write(f"表: {table['title']}\n\n")

        logger.info(f"书籍已保存到: {output_dir}")

def main():
    """命令行入口点"""
    import argparse

    parser = argparse.ArgumentParser(description="智能写书工具")
    parser.add_argument("--action", choices=["outline", "expand", "full"], 
                       default="outline", help="操作类型: outline(生成大纲), expand(扩写内容), full(全流程)")
    parser.add_argument("--prompt", type=str, help="书籍主题提示词")
    parser.add_argument("--book-path", type=str, help="书籍路径（扩写时使用）")
    parser.add_argument("--chapters", type=str, default="1,2,3", help="要扩写的章节（逗号分隔）")
    parser.add_argument("--output", type=str, help="输出目录名称")
    parser.add_argument("--max-chapters", type=int, default=3, help="最大章节数")

    args = parser.parse_args()

    # 创建写书器
    writer = BookWriter()

    if args.action == "outline":
        if not args.prompt:
            print("❌ 错误: 生成大纲需要提供 --prompt 参数")
            return

        print(f"📖 正在为 '{args.prompt}' 生成书籍大纲...")
        outline = writer.generate_outline(args.prompt, args.max_chapters)
        
        print(f"✅ 大纲生成完成！共 {len(outline.chapters)} 章")
        print(f"📚 书籍标题: {outline.title}")
        
        # 保存大纲
        output_name = args.output or outline.title.replace(" ", "_").replace("/", "_")
        outline_path = Path(writer.output_dir) / output_name
        outline_path.mkdir(parents=True, exist_ok=True)
        
        outline_data = {
            "title": outline.title,
            "subtitle": outline.subtitle,
            "chapters": outline.chapters,
            "metadata": outline.metadata
        }
        
        with open(outline_path / "outline.json", 'w', encoding='utf-8') as f:
            json.dump(outline_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 大纲已保存到: {outline_path}/outline.json")

    elif args.action == "expand":
        if not args.book_path:
            print("❌ 错误: 扩写内容需要提供 --book-path 参数")
            return
            
        if not args.prompt:
            print("❌ 错误: 扩写内容需要提供 --prompt 参数（用于重新生成大纲）")
            # 我们将从现有的大纲文件加载
            outline_path = Path(writer.output_dir) / args.book_path / "outline.json"
            if not outline_path.exists():
                print(f"❌ 错误: 未找到大纲文件 {outline_path}")
                return
            with open(outline_path, 'r', encoding='utf-8') as f:
                outline_data = json.load(f)
            # 重构BookOutline对象
            outline = BookOutline(
                title=outline_data["title"],
                subtitle=outline_data["subtitle"],
                chapters=outline_data["chapters"],
                metadata=outline_data["metadata"]
            )
        else:
            # 生成新大纲
            print(f"📖 正在为 '{args.prompt}' 生成书籍大纲...")
            outline = writer.generate_outline(args.prompt, args.max_chapters)

        print(f"✍️  正在扩写书籍内容...")
        selected_chapters = [int(x.strip()) for x in args.chapters.split(",")]
        max_chap = max(selected_chapters) if selected_chapters else args.max_chapters
        book = writer.expand_book(outline, max_chap)
        
        print(f"✅ 内容扩写完成！")
        
        # 保存完整书籍
        output_name = args.output or args.book_path
        writer.save_book(book, output_name)
        
        print(f"💾 书籍已保存到: {writer.output_dir}/{output_name}")

    elif args.action == "full":
        if not args.prompt:
            print("❌ 错误: 全流程操作需要提供 --prompt 参数")
            return

        print(f"📖 正在为 '{args.prompt}' 生成书籍大纲...")
        outline = writer.generate_outline(args.prompt, args.max_chapters)
        
        print(f"✍️  正在扩写书籍内容...")
        book = writer.expand_book(outline, args.max_chapters)
        
        output_name = args.output or outline.title.replace(" ", "_").replace("/", "_")
        writer.save_book(book, output_name)
        
        print(f"🎉 书籍生成完成！")
        print(f"📚 书籍标题: {book.title}")
        print(f"💾 保存位置: {writer.output_dir}/{output_name}")

if __name__ == "__main__":
    main()