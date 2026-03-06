#!/usr/bin/env node

const https = require("https");
const http = require("http");
const fs = require("fs");
const path = require("path");
const os = require("os");

const BASE_URL = "http://api-pro.theblockbeats.info";
const CONFIG_DIR = path.join(os.homedir(), ".openclaw", "skills", "blockbeats-openclaw-skill");
const CONFIG_FILE = path.join(CONFIG_DIR, "config.json");

// ── Config ────────────────────────────────────────────────────────────────────

function loadToken() {
  try {
    if (fs.existsSync(CONFIG_FILE)) {
      const cfg = JSON.parse(fs.readFileSync(CONFIG_FILE, "utf8"));
      return cfg.token || null;
    }
  } catch (_) {}
  return null;
}

function saveToken(token) {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify({ token }, null, 2), "utf8");
}

// ── HTTP ──────────────────────────────────────────────────────────────────────

function request(urlStr, token) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === "https:" ? 443 : 80),
      path: url.pathname + url.search,
      method: "GET",
      headers: { "api-key": token, "Content-Type": "application/json" },
    };
    const lib = url.protocol === "https:" ? https : http;
    const req = lib.request(options, (res) => {
      let body = "";
      res.setEncoding("utf8");
      res.on("data", (chunk) => (body += chunk));
      res.on("end", () => {
        try {
          resolve(JSON.parse(body));
        } catch (e) {
          reject(new Error("响应解析失败: " + body.slice(0, 200)));
        }
      });
    });
    req.on("error", reject);
    req.setTimeout(15000, () => { req.destroy(); reject(new Error("请求超时")); });
    req.end();
  });
}

function buildUrl(path, params) {
  const url = new URL(BASE_URL + path);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v);
  });
  return url.toString();
}

// ── Formatters ────────────────────────────────────────────────────────────────

function stripHtml(html) {
  return (html || "").replace(/<[^>]+>/g, "").replace(/\s+/g, " ").trim();
}

function formatTime(ts) {
  return new Date(Number(ts) * 1000).toLocaleString("zh-CN", { hour12: false });
}

function printNewsflashes(items) {
  if (!items || items.length === 0) { console.log("暂无数据"); return; }
  items.forEach((item, i) => {
    console.log(`\n[${ i + 1 }] #${item.id} ${item.title}`);
    console.log(`    时间: ${formatTime(item.create_time)}`);
    const text = stripHtml(item.content);
    if (text) console.log(`    内容: ${text.slice(0, 200)}${text.length > 200 ? "…" : ""}`);
    if (item.link) console.log(`    链接: ${item.link}`);
  });
}

function printArticles(items) {
  if (!items || items.length === 0) { console.log("暂无数据"); return; }
  items.forEach((item, i) => {
    console.log(`\n[${ i + 1 }] #${item.id} ${item.title}`);
    if (item.author) console.log(`    作者: ${item.author}`);
    if (item.create_time) console.log(`    时间: ${formatTime(item.create_time)}`);
    if (item.desc || item.summary) {
      const desc = stripHtml(item.desc || item.summary);
      if (desc) console.log(`    摘要: ${desc.slice(0, 200)}${desc.length > 200 ? "…" : ""}`);
    }
    if (item.link) console.log(`    链接: ${item.link}`);
  });
}

function printArticleDetail(item) {
  if (!item) { console.log("未找到文章"); return; }
  console.log(`\n标题: ${item.title}`);
  if (item.author) console.log(`作者: ${item.author}`);
  if (item.create_time) console.log(`时间: ${formatTime(item.create_time)}`);
  if (item.link) console.log(`链接: ${item.link}`);
  console.log("\n--- 内容 ---");
  const text = stripHtml(item.content || item.body || "");
  console.log(text || "（无内容）");
}

// ── Commands ──────────────────────────────────────────────────────────────────

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true;
    } else {
      args._.push(argv[i]);
    }
  }
  return args;
}

