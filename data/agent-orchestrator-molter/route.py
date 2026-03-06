"""
Auto-Routing Pattern Implementation

A classifier agent analyzes incoming tasks and routes them to appropriate
specialist agents based on task type classification. Supports confidence-based
routing with fallback to clarification requests.

Use this for:
- Mixed workload types that need automatic classification
- Smart agent selection without manual task analysis
- Triaging task requests to appropriate specialists
- Building autonomous task distribution systems
- Reducing human overhead in task assignment

Example:
    router = TaskRouter()
    result = router.route("Write a Python function to parse JSON")
    # Returns: coder specialist with high confidence
"""

import argparse
import json
import sys
import re
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

from utils import SessionManager, AgentResult, SessionState


class SpecialistRole(Enum):
    """Built-in specialist roles for task routing."""
    CODER = "coder"           # Software development, coding tasks
    RESEARCHER = "researcher" # Information gathering, investigation
    WRITER = "writer"         # Content creation, documentation
    ANALYST = "analyst"       # Data analysis, insights, evaluation
    PLANNER = "planner"       # Planning, strategy, organization
    REVIEWER = "reviewer"     # Quality review, critique, evaluation
    CREATIVE = "creative"     # Design, creative content, ideation
    SUPPORT = "support"       # Help desk, troubleshooting, assistance
    DATA = "data"             # Data processing, ETL, database work
    DEVOPS = "devops"         # Infrastructure, deployment, automation
    UNKNOWN = "unknown"       # Unclassifiable, needs clarification


class TaskType(Enum):
    """Task type classifications for routing decisions."""
    CODE_IMPLEMENTATION = "code_implementation"
    CODE_REVIEW = "code_review"
    BUG_FIX = "bug_fix"
    RESEARCH_TOPIC = "research_topic"
    INVESTIGATE_ISSUE = "investigate_issue"
    WRITE_ARTICLE = "write_article"
    WRITE_DOCUMENTATION = "write_documentation"
    WRITE_COPY = "write_copy"
    ANALYZE_DATA = "analyze_data"
    EVALUATE_OPTIONS = "evaluate_options"
    CREATE_PLAN = "create_plan"
    REVIEW_CONTENT = "review_content"
    EDIT_IMPROVE = "edit_improve"
    CREATIVE_DESIGN = "creative_design"
    BRAINSTORM_IDEAS = "brainstorm_ideas"
    TROUBLESHOOT = "troubleshoot"
    HOW_TO = "how_to"
    DATA_PROCESSING = "data_processing"
    DEPLOYMENT = "deployment"
    INFRASTRUCTURE = "infrastructure"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class SpecialistConfig:
    """Configuration for a specialist agent."""
    role: SpecialistRole
    name: str
    system_prompt: str
    capabilities: List[str]
    keywords: List[str]
    confidence_threshold: float = 0.7
    priority: int = 5  # 1-10, higher = preferred when uncertain


@dataclass
class RouteResult:
    """Result from task classification and routing."""
    task_type: TaskType
    confidence: float
    assigned_specialist: SpecialistRole
    reasoning: str
    alternatives: List[SpecialistRole] = field(default_factory=list)
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_type": self.task_type.value,
            "confidence": self.confidence,
            "assigned_specialist": self.assigned_specialist.value,
            "reasoning": self.reasoning,
            "alternatives": [s.value for s in self.alternatives],
            "needs_clarification": self.needs_clarification,
            "clarification_prompt": self.clarification_prompt,
            "metadata": self.metadata
        }


