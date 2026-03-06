---
name: xqueue
description: File-based X/Twitter post scheduler. Drop tweets into day/time folders, they post automatically. No frontend, no app — your file system is the UI.
metadata: {"openclaw":{"requires":{"env":["X_CONSUMER_KEY","X_CONSUMER_SECRET","X_ACCESS_TOKEN","X_ACCESS_TOKEN_SECRET"],"bins":["python3"]},"permissions":{"filesystem":"read/write within xqueue/ directory","network":"api.twitter.com, upload.twitter.com","keychain":"optional macOS Keychain if XQUEUE_KEYCHAIN_ACCOUNT is set"}}}
---

# XQueue

A file-based post scheduler for X (Twitter). Your file system is the UI.

## How It Works

Create a folder structure with days and times. Drop tweet files into the time slots. A cron job checks every 15 minutes — if it's the right day and time and there's content, it posts and cleans up.

```
xqueue/
  config.json
  backlog/
    ebook-launch-thread.md
    ai-tools-roundup.md
  Sunday/
    10am/
      my-tweet.md
      photo.jpg
  Monday/
    9am/
      thread-about-shipping.md
    12pm/
    5pm/
  Tuesday/
    ...
```

The schedule cycles weekly. Monday's 9am slot fires every Monday at 9am. If the folder is empty, it pulls the oldest file from `backlog/` (sorted alphabetically). If there's content in the slot, it posts that and backlog waits. This means you can schedule up to a week of specific content, and dump everything else in backlog — it'll fill empty slots automatically.

After posting, files are deleted (by default) so they don't repeat.

## Setup

Run the setup command to create your queue:

```bash
python3 xqueue-setup.py
```

This asks you:
1. How many times per day do you want to post?
2. What times? (or let it pick optimal times)
3. What timezone?
4. Any X communities to post to?
5. Thread separator preference (default: ---)
6. Delete after posting? (recommended yes — if off, posts may send twice)

Creates the full folder structure + config.json.

## Tweet Format

### Simple tweet
Just write the text in a `.md` or `.txt` file:

```
This is my tweet. It can be up to 280 characters.
```

### Tweet with community
Start with `Post to [community name]:` on the first line:

```
Post to Build in Public: Just shipped my first ClawHub skill. File-based tweet scheduler, no frontend needed.
```

### Thread
One file, tweets separated by your configured separator (default `---`):

```
I built a file-based tweet scheduler with no frontend. Your filesystem is the UI.
---
Drop a .md file into Monday/9am/ and a cron job posts it. Empty slot? It pulls from a backlog/ folder automatically.
---
No database, no app, no dashboard. Just folders and text files. Sometimes the simplest architecture wins.
```

### Tweet with media
Put image/video files in the same time folder as the tweet. Supported: JPG, PNG, GIF (under 5MB for images, 15MB for GIF).

```
9am/
  tweet.md        ← the text
  progress.png    ← gets attached
```

If multiple media files exist, they attach in alphabetical order (max 4 per tweet).

## Config

`xqueue/config.json`:

```json
{
  "timezone": "America/Chicago",
  "separator": "---",
  "deleteAfterPost": true,
  "communities": {
    "Build in Public": "community_id",
    "Indie Hackers": "community_id"
  },
  "logFile": "xqueue/posted.log",
  "dryRun": false
}
```

During setup, paste the community URL (like `x.com/i/communities/123456`) or the numeric ID directly. The script extracts the ID and asks for a display name. Plain names without an ID are rejected — everything needed to post is captured upfront.

## Backlog

The `xqueue/backlog/` folder holds tweets that aren't scheduled for a specific slot. When the cron fires and a time slot is empty, it pulls the oldest file from backlog (alphabetical sort — prefix with numbers like `01-`, `02-` to control order).

This lets you batch-write content without worrying about fitting it into exactly the right number of weekly slots. Schedule what's time-sensitive, backlog the rest.

## Cron Integration

The skill includes a cron job that runs every 15 minutes:
- Checks current day + time against folder structure
- If slot has content → post it
- If slot is empty → pull oldest from `backlog/`
- If both are empty → skip
- Logs results to posted.log
- Deletes posted files (if deleteAfterPost is on)

## What Goes Where

| You want to...                        | Do this                                               |
| ------------------------------------- | ----------------------------------------------------- |
| Schedule a tweet for Tuesday 9am      | Drop a .md file in `xqueue/Tuesday/9am/`              |
| Post a thread                         | One .md file with `---` between tweets                |
| Attach an image                       | Put the image file in the same folder as the .md file |
| Post to a community                   | Start text with `Post to Community Name:`             |
| Reorder posts                         | Move files between time folders                       |
| Skip a time slot                      | Leave the folder empty                                |
| See what's queued                     | Browse the xqueue folder                              |
| See what already posted               | Check xqueue/posted.log                               |
| Queue content without a specific time | Drop it in `xqueue/backlog/`                          |
| Control backlog order                 | Prefix filenames: `01-first.md`, `02-second.md`       |

## Important

- **deleteAfterPost: true** (default) means each file posts once then gets removed. If you turn this off, the same content will post again next week when the cycle repeats.
- Tweets over 280 characters are rejected (logged as error, not posted).
- Thread tweets are each checked for 280 char limit individually.
- Empty folders are silently skipped.
- The cron checks every 15 minutes, so posts go out within 0-15 min of the scheduled time.
