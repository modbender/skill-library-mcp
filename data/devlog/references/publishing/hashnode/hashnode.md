# Hashnode Publishing Reference

## Overview

Hashnode exposes a GraphQL API for programmatic blog publishing. Posts are authored in markdown and published to a user's Hashnode publication.

## API Endpoint

```
https://gql.hashnode.com
```

## Authentication

Requires a **Personal Access Token (PAT)**.

- Generate at: https://hashnode.com/settings/developer
- Pass via `Authorization` header: `Authorization: <PAT>`

### Required Environment Variables

| Variable | Description |
|---|---|
| `HASHNODE_PAT` | Personal Access Token from Hashnode developer settings |
| `HASHNODE_PUBLICATION_ID` | The publication (blog) to publish to |

### Finding Your Publication ID

1. Go to your Hashnode blog dashboard
2. The publication ID is in the URL: `https://hashnode.com/<username>/dashboard` — or query it via the API:

```graphql
query {
  me {
    publications(first: 10) {
      edges {
        node {
          id
          title
          url
        }
      }
    }
  }
}
```

## Publishing Mutation

```graphql
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) {
    post {
      id
      title
      url
      slug
    }
  }
}
```

### Input Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | String | Yes | Post title |
| `contentMarkdown` | String | Yes | Full markdown body |
| `publicationId` | ID | Yes | Target publication |
| `tags` | [TagInput] | No | Array of `{ slug, name }` objects |
| `coverImageOptions` | CoverImageInput | No | `{ coverImageURL: "https://..." }` |
| `originalArticleURL` | String | No | Canonical URL for cross-posts |
| `subtitle` | String | No | Post subtitle |

### Example curl

```bash
curl -s -X POST https://gql.hashnode.com \
  -H "Content-Type: application/json" \
  -H "Authorization: ${HASHNODE_PAT}" \
  -d '{
    "query": "mutation PublishPost($input: PublishPostInput!) { publishPost(input: $input) { post { id title url slug } } }",
    "variables": {
      "input": {
        "title": "My Post",
        "contentMarkdown": "# Hello World",
        "publicationId": "'"${HASHNODE_PUBLICATION_ID}"'",
        "tags": []
      }
    }
  }'
```

## Response

Success:
```json
{
  "data": {
    "publishPost": {
      "post": {
        "id": "...",
        "title": "My Post",
        "url": "https://blog.example.com/my-post",
        "slug": "my-post"
      }
    }
  }
}
```

Error:
```json
{
  "errors": [
    {
      "message": "Unauthenticated",
      "extensions": { "code": "UNAUTHENTICATED" }
    }
  ]
}
```

## Cover Images

The `publishPost` mutation accepts an optional `coverImageOptions` field to set a header image for the blog post. This image appears at the top of the post on Hashnode and in social media previews.

### Requirements

- The image must be a **publicly accessible URL** (Hashnode fetches it server-side)
- Recommended dimensions: **1200×630px** (landscape, 1.91:1 ratio) — optimized for social sharing (Open Graph)
- Supported formats: JPEG, PNG, WebP
- Keep file size under 5 MB

### GraphQL Field

```graphql
coverImageOptions: {
  coverImageURL: "https://example.com/my-cover-image.png"
}
```

This is passed inside the `input` object alongside `title`, `contentMarkdown`, etc. See the example curl above for placement.

### Generating Cover Images

If the agent has image generation capabilities (e.g. an image generation tool, skill or MCP server):

1. **Generate** a landscape image (1200×630) visually relevant to the blog topic
2. **Upload** it to any publicly accessible host (image CDN, S3 bucket, GitHub raw URL, drive etc.)
3. **Pass** the URL to `publish.sh` with the `--cover-image <url>` flag

Good cover images are abstract or thematic — architecture diagrams, code-themed visuals, or conceptual illustrations. Avoid putting the blog title as text in the image (Hashnode overlays the title automatically).

If the agent cannot generate images, skip this step entirely. The blog publishes fine without a cover image.

## Script

Use `publish.sh` in this directory to publish a markdown file. See the script header for usage.