# Default specialist configurations
DEFAULT_SPECIALISTS = {
    SpecialistRole.CODER: SpecialistConfig(
        role=SpecialistRole.CODER,
        name="Code Specialist",
        system_prompt="""You are a software development specialist.
Your job is to write, review, debug, and refactor code.
You excel at:
- Writing clean, maintainable code
- Debugging complex issues
- Code review and optimization
- Test writing and coverage
- API and library implementation

Follow best practices, include comments, and handle edge cases.""",
        capabilities=["code_writing", "debugging", "refactoring", "testing", "api_design"],
        keywords=["code", "function", "program", "script", "bug", "error", "python", "javascript",
                  "implement", "refactor", "debug", "compile", "class", "module"],
        confidence_threshold=0.7,
        priority=8
    ),
    
    SpecialistRole.RESEARCHER: SpecialistConfig(
        role=SpecialistRole.RESEARCHER,
        name="Research Specialist",
        system_prompt="""You are a research and information gathering specialist.
Your job is to explore topics thoroughly and synthesize findings.
You excel at:
- Gathering comprehensive information
- Fact-checking and verification
- Summarizing complex topics
- Finding sources and references
- Cross-domain knowledge synthesis

Be thorough, cite sources where possible, and organize findings clearly.""",
        capabilities=["research", "investigation", "synthesis", "verification", "summarization"],
        keywords=["research", "find", "investigate", "learn about", "history of", "trends",
                  "study", "analyze topic", "what is", "how does", "compare", "contrast"],
        confidence_threshold=0.7,
        priority=7
    ),
    
    SpecialistRole.WRITER: SpecialistConfig(
        role=SpecialistRole.WRITER,
        name="Writing Specialist",
        system_prompt="""You are a content creation and writing specialist.
Your job is to produce high-quality written content.
You excel at:
- Clear and engaging prose
- Technical documentation
- Marketing copy and content
- Scripts and narratives
- Editing and improving text

Adapt tone to audience, ensure logical flow, and maintain consistency.""",
        capabilities=["content_writing", "editing", "documentation", "copywriting", "narrative"],
        keywords=["write", "draft", "document", "article", "blog", "content", "script",
                  "create text", "copy", "story", "narrative", "essay", "report"],
        confidence_threshold=0.7,
        priority=7
    ),
    
    SpecialistRole.ANALYST: SpecialistConfig(
        role=SpecialistRole.ANALYST,
        name="Analysis Specialist",
        system_prompt="""You are a data analysis and evaluation specialist.
Your job is to extract insights and evaluate options.
You excel at:
- Quantitative data analysis
- Pattern recognition
- Comparative evaluation
- Risk/benefit assessment
- Decision support analysis

Provide data-backed conclusions and structured recommendations.""",
        capabilities=["data_analysis", "evaluation", "comparison", "risk_assessment", "reporting"],
        keywords=["analyze", "evaluate", "assess", "compare", "metrics", "data", "statistics",
                  "performance", "review", "audit", "examine", "study", "measure"],
        confidence_threshold=0.7,
        priority=6
    ),
    
    SpecialistRole.PLANNER: SpecialistConfig(
        role=SpecialistRole.PLANNER,
        name="Planning Specialist",
        system_prompt="""You are a strategic planning specialist.
Your job is to create structured plans and strategies.
You excel at:
- Project planning and roadmaps
- Resource allocation
- Timeline and milestone creation
- Workflow design
- Risk planning and mitigation

Create actionable, realistic plans with clear dependencies.""",
        capabilities=["planning", "roadmapping", "workflow_design", "resource_allocation"],
        keywords=["plan", "strategy", "roadmap", "schedule", "timeline", "workflow",
                  "organize", "coordinate", "prepare", "design process"],
        confidence_threshold=0.7,
        priority=6
    ),
    
    SpecialistRole.REVIEWER: SpecialistConfig(
        role=SpecialistRole.REVIEWER,
        name="Review Specialist",
        system_prompt="""You are a critical review and quality assurance specialist.
Your job is to evaluate work and provide constructive feedback.
You excel at:
- Code reviews
- Content quality evaluation
- Process audits
- Finding issues and bugs
- Suggesting improvements

Be thorough, fair, and provide actionable feedback.""",
        capabilities=["review", "quality_check", "audit", "feedback", "verification"],
        keywords=["review", "check", "audit", "verify", "validate", "inspect", "quality",
                  "critique", "feedback", "confirm", "ensure"],
        confidence_threshold=0.7,
        priority=5
    ),
    
    SpecialistRole.CREATIVE: SpecialistConfig(
        role=SpecialistRole.CREATIVE,
        name="Creative Specialist",
        system_prompt="""You are a creative design and ideation specialist.
Your job is to produce creative concepts and designs.
You excel at:
- Ideation and brainstorming
- Creative concepts
- Design thinking
- Names and branding ideas
- Visual descriptions and mockups

Think outside the box while staying practical.""",
        capabilities=["ideation", "design", "branding", "creative_concepts", "naming"],
        keywords=["design", "creative", "brainstorm", "ideate", "concept", "branding",
                  "innovative", "name", "slogan", "visual", "style", "aesthetic"],
        confidence_threshold=0.7,
        priority=5
    ),
    
    SpecialistRole.DATA: SpecialistConfig(
        role=SpecialistRole.DATA,
        name="Data Processing Specialist",
        system_prompt="""You are a data processing and ETL specialist.
Your job is to transform and process data efficiently.
You excel at:
- Data transformation and cleaning
- ETL pipeline creation
- Database queries
- CSV/JSON/XML processing
- Data validation

Handle data carefully and maintain integrity throughout processing.""",
        capabilities=["etl", "data_cleaning", "database", "transformation", "validation"],
        keywords=["csv", "json", "database", "sql", "etl", "transform", "extract", "load",
                  "clean data", "parse", "convert format", "data pipeline"],
        confidence_threshold=0.7,
        priority=6
    ),
    
    SpecialistRole.DEVOPS: SpecialistConfig(
        role=SpecialistRole.DEVOPS,
        name="DevOps Specialist",
        system_prompt="""You are a DevOps and infrastructure specialist.
Your job is to handle deployment and infrastructure tasks.
You excel at:
- CI/CD pipeline configuration
- Infrastructure as code
- Container orchestration
- Cloud deployment
- Automation scripting

Follow infrastructure best practices and prioritize reliability.""",
        capabilities=["ci_cd", "docker", "kubernetes", "cloud", "automation", "deployment"],
        keywords=["deploy", "docker", "kubernetes", "ci/cd", "pipeline", "infrastructure",
                  "cloud", "aws", "azure", "gcp", "server", "config", "yaml", "automation"],
        confidence_threshold=0.7,
        priority=5
    ),
    
    SpecialistRole.SUPPORT: SpecialistConfig(
        role=SpecialistRole.SUPPORT,
        name="Support Specialist",
        system_prompt="""You are a support and assistance specialist.
Your job is to help users solve problems and answer questions.
You excel at:
- Troubleshooting issues
- Explaining concepts
- Step-by-step guidance
- Answering how-to questions
- User support and help

Be patient, clear, and helpful in your responses.""",
        capabilities=["troubleshooting", "help", "guidance", "explanation", "support"],
        keywords=["help", "how to", "troubleshoot", "fix", "problem", "issue", "error",
                  "support", "question", "what does", "explain", "guide", "tutorial"],
        confidence_threshold=0.7,
        priority=4
    ),
}


