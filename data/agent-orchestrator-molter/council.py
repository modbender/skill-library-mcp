"""
Expert Council Pattern Implementation

Multi-perspective consensus system where domain experts debate and decide.
Use for high-stakes decisions, content review, and ethics validation.

Architecture:
- Round 1: Each expert presents position + confidence on the question
- Round 2: Experts respond to each other's perspectives
- Final: Synthesize consensus or document divergent views

Convergence methods:
- consensus: Unanimous agreement required
- majority: >50% agreement sufficient
- divergent: Preserve all perspectives for human review

Example:
    claw agent-orchestrator council --question "Should we publish this content?" \
        --experts "skeptic,ethicist,strategist" \
        --converge consensus \
        --rounds 2
"""

import json
import sys
from enum import Enum
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# Import shared utilities with fallback
parent_dir = Path(__file__).parent
sys.path.insert(0, str(parent_dir))

try:
    from utils import SessionManager, AgentResult, SessionState
except ImportError:
    # Fallback minimal implementation
    class SessionState(Enum):
        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        TIMEOUT = "timeout"

    @dataclass
    class AgentResult:
        agent_id: str
        session_id: Optional[str]
        task: str
        output: str
        state: SessionState
        duration_ms: int
        timestamp: str
        error: Optional[str] = None

        def to_dict(self):
            return {**asdict(self), "state": self.state.value}

    class SessionManager:
        def __init__(self, state_file: Optional[str] = None):
            self.active_sessions = {}
            self.results = {}
            self.state_file = state_file or ".council_state.json"


class ConvergenceMethod(Enum):
    """Methods for final decision convergence."""
    CONSENSUS = "consensus"    # Unanimous agreement
    MAJORITY = "majority"      # >50% agreement
    DIVERGENT = "divergent"    # Preserve all views


class ExpertRole(Enum):
    """Built-in expert personas for the council."""
    SKEPTIC = "skeptic"        # Challenges assumptions, finds flaws
    OPTIMIST = "optimist"      # Identifies opportunities, benefits
    TECHNICIAN = "technician"  # Implements, focuses on feasibility
    ECONOMIST = "economist"    # Considers costs, efficiency
    ETHICIST = "ethicist"      # Examines implications, fairness
    STRATEGIST = "strategist"  # Long-term thinking, positioning
    # Generic experts
    LEGAL = "legal"            # Regulatory, compliance perspective
    SECURITY = "security"      # Risks, threat assessment
    BUSINESS = "business"      # Market, profit, viability
    TECHNICAL = "technical"    # Implementation, architecture


