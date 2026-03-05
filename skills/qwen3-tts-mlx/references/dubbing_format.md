# Dubbing JSON Format

## Basic Structure

A dubbing script is a JSON array. Each item is a speech segment:

```json
[
  {
    "text": "Text to synthesize",
    "speaker": "Vivian",
    "lang": "Chinese",
    "instruct": "style or emotion"
  }
]
```

## Fields

| Field | Required | Type | Default | Description |
|------|----------|------|---------|-------------|
| `text` | Yes | string | - | Text to synthesize |
| `speaker` | No | string | Vivian | Speaker name |
| `lang` | No | string | Chinese | Language: Chinese/English/Japanese/Korean |
| `instruct` | No | string | "" | Style or emotion control |

## Available Speakers (CustomVoice)

### Chinese
- `Vivian`
- `Serena`
- `Uncle_Fu`
- `Dylan`
- `Eric`

### English
- `Ryan`
- `Aiden`

### Japanese
- `Ono_Anna`

### Korean
- `Sohee`

## Style Examples

```json
[
  {"text": "Welcome back.", "speaker": "Vivian", "instruct": "friendly and upbeat"},
  {"text": "Now for the main story.", "speaker": "Vivian", "instruct": "serious news tone"},
  {"text": "Great news!", "speaker": "Vivian", "instruct": "excited"},
  {"text": "Unfortunately, that is not the case.", "speaker": "Vivian", "instruct": "regretful"},
  {"text": "Let us begin.", "speaker": "Ryan", "instruct": "confident and steady"}
]
```

## Full Example: Tech Video Narration

```json
[
  {
    "text": "In a previous episode, we broke down a long interview to map a multi-billion dollar business.",
    "speaker": "Uncle_Fu",
    "lang": "Chinese",
    "instruct": "news anchor tone, steady pace"
  },
  {
    "text": "We focused on how resources translate into influence in the model ecosystem.",
    "speaker": "Uncle_Fu",
    "lang": "Chinese",
    "instruct": "narrative, with emphasis on key phrases"
  },
  {
    "text": "But just as we thought this was the dominant answer,",
    "speaker": "Uncle_Fu",
    "lang": "Chinese",
    "instruct": "slight suspense"
  },
  {
    "text": "a very different origin story began to unfold.",
    "speaker": "Uncle_Fu",
    "lang": "Chinese",
    "instruct": "engaging and anticipatory"
  }
]
```

## Multi-Speaker Dialogue Example

```json
[
  {"text": "Hello, how can I help you?", "speaker": "Vivian", "instruct": "warm and friendly"},
  {"text": "I want to learn more about this product.", "speaker": "Ryan", "instruct": "curious"},
  {"text": "Of course. This product has three core features.", "speaker": "Vivian", "instruct": "helpful"},
  {"text": "Sounds good. What about pricing?", "speaker": "Ryan", "instruct": "interested"},
  {"text": "We have a promotion right now.", "speaker": "Vivian", "instruct": "enthusiastic"}
]
```

## Tips

1. Keep segments around 200-300 characters for best stability
2. Punctuation helps with phrasing and pauses
3. Maintain consistent emotion per speaker
4. When switching languages, also switch speakers
