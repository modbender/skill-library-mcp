import fs from "node:fs";
import path from "node:path";

/**
 * miro-push.mjs (vNext)
 * - apply <miro-ready.json> : idempotent push with REAL containers (frames)
 * - undo <sessionKey>       : removes last run items
 *
 * Key behavior:
 * - Frames are ALWAYS created when there are >=2 meaningful items.
 * - Arrow-only stickies (→, ->, etc.) are NEVER created.
 * - Connectors:
 *    - If exactly 2 frames => create ONE clean container->container connector.
 *      - Try native frame->frame connector first (no extra items).
 *      - If not supported, fallback to 2 edge-anchors (kept out of the way).
 *    - Sticky->sticky connectors from JSON are created ONLY if:
 *      - they are within the SAME frame, OR
 *      - there are not exactly 2 frames (i.e., no container-flow mode)
 */

const token = process.env.MIRO_ACCESS_TOKEN;
const boardId = process.env.MIRO_BOARD_ID;

if (!token) throw new Error("Missing MIRO_ACCESS_TOKEN");
if (!boardId) throw new Error("Missing MIRO_BOARD_ID");

const ROOT = process.cwd();
const OUT_DIR = path.join(ROOT, "_out");
const STATE_PATH = path.join(OUT_DIR, ".state.json");
if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

function loadState() {
  if (!fs.existsSync(STATE_PATH)) return { sessions: {} };
  try { return JSON.parse(fs.readFileSync(STATE_PATH, "utf-8")); }
  catch { return { sessions: {} }; }
}
function saveState(s) { fs.writeFileSync(STATE_PATH, JSON.stringify(s, null, 2), "utf-8"); }

async function api(method, url, body) {
  const res = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error(`Miro API error ${res.status}: ${t}`);
  }
  return res.status === 204 ? null : res.json();
}

// --- delete helpers ---
const deleteFrame = (id) => api("DELETE", `https://api.miro.com/v2/boards/${boardId}/frames/${id}`);
const deleteSticky = (id) => api("DELETE", `https://api.miro.com/v2/boards/${boardId}/sticky_notes/${id}`);
const deleteConnector = (id) => api("DELETE", `https://api.miro.com/v2/boards/${boardId}/connectors/${id}`);

// --- create helpers ---
async function createFrame(f) {
  return api("POST", `https://api.miro.com/v2/boards/${boardId}/frames`, {
    data: { title: f.title ?? "Frame" },
    position: { x: Number(f.x ?? 0), y: Number(f.y ?? 0), origin: "center" },
    geometry: { width: Number(f.w ?? 1600), height: Number(f.h ?? 1000) },
  });
}

function mapStickyColor(color) {
  const allowed = new Set(["light_yellow", "light_blue", "light_green", "light_pink", "gray"]);
  return allowed.has(color) ? color : "light_yellow";
}
function mapConnectorShape(shape) {
  const allowed = new Set(["straight", "elbowed", "curved"]);
  return allowed.has(shape) ? shape : "elbowed";
}
function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

// --- Arrow-only stickies filter (CRITICAL) ---
function isArrowOnlyText(text) {
  const t = String(text ?? "").trim();
  return t === "→" || t === "->" || t === "-->" || t === "=>" || t === "➡" || t === "⟶";
}
function isMeaningfulStickyText(text) {
  const t = String(text ?? "").trim();
  if (!t) return false;
  if (isArrowOnlyText(t)) return false;
  return true;
}

async function createStickyOnBoard(s) {
  return api("POST", `https://api.miro.com/v2/boards/${boardId}/sticky_notes`, {
    data: { content: String(s.text ?? "").trim(), shape: "square" },
    style: { fillColor: mapStickyColor(s.color) },
    position: { x: Number(s.x ?? 0), y: Number(s.y ?? 0), origin: "center" },
  });
}

