# xhs-mac-mcp

通过 macOS Accessibility API 控制小红书（rednote）App 的 OpenClaw Plugin。

## 功能

补充 [xiaohongshu-mcp](https://github.com/...)（headless 版）无法实现的功能：

| 功能 | 说明 |
|------|------|
| 私信（send_dm） | headless 版无法做到 |
| 回复/删除评论 | 需要登录态 + App 交互 |
| 视频评论区完整读取 | AX API 可直接拿到评论列表 |
| 作者主页数据 | 关注/粉丝/获赞/bio |
| 搜索、点赞、收藏、关注 | 全部支持 |

## 前提条件

- Mac 安装了小红书（rednote）App
- Terminal 已获得辅助功能权限：**系统设置 → 隐私与安全 → 辅助功能** → 开启 Terminal
- 使用时 rednote App 必须在屏幕上**可见**（不能最小化/锁屏）
- 建议长时间任务时运行 `caffeinate -di &` 防止息屏

## 安装

```bash
# 1. 安装依赖
cd ~/.agents/skills/xhs-mac-mcp
uv sync   # 或 pip install atomacos pyobjc-framework-Quartz

# 2. 注册为 OpenClaw Plugin
ln -sf ~/.agents/skills/xhs-mac-mcp ~/.openclaw/extensions/xhs-mac

# 3. 允许 plugin 工具（加到 openclaw.json）
openclaw config set tools.allow '["xhs-mac"]'

# 4. 重启 Gateway
openclaw gateway restart
```

验证：
```bash
openclaw plugins list | grep xhs-mac
# 应显示 status: loaded
```

## 可用 Tools

| Tool | 说明 |
|------|------|
| `xhs_screenshot` | 截取当前界面截图 |
| `xhs_navigate` | 切换底部 Tab（home/messages/profile）|
| `xhs_navigate_top` | 切换顶部 Tab（follow/discover/video）|
| `xhs_back` | 返回上一页 |
| `xhs_search` | 搜索关键词 |
| `xhs_scroll_feed` | 滚动 Feed 流 |
| `xhs_open_note` | 打开 Feed 中的笔记 |
| `xhs_like` | 点赞 |
| `xhs_collect` | 收藏 |
| `xhs_get_note_url` | 获取笔记分享链接 |
| `xhs_follow_author` | 关注作者 |
| `xhs_open_comments` | 打开评论区 |
| `xhs_scroll_comments` | 滚动评论区 |
| `xhs_get_comments` | 获取评论列表 |
| `xhs_post_comment` | 发评论 |
| `xhs_reply_to_comment` | 回复评论 |
| `xhs_delete_comment` | 删除评论（只能删自己的）|
| `xhs_open_dm` | 打开私信对话 |
| `xhs_send_dm` | 发送私信 |
| `xhs_get_author_stats` | 读取主页数据 |

## 已知限制

- **图文帖评论**：小红书图文帖使用自绘渲染（Metal/Canvas），AX API 无法读取评论文字。视频帖无此限制，评论完整可读。
- **屏幕锁定**：锁屏后鼠标事件失效，需保持屏幕常亮。
- **App 可见性**：App 最小化后操作失效，需在屏幕上可见（可在后台，不需要在最前面）。

## 同时使用 Claude Desktop / Cursor

本项目同时包含标准 MCP server（`server.py`），可用于 Claude Desktop 或 Cursor：

```json
// claude_desktop_config.json
{
  "mcpServers": {
    "xhs-mac": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/xhs-mac-mcp", "python", "server.py"]
    }
  }
}
```
