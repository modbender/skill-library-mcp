#!/usr/bin/env python3
"""
子代理协调模块
协调子代理执行工作流任务
"""

import json
import importlib
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import time

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class AgentType(Enum):
    """代理类型"""
    LORE_BIBLE_MANAGER = "lore_bible_manager"
    CONFLICT_DETECTOR = "conflict_detector"
    PROFILE_SESSION = "profile_session"
    PROFILE_GENERATOR = "profile_generator"


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    status: TaskStatus
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    start_time: float = 0
    end_time: float = 0
    duration: float = 0


@dataclass
class WorkflowTask:
    """工作流任务定义"""
    id: str
    name: str
    description: str
    agent_type: str
    inputs: List[str]
    outputs: List[str]
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    timeout: int = 60
    retry_count: int = 1
    interactive: bool = False


class SubagentOrchestrator:
    """子代理协调器"""

    def __init__(self, workspace: str, config_file: Optional[str] = None):
        """初始化协调器

        Args:
            workspace: 工作目录
            config_file: 工作流配置文件路径
        """
        self.workspace = workspace
        self.config_file = config_file or str(Path(__file__).parent.parent / "config" / "workflow_tasks.json")
        self.workflows = self._load_workflows()
        self.tasks: Dict[str, WorkflowTask] = {}
        self.results: Dict[str, TaskResult] = {}
        self.context: Dict[str, Any] = {"workspace": workspace}
        self.agents: Dict[str, Any] = {}

    def _load_workflows(self) -> Dict:
        """加载工作流配置

        Returns:
            工作流配置字典
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"加载工作流配置: {self.config_file}")
            return config
        except Exception as e:
            logger.error(f"加载工作流配置失败: {e}")
            return {"workflows": {}, "agents": {}}

    def _initialize_agent(self, agent_type: str) -> Optional[Any]:
        """初始化代理实例

        Args:
            agent_type: 代理类型

        Returns:
            代理实例，失败返回None
        """
        if agent_type in self.agents:
            return self.agents[agent_type]

        agent_config = self.workflows.get("agents", {}).get(agent_type)
        if not agent_config:
            logger.error(f"未找到代理配置: {agent_type}")
            return None

        try:
            module_name = agent_config["module"]
            class_name = agent_config["class"]

            # 动态导入模块
            module = importlib.import_module(module_name.replace('/', '.'))
            agent_class = getattr(module, class_name)

            # 实例化代理
            if agent_type == AgentType.LORE_BIBLE_MANAGER.value:
                agent = agent_class(self.workspace)
            elif agent_type == AgentType.CONFLICT_DETECTOR.value:
                agent = agent_class()
            elif agent_type == AgentType.PROFILE_GENERATOR.value:
                agent = agent_class()
            elif agent_type == AgentType.PROFILE_SESSION.value:
                agent = None  # 会话需要特殊处理
            else:
                agent = agent_class()

            self.agents[agent_type] = agent
            logger.info(f"初始化代理: {agent_type}")
            return agent

        except Exception as e:
            logger.error(f"初始化代理失败 {agent_type}: {e}")
            return None

    def _execute_task(self, task: WorkflowTask) -> TaskResult:
        """执行单个任务

        Args:
            task: 任务定义

        Returns:
            任务结果
        """
        result = TaskResult(task_id=task.id, status=TaskStatus.RUNNING)
        result.start_time = time.time()

        try:
            logger.info(f"开始执行任务: {task.name} ({task.id})")

            # 检查条件
            if task.condition:
                if not self._evaluate_condition(task.condition):
                    result.status = TaskStatus.SKIPPED
                    result.outputs = {"skipped": True, "reason": "条件不满足"}
                    logger.info(f"跳过任务 {task.id}: 条件不满足")
                    return result

            # 准备输入参数
            inputs = self._prepare_inputs(task.inputs)

            # 执行任务
            if task.agent_type == AgentType.LORE_BIBLE_MANAGER.value:
                outputs = self._execute_lore_bible_task(task.id, inputs)
            elif task.agent_type == AgentType.CONFLICT_DETECTOR.value:
                outputs = self._execute_conflict_detector_task(task.id, inputs)
            elif task.agent_type == AgentType.PROFILE_SESSION.value:
                outputs = self._execute_profile_session_task(task.id, inputs)
            elif task.agent_type == AgentType.PROFILE_GENERATOR.value:
                outputs = self._execute_profile_generator_task(task.id, inputs)
            else:
                raise ValueError(f"未知的代理类型: {task.agent_type}")

            # 验证输出
            self._validate_outputs(task.outputs, outputs)

            # 更新上下文
            self.context.update(outputs)

            result.status = TaskStatus.COMPLETED
            result.outputs = outputs
            logger.info(f"任务完成: {task.name}")

        except Exception as e:
            result.status = TaskStatus.FAILED
            result.error = str(e)
            logger.error(f"任务失败 {task.id}: {e}")

        finally:
            result.end_time = time.time()
            result.duration = result.end_time - result.start_time

        return result

    def _prepare_inputs(self, input_keys: List[str]) -> Dict[str, Any]:
        """准备输入参数

        Args:
            input_keys: 输入键列表

        Returns:
            输入参数字典
        """
        inputs = {}
        for key in input_keys:
            if key in self.context:
                inputs[key] = self.context[key]
            else:
                # 尝试从结果中获取
                for task_id, result in self.results.items():
                    if key in result.outputs:
                        inputs[key] = result.outputs[key]
                        break
                else:
                    logger.warning(f"未找到输入参数: {key}")
                    inputs[key] = None

        return inputs

    def _validate_outputs(self, expected_outputs: List[str], actual_outputs: Dict[str, Any]):
        """验证输出参数

        Args:
            expected_outputs: 期望的输出键列表
            actual_outputs: 实际的输出字典
        """
        for output_key in expected_outputs:
            if output_key not in actual_outputs:
                logger.warning(f"任务缺少输出: {output_key}")

    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件表达式

        Args:
            condition: 条件表达式

        Returns:
            条件是否满足
        """
        try:
            # 简单的条件评估
            if condition == "user_confirmed == true":
                return self.context.get("user_confirmed", False) is True
            elif condition == "is_valid == true":
                return self.context.get("is_valid", False) is True
            else:
                # 尝试评估Python表达式
                local_vars = {**self.context}
                for task_id, result in self.results.items():
                    local_vars.update(result.outputs)

                return eval(condition, {}, local_vars)
        except Exception as e:
            logger.warning(f"评估条件失败 '{condition}': {e}")
            return False

    def _execute_lore_bible_task(self, task_id: str, inputs: Dict) -> Dict:
        """执行LoreBible管理任务

        Args:
            task_id: 任务ID
            inputs: 输入参数

        Returns:
            输出参数字典
        """
        agent = self._initialize_agent(AgentType.LORE_BIBLE_MANAGER.value)
        if not agent:
            raise RuntimeError("初始化LoreBibleManager失败")

        workspace = inputs.get("workspace", self.workspace)

        if task_id == "init_workspace":
            # 验证目录结构
            is_valid, missing_dirs = agent.validate_directory_structure()

            if not is_valid:
                # 创建缺失目录
                success = agent.create_directory_structure()
                if not success:
                    raise RuntimeError("创建目录结构失败")

            # 扫描现有角色
            characters = agent.scan_existing_characters()

            return {
                "directory_status": "valid" if is_valid else "created",
                "missing_dirs": missing_dirs if not is_valid else [],
                "character_count": len(characters),
                "character_index": characters
            }

        elif task_id == "scan_existing":
            characters = agent.scan_existing_characters()
            index = agent.get_character_index(force_refresh=True)

            return {
                "character_index": characters,
                "character_count": len(characters),
                "index_details": index
            }

        else:
            raise ValueError(f"未知的LoreBible任务: {task_id}")

    def _execute_conflict_detector_task(self, task_id: str, inputs: Dict) -> Dict:
        """执行冲突检测任务

        Args:
            task_id: 任务ID
            inputs: 输入参数

        Returns:
            输出参数字典
        """
        agent = self._initialize_agent(AgentType.CONFLICT_DETECTOR.value)
        if not agent:
            raise RuntimeError("初始化ConflictDetector失败")

        if task_id == "detect_conflicts":
            character_data = inputs.get("character_data", {})
            character_index = inputs.get("character_index", [])

            # 设置角色索引
            agent.set_character_index({
                "characters": character_index,
                "total_count": len(character_index)
            })

            # 检测冲突
            conflicts = agent.detect_conflicts(character_data, character_index)
            is_valid, _ = agent.validate_character(character_data)

            # 生成报告
            report = agent.generate_report(conflicts, "text")

            return {
                "conflicts": conflicts,
                "is_valid": is_valid,
                "conflict_count": len(conflicts),
                "report": report
            }

        else:
            raise ValueError(f"未知的冲突检测任务: {task_id}")

    def _execute_profile_session_task(self, task_id: str, inputs: Dict) -> Dict:
        """执行会话管理任务

        Args:
            task_id: 任务ID
            inputs: 输入参数

        Returns:
            输出参数字典
        """
        from profile_session import ProfileSession, SessionConfig

        if task_id == "save_temp":
            profile_content = inputs.get("profile_content", "")
            character_name = inputs.get("character_name", "")
            workspace = inputs.get("workspace", self.workspace)

            # 创建会话配置
            config = SessionConfig(
                workspace=workspace,
                character_name=character_name,
                enable_validation=False,
                enable_conflict_check=False,
                require_confirmation=False
            )

            # 创建会话
            session = ProfileSession(config)

            # 保存临时档案
            temp_path = session.save_temp_profile(profile_content)
            if not temp_path:
                raise RuntimeError("保存临时档案失败")

            # 保存会话ID到上下文
            self.context["session_id"] = session.session_id

            return {
                "temp_file_path": str(temp_path),
                "session_id": session.session_id
            }

        elif task_id == "user_review":
            conflicts = inputs.get("conflicts", [])
            temp_file_path = inputs.get("temp_file_path", "")
            session_id = self.context.get("session_id")

            if not session_id:
                raise ValueError("未找到会话ID")

            # 加载会话
            workspace = inputs.get("workspace", self.workspace)
            session = ProfileSession.load_session(session_id, workspace)
            if not session:
                raise RuntimeError("加载会话失败")

            # 向用户展示
            user_confirmed = session.present_to_user(conflicts)
            user_notes = session.session_data.user_notes

            return {
                "user_confirmed": user_confirmed,
                "user_notes": user_notes,
                "session_id": session_id
            }

        elif task_id == "move_final":
            temp_file_path = inputs.get("temp_file_path", "")
            character_name = inputs.get("character_name", "")
            user_confirmed = inputs.get("user_confirmed", False)
            session_id = self.context.get("session_id")

            if not user_confirmed:
                return {"skipped": True, "reason": "用户未确认"}

            if not session_id:
                raise ValueError("未找到会话ID")

            # 加载会话
            workspace = inputs.get("workspace", self.workspace)
            session = ProfileSession.load_session(session_id, workspace)
            if not session:
                raise RuntimeError("加载会话失败")

            # 移动到最终目录
            final_path = session.confirm_and_move()
            if not final_path:
                raise RuntimeError("移动档案失败")

            return {
                "final_file_path": str(final_path),
                "session_id": session_id
            }

        elif task_id == "cleanup":
            session_id = inputs.get("session_id", self.context.get("session_id"))
            workspace = inputs.get("workspace", self.workspace)

            if not session_id:
                return {"cleaned_count": 0}

            # 加载会话
            session = ProfileSession.load_session(session_id, workspace)
            if session:
                session.cleanup()

            return {"cleaned_count": 1}

        else:
            raise ValueError(f"未知的会话管理任务: {task_id}")

    def _execute_profile_generator_task(self, task_id: str, inputs: Dict) -> Dict:
        """执行档案生成任务

        Args:
            task_id: 任务ID
            inputs: 输入参数

        Returns:
            输出参数字典
        """
        agent = self._initialize_agent(AgentType.PROFILE_GENERATOR.value)
        if not agent:
            raise RuntimeError("初始化ProfileGenerator失败")

        if task_id == "generate_profile":
            character_data = inputs.get("character_data", {})
            template_type = inputs.get("template_type", "standard")

            # 设置模板类型
            agent.template_type = template_type

            # 生成档案内容
            profile_content = agent.generate_markdown(character_data, output_path=None)

            return {
                "profile_content": profile_content,
                "character_name": character_data.get("name", "")
            }

        elif task_id == "generate_and_save":
            character_data = inputs.get("character_data", {})
            template_type = inputs.get("template_type", "standard")
            workspace = inputs.get("workspace", self.workspace)

            # 设置工作空间
            agent.workspace = workspace
            agent.enable_enhanced_features = True

            # 使用增强功能生成
            success, final_path, conflicts = agent.generate_enhanced_profile(
                character_data,
                require_confirmation=False
            )

            if not success:
                raise RuntimeError(f"生成档案失败: {conflicts}")

            return {
                "final_file_path": str(final_path) if final_path else None,
                "success": success,
                "conflict_count": len(conflicts)
            }

        else:
            raise ValueError(f"未知的档案生成任务: {task_id}")

    def run_workflow(self, workflow_name: str, initial_context: Dict = None) -> Dict[str, Any]:
        """运行工作流

        Args:
            workflow_name: 工作流名称
            initial_context: 初始上下文

        Returns:
            最终上下文和结果
        """
        if initial_context:
            self.context.update(initial_context)

        # 获取工作流定义
        workflow = self.workflows.get("workflows", {}).get(workflow_name)
        if not workflow:
            raise ValueError(f"未找到工作流: {workflow_name}")

        logger.info(f"开始运行工作流: {workflow['name']}")

        # 解析任务
        tasks_data = workflow.get("tasks", [])
        self.tasks = {task["id"]: WorkflowTask(**task) for task in tasks_data}

        # 执行任务
        execution_order = self._calculate_execution_order()

        for task_id in execution_order:
            task = self.tasks[task_id]

            # 检查依赖是否完成
            for dep_id in task.depends_on:
                if dep_id not in self.results:
                    raise RuntimeError(f"任务 {task_id} 的依赖 {dep_id} 未执行")
                if self.results[dep_id].status == TaskStatus.FAILED:
                    logger.warning(f"任务 {task_id} 的依赖 {dep_id} 失败，跳过")
                    self.results[task_id] = TaskResult(
                        task_id=task_id,
                        status=TaskStatus.SKIPPED,
                        outputs={"skipped": True, "reason": f"依赖 {dep_id} 失败"}
                    )
                    continue

            # 执行任务（带重试）
            result = None
            for attempt in range(task.retry_count + 1):
                if attempt > 0:
                    logger.info(f"重试任务 {task_id} (尝试 {attempt + 1}/{task.retry_count + 1})")

                result = self._execute_task(task)

                if result.status == TaskStatus.COMPLETED:
                    break
                elif attempt < task.retry_count:
                    logger.warning(f"任务 {task_id} 失败，准备重试: {result.error}")
                    time.sleep(1)  # 重试前等待

            self.results[task_id] = result

        # 生成报告
        report = self._generate_report(workflow_name)

        logger.info(f"工作流完成: {workflow_name}")
        return {
            "context": self.context,
            "results": self.results,
            "report": report
        }

    def _calculate_execution_order(self) -> List[str]:
        """计算任务执行顺序（拓扑排序）

        Returns:
            任务ID列表
        """
        # 构建依赖图
        graph = {task_id: set(task.depends_on) for task_id, task in self.tasks.items()}

        # 拓扑排序
        visited = set()
        temp_visited = set()
        order = []

        def visit(node):
            if node in temp_visited:
                raise RuntimeError(f"检测到循环依赖: {node}")
            if node in visited:
                return

            temp_visited.add(node)
            for dep in graph.get(node, set()):
                if dep in self.tasks:  # 只包括定义的任务
                    visit(dep)

            temp_visited.remove(node)
            visited.add(node)
            order.append(node)

        for task_id in self.tasks:
            if task_id not in visited:
                visit(task_id)

        return order

    def _generate_report(self, workflow_name: str) -> Dict:
        """生成执行报告

        Args:
            workflow_name: 工作流名称

        Returns:
            报告字典
        """
        total_tasks = len(self.tasks)
        completed = sum(1 for r in self.results.values() if r.status == TaskStatus.COMPLETED)
        failed = sum(1 for r in self.results.values() if r.status == TaskStatus.FAILED)
        skipped = sum(1 for r in self.results.values() if r.status == TaskStatus.SKIPPED)

        task_details = []
        for task_id, result in self.results.items():
            task_details.append({
                "task_id": task_id,
                "name": self.tasks[task_id].name if task_id in self.tasks else "未知",
                "status": result.status.value,
                "duration": result.duration,
                "error": result.error
            })

        return {
            "workflow": workflow_name,
            "total_tasks": total_tasks,
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "success_rate": completed / total_tasks if total_tasks > 0 else 0,
            "total_duration": sum(r.duration for r in self.results.values()),
            "task_details": task_details,
            "final_context_keys": list(self.context.keys())
        }


