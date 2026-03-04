"""
Staged Pipeline Pattern Implementation

Work flows through a fixed sequence of stages, with each agent
transforming the output of the previous stage.

Stage Types:
- transform: Modify data (summarize, expand, rewrite)
- validate: Check quality, gate progression
- enrich: Add context or detail
- format: Convert to final output format

Use this for:
- Well-defined sequential processes
- Content creation (extract → analyze → write → review)
- Progressive refinement workflows
- Verification chains with quality gates
- ETL-like data transformation pipelines

Example:
    pipeline = Pipeline.from_config_file("content-pipeline.json")
    result = pipeline.run()

Or inline:
    config = PipelineConfig(
        stages=[
            StageConfig(name="extract", type=StageType.EXTRACT, prompt="Extract key facts..."),
            StageConfig(name="analyze", type=StageType.ANALYZE, prompt="Analyze patterns..."),
            StageConfig(name="write", type=StageType.WRITE, prompt="Write content..."),
        ],
        input_data="Bitcoin Lightning adoption trends"
    )
    pipeline = Pipeline(config)
    result = pipeline.run()
"""

import argparse
import json
import sys
from enum import Enum
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime

from utils import SessionManager, AgentResult, SessionState


class StageType(Enum):
    """Types of pipeline stages with specific behaviors."""
    EXTRACT = "extract"      # Pull information from input
    TRANSFORM = "transform"  # Modify/summarize/expand data
    VALIDATE = "validate"    # Check quality, gate progression
    ENRICH = "enrich"        # Add context or detail
    ANALYZE = "analyze"      # Deep analysis and insights
    WRITE = "write"          # Content creation
    REVIEW = "review"        # Critical review and feedback
    FORMAT = "format"        # Convert to final output format
    CUSTOM = "custom"        # User-defined behavior


class ContextPassing(Enum):
    """How context flows between pipeline stages."""
    FULL = "full"          # Pass entire previous output
    SUMMARY = "summary"    # Pass condensed summary (first 2000 chars)
    MINIMAL = "minimal"    # Pass only essential metadata


class FailureHandling(Enum):
    """How to handle stage failures."""
    STOP = "stop"           # Halt pipeline on failure
    CONTINUE = "continue"   # Continue with warning
    SKIP = "skip"           # Skip failed stage, use previous output


