---
name: asosuite
description: Do App Store Optimization (ASO) with the ASO Suite CLI across iPhone, iPad, Mac, Apple TV, Apple Watch, and VisionOS by finding keywords with popularity/difficulty data, tracking keyword position over time, and monitoring ratings, editorial features, and chart appearances.
homepage: https://www.asosuite.com/
metadata: {"openclaw":{"emoji":"📈","requires":{"bins":["asosuite"]},"install":[{"id":"npm","kind":"node","package":"asosuite","bins":["asosuite"],"label":"Install asosuite (npm)"}]}}
---

# ASO Suite CLI

Use `asosuite` to run ASO workflows across iPhone, iPad, Mac, Apple TV, Apple Watch, and VisionOS apps: discover keywords with popularity and difficulty data, track keyword position over time, and monitor ratings, editorial features, and chart appearances with machine-readable output.

## Setup

Install:

```bash
npm install -g asosuite
asosuite help
```

Authenticate:

```bash
asosuite login
```

## JSON-first rule

For easier parsing, always pass `--json` on every command that supports it.
Commands that do not take `--json`: `login`, `logout`.

## Defaults

- `region=US`
- `platform=iphone`
- `period=30` for `charts` and `ratings`
- Supported platforms: iPhone (`iphone`), iPad (`ipad`), Mac (`mac`), Apple TV (`appletv`), Apple Watch (`watch`), VisionOS (`vision`)

## Command reference (all commands)

- `asosuite login`
- `asosuite logout`
- `asosuite subscription [--json]`
- `asosuite search-apps [--json] [--region <REGION>] [--platform <PLATFORM>] <query...>`
- `asosuite list-apps [--json]`
- `asosuite keywords [--json] [--region <REGION>] [--platform <PLATFORM>] [--app <APP_ID_OR_URL>] <keyword...>`
- `asosuite track-app [--json] [--region <REGION>] [--platform <PLATFORM>] --app <APP_ID_OR_URL>`
- `asosuite untrack-app [--json] [--region <REGION>] [--platform <PLATFORM>] --app <APP_ID_OR_URL>`
- `asosuite plan-app [--json] --name <APP_NAME> [--id <PLANNED_APP_ID>] [--region <REGION>] [--platform <PLATFORM>]`
- `asosuite unplan-app [--json] --id <PLANNED_APP_ID> [--region <REGION>] [--platform <PLATFORM>]`
- `asosuite tracked-keywords list [--json] [--region <REGION>] [--platform <PLATFORM>] [--page <NUMBER>] [--sort <FIELD>] [--order <asc|desc>] --app <APP_ID_OR_URL_OR_PLANNED_ID>`
- `asosuite tracked-keywords add [--json] [--region <REGION>] [--platform <PLATFORM>] --app <APP_ID_OR_URL_OR_PLANNED_ID> <keyword...>`
- `asosuite tracked-keywords remove [--json] [--region <REGION>] [--platform <PLATFORM>] --app <APP_ID_OR_URL_OR_PLANNED_ID> <keyword...>`
- `asosuite related-apps list [--json] --app <APP_ID_OR_URL> [--platform <PLATFORM>]`
- `asosuite related-apps add [--json] --app <APP_ID_OR_URL> --related <APP_ID_OR_URL> [--platform <PLATFORM>] [--region <REGION>]`
- `asosuite related-apps remove [--json] --app <APP_ID_OR_URL> --related <APP_ID_OR_URL> [--platform <PLATFORM>]`
- `asosuite events list [--json] [--app <APP_ID_OR_URL>]`
- `asosuite events add [--json] --text <TEXT> [--date <YYYY-MM-DD>] [--app <APP_ID_OR_URL>]`
- `asosuite events delete [--json] <EVENT_ID>`
- `asosuite charts [--json] [--period <7|30|90>] [--region <REGION> | --regions <REGION,REGION>] [--platform <PLATFORM>] --app <APP_ID_OR_URL>`
- `asosuite features [--json] [--platform <PLATFORM>] --app <APP_ID_OR_URL>`
- `asosuite ratings [--json] [--period <7|30|90>] [--platform <PLATFORM>] --app <APP_ID_OR_URL>`

## Common ASO commands (JSON)

```bash
# Account info
asosuite subscription --json

# Discover apps
asosuite search-apps --json --region US --platform iphone "chat gpt"

# Tracked/planned apps
asosuite list-apps --json
asosuite track-app --json --app 6448311069 --platform iphone --region US
asosuite untrack-app --json --app 6448311069 --platform iphone --region US
asosuite plan-app --json --name "My Next App" --platform iphone --region US
asosuite unplan-app --json --id my-next-app --platform iphone --region US

# Keyword research + tracking
asosuite keywords --json --region US --platform iphone --app 6448311069 "step counter" "water tracker"
asosuite tracked-keywords list --json --app 6448311069 --platform iphone --region US --page 1 --sort relevance --order desc
asosuite tracked-keywords add --json --app 6448311069 --platform iphone --region US "step counter" "water tracker"
asosuite tracked-keywords remove --json --app 6448311069 --platform iphone --region US "step counter" "water tracker"

# Related apps / competitors
asosuite related-apps list --json --app 6448311069 --platform iphone
asosuite related-apps add --json --app 6448311069 --related 333903271 --platform iphone --region US
asosuite related-apps remove --json --app 6448311069 --related 333903271 --platform iphone

# Charts, featuring, ratings
asosuite charts --json --app 6448311069 --platform iphone --period 30
asosuite features --json --app 6448311069 --platform iphone
asosuite ratings --json --app 6448311069 --platform iphone --period 30

# Events
asosuite events list --json --app 6448311069
asosuite events add --json --app 6448311069 --text "Started ASO for 'keyword x'" --date 2026-02-25
asosuite events delete --json 123
```

## Notes

- `tracked-keywords list` returns up to 50 keywords per page.
- Sort fields for `tracked-keywords list`: `keyword`, `relevance`, `popularity`, `difficulty`, `position`, `lastUpdate`.
- Server limits:
  - `keywords`: up to 50 keywords per request
  - `tracked-keywords add`/`tracked-keywords remove`: up to 200 keywords per request