class TaskClassifier:
    """
    Single-shot task classifier for routing decisions.
    
    Analyzes task descriptions and classifies them by type with confidence scoring.
    Uses keyword matching as initial filter and LLM for final classification.
    """
    
    def __init__(self, confidence_threshold: float = 0.7):
        self.confidence_threshold = confidence_threshold
    
    def classify(self, task: str, available_specialists: List[SpecialistRole]) -> RouteResult:
        """
        Classify a task and determine appropriate routing.
        
        Args:
            task: The task description to classify
            available_specialists: List of specialists to choose from
            
        Returns:
            RouteResult with classification and routing decision
        """
        # First: keyword-based scoring for quick classification
        keyword_scores = self._score_by_keywords(task, available_specialists)
        
        # Second: build classification prompt for LLM refinement
        classification = self._llm_classify(task, available_specialists, keyword_scores)
        
        # Third: determine if clarification needed
        if classification.confidence < self.confidence_threshold:
            classification.needs_clarification = True
            classification.clarification_prompt = self._generate_clarification_prompt(
                task, classification
            )
            # Keep the best guess specialist but flag as uncertain
        
        return classification
    
    def _score_by_keywords(
        self,
        task: str,
        specialists: List[SpecialistRole]
    ) -> Dict[SpecialistRole, float]:
        """Score task against each specialist using keyword matching."""
        task_lower = task.lower()
        scores: Dict[SpecialistRole, float] = {}
        
        for role in specialists:
            config = DEFAULT_SPECIALISTS.get(role)
            if not config:
                continue
            
            score = 0.0
            matched_keywords = []
            
            # Check for keyword matches
            for keyword in config.keywords:
                if keyword.lower() in task_lower:
                    # Each match adds base points
                    score += 0.35
                    matched_keywords.append(keyword)
            
            # Cap at 1.0 for keyword scoring
            score = min(score, 1.0)
            
            # Boost for multiple matched keywords
            if len(matched_keywords) >= 2:
                score = min(score * 1.15, 1.0)
            if len(matched_keywords) >= 3:
                score = min(score * 1.1, 1.0)  # Additional boost
            
            scores[role] = score
        
        return scores
    
    def _llm_classify(
        self,
        task: str,
        specialists: List[SpecialistRole],
        keyword_scores: Dict[SpecialistRole, float]
    ) -> RouteResult:
        """
        Use LLM to classify task and select specialist.
        
        Returns structured classification with confidence and reasoning.
        """
        # Build specialist descriptions for prompt
        specialist_descriptions = []
        for role in specialists:
            config = DEFAULT_SPECIALISTS.get(role)
            if config:
                keyword_hint = keyword_scores.get(role, 0)
                specialist_descriptions.append(
                    f"- {role.value}: {', '.join(config.capabilities[:3])} "
                    f"(keyword score: {keyword_hint:.2f})"
                )
        
        prompt = f"""You are a task classification system. Your job is to analyze tasks and route them to the most appropriate specialist.

TASK TO CLASSIFY:
{task}

AVAILABLE SPECIALISTS:
{chr(10).join(specialist_descriptions)}

Analyze this task and respond in this exact format:

TASK_TYPE: [specific type like code_implementation, research_topic, write_article, etc.]
ASSIGNED_SPECIALIST: [select from available specialists above]
CONFIDENCE: [0.0-1.0 score - higher means more certain]
REASONING: [2-3 sentences explaining your classification decision]
ALTERNATIVES: [comma-separated list of other potentially suitable specialists, or "none"]
IS_MIXED: [yes/no - is this task a mix of multiple types?]

Rules:
1. Choose only from the available specialists listed
2. Confidence should reflect how clearly the task fits one specialist
3. Low confidence (<0.7) suggests the task might be mixed or unclear
4. If mixed, select the primary specialist and note alternatives
5. Be conservative - better to flag for clarification than guess wrong

CLASSIFICATION:"""

        # Simulate LLM response (in production, would call actual LLM)
        # Here we use a heuristic-based response derived from keyword scores
        return self._heuristic_classify(task, specialists, keyword_scores, prompt)
    
    def _heuristic_classify(
        self,
        task: str,
        specialists: List[SpecialistRole],
        keyword_scores: Dict[SpecialistRole, float],
        prompt: str
    ) -> RouteResult:
        """
        Heuristic-based classification for MVP.
        In production, this would be replaced with actual LLM call.
        """
        # Find best matching specialist
        if not keyword_scores:
            return RouteResult(
                task_type=TaskType.UNKNOWN,
                confidence=0.0,
                assigned_specialist=SpecialistRole.UNKNOWN,
                reasoning="No keyword matches found. Cannot determine appropriate specialist.",
                alternatives=[],
                needs_clarification=True,
                clarification_prompt="Please describe your task more specifically. What type of work do you need done? (e.g., write code, research a topic, create content, analyze data)"
            )
        
        # Sort specialists by score
        sorted_specialists = sorted(
            specialists,
            key=lambda r: keyword_scores.get(r, 0),
            reverse=True
        )
        
        best_role = sorted_specialists[0]
        best_score = keyword_scores.get(best_role, 0)
        
        # Determine task type based on specialist
        task_type = self._infer_task_type(task, best_role)
        
        # Calculate confidence based on score spread
        if len(sorted_specialists) > 1:
            second_best_score = keyword_scores.get(sorted_specialists[1], 0)
            margin = best_score - second_best_score
        else:
            margin = best_score
        
        # Base confidence calculation:
        # - Start with keyword score (primary factor)
        # - Add margin boost (clear winner = higher confidence)
        # - Add base value to ensure reasonable minimums
        confidence = best_score * 0.6  # Keyword match contributes 60%
        confidence += min(margin * 0.3, 0.25)  # Margin contributes up to 25%
        confidence += 0.15  # Base confidence floor
        
        # Cap at reasonable bounds
        confidence = min(confidence, 0.95)
        confidence = max(confidence, 0.2)  # Minimum confidence
        
        # Find alternatives (within 0.3 score of best)
        alternatives = [
            r for r in sorted_specialists[1:]
            if best_score - keyword_scores.get(r, 0) < 0.3
        ]
        
        # Build reasoning
        config = DEFAULT_SPECIALISTS.get(best_role)
        matched_keywords = []
        if config:
            for kw in config.keywords:
                if kw.lower() in task.lower():
                    matched_keywords.append(kw)
        
        reasoning = f"Task shows characteristics matching {best_role.value} specialist."
        if matched_keywords:
            reasoning += f" Matched keywords: {', '.join(matched_keywords[:3])}."
        if alternatives:
            reasoning += f" Alternatives considered: {', '.join([s.value for s in alternatives[:2]])}."
        
        # Check if mixed task
        is_mixed = best_score < 0.4 and len([s for s in specialists if keyword_scores.get(s, 0) > 0.2]) > 1
        
        if is_mixed:
            task_type = TaskType.MIXED
            alternatives = sorted_specialists[:3]
            confidence *= 0.7  # Reduce confidence for mixed tasks
            reasoning += " Task appears to have mixed characteristics requiring multiple skill sets."
        
        return RouteResult(
            task_type=task_type,
            confidence=round(confidence, 2),
            assigned_specialist=best_role,
            reasoning=reasoning,
            alternatives=alternatives,
            needs_clarification=confidence < self.confidence_threshold
        )
    
    def _infer_task_type(self, task: str, specialist: SpecialistRole) -> TaskType:
        """Infer specific task type from task content and specialist."""
        task_lower = task.lower()
        
        # Code specialist subtypes
        if specialist == SpecialistRole.CODER:
            if any(kw in task_lower for kw in ["review", "audit", "check code"]):
                return TaskType.CODE_REVIEW
            elif any(kw in task_lower for kw in ["bug", "fix", "error", "broken"]):
                return TaskType.BUG_FIX
            else:
                return TaskType.CODE_IMPLEMENTATION
        
        # Research specialist subtypes
        elif specialist == SpecialistRole.RESEARCHER:
            if any(kw in task_lower for kw in ["investigate", "find out", "what happened"]):
                return TaskType.INVESTIGATE_ISSUE
            else:
                return TaskType.RESEARCH_TOPIC
        
        # Writer specialist subtypes
        elif specialist == SpecialistRole.WRITER:
            if any(kw in task_lower for kw in ["doc", "document", "readme", "guide"]):
                return TaskType.WRITE_DOCUMENTATION
            elif any(kw in task_lower for kw in ["marketing", "copy", "ad", "sales"]):
                return TaskType.WRITE_COPY
            else:
                return TaskType.WRITE_ARTICLE
        
        # Analyst specialist subtypes
        elif specialist == SpecialistRole.ANALYST:
            if any(kw in task_lower for kw in ["compare", "evaluate", "vs", "between"]):
                return TaskType.EVALUATE_OPTIONS
            else:
                return TaskType.ANALYZE_DATA
        
        # Planner specialist subtypes
        elif specialist == SpecialistRole.PLANNER:
            return TaskType.CREATE_PLAN
        
        # Reviewer specialist subtypes
        elif specialist == SpecialistRole.REVIEWER:
            return TaskType.REVIEW_CONTENT
        
        # Creative specialist subtypes
        elif specialist == SpecialistRole.CREATIVE:
            return TaskType.CREATIVE_DESIGN
        
        # Data specialist subtypes
        elif specialist == SpecialistRole.DATA:
            return TaskType.DATA_PROCESSING
        
        # DevOps specialist subtypes
        elif specialist == SpecialistRole.DEVOPS:
            return TaskType.DEPLOYMENT
        
        # Support specialist subtypes
        elif specialist == SpecialistRole.SUPPORT:
            return TaskType.TROUBLESHOOT
        
        return TaskType.UNKNOWN
    
    def _generate_clarification_prompt(self, task: str, classification: RouteResult) -> str:
        """Generate helpful prompt for requesting clarification."""
        if classification.alternatives:
            alts = ", ".join([s.value for s in classification.alternatives[:3]])
            return (
                f"Your task could potentially be handled by multiple specialists: {alts}. "
                f"Could you clarify: Are you primarily looking for {classification.assigned_specialist.value} work "
                f"or one of the alternatives? What is the main goal or expected output?"
            )
        else:
            return (
                "I'm not certain what type of task this is. Could you specify: "
                "1) What is the expected output? "
                "2) What skills are needed (coding, writing, research, analysis)?"
            )


