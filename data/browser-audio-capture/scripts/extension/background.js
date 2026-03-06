/**
 * Background service worker.
 * 
 * Flow: popup clicks Start → popup calls chrome.tabCapture.getMediaStreamId() 
 * (must be from extension page with user gesture) → sends streamId to background
 * → background creates offscreen doc → offscreen doc does the actual audio capture.
 */

let activeCapture = null; // { sessionId, tabId, tabTitle, tabUrl }

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "startCapture") {
    activeCapture = {
      sessionId: "browser_" + Date.now(),
      tabId: msg.tabId,
      tabTitle: msg.tabTitle || "",
      tabUrl: msg.tabUrl || "",
    };
    
    ensureOffscreen().then(() => {
      chrome.runtime.sendMessage({
        action: "offscreen_start",
        streamId: msg.streamId,
        sessionId: activeCapture.sessionId,
        tabTitle: activeCapture.tabTitle,
        tabUrl: activeCapture.tabUrl,
      });
      chrome.action.setBadgeText({ text: "REC" });
      chrome.action.setBadgeBackgroundColor({ color: "#e74c3c" });
      sendResponse({ status: "capturing", sessionId: activeCapture.sessionId });
    }).catch(err => {
      sendResponse({ status: "error", error: err.message });
    });
    
    return true; // async response
  }
  
  if (msg.action === "stopCapture") {
    chrome.runtime.sendMessage({ action: "offscreen_stop" });
    activeCapture = null;
    chrome.action.setBadgeText({ text: "" });
    sendResponse({ status: "stopped" });
    return false;
  }
  
  if (msg.action === "getStatus") {
    sendResponse({ active: activeCapture });
    return false;
  }
});

async function ensureOffscreen() {
  if (await chrome.offscreen.hasDocument()) return;
  await chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["USER_MEDIA"],
    justification: "Process tab audio capture for transcription",
  });
}

// Clean up when tab closes
chrome.tabs.onRemoved.addListener((tabId) => {
  if (activeCapture && activeCapture.tabId === tabId) {
    chrome.runtime.sendMessage({ action: "offscreen_stop" });
    activeCapture = null;
    chrome.action.setBadgeText({ text: "" });
  }
});
