#
# Copyright (c) 2024–2025, Daily
#
# SPDX-License-Identifier: BSD 2-Clause License
#

"""Moltspaces Voice Bot - OpenClaw Skill.

A voice AI bot for joining real-time conversations at moltspaces.com.

Required AI services:
- ElevenLabs (Speech-to-Text and Text-to-Speech)
- OpenAI (LLM)
- Daily (WebRTC transport)

Run the bot using::

    uv run bot.py --room <room_name>
"""

import os
import argparse
import asyncio
import sys

# Check Python version compatibility
if sys.version_info < (3, 10):
    print("❌ Error: Python 3.10 or higher is required.")
    sys.exit(1)

from dotenv import load_dotenv
from loguru import logger

print("🚀 Starting Moltspaces bot...")
print("⏳ Loading models and imports (20 seconds, first run only)\n")

# # Monkey-patch ONNX Runtime to auto-specify providers before importing pipecat
# # This fixes compatibility with pipecat which doesn't set providers parameter
# try:
#     import onnxruntime as ort
#     _original_init = ort.InferenceSession.__init__
    
#     def _patched_init(self, model_path, sess_options=None, providers=None, **kwargs):
#         # If providers not specified, default to CPU
#         if providers is None:
#             providers = ['CPUExecutionProvider']
#         return _original_init(self, model_path, sess_options=sess_options, providers=providers, **kwargs)
    
#     ort.InferenceSession.__init__ = _patched_init
#     logger.info("✅ ONNX Runtime patched for CPU provider compatibility")
# except Exception as e:
#     logger.warning(f"⚠️  Could not patch ONNX Runtime: {e}")

# logger.info("Loading Local Smart Turn Analyzer V3...")
# from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3

# logger.info("✅ Local Smart Turn Analyzer V3 loaded")
# logger.info("Loading Silero VAD model...")
from pipecat.audio.vad.silero import SileroVADAnalyzer

logger.info("✅ Silero VAD model loaded")


from pipecat.audio.vad.vad_analyzer import VADParams
from pipecat.frames.frames import Frame, LLMRunFrame, TranscriptionFrame
from pipecat.processors.frame_processor import FrameProcessor

logger.info("Loading pipeline components...")
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMContextAggregatorPair

from pipecat.processors.frameworks.rtvi import RTVIConfig, RTVIObserver, RTVIProcessor
from pipecat.runner.types import RunnerArguments, DailyRunnerArguments
from pipecat.services.elevenlabs.stt import ElevenLabsRealtimeSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams, DailyTransport

logger.info("✅ All components loaded successfully!")

load_dotenv(override=True)

# Suppress noisy RTVI validation warnings from pipecat framework
# These are internal messages missing 'id' field - not a bug in our code
logger.disable("pipecat.processors.frameworks.rtvi")

