"""
Micro-Conversion Tracker — Find hidden money in every message.

Most bots think in terms of ONE big conversion: sale, signup, ticket resolved.
But between "hello" and "purchase complete," there are DOZENS of micro-moments
where a bot can extract measurable value.

Each micro-conversion has a real dollar value:
    - Email capture:          $2-5 (remarketing asset)
    - Preference reveal:      $0.50-1 (personalization data)
    - Need statement:         $1-3 (qualification data)
    - Competitor mention:     $3-5 (competitive intelligence)
    - Budget reveal:          $5-10 (qualification gold)
    - Timeline reveal:        $2-4 (urgency signal)
    - Referral mention:       $5-15 (viral coefficient)
    - Feature request:        $1-2 (product intelligence)
    - Pain point articulation: $3-5 (marketing copy gold)

This engine detects these micro-conversions in real-time and tells the bot
exactly how to CAPTURE the value.

Zero external dependencies. Pure pattern matching.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from convoyield.models.conversation import ConversationState, Speaker
from convoyield.models.yield_result import MicroConversion


@dataclass
class _MicroConversionPattern:
    type: str
    patterns: list[str]
    value_range: tuple[float, float]  # (min, max) dollar value
    capture_prompt: str
    category: str  # "data", "intent", "social", "qualification"


_MICRO_PATTERNS = [
    # ── Data Capture Opportunities ──────────────────────────────────────
    _MicroConversionPattern(
        type="email_capture_opportunity",
        patterns=[
            r"\b(send|email|inbox|notify|alert|update)\b",
            r"\b(keep me (posted|updated|informed))\b",
            r"\b(let me know)\b",
        ],
        value_range=(2.0, 5.0),
        capture_prompt="I'd love to keep you updated! What's the best email to reach you at?",
        category="data",
    ),
    _MicroConversionPattern(
        type="phone_capture_opportunity",
        patterns=[
            r"\b(call me|phone|text me|sms|whatsapp)\b",
            r"\b(prefer (to talk|calling|a call))\b",
        ],
        value_range=(3.0, 7.0),
        capture_prompt="Absolutely, a quick call would be great! What's the best number to reach you?",
        category="data",
    ),
    _MicroConversionPattern(
        type="name_capture_opportunity",
        patterns=[
            r"\b(my name is|i'm |i am |call me )\b",
            r"\b(this is \w+)\b",
        ],
        value_range=(0.5, 1.0),
        capture_prompt="[Personalize all future messages with their name — increases conversion 26%]",
        category="data",
    ),

    # ── Intent / Qualification Signals ──────────────────────────────────
    _MicroConversionPattern(
        type="budget_reveal",
        patterns=[
            r"\$\d+",
            r"\b\d+k\b",
            r"\b(budget|spend|invest|allocat)\w*\s.{0,15}\d",
            r"\b(willing to (pay|spend))\b",
            r"\b(price range|budget range)\b",
        ],
        value_range=(5.0, 10.0),
        capture_prompt="[Tag user with budget tier. Route to appropriate offer. This is qualification GOLD.]",
        category="qualification",
    ),
    _MicroConversionPattern(
        type="timeline_reveal",
        patterns=[
            r"\b(by (next|this) (week|month|quarter|year))\b",
            r"\b(need.{0,10}(today|tomorrow|asap|soon|quickly))\b",
            r"\b(deadline|due date|time frame|timeline)\b",
            r"\b(start(ing)? (next|this|in))\b",
            r"\b(how (soon|fast|quickly))\b",
        ],
        value_range=(2.0, 4.0),
        capture_prompt="Let me make sure we hit your timeline. When exactly do you need this by?",
        category="qualification",
    ),
    _MicroConversionPattern(
        type="team_size_reveal",
        patterns=[
            r"\b(\d+\s*(people|users|seats|licenses|team members|employees))\b",
            r"\b(my team|our team|our company|our org)\b",
            r"\b(small business|enterprise|startup|mid-size)\b",
        ],
        value_range=(3.0, 8.0),
        capture_prompt="[Size the deal. Route to SMB or Enterprise path. Adjust pricing presentation.]",
        category="qualification",
    ),
    _MicroConversionPattern(
        type="need_statement",
        patterns=[
            r"\b(i need|we need|looking for|searching for|want to)\b",
            r"\b(trying to (find|solve|fix|build|create|improve))\b",
            r"\b(problem (is|with)|issue (is|with)|challenge)\b",
            r"\b(wish (i|we) (could|had))\b",
        ],
        value_range=(1.0, 3.0),
        capture_prompt="I hear you. Let me make sure I understand exactly what you need so I can point you to the perfect solution.",
        category="qualification",
    ),

    # ── Competitive Intelligence ────────────────────────────────────────
    _MicroConversionPattern(
        type="competitor_mention",
        patterns=[
            r"\b(currently using|use|tried|switched from|compared to)\b",
            r"\b(competitor|alternative|other (tool|service|platform|app))\b",
            r"\b(vs|versus|compared|better than|worse than)\b",
        ],
        value_range=(3.0, 5.0),
        capture_prompt="[Log competitive intel. This data feeds product strategy and marketing positioning. Worth its weight in gold.]",
        category="intent",
    ),

    # ── Social / Viral Signals ──────────────────────────────────────────
    _MicroConversionPattern(
        type="referral_opportunity",
        patterns=[
            r"\b(friend|colleague|coworker|boss|team|partner)\b.{0,20}\b(told|mentioned|recommended|suggested)\b",
            r"\b(recommend|refer|tell (my|a) friend)\b",
            r"\b(share|sharing) (this|it) with\b",
        ],
        value_range=(5.0, 15.0),
        capture_prompt="That's wonderful to hear! Would you like a referral link? You and your friend both get [reward].",
        category="social",
    ),
    _MicroConversionPattern(
        type="testimonial_opportunity",
        patterns=[
            r"\b(love|amazing|perfect|best|incredible|game.?changer)\b.{0,20}\b(product|service|tool|app|platform)\b",
            r"\b(saved (me|us|my)|changed (my|our))\b",
            r"\b(can't live without|wouldn't go back)\b",
        ],
        value_range=(3.0, 8.0),
        capture_prompt="That means so much to us! Would you mind if we featured your experience? Happy users like you help others find us.",
        category="social",
    ),

    # ── Product Intelligence ────────────────────────────────────────────
    _MicroConversionPattern(
        type="feature_request",
        patterns=[
            r"\b(wish (it|you|this) (could|would|had))\b",
            r"\b(would be (nice|great|cool|helpful) if)\b",
            r"\b(can you|do you|does it) (support|handle|do)\b",
            r"\b(missing|lacking|need.{0,10}feature)\b",
        ],
        value_range=(1.0, 2.0),
        capture_prompt="Great suggestion! I'll make sure our product team sees this. Would you like to be notified when we ship it?",
        category="intent",
    ),
    _MicroConversionPattern(
        type="pain_point_articulation",
        patterns=[
            r"\b(biggest (problem|challenge|pain|issue|frustration))\b",
            r"\b(struggle|struggling) (with|to)\b",
            r"\b(keeps? (happening|breaking|failing))\b",
            r"\b(every (time|day|week) i have to)\b",
        ],
        value_range=(3.0, 5.0),
        capture_prompt="[This is marketing gold. The user's exact words describe their pain in language that resonates with similar prospects. Log verbatim for ad copy and landing pages.]",
        category="intent",
    ),
]


class MicroConversionTracker:
    """
    Detects and values micro-conversion opportunities in real-time.

    Every message is scanned for dozens of value-extraction moments.
    The tracker tells the bot exactly what value is available and how to capture it.
    """

    def __init__(self):
        self._compiled = [
            (p, [re.compile(r, re.IGNORECASE) for r in p.patterns])
            for p in _MICRO_PATTERNS
        ]

    def scan(self, state: ConversationState) -> list[MicroConversion]:
        """
        Scan the latest user message for micro-conversion opportunities.

        Returns a list of MicroConversion objects, sorted by value (highest first).
        """
        last_user = state.last_user_turn
        if not last_user:
            return []

        text = last_user.text
        conversions = []
        already_captured = set(state.micro_conversions_captured)

        for pattern_def, compiled_regexes in self._compiled:
            match_count = 0
            trigger = ""

            for regex in compiled_regexes:
                m = regex.search(text)
                if m:
                    match_count += 1
                    if not trigger:
                        trigger = m.group(0)

            if match_count == 0:
                continue

            # Value scales with match confidence
            confidence = min(1.0, match_count * 0.35)
            min_val, max_val = pattern_def.value_range
            estimated_value = min_val + (max_val - min_val) * confidence

            # Engagement multiplier — more invested users = higher value data
            engagement_mult = min(1.5, 1.0 + (state.turn_count * 0.05))
            estimated_value *= engagement_mult

            # Check if already captured
            captured = pattern_def.type in already_captured

            conversions.append(MicroConversion(
                type=pattern_def.type,
                value=round(estimated_value, 2),
                captured=captured,
                trigger_text=trigger,
                capture_prompt=pattern_def.capture_prompt,
            ))

        conversions.sort(key=lambda c: c.value, reverse=True)
        return conversions

    def mark_captured(self, state: ConversationState, conversion_type: str):
        """Mark a micro-conversion as successfully captured."""
        if conversion_type not in state.micro_conversions_captured:
            state.micro_conversions_captured.append(conversion_type)

    @staticmethod
    def total_available_value(conversions: list[MicroConversion]) -> float:
        return sum(c.value for c in conversions if not c.captured)

    @staticmethod
    def total_captured_value(conversions: list[MicroConversion]) -> float:
        return sum(c.value for c in conversions if c.captured)
