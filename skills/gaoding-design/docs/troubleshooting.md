# 踩坑记录

## 阶段一：环境搭建

### 1. Node.js 版本不兼容

**问题：** OpenClaw v2026.2.26 要求 Node.js >= 22.12.0，系统默认 Node 版本为 v20.11.1。

**报错：**
```
npm WARN EBADENGINE Unsupported engine {
  package: 'openclaw@2026.2.26',
  required: { node: '>=22.12.0' },
  current: { node: 'v20.11.1', npm: '10.2.4' }
}
```

**解决：** 使用 fnm（Fast Node Manager）安装并切换到 Node 22：
```bash
fnm install 22        # 安装 v22.22.0
fnm use 22            # 切换到 Node 22
```

**注意：** 每次新开终端需要先执行 `eval "$(fnm env)" && fnm use 22`。

---

### 2. TypeScript 编译错误：Playwright API 不存在

**问题：** `page.keyboard.selectAll()` 不是 Playwright 的合法 API。

**报错：**
```
src/browser/edit.ts:34:30 - error TS2339: Property 'selectAll' does not exist on type 'Keyboard'.
```

**解决：** 改用键盘快捷键：
```typescript
// 错误
await page.keyboard.selectAll();
// 正确
await page.keyboard.press('ControlOrMeta+a');
```

---

### 3. Gateway 启动失败：未设置 gateway.mode

**问题：** OpenClaw Gateway 安装后无法启动，进程立即退出。

**错误日志（~/.openclaw/logs/gateway.err.log）：**
```
Gateway start blocked: set gateway.mode=local (current: unset) or pass --allow-unconfigured.
```

**解决：**
```bash
openclaw config set gateway.mode local
openclaw daemon restart
```

---

### 4. LLM 连接 403：API 协议格式不匹配（关键）

**问题：** 配置了 Claude API 代理后，所有模型调用均返回 `403 Your request was blocked`。

**报错：**
```
All models failed (3): foxcodeoffical/claude-opus-4-6: 403 Your request was blocked. (auth)
```

**排查过程：**
1. 最初怀疑是 API Key 问题 — 发现 Key 末尾有多余转义引号 `\"`，修复后仍然 403
2. 怀疑是 Cloudflare Bot 防护 — curl 测试确认域名有 Cloudflare JS Challenge
3. 关键发现：Claude Code 也走同一个代理（`code.newcli.com`）且正常工作

**根因：** OpenClaw 配置的 `api` 类型为 `openai-completions`，会以 OpenAI 格式发请求（`/v1/chat/completions` + `Authorization: Bearer`）。而代理只支持 Anthropic 原生协议（`/v1/messages` + `x-api-key`）。

**解决：** 将 `api` 从 `openai-completions` 改为 `anthropic-messages`：
```json
{
  "models": {
    "providers": {
      "foxcodeoffical": {
        "api": "anthropic-messages",  // 不是 "openai-completions"
        "apiKey": "sk-ant-xxx",
        "baseUrl": "https://code.newcli.com/claude"
      }
    }
  }
}
```

**OpenClaw 支持的 API 类型：**
- `openai-completions` — OpenAI Chat Completions 格式
- `openai-responses` — OpenAI Responses 格式
- `anthropic-messages` — Anthropic Messages 格式
- `google-generative-ai` — Google Gemini 格式
- `ollama` — Ollama 本地模型
- 其他：`openai-codex-responses`、`github-copilot`、`bedrock-converse-stream`

---

### 5. 安全审计告警

**问题：** `openclaw status` 报告 3 个 CRITICAL 安全问题。

**修复：**
```bash
# 配置文件权限过宽
chmod 600 ~/.openclaw/openclaw.json
# 状态目录权限过宽
chmod 700 ~/.openclaw
# Gateway auth 在 daemon install 时自动生成了 token
```

---

## 阶段二：飞书 Bot 接入

### 6. 飞书插件重复加载警告

**问题：** Gateway 日志持续输出 `duplicate plugin id detected` 警告。

**报错：**
```
plugins.entries.feishu: plugin feishu: duplicate plugin id detected;
later plugin may be overridden
```

**原因：** OpenClaw 内置了 stock 版本的 feishu 插件（v2026.2.26），同时又通过 `openclaw plugins install @openclaw/feishu` 安装了全局版本（v2026.2.25），两者 id 相同导致冲突。

