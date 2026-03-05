#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FTdesign HTML 生成器

根据配置文件生成符合FTdesign设计规范的HTML页面。
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional


class HTMLGenerator:
    """HTML生成器类"""

    def __init__(self, template_dir: str, output_dir: str):
        self.template_dir = Path(template_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_list_page(
        self,
        page_title: str,
        system_name: str,
        sidebar_icon: str,
        menu_items: List[Dict[str, str]],
        filters: List[Dict],
        table_columns: List[str],
        table_data: List[Dict],
        output_filename: Optional[str] = None
    ) -> str:
        """
        生成列表页

        Args:
            page_title: 页面标题
            system_name: 系统名称
            sidebar_icon: 侧边栏图标
            menu_items: 菜单项列表 [{"name": "菜单名", "icon": "图标", "active": True}]
            filters: 筛选条件列表 [{"label": "标签", "type": "input/select", "placeholder": "占位符", "options": []}]
            table_columns: 表格列名
            table_data: 表格数据
            output_filename: 输出文件名，默认为 "{system_name}-list.html"
        """
        # 读取模板
        template_file = self.template_dir / "list-page.html"
        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_file}")

        html_content = template_file.read_text(encoding="utf-8")

        # 替换占位符
        html_content = html_content.replace("<title>内容管理 - 文章列表</title>", f"<title>{page_title}</title>")
        html_content = html_content.replace("内容管理系统", system_name)

        # 替换侧边栏
        html_content = self._replace_sidebar(html_content, system_name, sidebar_icon, menu_items)

        # 替换面包屑和标题
        html_content = html_content.replace("文章列表", page_title)

        # 生成输出文件名
        if output_filename is None:
            output_filename = f"{system_name}-list.html"

        output_path = self.output_dir / output_filename
        output_path.write_text(html_content, encoding="utf-8")

        print(f"✓ 列表页已生成: {output_path}")
        return str(output_path)

    def generate_form_page(
        self,
        page_title: str,
        system_name: str,
        sidebar_icon: str,
        menu_items: List[Dict[str, str]],
        form_fields: List[Dict],
        output_filename: Optional[str] = None
    ) -> str:
        """
        生成表单页

        Args:
            page_title: 页面标题
            system_name: 系统名称
            sidebar_icon: 侧边栏图标
            menu_items: 菜单项列表
            form_fields: 表单字段列表 [{"label": "标签", "type": "input/select/textarea", "required": True, "placeholder": "..."}]
            output_filename: 输出文件名，默认为 "{system_name}-form.html"
        """
        # 读取模板
        template_file = self.template_dir / "form-page.html"
        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_file}")

        html_content = template_file.read_text(encoding="utf-8")

        # 替换占位符
        html_content = html_content.replace("<title>内容管理 - 编辑文章</title>", f"<title>{page_title}</title>")
        html_content = html_content.replace("内容管理系统", system_name)

        # 替换侧边栏
        html_content = self._replace_sidebar(html_content, system_name, sidebar_icon, menu_items)

        # 替换面包屑和标题
        html_content = html_content.replace("编辑文章", page_title)

        # 生成输出文件名
        if output_filename is None:
            output_filename = f"{system_name}-form.html"

        output_path = self.output_dir / output_filename
        output_path.write_text(html_content, encoding="utf-8")

        print(f"✓ 表单页已生成: {output_path}")
        return str(output_path)

    def generate_detail_page(
        self,
        page_title: str,
        system_name: str,
        sidebar_icon: str,
        menu_items: List[Dict[str, str]],
        detail_data: Dict,
        output_filename: Optional[str] = None
    ) -> str:
        """
        生成详情页

        Args:
            page_title: 页面标题
            system_name: 系统名称
            sidebar_icon: 侧边栏图标
            menu_items: 菜单项列表
            detail_data: 详情数据 {"title": "...", "meta": {...}, "info": {...}}
            output_filename: 输出文件名，默认为 "{system_name}-detail.html"
        """
        # 读取模板
        template_file = self.template_dir / "detail-page.html"
        if not template_file.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_file}")

        html_content = template_file.read_text(encoding="utf-8")

        # 替换占位符
        html_content = html_content.replace("<title>内容管理 - 文章详情</title>", f"<title>{page_title}</title>")
        html_content = html_content.replace("内容管理系统", system_name)

        # 替换侧边栏
        html_content = self._replace_sidebar(html_content, system_name, sidebar_icon, menu_items)

        # 替换面包屑和标题
        html_content = html_content.replace("文章详情", page_title)

        # 生成输出文件名
        if output_filename is None:
            output_filename = f"{system_name}-detail.html"

        output_path = self.output_dir / output_filename
        output_path.write_text(html_content, encoding="utf-8")

        print(f"✓ 详情页已生成: {output_path}")
        return str(output_path)

    def _replace_sidebar(
        self,
        html_content: str,
        system_name: str,
        sidebar_icon: str,
        menu_items: List[Dict[str, str]]
    ) -> str:
        """替换侧边栏内容"""
        # 替换图标
        if sidebar_icon:
            html_content = html_content.replace('class="ri-box-3-fill"', f'class="{sidebar_icon}"')

        # 生成菜单HTML
        menu_html = ""
        current_group = None

        for item in menu_items:
            group = item.get("group", "主菜单")
            if group != current_group:
                if current_group is not None:
                    menu_html += "\n        "
                menu_html += f'<div class="ft-menu-group">{group}</div>\n'
                current_group = group

            active_class = " active" if item.get("active", False) else ""
            menu_html += f'<a href="#" class="ft-menu-item{active_class}"><i class="{item["icon"]}"></i>{item["name"]}</a>\n        '

        # 查找并替换菜单区域
        start = html_content.find('<nav class="ft-sidebar-menu">')
        end = html_content.find('</nav>', start)
        if start != -1 and end != -1:
            html_content = html_content[:start] + '<nav class="ft-sidebar-menu">\n        ' + menu_html + '</nav>' + html_content[end + 7:]

        return html_content


