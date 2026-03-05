#!/usr/bin/env python3
"""
LoreBible目录管理模块
负责管理LoreBible目录结构、文件操作和现有角色扫描
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class LoreBibleManager:
    """LoreBible目录管理器"""

    # 标准目录结构
    DEFAULT_DIRECTORY_STRUCTURE = {
        "00_Prepare": "临时档案目录",
        "01_Research": "研究资料目录",
        "02_LoreBible": {
            "Characters": "角色档案目录",
            "Locations": "地点设定目录",
            "Organizations": "组织设定目录",
            "Timeline": "时间线目录"
        }
    }

    def __init__(self, workspace: str):
        """初始化LoreBible管理器

        Args:
            workspace: 工作目录路径
        """
        self.workspace = Path(workspace).resolve()
        self.characters_dir = self.workspace / "02_LoreBible" / "Characters"
        self.prepare_dir = self.workspace / "00_Prepare"
        self._character_index = None  # 角色信息索引缓存

    def validate_directory_structure(self) -> Tuple[bool, List[str]]:
        """验证目录结构是否符合标准

        Returns:
            (是否有效, 缺失目录列表)
        """
        missing_dirs = []

        # 检查必需目录
        required_dirs = [
            self.workspace,
            self.characters_dir,
            self.prepare_dir
        ]

        for dir_path in required_dirs:
            if not dir_path.exists():
                missing_dirs.append(str(dir_path.relative_to(self.workspace)))

        return len(missing_dirs) == 0, missing_dirs

    def create_directory_structure(self) -> bool:
        """创建缺失的目录结构

        Returns:
            是否成功创建
        """
        try:
            # 创建必需目录
            self.characters_dir.mkdir(parents=True, exist_ok=True)
            self.prepare_dir.mkdir(parents=True, exist_ok=True)

            # 创建可选目录
            optional_dirs = [
                self.workspace / "01_Research",
                self.workspace / "02_LoreBible" / "Locations",
                self.workspace / "02_LoreBible" / "Organizations",
                self.workspace / "02_LoreBible" / "Timeline"
            ]

            for dir_path in optional_dirs:
                dir_path.mkdir(parents=True, exist_ok=True)

            logger.info(f"目录结构已创建在: {self.workspace}")
            return True

        except Exception as e:
            logger.error(f"创建目录结构失败: {e}")
            return False

    def scan_existing_characters(self) -> List[Dict]:
        """扫描现有角色档案

        Returns:
            角色信息列表
        """
        if not self.characters_dir.exists():
            return []

        characters = []
        pattern = re.compile(r'\.md$', re.IGNORECASE)

        for file_path in self.characters_dir.glob("*.md"):
            try:
                character_info = self._parse_character_file(file_path)
                if character_info:
                    characters.append(character_info)
            except Exception as e:
                logger.warning(f"解析角色文件失败 {file_path}: {e}")

        return characters

    def _parse_character_file(self, file_path: Path) -> Optional[Dict]:
        """解析单个角色档案文件

        Args:
            file_path: 角色档案文件路径

        Returns:
            角色信息字典，解析失败返回None
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # 提取基本信息
            info = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "last_modified": file_path.stat().st_mtime
            }

            # 提取角色姓名（从标题行）
            name_match = re.search(r'^#\s+(.+?)\s+-', content, re.MULTILINE)
            if name_match:
                info["name"] = name_match.group(1).strip()
            else:
                # 尝试从文件名提取
                info["name"] = file_path.stem.replace('character_profile_', '').replace('_', ' ')

            # 提取年龄
            age_match = re.search(r'- \*\*年龄\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if age_match:
                info["age"] = age_match.group(1).strip()

            # 提取性别
            gender_match = re.search(r'- \*\*性别\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if gender_match:
                info["gender"] = gender_match.group(1).strip()

            # 提取职业/身份
            occupation_match = re.search(r'- \*\*职业/身份\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if occupation_match:
                info["occupation"] = occupation_match.group(1).strip()

            # 提取故事中的角色
            role_match = re.search(r'- \*\*故事中的角色\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if role_match:
                info["role"] = role_match.group(1).strip()

            # 提取角色类型（从元数据）
            type_match = re.search(r'- \*\*角色类型\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if type_match:
                info["character_type"] = type_match.group(1).strip()

            # 提取创建时间
            created_match = re.search(r'- \*\*创建时间\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if created_match:
                info["created"] = created_match.group(1).strip()

            # 提取状态
            status_match = re.search(r'- \*\*状态\*\*[：:]\s*(.+?)(?:\n|$)', content)
            if status_match:
                info["status"] = status_match.group(1).strip()

            # 提取关系信息（简单提取）
            relationships_section = self._extract_section(content, "人物关系")
            if relationships_section:
                info["has_relationships"] = True
                # 可以进一步解析具体关系

            # 提取背景故事
            background_section = self._extract_section(content, "背景故事")
            if background_section:
                info["has_background"] = True

            return info

        except Exception as e:
            logger.error(f"解析角色文件失败 {file_path}: {e}")
            return None

    def _extract_section(self, content: str, section_title: str) -> Optional[str]:
        """提取指定章节内容

        Args:
            content: 文档内容
            section_title: 章节标题

        Returns:
            章节内容，未找到返回None
        """
        # 寻找章节标题
        pattern = rf'##\s+{re.escape(section_title)}(.*?)(?=##\s+|---|\Z)'
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)

        if match:
            return match.group(1).strip()
        return None

    def get_character_index(self, force_refresh: bool = False) -> Dict:
        """获取角色信息索引（带缓存）

        Args:
            force_refresh: 是否强制刷新缓存

        Returns:
            角色索引字典
        """
        if self._character_index is None or force_refresh:
            characters = self.scan_existing_characters()
            self._character_index = {
                "total_count": len(characters),
                "characters": characters,
                "name_map": {char.get("name", ""): char for char in characters if char.get("name")},
                "by_type": self._group_by_type(characters),
                "last_updated": os.path.getmtime(self.characters_dir) if self.characters_dir.exists() else 0
            }

        return self._character_index

    def _group_by_type(self, characters: List[Dict]) -> Dict:
        """按角色类型分组

        Args:
            characters: 角色列表

        Returns:
            按类型分组的字典
        """
        grouped = {}
        for char in characters:
            char_type = char.get("character_type", "未知")
            if char_type not in grouped:
                grouped[char_type] = []
            grouped[char_type].append(char)
        return grouped

    def save_temp_profile(self, content: str, character_name: str, session_id: str = None) -> Optional[Path]:
        """保存临时档案到00_Prepare目录

        Args:
            content: 档案内容
            character_name: 角色名称
            session_id: 会话ID，为None时自动生成

        Returns:
            临时文件路径，失败返回None
        """
        try:
            if not self.prepare_dir.exists():
                self.prepare_dir.mkdir(parents=True, exist_ok=True)

            # 生成会话ID
            import uuid
            if session_id is None:
                session_id = str(uuid.uuid4())[:8]

            # 安全文件名
            safe_name = re.sub(r'[^\w\s-]', '', character_name).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)

            # 临时文件名
            filename = f"temp_{safe_name}_{session_id}.md"
            temp_path = self.prepare_dir / filename

            # 写入文件
            temp_path.write_text(content, encoding='utf-8')
            logger.info(f"临时档案已保存: {temp_path}")

            return temp_path

        except Exception as e:
            logger.error(f"保存临时档案失败: {e}")
            return None

    def move_to_characters(self, temp_file_path: Path, character_name: str = None) -> Optional[Path]:
        """将临时档案移动到Characters目录

        Args:
            temp_file_path: 临时文件路径
            character_name: 角色名称，为None时从文件内容提取

        Returns:
            最终文件路径，失败返回None
        """
        try:
            if not temp_file_path.exists():
                logger.error(f"临时文件不存在: {temp_file_path}")
                return None

            # 确保目标目录存在
            if not self.characters_dir.exists():
                self.characters_dir.mkdir(parents=True, exist_ok=True)

            # 读取内容提取角色名
            if character_name is None:
                content = temp_file_path.read_text(encoding='utf-8', errors='ignore')
                name_match = re.search(r'^#\s+(.+?)\s+-', content, re.MULTILINE)
                if name_match:
                    character_name = name_match.group(1).strip()
                else:
                    character_name = temp_file_path.stem.replace('temp_', '').split('_')[0]

            # 安全文件名
            safe_name = re.sub(r'[^\w\s-]', '', character_name).strip()
            safe_name = re.sub(r'[-\s]+', '_', safe_name)

            # 最终文件名
            import datetime
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"character_profile_{safe_name}_{timestamp}.md"
            final_path = self.characters_dir / filename

            # 移动文件
            temp_file_path.rename(final_path)
            logger.info(f"档案已移动到: {final_path}")

            # 刷新缓存
            self._character_index = None

            return final_path

        except Exception as e:
            logger.error(f"移动档案失败: {e}")
            return None

    def cleanup_old_temp_files(self, max_age_hours: int = 24) -> int:
        """清理旧的临时文件

        Args:
            max_age_hours: 最大保留时间（小时）

        Returns:
            清理的文件数量
        """
        if not self.prepare_dir.exists():
            return 0

        import time
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        cleaned_count = 0

        for file_path in self.prepare_dir.glob("temp_*.md"):
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    cleaned_count += 1
                    logger.debug(f"清理临时文件: {file_path}")
            except Exception as e:
                logger.warning(f"清理文件失败 {file_path}: {e}")

        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个临时文件")

        return cleaned_count

    def get_workspace_info(self) -> Dict:
        """获取工作空间信息

        Returns:
            工作空间信息字典
        """
        info = {
            "workspace": str(self.workspace),
            "characters_dir": str(self.characters_dir),
            "prepare_dir": str(self.prepare_dir),
            "characters_count": 0,
            "temp_files_count": 0,
            "directory_exists": self.workspace.exists()
        }

        if self.characters_dir.exists():
            info["characters_count"] = len(list(self.characters_dir.glob("*.md")))

        if self.prepare_dir.exists():
            info["temp_files_count"] = len(list(self.prepare_dir.glob("temp_*.md")))

        return info


def main():
    """命令行测试"""
    import sys

    if len(sys.argv) < 2:
        print("用法: python lore_bible_manager.py <工作目录>")
        sys.exit(1)

    workspace = sys.argv[1]
    manager = LoreBibleManager(workspace)

    print(f"工作目录: {workspace}")

    # 验证目录结构
    is_valid, missing_dirs = manager.validate_directory_structure()
    if is_valid:
        print("✓ 目录结构完整")
    else:
        print("✗ 缺失目录:")
        for dir_name in missing_dirs:
            print(f"  - {dir_name}")

        # 询问是否创建
        response = input("是否创建缺失目录? (y/n): ").strip().lower()
        if response == 'y':
            if manager.create_directory_structure():
                print("✓ 目录结构已创建")
            else:
                print("✗ 创建目录失败")

    # 扫描现有角色
    characters = manager.scan_existing_characters()
    print(f"现有角色数量: {len(characters)}")

    for char in characters[:5]:  # 显示前5个
        print(f"  - {char.get('name', '未知')} ({char.get('character_type', '未知类型')})")

    if len(characters) > 5:
        print(f"  ... 还有 {len(characters) - 5} 个角色")

    # 显示工作空间信息
    info = manager.get_workspace_info()
    print(f"\n工作空间信息:")
    print(f"  角色档案数: {info['characters_count']}")
    print(f"  临时文件数: {info['temp_files_count']}")


if __name__ == "__main__":
    main()