---
name: token-report
description: 生成 Token 消耗仪表盘截图并发送到飞书
metadata:
  openclaw:
    emoji: 📊
    os: [darwin]
    requires: []
---

# Token 消耗汇报

当 Simon 要求汇报 Token 用量时执行：

## 步骤

1. **推送到 Canvas**
   - 用 `canvas action=present` 推送 HTML 仪表盘
   - 内容包含：主会话、Selina、Tars 的 tokens 和 context 用量

2. **截图**
   - 用 `browser action=screenshot` 截取 Canvas 画面
   - profile=openclaw

3. **发送到飞书**
   - 用 `message action=send` 发送到目标群
   - channel=feishu, target=chat:oc_ee1a93ad1eb6d46a8922d9ab898a0d10

## HTML 模板

```html
<html>
<body style="background:#0d1117;color:#e6edf3;font-family:-apple-system;padding:24px;">
<h2>📊 Token 消耗汇总</h2>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">
<div style="background:rgba(255,255,255,.06);padding:16px;border-radius:8px">
<div style="font-size:11px;color:#8b949e">主会话 (main)</div>
<div style="font-size:28px;font-weight:600">336k</div>
<div style="font-size:12px;color:#8b949e">Context 52%</div>
</div>
<!-- Selina, Tars similarly -->
</div>
<div style="margin-top:16px;font-size:12px;color:#8b949e">更新时间: 2026-02-27 17:00</div>
</body>
</html>
```