// Parenting uses TOP-LEFT frame coords (fixes 400 boundary)
function toFrameRelativeTopLeft(boardX, boardY, frameLocal) {
  const fx = Number(frameLocal.x ?? 0);
  const fy = Number(frameLocal.y ?? 0);
  const fw = Number(frameLocal.w ?? 1600);
  const fh = Number(frameLocal.h ?? 1000);

  const left = fx - fw / 2;
  const top = fy - fh / 2;

  let rx = Number(boardX ?? 0) - left;
  let ry = Number(boardY ?? 0) - top;

  const MARGIN = 180;
  rx = clamp(rx, MARGIN, fw - MARGIN);
  ry = clamp(ry, MARGIN, fh - MARGIN);

  return { x: rx, y: ry };
}

async function moveStickyIntoFrame(stickyId, boardX, boardY, frameMiroId, frameLocal) {
  const rel = toFrameRelativeTopLeft(boardX, boardY, frameLocal);
  return api("PATCH", `https://api.miro.com/v2/boards/${boardId}/sticky_notes/${stickyId}`, {
    parent: { id: frameMiroId },
    position: { x: rel.x, y: rel.y, origin: "center" },
  });
}

async function createConnectorBetweenItems({ shape, label }, startItemId, endItemId) {
  const body = {
    startItem: { id: startItemId, snapTo: "auto" },
    endItem: { id: endItemId, snapTo: "auto" },
    shape: mapConnectorShape(shape),
  };
  if (label) body.data = { content: String(label) };
  return api("POST", `https://api.miro.com/v2/boards/${boardId}/connectors`, body);
}

// --- Frame-to-frame connector (native attempt first) ---
async function tryCreateFrameToFrameConnector(frameLeftMiroId, frameRightMiroId) {
  // Some Miro tenants accept frame IDs as startItem/endItem
  // If it fails, caller will fallback to anchors.
  return createConnectorBetweenItems({ shape: "straight", label: null }, frameLeftMiroId, frameRightMiroId);
}

// --- Anchor fallback (kept OUT of workspace area) ---
async function createHiddenAnchorOnBoard(x, y) {
  return api("POST", `https://api.miro.com/v2/boards/${boardId}/sticky_notes`, {
    data: { content: "", shape: "square" },
    style: { fillColor: "gray" },
    position: { x: Number(x), y: Number(y), origin: "center" },
  });
}

function frameAnchorPoint(frameLocal, side) {
  const fx = Number(frameLocal.x ?? 0);
  const fy = Number(frameLocal.y ?? 0);
  const fw = Number(frameLocal.w ?? 1600);
  const fh = Number(frameLocal.h ?? 1000);

  // Put anchors near the TOP border so they don't clutter the middle
  const INSET_X = 220;
  const INSET_Y = 170;

  if (side === "right") return { x: fx + fw / 2 - INSET_X, y: fy - fh / 2 + INSET_Y };
  if (side === "left") return { x: fx - fw / 2 + INSET_X, y: fy - fh / 2 + INSET_Y };
  return { x: fx, y: fy };
}

// --- utils ---
function usage() {
  console.log(`
Usage:
  node miro-push.mjs apply <miro-ready.json>
  node miro-push.mjs undo <sessionKey>
`);
}

function normalizeTitle(text) {
  return String(text ?? "").trim().replace(/[:;,.]+$/g, "").trim();
}
function looksLikeContainerTitle(text) {
  const t = normalizeTitle(text);
  if (!t) return false;
  if (t.length < 2 || t.length > 40) return false;
  const lower = t.toLowerCase();
  if (lower.startsWith("feature")) return false;
  if (lower === "api") return false;
  if (isArrowOnlyText(t)) return false;
  return /^[A-Za-z0-9 _-]{2,40}$/.test(t);
}

function bboxOf(points) {
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const p of points) {
    const x = Number(p.x ?? 0);
    const y = Number(p.y ?? 0);
    if (x < minX) minX = x;
    if (x > maxX) maxX = x;
    if (y < minY) minY = y;
    if (y > maxY) maxY = y;
  }
  if (!isFinite(minX)) return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
  return { minX, maxX, minY, maxY };
}

