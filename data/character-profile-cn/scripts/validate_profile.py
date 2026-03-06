#!/usr/bin/env python3
"""
人物档案验证脚本
验证markdown格式的人物档案结构完整性
"""

import os
import re
import sys
from pathlib import Path

class ProfileValidator:
    """人物档案验证器"""

    # 各类型角色的必需章节
    REQUIRED_SECTIONS = {
        'protagonist': [
            '基本信息', '外貌特征', '性格特点', '背景故事',
            '动机层次', '人物关系', '故事发展'
        ],
        'antagonist': [
            '基本信息', '外貌特征', '性格特点', '核心理念',
            '动机发展', '镜像对比', '资源能力', '故事发展'
        ],
        'supporting': [
            '基本定位', '独立身份', '功能性设计', '关系发展',
            '发展可能性'
        ],
        'standard': [
            '基本信息', '外貌特征', '性格特点', '背景故事',
            '人物关系', '故事发展'
        ]
    }

    # 章节内的必需字段（根据模板）
    REQUIRED_FIELDS = {
        '基本信息': ['姓名', '年龄', '性别', '职业/身份', '故事中的角色'],
        '外貌特征': ['整体印象', '面部特征', '身材体型', '着装风格'],
        '性格特点': ['核心性格', '优点', '缺点', '价值观'],
        '背景故事': ['出身背景', '关键经历', '转折点'],
        '人物关系': ['与主角关系', '重要关系人'],
        '故事发展': ['角色目标', '内在冲突', '外在冲突', '发展弧线']
    }

    def __init__(self, profile_type='auto'):
        """初始化验证器

        Args:
            profile_type: 档案类型，可选值: 'protagonist', 'antagonist', 'supporting', 'standard', 'auto'
        """
        self.profile_type = profile_type

        # 检测平台，Windows上使用简单符号
        self.is_windows = sys.platform.startswith('win')

        # 符号定义
        if self.is_windows:
            self.symbols = {
                'building': '[结构]',
                'cross_mark': '[缺失]',
                'warning': '[注意]',
                'check': '[通过]',
                'wrench': '[修复]',
                'check_mark': '[OK]',
                'arrow': '->',
                'green_circle': '[良好]',
                'yellow_circle': '[一般]',
                'red_circle': '[需改进]',
                'file': '[文件]',
                'chart': '[统计]',
                'chart2': '[分布]',
                'bulb': '[建议]',
                'bullet': '-',
                'dash': '-'
            }
        else:
            self.symbols = {
                'building': '🏗️',
                'cross_mark': '❌',
                'warning': '⚠️',
                'check': '✅',
                'wrench': '🔧',
                'check_mark': '✓',
                'arrow': '→',
                'green_circle': '🟢',
                'yellow_circle': '🟡',
                'red_circle': '🔴',
                'file': '📋',
                'chart': '📊',
                'chart2': '📈',
                'bulb': '💡',
                'bullet': '•',
                'dash': '-'
            }

    def detect_profile_type(self, content):
        """检测档案类型"""
        # 通过内容特征检测类型
        lines = content.split('\n')

        # 检查是否有特定章节
        has_mirror = any('镜像对比' in line for line in lines)
        has_core_belief = any('核心理念' in line for line in lines)
        has_resources = any('资源能力' in line for line in lines)

        has_function = any('功能性设计' in line for line in lines)
        has_identity = any('独立身份' in line for line in lines)

        has_motivation = any('动机层次' in line for line in lines)
        has_core_identity = any('核心身份' in line for line in lines)

        if has_mirror or has_core_belief or has_resources:
            return 'antagonist'
        elif has_function or has_identity:
            return 'supporting'
        elif has_motivation or has_core_identity:
            return 'protagonist'
        else:
            return 'standard'

    def validate_structure(self, filepath):
        """验证档案结构

        Args:
            filepath: markdown文件路径

        Returns:
            验证结果字典
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检测类型
        if self.profile_type == 'auto':
            detected_type = self.detect_profile_type(content)
        else:
            detected_type = self.profile_type

        # 提取所有章节标题
        sections = self._extract_sections(content)

        # 检查必需章节
        required_sections = self.REQUIRED_SECTIONS.get(detected_type, [])
        missing_sections = []
        present_sections = []

        for required_section in required_sections:
            if required_section not in sections:
                missing_sections.append(required_section)
            else:
                present_sections.append(required_section)

        # 检查章节内的必需字段
        section_field_violations = {}
        for section_title in present_sections:
            section_content = self._get_section_content(content, section_title)
            missing_fields = self._check_required_fields(section_title, section_content)

            if missing_fields:
                section_field_violations[section_title] = missing_fields

        # 计算结构完整性评分
        structure_score = self._calculate_structure_score(
            len(required_sections), len(missing_sections), section_field_violations
        )

        return {
            'filepath': filepath,
            'detected_type': detected_type,
            'total_sections_found': len(sections),
            'required_sections': required_sections,
            'present_sections': present_sections,
            'missing_sections': missing_sections,
            'section_field_violations': section_field_violations,
            'structure_score': structure_score,
            'structure_level': self._get_structure_level(structure_score)
        }

    def _extract_sections(self, content):
        """提取所有章节标题"""
        sections = []

        # 匹配二级和三级标题（## 和 ###）
        header_pattern = r'^#{2,3}\s+(.+?)$'

        lines = content.split('\n')
        for line in lines:
            match = re.match(header_pattern, line.strip())
            if match:
                title = match.group(1).strip()
                # 去掉可能的内部链接
                title = re.sub(r'\[.*?\]\(.*?\)', '', title)
                sections.append(title)

        return sections

    def _get_section_content(self, content, section_title):
        """获取指定章节的内容"""
        lines = content.split('\n')
        in_target_section = False
        section_content = []

        for line in lines:
            # 检查是否是章节标题
            if re.match(rf'^#{{2,3}}\s+{re.escape(section_title)}\s*$', line.strip()):
                in_target_section = True
                continue

            # 如果进入下一个章节，停止收集
            if in_target_section and re.match(r'^#{2,3}\s+', line.strip()):
                break

            # 收集内容行
            if in_target_section:
                section_content.append(line)

        return '\n'.join(section_content)

    def _check_required_fields(self, section_title, section_content):
        """检查章节内的必需字段"""
        required_fields = self.REQUIRED_FIELDS.get(section_title, [])
        if not required_fields:
            return []

        missing_fields = []

        for field in required_fields:
            # 检查字段是否出现（作为粗体文本）
            pattern = rf'\*\*{re.escape(field)}\*\*'
            if not re.search(pattern, section_content):
                missing_fields.append(field)

        return missing_fields

    def _calculate_structure_score(self, total_required, missing_sections_count, field_violations):
        """计算结构完整性评分（0-100）"""
        if total_required == 0:
            return 100

        # 章节完整性（70分）
        section_score = ((total_required - missing_sections_count) / total_required) * 70

        # 字段完整性（30分）
        field_score = 30
        if field_violations:
            total_violations = sum(len(fields) for fields in field_violations.values())
            # 每个缺失字段扣3分
            field_penalty = min(30, total_violations * 3)
            field_score -= field_penalty

        total_score = section_score + field_score
        return max(0, min(100, total_score))

    def _get_structure_level(self, score):
        """获取结构完整性等级"""
        if score >= 90:
            return "优秀"
        elif score >= 75:
            return "良好"
        elif score >= 60:
            return "一般"
        elif score >= 40:
            return "不完整"
        else:
            return "结构缺失"

    def generate_validation_report(self, validation_result, output_format='text'):
        """生成验证报告"""
        result = validation_result

        if output_format == 'text':
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append(f"人物档案结构验证报告")
            report_lines.append(f"文件: {result['filepath']}")
            report_lines.append(f"检测类型: {result['detected_type']}")
            report_lines.append("=" * 60)
            report_lines.append("")

            # 结构完整性
            report_lines.append(f"{self.symbols['building']} 结构完整性")
            report_lines.append(f"  评分: {result['structure_score']:.1f}/100")
            report_lines.append(f"  等级: {result['structure_level']}")
            report_lines.append(f"  发现章节: {result['total_sections_found']}")
            report_lines.append("")

            # 章节检查
            if result['missing_sections']:
                report_lines.append(f"{self.symbols['cross_mark']} 缺失的必需章节")
                for section in result['missing_sections']:
                    report_lines.append(f"  {self.symbols['bullet']} {section}")
                report_lines.append("")

            # 字段检查
            if result['section_field_violations']:
                report_lines.append(f"{self.symbols['warning']} 章节内缺失字段")
                for section, fields in result['section_field_violations'].items():
                    report_lines.append(f"  {self.symbols['bullet']} {section}:")
                    for field in fields:
                        report_lines.append(f"      {self.symbols['dash']} {field}")
                report_lines.append("")

            # 通过检查的项目
            report_lines.append(f"{self.symbols['check']} 通过的检查")
            report_lines.append(f"  {self.symbols['bullet']} 必需章节: {len(result['present_sections'])}/{len(result['required_sections'])}")

            present_field_count = 0
            total_field_count = 0
            for section in result['present_sections']:
                required_fields = self.REQUIRED_FIELDS.get(section, [])
                total_field_count += len(required_fields)
                if section not in result['section_field_violations']:
                    present_field_count += len(required_fields)
                else:
                    missing_count = len(result['section_field_violations'][section])
                    present_field_count += (len(required_fields) - missing_count)

            if total_field_count > 0:
                report_lines.append(f"  {self.symbols['bullet']} 必需字段: {present_field_count}/{total_field_count}")

            report_lines.append("")

            # 修复建议
            report_lines.append(f"{self.symbols['wrench']} 修复建议")
            if result['structure_score'] >= 80:
                report_lines.append(f"  {self.symbols['check_mark']} 结构完整，可以继续完善内容细节")
            elif result['structure_score'] >= 60:
                if result['missing_sections']:
                    report_lines.append(f"  {self.symbols['arrow']} 添加缺失的章节: {', '.join(result['missing_sections'][:3])}")
                if result['section_field_violations']:
                    first_section = list(result['section_field_violations'].keys())[0]
                    first_field = result['section_field_violations'][first_section][0]
                    report_lines.append(f"  {self.symbols['arrow']} 补充字段: {first_section} → **{first_field}**")
            else:
                report_lines.append(f"  {self.symbols['arrow']} 需要补充基本的结构框架")
                report_lines.append(f"  {self.symbols['arrow']} 建议使用'{result['detected_type']}'模板重新整理")

            report_lines.append("")
            report_lines.append("=" * 60)

            return "\n".join(report_lines)

        elif output_format == 'json':
            import json
            return json.dumps(result, ensure_ascii=False, indent=2)

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    def validate_directory(self, directory_path, recursive=True):
        """验证目录下的所有markdown档案"""
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

        # 验证每个文件
        results = []
        for md_file in md_files:
            try:
                validation = self.validate_structure(str(md_file))
                results.append(validation)
            except Exception as e:
                results.append({
                    'filepath': str(md_file),
                    'error': str(e)
                })

        # 按结构评分排序
        valid_results = [r for r in results if 'structure_score' in r]
        sorted_results = sorted(valid_results, key=lambda x: x['structure_score'], reverse=True)

        return {
            'total_files': len(md_files),
            'successful_validation': len(valid_results),
            'failed_validation': len(results) - len(valid_results),
            'results': sorted_results
        }

    def generate_directory_validation_report(self, validation_results, output_format='text'):
        """生成目录验证报告"""
        if output_format == 'text':
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append(f"人物档案结构验证报告（目录）")
            report_lines.append(f"分析文件数: {validation_results['total_files']}")
            report_lines.append(f"成功验证: {validation_results['successful_validation']}")
            if validation_results['failed_validation'] > 0:
                report_lines.append(f"验证失败: {validation_results['failed_validation']}")
            report_lines.append("=" * 60)
            report_lines.append("")

            # 文件列表（按评分排序）
            if validation_results['results']:
                report_lines.append(f"{self.symbols['file']} 文件结构完整性排名")
                for i, result in enumerate(validation_results['results'], 1):
                    score = result['structure_score']
                    level = result['structure_level']
                    filename = os.path.basename(result['filepath'])
                    profile_type = result.get('detected_type', '未知')

                    # 使用符号表示等级
                    if score >= 80:
                        icon = self.symbols['green_circle']
                    elif score >= 60:
                        icon = self.symbols['yellow_circle']
                    else:
                        icon = self.symbols['red_circle']

                    report_lines.append(f"{icon} {i:2d}. {filename:<35} {score:5.1f}分 ({level}, {profile_type})")

                report_lines.append("")

                # 统计信息
                avg_score = sum(r['structure_score'] for r in validation_results['results']) / len(validation_results['results'])
                max_score = max(r['structure_score'] for r in validation_results['results'])
                min_score = min(r['structure_score'] for r in validation_results['results'])

                # 类型分布
                type_distribution = {}
                for result in validation_results['results']:
                    profile_type = result.get('detected_type', '未知')
                    type_distribution[profile_type] = type_distribution.get(profile_type, 0) + 1

                report_lines.append(f"{self.symbols['chart']} 统计信息")
                report_lines.append(f"  平均结构分: {avg_score:.1f}")
                report_lines.append(f"  最高分: {max_score:.1f}")
                report_lines.append(f"  最低分: {min_score:.1f}")
                report_lines.append("")

                report_lines.append(f"{self.symbols['chart2']} 类型分布")
                for profile_type, count in type_distribution.items():
                    percentage = (count / len(validation_results['results'])) * 100
                    report_lines.append(f"  {profile_type}: {count}个 ({percentage:.1f}%)")

                report_lines.append("")

                # 整体建议
                report_lines.append(f"{self.symbols['bulb']} 整体建议")
                if avg_score >= 75:
                    report_lines.append(f"  {self.symbols['check_mark']} 整体结构良好")
                    report_lines.append(f"  {self.symbols['arrow']} 可以开始关注内容深度和细节")
                elif avg_score >= 50:
                    report_lines.append(f"  {self.symbols['warning']} 结构基本完整但有缺失")
                    report_lines.append(f"  {self.symbols['arrow']} 建议补充缺失章节和字段")
                else:
                    report_lines.append(f"  {self.symbols['cross_mark']} 结构完整性不足")
                    report_lines.append(f"  {self.symbols['arrow']} 需要重新整理档案结构框架")

            report_lines.append("")
            report_lines.append("=" * 60)

            return "\n".join(report_lines)

        else:
            import json
            return json.dumps(validation_results, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='验证人物档案markdown文件结构')
    parser.add_argument('path', help='要验证的markdown文件或目录路径')
    parser.add_argument('--type', '-t', choices=['protagonist', 'antagonist', 'supporting', 'standard', 'auto'],
                      default='auto', help='档案类型（默认为自动检测）')
    parser.add_argument('--recursive', '-r', action='store_true', help='递归验证目录')
    parser.add_argument('--format', '-f', choices=['text', 'json'], default='text', help='输出格式')
    parser.add_argument('--output', '-o', help='输出文件路径')

    args = parser.parse_args()

    validator = ProfileValidator(args.type)
    path = Path(args.path)

    try:
        if path.is_file():
            # 验证单个文件
            if path.suffix.lower() != '.md':
                print("错误: 文件必须是.md格式")
                return 1

            validation = validator.validate_structure(str(path))
            report = validator.generate_validation_report(validation, args.format)

        elif path.is_dir():
            # 验证目录
            validation_results = validator.validate_directory(str(path), args.recursive)
            report = validator.generate_directory_validation_report(validation_results, args.format)

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
        print(f"验证失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())