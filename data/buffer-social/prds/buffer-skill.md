# Buffer Skill for OpenClaw

## Overview

Build an OpenClaw skill that integrates with Buffer's GraphQL API, enabling users to create, schedule, and manage social media posts from the command line or through OpenClaw conversations.

## Goals

1. Create a production-ready CLI tool for Buffer API
2. Support multi-channel posting (Twitter, LinkedIn, Facebook, Instagram, etc.)
3. Enable scheduling and queue management
4. Provide clear documentation and examples
5. Portfolio piece demonstrating GraphQL API integration

## Target Completion

All features complete and tested by end of day (March 3, 2026).

## Technical Stack

- **Language:** Node.js (ESM modules)
- **API:** Buffer GraphQL API (https://developers.buffer.com/)
- **Auth:** API key-based (Bearer token)
- **CLI Framework:** Commander.js
- **HTTP Client:** Axios or fetch
- **Testing:** Vitest
- **Styling:** Chalk for terminal colors

---

## Core Features

### 1. Authentication & Setup

- [x] Store API key securely (`.env` file or config)
- [x] Validate API key on first use
- [x] Clear error messages for auth failures
- [x] `.env.example` template for users

### 2. CLI Commands

#### `buffer profiles`

- [x] List all connected social media profiles
- [x] Show profile ID, service name, username
- [x] Format output clearly (table or list)

**Example output:**

```
Connected Profiles:
✓ Twitter (@learnopenclaw) - ID: abc123
✓ LinkedIn (Ahmad Abugosh) - ID: def456
✓ Facebook (Learn OpenClaw) - ID: ghi789
```

#### `buffer post <text>`

- [x] Create a post with text content
- [x] Options:
  - [x] `--profile <id>` - Single profile
  - [x] `--profiles <ids>` - Comma-separated profile IDs
  - [x] `--all` - Post to all profiles
  - [x] `--time <datetime>` - Schedule for specific time (ISO 8601)
  - [x] `--queue` - Add to queue instead of immediate/scheduled
  - [x] `--image <path>` - Attach image (local file path)
  - [x] `--draft` - Create as idea/draft instead of post
- [x] Validate inputs (text length, file exists, etc.)
- [x] Clear success messages with post IDs/URLs

**Examples:**

```bash
# Immediate post to Twitter
buffer post "Hello world!" --profile twitter

# Schedule for tomorrow 2pm
buffer post "Scheduled content" --profile linkedin --time "2026-03-03T14:00:00Z"

# Multi-channel with image
buffer post "Check this out!" --profiles twitter,linkedin --image ./photo.jpg

# Add to queue
buffer post "Queue this" --profile twitter --queue

# Create draft
buffer post "Draft idea" --profile twitter --draft
```

#### `buffer queue`

- [x] View pending/scheduled posts
- [x] Show: post text (truncated), profile(s), scheduled time
- [x] Option: `--profile <id>` to filter by profile
- [x] Option: `--limit <n>` to show only N posts

**Example output:**

```
Upcoming Posts (5):

1. "Hello world!" → Twitter
   Scheduled: Tomorrow at 9:00 AM

2. "Check out our new feature..." → LinkedIn, Twitter
   Scheduled: Tomorrow at 2:00 PM

...
```

#### `buffer ideas`

- [x] List saved ideas/drafts
- [x] Show text preview, created date
- [x] Option: `--limit <n>`

### 3. GraphQL Integration

#### API Wrapper (`lib/buffer-api.js`)

- [x] GraphQL client setup
- [x] Authentication header injection
- [x] Error handling for:
  - [x] Network errors
  - [x] API errors (rate limits, invalid token, etc.)
  - [x] Validation errors
- [x] Rate limit handling (60 req/min per Buffer docs)

#### Required GraphQL Operations

- [x] **Query: Get Profiles**

  ```graphql
  query GetProfiles {
    profiles {
      id
      service
      username
    }
  }
  ```

- [x] **Mutation: Create Post**

  ```graphql
  mutation CreatePost($input: CreatePostInput!) {
    createPost(input: $input) {
      id
      text
      scheduledAt
      profiles {
        id
        service
      }
    }
  }
  ```

- [x] **Query: Get Scheduled Posts**

  ```graphql
  query GetScheduledPosts($profileId: ID) {
    scheduledPosts(profileId: $profileId) {
      id
      text
      scheduledAt
      profiles {
        service
        username
      }
    }
  }
  ```

- [x] **Mutation: Create Idea**

  ```graphql
  mutation CreateIdea($input: CreateIdeaInput!) {
    createIdea(input: $input) {
      id
      text
    }
  }
  ```

- [x] **Query: Get Ideas**
  ```graphql
  query GetIdeas {
    ideas {
      id
      text
      createdAt
    }
  }
  ```

### 4. File Structure

```
skills/buffer/
├── SKILL.md              # OpenClaw skill documentation
├── README.md             # Project overview
├── package.json          # Dependencies
├── buffer.js             # Main CLI entry point (chmod +x)
├── lib/
│   ├── buffer-api.js    # GraphQL API wrapper
│   ├── auth.js          # Auth handling and validation
│   ├── config.js        # Config file management
│   └── utils.js         # Helper functions (date parsing, formatting)
├── examples/
│   ├── basic-post.js    # Simple post example
│   ├── scheduled-post.js
│   ├── multi-channel.js
│   └── with-image.js
├── tests/
│   ├── api.test.js      # API wrapper tests
│   ├── cli.test.js      # CLI command tests
│   └── utils.test.js    # Utility function tests
├── .env.example         # Template for API key
└── .gitignore           # Ignore .env, node_modules
```

### 5. Error Handling

- [x] Network failures (timeout, offline)
- [x] API errors (401, 403, 429, 500)
- [x] Invalid inputs (missing required fields, invalid dates)
- [x] File not found (for images)
- [x] Rate limit exceeded (clear message + retry suggestion)
- [x] All errors should have:
  - **What failed** (clear description)
  - **Why it failed** (root cause)
  - **How to fix** (actionable suggestion)

**Example error:**

```
❌ Failed to create post

Reason: API authentication failed (401 Unauthorized)

Fix:
1. Check your API key in .env
2. Generate a new key at: https://publish.buffer.com/settings/api
3. Make sure the key starts with "Bearer "

Need help? Visit: https://developers.buffer.com/
```

### 6. Testing

- [x] Unit tests for API wrapper
- [x] Unit tests for utilities (date parsing, validation)
- [x] Integration tests with Buffer API (if possible, or mocked)
- [x] CLI command tests
- [x] Minimum 80% code coverage
- [x] All tests passing

### 7. Documentation

#### SKILL.md

- [x] Quick start guide
- [x] Authentication setup
- [x] Command reference with examples
- [x] Common use cases
- [x] Troubleshooting section
- [x] OpenClaw integration examples

**Example OpenClaw usage:**

```
You: "Post to Buffer: 'Just shipped a new feature! 🚀' to Twitter"

Rose: *executes buffer post command*
✅ Posted to Twitter (@learnopenclaw)
🔗 https://twitter.com/learnopenclaw/status/...
```

#### README.md

- [x] Project overview
- [x] Installation instructions
- [x] Quick start
- [x] API documentation link
- [x] Contributing guidelines

#### Code Comments

- [x] All functions documented with JSDoc
- [x] Complex logic explained
- [x] GraphQL queries documented

### 8. Quality & Polish

- [x] Consistent code style (use Prettier/ESLint if time permits)
- [x] Meaningful variable names
- [x] No hardcoded values (use constants/config)
- [x] Helpful terminal output (colors, emojis, clear formatting)
- [x] Loading indicators for API calls (use `ora` or similar)
- [x] Success confirmations with actionable next steps

---

## Dependencies

```json
{
  "name": "buffer-skill",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "buffer": "./buffer.js"
  },
  "dependencies": {
    "commander": "^12.0.0",
    "axios": "^1.6.0",
    "dotenv": "^16.4.0",
    "chalk": "^5.3.0",
    "ora": "^8.0.0"
  },
  "devDependencies": {
    "vitest": "^1.3.0"
  },
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

---

## Implementation Order

### Phase 1: Foundation (Tasks 1-10)

1. [x] Initialize project structure
2. [x] Set up package.json with dependencies
3. [x] Create `.env.example` and `.gitignore`
4. [x] Implement `lib/config.js` for API key management
5. [x] Implement `lib/auth.js` for validation
6. [x] Create basic CLI skeleton with Commander
7. [x] Implement `buffer profiles` command (basic version)
8. [x] Set up GraphQL client in `lib/buffer-api.js`
9. [x] Implement GetProfiles query
10. [x] Test profiles command end-to-end

### Phase 2: Core Posting (Tasks 11-20)

11. [x] Implement `lib/utils.js` with date parsing and validation
12. [x] Implement CreatePost mutation in API wrapper
13. [x] Create `buffer post` command with basic options
14. [x] Add `--profile` option
15. [x] Add `--time` scheduling option
16. [x] Add `--queue` option
17. [x] Add `--profiles` (multi-channel) option
18. [x] Add `--all` option
19. [x] Test posting to single profile
20. [x] Test multi-channel posting

### Phase 3: Images & Ideas (Tasks 21-28)

21. [x] Implement image upload support (if Buffer API supports it, or document limitation)
22. [x] Add `--image` option to post command
23. [x] Implement CreateIdea mutation
24. [x] Add `--draft` option to post command
25. [x] Implement `buffer ideas` command
26. [x] Implement GetIdeas query
27. [x] Test idea creation
28. [x] Test image posting (or document workaround)

### Phase 4: Queue Management (Tasks 29-33)

29. [x] Implement GetScheduledPosts query
30. [x] Create `buffer queue` command
31. [x] Add `--profile` filter option
32. [x] Add `--limit` option
33. [x] Test queue viewing

### Phase 5: Error Handling (Tasks 34-40)

34. [x] Add network error handling to API wrapper
35. [x] Add rate limit detection and friendly errors
36. [x] Add auth error handling (401, 403)
37. [x] Add input validation for all commands
38. [x] Add file existence check for images
39. [x] Add date parsing validation
40. [x] Test all error scenarios

### Phase 6: Testing (Tasks 41-48)

41. [x] Write API wrapper unit tests
42. [x] Write utils unit tests
43. [x] Write CLI command tests
44. [x] Write integration tests (mocked or real API)
45. [x] Ensure 80%+ coverage
46. [x] Fix failing tests
47. [x] Add test documentation
48. [x] All tests passing

### Phase 7: Documentation (Tasks 49-56)

49. [x] Write SKILL.md with quick start
50. [x] Add command reference to SKILL.md
51. [x] Add examples to SKILL.md
52. [x] Add troubleshooting section
53. [x] Write README.md
54. [x] Add JSDoc comments to all functions
55. [x] Create example files (examples/\*.js)
56. [x] Add inline code comments

### Phase 8: Polish (Tasks 57-63)

57. [x] Add colored output with Chalk
58. [x] Add loading indicators with Ora
59. [x] Format all output clearly (tables, lists)
60. [x] Add success messages with next steps
61. [x] Make buffer.js executable (chmod +x)
62. [x] Test full workflow end-to-end
63. [x] Final cleanup and verification

### Phase 9: GitHub & Deployment (Tasks 64-68)

64. Initialize git repository
65. Create GitHub repo: `buffer-skill`
66. Push to GitHub
67. Add GitHub URL to SKILL.md and README
68. Tag release v1.0.0

---

## Acceptance Criteria

### Must Have (Critical)

- ✅ CLI works: `buffer profiles`, `buffer post`, `buffer queue`, `buffer ideas`
- ✅ Authentication working with Buffer API
- ✅ Can create immediate posts
- ✅ Can schedule posts for future time
- ✅ Multi-channel posting works
- ✅ Queue management works
- ✅ Clear error messages for all failures
- ✅ Tests written and passing
- ✅ Documentation complete (SKILL.md, README.md)
- ✅ Code pushed to GitHub

### Nice to Have (If Time Permits)

- Image upload support
- Idea management (create/list)
- Profile aliases (save "twitter" instead of profile ID)
- Config file for default profiles
- Prettier/ESLint setup

### Out of Scope

- Edit/delete posts (not supported by Buffer API yet)
- TikTok support (not available in API)
- OAuth flow (API key is simpler)
- Web UI (CLI only)

---

## Definition of Done

A task is complete when:

1. Code is written and working
2. Tests are passing (if applicable)
3. Documentation is updated
4. Committed to git with clear message
5. Checkbox is checked in this PRD

The project is complete when:

1. All 68 tasks are checked off
2. All tests passing
3. End-to-end workflow tested manually
4. Code pushed to GitHub
5. SKILL.md and README.md complete

---

## Buffer API Reference

**Base URL:** `https://api.buffer.com/graphql` (verify in docs)

**Authentication:**

```
Authorization: Bearer YOUR_API_KEY
```

**Get API Key:** https://publish.buffer.com/settings/api

**Developer Docs:** https://developers.buffer.com/

**Rate Limits:** 60 requests per minute per user

**Supported Channels:**

- Instagram
- Threads
- LinkedIn
- X/Twitter
- Facebook
- Google Business Profiles
- Mastodon
- YouTube
- Pinterest
- Bluesky

**Not Supported:**

- TikTok

---

## Success Metrics

By end of project, we should have:

- ✅ Working CLI tool
- ✅ 68/68 tasks complete
- ✅ Tests passing (80%+ coverage)
- ✅ Documentation complete
- ✅ GitHub repo created
- ✅ Portfolio-ready project

---

## Notes

- Buffer's API is GraphQL (not REST), so structure queries/mutations accordingly
- API is in beta, so some features may be limited
- Focus on what's supported now (create posts, schedule, queue, ideas)
- Don't spend time on unsupported features (edit/delete)
- This is a portfolio piece for Ahmad's Buffer job application, so quality matters!
- Ahmad trusts Rose to fix issues independently - no need to ask for permission

---

## Emergency Contact

If RALPH gets stuck or needs help:

- Rose will monitor progress via RALPH Telegram updates
- Rose will debug and fix issues autonomously
- Goal: Complete by end of March 3, 2026 (tomorrow)

Let's ship this! 🚀
