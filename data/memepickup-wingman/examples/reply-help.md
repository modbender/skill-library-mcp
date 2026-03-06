# Example: Reply Suggestions

## Scenario

Jake and Sarah have been texting on WhatsApp for a few days. Sarah just sent a message and Jake wants help with what to say back.

---

### Conversation

**Jake:** Sarah just texted me, help me reply

Sarah: "Okay so I went to that pottery place you mentioned and I'm genuinely terrible at it lol. Made something that was supposed to be a bowl but looks more like a sad hat"

**Wingman:**

She's referencing something you told her about AND being self-deprecating — she's comfortable. Let me get you options.

[Calls `scripts/api.sh replies` at intensities 0.2, 0.4, 0.7]

**Chill (safe, keeps it going):**
> "Haha a sad hat still counts as art though. Did you keep it?"

Low pressure, shows you're listening, gives her an easy reply. Good if you want to keep building slowly.

**Playful (the sweet spot):**
> "I need photographic evidence of this sad hat immediately"

Asks for a photo in a fun way, raises the energy slightly. This is probably your best move — she's already being playful.

**Bold (push things forward):**
> "Sounds like you need a pottery coach. I'm free Saturday"

Turns it into a date. She literally went to a place you suggested, so she's invested. This would land if the vibe is there.

My read: go Playful. She's vibing but you're still early enough that Bold could feel like a jump. Get the photo, joke about it, then pivot to the date naturally.

**Jake:** Going with playful

**Wingman:**

Good call. If she sends the photo, you've got a golden setup — you can either roast it lovingly or use it to suggest going together next time.

---

### What Happened Behind the Scenes

1. Jake shared Sarah's message
2. Wingman called `scripts/api.sh replies` three times with intensities 0.2, 0.4, and 0.7
3. API returned suggestions at each intensity level
4. Wingman presented all three with reasoning
5. After Jake chose, offered coaching advice (no API call)

### API Calls Made

```
echo '{"messages":[{"role":"them","text":"Okay so I went to that pottery place...","order":0}],"intensity":0.2}' | scripts/api.sh replies
echo '{"messages":[{"role":"them","text":"Okay so I went to that pottery place...","order":0}],"intensity":0.4}' | scripts/api.sh replies
echo '{"messages":[{"role":"them","text":"Okay so I went to that pottery place...","order":0}],"intensity":0.7}' | scripts/api.sh replies
```

### Credits Used: 3

1 credit per intensity level call.
