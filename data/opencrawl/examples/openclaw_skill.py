#!/usr/bin/env python3
"""
ConvoYield as an OpenClaw Skill — Drop-in integration.

This example shows how to wrap ConvoYield as an OpenClaw/MoltBot skill
that any bot operator can install and immediately start extracting
maximum value from every conversation.

The skill hooks into OpenClaw's message pipeline and enriches every
response with yield-optimized strategic guidance.
"""

# This is a reference implementation for OpenClaw skill integration.
# Adapt the hook points to match your specific bot framework.

from convoyield import ConvoYield


class ConvoYieldSkill:
    """
    OpenClaw-compatible skill wrapper for ConvoYield.

    Integrates with any message-based bot framework by providing:
    1. Pre-response analysis (what should the bot do?)
    2. Post-response tracking (how did it go?)
    3. Live dashboard data (what's the conversation worth?)
    """

    def __init__(self, base_value: float = 25.0):
        # One engine per conversation session
        self._sessions: dict[str, ConvoYield] = {}
        self._base_value = base_value

    def get_engine(self, session_id: str) -> ConvoYield:
        """Get or create a ConvoYield engine for a conversation session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ConvoYield(
                base_conversation_value=self._base_value
            )
        return self._sessions[session_id]

    def on_user_message(self, session_id: str, text: str) -> dict:
        """
        Hook: Called when a user message is received.

        Returns strategic guidance for the bot's response.
        """
        engine = self.get_engine(session_id)
        result = engine.process_user_message(text)

        # Return actionable guidance for the bot
        guidance = {
            "play": result.recommended_play,
            "tone": result.recommended_tone,
            "length": result.optimal_response_length,
            "urgency": result.urgency,
            "estimated_value": result.estimated_yield,
            "risk": result.risk_level,
            "phase": result.phase,
        }

        # Add execution hints from top play
        if result.recommended_plays:
            guidance["hints"] = result.recommended_plays[0].execution_hints

        # Add arbitrage alerts
        if result.arbitrage_opportunities:
            top = result.top_arbitrage
            guidance["arbitrage_alert"] = {
                "type": top.type,
                "value": top.estimated_value,
                "action": top.recommended_action,
                "window_seconds": top.window_seconds,
            }

        # Add uncaptured micro-conversion prompts
        uncaptured = result.uncaptured_micro_conversions
        if uncaptured:
            guidance["capture_opportunities"] = [
                {"type": mc.type, "value": mc.value, "prompt": mc.capture_prompt}
                for mc in uncaptured[:3]
            ]

        return guidance

    def on_bot_response(self, session_id: str, text: str):
        """Hook: Called after the bot sends its response."""
        engine = self.get_engine(session_id)
        engine.record_bot_response(text)

    def on_conversion(self, session_id: str, conversion_type: str, value: float = None):
        """Hook: Called when a micro-conversion is captured."""
        engine = self.get_engine(session_id)
        engine.mark_conversion(conversion_type, value)

    def get_dashboard(self, session_id: str) -> dict:
        """Get the live dashboard for a conversation."""
        engine = self.get_engine(session_id)
        return engine.get_dashboard()

    def end_session(self, session_id: str) -> dict:
        """End a conversation session and return final stats."""
        if session_id in self._sessions:
            engine = self._sessions[session_id]
            dashboard = engine.get_dashboard()
            del self._sessions[session_id]
            return dashboard
        return {}


# ── Example: Discord Bot Integration ─────────────────────────────────────────

DISCORD_EXAMPLE = """
# Discord integration example (pseudocode):

import discord
from convoyield_skill import ConvoYieldSkill

skill = ConvoYieldSkill(base_value=30.0)
client = discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return

    session_id = str(message.channel.id)

    # Get ConvoYield guidance BEFORE generating response
    guidance = skill.on_user_message(session_id, message.content)

    # Use guidance to shape your bot's response
    # guidance["play"] tells you WHAT strategy to use
    # guidance["tone"] tells you HOW to say it
    # guidance["hints"] tells you specific tactics

    response = generate_response(message.content, guidance)

    await message.channel.send(response)
    skill.on_bot_response(session_id, response)
"""

# ── Example: Telegram Bot Integration ────────────────────────────────────────

TELEGRAM_EXAMPLE = """
# Telegram integration example (pseudocode):

from telegram.ext import Application, MessageHandler, filters
from convoyield_skill import ConvoYieldSkill

skill = ConvoYieldSkill(base_value=25.0)

async def handle_message(update, context):
    session_id = str(update.effective_chat.id)
    text = update.message.text

    guidance = skill.on_user_message(session_id, text)

    # The guidance dict now contains everything your bot needs:
    # - What play to run
    # - What tone to use
    # - Any arbitrage opportunities to exploit
    # - Micro-conversions to capture
    # - Risk level and urgency

    response = your_bot_logic(text, guidance)
    await update.message.reply_text(response)
    skill.on_bot_response(session_id, response)
"""


def demo():
    """Run a quick demo of the skill."""
    skill = ConvoYieldSkill(base_value=50.0)
    session = "demo-001"

    messages = [
        "I need help choosing a CRM for my 50-person sales team",
        "We're currently using HubSpot but it's way too expensive for what we get",
        "Our budget is around $5000/month. Need something by end of quarter",
        "That sounds perfect! Can you email me the proposal?",
    ]

    for msg in messages:
        print(f"\nUser: {msg}")
        guidance = skill.on_user_message(session, msg)
        print(f"  Play: {guidance['play']} | Tone: {guidance['tone']} | Value: ${guidance['estimated_value']:.2f}")

        if "arbitrage_alert" in guidance:
            alert = guidance["arbitrage_alert"]
            print(f"  ★ ARBITRAGE: {alert['type']} (${alert['value']:.2f})")

        if "capture_opportunities" in guidance:
            for opp in guidance["capture_opportunities"]:
                print(f"  ○ Capture: {opp['type']} (${opp['value']:.2f})")

        # Simulate bot response
        skill.on_bot_response(session, f"[Bot responds to: {msg[:30]}...]")

    print(f"\nFinal Dashboard: {skill.get_dashboard(session)}")


if __name__ == "__main__":
    demo()