class StageStatus(Enum):
    """Status of individual pipeline stages."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNED = "warned"       # Completed but with issues


@dataclass
class StageConfig:
    """Configuration for a single pipeline stage."""
    name: str                           # Stage identifier
    type: StageType                     # Stage behavior type
    prompt: Optional[str] = None        # Custom prompt template
    system_prompt: Optional[str] = None # System instructions
    timeout: int = 300                  # Stage timeout in seconds
    on_failure: FailureHandling = FailureHandling.STOP
    gate_check: Optional[str] = None    # Validation criteria for gate stages
    output_format: Optional[str] = None # Expected output format
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type.value,
            "prompt": self.prompt,
            "system_prompt": self.system_prompt,
            "timeout": self.timeout,
            "on_failure": self.on_failure.value,
            "gate_check": self.gate_check,
            "output_format": self.output_format
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StageConfig':
        """Create StageConfig from dictionary (JSON/YAML-like)."""
        return cls(
            name=data["name"],
            type=StageType(data.get("type", "custom")),
            prompt=data.get("prompt"),
            system_prompt=data.get("system_prompt"),
            timeout=data.get("timeout", 300),
            on_failure=FailureHandling(data.get("on_failure", "stop")),
            gate_check=data.get("gate_check"),
            output_format=data.get("output_format")
        )


@dataclass
class PipelineConfig:
    """Configuration for Pipeline execution."""
    name: Optional[str] = None          # Pipeline name
    description: Optional[str] = None   # Pipeline description
    stages: List[StageConfig] = field(default_factory=list)
    input_data: str = ""                # Initial input for first stage
    context_passing: ContextPassing = ContextPassing.FULL
    state_file: Optional[str] = None
    verbose: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "stages": [s.to_dict() for s in self.stages],
            "input_data": self.input_data,
            "context_passing": self.context_passing.value,
            "verbose": self.verbose
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineConfig':
        """Create PipelineConfig from dictionary."""
        stages = [
            StageConfig.from_dict(s) for s in data.get("stages", [])
        ]
        return cls(
            name=data.get("name"),
            description=data.get("description"),
            stages=stages,
            input_data=data.get("input_data", ""),
            context_passing=ContextPassing(data.get("context_passing", "full")),
            verbose=data.get("verbose", False)
        )


@dataclass
class StageResult:
    """Result from a single pipeline stage execution."""
    stage_name: str
    stage_type: StageType
    status: StageStatus
    input_data: str
    output_data: str
    duration_ms: int
    timestamp: str
    error: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage_name": self.stage_name,
            "stage_type": self.stage_type.value,
            "status": self.status.value,
            "input_preview": self.input_data[:200] + "..." if len(self.input_data) > 200 else self.input_data,
            "output_preview": self.output_data[:200] + "..." if len(self.output_data) > 200 else self.output_data,
            "duration_ms": self.duration_ms,
            "timestamp": self.timestamp,
            "error": self.error,
            "warnings": self.warnings
        }


class Pipeline:
    """
    Pipeline pattern: Sequential staged processing.
    
    Work moves through fixed stages with each stage's output
    becoming the next stage's input. Supports:
    - Multiple stage types with specialized behaviors
    - Data transformation between stages
    - Validation gates that can halt progression
    - Context passing strategies (full/summary/minimal)
    - Progress tracking and stage-by-stage visibility
    - Failure handling (stop/continue/skip)
    
    Example:
        config = PipelineConfig(
            stages=[
                StageConfig(name="extract", type=StageType.EXTRACT),
                StageConfig(name="analyze", type=StageType.ANALYZE),
                StageConfig(name="validate", type=StageType.VALIDATE),
                StageConfig(name="format", type=StageType.FORMAT),
            ],
            input_data="Research topic: AI agent adoption"
        )
        pipeline = Pipeline(config)
        result = pipeline.run()
    """
    
    # Default prompts for each stage type
    DEFAULT_PROMPTS = {
        StageType.EXTRACT: """You are an information extraction specialist.
Your task is to identify and extract key information, facts, and data points.
Be thorough and structured in your extraction.
Output: List of extracted facts and information.""",
        
        StageType.TRANSFORM: """You are a data transformation specialist.
Your task is to transform the input according to the specific requirements.
This may include summarizing, expanding, rewriting, or restructuring content.
Maintain accuracy while performing the transformation.""",
        
        StageType.VALIDATE: """You are a quality validation specialist.
Your task is to critically evaluate the input against quality criteria.
Assess: accuracy, completeness, clarity, and appropriateness.
Output: Validation report with PASS/FAIL determination and specific issues found.""",
        
        StageType.ENRICH: """You are a content enrichment specialist.
Your task is to add valuable context, examples, details, and supporting information.
Enhance the content while maintaining its core meaning.
Make it more comprehensive and useful.""",
        
        StageType.ANALYZE: """You are an analysis specialist.
Your task is to perform deep analysis of the input.
Identify patterns, trends, insights, and implications.
Provide structured analysis with clear conclusions.""",
        
        StageType.WRITE: """You are a content creation specialist.
Your task is to produce high-quality written content based on the input.
Write clearly, engagingly, and appropriately for the target audience.
Follow any specified format or style guidelines.""",
        
        StageType.REVIEW: """You are a critical review specialist.
Your task is to review content and provide constructive feedback.
Identify strengths, weaknesses, errors, and improvement opportunities.
Output: Structured review with actionable recommendations.""",
        
        StageType.FORMAT: """You are a formatting specialist.
Your task is to convert content to the specified final output format.
Ensure proper structure, styling, and presentation.
Apply any required formatting standards.""",
        
        StageType.CUSTOM: """You are a specialized processing agent.
