#!/usr/bin/env node
/**
 * Update Dockge stacks (pull latest images + restart).
 * Usage: node dockge-update.mjs [stack1] [stack2] ...
 * If no stacks specified, updates all running stacks (excluding ix-* TrueNAS apps).
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

const specificStacks = process.argv.slice(2);
const socket = io(DOCKGE_URL, { transports: ["websocket"], reconnection: false });

function updateStacks(stacks) {
  if (stacks.length === 0) {
    console.error("No stacks to update.");
    socket.disconnect();
    process.exit(0);
  }

  console.error(`Updating ${stacks.length} stacks...`);

  stacks.forEach((name, i) => {
    setTimeout(() => {
      socket.emit("agent", "", "updateStack", name, () => {});
      console.error(`  Update requested: ${name}`);

      if (i === stacks.length - 1) {
        setTimeout(() => {
          console.error("All updateStack commands sent.");
          console.log(JSON.stringify({ updated: stacks }));
          socket.disconnect();
          process.exit(0);
        }, 1000);
      }
    }, i * 200);
  });
}

socket.on("connect", () => {
  console.error("Connected to Dockge");
  socket.emit("login", { username: DOCKGE_USER, password: DOCKGE_PASS, token: "" }, (r) => {
    if (!r || !r.ok) {
      console.error("Login failed:", r?.msg || "no response from server");
      process.exit(1);
    }
    console.error("Logged in.");

    if (specificStacks.length > 0) {
      updateStacks(specificStacks);
    } else {
      socket.emit("stackList");
    }
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
    const running = Object.entries(data.stackList)
      .filter(([name, v]) => v.status === 3 && !name.startsWith("ix-"))
      .map(([k]) => k)
      .sort();

    console.error(`Found ${running.length} running stacks`);
    updateStacks(running);
  }
});

setTimeout(() => {
  console.error("Timeout: No response after 120s");
  socket.disconnect();
  process.exit(1);
}, 120000);
