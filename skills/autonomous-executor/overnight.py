"""
OvernightRunner — Run tasks overnight with full progress logging and summaries.

This wraps the AutonomousExecutor for overnight batch processing with:
- Task queue management
- Scheduled execution
- Progress logging to MongoDB
- Morning summary reports
- Email/notification hooks (optional)

Usage:
    from autonomous_executor.overnight import OvernightRunner
    
    runner = OvernightRunner()
    
    # Queue tasks
    runner.queue("deploy", name="my-portfolio", type="portfolio")
    runner.queue("research", query="quantum computing trends")
    runner.queue("custom", fn=my_function, args=(1, 2, 3))
    
    # Run all queued tasks
    runner.run_all()
    
    # Get morning summary
    summary = runner.get_summary()
"""

import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

# Add parent to path for imports
_skill_dir = Path(__file__).parent
sys.path.insert(0, str(_skill_dir))
sys.path.insert(0, str(_skill_dir.parent))

from executor import AutonomousExecutor, TaskStatus
try:
    from common.mongo import get_collection, is_connected
    MONGO_AVAILABLE = is_connected()
except ImportError:
    MONGO_AVAILABLE = False
    def get_collection(name): return None


@dataclass
class QueuedTask:
    """A task queued for overnight execution."""
    task_id: str
    task_type: str  # deploy, research, custom
    params: Dict
    priority: int = 0  # Higher = run first
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "queued"
    result: Optional[Dict] = None


