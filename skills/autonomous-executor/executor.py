"""
AutonomousExecutor — Self-healing, error-recovering task execution.

This skill wraps any long-running task with:
- Automatic error detection and categorization
- Smart retry with exponential backoff
- Self-healing for common error patterns
- Checkpoint/resume for multi-step tasks
- Overnight progress logging with MongoDB persistence
- Full awareness of all OpenClaw capabilities

Usage:
    from autonomous_executor.executor import AutonomousExecutor
    
    executor = AutonomousExecutor()
    
    # Execute any function with auto-recovery
    result = executor.execute(
        task_fn=my_long_running_function,
        args=(...),
        task_name="Build and deploy portfolio",
        max_retries=5
    )
    
    # Run a complete project pipeline
    result = executor.run_project_pipeline(
        project_spec={
            "name": "my-portfolio",
            "type": "portfolio",
            "description": "My awesome portfolio"
        }
    )
"""

import sys
import time
import re
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps

# Use centralized MongoDB module
sys.path.insert(0, str(Path(__file__).parent.parent))
try:
    from common.mongo import get_collection, is_connected
    MONGO_AVAILABLE = is_connected()
except ImportError:
    MONGO_AVAILABLE = False
    def get_collection(name): return None


class ErrorCategory(Enum):
    """Categorize errors for targeted recovery strategies."""
    NETWORK = "network"           # Timeout, connection refused, DNS
    AUTH = "auth"                 # API key expired, unauthorized
    RATE_LIMIT = "rate_limit"     # Too many requests, quota exceeded
    RESOURCE = "resource"         # File not found, memory, disk space
    VALIDATION = "validation"     # Invalid input, schema mismatch
    DEPENDENCY = "dependency"     # Missing module, import error
    BROWSER = "browser"           # Playwright/browser errors
    API = "api"                   # API returned error response
    UNKNOWN = "unknown"           # Uncategorized


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    RETRYING = "retrying"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"
    CHECKPOINT = "checkpoint"


@dataclass
class ExecutionLog:
    """Single execution attempt log."""
    attempt: int
    timestamp: datetime
    status: str
    error: Optional[str] = None
    error_category: Optional[str] = None
    recovery_action: Optional[str] = None
    duration_seconds: float = 0.0
    output: Optional[Any] = None


@dataclass
class TaskRecord:
    """Complete record of a task execution."""
    task_id: str
    task_name: str
    created_at: datetime
    updated_at: datetime
    status: TaskStatus
    total_attempts: int = 0
    max_retries: int = 5
    execution_logs: List[ExecutionLog] = field(default_factory=list)
    checkpoints: List[Dict] = field(default_factory=list)
    final_result: Optional[Any] = None
    final_error: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


# Error pattern matching for auto-categorization
ERROR_PATTERNS = {
    ErrorCategory.NETWORK: [
        "timeout", "timed out", "connection refused", "connection reset",
        "network unreachable", "dns", "socket", "ssl", "certificate",
        "connectionerror", "readtimeout", "connecttimeout", "econnrefused"
    ],
    ErrorCategory.AUTH: [
        "unauthorized", "401", "403", "forbidden", "invalid token",
        "expired", "authentication", "not authenticated", "access denied",
        "invalid api key", "api key", "credentials"
    ],
    ErrorCategory.RATE_LIMIT: [
        "rate limit", "too many requests", "429", "quota exceeded",
        "throttled", "slow down", "retry after", "backoff"
    ],
    ErrorCategory.RESOURCE: [
        "file not found", "no such file", "directory not found",
        "permission denied", "disk full", "out of memory", "oom",
        "filenotfounderror", "oserror", "ioerror"
    ],
    ErrorCategory.VALIDATION: [
        "invalid", "validation error", "schema", "required field",
        "type error", "value error", "keyerror", "missing key"
    ],
    ErrorCategory.DEPENDENCY: [
        "modulenotfounderror", "importerror", "no module named",
        "package not found", "cannot import", "dependency"
    ],
    ErrorCategory.BROWSER: [
        "playwright", "browser", "page crashed", "execution context",
        "target closed", "navigation", "selector", "element not found",
        "chromium", "firefox", "webkit", "frame detached"
    ],
    ErrorCategory.API: [
        "api error", "500", "502", "503", "504", "bad gateway",
        "service unavailable", "internal server error", "json decode"
    ]
}


