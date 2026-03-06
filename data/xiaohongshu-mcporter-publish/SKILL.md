---
name: xiaohongshu-publish
description: 小红书创作者平台写帖子：mcporter 调用 chrome-devtools-mcp 操作浏览器，禁止 browser 工具。上传图片、填写标题正文，发布由用户手动完成。
metadata:
  {
    "openclaw":
      {
        "emoji": "📕",
        "requires": { "bins": ["mcporter"] },
      },
  }
---

# 小红书图文发布

- 页面：`https://creator.xiaohongshu.com/publish/publish?source=official&from=tab_switch`
- 用 mcporter 调用 chrome-devtools-mcp，禁止 browser 工具
- 图片路径：用户说「电脑桌上的 XX 文件夹」→ `~/Desktop/XX`，用 ls 查目录找到具体图片
- 禁止点击发布，由用户手动完成
