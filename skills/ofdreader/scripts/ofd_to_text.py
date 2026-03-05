#!/usr/bin/env python3
"""
OFD 文本提取脚本
从 OFD 文件中提取纯文本内容
"""
import zipfile
import xml.etree.ElementTree as ET
import sys
import os
from pathlib import Path


def extract_text_from_ofd(ofd_path):
    """
    从 OFD 文件中提取文本内容

    Args:
        ofd_path: OFD 文件路径

    Returns:
        提取的文本内容
    """
    if not os.path.exists(ofd_path):
        raise FileNotFoundError(f"OFD 文件不存在: {ofd_path}")

    text_content = []

    try:
        with zipfile.ZipFile(ofd_path, 'r') as zip_ref:
            # 获取所有 XML 文件
            file_list = zip_ref.namelist()

            # OFD 文件结构：根目录有 OFD.xml，内容在 Doc_0/ 下
            # 首先读取 OFD.xml 获取文档结构
            ofd_xml_files = [f for f in file_list if f.endswith('.xml') and 'Doc_' in f]

            for xml_file in ofd_xml_files:
                try:
                    with zip_ref.open(xml_file) as xml_file_obj:
                        tree = ET.parse(xml_file_obj)
                        root = tree.getroot()

                        # OFD 命名空间
                        namespace = {'ofd': 'http://www.ofdspec.org/2016'}

                        # 提取文本内容
                        # 文本可能在 TextCode 字段中
                        for text_elem in root.iter():
                            # 检查 TextCode 元素
                            if text_elem.tag.endswith('TextCode'):
                                if text_elem.text:
                                    text_content.append(text_elem.text)
                            # 检查 TextContent 元素
                            elif text_elem.tag.endswith('TextContent'):
                                if text_elem.text:
                                    text_content.append(text_elem.text)

                except Exception as e:
                    # 某些 XML 文件可能解析失败，跳过
                    continue

    except zipfile.BadZipFile:
        raise ValueError(f"文件不是有效的 OFD (ZIP) 格式: {ofd_path}")
    except Exception as e:
        raise RuntimeError(f"解析 OFD 文件时出错: {e}")

    return '\n'.join(text_content)


def main():
    if len(sys.argv) < 2:
        print("用法: python ofd_to_text.py <ofd文件路径> [输出文件路径]")
        sys.exit(1)

    ofd_path = sys.argv[1]

    try:
        text = extract_text_from_ofd(ofd_path)

        if len(sys.argv) >= 3:
            # 输出到文件
            output_path = sys.argv[2]
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"文本已提取到: {output_path}")
        else:
            # 输出到控制台
            print(text)

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
