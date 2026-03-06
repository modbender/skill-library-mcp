const fs = require("fs");
const path = require("path");
const http = require("http");
const { spawn } = require("child_process");

// ---------------------------------------------------------------------------
// Logging (stderr only — stdout is reserved for JSON)
// ---------------------------------------------------------------------------
function log(msg) {
  process.stderr.write(msg + "\n");
}

// ---------------------------------------------------------------------------
// Args parsing
// ---------------------------------------------------------------------------
function parseArgs() {
  const args = process.argv.slice(2);
  const named = {};
  const positional = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--") && i + 1 < args.length) {
      named[args[i].slice(2)] = args[i + 1];
      i++;
    } else {
      positional.push(args[i]);
    }
  }
  return { named, positional };
}

// ---------------------------------------------------------------------------
// Env loading
// ---------------------------------------------------------------------------
let envPath = null;

function loadEnv(customPath) {
  envPath = customPath
    ? path.resolve(customPath)
    : path.join(__dirname, "..", ".env");

  require("dotenv").config({ path: envPath, override: true });
}

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
function getConfig() {
  return {
    ig: {
      accessToken: process.env.INSTAGRAM_ACCESS_TOKEN,
      baseUrl: "https://graph.instagram.com/v24.0",
    },
    fb: {
      appId: process.env.FACEBOOK_APP_ID,
      appSecret: process.env.FACEBOOK_APP_SECRET,
      accessToken: process.env.FACEBOOK_USER_ACCESS_TOKEN,
      baseUrl: "https://graph.facebook.com/v24.0",
    },
  };
}

// ---------------------------------------------------------------------------
// API
// ---------------------------------------------------------------------------
async function apiGet(endpoint, params = {}) {
  const { ig } = getConfig();
  params.access_token = ig.accessToken;
  const query = new URLSearchParams(params).toString();
  const url = `${ig.baseUrl}${endpoint}?${query}`;

  const res = await fetch(url);
  const data = await res.json();

  if (data.error) {
    throw new Error(`API error: ${data.error.message}`);
  }
  return data;
}

