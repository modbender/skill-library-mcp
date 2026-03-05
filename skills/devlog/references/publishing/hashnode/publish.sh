#!/usr/bin/env bash
# publish.sh — Publish a markdown file to Hashnode via their GraphQL API.
#
# Usage:
#   ./publish.sh <markdown-file> <title> [--cover-image <url>]
#
# Required environment variables:
#   HASHNODE_PAT             — Personal Access Token from https://hashnode.com/settings/developer
#   HASHNODE_PUBLICATION_ID  — Target publication ID
#
# Options:
#   --cover-image <url>      — Publicly accessible URL for the blog header image
#
# Output: Published post URL on stdout.
# Exit code: 0 on success, non-zero on failure.
# Requires: curl, jq

set -euo pipefail

MARKDOWN_FILE=""
TITLE=""
COVER_IMAGE_URL=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --cover-image)
      COVER_IMAGE_URL="${2:-}"
      if [[ -z "$COVER_IMAGE_URL" ]]; then
        echo "Error: --cover-image requires a URL argument" >&2
        exit 1
      fi
      shift 2
      ;;
    *)
      if [[ -z "$MARKDOWN_FILE" ]]; then
        MARKDOWN_FILE="$1"
      elif [[ -z "$TITLE" ]]; then
        TITLE="$1"
      else
        echo "Error: unexpected argument: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

if [[ -z "$MARKDOWN_FILE" || -z "$TITLE" ]]; then
  echo "Usage: publish.sh <markdown-file> <title> [--cover-image <url>]" >&2
  exit 1
fi

if [[ ! -f "$MARKDOWN_FILE" ]]; then
  echo "Error: File not found: $MARKDOWN_FILE" >&2
  exit 1
fi

if ! command -v curl &>/dev/null; then
  echo "Error: curl is required but not installed." >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed." >&2
  exit 1
fi

if [[ -z "${HASHNODE_PAT:-}" ]]; then
  echo "Error: HASHNODE_PAT environment variable is not set." >&2
  echo "Generate a token at https://hashnode.com/settings/developer" >&2
  exit 1
fi

if [[ -z "${HASHNODE_PUBLICATION_ID:-}" ]]; then
  echo "Error: HASHNODE_PUBLICATION_ID environment variable is not set." >&2
  exit 1
fi

CONTENT=$(cat "$MARKDOWN_FILE")

# Build the GraphQL payload using jq for proper JSON escaping
if [[ -n "$COVER_IMAGE_URL" ]]; then
  PAYLOAD=$(jq -n \
    --arg title "$TITLE" \
    --arg content "$CONTENT" \
    --arg pubId "$HASHNODE_PUBLICATION_ID" \
    --arg coverUrl "$COVER_IMAGE_URL" \
    '{
      query: "mutation PublishPost($input: PublishPostInput!) { publishPost(input: $input) { post { id title url slug } } }",
      variables: {
        input: {
          title: $title,
          contentMarkdown: $content,
          publicationId: $pubId,
          coverImageOptions: { coverImageURL: $coverUrl },
          tags: []
        }
      }
    }')
else
  PAYLOAD=$(jq -n \
    --arg title "$TITLE" \
    --arg content "$CONTENT" \
    --arg pubId "$HASHNODE_PUBLICATION_ID" \
    '{
      query: "mutation PublishPost($input: PublishPostInput!) { publishPost(input: $input) { post { id title url slug } } }",
      variables: {
        input: {
          title: $title,
          contentMarkdown: $content,
          publicationId: $pubId,
          tags: []
        }
      }
    }')
fi

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://gql.hashnode.com \
  -H "Content-Type: application/json" \
  -H "Authorization: ${HASHNODE_PAT}" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [[ "$HTTP_CODE" -lt 200 || "$HTTP_CODE" -ge 300 ]]; then
  echo "Error: HTTP $HTTP_CODE from Hashnode API" >&2
  echo "$BODY" >&2
  exit 1
fi

# Check for GraphQL errors
ERRORS=$(echo "$BODY" | jq -r '.errors // empty')
if [[ -n "$ERRORS" && "$ERRORS" != "null" ]]; then
  ERROR_MSG=$(echo "$BODY" | jq -r '.errors[0].message // "Unknown error"')
  echo "Error: Hashnode API returned: $ERROR_MSG" >&2
  exit 1
fi

# Extract the published URL
POST_URL=$(echo "$BODY" | jq -r '.data.publishPost.post.url // empty')
if [[ -z "$POST_URL" ]]; then
  echo "Error: Could not extract post URL from response" >&2
  echo "$BODY" >&2
  exit 1
fi

echo "$POST_URL"