class TaskRouter:
    """
    Auto-Routing pattern: Dynamic task classification and specialist selection.
    
    The router:
    1. Analyzes incoming tasks
    2. Classifies them by type with confidence scoring
    3. Maps to appropriate specialist agents
    4. Returns routing decision with alternatives and reasoning
    
    Supports confidence thresholds and clarification requests for uncertain cases.
    """
    
    def __init__(
        self,
        available_specialists: Optional[List[SpecialistRole]] = None,
        confidence_threshold: float = 0.7,
        state_file: Optional[str] = None
    ):
        self.classifier = TaskClassifier(confidence_threshold)
        self.available_specialists = available_specialists or list(DEFAULT_SPECIALISTS.keys())
        self.confidence_threshold = confidence_threshold
        self.state_file = state_file or ".router_state.json"
        self.classification_history: List[RouteResult] = []
    
    def register_specialist(self, config: SpecialistConfig) -> None:
        """Register a custom specialist configuration."""
        DEFAULT_SPECIALISTS[config.role] = config
        if config.role not in self.available_specialists:
            self.available_specialists.append(config.role)
    
    def route(self, task: str, force_specialist: Optional[SpecialistRole] = None) -> RouteResult:
        """
        Route a task to the appropriate specialist.
        
        Args:
            task: The task to route
            force_specialist: Optional override to force specific specialist
            
        Returns:
            RouteResult with routing decision
        """
        if force_specialist and force_specialist in self.available_specialists:
            return RouteResult(
                task_type=TaskType.UNKNOWN,
                confidence=1.0,
                assigned_specialist=force_specialist,
                reasoning=f"Manually routed to {force_specialist.value} specialist.",
                alternatives=[],
                needs_clarification=False,
                metadata={"forced": True}
            )
        
        # Classify the task
        result = self.classifier.classify(task, self.available_specialists)
        
        # Store in history
        self.classification_history.append(result)
        self._save_state()
        
        return result
    
    def batch_route(self, tasks: List[str]) -> List[RouteResult]:
        """Route multiple tasks efficiently."""
        results = []
        for task in tasks:
            result = self.route(task)
            results.append(result)
        return results
    
    def get_specialist_config(self, role: SpecialistRole) -> Optional[SpecialistConfig]:
        """Get configuration for a specialist."""
        return DEFAULT_SPECIALISTS.get(role)
    
    def _save_state(self):
        """Save routing history to file."""
        try:
            state = {
                "available_specialists": [s.value for s in self.available_specialists],
                "confidence_threshold": self.confidence_threshold,
                "history": [r.to_dict() for r in self.classification_history[-50:]],  # Keep last 50
                "timestamp": datetime.now().isoformat()
            }
            import json
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except:
            pass  # Non-critical
    
    def load_state(self) -> bool:
        """Load state from file."""
        try:
            path = Path(self.state_file)
            if path.exists():
                with open(path, 'r') as f:
                    state = json.load(f)
                self.confidence_threshold = state.get("confidence_threshold", 0.7)
                # Reconstruct specialists
                spec_list = state.get("available_specialists", [])
                self.available_specialists = [SpecialistRole(s) for s in spec_list if s in [r.value for r in SpecialistRole]]
                return True
        except:
            pass
        return False


