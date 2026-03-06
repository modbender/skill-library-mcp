"""
Neuroscience-inspired memory scoring system.
Inspired by: Hippocampus (importance), Amygdala (emotions), VTA (value/reward).
"""

import re
import time
from datetime import datetime, timedelta
from typing import Any

# =============================================================================
# HIPPOCAMPUS - Importance Calculation
# =============================================================================

def calculate_importance(content: str, memory_history: list[dict] | None = None) -> float:
    """
    Calculate importance score based on recency, frequency, corrections, and emotional weight.
    
    Args:
        content: Memory content to evaluate
        memory_history: List of past memory entries with timestamps
        
    Returns:
        Score between 0-1
    """
    if not content:
        return 0.0
    
    score = 0.0
    factors = []
    
    # 1. Recency factor (0-0.3)
    recency_score = 0.3
    if memory_history:
        # Find most recent mention of similar content
        for mem in reversed(memory_history):
            if 'timestamp' in mem:
                try:
                    mem_time = datetime.fromisoformat(mem['timestamp'].replace('Z', '+00:00'))
                    age_hours = (datetime.now(mem_time.tzinfo) - mem_time).total_seconds() / 3600
                    if age_hours < 1:
                        recency_score = 0.3
                    elif age_hours < 24:
                        recency_score = 0.3 * (1 - age_hours / 24)
                    elif age_hours < 168:  # 1 week
                        recency_score = 0.1
                    else:
                        recency_score = 0.05
                    break
                except (ValueError, TypeError):
                    pass
    factors.append(("recency", recency_score))
    score += recency_score
    
    # 2. Frequency factor (0-0.25)
    frequency_score = 0.1  # base
    if memory_history:
        # Count mentions of similar content
        content_lower = content.lower()
        mentions = sum(1 for m in memory_history 
                      if m.get('content', '').lower() in content_lower or 
                      content_lower in m.get('content', '').lower())
        frequency_score = min(0.25, 0.1 + (mentions * 0.05))
    factors.append(("frequency", frequency_score))
    score += frequency_score
    
    # 3. Corrections/importance markers (0-0.25)
    correction_score = 0.0
    correction_keywords = [
        'important', 'remember', 'critical', 'essential', 'key', 
        'must not forget', 'dont forget', 'must remember',
        'significant', 'vital', 'crucial'
    ]
    content_lower = content.lower()
    for keyword in correction_keywords:
        if keyword in content_lower:
            correction_score += 0.1
            if 'important' in keyword or 'remember' in keyword:
                correction_score += 0.05
    correction_score = min(0.25, correction_score)
    factors.append(("corrections", correction_score))
    score += correction_score
    
    # 4. Emotional weight (0-0.2)
    emotional_score = 0.1
    emotional_keywords = {
        'love': 0.2, 'hate': 0.2, 'fear': 0.15, 'excited': 0.15,
        'happy': 0.1, 'sad': 0.1, 'angry': 0.15, 'wow': 0.1,
        'amazing': 0.15, 'terrible': 0.15, 'awesome': 0.1
    }
    for emotion, weight in emotional_keywords.items():
        if emotion in content_lower:
            emotional_score += weight
    emotional_score = min(0.2, emotional_score)
    factors.append(("emotional", emotional_score))
    score += emotional_score
    
    return min(1.0, max(0.0, score))


# =============================================================================
# AMYGDALA - Emotion Detection
# =============================================================================

EMOTION_KEYWORDS = {
    'joy': ['happy', 'joy', 'excited', 'love', 'wonderful', 'great', 'amazing', 'fantastic', 'glad', 'delighted', '😊', '🎉', '❤️'],
    'sadness': ['sad', 'depressed', 'upset', 'unhappy', 'disappointed', 'grief', 'sorrow', '😭', '😢', '😞'],
    'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated', 'irritated', 'hate', 'rage', '😠', '😡'],
    'fear': ['afraid', 'scared', 'fear', 'worried', 'anxious', 'nervous', 'terrified', 'panic', '😨', '😰'],
    'curiosity': ['curious', 'wonder', 'interesting', 'why', 'how', 'question', 'explore', 'discover', 'learn', '🤔', '💡'],
    'connection': ['friend', 'family', 'together', 'miss', 'bond', 'relationship', 'connect', 'belong', '👋', '🤝'],
    'accomplishment': ['achieved', 'success', 'completed', 'finished', 'won', 'accomplished', 'proud', 'victory', 'trophy', '🏆', '🎯'],
    'fatigue': ['tired', 'exhausted', 'drained', 'sleepy', 'burnout', 'overwhelmed', 'fatigue', '😴', '😩', '🥱']
}


