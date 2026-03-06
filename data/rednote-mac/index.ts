/**
 * rednote-mac OpenClaw Plugin
 * 通过 Accessibility API 控制 Mac 小红书 App
 */

import { execFile } from "node:child_process";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);

import { fileURLToPath } from "node:url";
import { dirname } from "node:path";
const SKILL_DIR = dirname(fileURLToPath(import.meta.url));

/** 调用 xhs_controller.py 里的函数，返回 stdout 字符串 */
async function xhsCall(pyCode: string): Promise<string> {
  const { stdout, stderr } = await execFileAsync(
    "uv",
    ["run", "--directory", SKILL_DIR, "python", "-c", pyCode],
    { timeout: 30000 }
  );
  if (stderr && stderr.trim()) {
    // stderr 里有些是正常的 import 警告，只打印非空内容
    process.stderr.write(`[rednote-mac] ${stderr}\n`);
  }
  return stdout.trim();
}

/** 截图并返回 base64 */
async function xhsScreenshot(): Promise<string | null> {
  const { execFile: ef } = await import("node:child_process");
  const { promisify: pf } = await import("node:util");
  const { readFileSync, unlinkSync } = await import("node:fs");
  const { tmpdir } = await import("node:os");
  const { join } = await import("node:path");
  
  const path = join(tmpdir(), `xhs_plugin_${Date.now()}.png`);
  try {
    await pf(ef)("uv", ["run", "--directory", SKILL_DIR, "python", "-c",
      `from xhs_controller import screenshot; screenshot(${JSON.stringify(path)})`
    ], { timeout: 10000 });
    const data = readFileSync(path);
    unlinkSync(path);
    return data.toString("base64");
  } catch {
    return null;
  }
}

function ok(text: string, screenshot?: string | null) {
  const content: any[] = [{ type: "text", text }];
  if (screenshot) content.push({ type: "image", data: screenshot, mimeType: "image/png" });
  return { content };
}

function err(msg: string) {
  return { content: [{ type: "text", text: `❌ ${msg}` }] };
}

