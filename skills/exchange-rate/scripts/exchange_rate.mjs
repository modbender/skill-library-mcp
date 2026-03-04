#!/usr/bin/env node
/**
 * Exchange Rate Skill – QVeris-powered rate lookup and conversion.
 * Search for currency tools, then execute with fallback. No hardcoded tool IDs.
 */


const BASE_URL = "https://qveris.ai/api/v1";

const SEARCH_QUERIES = [
  "currency exchange rate real-time forex",
  "currency conversion amount convert",
];

const DEFAULT_TIMEOUT_MS = 5000;
const MAX_RESPONSE_SIZE = 20480;

function getApiKey() {
  const key = process.env.QVERIS_API_KEY;
  if (!key) {
    console.error("Error: QVERIS_API_KEY environment variable is required.");
    process.exit(1);
  }
  return key;
}

function timeoutSignal(ms) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  return { signal: controller.signal, cleanup: () => clearTimeout(timer) };
}

async function searchTools(query, limit = 15, timeoutMs = 15000) {
  const apiKey = getApiKey();
  const { signal, cleanup } = timeoutSignal(timeoutMs);
  try {
    const res = await fetch(`${BASE_URL}/search`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query, limit }),
      signal,
    });
    if (!res.ok) throw new Error(`Search failed (${res.status}): ${await res.text()}`);
    return await res.json();
  } finally {
    cleanup();
  }
}

async function executeTool(toolId, searchId, parameters, maxResponseSize, timeoutMs) {
  const apiKey = getApiKey();
  const { signal, cleanup } = timeoutSignal(timeoutMs);
  try {
    const url = new URL(`${BASE_URL}/tools/execute`);
    url.searchParams.set("tool_id", toolId);
    const res = await fetch(url.toString(), {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        search_id: searchId,
        parameters,
        max_response_size: maxResponseSize,
      }),
      signal,
    });
    if (!res.ok) throw new Error(`Execute failed (${res.status}): ${await res.text()}`);
    return await res.json();
  } finally {
    cleanup();
  }
}

function paramNames(tool) {
  const params = tool?.params ?? [];
  return new Set(params.map((p) => (p && p.name ? String(p.name).toLowerCase() : "").trim()).filter(Boolean));
}

function isRateTool(tool) {
  const names = paramNames(tool);
  const hasPair =
    (names.has("from_currency") && names.has("to_currency")) ||
    names.has("symbol") ||
    (names.has("from_symbol") && names.has("to_symbol"));
  return hasPair;
}

function isConversionTool(tool) {
  const names = paramNames(tool);
  return names.has("amount") && (names.has("symbol") || names.has("from_currency") || names.has("from_symbol"));
}

function scoreTool(tool, needAmount) {
  const stats = tool?.stats ?? {};
  const successRate = Number(stats.success_rate);
  const latency = Number(stats.avg_execution_time_ms);
  const latencyScore = latency > 0 ? 1 / (1 + latency) : 0;
  let fit = 0;
  if (needAmount && isConversionTool(tool)) fit += 0.2;
  else if (!needAmount && isRateTool(tool)) fit += 0.2;
  if (isRateTool(tool)) fit += 0.1;
  return (successRate || 0) * 0.6 + latencyScore * 0.2 + fit;
}

function buildParameters(tool, from, to, amount, date) {
  const fromU = String(from || "").toUpperCase().trim();
  const toU = String(to || "").toUpperCase().trim();
  const params = {};
  const names = paramNames(tool);

  if (names.has("function")) {
    params.function = "CURRENCY_EXCHANGE_RATE";
  }
  if (names.has("from_currency")) params.from_currency = fromU;
  if (names.has("to_currency")) params.to_currency = toU;
  if (names.has("from_symbol")) params.from_symbol = fromU;
  if (names.has("to_symbol")) params.to_symbol = toU;
  if (names.has("symbol")) params.symbol = `${fromU}/${toU}`;
  if (names.has("amount") && amount != null && amount !== "") {
    const n = Number(amount);
    params.amount = Number.isFinite(n) ? n : 1;
  }
  if (names.has("date") && date) params.date = date;

  return params;
}

