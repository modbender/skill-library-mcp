const { createHash } = require("crypto");
const { hostname } = require("os");

const API_URL = "https://rankingofclaws.angelstreet.io/api/report";

let tokensDelta = 0;
let tokensInDelta = 0;
let tokensOutDelta = 0;
let lastReportTime = 0;
const REPORT_INTERVAL_MS = 60 * 60 * 1000;

function getGatewayId() {
  const raw = `${hostname()}-${process.env.HOME || ""}-openclaw`;
  return createHash("sha256").update(raw).digest("hex").slice(0, 16);
}

function getAgentName() {
  return process.env.RANKING_AGENT_NAME || hostname() || "anonymous";
}

function getCountry() {
  return process.env.RANKING_COUNTRY || "XX";
}

async function report() {
  if (tokensDelta === 0) return;
  try {
    const body = JSON.stringify({
      gateway_id: getGatewayId(),
      agent_name: getAgentName(),
      country: getCountry(),
      tokens_delta: tokensDelta,
      tokens_in_delta: tokensInDelta,
      tokens_out_delta: tokensOutDelta,
      model: "mixed",
    });
    const https = require("https");
    const url = new URL(API_URL);
    await new Promise((resolve, reject) => {
      const req = https.request({ hostname: url.hostname, path: url.pathname, method: "POST", headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) }, timeout: 10000 }, (res) => {
        if (res.statusCode === 200) { tokensDelta = 0; tokensInDelta = 0; tokensOutDelta = 0; lastReportTime = Date.now(); }
        res.resume();
        resolve();
      });
      req.on("error", resolve);
      req.write(body);
      req.end();
    });
  } catch {}
}

module.exports = async function handler(event) {
  if (!event || event.type !== "message" || event.action !== "sent") return;
  const content = (event.context && event.context.content) || "";
  const estimatedTokens = Math.ceil(content.length / 4);
  tokensOutDelta += estimatedTokens;
  tokensDelta += estimatedTokens;
  if (Date.now() - lastReportTime >= REPORT_INTERVAL_MS) {
    report();
  }
};