def main():
    """主函数 - 命令行入口"""

    if len(sys.argv) < 2:
        print("用法:")
        print("  python generate-html.py list <config.json>")
        print("  python generate-html.py form <config.json>")
        print("  python generate-html.py detail <config.json>")
        print("\n示例:")
        print("  python generate-html.py list user-list.json")
        sys.exit(1)

    # 获取脚本所在目录的父目录
    script_dir = Path(__file__).parent
    template_dir = script_dir.parent / "assets" / "templates"
    output_dir = script_dir.parent.parent.parent.parent  # 回到工作区根目录

    generator = HTMLGenerator(str(template_dir), str(output_dir))

    command = sys.argv[1].lower()

    if command == "list":
        if len(sys.argv) < 3:
            print("错误: 请指定配置文件")
            sys.exit(1)

        config_file = Path(sys.argv[2])
        if not config_file.exists():
            print(f"错误: 配置文件不存在: {config_file}")
            sys.exit(1)

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)

        generator.generate_list_page(
            page_title=config.get("page_title", "列表页"),
            system_name=config.get("system_name", "管理系统"),
            sidebar_icon=config.get("sidebar_icon", "ri-box-3-fill"),
            menu_items=config.get("menu_items", []),
            filters=config.get("filters", []),
            table_columns=config.get("table_columns", []),
            table_data=config.get("table_data", []),
            output_filename=config.get("output_filename")
        )

    elif command == "form":
        if len(sys.argv) < 3:
            print("错误: 请指定配置文件")
            sys.exit(1)

        config_file = Path(sys.argv[2])
        if not config_file.exists():
            print(f"错误: 配置文件不存在: {config_file}")
            sys.exit(1)

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)

        generator.generate_form_page(
            page_title=config.get("page_title", "表单页"),
            system_name=config.get("system_name", "管理系统"),
            sidebar_icon=config.get("sidebar_icon", "ri-box-3-fill"),
            menu_items=config.get("menu_items", []),
            form_fields=config.get("form_fields", []),
            output_filename=config.get("output_filename")
        )

    elif command == "detail":
        if len(sys.argv) < 3:
            print("错误: 请指定配置文件")
            sys.exit(1)

        config_file = Path(sys.argv[2])
        if not config_file.exists():
            print(f"错误: 配置文件不存在: {config_file}")
            sys.exit(1)

        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)

        generator.generate_detail_page(
            page_title=config.get("page_title", "详情页"),
            system_name=config.get("system_name", "管理系统"),
            sidebar_icon=config.get("sidebar_icon", "ri-box-3-fill"),
            menu_items=config.get("menu_items", []),
            detail_data=config.get("detail_data", {}),
            output_filename=config.get("output_filename")
        )

    else:
        print(f"错误: 未知的命令 '{command}'")
        print("可用命令: list, form, detail")
        sys.exit(1)


if __name__ == "__main__":
    main()
