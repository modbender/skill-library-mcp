#!/usr/bin/env python3
"""
会话管理模块
管理角色创建会话、临时文件和用户确认流程
"""

import json
import uuid
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import logging
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """会话状态"""
    CREATED = "created"          # 已创建
    TEMP_SAVED = "temp_saved"    # 临时文件已保存
    VALIDATED = "validated"      # 已校验
    CONFLICTS_DETECTED = "conflicts_detected"  # 检测到冲突
    USER_REVIEWED = "user_reviewed"  # 用户已审核
    CONFIRMED = "confirmed"      # 用户已确认
    MOVED = "moved"              # 已移动到最终目录
    CANCELLED = "cancelled"      # 已取消
    ERROR = "error"              # 错误状态


@dataclass
class SessionConfig:
    """会话配置"""
    workspace: str
    character_name: str
    template_type: str = "standard"
    auto_cleanup: bool = True
    max_temp_age_hours: int = 24
    enable_validation: bool = True
    enable_conflict_check: bool = True
    require_confirmation: bool = True


@dataclass
class SessionData:
    """会话数据"""
    session_id: str
    config: SessionConfig
    status: SessionStatus = SessionStatus.CREATED
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    temp_file_path: Optional[str] = None
    final_file_path: Optional[str] = None
    conflicts: List[Dict] = field(default_factory=list)
    validation_results: List[Dict] = field(default_factory=list)
    user_notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ProfileSession:
    """角色创建会话管理器"""

    def __init__(self, config: SessionConfig):
        """初始化会话

        Args:
            config: 会话配置
        """
        self.config = config
        self.session_id = str(uuid.uuid4())[:8]
        self.session_data = SessionData(
            session_id=self.session_id,
            config=config
        )
        self.workspace_path = Path(config.workspace).resolve()
        self.session_file = self.workspace_path / ".sessions" / f"session_{self.session_id}.json"

        # 确保会话目录存在
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"创建会话: {self.session_id} - {config.character_name}")

    def save_temp_profile(self, content: str) -> Optional[Path]:
        """保存临时档案

        Args:
            content: 档案内容

        Returns:
            临时文件路径
        """
        try:
            from lore_bible_manager import LoreBibleManager
            manager = LoreBibleManager(self.config.workspace)

            # 确保目录存在
            manager.create_directory_structure()

            # 保存临时文件
            temp_path = manager.save_temp_profile(
                content=content,
                character_name=self.config.character_name,
                session_id=self.session_id
            )

            if temp_path:
                self.session_data.temp_file_path = str(temp_path)
                self.session_data.status = SessionStatus.TEMP_SAVED
                self._update_timestamp()
                self._save_session_data()

                logger.info(f"临时档案已保存: {temp_path}")
                return temp_path

        except Exception as e:
            logger.error(f"保存临时档案失败: {e}")
            self.session_data.status = SessionStatus.ERROR
            self.session_data.metadata["error"] = str(e)
            self._save_session_data()

        return None

    def validate_and_check_conflicts(self, character_data: Dict) -> Tuple[bool, List[Dict]]:
        """验证角色并检查冲突

        Args:
            character_data: 角色数据

        Returns:
            (是否有效, 冲突列表)
        """
        if not self.config.enable_validation and not self.config.enable_conflict_check:
            return True, []

        try:
            from lore_bible_manager import LoreBibleManager
            from conflict_detector import ConflictDetector, ConflictSeverity

            manager = LoreBibleManager(self.config.workspace)
            detector = ConflictDetector()

            # 获取现有角色
            existing_characters = manager.scan_existing_characters()

            # 设置角色索引
            detector.set_character_index({
                "characters": existing_characters,
                "total_count": len(existing_characters)
            })

            # 检测冲突
            conflicts = []
            if self.config.enable_conflict_check:
                conflicts = detector.detect_conflicts(character_data, existing_characters)

            # 验证角色
            is_valid = True
            if self.config.enable_validation:
                valid, validation_conflicts = detector.validate_character(character_data)
                if not valid:
                    is_valid = False
                conflicts.extend(validation_conflicts)

            # 更新会话数据
            self.session_data.conflicts = [asdict(conflict) if hasattr(conflict, '__dataclass_fields__') else conflict
                                          for conflict in conflicts]
            self.session_data.validation_results = [{"valid": is_valid}]

            if conflicts:
                self.session_data.status = SessionStatus.CONFLICTS_DETECTED
            else:
                self.session_data.status = SessionStatus.VALIDATED

            self._update_timestamp()
            self._save_session_data()

            logger.info(f"验证完成: 有效={is_valid}, 冲突数={len(conflicts)}")
            return is_valid, conflicts

        except Exception as e:
            logger.error(f"验证失败: {e}")
            self.session_data.status = SessionStatus.ERROR
            self.session_data.metadata["error"] = str(e)
            self._save_session_data()
            return False, []

    def present_to_user(self, conflicts: List[Dict]) -> bool:
        """向用户展示结果并获取反馈

        Args:
            conflicts: 冲突列表

        Returns:
            用户是否确认继续
        """
        print(f"\n{'='*60}")
        print(f"角色创建会话: {self.session_id}")
        print(f"角色名称: {self.config.character_name}")
        print(f"工作目录: {self.config.workspace}")
        print(f"{'='*60}\n")

        # 显示临时文件位置
        if self.session_data.temp_file_path:
            print(f"临时档案: {self.session_data.temp_file_path}")
            print("")

        # 显示冲突和警告
        if conflicts:
            print("⚠️  检测到以下问题:")

            # 按严重程度分组
            errors = [c for c in conflicts if c.get("severity") == "error"]
            warnings = [c for c in conflicts if c.get("severity") == "warning"]
            infos = [c for c in conflicts if c.get("severity") == "info"]

            if errors:
                print("\n❌ 错误:")
                for i, conflict in enumerate(errors, 1):
                    print(f"  {i}. {conflict.get('message', '未知错误')}")
                    if conflict.get('suggested_fixes'):
                        print(f"     建议: {conflict['suggested_fixes'][0]}")

            if warnings:
                print("\n⚠️  警告:")
                for i, conflict in enumerate(warnings, 1):
                    print(f"  {i}. {conflict.get('message', '未知警告')}")

            if infos:
                print("\nℹ️  提示:")
                for i, conflict in enumerate(infos, 1):
                    print(f"  {i}. {conflict.get('message', '未知提示')}")

            print("")

            # 询问用户
            if errors:
                print("存在错误，无法继续。请修改角色设定后重试。")
                return False
            else:
                response = input("是否继续创建角色? (y/n): ").strip().lower()
                if response == 'y':
                    notes = input("请输入备注（可选，直接回车跳过）: ").strip()
                    if notes:
                        self.session_data.user_notes = notes
                    return True
                else:
                    return False
        else:
            print("✓ 未检测到冲突")
            print("")

            if self.config.require_confirmation:
                response = input("是否创建角色? (y/n): ").strip().lower()
                if response == 'y':
                    notes = input("请输入备注（可选，直接回车跳过）: ").strip()
                    if notes:
                        self.session_data.user_notes = notes
                    return True
                else:
                    return False
            else:
                return True

    def confirm_and_move(self) -> Optional[Path]:
        """用户确认后移动到最终目录

        Returns:
            最终文件路径
        """
        try:
            if not self.session_data.temp_file_path:
                logger.error("临时文件路径不存在")
                return None

            temp_path = Path(self.session_data.temp_file_path)
            if not temp_path.exists():
                logger.error(f"临时文件不存在: {temp_path}")
                return None

            from lore_bible_manager import LoreBibleManager
            manager = LoreBibleManager(self.config.workspace)

            # 移动文件
            final_path = manager.move_to_characters(temp_path, self.config.character_name)

            if final_path:
                self.session_data.final_file_path = str(final_path)
                self.session_data.status = SessionStatus.MOVED
                self._update_timestamp()
                self._save_session_data()

                logger.info(f"档案已移动到: {final_path}")
                return final_path

        except Exception as e:
            logger.error(f"移动档案失败: {e}")
            self.session_data.status = SessionStatus.ERROR
            self.session_data.metadata["error"] = str(e)
            self._save_session_data()

        return None

    def cancel(self) -> bool:
        """取消会话并清理临时文件

        Returns:
            是否成功取消
        """
        try:
            # 删除临时文件
            if self.session_data.temp_file_path:
                temp_path = Path(self.session_data.temp_file_path)
                if temp_path.exists():
                    temp_path.unlink()
                    logger.info(f"已删除临时文件: {temp_path}")

            # 更新状态
            self.session_data.status = SessionStatus.CANCELLED
            self._update_timestamp()
            self._save_session_data()

            logger.info(f"会话已取消: {self.session_id}")
            return True

        except Exception as e:
            logger.error(f"取消会话失败: {e}")
            return False

    def cleanup(self) -> bool:
        """清理会话文件

        Returns:
            是否成功清理
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
                logger.info(f"已删除会话文件: {self.session_file}")

            # 清理旧的临时文件
            if self.config.auto_cleanup:
                from lore_bible_manager import LoreBibleManager
                manager = LoreBibleManager(self.config.workspace)
                cleaned = manager.cleanup_old_temp_files(self.config.max_temp_age_hours)
                logger.info(f"清理了 {cleaned} 个临时文件")

            return True

        except Exception as e:
            logger.error(f"清理失败: {e}")
            return False

    def get_status_report(self) -> Dict:
        """获取状态报告

        Returns:
            状态报告字典
        """
        report = {
            "session_id": self.session_id,
            "character_name": self.config.character_name,
            "status": self.session_data.status.value,
            "created_at": datetime.fromtimestamp(self.session_data.created_at).isoformat(),
            "updated_at": datetime.fromtimestamp(self.session_data.updated_at).isoformat(),
            "temp_file": self.session_data.temp_file_path,
            "final_file": self.session_data.final_file_path,
            "conflict_count": len(self.session_data.conflicts),
            "user_notes": self.session_data.user_notes,
            "workspace": self.config.workspace
        }

        # 添加冲突摘要
        if self.session_data.conflicts:
            error_count = len([c for c in self.session_data.conflicts if c.get("severity") == "error"])
            warning_count = len([c for c in self.session_data.conflicts if c.get("severity") == "warning"])
            report["conflict_summary"] = {
                "errors": error_count,
                "warnings": warning_count
            }

        return report

    def _save_session_data(self):
        """保存会话数据到文件"""
        try:
            data = asdict(self.session_data)
            # 将枚举转换为字符串
            data["status"] = self.session_data.status.value

            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        except Exception as e:
            logger.error(f"保存会话数据失败: {e}")

    def _update_timestamp(self):
        """更新时间戳"""
        self.session_data.updated_at = time.time()

    @classmethod
    def load_session(cls, session_id: str, workspace: str) -> Optional["ProfileSession"]:
        """加载现有会话

        Args:
            session_id: 会话ID
            workspace: 工作目录

        Returns:
            会话实例，加载失败返回None
        """
        try:
            workspace_path = Path(workspace).resolve()
            session_file = workspace_path / ".sessions" / f"session_{session_id}.json"

            if not session_file.exists():
                logger.error(f"会话文件不存在: {session_file}")
                return None

            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 重建配置
            config_data = data.get("config", {})
            config = SessionConfig(**config_data)

            # 创建会话实例
            session = cls(config)
            session.session_id = session_id
            session.session_file = session_file

            # 重建会话数据
            session.session_data = SessionData(
                session_id=session_id,
                config=config,
                status=SessionStatus(data.get("status", "created")),
                created_at=data.get("created_at", time.time()),
                updated_at=data.get("updated_at", time.time()),
                temp_file_path=data.get("temp_file_path"),
                final_file_path=data.get("final_file_path"),
                conflicts=data.get("conflicts", []),
                validation_results=data.get("validation_results", []),
                user_notes=data.get("user_notes", ""),
                metadata=data.get("metadata", {})
            )

            logger.info(f"已加载会话: {session_id}")
            return session

        except Exception as e:
            logger.error(f"加载会话失败: {e}")
            return None

    @classmethod
    def list_sessions(cls, workspace: str, active_only: bool = True) -> List[Dict]:
        """列出所有会话

        Args:
            workspace: 工作目录
            active_only: 是否只显示活动会话

        Returns:
            会话列表
        """
        sessions = []
        workspace_path = Path(workspace).resolve()
        sessions_dir = workspace_path / ".sessions"

        if not sessions_dir.exists():
            return sessions

        for session_file in sessions_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                session_id = session_file.stem.replace("session_", "")
                status = data.get("status", "created")

                # 如果只显示活动会话，跳过已完成/取消的
                if active_only and status in ["moved", "cancelled", "error"]:
                    continue

                sessions.append({
                    "session_id": session_id,
                    "character_name": data.get("config", {}).get("character_name", "未知"),
                    "status": status,
                    "created_at": data.get("created_at"),
                    "temp_file": data.get("temp_file_path"),
                    "final_file": data.get("final_file_path")
                })

            except Exception as e:
                logger.warning(f"读取会话文件失败 {session_file}: {e}")

        # 按创建时间排序
        sessions.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return sessions


def main():
    """命令行测试"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python profile_session.py <工作目录> <角色姓名>")
        print("可选参数: --template <模板类型> --no-confirm")
        sys.exit(1)

    workspace = sys.argv[1]
    character_name = sys.argv[2]

    # 解析可选参数
    template_type = "standard"
    require_confirmation = True

    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--template" and i + 1 < len(sys.argv):
            template_type = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--no-confirm":
            require_confirmation = False
            i += 1
        else:
            i += 1

    # 创建配置
    config = SessionConfig(
        workspace=workspace,
        character_name=character_name,
        template_type=template_type,
        require_confirmation=require_confirmation
    )

    # 创建会话
    session = ProfileSession(config)
    print(f"创建会话: {session.session_id}")

    # 模拟角色数据
    character_data = {
        "name": character_name,
        "age": "25",
        "gender": "男",
        "occupation": "剑士",
        "role": "主角"
    }

    # 模拟档案内容
    profile_content = f"""# {character_name} - 角色档案

## 基本信息
- **姓名**: {character_name}
- **年龄**: 25
- **性别**: 男
- **职业/身份**: 剑士
- **故事中的角色**: 主角
"""

    # 保存临时档案
    temp_path = session.save_temp_profile(profile_content)
    if temp_path:
        print(f"临时档案已保存: {temp_path}")

    # 验证和冲突检测
    is_valid, conflicts = session.validate_and_check_conflicts(character_data)
    print(f"验证结果: {'有效' if is_valid else '无效'}, 冲突数: {len(conflicts)}")

    # 展示给用户
    if session.present_to_user(conflicts):
        print("用户确认继续")

        # 确认并移动
        final_path = session.confirm_and_move()
        if final_path:
            print(f"档案已保存到: {final_path}")
        else:
            print("保存失败")
    else:
        print("用户取消")
        session.cancel()

    # 显示状态报告
    report = session.get_status_report()
    print(f"\n会话状态: {report['status']}")
    print(f"最终文件: {report['final_file'] or '无'}")


if __name__ == "__main__":
    main()