def detect_emotions(content: str, query_context: str | None = None) -> dict[str, dict[str, float]]:
    """
    Detect emotions in content.
    
    Args:
        content: Text to analyze
        query_context: Optional context to calculate match_score
        
    Returns:
        Dict of emotion -> {intensity: 0-1, match_score: 0-1}
    """
    if not content:
        return {emotion: {'intensity': 0.0, 'match_score': 0.0} for emotion in EMOTION_KEYWORDS}
    
    content_lower = content.lower()
    emotions_found = {}
    
    # Detect each emotion
    for emotion, keywords in EMOTION_KEYWORDS.items():
        intensity = 0.0
        matches = 0
        for keyword in keywords:
            if keyword in content_lower:
                intensity += 0.15
                matches += 1
        intensity = min(1.0, intensity)
        emotions_found[emotion] = {'intensity': intensity, 'match_score': 0.0}
    
    # Calculate match_score if query_context provided
    if query_context:
        query_lower = query_context.lower()
        query_emotions = []
        for emotion, keywords in EMOTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query_lower:
                    query_emotions.append(emotion)
                    break
        
        for emotion in emotions_found:
            if emotion in query_emotions and emotions_found[emotion]['intensity'] > 0:
                emotions_found[emotion]['match_score'] = emotions_found[emotion]['intensity']
            else:
                emotions_found[emotion]['match_score'] = 0.0
    
    return emotions_found


def get_dominant_emotion(emotions: dict[str, dict[str, float]]) -> tuple[str, float]:
    """Get the strongest emotion from detected emotions."""
    if not emotions:
        return ('curiosity', 0.0)
    
    max_emotion = max(emotions.items(), key=lambda x: x[1].get('intensity', 0))
    return (max_emotion[0], max_emotion[1].get('intensity', 0))


# =============================================================================
# VTA - Value Calculation (Reward-based)
# =============================================================================

REWARD_TYPES = ['accomplishment', 'social', 'curiosity', 'connection', 'creative', 'competence']

REWARD_KEYWORDS = {
    'accomplishment': ['completed', 'finished', 'achieved', 'success', 'won', 'accomplished', 'done', 'goal', 'milestone', 'trophy'],
    'social': ['friend', 'family', 'together', 'team', 'collaborate', 'community', 'share', 'talk', 'chat', 'meet'],
    'curiosity': ['learn', 'discover', 'explore', 'question', 'wonder', 'research', 'investigate', 'understand', 'insight'],
    'connection': ['connect', 'bond', 'relate', 'understand', 'empathy', 'support', 'care', 'belong', 'trust'],
    'creative': ['create', 'design', 'invent', 'imagine', 'art', 'music', 'write', 'build', 'make', 'innovate'],
    'competence': ['skill', 'expert', 'master', 'learn', 'improve', 'better', 'efficient', 'capable', 'ability', 'proven']
}


def calculate_value(content: str, reward_type: str | None = None, task_alignment: float = 0.5) -> float:
    """
    Calculate value score based on reward type and task alignment.
    
    Args:
        content: Memory content to evaluate
        reward_type: Type of reward (accomplishment, social, curiosity, connection, creative, competence)
        task_alignment: How well this aligns with current task (0-1)
        
    Returns:
        Score between 0-1
    """
    if not content:
        return 0.0
    
    content_lower = content.lower()
    
    # Base value from reward keywords
    base_value = 0.2
    
    # Check specific reward type if provided
    if reward_type and reward_type in REWARD_KEYWORDS:
        reward_keywords = REWARD_KEYWORDS[reward_type]
        for keyword in reward_keywords:
            if keyword in content_lower:
                base_value += 0.12
    else:
        # Check all reward types
        for rtype, keywords in REWARD_KEYWORDS.items():
            for keyword in keywords:
                if keyword in content_lower:
                    base_value += 0.05
                    break
    
    base_value = min(0.7, base_value)
    
    # Task alignment factor
    alignment_score = task_alignment * 0.3
    
    return min(1.0, base_value + alignment_score)


