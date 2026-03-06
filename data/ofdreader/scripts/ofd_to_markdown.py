#!/usr/bin/env python3
"""
OFD 转 Markdown 脚本
将 OFD 文件转换为 Markdown 格式，保留基本格式和表格
"""
import zipfile
import xml.etree.ElementTree as ET
import sys
import os
import re
from pathlib import Path


class OFDToMarkdownConverter:
    """OFD 到 Markdown 转换器"""

    def __init__(self, ofd_path):
        self.ofd_path = ofd_path
        self.namespace = {'ofd': 'http://www.ofdspec.org/2016'}
        self.markdown_lines = []

    def convert(self):
        """执行转换"""
        if not os.path.exists(self.ofd_path):
            raise FileNotFoundError(f"OFD 文件不存在: {self.ofd_path}")

        try:
            with zipfile.ZipFile(self.ofd_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()

                # 查找文档内容文件
                doc_files = [f for f in file_list if f.endswith('.xml') and 'Doc_' in f]

                for doc_file in sorted(doc_files):
                    self._process_document(zip_ref, doc_file)

                return '\n'.join(self.markdown_lines)

        except zipfile.BadZipFile:
            raise ValueError(f"文件不是有效的 OFD (ZIP) 格式: {self.ofd_path}")
        except Exception as e:
            raise RuntimeError(f"解析 OFD 文件时出错: {e}")

    def _process_document(self, zip_ref, doc_file):
        """处理单个文档文件"""
        try:
            with zip_ref.open(doc_file) as f:
                tree = ET.parse(f)
                root = tree.getroot()

                # 处理页面
                for page in root.iter():
                    if page.tag.endswith('Page'):
                        self._process_page(page)

        except Exception:
            pass

    def _process_page(self, page_elem):
        """处理页面元素"""
        # 查找文本块
        text_blocks = list(page_elem.iter())
        current_text = []

        for elem in text_blocks:
            # 处理文本代码
            if elem.tag.endswith('TextCode'):
                if elem.text:
                    text = elem.text.strip()
                    if text:
                        current_text.append(text)

            # 处理表格
            elif elem.tag.endswith('Table'):
                # 先处理之前累积的文本
                if current_text:
                    self.markdown_lines.append(' '.join(current_text))
                    current_text = []

                table_md = self._process_table(elem)
                if table_md:
                    self.markdown_lines.append(table_md)
                    self.markdown_lines.append('')

            # 处理段落（可能是标题）
            elif elem.tag.endswith('Paragraph'):
                para_text = self._extract_paragraph_text(elem)
                if para_text:
                    # 简单的标题检测
                    if self._is_heading(para_text):
                        level = self._detect_heading_level(elem)
                        self.markdown_lines.append(f"{'#' * level} {para_text}")
                        self.markdown_lines.append('')
                    else:
                        self.markdown_lines.append(para_text)
                        self.markdown_lines.append('')

        # 处理剩余的文本
        if current_text:
            self.markdown_lines.append(' '.join(current_text))

    def _extract_paragraph_text(self, para_elem):
        """从段落元素中提取文本"""
        texts = []
        for text_elem in para_elem.iter():
            if text_elem.tag.endswith('TextCode') and text_elem.text:
                texts.append(text_elem.text.strip())
        return ' '.join(texts) if texts else None

    def _is_heading(self, text):
        """判断是否为标题"""
        # 简单的启发式规则
        if not text:
            return False

        # 较短的文本、可能以数字开头（如 1. 第一章）
        if len(text) < 50:
            # 检测常见标题模式
            patterns = [
                r'^第[一二三四五六七八九十\d]+[章节篇]',
                r'^\d+\.\s',
                r'^[一二三四五六七八九十]+[、.]',
            ]
            for pattern in patterns:
                if re.match(pattern, text):
                    return True

        return False

    def _detect_heading_level(self, elem):
        """检测标题级别"""
        # 基于 OFD 结构或属性判断
        # 这里使用简单的默认值
        return 2

    def _process_table(self, table_elem):
        """处理表格元素"""
        rows = []

        # 查找所有行
        for row_elem in table_elem.iter():
            if row_elem.tag.endswith('Row'):
                cells = self._extract_row_cells(row_elem)
                if cells:
                    rows.append(cells)

        if not rows:
            return None

        # 构建 Markdown 表格
        md_lines = []

        # 表头
        if rows:
            header = '| ' + ' | '.join(rows[0]) + ' |'
            md_lines.append(header)

            # 分隔线
            separator = '| ' + ' | '.join(['---'] * len(rows[0])) + ' |'
            md_lines.append(separator)

            # 数据行
            for row in rows[1:]:
                # 确保行与表头列数一致
                while len(row) < len(rows[0]):
                    row.append('')
                row_text = '| ' + ' | '.join(row) + ' |'
                md_lines.append(row_text)

        return '\n'.join(md_lines) if md_lines else None

    def _extract_row_cells(self, row_elem):
        """提取行的所有单元格"""
        cells = []

        for cell_elem in row_elem.iter():
            if cell_elem.tag.endswith('Cell') or cell_elem.tag.endswith('Td'):
                cell_text = self._extract_cell_text(cell_elem)
                cells.append(cell_text)

        return cells

    def _extract_cell_text(self, cell_elem):
        """提取单元格文本"""
        texts = []
        for text_elem in cell_elem.iter():
            if text_elem.tag.endswith('TextCode') and text_elem.text:
                texts.append(text_elem.text.strip())
        return ' '.join(texts) if texts else ''


def main():
    if len(sys.argv) < 2:
        print("用法: python ofd_to_markdown.py <ofd文件路径> [输出md文件路径]")
        sys.exit(1)

    ofd_path = sys.argv[1]

    try:
        converter = OFDToMarkdownConverter(ofd_path)
        markdown = converter.convert()

        if len(sys.argv) >= 3:
            # 输出到文件
            output_path = sys.argv[2]
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"Markdown 已生成: {output_path}")
        else:
            # 输出到控制台
            print(markdown)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