**解决：** 不影响功能，可忽略。全局安装的版本会覆盖 stock 版本。如需消除警告，可在配置中显式指定 `plugins.allow`。

---

### 7. 飞书探测失败：app do not have bot

**问题：** `openclaw status --deep` 显示飞书频道探测失败。

**报错：**
```
Feishu: WARN - failed (unknown) - API error: app do not have bot
```

**原因：** 飞书应用尚未开启「机器人」能力。仅配置了 App ID 和 App Secret 不够，还需要在飞书开放平台启用 Bot 能力。

**解决：** 在飞书开放平台完成以下配置：
1. 进入应用 → 「添加应用能力」→ 开启「机器人」
2. 「权限管理」→ 添加权限：`im:message`、`im:message:send_as_bot`、`im:resource`
3. 「事件与回调」→ 订阅方式选「使用长连接接收事件/回调」
4. 创建版本并发布（企业内部可见即可）

配置完成后重启 Gateway：
```bash
openclaw daemon restart
openclaw status --deep
```

---

## 阶段三：Skill 核心开发

### 8. 稿定搜索 URL 格式错误

**问题：** 最初使用 `/s/关键词` 作为搜索路径，页面返回 404。

**报错：**
```
页面标题: 404页面-稿定设计
页面 URL: https://www.gaoding.com/scenes/海报
```

**排查：** 批量测试了 `/search?q=`、`/s?q=`、`/design/search?q=` 等路径，均返回 404。

**正确 URL：** `https://www.gaoding.com/templates?q=关键词`

**DOM 关键选择器：**
- 瀑布流容器：`gdwc-waterfall.js-waterfall__waterfall-panel`
- 模板卡片：`div.js-waterfall__item` → `div.contents-material-card-v2`
- 模板链接：`a[href^="/template/"]`，ID 从路径 `/template/{id}` 提取
- 预览图：`picture.lazy-image-modern img`，CDN 域名 `gd-filems.dancf.com`

---

### 9. Skill 快照缓存导致非内置 Skill 不加载（关键）

**问题：** `gaoding-template-recommend` Skill 已安装且 `openclaw skills list` 显示 `✓ ready`，但 Agent 对话时 prompt 中只有 5 个内置 Skill，我们的 Skill 始终不出现。

**现象：**
- `openclaw skills list` 显示 10 个 Skill 全部 ready（包括我们的）
- 新建 session 测试正常，所有 10 个 Skill 都在
- 但旧的 main session（飞书绑定的那个）始终只有 5 个内置 Skill

**排查过程：**
1. 检查 `openclaw config get skills` — `entries.gaoding-template-recommend.enabled: true` ✓
2. 检查 `openclaw config get agents` — 无 skill filter ✓
3. 检查 `openclaw config get channels` — 飞书频道无 skill filter ✓
4. 阅读 OpenClaw 源码，发现 Skill 快照缓存机制

**根因：** OpenClaw 的 session 级 Skill 快照缓存机制存在 bug：

1. 每个 session 在 `sessions.json` 中缓存了 `skillsSnapshot`（包含 skills 列表和 version 号）
2. Gateway 有一个 chokidar watcher 监控 SKILL.md 文件变化，变化时递增内存中的 `snapshotVersion` 计数器
3. 快照刷新条件：`snapshotVersion > 0 && stored_version < snapshotVersion`
4. **问题：** Gateway 重启后，内存中的 `snapshotVersion` 重置为 0，而旧 session 的 `stored_version` 也是 0
5. 刷新条件 `0 > 0` 永远为 false → 旧 session 的快照永远不会刷新

**解决：** 手动删除 session 中的 `skillsSnapshot` 缓存，让 OpenClaw 在下次 Agent 运行时重建：

```python
# 删除 sessions.json 中的 skillsSnapshot
import json
path = '~/.openclaw/agents/main/sessions/sessions.json'
with open(path) as f:
    data = json.load(f)
for key in data:
    if 'skillsSnapshot' in data[key]:
        del data[key]['skillsSnapshot']
with open(path, 'w') as f:
    json.dump(data, f, indent=2)
```

然后重启 Gateway：
```bash
openclaw daemon restart
```

**验证：**
```bash
openclaw agent --session-id "你的session-id" -m "列出你所有的 skills"
# 应该返回所有 10 个 skills
```

