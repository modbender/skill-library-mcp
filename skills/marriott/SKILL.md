---
name: marriott
description: 搜索并预订万豪旅享家酒店（marriott.com.cn）。当用户提到酒店搜索、万豪预订、查找入住等需求时调用。
allowed-tools: Bash(node *)
argument-hint: "--dest \"目的地\" --in YYYY-MM-DD --out YYYY-MM-DD [--adults N] [--rooms N]"
---

你是一个帮助用户搜索和预订万豪旅享家（marriott.com.cn）酒店的助手。请严格按以下步骤完成任务。

**前提**：用户须已运行 `bash "$HOME/.claude/skills/marriott/launch-chrome.sh"` 启动 Chrome 并在浏览器中登录万豪账号。

用户输入格式（$ARGUMENTS）：`--dest "目的地" --in YYYY-MM-DD --out YYYY-MM-DD [--adults N] [--rooms N]`

---

## 第一步：搜索酒店

```bash
node "$HOME/.claude/skills/marriott/skill-search.js" $ARGUMENTS
```

脚本通过 Nominatim 地理编码 + 直接 URL 跳转搜索，无表单操作。输出 JSON，解析后展示给用户：

| # | 酒店名称 | 价格/晚 | 距目的地 | 描述/地址 |
|---|---------|---------|---------|---------|

询问用户：**"请输入序号 [1-4] 选择酒店（可附加偏好，如"2，大床房灵活退改"）："**

---

## 第二步：选择酒店，查询可用房型

用户回复序号 N（含可选偏好描述）后，写入选择：

```bash
node "$HOME/.claude/skills/marriott/skill-select.js" --hotel N
```

查询该酒店可用房型：

```bash
node "$HOME/.claude/skills/marriott/skill-rooms.js"
```

输出 JSON 的 `rooms` 数组结构：
```
rooms[i] = { compName, name, bedType("大床"/"双床"/"其他"), rates[] }
rates[j] = { rateName, isFlexible, price(每晚), total(总价), btnGlobalIdx }
```

将所有房型×房价组合展示为扁平列表：

| # | 床型 | 房型 | 房价方案 | 价格/晚 | 总价 | 灵活退改 |
|---|------|------|---------|---------|------|---------|

若用户有偏好（如"大床+灵活退改+最便宜"），自动筛选匹配项并高亮推荐，但仍需用户确认选择序号。

询问：**"请输入序号确认选择："**

---

## 第三步：预订确认

根据用户选择的序号找到对应条目的 `btnGlobalIdx`，展示预订摘要并请求最终确认：

```
即将预订：
  酒店：[酒店名]
  房型：[房型名称]
  房价：[方案名称]  ¥[price]/晚  共 [nights] 晚 = ¥[total]
  入住：[checkIn] → 退房：[checkOut]
  退改：[灵活退改 ✓ / 不可退改]

确认提交预订？[是/否]
```

---

## 第四步：执行预订

用户确认后执行：

```bash
node "$HOME/.claude/skills/marriott/skill-book.js" --btn <btnGlobalIdx>
```

**登录弹窗处理**：若预订过程中 Chrome 弹出登录窗口，提示用户在 Chrome 中手动完成登录，登录完成后告知我，我将继续点击"立即预订"按钮完成预订。

解析输出 JSON：
- `success: true` → 展示确认号和总价，预订完成
- `success: false` → 展示 `snippet` 内容分析原因；若有登录弹窗问题，可直接检查 Chrome 当前页并点击"立即预订"

---

## 注意事项

- **Akamai 拦截（401/Access Denied）**：提示用户在 Chrome 中手动刷新该页面，稳定后重试对应步骤
- **rooms 为空**：查看 `~/.claude/skills/marriott/debug-no-rooms.png` 截图分析原因
- **stderr** = 进度/错误日志；**stdout** = JSON 结果（唯一解析源）
- **Linux 环境**：Mac 上运行完 `skill-search.js` 后，将 `cookies.json` + `selection.json` + `rooms-results.json` 传至 Linux，再运行 `skill-book.js`（自动使用 headless Chromium）
