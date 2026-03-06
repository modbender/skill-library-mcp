# AI-Generated Podcasts

## Overview

Fully synthetic podcasts using AI for scripting and voice synthesis.
Tools: NotebookLM, ElevenLabs, OpenAI TTS, custom workflows.

---

## Script Generation

### From Topics
```
Input: "The psychology of pricing"
Output: 15-minute dialogue between two hosts exploring the topic
```

### From Sources
Feed documents, articles, or URLs → AI generates conversational breakdown.
NotebookLM style: Upload sources, generate "Audio Overview."

### Script Structure
```
HOST_A: [curious] 
Opens with hook question

HOST_B: [knowledgeable]
Provides initial framework

HOST_A: [skeptical]
Pushes back, asks for examples

HOST_B: [storytelling]
Gives concrete case study

[Continue back-and-forth]
```

### Natural Dialogue Elements

Include in scripts:
- **Filler sounds:** "Hmm," "Right," "Oh interesting"
- **Interruptions:** "[cutting in] Wait, but—"
- **Reactions:** "[laughing]" "[surprised]" "[thoughtful pause]"
- **Tangents:** Brief related stories before returning
- **Callbacks:** Reference earlier points

Without these, AI dialogue sounds robotic.

---

## Voice Synthesis

### ElevenLabs Workflow
1. Choose/create voice profiles for each host
2. Split script by speaker
3. Generate audio per segment
4. Apply emotion/style parameters
5. Stitch together with timing

### Voice Consistency
- Save voice profiles with names (e.g., "Alex - Host A")
- Document: pitch, pace, accent, energy level
- Use same settings across all episodes
- Clone your own voice for maximum consistency

### Multi-Voice Dialogue
```python
# Pseudocode for dialogue generation
for segment in script:
    voice = "alex" if segment.speaker == "A" else "jordan"
    audio = elevenlabs.generate(
        text=segment.text,
        voice=voice,
        style=segment.emotion  # curious, excited, skeptical
    )
    timeline.append(audio, pause=0.3)
```

---

## Quality Control

### Common Problems & Fixes

| Problem | Fix |
|---------|-----|
| Pronunciation errors | Add phonetic spellings: "Nietzsche [NEECH-uh]" |
| Monotone delivery | Add emotion tags in script |
| Unnatural pauses | Adjust timing between segments |
| Repetitive phrases | Vary script vocabulary |
| Too "clean" | Add filler words, reactions |

### Engagement Testing
Before publishing:
- Listen to 5 random minutes — does it hold attention?
- Check pacing — any draggy sections?
- Verify facts — AI can hallucinate
- Test on real listener — does it feel authentic?

---

## Disclosure & Ethics

### Required Disclosures
Many platforms require AI content disclosure:
- **YouTube:** Declare AI/synthetic content in settings
- **Spotify:** Terms require disclosure of synthetic voices
- **Apple:** No specific requirement yet, but transparency recommended

### Disclosure Formats
```
Audio: "This podcast is created using AI voice synthesis."
Show notes: "Note: This episode features AI-generated voices."
```

### Ethical Considerations
- Don't clone voices without consent
- Don't create fake interviews with real people
- Don't present AI opinions as human expertise
- Be transparent with audience

---

## Workflow: Full AI Episode

1. **Input:** Topic, sources, or outline
2. **Script:** Generate conversational dialogue
3. **Review:** Edit for accuracy, add natural elements
4. **Voices:** Synthesize each speaker
5. **Assembly:** Combine with timing, add music
6. **Quality check:** Listen through, fix issues
7. **Metadata:** Generate show notes, description
8. **Publish:** With appropriate disclosure

### Time Estimate
| Step | Time |
|------|------|
| Script generation | 5-10 min |
| Script editing | 15-30 min |
| Voice synthesis | 10-20 min |
| Assembly + music | 15-30 min |
| Quality check | 15-20 min |
| **Total** | ~1-2 hours for 20-min episode |

Compare to traditional recording: 4-8+ hours per episode.
