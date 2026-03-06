"""
Work Crew Pattern Implementation

Spawns multiple agents to tackle the same task from different angles,
then aggregates results using a convergence strategy.

Use this for:
- Breadth-first research (multiple perspectives)
- Verification tasks (redundancy for confidence)
- Multi-aspect analysis (parallel processing)
- Best-of-N attempts (quality through repetition)
"""

import argparse
import json
import sys
from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from utils import SessionManager, AgentResult, SessionState, spawn_agent, collect_results


class ConvergenceMethod(Enum):
    """Strategies for aggregating Work Crew results."""
    CONSENSUS = "consensus"  # Find common ground across all outputs
    BEST_OF = "best-of"      # Select the single best output
    MERGE = "merge"          # Combine all outputs into comprehensive result
    ALL = "all"              # Return all outputs without aggregation


@dataclass
class CrewConfig:
    """Configuration for a Work Crew execution."""
    task: str
    agent_count: int
    perspectives: List[str]
    converge: ConvergenceMethod
    timeout: int
    output_format: str
    state_file: Optional[str] = None


class WorkCrew:
    """
    Work Crew pattern: Parallel execution with result aggregation.
    
    Spawns N agents (optionally with different perspectives/focus areas)
    to work on the same task simultaneously, then aggregates their results.
    """
    
    def __init__(self, config: CrewConfig):
        self.config = config
        self.session_manager = SessionManager(state_file=config.state_file)
        self.results: Dict[str, AgentResult] = {}
    
    def _build_agent_task(self, perspective: Optional[str], index: int) -> str:
        """
        Build the task prompt for a specific agent.
        
        If perspectives are provided, each agent gets a different focus.
        Otherwise, agents work on identical tasks for redundancy.
        """
        base_task = self.config.task
        
        if perspective:
            return f"""Task: {base_task}

Your Focus/Perspective: {perspective}

Instructions:
1. Approach this task specifically from the {perspective} perspective
2. Consider aspects that are most relevant to {perspective}
3. Provide your analysis with this focus clearly labeled
4. Be thorough but concise in your response
5. Start your response with "[{perspective.upper()} PERSPECTIVE]\n\n"

Complete this task to the best of your ability."""
        else:
            return f"""Task: {base_task}

You are Agent {index + 1} of {self.config.agent_count} working on this task.
Instructions:
1. Work independently on this task
2. Provide your best attempt at a solution
3. Be thorough but concise
4. Start your response with "[AGENT {index + 1} OUTPUT]\n\n"

Complete this task to the best of your ability."""
    
    def spawn_crew(self) -> List[str]:
        """Spawn all agents in the crew. Returns list of agent IDs."""
        agent_ids = []
        perspectives = self.config.perspectives
        
        for i in range(self.config.agent_count):
            # Assign perspective if available
            perspective = perspectives[i] if i < len(perspectives) else None
            
            # Build task for this agent
            agent_task = self._build_agent_task(perspective, i)
            
            # Create label
            if perspective:
                label = f"{perspective.lower().replace(' ', '-')}-agent"
            else:
                label = f"agent-{i + 1}"
            
            # Spawn the agent
            print(f"Spawning {label}...", file=sys.stderr)
            try:
                agent_id = self.session_manager.spawn_session(
                    task=agent_task,
                    agent_label=label,
                    context={"perspective": perspective, "index": i}
                )
                agent_ids.append(agent_id)
            except Exception as e:
                print(f"Warning: Failed to spawn {label}: {e}", file=sys.stderr)
                # Continue with other agents
        
        return agent_ids
    
    def collect_crew_results(self, agent_ids: List[str]) -> Dict[str, AgentResult]:
        """Collect results from all crew agents."""
        print(f"\nCollecting results from {len(agent_ids)} agents...", file=sys.stderr)
        print(f"Timeout: {self.config.timeout} seconds", file=sys.stderr)
        
        self.results = self.session_manager.collect_all_results(
            timeout=self.config.timeout,
            poll_interval=5
        )
        
        # Filter to only requested agents
        self.results = {k: v for k, v in self.results.items() if k in agent_ids}
        
        return self.results
    
    def _aggregate_consensus(self, results: Dict[str, AgentResult]) -> str:
        """
        Aggregate results by finding consensus/common themes.
        Creates a synthesis that captures what most agents agreed on.
        """
        outputs = [r.output for r in results.values() if r.output]
        
        if not outputs:
            return "ERROR: No valid outputs to aggregate"
        
        if len(outputs) == 1:
            return outputs[0]
        
        # Build consensus prompt for a synthesizer
        consensus_task = f"""Analyze the following {len(outputs)} agent outputs and identify:
1. Key points of agreement/consensus
2. Any significant differences or outlier views
3. The most commonly supported conclusions
4. A synthesized recommendation based on majority consensus

Agent Outputs:
{"=" * 60}
"""
        for i, output in enumerate(outputs, 1):
            consensus_task += f"\n--- AGENT {i} OUTPUT ---\n{output}\n"
        
        consensus_task += f"\n{'=' * 60}\n\nProvide your consensus analysis in this format:\n"
        consensus_task += """
[CONSENSUS ANALYSIS]

Points of Agreement:
- 

Notable Differences:
- 

Synthesized Recommendation:
"""
        
        # Spawn a synthesizer agent
        print("Spawning consensus synthesizer...", file=sys.stderr)
        try:
            synthesizer_id = self.session_manager.spawn_session(
                task=consensus_task,
                agent_label="consensus-synthesizer",
                context={"aggregation": "consensus"}
            )
            
            # Collect single result
            synth_results = self.session_manager.collect_all_results(timeout=120)
            
            if synthesizer_id in synth_results:
                return synth_results[synthesizer_id].output
            else:
                # Fallback: simple concatenation with summary
                return self._simple_consensus(outputs)
                
        except Exception as e:
            print(f"Warning: Consensus synthesis failed: {e}", file=sys.stderr)
            return self._simple_consensus(outputs)
    
    def _simple_consensus(self, outputs: List[str]) -> str:
        """Fallback consensus when synthesizer fails."""
        return f"""[WORK CREW CONSENSUS - RAW AGGREGATION]

Note: Synthesizer agent failed, providing raw aggregation.

Number of Agents: {len(outputs)}

--- INDIVIDUAL OUTPUTS ---

""" + "\n\n---\n\n".join(outputs)
    
    def _aggregate_best_of(self, results: Dict[str, AgentResult]) -> str:
        """
        Select the single best output based on heuristics or evaluation.
        For MVP: returns the longest/most detailed output as a simple heuristic.
        """
        valid_results = [r for r in results.values() if r.state == SessionState.COMPLETED and r.output]
        
        if not valid_results:
            return "ERROR: No valid completed results"
        
        # Simple heuristic: longest output as proxy for "most thorough"
        # In production, could use quality evaluation agent
        best = max(valid_results, key=lambda r: len(r.output))
        
        # Build header
        header = f"""[WORK CREW BEST-OF SELECTION]

Selected from {len(valid_results)} agents.
Selected Agent: {best.agent_id}
Selection Reason: Most comprehensive output (by length)

--- BEST OUTPUT ---

"""
        return header + best.output
    
    def _aggregate_merge(self, results: Dict[str, AgentResult]) -> str:
        """
        Merge all outputs into a comprehensive result.
        For MVP: simple concatenation with headers.
        """
        outputs = []
        for agent_id, result in results.items():
            if result.output:
                outputs.append(f"### {agent_id}\n\n{result.output}")
        
        if not outputs:
            return "ERROR: No valid outputs to merge"
        
        header = f"""[WORK CREW MERGED OUTPUT]

Combined analysis from {len(outputs)} agents:

"""
        return header + "\n\n---\n\n".join(outputs)
    
    def _aggregate_all(self, results: Dict[str, AgentResult]) -> str:
        """Return all outputs in structured format without aggregation."""
        output_data = {
            "crew_config": {
                "task": self.config.task,
                "agent_count": self.config.agent_count,
                "perspectives": self.config.perspectives,
                "converge": self.config.converge.value
            },
            "results": {}
        }
        
        for agent_id, result in results.items():
            output_data["results"][agent_id] = result.to_dict()
        
        # Return as JSON for programmatic use
        return json.dumps(output_data, indent=2)
    
    def aggregate(self) -> str:
        """
        Aggregate results based on configured convergence method.
        
        Returns:
            The aggregated output as a string
        """
        if not self.results:
            return "ERROR: No results to aggregate"
        
        method = self.config.converge
        
        if method == ConvergenceMethod.CONSENSUS:
            return self._aggregate_consensus(self.results)
        elif method == ConvergenceMethod.BEST_OF:
            return self._aggregate_best_of(self.results)
        elif method == ConvergenceMethod.MERGE:
            return self._aggregate_merge(self.results)
        elif method == ConvergenceMethod.ALL:
            return self._aggregate_all(self.results)
        else:
            return f"ERROR: Unknown convergence method: {method}"
    
    def run(self) -> Dict[str, Any]:
        """
        Execute the full Work Crew workflow.
        
        Returns:
            Dictionary with individual results and aggregated output
        """
        # Step 1: Spawn the crew
        agent_ids = self.spawn_crew()
        
        if not agent_ids:
            return {
                "success": False,
                "error": "Failed to spawn any agents",
                "results": {},
                "aggregated": None
            }
        
        print(f"\nSpawned {len(agent_ids)} agents successfully", file=sys.stderr)
        
        # Step 2: Collect results
        self.collect_crew_results(agent_ids)
        
        # Step 3: Aggregate
        aggregated = self.aggregate()
        
        # Build return structure
        return {
            "success": True,
            "agent_count": len(agent_ids),
            "completed_count": len([r for r in self.results.values() if r.state == SessionState.COMPLETED]),
            "failed_count": len([r for r in self.results.values() if r.state == SessionState.FAILED]),
            "convergence_method": self.config.converge.value,
            "results": {k: v.to_dict() for k, v in self.results.items()},
            "aggregated_output": aggregated
        }


