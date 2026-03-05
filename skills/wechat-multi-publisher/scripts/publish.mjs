/**
 * wechat-mp-publisher — Multi-article WeChat MP draft publisher
 * Supports: 1 main article + up to 7 sub-articles in a single draft push
 * Styling: wenyan-core + custom gold quotes, && section dividers, strong highlights
 *
 * Usage:
 *   node publish.mjs <main.md> [sub1.md] [sub2.md] ... [--dry-run] [--publish] [--media-id=xxx]
 *
 * Credentials (priority order):
 *   1. Env vars: WECHAT_APP_ID, WECHAT_APP_SECRET
 *   2. ~/.config/wechat-mp/credentials.json  { "appId": "...", "appSecret": "..." }
 */

import { renderStyledContent } from "@wenyan-md/core/wrapper";
import fs from "fs";
import path from "path";

const WECHAT_API = "https://api.weixin.qq.com/cgi-bin";
const CREDENTIALS_PATH = path.resolve(process.env.HOME, ".config/wechat-mp/credentials.json");

// === Cover image: keyword → Unsplash search ===
const ZH_TO_EN_KEYWORDS = [
  ["anthropic",  "anthropic AI neural network"],
  ["claude",     "claude AI assistant"],
  ["openai",     "openai artificial intelligence"],
  ["chatgpt",    "chatgpt AI conversation"],
  ["gemini",     "google AI technology"],
  ["deepseek",   "AI technology neural network"],
  ["数字员工",    "digital worker automation office"],
  ["机器人",      "robot automation technology"],
  ["自动化",      "automation workflow technology"],
  ["芯片",        "semiconductor chip technology"],
  ["算力",        "data center server computing"],
  ["安全",        "cybersecurity digital protection"],
  ["赚钱",        "business profit growth revenue"],
  ["创业",        "startup entrepreneurship team"],
  ["投资",        "investment finance growth chart"],
  ["融资",        "venture capital startup funding"],
  ["医疗",        "healthcare medical technology"],
  ["教育",        "education learning technology"],
  ["金融",        "finance banking technology"],
  ["agent",       "AI agent robot automation"],
  ["llm",         "large language model AI neural"],
  ["gpt",         "AI language model neural network"],
  ["企业",        "enterprise business office technology"],
  ["数据",        "data visualization analytics technology"],
  ["ai",          "artificial intelligence technology futuristic"],
];

// Reliable fallback covers — hashed by title so each article gets a different one
const FALLBACK_COVERS = [
  "photo-1677442136019-21780ecad995",
  "photo-1620712943543-bcc4688e7485",
  "photo-1551288049-bebda4e38f71",
  "photo-1485827404703-89b55fcc595e",
  "photo-1518770660439-4636190af475",
  "photo-1526374965328-7f61d4dc18c5",
  "photo-1558494949-ef010cbdcc31",
  "photo-1504711434969-e33886168f5c",
  "photo-1507003211169-0a1dd7228f2d",
  "photo-1460925895917-afdab827c52f",
  "photo-1611974789855-9c2a0a7236a3",
  "photo-1639762681485-074b7f938ba0",
];

function selectCoverUrl(title, content) {
  const text = (title + " " + (content || "").substring(0, 300)).toLowerCase();
  const terms = [];
  for (const [zh, en] of ZH_TO_EN_KEYWORDS) {
    if (text.includes(zh.toLowerCase())) {
      terms.push(...en.split(" ").slice(0, 2));
      if (terms.length >= 4) break;
    }
  }
  if (terms.length === 0) terms.push("artificial", "intelligence", "technology");
  const query = encodeURIComponent([...new Set(terms)].slice(0, 4).join(","));
  return `https://source.unsplash.com/900x383/?${query}`;
}

function pickFallbackIndex(title) {
  let hash = 0;
  for (const ch of title) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return hash % FALLBACK_COVERS.length;
}

