import test from "node:test"
import assert from "node:assert/strict"
import { DownloadTool } from "../src/tools/download.mjs"

test("sanitizeName strips special characters and limits length", () => {
  assert.equal(DownloadTool.sanitizeName("My <Cool> Video!"), "my--cool--video!")
  assert.equal(DownloadTool.sanitizeName(""), "project")
  assert.equal(DownloadTool.sanitizeName(null), "project")
  assert.ok(DownloadTool.sanitizeName("a".repeat(200)).length <= 120)
})

test("isTypeEnabled checks membership or 'all'", () => {
  assert.equal(DownloadTool.isTypeEnabled(["main", "shorts"], "main"), true)
  assert.equal(DownloadTool.isTypeEnabled(["main", "shorts"], "subtitles"), false)
  assert.equal(DownloadTool.isTypeEnabled(["all"], "subtitles"), true)
  assert.equal(DownloadTool.isTypeEnabled(["all"], "main"), true)
})

test("collectArtifacts gathers matching artifacts", () => {
  const results = {
    name: "test",
    mainVideo: { url: "/main.mp4", filename: "main.mp4" },
    shorts: [{ url: "/short1.mp4", filename: "short1.mp4" }],
    subtitles: { url: "/subs.srt" },
    transcription: { url: "/trans.json" },
    timelineExports: [
      { format: "edl", url: "/t.edl", filename: "t.edl" },
    ],
    thumbnails: [
      { variant: "A", imageUrl: "/thumb-a.png" },
    ],
  }

  const all = DownloadTool.collectArtifacts(results, ["all"])
  assert.ok(all.length >= 5)

  const mainOnly = DownloadTool.collectArtifacts(results, ["main"])
  assert.equal(mainOnly.length, 1)
  assert.equal(mainOnly[0].kind, "main")
})

test("DownloadTool throws on missing project_id", async () => {
  await assert.rejects(
    () => DownloadTool.execute({}, {}),
    { message: "project_id is required" }
  )
})
