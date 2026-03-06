#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公文格式规范生成器 - 简化版 API
用于在对话中快速调用
"""

from docx_formatter import DocxFormatter

def quick_generate(title, author, content_items, output_path):
    """
    快速生成公文
    
    Args:
        title: 文档标题
        author: 署名（可包含日期，用 \\n 分隔）
        content_items: 内容列表，每项是 dict:
            {
                'type': 'heading1' | 'heading2' | 'paragraph' | 'empty',
                'text': '内容文本',
                'bold_prefix': '加粗前缀'  # 可选
            }
        output_path: 输出文件路径
    
    Returns:
        生成的文件路径
    """
    formatter = DocxFormatter()
    
    # 添加标题
    if title:
        formatter.add_title(title)
    
    # 添加署名
    if author:
        formatter.add_author(author)
        formatter.add_empty_line()
    
    # 添加内容
    for item in content_items:
        item_type = item.get('type')
        text = item.get('text', '')
        
        if item_type == 'heading1':
            formatter.add_heading1(text)
        elif item_type == 'heading2':
            formatter.add_heading2(text)
        elif item_type == 'paragraph':
            bold_prefix = item.get('bold_prefix')
            formatter.add_paragraph(text, bold_prefix)
        elif item_type == 'empty':
            formatter.add_empty_line()
    
    # 保存
    formatter.save(output_path)
    return output_path

# 使用示例
if __name__ == '__main__':
    content = [
        {'type': 'heading1', 'text': '一、工作总结'},
        {'type': 'paragraph', 'text': '2025年，在区委的正确领导下，我们认真贯彻落实各项决策部署...'},
        {'type': 'paragraph', 'text': '深入学习贯彻习近平新时代中国特色社会主义思想...', 'bold_prefix': '一是强化理论学习。'},
        {'type': 'heading2', 'text': '（一）主要成绩'},
        {'type': 'paragraph', 'text': '全年完成各项指标任务...'},
    ]
    
    quick_generate(
        title='2025年度工作总结',
        author='某某单位\n（2026年2月1日）',
        content_items=content,
        output_path='test-output.docx'
    )
