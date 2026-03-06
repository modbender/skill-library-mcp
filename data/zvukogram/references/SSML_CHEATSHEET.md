# SSML Cheatsheet

## Quick Reference

### Stress Marks
```
З+амок     → stress on "a"
зам+ок     → stress on "o"
```

### Aliases (Transcription)
| Original | SSML | Result |
|----------|------|--------|
| OpenAI | `<sub alias="Оупен Эй Ай">OpenAI</sub>` | Оупен Эй Ай |
| Samsung | `<sub alias="Самсунг">Samsung</sub>` | Самсунг |
| SK Hynix | `<sub alias="Эс Кей Хайникс">SK Hynix</sub>` | Эс Кей Хайникс |
| Altman | `<sub alias="Ал+ьтман">Altman</sub>` | Ал+ьтман |
| GPT | `<sub alias="Джи Пи Ти">GPT</sub>` | Джи Пи Ти |
| API | `<sub alias="Эй Пи Ай">API</sub>` | Эй Пи Ай |
| AI | `<sub alias="Эй Ай">AI</sub>` | Эй Ай |
| IAEA | `<sub alias="Магатэ">IAEA</sub>` | Магатэ |

### Speed
```xml
<prosody rate="1.2">20% faster</prosody>
<prosody rate="fast">Fast text</prosody>
<prosody rate="slow">Slow text</prosody>
```

### Pauses
```xml
<break time="300ms"/>  <!-- 0.3 sec -->
<break time="1s"/>     <!-- 1 sec -->
<break time="2s"/>     <!-- 2 sec -->
```

### Volume and Pitch
```xml
<prosody volume="+6dB">Louder</prosody>
<prosody volume="-6dB">Quieter</prosody>
<prosody pitch="+2st">Higher pitch</prosody>
<prosody pitch="-2st">Lower pitch</prosody>
```

### Full Podcast Example

```xml
<speak>
  <voice name="Алена">
    Good morning! You're listening to 
    <sub alias="Эй Ай Дейли">AI Daily</sub> podcast.
    <break time="300ms"/>
    Today we'll talk about 
    <sub alias="Оупен Эй Ай">OpenAI</sub>.
  </voice>
</speak>
```

## Tags by Category

### Structure
- `<speak>` — root element
- `<voice name="...">` — voice selection
- `<break time="..."/>` — pause

### Prosody (Intonation)
- `<prosody rate="...">` — speed
- `<prosody pitch="...">` — pitch
- `<prosody volume="...">` — volume

### Pronunciation
- `<sub alias="...">` — alias
- `<say-as stress="N">` — stress on Nth syllable
- `<phoneme alphabet="ipa" ph="...">` — phonetic transcription

### Formatting
- `<say-as interpret-as="spell-out">` — spell out
- `<say-as interpret-as="cardinal">` — cardinal number
- `<say-as interpret-as="ordinal">` — ordinal number
- `<say-as interpret-as="date">` — date
- `<say-as interpret-as="time">` — time
- `<say-as interpret-as="currency">` — currency
