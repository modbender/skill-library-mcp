"""
CLI entry point for agent-orchestrator skill.

Provides commands for 5 multi-agent patterns:
- crew: Work Crew (parallel execution)
- supervise: Supervisor (orchestrator-worker)
- pipeline: Staged Pipeline (sequential assembly)
- council: Expert Council (multi-expert deliberation)
- route: Auto-Routing (dynamic classification)

Usage:
    claw agent-orchestrator crew --task "Research topic" --agents 5
    claw agent-orchestrator supervise --task "Code review" --workers coder,reviewer
    claw agent-orchestrator pipeline --stages research,draft,review
    claw agent-orchestrator council --experts legal,technical,business
    claw agent-orchestrator route --task "Mixed task"
"""

import argparse
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main CLI dispatcher for agent-orchestrator commands."""
    parser = argparse.ArgumentParser(
        description="Multi-agent orchestration for OpenClaw",
        prog="claw agent-orchestrator"
    )
    
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="agent-orchestrator 0.1.0"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="Multi-agent pattern to execute",
        metavar="PATTERN"
    )
    
    # === CREW Command (Work Crew Pattern - MVP) ===
    crew_parser = subparsers.add_parser(
        "crew",
        help="Work Crew: Spawn parallel agents, aggregate results",
        description="Multiple agents tackle the same task from different angles simultaneously, then aggregate results."
    )
    
    crew_parser.add_argument(
        "--task", "-t",
        required=True,
        help="The task to assign to the crew"
    )
    
    crew_parser.add_argument(
        "--agents", "-n",
        type=int,
        default=3,
        help="Number of agents to spawn (default: 3)"
    )
    
    crew_parser.add_argument(
        "--perspectives", "-p",
        type=str,
        default="",
        help="Comma-separated perspectives: 'technical,business,security'"
    )
    
    crew_parser.add_argument(
        "--converge", "-c",
        choices=["consensus", "best-of", "merge", "all"],
        default="consensus",
        help="Result aggregation: consensus, best-of, merge, all (default: consensus)"
    )
    
    crew_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout per agent in seconds (default: 300)"
    )
    
    crew_parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    # === SUPERVISE Command (Supervisor Pattern - Phase 2) ===
    supervise_parser = subparsers.add_parser(
        "supervise",
        help="Supervisor: Orchestrator-worker with dynamic delegation (Phase 2)",
        description="A central supervisor agent coordinates workers, breaking down tasks and delegating dynamically."
    )
    
    supervise_parser.add_argument(
        "--task", "-t",
        required=True,
        help="The task to supervise"
    )
    
    supervise_parser.add_argument(
        "--workers", "-w",
        type=str,
        required=True,
        help="Comma-separated worker types: 'coder,reviewer,tester'"
    )
    
    supervise_parser.add_argument(
        "--strategy",
        choices=["adaptive", "fixed", "iterative"],
        default="adaptive",
        help="Delegation strategy (default: adaptive)"
    )
    
    supervise_parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum delegation iterations (default: 5)"
    )
    
    supervise_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show supervisor reasoning and progress"
    )
    
    supervise_parser.add_argument(
        "--no-synthesize",
        action="store_true",
        help="Return raw worker outputs without final synthesis"
    )
    
    # === PIPELINE Command (Staged Pipeline - Phase 2) ===
    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Pipeline: Sequential staged processing (Phase 2)",
        description="Work flows through a fixed sequence of stages, each agent transforming the output of the previous."
    )
    
    pipeline_parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to JSON pipeline configuration file"
    )
    
    pipeline_parser.add_argument(
        "--stages", "-s",
        type=str,
        help="Comma-separated stages: 'research,draft,review,finalize'"
    )
    
    pipeline_parser.add_argument(
        "--input", "-i",
        type=str,
        help="Initial input or topic for the pipeline"
    )
    
    pipeline_parser.add_argument(
        "--task", "-t",
        type=str,
        help="Task description (alternative to --input)"
    )
    
    pipeline_parser.add_argument(
        "--context-passing",
        choices=["full", "summary", "minimal"],
        default="full",
        help="How much context passes between stages (default: full)"
    )
    
    pipeline_parser.add_argument(
        "--on-failure",
        choices=["stop", "continue", "skip"],
        default="stop",
        help="How to handle stage failures (default: stop)"
    )
    
    pipeline_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show pipeline progress and stage details"
    )
    
    pipeline_parser.add_argument(
        "--state-file",
        type=str,
        default=".pipeline_state.json",
        help="State file for session tracking"
    )
    
    # === COUNCIL Command (Expert Council) ===
    council_parser = subparsers.add_parser(
        "council",
        help="Council: Multi-expert deliberation and consensus",
        description="Multiple specialized experts deliberate on a question through structured rounds."
    )

    council_parser.add_argument(
        "--experts", "-e",
        type=str,
        required=True,
        help="Comma-separated experts: 'skeptic,optimist,technician,economist,ethicist,strategist'"
    )

    council_parser.add_argument(
        "--question", "-q",
        type=str,
        required=True,
        help="The question or proposal for the council to deliberate"
    )

    council_parser.add_argument(
        "--converge", "-c",
        type=str,
        choices=["consensus", "majority", "divergent"],
        default="consensus",
        help="Convergence method: consensus (unanimous), majority (>50%%), divergent (preserve views)"
    )

    council_parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=2,
        help="Number of deliberation rounds (default: 2)"
    )

    council_parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout per expert in seconds (default: 300)"
    )

    council_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show council deliberation progress"
    )

    council_parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    # === ROUTE Command (Auto-Routing - Phase 2) ===
    route_parser = subparsers.add_parser(
        "route",
        help="Route: Dynamic task classification and specialist selection (Phase 2)",
        description="A routing agent analyzes requests and dynamically selects the most appropriate specialist."
    )

    route_parser.add_argument(
        "--task", "-t",
        required=True,
        help="The task to route to appropriate specialists"
    )

    route_parser.add_argument(
        "--specialists", "-s",
        type=str,
        default="",
        help="Available specialists: 'coder,researcher,writer,analyst' (default: all)"
    )

    route_parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.7,
        help="Minimum confidence to auto-route (default: 0.7)"
    )

    route_parser.add_argument(
        "--force",
        type=str,
        choices=["coder", "researcher", "writer", "analyst", "planner", "reviewer", "creative", "data", "devops", "support"],
        help="Force routing to specific specialist"
    )

    route_parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    route_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show routing analysis details"
    )

    route_parser.add_argument(
        "--state-file",
        type=str,
        default=".router_state.json",
        help="State file for routing history"
    )
    
    # Parse args
    args = parser.parse_args()
    
    # Handle no command
    if not args.command:
        parser.print_help()
        return 1
    
    # Route to appropriate pattern implementation
    if args.command == "crew":
        # Import and run Work Crew
        from crew import WorkCrew, ConvergenceMethod, CrewConfig
        
        perspectives = [p.strip() for p in args.perspectives.split(",") if p.strip()]
        
        config = CrewConfig(
            task=args.task,
            agent_count=args.agents,
            perspectives=perspectives,
            converge=ConvergenceMethod(args.converge),
            timeout=args.timeout,
            output_format=args.format
        )
        
        crew = WorkCrew(config)
        result = crew.run()
        
        if result["success"]:
            print(result["aggregated_output"])
            return 0
        else:
            print(f"Error: {result.get('error')}", file=sys.stderr)
            return 1
    
    elif args.command == "supervise":
        # Import and run Supervisor
        from supervise import Supervisor, DelegationStrategy, SupervisorConfig, parse_worker_definitions
        
        # Parse worker definitions
        worker_configs = parse_worker_definitions(args.workers)
        
        if not worker_configs:
            print("ERROR: No valid workers specified", file=sys.stderr)
            return 1
        
        config = SupervisorConfig(
            task=args.task,
            workers=worker_configs,
            strategy=DelegationStrategy(args.strategy),
            max_iterations=args.max_iterations,
            verbose=getattr(args, 'verbose', False),
            synthesize_final=not getattr(args, 'no_synthesize', False),
            state_file=getattr(args, 'state_file', '.supervisor_state.json')
        )
        
        supervisor = Supervisor(config)
        result = supervisor.run()
        
        if result["success"]:
            print(result["final_output"])
            return 0
        else:
            print(f"Error: {result.get('error')}", file=sys.stderr)
            if result.get("final_output"):
                print("\nPartial output:", file=sys.stderr)
                print(result["final_output"])
            return 1
    
    elif args.command == "pipeline":
        # Import and run Pipeline
        from pipeline import Pipeline, ContextPassing, FailureHandling, PipelineConfig, parse_inline_stages
        
        # Determine input source
        input_data = getattr(args, 'input', '') or getattr(args, 'task', '')
        
        # Build configuration
        if getattr(args, 'config', None):
            # Load from config file
            pipeline = Pipeline.from_config_file(args.config)
        elif getattr(args, 'stages', None):
            # Parse inline stages
            stages = parse_inline_stages(args.stages, input_data)
            
            # Apply failure handling default
            failure_handling = FailureHandling(getattr(args, 'on_failure', 'stop'))
            for stage in stages:
                stage.on_failure = failure_handling
            
            config = PipelineConfig(
                name="cli-pipeline",
                stages=stages,
                input_data=input_data,
                context_passing=ContextPassing(getattr(args, 'context_passing', 'full')),
                verbose=getattr(args, 'verbose', False),
                state_file=getattr(args, 'state_file', '.pipeline_state.json')
            )
            pipeline = Pipeline(config)
        else:
            print("ERROR: Pipeline requires --config or --stages", file=sys.stderr)
            return 1
        
        # Run pipeline
        result = pipeline.run()
        
        if result["success"]:
            print(result["final_output"])
            return 0
        else:
            print(f"Pipeline completed with failures", file=sys.stderr)
            # Still output what we have
            if result.get("final_output"):
                print("\n--- PARTIAL OUTPUT ---", file=sys.stderr)
                print(result["final_output"])
            return 1
    
    elif args.command == "council":
        # Import and run Expert Council
        from council import Council, CouncilConfig, ConvergenceMethod, parse_experts

        # Parse experts list
        expert_list = [e.strip() for e in args.experts.split(",")]
        experts = parse_experts(expert_list)

        if not experts:
            print("ERROR: No valid experts specified", file=sys.stderr)
            print("Valid experts: skeptic, optimist, technician, economist, ethicist, strategist, legal, security, business, technical", file=sys.stderr)
            return 1

        config = CouncilConfig(
            question=args.question,
            experts=experts,
            converge=ConvergenceMethod(args.converge),
            rounds=args.rounds,
            timeout=args.timeout,
            verbose=getattr(args, 'verbose', False),
            output_format=args.format
        )

        # Run the council
        council = Council(config)
        result = council.run()

        # Format and output result
        from council import format_output_markdown, format_output_json, format_output_text

        if args.format == "json":
            print(format_output_json(result))
        elif args.format == "text":
            print(format_output_text(result))
        else:  # markdown
            print(format_output_markdown(result))

        # Return non-zero if no consensus (unless divergent mode)
        if not result['consensus_reached'] and args.converge != "divergent":
            return 2  # Deliberation completed but consensus not reached

        return 0
    
    elif args.command == "route":
        # Import and run Auto-Router
        from route import (
            TaskRouter, parse_specialist_list, SpecialistRole,
            format_output_text, format_output_json, format_output_markdown
        )
        
        # Parse specialists
        available_specialists = parse_specialist_list(
            getattr(args, 'specialists', '') or ''
        )
        
        # Create router
        router = TaskRouter(
            available_specialists=available_specialists,
            confidence_threshold=getattr(args, 'confidence_threshold', 0.7),
            state_file=getattr(args, 'state_file', '.router_state.json')
        )
        
        # Parse force specialist if provided
        force_specialist = None
        if hasattr(args, 'force') and args.force:
            try:
                force_specialist = SpecialistRole(args.force)
            except ValueError:
                print(f"Warning: Invalid force specialist '{args.force}'", file=sys.stderr)
        
        # Route the task
        result = router.route(args.task, force_specialist=force_specialist)
        
        # Format output
        output_format = getattr(args, 'format', 'markdown')
        if output_format == "text":
            print(format_output_text(result))
        elif output_format == "json":
            print(format_output_json(result))
        else:  # markdown
            print(format_output_markdown(result))
        
        # Return exit code
        if result.needs_clarification:
            return 2  # Indicates clarification needed
        return 0
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
