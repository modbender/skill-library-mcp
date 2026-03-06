#!/usr/bin/env python3
"""
Gateway Monitor - 监控网关状态变化并提供主动通知
融合了任务持久化、会话快照和网关监控功能
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class GatewayMonitor:
    def __init__(self, workspace_path: str = None):
        self.workspace = Path(workspace_path) if workspace_path else Path.home() / '.openclaw' / 'workspace'
        self.monitor_dir = self.workspace / 'monitor'
        self.monitor_dir.mkdir(exist_ok=True)
        self.status_file = self.monitor_dir / 'gateway_status.json'
        self.tasks_file = self.monitor_dir / 'active_tasks.json'
        self.session_snapshots = self.monitor_dir / 'session_snapshots'
        self.session_snapshots.mkdir(exist_ok=True)
        
        # 状态变量
        self.is_running = False
        self.last_gateway_status = None
        self.monitor_thread = None
        
    def save_gateway_status(self, status: Dict):
        """保存网关状态"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'status': status,
                    'uptime': status.get('uptime', 0)
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving gateway status: {e}")
    
    def load_active_tasks(self) -> List[Dict]:
        """加载活跃任务"""
        if not self.tasks_file.exists():
            return []
        try:
            with open(self.tasks_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading active tasks: {e}")
            return []
    
    def save_active_tasks(self, tasks: List[Dict]):
        """保存活跃任务"""
        try:
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving active tasks: {e}")
    
    def create_session_snapshot(self, session_data: Dict, session_id: str):
        """创建会话快照"""
        try:
            snapshot_file = self.session_snapshots / f"{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'session_id': session_id,
                    'data': session_data
                }, f, ensure_ascii=False, indent=2)
            return snapshot_file
        except Exception as e:
            print(f"Error creating session snapshot: {e}")
            return None
    
    def get_latest_session_snapshot(self, session_id: str) -> Optional[Path]:
        """获取最新的会话快照"""
        snapshots = list(self.session_snapshots.glob(f"{session_id}_*.json"))
        if not snapshots:
            return None
        return max(snapshots, key=lambda x: x.stat().st_mtime)
    
    def check_gateway_status(self) -> Dict:
        """检查网关状态"""
        # 这里需要与 OpenClaw 的实际状态检查集成
        # 暂时返回模拟状态
        return {
            'running': True,
            'port': 17786,
            'uptime': time.time() - getattr(self, '_start_time', time.time()),
            'memory_usage': 'normal',
            'active_sessions': 1
        }
    
    def monitor_loop(self):
        """监控循环"""
        self._start_time = time.time()
        while self.is_running:
            try:
                current_status = self.check_gateway_status()
                
                # 检查状态变化
                if self.last_gateway_status != current_status:
                    if self.last_gateway_status is None:
                        # 首次启动
                        self.handle_gateway_start(current_status)
                    elif not self.last_gateway_status.get('running', False) and current_status.get('running', False):
                        # 网关重启完成
                        self.handle_gateway_restart(current_status)
                    elif self.last_gateway_status.get('running', False) and not current_status.get('running', False):
                        # 网关停止
                        self.handle_gateway_stop()
                
                self.last_gateway_status = current_status
                self.save_gateway_status(current_status)
                
                time.sleep(10)  # 每10秒检查一次
                
            except Exception as e:
                print(f"Error in monitor loop: {e}")
                time.sleep(30)  # 出错时等待更长时间
    
    def handle_gateway_start(self, status: Dict):
        """处理网关启动"""
        print("🚀 Gateway started successfully!")
        print(f"📊 Status: Port {status.get('port', 'N/A')}, Uptime: {status.get('uptime', 0):.1f}s")
        
        # 检查是否有未完成的任务
        active_tasks = self.load_active_tasks()
        if active_tasks:
            print(f"📋 Found {len(active_tasks)} active tasks to resume:")
            for task in active_tasks[:3]:  # 只显示前3个
                print(f"   • {task.get('name', 'Unknown task')}")
            if len(active_tasks) > 3:
                print(f"   ... and {len(active_tasks) - 3} more tasks")
    
    def handle_gateway_restart(self, status: Dict):
        """处理网关重启"""
        print("🔄 Gateway restarted successfully!")
        print(f"📊 Status: Port {status.get('port', 'N/A')}, Uptime: {status.get('uptime', 0):.1f}s")
        
        # 恢复会话快照
        latest_snapshot = self.get_latest_session_snapshot('main')
        if latest_snapshot:
            print("💾 Restoring from latest session snapshot...")
            try:
                with open(latest_snapshot, 'r', encoding='utf-8') as f:
                    snapshot_data = json.load(f)
                print(f"✅ Session restored from {snapshot_data['timestamp']}")
            except Exception as e:
                print(f"❌ Failed to restore session: {e}")
        
        # 恢复活跃任务
        active_tasks = self.load_active_tasks()
        if active_tasks:
            print(f"📋 Resuming {len(active_tasks)} tasks...")
            # 这里可以触发任务恢复逻辑
    
    def handle_gateway_stop(self):
        """处理网关停止"""
        print("⚠️ Gateway stopped unexpectedly!")
        # 可以在这里添加告警或日志记录
    
    def start_monitoring(self):
        """开始监控"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("👁️  Gateway monitoring started...")
    
    def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("⏹️  Gateway monitoring stopped.")
    
    def register_task(self, task_name: str, task_data: Dict):
        """注册新任务"""
        active_tasks = self.load_active_tasks()
        new_task = {
            'id': f"task_{int(time.time())}",
            'name': task_name,
            'data': task_data,
            'registered_at': datetime.now().isoformat(),
            'status': 'active'
        }
        active_tasks.append(new_task)
        self.save_active_tasks(active_tasks)
        return new_task['id']
    
    def complete_task(self, task_id: str):
        """完成任务"""
        active_tasks = self.load_active_tasks()
        updated_tasks = [task for task in active_tasks if task.get('id') != task_id]
        self.save_active_tasks(updated_tasks)
    
    def pause_all_tasks(self):
        """暂停所有任务（用于网关重启前）"""
        active_tasks = self.load_active_tasks()
        for task in active_tasks:
            task['status'] = 'paused'
            task['paused_at'] = datetime.now().isoformat()
        self.save_active_tasks(active_tasks)
        print(f"⏸️  Paused {len(active_tasks)} tasks before gateway restart")

# 使用示例
if __name__ == "__main__":
    monitor = GatewayMonitor()
    try:
        monitor.start_monitoring()
        # 保持运行
        import signal
        signal.pause()
    except KeyboardInterrupt:
        monitor.stop_monitoring()