"""
Supervisor Pattern Implementation

A central supervisor orchestrates workers by dynamically analyzing tasks,
breaking them down, and delegating to specialized workers. Unlike Work Crew
(which runs parallel redundancy), Supervisor enables complex multi-step
workflows with adaptive planning.

Use this for:
- Complex tasks requiring dynamic decomposition
- Multi-stage work with dependencies between steps
- Tasks needing different specialist skills at different phases
- Work requiring iterative refinement and review cycles
- Complex planning and coordination scenarios

Example: "Research, write, and review a technical article" would spawn
research_worker → writer_worker (with research output) → reviewer_worker.
"""

import argparse
import json
import sys
import re
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

from utils import SessionManager, AgentResult, SessionState


class WorkerRole(Enum):
    """Predefined worker role types with specializations."""
    RESEARCH = "research"
    WRITE = "write"
    REVIEW = "review"
    CODE = "code"
    TEST = "test"
    ANALYZE = "analyze"
    PLAN = "plan"
    CUSTOM = "custom"


class DelegationStrategy(Enum):
    """Strategies for task delegation."""
    ADAPTIVE = "adaptive"      # Dynamic planning based on task analysis
    FIXED = "fixed"            # Predefined workflow
    ITERATIVE = "iterative"    # Feedback loops with refinement


class WorkerStatus(Enum):
    """Status of individual workers in the pool."""
    PENDING = "pending"        # Not yet started
    RUNNING = "running"        # Currently working
    COMPLETED = "completed"    # Finished successfully
    FAILED = "failed"          # Error occurred
    RETRYING = "retrying"      # Attempting restart after failure


@dataclass
class WorkerConfig:
    """Configuration for a specialized worker."""
    role: WorkerRole
    name: str                          # Unique identifier
    system_prompt: str                 # Role-specific instructions
    input_transform: Optional[Callable] = None  # Function to prepare inputs
    output_transform: Optional[Callable] = None  # Function to process outputs
    max_retries: int = 2
    timeout: int = 300


@dataclass
class TaskStep:
    """A single step in a decomposed task."""
    step_id: str
    description: str
    assigned_worker: str               # Worker name
    dependencies: List[str] = field(default_factory=list)  # Step IDs this depends on
    input_data: Optional[str] = None   # Input from previous steps or user
    output_data: Optional[str] = None  # Result from execution
    status: WorkerStatus = WorkerStatus.PENDING
    retry_count: int = 0
    error: Optional[str] = None


@dataclass
class SupervisorConfig:
    """Configuration for Supervisor execution."""
    task: str
    workers: List[WorkerConfig]
    strategy: DelegationStrategy
    max_iterations: int
    verbose: bool = False
    state_file: Optional[str] = None
    synthesize_final: bool = True