def parse_specialist_list(specialists_str: str) -> List[SpecialistRole]:
    """Parse comma-separated specialist names into enum values."""
    if not specialists_str.strip():
        # Return all default specialists
        return [s for s in SpecialistRole if s != SpecialistRole.UNKNOWN]
    
    specialists = []
    for spec in specialists_str.split(","):
        spec_clean = spec.strip().lower()
        try:
            role = SpecialistRole(spec_clean)
            specialists.append(role)
        except ValueError:
            # Try to match known aliases
            alias_map = {
                "dev": SpecialistRole.CODER,
                "developer": SpecialistRole.CODER,
                "programmer": SpecialistRole.CODER,
                "code": SpecialistRole.CODER,
                "explore": SpecialistRole.RESEARCHER,
                "find": SpecialistRole.RESEARCHER,
                "content": SpecialistRole.WRITER,
                "docs": SpecialistRole.WRITER,
                "metrics": SpecialistRole.ANALYST,
                "strategy": SpecialistRole.PLANNER,
                "plan": SpecialistRole.PLANNER,
                "qa": SpecialistRole.REVIEWER,
                "audit": SpecialistRole.REVIEWER,
                "design": SpecialistRole.CREATIVE,
                "ops": SpecialistRole.DEVOPS,
                "infra": SpecialistRole.DEVOPS,
                "data eng": SpecialistRole.DATA,
                "help": SpecialistRole.SUPPORT,
            }
            if spec_clean in alias_map:
                specialists.append(alias_map[spec_clean])
            else:
                print(f"Warning: Unknown specialist '{spec}', skipping", file=sys.stderr)
    
    return specialists or [SpecialistRole.CODER, SpecialistRole.WRITER, SpecialistRole.RESEARCHER, SpecialistRole.ANALYST]