# =============================================================================
# HYBRID SCORING - Combining All Factors
# =============================================================================

def neuroscience_score(memory: dict[str, Any], query_context: str | None = None) -> float:
    """
    Calculate hybrid neuroscience-based score for a memory.
    
    Formula: (Base × 0.25) + (Importance × 0.30) + (Value × 0.25) + (Emotion × 0.20)
    
    Args:
        memory: Dict with 'content', 'timestamp', 'reward_type', 'task_alignment'
        query_context: Optional context for emotion matching
        
    Returns:
        Combined score 0-1
    """
    content = memory.get('content', '')
    memory_history = memory.get('history', [])
    
    # 1. Base score (0.25)
    base_score = 0.25 if content else 0.0
    
    # 2. Importance (0.30) - Hippocampus
    importance = calculate_importance(content, memory_history)
    
    # 3. Value (0.25) - VTA
    reward_type = memory.get('reward_type')
    task_alignment = memory.get('task_alignment', 0.5)
    value = calculate_value(content, reward_type, task_alignment)
    
    # 4. Emotion (0.20) - Amygdala
    emotions = detect_emotions(content, query_context)
    dominant_intensity = get_dominant_emotion(emotions)[1]
    emotion_score = dominant_intensity * 0.5  # Scale to 0-0.5, then ×0.4 in formula
    
    # Combined formula
    combined = (
        (base_score * 0.25) +
        (importance * 0.30) +
        (value * 0.25) +
        (emotion_score * 0.20)
    )
    
    return min(1.0, max(0.0, combined))


# =============================================================================
# QUICK FILTER - Fast Pre-filtering
# =============================================================================

def quick_filter(memories: list[dict], intent: str | None = None) -> list[dict]:
    """
    Quick filter to skip irrelevant memories.
    
    Filters out:
    - Memories with 0 importance
    - Memories with mismatched emotions (if intent provided)
    
    Args:
        memories: List of memory dicts
        intent: Query intent/context for emotion matching
        
    Returns:
        Filtered list of memories
    """
    if not memories:
        return []
    
    filtered = []
    
    for memory in memories:
        content = memory.get('content', '')
        
        # Skip if no content
        if not content:
            continue
        
        # Calculate importance - skip if 0
        importance = calculate_importance(content, memory.get('history', []))
        if importance <= 0:
            continue
        
        # If intent provided, check emotion alignment
        if intent:
            emotions = detect_emotions(content, intent)
            intent_lower = intent.lower()
            
            # Check if any detected emotion aligns with intent
            has_aligned_emotion = False
            for emotion, scores in emotions.items():
                if emotion in intent_lower or scores.get('match_score', 0) > 0:
                    has_aligned_emotion = True
                    break
            
            # If no alignment, still include but with low priority flag
            if not has_aligned_emotion:
                memory['_low_priority'] = True
        
        memory['_importance'] = importance
        filtered.append(memory)
    
    # Sort by importance
    filtered.sort(key=lambda m: m.get('_importance', 0), reverse=True)
    
    return filtered


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def explain_score(memory: dict[str, Any], query_context: str | None = None) -> dict[str, float]:
    """
    Get detailed breakdown of scoring components.
    
    Returns:
        Dict with individual component scores
    """
    content = memory.get('content', '')
    memory_history = memory.get('history', [])
    
    return {
        'base': 0.25 if content else 0.0,
        'importance': calculate_importance(content, memory_history),
        'value': calculate_value(
            content, 
            memory.get('reward_type'), 
            memory.get('task_alignment', 0.5)
        ),
        'emotion': get_dominant_emotion(detect_emotions(content, query_context))[1] * 0.5,
        'total': neuroscience_score(memory, query_context)
    }