# Recovery strategies for each error category
RECOVERY_STRATEGIES = {
    ErrorCategory.NETWORK: [
        ("wait_and_retry", {"wait_multiplier": 2.0, "max_wait": 60}),
        ("check_connectivity", {}),
        ("try_alternate_endpoint", {}),
    ],
    ErrorCategory.AUTH: [
        ("refresh_credentials", {}),
        ("prompt_reauth", {}),  # Last resort - notify for manual intervention
    ],
    ErrorCategory.RATE_LIMIT: [
        ("wait_and_retry", {"wait_multiplier": 3.0, "max_wait": 120}),
        ("use_backoff_header", {}),  # Use Retry-After if present
    ],
    ErrorCategory.RESOURCE: [
        ("create_missing_resource", {}),
        ("clean_temp_files", {}),
        ("expand_path", {}),
    ],
    ErrorCategory.VALIDATION: [
        ("auto_fix_input", {}),
        ("use_defaults", {}),
    ],
    ErrorCategory.DEPENDENCY: [
        ("install_dependency", {}),
        ("try_alternate_import", {}),
    ],
    ErrorCategory.BROWSER: [
        ("restart_browser", {}),
        ("wait_and_retry", {"wait_multiplier": 1.5, "max_wait": 30}),
        ("reduce_concurrency", {}),
    ],
    ErrorCategory.API: [
        ("wait_and_retry", {"wait_multiplier": 2.0, "max_wait": 45}),
        ("try_alternate_api", {}),
    ],
    ErrorCategory.UNKNOWN: [
        ("wait_and_retry", {"wait_multiplier": 1.5, "max_wait": 30}),
        ("log_and_continue", {}),
    ],
}


