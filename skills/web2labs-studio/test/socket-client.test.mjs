import test from "node:test"
import assert from "node:assert/strict"
import { SocketClient } from "../src/lib/socket-client.mjs"

test("SocketClient constructor stores config", () => {
  const apiClient = { baseUrl: "https://web2labs.com" }
  const client = new SocketClient(apiClient)
  assert.equal(client.apiClient, apiClient)
  assert.equal(client.socketUrl, "https://web2labs.com")
  assert.equal(client.socket, null)
})

test("SocketClient constructor uses custom socketUrl", () => {
  const apiClient = { baseUrl: "https://web2labs.com" }
  const client = new SocketClient(apiClient, "https://custom:3001")
  assert.equal(client.socketUrl, "https://custom:3001")
})

test("SocketClient constructor uses WEB2LABS_SOCKET_URL env var", () => {
  const original = process.env.WEB2LABS_SOCKET_URL
  try {
    process.env.WEB2LABS_SOCKET_URL = "https://env-socket:4000"
    const apiClient = { baseUrl: "https://web2labs.com" }
    const client = new SocketClient(apiClient)
    assert.equal(client.socketUrl, "https://env-socket:4000")
  } finally {
    if (original === undefined) {
      delete process.env.WEB2LABS_SOCKET_URL
    } else {
      process.env.WEB2LABS_SOCKET_URL = original
    }
  }
})

test("SocketClient explicit socketUrl takes precedence over env var", () => {
  const original = process.env.WEB2LABS_SOCKET_URL
  try {
    process.env.WEB2LABS_SOCKET_URL = "https://env-socket:4000"
    const apiClient = { baseUrl: "https://web2labs.com" }
    const client = new SocketClient(apiClient, "https://explicit:5000")
    assert.equal(client.socketUrl, "https://explicit:5000")
  } finally {
    if (original === undefined) {
      delete process.env.WEB2LABS_SOCKET_URL
    } else {
      process.env.WEB2LABS_SOCKET_URL = original
    }
  }
})

test("SocketClient connect rejects when getSocketToken fails", async () => {
  const apiClient = {
    baseUrl: "https://web2labs.com",
    getSocketToken: async () => { throw new Error("auth failed") },
  }
  const client = new SocketClient(apiClient)
  await assert.rejects(() => client.connect(), /auth failed/)
})

test("SocketClient connect rejects when token is empty", async () => {
  const apiClient = {
    baseUrl: "https://web2labs.com",
    getSocketToken: async () => ({}),
  }
  const client = new SocketClient(apiClient)
  await assert.rejects(() => client.connect(), /Failed to obtain socket token/)
})

test("SocketClient disconnect is safe to call when not connected", () => {
  const apiClient = { baseUrl: "https://web2labs.com" }
  const client = new SocketClient(apiClient)
  // Should not throw
  client.disconnect()
  client.disconnect()
  assert.equal(client.socket, null)
})

test("SocketClient disconnect cleans up socket", () => {
  const apiClient = { baseUrl: "https://web2labs.com" }
  const client = new SocketClient(apiClient)
  let removedAll = false
  let closed = false
  client.socket = {
    removeAllListeners: () => { removedAll = true },
    close: () => { closed = true },
  }
  client.disconnect()
  assert.equal(removedAll, true)
  assert.equal(closed, true)
  assert.equal(client.socket, null)
})

test("SocketClient waitForCompletion rejects when not connected", async () => {
  const apiClient = { baseUrl: "https://web2labs.com" }
  const client = new SocketClient(apiClient)
  await assert.rejects(
    () => client.waitForCompletion("proj-1", 5000),
    /Socket not connected/
  )
})
