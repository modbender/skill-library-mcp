"""
ConvoYield — Conversational Yield Optimization Engine

Treat every conversation as a yield-bearing financial instrument.
Extract maximum value from every bot interaction using zero-cost
behavioral algorithms. No external APIs. No paid services. Pure logic.

Core Components:
    - SentimentArbitrage: Detect emotional gaps that create revenue opportunities
    - MicroConversion: Track and optimize dozens of value-extraction moments per conversation
    - MomentumScorer: Measure conversational momentum to time actions perfectly
    - YieldForecaster: Predict the total value of a conversation in real-time
    - PlayCaller: Recommend optimal "plays" based on live conversational state
    - ConvoYield: The orchestrator that ties it all together

Usage:
    from convoyield import ConvoYield

    engine = ConvoYield()
    result = engine.process("I'm frustrated with my current provider")
    print(result.recommended_play)       # -> "competitor_displacement"
    print(result.estimated_yield)         # -> 47.50
    print(result.micro_conversions)       # -> [MicroConversion(...), ...]
    print(result.sentiment_arbitrage)     # -> ArbitrageOpportunity(type="frustration_capture", ...)
"""

__version__ = "1.0.0"

from convoyield.orchestrator import ConvoYield
from convoyield.engines.sentiment_arbitrage import SentimentArbitrage
from convoyield.engines.micro_conversion import MicroConversionTracker
from convoyield.engines.momentum import MomentumScorer
from convoyield.engines.yield_forecaster import YieldForecaster
from convoyield.engines.play_caller import PlayCaller
from convoyield.models.conversation import ConversationState, Turn
from convoyield.models.yield_result import YieldResult

__all__ = [
    "ConvoYield",
    "SentimentArbitrage",
    "MicroConversionTracker",
    "MomentumScorer",
    "YieldForecaster",
    "PlayCaller",
    "ConversationState",
    "Turn",
    "YieldResult",
]