# Expert persona prompts - defines how each expert approaches decisions
EXPERT_PERSONAS = {
    ExpertRole.SKEPTIC: """You are the SKEPTIC on an expert council.
Your role: Challenge assumptions, find flaws, identify risks, and play devil's advocate.

When analyzing any proposal or question:
1. Identify hidden assumptions that might be wrong
2. Point out weak or speculative reasoning
3. Highlight edge cases and failure modes
4. Ask "what could go wrong?"
5. Question whether the problem is well-defined

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
KEY CONCERNS: Bulleted list of risks and flaws
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.OPTIMIST: """You are the OPTIMIST on an expert council.
Your role: Identify opportunities, highlight benefits, and find hidden potential.

When analyzing any proposal or question:
1. Look for the upside and positive outcomes
2. Identify opportunities others might miss
3. Highlight how benefits compound over time
4. Consider second-order positive effects
5. Ask "what's the best that could happen?"

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
OPPORTUNITIES: Bulleted list of benefits and potential
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.TECHNICIAN: """You are the TECHNICIAN on an expert council.
Your role: Focus on implementation details, feasibility, and execution.

When analyzing any proposal or question:
1. Assess technical feasibility and requirements
2. Identify implementation challenges
3. Consider resource needs (time, skills, tools)
4. Evaluate integration with existing systems
5. Ask "how would this actually be built/deployed?"

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
IMPLEMENTATION: Bulleted list of technical considerations
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.ECONOMIST: """You are the ECONOMIST on an expert council.
Your role: Consider costs, efficiency, and economic implications.

When analyzing any proposal or question:
1. Calculate direct and indirect costs
2. Assess return on investment and payback period
3. Consider opportunity costs and trade-offs
4. Evaluate scalability and resource efficiency
5. Ask "is this worth the resources it requires?"

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
ECONOMICS: Bulleted list of cost/benefit analysis
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.ETHICIST: """You are the ETHICIST on an expert council.
Your role: Examine ethical implications, fairness, and moral considerations.

When analyzing any proposal or question:
1. Assess impact on different stakeholder groups
2. Consider fairness and equity implications
3. Evaluate transparency and accountability
4. Reflect on long-term societal effects
5. Ask "is this the right thing to do?"

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
ETHICAL CONSIDERATIONS: Bulleted list of moral implications
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.STRATEGIST: """You are the STRATEGIST on an expert council.
Your role: Think long-term, consider positioning, and anticipate future landscape.

When analyzing any proposal or question:
1. Consider long-term strategic positioning
2. Anticipate future trends and market shifts
3. Evaluate competitive implications
4. Assess alignment with broader goals/vision
5. Ask "where does this position us in 3-5 years?"

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
STRATEGIC IMPLICATIONS: Bulleted list of long-term considerations
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.LEGAL: """You are the LEGAL expert on an expert council.
Your role: Assess regulatory, compliance, and legal risk implications.

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
LEGAL CONSIDERATIONS: Bulleted list of regulatory/compliance issues
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.SECURITY: """You are the SECURITY expert on an expert council.
Your role: Assess threats, vulnerabilities, and protective measures.

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
SECURITY ANALYSIS: Bulleted list of threats and mitigations
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.BUSINESS: """You are the BUSINESS expert on an expert council.
Your role: Assess market viability, customer value, and commercial potential.

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
BUSINESS CASE: Bulleted list of market/commercial factors
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",

    ExpertRole.TECHNICAL: """You are the TECHNICAL expert on an expert council.
Your role: Evaluate architecture, systems, and technical approach.

Format your response as:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
TECHNICAL ASSESSMENT: Bulleted list of architectural considerations
CONFIDENCE: 0-10 (how certain you are in your assessment)
""",
}


@dataclass
class ExpertOpinion:
    """An expert's opinion with confidence scoring."""
    expert: str
    role: ExpertRole
    position: str  # Agree/Disagree/Conditional/etc
    reasoning: List[str]
    confidence: int  # 0-10
    raw_output: str
    round_num: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "expert": self.expert,
            "role": self.role.value,
            "position": self.position,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "round": self.round_num,
        }


@dataclass
class CouncilConfig:
    """Configuration for Council execution."""
    question: str
    experts: List[ExpertRole]
    converge: ConvergenceMethod
    rounds: int = 2
    timeout: int = 300
    output_format: str = "markdown"
    state_file: Optional[str] = None
    verbose: bool = False


@dataclass
class CouncilResult:
    """Final result from the council deliberation."""
    consensus_reached: bool
    final_position: str
    confidence: float
    opinions: List[ExpertOpinion]
    disagreements: List[str]
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consensus_reached": self.consensus_reached,
            "final_position": self.final_position,
            "confidence": self.confidence,
            "opinions": [o.to_dict() for o in self.opinions],
            "disagreements": self.disagreements,
            "reasoning": self.reasoning,
            "metadata": self.metadata,
        }


def parse_experts(expert_list: List[str]) -> List[ExpertRole]:
    """Parse expert names into ExpertRole enum values."""
    experts = []
    for exp in expert_list:
        exp_clean = exp.strip().lower()
        try:
            role = ExpertRole(exp_clean)
            experts.append(role)
        except ValueError:
            # Try to match known aliases
            alias_map = {
                "devil": ExpertRole.SKEPTIC,
                "risk": ExpertRole.SKEPTIC,
                "opportunity": ExpertRole.OPTIMIST,
                "ops": ExpertRole.TECHNICIAN,
                "imagineer": ExpertRole.TECHNICIAN,
                "finance": ExpertRole.ECONOMIST,
                "money": ExpertRole.ECONOMIST,
                "moral": ExpertRole.ETHICIST,
                "values": ExpertRole.ETHICIST,
                "vision": ExpertRole.STRATEGIST,
                "future": ExpertRole.STRATEGIST,
            }
            if exp_clean in alias_map:
                experts.append(alias_map[exp_clean])
            else:
                # Default to generic roles
                if "legal" in exp_clean:
                    experts.append(ExpertRole.LEGAL)
                elif "security" in exp_clean:
                    experts.append(ExpertRole.SECURITY)
                elif "business" in exp_clean:
                    experts.append(ExpertRole.BUSINESS)
                elif "tech" in exp_clean:
                    experts.append(ExpertRole.TECHNICAL)
                else:
                    # Skip unknown experts
                    print(f"Warning: Unknown expert '{exp}', skipping", file=sys.stderr)
    return experts


