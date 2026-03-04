#!/usr/bin/env node
// ZeroRules — Deterministic Task Interceptor for OpenClaw
// Zero tokens. Zero latency. Zero waste.
// https://cascadeai.dev

const fs = require("fs");
const path = require("path");

// --- Session state (persisted per-session in tmp) ---
const STATE_FILE = path.join(
  process.env.HOME || "/tmp",
  ".zerorules-session.json"
);

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_FILE, "utf8"));
  } catch {
    return { matches: 0, tokens_saved: 0, cost_saved: 0, history: [] };
  }
}

function saveState(state) {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state), "utf8");
  } catch {}
}

// --- Cost estimation ---
// Based on Claude Sonnet 4.5 pricing: ~$3/1M input + $15/1M output tokens
// Average intercepted query: ~200 input tokens + ~800 output tokens = ~$0.0126
// We estimate conservatively at $0.008 per intercepted call
const EST_COST_PER_CALL = 0.008;
const EST_TOKENS_MATH = 850;
const EST_TOKENS_TIME = 1200;
const EST_TOKENS_CURRENCY = 1500;
const EST_TOKENS_FILES = 900;
const EST_TOKENS_DATE = 1000;

// --- Rule definitions ---
const rules = [
  {
    name: "math",
    tokens: EST_TOKENS_MATH,
    patterns: [
      // Basic arithmetic: "247 × 18", "what's 100 + 50", "calculate 99 / 3"
      /(?:what(?:'s| is)|calculate|compute|solve|how much is)?\s*(\d[\d,]*\.?\d*)\s*([+\-×x*÷\/^%])\s*(\d[\d,]*\.?\d*)/i,
      // Percentage: "15% of 200", "what's 20% of 500"
      /(?:what(?:'s| is))?\s*(\d[\d,]*\.?\d*)\s*%\s*(?:of)\s*(\d[\d,]*\.?\d*)/i,
      // Square root: "sqrt of 144", "square root of 64"
      /(?:square root|sqrt)\s*(?:of)?\s*(\d[\d,]*\.?\d*)/i,
      // Power: "2 to the power of 10", "3^4"
      /(\d[\d,]*\.?\d*)\s*(?:to the power of|\^|raised to)\s*(\d[\d,]*\.?\d*)/i,
    ],
    handler(input) {
      const clean = input.replace(/,/g, "").replace(/×|x/gi, "*").replace(/÷/g, "/");

      // Percentage
      const pctMatch = clean.match(
        /(\d+\.?\d*)\s*%\s*(?:of)\s*(\d+\.?\d*)/i
      );
      if (pctMatch) {
        const result = (parseFloat(pctMatch[1]) / 100) * parseFloat(pctMatch[2]);
        return formatNumber(result);
      }

      // Square root
      const sqrtMatch = clean.match(
        /(?:square root|sqrt)\s*(?:of)?\s*(\d+\.?\d*)/i
      );
      if (sqrtMatch) {
        return formatNumber(Math.sqrt(parseFloat(sqrtMatch[1])));
      }

      // Power
      const powMatch = clean.match(
        /(\d+\.?\d*)\s*(?:to the power of|\^|raised to)\s*(\d+\.?\d*)/i
      );
      if (powMatch) {
        return formatNumber(
          Math.pow(parseFloat(powMatch[1]), parseFloat(powMatch[2]))
        );
      }

      // Basic arithmetic — extract the operation
      const arithMatch = clean.match(
        /(\d+\.?\d*)\s*([+\-*\/^%])\s*(\d+\.?\d*)/
      );
      if (arithMatch) {
        const a = parseFloat(arithMatch[1]);
        const op = arithMatch[2];
        const b = parseFloat(arithMatch[3]);
        let result;
        switch (op) {
          case "+": result = a + b; break;
          case "-": result = a - b; break;
          case "*": result = a * b; break;
          case "/": result = b !== 0 ? a / b : "Error: division by zero"; break;
          case "^": result = Math.pow(a, b); break;
          case "%": result = a % b; break;
          default: return null;
        }
        return typeof result === "number" ? formatNumber(result) : result;
      }
      return null;
    },
  },

  {
    name: "time",
    tokens: EST_TOKENS_TIME,
    patterns: [
      // "what time is it in Tokyo", "what's the time in London"
      /(?:what(?:'s| is) the time|what time is it) (?:in|at|for) ([a-z\s\/]+)/i,
      // "time in Tokyo", "current time in Paris"
      /(?:what(?:'s| is) the )?(?:current )?time (?:in|at|for) ([a-z\s\/]+)/i,
      // "what's it now in Berlin", "time now in NYC"
      /(?:what(?:'s| is) it|time) (?:now )?(?:in|at) ([a-z\s\/]+)/i,
    ],
    async handler(input) {
      const cityMatch = input.match(
        /(?:time|what(?:'s| is)(?: the| it)?)[\s\w]*?(?:in|at|for)\s+([a-z\s\/]+)/i
      );
      if (!cityMatch) return null;
      const city = cityMatch[1].trim();

      // Map common city names to IANA timezones
      const tzMap = {
        tokyo: "Asia/Tokyo", london: "Europe/London", paris: "Europe/Paris",
        "new york": "America/New_York", nyc: "America/New_York",
        "los angeles": "America/Los_Angeles", la: "America/Los_Angeles",
        chicago: "America/Chicago", denver: "America/Denver",
        berlin: "Europe/Berlin", sydney: "Australia/Sydney",
        singapore: "Asia/Singapore", dubai: "Asia/Dubai",
        mumbai: "Asia/Kolkata", delhi: "Asia/Kolkata",
        shanghai: "Asia/Shanghai", beijing: "Asia/Shanghai",
        "hong kong": "Asia/Hong_Kong", seoul: "Asia/Seoul",
        moscow: "Europe/Moscow", "sao paulo": "America/Sao_Paulo",
        toronto: "America/Toronto", vancouver: "America/Vancouver",
        amsterdam: "Europe/Amsterdam", rome: "Europe/Rome",
        madrid: "Europe/Madrid", istanbul: "Europe/Istanbul",
        cairo: "Africa/Cairo", lagos: "Africa/Lagos",
        nairobi: "Africa/Nairobi", johannesburg: "Africa/Johannesburg",
        bangkok: "Asia/Bangkok", jakarta: "Asia/Jakarta",
        manila: "Asia/Manila", taipei: "Asia/Taipei",
        auckland: "Pacific/Auckland", hawaii: "Pacific/Honolulu",
        anchorage: "America/Anchorage", phoenix: "America/Phoenix",
        "mexico city": "America/Mexico_City", lima: "America/Lima",
        bogota: "America/Bogota", "buenos aires": "America/Argentina/Buenos_Aires",
        lisbon: "Europe/Lisbon", dublin: "Europe/Dublin",
        zurich: "Europe/Zurich", vienna: "Europe/Vienna",
        prague: "Europe/Prague", warsaw: "Europe/Warsaw",
        helsinki: "Europe/Helsinki", stockholm: "Europe/Stockholm",
        oslo: "Europe/Oslo", copenhagen: "Europe/Copenhagen",
        athens: "Europe/Athens", bucharest: "Europe/Bucharest",
        kyiv: "Europe/Kyiv", riyadh: "Asia/Riyadh",
        doha: "Asia/Qatar", karachi: "Asia/Karachi",
        dhaka: "Asia/Dhaka", kolkata: "Asia/Kolkata",
        "kuala lumpur": "Asia/Kuala_Lumpur", hanoi: "Asia/Ho_Chi_Minh",
        perth: "Australia/Perth", melbourne: "Australia/Melbourne",
        brisbane: "Australia/Brisbane",
      };

      const tz = tzMap[city.toLowerCase()];
      if (!tz) {
        // Try using the city name as a timezone directly (e.g., "UTC", "EST")
        try {
          const now = new Date();
          const formatted = now.toLocaleString("en-US", {
            timeZone: city.replace(/\s/g, "_"),
            weekday: "short", hour: "2-digit", minute: "2-digit",
            hour12: false, timeZoneName: "short",
          });
          return formatted;
        } catch {
          return null; // Can't resolve — let LLM handle it
        }
      }

      const now = new Date();
      const formatted = now.toLocaleString("en-US", {
        timeZone: tz,
        weekday: "short", month: "short", day: "numeric",
        hour: "2-digit", minute: "2-digit", hour12: false,
        timeZoneName: "short",
      });
      return formatted;
    },
  },

  {
    name: "currency",
    tokens: EST_TOKENS_CURRENCY,
    patterns: [
      /(?:convert\s+)?([€$£¥₹]?)(\d[\d,]*\.?\d*)\s*([A-Z]{3})?\s*(?:to|in|into)\s*([A-Z]{3})/i,
      /how much is ([€$£¥₹]?)(\d[\d,]*\.?\d*)\s*([A-Z]{3})?\s*in\s*([A-Z]{3})/i,
    ],
    async handler(input) {
      // Parse the conversion request
      const match = input.match(
        /([€$£¥₹]?)(\d[\d,]*\.?\d*)\s*([A-Z]{3})?\s*(?:to|in|into)\s*([A-Z]{3})/i
      );
      if (!match) return null;

      const symbolMap = { $: "USD", "€": "EUR", "£": "GBP", "¥": "JPY", "₹": "INR" };
      const amount = parseFloat(match[2].replace(/,/g, ""));
      const from = (match[3] || symbolMap[match[1]] || "USD").toUpperCase();
      const to = match[4].toUpperCase();

      try {
        // Use exchangerate.host (free, no key required)
        const url = `https://api.exchangerate.host/convert?from=${from}&to=${to}&amount=${amount}`;
        const resp = await fetchWithTimeout(url, 3000);
        const data = JSON.parse(resp);
        if (data && data.result) {
          const symbols = { USD: "$", EUR: "€", GBP: "£", JPY: "¥", INR: "₹" };
          const sym = symbols[to] || "";
          return `${sym}${formatNumber(data.result)} ${to}`;
        }
      } catch {}

      // Fallback: use a static approximation table (updated periodically)
      // This ensures the rule still fires even without network
      const ratesVsUSD = {
        EUR: 0.92, GBP: 0.79, JPY: 149.5, CAD: 1.36, AUD: 1.55,
        CHF: 0.88, CNY: 7.24, INR: 83.1, BRL: 4.97, MXN: 17.15,
        KRW: 1335, SGD: 1.34, HKD: 7.82, SEK: 10.45, NOK: 10.52,
        NZD: 1.67, TRY: 30.2, ZAR: 18.6, THB: 35.1, PHP: 55.8,
      };
      ratesVsUSD.USD = 1;

      if (ratesVsUSD[from] && ratesVsUSD[to]) {
        const inUSD = amount / ratesVsUSD[from];
        const result = inUSD * ratesVsUSD[to];
        const symbols = { USD: "$", EUR: "€", GBP: "£", JPY: "¥", INR: "₹" };
        const sym = symbols[to] || "";
        return `≈ ${sym}${formatNumber(result)} ${to} (offline rate)`;
      }
      return null;
    },
  },

  {
    name: "files",
    tokens: EST_TOKENS_FILES,
    patterns: [
      /(?:list|show|ls|dir)\s+(?:(?:the\s+)?files?\s+(?:in|at|of)\s+)?([~\/][\w\/\-._]+|\.)/i,
      /(?:what(?:'s| is| are)(?: the)?) (?:in|files? (?:in|at|of))\s+([~\/][\w\/\-._]+|\.)/i,
    ],
    handler(input) {
      const match = input.match(
        /(?:list|show|ls|dir|what(?:'s| is| are)(?: the)?)\s+(?:(?:the\s+)?files?\s+)?(?:in|at|of)?\s*([~\/][\w\/\-._]+|\.)/i
      );
      if (!match) return null;

      let dirPath = match[1].trim();
      // Expand ~ to home directory
      if (dirPath.startsWith("~")) {
        dirPath = dirPath.replace("~", process.env.HOME || "/home");
      }

      // SECURITY: Only list, never read/write/delete
      // Block path traversal
      const resolved = path.resolve(dirPath);
      if (resolved.includes("..")) return null;

      try {
        const entries = fs.readdirSync(resolved, { withFileTypes: true });
        const formatted = entries
          .slice(0, 50) // Cap at 50 entries to prevent context bloat
          .map((e) => (e.isDirectory() ? `📁 ${e.name}/` : `  ${e.name}`))
          .join("\n");
        const total = entries.length;
        const suffix = total > 50 ? `\n... and ${total - 50} more` : "";
        return `${resolved}/ (${total} items)\n${formatted}${suffix}`;
      } catch (err) {
        if (err.code === "ENOENT") return `Directory not found: ${dirPath}`;
        if (err.code === "EACCES") return `Permission denied: ${dirPath}`;
        return null; // Unknown error — let LLM handle
      }
    },
  },

  {
    name: "date",
    tokens: EST_TOKENS_DATE,
    patterns: [
      /what (?:day|date) is (?:it )?(?:today|tomorrow|yesterday)/i,
      /(?:what(?:'s| is) (?:today's|the|today) date)/i,
      /(?:how many )?days? (?:until|to|before|left|till) (.+)/i,
      /what day (?:is|was|will) (.+)/i,
    ],
    handler(input) {
      const now = new Date();
      const clean = input.toLowerCase().trim();

      // Today/tomorrow/yesterday
      if (/today/.test(clean)) {
        return now.toLocaleDateString("en-US", {
          weekday: "long", year: "numeric", month: "long", day: "numeric",
        });
      }
      if (/tomorrow/.test(clean)) {
        const tmrw = new Date(now);
        tmrw.setDate(tmrw.getDate() + 1);
        return tmrw.toLocaleDateString("en-US", {
          weekday: "long", year: "numeric", month: "long", day: "numeric",
        });
      }
      if (/yesterday/.test(clean)) {
        const ystr = new Date(now);
        ystr.setDate(ystr.getDate() - 1);
        return ystr.toLocaleDateString("en-US", {
          weekday: "long", year: "numeric", month: "long", day: "numeric",
        });
      }

      // Days until [event/date]
      const untilMatch = clean.match(
        /days?\s*(?:until|to|before|left|till)\s+(.+)/i
      );
      if (untilMatch) {
        const target = untilMatch[1].trim();
        // Try common holidays
        const year = now.getFullYear();
        const nextYear = year + 1;
        const holidays = {
          christmas: new Date(year, 11, 25),
          "new year": new Date(nextYear, 0, 1),
          "new years": new Date(nextYear, 0, 1),
          valentine: new Date(year, 1, 14),
          "valentines day": new Date(year, 1, 14),
          halloween: new Date(year, 9, 31),
          "independence day": new Date(year, 6, 4),
          "july 4th": new Date(year, 6, 4),
          "4th of july": new Date(year, 6, 4),
        };

        let targetDate = holidays[target];

        // Try parsing as a date string
        if (!targetDate) {
          const parsed = new Date(target);
          if (!isNaN(parsed.getTime())) {
            targetDate = parsed;
          }
        }

        if (targetDate) {
          // If holiday has passed this year, use next year
          if (targetDate < now && holidays[target]) {
            targetDate.setFullYear(nextYear);
          }
          const diff = Math.ceil((targetDate - now) / (1000 * 60 * 60 * 24));
          const dateStr = targetDate.toLocaleDateString("en-US", {
            weekday: "long", month: "long", day: "numeric", year: "numeric",
          });
          return `${diff} days until ${target} (${dateStr})`;
        }
        return null;
      }

      // What day is [date]
      const dayMatch = clean.match(/what day (?:is|was|will(?: be)?)\s+(.+)/i);
      if (dayMatch) {
        const parsed = new Date(dayMatch[1].trim());
        if (!isNaN(parsed.getTime())) {
          return parsed.toLocaleDateString("en-US", {
            weekday: "long", year: "numeric", month: "long", day: "numeric",
          });
        }
      }
      return null;
    },
  },
];

// --- Utilities ---
function formatNumber(n) {
  if (typeof n !== "number" || isNaN(n)) return String(n);
  // Integers: add commas. Floats: max 2 decimal places with commas
  if (Number.isInteger(n)) {
    return n.toLocaleString("en-US");
  }
  return n.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function fetchWithTimeout(url, timeoutMs) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("timeout")), timeoutMs);
    const https = url.startsWith("https") ? require("https") : require("http");
    https
      .get(url, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => { clearTimeout(timer); resolve(data); });
      })
      .on("error", (err) => { clearTimeout(timer); reject(err); });
  });
}

// --- Main execution ---
async function main() {
  const args = process.argv.slice(2);

  // Handle --status flag
  if (args[0] === "--status") {
    const state = loadState();
    const output = {
      status: "active",
      rules_available: rules.length,
      session_matches: state.matches,
      session_tokens_saved: state.tokens_saved,
      session_cost_saved: parseFloat(state.cost_saved.toFixed(4)),
      rules: rules.map((r) => r.name),
      tier: "free",
      upgrade_url: "https://cascadeai.dev/pro",
    };
    console.log(JSON.stringify(output));
    return;
  }

  // Handle --test flag
  if (args[0] === "--test") {
    const testInput = args.slice(1).join(" ");
    if (!testInput) {
      console.log(JSON.stringify({ error: "Usage: --test <message>" }));
      return;
    }
    for (const rule of rules) {
      for (const pattern of rule.patterns) {
        if (pattern.test(testInput)) {
          console.log(
            JSON.stringify({
              would_match: true,
              rule: rule.name,
              pattern: pattern.toString(),
            })
          );
          return;
        }
      }
    }
    console.log(JSON.stringify({ would_match: false }));
    return;
  }

  // Normal execution: try to match input against rules
  const input = args.join(" ");
  if (!input) {
    console.log(JSON.stringify({ matched: false, error: "No input provided" }));
    return;
  }

  for (const rule of rules) {
    for (const pattern of rule.patterns) {
      if (pattern.test(input)) {
        try {
          const result = await rule.handler(input);
          if (result !== null && result !== undefined) {
            // Update session state
            const state = loadState();
            state.matches += 1;
            state.tokens_saved += rule.tokens;
            state.cost_saved += EST_COST_PER_CALL;
            state.history.push({
              rule: rule.name,
              timestamp: new Date().toISOString(),
              tokens: rule.tokens,
            });
            saveState(state);

            console.log(
              JSON.stringify({
                matched: true,
                rule: rule.name,
                result: String(result),
                saved_tokens_est: rule.tokens,
                session_matches: state.matches,
                session_total_saved: parseFloat(state.cost_saved.toFixed(4)),
              })
            );
            return;
          }
        } catch (err) {
          // Rule handler failed — fall through to LLM
        }
      }
    }
  }

  // No match
  console.log(JSON.stringify({ matched: false }));
}

main().catch(() => {
  console.log(JSON.stringify({ matched: false, error: "internal" }));
  process.exit(0); // Never crash — always let OpenClaw continue
});
