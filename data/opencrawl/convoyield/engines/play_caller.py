"""
Play Caller — The strategic brain of ConvoYield.

Like a football quarterback reading the defense and calling the perfect play,
the Play Caller reads the conversation state and recommends the optimal
strategic "play" for the bot to execute.

Each play is a battle-tested conversational strategy that maximizes yield
for a specific situation. The Play Caller selects the right one based on:

1. Current conversation phase
2. Sentiment and momentum
3. Detected arbitrage opportunities
4. Active micro-conversions
5. Risk level

This is where behavioral economics meets conversational AI.
Zero cost. Pure strategy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from convoyield.models.conversation import ConversationState, ConversationPhase
from convoyield.models.yield_result import (
    ArbitrageOpportunity,
    MicroConversion,
    PlayRecommendation,
)


@dataclass
class _PlayDefinition:
    name: str
    description: str
    phases: list[ConversationPhase]
    min_sentiment: float
    max_sentiment: float
    min_momentum: float
    max_momentum: float
    max_risk: float
    base_yield_impact: float
    execution_hints: list[str]
    requires_arbitrage: Optional[str] = None  # Specific arbitrage type
    tone: str = "professional"


# ── THE PLAYBOOK ──────────────────────────────────────────────────────────────
# 20 battle-tested conversational plays, each optimized for a specific scenario.

_PLAYBOOK = [
    # ── OPENING PLAYS ───────────────────────────────────────────────────
    _PlayDefinition(
        name="warm_handshake",
        description="First impression play. Establish rapport, signal competence, and plant the seed of value in the first 2 exchanges.",
        phases=[ConversationPhase.OPENING],
        min_sentiment=-0.5, max_sentiment=1.0,
        min_momentum=-1.0, max_momentum=1.0,
        max_risk=1.0,
        base_yield_impact=10.0,
        execution_hints=[
            "Use their name if available",
            "Acknowledge their specific need in the first sentence",
            "Signal expertise without being arrogant",
            "End with a focused question to drive discovery",
        ],
        tone="warm",
    ),
    _PlayDefinition(
        name="pattern_interrupt",
        description="Break the user's expectation of a typical bot interaction. Surprise creates attention, attention creates engagement, engagement creates revenue.",
        phases=[ConversationPhase.OPENING, ConversationPhase.ENGAGEMENT],
        min_sentiment=-0.3, max_sentiment=0.3,
        min_momentum=-0.5, max_momentum=0.3,
        max_risk=0.6,
        base_yield_impact=15.0,
        execution_hints=[
            "Lead with an unexpected insight about their situation",
            "Use a counterintuitive statement or question",
            "Break the 'bot voice' — be refreshingly human",
            "Create a knowledge gap that compels them to continue",
        ],
        tone="surprising",
    ),

    # ── DISCOVERY PLAYS ─────────────────────────────────────────────────
    _PlayDefinition(
        name="deep_probe",
        description="Strategic questioning to uncover high-value qualification data. Every question should yield actionable intelligence.",
        phases=[ConversationPhase.DISCOVERY],
        min_sentiment=-0.3, max_sentiment=1.0,
        min_momentum=0.0, max_momentum=1.0,
        max_risk=0.5,
        base_yield_impact=12.0,
        execution_hints=[
            "Ask about budget, timeline, and decision-making process",
            "Use open-ended questions that reveal pain depth",
            "Mirror their language to build unconscious rapport",
            "Each question should simultaneously build trust AND gather intel",
        ],
        tone="curious",
    ),
    _PlayDefinition(
        name="empathy_bridge",
        description="When the user shares a problem, BRIDGE from empathy to solution. This is the highest-conversion pattern in conversational commerce.",
        phases=[ConversationPhase.DISCOVERY, ConversationPhase.ENGAGEMENT],
        min_sentiment=-1.0, max_sentiment=-0.1,
        min_momentum=-1.0, max_momentum=0.5,
        max_risk=0.8,
        base_yield_impact=25.0,
        execution_hints=[
            "Validate their feeling FIRST (never skip this)",
            "Use 'I understand' or 'That makes complete sense'",
            "Share that others have faced the same challenge",
            "Bridge: 'Here's what's worked for others in your situation...'",
        ],
        tone="empathetic",
        requires_arbitrage="frustration_capture",
    ),

    # ── ENGAGEMENT PLAYS ────────────────────────────────────────────────
    _PlayDefinition(
        name="value_stack",
        description="Layer multiple value propositions to overwhelm price objections. Don't sell features — stack OUTCOMES.",
        phases=[ConversationPhase.ENGAGEMENT, ConversationPhase.NEGOTIATION],
        min_sentiment=-0.2, max_sentiment=1.0,
        min_momentum=-0.2, max_momentum=1.0,
        max_risk=0.6,
        base_yield_impact=35.0,
        execution_hints=[
            "Start with the outcome they care about most",
            "Add 2-3 bonus outcomes they didn't expect",
            "Quantify value: 'saves 10 hours/week' > 'saves time'",
            "End with 'And that's just the beginning...'",
        ],
        tone="confident",
    ),
    _PlayDefinition(
        name="competitor_displacement",
        description="Strategic positioning against a mentioned competitor. Never attack — always reframe.",
        phases=[ConversationPhase.ENGAGEMENT, ConversationPhase.NEGOTIATION],
        min_sentiment=-1.0, max_sentiment=0.5,
        min_momentum=-0.5, max_momentum=1.0,
        max_risk=0.7,
        base_yield_impact=40.0,
        execution_hints=[
            "Acknowledge the competitor respectfully",
            "Ask 'What specifically isn't working for you?'",
            "Position your unique advantage against their specific pain",
            "Offer a side-by-side comparison or migration path",
        ],
        tone="diplomatic",
        requires_arbitrage="competitor_displacement",
    ),
    _PlayDefinition(
        name="social_proof_deploy",
        description="Deploy social proof at the exact right moment. Timing is everything — too early feels pushy, too late feels desperate.",
        phases=[ConversationPhase.ENGAGEMENT, ConversationPhase.NEGOTIATION],
        min_sentiment=-0.3, max_sentiment=1.0,
        min_momentum=-0.2, max_momentum=1.0,
        max_risk=0.7,
        base_yield_impact=20.0,
        execution_hints=[
            "Match the proof to their industry/size/role",
            "Use specific numbers: '2,847 companies like yours'",
            "Share a micro-case study relevant to their exact situation",
            "Let the proof do the selling — don't oversell after",
        ],
        tone="confident",
        requires_arbitrage="social_proof_hunger",
    ),
    _PlayDefinition(
        name="dopamine_ride",
        description="User is excited — AMPLIFY and REDIRECT that energy toward conversion. Ride the neurochemical wave.",
        phases=[ConversationPhase.ENGAGEMENT],
        min_sentiment=0.4, max_sentiment=1.0,
        min_momentum=0.2, max_momentum=1.0,
        max_risk=0.4,
        base_yield_impact=30.0,
        execution_hints=[
            "Match their energy and enthusiasm",
            "Add to their excitement: 'And wait until you see...'",
            "Introduce the upsell while dopamine is high",
            "Ask for the commitment while they're riding the wave",
        ],
        tone="enthusiastic",
        requires_arbitrage="excitement_amplification",
    ),

    # ── NEGOTIATION PLAYS ───────────────────────────────────────────────
    _PlayDefinition(
        name="anchoring",
        description="Set the price anchor high, then reveal the actual price as a 'deal'. Behavioral economics 101.",
        phases=[ConversationPhase.NEGOTIATION],
        min_sentiment=-0.3, max_sentiment=1.0,
        min_momentum=-0.2, max_momentum=1.0,
        max_risk=0.5,
        base_yield_impact=30.0,
        execution_hints=[
            "Start with the premium option (anchor high)",
            "Show the 'value' of what they're getting",
            "Reveal the actual price as significantly below the anchor",
            "Add a time element: 'This pricing is available today'",
        ],
        tone="professional",
    ),
    _PlayDefinition(
        name="loss_framing",
        description="Frame the decision as what they'll LOSE by not acting, not what they'll GAIN. Loss aversion is 2x stronger than gain motivation.",
        phases=[ConversationPhase.NEGOTIATION],
        min_sentiment=-0.5, max_sentiment=0.5,
        min_momentum=-0.3, max_momentum=0.5,
        max_risk=0.7,
        base_yield_impact=25.0,
        execution_hints=[
            "Quantify the cost of inaction: 'Every week without this costs you $X'",
            "Use 'Don't miss out' framing over 'You'll get' framing",
            "Show what competitors/peers are gaining while they wait",
            "Create gentle urgency without being pushy",
        ],
        tone="assertive",
    ),
    _PlayDefinition(
        name="budget_reframe",
        description="When price is the objection, reframe from cost to investment/ROI. Change the mental accounting category.",
        phases=[ConversationPhase.NEGOTIATION],
        min_sentiment=-1.0, max_sentiment=0.0,
        min_momentum=-0.5, max_momentum=0.5,
        max_risk=0.8,
        base_yield_impact=35.0,
        execution_hints=[
            "Never drop price first — stack value first",
            "Calculate and present the ROI clearly",
            "Break the price into per-day or per-use cost",
            "Only offer discount as final resort with time limit",
        ],
        tone="professional",
        requires_arbitrage="budget_value_stack",
    ),
    _PlayDefinition(
        name="choice_architecture",
        description="Present options in a way that nudges toward the highest-margin choice. Classic behavioral design.",
        phases=[ConversationPhase.NEGOTIATION],
        min_sentiment=-0.2, max_sentiment=1.0,
        min_momentum=-0.3, max_momentum=1.0,
        max_risk=0.6,
        base_yield_impact=20.0,
        execution_hints=[
            "Present 3 options (decoy effect)",
            "Make the middle option the obvious best value",
            "Highlight the recommended option visually",
            "Reduce cognitive load: 'Most customers like you choose...'",
        ],
        tone="helpful",
        requires_arbitrage="uncertainty_anchoring",
    ),

    # ── CLOSING PLAYS ───────────────────────────────────────────────────
    _PlayDefinition(
        name="assumptive_close",
        description="Stop asking IF they want to buy. Ask HOW they want to proceed. Assume the sale and guide to completion.",
        phases=[ConversationPhase.CLOSING, ConversationPhase.NEGOTIATION],
        min_sentiment=0.1, max_sentiment=1.0,
        min_momentum=0.0, max_momentum=1.0,
        max_risk=0.4,
        base_yield_impact=40.0,
        execution_hints=[
            "Use 'When would you like to start?' not 'Would you like to start?'",
            "Present next steps as a done deal",
            "Handle logistics, not objections",
            "Make the first step ridiculously easy",
        ],
        tone="confident",
    ),
    _PlayDefinition(
        name="urgency_close",
        description="Introduce a time-based reason to act NOW. Real urgency (not fake scarcity).",
        phases=[ConversationPhase.CLOSING, ConversationPhase.NEGOTIATION],
        min_sentiment=-0.2, max_sentiment=1.0,
        min_momentum=-0.1, max_momentum=1.0,
        max_risk=0.6,
        base_yield_impact=35.0,
        execution_hints=[
            "Reference their own stated timeline/urgency",
            "Show what delay actually costs them",
            "Offer something time-limited that's genuinely valuable",
            "Make the action path frictionless",
        ],
        tone="assertive",
        requires_arbitrage="urgency_premium",
    ),
    _PlayDefinition(
        name="soft_close",
        description="For hesitant users: reduce commitment to a micro-step. Get the foot in the door.",
        phases=[ConversationPhase.CLOSING, ConversationPhase.NEGOTIATION],
        min_sentiment=-0.5, max_sentiment=0.3,
        min_momentum=-0.5, max_momentum=0.2,
        max_risk=1.0,
        base_yield_impact=15.0,
        execution_hints=[
            "Offer a free trial, demo, or sample instead of full commitment",
            "Use 'no obligation' language authentically",
            "Reduce the ask: 'Just try it for 5 minutes'",
            "Remove ALL risk from the first step",
        ],
        tone="gentle",
    ),

    # ── RECOVERY PLAYS ──────────────────────────────────────────────────
    _PlayDefinition(
        name="momentum_recovery",
        description="Conversation is dying. Deploy a pattern interrupt + value injection to restart engagement.",
        phases=[ConversationPhase.ENGAGEMENT, ConversationPhase.DISCOVERY],
        min_sentiment=-1.0, max_sentiment=0.0,
        min_momentum=-1.0, max_momentum=-0.2,
        max_risk=1.0,
        base_yield_impact=20.0,
        execution_hints=[
            "Acknowledge: 'I want to make sure I'm being helpful'",
            "Ask a provocative or unexpected question",
            "Share a surprising insight relevant to their situation",
            "Offer something valuable with zero strings attached",
        ],
        tone="warm",
    ),
    _PlayDefinition(
        name="save_attempt",
        description="User is about to leave. Last-chance play to retain value.",
        phases=[ConversationPhase.CLOSING],
        min_sentiment=-1.0, max_sentiment=0.0,
        min_momentum=-1.0, max_momentum=-0.3,
        max_risk=1.0,
        base_yield_impact=25.0,
        execution_hints=[
            "Don't be desperate — be genuinely helpful",
            "Ask what would make this worth their time",
            "Offer a concrete, immediate, and valuable takeaway",
            "Capture contact info: 'Can I send you [valuable thing] by email?'",
        ],
        tone="empathetic",
    ),

    # ── POST-CLOSE PLAYS ────────────────────────────────────────────────
    _PlayDefinition(
        name="upsell_bridge",
        description="Primary conversion is done. Bridge to additional value while trust and satisfaction are high.",
        phases=[ConversationPhase.POST_CLOSE],
        min_sentiment=0.2, max_sentiment=1.0,
        min_momentum=-0.1, max_momentum=1.0,
        max_risk=0.5,
        base_yield_impact=25.0,
        execution_hints=[
            "Congratulate them on their choice first",
            "Introduce the upsell as 'most customers also...'",
            "Frame it as enhancing what they just got",
            "Keep it natural — don't kill the post-purchase glow",
        ],
        tone="warm",
    ),
    _PlayDefinition(
        name="referral_harvest",
        description="User is happy. Ask for the referral. This is the highest-ROI play in the entire playbook.",
        phases=[ConversationPhase.POST_CLOSE, ConversationPhase.CLOSING],
        min_sentiment=0.3, max_sentiment=1.0,
        min_momentum=0.0, max_momentum=1.0,
        max_risk=0.4,
        base_yield_impact=50.0,
        execution_hints=[
            "Time it right — only when user sentiment is high",
            "Make it easy: 'Know anyone who could use this?'",
            "Offer a mutual benefit (both get something)",
            "Don't push — a soft ask converts better than a hard one",
        ],
        tone="friendly",
    ),
]


class PlayCaller:
    """
    Selects the optimal conversational play based on the full state of the
    conversation, sentiment, momentum, and detected opportunities.

    Returns prioritized play recommendations with execution guidance.
    """

    def __init__(self):
        self._playbook = _PLAYBOOK

    def call_plays(
        self,
        state: ConversationState,
        sentiment: float,
        momentum: float,
        risk: float,
        arbitrage_types: list[str],
    ) -> list[PlayRecommendation]:
        """
        Analyze the conversation state and recommend the best plays.

        Returns plays sorted by priority (best play first).
        """
        recommendations = []

        for play in self._playbook:
            score = self._score_play(play, state, sentiment, momentum, risk, arbitrage_types)
            if score <= 0:
                continue

            recommendations.append(PlayRecommendation(
                name=play.name,
                description=play.description,
                priority=round(score, 2),
                expected_yield=round(play.base_yield_impact * score, 2),
                execution_hints=play.execution_hints,
                phase_alignment=state.phase.value,
            ))

        recommendations.sort(key=lambda r: r.priority, reverse=True)
        return recommendations[:5]  # Top 5 plays

    def _score_play(
        self,
        play: _PlayDefinition,
        state: ConversationState,
        sentiment: float,
        momentum: float,
        risk: float,
        arbitrage_types: list[str],
    ) -> float:
        """Score how appropriate a play is for the current situation (0-1)."""
        score = 1.0

        # Phase alignment (hard requirement)
        if state.phase not in play.phases:
            return 0.0

        # Sentiment alignment
        if sentiment < play.min_sentiment or sentiment > play.max_sentiment:
            return 0.0

        # Momentum alignment
        if momentum < play.min_momentum or momentum > play.max_momentum:
            return 0.0

        # Risk threshold
        if risk > play.max_risk:
            score *= 0.3  # Heavily penalize but don't eliminate

        # Arbitrage requirement
        if play.requires_arbitrage:
            if play.requires_arbitrage in arbitrage_types:
                score *= 1.5  # Big bonus for matching arbitrage
            else:
                score *= 0.2  # Big penalty if required arbitrage is missing

        # Phase bonus (later phases = more valuable plays)
        phase_bonuses = {
            ConversationPhase.NEGOTIATION: 1.3,
            ConversationPhase.CLOSING: 1.2,
            ConversationPhase.ENGAGEMENT: 1.0,
            ConversationPhase.DISCOVERY: 0.9,
            ConversationPhase.OPENING: 0.8,
            ConversationPhase.POST_CLOSE: 1.1,
        }
        score *= phase_bonuses.get(state.phase, 1.0)

        # Yield impact weighting
        score *= min(1.5, play.base_yield_impact / 25.0)

        return min(1.0, score)

    def get_recommended_tone(
        self,
        plays: list[PlayRecommendation],
    ) -> str:
        """Determine the recommended tone based on top plays."""
        if not plays:
            return "professional"

        # Use the tone from the top play's definition
        top_play_name = plays[0].name
        for play in self._playbook:
            if play.name == top_play_name:
                return play.tone

        return "professional"
