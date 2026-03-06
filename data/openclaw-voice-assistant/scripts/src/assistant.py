"""OpenClaw Voice Assistant — main entry point.

Always-on voice assistant that connects to an OpenClaw gateway.
Listens for a wake word, transcribes speech, sends to the AI, and speaks the response.
After speaking, listens for a follow-up to enable natural back-and-forth.

Mic suppression prevents the mic from hearing its own speaker output.
"""

import asyncio
import logging
import sys
import threading
import time
from pathlib import Path

# Add src to path so imports work when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from audio_pipeline import (
    AudioPipeline,
    play_chime,
    play_thinking,
    stop_thinking,
    suppress_mic,
    unsuppress_mic,
    transcribe,
)
from gateway_client import GatewayClient
import tts_player

log = logging.getLogger("assistant")

# State
_pipeline: AudioPipeline | None = None
_gateway: GatewayClient | None = None
_loop: asyncio.AbstractEventLoop | None = None
_running = True
_paused = False
_in_conversation = False

# Timing
FOLLOW_UP_WINDOW = 5.0    # seconds to wait for follow-up after response
POST_SPEECH_PAUSE = 0.8   # breathing room after TTS before listening


def _on_wake(follow_up: bool = False):
    """Called when wake word is detected, hotkey pressed, or after TTS finishes."""
    global _in_conversation
    if _paused or not _running:
        return

    if follow_up:
        log.info("Listening for follow-up...")
        # Soft chime for follow-up — mic suppressed so it won't hear itself
        play_chime()
    else:
        log.info("Activated! Listening for command...")
        _in_conversation = True
        # Chime plays with mic suppressed internally
        play_chime()

    # Start recording (mic is unsuppressed now — chime is done)
    _pipeline.start_recording()

    # Wait for silence
    timeout = FOLLOW_UP_WINDOW if follow_up else 15.0
    got_silence = _pipeline.wait_for_silence(timeout=timeout)

    if not got_silence:
        if follow_up:
            _pipeline.stop_recording()
            _in_conversation = False
            log.info("Conversation ended (no follow-up)")
            return
        log.warning("Recording timeout — no silence detected")

    # Get recorded audio
    audio = _pipeline.stop_recording()
    if audio is None or len(audio) < 1600:
        if follow_up:
            _in_conversation = False
            log.debug("No audio in follow-up, back to idle")
        return

    # Transcribe
    text = transcribe(audio)
    if not text or len(text.strip()) < 2:
        if follow_up:
            _in_conversation = False
        return

    log.info("You said: %s", text)

    # Play thinking sound (mic suppressed during playback, then unsuppressed)
    play_thinking()

    # Send to gateway and speak response
    if _loop:
        asyncio.run_coroutine_threadsafe(_send_and_speak(text), _loop)


async def _send_and_speak(text: str):
    """Send text to gateway, collect response, speak it, then listen for follow-up."""
    global _in_conversation
    try:
        full_response = ""
        async for chunk in _gateway.send_message(text):
            full_response = chunk

        # Stop thinking sound
        stop_thinking()

        if full_response:
            log.info("Assistant: %s", full_response[:200])

            def _speak_then_listen():
                # Suppress mic during TTS so it doesn't hear itself
                suppress_mic()
                try:
                    tts_player.speak(full_response)
                finally:
                    time.sleep(0.15)
                    unsuppress_mic()

                # Breathing room — clear separation between response and listen
                time.sleep(POST_SPEECH_PAUSE)

                # Listen for follow-up
                _on_wake(follow_up=True)

            threading.Thread(target=_speak_then_listen, daemon=True).start()
        else:
            _in_conversation = False
            log.warning("Empty response from gateway")

    except Exception as e:
        stop_thinking()
        _in_conversation = False
        log.error("Error communicating with gateway: %s", e)


def _setup_hotkey():
    """Register global hotkey as alternative to wake word."""
    try:
        from pynput.keyboard import GlobalHotKeys

        parts = config.HOTKEY.split("+")
        combo_parts = []
        for p in parts:
            p = p.strip().lower()
            if p in ("ctrl", "control"):
                combo_parts.append("<ctrl>")
            elif p in ("shift",):
                combo_parts.append("<shift>")
            elif p in ("alt",):
                combo_parts.append("<alt>")
            elif p in ("cmd", "win", "super"):
                combo_parts.append("<cmd>")
            else:
                combo_parts.append(p)
        combo = "+".join(combo_parts)

        def on_hotkey():
            log.info("Hotkey pressed!")
            threading.Thread(target=_on_wake, daemon=True).start()

        hotkeys = GlobalHotKeys({combo: on_hotkey})
        hotkeys.daemon = True
        hotkeys.start()
        log.info("Global hotkey registered: %s", config.HOTKEY)
    except Exception as e:
        log.warning("Could not register hotkey: %s", e)


def _run_tray():
    """Run system tray icon (blocks on main thread)."""
    try:
        import pystray
        from PIL import Image

        icon_path = config.ASSETS_DIR / "icon.png"
        if icon_path.exists():
            image = Image.open(icon_path)
        else:
            image = Image.new("RGB", (64, 64), color=(0, 180, 120))

        def on_pause(icon, item):
            global _paused
            _paused = not _paused
            if _paused:
                _pipeline.pause()
                log.info("Paused")
            else:
                _pipeline.resume()
                log.info("Resumed")

        def on_quit(icon, item):
            global _running
            _running = False
            icon.stop()
            log.info("Quitting...")

        menu = pystray.Menu(
            pystray.MenuItem(
                lambda item: "Resume" if _paused else "Pause",
                on_pause,
            ),
            pystray.MenuItem("Quit", on_quit),
        )

        icon = pystray.Icon("openclaw-voice", image, "OpenClaw Voice", menu)
        icon.run()

    except ImportError:
        log.warning("pystray not available — running without tray icon")
        try:
            while _running:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            pass


async def _async_main():
    """Async main: connect to gateway, start audio pipeline."""
    global _gateway, _pipeline, _loop
    _loop = asyncio.get_event_loop()

    _gateway = GatewayClient()
    try:
        await _gateway.connect()
    except Exception as e:
        log.error("Failed to connect to gateway: %s", e)
        log.error("Make sure OpenClaw is running and GATEWAY_TOKEN is set in .env")
        return

    _pipeline = AudioPipeline()

    if not config.PORCUPINE_ACCESS_KEY:
        log.error(
            "PORCUPINE_ACCESS_KEY not set in .env. "
            "Sign up free at https://picovoice.ai to get one."
        )
        await _gateway.disconnect()
        return

    try:
        _pipeline.start(on_wake=_on_wake)
    except Exception as e:
        log.error("Failed to start audio pipeline: %s", e)
        log.error("Check your Porcupine access key and mic permissions.")
        await _gateway.disconnect()
        return

    _setup_hotkey()
    log.info("Voice assistant ready! Say your wake word or press %s", config.HOTKEY)

    while _running:
        await asyncio.sleep(1)

    _pipeline.stop()
    await _gateway.disconnect()


def main():
    """Entry point."""
    global _running

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    log.info("OpenClaw Voice Assistant starting...")

    def run_async():
        asyncio.run(_async_main())

    async_thread = threading.Thread(target=run_async, daemon=True)
    async_thread.start()

    time.sleep(2)

    if not _running:
        return

    _run_tray()

    _running = False
    async_thread.join(timeout=5)
    log.info("Goodbye!")


if __name__ == "__main__":
    main()
