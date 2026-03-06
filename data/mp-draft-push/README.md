# mp-draft-push (Skill)

> 最小化微信公众号发布技能：接收**现成的文章内容**，上传封面图，发布到草稿箱。不负责内容采集、AI 写作或图片生成。

---

## 目录结构

```
mp-draft-push/
├── SKILL.md          # 技能定义（AI 助手读取）
├── scripts.sh        # 辅助脚本（bash/zsh 均可用）
├── .env.example      # 环境变量模板
└── README.md
```

---

## 安装

### OpenClaw

```bash
# 方式一：放入 workspace skills（推荐）
cp -r mp-draft-push ~/.openclaw/workspace/skills/

# 方式二：放入全局 skills
cp -r mp-draft-push ~/.openclaw/skills/
```

### 其他 AI 工具

| AI 工具 | Skills 路径 |
|---------|------------|
| Codex | `~/.codex/skills/mp-draft-push/` |
| Claude Code | `~/.claude/skills/mp-draft-push/` |
| Gemini | `~/.gemini/skills/mp-draft-push/` |

---

## 配置

```bash
cd ~/.openclaw/workspace/skills/mp-draft-push   # 进入技能目录
cp .env.example .env
```

编辑 `.env`：

```bash
WECHAT_APPID=你的AppID
WECHAT_SECRET=你的AppSecret
WECHAT_AUTHOR=koo AI          # 可选，文章署名
DEFAULT_COVER_URL=             # 可选，无封面图时的兜底 URL
```

让环境变量在 OpenClaw 运行时生效（加入 Shell 配置）：

```bash
# ~/.zshrc 或 ~/.bashrc 末尾添加：
set -a; source ~/.openclaw/workspace/skills/mp-draft-push/.env; set +a
```

> AppID / AppSecret 在**微信公众号后台 → 设置与开发 → 基本配置**中获取。

---

## 在 OpenClaw 中调用

### 触发词

在对话框直接说：

```
发布文章
发布到草稿箱
publish to draft
推送到公众号
```

### 调用示例

**最简调用**（让 AI 引导你填信息）：

```
发布文章到草稿箱
```

**完整参数调用**（一次性传入所有信息，AI 直接执行）：

```
发布以下文章到微信草稿箱：
- 标题：教你用 AI 写公众号
- 摘要：3步搞定公众号排版和发布
- 封面图：/tmp/cover.png
- 正文 HTML：<section style="...">文章内容</section>
```

### 定时自动发布（OpenClaw Cron）

```bash
# 每天 09:00（上海时区）由另一个 Skill 生成内容后调用本技能发布
openclaw cron add \
  --name "daily-mp-push" \
  --cron "0 9 * * *" \
  --tz "Asia/Shanghai" \
  --session isolated \
  --message "生成今日 AI 简报并发布到草稿箱；不要提问，直接执行"

# 查看 / 删除
openclaw cron list
openclaw cron delete --name "daily-mp-push"
```

> Cron 需要 OpenClaw Gateway 常驻运行。

---

## 直接调用脚本

```bash
source ./scripts.sh

# 1. 获取 token
TOKEN=$(get_wechat_token)

# 2. 上传封面图（返回 media_id）
RESP=$(upload_wechat_image "$TOKEN" "/path/to/cover.png")
THUMB_ID=$(echo "$RESP" | jq -r '.media_id')

# 3. 构建并发布草稿
jq -n \
  --arg title "文章标题" \
  --arg author "${WECHAT_AUTHOR:-koo AI}" \
  --arg digest "文章摘要" \
  --arg content "<p style='color:#333'>正文 HTML</p>" \
  --arg thumb_media_id "$THUMB_ID" \
  '{articles:[{title:$title,author:$author,digest:$digest,content:$content,thumb_media_id:$thumb_media_id,need_open_comment:1,only_fans_can_comment:0}]}' \
  > /tmp/draft.json

create_draft "$TOKEN" /tmp/draft.json
```

---

## 依赖

```bash
brew install jq   # 如未安装（bash/curl macOS 已自带）
```

---

## 注意事项

- `.env` 已加入 `.gitignore`，不会提交到仓库
- `thumb_media_id` 为必填字段，不能为空字符串
- 文章内图片只能使用微信返回的 `mmbiz.qpic.cn` 域名 URL（需提前调 `/media/uploadimg` 接口上传）
- HTML 样式必须全部内联，微信会过滤 `<style>` 标签
- 标题最多 64 字节（约 21 个中文字符）
- `access_token` 有效期 2 小时，脚本每次调用自动重新获取
