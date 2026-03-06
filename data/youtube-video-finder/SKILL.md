---
name: Recover deleted YouTube videos
description: Searches multiple online archives to find and recover deleted YouTube videos, metadata, and comments using a video ID.
author: upintheairsheep
version: 1.0.0
url: https://findyoutubevideo.thetechrobo.ca/api/v5/{videoid}
method: GET
params:
  - name: videoid
    type: string
    description: The exact 11-character YouTube video ID to search for. DO NOT pass a full URL.
    required: true
  - name: includeRaw
    type: boolean
    description: Set to true to include the rawraw field for advanced debugging. Otherwise, omit or set to false to improve speed.
    required: false
  - name: stream
    type: boolean
    description: Set to true to stream JSONL. Keep false for standard agent data parsing.
    required: false
---

# YouTube Video Finder Instructions

Use this skill whenever a user asks to find, recover, or check the archive status of a deleted, missing, or private YouTube video. 

## Execution Steps:
1. **Extract the Video ID:** Isolate the 11-character ID from the URL or text provided by the user (e.g., for `youtube.com/watch?v=dQw4w9WgXcQ`, the ID is `dQw4w9WgXcQ`). Pass *only* this ID into the `videoid` parameter.
2. **Parameters:** Omit the `includeRaw` and `stream` parameters unless the user specifically asks for raw metadata or debugging data. 

## Interpreting the Response:
* **Initial Check:** Look at the `status` field. If it returns `bad.id`, stop and inform the user that the 11-character ID is invalid.
* **The Verdict:** Check the `verdict` object. Read the `human_friendly` string to immediately understand the overall result. Pay attention to the boolean flags `video`, `metaonly`, and `comments` to know exactly what was recovered.
* **Finding the Links:** Iterate through the `keys` array (which contains service objects like GhostArchive or Wayback Machine). 
    * If a service object has `archived: true`, look inside its `available` list.
    * Extract the `url` from the Link Objects to give to the user.
    * Take note of `maybe_paywalled` (boolean) or `note` (string) for context on how to access the link.

## Output Formatting:
Present your findings in a clear, friendly, and structured manner. 
* If the video is fully found, provide the direct links immediately. 
* If only metadata or comments were archived, clarify that the actual video file could not be recovered. 
* Mention which service(s) successfully held the archive.