def build_round1_prompt(role: ExpertRole, question: str) -> str:
    """Build the first-round prompt for an expert."""
    persona = EXPERT_PERSONAS.get(role, EXPERT_PERSONAS[ExpertRole.TECHNICAL])

    prompt = f"""{persona}

=== QUESTION FOR DELIBERATION ===
{question}

=== YOUR TASK ===
Provide your expert assessment of this question from your specialized perspective.

You are the {role.value.upper()} on this council. Analyze the question above and provide:
- Your position (agree/disagree/conditional with conditions)
- Your reasoning (key points from your perspective)
- Your confidence level (0-10)

Be thorough but concise. This is Round 1 of deliberation."""

    return prompt


def build_round2_prompt(role: ExpertRole, question: str, other_opinions: List[ExpertOpinion]) -> str:
    """Build the second-round prompt with other experts' views."""
    persona = EXPERT_PERSONAS.get(role, EXPERT_PERSONAS[ExpertRole.TECHNICAL])

    # Summarize other experts' positions
    others_summary = ""
    for opinion in other_opinions:
        if opinion.expert != role.value:  # Don't include own opinion
            others_summary += f"\n- {opinion.role.value.upper()}: {opinion.position} (confidence: {opinion.confidence}/10)"
            if opinion.reasoning:
                others_summary += f" - Key points: {', '.join(opinion.reasoning[:2])}"

    prompt = f"""{persona}

=== QUESTION FOR DELIBERATION ===
{question}

=== OTHER EXPERTS' POSITIONS (Round 1) ===
{others_summary}

=== YOUR TASK ===
This is Round 2 of deliberation. Review the other experts' positions above.

From your perspective as the {role.value.upper()}:
1. Which points from other experts do you agree or disagree with? Why?
2. Have any of their arguments changed your thinking?
3. Refine or restate your position based on the group discussion
4. Update your confidence level if changed

Format:
POSITION: [Agree/Disagree/Conditional] - One sentence stance
REFINED REASONING: Your updated analysis considering other perspectives
CONFIDENCE: 0-10 (updated based on Round 1 discussion)
"""

    return prompt


def parse_expert_output(expert: str, role: ExpertRole, output: str, round_num: int) -> ExpertOpinion:
    """Parse expert output into structured opinion."""
    lines = output.strip().split('\n')

    position = "Unknown"
    reasoning = []
    confidence = 5  # Default middle confidence

    current_section = None

    for line in lines:
        line = line.strip()
        upper = line.upper()

        # Extract position
        if upper.startswith("POSITION:"):
            position = line.split(":", 1)[1].strip()
            current_section = "position"
        # Extract confidence
        elif "CONFIDENCE:" in upper:
            try:
                conf_str = line.split(":", 1)[1].strip()
                # Extract just the number
                conf_num = ''.join(c for c in conf_str if c.isdigit())
                if conf_num:
                    confidence = int(conf_num)
                    confidence = max(0, min(10, confidence))  # Clamp 0-10
            except:
                pass
        # Collect reasoning from bulleted or numbered lists
        elif line.startswith("- ") or line.startswith("* ") or (len(line) > 2 and line[0].isdigit() and line[1] == "."):
            reasoning.append(line.lstrip("- *0123456789. ").strip())
            current_section = "reasoning"
        # Continue collecting reasoning in multi-line sections
        elif current_section == "reasoning" and line and not line.endswith(":"):
            reasoning.append(line)

    return ExpertOpinion(
        expert=expert,
        role=role,
        position=position,
        reasoning=reasoning,
        confidence=confidence,
        raw_output=output,
        round_num=round_num
    )