def main():
    """命令行测试"""
    import sys

    if len(sys.argv) < 3:
        print("用法: python subagent_orchestrator.py <工作目录> <工作流名称>")
        print("可用工作流: character_creation, quick_creation")
        sys.exit(1)

    workspace = sys.argv[1]
    workflow_name = sys.argv[2]

    # 创建协调器
    orchestrator = SubagentOrchestrator(workspace)

    # 运行工作流
    try:
        result = orchestrator.run_workflow(workflow_name)

        print(f"\n{'='*60}")
        print(f"工作流执行完成: {workflow_name}")
        print(f"{'='*60}\n")

        report = result["report"]
        print(f"任务统计: {report['completed']}/{report['total_tasks']} 完成, "
              f"{report['failed']} 失败, {report['skipped']} 跳过")
        print(f"成功率: {report['success_rate']:.1%}")
        print(f"总耗时: {report['total_duration']:.2f} 秒\n")

        print("任务详情:")
        for task in report["task_details"]:
            status_icon = {
                "completed": "✓",
                "failed": "✗",
                "skipped": "⏭",
                "running": "↻",
                "pending": "⏳"
            }.get(task["status"], "?")

            print(f"  {status_icon} {task['name']} ({task['task_id']})")
            print(f"    状态: {task['status']}, 耗时: {task['duration']:.2f}秒")
            if task["error"]:
                print(f"    错误: {task['error']}")

        # 显示最终输出
        if "final_file_path" in result["context"]:
            print(f"\n生成的档案: {result['context']['final_file_path']}")

    except Exception as e:
        print(f"工作流执行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()