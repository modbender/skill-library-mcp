# Usage Examples

## Example 1: Simple Greeting

**Command:**
```bash
python3 skills/zvukogram/scripts/tts.py \
  --text "Привет, Сергей! Как дела?" \
  --voice Алена \
  --output hello.mp3
```

## Example 2: News Voiceover

**Text (news.txt):**
```
Компания Оупен Эй Ай представила новую модель Джи Пи Ти 5.
Сэм Ал+ьтман заявил о прорыве в области искусственного интеллекта.
```

**Command:**
```bash
python3 skills/zvukogram/scripts/tts.py \
  --file news.txt \
  --voice Алена \
  --speed 1.1 \
  --output news.mp3
```

## Example 3: Dialog (Podcast)

**Dialog script (dialog.txt):**
```
[Алена|1.2] Доброе утро! Это подкаст Эй Ай Дейли.
[Андрей|1.2] Привет! Рад быть в эфире.
[Алена|1.2] Начнём с главных новостей.
[Андрей|1.2] В мире ИИ сегодня много интересного.
```

**Generation script:**
```bash
#!/bin/bash
TMP_DIR="/tmp/podcast_$(date +%s)"
mkdir -p $TMP_DIR

# Read dialog and generate fragments
while IFS= read -r line; do
    if [[ $line =~ ^\[(.+)\|(.+)\]\ (.+)$ ]]; then
        voice="${BASH_REMATCH[1]}"
        speed="${BASH_REMATCH[2]}"
        text="${BASH_REMATCH[3]}"
        
        python3 skills/zvukogram/scripts/tts.py \
          --text "$text" \
          --voice "$voice" \
          --speed "$speed" \
          --output "$TMP_DIR/$(date +%s%N).mp3"
    fi
done < dialog.txt

# Merge
python3 skills/zvukogram/scripts/merge.py \
  $TMP_DIR/*.mp3 \
  --output podcast.mp3

# Cleanup
rm -rf $TMP_DIR
```

## Example 4: Voice Notification

```bash
python3 skills/zvukogram/scripts/tts.py \
  --text "Напоминание: встреча через 15 минут" \
  --voice Алена \
  --speed 1.1 \
  --output reminder.mp3
```

## Example 5: Long Text

For texts longer than 1000 characters, use splitting:

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, 'skills/zvukogram/scripts')
from tts import generate_tts, download_audio, load_config

def split_text(text, max_len=900):
    """Split text by sentences"""
    sentences = text.replace('! ', '!|').replace('? ', '?|').replace('. ', '.|').split('|')
    parts = []
    current = ""
    
    for sent in sentences:
        if len(current) + len(sent) < max_len:
            current += sent + " "
        else:
            parts.append(current.strip())
            current = sent + " "
    
    if current:
        parts.append(current.strip())
    
    return parts

# Load text
with open('long_document.txt') as f:
    text = f.read()

# Split and generate
config = load_config()
parts = split_text(text)
files = []

for i, part in enumerate(parts):
    print(f"Генерация части {i+1}/{len(parts)}...")
    url = generate_tts(part, "Алена", config["token"], config["email"], 1.0, "mp3")
    if url:
        filename = f"/tmp/part_{i:03d}.mp3"
        download_audio(url, filename)
        files.append(filename)

# Merge
import subprocess
with open('/tmp/merge_list.txt', 'w') as f:
    for file in files:
        f.write(f"file '{file}'\n")

subprocess.run([
    'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
    '-i', '/tmp/merge_list.txt', '-acodec', 'copy',
    'audiobook.mp3'
])
```

## Example 6: SSML with Stress

**SSML text:**
```xml
<speak>
  В слове "з+амок" ударение падает на первый слог,
  а в слове "зам+ок" — на второй.
  
  <break time="500ms"/>
  
  Компания <sub alias="Оупен Эй Ай">OpenAI</sub>
  выпустила новую версию <sub alias="Джи Пи Ти">GPT</sub>.
</speak>
```

**Note:** SSML via API has limited support. For full support use Zvukogram web interface.

## Example 7: Daily Podcast Automation

```bash
#!/bin/bash
# daily_podcast.sh

TOKEN="your_token"
EMAIL="your_email"
DATE=$(date +%Y-%m-%d)
OUTPUT="podcast_${DATE}.mp3"

# Generate parts
curl -s -X POST "https://zvukogram.com/index.php?r=api/text" \
  -d "token=$TOKEN" -d "email=$EMAIL" \
  -d "voice=Алена" -d "speed=1.2" \
  -d "text=Доброе утро! Новости ИИ на $(date +%d.%m.%Y)" \
  -d "format=mp3" | jq -r '.file' | xargs curl -s -L -o /tmp/p1.mp3

# ... more parts ...

# Merge
ffmpeg -y -i "concat:/tmp/p1.mp3|/tmp/p2.mp3|/tmp/p3.mp3" \
  -acodec copy "$OUTPUT"

echo "Done: $OUTPUT"
```