async function apiPost(endpoint, body = {}) {
  const { ig } = getConfig();
  body.access_token = ig.accessToken;

  const res = await fetch(`${ig.baseUrl}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();

  if (data.error) {
    throw new Error(`API error: ${data.error.message}`);
  }
  return data;
}

async function fbApiGet(endpoint, params = {}) {
  const { fb } = getConfig();
  if (!fb.accessToken) {
    throw new Error("FACEBOOK_USER_ACCESS_TOKEN is required for comment operations");
  }
  params.access_token = fb.accessToken;
  const query = new URLSearchParams(params).toString();
  const url = `${fb.baseUrl}${endpoint}?${query}`;

  const res = await fetch(url);
  const data = await res.json();

  if (data.error) {
    throw new Error(`Facebook API error: ${data.error.message}`);
  }
  return data;
}

async function fbApiPost(endpoint, body = {}) {
  const { fb } = getConfig();
  if (!fb.accessToken) {
    throw new Error("FACEBOOK_USER_ACCESS_TOKEN is required for comment operations");
  }
  body.access_token = fb.accessToken;

  const res = await fetch(`${fb.baseUrl}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();

  if (data.error) {
    throw new Error(`Facebook API error: ${data.error.message}`);
  }
  return data;
}

// ---------------------------------------------------------------------------
// Token
// ---------------------------------------------------------------------------
async function refreshIgToken() {
  const { ig } = getConfig();

  // Instagram long-lived refresh endpoint only works for IG user tokens (typically IGA...)
  if (!ig.accessToken || !ig.accessToken.startsWith("IG")) {
    log("Skipping IG token refresh (non-IG token detected)");
    return { access_token: ig.accessToken, skipped: true };
  }

  const url = `https://graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=${ig.accessToken}`;

  const res = await fetch(url);
  const data = await res.json();

  if (data.error) {
    throw new Error(`Token refresh failed: ${data.error.message}`);
  }

  const newToken = data.access_token;
  const expiresInDays = Math.floor(data.expires_in / 86400);

  // Update runtime
  process.env.INSTAGRAM_ACCESS_TOKEN = newToken;

  // Persist to .env file
  let envContent = fs.readFileSync(envPath, "utf-8");
  envContent = envContent.replace(
    /INSTAGRAM_ACCESS_TOKEN=.*/,
    `INSTAGRAM_ACCESS_TOKEN=${newToken}`
  );
  fs.writeFileSync(envPath, envContent);

  log(`IG token refreshed (expires in ${expiresInDays} days)`);
  return { access_token: newToken, expires_in: data.expires_in, expires_in_days: expiresInDays };
}

async function refreshFbToken() {
  const { fb } = getConfig();

  if (!fb.accessToken) {
    throw new Error("FACEBOOK_USER_ACCESS_TOKEN is missing");
  }
  if (!fb.appId || !fb.appSecret) {
    throw new Error("FACEBOOK_APP_ID / FACEBOOK_APP_SECRET are required for FB token refresh");
  }

  const url = `${fb.baseUrl}/oauth/access_token?grant_type=fb_exchange_token&client_id=${encodeURIComponent(fb.appId)}&client_secret=${encodeURIComponent(fb.appSecret)}&fb_exchange_token=${encodeURIComponent(fb.accessToken)}`;

  const res = await fetch(url);
  const data = await res.json();

  if (data.error) {
    throw new Error(`FB token refresh failed: ${data.error.message}`);
  }

  const newToken = data.access_token;
  const expiresInDays = data.expires_in
    ? Math.floor(Number(data.expires_in) / 86400)
    : null;

  process.env.FACEBOOK_USER_ACCESS_TOKEN = newToken;

  let envContent = fs.readFileSync(envPath, "utf-8");
  if (/^FACEBOOK_USER_ACCESS_TOKEN=.*/m.test(envContent)) {
    envContent = envContent.replace(
      /^FACEBOOK_USER_ACCESS_TOKEN=.*/m,
      `FACEBOOK_USER_ACCESS_TOKEN=${newToken}`
    );
  } else {
    envContent = envContent.trimEnd() + `\nFACEBOOK_USER_ACCESS_TOKEN=${newToken}\n`;
  }
  fs.writeFileSync(envPath, envContent);

  if (expiresInDays != null) {
    log(`FB token refreshed (expires in ${expiresInDays} days)`);
  } else {
    log("FB token refreshed");
  }

  return {
    access_token: newToken,
    expires_in: data.expires_in,
    expires_in_days: expiresInDays,
  };
}

// ---------------------------------------------------------------------------
// Profile
// ---------------------------------------------------------------------------
async function getProfile() {
  return apiGet("/me", {
    fields: "id,username,name,account_type,media_count,profile_picture_url",
  });
}

async function getMyPosts(limit = 10) {
  return apiGet("/me/media", {
    fields:
      "id,caption,media_type,media_url,thumbnail_url,timestamp,permalink",
    limit: String(limit),
  });
}

async function getPost(mediaId) {
  return apiGet(`/${mediaId}`, {
    fields:
      "id,caption,media_type,media_url,thumbnail_url,timestamp,permalink,like_count,comments_count",
  });
}

// ---------------------------------------------------------------------------
// Comments
// ---------------------------------------------------------------------------
async function getComments(mediaId) {
  const commentFields = "id,text,username,timestamp,replies{id,text,username,timestamp}";

  // 1) Primary comments on the target media
  const primary = await fbApiGet(`/${mediaId}/comments`, {
    fields: commentFields,
  });

  // 2) For carousel posts, comments can live on child media items.
  //    If primary is empty, collect child comments as a fallback.
  if (Array.isArray(primary?.data) && primary.data.length > 0) {
    return primary;
  }

  let mediaInfo;
  try {
    mediaInfo = await apiGet(`/${mediaId}`, {
      fields: "id,media_type,children{id}",
    });
  } catch {
    return primary;
  }

  if (mediaInfo?.media_type !== "CAROUSEL_ALBUM" || !Array.isArray(mediaInfo?.children?.data)) {
    return primary;
  }

  const childResults = [];

  for (const child of mediaInfo.children.data) {
    if (!child?.id) continue;
    try {
      const childComments = await fbApiGet(`/${child.id}/comments`, {
        fields: commentFields,
      });
      if (Array.isArray(childComments?.data) && childComments.data.length > 0) {
        childResults.push({
          media_id: child.id,
          comments: childComments.data,
        });
      }
    } catch {
      // Ignore child-level fetch failures and continue
    }
  }

  if (childResults.length === 0) return primary;

  return {
    data: childResults.flatMap((entry) =>
      entry.comments.map((comment) => ({ ...comment, media_id: entry.media_id }))
    ),
    meta: {
      source: "carousel-children",
      children_with_comments: childResults.map((c) => c.media_id),
    },
  };
}

async function postComment(mediaId, text) {
  return fbApiPost(`/${mediaId}/comments`, { message: text });
}

async function replyToComment(commentId, text) {
  return fbApiPost(`/${commentId}/replies`, { message: text });
}

// ---------------------------------------------------------------------------
// Tunnel
// ---------------------------------------------------------------------------
let tunnelProcess = null;

function startTunnel(port) {
  return new Promise((resolve, reject) => {
    tunnelProcess = spawn("cloudflared", [
      "tunnel",
      "--url",
      `http://localhost:${port}`,
    ]);

    let resolved = false;
    let tunnelUrl = null;
    let registered = false;

    const timeout = setTimeout(() => {
      if (!resolved) {
        resolved = true;
        reject(new Error("cloudflared tunnel start timeout (30s)"));
      }
    }, 30000);

    function tryResolve() {
      if (tunnelUrl && registered && !resolved) {
        resolved = true;
        clearTimeout(timeout);
        setTimeout(() => resolve(tunnelUrl), 3000);
      }
    }

    function handleData(data) {
      const output = data.toString();
      if (!tunnelUrl) {
        const match = output.match(
          /https:\/\/[a-zA-Z0-9-]+\.trycloudflare\.com/
        );
        if (match) tunnelUrl = match[0];
      }
      if (output.includes("Registered tunnel connection")) {
        registered = true;
      }
      tryResolve();
    }

    tunnelProcess.stdout.on("data", handleData);
    tunnelProcess.stderr.on("data", handleData);

    tunnelProcess.on("error", (err) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        if (err.code === "ENOENT") {
          reject(
            new Error(
              "cloudflared is not installed. Install with: brew install cloudflared"
            )
          );
        } else {
          reject(new Error(`cloudflared failed: ${err.message}`));
        }
      }
    });

    tunnelProcess.on("close", (code) => {
      if (!resolved) {
        resolved = true;
        clearTimeout(timeout);
        reject(new Error(`cloudflared exited with code ${code}`));
      }
    });
  });
}

