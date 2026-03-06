"""
Task Planner and Validator
A secure, step-by-step task management system for AI Agents

Author: cerbug45
License: MIT
"""

import json
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from enum import Enum
from dataclasses import dataclass, asdict, field
import uuid
import logging


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    APPROVED = "approved"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NEEDS_REVIEW = "needs_review"


class StepStatus(Enum):
    """Step execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ValidationRule:
    """Validation rule for safety checks"""
    rule_id: str
    description: str
    severity: str  # "error", "warning", "info"
    enabled: bool = True


@dataclass
class Step:
    """Single task step"""
    step_id: str
    order: int
    description: str
    action: str
    parameters: Dict[str, Any]
    expected_output: str
    safety_check: bool = True
    rollback_possible: bool = True
    status: StepStatus = StepStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        return data
    
    def mark_running(self):
        """Mark step as running"""
        self.status = StepStatus.RUNNING
        self.started_at = datetime.now().isoformat()
    
    def mark_completed(self, result: Any):
        """Mark step as completed"""
        self.status = StepStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now().isoformat()
    
    def mark_failed(self, error: str):
        """Mark step as failed"""
        self.status = StepStatus.FAILED
        self.error = error
        self.completed_at = datetime.now().isoformat()


@dataclass
class TaskPlan:
    """Complete task plan with steps"""
    task_id: str
    title: str
    description: str
    steps: List[Step]
    created_at: str
    status: TaskStatus = TaskStatus.PENDING
    approved_by: Optional[str] = None
    approved_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'task_id': self.task_id,
            'title': self.title,
            'description': self.description,
            'steps': [step.to_dict() for step in self.steps],
            'created_at': self.created_at,
            'status': self.status.value,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at,
            'completed_at': self.completed_at,
            'metadata': self.metadata,
            'checksum': self.checksum
        }
    
    def calculate_checksum(self) -> str:
        """Calculate checksum for plan integrity"""
        plan_str = json.dumps({
            'task_id': self.task_id,
            'title': self.title,
            'steps': [s.to_dict() for s in self.steps]
        }, sort_keys=True)
        return hashlib.sha256(plan_str.encode()).hexdigest()
    
    def verify_integrity(self) -> bool:
        """Verify plan hasn't been tampered with"""
        if not self.checksum:
            return True
        return self.checksum == self.calculate_checksum()


class SafetyValidator:
    """Security validation layer"""
    
    def __init__(self):
        self.dangerous_operations = [
            'delete', 'remove', 'drop', 'truncate', 'format',
            'rm ', 'rmdir', 'kill', 'shutdown', 'reboot', 'destroy'
        ]
        self.sensitive_paths = [
            '/etc', '/sys', '/proc', '/boot', '/root',
            'C:\\Windows', 'C:\\Program Files', '/home'
        ]
        self.validation_rules = []
        self._setup_default_rules()
    
    def _setup_default_rules(self):
        """Setup default validation rules"""
        self.validation_rules = [
            ValidationRule(
                rule_id="dangerous_ops",
                description="Check for dangerous operations",
                severity="error"
            ),
            ValidationRule(
                rule_id="sensitive_paths",
                description="Check for sensitive system paths",
                severity="warning"
            ),
            ValidationRule(
                rule_id="parameter_validation",
                description="Validate step parameters",
                severity="error"
            )
        ]
    
    def validate_step(self, step: Step) -> tuple[bool, List[str]]:
        """
        Validate step safety
        Returns: (is_safe, warnings)
        """
        warnings = []
        is_safe = True
        
        # Check for dangerous operations
        action_lower = step.action.lower()
        for dangerous_op in self.dangerous_operations:
            if dangerous_op in action_lower:
                msg = f"⚠️ Dangerous operation detected: '{dangerous_op}'"
                warnings.append(msg)
                if not step.safety_check:
                    is_safe = False
        
        # Check for sensitive paths
        params_str = json.dumps(step.parameters).lower()
        for sensitive_path in self.sensitive_paths:
            if sensitive_path.lower() in params_str:
                msg = f"⚠️ Sensitive system path detected: '{sensitive_path}'"
                warnings.append(msg)
        
        # Validate parameters are not empty for critical operations
        if not step.parameters and step.safety_check:
            warnings.append("ℹ️ No parameters provided for this step")
        
        # Check rollback capability for dangerous operations
        if warnings and not step.rollback_possible:
            warnings.append("⚠️ This operation cannot be rolled back!")
        
        return is_safe, warnings
    
    def validate_plan(self, plan: TaskPlan) -> tuple[bool, List[str]]:
        """
        Validate entire task plan
        Returns: (is_safe, all_warnings)
        """
        all_warnings = []
        plan_is_safe = True
        
        # Verify plan integrity
        if not plan.verify_integrity():
            all_warnings.append("❌ Plan integrity check failed! Plan may have been tampered with.")
            return False, all_warnings
        
        # Validate each step
        for step in plan.steps:
            is_safe, warnings = self.validate_step(step)
            if not is_safe:
                plan_is_safe = False
            all_warnings.extend([f"Step {step.order}: {w}" for w in warnings])
        
        # Check step order
        orders = [step.order for step in plan.steps]
        if orders != sorted(orders) or len(orders) != len(set(orders)):
            all_warnings.append("⚠️ Step ordering issue detected")
        
        return plan_is_safe, all_warnings


