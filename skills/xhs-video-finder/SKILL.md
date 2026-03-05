# xhs-video-finder

Find fresh, viral videos on Xiaohongshu (小红书 / RedNote) for repurposing to YouTube Shorts or other platforms. Uses browser automation to search, filter by type and publish date, and extract video URLs.

## When to Use
- You need a fresh Xiaohongshu video to repurpose (e.g., for a YouTube Shorts cron)
- You want to find trending content by niche (food, travel, crafts, etc.)
- You need a URL with a valid `xsec_token` for downstream tools (creator.octodance.com, etc.)

## Step-by-Step Workflow

### 1. Open Xiaohongshu in the Managed Browser
```
browser action=open profile=openclaw url=https://www.xiaohongshu.com
```
Wait for the page to fully load.

### 2. Search for Content
Use the search bar with a niche keyword. Examples by channel:
- **Chinese food:** `中国美食` `家常菜` `街头小吃` `火锅`
- **Travel:** `旅行` `旅游攻略` `小众景点` `城市打卡`
- **Crafting/DIY:** `手工DIY` `手工制作` `手工教程`
- **Curiosities:** `冷知识` `涨知识` `神奇` `你不知道的`

Take a snapshot, find the search input, and type your keyword.

### 3. Apply Filters (Top-Right Corner)
After search results load, tap the **filter icon** (top-right — shows "已筛选" when active).

Set these options in the filter panel:

| Filter (Chinese) | Setting | Meaning |
|-----------------|---------|---------|
| 排序依据 | **最新** | Sort: Newest first |
| 笔记类型 | **视频** | Type: Videos only |
| 发布时间 | **一周内** | Posted: Within 1 week |
| 搜索范围 | 不限 | Scope: All |

Tap **收起** to close the filter panel.

### 4. Browse Results & Pick a Video
Look for:
- ✅ **1,000+ likes** (❤️ count shown under each card)
- ✅ **Under 6 minutes** (check duration indicator on the thumbnail)
- ✅ **Clear, engaging visuals**
- ✅ **No heavy watermarks** blocking the subject
- ❌ Skip static image posts (图文) — filter should exclude these already

Post timestamps are shown as relative time: `2小时前` = 2 hours ago, `1天前` = 1 day ago.

### 5. Open the Video & Get the URL
Click a video card to open it. Copy the full URL from the address bar:

```
https://www.xiaohongshu.com/explore/VIDEO_ID?xsec_token=ABxxxxxx&xsec_source=pc_search
```

**⚠️ Always include the full URL with `xsec_token`** — this token is required for video download tools. Tokens expire, so get a fresh URL each time.

### 6. Alternative: Use the Share Link
If you prefer a cleaner URL:
1. Click the **Share** button (分享) inside the video — bottom right
2. The share link is **auto-copied to clipboard**
3. Format: `https://www.xiaohongshu.com/discovery/item/VIDEO_ID?source=webshare&xhsshare=...`

Both formats work with creator.octodance.com / lazyai.octodance.com.

## Troubleshooting

| Problem | Fix |
|---------|-----|
| JSON parse error in creator tool | Token expired — get a fresh URL from Xiaohongshu |
| Filter not visible | Scroll up to the top of search results |
| No videos shown | Check filter — make sure 笔记类型 = 视频, not 图文 |
| Video won't load | Try a different video; some have regional restrictions |
| Search results are empty | Try a broader keyword or remove time filter |

## ⚠️ Login Required
Xiaohongshu **requires login to view search results** in the browser. Before using this skill, make sure the managed browser is logged into XHS:

1. Open `https://www.xiaohongshu.com` in the managed browser
2. If a login modal appears, scan the QR code with the XHS mobile app (WeChat scan also works)
3. Once logged in, the session persists — you won't need to log in again unless it expires

**If you can't log in via the managed browser:** Use the XHS mobile app to find a video manually, copy the share link, and paste it directly into the creator tool.

## Notes
- `explore/` URLs and `discovery/item/` URLs both work — use whichever the browser gives you
- The filter state persists across searches in the same session, so you only need to set it once
- Login sessions may expire periodically — if search results are blocked, re-scan the QR code
