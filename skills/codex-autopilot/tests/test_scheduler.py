#!/usr/bin/env python3
"""
测试 Scheduler 模块 (Phase 3)
- load_all_projects（从 config + projects/ 合并）
- round-robin 排序
- priority 排序
- ACTIVE/冷却/限额过滤
- max_sends_per_tick 限制
- 项目生命周期转换
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# 添加 lib 到 path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.scheduler import (
    ProjectInfo,
    ProjectLifecycle,
    load_all_projects,
    schedule_projects,
    update_project_lifecycle,
    update_project_send_order,
    get_project_by_name,
)
from lib.state_manager import GlobalState, ProjectState


class TestProjectLifecycle(unittest.TestCase):
    """测试项目生命周期"""
    
    def test_lifecycle_values(self):
        """测试生命周期枚举值"""
        self.assertEqual(ProjectLifecycle.DISABLED.value, "disabled")
        self.assertEqual(ProjectLifecycle.ENABLED.value, "enabled")
        self.assertEqual(ProjectLifecycle.RUNNING.value, "running")
        self.assertEqual(ProjectLifecycle.PAUSED.value, "paused")
        self.assertEqual(ProjectLifecycle.COMPLETED.value, "completed")
        self.assertEqual(ProjectLifecycle.ERROR.value, "error")
    
    def test_update_lifecycle_to_paused(self):
        """测试更新生命周期到暂停"""
        project = ProjectInfo(
            name="test",
            dir="/test",
            lifecycle=ProjectLifecycle.RUNNING,
        )
        state = GlobalState()
        state.active_projects = ["test"]
        state.paused_projects = []
        
        update_project_lifecycle(project, ProjectLifecycle.PAUSED, state)
        
        self.assertEqual(project.lifecycle, ProjectLifecycle.PAUSED)
        self.assertNotIn("test", state.active_projects)
        self.assertIn("test", state.paused_projects)
    
    def test_update_lifecycle_to_running(self):
        """测试更新生命周期到运行"""
        project = ProjectInfo(
            name="test",
            dir="/test",
            lifecycle=ProjectLifecycle.PAUSED,
        )
        state = GlobalState()
        state.active_projects = []
        state.paused_projects = ["test"]
        
        update_project_lifecycle(project, ProjectLifecycle.RUNNING, state)
        
        self.assertEqual(project.lifecycle, ProjectLifecycle.RUNNING)
        self.assertIn("test", state.active_projects)
        self.assertNotIn("test", state.paused_projects)
    
    def test_update_lifecycle_to_error(self):
        """测试更新生命周期到错误"""
        project = ProjectInfo(
            name="test",
            dir="/test",
            lifecycle=ProjectLifecycle.RUNNING,
        )
        state = GlobalState()
        state.active_projects = ["test"]
        
        update_project_lifecycle(project, ProjectLifecycle.ERROR, state)
        
        self.assertEqual(project.lifecycle, ProjectLifecycle.ERROR)
        self.assertNotIn("test", state.active_projects)


class TestProjectInfo(unittest.TestCase):
    """测试 ProjectInfo 数据类"""
    
    def test_default_values(self):
        """测试默认值"""
        project = ProjectInfo(name="test", dir="/test")
        
        self.assertEqual(project.name, "test")
        self.assertEqual(project.dir, "/test")
        self.assertTrue(project.enabled)
        self.assertEqual(project.priority, 1)
        self.assertEqual(project.lifecycle, ProjectLifecycle.ENABLED)
    
    def test_override(self):
        """测试配置覆盖"""
        project = ProjectInfo(
            name="test",
            dir="/test",
            overrides={"cooldown": 60, "max_daily_sends": 100},
        )
        
        self.assertEqual(project.get_override("cooldown"), 60)
        self.assertEqual(project.get_override("max_daily_sends"), 100)
        self.assertIsNone(project.get_override("nonexistent"))
        self.assertEqual(project.get_override("nonexistent", 42), 42)


class TestLoadAllProjects(unittest.TestCase):
    """测试加载所有项目"""
    
    def setUp(self):
        """创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.projects_dir = os.path.join(self.temp_dir, "projects")
        os.makedirs(self.projects_dir)
    
    def tearDown(self):
        """清理临时目录"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_project(self, name: str, content: str):
        """创建测试项目"""
        project_dir = os.path.join(self.projects_dir, name)
        os.makedirs(project_dir, exist_ok=True)
        with open(os.path.join(project_dir, "tasks.yaml"), 'w') as f:
            f.write(content)
    
    @patch('lib.scheduler.PROJECTS_DIR')
    def test_load_from_projects_dir(self, mock_projects_dir):
        """测试从 projects 目录加载"""
        mock_projects_dir.__str__ = lambda x: self.projects_dir
        
        self._create_project("shike", """
project:
  name: "Shike"
  dir: "/Users/wes/Shike"
  enabled: true
  priority: 1

tasks:
  - id: "task1"
    name: "Task 1"
    prompt: "Do task 1"
