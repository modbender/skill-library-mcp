# Ghost CMS Skill for OpenClaw

> Comprehensive Ghost CMS integration for creating, publishing, scheduling, and managing blog content, newsletters, members, and analytics.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This skill enables OpenClaw agents to interact with [Ghost CMS](https://ghost.org), the open-source publishing platform. Manage content, members, subscriptions, comments, and analytics—all via the Ghost Admin API.

**Status:** ✅ **Production Ready** (Security hardened Feb 10, 2026)  
**API Version:** Ghost Admin API v5.0  
**Hosting:** ✅ **Works with Ghost(Pro) AND self-hosted Ghost installations** (v5.0+)

## Features

✅ **Content Management** - Create, update, publish, schedule posts and pages  
✅ **Member Management** - Manage subscribers, free and paid memberships  
✅ **Subscription Management** - Create and manage pricing tiers  
✅ **Comment Management** - Reply to, approve, and moderate comments  
✅ **Newsletter Management** - Configure newsletters and email campaigns  
✅ **Analytics** - Access subscriber stats, popular content, MRR  
✅ **Media Management** - Upload images and featured images  
✅ **User Management** - Invite and manage site users  
✅ **Theme Management** - Upload, activate, switch, and manage custom themes  
✅ **Theme Validation** - Validate themes before upload using official Ghost gscan validator

## Security

**This skill includes comprehensive security controls:**

- **🔒 Autonomous invocation disabled** - Requires explicit user commands
- **📋 Capability declarations** - 8 capabilities clearly documented
- **🔑 Credential documentation** - Multiple secure storage options
- **📚 Operation classification** - ~50 operations (17 read-only, 33 destructive)
- **⚠️ Security warnings** - Prominent warnings about public publishing
- **📖 Comprehensive docs** - Complete API reference with safety guide
- **🛡️ Recovery procedures** - Undo guide for all operations

**Admin API Key Access:**
- Ghost Admin API keys provide **full site access**
- **No read-only scopes available** - keys have complete permissions
- **Published content is immediately public** - extra caution required
- Store securely (1Password CLI, environment variables)
- Rotate regularly (every 90 days recommended)
- Never commit keys to version control

See [SKILL.md](SKILL.md) for detailed security information and [references/api-reference.md](references/api-reference.md) for operation-by-operation safety classifications.

## Installation

### Prerequisites

- Node.js >= 18.0.0
- npm
- Ghost site (self-hosted or Ghost Pro)
- Ghost Admin API credentials

### Setup

1. **Get your Ghost Admin API credentials:**
   - Ghost dashboard → Settings → Integrations
   - Create a new "Custom Integration"
   - Copy the **Admin API Key** and **API URL**

2. **Install dependencies:**
   ```bash
   cd ghost-cms-skill/scripts
   npm install
   ```

   **What gets installed:**
   - `form-data` (^4.0.5) - Multipart file uploads (theme ZIP files)
   - `jsonwebtoken` (^9.0.3) - JWT token generation for Ghost Admin API authentication
   - `gscan` (^5.2.4) - Official Ghost theme validator (from TryGhost/gscan)
   
   All dependencies from public npm registry. No custom downloads or external sources.

3. **Store credentials securely:**

   **Option A: Environment Variables (Recommended)**
   ```bash
   # Add to your shell profile (~/.zshrc, ~/.bashrc)
   export GHOST_ADMIN_KEY="YOUR_ADMIN_API_KEY"
   export GHOST_API_URL="YOUR_GHOST_URL"
   
   # Examples (works with ALL hosting types):
   # Ghost(Pro):        https://yourblog.ghost.io
   # Self-hosted:       https://blog.yourdomain.com
   # Development:       http://localhost:2368
   # Custom port:       https://ghost.example.com:8080
   ```
   
   **See [SKILL.md](SKILL.md#quick-setup) for detailed URL format guide and examples.**

   **Option B: Config Files**
   ```bash
   mkdir -p ~/.config/ghost
   echo "YOUR_ADMIN_API_KEY" > ~/.config/ghost/api_key
   echo "YOUR_GHOST_URL" > ~/.config/ghost/api_url
   chmod 600 ~/.config/ghost/api_key ~/.config/ghost/api_url
   ```

   **Option C: 1Password CLI (Most Secure)**
   ```bash
   # Store in 1Password
   op item create --category=API_CREDENTIAL \
     --title="Ghost Admin API" \
     admin_key[password]="YOUR_ADMIN_API_KEY" \
     api_url[text]="YOUR_GHOST_URL"

   # Use in commands
   export GHOST_ADMIN_KEY=$(op read "op://Private/Ghost Admin API/admin_key")
   export GHOST_API_URL=$(op read "op://Private/Ghost Admin API/api_url")
   ```

4. **Test connection:**
   ```bash
   cd ghost-cms-skill/scripts
   node ghost-crud.js list posts
   ```

## Quick Start

### List Recent Posts

```bash
cd scripts
node ghost-crud.js list posts --limit 5
```

### Create Draft Post

```bash
node ghost-crud.js create post \
  --title "New Blog Post" \
  --content "<p>Content goes here</p>" \
  --tags "tutorial,ghost"
```

### Publish a Draft

```bash
# Get post ID first
POST_ID=$(node ghost-crud.js list posts --filter "status:draft" | jq -r '.[0].id')

# Publish it
node ghost-crud.js update post "$POST_ID" \
  --status published
```

### Get Member Stats

```bash
node ghost-crud.js stats members
```

See [SKILL.md](SKILL.md) for complete usage guide and [references/](references/) for detailed documentation.

## Documentation

**Primary Documentation:**
- [SKILL.md](SKILL.md) - Complete skill reference and security guide
- [references/setup.md](references/setup.md) - Detailed setup and troubleshooting
- [references/api-reference.md](references/api-reference.md) - API endpoints with safety classifications

**Operation Guides:**
- [references/content.md](references/content.md) - Posts, pages, drafts, publishing, scheduling
- [references/members.md](references/members.md) - Member management, subscriptions, tiers
- [references/newsletters.md](references/newsletters.md) - Newsletter configuration, campaigns
- [references/comments.md](references/comments.md) - Comment replies, moderation
- [references/analytics.md](references/analytics.md) - Subscriber stats, popular content, MRR
- [references/lexical-cards.md](references/lexical-cards.md) - Lexical content format cards

## API Coverage

**~45 Ghost Admin API operations supported:**

| Category | Read-Only | Destructive | Total |
|----------|-----------|-------------|-------|
| Posts | 2 | 3 | 5 |
| Pages | 2 | 3 | 5 |
| Tags | 2 | 3 | 5 |
| Members | 3 (incl stats) | 3 | 6 |
| Tiers | 2 | 3 | 5 |
| Newsletters | 2 | 3 | 5 |
| Comments | 2 | 3 | 5 |
| Users | 2 | 3 | 5 |
| Images | 0 | 1 (upload) | 1 |
| Site/Settings | 2 | 1 | 3 |
| Webhooks | 1 | 3 | 4 |

**Total:** 15 read-only, 30 destructive operations

All operations documented with safety classifications, side effects, and recovery procedures.

## Security Features

### Operation Classification

Every API operation is classified:
- **✅ Safe (Read-Only)** - No data modification (all GET requests)
- **⚠️ Destructive** - Modifies or creates data (POST, PUT)
- **🚨 Permanent** - Cannot be undone (DELETE operations)
- **🚨 PUBLIC RISK** - Publishes content to the internet

### Metadata Security Controls

```json
{
  "openclaw": {
    "disable-model-invocation": true,
    "capabilities": [
      "content-management",
      "member-management",
      "subscription-management",
      "comment-management",
      "user-management",
      "media-management",
      "destructive-operations",
      "public-publishing"
    ],
    "requires": {"bins": ["node", "npm"]},
    "credentials": {
      "types": [
        {
          "type": "file",
          "locations": ["~/.config/ghost/api_key", "~/.config/ghost/api_url"]
        },
        {
          "type": "env",
          "variables": [
            {"name": "GHOST_ADMIN_KEY", "required": true},
            {"name": "GHOST_API_URL", "required": true}
          ]
        }
      ]
    }
  }
}
```

### Recovery & Undo Guide

Complete undo procedures documented for all operations:
- Create operations → Can delete
- Update operations → Update again with old values (no version history!)
- Delete operations → **Permanent, cannot undo**
- Publish operations → Can unpublish, but content was temporarily public

**⚠️ Important:** Ghost does not keep version history. Always save important data before modifying.

## Scripts

**Main Scripts:**
- `ghost-crud.js` - CRUD operations for all resources
- `ghost-api.js` - Low-level API wrapper
- `lexical-builder.js` - Build Lexical content format
- `update-teapot.js` - Example workflow (update specific post)

All scripts support:
- Environment variables or config files
- JSON output for piping
- Error handling with detailed messages
- Rate limit awareness

## Common Workflows

### Draft → Review → Publish

```bash
# 1. Create draft
POST_ID=$(node ghost-crud.js create post \
  --title "My Post" \
  --content "<p>Content here</p>" \
  --status draft | jq -r '.id')

# 2. Review in Ghost Admin UI
echo "Review at: ${GHOST_API_URL}/ghost/#/editor/post/${POST_ID}"

# 3. Publish when ready
node ghost-crud.js update post "$POST_ID" --status published
```

### Weekly Newsletter from Notes

```bash
# Collect week's notes, generate post with AI, publish
# (Example integration with Notion/other note systems)
```

### Comment Moderation

```bash
# List pending comments
node ghost-crud.js list comments --filter "status:pending"

# Approve a comment
node ghost-crud.js update comment "$COMMENT_ID" --status published
```

### Member Stats Dashboard

```bash
# Get counts
node ghost-crud.js stats members

# Get MRR
node ghost-crud.js stats mrr

# Recent paid members
node ghost-crud.js list members \
  --filter "status:paid" \
  --limit 10 \
  --order "created_at desc"
```

## Rate Limits

- **500 requests per hour** per integration
- Monitor `X-RateLimit-Remaining` header
- Scripts implement automatic retry with backoff
- Use batch operations where possible

## Troubleshooting

**Authentication Errors:**
```bash
# Verify credentials are set
echo $GHOST_ADMIN_KEY
echo $GHOST_API_URL

# Test connection
node ghost-crud.js list posts --limit 1
```

**Permission Errors:**
- Ghost Admin API keys have full permissions
- If you see 403 errors, regenerate integration key

**Rate Limit Errors:**
- Wait for rate limit reset (check `X-RateLimit-Reset` header)
- Reduce request frequency
- Use pagination to limit batch sizes

See [references/setup.md](references/setup.md) for complete troubleshooting guide.

## Snippet Library

**Local snippet storage system** - workaround for Ghost's native snippet API limitation.

**About Ghost Snippets:**

Ghost has a built-in snippet feature that allows authors to save and reuse content blocks (signatures, CTAs, disclosures, etc.) in the editor. However, the Admin API **blocks access to snippets** for integration tokens (403 Forbidden), meaning:

- ❌ Cannot list snippets programmatically
- ❌ Cannot fetch snippet content via API
- ❌ Cannot use author's existing Ghost snippets in code

**Our Solution:**

This skill includes a **complete snippet system** with automated extraction from Ghost:

**🚀 Automated Snippet Extraction:**
- ✅ Migrate all existing Ghost snippets in one command
- ✅ Create extraction post in Ghost (one-time setup)
- ✅ Run extractor script → all snippets saved locally
- ✅ Preserves exact structure (bookmarks, callouts, images, etc.)
- ✅ Takes ~15 minutes manual + 5 seconds automated

**Extraction Workflow:**
```bash
# 1. Create "My Snippets" draft in Ghost with all your snippets
# 2. Run extractor
node scripts/snippet-extractor.js my-snippets-post

# Done! All snippets now in library/
```

**Local Snippet Library:**
- ✅ Reusable content blocks (signatures, CTAs, disclosures)
- ✅ Stored as Lexical JSON fragments (same format Ghost uses)
- ✅ CLI management tool for easy snippet handling
- ✅ Example snippets included to get started
- ✅ Git version control (bonus: Ghost doesn't version snippets!)
- ✅ Programmatic injection into posts via API

**Snippet Management:**
```bash
# Extract from Ghost (one-time migration)
node scripts/snippet-extractor.js my-snippets-post

# List snippets
node snippets/ghost-snippet.js list

# Preview snippet
node snippets/ghost-snippet.js preview signature

# Use in code
import { loadSnippet } from './snippets/ghost-snippet.js';
const sig = loadSnippet('signature');
```

See [snippets/README.md](snippets/README.md) for complete documentation.

## Lexical Card Support

**23 card types fully documented** with helper functions:

**Text Content:**
- Paragraph, Heading (h1-h6), Markdown

**Media:**
- Image, Gallery, Bookmark
- ✨ **Video** - MP4, WebM, OGG embeds
- ✨ **Audio** - MP3, WAV, OGG embeds
- ✨ **File** - Downloadable files (any type)

**Layout:**
- Callout, Divider
- ✨ **Header** - Section headers with images/layouts

**Interactive:**
- ✨ **Button** - Call-to-action buttons
- ✨ **Toggle** - Collapsible content
- Signup forms

**Marketing:**
- ✨ **Call-to-Action** - Promotional content with visibility
- ✨ **Product** - E-commerce product displays

**Member Content:**
- ✨ **Paywall** - Public preview divider
- ✨ **HTML** - Custom HTML with visibility

**Embeds:**
- ✨ **Embed** - YouTube, Spotify, Twitter, and more via oEmbed

**📖 Complete Documentation:** [lexical-cards.md](references/lexical-cards.md) - Likely the most comprehensive public documentation of Ghost Lexical card types, with complete JSON structures, field references, and usage examples for all 23 card types.

**🛠️ Helper Functions:** [lexical-builder.js](scripts/lexical-builder.js) - **Complete set of 20+ builder functions** for all documented card types:

```javascript
import {
  // Text & basic content
  createParagraph, createHeading, createMarkdownCard,
  
  // Media cards
  createImageCard, createGalleryCard, createBookmarkCard,
  
  // Layout & design
  createCalloutCard, createHorizontalRule, createHeaderCard,
  
  // Interactive
  createButtonCard, createToggleCard, createSignupCard,
  
  // Upload cards
  createVideoCard, createAudioCard, createFileCard,
  
  // Marketing & advanced
  createCallToActionCard, createProductCard, createPaywallCard,
  
  // Developer content
  createHTMLCard, createEmbedCard
} from './scripts/lexical-builder.js';
```

Every documented card type has a helper function with smart defaults and full customization options.

## Future Enhancements

This skill provides complete core functionality for Ghost CMS management. See [open issues](https://github.com/chrisagiddings/moltbot-ghost-skill/issues) for planned enhancements:

**Planned for future releases:**
- Theme management and switching
- Multi-blog support (manage multiple Ghost instances)
- Navigation configuration
- Automation workflows and webhooks
- AI-powered image generation
- Content snippets via API (Ghost limitation)

**Current version (v0.1.0) provides:**
- ✅ Complete content management (posts, pages, tags)
- ✅ **23 Lexical card types documented** (expanded!)
- ✅ **20+ builder helper functions** for all card types
- ✅ **Automated snippet extraction tool** (new!)
- ✅ **Local snippet library system** with CLI
- ✅ Full member and subscription management
- ✅ Comment moderation
- ✅ Newsletter management
- ✅ Basic analytics
- ✅ Image uploads
- ✅ User management

## Privacy & Security

**What this skill stores locally:**
- ✅ Extracted snippets in `snippets/library/` (your content, git-ignored)
- ✅ Temporary test data in `extracted-cards/` (git-ignored)
- ❌ NO credentials (user responsibility to secure)

**What this skill transmits:**
- ✅ API requests to YOUR Ghost site only (HTTPS)
- ❌ NO third-party API calls
- ❌ NO telemetry or analytics
- ❌ NO external logging

**Security features:**
- ✅ Credentials never logged or transmitted to third parties
- ✅ JWT tokens generated on-demand (5-minute expiry)
- ✅ Input sanitization (filenames, sizes)
- ✅ Operation classification (safe vs. destructive)
- ✅ `.gitignore` prevents credential commits

**Best practices:**
- 🔒 Store API keys securely (1Password CLI, env vars, or `~/.config/ghost/`)
- 🔄 Rotate API keys every 90 days
- 🧪 Test on staging sites before production
- 📝 Review content before publishing
- 🚫 Never commit credentials to version control

**For detailed security information:**
- See [SECURITY.md](../SECURITY.md) for security policy and incident response
- See [SKILL.md](SKILL.md) for operation classifications and security warnings
- Report security issues privately to repository owner (NOT via GitHub issues)

## Resources

- **Ghost Admin API Docs:** https://ghost.org/docs/admin-api/
- **Ghost Content API Docs:** https://ghost.org/docs/content-api/ (read-only public API)
- **Ghost Community:** https://forum.ghost.org
- **Issue Tracker:** https://github.com/chrisagiddings/moltbot-ghost-skill/issues
- **Enhancement Requests:** See open issues for planned features

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:
1. Review security guidelines in SKILL.md
2. Test changes on a staging Ghost site
3. Document new operations with safety classifications
4. Update api-reference.md with any new endpoints

---

**⚠️ Security Notice:** This skill can publish content to the public internet. Always review content before publishing. Test on staging sites when possible. Store API keys securely.
