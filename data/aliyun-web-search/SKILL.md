---
name: aliyun-web-search
description: 阿里云实时搜索 | Aliyun Real-time Web Search with Quark Engine
metadata: {"clawdbot":{"emoji":"🔍","requires":{"env":["ALIYUN_SEARCH_API_KEY","ALIYUN_SEARCH_HOST"]}}}
---

# Aliyun Web Search | 阿里云实时搜索

> 📢 **Note**: Aliyun's service management is a bit chaotic - this skill helps you configure it step by step!
> 
> 📢 **吐槽**：阿里云的服务管理确实有点混乱，这个技能帮你理清配置步骤！

Real-time web search using Aliyun Open Search Platform (AI Gateway) with Quark search engine. Returns latest, accurate Chinese search results.

使用阿里云开放搜索平台（AI 网关）进行实时网页搜索，支持夸克搜索引擎，返回最新、最准确的中文搜索结果。

---

## 🎯 Features | 功能特性

- ✅ **Real-time Search** - Returns latest web content, not model training data
- ✅ **Chinese Optimized** - Quark search engine, high-quality Chinese results
- ✅ **Auto Query Rewrite** - Intelligently optimizes search queries
- ✅ **Flexible Configuration** - Customizable result count, time range, etc.
- ✅ **Conversation History Support** - Can search with context

- ✅ **实时搜索** - 返回最新网页内容，不是模型训练数据
- ✅ **中文优化** - 夸克搜索引擎，中文结果质量高
- ✅ **自动重写** - 智能优化搜索查询
- ✅ **灵活配置** - 支持自定义结果数量、时间范围等
- ✅ **支持对话历史** - 可结合上下文进行搜索

---

## 📋 Configuration Steps | 配置步骤

### Step 1: Activate Aliyun Information Query Service | 开通阿里云信息查询服务

1. Open **Aliyun AI Gateway Console** | 打开 **阿里云 AI 网关控制台**：
   ```
   https://apigw.console.aliyun.com/#/cn-hangzhou/ai-gateway
   ```

2. Select your instance region in the top menu (e.g., North China 2-Beijing, East China 1-Hangzhou)
   
   在顶部菜单栏选择你的实例所在地域（如：华北 2-北京、华东 1-杭州等）

3. Click your instance ID to enter the details page
   
   单击你的实例 ID 进入详情页

4. Left navigation → **Model API** → Click target API name
   
   左侧导航栏 → **Model API** → 点击目标 API 名称

5. Click **Strategies & Plugins** tab
   
   点击 **策略与插件** 标签

6. Find **Web Search** switch and turn it on
   
   找到 **联网搜索** 开关，打开它

7. First time use shows "Not Activated", click **Go to Activate**
   
   首次使用会显示 "未开通"，点击 **前往开通**

8. After activation, click **Activate Validation**, status changes to "Trial"
   
   开通后点击 **开通校验**，状态变为 "试用中"

> 💡 **Free Trial**: 15 days free, 1000 requests/day, 5 QPS limit
> 
> 💡 **免费试用**：15 天免费，1000 次/天，5 QPS 性能限制
> 
> 📖 **Formal Activation**: https://help.aliyun.com/document_detail/2869993.html

---

### Step 2: Get API Key | 获取 API Key

1. Open **API Key Management Console** | 打开 **凭证管理控制台**：
   ```
   https://ipaas.console.aliyun.com/api-key
   ```

2. Click **Create API Key**
   
   点击 **创建 API Key**

3. Copy your API Key (format: `OS-xxxxxxxxxxxxxxxx`)
   
   复制你的 API Key（格式：`OS-xxxxxxxxxxxxxxxx`）

> ⚠️ **Security**: API Key is shown only once, save it immediately!
> 
> ⚠️ **安全提示**：API Key 只在第一次显示，记得马上复制保存！

---

### Step 3: Configure Service URL by Region | 配置服务地址（按地区选择）

**Select service address based on your instance region:**

**根据你的实例所在地域，选择对应的服务地址：**

| Region | Service URL Example |
|--------|---------------------|
| North China 2-Beijing (华北 2-北京) | `http://default-21rb.platform-cn-beijing.opensearch.aliyuncs.com` |
| East China 1-Hangzhou (华东 1-杭州) | `http://default-21rb.platform-cn-hangzhou.opensearch.aliyuncs.com` |
| South China 1-Shenzhen (华南 1-深圳) | `http://default-21rb.platform-cn-shenzhen.opensearch.aliyuncs.com` |
| Other Regions (其他地域) | Check your instance details page in AI Gateway Console |

> 💡 **How to Find Service URL** | **如何查看服务地址**：
> 1. Open AI Gateway Console | 打开 AI 网关控制台
> 2. Select your region | 选择你的地域
> 3. Click instance ID | 点击实例 ID
> 4. Find your URL in "Access Information" or "Service Address" tab | 在 "接入信息" 或 "服务地址" 标签页找到你的专属地址

---

### Step 4: Configure in OpenClaw | 配置到 OpenClaw

Add to `openclaw.json`:

在 `openclaw.json` 中添加：