class OvernightRunner:
    """
    Manages overnight batch task execution.
    
    Designed to run tasks while you sleep with full logging and summaries.
    """
    
    def __init__(self, user: str = "default"):
        self.user = user
        self.executor = AutonomousExecutor(user=user)
        self.queue: List[QueuedTask] = []
        self.run_id = f"overnight_{int(time.time())}"
        self._load_persistent_queue()
    
    def _load_persistent_queue(self):
        """Load any persisted queued tasks from MongoDB."""
        col = get_collection("overnight_queue")
        if col is None:
            return
        
        try:
            docs = col.find({"user": self.user, "status": "queued"})
            for doc in docs:
                task = QueuedTask(
                    task_id=doc["task_id"],
                    task_type=doc["task_type"],
                    params=doc["params"],
                    priority=doc.get("priority", 0),
                    created_at=doc.get("created_at", datetime.now(timezone.utc)),
                    status=doc.get("status", "queued")
                )
                self.queue.append(task)
        except:
            pass
    
    def _save_queue(self):
        """Persist queue to MongoDB."""
        col = get_collection("overnight_queue")
        if col is None:
            return
        
        try:
            for task in self.queue:
                col.update_one(
                    {"task_id": task.task_id},
                    {"$set": {
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "params": task.params,
                        "priority": task.priority,
                        "created_at": task.created_at,
                        "status": task.status,
                        "user": self.user
                    }},
                    upsert=True
                )
        except:
            pass
    
    def _log_progress(self, message: str, task_id: str = None):
        """Log progress to console and MongoDB."""
        timestamp = datetime.now(timezone.utc)
        ts_str = timestamp.strftime("%H:%M:%S")
        print(f"[{ts_str}] {message}")
        
        col = get_collection("overnight_logs")
        if col is not None:
            try:
                col.insert_one({
                    "run_id": self.run_id,
                    "task_id": task_id,
                    "timestamp": timestamp,
                    "message": message,
                    "user": self.user
                })
            except:
                pass
    
    def queue_deploy(self, name: str, project_type: str = "nextjs",
                     description: str = "", priority: int = 0, **extra) -> str:
        """Queue a project deployment."""
        task_id = f"deploy_{name}_{int(time.time())}"
        task = QueuedTask(
            task_id=task_id,
            task_type="deploy",
            params={
                "name": name,
                "type": project_type,
                "description": description,
                "extra": extra
            },
            priority=priority
        )
        self.queue.append(task)
        self._save_queue()
        self._log_progress(f"📋 Queued deploy: {name} ({project_type})", task_id)
        return task_id
    
    def queue_research(self, query: str, depth: str = "deep",
                       priority: int = 0) -> str:
        """Queue a research task."""
        task_id = f"research_{hash(query) % 10000}_{int(time.time())}"
        task = QueuedTask(
            task_id=task_id,
            task_type="research",
            params={
                "query": query,
                "depth": depth
            },
            priority=priority
        )
        self.queue.append(task)
        self._save_queue()
        self._log_progress(f"📋 Queued research: {query[:50]}...", task_id)
        return task_id
    
    def queue_custom(self, fn: Callable, args: tuple = (), kwargs: dict = None,
                     task_name: str = "Custom Task", priority: int = 0) -> str:
        """Queue a custom function for execution."""
        kwargs = kwargs or {}
        task_id = f"custom_{task_name.replace(' ', '_')}_{int(time.time())}"
        
        # Note: For custom functions, we store a reference not the actual function
        # This means the function must be importable or the caller must handle it
        task = QueuedTask(
            task_id=task_id,
            task_type="custom",
            params={
                "task_name": task_name,
                "fn_name": fn.__name__ if hasattr(fn, '__name__') else "anonymous",
                "_fn_ref": fn,  # Not persisted, only for current session
                "args": args,
                "kwargs": kwargs
            },
            priority=priority
        )
        self.queue.append(task)
        self._log_progress(f"📋 Queued custom: {task_name}", task_id)
        return task_id
    
    def queue(self, task_type: str, **kwargs) -> str:
        """Generic queue method - dispatches to specific methods."""
        if task_type == "deploy":
            return self.queue_deploy(
                name=kwargs.get("name", "my-project"),
                project_type=kwargs.get("type", "nextjs"),
                description=kwargs.get("description", ""),
                priority=kwargs.get("priority", 0),
                **{k: v for k, v in kwargs.items() 
                   if k not in ["name", "type", "description", "priority"]}
            )
        elif task_type == "research":
            return self.queue_research(
                query=kwargs.get("query", ""),
                depth=kwargs.get("depth", "deep"),
                priority=kwargs.get("priority", 0)
            )
        elif task_type == "custom":
            return self.queue_custom(
                fn=kwargs.get("fn"),
                args=kwargs.get("args", ()),
                kwargs=kwargs.get("kwargs", {}),
                task_name=kwargs.get("task_name", "Custom Task"),
                priority=kwargs.get("priority", 0)
            )
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    def _execute_task(self, task: QueuedTask) -> Dict:
        """Execute a single queued task."""
        self._log_progress(f"🚀 Starting: {task.task_type} - {task.task_id}", task.task_id)
        
        start_time = time.time()
        result = {"task_id": task.task_id, "task_type": task.task_type}
        
        try:
            if task.task_type == "deploy":
                result = self.executor.run_project_pipeline(task.params)
            
            elif task.task_type == "research":
                result = self.executor.run_research_pipeline(
                    task.params["query"],
                    task.params.get("depth", "deep")
                )
            
            elif task.task_type == "custom":
                fn = task.params.get("_fn_ref")
                if fn:
                    result = self.executor.execute(
                        fn,
                        args=task.params.get("args", ()),
                        kwargs=task.params.get("kwargs", {}),
                        task_name=task.params.get("task_name", "Custom Task")
                    )
                else:
                    result = {"success": False, "error": "Function reference lost (not persisted)"}
            
            else:
                result = {"success": False, "error": f"Unknown task type: {task.task_type}"}
        
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
        
        duration = time.time() - start_time
        result["duration"] = duration
        result["task_id"] = task.task_id
        
        task.status = "completed" if result.get("success") else "failed"
        task.result = result
        
        # Log result
        status_emoji = "✅" if result.get("success") else "❌"
        self._log_progress(
            f"{status_emoji} Finished {task.task_id} in {duration:.1f}s",
            task.task_id
        )
        
        # Update in MongoDB
        col = get_collection("overnight_queue")
        if col is not None:
            try:
                col.update_one(
                    {"task_id": task.task_id},
                    {"$set": {
                        "status": task.status,
                        "result": result,
                        "completed_at": datetime.now(timezone.utc)
                    }}
                )
            except:
                pass
        
        return result
    
    def run_all(self, max_concurrent: int = 1) -> Dict:
        """
        Run all queued tasks.
        
        Args:
            max_concurrent: Max tasks to run at once (1 = sequential)
        
        Returns:
            Summary of execution results
        """
        if not self.queue:
            self._log_progress("📭 No tasks in queue")
            return {"tasks": 0, "completed": 0, "failed": 0}
        
        # Sort by priority (higher first)
        self.queue.sort(key=lambda t: t.priority, reverse=True)
        
        self._log_progress(f"🌙 Starting overnight run: {len(self.queue)} tasks")
        self._log_progress(f"   Run ID: {self.run_id}")
        
        start_time = time.time()
        results = []
        completed = 0
        failed = 0
        
        # Save run start to MongoDB
        col = get_collection("overnight_runs")
        if col is not None:
            try:
                col.insert_one({
                    "run_id": self.run_id,
                    "user": self.user,
                    "started_at": datetime.now(timezone.utc),
                    "total_tasks": len(self.queue),
                    "status": "running"
                })
            except:
                pass
        
        # Execute tasks sequentially (can be parallelized later)
        for task in self.queue:
            if task.status != "queued":
                continue
            
            result = self._execute_task(task)
            results.append(result)
            
            if result.get("success"):
                completed += 1
            else:
                failed += 1
        
        total_duration = time.time() - start_time
        
        summary = {
            "run_id": self.run_id,
            "total_tasks": len(self.queue),
            "completed": completed,
            "failed": failed,
            "success_rate": f"{completed/len(self.queue)*100:.1f}%" if self.queue else "N/A",
            "total_duration": total_duration,
            "results": results
        }
        
        # Save run completion
        col = get_collection("overnight_runs")
        if col is not None:
            try:
                col.update_one(
                    {"run_id": self.run_id},
                    {"$set": {
                        "status": "completed",
                        "completed_at": datetime.now(timezone.utc),
                        "summary": summary
                    }}
                )
            except:
                pass
        
        self._log_progress(f"🌅 Overnight run complete!")
        self._log_progress(f"   Total: {len(self.queue)} | ✅ {completed} | ❌ {failed}")
        self._log_progress(f"   Duration: {total_duration/60:.1f} minutes")
        
        # Clear completed tasks from queue
        self.queue = [t for t in self.queue if t.status == "queued"]
        
        return summary
    
    def get_summary(self, run_id: str = None) -> Dict:
        """Get summary of a specific run or the most recent run."""
        col = get_collection("overnight_runs")
        if col is None:
            return {"error": "MongoDB not available"}
        
        try:
            if run_id:
                doc = col.find_one({"run_id": run_id})
            else:
                doc = col.find_one(
                    {"user": self.user},
                    sort=[("started_at", -1)]
                )
            
            if doc:
                return doc.get("summary", doc)
            return {"error": "No runs found"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_morning_report(self) -> str:
        """Generate a human-readable morning report."""
        summary = self.get_summary()
        
        if "error" in summary:
            return f"⚠️ Could not generate report: {summary['error']}"
        
        lines = [
            "🌅 **Good Morning! Here's your overnight report:**",
            "",
            f"**Run:** {summary.get('run_id', 'Unknown')}",
            f"**Tasks:** {summary.get('total_tasks', 0)}",
            f"**Completed:** {summary.get('completed', 0)} ✅",
            f"**Failed:** {summary.get('failed', 0)} ❌",
            f"**Success Rate:** {summary.get('success_rate', 'N/A')}",
            f"**Duration:** {summary.get('total_duration', 0)/60:.1f} minutes",
            ""
        ]
        
        # Add details for failed tasks
        results = summary.get("results", [])
        failed_results = [r for r in results if not r.get("success")]
        
        if failed_results:
            lines.append("**Failed Tasks:**")
            for r in failed_results:
                lines.append(f"  - {r.get('task_id', 'Unknown')}: {r.get('error', 'Unknown error')[:100]}")
        
        # Add details for successful deployments
        deploy_results = [r for r in results if r.get("success") and "vercel_url" in r.get("result", {})]
        if deploy_results:
            lines.append("\n**Deployed Projects:**")
            for r in deploy_results:
                result = r.get("result", {})
                lines.append(f"  - {result.get('name', 'Unknown')}: {result.get('vercel_url', '')}")
        
        return "\n".join(lines)
    
    def status(self) -> Dict:
        """Get current queue status."""
        return {
            "queue_length": len(self.queue),
            "queued": len([t for t in self.queue if t.status == "queued"]),
            "completed": len([t for t in self.queue if t.status == "completed"]),
            "failed": len([t for t in self.queue if t.status == "failed"]),
            "tasks": [
                {
                    "id": t.task_id,
                    "type": t.task_type,
                    "status": t.status,
                    "priority": t.priority
                }
                for t in self.queue
            ]
        }
    
    def clear_queue(self):
        """Clear all queued tasks."""
        self.queue = []
        col = get_collection("overnight_queue")
        if col is not None:
            try:
                col.delete_many({"user": self.user, "status": "queued"})
            except:
                pass
        self._log_progress("🗑️ Queue cleared")


# Convenience interface
class Overnight:
    """Quick overnight execution interface."""
    
    _runner: OvernightRunner = None
    
    @classmethod
    def _get_runner(cls) -> OvernightRunner:
        if cls._runner is None:
            cls._runner = OvernightRunner()
        return cls._runner
    
    @classmethod
    def deploy(cls, name: str, project_type: str = "nextjs", **kwargs) -> str:
        """Queue a deployment."""
        return cls._get_runner().queue_deploy(name, project_type, **kwargs)
    
    @classmethod
    def research(cls, query: str, **kwargs) -> str:
        """Queue research."""
        return cls._get_runner().queue_research(query, **kwargs)
    
    @classmethod
    def run(cls, fn: Callable, *args, **kwargs) -> str:
        """Queue a custom function."""
        task_name = kwargs.pop("_name", fn.__name__)
        return cls._get_runner().queue_custom(fn, args, kwargs, task_name)
    
    @classmethod
    def start(cls) -> Dict:
        """Start running all queued tasks."""
        return cls._get_runner().run_all()
    
    @classmethod
    def report(cls) -> str:
        """Get morning report."""
        return cls._get_runner().get_morning_report()
    
    @classmethod
    def status(cls) -> Dict:
        """Get queue status."""
        return cls._get_runner().status()
    
    @classmethod
    def clear(cls):
        """Clear queue."""
        return cls._get_runner().clear_queue()


if __name__ == "__main__":
    print("Testing OvernightRunner...")
    
    runner = OvernightRunner()
    
    # Queue some test tasks
    def test_task():
        time.sleep(1)
        return "Test completed!"
    
    runner.queue_custom(test_task, task_name="Test Task 1")
    runner.queue_custom(test_task, task_name="Test Task 2")
    
    print(f"\nQueue status: {runner.status()}")
    
    # Run them
    summary = runner.run_all()
    print(f"\nSummary: {summary}")
    
    # Morning report
    print(f"\n{runner.get_morning_report()}")
