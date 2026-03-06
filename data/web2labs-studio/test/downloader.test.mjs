import test from "node:test"
import assert from "node:assert/strict"
import { VideoDownloader } from "../src/lib/downloader.mjs"

test("VideoDownloader URL checks", () => {
  assert.equal(VideoDownloader.isUrl("https://youtube.com/watch?v=abc"), true)
  assert.equal(VideoDownloader.isUrl("C:/video.mp4"), false)
})

test("VideoDownloader supported domains", () => {
  assert.equal(VideoDownloader.isSupportedUrl("https://www.youtube.com/watch?v=abc"), true)
  assert.equal(VideoDownloader.isSupportedUrl("https://twitch.tv/channel/videos"), true)
  assert.equal(VideoDownloader.isSupportedUrl("https://example.com/video"), false)
})