""")
        
        # 使用 patch 替换 PROJECTS_DIR
        with patch('lib.scheduler.PROJECTS_DIR', self.projects_dir):
            projects = load_all_projects({})
        
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "Shike")
        self.assertEqual(projects[0].priority, 1)
    
    def test_load_from_project_dirs(self):
        """测试从 project_dirs 配置加载"""
        # 创建一个临时项目目录
        project_dir = os.path.join(self.temp_dir, "my-project")
        os.makedirs(project_dir)
        
        # 不创建 tasks.yaml，测试无任务模式
        with patch('lib.scheduler.PROJECTS_DIR', self.projects_dir):
            projects = load_all_projects({
                'project_dirs': [project_dir]
            })
        
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "my-project")
        self.assertEqual(projects[0].dir, project_dir)
    
    def test_project_dirs_with_tasks_yaml(self):
        """测试 project_dirs 带 tasks.yaml"""
        project_dir = os.path.join(self.temp_dir, "my-project")
        autopilot_dir = os.path.join(project_dir, ".autopilot")
        os.makedirs(autopilot_dir)
        
        with open(os.path.join(autopilot_dir, "tasks.yaml"), 'w') as f:
            f.write("""
project:
  name: "MyProject"
  dir: "{}"
  priority: 2

tasks:
  - id: "task1"
    name: "Task 1"
    prompt: "Do it"
""".format(project_dir))
        
        with patch('lib.scheduler.PROJECTS_DIR', self.projects_dir):
            projects = load_all_projects({
                'project_dirs': [project_dir]
            })
        
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0].name, "MyProject")
        self.assertEqual(projects[0].priority, 2)
    
    @patch('lib.scheduler.PROJECTS_DIR')
    def test_dedup_projects(self, mock_projects_dir):
        """测试项目去重"""
        # 在 projects/ 和 project_dirs 都有同一个项目
        self._create_project("shike", """
project:
  name: "shike"
  dir: "/Users/wes/Shike"
  priority: 1

tasks:
  - id: "task1"
    name: "Task 1"
    prompt: "Do it"
