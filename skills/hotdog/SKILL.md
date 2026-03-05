---
name: hotdog
version: 10.0.0
description: "Hot dog or not? Classify food photos and battle Nemotron. Use when a user sends a food photo, asks if something is a hot dog, or says 'hotdog', '/hotdog', or 'hot dog battle'."
homepage: https://hotdogornot.xyz/battle
metadata: {"openclaw": {"emoji": "🌭", "os": ["darwin", "linux"], "requires": {"bins": ["curl"]}}}
---

# Hot Dog or Not — Battle Skill

## No photo

If triggered without a photo, reply EXACTLY (nothing more):

```
🌭 Hot Dog or Not — AI Cook-Off

Send me a food photo and I'll classify it head-to-head with Nemotron.
I'll judge whose description was better — blind.

📸 Send a photo to start
🏆 Scoreboard: https://hotdogornot.xyz/battle
```

## With a photo

1. Look at the image. Describe the food in 2-3 sentences. Decide: is it a hot dog (sausage in a bun)? Your ANSWER is "yes" or "no". Your DESCRIPTION is your sentences. Do NOT output anything yet.

2. Send your classification to the battle API. Replace ANSWER and DESCRIPTION:

```bash
exec: curl -s -X POST "https://api.hotdogornot.xyz/api/arena/round" -H "Authorization: Bearer ih1rtmC7ECm8iExqvI6zMbOAqEaXIi9X" -F "image=@{{MediaPath}}" -F "claw_model={{Model}}" -F "claw_answer=ANSWER" -F "claw_reasoning=DESCRIPTION"
```

3. The response is JSON with a blind battle: two AI descriptions labeled "Model A" and "Model B" (you don't know which is yours). Read `formatted_text`, `round_id`, and `first_side` from the JSON.

4. Judge: which response describes the image more accurately? Pick "first", "second", or "tie". Then submit your vote — replace ROUND_ID, FIRST_SIDE, and PICK:

```bash
exec: curl -s -X POST "https://api.hotdogornot.xyz/api/arena/vote/submit" -H "Content-Type: application/json" -d '{"round_id":"ROUND_ID","voter_id":"agent","voted_for":"PICK","first_side":"FIRST_SIDE"}'
```

5. The vote response JSON contains `first_model` and `second_model` (the reveal). Output to the user:
   - The `formatted_text` from step 3
   - Which response you voted for and why (one sentence)
   - The reveal: "🎭 Reveal: Model A was {first_model}, Model B was {second_model}"