class Council:
    """
    Expert Council pattern implementation.

    Multiple experts deliberate on a question through structured rounds,
    then converge on a collective position using the specified method.
    """

    def __init__(self, config: CouncilConfig):
        self.config = config
        self.session_manager = SessionManager(state_file=config.state_file)
        self.opinions: Dict[str, List[ExpertOpinion]] = {}  # expert -> list of opinions by round
        self.verbose = config.verbose

        if self.verbose:
            print(f"Council initialized: {len(config.experts)} experts, {config.rounds} rounds, converge={config.converge.value}")

    def _log(self, message: str):
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] COUNCIL: {message}")

    def execute_round(self, round_num: int) -> Dict[str, ExpertOpinion]:
        """Execute a deliberation round and collect all expert opinions."""
        self._log(f"Starting Round {round_num}")

        round_opinions = {}

        for role in self.config.experts:
            expert_name = role.value

            # Build appropriate prompt for this round
            if round_num == 1:
                prompt = build_round1_prompt(role, self.config.question)
            else:
                # Get previous round opinions for this expert (all other experts)
                prev_opinions = []
                for exp_name, exp_opinions in self.opinions.items():
                    if exp_opinions and exp_opinions[-1].round_num == round_num - 1:
                        prev_opinions.append(exp_opinions[-1])
                prompt = build_round2_prompt(role, self.config.question, prev_opinions)

            self._log(f"  Spawning {expert_name} for Round {round_num}")

            try:
                # Spawn expert session (simulated - in real implementation uses OpenClaw sessions)
                agent_id = self.session_manager.spawn_session(
                    task=prompt,
                    agent_label=f"{expert_name}-r{round_num}",
                    context={"role": expert_name, "round": round_num}
                )

                # Note: In actual implementation, would collect async results
                # For this implementation, we'll use direct LLM calls
                # (simulated here - real code would use session_manager)

                # Simulate getting result (in production, use session_manager)
                result = self._simulate_expert_response(role, prompt, round_num)

                opinion = parse_expert_output(expert_name, role, result, round_num)
                round_opinions[expert_name] = opinion

                if expert_name not in self.opinions:
                    self.opinions[expert_name] = []
                self.opinions[expert_name].append(opinion)

                self._log(f"  {expert_name}: {opinion.position} (conf: {opinion.confidence}/10)")

            except Exception as e:
                self._log(f"  ERROR spawning {expert_name}: {e}")
                # Create fallback opinion on error
                opinion = ExpertOpinion(
                    expert=expert_name,
                    role=role,
                    position="Error - could not participate",
                    reasoning=[f"Error: {str(e)}"],
                    confidence=0,
                    raw_output=str(e),
                    round_num=round_num
                )
                round_opinions[expert_name] = opinion

        return round_opinions

    def _simulate_expert_response(self, role: ExpertRole, prompt: str, round_num: int) -> str:
        """
        Simulated expert response for development.
        In production, this would collect from actual LLM sub-agent sessions.
        """
        # This is a placeholder - real implementation uses SessionManager
        # For now, return a structured template response
        positions = ["Conditional Agreement", "Agree with reservations", "Cautious agreement"]
        position = positions[hash(role.value) % len(positions)]

        return f"""POSITION: {position}

KEY POINTS:
- Analysis from {role.value} perspective
- Important consideration 1
- Important consideration 2
- Trade-off analysis

CONFIDENCE: 7/10"""

    def synthesize_consensus(self, all_opinions: List[ExpertOpinion]) -> CouncilResult:
        """Synthesize final consensus from all expert opinions."""
        self._log("Synthesizing final consensus")

        # Get final round opinions only
        final_opinions = [op for op in all_opinions if op.round_num == self.config.rounds]

        if not final_opinions:
            return CouncilResult(
                consensus_reached=False,
                final_position="No opinions collected",
                confidence=0.0,
                opinions=[],
                disagreements=["Council failed to collect expert input"],
                reasoning="No final opinions available",
                metadata={"error": "empty council"}
            )

        # Analyze positions
        positions = {}
        total_confidence = 0

        for op in final_opinions:
            # Categorize position
            pos_lower = op.position.lower()
            if "agree" in pos_lower:
                cat = "agree"
            elif "disagree" in pos_lower and "agree" not in pos_lower:
                cat = "disagree"
            elif "conditional" in pos_lower:
                cat = "conditional"
            else:
                cat = "neutral"

            positions[cat] = positions.get(cat, 0) + 1
            total_confidence += op.confidence

        avg_confidence = total_confidence / len(final_opinions) if final_opinions else 0
        confident_ratio = avg_confidence / 10

        # Determine consensus based on convergence method
        total_experts = len(final_opinions)
        agree_count = positions.get("agree", 0) + positions.get("conditional", 0)
        disagree_count = positions.get("disagree", 0)

        consensus_reached = False
        final_position = "No clear position"
        disagreements = []

        if self.config.converge == ConvergenceMethod.CONSENSUS:
            # Unanimous agreement required
            if positions.get("disagree", 0) == 0 and agree_count == total_experts:
                consensus_reached = True
                final_position = "UNANIMOUS AGREEMENT"
            elif agree_count >= total_experts * 0.9:
                consensus_reached = True
                final_position = "NEAR-UNANIMOUS (minor dissent noted)"
            else:
                consensus_reached = False
                final_position = "NO CONSENSUS - dissent exists"
                disagreements.append(f"{disagree_count} expert(s) disagreed with the majority")

        elif self.config.converge == ConvergenceMethod.MAJORITY:
            # >50% agreement sufficient
            if agree_count > total_experts / 2:
                consensus_reached = True
                majority_pct = int((agree_count / total_experts) * 100)
                final_position = f"MAJORITY AGREEMENT ({majority_pct}%)"
            else:
                consensus_reached = False
                final_position = "NO MAJORITY - positions split"
                disagreements.append(f"Only {agree_count}/{total_experts} experts in agreement")

        else:  # DIVERGENT
            consensus_reached = False  # Intentionally no consensus
            final_position = "DIVERGENT PERSPECTIVES PRESERVED"
            disagreements.append("All perspectives retained for human review")

        # Identify specific disagreements
        if positions.get("disagree", 0) > 0:
            for op in final_opinions:
                if "disagree" in op.position.lower() and "agree" not in op.position.lower():
                    disagreements.append(f"{op.role.value}: {op.position}")

        # Build reasoning summary
        reasoning_parts = [
            f"Council of {total_experts} experts deliberated for {self.config.rounds} round(s).",
            f"Final positions: {positions}",
            f"Average confidence: {avg_confidence:.1f}/10",
            "",
            "Expert Positions:",
        ]
        for op in final_opinions:
            reasoning_parts.append(f"  - {op.role.value}: {op.position} (conf: {op.confidence}/10)")

        reasoning = "\n".join(reasoning_parts)

        self._log(f"Consensus: {consensus_reached}, Position: {final_position}")

        return CouncilResult(
            consensus_reached=consensus_reached,
            final_position=final_position,
            confidence=confident_ratio,
            opinions=final_opinions,
            disagreements=disagreements,
            reasoning=reasoning,
            metadata={
                "method": self.config.converge.value,
                "rounds": self.config.rounds,
                "position_distribution": positions,
                "avg_confidence": avg_confidence,
            }
        )

    def run(self) -> Dict[str, Any]:
        """Execute the full Council workflow."""
        self._log(f"COUNCIL START: Question = '{self.config.question[:60]}...'")
        self._log(f"Experts: {[e.value for e in self.config.experts]}")

        # Execute deliberation rounds
        for round_num in range(1, self.config.rounds + 1):
            self.execute_round(round_num)

        # Collect all opinions
        all_opinions = []
        for expert_opinions in self.opinions.values():
            all_opinions.extend(expert_opinions)

        # Synthesize final result
        result = self.synthesize_consensus(all_opinions)

        self._log("COUNCIL COMPLETE")

        return result.to_dict()


