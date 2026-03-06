---
name: ghost
description: "Ghost CMS content management via Admin API v5.x. Use when: (1) creating, editing, or publishing blog posts or static pages, (2) managing tags, (3) uploading images, (4) reading member/newsletter/tier info, (5) checking site settings. NOT for: theme management (needs Ghost CLI), webhook config, email sending (auto on publish), content import/export (use Ghost Admin UI), or multi-site setups."
homepage: https://github.com/rwx-g/openclaw-skill-ghost
compatibility: Python 3.9+ · network access to Ghost instance · Admin API Key
metadata:
  {
    "openclaw": {
      "emoji": "👻",
      "requires": { "env": ["GHOST_URL", "GHOST_ADMIN_KEY"] },
      "primaryEnv": "GHOST_ADMIN_KEY"
    }
  }
ontology:
  reads: [posts, pages, tags, site, members, newsletters, tiers, users]
  writes: [posts, pages, tags, images]
---

# Ghost Skill

Full Ghost Admin API v5 client. HS256 JWT auth and all HTTP calls via stdlib (urllib) - zero external dependencies.
Credentials: `~/.openclaw/secrets/ghost_creds` · Config: `~/.openclaw/config/ghost/config.json`

## Trigger phrases

Load this skill immediately when the user says anything like:

- "create / write / draft a blog post / article"
- "publish this post / article", "make this live on Ghost"
- "update / edit [post title or slug]", "change the title of my post"
- "unpublish / revert to draft [post]"
- "create / add a tag", "list my tags on Ghost"
- "create / update / publish a page"
- "upload this image to Ghost"
- "list my posts / drafts", "show me what's in draft"
- "schedule this post for [date]"
- "what's on my Ghost site?", "show site info"

## Quick Start

```bash
python3 scripts/ghost.py config    # verify credentials + active config
python3 scripts/ghost.py site      # test connection + show site info
python3 scripts/ghost.py posts --limit 3 --fields "id,title,status"
```

## Setup

```bash
python3 scripts/setup.py       # interactive: credentials + permissions + connection test
python3 scripts/init.py        # validate all configured permissions against live instance
```

> init.py only runs write/delete tests when `allow_delete=true`. When `allow_delete=false`, write tests are skipped - no test artifacts are created, so none can be left behind.

**Manual** - `~/.openclaw/secrets/ghost_creds` (chmod 600):
```
GHOST_URL=https://your-ghost.example.com
GHOST_ADMIN_KEY=id:secret_hex
```
Admin API Key: Ghost Admin → Settings → Integrations → Add custom integration → copy **Admin API Key**.

**config.json** - behavior restrictions:

| Key | Default | Effect |
|-----|---------|--------|
| `allow_publish` | `false` | allow status=published (enable explicitly to publish) |
| `allow_delete` | `false` | allow delete posts/pages/tags |
| `allow_member_access` | `false` | enable member read/write |
| `default_status` | `"draft"` | status applied when not specified |
| `default_tags` | `[]` | tags always merged into new posts |
| `readonly_mode` | `false` | override: block all writes |

## Storage & credentials

The skill reads and writes the following paths. All usage is intentional and documented:

| Path | Written by | Purpose |
|------|-----------|---------|
| `~/.openclaw/secrets/ghost_creds` | `setup.py` | Ghost credentials (GHOST_URL, GHOST_ADMIN_KEY). chmod 600. Never committed. |
| `~/.openclaw/config/ghost/config.json` | `setup.py` | Behavior restrictions (allow_publish, allow_delete, etc.). No secrets. Not in skill dir - survives clawhub updates. |

Credentials can also be provided via environment variables (`GHOST_URL`, `GHOST_ADMIN_KEY`). The skill checks env vars first.

**Cleanup on uninstall:** `clawhub uninstall ghost-admin` removes the skill directory. To also remove credentials and config:
```bash
python3 scripts/setup.py --cleanup
```
On reinstall, any existing config at `~/.openclaw/config/ghost/config.json` is picked up automatically.

## Module usage

```python
from scripts.ghost import GhostClient
gc = GhostClient()
post = gc.create_post("My Title", html="<p>Body</p>", status="draft")
gc.publish_post(post["id"])
```

## CLI reference

