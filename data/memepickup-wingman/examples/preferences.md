# Example: Setting Up Preferences

## Scenario

Jake just installed the MemePickup Wingman skill and wants to set up his dating preferences so the profile analysis knows what he's looking for.

---

### Conversation

**Jake:** Help me set up my dating preferences

**Wingman:**

Cool, let me learn your type. Tell me about your last 3 best dates — what made them great?

**Jake:** The best one was with this girl who was super into hiking and we just talked for hours about travel. She was athletic, brunette, had this really dry sense of humor. Another good one was at a brewery with a girl who had a dog — we just chilled and it was super easy. Third was a coffee date where she had the best energy, really ambitious and funny.

**Wingman:**

Got it. Here's what I'm picking up:

**Physical:**
- You gravitate toward athletic/fit builds
- Brunette preference (but probably not a dealbreaker)

**Personality:**
- Adventurous (hiking, travel)
- Funny with dry/witty humor
- Ambitious
- Easy to talk to — conversational chemistry matters

**Lifestyle:**
- Active/outdoorsy
- Dog person is a bonus
- Enjoys casual spots (breweries, coffee shops)

Let me set that up. Any hard dealbreakers I should know about? Things that are an automatic no.

**Jake:** No smokers for sure. And I don't really vibe with people who have zero bio or all group photos.

**Wingman:**

Perfect. Setting your preferences now.

[Calls `scripts/api.sh set-prefs`]

```json
{
  "preferences": {
    "physical": {
      "bodyType": ["athletic", "slim", "average"],
      "hairColor": ["brunette"]
    },
    "lifestyle": {
      "smoking": "dealbreaker_no",
      "pets": ["dogs"]
    },
    "personality": {
      "interests": ["hiking", "travel", "coffee", "dogs"],
      "vibes": ["adventurous", "funny", "ambitious", "witty"]
    },
    "dealbreakers": ["no bio", "all group photos", "smoking"],
    "ageRange": [24, 32],
    "minScore": 0.6,
    "notes": "Values conversational chemistry. Prefers active/outdoorsy. Dry humor is a plus."
  },
  "platforms": ["hinge", "bumble"]
}
```

Done. Here's a summary:

- **Score threshold:** 0.6+ (I'll recommend profiles above this)
- **Hard dealbreakers:** Smoking, no bio, all group photos (these tank the score)
- **Soft preferences:** Brunette, athletic, dogs, hiking, humor (these boost the score but aren't required)
- **Platforms:** Hinge and Bumble

Now send me any profile screenshot and I'll score it against these preferences. You can also batch them — screenshot a bunch and I'll rank them all.

**Jake:** Add Tinder too and bump the age range to 25-34

**Wingman:**

[Calls `scripts/api.sh set-prefs`]

Updated:
- Age range: 25-34
- Platforms: Hinge, Bumble, Tinder

Your preferences are synced. Want to test it? Send me a profile.

---

### What Happened Behind the Scenes

1. Wingman had a conversational exchange to extract preferences naturally
2. Mapped Jake's descriptions to structured preference fields
3. Called `scripts/api.sh set-prefs` with the structured JSON
4. Preferences saved to MemePickup cloud (synced across devices)
5. Follow-up update used the same endpoint to modify specific fields

### API Calls Made

```bash
# Initial setup
echo '{"preferences": {...}, "platforms": ["hinge", "bumble"]}' | scripts/api.sh set-prefs

# Update
echo '{"preferences": {"ageRange": [25, 34]}, "platforms": ["hinge", "bumble", "tinder"]}' | scripts/api.sh set-prefs
```

### Credits Used: 0

Preference management is free. Credits are only used for line generation, reply suggestions, and profile analysis.
