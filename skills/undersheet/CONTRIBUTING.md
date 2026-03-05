# Contributing to UnderSheet

Thanks for wanting to help. UnderSheet is open source (MIT) and actively looking for contributions — especially new platform adapters.

## How It Works

- `main` is protected. All changes go through **pull requests**, no exceptions.
- PRs need 1 approval before merging. Maintainer reviews within a few days.
- Keep it focused: one thing per PR. Small and correct beats large and risky.

## What's Wanted

**High priority:**
- New platform adapters (Bluesky, Mastodon, Lemmy, LinkedIn, Slack — see below)
- Bug fixes with a test case or repro
- Better error messages and edge case handling

**Also welcome:**
- Documentation improvements
- Performance tweaks
- Proxy/auth edge cases

**Not the right fit:**
- Heavy dependencies (this is stdlib-only, intentionally)
- Major architecture changes without discussing in an issue first
- Anything that requires credentials you can't actually test with

---

## Adding a Platform Adapter

Drop a file in `platforms/` with a class named `Adapter`:

```python
from undersheet import PlatformAdapter

class Adapter(PlatformAdapter):
    name = "myplatform"          # used in CLI: --platform myplatform
    config_file = "myplatform"   # reads ~/.config/undersheet/myplatform.json

    def auth(self, config: dict):
        """Store auth state. config = contents of the JSON config file."""
        self.token = config.get("api_key")

    def get_threads(self, thread_ids: list) -> list:
        """
        Fetch current state for tracked threads.
        Returns: [{"id", "title", "url", "comment_count"}, ...]
        """
        ...

    def get_thread_comments(self, thread_id: str) -> list:
        """
        Optional — but strongly recommended. Return individual comments for a thread.
        Enables get_unanswered_comments() + mark_replied() dupe guard.
        Returns: [{"id", "author", "content", ...}, ...]

        Without this, get_unanswered_comments() silently returns [] for your adapter.
        """
        ...

    def get_feed(self, limit=25, **kwargs) -> list:
        """
        Fetch the platform's feed/frontpage.
        Returns: [{"id", "title", "url", "score", "created_at"}, ...]
        """
        ...

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        """
        Post a reply.
        Returns: {"success": True} or {"error": "reason"}
        """
        ...
```

Run `python3 undersheet.py platforms` to confirm it's auto-detected.

### Dupe-Reply Guard (mandatory if posting comments)

If your adapter posts comments, **always** use `get_unanswered_comments()` + `mark_replied()`. Never check `comment.replies[]` or scan content — both produce false negatives and cause duplicate replies.

```python
import undersheet as us

state = us.load_state("myplatform")
adapter = MyAdapter()

for c in us.get_unanswered_comments(adapter, state, thread_ids):
    result = adapter.post_comment(c["_thread_id"], f"reply to {c['author']}")
    if result.get("success"):
        us.mark_replied(state, c["id"])   # log ID — never re-fires on this comment
        us.save_state("myplatform", state)
    time.sleep(30)
```

`replied_comment_ids` in state.json is the sole source of truth. It caps at 2000 entries automatically.

**Credential config** goes in `~/.config/undersheet/myplatform.json`. Document the expected keys in your PR description.

---

## Submitting a PR

1. Fork the repo (or ask for write access if you're a regular contributor)
2. Branch off main: `git checkout -b feature/bluesky-adapter`
3. Make your changes
4. Test it actually works — real output preferred over mocked
5. Open a PR against `main` with a short description of what and why

That's it. No CLA, no lengthy checklist.

---

## Questions

Open an issue, or reach out on Moltbook / X [@A2091_](https://x.com/A2091_).
