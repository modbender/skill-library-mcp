---
name: realtime-interact
description: |
  实时交互浮窗技能。在需要用户确认、输入或交互的场景中，通过浮窗方式在当前操作界面旁边进行交互，
  而不是回到OpenClaw聊天窗口。适用于：(1) 评论内容需要用户确认后执行，(2) 删除文件前需要用户确认，
  (3) 购物付款时需要输入密码，(4) 任何需要即时交互的场景。支持系统级浮窗和浏览器内浮窗。
metadata:
  version: "1.0.0"
  author: "liuyong74"
---

# Realtime Interact - 实时交互浮窗

在用户当前操作界面旁边弹出浮窗进行交互，提供流畅的确认/输入体验。

## 快速开始

### 浮窗类型

| 场景 | 使用方式 |
|------|---------|
| 确认框（是/否） | `interact.confirm(title, message)` |
| 输入框 | `interact.input(title, message, default)` |
| 选择框 | `interact.select(title, options)` |
| 自定义HTML | `interact.html(title, html_content)` |

### 基础示例

**1. 评论前确认**
```
用户：帮我评论这条朋友圈

AI：准备评论内容后，调用浮窗确认
→ 浮窗弹出：显示"写的评论内容"
→ 用户点击"确认"
→ AI执行评论
```

**2. 删除文件确认**
```
用户：帮我删除这个文件

AI：准备删除操作后，调用浮窗确认
→ 系统浮窗弹出："确定删除 xxx 吗？"
→ 用户点击"确认删除"
→ AI执行删除
```

**3. 密码输入**
```
用户：帮我完成支付

AI：准备支付后，调用输入框
→ 浮窗弹出：密码输入框
→ 用户输入密码
→ AI执行支付
```

## 技术实现

### 方式一：macOS 系统浮窗（本地操作）

适用于：删除文件、执行命令等本地操作

```bash
python3 ~/.openclaw/skills/realtime-interact-1.0.0/scripts/macos_dialog.py \
  --type confirm \
  --title "确认删除" \
  --message "确定要删除文件 /path/to/file 吗？"
```

**参数：**
- `--type`: confirm | input | select
- `--title`: 浮窗标题
- `--message`: 浮窗内容
- `--default`: 默认值（input类型需要）
- `--options`: 选项（select类型需要，用逗号分隔）

### 方式二：浏览器内浮窗（网页操作）

适用于：网页评论、购物等浏览器内操作

```bash
# 在当前浏览器页面注入浮窗
python3 ~/.openclaw/skills/realtime-interact-1.0.0/scripts/browser_modal.py \
  --action show \
  --type confirm \
  --title "评论确认" \
  --message "确认发送这条评论吗？"
```

### 方式三：Canvas 覆盖层（通用）

使用 OpenClaw canvas 绘制覆盖层：

```javascript
// 通过 JavaScript 注入创建浮窗
// 见 scripts/inject_modal.js
```

## 浮窗样式

浮窗采用现代美观设计：
- 🎨 毛玻璃效果背景
- 📐 居中弹出，带阴影
- 🔘 圆角按钮
- ✨ 流畅动画过渡

## 交互流程

```
1. 用户发起请求（如：评论朋友圈）
2. AI 准备交互内容（评论文案、操作指令等）
3. 判断场景类型：
   - 本地操作 → macOS 浮窗
   - 浏览器操作 → 浏览器内浮窗
   - 不确定 → 优先浏览器浮窗
4. 弹出浮窗展示内容
5. 用户确认/输入
6. 返回结果给 AI
7. AI 执行实际操作
8. 反馈结果给用户
```

## 错误处理

- 用户取消：返回 `{"result": "cancel"}`
- 超时（默认60秒）：返回 `{"result": "timeout"}`
- 执行失败：返回 `{"result": "error", "message": "..."}`

## 扩展功能

### 语音交互（未来）

计划支持：
- 语音输入
- 语音确认（"好的"、"确认"）
- 语音播报结果

---

**注意**：首次使用需要授权 macOS 辅助功能权限（系统偏好设置 → 安全性与隐私 → 辅助功能）