class TaskExecutor:
    """Task execution engine with rollback support"""
    
    def __init__(self, safety_validator: SafetyValidator):
        self.safety_validator = safety_validator
        self.execution_history = []
        self.checkpoint_stack = []
        self.logger = logging.getLogger(__name__)
    
    def create_checkpoint(self, step: Step):
        """Create a checkpoint before executing a step"""
        checkpoint = {
            'step_id': step.step_id,
            'timestamp': datetime.now().isoformat(),
            'state': step.to_dict()
        }
        self.checkpoint_stack.append(checkpoint)
    
    def execute_step(
        self, 
        step: Step, 
        executor_func: Callable,
        dry_run: bool = False
    ) -> tuple[bool, Any, Optional[str]]:
        """
        Execute a single step
        Returns: (success, result, error)
        """
        if dry_run:
            self.logger.info(f"DRY RUN: Would execute step {step.step_id}")
            return True, "Dry run successful", None
        
        # Validate step before execution
        is_safe, warnings = self.safety_validator.validate_step(step)
        if not is_safe:
            error = f"Step failed safety validation: {'; '.join(warnings)}"
            self.logger.error(error)
            return False, None, error
        
        # Create checkpoint if rollback is possible
        if step.rollback_possible:
            self.create_checkpoint(step)
        
        # Mark as running
        step.mark_running()
        
        try:
            # Execute the step
            result = executor_func(step.action, step.parameters)
            step.mark_completed(result)
            
            # Record execution
            self.execution_history.append({
                'step_id': step.step_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'success',
                'result': result
            })
            
            return True, result, None
            
        except Exception as e:
            error = str(e)
            step.mark_failed(error)
            
            # Record failure
            self.execution_history.append({
                'step_id': step.step_id,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': error
            })
            
            self.logger.error(f"Step {step.step_id} failed: {error}")
            return False, None, error
    
    def rollback_to_checkpoint(self, checkpoint_index: int = -1) -> bool:
        """Rollback to a specific checkpoint"""
        if not self.checkpoint_stack:
            self.logger.warning("No checkpoints available for rollback")
            return False
        
        try:
            checkpoint = self.checkpoint_stack[checkpoint_index]
            self.logger.info(f"Rolling back to checkpoint: {checkpoint['step_id']}")
            # Here you would implement actual rollback logic
            return True
        except IndexError:
            self.logger.error(f"Invalid checkpoint index: {checkpoint_index}")
            return False


