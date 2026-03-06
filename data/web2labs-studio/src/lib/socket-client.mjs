import { io } from "socket.io-client"

const TERMINAL_STATUSES = new Set(["completed", "failed"])

const VERIFICATION_TIMEOUT_MS = 10000
const DEFAULT_SOCKET_PATH = "/socket.io/"

export class SocketClient {
  constructor(apiClient, socketUrl) {
    this.apiClient = apiClient
    this.socketUrl = socketUrl || process.env.WEB2LABS_SOCKET_URL || apiClient.baseUrl
    this.socket = null
  }

  async connect() {
    const tokenResponse = await this.apiClient.getSocketToken()
    const token = tokenResponse?.token
    if (!token) {
      throw new Error("Failed to obtain socket token")
    }

    const extraHeaders = {}
    if (this.apiClient.basicAuth) {
      const encoded = Buffer.from(this.apiClient.basicAuth).toString("base64")
      extraHeaders.Authorization = `Basic ${encoded}`
    }

    this.socket = io(this.socketUrl, {
      path: DEFAULT_SOCKET_PATH,
      auth: { token },
      reconnection: false,
      transports: ["websocket", "polling"],
      extraHeaders,
    })

    await new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        reject(new Error("Socket verification timed out"))
      }, VERIFICATION_TIMEOUT_MS)

      this.socket.on("verification_success", () => {
        clearTimeout(timer)
        resolve()
      })

      this.socket.on("verification_error", (err) => {
        clearTimeout(timer)
        reject(new Error(`Socket verification failed: ${err?.message || err}`))
      })

      this.socket.on("connect_error", (err) => {
        clearTimeout(timer)
        reject(new Error(`Socket connection error: ${err?.message || err}`))
      })
    })
  }

  async waitForCompletion(projectId, timeoutMs, onProgress) {
    if (!this.socket) {
      throw new Error("Socket not connected")
    }

    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        cleanup()
        reject(new Error(`Socket polling timed out after ${Math.round(timeoutMs / 60000)} minutes`))
      }, timeoutMs)

      const listeners = []

      const cleanup = () => {
        clearTimeout(timer)
        for (const [event, fn] of listeners) {
          this.socket.off(event, fn)
        }
      }

      const resolveWithHttpStatus = async () => {
        cleanup()
        try {
          const status = await this.apiClient.getProjectStatus(projectId)
          resolve(status)
        } catch (err) {
          reject(err)
        }
      }

      const on = (event, fn) => {
        listeners.push([event, fn])
        this.socket.on(event, fn)
      }

      on("video_render_progress", (data) => {
        if (data?.projectId !== projectId) return
        if (typeof onProgress === "function") {
          onProgress({
            projectId,
            status: "rendering",
            progress: data.progress ?? null,
          })
        }
      })

      on("video_render_end", (data) => {
        if (data?.projectId !== projectId) return
        resolveWithHttpStatus()
      })

      on("video_render_error", (data) => {
        if (data?.projectId !== projectId) return
        resolveWithHttpStatus()
      })

      on("video_project_core_updated", (data) => {
        if (data?.projectId !== projectId) return
        const status = String(data?.status || "").toLowerCase()
        if (TERMINAL_STATUSES.has(status)) {
          resolveWithHttpStatus()
        } else if (typeof onProgress === "function") {
          onProgress({
            projectId,
            status: data.status,
            progress: data.progress ?? null,
          })
        }
      })

      on("disconnect", () => {
        cleanup()
        reject(new Error("Socket disconnected during polling"))
      })
    })
  }

  disconnect() {
    if (this.socket) {
      try {
        this.socket.removeAllListeners()
        this.socket.close()
      } catch (_) {
        // ignore
      }
      this.socket = null
    }
  }
}
