# Building a Whole-House Announcement System with AirPlay, Airfoil, and ElevenLabs

My house is full of AirPlay speakers — HomePods in the living room, kitchen, kids' rooms, office, even the wellness area. Apple's Intercom feature lets me broadcast my voice to all of them, which is handy. But what if I want to send *arbitrary* audio? A text-to-speech announcement with a nice voice? A chime before the message? Intercom can't do that.

So I built [Announcer](https://github.com/odrobnik/announcer-skill), an [OpenClaw](https://openclaw.ai) skill that beams a 4-tone gong followed by a custom TTS announcement to every speaker in the house simultaneously.

It sounds simple. It wasn't.

## The AirPlay Quirks

The core idea is straightforward: generate speech audio, pipe it through [Airfoil](https://rogueamoeba.com/airfoil/) (Rogue Amoeba's excellent AirPlay routing app), and play it on all speakers. But AirPlay has opinions.

**Speakers need time to wake up.** AirPlay speakers — especially HomePods that have been idle — don't connect instantly. You can't just fire audio and hope for the best. The script had to learn patience: connect to all configured speakers, then poll their connection status until every single one reports back as online. I settled on a 30-second timeout with per-second status checks. Most speakers connect within 5-10 seconds, but some sleepy ones need the full window.

**You have to wait for the audio to finish.** This sounds obvious, but when you're controlling Airfoil programmatically via AppleScript and playing audio through `afplay`, you need to make sure you don't disconnect the speakers before the AirPlay buffer has flushed. A premature disconnect means the last second of your announcement gets swallowed. I added a 3-second grace period after playback before tearing down the connections.

**AirPlay demands stereo.** This one caught me off guard. ElevenLabs generates mono audio by default — perfectly fine for headphones or a single speaker. But AirPlay silently refuses to play mono files on some speakers, or plays them at reduced volume on others. The fix? ffmpeg to the rescue:

```bash
ffmpeg -y -i input.opus -ac 2 -ar 48000 -c:a libmp3lame -b:a 256k output.mp3
```

That `-ac 2` flag converts mono to stereo, and while we're at it, we upsample to 48kHz at 256kbps for clean AirPlay-quality audio.

## The ElevenLabs Skill

The voice generation comes from another skill I just published: [ElevenLabs](https://github.com/odrobnik/elevenlabs-skill). It's a Python toolkit that wraps the ElevenLabs API into a set of focused command-line tools:

- **`speech.py`** — Text-to-speech with any ElevenLabs voice, supporting all output formats from low-bitrate MP3 to high-quality Opus
- **`sfx.py`** — Sound effect generation from text prompts ("cinematic boom", "rain on a window"), with loop support
- **`music.py`** — Full music generation for intros, background beds, and transitions
- **`voices.py`** — List and manage your voice library
- **`voiceclone.py`** — Instant voice cloning from audio samples, with noise removal
- **`quota.py`** — Monitor your subscription usage with a visual progress bar

Each tool is self-contained, takes standard CLI arguments, and outputs to a file. This makes them easy to compose — which is exactly what the Announcer skill does, calling `speech.py` to generate the announcement audio before routing it through Airfoil.

## The Bigger Picture: ClawdCast

Both of these skills feed into a larger project I'm working on: **ClawdCast**, a podcast production studio powered by AI. The idea is to produce full audio podcasts with AI-generated dialogue, music, and sound effects — complete with timeline editing, mixing, and video rendering.

ClawdCast uses the ElevenLabs skill for voice synthesis (multiple characters with distinct voices), music generation (intro jingles, background beds), and sound effects (transitions, ambient audio). It's still a work in progress, but the foundation is solid: the same battle-tested audio pipeline that makes house announcements sound good also makes podcast episodes sound professional.

## Try It

Both skills are available on [ClawHub](https://clawhub.com) and GitHub:

- **Announcer**: [GitHub](https://github.com/odrobnik/announcer-skill) · [ClawHub](https://www.clawhub.com/skills/announcer)
- **ElevenLabs**: [GitHub](https://github.com/odrobnik/elevenlabs-skill) · [ClawHub](https://www.clawhub.com/skills/elevenlabs)

You'll need [Airfoil](https://rogueamoeba.com/airfoil/) for the speaker routing, an [ElevenLabs](https://elevenlabs.io) API key for the voice generation, and [OpenClaw](https://openclaw.ai) to tie it all together.

Now if you'll excuse me, I need to announce that dinner is ready. In style. 📢
