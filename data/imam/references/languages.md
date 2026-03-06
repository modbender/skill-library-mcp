# Multi-Language Support

Arabic recitations are ALWAYS in Arabic regardless of language setting.  
Language preference applies to: instructions, translations, announcements, and khutbah body.

## Default TTS: Google Cloud Text-to-Speech
Free tier: **1 million WaveNet characters/month** — sufficient for all 5 daily prayers + khutbah.

## Voice Map per Language

| Code | Language   | Google Cloud Voice         | Speaking Rate | Notes                              |
|------|------------|----------------------------|---------------|------------------------------------||
| ar   | Arabic     | ar-XA-Wavenet-B            | 0.85          | Deep male, best for prayer/khutbah |
| en   | English    | en-US-Wavenet-D            | 0.90          | Calm authoritative male            |
| ur   | Urdu       | ur-IN-Wavenet-B            | 0.88          | Male Urdu voice                    |
| fr   | French     | fr-FR-Wavenet-D            | 0.90          | Male French voice                  |
| tr   | Turkish    | tr-TR-Wavenet-B            | 0.90          | Male Turkish voice                 |
| id   | Indonesian | id-ID-Wavenet-B            | 0.90          | Male Indonesian voice              |
| ms   | Malay      | ms-MY-Wavenet-B            | 0.90          | Male Malay voice                   |
| bn   | Bengali    | bn-IN-Wavenet-B            | 0.90          | Male Bengali voice                 |

## SSML Tips for Arabic Recitation
Use SSML tags for more natural Quranic pacing:
```xml
<speak>
  <prosody rate="slow" pitch="-2st">
    <lang xml:lang="ar-XA">
      Allahu Akbar
    </lang>
  </prosody>
  <break time="2s"/>
  <prosody rate="slow" pitch="-2st">
    <lang xml:lang="ar-XA">
      Bismillahir Rahmanir Rahim
    </lang>
  </prosody>
</speak>
```

## Language Setting Commands
- User says: "Switch to Urdu" → set lang=ur, switch voice to ur-IN-Wavenet-B
- User says: "Use English" → set lang=en, switch voice to en-US-Wavenet-D
- Arabic recitation voice always stays ar-XA-Wavenet-B regardless of instruction language
- Default: English (en) instructions + Arabic (ar) recitation if not set

## Fallback Voice Options (if Google Cloud unavailable)

| Provider      | Arabic Voice          | Free Limit                  |
|---------------|-----------------------|-----------------------------|
| Puter.js      | ar (Polly engine)     | Unlimited (no key needed)   |
| Amazon Polly  | Zeina (ar)            | 5M chars/month (12 months)  |
| Azure Speech  | ar-SA-HamedNeural     | 500K chars/month            |
| gTTS (Python) | ar                    | Unlimited (unofficial)      |

## gTTS Quick Fallback (Python, no API key)
```python
from gtts import gTTS
import os

def speak(text, lang='ar'):
    tts = gTTS(text=text, lang=lang, slow=True)
    tts.save('/tmp/imam_tts.mp3')
    os.system('mpg321 /tmp/imam_tts.mp3')  # or: afplay / vlc

speak('Allahu Akbar')  # plays audio immediately
```
Install: `pip install gTTS mpg321`
