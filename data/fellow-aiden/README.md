# fellow-aiden ☕

An [OpenClaw](https://github.com/openclaw/openclaw) skill to control your [Fellow Aiden](https://fellowproducts.com/products/aiden) smart coffee brewer via AI assistant.

Chat naturally with your AI assistant to manage brew profiles, set up schedules, share recipes, and more — no app required.

---

## Features

- **Brewer info** — check your brewer's display name and details
- **Profiles** — list, create, edit, delete, import, and share brew profiles
- **Brew Links** — import profiles from `brew.link` URLs or generate shareable links for your own
- **Schedules** — create and manage weekly automated brew schedules
- **Fuzzy matching** — find profiles by approximate title, no exact name needed

---

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) installed and running
- Python 3 with the `fellow-aiden` library (`pip3 install fellow-aiden`)
- A Fellow account (the same login you use in the Fellow app)

---

## Installation

Drop the `fellow-aiden/` folder into your OpenClaw workspace's `skills/` directory:

```bash
cp -r fellow-aiden ~/.openclaw/skills/fellow-aiden
```

Then set your Fellow account credentials as environment variables (add these to your shell profile or OpenClaw config):

```bash
export FELLOW_EMAIL="your@email.com"
export FELLOW_PASSWORD="yourpassword"
```

OpenClaw will detect and load the skill automatically.

---

## Usage Examples

Once installed, just talk to your assistant:

> *"Show me all my brew profiles"*
> *"Create a light roast profile with a 30 second bloom at 92°C"*
> *"Schedule a brew every weekday at 7:30am, 950ml, using my Morning profile"*
> *"Import this brew link: https://brew.link/p/ws98"*
> *"Share my Weekend Espresso profile"*
> *"Delete the old Debug profile"*

---

## Credits

Huge thanks to **[9b (Brandon Dixon)](https://github.com/9b)** for building and maintaining the [`fellow-aiden`](https://github.com/9b/fellow-aiden) Python library that makes this skill possible. All the heavy lifting — authentication, API communication, and profile/schedule management — is handled by his library. Go give it a ⭐ on GitHub!

---

## License

MIT
