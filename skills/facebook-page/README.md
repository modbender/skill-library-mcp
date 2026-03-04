# facebook-page

Facebook Page automation skill for [OpenClaw](https://github.com/openclaw/openclaw).

Interact with any Facebook Page feature via the Meta Graph API — posting, scheduling, insights, events, comments, and more. The agent constructs API calls inline from your natural language requests. No scripts needed.

## How It Works

1. Loads your credentials from `~/.config/fb-page/credentials.json`
2. Figures out the right Graph API call from what you ask
3. Executes it inline — no script files required
4. If a permission is missing, tells you exactly which one to add and where

## What You Can Ask

Anything the Meta Graph API supports, including:

- **Posts** — text, image, link, video, scheduled
- **Comments** — get, reply, hide, delete
- **Insights** — page stats, post performance
- **Events** — list, create
- **Page info** — name, followers, about
- **Token management** — refresh expired tokens

## Setup (One Time)

You need: **Page ID**, **App ID**, **App Secret**, **short-lived User Access Token**.

The agent will exchange your short-lived token for a never-expiring Page token and save it to `~/.config/fb-page/credentials.json`. File permissions are restricted immediately after saving.

## Credentials File

Location: `~/.config/fb-page/credentials.json`

| Field | Description | Used when |
|---|---|---|
| `FB_PAGE_ID` | Your Facebook Page ID | All API calls |
| `FB_PAGE_TOKEN` | Never-expiring Page Access Token | All API calls |
| `FB_APP_ID` | Meta Developer App ID | One-time token exchange only |
| `FB_APP_SECRET` | Meta Developer App Secret | One-time token exchange only |

> This skill only communicates with `graph.facebook.com`. No data is sent to any other service.

## Requirements

- **Windows:** PowerShell 5.1+ (built-in) or `pwsh`
- **macOS / Linux:** PowerShell Core (`pwsh`)
- A Meta Developer App with the required permissions

## Permissions Reference

| Permission | Required for |
|---|---|
| `pages_manage_posts` | Post, delete, schedule |
| `pages_read_engagement` | Read posts, comments, insights |
| `pages_show_list` | List managed pages |
| `pages_manage_metadata` | Update page settings |
| `pages_manage_engagement` | Moderate comments |
| `pages_read_user_content` | Read visitor posts and comments |

## Platform Support

Works on **Windows**, **macOS**, and **Linux**.

## License

MIT
