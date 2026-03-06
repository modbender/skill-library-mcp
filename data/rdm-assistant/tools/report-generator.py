#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器 - 基于模板生成晨会报告、周报等
用法: python report-generator.py --template <模板路径> --config <配置路径> --output <输出路径>
"""

import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path


class ReportGenerator:
    """报告生成器类"""

    def __init__(self, template_path, config_path=None, output_path=None):
        self.template_path = Path(template_path)
        self.config_path = Path(config_path) if config_path else None
        self.output_path = Path(output_path) if output_path else None

        # 加载配置
        self.config = self._load_config()

        # 模板变量
        self.variables = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M'),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'weekday': datetime.now().strftime('%A'),
        }

        # 合并配置到变量
        if self.config:
            self.variables.update(self._config_to_variables())

    def _load_config(self):
        """加载配置文件（支持 YAML 或 JSON）"""
        if not self.config_path or not self.config_path.exists():
            return {}

        # 简单实现：只支持 JSON
        # 实际应该支持 YAML
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                import json
                return json.load(f)
        except:
            return {}

    def _config_to_variables(self):
        """将配置转换为模板变量"""
        variables = {}

        if 'project' in self.config:
            variables['project_name'] = self.config['project'].get('name', '')

        if 'team' in self.config:
            members = self.config['team']
            variables['team_members'] = ', '.join([m['name'] for m in members])

        return variables

    def _read_template(self):
        """读取模板文件"""
        with open(self.template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def _fill_template(self, template):
        """填充模板变量（简单实现）"""
        content = template

        # 替换 {{变量}}
        for key, value in self.variables.items():
            placeholder = '{{' + key + '}}'
            content = content.replace(placeholder, str(value))

        return content

    def generate(self):
        """生成报告"""
        # 检查模板文件
        if not self.template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {self.template_path}")

        # 读取模板
        template = self._read_template()

        # 填充模板
        content = self._fill_template(template)

        # 输出结果
        if self.output_path:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 报告已生成: {self.output_path}")
            return str(self.output_path)
        else:
            print(content)
            return content

    def set_variable(self, key, value):
        """设置模板变量"""
        self.variables[key] = value

    def set_variables(self, variables):
        """批量设置模板变量"""
        self.variables.update(variables)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description='报告生成器')
    parser.add_argument('--template', '-t', required=True, help='模板文件路径')
    parser.add_argument('--config', '-c', help='配置文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径')
    parser.add_argument('--var', nargs=2, metavar=('KEY', 'VALUE'), action='append',
                       help='设置模板变量（可多次使用）')

    args = parser.parse_args()

    # 创建生成器
    generator = ReportGenerator(args.template, args.config, args.output)

    # 设置命令行变量
    if args.var:
        for key, value in args.var:
            generator.set_variable(key, value)

    # 生成报告
    try:
        generator.generate()
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