```bash
# Posts
python3 scripts/ghost.py posts --status published --limit 10
python3 scripts/ghost.py posts --tag devops --fields "id,title,published_at"
python3 scripts/ghost.py post <id_or_slug>
python3 scripts/ghost.py post-create "Title" --html "<p>...</p>" --status draft
python3 scripts/ghost.py post-create "Title" --html-file body.html --tags "DevOps,Linux"
python3 scripts/ghost.py post-create "Title" --html-file body.html --feature-image "https://..."
python3 scripts/ghost.py post-update <id> --fields-json '{"title":"New","custom_excerpt":"..."}'
python3 scripts/ghost.py post-publish <id>
python3 scripts/ghost.py post-unpublish <id>
python3 scripts/ghost.py post-delete <id>          # requires allow_delete: true

# Pages
python3 scripts/ghost.py pages
python3 scripts/ghost.py page-create "About" --html "<p>...</p>"
python3 scripts/ghost.py page-publish <id>

# Tags
python3 scripts/ghost.py tags
python3 scripts/ghost.py tag-create "DevOps" --slug devops --desc "DevOps content"
python3 scripts/ghost.py tag-delete <id>           # requires allow_delete: true

# Images
python3 scripts/ghost.py image-upload ./image.png --alt "Description"

# Members & newsletters (read)
python3 scripts/ghost.py members --limit 20        # requires allow_member_access: true
python3 scripts/ghost.py newsletters
python3 scripts/ghost.py tiers

# Account
python3 scripts/ghost.py site
python3 scripts/ghost.py me
python3 scripts/ghost.py config
```

## Templates

### Draft → review → publish
```python
gc = GhostClient()
# 1. Create draft
post = gc.create_post(
    title="My Article",
    html=article_html,
    tags=[{"name": "DevOps"}, {"name": "Linux"}],
    meta_description="Short SEO description",
    status="draft",
)
draft_url = f"{gc.base_url}/ghost/#/editor/post/{post['id']}"
# 2. Return preview link to user for review
# → f"Draft created: {draft_url}"
# 3. After user approval:
gc.publish_post(post["id"])
# → f"Published: {post['url']}"
```

### Research → structured post
```python
# Create a post with full SEO metadata
post = gc.create_post(
    title="Why Rust is Taking Over Systems Programming",
    html=content_html,
    custom_excerpt="A technical deep-dive into Rust's memory model and adoption trends.",
    meta_title="Rust Systems Programming 2025",
    meta_description="Why Rust is replacing C++ in systems programming in 2025.",
    og_title="Rust is Taking Over Systems Programming",
    tags=[{"name": "Rust"}, {"name": "Systems"}],
    feature_image="https://example.com/rust.png",
    status="draft",
)
```

### Content audit by tag
```python
result = gc.list_posts(limit="all", tag="devops", fields="id,title,status,published_at")
posts  = result["posts"]
drafts    = [p for p in posts if p["status"] == "draft"]
published = [p for p in posts if p["status"] == "published"]
# → summarize backlog for user
```

### Batch tag creation
```python
for name in ["DevOps", "Security", "Linux", "Cloud"]:
    try:
        gc.create_tag(name, slug=name.lower())
    except Exception:
        pass  # already exists
```

## Ideas
- Set `allow_publish: false` + `default_status: draft` for a "suggest only" mode
- Use `default_tags` in config for auto-tagging (e.g. always add "AI-assisted")
- Draft from a research summary, share preview link, publish after human review
- List `posts --status draft` to surface the content backlog for triage
- Upload a feature image first, then embed the returned URL in post HTML

## Notes
- **`updated_at` conflict guard**: `update_post`/`update_page` auto-fetches `updated_at` if omitted.
- **HTML content**: Ghost v5 stores Lexical internally but `html` import works perfectly for agent-generated content.
- **`allow_publish: false`**: Status is silently capped to `"draft"` - no error raised.
- **JWT tokens**: Generated fresh per request (5-min TTL), no caching needed.
- **Slug**: Auto-generated from title if omitted. Override with `--slug` for clean URLs.

## Combine with

| Skill | Workflow |
|-------|----------|
| **summarize** | Summarize a URL / PDF → draft a Ghost post from the summary |
| **tavily-search** | Research a topic → structured Ghost draft with sources |
| **nextcloud** | Save draft `.md` to NC → review → publish to Ghost |
| **gmail** | Forward a newsletter / article → draft Ghost post from it |
| **api-gateway (linkedin)** | Publish Ghost post → cross-post excerpt to LinkedIn |

## API reference
See `references/api.md` for endpoint details, NQL filters, field list, and error codes.

## Troubleshooting
See `references/troubleshooting.md` for common errors and fixes.