Execute your assigned task with expertise and attention to detail.
Provide high-quality output appropriate to the task requirements."""
    }
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.session_manager = SessionManager(state_file=config.state_file)
        self.stage_results: List[StageResult] = []
        self.current_stage_index = 0
        self.warnings: List[str] = []
        self.execution_start: Optional[datetime] = None
    
    def _log(self, message: str, level: str = "info"):
        """Log message if verbose mode enabled."""
        if self.config.verbose:
            prefix = "[PIPELINE]"
            if level == "error":
                prefix = "[PIPELINE ERROR]"
            elif level == "warn":
                prefix = "[PIPELINE WARN]"
            elif level == "success":
                prefix = "[PIPELINE SUCCESS]"
            print(f"{prefix} {message}", file=sys.stderr)
    
    def _build_stage_prompt(self, stage: StageConfig, stage_input: str) -> str:
        """Build the complete prompt for a stage agent."""
        # Get base system prompt
        if stage.system_prompt:
            system_prompt = stage.system_prompt
        else:
            system_prompt = self.DEFAULT_PROMPTS.get(stage.type, self.DEFAULT_PROMPTS[StageType.CUSTOM])
        
        # Add custom prompt if provided
        custom_instructions = ""
        if stage.prompt:
            custom_instructions = f"\n\nSpecific Instructions:\n{stage.prompt}"
        
        # Add output format if specified
        output_format = ""
        if stage.output_format:
            output_format = f"\n\nRequired Output Format:\n{stage.output_format}"
        
        # Build full prompt
        prompt = f"""{system_prompt}{custom_instructions}{output_format}

{'='*60}
INPUT TO PROCESS:

{stage_input}

{'='*60}

Execute your task on the input above. Provide your output clearly labeled.
Start your response with [STAGE: {stage.name.upper()}] and then provide your output."""
        
        # Add validation criteria for validate stages
        if stage.type == StageType.VALIDATE and stage.gate_check:
            prompt += f"""

VALIDATION CRITERIA:
{stage.gate_check}

