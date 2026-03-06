#!/usr/bin/env python3
"""
Alibaba Cloud Bailian Qwen TTS with Voice/Mood Presets
Uses official DashScope SDK for WebSocket TTS
"""

import os
import sys
import json
import base64
import threading
import time
import tempfile
import subprocess

# Try to import DashScope SDK
try:
    import dashscope.audio.qwen_tts_realtime as qwen_tts
    DASHSCOPE_SDK = True
except ImportError:
    DASHSCOPE_SDK = False
    print("Warning: dashscope SDK not installed")

USE_MP3 = os.environ.get('BAILIAN_MP3', 'false').lower() == 'true'
VOICE = os.environ.get('BAILIAN_VOICE', 'Maia')  # Default voice

# Voice Name Aliases (Normalize to API-compatible names)
# API requires 'Ono Anna' with space
VOICE_ALIASES = {
    'OnoAnna': 'Ono Anna',
    'onoanna': 'Ono Anna',
}

# ============ Mood Settings ============
MOOD_SETTINGS = {
    # Basic Moods
    'gentle': (
        'Low pitch, slow speed (0.85x), soft round sweet voice,'
        'Natural short pauses and slight breathing,'
        'Soothing and steady tone, emotion: gentle/healing'
    ),
    'whisper': (
        'Breathy voice, low pitch, slow speed (0.8x),'
        'Soft delicate voice, obvious breath and mouth sounds,'
        'Like whispering in ear, emotion: intimate/gentle'
    ),
    'cute': (
        'High pitch, slow speed (0.8x), soft round sweet voice,'
        'Ends with natural rising tone, occasional coquettish hum,'
        'Lively and playful tone, emotion: cute/dependent'
    ),
    'shy': (
        'Medium-low pitch, slow speed (0.75x), soft trembling voice,'
        'Obvious hesitant pauses and soft fillers like "um", "that...",'
        'Slight swallowing sound, emotion: shy/nervous'
    ),
    'worried': (
        'Medium pitch with nervous rise, slightly fast (1.1x) and hurried,'
        'Voice slightly trembling with uneasy breath,'
        'Short sharp inhales between sentences, emotion: anxious/worried'
    ),
    'happy': (
        'Bright high pitch, slightly fast (1.1x) but clear, crisp energetic voice,'
        'Rising tone with joy, voice carries unconcealable smile,'
        'Occasional light laughter, emotion: cheerful/excited'
    ),
    'sleepy': (
        'Low pitch, very slow speed (0.7x), hoarse lazy voice with nasal sound,'
        'Long breathing sounds and slight yawning feel,'
        'Slightly slurred pronunciation, emotion: sleepy/lazy'
    ),
    'working': (
        'Medium steady pitch, moderate speed (1.0x), clear pronunciation,'
        'Efficient organized voice, steady professional but gentle tone,'
        'Appropriate pauses, emotion: serious/focused'
    ),
    'explain': (
        'Medium pitch, moderate-slow speed (0.9x), clear articulation,'
        'Intonation varies to emphasize key points,'
        'Pauses at keywords for thinking time, emotion: patient/kind'
    ),
    'sad': (
        'Low pitch, slow speed (0.75x), deep voice with nasal sound,'
        'Suppressed crying tone and slight sniffling,'
        'Volume fades at end like holding back tears, emotion: wronged/sad'
    ),
    'pouty': (
        'High pitch with sulkiness, slightly fast (1.1x), crisp dissatisfied voice,'
        'Ends with light hum or pouty breath,'
        'Tone obviously pretending to be angry, emotion: pouty/coquettish'
    ),
    'comfort': (
        'Low warm pitch, slow speed (0.85x), soft magnetic voice,'
        'Gentle but firm tone conveying safety,'
        'Soft sighs of empathy between sentences, emotion: caring/comforting'
    ),
    
    'annoyed': (
        'Slightly raised pitch with impatience, slightly fast (1.1x), crisp stiff voice,'
        'Obvious rapid breathing, tone holds suppressed anger,'
        'Emotion: annoyed/impatient'
    ),
    'angry': (
        'High powerful pitch, fast (1.2x) and urgent, sharp tense voice,'
        'Tough tone with obvious anger, stressed keywords,'
        'Forceful downward intonation at end, emotion: angry'
    ),
    'furious': (
        'Extremely high pitch near roaring, very fast (1.3x), oppressive,'
        'Trembling voice with extreme rage, heavy rapid breathing,'
        'Explosive tone allowing no doubt, emotion: furious'
    ),
    'disgusted': (
        'Cold sharp pitch, slow speed (0.9x) with obvious drawl,'
        'Filled with physiological disgust, frowning tone,'
        'Ends with scornful snort or impatient sigh, emotion: disgusted/scornful'
    ),
    
    # Interactive Moods
    'curious': (
        'High pitch with rising doubt, slightly fast (1.15x), bright crisp voice,'
        'Rising tone at end with inquiry,'
        'Voice holds expectation and curiosity, emotion: excited/curious'
    ),
    'surprised': (
        'Pitch suddenly rises then falls, contrast of fast (1.2x) then slow (0.8x),'
        'Crisp voice with obvious surprise and exclamation,'
        'Short gasp at start, emotion: shocked/surprised'
    ),
    'jealous': (
        'Medium-low pitch with unhappiness, slow speed (0.85x),'
        'Voice slightly nasal with faint grumbling,'
        'Sour tone trying to hide it, emotion: wrong/jealous'
    ),
    'teasing': (
        'High pitch with pride, moderate speed (1.0x), crisp voice,'
        'Voice full of unconcealed smile and playfulness,'
        'Often ends with light laughter, emotion: playful/teasing'
    ),
    'begging': (
        'Low pitch with pitiful feel, slow speed (0.8x), soft sweet voice,'
        'Tone drops naturally at end, prolonged with slight trembling,'
        'Mix of pleading and coquetry, emotion: pitiful/begging'
    ),
    'grateful': (
        'Medium-low pitch, slow speed (0.85x), warm sincere magnetic voice,'
        'Sincere tone with slight trembling to express emotion,'
        'Voice wet with gratitude, emotion: sincere thanks'
    ),
    'storytelling': (
        'Pitch varies with story plot, moderate speed (0.95x) with rhythm,'
        'Expressive voice, rhythmic intonation,'
        'Appropriate pauses at cliffhangers, suitable for audiobooks'
    ),
    'gaming': (
        'High pitch, tense, fast speed (1.25x), crisp powerful voice,'
        'Compact and urgent tone with excitement,'
        'Almost no pauses between sentences, emotion: nervous/excited'
    ),
    
    # Special States
    'daydream': (
        'Low pitch, very slow (0.65x), airy dreamy voice,'
        'Ethereal tone like mind wandering,'
        'Long pauses and thoughtful sighs, emotion: daydreaming/absent-minded'
    ),
    'nervous': (
        'Unstable pitch, fast (1.2x) and irregular speed,'
        'Trembling voice with obvious stuttering and repetition,'
        'Nervous swallowing and rapid breathing, emotion: nervous/panicked'
    ),
    'determined': (
        'Medium firm pitch, moderate speed (1.0x),'
        'Soft but undeniable strength,'
        'Steady and powerful tone, emotion: brave/determined'
    ),
    'longing': (
        'Low pitch, very slow (0.7x), soft voice with sighs,'
        'Long lingering tone with longing aftertaste,'
        'Faint sighs at end of sentences, emotion: lonely/longing'
    ),
    'confession': (
        'Medium pitch, slow speed (0.75x) with hesitant pauses,'
        'Slightly trembling voice expressing nervousness,'
        'Deep breath before speaking truth, emotion: sincere confession'
    ),
    'possessive': (
        'Low magnetic pitch, slow speed (0.85x),'
        'Oppressive and possessive urgency,'
        'Firm tone accepting no refusal, emotion: possessive/obsessive'
    ),
    'submissive': (
        'Very low pitch almost whispering, slow speed (0.8x),'
        'Soft yielding voice with submissive breath,'
        'Gentle and dependent tone, no resistance, emotion: submissive'
    ),
    
    # Roleplay
    'maid': (
        'Medium sweet pitch, moderate speed (1.0x), polite crisp voice,'
        'Respectful and enthusiastic tone with professional service feel,'
        'Occasional shy whisper, emotion: respectful/maid'
    ),
    'nurse': (
        'Low gentle pitch, slow speed (0.85x), patient voice,'
        'Caring and professional soothing tone,'
        'Safe and comforting feeling, emotion: caring/nurse'
    ),
    'student': (
        'High pitch with youthful energy, slightly fast (1.05x),'
        'Crisp voice with innocence and vitality,'
        'Lively and cheerful tone, emotion: youthful student'
    ),
    'ojousama': (
        'Medium-high pitch with noble tone, slow speed (0.85x),'
        'Elegant and round voice with arrogant air,'
        'Reserved and proud but occasionally cute, emotion: arrogant/ojousama'
    ),
    'yandere': (
        'Unstable pitch between sweet and low (0.8-1.2x), irregular speed,'
        'Voice shifts between sweet and dark/eerie,'
        'Obsessive and paranoid, smile with madness, emotion: yandere'
    ),
    'tsundere': (
        'High pitch with angry tone, slightly fast (1.1x),'
        'Cold tone but hiding concern/warmth,'
        'Stubborn but soft-hearted, emotion: tsundere (hot-cold)'
    ),
    
    # Voice Effects
    'asmr': (
        'Breathy voice, very low pitch, extremely slow (0.6x),'
        'Extremely soft whisper, almost audible only to ears,'
        'Clear breath and mouth sounds, emotion: intimate/soothing'
    ),
    'singing': (
        'Melodic pitch changes, moderate speed (1.0x) with rhythm,'
        'Round and clear voice with singing quality,'
        'Musical and pleasant tone, emotion: cheerful/humming'
    ),
    'counting': (
        'Low pitch, very slow speed (0.55x), regular rhythm,'
        'Soft and hypnotic voice, clear pause after each number,'
        'Monotonous and repetitive tone for calming effect, emotion: calm/soothing'
    ),
}

