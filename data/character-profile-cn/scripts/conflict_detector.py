#!/usr/bin/env python3
"""
冲突检测和常识校验模块
检测角色冲突和常识错误
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set, Any
from pathlib import Path
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ConflictSeverity(Enum):
    """冲突严重程度"""
    INFO = "info"       # 信息提示
    WARNING = "warning" # 警告
    ERROR = "error"     # 错误


class ConflictType(Enum):
    """冲突类型"""
    DUPLICATE_NAME = "duplicate_name"           # 重复姓名
    SIMILAR_CHARACTER = "similar_character"     # 相似角色
    TIMELINE_CONFLICT = "timeline_conflict"     # 时间线冲突
    RELATIONSHIP_CONFLICT = "relationship_conflict"  # 关系冲突
    AGE_INCONSISTENCY = "age_inconsistency"     # 年龄不一致
    COMMON_SENSE_ERROR = "common_sense_error"   # 常识错误
    LOGIC_CONFLICT = "logic_conflict"          # 逻辑冲突


@dataclass
class Conflict:
    """冲突信息"""
    type: ConflictType
    severity: ConflictSeverity
    message: str
    character_name: str
    details: Dict[str, Any] = field(default_factory=dict)
    related_characters: List[str] = field(default_factory=list)
    suggested_fixes: List[str] = field(default_factory=list)


@dataclass
class ValidationRule:
    """校验规则"""
    id: str
    name: str
    description: str
    pattern: Optional[str] = None
    condition: Optional[str] = None
    severity: ConflictSeverity = ConflictSeverity.WARNING
    enabled: bool = True
    category: str = "common_sense"


class ConflictDetector:
    """冲突检测器"""

    # 预定义常识规则
    DEFAULT_COMMON_SENSE_RULES = [
        ValidationRule(
            id="age_realistic",
            name="年龄合理性",
            description="检查年龄是否在合理范围内（0-150岁）",
            condition="age.isdigit() and not (0 <= int(age) <= 150)",
            severity=ConflictSeverity.WARNING,
            category="common_sense"
        ),
        ValidationRule(
            id="age_format",
            name="年龄格式",
            description="年龄应为数字或数字范围",
            pattern=r"^\d+(\s*-\s*\d+)?$",
            severity=ConflictSeverity.INFO,
            category="common_sense"
        ),
        ValidationRule(
            id="timeline_consistency",
            name="时间线一致性",
            description="检查关键事件时间线是否合理",
            condition="'background' in character and 'timeline_events' in character",
            severity=ConflictSeverity.WARNING,
            category="timeline"
        ),
        ValidationRule(
            id="relationship_consistency",
            name="关系一致性",
            description="检查角色关系是否相互一致",
            condition="'relationships' in character",
            severity=ConflictSeverity.WARNING,
            category="relationships"
        ),
        ValidationRule(
            id="duplicate_detection",
            name="重复检测",
            description="检测是否有重复角色",
            condition="True",  # 始终启用
            severity=ConflictSeverity.ERROR,
            category="duplicate"
        )
    ]

    def __init__(self, rules_file: Optional[str] = None):
        """初始化冲突检测器

        Args:
            rules_file: 规则配置文件路径
        """
        self.rules = self._load_rules(rules_file)
        self.character_index = {}  # 角色信息索引

    def _load_rules(self, rules_file: Optional[str]) -> List[ValidationRule]:
        """加载校验规则

        Args:
            rules_file: 规则文件路径

        Returns:
            规则列表
        """
        rules = []

        # 先加载默认规则
        rules.extend(self.DEFAULT_COMMON_SENSE_RULES)

        # 如果指定了规则文件，从文件加载
        if rules_file and Path(rules_file).exists():
            try:
                with open(rules_file, 'r', encoding='utf-8') as f:
                    rule_data = json.load(f)

                for rule_item in rule_data.get("rules", []):
                    rule = ValidationRule(
                        id=rule_item.get("id"),
                        name=rule_item.get("name"),
                        description=rule_item.get("description"),
                        pattern=rule_item.get("pattern"),
                        condition=rule_item.get("condition"),
                        severity=ConflictSeverity(rule_item.get("severity", "warning")),
                        enabled=rule_item.get("enabled", True),
                        category=rule_item.get("category", "common_sense")
                    )
                    rules.append(rule)

                logger.info(f"从文件加载了 {len(rule_data.get('rules', []))} 条规则")
            except Exception as e:
                logger.error(f"加载规则文件失败: {e}")

        return rules

    def set_character_index(self, character_index: Dict):
        """设置角色信息索引

        Args:
            character_index: 角色索引字典
        """
        self.character_index = character_index

    def detect_conflicts(self, new_character: Dict, existing_characters: List[Dict] = None) -> List[Conflict]:
        """检测新角色与现有角色的冲突

        Args:
            new_character: 新角色信息
            existing_characters: 现有角色列表，为None时使用character_index

        Returns:
            冲突列表
        """
        conflicts = []

        # 获取现有角色
        if existing_characters is None:
            existing_characters = self.character_index.get("characters", [])

        # 1. 检测重复姓名
        duplicate_conflicts = self._detect_duplicate_names(new_character, existing_characters)
        conflicts.extend(duplicate_conflicts)

        # 2. 检测相似角色
        similar_conflicts = self._detect_similar_characters(new_character, existing_characters)
        conflicts.extend(similar_conflicts)

        # 3. 检测常识错误
        common_sense_conflicts = self._check_common_sense(new_character)
        conflicts.extend(common_sense_conflicts)

        # 4. 检测时间线冲突
        timeline_conflicts = self._detect_timeline_conflicts(new_character, existing_characters)
        conflicts.extend(timeline_conflicts)

        # 5. 检测关系冲突
        relationship_conflicts = self._detect_relationship_conflicts(new_character, existing_characters)
        conflicts.extend(relationship_conflicts)

        return conflicts

    def _detect_duplicate_names(self, new_char: Dict, existing_chars: List[Dict]) -> List[Conflict]:
        """检测重复姓名

        Args:
            new_char: 新角色
            existing_chars: 现有角色

        Returns:
            冲突列表
        """
        conflicts = []
        new_name = new_char.get("name", "").strip().lower()

        if not new_name:
            return conflicts

        for existing_char in existing_chars:
            existing_name = existing_char.get("name", "").strip().lower()

            if existing_name and existing_name == new_name:
                conflict = Conflict(
                    type=ConflictType.DUPLICATE_NAME,
                    severity=ConflictSeverity.ERROR,
                    message=f"角色姓名重复: '{new_char.get('name')}' 已存在",
                    character_name=new_char.get("name", "未知"),
                    details={
                        "new_character": new_char.get("name"),
                        "existing_character": existing_char.get("name"),
                        "existing_file": existing_char.get("file_path", "")
                    },
                    related_characters=[existing_char.get("name", "未知")],
                    suggested_fixes=[
                        f"修改新角色姓名为 '{new_char.get('name')}_新'",
                        f"合并两个角色的设定",
                        f"删除或重命名现有角色"
                    ]
                )
                conflicts.append(conflict)

        return conflicts

    def _detect_similar_characters(self, new_char: Dict, existing_chars: List[Dict]) -> List[Conflict]:
        """检测相似角色

        Args:
            new_char: 新角色
            existing_chars: 现有角色

        Returns:
            冲突列表
        """
        conflicts = []
        new_name = new_char.get("name", "").lower()

        if not new_name:
            return conflicts

        # 相似度检测阈值
        similarity_threshold = 0.7

        for existing_char in existing_chars:
            existing_name = existing_char.get("name", "").lower()

            # 计算姓名相似度
            similarity = self._calculate_name_similarity(new_name, existing_name)

            if similarity > similarity_threshold:
                conflict = Conflict(
                    type=ConflictType.SIMILAR_CHARACTER,
                    severity=ConflictSeverity.WARNING,
                    message=f"角色姓名相似: '{new_char.get('name')}' 与 '{existing_char.get('name')}' 相似度较高",
                    character_name=new_char.get("name", "未知"),
                    details={
                        "new_character": new_char.get("name"),
                        "existing_character": existing_char.get("name"),
                        "similarity_score": similarity,
                        "existing_file": existing_char.get("file_path", "")
                    },
                    related_characters=[existing_char.get("name", "未知")],
                    suggested_fixes=[
                        f"确认是否为不同角色",
                        f"修改其中一个角色的姓名以增加区分度",
                        f"检查角色设定是否重复"
                    ]
                )
                conflicts.append(conflict)

            # 检查其他相似特征
            similarity_features = self._check_feature_similarity(new_char, existing_char)
            if similarity_features:
                conflict = Conflict(
                    type=ConflictType.SIMILAR_CHARACTER,
                    severity=ConflictSeverity.INFO,
                    message=f"角色特征相似: '{new_char.get('name')}' 与 '{existing_char.get('name')}' 有相似特征",
                    character_name=new_char.get("name", "未知"),
                    details={
                        "new_character": new_char.get("name"),
                        "existing_character": existing_char.get("name"),
                        "similar_features": similarity_features,
                        "existing_file": existing_char.get("file_path", "")
                    },
                    related_characters=[existing_char.get("name", "未知")],
                    suggested_fixes=[
                        f"区分角色特征",
                        f"强化角色独特性",
                        f"考虑角色合并"
                    ]
                )
                conflicts.append(conflict)

        return conflicts

    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """计算姓名相似度

        Args:
            name1: 姓名1
            name2: 姓名2

        Returns:
            相似度得分 (0-1)
        """
        if not name1 or not name2:
            return 0.0

        # 简单的相似度计算：共同字符比例
        set1 = set(name1.replace(' ', ''))
        set2 = set(name2.replace(' ', ''))

        if not set1 or not set2:
            return 0.0

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0.0

    def _check_feature_similarity(self, char1: Dict, char2: Dict) -> List[str]:
        """检查特征相似性

        Args:
            char1: 角色1
            char2: 角色2

        Returns:
            相似特征列表
        """
        similar_features = []

        # 检查年龄
        age1 = char1.get("age", "")
        age2 = char2.get("age", "")
        if age1 and age2 and age1 == age2:
            similar_features.append(f"年龄相同: {age1}")

        # 检查职业
        occupation1 = char1.get("occupation", "")
        occupation2 = char2.get("occupation", "")
        if occupation1 and occupation2 and occupation1.lower() == occupation2.lower():
            similar_features.append(f"职业相同: {occupation1}")

        # 检查角色类型
        type1 = char1.get("character_type", "")
        type2 = char2.get("character_type", "")
        if type1 and type2 and type1.lower() == type2.lower():
            similar_features.append(f"角色类型相同: {type1}")

        return similar_features

    def _check_common_sense(self, character: Dict) -> List[Conflict]:
        """检查常识错误

        Args:
            character: 角色信息

        Returns:
            冲突列表
        """
        conflicts = []

        for rule in self.rules:
            if not rule.enabled or rule.category != "common_sense":
                continue

            # 根据规则类型进行检查
            if rule.pattern:
                # 模式匹配规则
                for field_name, field_value in character.items():
                    if isinstance(field_value, str):
                        if not re.match(rule.pattern, field_value):
                            conflict = Conflict(
                                type=ConflictType.COMMON_SENSE_ERROR,
                                severity=rule.severity,
                                message=f"{rule.name}: {field_name} '{field_value}' 不符合格式要求",
                                character_name=character.get("name", "未知"),
                                details={
                                    "rule_id": rule.id,
                                    "rule_name": rule.name,
                                    "field": field_name,
                                    "value": field_value,
                                    "expected_pattern": rule.pattern
                                },
                                suggested_fixes=[
                                    f"修改 {field_name} 为符合格式: {rule.pattern}",
                                    f"检查 {field_name} 是否正确"
                                ]
                            )
                            conflicts.append(conflict)

            elif rule.condition:
                # 条件规则（简化实现）
                try:
                    # 这里实现简化的条件检查
                    if rule.id == "age_realistic":
                        age_str = character.get("age", "")
                        if age_str.isdigit():
                            age = int(age_str)
                            if not (0 <= age <= 150):
                                conflict = Conflict(
                                    type=ConflictType.COMMON_SENSE_ERROR,
                                    severity=rule.severity,
                                    message=f"{rule.name}: 年龄 {age} 不在合理范围 (0-150)",
                                    character_name=character.get("name", "未知"),
                                    details={
                                        "rule_id": rule.id,
                                        "rule_name": rule.name,
                                        "field": "age",
                                        "value": age,
                                        "expected_range": "0-150"
                                    },
                                    suggested_fixes=[
                                        "调整年龄到合理范围",
                                        "如果是特殊设定（如非人类），请明确说明"
                                    ]
                                )
                                conflicts.append(conflict)
                except Exception as e:
                    logger.debug(f"规则检查失败 {rule.id}: {e}")

        return conflicts

    def _detect_timeline_conflicts(self, new_char: Dict, existing_chars: List[Dict]) -> List[Conflict]:
        """检测时间线冲突

        Args:
            new_char: 新角色
            existing_chars: 现有角色

        Returns:
            冲突列表
        """
        conflicts = []
        # 这里实现时间线冲突检测逻辑
        # 需要从角色信息中提取时间线事件
        return conflicts

    def _detect_relationship_conflicts(self, new_char: Dict, existing_chars: List[Dict]) -> List[Conflict]:
        """检测关系冲突

        Args:
            new_char: 新角色
            existing_chars: 现有角色

        Returns:
            冲突列表
        """
        conflicts = []
        # 这里实现关系冲突检测逻辑
        # 需要从角色信息中提取关系信息
        return conflicts

    def validate_character(self, character: Dict) -> Tuple[bool, List[Conflict]]:
        """验证单个角色

        Args:
            character: 角色信息

        Returns:
            (是否有效, 冲突列表)
        """
        conflicts = self.detect_conflicts(character)
        is_valid = all(conflict.severity != ConflictSeverity.ERROR for conflict in conflicts)

        return is_valid, conflicts

    def generate_report(self, conflicts: List[Conflict], output_format: str = "text") -> str:
        """生成冲突报告

        Args:
            conflicts: 冲突列表
            output_format: 输出格式，支持 'text', 'json', 'markdown'

        Returns:
            报告字符串
        """
        if output_format == "json":
            report_data = []
            for conflict in conflicts:
                report_data.append({
                    "type": conflict.type.value,
                    "severity": conflict.severity.value,
                    "message": conflict.message,
                    "character_name": conflict.character_name,
                    "details": conflict.details,
                    "related_characters": conflict.related_characters,
                    "suggested_fixes": conflict.suggested_fixes
                })
            return json.dumps(report_data, ensure_ascii=False, indent=2)

        elif output_format == "markdown":
            report_lines = ["# 冲突检测报告", ""]

            # 按严重程度分组
            errors = [c for c in conflicts if c.severity == ConflictSeverity.ERROR]
            warnings = [c for c in conflicts if c.severity == ConflictSeverity.WARNING]
            infos = [c for c in conflicts if c.severity == ConflictSeverity.INFO]

            if errors:
                report_lines.append("## ❌ 错误")
                for conflict in errors:
                    report_lines.append(f"### {conflict.message}")
                    report_lines.append(f"- **角色**: {conflict.character_name}")
                    report_lines.append(f"- **类型**: {conflict.type.value}")
                    if conflict.related_characters:
                        report_lines.append(f"- **相关角色**: {', '.join(conflict.related_characters)}")
                    if conflict.suggested_fixes:
                        report_lines.append(f"- **建议**:")
                        for fix in conflict.suggested_fixes:
                            report_lines.append(f"  - {fix}")
                    report_lines.append("")

            if warnings:
                report_lines.append("## ⚠️ 警告")
                for conflict in warnings:
                    report_lines.append(f"### {conflict.message}")
                    report_lines.append(f"- **角色**: {conflict.character_name}")
                    report_lines.append(f"- **类型**: {conflict.type.value}")
                    if conflict.suggested_fixes:
                        report_lines.append(f"- **建议**: {conflict.suggested_fixes[0]}")
                    report_lines.append("")

            if infos:
                report_lines.append("## ℹ️ 提示")
                for conflict in infos:
                    report_lines.append(f"- {conflict.message}")
                report_lines.append("")

            return "\n".join(report_lines)

        else:  # text格式
            report_lines = ["冲突检测报告", "=" * 40, ""]

            # 统计
            error_count = len([c for c in conflicts if c.severity == ConflictSeverity.ERROR])
            warning_count = len([c for c in conflicts if c.severity == ConflictSeverity.WARNING])
            info_count = len([c for c in conflicts if c.severity == ConflictSeverity.INFO])

            report_lines.append(f"发现 {error_count} 个错误, {warning_count} 个警告, {info_count} 个提示")
            report_lines.append("")

            # 按角色分组显示
            characters_conflicts = {}
            for conflict in conflicts:
                char_name = conflict.character_name
                if char_name not in characters_conflicts:
                    characters_conflicts[char_name] = []
                characters_conflicts[char_name].append(conflict)

            for char_name, char_conflicts in characters_conflicts.items():
                report_lines.append(f"角色: {char_name}")
                report_lines.append("-" * 30)

                for conflict in char_conflicts:
                    severity_icon = {
                        ConflictSeverity.ERROR: "[错误]",
                        ConflictSeverity.WARNING: "[警告]",
                        ConflictSeverity.INFO: "[提示]"
                    }.get(conflict.severity, "[未知]")

                    report_lines.append(f"{severity_icon} {conflict.message}")

                    if conflict.related_characters:
                        report_lines.append(f"  相关角色: {', '.join(conflict.related_characters)}")

                    if conflict.suggested_fixes:
                        report_lines.append(f"  建议: {conflict.suggested_fixes[0]}")

                report_lines.append("")

            return "\n".join(report_lines)


def main():
    """命令行测试"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python conflict_detector.py <新角色JSON文件> [现有角色目录]")
        sys.exit(1)

    # 加载新角色信息
    new_char_file = sys.argv[1]
    try:
        with open(new_char_file, 'r', encoding='utf-8') as f:
            new_character = json.load(f)
    except Exception as e:
        print(f"加载新角色文件失败: {e}")
        sys.exit(1)

    # 创建检测器
    detector = ConflictDetector()

    # 如果有现有角色目录，扫描现有角色
    existing_characters = []
    if len(sys.argv) > 2:
        from lore_bible_manager import LoreBibleManager
        try:
            manager = LoreBibleManager(sys.argv[2])
            existing_characters = manager.scan_existing_characters()
            print(f"扫描到 {len(existing_characters)} 个现有角色")
        except Exception as e:
            print(f"扫描现有角色失败: {e}")

    # 设置角色索引
    if existing_characters:
        detector.set_character_index({
            "characters": existing_characters,
            "total_count": len(existing_characters)
        })

    # 检测冲突
    conflicts = detector.detect_conflicts(new_character, existing_characters)

    # 生成报告
    report = detector.generate_report(conflicts, "text")
    print(report)

    # 检查是否有效
    is_valid, _ = detector.validate_character(new_character)
    if is_valid:
        print("\n✓ 角色设定基本有效")
    else:
        print("\n✗ 角色设定存在错误")


if __name__ == "__main__":
    main()