// === Credentials ===
function getCredentials() {
  const appId = process.env.WECHAT_APP_ID;
  const appSecret = process.env.WECHAT_APP_SECRET;
  if (appId && appSecret) return { appId, appSecret };
  if (fs.existsSync(CREDENTIALS_PATH)) {
    const creds = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, "utf-8"));
    return { appId: creds.appId, appSecret: creds.appSecret };
  }
  throw new Error("No credentials found. Set WECHAT_APP_ID + WECHAT_APP_SECRET env vars, or create ~/.config/wechat-mp/credentials.json");
}

async function getAccessToken(appId, appSecret) {
  const res = await fetch(`${WECHAT_API}/token?grant_type=client_credential&appid=${appId}&secret=${appSecret}`);
  const data = await res.json();
  if (data.errcode) throw new Error(`Token error ${data.errcode}: ${data.errmsg}`);
  return data.access_token;
}

// === Image upload ===
async function uploadImage(url, accessToken, articleTitle = "") {
  let imgRes = await fetch(url);
  if (!imgRes.ok) {
    console.log(`  ⚠️ Cover fetch failed (${imgRes.status}), trying fallback...`);
    const startIdx = pickFallbackIndex(articleTitle);
    for (let i = 0; i < FALLBACK_COVERS.length; i++) {
      const id = FALLBACK_COVERS[(startIdx + i) % FALLBACK_COVERS.length];
      imgRes = await fetch(`https://images.unsplash.com/${id}?w=900&h=383&fit=crop&q=80`);
      if (imgRes.ok) { console.log(`  ✅ Using fallback [${id.slice(0, 20)}...]`); break; }
    }
    if (!imgRes.ok) throw new Error("All cover image sources failed");
  }
  const buffer = await imgRes.arrayBuffer();
  const form = new FormData();
  form.append("media", new Blob([buffer], { type: "image/jpeg" }), "cover.jpg");
  const res = await fetch(`${WECHAT_API}/material/add_material?access_token=${accessToken}&type=image`, { method: "POST", body: form });
  const data = await res.json();
  if (data.errcode) throw new Error(`Upload failed ${data.errcode}: ${data.errmsg}`);
  return data.media_id;
}

async function uploadInlineImage(localPath, accessToken) {
  if (!fs.existsSync(localPath)) return null;
  const buffer = fs.readFileSync(localPath);
  const mimeType = localPath.endsWith(".png") ? "image/png" : "image/jpeg";
  const form = new FormData();
  form.append("media", new Blob([buffer], { type: mimeType }), path.basename(localPath));
  const res = await fetch(`${WECHAT_API}/media/uploadimg?access_token=${accessToken}`, { method: "POST", body: form });
  const data = await res.json();
  return data.errcode ? null : data.url;
}

async function processInlineImages(html, mdDir, accessToken) {
  const imgRegex = /<img\s+[^>]*src="([^"]+\.(png|jpg|jpeg|gif|webp))"[^>]*>/gi;
  let result = html;
  for (const match of [...html.matchAll(imgRegex)]) {
    const src = match[1];
    if (src.startsWith("http")) continue;
    const wxUrl = await uploadInlineImage(path.resolve(mdDir, src), accessToken);
    result = wxUrl
      ? result.replace(src, wxUrl)
      : result.replace(match[0], `<p style="color:#999;text-align:center;">[Image load failed]</p>`);
  }
  return result;
}

// === Styling theme ===
const T = {
  primary:    "#FF6B35",
  primaryDark:"#C84B00",
  primaryMid: "#FF8C5A",
  primaryBg:  "#FFF4EE",
  text:       "#1A1A1A",
  textLight:  "#666666",
  border:     "#F0E6DE",
  codeBg:     "#F7F3F0",
};