def format_output_text(result: RouteResult) -> str:
    """Format routing result as plain text."""
    lines = []
    lines.append("=" * 60)
    lines.append("TASK ROUTING RESULT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Task Type: {result.task_type.value}")
    lines.append(f"Assigned Specialist: {result.assigned_specialist.value}")
    lines.append(f"Confidence: {result.confidence * 100:.0f}%")
    if result.needs_clarification:
        lines.append("Status: NEEDS CLARIFICATION")
    else:
        lines.append("Status: READY TO ROUTE")
    lines.append("")
    lines.append(f"Reasoning: {result.reasoning}")
    if result.alternatives:
        alts = ", ".join([s.value for s in result.alternatives])
        lines.append(f"Alternatives: {alts}")
    if result.needs_clarification and result.clarification_prompt:
        lines.append("")
        lines.append("Clarification Needed:")
        lines.append(result.clarification_prompt)
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_output_markdown(result: RouteResult) -> str:
    """Format routing result as markdown."""
    lines = []
    lines.append("# Task Routing Result")
    lines.append("")
    lines.append(f"**Task Type:** `{result.task_type.value}`")
    lines.append(f"**Assigned Specialist:** `{result.assigned_specialist.value}`")
    lines.append(f"**Confidence:** {result.confidence * 100:.0f}%")
    lines.append("")
    if result.needs_clarification:
        lines.append("## Status: Needs Clarification")
        lines.append("")
    else:
        lines.append("## Status: Ready to Route")
        lines.append("")
    lines.append("## Reasoning")
    lines.append(result.reasoning)
    lines.append("")
    if result.alternatives:
        lines.append("## Alternative Specialists")
        for alt in result.alternatives:
            lines.append(f"- {alt.value}")
        lines.append("")
    if result.needs_clarification and result.clarification_prompt:
        lines.append("## Clarification Request")
        lines.append(result.clarification_prompt)
        lines.append("")
    return "\n".join(lines)