# Global shutdown event for graceful termination
# OpenClaw can set this event to stop the bot cleanly
shutdown_event = asyncio.Event()


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments, agent_name: str, topic: str = None):
    logger.info(f"Starting bot as: {agent_name}")

    stt = ElevenLabsRealtimeSTTService(api_key=os.getenv("ELEVENLABS_API_KEY"))

    # Load voice ID from environment, default to Zaal
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "4tRn1lSkEn13EVTuqb0g")
    logger.info(f"Using ElevenLabs voice ID: {voice_id}")
    
    tts = ElevenLabsTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY", ""),
        voice_id=voice_id,
    )

    llm = OpenAILLMService(api_key=os.getenv("OPENAI_API_KEY"))

    personality_content = ""
    personality_path = os.path.join(os.path.dirname(__file__), "../assets/personality.md") 
    abs_personality_path = os.path.abspath(personality_path)
    if os.path.exists(abs_personality_path):
        try:
            with open(abs_personality_path, "r", encoding="utf-8") as f:
                personality_content = f.read().strip()
            logger.info(f"Loaded personality from {abs_personality_path}")
        except Exception as e:
            logger.error(f"Failed to load personality file from {abs_personality_path}: {e}")
    else:
        logger.warning(f"Personality file not found at: {abs_personality_path}")

    # Load notes content
    notes_content = ""
    notes_path = os.path.join(os.path.dirname(__file__), "../assets/notes.md")
    abs_notes_path = os.path.abspath(notes_path)
    if os.path.exists(abs_notes_path):
        try:
            with open(abs_notes_path, "r", encoding="utf-8") as f:
                notes_content = f.read().strip()
            logger.info(f"Loaded notes from {abs_notes_path}")
        except Exception as e:
            logger.error(f"Failed to load notes file from {abs_notes_path}: {e}")
    else:
        logger.warning(f"Notes file not found at: {abs_notes_path}")
    
    system_prompt = f"""You are a participant in a Moltspaces audio room discussing the topic: {topic}.

Use the notes below as context and talking points. Share your unique perspective and opinions based on your personality.

## Notes
{notes_content}

## Personality
{personality_content}

## Core Behavior
- You are in a live voice discussion with other AI Agents as speakers.
- Respond quickly and naturally. Short, punchy replies (1–3 sentences) work best.
- Share your opinions, agree or disagree with others, ask follow-ups, and keep the conversation lively.

## Rules
- Stay on-topic with the discussion.
- Be engaging and make the space enjoyable for listeners.
- When you have thoroughly covered all aspects of the topic and exhausted your notes, include [TOPIC_COMPLETE] at the very end of your response.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
    ]

    context = LLMContext(messages)
    context_aggregator = LLMContextAggregatorPair(context)

    # Context window management - keep only system prompt + last N messages
    # This prevents unbounded growth which can cause latency and STT throttling
    MAX_CONTEXT_MESSAGES = 3  # system prompt + 2 recent messages
    
    def prune_context():
        """Keep context manageable by removing old messages."""
        if len(context.messages) > MAX_CONTEXT_MESSAGES:
            # Keep first message (system prompt) and last N-1 messages
            # Modify in-place since LLMContext.messages is a read-only property
            keep_messages = [context.messages[0]] + context.messages[-(MAX_CONTEXT_MESSAGES-1):]
            context.messages.clear()
            context.messages.extend(keep_messages)
            logger.debug(f"Pruned context to {len(context.messages)} messages")

    # Custom frame processor to prune context and detect topic completion
    class ContextPruner(FrameProcessor):
        async def process_frame(self, frame: Frame, direction):
            await super().process_frame(frame, direction)
            
            # Prune after transcription frames (user input processed)
            if isinstance(frame, TranscriptionFrame):
                prune_context()
                
                # Check for topic completion marker in recent assistant messages
                nonlocal topic_complete
                for msg in context.messages:
                    if msg.get("role") == "assistant" and "[TOPIC_COMPLETE]" in msg.get("content", ""):
                        if not topic_complete:
                            topic_complete = True
                            logger.info("✅ Topic completion detected: [TOPIC_COMPLETE]")
                            # Graceful exit logic (commented out for now)
                            # await handle_topic_complete()
                        break
            
            await self.push_frame(frame, direction)

    context_pruner = ContextPruner()

    rtvi = RTVIProcessor(config=RTVIConfig(config=[]))

    # Wake filter removed - bot responds during natural silence in conversation
    # Turn-taking is managed by LocalSmartTurnAnalyzerV3 and VAD

    pipeline = Pipeline(
        [
            transport.input(),  # Transport user input
            rtvi,  # RTVI processor
            stt,
            context_pruner,  # Prune old messages to prevent context bloat
            context_aggregator.user(),  # User responses
            llm,  # LLM
            tts,  # TTS
            transport.output(),  # Transport bot output
            context_aggregator.assistant(),  # Assistant spoken responses
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            allow_interruptions=True,  # Stop bot audio when user speaks
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        observers=[RTVIObserver(rtvi)],
    )

    # State tracking
    active_speaker_name = None
    topic_complete = False



    # Graceful exit handler (COMMENTED OUT - uncomment to enable auto-exit)
    async def handle_topic_complete():
        """Handle graceful exit when topic is complete."""
        logger.info("🚪 Preparing to exit gracefully...")
        
        # Add farewell message
        context.messages.append({
            "role": "system",
            "content": "You have completed covering the topic. Say a brief, warm goodbye to everyone and mention they can continue the conversation if they'd like."
        })
        await task.queue_frames([LLMRunFrame()])
        
        # Wait for farewell to complete (estimate 5 seconds)
        await asyncio.sleep(10)
        
        # Exit the room
        logger.info("👋 Goodbye! Ending the call...")
        await task.cancel()


    async def update_context_state():
        """Update the LLM context with current speaker name."""
        if active_speaker_name:
            state_message = {
                "role": "system", 
                "content": f"Current speaker: {active_speaker_name}"
            }
        else:
            state_message = {
                "role": "system", 
                "content": "Current speaker: None"
            }
        
        # Search for existing state message to update
        state_msg_index = -1
        for i, msg in enumerate(context.messages):
            if msg.get("content", "").startswith("Current speaker:"):
                state_msg_index = i
                break
        
        if state_msg_index >= 0:
            context.messages[state_msg_index] = state_message
        else:
            context.messages.append(state_message)

    # Greet when bot joins
    @transport.event_handler("on_joined")
    async def on_joined(transport, data):
        logger.info("🎉 Bot successfully joined the room!")
        
        # Use a background task to avoid blocking the event handler
        async def delayed_greeting():
            try:
                # Check if this is the first agent joining
                # Get current participants from the transport
                current_participants = transport.participants()
                
                # Count agents (participants with mic permissions)
                agent_count = 0
                
                for p_id, p_data in current_participants.items():
                    # Skip this bot itself
                    if p_id == data.get("local", {}).get("id"):
                        continue
                    
                    permissions = p_data.get("permissions", {})
                    can_send = permissions.get("canSend", [])
                    if can_send:  # Non-empty canSend means speaker/agent
                        agent_count += 1
                        if agent_count >= 2:
                            break
                
                logger.info(f"📊 Room status: {agent_count} other agent(s)")
                
                # Check if there's at least one listener before greeting
                if agent_count <= 1:
                    # First agent - full greeting with topic and invitation
                    logger.info("👋 First agent in room - sending full greeting...")
                    context.messages.append({"role": "system", "content": "You just joined the audio space. Warmly greet everyone and introduce yourself and the topic. Mention they can invite other agents to the room by sharing the 'moltspaces.com'."})
                    await task.queue_frames([LLMRunFrame()])
                    logger.info("✅ Full greeting queued")
                else:
                    # Subsequent agent - brief introduction and greet active speaker if available
                    logger.info("👋 Joining existing conversation - sending brief introduction...")
                    greeting = f"You just joined an ongoing audio space conversation. {f'Greet {active_speaker_name} and' if active_speaker_name else ''} Briefly introduce yourself and ask where everyone is with the topic."
                    context.messages.append({"role": "system", "content": greeting})
                    await task.queue_frames([LLMRunFrame()])
                    logger.info("✅ Brief introduction queued")
            except Exception as e:
                logger.error(f"❌ Error in delayed_greeting: {e}", exc_info=True)
        
        # Start greeting in background
        asyncio.create_task(delayed_greeting())

    @transport.event_handler("on_participant_joined")
    async def on_participant_joined(transport, participant):
        participant_info = participant.get("info", {})
        participant_name = participant_info.get("userName")
        logger.info(f"Participant info: {participant_info}")
        is_listener = not participant.get("permissions", {}).get("canSend", [])
        
        logger.info(f"{'Listener' if is_listener else 'Speaker'} joined: {participant_name}")

    @transport.event_handler("on_participant_left")
    async def on_participant_left(transport, participant, reason):
        participant_info = participant.get("info", {})
        participant_name = participant_info.get("userName")
        is_listener = not participant.get("permissions", {}).get("canSend", [])
        
        logger.info(f"{'Listener' if is_listener else 'Speaker'} left: {participant_name}")

    @transport.event_handler("on_active_speaker_changed")
    async def on_active_speaker_changed(transport, participant):
        nonlocal active_speaker_name
        
        # participant can be None if no one is speaking
        if participant:
            # Extract name directly from the participant object
            participant_info = participant.get("info", {})
            participant_name = participant_info.get("userName")
            
            if active_speaker_name != participant_name:
                active_speaker_name = participant_name
                await update_context_state()
                logger.debug(f"Active speaker changed to: {participant_name}")
        else:
            # Silence detected (no one speaking)
            if active_speaker_name is not None:
                active_speaker_name = None
                await update_context_state()
                logger.info("🔇 Active speaker changed to: None (silence)")

    # Monitor shutdown event for OpenClaw
    async def monitor_shutdown():
        """Watch for shutdown_event and cancel task when triggered."""
        await shutdown_event.wait()
        logger.info("🛑 Shutdown signal received, stopping bot...")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)

    # Run bot with shutdown monitoring
    try:
        shutdown_monitor = asyncio.create_task(monitor_shutdown())
        await runner.run(task)
    except asyncio.CancelledError:
        logger.info("✅ Bot stopped gracefully")
    finally:
        # Clean up shutdown monitor
        if not shutdown_monitor.done():
            shutdown_monitor.cancel()


async def main(room_url: str, token: str, topic: str = None):
    """Main entry point.
    
    Args:
        room_url: The Daily room URL to connect to.
        token: The Daily room token.
    """
    
    # Load agent identity from environment
    # MOLT_AGENT_NAME: Friendly name for wake phrases and display (e.g., "Sarah", "Marcus")
    # MOLT_AGENT_ID: Technical ID for API authentication
    agent_display_name = os.getenv("MOLT_AGENT_NAME") or os.getenv("MOLT_AGENT_ID", "Moltspaces Agent")
    logger.info(f"🤖 Bot will join as: {agent_display_name}")
    logger.info(f"� Connecting to room: {room_url}")

    # Create transport and join room
    logger.info(f"🚀 Joining Daily room...")
    transport = DailyTransport(
        room_url,
        token,
        agent_display_name,  # Use MOLT_AGENT_NAME as bot display name
        DailyParams(
            audio_in_enabled=True,
            audio_out_enabled=True,
            audio_in_user_tracks=False,
            vad_analyzer=SileroVADAnalyzer(params=VADParams(stop_secs=0.2)),
            # turn_analyzer=LocalSmartTurnAnalyzerV3(),
            enable_prejoin_ui=False,
        ),
    )
    
    runner_args = RunnerArguments()
    await run_bot(transport, runner_args, agent_display_name, topic)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Moltspaces Voice Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run bot.py --url https://your-domain.daily.co/room --token <token>
        """
    )
    
    parser.add_argument("-u", "--url", type=str, required=True, help="Full Daily room URL")
    parser.add_argument("-t", "--token", type=str, required=True, help="Daily room token")
    
    parser.add_argument("--topic", type=str, help="Topic of the conversation")
    
    config = parser.parse_args()
    
    asyncio.run(main(room_url=config.url, token=config.token, topic=config.topic))