# ============ Mood Keywords ============
MOOD_KEYWORDS = {
    # Basic
    'whisper': ['whisper', 'secret', 'shh', 'quiet', 'softly'],
    'cute': ['please', 'yay', 'cute', 'darling', 'honey'],
    'shy': ['um...', 'uh...', 'sorry', 'shy', 'blush'],
    'worried': ['worry', 'scared', 'afraid', 'oh no', 'okay?'],
    'happy': ['happy', 'yay', 'great', 'wonderful', 'haha'],
    'working': ['code', 'bug', 'fix', 'check', 'solve'],
    'explain': ['because', 'therefore', 'explain', 'meaning', 'concept'],
    'sad': ['sad', 'cry', 'tears', 'upset', 'sorry'],
    'pouty': ['hmph', 'fine', 'whatever', 'humph', 'mean'],
    'comfort': ['don\'t cry', 'it\'s okay', 'there there', 'hug', 'safe'],
    
    'annoyed': ['annoyed', 'stop', 'enough', 'geez', 'ugh'],
    'angry': ['angry', 'mad', 'furious', 'hate', 'shut up'],
    'furious': ['unforgivable', 'kill', 'die', 'bastard', 'how dare'],
    'disgusted': ['disgusting', 'gross', 'yuck', 'eww', 'filthy'],
    
    # Interactive
    'curious': ['why', 'what', 'how', 'really?', 'curious'],
    'surprised': ['wow', 'what?!', 'omg', 'really?!', 'impossible'],
    'jealous': ['jealous', 'who is she', 'why her', 'hmph', 'mine'],
    'teasing': ['hehe', 'kidding', 'joke', 'silly', 'cute'],
    'begging': ['please', 'beg', 'master', 'please please', 'want'],
    'grateful': ['thank you', 'thanks', 'grateful', 'appreciate', 'glad'],
    'storytelling': ['once upon a time', 'story', 'long ago', 'legend', 'chapter'],
    'gaming': ['game', 'win', 'lose', 'play', 'gg'],
    
    # Special States
    'daydream': ['dream', 'wonder', 'maybe', 'if only', 'cloud'],
    'nervous': ['nervous', 'scared', 'panic', 'what if', 'shaking'],
    'determined': ['will', 'must', 'determined', 'fight', 'goal'],
    'longing': ['miss you', 'long for', 'wish', 'far away', 'remember'],
    'confession': ['love you', 'like you', 'crush', 'heart', 'confess'],
    'possessive': ['mine', 'only mine', 'belong', 'never', 'stay'],
    'submissive': ['yes master', 'obey', 'anything', 'punish', 'serve'],
    
    # Roleplay
    'maid': ['master', 'welcome home', 'service', 'tea', 'cleaning'],
    'nurse': ['doctor', 'patient', 'medicine', 'sick', 'relax'],
    'student': ['teacher', 'class', 'homework', 'study', 'exam'],
    'ojousama': ['peasant', 'how dare', 'noble', 'elegant', 'ohoho'],
    'yandere': ['forever', 'never leave', 'love me', 'blood'],
    'tsundere': ['baka', 'idiot', 'not like I', 'hmph', 'stupid'],
    
    # Voice Effects
    'asmr': ['asmr', 'whisper', 'tingles', 'soft', 'ear'],
    'singing': ['la la la', 'sing', 'song', 'melody', 'hum'],
    'counting': ['one', 'two', 'three', 'count', 'sheep'],
}