function enhanceFormatting(html) {
  let e = html;

  // H1: centered
  e = e.replace(/<h1[^>]*>(.*?)<\/h1>/gs,
    `<section style="text-align:center;margin:2em 0 1.5em;"><span style="font-size:1.6em;font-weight:700;color:${T.text};">$1</span><section style="width:40px;height:3px;background:${T.primary};margin:10px auto 0;border-radius:2px;"></section></section>`);

  // H2: left accent
  e = e.replace(/<h2[^>]*>(.*?)<\/h2>/gs,
    `<section style="display:flex;align-items:center;margin:2em 0 1em;padding:12px 16px;background:#F8F8F8;border-radius:4px;border-left:4px solid ${T.primary};"><span style="font-size:1.05em;font-weight:700;color:${T.text};">$1</span></section>`);

  // && alone → divider
  e = e.replace(/<p[^>]*>\s*&amp;&amp;\s*<\/p>/g,
    `<section style="text-align:center;margin:2em 0 1.5em;"><section style="display:inline-block;width:60%;height:1px;background:linear-gradient(to right,transparent,${T.primary}80,transparent);"></section></section>`);

  // && text → section header
  e = e.replace(/<p[^>]*>\s*&amp;&amp;\s*([^<]+)<\/p>/g,
    `<section style="display:flex;align-items:center;margin:2em 0 1em;padding:12px 16px;background:#F8F8F8;border-radius:4px;border-left:4px solid ${T.primary};"><span style="font-size:1.05em;font-weight:700;color:${T.text};">$1</span></section>`);

  // Gold quotes
  for (const pat of [
    /(<p[^>]*>)(真正的[^<]{5,})<\/p>/g,
    /(<p[^>]*>)(不是[^<]*?而是[^<]{5,})<\/p>/g,
    /(<p[^>]*>)(底层逻辑是[^<]{5,})<\/p>/g,
    /(<p[^>]*>)(关键不是[^<]{5,})<\/p>/g,
  ]) {
    e = e.replace(pat, (_, p, content) =>
      `<section style="border-left:4px solid ${T.primary};background:${T.primaryBg};padding:14px 18px;margin:1.5em 0;border-radius:0 6px 6px 0;font-size:16px;font-weight:600;color:${T.text};line-height:1.8;"><span style="color:${T.primary};margin-right:6px;">▎</span>${content}</section>`);
  }

  // Strong → accent color
  e = e.replace(/<strong>([^<]{2,})<\/strong>/g,
    `<strong style="color:${T.primaryDark};font-weight:700;">$1</strong>`);

  // Blockquote
  e = e.replace(/<blockquote[^>]*>/g,
    `<blockquote style="background:${T.primaryBg};border-left:4px solid ${T.primaryMid};margin:1.5em 0;padding:14px 18px;border-radius:0 6px 6px 0;font-style:normal;color:${T.textLight};font-size:15px;line-height:1.75;">`);

  // Inline code
  e = e.replace(/<code[^>]*>/g,
    `<code style="background:${T.codeBg};color:${T.primaryDark};padding:2px 6px;border-radius:3px;font-size:14px;font-family:monospace;">`);

  // Body paragraphs
  e = e.replace(/<p style="margin: 1em 0px;">/g,
    `<p style="margin:0.9em 0;line-height:1.85;font-size:16px;color:${T.text};">`);

  return e;
}

function extractDigest(markdown) {
  const bodyLines = markdown.split("\n").filter(l =>
    l.trim() && !l.startsWith("#") && !l.startsWith(">") && !l.startsWith("---") && !l.startsWith("```") && !l.startsWith("!")
  );
  const text = bodyLines.slice(0, 3).join("").replace(/\*\*/g, "").replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").trim();
  return text.length > 120 ? text.substring(0, 117) + "..." : text;
}

