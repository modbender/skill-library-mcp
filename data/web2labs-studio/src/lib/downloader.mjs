import { execFile } from "node:child_process"
import { mkdtemp, rm, stat } from "node:fs/promises"
import { readdirSync } from "node:fs"
import { tmpdir } from "node:os"
import { basename, join } from "node:path"
import { promisify } from "node:util"

const execFileAsync = promisify(execFile)

export class VideoDownloader {
  static SUPPORTED_DOMAINS = [
    "youtube.com",
    "youtu.be",
    "www.youtube.com",
    "twitch.tv",
    "www.twitch.tv",
    "vimeo.com",
    "www.vimeo.com",
    "dailymotion.com",
    "www.dailymotion.com",
    "streamable.com",
    "reddit.com",
    "www.reddit.com",
  ]

  static isUrl(input) {
    try {
      const url = new URL(input)
      return url.protocol === "http:" || url.protocol === "https:"
    } catch {
      return false
    }
  }

  static isSupportedUrl(input) {
    try {
      const url = new URL(input)
      const host = url.hostname.toLowerCase()
      return VideoDownloader.SUPPORTED_DOMAINS.some(
        (domain) => host === domain || host.endsWith(`.${domain}`)
      )
    } catch {
      return false
    }
  }

  static async checkYtDlp() {
    try {
      const { stdout } = await execFileAsync("yt-dlp", ["--version"])
      return { installed: true, version: stdout.trim() }
    } catch {
      return { installed: false, version: null }
    }
  }

  static async getVideoInfo(url) {
    const { stdout } = await execFileAsync(
      "yt-dlp",
      ["--dump-json", "--no-download", url],
      { timeout: 30000 }
    )

    const info = JSON.parse(stdout)
    return {
      title: info.title || "Untitled",
      duration: Number(info.duration || 0),
      uploader: info.uploader || null,
      uploadDate: info.upload_date || null,
      description: info.description || null,
      filesize: info.filesize_approx || null,
    }
  }

  static async download(url, options = {}) {
    const tmpPath = await mkdtemp(join(tmpdir(), "w2l-dl-"))
    try {
      const outputTemplate = join(tmpPath, "%(title)s.%(ext)s")

      const args = [
        "-f",
        "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "--merge-output-format",
        "mp4",
        "--no-playlist",
        "--no-overwrites",
        "--restrict-filenames",
        "--output",
        outputTemplate,
      ]

      if (Number(options.maxDuration) > 0) {
        args.push("--match-filter", `duration<=${Number(options.maxDuration)}`)
      }

      args.push(url)

      const { stdout, stderr } = await execFileAsync("yt-dlp", args, {
        timeout: Number(options.timeout || 600000),
        maxBuffer: 5 * 1024 * 1024,
      })

      const fromMerge = stderr.match(/\[Merger\] Merging formats into \"(.+)\"/)
      const fromExisting = stderr.match(/\[download\] (.+\.mp4) has already been downloaded/)
      const fromDestination = stdout.match(/\[download\] Destination: (.+)/)

      let filePath = null
      if (fromMerge?.[1]) {
        filePath = fromMerge[1]
      } else if (fromExisting?.[1]) {
        filePath = fromExisting[1]
      } else if (fromDestination?.[1]) {
        filePath = fromDestination[1]
      }

      if (!filePath) {
        const candidates = readdirSync(tmpPath)
          .filter((name) => name.toLowerCase().endsWith(".mp4"))
          .map((name) => join(tmpPath, name))
        if (candidates.length > 0) {
          filePath = candidates[0]
        }
      }

      if (!filePath) {
        throw new Error("Download completed but output file was not found")
      }

      const fileStats = await stat(filePath)
      return {
        filePath,
        tmpDir: tmpPath,
        fileSize: Number(fileStats.size || 0),
        fileName: basename(filePath),
      }
    } catch (err) {
      err.tmpDir = tmpPath
      throw err
    }
  }

  static async cleanup(tmpPath) {
    if (!tmpPath) {
      return
    }
    try {
      await rm(tmpPath, { recursive: true, force: true })
    } catch {
      // Best-effort cleanup.
    }
  }

  static async listChannelVods(channelUrl, limit = 10) {
    const args = [
      "--flat-playlist",
      "--print",
      "%(id)s\t%(title)s\t%(upload_date)s\t%(duration)s",
      "--playlist-end",
      String(limit),
      channelUrl,
    ]

    const { stdout } = await execFileAsync("yt-dlp", args, { timeout: 30000 })

    return stdout
      .trim()
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        const [id, title, date, duration] = line.split("\t")
        return {
          id,
          title,
          date,
          duration: Number(duration || 0),
        }
      })
  }
}