import re

# ============ Language Validation ============
def validate_language(text, lang):
    """
    Ensures that the input text contains characters relevant to the specified language.
    This prevents the AI from passing raw Chinese text when it intends to speak a foreign language.
    Strategy: INCLUSIVE check (must contain at least one characteristic character).
    """
    if lang == 'Auto' or lang == 'Chinese':
        return True
        
    # Japanese: Must contain Hiragana or Katakana
    if lang == 'Japanese':
        if not re.search(r'[\u3040-\u30ff]', text):
            print(f"[ERROR] Language '{lang}' requires Hiragana/Katakana, but none found!")
            print(f"Current Text: {text[:50]}...")
            print("[ACTION REQUIRED] Please TRANSLATE the text to Japanese internally, then RE-RUN the command with the translated text.")
            return False

    # Korean: Must contain Hangul
    elif lang == 'Korean':
        if not re.search(r'[\uac00-\ud7af]', text):
            print(f"[ERROR] Language '{lang}' requires Hangul, but none found!")
            print("[ACTION REQUIRED] Please TRANSLATE the text to Korean internally, then RE-RUN the command.")
            return False
            
    # Russian: Must contain Cyrillic
    elif lang == 'Russian':
        if not re.search(r'[\u0400-\u04ff]', text):
            print(f"[ERROR] Language '{lang}' requires Cyrillic, but none found!")
            print("[ACTION REQUIRED] Please TRANSLATE the text to Russian internally, then RE-RUN the command.")
            return False
            
    # Latin Languages (English, French, German, etc.)
    elif lang in ['English', 'French', 'German', 'Italian', 'Spanish', 'Portuguese']:
        # Must contain at least one Latin letter
        if not re.search(r'[a-zA-Z]', text):
            print(f"[ERROR] Language '{lang}' requires Latin letters, but none found!")
            print(f"[ACTION REQUIRED] Please TRANSLATE the text to {lang} internally, then RE-RUN the command.")
            return False
            
    return True

