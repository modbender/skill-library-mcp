# 新能源汽车品牌监控 Skill

> 适用于 OpenClaw 2026.2.9+

专为新能源汽车品牌打造的零代码舆情监控解决方案。使用 SerpAPI 专业搜索服务，自动监控小红书、微博、汽车之家、懂车帝、易车网、知乎、百度贴吧、抖音/快手等国内平台的品牌提及。

## 特性

- 🔍 **多平台监控** - 覆盖 9+ 国内主流平台
- 😊 **情感分析** - 自动分析正面/中性/负面情感
- 🚨 **实时警报** - 及时发现负面提及和病毒式传播
- 📊 **趋势分析** - 生成品牌趋势报告
- 🎯 **汽车行业优化** - 识别汽车媒体大V，关注新能源汽车特定问题
- 📱 **飞书推送** - 自动推送监控报告到飞书群
- ⚡ **稳定可靠** - 使用 SerpAPI 专业搜索服务
- 🎭 **官方账号过滤** - 默认排除品牌官方账号，关注第三方真实声音

## 快速开始

### 1. 安装 Skill

```bash
cd ~/.openclaw/workspace/skills/
# 复制或克隆 brand-monitor-skill 到此目录
```

### 2. 安装依赖

```bash
cd brand-monitor-skill
chmod +x install.sh
./install.sh
```

### 3. 获取 SerpAPI Key

访问 [https://serpapi.com/](https://serpapi.com/) 注册并获取免费 API Key

- 免费额度：100 次搜索/月
- 付费计划：$50/月（5000 次搜索）

### 4. 配置环境变量

```bash
# Linux/macOS
export SERPAPI_KEY='your_api_key_here'
echo 'export SERPAPI_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc

# Windows (PowerShell)
$env:SERPAPI_KEY='your_api_key_here'
```

### 5. 配置 Skill

```bash
cp config.example.json config.json
nano config.json
```

最小配置：

```json
{
  "brand_name": "理想汽车",
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的webhook"
}
```

### 6. 测试

```bash
# 测试爬虫（Mock 模式，无需 API Key）
cd crawler
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 5 24 --mock

# 测试真实搜索（需要 API Key，默认排除官方账号）
python search_crawler_serpapi.py "理想汽车" "weibo" 3 24

# 包含官方账号（用于品牌传播分析）
python search_crawler_serpapi.py "理想汽车" "weibo" 3 24 --include-official
```

### 7. 运行监控

```bash
openclaw agent --message "执行品牌监控"
```

## 监控平台

| 平台 | 标识符 | 搜索效果 | 说明 |
|------|--------|---------|------|
| 🔴 微博 | weibo | ✅ 优秀 | 实时热点和传播，数据完整 |
| 🤔 知乎 | zhihu | ✅ 良好 | 深度讨论，结果准确 |
| 📕 小红书 | xiaohongshu | ⚠️ 有限 | 用户体验分享，需改进 |
| 🚗 汽车之家 | autohome | ⚠️ 待测试 | 专业评测和口碑 |
| 🎬 懂车帝 | dongchedi | ⚠️ 待测试 | 视频评测内容 |
| 🚙 易车网 | yiche | ⚠️ 待测试 | 新车资讯 |
| 💬 百度贴吧 | tieba | ⚠️ 待测试 | 车友社区 |
| 🎵 抖音 | douyin | ⚠️ 待测试 | 短视频 |
| 📹 快手 | kuaishou | ⚠️ 待测试 | 短视频 |

**推荐配置**: 使用百度搜索引擎，监控微博和知乎效果最好。

## 核心功能

### 每日监控

搜索各平台的品牌提及，分析情感和影响力，生成结构化报告。

### 实时警报

检测需要关注的负面提及、病毒式传播、危机信号。

### 趋势分析

分析历史数据，生成提及数量、情感变化、平台分布等趋势报告。

## 配置说明

### 完整配置示例

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
  "report_language": "zh-CN",
  
  "industry_specific": {
    "focus_keywords": [
      "续航", "充电", "智能驾驶", "辅助驾驶",
      "电池", "安全", "空间", "舒适性"
    ],
    "kol_min_followers": 100000,
    "media_accounts": [
      "汽车之家", "懂车帝", "易车网",
      "新出行", "电动邦", "42号车库"
    ]
  }
}
```

### 获取飞书 Webhook

1. 打开飞书，进入要接收报告的群聊
2. 点击右上角 "..." → "设置" → "群机器人"
3. 点击 "添加机器人" → "自定义机器人"
4. 设置名称（如：品牌监控）
5. 复制 Webhook 地址

详见：[获取飞书Webhook指南.md](获取飞书Webhook指南.md)

## 成本说明

### SerpAPI 定价

| 计划 | 价格 | 搜索次数 | 适用场景 |
|------|------|---------|---------|
| Free | $0 | 100次/月 | 测试和小规模使用 |
| Developer | $50/月 | 5,000次/月 | 个人和小团队 |
| Production | $130/月 | 15,000次/月 | 中小企业 |

### 使用成本估算

**每次监控消耗：**
- 监控 3 个平台 = 3 次搜索
- 监控 5 个平台 = 5 次搜索

**月度成本：**
- 每天监控 1 次，3 个平台 = 90 次/月（免费额度内 ✅）
- 每天监控 1 次，5 个平台 = 150 次/月（需要付费）
- 每天监控 2 次，3 个平台 = 180 次/月（需要付费）

### Mock 模式（免费测试）

如果只是测试或演示，可以使用 Mock 模式，完全免费且无限制：

```bash
python search_crawler_serpapi.py "理想汽车" "weibo,zhihu" 10 24 --mock
```

## 定时任务

### 使用 cron

```bash
crontab -e
```

添加：

```bash
# 每天早上 9 点执行品牌监控
0 9 * * * cd ~/.openclaw && openclaw agent --message "执行品牌监控" >> /var/log/brand-monitor.log 2>&1
```

### 使用 systemd timer（Linux）

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
3. 等待下月配额重置
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
# 使用百度（推荐，对中文内容友好）
export SERPAPI_ENGINE=baidu

# 使用 Google（默认）
export SERPAPI_ENGINE=google

# 使用 Bing
export SERPAPI_ENGINE=bing
```