class WorkerPool:
    """
    Manages a pool of specialized workers with different capabilities.
    """
    
    # Default system prompts for each role type
    DEFAULT_PROMPTS = {
        WorkerRole.RESEARCH: """You are a research specialist.
Your job is to gather information, facts, and context.
Provide thorough, well-sourced information in a structured format.
Focus on accuracy and comprehensiveness.""",
        
        WorkerRole.WRITE: """You are a content creation specialist.
Your job is to produce well-structured, clear, and engaging content.
Adapt your style to the task requirements.
Ensure proper formatting and logical flow.""",
        
        WorkerRole.REVIEW: """You are a critical review specialist.
Your job is to evaluate work, identify issues, and suggest improvements.
Be thorough, constructive, and objective.
Provide specific, actionable feedback.""",
        
        WorkerRole.CODE: """You are a software development specialist.
Your job is to write, refactor, or debug code.
Follow best practices, write clean code, and include comments.
Consider edge cases and error handling.""",
        
        WorkerRole.TEST: """You are a quality assurance specialist.
Your job is to test functionality, identify bugs, and verify requirements.
Be systematic and thorough in your testing approach.
Document test cases and results clearly.""",
        
        WorkerRole.ANALYZE: """You are an analytical specialist.
Your job is to examine data, identify patterns, and extract insights.
Provide quantitative and qualitative analysis.
Support conclusions with evidence.""",
        
        WorkerRole.PLAN: """You are a planning specialist.
Your job is to break down complex tasks, identify dependencies, and create structured plans.
Think about sequencing, resource needs, and potential obstacles.
Provide clear, actionable plans.""",
        
        WorkerRole.CUSTOM: """You are a specialized worker.
Execute your assigned task with expertise and attention to detail.
Provide high-quality output appropriate to the task domain."""
    }
    
    def __init__(self):
        self.workers: Dict[str, WorkerConfig] = {}
    
    def register_worker(self, config: WorkerConfig):
        """Register a worker with the pool."""
        self.workers[config.name] = config
    
    def get_worker(self, name: str) -> Optional[WorkerConfig]:
        """Get a worker configuration by name."""
        return self.workers.get(name)
    
    def list_workers(self) -> List[str]:
        """List all registered worker names."""
        return list(self.workers.keys())
    
    @classmethod
    def create_from_roles(cls, roles: List[str]) -> 'WorkerPool':
        """
        Create a worker pool from simple role names.
        
        Args:
            roles: List of role names like ['research', 'write', 'review']
        
        Returns:
            Configured WorkerPool
        """
        pool = cls()
        
        for i, role_str in enumerate(roles):
            # Normalize role string
            role_str = role_str.lower().strip()
            
            # Map to enum
            try:
                role = WorkerRole(role_str)
            except ValueError:
                role = WorkerRole.CUSTOM
            
            # Create unique name
            name = f"{role.value}-{i + 1}"
            
            # Get default prompt
            system_prompt = cls.DEFAULT_PROMPTS.get(role, cls.DEFAULT_PROMPTS[WorkerRole.CUSTOM])
            
            config = WorkerConfig(
                role=role,
                name=name,
                system_prompt=system_prompt
            )
            
            pool.register_worker(config)
        
        return pool


