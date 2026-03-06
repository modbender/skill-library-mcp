# Example: Telegram Wingman (Manus)

## Scenario

Jake has Manus set up as a Telegram agent. He forwards a dating app notification to Manus, and the wingman helps him reply without leaving Telegram.

> **Note:** This workflow requires Manus with Telegram integration. Availability may vary as Manus Telegram agents are a new feature. Fallback: use the Manus desktop app or sandbox directly. This pattern will also work with WhatsApp, LINE, Slack, and Discord when Manus adds support for those platforms.

---

### Conversation (via Telegram)

**Jake** *(forwards a Hinge notification to Manus):*
> New message from Sarah: "Okay but what's your most controversial food take"

**Wingman:**

She's testing your personality — this is a "are you interesting or boring" question. Let me get you options.

[Calls `scripts/api.sh replies` at intensities 0.2, 0.4, 0.7]

**Chill:**
> "Cereal is a soup. I will not be taking questions at this time"

**Playful:**
> "Pineapple on pizza is elite and I'm tired of pretending it's not"

**Bold:**
> "Ranch on everything. Yes, everything. Fight me over dinner"

My pick: Playful. It's a confident take that's easy to riff on. Bold works too — "fight me over dinner" is a smooth pivot to a date.

**Jake:** Going with bold, that's smooth

**Wingman:**

Sent. That "fight me over dinner" is doing double duty — funny take AND a date suggestion. If she picks up on the dinner part, you're in.

---

### What Happened Behind the Scenes

1. Jake forwarded a dating app notification to Manus via Telegram
2. Manus recognized it as a dating conversation (activation trigger)
3. Wingman called `scripts/api.sh replies` with the message at three intensities
4. Returned Chill/Playful/Bold suggestions back through Telegram
5. Jake picked one and could send it directly from his phone

### Credits Used: 3

- 1 credit per intensity level call (3 calls for Chill/Playful/Bold)

### Why This Works

The API call is the same regardless of delivery channel — Telegram is just how the user interacts with Manus. The wingman skill runs in Manus's sandbox, makes the same API calls as it would from OpenClaw or the Manus desktop app, and returns results through whatever messaging platform Manus is connected to.
