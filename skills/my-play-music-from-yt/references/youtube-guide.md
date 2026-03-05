# YouTube Page Element Identification Guide

How to read `playwright-cli snapshot` output and find the right elements on YouTube pages.

## YouTube Homepage

After `playwright-cli -s=music_player open "https://www.youtube.com" --headed --persistent`:

**Search bar** — the primary target:

```yaml
- combobox "搜尋" [ref=e34]       # Chinese locale
- combobox "Search" [ref=e34]     # English locale
```

**Search button** (alternative to pressing Enter):

```yaml
- button "Search" [ref=e35]
```

## Search Results Page

After searching, the snapshot contains mixed result types. Identify them by structure:

### Single Video

Look for a `heading` + `link` with a video title and duration:

```yaml
- heading "Artist【Song Title】Official MV 4 分鐘 29 秒" [level=3] [ref=eXXX]:
    - link "Artist【Song Title】Official MV ..." [ref=eYYY]:
        - /url: /watch?v=VIDEO_ID
```

Click the `link` ref to play.

### Mix (Auto-generated Playlist)

YouTube creates a "Mix" for popular artists. Look for `"Mix - [Artist]"`:

```yaml
- heading "Mix - 周杰倫" [level=3] [ref=eXXX]:
    - link "Mix - 周杰倫" [ref=eYYY]:
        - /url: /watch?v=...&list=RDEM...&start_radio=1
```

**Prefer Mix links for artist requests** — they provide continuous playback of related songs.

### User Playlist

Playlists show a video count badge:

```yaml
- generic [ref=eXXX]: 13 部影片        # "13 videos" badge
- heading "Playlist Title" [level=3]:
    - link "Playlist Title" [ref=eYYY]:
        - /url: /watch?v=...&list=PL...
```

### Channel Card

Artist/channel cards appear at the top of results for artist searches:

```yaml
- link "Artist Name ... @handle•NNNK subscribers ..." [ref=eXXX]:    # English locale
    - /url: /@handle
- link "Artist Name ... @handle•NNN萬位訂閱者 ..." [ref=eXXX]:      # Chinese locale
    - /url: /@handle
```

Do NOT click the channel card itself (it goes to the channel page, not music). Instead look for the Mix or playlist results below it.

### Sponsored / Ad Results

Ads have a `"贊助商廣告"` (Sponsored) badge:

```yaml
- img "贊助商廣告" [ref=eXXX]
```

Skip these results; scroll past them to find organic results.

## Video Player Page

After clicking a video/mix, the player page snapshot contains:

### Player Controls

```yaml
- button "Play (k)" [ref=eXXX]        # or "Pause (k)" when playing
- button "Next (SHIFT+n)" [ref=eXXX]
- button "Previous" [ref=eXXX]
- button "Mute (m)" [ref=eXXX]
```

### Ad Overlay

When an ad is playing before the video, the snapshot structure changes significantly. Normal player controls (Pause, Next) may be absent or replaced by ad-specific elements.

**Skip button variations** — match by partial text containing "skip", "Skip", or "略過":

```yaml
- button "Skip Ad" [ref=eXXX]
- button "Skip Ads" [ref=eXXX]
- button "略過廣告" [ref=eXXX]
- button "Skip" [ref=eXXX]
- button "略過" [ref=eXXX]
```

**Countdown indicator** (skip button not yet active):

```yaml
- generic [ref=eXXX]: "You can skip ad in 3..."
- generic [ref=eXXX]: "3 秒後可略過廣告"
- button "Skip Ad" [disabled] [ref=eXXX]     # button present but disabled
```

When you see a countdown, wait ~5 seconds and snapshot again — the skip button will become clickable.

**Ad indicators** (how to tell an ad is playing even without a skip button):

```yaml
- generic [ref=eXXX]: "Ad · 0:12"            # ad timer
- generic [ref=eXXX]: "廣告 · 0:12"          # Chinese ad timer
- link "Visit advertiser's site" [ref=eXXX]
- link "造訪廣告主網站" [ref=eXXX]
- button "Why this ad?" [ref=eXXX]
- button "為什麼會顯示這則廣告？" [ref=eXXX]
```

**Important**: YouTube often plays **two consecutive ads**. After skipping one ad, always snapshot again to check for a second ad before confirming playback.

### Popups and Dialogs

> **With persistent profile:** If the user has previously logged in and accepted cookies, these dialogs appear **much less frequently**. They may still appear when Google forces re-authentication or after profile reset.

Cookie consent:

```yaml
- button "Accept all" [ref=eXXX]
- button "Reject all" [ref=eXXX]
```

Sign-in / Premium trial:

```yaml
- button "No thanks" [ref=eXXX]
- button "不用了，謝謝" [ref=eXXX]
- button "Dismiss" [ref=eXXX]
```

Logged-in user indicator (confirms login state is active):

```yaml
- button "Avatar image" [ref=eXXX]          # user avatar in top-right corner
- img "Avatar image" [ref=eXXX]             # alternative form
```

If the top-right shows `button "登入"` / `button "Sign in"` instead, the user is **not logged in**.

## Auto-correction Banner (Search Results)

When searching with typos or homophones (common with voice input), YouTube auto-corrects the query. Look for:

```yaml
- generic [ref=eXXX]: "顯示以下搜尋結果: 楊丞琳"
- link "改為搜尋：楊成林" [ref=eXXX]
```

Or in English:

```yaml
- generic [ref=eXXX]: "Showing results for: Yang Cheng Lin"
- link "Search instead for: ..." [ref=eXXX]
```

This means YouTube has already corrected the query and is showing the right results. No action needed — proceed to select a result as normal.

## Filter Tabs (Search Results)

Search results include filter tabs at the top:

```yaml
- tab "全部" [selected] [ref=eXXX]     # All (default)
- tab "影片" [ref=eXXX]                # Videos
- tab "播放清單" [ref=eXXX]            # Playlists
- tab "合輯" [ref=eXXX]                # Mixes / Collections
```

Click the `"播放清單"` or `"合輯"` tab to filter for playlists/mixes when the user wants continuous playback.