async function renderArticle(mdPath) {
  const markdown = fs.readFileSync(mdPath, "utf-8");
  const { content } = await renderStyledContent(markdown, {
    themeId: "default",
    hlThemeId: "solarized-light",
    isMacStyle: true,
  });
  const titleMatch = markdown.match(/^#\s+(.+)/m);
  const title = titleMatch ? titleMatch[1].trim() : path.basename(mdPath, ".md");
  const noH1 = content.replace(/<h1[^>]*>.*?<\/h1>/gi, "");
  const enhanced = enhanceFormatting(noH1);
  return { title, content: enhanced, markdown, digest: extractDigest(markdown), mdDir: path.dirname(mdPath) };
}

// === Main ===
async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.log("Usage: node publish.mjs <main.md> [sub1.md] ... [--dry-run] [--publish] [--media-id=xxx]");
    process.exit(1);
  }

  const dryRun = args.includes("--dry-run");
  const shouldPublish = args.includes("--publish");
  const mediaIdArg = args.find(a => a.startsWith("--media-id="));
  const mdFiles = args.filter(a => !a.startsWith("--") && a.endsWith(".md"));

  // Publish existing draft by media_id
  if (mediaIdArg) {
    const { appId, appSecret } = getCredentials();
    const token = await getAccessToken(appId, appSecret);
    const mediaId = mediaIdArg.split("=")[1];
    const res = await fetch(`${WECHAT_API}/freepublish/submit?access_token=${token}`, {
      method: "POST", body: JSON.stringify({ media_id: mediaId })
    });
    const data = await res.json();
    if (data.errcode) throw new Error(`Publish failed ${data.errcode}: ${data.errmsg}`);
    console.log(`✅ Published! publish_id: ${data.publish_id}`);
    return;
  }

  // Render articles
  console.log(`📝 Rendering ${mdFiles.length} article(s)...`);
  const rendered = [];
  for (let i = 0; i < mdFiles.length; i++) {
    const art = await renderArticle(mdFiles[i]);
    console.log(`  ✅ [${i === 0 ? "main" : "sub"}] ${art.title}`);
    rendered.push(art);
  }

  if (dryRun) {
    fs.mkdirSync("/tmp/wechat-preview", { recursive: true });
    rendered.forEach((art, i) => {
      const f = `/tmp/wechat-preview/article-${i + 1}.html`;
      fs.writeFileSync(f, `<!DOCTYPE html><html><head><meta charset="utf-8"></head><body style="max-width:600px;margin:0 auto;padding:20px;">${art.content}</body></html>`);
      console.log(`📄 Preview: ${f}`);
    });
    return;
  }

  const { appId, appSecret } = getCredentials();
  console.log("🔑 Getting access token...");
  const token = await getAccessToken(appId, appSecret);

  console.log("🖼️  Processing inline images...");
  for (const art of rendered) {
    art.content = await processInlineImages(art.content, art.mdDir, token);
  }

  console.log("🖼️  Uploading cover images...");
  const coverIds = [];
  for (const art of rendered) {
    const coverUrl = selectCoverUrl(art.title, art.markdown);
    coverIds.push(await uploadImage(coverUrl, token, art.title));
  }

  const articles = rendered.map((art, idx) => ({
    title: art.title,
    author: process.env.WECHAT_AUTHOR || "",
    content: art.content,
    thumb_media_id: coverIds[idx],
    digest: art.digest,
  }));

  console.log(`\n📤 Pushing ${articles.length} article(s) to draft box...`);
  const draftRes = await fetch(`${WECHAT_API}/draft/add?access_token=${token}`, {
    method: "POST", body: JSON.stringify({ articles })
  });
  const draftData = await draftRes.json();
  if (draftData.errcode) throw new Error(`Draft failed ${draftData.errcode}: ${draftData.errmsg}`);
  console.log(`✅ Draft created! media_id: ${draftData.media_id}`);

  if (shouldPublish) {
    const pubRes = await fetch(`${WECHAT_API}/freepublish/submit?access_token=${token}`, {
      method: "POST", body: JSON.stringify({ media_id: draftData.media_id })
    });
    const pubData = await pubRes.json();
    if (pubData.errcode) throw new Error(`Publish failed ${pubData.errcode}: ${pubData.errmsg}`);
    console.log(`✅ Published! publish_id: ${pubData.publish_id}`);
  }
}

main().catch(e => { console.error("❌ Error:", e.message); process.exit(1); });