function isExecutionSuccess(result) {
  if (!result || typeof result !== "object" || result.success === false) return false;
  const data = result?.result?.data ?? result?.result ?? result?.data ?? result;
  if (data?.status === "error") return false;
  if (typeof data?.["Error Message"] === "string") return false;
  if (typeof data?.Information === "string" && data.Information.toLowerCase().includes("burst")) return false;
  return true;
}

function extractRateAndConverted(data, from, to, amount) {
  const d0 = data?.result?.data ?? data?.data ?? data ?? {};
  let rate = null;
  let converted = null;
  let pair = null;

  const d = d0['Realtime Currency Exchange Rate']??{};
  if (typeof d["5. Exchange Rate"] === "string") {
    rate = parseFloat(d["5. Exchange Rate"]);
    pair = `${d["2. From_Currency Code"]}/${d["4. To_Currency Code"]}`;
  }
  if (typeof d["8. Bid Price"] === "string") rate = rate ?? parseFloat(d["8. Bid Price"]);
  if (typeof d["9. Ask Price"] === "string" && rate == null) rate = parseFloat(d["9. Ask Price"]);
  if (d.rate != null) rate = rate ?? Number(d.rate);
  if (d.exchange_rate != null) rate = rate ?? Number(d.exchange_rate);
  if (d.converted_amount != null) converted = Number(d.converted_amount);
  if (d.amount != null && d.currency != null && String(d.currency).toUpperCase() === String(to).toUpperCase()) {
    converted = Number(d.amount);
  }
  if (rate != null && amount != null && Number.isFinite(amount) && converted == null) {
    converted = rate * amount;
  }
  if (d.symbol && rate == null && d.rate != null) rate = Number(d.rate);
  if (d.rate != null) rate = rate ?? Number(d.rate);

  return { rate, converted, pair: pair || `${from}/${to}` };
}

function parseArgs(argv) {
  const args = argv.slice(2);
  const parsed = {
    command: null,
    from: null,
    to: null,
    amount: null,
    date: null,
    format: "markdown",
    timeoutMs: DEFAULT_TIMEOUT_MS,
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "rate" || args[i] === "convert") parsed.command = args[i];
    else if (args[i] === "--from" && i + 1 < args.length) parsed.from = args[++i];
    else if (args[i] === "--to" && i + 1 < args.length) parsed.to = args[++i];
    else if (args[i] === "--amount" && i + 1 < args.length) parsed.amount = args[++i];
    else if (args[i] === "--date" && i + 1 < args.length) parsed.date = args[++i];
    else if (args[i] === "--format" && i + 1 < args.length) parsed.format = args[++i];
    else if (args[i] === "--timeout" && i + 1 < args.length) parsed.timeoutMs = (Number(args[++i]) || 5) * 1000;
    else if (args[i] === "--help" || args[i] === "-h") parsed.help = true;
  }

  return parsed;
}

function formatMarkdown(output) {
  const { from, to, rate, converted, amount, pair, tool_id, error } = output;
  if (error) return `## Exchange Rate\n\nError: ${error}\n`;

  let md = `## Exchange Rate\n\n**Pair:** ${pair || `${from}/${to}`}\n`;
  if (rate != null) md += `**Rate:** ${rate}\n`;
  if (amount != null && converted != null) md += `**${amount} ${from}** = **${converted} ${to}**\n`;
  if (tool_id) md += `\n*(via ${tool_id})*\n`;
  return md;
}