function stopTunnel() {
  if (tunnelProcess) {
    tunnelProcess.kill();
    tunnelProcess = null;
  }
}

// ---------------------------------------------------------------------------
// Media helpers
// ---------------------------------------------------------------------------
const sharp = require("sharp");

const MIME_TYPES = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".gif": "image/gif",
  ".webp": "image/webp",
};

const HEIC_EXTENSIONS = new Set([".heic", ".heif"]);

const VIDEO_MIME_TYPES = {
  ".mp4": "video/mp4",
  ".mov": "video/quicktime",
};

const VIDEO_MAX_SIZE = 100 * 1024 * 1024; // 100MB

const VIDEO_CONTAINER_TIMEOUT = 10 * 60 * 1000; // 10 minutes

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function getMyUserId() {
  const data = await apiGet("/me", { fields: "id" });
  return data.id;
}

async function convertHeicToJpeg(inputPath) {
  const outputPath = inputPath.replace(/\.heic$/i, ".jpg").replace(/\.heif$/i, ".jpg");
  await sharp(inputPath).jpeg({ quality: 90 }).toFile(outputPath);
  log(`Converted HEIC → JPEG: ${path.basename(outputPath)}`);
  return outputPath;
}

async function validateImageFile(filePath) {
  let absolutePath = path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`File not found: ${absolutePath}`);
  }

  const ext = path.extname(absolutePath).toLowerCase();

  if (HEIC_EXTENSIONS.has(ext)) {
    absolutePath = await convertHeicToJpeg(absolutePath);
    return { absolutePath, mimeType: "image/jpeg", converted: true };
  }

  const mimeType = MIME_TYPES[ext];
  if (!mimeType) {
    throw new Error(
      `Unsupported image format: ${ext} (supported: jpg, png, gif, webp, heic)`
    );
  }
  return { absolutePath, mimeType, converted: false };
}

