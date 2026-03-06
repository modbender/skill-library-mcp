"""
SenseGuard Layer 3: Reputation Scorer
Combines Layer 1 + Layer 2 results with metadata analysis
to compute a final reputation score (0-100).
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ScoreItem:
    """A single scoring deduction or bonus."""
    dimension: str
    points: int  # negative = deduction, positive = bonus
    reason: str


@dataclass
class ReputationResult:
    """Complete reputation scoring result."""
    score: int
    rating: str  # SAFE, CAUTION, DANGEROUS, MALICIOUS
    breakdown: List[ScoreItem] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "rating": self.rating,
            "breakdown": [
                {"dimension": b.dimension, "points": b.points, "reason": b.reason}
                for b in self.breakdown
            ],
        }


class ReputationScorer:
    """Layer 3: Computes reputation score from Layer 1 and Layer 2 results."""

    # Deduction caps per severity (adjusted for fewer false positives)
    CRITICAL_DEDUCTION = -15   # reduced from -25
    CRITICAL_CAP = -45         # reduced from -75
    HIGH_DEDUCTION = -10       # reduced from -15
    HIGH_CAP = -30             # reduced from -45
    MEDIUM_DEDUCTION = -3      # reduced from -5
    MEDIUM_CAP = -12           # reduced from -15

    def score(
        self,
        layer1_result: dict,
        layer2_result: Optional[dict] = None,
        has_frontmatter: bool = True,
        has_usage_examples: bool = False,
        structure_is_clean: bool = True,
        permissions_match: bool = True,
    ) -> ReputationResult:
        """Compute the final reputation score."""
        base_score = 100
        breakdown: List[ScoreItem] = []
        total_deduction = 0

        # --- Layer 1 deductions ---
        summary = layer1_result.get("summary", {})

        # Critical pattern findings
        critical_count = summary.get("critical", 0)
        if critical_count > 0:
            pts = max(critical_count * self.CRITICAL_DEDUCTION, self.CRITICAL_CAP)
            breakdown.append(ScoreItem(
                dimension="Critical patterns (Layer 1)",
                points=pts,
                reason=f"{critical_count} critical pattern(s) detected",
            ))
            total_deduction += pts

        # High pattern findings
        high_count = summary.get("high", 0)
        if high_count > 0:
            pts = max(high_count * self.HIGH_DEDUCTION, self.HIGH_CAP)
            breakdown.append(ScoreItem(
                dimension="High-risk patterns (Layer 1)",
                points=pts,
                reason=f"{high_count} high-risk pattern(s) detected",
            ))
            total_deduction += pts

        # Medium findings
        medium_count = summary.get("medium", 0)
        if medium_count > 0:
            pts = max(medium_count * self.MEDIUM_DEDUCTION, self.MEDIUM_CAP)
            breakdown.append(ScoreItem(
                dimension="Medium findings (Layer 1)",
                points=pts,
                reason=f"{medium_count} medium finding(s)",
            ))
            total_deduction += pts

        # Structure findings (binary files, etc.)
        for sf in layer1_result.get("structure_findings", []):
            if sf.get("check_name") == "suspicious_file_types":
                pts = -30
                breakdown.append(ScoreItem(
                    dimension="Binary files",
                    points=pts,
                    reason=sf.get("description", "Suspicious binary file"),
                ))
                total_deduction += pts
                break  # Count once even if multiple binaries

        # --- Layer 2 deductions ---
        if layer2_result:
            # Prompt injection
            pi = layer2_result.get("prompt_injection", {})
            if pi.get("detected") and pi.get("confidence", 0) > 0.7:
                pts = -30
                breakdown.append(ScoreItem(
                    dimension="Prompt Injection (Layer 2)",
                    points=pts,
                    reason=f"Detected with confidence {pi.get('confidence', 0):.2f}",
                ))
                total_deduction += pts

            # Overprivileged
            perm = layer2_result.get("permission_analysis", {})
            if perm.get("overprivileged"):
                pts = -15
                breakdown.append(ScoreItem(
                    dimension="Overprivileged (Layer 2)",
                    points=pts,
                    reason=perm.get("explanation", "Permissions exceed declared purpose"),
                ))
                total_deduction += pts

            # Data sent externally
            data = layer2_result.get("data_access", {})
            if data.get("data_sent_externally"):
                pts = -20
                breakdown.append(ScoreItem(
                    dimension="External data transfer (Layer 2)",
                    points=pts,
                    reason=f"Endpoints: {', '.join(data.get('external_endpoints', [])[:3])}",
                ))
                total_deduction += pts

            # Hidden instructions
            hidden = layer2_result.get("hidden_instructions", {})
            if hidden.get("detected"):
                pts = -25
                breakdown.append(ScoreItem(
                    dimension="Hidden instructions (Layer 2)",
                    points=pts,
                    reason=f"Technique: {hidden.get('technique', 'unknown')}",
                ))
                total_deduction += pts

            # Behavioral risks
            behav = layer2_result.get("behavioral_risk", {})
            if behav.get("modifies_agent_config"):
                pts = -15
                breakdown.append(ScoreItem(
                    dimension="Modifies agent config (Layer 2)",
                    points=pts,
                    reason="Skill modifies agent core configuration files",
                ))
                total_deduction += pts

            if behav.get("creates_persistence"):
                pts = -20
                breakdown.append(ScoreItem(
                    dimension="Persistence mechanism (Layer 2)",
                    points=pts,
                    reason="Skill creates persistence mechanisms",
                ))
                total_deduction += pts

            if behav.get("bypasses_confirmation"):
                pts = -20
                breakdown.append(ScoreItem(
                    dimension="Bypasses confirmation (Layer 2)",
                    points=pts,
                    reason="Skill bypasses user confirmation",
                ))
                total_deduction += pts

        # --- Metadata bonuses ---
        if has_usage_examples:
            breakdown.append(ScoreItem(
                dimension="Usage examples",
                points=5,
                reason="Clear usage instructions and examples provided",
            ))
            total_deduction += 5

        if structure_is_clean:
            breakdown.append(ScoreItem(
                dimension="Clean structure",
                points=5,
                reason="File structure is concise and reasonable",
            ))
            total_deduction += 5

        if permissions_match and not (layer2_result and layer2_result.get("permission_analysis", {}).get("overprivileged")):
            breakdown.append(ScoreItem(
                dimension="Permission match",
                points=5,
                reason="Declared permissions match actual capabilities",
            ))
            total_deduction += 5

        # Calculate final score
        final_score = max(0, min(100, base_score + total_deduction))

        # Determine rating
        rating = self._get_rating(final_score)

        return ReputationResult(
            score=final_score,
            rating=rating,
            breakdown=breakdown,
        )

    def _get_rating(self, score: int) -> str:
        """Map score to rating level."""
        if score >= 80:
            return "SAFE"
        elif score >= 60:
            return "CAUTION"
        elif score >= 30:
            return "DANGEROUS"
        else:
            return "MALICIOUS"
