/**
 * Offscreen document — persists after popup closes.
 * Handles actual audio capture and streaming to Percept.
 */

const PERCEPT_URL = "http://127.0.0.1:8900";
const SAMPLE_RATE = 16000;
const CHUNK_MS = 3000;

let stream = null;
let audioCtx = null;
let processor = null;
let currentSessionId = null;
let currentTabUrl = "";
let currentTabTitle = "";

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.action === "offscreen_start") {
    startCapture(msg.streamId, msg.sessionId, msg.tabUrl, msg.tabTitle);
  }
  if (msg.action === "offscreen_stop") {
    stopCapture();
  }
});

async function startCapture(streamId, sessionId, tabUrl, tabTitle) {
  try {
    currentSessionId = sessionId;
    currentTabUrl = tabUrl;
    currentTabTitle = tabTitle;

    stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        mandatory: {
          chromeMediaSource: "tab",
          chromeMediaSourceId: streamId,
        },
      },
    });

    audioCtx = new AudioContext({ sampleRate: SAMPLE_RATE });
    const source = audioCtx.createMediaStreamSource(stream);
    processor = audioCtx.createScriptProcessor(4096, 1, 1);

    let audioBuffer = [];
    let chunkStart = Date.now();

    processor.onaudioprocess = (e) => {
      const input = e.inputBuffer.getChannelData(0);
      const pcm16 = new Int16Array(input.length);
      for (let i = 0; i < input.length; i++) {
        const s = Math.max(-1, Math.min(1, input[i]));
        pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }
      audioBuffer.push(pcm16);

      if (Date.now() - chunkStart >= CHUNK_MS) {
        sendChunk(audioBuffer);
        audioBuffer = [];
        chunkStart = Date.now();
      }
    };

    source.connect(processor);
    processor.connect(audioCtx.destination);

    console.log("[Percept Offscreen] Capturing:", tabTitle, sessionId);
  } catch (err) {
    console.error("[Percept Offscreen] Error:", err);
  }
}

function stopCapture() {
  try {
    if (processor) processor.disconnect();
    if (audioCtx) audioCtx.close();
    if (stream) stream.getTracks().forEach(t => t.stop());
  } catch (e) {}
  processor = null;
  audioCtx = null;
  stream = null;
  currentSessionId = null;
  console.log("[Percept Offscreen] Stopped");
}

function sendChunk(buffers) {
  const totalLen = buffers.reduce((a, b) => a + b.length, 0);
  if (totalLen === 0) return;

  const merged = new Int16Array(totalLen);
  let off = 0;
  for (const b of buffers) { merged.set(b, off); off += b.length; }

  const bytes = new Uint8Array(merged.buffer);
  let bin = "";
  for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
  const b64 = btoa(bin);

  fetch(PERCEPT_URL + "/audio/browser", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessionId: currentSessionId,
      audio: b64,
      sampleRate: SAMPLE_RATE,
      format: "pcm16",
      source: "browser_extension",
      tabUrl: currentTabUrl,
      tabTitle: currentTabTitle,
    }),
  }).catch(err => console.error("[Percept Offscreen] Send error:", err));
}