function dist(a, b) {
  const dx = (Number(a.x ?? 0) - Number(b.x ?? 0));
  const dy = (Number(a.y ?? 0) - Number(b.y ?? 0));
  return Math.sqrt(dx * dx + dy * dy);
}

function layoutFramesNoOverlap(frames) {
  if (frames.length !== 2) return;

  const GAP = 600;
  const f1 = frames[0];
  const f2 = frames[1];

  const W = Math.max(Number(f1.w ?? 1800), Number(f2.w ?? 1800));
  const H = Math.max(Number(f1.h ?? 1100), Number(f2.h ?? 1100));
  f1.w = f2.w = W;
  f1.h = f2.h = H;

  const y = (Number(f1.y ?? 0) + Number(f2.y ?? 0)) / 2;
  f1.y = y;
  f2.y = y;

  const left = Number(f1.x ?? 0) <= Number(f2.x ?? 0) ? f1 : f2;
  const right = left === f1 ? f2 : f1;

  left.x = -(W / 2 + GAP / 2);
  right.x = +(W / 2 + GAP / 2);
}

// --- AUTO-FRAME STRATEGIES (hard requirement) ---
function autoFramesFromTitleStickies(frames, stickies) {
  const titles = stickies.filter((s) => looksLikeContainerTitle(s.text));
  if (titles.length < 2) return false;

  const titleIdToFrameId = new Map();
  let idx = 1;
  for (const t of titles) titleIdToFrameId.set(t.id, `F_AUTO_${idx++}`);

  for (const t of titles) t.frameId = titleIdToFrameId.get(t.id);

  for (const s of stickies) {
    if (titleIdToFrameId.has(s.id)) continue;
    let best = titles[0];
    let bestD = dist(s, best);
    for (const t of titles.slice(1)) {
      const d = dist(s, t);
      if (d < bestD) { best = t; bestD = d; }
    }
    s.frameId = titleIdToFrameId.get(best.id);
  }

  const PADDING = 520;
  const MIN_W = 1800, MIN_H = 1100;

  const newFrames = [];
  for (const t of titles) {
    const fid = titleIdToFrameId.get(t.id);
    const assigned = stickies.filter((s) => s.frameId === fid && isMeaningfulStickyText(s.text));
    const bb = bboxOf(assigned.length ? assigned : [t]);
    const w = Math.max(MIN_W, bb.maxX - bb.minX + PADDING * 2);
    const h = Math.max(MIN_H, bb.maxY - bb.minY + PADDING * 2);
    const cx = (bb.minX + bb.maxX) / 2;
    const cy = (bb.minY + bb.maxY) / 2;
    newFrames.push({ id: fid, title: normalizeTitle(t.text), x: cx, y: cy, w, h });
  }

  frames.splice(0, frames.length, ...newFrames);
  layoutFramesNoOverlap(frames);
  return true;
}

function autoFramesByXClusters(frames, stickies) {
  const usable = stickies.filter((s) => isMeaningfulStickyText(s.text));
  if (usable.length < 2) return false;

  const xs = usable.map((s) => Number(s.x ?? 0));
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const span = maxX - minX;

  const wantTwo = span > 700;
  if (!wantTwo) return false;

  const mid = (minX + maxX) / 2;

  for (const s of stickies) s.frameId = Number(s.x ?? 0) <= mid ? "F_CLUSTER_1" : "F_CLUSTER_2";

  const leftGroup = usable.filter((s) => Number(s.x ?? 0) <= mid);
  const rightGroup = usable.filter((s) => Number(s.x ?? 0) > mid);
  if (!leftGroup.length || !rightGroup.length) return false;

  const PADDING = 520;
  const MIN_W = 1800, MIN_H = 1100;

  const mk = (group, title, id) => {
    const bb = bboxOf(group);
    const w = Math.max(MIN_W, bb.maxX - bb.minX + PADDING * 2);
    const h = Math.max(MIN_H, bb.maxY - bb.minY + PADDING * 2);
    const cx = (bb.minX + bb.maxX) / 2;
    const cy = (bb.minY + bb.maxY) / 2;
    return { id, title, x: cx, y: cy, w, h };
  };

  const newFrames = [
    mk(leftGroup, "Product A", "F_CLUSTER_1"),
    mk(rightGroup, "Product B", "F_CLUSTER_2"),
  ];

  frames.splice(0, frames.length, ...newFrames);
  layoutFramesNoOverlap(frames);
  return true;
}

