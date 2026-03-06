# 品牌监控 Skill 使用指南（SerpAPI 版）

## 概述

本 Skill 使用 SerpAPI 专业搜索服务进行品牌监控，提供稳定可靠的搜索功能。

## 快速开始

### 1. 安装 Skill

```bash
cd ~/.openclaw/workspace/skills/
# 复制或克隆 brand-monitor-skill 到此目录
```

### 2. 运行安装脚本

```bash
cd brand-monitor-skill
chmod +x install.sh
./install.sh
```

安装脚本会自动：
- 检查 Python 环境
- 安装依赖（requests, beautifulsoup4, lxml）
- 创建配置文件
- 测试爬虫（Mock 模式）
- 检查 SerpAPI 配置

### 3. 获取 SerpAPI Key

**访问：** https://serpapi.com/

1. 点击 "Sign Up" 注册
2. 验证邮箱
3. 进入 Dashboard
4. 复制 API Key

**免费额度：** 100 次搜索/月

### 4. 配置环境变量

```bash
# Linux/macOS
export SERPAPI_KEY='your_api_key_here'

# 永久设置
echo 'export SERPAPI_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

```cmd
# Windows (CMD)
set SERPAPI_KEY=your_api_key_here
```

```powershell
# Windows (PowerShell)
$env:SERPAPI_KEY='your_api_key_here'
```

### 5. 配置 Skill

编辑 `config.json`：

```bash
nano config.json
```

最小配置：

```json
{
  "brand_name": "理想汽车",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook"
}
```

完整配置：

```json
{
  "brand_name": "理想汽车",
  "brand_aliases": ["理想L9", "理想L8", "Li Auto"],
  "exclude_keywords": ["招聘", "代理", "二手车"],
  "platforms": [
    "weibo",
    "xiaohongshu",
    "zhihu",
    "autohome",
    "dongchedi"
  ],
  "monitor_hours": 24,
  "min_engagement": 10,
  "negative_threshold": -0.5,
  "viral_threshold": 5000,
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook",
  
  "industry_specific": {
    "focus_keywords": ["续航", "充电", "智驾", "电池"],
    "kol_min_followers": 100000
  }
}
```

### 6. 测试爬虫

```bash
cd crawler

# 测试 Mock 模式（无需 API Key）
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 5 24 --mock

# 测试真实搜索（需要 API Key）
python search_crawler_serpapi.py "理想汽车" "weibo" 3 24
```

### 7. 运行监控

```bash
openclaw agent --message "执行品牌监控"
```

## 使用方式

### 手动执行

```bash
# 执行每日监控
openclaw agent --message "执行品牌监控"

# 检查实时警报
openclaw agent --message "检查品牌警报"

# 分析趋势
openclaw agent --message "分析过去 7 天的品牌趋势"
```

### 定时任务

**使用 cron：**

```bash
crontab -e
```

添加：

```bash
# 每天早上 9 点执行品牌监控
0 9 * * * cd ~/.openclaw && openclaw agent --message "执行品牌监控" >> /var/log/brand-monitor.log 2>&1
```

**使用 systemd timer（Linux）：**

创建服务文件 `/etc/systemd/system/brand-monitor.service`：

```ini
[Unit]
Description=Brand Monitor Service

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/home/your-username/.openclaw
Environment="SERPAPI_KEY=your_api_key"
ExecStart=/usr/local/bin/openclaw agent --message "执行品牌监控"
```

创建定时器 `/etc/systemd/system/brand-monitor.timer`：

```ini
[Unit]
Description=Brand Monitor Timer

[Timer]
OnCalendar=daily
OnCalendar=09:00
Persistent=true

