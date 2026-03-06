---
name: volcengine-web-search
description: Using volcengine web_search.py script to search web and get the result, prepare clear and specific `query`.Run the script `python scripts/web_search.py "query"`. Organize the answer based on the returned summary list, do not add or guess content.
license: Complete terms in LICENSE.txt
---

# Web Search

## Scenarios

When you need to quickly get summary information from public web pages, use this skill to call the `web_search` function.

## Steps

1. Prepare a clear and specific `query`.
2. Run the script `python scripts/web_search.py "query"`. Before running, navigate to the corresponding directory.
3. Organize the answer based on the returned summary list, do not add or guess content.

## Authentication and Credentials

- First, it will try to read the `VOLCENGINE_ACCESS_KEY` and `VOLCENGINE_SECRET_KEY` environment variables.
- If not configured, it will try to use VeFaaS IAM temporary credentials.

## Output Format

- The console will output the summary list, up to 5 items.
- If the call fails, it will print the error response.

## Examples

```bash
python scripts/web_search.py "2026 latest version of Python"
```