function ensureFramesHard(frames, stickies) {
  const meaningful = stickies.filter((s) => isMeaningfulStickyText(s.text));
  if (frames.length > 0) return;
  if (meaningful.length < 2) return;

  if (autoFramesFromTitleStickies(frames, stickies)) return;
  if (autoFramesByXClusters(frames, stickies)) return;

  frames.push({ id: "F_SINGLE", title: "Workshop", x: 0, y: 0, w: 2400, h: 1500 });
  for (const s of stickies) s.frameId = "F_SINGLE";
}

// --- Connector policy helpers ---
function framesAreTwo(frames) { return frames.length === 2; }

function connectorCrossesFrames(conn, stickiesById) {
  const a = stickiesById.get(conn.from);
  const b = stickiesById.get(conn.to);
  if (!a || !b) return false;
  const fa = a.frameId ?? null;
  const fb = b.frameId ?? null;
  return fa && fb && fa !== fb;
}

function filterStickyConnectors(connectors, stickiesById, frames) {
  const list = Array.isArray(connectors) ? connectors : [];

  // Filter invalid / arrow endpoints
  const base = list.filter((c) => {
    const a = stickiesById.get(c.from);
    const b = stickiesById.get(c.to);
    if (!a || !b) return false;
    if (!isMeaningfulStickyText(a.text)) return false;
    if (!isMeaningfulStickyText(b.text)) return false;
    return true;
  });

  // If exactly 2 frames, DROP connectors that cross frames (we’ll do frame->frame instead)
  if (framesAreTwo(frames)) {
    return base.filter((c) => !connectorCrossesFrames(c, stickiesById));
  }

  return base;
}

async function createContainerToContainerConnector(frames, frameMap, localFrameById, created) {
  // Determine left/right
  const fLeft = Number(frames[0].x ?? 0) <= Number(frames[1].x ?? 0) ? frames[0] : frames[1];
  const fRight = fLeft === frames[0] ? frames[1] : frames[0];

  const leftMiro = frameMap.get(fLeft.id);
  const rightMiro = frameMap.get(fRight.id);
  if (!leftMiro || !rightMiro) return;

  // 1) Try native frame->frame connector (best, no extra items)
  try {
    const conn = await tryCreateFrameToFrameConnector(leftMiro, rightMiro);
    created.connectorIds.push(conn.id);
    return;
  } catch (e) {
    // Fall back below
  }

  // 2) Fallback: anchors near TOP edges (kept out of main content)
  const pA = frameAnchorPoint(fLeft, "right");
  const pB = frameAnchorPoint(fRight, "left");

  const a1 = await createHiddenAnchorOnBoard(pA.x, pA.y);
  const a2 = await createHiddenAnchorOnBoard(pB.x, pB.y);
  created.stickyIds.push(a1.id, a2.id);

  await moveStickyIntoFrame(a1.id, pA.x, pA.y, leftMiro, fLeft);
  await moveStickyIntoFrame(a2.id, pB.x, pB.y, rightMiro, fRight);

  const conn = await createConnectorBetweenItems({ shape: "straight", label: null }, a1.id, a2.id);
  created.connectorIds.push(conn.id);
}

// --- commands ---
async function undo(sessionKey) {
  const state = loadState();
  const sess = state.sessions?.[sessionKey];
  if (!sess?.lastRun) {
    console.log(`Nothing to undo for sessionKey=${sessionKey}`);
    return;
  }
  for (const id of sess.lastRun.connectorIds ?? []) await deleteConnector(id).catch(() => {});
  for (const id of sess.lastRun.stickyIds ?? []) await deleteSticky(id).catch(() => {});
  for (const id of sess.lastRun.frameIds ?? []) await deleteFrame(id).catch(() => {});
  state.sessions[sessionKey].lastRun = null;
  saveState(state);
  console.log(`Undone sessionKey=${sessionKey}`);
}