async function cmdSetToken(token) {
  if (!token) { console.error("用法: set-token <api-key>"); process.exit(1); }
  saveToken(token);
  console.log("Token 已保存：" + CONFIG_FILE);
}

async function cmdNewsflash(args, token) {
  const typeMap = {
    important: "/v1/newsflash/important",
    original:  "/v1/newsflash/original",
    first:     "/v1/newsflash/first",
    onchain:   "/v1/newsflash/onchain",
    financing: "/v1/newsflash/financing",
    prediction:"/v1/newsflash/prediction",
  };
  const apiPath = args.type ? (typeMap[args.type] || "/v1/newsflash") : "/v1/newsflash";
  const params = {
    page: args.page || 1,
    size: args.size || 10,
    lang: args.lang || "cn",
  };
  const url = buildUrl(apiPath, params);
  console.log(`正在获取快讯 [${args.type || "全部"}] page=${params.page} size=${params.size} lang=${params.lang} ...`);
  const res = await request(url, token);
  if (res.status !== 0) { console.error("API 错误:", res.message || res.status); process.exit(1); }
  const items = res.data?.data || [];
  console.log(`共 ${items.length} 条快讯（第 ${res.data?.page || params.page} 页）`);
  printNewsflashes(items);
}

async function cmdArticle(args, token) {
  const params = {
    page: args.page || 1,
    size: args.size || 10,
    lang: args.lang || "cn",
  };
  const url = buildUrl("/v1/article", params);
  console.log(`正在获取文章列表 page=${params.page} size=${params.size} lang=${params.lang} ...`);
  const res = await request(url, token);
  if (res.status !== 0) { console.error("API 错误:", res.message || res.status); process.exit(1); }
  const items = res.data?.data || [];
  console.log(`共 ${items.length} 篇文章（第 ${res.data?.page || params.page} 页）`);
  printArticles(items);
}

async function cmdArticleDetail(id, args, token) {
  if (!id) { console.error("用法: article-detail <id>"); process.exit(1); }
  const params = { lang: args.lang || "cn" };
  const url = buildUrl(`/v1/article/${id}`, params);
  console.log(`正在获取文章 #${id} ...`);
  const res = await request(url, token);
  if (res.status !== 0) { console.error("API 错误:", res.message || res.status); process.exit(1); }
  printArticleDetail(res.data);
}

// ── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const argv = process.argv.slice(2);
  const cmd = argv[0];
  const args = parseArgs(argv.slice(1));

  if (cmd === "set-token") {
    await cmdSetToken(args._[0]);
    return;
  }

  const token = loadToken();
  if (!token) {
    console.error("未设置 API Token。");
    console.error("请先执行：设置 BlockBeats token: <your-api-key>");
    console.error("或运行：node api.js set-token <your-api-key>");
    process.exit(1);
  }

  switch (cmd) {
    case "newsflash":
      await cmdNewsflash(args, token);
      break;
    case "article":
      await cmdArticle(args, token);
      break;
    case "article-detail":
      await cmdArticleDetail(args._[0], args, token);
      break;
    default:
      console.log("BlockBeats API Skill");
      console.log("");
      console.log("用法:");
      console.log("  node api.js set-token <api-key>          设置 API Token");
      console.log("  node api.js newsflash [选项]              获取快讯列表");
      console.log("  node api.js article [选项]                获取文章列表");
      console.log("  node api.js article-detail <id> [选项]   获取文章详情");
      console.log("");
      console.log("newsflash 选项:");
      console.log("  --type  important|original|first|onchain|financing|prediction");
      console.log("  --page  页码（默认 1）");
      console.log("  --size  每页数量 1-50（默认 10）");
      console.log("  --lang  cn|en|cht|vi|ko|ja|th|tr（默认 cn）");
  }
}

main().catch((err) => {
  console.error("错误:", err.message);
  process.exit(1);
});
