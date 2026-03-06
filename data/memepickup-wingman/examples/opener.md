# Example: Generating an Opener

## Scenario

Jake just matched with Sarah on Hinge. He screenshots her profile and sends it to the wingman for help with an opener.

---

### Conversation

**Jake:** Just matched with this girl on Hinge, she seems cool. Help me out
[Attaches screenshot of Sarah's Hinge profile — photos show her at a pottery class, hiking with a dog, and at a rooftop bar. Bio reads: "Looking for someone who can keep up. Dog mom. Pottery is my therapy. Will judge you by your coffee order."]

**Wingman:**

Let me analyze her profile first.

[Calls `analyze` with the screenshot, platform: "hinge"]

Score: **0.85** — strong match. She's got the pottery thing, the dog, the coffee snobbery — and that "keep up" energy says she wants someone with their own thing going on.

My recommendation: **Like with comment** on her "Will judge you by your coffee order" prompt.

Suggested comment:
> "I'll let you judge my coffee order, but fair warning — it's going to reveal way too much about me"

It plays into her bio directly without being try-hard about it. It's self-aware, gives her something to riff on, and doesn't mention the dog (everyone mentions the dog).

Want me to generate some alternative lines too?

**Jake:** Yeah give me options

**Wingman:**

[Calls `lines` at intensities 0.2, 0.5, 0.7]

**Chill (0.2):** "Your pottery looks better than anything I could make — and I've tried"

**Playful (0.5):** "I'll let you judge my coffee order, but fair warning — it's going to reveal way too much about me"

**Bold (0.7):** "You had me at 'will judge you.' I respect a woman with standards"

My pick: go Playful. She's witty in her bio so she'll appreciate the self-aware humor.

**Jake:** Sent the playful one. She replied "lol okay what's the order then"

**Wingman:**

She bit. Now don't over-explain it — keep it playful:

> "Oat milk cortado. Go ahead, read me like a book"

Short, confident, gives her another opening to keep going. She's clearly engaged — match her energy.

---

### What Happened Behind the Scenes

1. Jake sent a Hinge profile screenshot
2. Wingman called `scripts/api.sh analyze` with the image + platform "hinge"
3. API scored the profile (0.85), identified best prompt to comment on, suggested a comment
4. Wingman called `scripts/api.sh lines` at three intensities for alternatives
5. When Jake shared her reply, wingman shifted to reply coaching (no API call — local)

### Credits Used: 2

- 1 credit: profile analysis
- 1 credit: pickup line generation (one call, multiple intensities in presentation)