def parse_arguments() -> CrewConfig:
    """Parse command line arguments for Work Crew."""
    parser = argparse.ArgumentParser(
        description="Work Crew Pattern: Parallel agent execution with result aggregation",
        prog="claw agent-orchestrator crew"
    )
    
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="The task to assign to the crew"
    )
    
    parser.add_argument(
        "--agents", "-n",
        type=int,
        default=3,
        help="Number of agents to spawn (default: 3)"
    )
    
    parser.add_argument(
        "--perspectives", "-p",
        type=str,
        default="",
        help="Comma-separated list of perspectives (e.g., 'technical,business,security')"
    )
    
    parser.add_argument(
        "--converge", "-c",
        choices=["consensus", "best-of", "merge", "all"],
        default="consensus",
        help="Convergence method: consensus, best-of, merge, or all (default: consensus)"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout in seconds for each agent (default: 300)"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "--state-file",
        type=str,
        default=".crew_state.json",
        help="State file for session tracking"
    )
    
    args = parser.parse_args()
    
    # Parse perspectives
    perspectives = [p.strip() for p in args.perspectives.split(",") if p.strip()]
    
    return CrewConfig(
        task=args.task,
        agent_count=args.agents,
        perspectives=perspectives,
        converge=ConvergenceMethod(args.converge),
        timeout=args.timeout,
        output_format=args.format,
        state_file=args.state_file
    )