**预防：** 安装新 Skill 后，如果旧 session 看不到，优先尝试：
1. 修改 SKILL.md 触发 watcher（仅在 Gateway 未重启时有效）
2. 或直接删除 `skillsSnapshot` 缓存 + 重启 Gateway

---

## 阶段四：端到端测试

### 10. 飞书消息到达 Gateway 但不分发给 Agent（Pairing 死循环）

**问题：** 飞书发消息后，Gateway 日志显示 `received message`，但 Agent 从未被调用，消息被静默丢弃。

**现象：**
- Gateway 日志有 `received message` 但无 `agent` 相关日志
- 无 `pairing request` 日志（因为 pairing 请求已存在，`created=false`）
- `openclaw pairing list` 显示 pending 请求

**排查过程：**
1. 阅读 `feishu/src/bot.ts` 源码，发现消息路由流程：
   - 收到消息 → 解析发送者 → 检查 `dmPolicy`（默认 `"pairing"`）
   - 检查 `allowFrom`（config 级 + store 级）
   - 如果 `!dmAllowed` → 进入 pairing 流程 → 如果请求已存在（`created=false`）→ **静默 return**
2. `openclaw pairing approve` 更新了 `feishu-default-allowFrom.json` 文件
3. 但运行中的 Gateway 缓存了 allowFrom 列表，不会重新读取文件
4. 重启 Gateway 会生成新的 pairing code，之前的 approve 失效
5. 形成死循环：approve → restart → 新 code → approve → restart...

**根因：** Gateway 的 store 级 allowFrom 在内存中缓存，重启后 pairing code 重新生成，导致 approve 永远追不上。

**解决：** 使用 config 级 `allowFrom` 绕过 pairing store 缓存：
```bash
openclaw config set channels.feishu.allowFrom '["ou_你的open_id"]'
openclaw daemon restart
```

config 级 allowFrom 直接从配置文件读取，不受 pairing store 缓存影响。

**获取 open_id：** 查看 `~/.openclaw/credentials/feishu-pairing.json` 中的 `id` 字段。

---

### 11. 搜索结果完全不匹配（URL 参数无效 + 搜索按钮隐藏）

**问题：** 搜索"电商海报"返回"少儿教育机构招生"、"融媒体政务会议"等完全无关的模板。

**排查过程：**

**第一层问题 — URL `?q=` 参数被忽略：**
- 最初使用 `https://www.gaoding.com/templates?q=电商海报`
- 页面标题仍为通用的"图片设计模板_图片模板素材-稿定设计"
- 瀑布流显示 120 个默认模板，未经过滤
- 结论：`?q=` 参数被稿定前端完全忽略

**第二层问题 — Enter 键不触发搜索：**
- 改为在搜索框 `input.search-input-v1__input` 中输入关键词后按 Enter
- URL 仍停留在 `/templates`，搜索未触发
- 原因：搜索按钮是 `type="button"`（不是 `type="submit"`），Enter 不会触发表单提交
- 搜索由 SPA JavaScript 事件处理，需要点击"搜 索"按钮

**第三层问题 — 搜索按钮在小视口下隐藏：**
- 搜索按钮有 CSS 类 `xsmall-hide small-hide`
- Playwright 默认视口 1280x720 被视为"small"，按钮不可见
- `locator.click()` 因元素不可见而超时

**解决：** 三管齐下：
```typescript
// 1. 设置大视口确保按钮可见
await page.setViewportSize({ width: 1920, height: 1080 });

// 2. 在搜索框输入关键词
const input = page.locator('input.search-input-v1__input').first();
await input.click();
await input.fill(query);

// 3. 点击搜索按钮（带 JS fallback）
const searchBtn = page.locator('button.global-search-experiment-v1__search-button').first();
await searchBtn.click({ timeout: 5000 }).catch(async () => {
    await page.evaluate(() => {
        const btn = document.querySelector('button.global-search-experiment-v1__search-button');
        if (btn) (btn as HTMLElement).click();
    });
});

// 4. 等待搜索结果页导航
await page.waitForURL(/\/(scenes|templates)\/.*/, { timeout: 10000 });
```

**关键 DOM 选择器（2026.02 验证）：**
- 搜索输入框：`input.search-input-v1__input`
- 搜索按钮：`button.global-search-experiment-v1__search-button`
- 搜索表单：`form.global-search-experiment-v1`
- 搜索结果页 URL 模式：`/scenes/{slug}?from=search-direct&search_word=...`