**推荐**: 使用百度搜索引擎，对微博、知乎等中文平台效果最好。

### 数据质量说明

SerpAPI 返回的是搜索结果摘要，不是完整的社交媒体数据。爬虫会尽力从摘要中提取：
- ✅ 标题和内容摘要
- ✅ URL 和发布时间
- ✅ 作者信息
- ⚠️ 互动数据（点赞、评论、转发）- 部分提取
- ⚠️ 粉丝数 - 部分提取

对于需要完整数据的场景，建议：
1. 使用 `web_fetch` 工具获取完整页面
2. 或使用平台官方 API（如果有）

详见：[测试结果说明](crawler/测试结果说明.md)

### 官方账号过滤

默认情况下，爬虫会排除品牌官方账号，只保留第三方声音：

```bash
# 默认排除官方账号（推荐用于舆情监控）
python search_crawler_serpapi.py "理想汽车" "weibo" 10 24

# 包含官方账号（用于品牌传播分析）
python search_crawler_serpapi.py "理想汽车" "weibo" 10 24 --include-official
```

**官方账号识别规则**:
- 作者名包含品牌名 + "官方"/"法务"/"客服"等关键词
- URL 包含品牌官方域名

**示例**:
- ✅ 过滤："理想汽车"、"理想汽车官方"、"理想汽车法务部"
- ❌ 保留："李想"（CEO个人）、"汽车评测师"、普通用户

详见：[官方账号过滤说明](crawler/官方账号过滤说明.md)

### 优化配额使用

1. **减少平台数量** - 只监控核心平台（微博、知乎）
2. **降低监控频率** - 每 2 天监控一次
3. **使用 Mock 模式** - 开发测试时使用
4. **批量搜索** - 一次搜索多个关键词

## 文档

- **快速参考：** [快速参考.md](快速参考.md)
- **使用指南：** [使用指南-SerpAPI版.md](使用指南-SerpAPI版.md)
- **SerpAPI 详细文档：** [crawler/SerpAPI使用指南.md](crawler/SerpAPI使用指南.md)
- **飞书配置：** [获取飞书Webhook指南.md](获取飞书Webhook指南.md)

## 要求

- OpenClaw 2026.2.9+
- Python 3.7+
- 已配置 LLM（Claude/GPT/Gemini）
- 飞书账号
- SerpAPI Key（免费或付费）或使用 Mock 模式测试

## 许可证

MIT License

---

**Made with ❤️ for New Energy Vehicle Brands**
