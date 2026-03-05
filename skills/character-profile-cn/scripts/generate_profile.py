#!/usr/bin/env python3
"""
人物档案生成脚本
根据模板生成结构化的人物档案markdown文件
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import logging
from typing import Optional, Dict, List, Tuple

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class CharacterProfileGenerator:
    """人物档案生成器"""

    def __init__(self, template_type="standard", workspace=None):
        """初始化生成器

        Args:
            template_type: 模板类型，可选值: 'protagonist', 'antagonist', 'supporting', 'standard'
            workspace: 工作目录路径，启用LoreBible管理功能
        """
        self.template_type = template_type
        self.templates = self._load_templates()
        self.workspace = workspace
        self.enable_enhanced_features = workspace is not None

        if self.enable_enhanced_features:
            logger.info(f"启用增强功能，工作目录: {workspace}")
            # 延迟导入，避免循环依赖
            self.lore_bible_manager = None
            self.conflict_detector = None
            self.profile_session = None

    def _init_enhanced_components(self):
        """初始化增强组件"""
        if not self.enable_enhanced_features:
            return

        try:
            # 延迟导入
            from lore_bible_manager import LoreBibleManager
            from conflict_detector import ConflictDetector
            from profile_session import ProfileSession, SessionConfig

            # 初始化管理器
            self.lore_bible_manager = LoreBibleManager(self.workspace)

            # 验证并创建目录结构
            is_valid, missing_dirs = self.lore_bible_manager.validate_directory_structure()
            if not is_valid:
                logger.warning(f"目录结构不完整，缺失: {missing_dirs}")
                logger.info("正在创建缺失目录...")
                if self.lore_bible_manager.create_directory_structure():
                    logger.info("目录结构创建成功")
                else:
                    logger.error("创建目录结构失败")

            # 初始化冲突检测器
            self.conflict_detector = ConflictDetector()

            # 配置会话（稍后在generate_markdown中创建）
            self.session_config = SessionConfig(
                workspace=self.workspace,
                character_name="",  # 稍后设置
                template_type=self.template_type,
                enable_validation=True,
                enable_conflict_check=True,
                require_confirmation=True
            )

            logger.info("增强组件初始化完成")

        except ImportError as e:
            logger.error(f"导入增强组件失败: {e}")
            logger.error("请确保lore_bible_manager.py、conflict_detector.py、profile_session.py在脚本目录中")
            self.enable_enhanced_features = False
        except Exception as e:
            logger.error(f"初始化增强组件失败: {e}")
            self.enable_enhanced_features = False

    def _load_templates(self):
        """加载模板配置"""
        templates = {
            "protagonist": {
                "name": "主角模板",
                "sections": [
                    {"id": "basic", "title": "基本信息", "required": True},
                    {"id": "appearance", "title": "外貌特征", "required": True},
                    {"id": "personality", "title": "性格特点", "required": True},
                    {"id": "background", "title": "背景故事", "required": True},
                    {"id": "motivation", "title": "动机层次", "required": True},
                    {"id": "relationships", "title": "人物关系", "required": True},
                    {"id": "development", "title": "故事发展", "required": True},
                    {"id": "core_identity", "title": "核心身份", "required": False},
                    {"id": "notes", "title": "创作笔记", "required": False}
                ]
            },
            "antagonist": {
                "name": "反派模板",
                "sections": [
                    {"id": "basic", "title": "基本信息", "required": True},
                    {"id": "appearance", "title": "外貌特征", "required": True},
                    {"id": "personality", "title": "性格特点", "required": True},
                    {"id": "core_belief", "title": "核心理念", "required": True},
                    {"id": "motivation", "title": "动机发展", "required": True},
                    {"id": "mirror", "title": "镜像对比", "required": True},
                    {"id": "resources", "title": "资源能力", "required": True},
                    {"id": "development", "title": "故事发展", "required": True}
                ]
            },
            "supporting": {
                "name": "配角模板",
                "sections": [
                    {"id": "basic", "title": "基本定位", "required": True},
                    {"id": "identity", "title": "独立身份", "required": True},
                    {"id": "function", "title": "功能性设计", "required": True},
                    {"id": "relationships", "title": "关系发展", "required": True},
                    {"id": "development", "title": "发展可能性", "required": True}
                ]
            },
            "standard": {
                "name": "标准模板",
                "sections": [
                    {"id": "basic", "title": "基本信息", "required": True},
                    {"id": "appearance", "title": "外貌特征", "required": True},
                    {"id": "personality", "title": "性格特点", "required": True},
                    {"id": "background", "title": "背景故事", "required": True},
                    {"id": "relationships", "title": "人物关系", "required": True},
                    {"id": "development", "title": "故事发展", "required": True},
                    {"id": "notes", "title": "创作笔记", "required": False}
                ]
            }
        }
        return templates

    def _get_section_content(self, section_id, character_data):
        """获取章节内容

        Args:
            section_id: 章节ID
            character_data: 角色数据字典

        Returns:
            章节内容字符串
        """
        section_templates = {
            "basic": """- **姓名**：{name}