You must explicitly state PASS or FAIL based on these criteria."""
        
        return prompt
    
    def _pass_context(self, output: str) -> str:
        """Transform output for next stage based on context_passing strategy."""
        strategy = self.config.context_passing
        
        if strategy == ContextPassing.FULL:
            return output
        
        elif strategy == ContextPassing.SUMMARY:
            # Limit to first 2000 chars as simple summary
            if len(output) > 2000:
                return output[:2000] + "\n\n[... Content truncated for summary mode ...]"
            return output
        
        elif strategy == ContextPassing.MINIMAL:
            # Pass only metadata and key line
            lines = output.split('\n')
            header = "[MINIMAL CONTEXT MODE - Previous stage complete. Key excerpt follows:]\n\n"
            # Get first non-empty line as key excerpt
            key_line = next((l for l in lines if l.strip()), "[No content]")
            return header + key_line
        
        return output
    
    def _check_validation_gate(self, stage: StageConfig, output: str) -> tuple[bool, List[str]]:
        """
        Check if validation stage passed its gate.
        
        Returns:
            (passed, warnings): Boolean and list of warning messages
        """
        if stage.type != StageType.VALIDATE:
            return True, []
        
        warnings = []
        output_lower = output.lower()
        
        # Check for explicit PASS/FAIL
        has_pass = "pass" in output_lower and "fail" not in output_lower.replace("failed", "").replace("failures", "")
        has_fail = "fail" in output_lower
        
        if has_fail or not has_pass:
            warnings.append("Validation stage did not report PASS")
        
        # Check against specific gate criteria if provided
        if stage.gate_check:
            criteria_met = self._evaluate_gate_criteria(output, stage.gate_check)
            if not criteria_met:
                warnings.append("Validation criteria not fully met")
        
        passed = len(warnings) == 0
        return passed, warnings
    
    def _evaluate_gate_criteria(self, output: str, criteria: str) -> bool:
        """Simple heuristic check against gate criteria."""
        # Simple implementation: check if key terms from criteria appear in output
        # In production, this could use another LLM call or more sophisticated parsing
        criteria_terms = [t.strip().lower() for t in criteria.replace(",", " ").split() if len(t.strip()) > 3]
        output_lower = output.lower()
        
        matches = sum(1 for term in criteria_terms if term in output_lower)
        return matches >= len(criteria_terms) * 0.5  # At least 50% of criteria terms found
    
    def execute_stage(self, stage: StageConfig, stage_input: str) -> StageResult:
        """
        Execute a single pipeline stage.
        
        Args:
            stage: Stage configuration
            stage_input: Input for this stage
            
        Returns:
            StageResult with output, status, and metadata
        """
        start_time = datetime.now()
        self._log(f"Starting stage: {stage.name} ({stage.type.value})")
        
        try:
            # Build stage prompt
            prompt = self._build_stage_prompt(stage, stage_input)
            
            # Spawn stage agent
            agent_id = self.session_manager.spawn_session(
                task=prompt,
                agent_label=f"stage-{stage.name}",
                context={
                    "stage_name": stage.name,
                    "stage_type": stage.type.value,
                    "pipeline_name": self.config.name or "unnamed"
                }
            )
            
            # Collect result
            results = self.session_manager.collect_all_results(timeout=stage.timeout)
            
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            
            if agent_id in results:
                result = results[agent_id]
                
                if result.state == SessionState.COMPLETED and result.output:
                    output = result.output
                    
                    # Check validation for gate stages
                    if stage.type == StageType.VALIDATE:
                        passed, warnings = self._check_validation_gate(stage, output)
                        if not passed:
                            self._log(f"Stage {stage.name} validation FAILED", "warn")
                            return StageResult(
                                stage_name=stage.name,
                                stage_type=stage.type,
                                status=StageStatus.FAILED,
                                input_data=stage_input,
                                output_data=output,
                                duration_ms=duration,
                                timestamp=start_time.isoformat(),
                                error="Validation gate failed",
                                warnings=warnings
                            )
                        if warnings:
                            self._log(f"Stage {stage.name} completed with warnings", "warn")
                            return StageResult(
                                stage_name=stage.name,
                                stage_type=stage.type,
                                status=StageStatus.WARNED,
                                input_data=stage_input,
                                output_data=output,
                                duration_ms=duration,
                                timestamp=start_time.isoformat(),
                                warnings=warnings
                            )
                    
                    self._log(f"Stage {stage.name} completed successfully", "success")
                    return StageResult(
                        stage_name=stage.name,
                        stage_type=stage.type,
                        status=StageStatus.COMPLETED,
                        input_data=stage_input,
                        output_data=output,
                        duration_ms=duration,
                        timestamp=start_time.isoformat()
                    )
                else:
                    error = result.error or "Stage failed to complete"
                    self._log(f"Stage {stage.name} failed: {error}", "error")
                    return StageResult(
                        stage_name=stage.name,
                        stage_type=stage.type,
                        status=StageStatus.FAILED,
                        input_data=stage_input,
                        output_data="",
                        duration_ms=duration,
                        timestamp=start_time.isoformat(),
                        error=error
                    )
            else:
                self._log(f"Stage {stage.name} timeout - no result collected", "error")
                return StageResult(
                    stage_name=stage.name,
                    stage_type=stage.type,
                    status=StageStatus.FAILED,
                    input_data=stage_input,
                    output_data="",
                    duration_ms=duration,
                    timestamp=start_time.isoformat(),
                    error="Timeout - no result from agent"
                )
                
        except Exception as e:
            duration = int((datetime.now() - start_time).total_seconds() * 1000)
            self._log(f"Stage {stage.name} exception: {e}", "error")
            return StageResult(
                stage_name=stage.name,
                stage_type=stage.type,
                status=StageStatus.FAILED,
                input_data=stage_input,
                output_data="",
                duration_ms=duration,
                timestamp=start_time.isoformat(),
                error=str(e)
            )
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the full Pipeline workflow through all stages.
        
        Returns:
            Dictionary with:
            - success: Boolean indicating overall success
            - final_output: Output from final stage (or last successful)
            - stages: List of all stage results
            - execution_time_ms: Total pipeline execution time
            - warnings: Any warnings generated during execution
        """
        self.execution_start = datetime.now()
        self._log(f"Starting pipeline: {self.config.name or 'unnamed'}")
        self._log(f"Stages: {[s.name for s in self.config.stages]}")
        self._log(f"Context passing: {self.config.context_passing.value}")
        
        current_input = self.config.input_data
        stage_results = []
        
        for i, stage in enumerate(self.config.stages):
            self.current_stage_index = i
            
            # Execute stage
            result = self.execute_stage(stage, current_input)
            stage_results.append(result)
            
            # Handle result
            if result.status == StageStatus.COMPLETED:
                # Success - pass output to next stage
                current_input = self._pass_context(result.output_data)
                
            elif result.status == StageStatus.WARNED:
                # Warning but continuing
                self.warnings.extend(result.warnings)
                current_input = self._pass_context(result.output_data)
                
            elif result.status == StageStatus.FAILED:
                # Failure - apply failure handling strategy
                if stage.on_failure == FailureHandling.STOP:
                    self._log(f"Pipeline halted at stage {stage.name} (STOP on failure)", "error")
                    break
                elif stage.on_failure == FailureHandling.CONTINUE:
                    self._log(f"Continuing pipeline despite failure in {stage.name}", "warn")
                    self.warnings.append(f"Stage {stage.name} failed but pipeline continuing: {result.error}")
                    # Continue with same input
                elif stage.on_failure == FailureHandling.SKIP:
                    self._log(f"Skipping failed stage {stage.name}", "warn")
                    self.warnings.append(f"Stage {stage.name} skipped due to failure: {result.error}")
                    # Continue with same input (don't update)
            
            import time
            time.sleep(1)  # Small delay between stages
        
        total_duration = int((datetime.now() - self.execution_start).total_seconds() * 1000)
        
        # Determine final output
        completed_stages = [r for r in stage_results if r.status in (StageStatus.COMPLETED, StageStatus.WARNED)]
        if completed_stages:
            final_output = completed_stages[-1].output_data
        else:
            final_output = "[No stages completed successfully]"
        
        # Determine success
        all_completed = all(r.status == StageStatus.COMPLETED for r in stage_results)
        no_failures = all(r.status != StageStatus.FAILED for r in stage_results)
        success = no_failures or (len(completed_stages) > 0 and any(r.status == StageStatus.COMPLETED for r in stage_results))
        
        self._log(f"Pipeline complete: {len(completed_stages)}/{len(stage_results)} stages successful")
        
        return {
            "success": success,
            "pipeline_name": self.config.name,
            "total_stages": len(self.config.stages),
            "completed_stages": len([r for r in stage_results if r.status == StageStatus.COMPLETED]),
            "failed_stages": len([r for r in stage_results if r.status == StageStatus.FAILED]),
            "execution_time_ms": total_duration,
            "final_output": final_output,
            "stages": [r.to_dict() for r in stage_results],
            "warnings": self.warnings,
            "config": self.config.to_dict()
        }
    
    @classmethod
    def from_config_file(cls, file_path: str) -> 'Pipeline':
        """Create a Pipeline from a JSON configuration file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        config = PipelineConfig.from_dict(data)
        return cls(config)


def parse_inline_stages(stages_str: str, task_str: str) -> List[StageConfig]:
    """
    Parse inline stage definitions from CLI string.
    
    Format: "extract,analyze,write,review"
    Maps generic names to appropriate stage types.
    """
    stages = []
    stage_names = [s.strip() for s in stages_str.split(",") if s.strip()]
    
    # Map common names to types
    type_mapping = {
        "extract": StageType.EXTRACT,
        "pull": StageType.EXTRACT,
        "gather": StageType.EXTRACT,
        "fetch": StageType.EXTRACT,
        "transform": StageType.TRANSFORM,
        "convert": StageType.TRANSFORM,
        "rewrite": StageType.TRANSFORM,
        "summarize": StageType.TRANSFORM,
        "validate": StageType.VALIDATE,
        "check": StageType.VALIDATE,
        "verify": StageType.VALIDATE,
        "gate": StageType.VALIDATE,
        "enrich": StageType.ENRICH,
        "expand": StageType.ENRICH,
        "enhance": StageType.ENRICH,
        "detail": StageType.ENRICH,
        "analyze": StageType.ANALYZE,
        "analysis": StageType.ANALYZE,
        "research": StageType.ANALYZE,
        "write": StageType.WRITE,
        "draft": StageType.WRITE,
        "create": StageType.WRITE,
        "compose": StageType.WRITE,
        "review": StageType.REVIEW,
        "critique": StageType.REVIEW,
        "feedback": StageType.REVIEW,
        "format": StageType.FORMAT,
        "finalize": StageType.FORMAT,
        "polish": StageType.FORMAT,
        "render": StageType.FORMAT,
    }
    
    for i, name in enumerate(stage_names):
        # Determine type from name mapping or use default
        stage_type = type_mapping.get(name.lower(), StageType.CUSTOM)
        
        # Build prompt based on position and task
        if i == 0:
            prompt = f"Begin processing this task: {task_str}"
        elif i == len(stage_names) - 1:
            prompt = "Produce the final polished output."
        else:
            prompt = f"Continue the workflow from the previous stage output."
        
        config = StageConfig(
            name=name,
            type=stage_type,
            prompt=prompt
        )
        stages.append(config)
    
    return stages


def main():
    """CLI entry point for Pipeline pattern."""
    parser = argparse.ArgumentParser(
        description="Pipeline Pattern: Sequential staged multi-agent processing",
        prog="claw agent-orchestrator pipeline"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to JSON pipeline configuration file"
    )
    
    parser.add_argument(
        "--stages", "-s",
        type=str,
        help="Comma-separated stage names (e.g., 'extract,analyze,write,review')"
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="Initial input or topic for the pipeline"
    )
    
    parser.add_argument(
        "--task", "-t",
        type=str,
        help="Task description (alternative to --input)"
    )
    
    parser.add_argument(
        "--context-passing",
        choices=["full", "summary", "minimal"],
        default="full",
        help="How much context passes between stages (default: full)"
    )
    
    parser.add_argument(
        "--on-failure",
        choices=["stop", "continue", "skip"],
        default="stop",
        help="How to handle stage failures (default: stop)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show pipeline progress and stage details"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format for result (default: markdown)"
    )
    
    parser.add_argument(
        "--state-file",
        type=str,
        default=".pipeline_state.json",
        help="State file for session tracking"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.config and not args.stages:
        print("ERROR: Must provide either --config or --stages", file=sys.stderr)
        return 1
    
    if not args.config and not (args.input or args.task):
        print("ERROR: Must provide --input or --task when using --stages", file=sys.stderr)
        return 1
    
    try:
        # Build configuration
        if args.config:
            # Load from config file
            print(f"Loading pipeline from: {args.config}", file=sys.stderr)
            pipeline = Pipeline.from_config_file(args.config)
        else:
            # Parse inline stages
            input_data = args.input or args.task or ""
            stages = parse_inline_stages(args.stages, input_data)
            
            # Update failure handling for all stages
            failure_handling = FailureHandling(args.on_failure)
            for stage in stages:
                stage.on_failure = failure_handling
            
            config = PipelineConfig(
                name="inline-pipeline",
                stages=stages,
                input_data=input_data,
                context_passing=ContextPassing(args.context_passing),
                verbose=args.verbose,
                state_file=args.state_file
            )
            pipeline = Pipeline(config)
        
        # Run pipeline
        if args.verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"PIPELINE EXECUTION", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)
        
        result = pipeline.run()
        
        # Output results
        if args.verbose:
            print(f"\n{'='*60}", file=sys.stderr)
            print(f"PIPELINE SUMMARY", file=sys.stderr)
            print(f"{'='*60}", file=sys.stderr)
            print(f"Total Stages: {result['total_stages']}", file=sys.stderr)
            print(f"Completed: {result['completed_stages']}", file=sys.stderr)
            print(f"Failed: {result['failed_stages']}", file=sys.stderr)
            print(f"Execution Time: {result['execution_time_ms']}ms", file=sys.stderr)
            if result['warnings']:
                print(f"Warnings: {len(result['warnings'])}", file=sys.stderr)
            print(f"{'='*60}\n", file=sys.stderr)
        
        # Format output
        if args.output_format == "json":
            print(json.dumps(result, indent=2))
        elif args.output_format == "markdown":
            # Output final result as markdown
            if result['success']:
                print(result['final_output'])
            else:
                print(f"## Pipeline Execution Failed\n")
                print(f"Completed: {result['completed_stages']}/{result['total_stages']} stages\n")
                for stage in result['stages']:
                    if stage['status'] == 'failed':
                        print(f"**Failed Stage:** {stage['stage_name']}")
                        print(f"- Error: {stage.get('error', 'Unknown error')}\n")
                if result['warnings']:
                    print(f"### Warnings\n")
                    for w in result['warnings']:
                        print(f"- {w}")
        else:
            # text format
            print(result['final_output'])
        
        return 0 if result['success'] else 1
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERROR: Pipeline execution failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