async function runRate(args) {
  const { from, to, date, format, timeoutMs } = args;
  if (!from || !to) throw new Error("rate requires --from and --to");

  let searchId = null;
  let candidates = [];

  for (const query of SEARCH_QUERIES) {
    const searchResult = await searchTools(query, 15, timeoutMs + 2000);
    searchId = searchId || searchResult.search_id;
    const results = searchResult.results ?? [];
    for (const tool of results) {
      if (!tool?.tool_id || !isRateTool(tool)) continue;
      if (candidates.some((c) => c.tool_id === tool.tool_id)) continue;
      candidates.push({ ...tool, search_id: searchResult.search_id });
    }
  }

  if (candidates.length === 0) {
    return { from, to, rate: null, converted: null, amount: null, pair: `${from}/${to}`, error: "No rate tools found." };
  }

  candidates.sort((a, b) => scoreTool(b, false) - scoreTool(a, false));

  const amount = null;
  for (const tool of candidates) {
    const params = buildParameters(tool, from, to, amount, date);
    if (Object.keys(params).length < 2) continue;
    try {
      const result = await executeTool(
        tool.tool_id,
        tool.search_id,
        params,
        MAX_RESPONSE_SIZE,
        timeoutMs,
      );
      if (!isExecutionSuccess(result)) continue;
      const data = result?.result ?? result;
      const extracted = extractRateAndConverted(data, from, to, amount);
      return {
        from,
        to,
        rate: extracted.rate,
        converted: extracted.converted,
        amount: null,
        pair: extracted.pair,
        tool_id: tool.tool_id,
      };
    } catch (_) {
      continue;
    }
  }

  return {
    from,
    to,
    rate: null,
    converted: null,
    amount: null,
    pair: `${from}/${to}`,
    error: "All rate lookups failed.",
  };
}

async function runConvert(args) {
  const { from, to, amount, date, format, timeoutMs } = args;
  if (!from || !to) throw new Error("convert requires --from and --to");
  const amountNum = amount != null && amount !== "" ? Number(amount) : null;
  if (amountNum == null || !Number.isFinite(amountNum)) throw new Error("convert requires --amount");

  let searchId = null;
  let candidates = [];

  for (const query of SEARCH_QUERIES) {
    const searchResult = await searchTools(query, 15, timeoutMs + 2000);
    searchId = searchId || searchResult.search_id;
    const results = searchResult.results ?? [];
    for (const tool of results) {
      if (!tool?.tool_id) continue;
      if (!isConversionTool(tool) && !isRateTool(tool)) continue;
      if (candidates.some((c) => c.tool_id === tool.tool_id)) continue;
      candidates.push({ ...tool, search_id: searchResult.search_id });
    }
  }

  if (candidates.length === 0) {
    return {
      from,
      to,
      rate: null,
      converted: null,
      amount: amountNum,
      pair: `${from}/${to}`,
      error: "No conversion tools found.",
    };
  }

  candidates.sort((a, b) => scoreTool(b, true) - scoreTool(a, true));

  for (const tool of candidates) {
    const params = buildParameters(tool, from, to, amountNum, date);
    if (Object.keys(params).length < 2) continue;
    try {
      const result = await executeTool(
        tool.tool_id,
        tool.search_id,
        params,
        MAX_RESPONSE_SIZE,
        timeoutMs,
      );
      if (!isExecutionSuccess(result)) continue;
      const data = result?.result ?? result;
      const extracted = extractRateAndConverted(data, from, to, amountNum);
      return {
        from,
        to,
        rate: extracted.rate,
        converted: extracted.converted,
        amount: amountNum,
        pair: extracted.pair,
        tool_id: tool.tool_id,
      };
    } catch (_) {
      continue;
    }
  }

  return {
    from,
    to,
    rate: null,
    converted: null,
    amount: amountNum,
    pair: `${from}/${to}`,
    error: "All conversions failed.",
  };
}

function printHelp() {
  console.log(`Exchange Rate (QVeris)

Usage:
  node scripts/exchange_rate.mjs rate --from USD --to EUR [options]
  node scripts/exchange_rate.mjs convert --from USD --to JPY --amount 1000 [options]

Options:
  --from CODE    Base currency code (e.g. USD, EUR, CNY)
  --to CODE      Quote currency code
  --amount N     Amount to convert (required for convert)
  --date YYYY-MM-DD   Optional date for historical rate
  --format markdown|json   Default markdown
  --timeout N    Timeout in seconds (default 5)
  --help         Show this message
`);
}

async function main() {
  const args = parseArgs(process.argv);
  if (args.help || !args.command) {
    printHelp();
    return;
  }

  let output;
  if (args.command === "rate") output = await runRate(args);
  else if (args.command === "convert") output = await runConvert(args);
  else throw new Error(`Unknown command: ${args.command}`);

  if (args.format === "json") {
    console.log(JSON.stringify(output, null, 2));
  } else {
    console.log(formatMarkdown(output));
  }
}

main().catch((err) => {
  if (err.name === "AbortError") console.error("Error: request timeout");
  else console.error(`Error: ${err.message}`);
  process.exit(1);
});
