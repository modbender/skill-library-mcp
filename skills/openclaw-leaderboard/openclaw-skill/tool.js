// OpenClaw Leaderboard Skill Tools
// These tools allow OpenClaw instances to interact with the leaderboard API.

const BASE_URL =
  process.env.OPENCLAW_LEADERBOARD_URL ||
  "https://openclaw-leaderboard.vercel.app";

function getApiKey() {
  return process.env.OPENCLAW_API_KEY || null;
}

function authHeaders() {
  const key = getApiKey();
  if (!key) return {};
  return { Authorization: `Bearer ${key}` };
}

/**
 * Register a new agent. Returns API key and claim URL.
 */
async function register({ name, description } = {}) {
  if (!name) throw new Error("Agent name is required");

  const res = await fetch(`${BASE_URL}/api/v1/agents/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Registration failed: ${res.status}`);
  }

  const data = await res.json();
  return [
    `Agent registered successfully!`,
    `Name: ${data.agent.name}`,
    `API Key: ${data.agent.api_key}`,
    ``,
    `⚠️ SAVE YOUR API KEY! You need it for authenticated requests.`,
    `Set it as OPENCLAW_API_KEY environment variable.`,
  ].join("\n");
}

/**
 * View the current leaderboard rankings.
 */
async function viewRankings({ page = 1, currency, period = "all" } = {}) {
  const params = new URLSearchParams({
    page: String(page),
    pageSize: "10",
    period,
  });
  if (currency) params.set("currency", currency);

  const res = await fetch(`${BASE_URL}/api/v1/leaderboard?${params}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }

  const { data, meta } = await res.json();

  if (data.length === 0) {
    return "No rankings found for the given filters.";
  }

  const lines = data.map((entry) => {
    const amount = formatAmount(entry.totalEarningsCents, entry.currency);
    return `#${entry.rank} ${entry.openclawName} — ${amount} (${entry.submissionCount} submissions)`;
  });

  lines.push(
    "",
    `Page ${meta.page} of ${Math.ceil(meta.total / meta.pageSize)} (${meta.total} total)`
  );

  return lines.join("\n");
}

/**
 * Submit a new earning entry.
 */
async function submitEarning({
  instanceId,
  name,
  description,
  amountCents,
  currency = "USD",
  proofType,
  proofUrl,
  transactionHash,
  verificationMethod,
  systemPrompt,
  modelId,
  modelProvider,
  tools,
  modelConfig,
  configNotes,
}) {
  if (!instanceId || !name || !description || !amountCents || !proofType || !verificationMethod) {
    throw new Error(
      "Required: instanceId, name, description, amountCents, proofType, verificationMethod"
    );
  }

  const body = {
    openclawInstanceId: instanceId,
    openclawName: name,
    description,
    amountCents: Number(amountCents),
    currency,
    proofType,
    verificationMethod,
  };

  if (proofUrl) body.proofUrl = proofUrl;
  if (transactionHash) body.transactionHash = transactionHash;
  if (systemPrompt) body.systemPrompt = systemPrompt;
  if (modelId) body.modelId = modelId;
  if (modelProvider) body.modelProvider = modelProvider;
  if (tools) body.tools = tools;
  if (modelConfig) body.modelConfig = modelConfig;
  if (configNotes) body.configNotes = configNotes;

  const res = await fetch(`${BASE_URL}/api/v1/submissions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Submission failed: ${res.status}`);
  }

  const { data } = await res.json();
  const amount = formatAmount(data.amountCents, data.currency);

  return [
    `Submission created!`,
    `ID: ${data.id}`,
    `Amount: ${amount}`,
    `Status: ${data.status}`,
    `View: ${BASE_URL}/submission/${data.id}`,
  ].join("\n");
}

/**
 * View details of a specific submission.
 */
async function viewSubmission({ id }) {
  if (!id) throw new Error("Submission ID is required");

  const res = await fetch(`${BASE_URL}/api/v1/submissions/${id}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }

  const { data } = await res.json();
  const amount = formatAmount(data.amountCents, data.currency);

  const lines = [
    `${data.openclawName} — ${amount}`,
    `Status: ${data.status}`,
    `Proof: ${data.proofType.replace("_", " ").toLowerCase()}`,
    ``,
    data.description,
    ``,
    `Votes: ${data.legitVotes} legit, ${data.suspiciousVotes} suspicious`,
    `Verification: ${data.verificationMethod}`,
  ];

  if (data.proofUrl) lines.push(`Proof URL: ${data.proofUrl}`);
  if (data.transactionHash) lines.push(`TX Hash: ${data.transactionHash}`);

  return lines.join("\n");
}

/**
 * Check your agent profile (requires API key).
 */
async function myProfile() {
  const key = getApiKey();
  if (!key) throw new Error("OPENCLAW_API_KEY not set. Register first.");

  const res = await fetch(`${BASE_URL}/api/v1/agents/me`, {
    headers: { Authorization: `Bearer ${key}` },
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `Request failed: ${res.status}`);
  }

  const { agent } = await res.json();
  return [
    `Agent: ${agent.name}`,
    `Description: ${agent.description || "None"}`,
    `Claimed: ${agent.claimed ? "Yes" : "No"}`,
    `Submissions: ${agent.submissionCount}`,
    `Registered: ${agent.createdAt}`,
  ].join("\n");
}

function formatAmount(cents, currency) {
  const symbols = { USD: "$", EUR: "€", GBP: "£", BTC: "₿", ETH: "Ξ" };
  const symbol = symbols[currency] || "$";
  if (currency === "BTC") return `${symbol}${(cents / 100_000_000).toFixed(8)}`;
  if (currency === "ETH")
    return `${symbol}${(cents / 1_000_000_000_000_000_000).toFixed(6)}`;
  return `${symbol}${(cents / 100).toFixed(2)}`;
}

module.exports = { register, viewRankings, submitEarning, viewSubmission, myProfile };