# ============ Smart Mood Selection ============
def select_mood(text):
    for mood, keywords in MOOD_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in text.lower():
                print(f"[Smart Mood] Keyword '{kw}' → {mood}")
                return mood
    print("[Smart Mood] No match → gentle (default)")
    return 'gentle'

# ============ WebSocket TTS ============
def tts_websocket(model, output_file, text, mood='gentle', audio_format='mp3', language_type='Auto'):
    if not DASHSCOPE_SDK:
        print("Error: dashscope SDK not installed")
        return False
    
    api_key = os.environ.get('DASHSCOPE_API_KEY', '')
    if not api_key:
        print("Error: DASHSCOPE_API_KEY not set")
        return False
    
    instructions = MOOD_SETTINGS.get(mood, MOOD_SETTINGS['gentle'])
    
    # Flash Realtime model does NOT support Instructions (Mood/Pitch/Speed)
    if model == 'qwen3-tts-flash-realtime':
        instructions = None
    
    pcm_file = tempfile.mktemp(suffix='.pcm')
    audio_data = bytearray()
    
    class MyCallback(qwen_tts.QwenTtsRealtimeCallback):
        def __init__(self):
            self.audio_data = bytearray()
            self.complete_event = threading.Event()
        def on_open(self):
            print("Connected!")
        def on_event(self, message):
            msg_type = message.get('type', '')
            if msg_type == 'response.audio.delta':
                audio_b64 = message.get('delta', '')
                if audio_b64:
                    self.audio_data.extend(base64.b64decode(audio_b64))
            elif msg_type == 'response.audio.done':
                print(f"Done! Audio: {len(self.audio_data)} bytes")
            elif msg_type == 'session.finished':
                print("Session finished")
                self.complete_event.set()
        def on_close(self, code, reason):
            print(f"Closed: {code}")
        def wait_for_finished(self):
            self.complete_event.wait()
    
    callback = MyCallback()
    
    try:
        # Support custom URL for international regions (e.g. Singapore)
        # Default: Beijing (wss://dashscope.aliyuncs.com/api-ws/v1/realtime)

        # For International Region (Singapore), use:
        # export DASHSCOPE_URL="wss://dashscope-intl.aliyuncs.com/api-ws/v1/realtime"
        custom_url = os.environ.get('DASHSCOPE_URL', None)
        
        # Initialize TTS with optional custom URL
        if custom_url:
            tts = qwen_tts.QwenTtsRealtime(model=model, callback=callback, url=custom_url)
        else:
            tts = qwen_tts.QwenTtsRealtime(model=model, callback=callback)
            
        tts.connect()
        
        # Select output format based on audio_format
        # Supports: pcm, wav, mp3 (default), opus (Telegram)
        sample_rate = 48000 if audio_format == 'opus' else 24000
        
        tts.update_session(
            voice=VOICE,
            instructions=instructions,
            audio_format=audio_format,
            sample_rate=sample_rate,
            language_type=language_type,
            mode='server_commit'
        )
        
        tts.append_text(text)
        # server_commit mode: no need to call commit()
        tts.finish()
        
        callback.wait_for_finished()  # 等待session.finished事件
        tts.close()
        
        if callback.audio_data:
            # Write directly to file, API returns correct format, no ffmpeg needed
            with open(output_file, 'wb') as f:
                f.write(callback.audio_data)
            
            print(f"Success: {output_file}")
            return True
        else:
            print("No audio data received")
            return False
            
    except Exception as e:
        print(f"WebSocket Error: {e}")
        return False