- **年龄**：{age}
- **性别**：{gender}
- **职业/身份**：{occupation}
- **故事中的角色**：{role}""",

            "appearance": """- **整体印象**：{overall_impression}
- **面部特征**：{facial_features}
- **身材体型**：{body_type}
- **着装风格**：{clothing_style}
- **标志性特征**：{distinctive_features}""",

            "personality": """- **核心性格**：{core_personality}
- **优点**：{strengths}
- **缺点**：{weaknesses}
- **价值观**：{values}
- **恐惧**：{fears}
- **渴望**：{desires}""",

            "background": """- **出身背景**：{origin}
- **关键经历**：{key_experiences}
- **转折点**：{turning_points}
- **未解之谜**：{unsolved_mysteries}""",

            "relationships": """- **与主角关系**：{relationship_with_protagonist}
- **重要关系人**：{important_relationships}
- **敌对关系**：{enemy_relationships}
- **情感羁绊**：{emotional_bonds}""",

            "development": """- **角色目标**：{goals}
- **内在冲突**：{internal_conflicts}
- **外在冲突**：{external_conflicts}
- **发展弧线**：{development_arc}
- **可能的结局**：{possible_endings}""",

            "notes": """- **灵感来源**：{inspiration_sources}
- **象征意义**：{symbolic_meanings}
- **潜在发展**：{potential_developments}""",

            "core_identity": """- **本质自我**：{true_self}
- **社会面具**：{social_mask}
- **理想自我**：{ideal_self}
- **恐惧自我**：{feared_self}""",

            "motivation": """- **表层目标**：{surface_goals}
- **情感需求**：{emotional_needs}
- **存在需求**：{existential_needs}
- **未意识需求**：{unconscious_needs}""",

            "core_belief": """- **世界观**：{worldview}
- **核心信念**：{core_beliefs}
- **正义观**：{justice_view}
- **变革愿景**：{change_vision}""",

            "mirror": """- **相似点**：{similarities}
- **分歧点**：{divergences}
- **对立逻辑**：{opposition_logic}
- **潜在转化**：{potential_transformation}""",

            "resources": """- **核心团队**：{core_team}
- **盟友势力**：{ally_forces}
- **影响范围**：{influence_scope}
- **弱点环节**：{weakness_points}""",

            "function": """- **推动剧情的方式**：{plot_push_methods}