def main():
    """CLI entry point for Work Crew pattern."""
    config = parse_arguments()
    
    print(f"Work Crew Configuration:", file=sys.stderr)
    print(f"  Task: {config.task}", file=sys.stderr)
    print(f"  Agents: {config.agent_count}", file=sys.stderr)
    print(f"  Perspectives: {config.perspectives or 'None (redundancy)'}", file=sys.stderr)
    print(f"  Convergence: {config.converge.value}", file=sys.stderr)
    print(f"", file=sys.stderr)
    
    # Run the crew
    crew = WorkCrew(config)
    result = crew.run()
    
    # Output results
    if result["success"]:
        print(f"\n{'=' * 60}", file=sys.stderr)
        print(f"CREW EXECUTION SUMMARY", file=sys.stderr)
        print(f"{'=' * 60}", file=sys.stderr)
        print(f"Total Agents: {result['agent_count']}", file=sys.stderr)
        print(f"Completed: {result['completed_count']}", file=sys.stderr)
        print(f"Failed: {result['failed_count']}", file=sys.stderr)
        print(f"Convergence: {result['convergence_method']}", file=sys.stderr)
        print(f"{'=' * 60}\n", file=sys.stderr)
        
        # Output the aggregated result to stdout
        print(result["aggregated_output"])
        
        return 0
    else:
        print(f"ERROR: {result.get('error', 'Unknown error')}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