export default function register(api: any) {

  // ── 截图 ──
  api.registerTool({
    name: "xhs_screenshot",
    description: "截取小红书当前界面截图",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      const b64 = await xhsScreenshot();
      if (!b64) return err("截图失败，rednote 窗口可能不在屏幕上");
      return { content: [{ type: "image", data: b64, mimeType: "image/png" }] };
    },
  }, { optional: true });

  // ── 导航 ──
  api.registerTool({
    name: "xhs_navigate",
    description: "切换底部 Tab：home(首页) messages(消息) profile(我)",
    parameters: {
      type: "object",
      properties: {
        tab: { type: "string", enum: ["home", "messages", "profile"], description: "目标 Tab" }
      },
      required: ["tab"],
    },
    async execute(_id: string, { tab }: { tab: string }) {
      await xhsCall(`from xhs_controller import navigate_tab; import time; navigate_tab(${JSON.stringify(tab)}); time.sleep(1.0)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 已导航到 ${tab}`, b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_navigate_top",
    description: "切换顶部 Tab：follow(关注) discover(发现) video(视频)",
    parameters: {
      type: "object",
      properties: {
        tab: { type: "string", enum: ["follow", "discover", "video"], description: "目标 Tab" }
      },
      required: ["tab"],
    },
    async execute(_id: string, { tab }: { tab: string }) {
      await xhsCall(`from xhs_controller import navigate_top_tab; import time; navigate_top_tab(${JSON.stringify(tab)}); time.sleep(1.0)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 已切换到 ${tab}`, b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_back",
    description: "返回上一页",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      await xhsCall(`from xhs_controller import back; import time; back(); time.sleep(1.0)`);
      const b64 = await xhsScreenshot();
      return ok("✅ 已返回", b64);
    },
  }, { optional: true });

  // ── 搜索 ──
  api.registerTool({
    name: "xhs_search",
    description: "搜索关键词，跳转到搜索结果页",
    parameters: {
      type: "object",
      properties: {
        keyword: { type: "string", description: "搜索关键词" }
      },
      required: ["keyword"],
    },
    async execute(_id: string, { keyword }: { keyword: string }) {
      await xhsCall(`from xhs_controller import search; import time; search(${JSON.stringify(keyword)}); time.sleep(2.0)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 搜索: ${keyword}`, b64);
    },
  }, { optional: true });

  // ── Feed ──
  api.registerTool({
    name: "xhs_scroll_feed",
    description: "滚动 Feed 流",
    parameters: {
      type: "object",
      properties: {
        direction: { type: "string", enum: ["down", "up"], default: "down" },
        times: { type: "integer", default: 3 },
      },
      required: [],
    },
    async execute(_id: string, { direction = "down", times = 3 }: any) {
      await xhsCall(`from xhs_controller import scroll_feed; import time; scroll_feed(${JSON.stringify(direction)}, ${times}); time.sleep(0.5)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 向 ${direction} 滚动 ${times} 次`, b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_open_note",
    description: "点击 Feed 双列瀑布流中的笔记",
    parameters: {
      type: "object",
      properties: {
        col: { type: "integer", default: 0, description: "列号：0=左列，1=右列" },
        row: { type: "integer", default: 0, description: "行号：0=第一行" },
      },
      required: [],
    },
    async execute(_id: string, { col = 0, row = 0 }: any) {
      await xhsCall(`from xhs_controller import open_note; import time; open_note(${col}, ${row}); time.sleep(2.0)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 已打开第 ${row} 行第 ${col} 列笔记`, b64);
    },
  }, { optional: true });

  // ── 笔记互动 ──
  api.registerTool({
    name: "xhs_like",
    description: "点赞当前笔记（需先进入笔记详情页）",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      await xhsCall(`from xhs_controller import like; import time; like(); time.sleep(0.8)`);
      const b64 = await xhsScreenshot();
      return ok("✅ 已点赞", b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_collect",
    description: "收藏当前笔记（需先进入笔记详情页）",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      await xhsCall(`from xhs_controller import collect; import time; collect(); time.sleep(0.8)`);
      const b64 = await xhsScreenshot();
      return ok("✅ 已收藏", b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_get_note_url",
    description: "获取当前笔记的分享链接",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      const url = await xhsCall(`from xhs_controller import get_note_url; print(get_note_url())`);
      return ok(`✅ 笔记链接: ${url}`);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_follow_author",
    description: "关注当前笔记的作者",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      await xhsCall(`from xhs_controller import follow_author; import time; follow_author(); time.sleep(0.8)`);
      const b64 = await xhsScreenshot();
      return ok("✅ 已点击关注", b64);
    },
  }, { optional: true });

  // ── 评论 ──
  api.registerTool({
    name: "xhs_open_comments",
    description: "打开评论区。视频帖完全可用；图文帖受 App 自绘渲染限制。",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      await xhsCall(`from xhs_controller import open_comments; import time; open_comments(); time.sleep(1.5)`);
      const b64 = await xhsScreenshot();
      return ok("✅ 已打开评论区", b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_scroll_comments",
    description: "滚动评论区（视频帖完全可用）",
    parameters: {
      type: "object",
      properties: { times: { type: "integer", default: 3 } },
      required: [],
    },
    async execute(_id: string, { times = 3 }: any) {
      await xhsCall(`from xhs_controller import scroll_comments; import time; scroll_comments(${times}); time.sleep(0.8)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 评论区已滚动 ${times} 次`, b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_get_comments",
    description: "获取评论列表（视频帖可靠）。返回 [{index, author, cx, cy}, ...]",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      const raw = await xhsCall(`from xhs_controller import get_comments; import json; print(json.dumps(get_comments(), ensure_ascii=False))`);
      return { content: [{ type: "text", text: raw }] };
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_post_comment",
    description: "发送评论（需先进入笔记详情页）",
    parameters: {
      type: "object",
      properties: { text: { type: "string", description: "评论内容" } },
      required: ["text"],
    },
    async execute(_id: string, { text }: { text: string }) {
      const result = await xhsCall(`from xhs_controller import post_comment; import time; r=post_comment(${JSON.stringify(text)}); time.sleep(1.0); print(r)`);
      const b64 = await xhsScreenshot();
      return ok(result === "True" ? `✅ 评论已发送: ${text}` : "❌ 发送失败，请截图检查", b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_reply_to_comment",
    description: "回复评论（index 来自 get_comments）",
    parameters: {
      type: "object",
      properties: {
        index: { type: "integer", description: "评论序号" },
        text: { type: "string", description: "回复内容" },
      },
      required: ["index", "text"],
    },
    async execute(_id: string, { index, text }: { index: number; text: string }) {
      const result = await xhsCall(`from xhs_controller import reply_to_comment; import time; r=reply_to_comment(${index}, ${JSON.stringify(text)}); time.sleep(1.0); print(r)`);
      const b64 = await xhsScreenshot();
      return ok(result === "True" ? `✅ 已回复评论 #${index}: ${text}` : "❌ 回复失败", b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_delete_comment",
    description: "删除评论（只能删自己的，不可逆）",
    parameters: {
      type: "object",
      properties: { index: { type: "integer", description: "评论序号" } },
      required: ["index"],
    },
    async execute(_id: string, { index }: { index: number }) {
      const result = await xhsCall(`from xhs_controller import delete_comment; import time; r=delete_comment(${index}); time.sleep(1.0); print(r)`);
      const b64 = await xhsScreenshot();
      return ok(result === "True" ? `✅ 评论 #${index} 已删除` : "❌ 删除失败", b64);
    },
  }, { optional: true });

  // ── 私信 ──
  api.registerTool({
    name: "xhs_open_dm",
    description: "打开消息列表中指定序号的私信对话（index=0 为第一条）",
    parameters: {
      type: "object",
      properties: { index: { type: "integer", default: 0 } },
      required: [],
    },
    async execute(_id: string, { index = 0 }: any) {
      await xhsCall(`from xhs_controller import navigate_tab, open_dm_by_index; import time; navigate_tab('messages'); time.sleep(1.0); open_dm_by_index(${index}); time.sleep(1.5)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 已打开第 ${index} 条私信`, b64);
    },
  }, { optional: true });

  api.registerTool({
    name: "xhs_send_dm",
    description: "在当前私信对话中发送消息（需先 xhs_open_dm）",
    parameters: {
      type: "object",
      properties: { text: { type: "string", description: "消息内容" } },
      required: ["text"],
    },
    async execute(_id: string, { text }: { text: string }) {
      await xhsCall(`from xhs_controller import send_dm; import time; send_dm(${JSON.stringify(text)}); time.sleep(1.0)`);
      const b64 = await xhsScreenshot();
      return ok(`✅ 私信已发送: ${text}`, b64);
    },
  }, { optional: true });

  // ── 个人主页 ──
  api.registerTool({
    name: "xhs_get_author_stats",
    description: "读取当前主页的关注数/粉丝数/获赞收藏数/bio（需先导航到 profile）",
    parameters: { type: "object", properties: {}, required: [] },
    async execute(_id: string, _params: any) {
      const raw = await xhsCall(`from xhs_controller import get_author_stats; import json; print(json.dumps(get_author_stats(), ensure_ascii=False))`);
      return { content: [{ type: "text", text: raw }] };
    },
  }, { optional: true });
}
