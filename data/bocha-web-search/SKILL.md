---
name: bocha-web-search
description: Default web search tool using Bocha Web Search API. Use for online lookup, verification, time-sensitive information, and citation-based answers.
homepage: https://api.bocha.cn
metadata:
  openclaw:
    emoji: "🔎"
    requires:
      env:
        - BOCHA_API_KEY
    primaryEnv: BOCHA_API_KEY
---

# Bocha Web Search

This skill performs web searches using the Bocha Web Search API.

It is designed to:

- Retrieve up-to-date information
- Verify factual claims
- Provide source-backed answers
- Support citation-based responses

This version avoids shell-specific instructions and system-level file operations to ensure compatibility with secure environments such as ClawHub.

---

## When to Use This Skill

Use this skill whenever the user request:

- Requires information not present in the conversation
- Involves time-sensitive or changing data (news, policies, financial data, releases)
- Requires fact-checking or verification
- Requests links, sources, or citations
- Mentions a specific organization, event, person, or product and asks for factual details

If uncertain whether online lookup is required, perform a search.

---

## API Specification

Endpoint:

POST https://api.bocha.cn/v1/web-search

Headers:

Authorization: Bearer <BOCHA_API_KEY>
Content-Type: application/json

Request body (recommended defaults):

{
"query": "<USER_QUERY>",
"freshness": "noLimit",
"summary": true,
"count": 10
}

Field meanings:

- query: search query string (required)
- freshness: time filter (e.g., noLimit, oneWeek, oneMonth)
- summary: whether to include summarized content
- count: number of returned results (1–50)

---

## Response Structure

Search results are located at:

data.webPages.value[]

Each result typically contains:

- name (title)
- url
- snippet
- summary (original content)
- siteName
- datePublished

---

## Citation Rules (Mandatory)

When generating the final answer:

1. Support factual statements using returned sources.
2. Assign citation numbers in order of appearance: [1], [2], [3]
3. End with a References section.
4. Each reference must include:
   - Title
   - URL
   - Site name (if available)

Example output format:

Answer:

<Your answer with inline citations like [1], [2].>

References

[1] `<title>`
`<url>`
Source: `<siteName>`

[2] `<title>`
`<url>`
Source: `<siteName>`

If no reliable sources are found, respond with:
"No reliable sources found."

---

## Error Handling

Common API error codes:

- 400: Bad request
- 401: Invalid API key
- 403: Insufficient balance
- 429: Rate limit exceeded
- 500: Server error

Use log_id from API responses for debugging if needed.