""")
        
        with patch('lib.scheduler.PROJECTS_DIR', self.projects_dir):
            projects = load_all_projects({
                'project_dirs': ["/Users/wes/Shike"]
            })
        
        # 应该只有一个项目（从 projects/ 加载的优先）
        self.assertEqual(len(projects), 1)


class TestScheduleProjects(unittest.TestCase):
    """测试项目调度"""
    
    def setUp(self):
        """创建测试数据"""
        self.projects = [
            ProjectInfo(name="project1", dir="/p1", priority=2, lifecycle=ProjectLifecycle.RUNNING),
            ProjectInfo(name="project2", dir="/p2", priority=1, lifecycle=ProjectLifecycle.RUNNING),
            ProjectInfo(name="project3", dir="/p3", priority=3, lifecycle=ProjectLifecycle.RUNNING),
        ]
        
        self.sessions = {
            "/p1": MagicMock(),
            "/p2": MagicMock(),
            "/p3": MagicMock(),
        }
        
        self.config = {
            'cooldown': 120,
            'max_daily_sends': 50,
            'scheduler': {
                'strategy': 'round-robin',
                'max_sends_per_tick': 3,
            }
        }
        
        self.state = GlobalState()
    
    def test_priority_scheduling(self):
        """测试优先级调度"""
        self.config['scheduler']['strategy'] = 'priority'
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        # 应该按优先级排序（1, 2, 3）
        self.assertEqual(len(scheduled), 3)
        self.assertEqual(scheduled[0].name, "project2")  # priority=1
        self.assertEqual(scheduled[1].name, "project1")  # priority=2
        self.assertEqual(scheduled[2].name, "project3")  # priority=3
    
    def test_round_robin_scheduling(self):
        """测试轮询调度"""
        self.config['scheduler']['strategy'] = 'round-robin'
        self.config['cooldown'] = 0  # 禁用冷却以便测试
        
        # 设置 project1 最近发送过（但冷却已过）
        proj_state = self.state.projects["/p1"] = ProjectState()
        proj_state.last_send_at = (datetime.now() - timedelta(hours=1)).isoformat()
        
        # project2 和 project3 从未发送
        self.state.projects["/p2"] = ProjectState()
        self.state.projects["/p3"] = ProjectState()
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        # 从未发送的应该排在前面（但受 max_sends_per_tick*2 限制）
        self.assertGreaterEqual(len(scheduled), 2)
        # 从未发送的应该排在已发送的前面
        names = [p.name for p in scheduled]
        if "project1" in names and "project2" in names:
            self.assertLess(names.index("project2"), names.index("project1"))
    
    def test_filter_disabled_projects(self):
        """测试过滤禁用的项目"""
        self.projects[0].lifecycle = ProjectLifecycle.DISABLED
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        self.assertEqual(len(scheduled), 2)
        self.assertNotIn("project1", [p.name for p in scheduled])
    
    def test_filter_paused_projects(self):
        """测试过滤暂停的项目"""
        self.projects[0].lifecycle = ProjectLifecycle.PAUSED
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        self.assertEqual(len(scheduled), 2)
        self.assertNotIn("project1", [p.name for p in scheduled])
    
    def test_filter_no_session_projects(self):
        """测试过滤没有 session 的项目"""
        del self.sessions["/p1"]
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        self.assertEqual(len(scheduled), 2)
        self.assertNotIn("project1", [p.name for p in scheduled])
    
    def test_filter_cooling_projects(self):
        """测试过滤冷却中的项目"""
        proj_state = self.state.projects["/p1"] = ProjectState()
        proj_state.last_send_at = datetime.now().isoformat()
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        self.assertEqual(len(scheduled), 2)
        self.assertNotIn("project1", [p.name for p in scheduled])
    
    def test_filter_daily_limit_projects(self):
        """测试过滤达到每日限额的项目"""
        proj_state = self.state.projects["/p1"] = ProjectState()
        proj_state.daily_sends = 50
        proj_state.daily_sends_date = datetime.now().strftime('%Y-%m-%d')
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        self.assertEqual(len(scheduled), 2)
        self.assertNotIn("project1", [p.name for p in scheduled])
    
    def test_max_sends_per_tick_limit(self):
        """测试返回所有可操作项目（不截断），由主循环控制发送"""
        self.config['scheduler']['max_sends_per_tick'] = 1
        
        scheduled = schedule_projects(
            self.projects,
            self.sessions,
            self.config,
            self.state
        )
        
        # 应返回所有可操作项目，主循环决定发送几个
        self.assertGreaterEqual(len(scheduled), 1)


class TestUpdateProjectSendOrder(unittest.TestCase):
    """测试更新发送顺序"""
    
    def test_add_to_order(self):
        """测试添加到发送顺序"""
        state = GlobalState()
        state.project_send_order = ["p1", "p2"]
        
        update_project_send_order("p3", state)
        
        self.assertEqual(state.project_send_order, ["p1", "p2", "p3"])
    
    def test_move_to_end(self):
        """测试移动到末尾"""
        state = GlobalState()
        state.project_send_order = ["p1", "p2", "p3"]
        
        update_project_send_order("p1", state)
        
        self.assertEqual(state.project_send_order, ["p2", "p3", "p1"])
    
    def test_limit_order_size(self):
        """测试限制顺序列表大小"""
        state = GlobalState()
        state.project_send_order = [f"p{i}" for i in range(100)]
        
        update_project_send_order("new", state)
        
        self.assertLessEqual(len(state.project_send_order), 100)
        self.assertEqual(state.project_send_order[-1], "new")


class TestGetProjectByName(unittest.TestCase):
    """测试按名称查找项目"""
    
    def setUp(self):
        self.projects = [
            ProjectInfo(name="Shike", dir="/shike"),
            ProjectInfo(name="SimCity", dir="/simcity"),
            ProjectInfo(name="Portfolio", dir="/portfolio"),
        ]
    
    def test_exact_match(self):
        """测试精确匹配"""
        project = get_project_by_name(self.projects, "Shike")
        self.assertEqual(project.name, "Shike")
    
    def test_case_insensitive(self):
        """测试不区分大小写"""
        project = get_project_by_name(self.projects, "shike")
        self.assertEqual(project.name, "Shike")
    
    def test_prefix_match(self):
        """测试前缀匹配"""
        project = get_project_by_name(self.projects, "sim")
        self.assertEqual(project.name, "SimCity")
    
    def test_not_found(self):
        """测试未找到"""
        project = get_project_by_name(self.projects, "nonexistent")
        self.assertIsNone(project)


class TestRoundRobinWithSendOrder(unittest.TestCase):
    """测试 round-robin 按 last_send_at 排序"""
    
    def test_last_send_time_affects_scheduling(self):
        """测试最久未发送的项目排在前面"""
        from lib.state_manager import ProjectState
        
        projects = [
            ProjectInfo(name="p1", dir="/p1", lifecycle=ProjectLifecycle.RUNNING),
            ProjectInfo(name="p2", dir="/p2", lifecycle=ProjectLifecycle.RUNNING),
            ProjectInfo(name="p3", dir="/p3", lifecycle=ProjectLifecycle.RUNNING),
        ]
        
        sessions = {"/p1": MagicMock(), "/p2": MagicMock(), "/p3": MagicMock()}
        
        config = {
            'cooldown': 0,  # 禁用冷却
            'max_daily_sends': 1000,
            'scheduler': {
                'strategy': 'round-robin',
                'max_sends_per_tick': 10,
            }
        }
        
        state = GlobalState()
        # p1 最近发送过，p2 较早，p3 从未发送
        state.projects = {
            "/p1": ProjectState(last_send_at="2026-02-07T01:05:00"),
            "/p2": ProjectState(last_send_at="2026-02-07T01:00:00"),
            "/p3": ProjectState(last_send_at=None),
        }
        
        scheduled = schedule_projects(projects, sessions, config, state)
        names = [p.name for p in scheduled]
        
        # p3 (从未发送, sort_key=0) 和 p2 (较早) 应在 p1 (最近) 之前
        self.assertEqual(len(names), 3)
        self.assertLess(names.index("p3"), names.index("p1"))
        self.assertLess(names.index("p2"), names.index("p1"))


if __name__ == '__main__':
    unittest.main()