class Supervisor:
    """
    Supervisor pattern: Orchestrator-worker coordination
    
    The supervisor dynamically:
    1. Analyzes the incoming task
    2. Decomposes it into steps
    3. Assigns steps to appropriate workers
    4. Manages dependencies and execution order
    5. Synthesizes worker outputs into coherent final result
    6. Handles failures and retries
    """
    
    def __init__(self, config: SupervisorConfig):
        self.config = config
        self.worker_pool = WorkerPool()
        self.session_manager = SessionManager(state_file=config.state_file)
        self.execution_plan: List[TaskStep] = []
        self.completed_steps: Dict[str, TaskStep] = {}
        self.iteration = 0
        
        # Register all configured workers
        for worker_config in config.workers:
            self.worker_pool.register_worker(worker_config)
    
    def _log(self, message: str, level: str = "info"):
        """Log message if verbose mode enabled."""
        if self.config.verbose:
            prefix = "[SUPERVISOR]"
            if level == "error":
                prefix = "[SUPERVISOR ERROR]"
            elif level == "debug":
                prefix = "[SUPERVISOR DEBUG]"
            print(f"{prefix} {message}", file=sys.stderr)
    
    def analyze_task(self) -> Dict[str, Any]:
        """
        Analyze the task to determine:
        - Complexity level
        - Required worker types
        - Suggested decomposition approach
        """
        self._log(f"Analyzing task: {self.config.task[:100]}...")
        
        # Build analysis prompt for supervisor
        analysis_task = f"""Analyze this task and provide structured output:

TASK: {self.config.task}

AVAILABLE WORKERS: {', '.join(self.worker_pool.list_workers())}

Analyze and respond in this exact format:

COMPLEXITY: [low|medium|high]
ESTIMATED_STEPS: [number]
REQUIRED_WORKERS: [comma-separated list]
DECOMPOSITION_APPROACH: [sequential|parallel|mixed]
KEY_CHALLENGES: [brief description]

OUTPUT_FORMAT: [text|structured|code|report]"""
        
        try:
            # Spawn analysis agent (supervisor itself acts as analysis agent)
            analysis_id = self.session_manager.spawn_session(
                task=analysis_task,
                agent_label="supervisor-analyzer",
                context={"phase": "task_analysis"}
            )
            
            # Collect analysis result
            results = self.session_manager.collect_all_results(timeout=60)
            
            if analysis_id in results:
                output = results[analysis_id].output
                return self._parse_analysis(output)
            else:
                self._log("Analysis failed to return result", "error")
                return self._default_analysis()
                
        except Exception as e:
            self._log(f"Task analysis failed: {e}", "error")
            return self._default_analysis()
    
    def _parse_analysis(self, output: str) -> Dict[str, Any]:
        """Parse structured analysis from agent output."""
        analysis = {
            "complexity": "medium",
            "estimated_steps": len(self.worker_pool.list_workers()),
            "required_workers": self.worker_pool.list_workers(),
            "approach": "sequential",
            "challenges": "",
            "output_format": "text"
        }
        
        # Extract fields using regex
        patterns = {
            "complexity": r'COMPLEXITY:\s*(\w+)',
            "estimated_steps": r'ESTIMATED_STEPS:\s*(\d+)',
            "required_workers": r'REQUIRED_WORKERS:\s*([\w,\s-]+)',
            "approach": r'DECOMPOSITION_APPROACH:\s*(\w+)',
            "challenges": r'KEY_CHALLENGES:\s*([^.]+)',
            "output_format": r'OUTPUT_FORMAT:\s*(\w+)'
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                value = match.group(1).strip()
                if key == "estimated_steps":
                    try:
                        analysis[key] = int(value)
                    except ValueError:
                        pass
                else:
                    analysis[key] = value
        
        # Parse required workers
        if "required_workers" in analysis:
            workers_str = analysis["required_workers"]
            analysis["required_workers"] = [w.strip() for w in workers_str.split(",")]
        
        self._log(f"Analysis complete: complexity={analysis['complexity']}, "
                 f"workers={analysis['required_workers']}")
        
        return analysis
    
    def _default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when parsing fails."""
        available = self.worker_pool.list_workers()
        return {
            "complexity": "medium",
            "estimated_steps": len(available),
            "required_workers": available,
            "approach": "sequential",
            "challenges": "Unable to analyze",
            "output_format": "text"
        }
    
    def decompose_task(self, analysis: Dict[str, Any]) -> List[TaskStep]:
        """
        Decompose task into steps based on analysis.
        Creates a dependency-aware execution plan.
        """
        self._log("Decomposing task into execution steps...")
        
        required_workers = analysis.get("required_workers", self.worker_pool.list_workers())
        approach = analysis.get("approach", "sequential")
        
        steps: List[TaskStep] = []
        
        # Map worker names to registered workers
        for i, worker_name in enumerate(required_workers):
            # Normalize and find matching worker
            worker_config = None
            for name, config in self.worker_pool.workers.items():
                if worker_name in name or config.role.value in worker_name:
                    worker_config = config
                    break
            
            if not worker_config:
                # Skip unknown workers
                self._log(f"Unknown worker requested: {worker_name}", "error")
                continue
            
            # Build step
            step_id = f"step-{i + 1}"
            
            # Determine dependencies based on approach
            dependencies = []
            if approach == "sequential" and i > 0:
                dependencies = [f"step-{i}"]
            elif approach == "mixed" and i > 0:
                # Every other step depends on previous
                if i % 2 == 1:
                    dependencies = [f"step-{i}"]
            
            step = TaskStep(
                step_id=step_id,
                description=f"Execute {worker_config.role.value} phase",
                assigned_worker=worker_config.name,
                dependencies=dependencies
            )
            
            steps.append(step)
            self._log(f"Created {step_id}: {worker_config.name} "
                     f"(deps: {dependencies})")
        
        self.execution_plan = steps
        return steps
    
    def _build_worker_task(self, step: TaskStep) -> str:
        """Build the task prompt for a specific worker step."""
        worker_config = self.worker_pool.get_worker(step.assigned_worker)
        if not worker_config:
            return step.description
        
        # Build context from dependencies
        context_parts = []
        for dep_id in step.dependencies:
            if dep_id in self.completed_steps:
                dep_step = self.completed_steps[dep_id]
                context_parts.append(f"## Output from {dep_id}\n\n{dep_step.output_data}")
        
        dependency_context = "\n\n".join(context_parts)
        
        # Build full task
        base_task = self.config.task
        system_prompt = worker_config.system_prompt
        
        task = f"""{system_prompt}

ORIGINAL TASK: {base_task}

YOUR SPECIFIC ASSIGNMENT: {step.description}
{"=" * 60}"""
        
        if dependency_context:
            task += f"""

INPUT FROM PREVIOUS STEPS:

{dependency_context}
"""
        
        if step.input_data:
            task += f"""

ADDITIONAL INPUT:

{step.input_data}
"""
        
        task += """

Execute your assignment and provide your output clearly labeled with your role.
Start your response with your role identifier in brackets, e.g., [RESEARCH OUTPUT].
"""
        
        return task
    
    def execute_step(self, step: TaskStep) -> bool:
        """
        Execute a single step by spawning the assigned worker.
        Returns True if successful, False otherwise.
        """
        self._log(f"Executing {step.step_id} with {step.assigned_worker}...")
        
        step.status = WorkerStatus.RUNNING
        
        try:
            # Build task for worker
            worker_task = self._build_worker_task(step)
            
            # Spawn worker
            agent_id = self.session_manager.spawn_session(
                task=worker_task,
                agent_label=f"worker-{step.assigned_worker}",
                context={
                    "step_id": step.step_id,
                    "worker_role": step.assigned_worker,
                    "original_task": self.config.task
                }
            )
            
            # Collect result
            results = self.session_manager.collect_all_results(
                timeout=worker_config.timeout if (worker_config := self.worker_pool.get_worker(step.assigned_worker)) else 300
            )
            
            if agent_id in results:
                result = results[agent_id]
                
                if result.state == SessionState.COMPLETED and result.output:
                    step.output_data = result.output
                    step.status = WorkerStatus.COMPLETED
                    self.completed_steps[step.step_id] = step
                    self._log(f"{step.step_id} completed successfully")
                    return True
                else:
                    step.error = result.error or "Failed to complete"
                    step.status = WorkerStatus.FAILED
                    self._log(f"{step.step_id} failed: {step.error}", "error")
                    return False
            else:
                step.error = "No result collected"
                step.status = WorkerStatus.FAILED
                self._log(f"{step.step_id} failed: no result", "error")
                return False
                
        except Exception as e:
            step.error = str(e)
            step.status = WorkerStatus.FAILED
            self._log(f"{step.step_id} exception: {e}", "error")
            return False
    
    def handle_failure(self, step: TaskStep) -> bool:
        """
        Handle a failed step - attempt retry if configured.
        Returns True if retry should proceed, False if max retries reached.
        """
        worker_config = self.worker_pool.get_worker(step.assigned_worker)
        max_retries = worker_config.max_retries if worker_config else 2
        
        if step.retry_count < max_retries:
            step.retry_count += 1
            step.status = WorkerStatus.RETRYING
            step.error = None
            self._log(f"Retrying {step.step_id} (attempt {step.retry_count}/{max_retries})")
            return True
        else:
            step.status = WorkerStatus.FAILED
            self._log(f"{step.step_id} max retries exceeded", "error")
            return False
    
    def can_execute(self, step: TaskStep) -> bool:
        """Check if a step can be executed (dependencies satisfied)."""
        for dep_id in step.dependencies:
            if dep_id not in self.completed_steps:
                return False
            if self.completed_steps[dep_id].status != WorkerStatus.COMPLETED:
                return False
        return True
    
    def execute_plan(self) -> Dict[str, Any]:
        """
        Execute the full task plan, managing dependencies and failures.
        """
        self._log(f"Starting execution plan with {len(self.execution_plan)} steps")
        
        pending_steps = list(self.execution_plan)
        failed_steps: List[TaskStep] = []
        
        while pending_steps and self.iteration < self.config.max_iterations:
            self.iteration += 1
            self._log(f"Iteration {self.iteration}/{self.config.max_iterations}")
            
            still_pending: List[TaskStep] = []
            
            for step in pending_steps:
                # Check if dependencies satisfied
                if not self.can_execute(step):
                    still_pending.append(step)
                    continue
                
                # Execute step
                success = self.execute_step(step)
                
                if not success:
                    # Try retry
                    if self.handle_failure(step):
                        still_pending.append(step)
                    else:
                        failed_steps.append(step)
                        # Continue with remaining steps if possible
                        if self.config.strategy == DelegationStrategy.ADAPTIVE:
                            self._log(f"Continuing despite failure in {step.step_id}")
                
                # Small delay between spawns
                import time
                time.sleep(1)
            
            pending_steps = still_pending
        
        # Mark remaining pending as failed
        for step in pending_steps:
            step.status = WorkerStatus.FAILED
            step.error = "Not executed - iteration limit or dependency failure"
            failed_steps.append(step)
        
        success_count = len([s for s in self.execution_plan if s.status == WorkerStatus.COMPLETED])
        fail_count = len(failed_steps)
        
        self._log(f"Execution complete: {success_count} succeeded, {fail_count} failed")
        
        return {
            "completed": success_count,
            "failed": fail_count,
            "iterations": self.iteration,
            "steps": self.execution_plan
        }
    
    def synthesize_final_result(self) -> str:
        """
        Synthesize all worker outputs into a coherent final result.
        """
        if not self.config.synthesize_final:
            # Return raw outputs
            outputs = []
            for step_id, step in self.completed_steps.items():
                if step.output_data:
                    outputs.append(f"## {step.assigned_worker}\n\n{step.output_data}")
            return "\n\n---\n\n".join(outputs)
        
        self._log("Synthesizing final result...")
        
        # Collect all outputs
        worker_outputs = []
        for step_id, step in self.completed_steps.items():
            if step.output_data:
                worker_outputs.append({
                    "worker": step.assigned_worker,
                    "step": step_id,
                    "output": step.output_data
                })
        
        if not worker_outputs:
            return "ERROR: No worker outputs to synthesize"
        
        if len(worker_outputs) == 1:
            return worker_outputs[0]["output"]
        
        # Build synthesis prompt
        outputs_text = "\n\n".join([
            f"### {w['worker']} ({w['step']})\n{w['output'][:500]}..."
            for w in worker_outputs
        ])
        
        synthesis_task = f"""Synthesize the following worker outputs into a coherent final result.

ORIGINAL TASK: {self.config.task}

WORKER OUTPUTS:
{outputs_text}

Create a final synthesized output that:
1. Integrates insights from all workers
2. Maintains logical flow and coherence
3. Resolves any contradictions or conflicts
4. Presents a unified solution or deliverable

Provide the synthesized result in a clear, well-structured format."""
        
        try:
            synth_id = self.session_manager.spawn_session(
                task=synthesis_task,
                agent_label="supervisor-synthesizer",
                context={"phase": "synthesis"}
            )
            
            results = self.session_manager.collect_all_results(timeout=120)
            
            if synth_id in results and results[synth_id].output:
                self._log("Synthesis complete")
                return results[synth_id].output
            else:
                # Fallback: combine outputs manually
                return self._manual_synthesis(worker_outputs)
                
        except Exception as e:
            self._log(f"Synthesis failed: {e}", "error")
            return self._manual_synthesis(worker_outputs)
    
    def _manual_synthesis(self, worker_outputs: List[Dict]) -> str:
        """Fallback manual synthesis when synthesizer fails."""
        parts = ["[SUPERVISED WORKFLOW RESULT - MANUAL SYNTHESIS]\n"]
        
        for w in worker_outputs:
            parts.append(f"\n## Output from {w['worker']}\n\n{w['output']}")
        
        return "\n---\n".join(parts)
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the full Supervisor workflow.
        
        Returns:
            Dictionary with execution results and synthesized output
        """
        self._log("Supervisor starting task execution")
        self._log(f"Workers: {self.worker_pool.list_workers()}")
        self._log(f"Strategy: {self.config.strategy.value}")
        
        # Phase 1: Analyze task
        analysis = self.analyze_task()
        
        # Phase 2: Decompose into steps
        self.decompose_task(analysis)
        
        if not self.execution_plan:
            return {
                "success": False,
                "error": "No execution plan generated",
                "output": None
            }
        
        # Phase 3: Execute plan
        execution_result = self.execute_plan()
        
        # Phase 4: Synthesize final result
        final_output = self.synthesize_final_result()
        
        # Build result structure
        return {
            "success": execution_result["failed"] == 0,
            "task": self.config.task,
            "analysis": analysis,
            "execution": execution_result,
            "workers_used": self.worker_pool.list_workers(),
            "steps_executed": len(self.completed_steps),
            "final_output": final_output,
            "verbose_log": None  # Could capture all logs if needed
        }


def parse_worker_definitions(workers_str: str) -> List[WorkerConfig]:
    """
    Parse worker definitions from CLI string.
    
    Formats supported:
    - Simple: "research,write,review"
    - With counts: "research:2,write:1,review:1"
    """
    configs = []
    
    for part in workers_str.split(","):
        part = part.strip()
        if not part:
            continue
        
        # Parse role and optional count
        if ":" in part:
            role_str, count_str = part.split(":", 1)
            try:
                count = int(count_str.strip())
            except ValueError:
                count = 1
        else:
            role_str = part
            count = 1
        
        role_str = role_str.strip().lower()
        
        # Map to role enum
        try:
            role = WorkerRole(role_str)
        except ValueError:
            role = WorkerRole.CUSTOM
        
        # Create configs
        for i in range(count):
            name = f"{role.value}-{i + 1}" if count > 1 else role.value
            
            config = WorkerConfig(
                role=role,
                name=name,
                system_prompt=WorkerPool.DEFAULT_PROMPTS.get(role, WorkerPool.DEFAULT_PROMPTS[WorkerRole.CUSTOM])
            )
            
            configs.append(config)
    
    return configs


def parse_arguments() -> SupervisorConfig:
    """Parse command line arguments for Supervisor."""
    parser = argparse.ArgumentParser(
        description="Supervisor Pattern: Orchestrator-worker coordination with dynamic delegation",
        prog="claw agent-orchestrator supervise"
    )
    
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="The task to supervise and delegate"
    )
    
    parser.add_argument(
        "--workers", "-w",
        type=str,
        required=True,
        help="Comma-separated worker types: 'coder,reviewer,tester' or 'research:2,write:1'"
    )
    
    parser.add_argument(
        "--strategy",
        choices=["adaptive", "fixed", "iterative"],
        default="adaptive",
        help="Delegation strategy (default: adaptive)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum execution iterations (default: 5)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show supervisor reasoning and progress"
    )
    
    parser.add_argument(
        "--no-synthesize",
        action="store_true",
        help="Return raw worker outputs without final synthesis"
    )
    
    parser.add_argument(
        "--state-file",
        type=str,
        default=".supervisor_state.json",
        help="State file for session tracking"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    args = parser.parse_args()
    
    # Parse worker definitions
    worker_configs = parse_worker_definitions(args.workers)
    
    if not worker_configs:
        print("ERROR: No valid workers specified", file=sys.stderr)
        sys.exit(1)
    
    return SupervisorConfig(
        task=args.task,
        workers=worker_configs,
        strategy=DelegationStrategy(args.strategy),
        max_iterations=args.max_iterations,
        verbose=args.verbose,
        synthesize_final=not args.no_synthesize,
        state_file=args.state_file
    )


def main():
    """CLI entry point for Supervisor pattern."""
    config = parse_arguments()
    
    if config.verbose:
        print(f"Supervisor Configuration:", file=sys.stderr)
        print(f"  Task: {config.task[:80]}...", file=sys.stderr)
        print(f"  Workers: {[w.name for w in config.workers]}", file=sys.stderr)
        print(f"  Strategy: {config.strategy.value}", file=sys.stderr)
        print(f"  Max Iterations: {config.max_iterations}", file=sys.stderr)
        print(f"", file=sys.stderr)
    
    # Run the supervisor
    supervisor = Supervisor(config)
    result = supervisor.run()
    
    # Output results
    if result["success"]:
        if config.verbose:
            print(f"\n{'=' * 60}", file=sys.stderr)
            print(f"SUPERVISOR EXECUTION SUMMARY", file=sys.stderr)
            print(f"{'=' * 60}", file=sys.stderr)
            print(f"Steps Executed: {result['steps_executed']}", file=sys.stderr)
            print(f"Workers Used: {', '.join(result['workers_used'])}", file=sys.stderr)
            print(f"Complexity: {result['analysis'].get('complexity', 'unknown')}", file=sys.stderr)
            print(f"{'=' * 60}", file=sys.stderr)
        
        # Output the final result to stdout
        print(result["final_output"])
        
        return 0
    else:
        print(f"ERROR: {result.get('error', 'Unknown error')}", file=sys.stderr)
        if result.get("final_output"):
            print("\nPartial output:", file=sys.stderr)
            print(result["final_output"])
        return 1


if __name__ == "__main__":
    sys.exit(main())
