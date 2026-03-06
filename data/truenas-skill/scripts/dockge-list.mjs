#!/usr/bin/env node
/**
 * List Dockge stacks and their status.
 * Usage: node dockge-list.mjs
 *
 * Requires: DOCKGE_URL, DOCKGE_USER, DOCKGE_PASS
 */

import { io } from "socket.io-client";

const DOCKGE_URL = process.env.DOCKGE_URL;
const DOCKGE_USER = process.env.DOCKGE_USER;
const DOCKGE_PASS = process.env.DOCKGE_PASS;

if (!DOCKGE_URL) {
  console.error("Error: DOCKGE_URL env var required (e.g., http://10.0.0.5:5001)");
  process.exit(1);
}

if (!DOCKGE_USER) {
  console.error("Error: DOCKGE_USER env var required");
  process.exit(1);
}

if (!DOCKGE_PASS) {
  console.error("Error: DOCKGE_PASS env var required");
  process.exit(1);
}

const socket = io(DOCKGE_URL, { transports: ["websocket"], reconnection: false });

socket.on("connect", () => {
  console.error("Connected to Dockge");
  socket.emit("login", { username: DOCKGE_USER, password: DOCKGE_PASS, token: "" }, (r) => {
    if (!r || !r.ok) {
      console.error("Login failed:", r?.msg || "no response from server");
      process.exit(1);
    }
    console.error("Logged in. Fetching stacks...");
    socket.emit("stackList");
  });
});

socket.on("connect_error", (err) => {
  console.error("Connection failed:", err.message);
  process.exit(1);
});

socket.on("agent", (eventType, data) => {
  if (eventType === "stackList") {
    if (!data || !data.ok) {
      console.error("Error: stackList failed:", data?.msg || "unknown error");
      process.exit(1);
    }
    console.log(JSON.stringify(
      Object.entries(data.stackList).map(([name, v]) => ({
        name,
        status: v.status,
        state: v.status === 3 ? "running" : "stopped"
      })),
      null, 2
    ));
    socket.disconnect();
    process.exit(0);
  }
});

setTimeout(() => {
  console.error("Timeout: No response after 10s");
  socket.disconnect();
  process.exit(1);
}, 10000);
