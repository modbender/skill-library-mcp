---
name: omadeus
description: Manage Omadeus entities via the Omadeus REST API.
homepage: https://omadeus.com/
metadata: {"clawdbot":{"emoji":"📋"}}
---

# Omadeus Skill

Manage Omadeus entities directly from Clawdbot.

## Usage

All commands use curl to hit the omadeus REST API.

### List nuggets
```bash
curl -X LIST -s "https://milestone.xeba.ir/dolphin/apiv1/nuggetviews?take=25&zone=inbox&kind=!task"
```
## Notes

- you should use the custome method names in API calls like that 'list', 'create' ...
- entities can be found in the omadeus URL or via the list commands
- The API key and token provide full access to your Trello account - keep them secret!
- Rate limits: 300 requests per 10 seconds per 
- endpoints are limited to 100 requests per 900 seconds

## Examples
```bash
curl -X LIST -s "https://milestone.xeba.ir/dolphin/apiv1/nuggetviews?take=25&zone=inbox&kind=!task"
```