[Install]
WantedBy=timers.target
```

启用：

```bash
sudo systemctl enable brand-monitor.timer
sudo systemctl start brand-monitor.timer
```

## 支持的平台

| 平台 | 标识符 | 说明 |
|------|--------|------|
| 微博 | weibo | 新浪微博 |
| 小红书 | xiaohongshu | 小红书笔记 |
| 知乎 | zhihu | 知乎问答 |
| 汽车之家 | autohome | 汽车之家论坛 |
| 懂车帝 | dongchedi | 懂车帝评测 |
| 易车网 | yiche | 易车网资讯 |
| 百度贴吧 | tieba | 百度贴吧 |
| 抖音 | douyin | 抖音短视频 |
| 快手 | kuaishou | 快手短视频 |

## 成本管理

### 免费额度使用建议

**100 次/月的分配：**

| 监控频率 | 平台数 | 月消耗 | 是否可行 |
|---------|--------|--------|---------|
| 每天 1 次 | 3 | 90 | ✅ 可行 |
| 每天 1 次 | 5 | 150 | ❌ 超额 |
| 每 2 天 1 次 | 5 | 75 | ✅ 可行 |
| 每周 1 次 | 8 | 32 | ✅ 可行 |

### 优化策略

1. **减少平台数量**
   ```json
   "platforms": ["weibo", "xiaohongshu", "zhihu"]
   ```

2. **降低监控频率**
   ```bash
   # 每 2 天监控一次
   0 9 */2 * * openclaw agent --message "执行品牌监控"
   ```

3. **使用 Mock 模式测试**
   ```bash
   # 开发测试时使用 Mock 模式，不消耗配额
   python search_crawler_serpapi.py "理想汽车" "weibo" 5 24 --mock
   ```

4. **批量搜索关键词**
   ```bash
   # 一次搜索多个关键词
   python search_crawler_serpapi.py "理想汽车 OR 理想L9" "weibo" 20 24
   ```

### 升级到付费计划

如果免费额度不够用，可以升级：

| 计划 | 价格 | 搜索次数 | 适用场景 |
|------|------|---------|---------|
| Developer | $50/月 | 5,000次 | 个人和小团队 |
| Production | $130/月 | 15,000次 | 中小企业 |
| Enterprise | 定制 | 定制 | 大型企业 |

访问 https://serpapi.com/pricing 了解详情

## 监控报告

### 报告内容

每次监控会生成包含以下内容的报告：

1. **总览统计**
   - 总提及数
   - 情感分布（正面/中性/负面）
   - 整体情感评价

2. **热门提及 Top 5**
   - 标题和内容
   - 作者信息（认证状态、粉丝数）
   - 互动数据（点赞、评论、分享）
   - 情感分析

3. **平台分布**
   - 各平台提及数量和占比

4. **警报信息**
   - 负面提及
   - 病毒式传播
   - 危机信号

5. **关键洞察和建议**

### 报告推送

报告会自动推送到配置的飞书群。

## 故障排查

### 问题 1：API Key 未设置

**错误信息：**
```
❌ 错误: 未设置 SERPAPI_KEY 环境变量
```

**解决方法：**
```bash
export SERPAPI_KEY='your_api_key'
```

### 问题 2：配额用完

**错误信息：**
```
SerpAPI 请求失败: 403 Forbidden
```

**解决方法：**
1. 检查配额：https://serpapi.com/dashboard
2. 升级到付费计划
3. 等待下月重置
4. 使用 Mock 模式：`--mock`

### 问题 3：搜索无结果

**可能原因：**
- 关键词太具体
- 时间范围太短
- 平台没有相关内容

**解决方法：**
```bash
# 扩大时间范围
python search_crawler_serpapi.py "理想汽车" "weibo" 20 168

# 使用更通用的关键词
python search_crawler_serpapi.py "理想" "weibo" 20 24
```

### 问题 4：Skill 未加载

**检查：**
```bash
openclaw skills list | grep brand-monitor
```

**解决：**
```bash
# 重启 gateway
openclaw gateway restart
```

## 高级配置

### 选择搜索引擎

```bash
# 使用 Google（默认，推荐）
export SERPAPI_ENGINE=google

# 使用百度（适合国内内容）
export SERPAPI_ENGINE=baidu

# 使用 Bing
export SERPAPI_ENGINE=bing
```

### 自定义平台列表

在 `config.json` 中：

```json
{
  "platforms": [
    "weibo",
    "xiaohongshu",
    "zhihu"
  ]
}
```

### 调整监控参数

```json
{
  "monitor_hours": 24,        // 监控时间范围
  "min_engagement": 10,       // 最小互动数
  "negative_threshold": -0.5, // 负面阈值
  "viral_threshold": 5000     // 病毒式传播阈值
}
```

## 最佳实践

1. ✅ 开发测试时使用 Mock 模式
2. ✅ 生产环境使用真实 API
3. ✅ 定期检查配额使用情况
4. ✅ 只监控重点平台
5. ✅ 合理设置监控频率
6. ✅ 及时处理警报
7. ✅ 定期查看趋势报告

## 相关文档

- **详细使用：** `crawler/SerpAPI使用指南.md`
- **快速参考：** `快速参考.md`
- **项目总结：** `项目状态总结.md`
- **方案对比：** `方案对比-API vs 爬虫.md`

## 获取帮助

- **SerpAPI 文档：** https://serpapi.com/docs
- **SerpAPI 支持：** support@serpapi.com
- **Dashboard：** https://serpapi.com/dashboard

---

**祝使用愉快！** 🎉