```json
{
  "env": {
    "ALIYUN_SEARCH_API_KEY": "YOUR_API_KEY",
    "ALIYUN_SEARCH_HOST": "YOUR_SERVICE_URL"
  },
  "skills": {
    "entries": {
      "aliyun-web-search": {
        "enabled": true,
        "env": {
          "ALIYUN_SEARCH_API_KEY": "YOUR_API_KEY",
          "ALIYUN_SEARCH_HOST": "YOUR_SERVICE_URL"
        }
      }
    }
  }
}
```

**Example (Beijing Region) | 示例（北京地区）**：
```json
{
  "env": {
    "ALIYUN_SEARCH_API_KEY": "OS-0fw5937ch3u5eegd",
    "ALIYUN_SEARCH_HOST": "http://default-21rb.platform-cn-beijing.opensearch.aliyuncs.com"
  }
}
```

Restart gateway after configuration | 配置完成后重启网关：
```bash
openclaw gateway restart
```

---

## 🔧 Advanced Configuration | 高级配置

Configure in AI Gateway Console | 在 AI 网关控制台配置：

- **Result Count** | 返回结果数量：1-10 (default 5 | 默认 5)
- **Timeout** | 超时时间：default 3000ms | 默认 3000ms
- **Time Range** | 查询时间范围：1 day / 1 week / 1 month / 1 year / unlimited
- **Industry Filter** | 行业筛选：Finance / Law / Medical / Internet / Tax / News
- **Content Type** | 内容类型：Snippet (default) / Full Text
- **Default Language** | 默认语言：Chinese / English
- **Show Citations** | 输出引用来源：Yes/No

---

## 💡 Usage Examples | 使用示例

### In Conversation | 在对话中使用

```
User: Search for latest AI news | 帮我搜索最新的 AI 新闻
Assistant: [Using aliyun-web-search]
```

### Manual Script Call | 手动调用脚本

**PowerShell**:
```powershell
$env:ALIYUN_SEARCH_API_KEY="OS-xxxxxxxx"
$env:ALIYUN_SEARCH_HOST="http://default-21rb.platform-cn-beijing.opensearch.aliyuncs.com"
cd skills/aliyun-web-search
.\scripts\search.ps1 "AI news" 5
```

**Bash**:
```bash
export ALIYUN_SEARCH_API_KEY="OS-xxxxxxxx"
export ALIYUN_SEARCH_HOST="http://default-21rb.platform-cn-beijing.opensearch.aliyuncs.com"
cd skills/aliyun-web-search
./scripts/search.sh "AI news" 5
```

---

## 🔍 Search Result Example | 搜索结果示例

```json
{
  "result": {
    "search_result": [
      {
        "title": "AI Development Trends 2026 | 2026 年 AI 发展趋势",
        "link": "https://example.com/ai-trends-2026",
        "snippet": "AI field will see major breakthroughs in 2026... | 2026 年 AI 领域将迎来重大突破...",
        "publishedTime": "2026-02-20T10:00:00+08:00"
      }
    ]
  }
}
```

---

## ⚠️ FAQ | 常见问题

### Q: Search returns garbled text? | 搜索返回乱码？
**A**: Check if API Key is correct, ensure service is activated and in "Trial" or "Formal" status
   检查 API Key 是否正确，确保服务已开通并处于 "试用中" 或 "正式" 状态

### Q: Where to find service URL? | 服务地址在哪里找？
**A**: AI Gateway Console → Select region → Instance details → Access information/Service address
   AI 网关控制台 → 选择地域 → 实例详情 → 接入信息/服务地址

### Q: Free quota exhausted? | 免费额度用完了怎么办？
**A**: Apply for formal activation | 申请正式开通：https://help.aliyun.com/document_detail/2869993.html

### Q: Search results not relevant? | 搜索结果不相关？
**A**: Enable "Intent Recognition" in console to let AI optimize search queries
   在控制台开启 "意图识别"，让 AI 自动优化搜索查询

---

## 📚 Related Documentation | 相关文档

- [Aliyun AI Gateway Console | 阿里云 AI 网关控制台](https://apigw.console.aliyun.com/#/cn-hangzhou/ai-gateway)
- [API Key Management | 凭证管理](https://ipaas.console.aliyun.com/api-key)
- [Web Search Official Docs | 联网搜索官方文档](https://help.aliyun.com/zh/api-gateway/ai-gateway/user-guide/networked-search)
- [Formal Activation | 正式开通流程](https://help.aliyun.com/document_detail/2869993.html)

---

## 🔒 Security Notice | 安全提示

- ⚠️ **Do NOT upload API Key to public repositories** | 不要将 API Key 上传到公开仓库
- ⚠️ **Do NOT share your service URL publicly** | 不要在公开场合分享你的服务地址
- ✅ Use environment variables or encrypted config files | 使用环境变量或加密配置文件存储敏感信息
- ✅ Rotate API Keys regularly | 定期轮换 API Key

---

*Created by 猪王 (Pig King) 🐷 | Based on Aliyun Open Search Platform | 基于阿里云开放搜索平台*