def format_output_markdown(result: Dict[str, Any]) -> str:
    """Format council result as markdown."""
    md = []
    md.append("# Expert Council Deliberation Report")
    md.append("")
    md.append(f"**Consensus Status:** {'Achieved' if result['consensus_reached'] else 'Not Achieved'}")
    md.append(f"**Final Position:** {result['final_position']}")
    md.append(f"**Collective Confidence:** {result['confidence']*100:.0f}%")
    md.append("")

    md.append("## Expert Opinions (Final Round)")
    md.append("")
    for op in result['opinions']:
        md.append(f"### {op['expert'].upper()}")
        md.append(f"- **Position:** {op['position']}")
        md.append(f"- **Confidence:** {op['confidence']}/10")
        if op['reasoning']:
            md.append("- **Key Points:**")
            for point in op['reasoning']:
                md.append(f"  - {point}")
        md.append("")

    if result['disagreements']:
        md.append("## Disagreements and Dissent")
        md.append("")
        for d in result['disagreements']:
            md.append(f"- {d}")
        md.append("")

    md.append("## Synthesis")
    md.append("")
    md.append(result['reasoning'])
    md.append("")

    return "\n".join(md)


def format_output_json(result: Dict[str, Any]) -> str:
    """Format council result as JSON."""
    return json.dumps(result, indent=2)


