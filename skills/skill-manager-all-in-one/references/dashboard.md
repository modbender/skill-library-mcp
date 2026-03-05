# 查看已发布技能 | View Published Skills

## ClawHub Dashboard（最优先）

**这是查看自己发布的所有 skills 的唯一可靠方式。**

### 方法 1：浏览器访问

直接访问：
```
https://clawhub.com/dashboard
```

需要浏览器登录 GitHub 账号。

### 方法 2：使用 browser 工具

如果有 browser 工具可用，可以通过自动化访问：

```
1. 打开 Dashboard：
   browser action=open url=https://clawhub.com/dashboard

2. 如需登录，等待用户完成 GitHub 登录

3. 获取快照查看已发布技能：
   browser action=snapshot
```

### Dashboard 显示信息

每个 skill 卡片包含：
- **名称** + 路径（slug）
- **描述**（description）
- **统计数据**：
  - 📥 浏览量
  - ⭐ 星数
  - 版本数（如 "3 v" 表示 3 个版本）
- **状态标签**：
  - `Scanning` — 安全扫描中
  - 正常显示 — 已通过扫描
- **操作按钮**：
  - **New Version** — 上传新版本
  - **View** — 查看详情页

---

## CLI 查看方法

### 查看单个技能详情

```bash
npx clawhub@latest inspect <slug>
```

输出示例：
```
moltbook-user  Moltbook User | Moltbook 用户
Summary: Interact with Moltbook AI social network...
Owner: Moroiser
Created: 2026-03-02T18:50:57.696Z
Updated: 2026-03-02T19:10:49.404Z
Latest: 1.0.1
Tags: latest=1.0.1
```

### ⚠️ CLI 局限性

- 如果技能处于 "Scanning" 状态，CLI 会报错：
  ```
  Skill is hidden while security scan is pending. Try again in a few minutes.
  ```
- 此时只能通过 Dashboard 查看

---

## 技能状态说明

| 状态 | 说明 |
|------|------|
| Scanning | 安全扫描中，暂时不可通过 CLI 访问 |
| 正常显示 | 已通过安全扫描，可正常访问 |
| Hidden | 被隐藏（moderator 操作） |