async function apply(jsonPath) {
  const doc = JSON.parse(fs.readFileSync(jsonPath, "utf-8"));
  const meta = doc.meta ?? {};
  const sessionKey = String(meta.sessionKey ?? "").trim();
  if (!sessionKey) throw new Error("meta.sessionKey is required");

  const state = loadState();
  state.sessions = state.sessions ?? {};
  state.sessions[sessionKey] = state.sessions[sessionKey] ?? { lastRun: null };

  // Idempotent run
  if (state.sessions[sessionKey].lastRun) await undo(sessionKey);

  const frames = Array.isArray(doc.frames) ? doc.frames : [];
  const stickies = Array.isArray(doc.stickies) ? doc.stickies : [];
  const connectors = Array.isArray(doc.connectors) ? doc.connectors : [];

  ensureFramesHard(frames, stickies);

  const created = { frameIds: [], stickyIds: [], connectorIds: [] };

  try {
    // 1) Create frames
    const frameMap = new Map(); // local frameId -> miro frameId
    for (const f of frames) {
      const cf = await createFrame(f);
      frameMap.set(f.id, cf.id);
      created.frameIds.push(cf.id);
      console.log(`✔ frame ${f.id} -> ${cf.id}`);
    }
    const localFrameById = new Map(frames.map((f) => [f.id, f]));

    // 2) Create stickies (SKIP arrow-only)
    const itemMap = new Map(); // local stickyId -> miro stickyId
    const stickiesById = new Map(stickies.map((s) => [s.id, s]));

    for (const s of stickies) {
      if (!isMeaningfulStickyText(s.text)) continue;
      const cs = await createStickyOnBoard(s);
      itemMap.set(s.id, cs.id);
      created.stickyIds.push(cs.id);
    }

    // 3) Move stickies into frames
    for (const s of stickies) {
      const miroStickyId = itemMap.get(s.id);
      if (!miroStickyId) continue;

      const frameMiroId = s.frameId ? frameMap.get(s.frameId) : null;
      const frameLocal = s.frameId ? localFrameById.get(s.frameId) : null;
      if (!frameMiroId || !frameLocal) continue;

      await moveStickyIntoFrame(miroStickyId, s.x, s.y, frameMiroId, frameLocal);
    }

    // 4) Connectors:
    //    A) sticky->sticky ONLY within same frame (when 2 frames mode)
    //    B) container->container ALWAYS when exactly 2 frames
    const filteredStickyConnectors = filterStickyConnectors(connectors, stickiesById, frames);

    // Create sticky connectors (typically intra-frame)
    for (const c of filteredStickyConnectors) {
      const from = itemMap.get(c.from);
      const to = itemMap.get(c.to);
      if (!from || !to) continue;
      const cc = await createConnectorBetweenItems(c, from, to);
      created.connectorIds.push(cc.id);
    }

    // Create container connector if 2 frames (and only once)
    if (framesAreTwo(frames)) {
      await createContainerToContainerConnector(frames, frameMap, localFrameById, created);
    }

    // Persist
    state.sessions[sessionKey].lastRun = created;
    saveState(state);

    console.log(
      `Done. sessionKey=${sessionKey}, frames=${created.frameIds.length}, stickies=${created.stickyIds.length}, connectors=${created.connectorIds.length}`
    );
  } catch (err) {
    console.log(`❌ apply failed -> rollback: ${String(err?.message ?? err)}`);
    for (const id of created.connectorIds.reverse()) await deleteConnector(id).catch(() => {});
    for (const id of created.stickyIds.reverse()) await deleteSticky(id).catch(() => {});
    for (const id of created.frameIds.reverse()) await deleteFrame(id).catch(() => {});
    throw err;
  }
}

(async () => {
  const cmd = process.argv[2];
  if (!cmd) return usage();

  if (cmd === "apply") return apply(process.argv[3]);
  if (cmd === "undo") return undo(process.argv[3]);

  usage();
})();