- **服务主角的方式**：{protagonist_service_methods}
- **独特价值**：{unique_value}
- **退出时机**：{exit_timing}"""
        }

        template = section_templates.get(section_id, "")
        if not template:
            return ""

        # 从character_data中获取数据，如果不存在则使用占位符
        content = template
        for key in character_data:
            placeholder = "{" + key + "}"
            if placeholder in content:
                content = content.replace(placeholder, character_data.get(key, f"[待填写{key}]"))

        # 清理未替换的占位符
        import re
        content = re.sub(r'\{[^}]*\}', '[待填写]', content)

        return content

    def generate_markdown(self, character_data, output_path=None):
        """生成markdown档案

        Args:
            character_data: 角色数据字典，必须包含'name'字段
            output_path: 输出文件路径，如果为None则返回字符串

        Returns:
            如果output_path为None，返回markdown字符串；否则写入文件
        """
        if 'name' not in character_data:
            raise ValueError("角色数据必须包含'name'字段")

        template = self.templates.get(self.template_type, self.templates["standard"])

        # 生成markdown内容
        lines = []
        lines.append(f"# {character_data['name']} - 角色档案")
        lines.append("")
        lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"> 模板类型：{template['name']}")
        lines.append("")

        for section in template['sections']:
            section_id = section['id']
            section_title = section['title']

            lines.append(f"## {section_title}")
            lines.append("")

            content = self._get_section_content(section_id, character_data)
            if content:
                lines.append(content)
            else:
                lines.append(f"*{section_title}内容待填写*")

            lines.append("")

        # 添加元数据部分
        lines.append("---")
        lines.append("")
        lines.append("## 档案元数据")
        lines.append("")
        lines.append(f"- **角色类型**：{template['name']}")
        lines.append(f"- **创建时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **状态**：{'草稿' if character_data.get('status') != 'final' else '完成'}")
        lines.append(f"- **版本**：{character_data.get('version', '1.0')}")
        lines.append("")

        markdown_content = "\n".join(lines)

        if output_path:
            # 确保目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            print(f"档案已生成：{output_path}")
            return output_path
        else:
            return markdown_content

    def generate_enhanced_profile(self, character_data, require_confirmation=True):
        """使用增强功能生成角色档案

        Args:
            character_data: 角色数据字典，必须包含'name'字段
            require_confirmation: 是否需要用户确认

        Returns:
            (是否成功, 最终文件路径, 冲突列表)
        """
        if not self.enable_enhanced_features:
            logger.error("增强功能未启用，请指定workspace参数初始化生成器")
            return False, None, []

        if 'name' not in character_data:
            raise ValueError("角色数据必须包含'name'字段")

        # 初始化增强组件
        if self.lore_bible_manager is None:
            self._init_enhanced_components()

        if not self.enable_enhanced_features:
            return False, None, []

        try:
            from profile_session import ProfileSession, SessionConfig

            # 更新会话配置
            self.session_config.character_name = character_data['name']
            self.session_config.require_confirmation = require_confirmation

            # 创建会话
            session = ProfileSession(self.session_config)

            # 生成基础markdown内容
            markdown_content = self.generate_markdown(character_data, output_path=None)

            # 保存临时档案
            temp_path = session.save_temp_profile(markdown_content)
            if not temp_path:
                logger.error("保存临时档案失败")
                return False, None, []

            # 验证和冲突检测
            is_valid, conflicts = session.validate_and_check_conflicts(character_data)

            # 展示给用户
            if require_confirmation:
                user_confirmed = session.present_to_user(conflicts)
                if not user_confirmed:
                    logger.info("用户取消创建")
                    session.cancel()
                    return False, None, conflicts
            else:
                logger.info("跳过用户确认")

            # 确认并移动
            final_path = session.confirm_and_move()
            if not final_path:
                logger.error("移动档案失败")
                return False, None, conflicts

            # 清理会话
            session.cleanup()

            logger.info(f"角色档案创建成功: {final_path}")
            return True, final_path, conflicts

        except Exception as e:
            logger.error(f"增强生成失败: {e}")
            return False, None, []

    def create_from_cli(self):
        """从命令行交互创建"""
        print("=== 人物档案生成器 ===")
        print("")

        # 选择模板
        print("请选择角色类型：")
        print("1. 主角")
        print("2. 反派")
        print("3. 配角")
        print("4. 标准")

        choice = input("请输入选择 (1-4，默认4): ").strip()
        type_map = {"1": "protagonist", "2": "antagonist", "3": "supporting", "4": "standard"}
        template_type = type_map.get(choice, "standard")

        self.template_type = template_type
        print(f"使用模板：{self.templates[template_type]['name']}")
        print("")

        # 收集基本信息
        character_data = {}
        print("请输入角色基本信息：")
        character_data['name'] = input("角色姓名: ").strip() or "未命名角色"
        character_data['age'] = input("年龄: ").strip() or "未知"
        character_data['gender'] = input("性别: ").strip() or "未指定"
        character_data['occupation'] = input("职业/身份: ").strip() or "未指定"
        character_data['role'] = input("故事中的角色: ").strip() or "未指定"

        print("")
        print("其他信息将在生成的档案中以占位符形式出现，请后续编辑完善。")

        # 生成文件名
        safe_name = "".join(c for c in character_data['name'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"character_profile_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        # 选择输出路径
        default_output = os.path.join(os.getcwd(), filename)
        output_path = input(f"输出文件路径 (默认: {default_output}): ").strip() or default_output

        # 生成档案
        try:
            result = self.generate_markdown(character_data, output_path)
            print("")
            print("✓ 人物档案生成成功！")
            print(f"文件位置: {result if isinstance(result, str) else output_path}")
            print("")
            print("下一步：")
            print("1. 使用文本编辑器打开生成的markdown文件")
            print("2. 根据模板提示填写详细信息")
            print("3. 保存并用于创作参考")

        except Exception as e:
            print(f"生成失败: {e}")
            return 1

        return 0


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 命令行参数模式
        import argparse

        parser = argparse.ArgumentParser(description='生成人物档案markdown文件')
        parser.add_argument('--type', '-t', choices=['protagonist', 'antagonist', 'supporting', 'standard'],
                          default='standard', help='角色类型')
        parser.add_argument('--name', '-n', required=True, help='角色姓名')
        parser.add_argument('--age', help='年龄')
        parser.add_argument('--gender', help='性别')
        parser.add_argument('--occupation', help='职业/身份')
        parser.add_argument('--role', help='故事中的角色')
        parser.add_argument('--output', '-o', help='输出文件路径')
        parser.add_argument('--workspace', '-w', help='工作目录路径，启用LoreBible管理功能')
        parser.add_argument('--no-confirm', action='store_true', help='跳过用户确认（仅增强模式）')
        parser.add_argument('--interactive', '-i', action='store_true', help='交互模式')

        args = parser.parse_args()

        if args.interactive:
            # 交互模式，暂时不支持增强功能
            generator = CharacterProfileGenerator(args.type)
            return generator.create_from_cli()
        else:
            character_data = {
                'name': args.name,
                'age': args.age or '未知',
                'gender': args.gender or '未指定',
                'occupation': args.occupation or '未指定',
                'role': args.role or '未指定'
            }

            # 检查是否启用增强模式
            if args.workspace:
                # 增强模式
                generator = CharacterProfileGenerator(args.type, workspace=args.workspace)

                # 使用增强生成
                success, final_path, conflicts = generator.generate_enhanced_profile(
                    character_data,
                    require_confirmation=not args.no_confirm
                )

                if success:
                    print(f"✓ 角色档案创建成功: {final_path}")
                    if conflicts:
                        print(f"   检测到 {len(conflicts)} 个问题，已处理")
                    return 0
                else:
                    print(f"✗ 角色档案创建失败")
                    if conflicts:
                        print(f"   存在 {len(conflicts)} 个问题需要解决")
                    return 1
            else:
                # 传统模式
                generator = CharacterProfileGenerator(args.type)

                if args.output:
                    output_path = args.output
                else:
                    safe_name = "".join(c for c in args.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    filename = f"character_profile_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    output_path = os.path.join(os.getcwd(), filename)

                result = generator.generate_markdown(character_data, output_path)
                print(f"档案已生成: {output_path}")
                return 0
    else:
        # 交互模式
        generator = CharacterProfileGenerator()
        return generator.create_from_cli()


if __name__ == "__main__":
    sys.exit(main())