class TaskPlanner:
    """Main task planner and validator interface"""
    
    def __init__(self, auto_approve: bool = False):
        self.safety_validator = SafetyValidator()
        self.executor = TaskExecutor(self.safety_validator)
        self.auto_approve = auto_approve
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def create_plan(
        self,
        title: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> TaskPlan:
        """
        Create a new task plan
        
        Args:
            title: Task title
            description: Task description
            steps: List of step dictionaries
            
        Returns:
            TaskPlan object
        """
        task_id = str(uuid.uuid4())
        
        # Convert step dicts to Step objects
        step_objects = []
        for i, step_dict in enumerate(steps):
            step = Step(
                step_id=str(uuid.uuid4()),
                order=i + 1,
                description=step_dict['description'],
                action=step_dict['action'],
                parameters=step_dict.get('parameters', {}),
                expected_output=step_dict.get('expected_output', ''),
                safety_check=step_dict.get('safety_check', True),
                rollback_possible=step_dict.get('rollback_possible', True),
                max_retries=step_dict.get('max_retries', 3)
            )
            step_objects.append(step)
        
        # Create task plan
        plan = TaskPlan(
            task_id=task_id,
            title=title,
            description=description,
            steps=step_objects,
            created_at=datetime.now().isoformat(),
            metadata={}
        )
        
        # Calculate checksum for integrity
        plan.checksum = plan.calculate_checksum()
        
        self.logger.info(f"Created task plan: {task_id}")
        return plan
    
    def validate_plan(self, plan: TaskPlan) -> tuple[bool, List[str]]:
        """
        Validate a task plan
        
        Returns: (is_valid, warnings)
        """
        return self.safety_validator.validate_plan(plan)
    
    def approve_plan(self, plan: TaskPlan, approved_by: str = "user") -> bool:
        """
        Approve a task plan for execution
        
        Args:
            plan: TaskPlan to approve
            approved_by: User or system approving the plan
            
        Returns:
            Success status
        """
        is_valid, warnings = self.validate_plan(plan)
        
        if not is_valid:
            self.logger.error(f"Plan validation failed: {warnings}")
            return False
        
        if warnings:
            self.logger.warning(f"Plan has warnings: {warnings}")
        
        plan.status = TaskStatus.APPROVED
        plan.approved_by = approved_by
        plan.approved_at = datetime.now().isoformat()
        
        self.logger.info(f"Plan approved: {plan.task_id}")
        return True
    
    def execute_plan(
        self,
        plan: TaskPlan,
        executor_func: Callable,
        dry_run: bool = False,
        stop_on_error: bool = True
    ) -> tuple[bool, List[Dict]]:
        """
        Execute a task plan
        
        Args:
            plan: TaskPlan to execute
            executor_func: Function to execute each step
            dry_run: If True, simulate execution without running
            stop_on_error: If True, stop on first error
            
        Returns:
            (success, results)
        """
        # Check if plan is approved
        if plan.status != TaskStatus.APPROVED and not self.auto_approve:
            self.logger.error("Plan must be approved before execution")
            return False, []
        
        # Auto-approve if enabled
        if self.auto_approve and plan.status == TaskStatus.PENDING:
            if not self.approve_plan(plan):
                return False, []
        
        # Mark plan as running
        plan.status = TaskStatus.RUNNING
        results = []
        
        self.logger.info(f"Starting execution of plan: {plan.task_id} (dry_run={dry_run})")
        
        # Execute each step
        for step in plan.steps:
            self.logger.info(f"Executing step {step.order}: {step.description}")
            
            success, result, error = self.executor.execute_step(
                step, executor_func, dry_run
            )
            
            results.append({
                'step_id': step.step_id,
                'order': step.order,
                'success': success,
                'result': result,
                'error': error
            })
            
            if not success:
                if stop_on_error:
                    plan.status = TaskStatus.FAILED
                    self.logger.error(f"Plan execution failed at step {step.order}")
                    return False, results
                else:
                    step.status = StepStatus.FAILED
                    continue
        
        # Mark plan as completed
        plan.status = TaskStatus.COMPLETED
        plan.completed_at = datetime.now().isoformat()
        
        self.logger.info(f"Plan execution completed: {plan.task_id}")
        return True, results
    
    def save_plan(self, plan: TaskPlan, filepath: str):
        """Save plan to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(plan.to_dict(), f, indent=2)
        self.logger.info(f"Plan saved to: {filepath}")
    
    def load_plan(self, filepath: str) -> TaskPlan:
        """Load plan from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Reconstruct steps
        steps = []
        for step_data in data['steps']:
            step = Step(
                step_id=step_data['step_id'],
                order=step_data['order'],
                description=step_data['description'],
                action=step_data['action'],
                parameters=step_data['parameters'],
                expected_output=step_data['expected_output'],
                safety_check=step_data['safety_check'],
                rollback_possible=step_data['rollback_possible'],
                status=StepStatus(step_data['status']),
                result=step_data.get('result'),
                error=step_data.get('error'),
                started_at=step_data.get('started_at'),
                completed_at=step_data.get('completed_at')
            )
            steps.append(step)
        
        # Reconstruct plan
        plan = TaskPlan(
            task_id=data['task_id'],
            title=data['title'],
            description=data['description'],
            steps=steps,
            created_at=data['created_at'],
            status=TaskStatus(data['status']),
            approved_by=data.get('approved_by'),
            approved_at=data.get('approved_at'),
            completed_at=data.get('completed_at'),
            metadata=data.get('metadata', {}),
            checksum=data.get('checksum')
        )
        
        self.logger.info(f"Plan loaded from: {filepath}")
        return plan
    
    def get_execution_summary(self, plan: TaskPlan) -> Dict:
        """Get execution summary of a plan"""
        total_steps = len(plan.steps)
        completed = sum(1 for s in plan.steps if s.status == StepStatus.COMPLETED)
        failed = sum(1 for s in plan.steps if s.status == StepStatus.FAILED)
        pending = sum(1 for s in plan.steps if s.status == StepStatus.PENDING)
        
        return {
            'task_id': plan.task_id,
            'title': plan.title,
            'status': plan.status.value,
            'total_steps': total_steps,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'progress_percentage': (completed / total_steps * 100) if total_steps > 0 else 0,
            'created_at': plan.created_at,
            'completed_at': plan.completed_at
        }