function validateVideoFile(filePath) {
  const absolutePath = path.resolve(filePath);
  if (!fs.existsSync(absolutePath)) {
    throw new Error(`File not found: ${absolutePath}`);
  }

  const ext = path.extname(absolutePath).toLowerCase();
  const mimeType = VIDEO_MIME_TYPES[ext];
  if (!mimeType) {
    throw new Error(
      `Unsupported video format: ${ext} (supported: mp4, mov)`
    );
  }

  const stat = fs.statSync(absolutePath);
  if (stat.size > VIDEO_MAX_SIZE) {
    throw new Error(
      `Video file too large: ${(stat.size / 1024 / 1024).toFixed(1)}MB (max 100MB)`
    );
  }

  return { absolutePath, mimeType };
}

function createFileServer(fileMap) {
  return http.createServer((req, res) => {
    const fileName = decodeURIComponent(req.url.replace(/^\//, ""));
    const entry = fileMap.get(fileName);
    if (entry) {
      res.writeHead(200, {
        "Content-Type": entry.mimeType,
        "Content-Length": entry.data.length,
      });
      res.end(entry.data);
    } else {
      res.writeHead(404);
      res.end();
    }
  });
}

async function startLocalTunnel(fileMap) {
  const server = createFileServer(fileMap);
  const port = await new Promise((resolve) => {
    server.listen(0, () => resolve(server.address().port));
  });
  log(`Local server started (port: ${port})`);

  log("Starting cloudflared tunnel...");
  const publicUrl = await startTunnel(port);
  log(`Public URL: ${publicUrl}`);

  return { server, publicUrl };
}

async function waitForContainer(containerId, timeoutMs = 5 * 60 * 1000) {
  const deadline = Date.now() + timeoutMs;
  while (true) {
    const status = await apiGet(`/${containerId}`, {
      fields: "status_code",
    });
    if (status.status_code === "FINISHED") return;
    if (status.status_code === "ERROR") {
      throw new Error(`Media container processing failed: ${containerId}`);
    }
    if (Date.now() >= deadline) {
      throw new Error(`Media container processing timed out after ${timeoutMs / 1000}s: ${containerId}`);
    }
    await sleep(3000);
  }
}

// ---------------------------------------------------------------------------
// Media: post
// ---------------------------------------------------------------------------
async function postImage(imageUrl, caption) {
  const userId = await getMyUserId();

  log("Creating container...");
  const container = await apiPost(`/${userId}/media`, {
    image_url: imageUrl,
    caption,
  });
  log(`Container created: ${container.id}`);

  log("Waiting for upload processing...");
  await waitForContainer(container.id);

  log("Publishing...");
  const result = await apiPost(`/${userId}/media_publish`, {
    creation_id: container.id,
  });
  const detail = await apiGet(`/${result.id}`, { fields: "permalink" });
  log(`Published! ID: ${result.id}`);
  return { id: result.id, permalink: detail.permalink };
}

async function postLocalImage(filePath, caption) {
  const { absolutePath, mimeType } = await validateImageFile(filePath);
  const fileName = path.basename(absolutePath);
  const fileMap = new Map([
    [fileName, { data: fs.readFileSync(absolutePath), mimeType }],
  ]);

  let server = null;
  try {
    const tunnel = await startLocalTunnel(fileMap);
    server = tunnel.server;
    return await postImage(`${tunnel.publicUrl}/${encodeURIComponent(fileName)}`, caption);
  } finally {
    stopTunnel();
    if (server) server.close();
    log("Server and tunnel stopped");
  }
}

async function postCarousel(imageUrls, caption) {
  const userId = await getMyUserId();

  const childIds = [];
  for (let i = 0; i < imageUrls.length; i++) {
    log(`Creating container for image ${i + 1}/${imageUrls.length}...`);
    const container = await apiPost(`/${userId}/media`, {
      image_url: imageUrls[i],
      is_carousel_item: true,
    });
    childIds.push(container.id);
    log(`  Container created: ${container.id}`);
  }

  log("Waiting for upload processing...");
  for (const id of childIds) {
    await waitForContainer(id);
  }

  log("Creating carousel container...");
  const carousel = await apiPost(`/${userId}/media`, {
    media_type: "CAROUSEL",
    children: childIds.join(","),
    caption,
  });
  log(`Carousel container: ${carousel.id}`);

  await waitForContainer(carousel.id);

  log("Publishing carousel...");
  const result = await apiPost(`/${userId}/media_publish`, {
    creation_id: carousel.id,
  });
  const detail = await apiGet(`/${result.id}`, { fields: "permalink" });
  log(`Published! ID: ${result.id}`);
  return { id: result.id, permalink: detail.permalink };
}

async function postLocalCarousel(filePaths, caption) {
  const fileMap = new Map();
  const fileNames = [];

  for (const fp of filePaths) {
    const { absolutePath, mimeType } = await validateImageFile(fp);
    const fileName = path.basename(absolutePath);
    fileMap.set(fileName, { data: fs.readFileSync(absolutePath), mimeType });
    fileNames.push(fileName);
  }

  let server = null;
  try {
    const tunnel = await startLocalTunnel(fileMap);
    server = tunnel.server;
    const imageUrls = fileNames.map((f) => `${tunnel.publicUrl}/${encodeURIComponent(f)}`);
    return await postCarousel(imageUrls, caption);
  } finally {
    stopTunnel();
    if (server) server.close();
    log("Server and tunnel stopped");
  }
}

// ---------------------------------------------------------------------------
// Media: post video (Reels)
// ---------------------------------------------------------------------------
async function postVideo(videoUrl, caption, options = {}) {
  const userId = await getMyUserId();

  const body = {
    media_type: "REELS",
    video_url: videoUrl,
    caption,
  };
  if (options.coverUrl) body.cover_url = options.coverUrl;
  if (options.thumbOffset != null) body.thumb_offset = options.thumbOffset;
  if (options.shareToFeed != null) body.share_to_feed = options.shareToFeed;

  log("Creating video container...");
  const container = await apiPost(`/${userId}/media`, body);
  log(`Container created: ${container.id}`);

  log("Waiting for video processing...");
  await waitForContainer(container.id, VIDEO_CONTAINER_TIMEOUT);

  log("Publishing...");
  const result = await apiPost(`/${userId}/media_publish`, {
    creation_id: container.id,
  });
  const detail = await apiGet(`/${result.id}`, { fields: "permalink" });
  log(`Published! ID: ${result.id}`);
  return { id: result.id, permalink: detail.permalink };
}

async function postLocalVideo(filePath, caption, options = {}) {
  const { absolutePath, mimeType } = validateVideoFile(filePath);
  const fileName = path.basename(absolutePath);
  const fileMap = new Map([
    [fileName, { data: fs.readFileSync(absolutePath), mimeType }],
  ]);

  // Serve local cover image if provided
  if (options.coverUrl && !options.coverUrl.startsWith("http")) {
    const cover = await validateImageFile(options.coverUrl);
    const coverName = path.basename(cover.absolutePath);
    fileMap.set(coverName, {
      data: fs.readFileSync(cover.absolutePath),
      mimeType: cover.mimeType,
    });
    options._coverFileName = coverName;
  }

  let server = null;
  try {
    const tunnel = await startLocalTunnel(fileMap);
    server = tunnel.server;
    const tunnelOptions = { ...options };
    if (options._coverFileName) {
      tunnelOptions.coverUrl = `${tunnel.publicUrl}/${encodeURIComponent(options._coverFileName)}`;
      delete tunnelOptions._coverFileName;
    }
    return await postVideo(
      `${tunnel.publicUrl}/${encodeURIComponent(fileName)}`,
      caption,
      tunnelOptions
    );
  } finally {
    stopTunnel();
    if (server) server.close();
    log("Server and tunnel stopped");
  }
}

async function postVideoCarousel(videoUrls, caption) {
  const userId = await getMyUserId();

  const childIds = [];
  for (let i = 0; i < videoUrls.length; i++) {
    log(`Creating container for video ${i + 1}/${videoUrls.length}...`);
    const container = await apiPost(`/${userId}/media`, {
      media_type: "VIDEO",
      video_url: videoUrls[i],
      is_carousel_item: true,
    });
    childIds.push(container.id);
    log(`  Container created: ${container.id}`);
  }

  log("Waiting for video processing...");
  for (const id of childIds) {
    await waitForContainer(id, VIDEO_CONTAINER_TIMEOUT);
  }

  log("Creating carousel container...");
  const carousel = await apiPost(`/${userId}/media`, {
    media_type: "CAROUSEL",
    children: childIds.join(","),
    caption,
  });
  log(`Carousel container: ${carousel.id}`);

  await waitForContainer(carousel.id);

  log("Publishing carousel...");
  const result = await apiPost(`/${userId}/media_publish`, {
    creation_id: carousel.id,
  });
  const detail = await apiGet(`/${result.id}`, { fields: "permalink" });
  log(`Published! ID: ${result.id}`);
  return { id: result.id, permalink: detail.permalink };
}

async function postLocalVideoCarousel(filePaths, caption) {
  const fileMap = new Map();
  const fileNames = [];

  for (const fp of filePaths) {
    const { absolutePath, mimeType } = validateVideoFile(fp);
    const fileName = path.basename(absolutePath);
    fileMap.set(fileName, { data: fs.readFileSync(absolutePath), mimeType });
    fileNames.push(fileName);
  }

  let server = null;
  try {
    const tunnel = await startLocalTunnel(fileMap);
    server = tunnel.server;
    const videoUrls = fileNames.map((f) => `${tunnel.publicUrl}/${encodeURIComponent(f)}`);
    return await postVideoCarousel(videoUrls, caption);
  } finally {
    stopTunnel();
    if (server) server.close();
    log("Server and tunnel stopped");
  }
}

// ---------------------------------------------------------------------------
// run() — script entrypoint wrapper
// ---------------------------------------------------------------------------
async function run(fn, options = {}) {
  try {
    const { named, positional } = parseArgs();
    loadEnv(named.env);

    const refreshIg = options.refreshIg !== false;
    const refreshFb = options.refreshFb === true;

    if (refreshIg) {
      await refreshIgToken();
    }

    if (refreshFb && process.env.FACEBOOK_USER_ACCESS_TOKEN) {
      try {
        await refreshFbToken();
      } catch (err) {
        // Keep running with existing token if refresh endpoint fails temporarily.
        log(`FB token refresh skipped: ${err.message}`);
      }
    }

    const result = await fn({ named, positional });
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
    process.exit(0);
  } catch (err) {
    process.stdout.write(JSON.stringify({ error: err.message }) + "\n");
    process.exit(1);
  }
}

// ---------------------------------------------------------------------------
// Exports
// ---------------------------------------------------------------------------
module.exports = {
  log,
  parseArgs,
  loadEnv,
  getConfig,
  apiGet,
  apiPost,
  refreshIgToken,
  refreshFbToken,
  getProfile,
  getMyPosts,
  getPost,
  getComments,
  postComment,
  replyToComment,
  startTunnel,
  stopTunnel,
  postImage,
  postLocalImage,
  postCarousel,
  postLocalCarousel,
  validateVideoFile,
  postVideo,
  postLocalVideo,
  postVideoCarousel,
  postLocalVideoCarousel,
  VIDEO_CONTAINER_TIMEOUT,
  run,
};