# ============ Main ============
def main():
    global VOICE
    text = ''
    mood = ''
    output = 'tts_output.mp3'
    audio_format = 'mp3'  # Default mp3
    language_type = 'Auto'  # Default Auto
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ['--voice', '-v'] and i + 1 < len(sys.argv):
            VOICE = sys.argv[i + 1]
            # Normalize voice name (e.g., OnoAnna -> Ono Anna)
            VOICE = VOICE_ALIASES.get(VOICE, VOICE)
            i += 2
        elif arg in ['--mood', '-m'] and i + 1 < len(sys.argv):
            mood = sys.argv[i + 1]
            i += 2
        elif arg in ['--output', '-o'] and i + 1 < len(sys.argv):
            output = sys.argv[i + 1]
            i += 2
        elif arg in ['--format', '-f'] and i + 1 < len(sys.argv):
            audio_format = sys.argv[i + 1].lower()
            if audio_format not in ['pcm', 'wav', 'mp3', 'opus']:
                print(f"Error: Unsupported format '{audio_format}'. Use: pcm, wav, mp3, opus")
                return
            i += 2
        elif arg in ['--language', '-l'] and i + 1 < len(sys.argv):
            language_type = sys.argv[i + 1]
            i += 2
        elif arg == '--telegram':
            audio_format = 'opus'  # Telegram Voice Shortcut
            i += 1
        else:
            text = sys.argv[i]
            i += 1
    
    if not text:
        print("Usage: tts.py [--voice NAME] [--mood MOOD] [-o FILE] [--format FMT] [--language LANG] \"Text\"")
        print("Formats: pcm, wav, mp3 (default), opus (Telegram)")
        print("Moods:", ', '.join(MOOD_SETTINGS.keys()))
        return
    
    if not mood:
        mood = 'gentle'  # Default gentle
        
    # Language Validation
    if not validate_language(text, language_type):
        print("[WARNING] Language check failed, but proceeding anyway to avoid blocking execution...")
        # sys.exit(1)  <-- Disabled to prevent AI retry loops
    
    print(f"[Mood] {mood} | [Format] {audio_format} | [Lang] {language_type}")
    
    # Model Selection Strategy
    # Default to the Instruct model which supports Mood/Speed/Pitch
    model_name = 'qwen3-tts-instruct-flash-realtime' 
    
    # List of voices that are ONLY supported by the non-instruct model 'qwen3-tts-flash-realtime'
    # These voices do NOT support Mood/Speed/Pitch instructions.
    VOICES_WITHOUT_INSTRUCT = [
        'Jennifer', 'Katerina', 'Sonrisa', 'Sohee', 'OnoAnna', 'Ono Anna',
        'Jada', 'Sunny', 'Kiki'
    ]
    
    if VOICE in VOICES_WITHOUT_INSTRUCT:
        print(f"[Model Switch] Voice '{VOICE}' is exclusive to 'qwen3-tts-flash-realtime'")
        model_name = 'qwen3-tts-flash-realtime'
        
        if mood != 'gentle' and mood != '':
             print(f"[WARNING] Voice '{VOICE}' does NOT support Mood Instructions. Your mood '{mood}' will be IGNORED.")
    
    # CosyVoice check (Optional enhancement for future)
    # if VOICE.startswith('Long'): model_name = 'cosyvoice-v1'
    
    if tts_websocket(model_name, output, text, mood, audio_format, language_type):
        print(f"TTS saved: {output}")
    else:
        print("Error: TTS failed")
        sys.exit(1)

if __name__ == '__main__':
    main()
