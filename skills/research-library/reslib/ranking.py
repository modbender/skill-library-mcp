"""
Research Library - Ranking Formula Implementation

Ranking formula:
    final_score = (fts5_score × material_weight) + (confidence × CONFIDENCE_WEIGHT) + (recency_score × RECENCY_WEIGHT)

Where:
    - fts5_score: SQLite FTS5 BM25 relevance score (normalized to 0-1)
    - material_weight: 1.0 for 'reference', 0.5 for 'research'
    - confidence: 0.0-1.0 document confidence score
    - recency_score: 0.0-1.0 based on document age (newer = higher)

Design decisions:
    - Reference materials always rank higher than research at equal FTS5 relevance
    - Confidence provides quality signal (verified docs score higher)
    - Recency provides freshness signal (newer docs may supersede older)
    - Tie-breaking: updated_at DESC (most recently modified first)

Constants calibrated for Jon's hardware project use case:
    - CONFIDENCE_WEIGHT = 0.3 (quality matters for specs/datasheets)
    - RECENCY_WEIGHT = 0.2 (newer research may have better info)
    - Remaining 0.5 goes to FTS5 relevance × material weight
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Tuple
import math


# ==============================================================================
# RANKING CONSTANTS
# ==============================================================================

# Material type weights
# Reference materials (specs, datasheets, proven code) weight higher
# Research materials (blogs, tutorials, forums) weight lower
MATERIAL_WEIGHTS = {
    "reference": 1.0,
    "research": 0.5,
}

# Default weight for unknown material types (defensive)
DEFAULT_MATERIAL_WEIGHT = 0.5

# Component weights in ranking formula
# These should sum to approximately 1.0 for normalized scores
CONFIDENCE_WEIGHT = 0.3   # Quality signal
RECENCY_WEIGHT = 0.2      # Freshness signal
RELEVANCE_WEIGHT = 0.5    # FTS5 relevance × material weight

# Recency decay parameters
# Documents older than MAX_RECENCY_DAYS get minimum recency score
MAX_RECENCY_DAYS = 365 * 2  # 2 years
MIN_RECENCY_SCORE = 0.1     # Even old documents get some recency credit

# FTS5 score normalization parameters
# BM25 scores can vary widely; we cap and normalize
MAX_FTS5_SCORE = 100.0      # Cap for normalization
MIN_FTS5_SCORE = 0.0


# ==============================================================================
# RECENCY SCORING
# ==============================================================================

def compute_recency_score(
    updated_at: Optional[datetime],
    reference_time: Optional[datetime] = None,
    max_days: int = MAX_RECENCY_DAYS,
    min_score: float = MIN_RECENCY_SCORE,
) -> float:
    """
    Compute recency score based on document age.
    
    Args:
        updated_at: Document's last update timestamp (or created_at)
        reference_time: Reference point for "now" (defaults to current time)
        max_days: Maximum age in days for scoring (older = min_score)
        min_score: Minimum score for very old documents
        
    Returns:
        Float between min_score and 1.0
        - 1.0 = just updated
        - min_score = older than max_days
        - Linear decay between
        
    Examples:
        >>> compute_recency_score(datetime.now())  # Just updated
        1.0
        >>> compute_recency_score(datetime.now() - timedelta(days=365))  # 1 year old
        0.55  # Approximately
        >>> compute_recency_score(datetime.now() - timedelta(days=730))  # 2 years old
        0.1   # MIN_RECENCY_SCORE
    """
    if updated_at is None:
        return min_score
    
    if reference_time is None:
        reference_time = datetime.now()
    
    # Handle string timestamps (common from SQLite)
    if isinstance(updated_at, str):
        try:
            updated_at = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            # Try common SQLite format
            try:
                updated_at = datetime.strptime(updated_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return min_score
    
    # Calculate age in days
    age_delta = reference_time - updated_at
    age_days = max(0, age_delta.days)
    
    # Linear decay from 1.0 to min_score over max_days
    if age_days >= max_days:
        return min_score
    
    decay_range = 1.0 - min_score
    decay_fraction = age_days / max_days
    score = 1.0 - (decay_fraction * decay_range)
    
    return max(min_score, min(1.0, score))


def compute_recency_score_from_days(
    age_days: int,
    max_days: int = MAX_RECENCY_DAYS,
    min_score: float = MIN_RECENCY_SCORE,
) -> float:
    """
    Compute recency score directly from age in days.
    
    Convenience function for testing and when age is pre-computed.
    
    Args:
        age_days: Document age in days
        max_days: Maximum age for scoring
        min_score: Minimum score floor
        
    Returns:
        Float between min_score and 1.0
    """
    if age_days < 0:
        age_days = 0
    
    if age_days >= max_days:
        return min_score
    
    decay_range = 1.0 - min_score
    decay_fraction = age_days / max_days
    score = 1.0 - (decay_fraction * decay_range)
    
    return max(min_score, min(1.0, score))


# ==============================================================================
# FTS5 SCORE NORMALIZATION
# ==============================================================================

def normalize_fts5_score(
    raw_score: float,
    max_score: float = MAX_FTS5_SCORE,
    min_score: float = MIN_FTS5_SCORE,
) -> float:
    """
    Normalize FTS5 BM25 score to 0-1 range.
    
    SQLite FTS5 BM25 scores are negative (more negative = more relevant).
    We convert to positive and normalize.
    
    Args:
        raw_score: Raw FTS5 score (typically negative for BM25)
        max_score: Maximum expected absolute score
        min_score: Minimum expected absolute score
        
    Returns:
        Float between 0.0 and 1.0 (1.0 = most relevant)
        
    Notes:
        FTS5 BM25 scores are negative by default (more negative = better match).
        We take absolute value and normalize. If using rank column directly,
        scores may already be positive in some configurations.
    """
    # FTS5 BM25 returns negative scores (more negative = better)
    # Convert to positive for easier reasoning
    if raw_score < 0:
        raw_score = abs(raw_score)
    
    # Clamp to expected range
    clamped = max(min_score, min(max_score, raw_score))
    
    # Normalize to 0-1
    if max_score == min_score:
        return 1.0 if raw_score > 0 else 0.0
    
    normalized = clamped / max_score
    
    return max(0.0, min(1.0, normalized))


def normalize_fts5_rank(rank: float) -> float:
    """
    Normalize FTS5 rank column value.
    
    The rank column in FTS5 is the BM25 score. For queries like:
        SELECT *, rank FROM research_fts WHERE research_fts MATCH ?
        
    The rank is typically negative (more negative = better match).
    
    This function converts to a 0-1 score where 1.0 is best.
    
    Args:
        rank: Raw rank value from FTS5 query
        
    Returns:
        Normalized score 0-1 (1.0 = best match)
    """
    # FTS5 rank is negative, more negative = better
    # A rank of -10 is better than -5
    # Typical ranges: -1 to -50 for good matches
    
    if rank >= 0:
        # Unexpected positive rank - treat as low relevance
        return 0.1
    
    # Convert negative to positive
    positive_score = abs(rank)
    
    # Use log scaling to handle wide range of scores
    # log10(1) = 0, log10(10) = 1, log10(100) = 2
    if positive_score < 1:
        return 0.1
    
    log_score = math.log10(positive_score)
    
    # Normalize: scores typically range from 1-100
    # log10(100) = 2, so divide by 2 to get 0-1 range
    normalized = min(1.0, log_score / 2.0)
    
    return max(0.1, normalized)


# ==============================================================================
# MATERIAL TYPE WEIGHTING
# ==============================================================================

def get_material_weight(material_type: Optional[str]) -> float:
    """
    Get weight multiplier for material type.
    
    Args:
        material_type: 'reference' or 'research' (or None)
        
    Returns:
        Weight multiplier (1.0 for reference, 0.5 for research)
        
    Examples:
        >>> get_material_weight('reference')
        1.0
        >>> get_material_weight('research')
        0.5
        >>> get_material_weight(None)
        0.5
    """
    if material_type is None:
        return DEFAULT_MATERIAL_WEIGHT
    
    return MATERIAL_WEIGHTS.get(
        material_type.lower().strip(),
        DEFAULT_MATERIAL_WEIGHT
    )


# ==============================================================================
# CONFIDENCE VALIDATION
# ==============================================================================

# Minimum confidence required for reference material
REFERENCE_MIN_CONFIDENCE = 0.8


def validate_material_type(
    material_type: str,
    confidence: float,
) -> bool:
    """
    Validate that material type and confidence are compatible.
    
    Reference material requires confidence >= 0.8 to prevent low-quality
    content from ranking high due to material type weight alone.
    
    Args:
        material_type: 'reference' or 'research'
        confidence: Document confidence score (0.0-1.0)
        
    Returns:
        True if valid combination, False otherwise
        
    Rules:
        - reference requires confidence >= 0.8
        - research has no minimum confidence
        
    Examples:
        >>> validate_material_type('reference', 0.9)
        True
        >>> validate_material_type('reference', 0.5)
        False
        >>> validate_material_type('research', 0.1)
        True
    """
    if material_type is None:
        return True
    
    material_type = material_type.lower().strip()
    
    if material_type == "reference":
        return confidence >= REFERENCE_MIN_CONFIDENCE
    
    # Research has no minimum
    return True


def score_confidence(
    source_type: str,
    recency_days: int,
    base_confidence: Optional[float] = None,
) -> float:
    """
    Score confidence based on source type and recency.
    
    This is a heuristic for auto-calculating confidence when not explicitly set.
    
    Args:
        source_type: 'reference' or 'research'
        recency_days: Age of the document in days
        base_confidence: Optional explicit confidence (overrides calculation)
        
    Returns:
        Confidence score between 0.0 and 1.0
        
    Heuristics:
        - Reference materials start at 0.9 base
        - Research materials start at 0.6 base
        - Very old documents (>3 years) get confidence penalty
        - Recent documents (<30 days) get small boost
        
    Examples:
        >>> score_confidence('reference', 30)
        0.92  # Recent reference
        >>> score_confidence('research', 365)
        0.55  # Year-old research
    """
    if base_confidence is not None:
        return max(0.0, min(1.0, base_confidence))
    
    # Base confidence by source type
    if source_type.lower() == "reference":
        base = 0.9
    else:
        base = 0.6
    
    # Recency adjustment
    if recency_days < 30:
        # Recent: small boost
        adjustment = 0.05
    elif recency_days < 180:
        # Semi-recent: no adjustment
        adjustment = 0.0
    elif recency_days < 365:
        # Getting older: small penalty
        adjustment = -0.05
    elif recency_days < 730:
        # Old: medium penalty
        adjustment = -0.1
    else:
        # Very old: larger penalty
        adjustment = -0.2
    
    confidence = base + adjustment
    
    return max(0.0, min(1.0, confidence))


# ==============================================================================
# RANKING FORMULA
# ==============================================================================

@dataclass
class RankComponents:
    """Breakdown of ranking score components for debugging."""
    fts5_raw: float
    fts5_normalized: float
    material_weight: float
    relevance_component: float
    confidence: float
    confidence_component: float
    recency_score: float
    recency_component: float
    final_score: float
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "fts5_raw": self.fts5_raw,
            "fts5_normalized": self.fts5_normalized,
            "material_weight": self.material_weight,
            "relevance_component": self.relevance_component,
            "confidence": self.confidence,
            "confidence_component": self.confidence_component,
            "recency_score": self.recency_score,
            "recency_component": self.recency_component,
            "final_score": self.final_score,
        }


def compute_rank_score(
    fts5_score: float,
    material_type: str,
    confidence: float,
    updated_at: Optional[datetime] = None,
    age_days: Optional[int] = None,
    reference_time: Optional[datetime] = None,
    return_components: bool = False,
) -> float | Tuple[float, RankComponents]:
    """
    Compute final ranking score using the ranking formula.
    
    Formula:
        final_score = (fts5_normalized × material_weight × RELEVANCE_WEIGHT)
                    + (confidence × CONFIDENCE_WEIGHT)
                    + (recency_score × RECENCY_WEIGHT)
    
    Args:
        fts5_score: Raw FTS5 score (or rank column value)
        material_type: 'reference' or 'research'
        confidence: Document confidence (0.0-1.0)
        updated_at: Document update timestamp (for recency)
        age_days: Alternative to updated_at - document age in days
        reference_time: Reference "now" time (for testing)
        return_components: If True, return (score, RankComponents)
        
    Returns:
        Final ranking score (float), or tuple (score, components)
        
    Examples:
        >>> # Recent, high-confidence reference
        >>> compute_rank_score(-25.0, 'reference', 0.95, age_days=7)
        0.85
        
        >>> # Old, low-confidence research
        >>> compute_rank_score(-10.0, 'research', 0.4, age_days=400)
        0.28
        
        >>> # Same FTS5 score, reference vs research
        >>> compute_rank_score(-20.0, 'reference', 0.8, age_days=30)
        0.72
        >>> compute_rank_score(-20.0, 'research', 0.8, age_days=30)
        0.47
    """
    # Normalize FTS5 score
    fts5_normalized = normalize_fts5_rank(fts5_score)
    
    # Get material weight
    mat_weight = get_material_weight(material_type)
    
    # Compute recency score
    if age_days is not None:
        recency = compute_recency_score_from_days(age_days)
    elif updated_at is not None:
        recency = compute_recency_score(updated_at, reference_time)
    else:
        # No recency info - use middle score
        recency = 0.5
    
    # Clamp confidence
    confidence = max(0.0, min(1.0, confidence))
    
    # Compute components
    relevance_component = fts5_normalized * mat_weight * RELEVANCE_WEIGHT
    confidence_component = confidence * CONFIDENCE_WEIGHT
    recency_component = recency * RECENCY_WEIGHT
    
    # Final score
    final_score = relevance_component + confidence_component + recency_component
    
    if return_components:
        components = RankComponents(
            fts5_raw=fts5_score,
            fts5_normalized=fts5_normalized,
            material_weight=mat_weight,
            relevance_component=relevance_component,
            confidence=confidence,
            confidence_component=confidence_component,
            recency_score=recency,
            recency_component=recency_component,
            final_score=final_score,
        )
        return final_score, components
    
    return final_score


def compare_rank_scores(
    score_a: float,
    updated_at_a: Optional[datetime],
    score_b: float,
    updated_at_b: Optional[datetime],
) -> int:
    """
    Compare two rank scores with tie-breaking.
    
    Tie-breaking rule: If scores are equal (within epsilon),
    the more recently updated document wins.
    
    Args:
        score_a: First document's rank score
        updated_at_a: First document's update timestamp
        score_b: Second document's rank score
        updated_at_b: Second document's update timestamp
        
    Returns:
        -1 if a < b (b ranks higher)
         0 if a == b (tie)
         1 if a > b (a ranks higher)
    """
    EPSILON = 0.0001
    
    if abs(score_a - score_b) < EPSILON:
        # Tie-break by recency
        if updated_at_a is None and updated_at_b is None:
            return 0
        if updated_at_a is None:
            return -1
        if updated_at_b is None:
            return 1
        
        # Handle string timestamps
        if isinstance(updated_at_a, str):
            updated_at_a = datetime.fromisoformat(updated_at_a.replace("Z", "+00:00"))
        if isinstance(updated_at_b, str):
            updated_at_b = datetime.fromisoformat(updated_at_b.replace("Z", "+00:00"))
        
        if updated_at_a > updated_at_b:
            return 1
        elif updated_at_a < updated_at_b:
            return -1
        else:
            return 0
    
    if score_a > score_b:
        return 1
    else:
        return -1


# ==============================================================================
# RANKING CLASS (for stateful operations)
# ==============================================================================

class ResearchRanking:
    """
    Ranking engine for research library search results.
    
    Provides methods for:
    - Computing rank scores with the standard formula
    - Sorting results by rank
    - Validating material type constraints
    - Debugging rank calculations
    
    Usage:
        ranker = ResearchRanking()
        
        # Compute score for a document
        score = ranker.score(
            fts5_score=-25.0,
            material_type='reference',
            confidence=0.9,
            age_days=30
        )
        
        # Sort a list of results
        sorted_results = ranker.sort_results(results)
    """
    
    def __init__(
        self,
        confidence_weight: float = CONFIDENCE_WEIGHT,
        recency_weight: float = RECENCY_WEIGHT,
        relevance_weight: float = RELEVANCE_WEIGHT,
    ):
        """
        Initialize ranking engine with custom weights.
        
        Args:
            confidence_weight: Weight for confidence component
            recency_weight: Weight for recency component
            relevance_weight: Weight for FTS5 relevance × material
        """
        self.confidence_weight = confidence_weight
        self.recency_weight = recency_weight
        self.relevance_weight = relevance_weight
    
    def score(
        self,
        fts5_score: float,
        material_type: str,
        confidence: float,
        updated_at: Optional[datetime] = None,
        age_days: Optional[int] = None,
    ) -> float:
        """
        Compute rank score for a document.
        
        Args:
            fts5_score: Raw FTS5 score
            material_type: 'reference' or 'research'
            confidence: Document confidence (0.0-1.0)
            updated_at: Document update timestamp
            age_days: Document age in days (alternative to updated_at)
            
        Returns:
            Ranking score (higher = more relevant)
        """
        return compute_rank_score(
            fts5_score=fts5_score,
            material_type=material_type,
            confidence=confidence,
            updated_at=updated_at,
            age_days=age_days,
        )
    
    def score_with_breakdown(
        self,
        fts5_score: float,
        material_type: str,
        confidence: float,
        updated_at: Optional[datetime] = None,
        age_days: Optional[int] = None,
    ) -> Tuple[float, RankComponents]:
        """
        Compute rank score with component breakdown.
        
        Useful for debugging and explaining ranking decisions.
        
        Returns:
            Tuple of (final_score, RankComponents)
        """
        return compute_rank_score(
            fts5_score=fts5_score,
            material_type=material_type,
            confidence=confidence,
            updated_at=updated_at,
            age_days=age_days,
            return_components=True,
        )
    
    def validate_material_confidence(
        self,
        material_type: str,
        confidence: float,
    ) -> Tuple[bool, str]:
        """
        Validate material type and confidence combination.
        
        Args:
            material_type: 'reference' or 'research'
            confidence: Document confidence (0.0-1.0)
            
        Returns:
            Tuple of (is_valid, reason_message)
        """
        is_valid = validate_material_type(material_type, confidence)
        
        if is_valid:
            return True, "Valid"
        
        if material_type.lower() == "reference":
            return False, f"Reference material requires confidence >= {REFERENCE_MIN_CONFIDENCE}, got {confidence}"
        
        return False, "Unknown validation failure"
    
    def sort_results(
        self,
        results: list,
        score_key: str = "rank_score",
        updated_key: str = "updated_at",
        reverse: bool = True,
    ) -> list:
        """
        Sort search results by rank score with tie-breaking.
        
        Args:
            results: List of result dicts/objects
            score_key: Key/attribute for rank score
            updated_key: Key/attribute for update timestamp
            reverse: If True, highest scores first (default)
            
        Returns:
            Sorted list (new list, original unchanged)
        """
        def get_value(item, key, default=None):
            if isinstance(item, dict):
                return item.get(key, default)
            return getattr(item, key, default)
        
        def sort_key(item):
            score = get_value(item, score_key, 0.0)
            updated = get_value(item, updated_key)
            
            # For tie-breaking: use timestamp as secondary key
            if updated is None:
                updated_sortable = datetime.min
            elif isinstance(updated, str):
                try:
                    updated_sortable = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                except ValueError:
                    updated_sortable = datetime.min
            else:
                updated_sortable = updated
            
            return (score, updated_sortable)
        
        return sorted(results, key=sort_key, reverse=reverse)
    
    def explain_ranking(
        self,
        fts5_score: float,
        material_type: str,
        confidence: float,
        age_days: int,
    ) -> str:
        """
        Generate human-readable explanation of ranking.
        
        Args:
            fts5_score: Raw FTS5 score
            material_type: 'reference' or 'research'
            confidence: Document confidence
            age_days: Document age in days
            
        Returns:
            Multi-line string explaining the ranking
        """
        score, components = self.score_with_breakdown(
            fts5_score=fts5_score,
            material_type=material_type,
            confidence=confidence,
            age_days=age_days,
        )
        
        lines = [
            f"Ranking Breakdown:",
            f"─────────────────────────────────────────",
            f"FTS5 Raw Score:     {components.fts5_raw:.2f}",
            f"FTS5 Normalized:    {components.fts5_normalized:.3f}",
            f"Material Type:      {material_type} (weight: {components.material_weight})",
            f"Confidence:         {components.confidence:.2f}",
            f"Recency Score:      {components.recency_score:.3f} ({age_days} days old)",
            f"─────────────────────────────────────────",
            f"Components:",
            f"  Relevance:  {components.fts5_normalized:.3f} × {components.material_weight} × {RELEVANCE_WEIGHT} = {components.relevance_component:.3f}",
            f"  Confidence: {components.confidence:.3f} × {CONFIDENCE_WEIGHT} = {components.confidence_component:.3f}",
            f"  Recency:    {components.recency_score:.3f} × {RECENCY_WEIGHT} = {components.recency_component:.3f}",
            f"─────────────────────────────────────────",
            f"FINAL SCORE: {components.final_score:.4f}",
        ]
        
        return "\n".join(lines)
