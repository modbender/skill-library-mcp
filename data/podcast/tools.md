# Tools — Platforms, Software, APIs

## Recording

### Remote Recording
| Tool | Strengths | Pricing |
|------|-----------|---------|
| Riverside | Separate tracks, video + audio | $15-24/mo |
| Squadcast | Reliable, good audio | $12-24/mo |
| Zencastr | Free tier, simple | Free-$20/mo |
| Zoom | Ubiquitous, fallback option | Free-$15/mo |

### Local Recording
- **Mac:** QuickTime, GarageBand, Logic Pro
- **Windows:** Audacity, Adobe Audition
- **Cross-platform:** OBS (for video), Audacity

---

## Editing

### Audio Editing
| Tool | Best for | Pricing |
|------|----------|---------|
| Descript | AI editing, transcription | $12-24/mo |
| Adobe Audition | Professional audio | $23/mo |
| Audacity | Free, open source | Free |
| GarageBand | Mac users, simple | Free |

### Video Editing
| Tool | Best for | Pricing |
|------|----------|---------|
| Descript | Podcast-specific, easy | $12-24/mo |
| DaVinci Resolve | Professional, free tier | Free |
| CapCut | Quick clips, social | Free |
| Premiere Pro | Full control | $23/mo |

### AI Enhancement
- **Adobe Podcast Enhance:** Free noise removal, enhancement
- **Auphonic:** Auto-leveling, noise reduction
- **Descript:** Studio Sound feature

---

## Hosting & Distribution

### Podcast Hosts
| Platform | Free tier | Premium |
|----------|-----------|---------|
| Spotify for Podcasters | Yes | Free |
| Buzzsprout | 2hr/mo | $12-24/mo |
| Transistor | No | $19-99/mo |
| Podbean | 5hr/mo | $9-99/mo |

All distribute to Apple Podcasts, Spotify, Google, etc. via RSS.

### Video Distribution
- **YouTube:** Full episodes + shorts
- **Spotify:** Video podcast support
- **TikTok/Instagram:** Clips only

---

## Transcription

### Automated
| Tool | Accuracy | Pricing |
|------|----------|---------|
| Whisper (local) | 95%+ | Free |
| Descript | 95%+ | Included |
| Otter.ai | 90%+ | $10-20/mo |
| Rev | 99% (human) | $1.50/min |

### Command Line (Whisper)
```bash
whisper episode.mp3 --model turbo --language en --output_format all
```

---

## AI Voice Generation

### Text-to-Speech
| Tool | Quality | Use case |
|------|---------|----------|
| ElevenLabs | Excellent | Full episodes, cloning |
| OpenAI TTS | Good | Quick narration |
| Play.ht | Good | Multiple voices |
| Resemble.ai | Excellent | Voice cloning |

### AI Dialogue Generation
- **NotebookLM:** Upload sources → conversational podcast
- **Custom workflows:** LLM script + ElevenLabs voices

---

## Clip Creation

### Automated Clip Tools
| Tool | Features | Pricing |
|------|----------|---------|
| Opus Clip | AI clip detection | $9-29/mo |
| Vidyo.ai | Auto-captions, clips | $15-30/mo |
| Headliner | Audiograms | Free-$15/mo |
| Descript | Clips + captions | Included |

### Manual Clip Creation
```bash
# Extract clip
ffmpeg -i episode.mp4 -ss 00:15:30 -t 00:00:45 clip.mp4

# Add captions
ffmpeg -i clip.mp4 -vf "subtitles=captions.srt" captioned.mp4

# Convert to vertical
ffmpeg -i clip.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" vertical.mp4
```

---

## Analytics

### Platform Analytics
- **Spotify for Podcasters:** Demographics, retention
- **Apple Podcasts Connect:** Downloads, followers
- **YouTube Studio:** Watch time, retention curves

### Third-Party
| Tool | Features | Pricing |
|------|----------|---------|
| Chartable | Rankings, attribution | $50-500/mo |
| Podtrac | Industry measurement | Free |
| Transistor | Built-in analytics | Included |

---

## Music & Sound

### Royalty-Free Music
- **Epidemic Sound:** $15/mo, huge library
- **Artlist:** $10-17/mo, unlimited
- **YouTube Audio Library:** Free
- **Uppbeat:** Free tier available

### Sound Effects
- **Freesound.org:** Free, CC licensed
- **Epidemic Sound:** Included with subscription
- **Soundsnap:** Pay per download

---

## Workflow Integration

### Automation
- **Zapier:** Connect tools (new episode → social post)
- **Make:** More complex workflows
- **IFTTT:** Simple automations

### Project Management
- **Notion:** Episode tracking, guest CRM
- **Airtable:** Content calendar, guest database
- **Trello:** Kanban for episode pipeline

### Guest Scheduling
- **Calendly:** Self-service booking
- **SavvyCal:** Personalized scheduling
- **Riverside/Squadcast:** Built-in scheduling
