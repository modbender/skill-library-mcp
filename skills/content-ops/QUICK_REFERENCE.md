# Content Ops 快速操作指南

## 🚀 初始化检查清单

### 1. 环境检查
```bash
cd /home/admin/.openclaw/workspace/skills/content-ops

# 检查 Node 依赖
ls node_modules/ | head -5

# 检查数据库
ls ~/.openclaw/workspace/content-ops-workspace/data/content-ops.db
```

### 2. MCP 服务检查
```bash
# 检查小红书 MCP 是否运行
curl http://localhost:18060/api/v1/login/status

# 预期返回：
# {"success": true, "data": {"is_logged_in": true, "username": "xxx"}}
```

### 3. 账号配置检查
```bash
# 查看已配置账号
npx tsx scripts/list-accounts.ts
```

---

## 🧪 测试任务

### 快速测试流程（5分钟）

```bash
cd /home/admin/.openclaw/workspace/skills/content-ops

# 1. 创建测试任务
npx tsx scripts/create-crawl-task.ts \
  --keyword "AI教程" \
  --target-count 5

# 2. 查看任务列表（复制 task-id）
npx tsx scripts/list-crawl-tasks.ts

# 3. 审核结果
npx tsx scripts/show-crawl-results.ts --task-id <task-id>

# 4. 全部通过
npx tsx scripts/approve-all.ts --task-id <task-id>

# 5. 查看可用语料
npx tsx scripts/show-available-corpus.ts
```

---

## 📋 正式任务

### 完整抓取流程

```bash
# 1. 创建抓取任务
npx tsx scripts/create-crawl-task.ts \
  --keywords "AI人工智能,ChatGPT,AI工具" \
  --target-count 50

# 2. 等待抓取完成

# 3. 查看并审核
npx tsx scripts/show-crawl-results.ts --task-id <task-id>
npx tsx scripts/approve-items.ts --task-id <task-id> --items 1,2,3

# 4. （可选）补充详情
npx tsx scripts/show-pending-details.ts
# 用户提供正文后
npx tsx scripts/import-manual-detail.ts --input /tmp/manual.txt
```

### 完整发布流程

```bash
# 1. 创建发布任务
npx tsx scripts/create-publish-task.ts \
  --source-ids <id1>,<id2> \
  --target-platform reddit

# 2. AI 生成内容
npx tsx scripts/generate-content.ts --task-id <task-id>

# 3. 人工审核
npx tsx scripts/review-publish-content.ts --task-id <task-id>

# 4. 执行发布
npx tsx scripts/execute-publish.ts --task-id <task-id>
```

---

## 🔧 故障排查

### MCP 服务未启动
```bash
# 重启小红书 MCP
cd ~/.openclaw/workspace/bin
screen -dmS xhs-mcp ./xiaohongshu-mcp -headless=true
```

### Cookie 过期
```bash
# 重新登录
cd ~/.openclaw/workspace/bin
./xiaohongshu-login  # 扫码
```

### 数据库问题
```bash
# 重新生成迁移
npx drizzle-kit generate
npx drizzle-kit migrate
```

---

## 📊 常用查询

### 查看统计
```bash
npx tsx scripts/show-overview.ts
```

### 查看可用语料
```bash
npx tsx scripts/show-available-corpus.ts --min-quality 7
```

### 查看待审核内容
```bash
npx tsx scripts/show-pending-review.ts
```

### 查看发布任务状态
```bash
npx tsx scripts/list-publish-tasks.ts --status scheduled
```
