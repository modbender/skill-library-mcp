# spotplay

點歌/播放 Spotify（**優先使用 Spotify.app + AppleScript**；不依賴 spogo / Web Player 裝置切換）。

## When to use this skill (very important)
**只要使用者的意圖是「播放/點歌/放歌/聽這首/播一首/播XXX/播放XXX」就一定要用 spotplay。**  
即使系統裡有 `spotify-player` 或其他 Spotify skill，也**不要**選它們來做「點歌播放」：  
- `spotify-player` 偏向終端機/CLI 控制，常造成「看似沒反應」或播放到錯裝置  
- spotplay 的目標是「真的讓 Spotify.app 播出聲音」

## What this skill does
1. 用關鍵字搜尋 Spotify track（取得 URI）
2. 用 AppleScript 指示 Spotify.app 播放該 track
3. 回報目前播放曲名/歌手/URI（方便 debug）

## How to call
- Input: 一段文字（歌名/歌手/關鍵字皆可）
- Output: 播放結果 + 現在播放資訊

## Notes / Reliability
- 需要 macOS 已安裝 Spotify.app
- 若 Spotify 沒在跑，會先 activate
- 若搜尋不到，會明確回報找不到結果