class AutonomousExecutor:
    """Self-healing task executor with automatic error recovery."""
    
    def __init__(self, user: str = "default"):
        self.user = user
        self.current_task: Optional[TaskRecord] = None
        self._browser_context = None
        self._recovery_attempts = {}
        
        # Load available capabilities
        self.capabilities = self._discover_capabilities()
    
    def _discover_capabilities(self) -> Dict[str, Any]:
        """Discover all available OpenClaw capabilities."""
        caps = {
            "skills": [],
            "apis": {},
            "agents": [],
            "tools": []
        }
        
        skills_dir = Path(__file__).parent.parent
        if skills_dir.exists():
            for d in skills_dir.iterdir():
                if d.is_dir() and not d.name.startswith(('_', '.')):
                    skill_md = d / "SKILL.md"
                    caps["skills"].append({
                        "name": d.name,
                        "path": str(d),
                        "has_doc": skill_md.exists()
                    })
        
        # Check for web agent
        web_agent_path = skills_dir.parent / "src" / "skills" / "web-agent"
        if web_agent_path.exists():
            caps["agents"].append({
                "name": "web-agent",
                "description": "Full browser automation with Playwright"
            })
        
        # Check project deployer
        deployer_path = skills_dir / "project-deployer"
        if deployer_path.exists():
            caps["tools"].append({
                "name": "project-deployer",
                "functions": ["build_and_deploy", "scaffold", "push_to_github", "deploy_to_vercel"]
            })
        
        # Check free APIs
        api_intel_path = skills_dir / "api-intel"
        if api_intel_path.exists():
            caps["apis"] = {
                "crypto": ["coingecko", "fear_greed_index"],
                "news": ["hackernews", "reddit"],
                "weather": ["wttr.in"],
                "knowledge": ["wikipedia"],
                "quotes": ["zenquotes"]
            }
        
        return caps
    
    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize an error for targeted recovery."""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        full_text = f"{error_type} {error_str}"
        
        for category, patterns in ERROR_PATTERNS.items():
            for pattern in patterns:
                if pattern in full_text:
                    return category
        
        return ErrorCategory.UNKNOWN
    
    def _get_recovery_strategy(self, category: ErrorCategory, attempt: int) -> Optional[tuple]:
        """Get the appropriate recovery strategy for an error category and attempt."""
        strategies = RECOVERY_STRATEGIES.get(category, RECOVERY_STRATEGIES[ErrorCategory.UNKNOWN])
        
        # Cycle through strategies based on attempt number
        if attempt <= len(strategies):
            return strategies[attempt - 1]
        return None
    
    def _execute_recovery(self, strategy: str, params: dict, error: Exception, context: dict) -> bool:
        """Execute a recovery strategy. Returns True if recovery succeeded."""
        
        if strategy == "wait_and_retry":
            wait_time = min(
                params.get("wait_multiplier", 2.0) ** context.get("attempt", 1) * 2,
                params.get("max_wait", 60)
            )
            self._log(f"⏳ Waiting {wait_time:.1f}s before retry...")
            time.sleep(wait_time)
            return True
        
        elif strategy == "check_connectivity":
            import subprocess
            try:
                subprocess.run(["ping", "-c", "1", "8.8.8.8"], 
                             capture_output=True, timeout=5)
                return True
            except:
                self._log("❌ Network connectivity check failed")
                return False
        
        elif strategy == "restart_browser":
            self._log("🔄 Restarting browser context...")
            try:
                if self._browser_context:
                    self._browser_context.close()
                self._browser_context = None
                time.sleep(2)
                return True
            except:
                return False
        
        elif strategy == "install_dependency":
            # Try to extract module name and install
            error_str = str(error)
            import re
            match = re.search(r"No module named ['\"]([^'\"]+)['\"]", error_str)
            if match:
                module = match.group(1).split('.')[0]
                self._log(f"📦 Installing missing module: {module}")
                import subprocess
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", module],
                                 capture_output=True, timeout=60)
                    return True
                except:
                    return False
            return False
        
        elif strategy == "create_missing_resource":
            # Try to create missing file/directory
            error_str = str(error)
            import re
            match = re.search(r"(?:No such file or directory|FileNotFoundError)[:\s]+['\"]?([^'\"]+)['\"]?", error_str)
            if match:
                path = Path(match.group(1))
                if '.' in path.name:  # It's a file
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.touch()
                else:  # It's a directory
                    path.mkdir(parents=True, exist_ok=True)
                self._log(f"📁 Created missing resource: {path}")
                return True
            return False
        
        elif strategy == "clean_temp_files":
            import tempfile
            import shutil
            temp_dir = Path(tempfile.gettempdir()) / "openclaw_temp"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            return True
        
        elif strategy == "auto_fix_input":
            # Placeholder - would analyze error and suggest fixes
            self._log("🔧 Attempting to auto-fix input...")
            return True
        
        elif strategy == "log_and_continue":
            self._log(f"📝 Logged error and continuing: {error}")
            return True
        
        elif strategy == "use_defaults":
            return True
        
        return False
    
    def _log(self, message: str, level: str = "info"):
        """Log message to console and MongoDB."""
        timestamp = datetime.now(timezone.utc)
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "message": message,
            "task_id": self.current_task.task_id if self.current_task else None,
            "user": self.user
        }
        
        # Console output with timestamp
        ts_str = timestamp.strftime("%H:%M:%S")
        print(f"[{ts_str}] {message}")
        
        # Persist to MongoDB
        if MONGO_AVAILABLE:
            col = get_collection("execution_logs")
            if col is not None:
                try:
                    col.insert_one(log_entry)
                except:
                    pass
    
    def _save_checkpoint(self, step_name: str, data: Any):
        """Save a checkpoint for resumable execution."""
        if not self.current_task:
            return
        
        checkpoint = {
            "step": step_name,
            "timestamp": datetime.now(timezone.utc),
            "data": data
        }
        self.current_task.checkpoints.append(checkpoint)
        
        if MONGO_AVAILABLE:
            col = get_collection("task_checkpoints")
            if col is not None:
                try:
                    col.update_one(
                        {"task_id": self.current_task.task_id},
                        {"$push": {"checkpoints": checkpoint}},
                        upsert=True
                    )
                except:
                    pass
    
    def _load_checkpoint(self, task_id: str) -> Optional[Dict]:
        """Load the most recent checkpoint for a task."""
        if MONGO_AVAILABLE:
            col = get_collection("task_checkpoints")
            if col is not None:
                try:
                    doc = col.find_one({"task_id": task_id})
                    if doc and doc.get("checkpoints"):
                        return doc["checkpoints"][-1]
                except:
                    pass
        return None
    
    def _save_task_record(self):
        """Persist current task record to MongoDB."""
        if not self.current_task or not MONGO_AVAILABLE:
            return
        
        record = {
            "task_id": self.current_task.task_id,
            "task_name": self.current_task.task_name,
            "created_at": self.current_task.created_at,
            "updated_at": datetime.now(timezone.utc),
            "status": self.current_task.status.value,
            "total_attempts": self.current_task.total_attempts,
            "max_retries": self.current_task.max_retries,
            "execution_logs": [
                {
                    "attempt": log.attempt,
                    "timestamp": log.timestamp,
                    "status": log.status,
                    "error": log.error,
                    "error_category": log.error_category,
                    "recovery_action": log.recovery_action,
                    "duration_seconds": log.duration_seconds
                }
                for log in self.current_task.execution_logs
            ],
            "final_result": self.current_task.final_result,
            "final_error": self.current_task.final_error,
            "metadata": self.current_task.metadata,
            "user": self.user
        }
        
        col = get_collection("task_records")
        if col is not None:
            try:
                col.update_one(
                    {"task_id": record["task_id"]},
                    {"$set": record},
                    upsert=True
                )
            except Exception as e:
                print(f"⚠ Failed to save task record: {e}")
    
    def execute(self, task_fn: Callable, args: tuple = (), kwargs: dict = None,
                task_name: str = "Unnamed Task", max_retries: int = 5,
                timeout: int = 0, checkpoint_fn: Callable = None) -> Dict[str, Any]:
        """
        Execute a function with automatic error recovery.
        
        Args:
            task_fn: The function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            task_name: Human-readable task name
            max_retries: Maximum retry attempts
            timeout: Timeout in seconds (0 = no timeout)
            checkpoint_fn: Optional function to call for checkpointing
        
        Returns:
            Dict with: success, result/error, attempts, logs
        """
        kwargs = kwargs or {}
        task_id = f"exec_{int(time.time())}_{hash(task_name) % 10000}"
        
        self.current_task = TaskRecord(
            task_id=task_id,
            task_name=task_name,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            status=TaskStatus.PENDING,
            max_retries=max_retries
        )
        
        self._log(f"🚀 Starting task: {task_name}")
        self._log(f"   Max retries: {max_retries}, Timeout: {timeout}s")
        self._log(f"   Available capabilities: {len(self.capabilities['skills'])} skills")
        
        attempt = 0
        last_error = None
        
        while attempt < max_retries:
            attempt += 1
            self.current_task.total_attempts = attempt
            self.current_task.status = TaskStatus.RUNNING if attempt == 1 else TaskStatus.RETRYING
            
            start_time = time.time()
            exec_log = ExecutionLog(
                attempt=attempt,
                timestamp=datetime.now(timezone.utc),
                status="running"
            )
            
            try:
                self._log(f"⚡ Attempt {attempt}/{max_retries}...")
                
                # Execute with optional timeout
                if timeout > 0:
                    result = self._execute_with_timeout(task_fn, args, kwargs, timeout)
                else:
                    result = task_fn(*args, **kwargs)
                
                # Success!
                duration = time.time() - start_time
                exec_log.status = "success"
                exec_log.duration_seconds = duration
                exec_log.output = str(result)[:500] if result else None
                self.current_task.execution_logs.append(exec_log)
                
                self.current_task.status = TaskStatus.COMPLETED
                self.current_task.final_result = result
                self._save_task_record()
                
                self._log(f"✅ Task completed successfully in {duration:.1f}s")
                
                return {
                    "success": True,
                    "result": result,
                    "attempts": attempt,
                    "task_id": task_id,
                    "duration": duration
                }
            
            except Exception as e:
                duration = time.time() - start_time
                last_error = e
                
                # Categorize the error
                category = self._categorize_error(e)
                
                exec_log.status = "error"
                exec_log.error = str(e)
                exec_log.error_category = category.value
                exec_log.duration_seconds = duration
                
                self._log(f"❌ Attempt {attempt} failed: {type(e).__name__}: {str(e)[:200]}")
                self._log(f"   Error category: {category.value}")
                
                # Attempt recovery
                if attempt < max_retries:
                    strategy = self._get_recovery_strategy(category, attempt)
                    if strategy:
                        strategy_name, params = strategy
                        self._log(f"🔧 Trying recovery: {strategy_name}")
                        exec_log.recovery_action = strategy_name
                        
                        self.current_task.status = TaskStatus.RECOVERING
                        recovery_context = {
                            "attempt": attempt,
                            "task_name": task_name,
                            "error": e,
                            "category": category
                        }
                        
                        recovery_success = self._execute_recovery(
                            strategy_name, params, e, recovery_context
                        )
                        
                        if recovery_success:
                            self._log(f"   Recovery action completed, retrying...")
                        else:
                            self._log(f"   Recovery action failed")
                
                self.current_task.execution_logs.append(exec_log)
                self._save_task_record()
        
        # All retries exhausted
        self.current_task.status = TaskStatus.FAILED
        self.current_task.final_error = str(last_error)
        self._save_task_record()
        
        self._log(f"💀 Task failed after {max_retries} attempts")
        self._log(f"   Final error: {last_error}")
        
        return {
            "success": False,
            "error": str(last_error),
            "error_type": type(last_error).__name__,
            "error_category": self._categorize_error(last_error).value,
            "attempts": attempt,
            "task_id": task_id,
            "logs": [asdict(log) for log in self.current_task.execution_logs]
        }
    
    def _execute_with_timeout(self, fn: Callable, args: tuple, kwargs: dict, timeout: int) -> Any:
        """Execute function with timeout."""
        result = [None]
        error = [None]
        
        def target():
            try:
                result[0] = fn(*args, **kwargs)
            except Exception as e:
                error[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout=timeout)
        
        if thread.is_alive():
            raise TimeoutError(f"Task timed out after {timeout} seconds")
        
        if error[0]:
            raise error[0]
        
        return result[0]
    
    def run_project_pipeline(self, project_spec: Dict) -> Dict:
        """
        Run a complete project build/deploy pipeline with full autonomy.
        
        Args:
            project_spec: Dict with name, type, description, and optional extra settings
        
        Returns:
            Pipeline result with URLs and status
        """
        name = project_spec.get("name", "my-project")
        project_type = project_spec.get("type", "nextjs")
        description = project_spec.get("description", "")
        extra = project_spec.get("extra", {})
        
        self._log(f"🏗️ Starting project pipeline: {name}")
        self._log(f"   Type: {project_type}")
        self._log(f"   Description: {description[:100]}...")
        
        # Import deployer
        try:
            skills_dir = Path(__file__).parent.parent
            sys.path.insert(0, str(skills_dir / "project-deployer"))
            import importlib
            deployer_mod = importlib.import_module("deployer")
            ProjectDeployer = deployer_mod.ProjectDeployer
        except Exception as e:
            return {
                "success": False,
                "error": f"Could not load ProjectDeployer: {e}"
            }
        
        def deploy_task():
            deployer = ProjectDeployer()
            return deployer.build_and_deploy(
                name=name,
                project_type=project_type,
                description=description,
                extra=extra
            )
        
        result = self.execute(
            task_fn=deploy_task,
            task_name=f"Deploy {name} ({project_type})",
            max_retries=5
        )
        
        if result["success"]:
            deploy_result = result["result"]
            self._log(f"🎉 Project deployed successfully!")
            if deploy_result.get("vercel_url"):
                self._log(f"   URL: {deploy_result['vercel_url']}")
            if deploy_result.get("github_url"):
                self._log(f"   GitHub: {deploy_result['github_url']}")
        
        return result
    
    def run_research_pipeline(self, query: str, depth: str = "deep") -> Dict:
        """Run an autonomous research task with error recovery."""
        self._log(f"🔬 Starting research: {query[:100]}...")
        
        def research_task():
            # Use available APIs and capabilities
            results = {"query": query, "sources": [], "findings": []}
            
            # Try to use research engine if available
            skills_dir = Path(__file__).parent.parent
            research_path = skills_dir / "research-engine"
            
            if research_path.exists():
                sys.path.insert(0, str(research_path))
                try:
                    from research import ResearchEngine
                    engine = ResearchEngine()
                    return engine.research(query, depth=depth)
                except:
                    pass
            
            # Fallback to API intel
            api_path = skills_dir / "api-intel"
            if api_path.exists():
                sys.path.insert(0, str(api_path))
                try:
                    from apis import FreeAPIs
                    apis = FreeAPIs()
                    
                    # Search Wikipedia
                    wiki = apis.wikipedia_search(query)
                    if wiki.get("extract"):
                        results["sources"].append({
                            "type": "wikipedia",
                            "title": wiki.get("title"),
                            "content": wiki.get("extract")
                        })
                    
                    # Check HackerNews for tech topics
                    hn = apis.hackernews_top(5)
                    for story in hn:
                        if query.lower() in story.get("title", "").lower():
                            results["sources"].append({
                                "type": "hackernews",
                                "title": story.get("title"),
                                "url": story.get("url")
                            })
                    
                    results["findings"].append(f"Gathered {len(results['sources'])} sources")
                except Exception as e:
                    results["error"] = str(e)
            
            return results
        
        return self.execute(
            task_fn=research_task,
            task_name=f"Research: {query[:50]}",
            max_retries=3
        )
    
    def get_execution_history(self, limit: int = 20) -> List[Dict]:
        """Get recent task execution history."""
        col = get_collection("task_records")
        if col is None:
            return []
        try:
            return list(col.find({"user": self.user}).sort("created_at", -1).limit(limit))
        except:
            return []
    
    def get_overnight_report(self) -> Dict:
        """Generate a report of overnight task executions."""
        from datetime import timedelta
        col = get_collection("task_records")
        if col is None:
            return {"error": "MongoDB not available"}
        
        # Get tasks from last 12 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=12)
        
        try:
            tasks = list(col.find({
                "user": self.user,
                "created_at": {"$gte": cutoff}
            }))
            
            completed = [t for t in tasks if t.get("status") == "completed"]
            failed = [t for t in tasks if t.get("status") == "failed"]
            
            total_attempts = sum(t.get("total_attempts", 0) for t in tasks)
            successful_first_try = len([t for t in completed if t.get("total_attempts") == 1])
            
            report = {
                "period": "Last 12 hours",
                "total_tasks": len(tasks),
                "completed": len(completed),
                "failed": len(failed),
                "success_rate": f"{len(completed)/len(tasks)*100:.1f}%" if tasks else "N/A",
                "total_attempts": total_attempts,
                "first_try_success": successful_first_try,
                "recovery_saves": len(completed) - successful_first_try,
                "failed_tasks": [
                    {
                        "name": t.get("task_name"),
                        "error": t.get("final_error", "")[:200]
                    }
                    for t in failed
                ]
            }
            
            return report
        except Exception as e:
            return {"error": str(e)}
    
    def list_capabilities(self) -> str:
        """Return a formatted string of all available capabilities."""
        lines = ["🔧 **OpenClaw Capabilities**\n"]
        
        lines.append(f"**Skills ({len(self.capabilities['skills'])}):**")
        for skill in self.capabilities["skills"]:
            lines.append(f"  - {skill['name']}")
        
        if self.capabilities.get("agents"):
            lines.append(f"\n**Agents ({len(self.capabilities['agents'])}):**")
            for agent in self.capabilities["agents"]:
                lines.append(f"  - {agent['name']}: {agent.get('description', '')}")
        
        if self.capabilities.get("tools"):
            lines.append(f"\n**Tools ({len(self.capabilities['tools'])}):**")
            for tool in self.capabilities["tools"]:
                funcs = ", ".join(tool.get("functions", []))
                lines.append(f"  - {tool['name']}: {funcs}")
        
        if self.capabilities.get("apis"):
            lines.append("\n**Free APIs:**")
            for category, apis in self.capabilities["apis"].items():
                lines.append(f"  - {category}: {', '.join(apis)}")
        
        return "\n".join(lines)


# Convenience decorator for autonomous execution
def autonomous(max_retries: int = 5, task_name: str = None):
    """Decorator to make any function autonomous with error recovery."""
    def decorator(fn: Callable) -> Callable:
        @wraps(fn)
        def wrapper(*args, **kwargs):
            executor = AutonomousExecutor()
            name = task_name or fn.__name__
            return executor.execute(fn, args, kwargs, task_name=name, max_retries=max_retries)
        return wrapper
    return decorator


# Quick interface
class AutoExec:
    """Quick autonomous execution interface."""
    
    _executor: AutonomousExecutor = None
    
    @classmethod
    def _get_executor(cls) -> AutonomousExecutor:
        if cls._executor is None:
            cls._executor = AutonomousExecutor()
        return cls._executor
    
    @classmethod
    def run(cls, fn: Callable, *args, **kwargs) -> Dict:
        """Run any function with autonomous error recovery."""
        task_name = kwargs.pop("_task_name", fn.__name__)
        max_retries = kwargs.pop("_max_retries", 5)
        return cls._get_executor().execute(fn, args, kwargs, task_name=task_name, max_retries=max_retries)
    
    @classmethod
    def deploy(cls, name: str, project_type: str = "nextjs", description: str = "", **extra) -> Dict:
        """Deploy a project with full autonomy."""
        return cls._get_executor().run_project_pipeline({
            "name": name,
            "type": project_type,
            "description": description,
            "extra": extra
        })
    
    @classmethod
    def research(cls, query: str, depth: str = "deep") -> Dict:
        """Run autonomous research."""
        return cls._get_executor().run_research_pipeline(query, depth)
    
    @classmethod
    def history(cls, limit: int = 20) -> List[Dict]:
        """Get execution history."""
        return cls._get_executor().get_execution_history(limit)
    
    @classmethod
    def report(cls) -> Dict:
        """Get overnight execution report."""
        return cls._get_executor().get_overnight_report()
    
    @classmethod
    def caps(cls) -> str:
        """List all capabilities."""
        return cls._get_executor().list_capabilities()


# Test function
if __name__ == "__main__":
    executor = AutonomousExecutor()
    
    print("\n" + "="*60)
    print(executor.list_capabilities())
    print("="*60)
    
    # Test with a function that might fail
    def flaky_function():
        import random
        if random.random() < 0.7:  # 70% chance of failure
            raise ConnectionError("Simulated network error")
        return "Success!"
    
    print("\n🧪 Testing with flaky function...")
    result = executor.execute(flaky_function, task_name="Flaky Test", max_retries=5)
    print(f"Result: {result}")
