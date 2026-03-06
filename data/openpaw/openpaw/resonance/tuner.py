"""
Response Tuner.

Takes frequency profile + signals and generates specific, actionable
recommendations for how the bot should adjust its next response.

This is the money-making layer — it turns abstract frequencies into
concrete guidance that directly improves conversion and engagement.
"""

from __future__ import annotations

from openpaw.models.metrics import (
    ActionTiming,
    FrequencyProfile,
    ResponseStyle,
    TuningRecommendation,
    UrgencyLevel,
)
from openpaw.resonance.signals import ConversationSignals


class ResponseTuner:
    """Generates response tuning recommendations from frequencies + signals."""

    def tune(
        self,
        profile: FrequencyProfile,
        signals: ConversationSignals,
    ) -> TuningRecommendation:

        style = self._determine_style(profile, signals)
        timing = self._determine_timing(profile, signals)
        urgency = self._determine_urgency(profile, signals)

        rec = TuningRecommendation(
            style=style,
            timing=timing,
            urgency=urgency,
        )

        self._set_length(rec, profile, signals)
        self._set_techniques(rec, profile, signals)
        self._set_objection_handling(rec, signals)
        self._set_confidence(rec, profile)
        self._generate_action(rec, profile, signals)

        return rec

    def _determine_style(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> ResponseStyle:
        if signals.mirror_behavior > 0.6:
            return ResponseStyle.AMPLIFY
        if profile.trust < 0.3:
            return ResponseStyle.MIRROR
        if profile.decision > 0.7 and profile.trust > 0.5:
            return ResponseStyle.AMPLIFY
        if signals.volatility > 0.6:
            return ResponseStyle.SOFTEN
        if profile.engagement < 0.3:
            return ResponseStyle.REDIRECT
        return ResponseStyle.MIRROR

    def _determine_timing(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> ActionTiming:
        if profile.decision >= 0.7 and profile.trust >= 0.5:
            return ActionTiming.NOW
        if profile.decision >= 0.5 and signals.commitment_language > 0.3:
            return ActionTiming.NEXT_TURN
        if profile.engagement >= 0.4 and profile.trust >= 0.3:
            return ActionTiming.BUILD_MORE
        return ActionTiming.NOT_READY

    def _determine_urgency(
        self, profile: FrequencyProfile, signals: ConversationSignals
    ) -> UrgencyLevel:
        # Critical: user showing strong intent but might leave
        if (
            signals.commitment_language > 0.4
            and signals.message_length_trajectory < -0.3
        ):
            return UrgencyLevel.CRITICAL

        # High: strong engagement, approaching decision
        if profile.composite >= 0.6:
            return UrgencyLevel.HIGH

        # Low: user not engaged
        if profile.engagement < 0.3:
            return UrgencyLevel.LOW

        return UrgencyLevel.MEDIUM

    def _set_length(
        self,
        rec: TuningRecommendation,
        profile: FrequencyProfile,
        signals: ConversationSignals,
    ) -> None:
        if signals.response_elaboration < 0.2:
            rec.recommended_length = "very_short"
        elif signals.response_elaboration < 0.4:
            rec.recommended_length = "short"
        elif profile.engagement > 0.7 and signals.question_density > 0.3:
            rec.recommended_length = "long"
        else:
            rec.recommended_length = "medium"

    def _set_techniques(
        self,
        rec: TuningRecommendation,
        profile: FrequencyProfile,
        signals: ConversationSignals,
    ) -> None:
        # Mirror when building trust
        rec.mirror_language = profile.trust < 0.5

        # Questions when engagement is medium (not too many, not too few)
        rec.use_questions = 0.3 <= profile.engagement <= 0.7

        # Empathy when sentiment is dropping
        rec.use_empathy = signals.positive_sentiment_trend < -0.2

        # Social proof when trust is medium but decision is pending
        rec.use_social_proof = (
            0.3 <= profile.trust <= 0.7 and profile.decision >= 0.3
        )

        # Scarcity only when very close to decision and trust is high
        rec.use_scarcity = profile.decision >= 0.6 and profile.trust >= 0.6

    def _set_objection_handling(
        self,
        rec: TuningRecommendation,
        signals: ConversationSignals,
    ) -> None:
        if signals.objection_frequency > 0.3:
            if signals.hedge_ratio > 0.3:
                rec.address_objection = (
                    "User is uncertain — provide reassurance and specifics"
                )
            else:
                rec.address_objection = (
                    "User has concrete concerns — address directly with evidence"
                )

    def _set_confidence(
        self, rec: TuningRecommendation, profile: FrequencyProfile
    ) -> None:
        if profile.trust >= 0.6 and profile.decision >= 0.5:
            rec.confidence_level = "authoritative"
        elif profile.trust < 0.3:
            rec.confidence_level = "humble"
        else:
            rec.confidence_level = "balanced"

    def _generate_action(
        self,
        rec: TuningRecommendation,
        profile: FrequencyProfile,
        signals: ConversationSignals,
    ) -> None:
        level = profile.resonance_level

        if level == "PEAK_RESONANCE":
            rec.action = (
                "User is at peak resonance — present the offer/solution now. "
                "They are primed to commit."
            )
            rec.reasoning = (
                "All frequencies are aligned: high engagement, high trust, "
                "high decision readiness. This is the optimal moment."
            )

        elif level == "HIGH_RESONANCE":
            if profile.decision > profile.trust:
                rec.action = (
                    "User wants to decide but needs more trust. "
                    "Provide social proof or a guarantee."
                )
                rec.reasoning = (
                    "Decision frequency exceeds trust — bridge the gap "
                    "with credibility signals."
                )
            else:
                rec.action = (
                    "User trusts you but hasn't crystallized their decision. "
                    "Help them envision the outcome."
                )
                rec.reasoning = (
                    "Trust exceeds decision readiness — paint the picture "
                    "of what success looks like."
                )

        elif level == "BUILDING":
            if signals.objection_frequency > 0.3:
                rec.action = (
                    "User is engaged but has concerns. "
                    "Acknowledge objections, then redirect to value."
                )
                rec.reasoning = (
                    "Engagement is building but objections are present. "
                    "Don't push — address concerns first."
                )
            else:
                rec.action = (
                    "Momentum is building. Keep the conversation flowing. "
                    "Ask a focused question to deepen engagement."
                )
                rec.reasoning = (
                    "Frequencies are developing positively. "
                    "Continue building rapport and understanding."
                )

        elif level == "WEAK":
            rec.action = (
                "User is not yet engaged. Change approach — try a different "
                "angle, ask about their specific situation, or offer "
                "something unexpected."
            )
            rec.reasoning = (
                "Low resonance across all frequencies. "
                "Current approach isn't connecting. Pivot."
            )

        else:  # NO_RESONANCE
            rec.action = (
                "No resonance detected. Reset the conversation. "
                "Ask an open-ended question about what matters most to them."
            )
            rec.reasoning = (
                "No conversational signal detected. "
                "Either just started or completely disconnected."
            )