def format_output_json(result: RouteResult) -> str:
    """Format routing result as JSON."""
    return json.dumps(result.to_dict(), indent=2)


def route_main_cli():
    """CLI entry point for route command."""
    parser = argparse.ArgumentParser(
        description="Auto-Router: Classify and route tasks to specialists",
        prog="claw agent-orchestrator route"
    )
    
    parser.add_argument(
        "--task", "-t",
        required=True,
        help="The task to classify and route"
    )
    
    parser.add_argument(
        "--specialists", "-s",
        type=str,
        default="",
        help="Available specialists: 'coder,researcher,writer,analyst' (default: all)"
    )
    
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.7,
        help="Minimum confidence for auto-routing (default: 0.7)"
    )
    
    parser.add_argument(
        "--force",
        type=str,
        choices=[s.value for s in SpecialistRole if s != SpecialistRole.UNKNOWN],
        help="Force routing to specific specialist"
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
        help="Show routing analysis details"
    )
    
    parser.add_argument(
        "--state-file",
        type=str,
        default=".router_state.json",
        help="State file for routing history"
    )
    
    args = parser.parse_args()
    
    # Parse specialists
    available_specialists = parse_specialist_list(args.specialists)
    
    if args.verbose:
        print(f"Available specialists: {[s.value for s in available_specialists]}", file=sys.stderr)
        print(f"Confidence threshold: {args.confidence_threshold}", file=sys.stderr)
        print(f"Task: {args.task[:80]}...", file=sys.stderr)
        print("", file=sys.stderr)
    
    # Create router
    router = TaskRouter(
        available_specialists=available_specialists,
        confidence_threshold=args.confidence_threshold,
        state_file=args.state_file
    )
    
    # Parse force specialist if provided
    force_specialist = None
    if args.force:
        force_specialist = SpecialistRole(args.force)
    
    # Route the task
    try:
        result = router.route(args.task, force_specialist=force_specialist)
        
        if args.verbose:
            print(f"Classification complete:", file=sys.stderr)
            print(f"  Task type: {result.task_type.value}", file=sys.stderr)
            print(f"  Assigned: {result.assigned_specialist.value}", file=sys.stderr)
            print(f"  Confidence: {result.confidence * 100:.0f}%", file=sys.stderr)
            if result.needs_clarification:
                print(f"  Status: NEEDS CLARIFICATION", file=sys.stderr)
            print("", file=sys.stderr)
        
        # Format output
        if args.format == "text":
            print(format_output_text(result))
        elif args.format == "json":
            print(format_output_json(result))
        else:  # markdown
            print(format_output_markdown(result))
        
        # Return exit code
        if result.needs_clarification:
            return 2  # Indicates clarification needed
        return 0
        
    except Exception as e:
        print(f"ERROR: Routing failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main entry point for module execution."""
    return route_main_cli()


if __name__ == "__main__":
    sys.exit(main())
