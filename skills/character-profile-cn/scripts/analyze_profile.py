#!/usr/bin/env python3
"""
人物档案分析脚本
分析markdown格式的人物档案完整性
"""

import os
import re
import sys
from pathlib import Path

class ProfileAnalyzer:
    """人物档案分析器"""

    def __init__(self):
        self.placeholder_patterns = [
            r'待填写',
            r'TODO',
            r'待补充',
            r'待完善',
            r'\[.*\]',
            r'\{.*\}',
            r'未指定',
            r'未知',
            r'待定'
        ]

        # 检测平台，Windows上使用简单符号
        self.is_windows = sys.platform.startswith('win')

        # 符号定义
        if self.is_windows:
            self.symbols = {
                'chart': '[统计]',
                'trophy': '[评估]',
                'file': '[章节]',
                'warning': '[注意]',
                'bulb': '[建议]',
                'check': '[OK]',
                'arrow': '->',
                'cross': '[X]',
                'green_circle': '[良好]',
                'yellow_circle': '[一般]',
                'red_circle': '[需改进]',
                'bullet': '-'
            }
        else:
            self.symbols = {
                'chart': '📊',
                'trophy': '🏆',
                'file': '📑',
                'warning': '⚠️',
                'bulb': '💡',
                'check': '✓',
                'arrow': '→',
                'cross': '✗',
                'green_circle': '🟢',
                'yellow_circle': '🟡',
                'red_circle': '🔴',
                'bullet': '•'
            }

    def analyze_markdown(self, filepath):
        """分析markdown档案

        Args:
            filepath: markdown文件路径

        Returns:
            分析结果字典
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 基本统计
        lines = content.split('\n')
        total_lines = len(lines)
        non_empty_lines = len([line for line in lines if line.strip()])

        # 章节分析
        sections = self._extract_sections(content)

        # 占位符检测
        placeholder_count = 0
        placeholder_details = []

        for i, line in enumerate(lines, 1):
            for pattern in self.placeholder_patterns:
                if re.search(pattern, line):
                    placeholder_count += 1
                    placeholder_details.append({
                        'line': i,
                        'content': line.strip()[:50] + '...' if len(line.strip()) > 50 else line.strip()
                    })
                    break

        # 完整性评分
        completeness_score = self._calculate_completeness_score(
            non_empty_lines, placeholder_count, len(sections)
        )

        return {
            'filepath': filepath,
            'total_lines': total_lines,
            'non_empty_lines': non_empty_lines,
            'sections_count': len(sections),
            'sections': sections,
            'placeholder_count': placeholder_count,
            'placeholder_details': placeholder_details[:10],  # 只显示前10个
            'completeness_score': completeness_score,
            'completeness_level': self._get_completeness_level(completeness_score)
        }

    def _extract_sections(self, content):
        """提取章节信息"""
        sections = []

        # 匹配各级标题
        header_pattern = r'^(#{1,3})\s+(.+?)$'

        lines = content.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            match = re.match(header_pattern, line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                # 计算章节内容行数（直到下一个标题）
                content_lines = 0
                for j in range(i + 1, len(lines)):
                    if re.match(r'^#{1,3}\s+', lines[j].strip()):
                        break
                    if lines[j].strip():
                        content_lines += 1

                sections.append({
                    'level': level,
                    'title': title,
                    'start_line': i + 1,
                    'content_lines': content_lines
                })

        return sections

    def _calculate_completeness_score(self, non_empty_lines, placeholder_count, sections_count):
        """计算完整性评分（0-100）"""
        if non_empty_lines == 0:
            return 0

        # 基础分：基于非空行数（假设完整档案至少50行）
        base_score = min(100, (non_empty_lines / 50) * 60)

        # 占位符扣分：每个占位符扣2分，最多扣30分
        placeholder_penalty = min(30, placeholder_count * 2)

        # 章节加分：每节加5分，最多加20分
        section_bonus = min(20, sections_count * 5)

        score = base_score - placeholder_penalty + section_bonus
        return max(0, min(100, score))

    def _get_completeness_level(self, score):
        """获取完整性等级"""
        if score >= 90:
            return "优秀"
        elif score >= 75:
            return "良好"
        elif score >= 60:
            return "一般"
        elif score >= 40:
            return "待完善"
        else:
            return "草稿"

    def generate_report(self, analysis_result, output_format='text'):
        """生成分析报告"""
        result = analysis_result

        if output_format == 'text':
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append(f"人物档案分析报告")
            report_lines.append(f"文件: {result['filepath']}")
            report_lines.append("=" * 60)
            report_lines.append("")

            # 基本信息
            report_lines.append(f"{self.symbols['chart']} 基本信息")
            report_lines.append(f"  总行数: {result['total_lines']}")
            report_lines.append(f"  非空行数: {result['non_empty_lines']}")
            report_lines.append(f"  章节数: {result['sections_count']}")
            report_lines.append(f"  占位符数量: {result['placeholder_count']}")
            report_lines.append("")

            # 完整性评分
            report_lines.append(f"{self.symbols['trophy']} 完整性评估")
            report_lines.append(f"  评分: {result['completeness_score']:.1f}/100")
            report_lines.append(f"  等级: {result['completeness_level']}")
            report_lines.append("")

            # 章节详情
            if result['sections']:
                report_lines.append(f"{self.symbols['file']} 章节详情")
                for section in result['sections']:
                    level_indent = "  " * (section['level'] - 1)
                    report_lines.append(f"{level_indent}{self.symbols['bullet']} {section['title']} (行 {section['start_line']}, {section['content_lines']} 行)")
                report_lines.append("")

            # 占位符详情
            if result['placeholder_details']:
                report_lines.append(f"{self.symbols['warning']} 需要完善的部分")
                for detail in result['placeholder_details']:
                    report_lines.append(f"  第 {detail['line']} 行: {detail['content']}")

                if result['placeholder_count'] > 10:
                    report_lines.append(f"  ... 还有 {result['placeholder_count'] - 10} 个占位符未显示")
                report_lines.append("")

            # 建议
            report_lines.append(f"{self.symbols['bulb']} 建议")
            if result['completeness_score'] >= 80:
                report_lines.append(f"  {self.symbols['check']} 档案比较完整，可以开始用于创作")
                report_lines.append(f"  {self.symbols['arrow']} 可以考虑添加更多细节和情感描写")
            elif result['completeness_score'] >= 60:
                report_lines.append(f"  {self.symbols['warning']} 档案基本完整，但还有完善空间")
                report_lines.append(f"  {self.symbols['arrow']} 建议完善 {result['placeholder_count']} 处占位符")
            else:
                report_lines.append(f"  {self.symbols['cross']} 档案还处于草稿阶段")
                report_lines.append(f"  {self.symbols['arrow']} 需要补充大量内容，建议逐个章节完善")

            report_lines.append("")
            report_lines.append("=" * 60)

            return "\n".join(report_lines)

        elif output_format == 'json':
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def analyze_directory(self, directory_path, recursive=True):
        """分析目录下的所有markdown档案"""
        directory = Path(directory_path)

        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory_path}")

        # 查找markdown文件
        md_files = []
        if recursive:
            md_files = list(directory.rglob("*.md"))
        else:
            md_files = list(directory.glob("*.md"))

        if not md_files:
            return {"message": "未找到markdown文件", "files": []}

        # 分析每个文件
        results = []
        for md_file in md_files:
            try:
                analysis = self.analyze_markdown(str(md_file))
                results.append(analysis)
            except Exception as e:
                results.append({
                    'filepath': str(md_file),
                    'error': str(e)
                })

        # 按完整性评分排序
        valid_results = [r for r in results if 'completeness_score' in r]
        sorted_results = sorted(valid_results, key=lambda x: x['completeness_score'], reverse=True)

        return {
            'total_files': len(md_files),
            'successful_analysis': len(valid_results),
            'failed_analysis': len(results) - len(valid_results),
            'results': sorted_results
        }

    def generate_directory_report(self, analysis_results, output_format='text'):
        """生成目录分析报告"""
        if output_format == 'text':
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append(f"人物档案目录分析报告")
            report_lines.append(f"分析文件数: {analysis_results['total_files']}")
            report_lines.append(f"成功分析: {analysis_results['successful_analysis']}")
            if analysis_results['failed_analysis'] > 0:
                report_lines.append(f"分析失败: {analysis_results['failed_analysis']}")
            report_lines.append("=" * 60)
            report_lines.append("")

            # 文件列表（按评分排序）
            if analysis_results['results']:
                report_lines.append(f"{self.symbols['file']} 文件完整性排名")
                for i, result in enumerate(analysis_results['results'], 1):
                    score = result['completeness_score']
                    level = result['completeness_level']
                    filename = os.path.basename(result['filepath'])

                    # 使用符号表示等级
                    if score >= 80:
                        icon = self.symbols['green_circle']
                    elif score >= 60:
                        icon = self.symbols['yellow_circle']
                    else:
                        icon = self.symbols['red_circle']

                    report_lines.append(f"{icon} {i:2d}. {filename:<40} {score:5.1f}分 ({level})")

                report_lines.append("")

                # 统计信息
                avg_score = sum(r['completeness_score'] for r in analysis_results['results']) / len(analysis_results['results'])
                max_score = max(r['completeness_score'] for r in analysis_results['results'])
                min_score = min(r['completeness_score'] for r in analysis_results['results'])

                report_lines.append(f"{self.symbols['chart']} 统计信息")
                report_lines.append(f"  平均分: {avg_score:.1f}")
                report_lines.append(f"  最高分: {max_score:.1f}")
                report_lines.append(f"  最低分: {min_score:.1f}")
                report_lines.append("")

                # 建议
                report_lines.append(f"{self.symbols['bulb']} 整体建议")
                if avg_score >= 75:
                    report_lines.append(f"  {self.symbols['check']} 整体完成度良好")
                    report_lines.append(f"  {self.symbols['arrow']} 可以考虑开始故事创作")
                elif avg_score >= 50:
                    report_lines.append(f"  {self.symbols['warning']} 整体完成度一般")
                    report_lines.append(f"  {self.symbols['arrow']} 建议继续完善人物档案")
                else:
                    report_lines.append(f"  {self.symbols['cross']} 整体完成度较低")
                    report_lines.append(f"  {self.symbols['arrow']} 需要重点完善主要角色的档案")

            report_lines.append("")
            report_lines.append("=" * 60)

            return "\n".join(report_lines)

        else:
            import json
            return json.dumps(analysis_results, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='分析人物档案markdown文件')
    parser.add_argument('path', help='要分析的markdown文件或目录路径')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归分析目录')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')

    args = parser.parse_args()

    analyzer = ProfileAnalyzer()
    path = Path(args.path)

    try:
        if path.is_file():
            # 分析单个文件
            if path.suffix.lower() != '.md':
                print("错误: 文件必须是.md格式")
                return 1

            analysis = analyzer.analyze_markdown(str(path))
            report = analyzer.generate_report(analysis, args.format)

        elif path.is_dir():
            # 分析目录
            analysis_results = analyzer.analyze_directory(str(path), args.recursive)
            report = analyzer.generate_directory_report(analysis_results, args.format)

        else:
            print(f"错误: 路径不存在: {args.path}")
            return 1

        # 输出结果
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"报告已保存到: {args.output}")
        else:
            print(report)

        return 0

    except Exception as e:
        print(f"分析失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())