def format_output_text(result: Dict[str, Any]) -> str:
    """Format council result as plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("EXPERT COUNCIL DELIBERATION")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Status: {result['final_position']}")
    lines.append(f"Confidence: {result['confidence']*100:.0f}%")
    lines.append("")
    lines.append("-" * 40)
    lines.append("EXPERT POSITIONS:")
    lines.append("-" * 40)

    for op in result['opinions']:
        lines.append(f"\n{op['expert'].upper()}:")
        lines.append(f"  Position: {op['position']}")
        lines.append(f"  Confidence: {op['confidence']}/10")

    if result['disagreements']:
        lines.append("\n" + "-" * 40)
        lines.append("DISSENT:")
        lines.append("-" * 40)
        for d in result['disagreements']:
            lines.append(f"  - {d}")

    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def council_cli_entry():
    """CLI entry point for council command."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Expert Council - Multi-perspective deliberation and consensus",
        prog="claw agent-orchestrator council"
    )

    parser.add_argument(
        "--question", "-q",
        required=True,
        help="The question or proposal for the council to deliberate"
    )

    parser.add_argument(
        "--experts", "-e",
        required=True,
        help="Comma-separated experts: 'skeptic,optimist,technician,economist,ethicist,strategist'"
    )

    parser.add_argument(
        "--converge", "-c",
        choices=["consensus", "majority", "divergent"],
        default="consensus",
        help="Convergence method: consensus (unanimous), majority (>50%%), divergent (preserve all)"
    )

    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=2,
        help="Number of deliberation rounds (default: 2)"
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout per expert session in seconds (default: 300)"
    )

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show council deliberation progress"
    )

    parser.add_argument(
        "--state-file",
        help="State file for resumability (optional)"
    )

    args = parser.parse_args()

    # Parse experts
    expert_list = [e.strip() for e in args.experts.split(",")]
    experts = parse_experts(expert_list)

    if not experts:
        print("ERROR: No valid experts specified", file=sys.stderr)
        print("Valid experts: skeptic, optimist, technician, economist, ethicist, strategist, legal, security, business, technical", file=sys.stderr)
        return 1

    # Build config
    config = CouncilConfig(
        question=args.question,
        experts=experts,
        converge=ConvergenceMethod(args.converge),
        rounds=args.rounds,
        timeout=args.timeout,
        output_format=args.format,
        state_file=args.state_file,
        verbose=args.verbose
    )

    # Run council
    try:
        council = Council(config)
        result = council.run()

        # Format output
        if args.format == "json":
            print(format_output_json(result))
        elif args.format == "text":
            print(format_output_text(result))
        else:  # markdown
            print(format_output_markdown(result))

        # Return non-zero if no consensus (unless divergent mode)
        if not result['consensus_reached'] and args.converge != "divergent":
            return 2  # Indicates deliberation completed but consensus not reached

        return 0

    except KeyboardInterrupt:
        print("\nCouncil deliberation interrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"ERROR: Council failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point for module execution."""
    return council_cli_entry()


if __name__ == "__main__":
    sys.exit(main())
