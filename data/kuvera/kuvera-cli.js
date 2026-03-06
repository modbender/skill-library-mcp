#!/usr/bin/env node
// kuvera-cli: CLI wrapper for Kuvera's unofficial API
const https = require("https");
const fs = require("fs");
const path = require("path");

const CRED_DIR = path.join(process.env.HOME, ".openclaw", "credentials", "kuvera");
const TOKEN_FILE = path.join(CRED_DIR, "token.json");
const BASE = "api.kuvera.in";

// SAFETY: This CLI is READ-ONLY. Only GET requests and the login POST are allowed.
// Never add PUT, PATCH, DELETE, or any POST that modifies portfolio/transactions.
const ALLOWED_WRITE_PATHS = ["/api/v5/users/authenticate.json"];

function request(method, urlPath, body = null, token = null) {
  if (method !== "GET" && !ALLOWED_WRITE_PATHS.includes(urlPath)) {
    return Promise.reject(new Error(`BLOCKED: ${method} ${urlPath} — kuvera-cli is read-only. Write operations are not permitted.`));
  }
  return new Promise((resolve, reject) => {
    const headers = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;
    const opts = { hostname: BASE, port: 443, path: urlPath, method, headers };
    const req = https.request(opts, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => {
        try { resolve(JSON.parse(data)); }
        catch { resolve(data); }
      });
    });
    req.on("error", reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

function saveToken(data) {
  fs.mkdirSync(CRED_DIR, { recursive: true });
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(data, null, 2));
}

function loadToken() {
  try { return JSON.parse(fs.readFileSync(TOKEN_FILE, "utf8")); }
  catch { return null; }
}

async function login(email, password) {
  const res = await request("POST", "/api/v5/users/authenticate.json", { email, password });
  if (res.status === "success") {
    saveToken({ token: res.token, name: res.name, email: res.email, saved_at: new Date().toISOString() });
    console.log(`✅ Logged in as ${res.name} (${res.email})`);
  } else {
    console.error("❌ Login failed:", JSON.stringify(res));
    process.exit(1);
  }
}

async function userInfo() {
  const cred = requireLogin();
  const res = await request("GET", "/api/v3/user/info.json", null, cred.token);
  if (res.id) {
    console.log(`Name: ${res.name}`);
    console.log(`Email: ${res.email}`);
    console.log(`Phone: ${res.mobile_phone}`);
    console.log(`DOB: ${res.dob}`);
    if (res.current_portfolio) {
      console.log(`Portfolio: ${res.current_portfolio.name} (${res.current_portfolio.mode_of_investment})`);
      console.log(`Smart Switch: ${res.current_portfolio.smart_switch}`);
      console.log(`Tax Harvesting: ${res.current_portfolio.tax_harvesting}`);
    }
  } else {
    console.error("❌ Failed to fetch user info. Token may have expired. Run: kuvera-cli login <email> <password>");
    console.error(JSON.stringify(res));
  }
}

function requireLogin() {
  const cred = loadToken();
  if (!cred) { console.error("❌ Not logged in. Run: kuvera-cli login <email> <password>"); process.exit(1); }
  return cred;
}

async function portfolio() {
  const cred = requireLogin();
  const [info, holdings, txns] = await Promise.all([
    request("GET", "/api/v3/portfolio.json", null, cred.token),
    request("GET", "/api/v3/portfolio/holdings.json", null, cred.token),
    request("GET", "/api/v3/portfolio/transactions.json", null, cred.token),
  ]);
  console.log(`Portfolio: ${info.portfolio_name} (${info.mode_of_investment})`);
  console.log(`Code: ${info.portfolio_code}\n`);
  if (typeof holdings === "object" && !Array.isArray(holdings)) {
    const codes = Object.keys(holdings);
    if (codes.length === 0) { console.log("No holdings found."); return; }
    // Build name & NAV map from transactions (most reliable source)
    const fundInfo = {};
    if (Array.isArray(txns)) {
      for (const t of txns) {
        if (t.code && !fundInfo[t.code]) fundInfo[t.code] = { name: t.name || t.scheme_name, nav: t.latest_nav };
      }
    }
    let totalInvested = 0, totalCurrent = 0;
    const rows = [];
    for (const code of codes) {
      const folios = holdings[code];
      let units = 0, invested = 0;
      for (const f of folios) { units += f.units; invested += f.allottedAmount; }
      const nav = fundInfo[code]?.nav || 0;
      const current = units * nav;
      totalInvested += invested;
      totalCurrent += current;
      rows.push({ name: fundInfo[code]?.name || code, code, units, invested, current, nav });
    }
    console.log(`${"Fund".padEnd(42)} ${"Units".padStart(10)} ${"Invested".padStart(12)} ${"Current".padStart(12)} ${"P&L".padStart(12)}`);
    console.log("-".repeat(92));
    for (const r of rows) {
      const pnl = r.current - r.invested;
      console.log(`${r.name.substring(0, 41).padEnd(42)} ${r.units.toFixed(2).padStart(10)} ${("₹" + r.invested.toFixed(0)).padStart(12)} ${("₹" + r.current.toFixed(0)).padStart(12)} ${((pnl >= 0 ? "+" : "") + "₹" + pnl.toFixed(0)).padStart(12)}`);
    }
    console.log("-".repeat(92));
    const totalPnl = totalCurrent - totalInvested;
    const pnlPct = totalInvested > 0 ? ((totalPnl / totalInvested) * 100).toFixed(1) : "0.0";
    console.log(`${"TOTAL".padEnd(42)} ${"".padStart(10)} ${("₹" + totalInvested.toFixed(0)).padStart(12)} ${("₹" + totalCurrent.toFixed(0)).padStart(12)} ${((totalPnl >= 0 ? "+" : "") + "₹" + totalPnl.toFixed(0) + " (" + pnlPct + "%)").padStart(12)}`);
  } else {
    console.error("❌ Failed to fetch holdings. Token may have expired.");
  }
}

async function transactions(limit) {
  const cred = requireLogin();
  const res = await request("GET", "/api/v3/portfolio/transactions.json", null, cred.token);
  if (Array.isArray(res)) {
    const txns = limit ? res.slice(0, limit) : res;
    if (txns.length === 0) { console.log("No transactions found."); return; }
    console.log(`Showing ${txns.length} of ${res.length} transactions:\n`);
    console.log(`${"Date".padEnd(12)} ${"Type".padEnd(8)} ${"Fund".padEnd(40)} ${"Units".padStart(10)} ${"NAV".padStart(10)} ${"Amount".padStart(12)}`);
    console.log("-".repeat(96));
    for (const t of txns) {
      const date = t.order_date || t.trade_date?.substring(0, 10) || "";
      const type = (t.order_sub_type || t.trans_type || "").substring(0, 7);
      const name = (t.name || t.scheme_code || "").substring(0, 39);
      console.log(`${date.padEnd(12)} ${type.padEnd(8)} ${name.padEnd(40)} ${t.units.toFixed(3).padStart(10)} ${("₹" + t.nav.toFixed(2)).padStart(10)} ${("₹" + t.allotted_amount.toFixed(0)).padStart(12)}`);
    }
  } else {
    console.error("❌ Failed to fetch transactions. Token may have expired.");
  }
}

async function sips() {
  const cred = requireLogin();
  const res = await request("GET", "/api/v3/portfolio/sips.json", null, cred.token);
  if (Array.isArray(res)) {
    if (res.length === 0) { console.log("No active SIPs found."); return; }
    for (const s of res) {
      console.log(`${s.scheme_name || s.code}: ₹${s.amount} on ${s.sip_date} (${s.frequency || "monthly"})`);
    }
  } else {
    console.error("❌ Failed to fetch SIPs. Token may have expired.");
  }
}

async function goldPrice() {
  const res = await request("GET", "/api/v3/gold/current_price.json");
  if (res.current_gold_price) {
    console.log(`Gold Buy Price: ₹${res.current_gold_price.buy}/gm`);
    console.log(`Gold Sell Price: ₹${res.current_gold_price.sell}/gm`);
    console.log(`Fetched at: ${res.fetched_at}`);
    console.log(`GST: CGST ${res.taxes.cgst}%, SGST ${res.taxes.sgst}%, IGST ${res.taxes.igst}%`);
  } else {
    console.error("Failed to fetch gold prices");
  }
}

async function marketOverview() {
  const [cats, gold, usd] = await Promise.all([
    request("GET", "/mf/api/v4/fund_categories.json"),
    request("GET", "/api/v3/gold/current_price.json"),
    request("GET", "/vested/api/v1/exchange_rates/live.json"),
  ]);
  console.log("=== Market Overview ===\n");
  if (gold.current_gold_price) {
    console.log(`Gold: ₹${gold.current_gold_price.buy}/gm (buy) | ₹${gold.current_gold_price.sell}/gm (sell)`);
  }
  if (usd.status === "success") {
    console.log(`USD/INR: ₹${usd.data.price}`);
  }
  console.log("");
  if (Array.isArray(cats)) {
    // Show key categories
    const key = ["Large Cap Fund", "Mid Cap Fund", "Small Cap Fund", "ELSS", "Aggressive Hybrid Fund", "Liquid Fund"];
    const filtered = cats.filter((c) => key.includes(c.category_name));
    console.log("Key MF Category Returns (%):");
    console.log("-".repeat(70));
    console.log(`${"Category".padEnd(28)} ${"1M".padStart(7)} ${"3M".padStart(7)} ${"1Y".padStart(7)} ${"3Y".padStart(7)} ${"5Y".padStart(7)}`);
    console.log("-".repeat(70));
    for (const cat of filtered) {
      console.log(
        `${cat.category_name.padEnd(28)} ${(cat.month_1?.toFixed(1) || "-").padStart(7)} ${(cat.month_3?.toFixed(1) || "-").padStart(7)} ${(cat.year_1?.toFixed(1) || "-").padStart(7)} ${(cat.year_3?.toFixed(1) || "-").padStart(7)} ${(cat.year_5?.toFixed(1) || "-").padStart(7)}`
      );
    }
  }
}

async function fundCategories() {
  const res = await request("GET", "/mf/api/v4/fund_categories.json");
  if (Array.isArray(res)) {
    console.log("Fund Category Returns (%):");
    console.log("-".repeat(90));
    console.log(`${"Category".padEnd(30)} ${"1M".padStart(7)} ${"3M".padStart(7)} ${"1Y".padStart(7)} ${"3Y".padStart(7)} ${"5Y".padStart(7)}`);
    console.log("-".repeat(90));
    for (const cat of res) {
      console.log(
        `${cat.category_name.padEnd(30)} ${(cat.month_1?.toFixed(1) || "-").padStart(7)} ${(cat.month_3?.toFixed(1) || "-").padStart(7)} ${(cat.year_1?.toFixed(1) || "-").padStart(7)} ${(cat.year_3?.toFixed(1) || "-").padStart(7)} ${(cat.year_5?.toFixed(1) || "-").padStart(7)}`
      );
    }
  } else {
    console.error("Failed to fetch fund categories");
  }
}

async function fundDetails(codes) {
  const res = await request("GET", `/mf/api/v4/fund_schemes/${codes}.json`);
  if (Array.isArray(res)) {
    for (const f of res) {
      console.log(`Fund: ${f.name}`);
      console.log(`Code: ${f.code} | ISIN: ${f.ISIN}`);
      console.log(`Category: ${f.fund_category} | Type: ${f.fund_type}`);
      console.log(`Fund House: ${f.fund_house}`);
      console.log(`NAV: ₹${f.nav?.nav} (${f.nav?.date})`);
      console.log(`AUM: ₹${(f.aum / 10000000).toFixed(2)} Cr`);
      console.log(`Expense Ratio: ${f.expense_ratio}% (as of ${f.expense_ratio_date})`);
      if (f.returns) {
        console.log(`Returns: 1W: ${f.returns.week_1}% | 1Y: ${f.returns.year_1}% | 3Y: ${f.returns.year_3}% | 5Y: ${f.returns.year_5}%`);
      }
      console.log(`Fund Manager: ${f.fund_manager}`);
      console.log("---");
    }
  } else {
    console.error("Fund not found or error:", JSON.stringify(res));
  }
}

async function topFunds(type) {
  const endpoints = {
    bought: "/api/v3/funds/tags/top_bought.json",
    sold: "/api/v3/funds/tags/top_sold.json",
    watched: "/api/v3/funds/tags/top_watchlist.json",
  };
  const url = endpoints[type];
  if (!url) { console.error(`Unknown type: ${type}. Use: bought, sold, watched`); process.exit(1); }
  const codes = await request("GET", url);
  if (Array.isArray(codes) && codes.length > 0) {
    console.log(`Top ${type} funds: ${codes.join(", ")}`);
    // Fetch details for top 5
    const top5 = codes.slice(0, 5).join(",");
    await fundDetails(top5);
  } else {
    console.error("Failed to fetch top funds");
  }
}

async function exchangeRate() {
  const res = await request("GET", "/vested/api/v1/exchange_rates/live.json");
  if (res.status === "success" && res.data) {
    console.log(`USD/INR: ₹${res.data.price}`);
    console.log(`Updated: ${res.data.date}`);
  } else {
    console.error("Failed to fetch exchange rate");
  }
}

async function main() {
  const [,, cmd, ...args] = process.argv;
  switch (cmd) {
    case "login":
      if (args.length < 2) { console.error("Usage: kuvera-cli login <email> <password>"); process.exit(1); }
      await login(args[0], args[1]);
      break;
    case "user":
      await userInfo();
      break;
    case "gold":
      await goldPrice();
      break;
    case "nifty":
    case "nifty50":
    case "market":
      await marketOverview();
      break;
    case "categories":
      await fundCategories();
      break;
    case "fund":
      if (!args[0]) { console.error("Usage: kuvera-cli fund <code1,code2,...>"); process.exit(1); }
      await fundDetails(args[0]);
      break;
    case "top":
      await topFunds(args[0] || "bought");
      break;
    case "usd":
    case "forex":
      await exchangeRate();
      break;
    case "portfolio":
    case "holdings":
      await portfolio();
      break;
    case "transactions":
    case "txns":
      await transactions(parseInt(args[0]) || 20);
      break;
    case "sips":
      await sips();
      break;
    case "help":
    default:
      console.log(`kuvera-cli — Kuvera Portfolio & Market Data CLI

Commands:
  login <email> <password>   Login to Kuvera (stores JWT token)
  user                       Show user profile & portfolio info (requires login)
  portfolio                  Investment holdings with P&L summary (requires login)
  transactions [N]           Recent transactions, last N (default 20) (requires login)
  sips                       Active SIP registrations (requires login)
  market                     Market overview: gold, USD/INR, key MF category returns
  gold                       Current gold buy/sell prices
  categories                 All mutual fund category returns
  fund <code1,code2>         Mutual fund details by code (e.g., LFAG-GR)
  top <bought|sold|watched>  Top mutual funds by activity
  usd                        Current USD/INR exchange rate
  help                       Show this help message`);
  }
}

main().catch((e) => { console.error("Error:", e.message); process.exit(1); });
