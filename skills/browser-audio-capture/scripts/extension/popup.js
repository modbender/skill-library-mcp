/**
 * Popup — gets user gesture for tabCapture, hands off to background/offscreen.
 * Can close safely after starting — offscreen doc keeps capturing.
 */

let capturing = false;

function log(msg) {
  document.getElementById("debug").textContent = msg;
  console.log("[Percept Popup]", msg);
}

function showStatus(text, cls) {
  const el = document.getElementById("status");
  el.className = "status " + cls;
  el.textContent = text;
}

async function init() {
  try {
    // Check if already capturing
    const status = await chrome.runtime.sendMessage({ action: "getStatus" });
    if (status.active) {
      capturing = true;
      showStatus("🎙️ Capturing: " + (status.active.tabTitle || "").substring(0, 30), "active");
      document.getElementById("toggleBtn").className = "stop";
      document.getElementById("toggleBtn").textContent = "Stop Capturing";
      log("Session: " + status.active.sessionId);
    } else {
      showStatus("Ready to capture", "idle");
      log("Click Start on a meeting tab");
    }
  } catch (err) {
    log("Init: " + err.message);
  }
}

document.getElementById("toggleBtn").addEventListener("click", async function() {
  this.disabled = true;

  if (capturing) {
    // Stop
    await chrome.runtime.sendMessage({ action: "stopCapture" });
    capturing = false;
    showStatus("Ready to capture", "idle");
    this.className = "start";
    this.textContent = "Start Capturing This Tab";
    this.disabled = false;
    log("Stopped.");
    return;
  }

  try {
    // Get active tab
    log("Getting tab...");
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      showStatus("No active tab", "error");
      this.disabled = false;
      return;
    }
    log("Tab: " + (tab.title || "").substring(0, 30));

    // Get stream ID — MUST be called from popup (user gesture context)
    log("Requesting audio access...");
    const streamId = await new Promise((resolve, reject) => {
      chrome.tabCapture.getMediaStreamId({ targetTabId: tab.id }, (id) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
        } else {
          resolve(id);
        }
      });
    });
    log("Got stream ID, handing to background...");

    // Hand off to background → offscreen (persists after popup closes)
    const result = await chrome.runtime.sendMessage({
      action: "startCapture",
      streamId: streamId,
      tabId: tab.id,
      tabTitle: tab.title || "",
      tabUrl: tab.url || "",
    });

    if (result.status === "capturing") {
      capturing = true;
      showStatus("🎙️ Capturing! You can close this popup.", "active");
      this.className = "stop";
      this.textContent = "Stop Capturing";
      log("Session: " + result.sessionId);
    } else {
      showStatus("Error: " + (result.error || "Unknown"), "error");
      log("Failed: " + JSON.stringify(result));
    }
  } catch (err) {
    showStatus("Error: " + err.message, "error");
    log(err.message);
  }

  this.disabled = false;
});

init();
