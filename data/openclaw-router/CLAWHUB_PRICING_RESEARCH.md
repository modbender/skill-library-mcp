# 📊 ClawHub 定价调研报告

**调研日期：** 2026-03-02  
**调研对象：** ClawHub Skills  
**状态：** ✅ 完成

---

## 🔍 调研结果

### 1. ClawHub 定价模式

**核心发现：ClawHub 上所有技能都是免费的！**

| 发现 | 详情 |
|------|------|
| **付费技能** | 0 个 |
| **免费技能** | 12,970+ 个 |
| **订阅模式** | 无 |
| **一次性付费** | 无 |
| **Freemium 模式** | 无 |

**结论：ClawHub 目前采用完全免费模式**

---

### 2. 热门技能统计

| 技能 | 下载量 | 星级 | 版本 | 作者 |
|------|--------|------|------|------|
| Ontology | 91.2k | 224 | 3 | @oswalpalash |
| self-improving-agent | 81.1k | 958 | 12 | @pskoett |
| Gog | 75.5k | 593 | 1 | @steipete |
| Tavily Web Search | 71.8k | 320 | 1 | @arun-8687 |
| Find Skills | 66.6k | 283 | 1 | @JimLiuxinghai |
| Summarize | 62.8k | 295 | 1 | @steipete |
| Github | 58.8k | 198 | 1 | @steipete |
| Weather | 49.7k | 170 | 1 | @steipete |
| Sonoscli | 43.7k | 29 | 1 | @steipete |

**观察：**
- 大部分技能都是 1 个版本
- 作者 @steipete 贡献了很多热门技能
- 下载量从 25k 到 91k 不等
- 星级从 29 到 958 不等

---

### 3. 技能类型分析

**常见技能类型：**
- CLI 工具封装（Weather, Sonoscli, Gog）
- API 集成（Github, Notion, Slack）
- 自动化脚本（Auto-Updater, self-improving-agent）
- 数据处理（Summarize, Nano Pdf）
- 知识管理（Ontology, ByteRover）

**共同特点：**
- ✅ 开源（MIT 许可证）
- ✅ 免费使用
- ✅ 通过 ClawHub CLI 安装
- ✅ 无付费墙
- ✅ 无订阅限制

---

### 4. ClawHub 商业模式

**推测 ClawHub 的商业模式：**

| 可能性 | 模式 | 说明 |
|--------|------|------|
| **高** | OpenClaw 项目一部分 | ClawHub 是 OpenClaw 生态的免费技能商店 |
| **中** | 通过 Convex 盈利 | 页面底部显示 "Powered by Convex" |
| **低** | 未来引入付费 | 目前无付费迹象，但可能未来引入 |

**证据：**
- 页面底部：`ClawHub · An OpenClaw project · Powered by Convex`
- GitHub 链接：`https://github.com/openclaw/clawhub` (MIT 许可证)
- 作者链接：`https://steipete.me` (Peter Steinberger 的个人项目)

---

## 💡 定价策略建议

### 基于调研结果

**方案 A: 完全免费（推荐 ⭐⭐⭐⭐⭐）**

**理由：**
- ✅ 符合 ClawHub 生态
- ✅ 快速积累用户
- ✅ 提高知名度
- ✅ 建立口碑
- ✅ 后续可通过其他方式变现

**变现方式：**
- 捐赠（GitHub Sponsors, Buy Me a Coffee）
- 企业定制服务
- 私有化部署
- 技术支持服务
- 培训课程

---

**方案 B: 免费 + 付费支持（推荐 ⭐⭐⭐⭐）**

**基础功能：** 免费
- ✅ 基础路由
- ✅ Token 追踪
- ✅ 环境检测
- ✅ 配置向导

**付费支持：** ¥29/月
- ✅ 优先支持（24 小时响应）
- ✅ 远程协助
- ✅ 定制配置
- ✅ 定期更新

**优点：**
- ✅ 保持免费，符合生态
- ✅ 通过服务盈利
- ✅ 用户接受度高

---

**方案 C: 免费 + 企业版（推荐 ⭐⭐⭐）**

**个人版：** 免费
- ✅ 所有核心功能
- ✅ 社区支持

**企业版：** ¥199/月
- ✅ 多用户管理
- ✅ API 访问
- ✅ SLA 保障
- ✅ 专属支持
- ✅ 私有化部署

**优点：**
- ✅ 个人用户免费，积累用户
- ✅ 企业用户付费，获得收入
- ✅ 符合 ClawHub 生态

---

## 🎯 最终建议

### 推荐策略：免费 + 付费服务

**定价配置：**

```json
{
  "pricing": {
    "type": "free",
    "note": "Free and open source (MIT). Paid support available.",
    "support_tiers": {
      "community": {
        "price": 0,
        "response_time": "Best effort",
        "channels": ["GitHub Issues", "Discord"]
      },
      "priority": {
        "price": 29,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "response_time": "24 hours",
        "channels": ["Email", "WeChat"],
        "features": [
          "优先支持",
          "远程协助",
          "定制配置",
          "定期更新"
        ]
      },
      "enterprise": {
        "price": 199,
        "currency": "CNY",
        "billing_cycle": "monthly",
        "response_time": "4 hours",
        "channels": ["专属微信", "电话"],
        "features": [
          "多用户管理",
          "API 访问",
          "SLA 保障",
          "专属支持",
          "私有化部署",
          "定制开发"
        ]
      }
    }
  }
}
```

---

## 📋 需要更新的文件

### 1. clawhub.json

**修改前：**
```json
"pricing": {
  "type": "freemium",
  "free_tier": {...},
  "premium_tier": {...},
  "enterprise_tier": {...}
}
```

**修改后：**
```json
"pricing": {
  "type": "free",
  "license": "MIT",
  "note": "Free and open source. Paid support available.",
  "support_url": "https://github.com/pepsiboy87/openclaw-router/issues"
}
```

---

### 2. SUBMISSION_DESCRIPTION.md

**更新定价部分：**

```markdown
## 💰 定价

**完全免费！** (MIT 许可证)

Router Skill 是开源免费软件，遵循 MIT 许可证。

**付费支持（可选）：**
- 优先支持：¥29/月
- 企业版：¥199/月

所有核心功能完全免费，付费支持用于维持项目开发。
```

---

### 3. PRODUCT_INTRODUCTION.md

**更新定价策略：**

```markdown
## 💰 定价

**免费开源！** (MIT License)

Router Skill 是免费开源软件，任何人都可以：
- ✅ 免费使用所有功能
- ✅ 自由修改源代码
- ✅ 自由分发
- ✅ 用于商业用途

**自愿支持：**
- GitHub Sponsors: [链接]
- Buy Me a Coffee: [链接]
- 微信打赏：[二维码]

**付费服务（可选）：**
- 优先支持：¥29/月
- 企业定制：¥199/月
- 私有化部署：面议

所有收入用于维持项目开发和服务器成本。
```

---

## ✅ 行动计划

### 立即行动（现在）

1. **更新 clawhub.json**
   - 改为 "type": "free"
   - 添加 MIT 许可证说明
   - 移除付费版配置

2. **更新文档**
   - SUBMISSION_DESCRIPTION.md
   - PRODUCT_INTRODUCTION.md
   - PRICING_STRATEGY.md

3. **重新打包**
   - 更新提交包
   - 准备提交

### 后续行动（可选）

1. **设置 GitHub Sponsors**
   - 创建 Sponsor 页面
   - 设置支持等级

2. **设置付费支持**
   - 创建支持页面
   - 设置支付渠道

3. **企业版开发**
   - 多用户管理
   - API 访问
   - SLA 保障

---

## 📊 调研总结

| 项目 | 发现 | 建议 |
|------|------|------|
| **ClawHub 定价** | 全部免费 | 我们也免费 |
| **许可证** | MIT | 保持 MIT |
| **变现方式** | 无（可能通过 Convex） | 付费支持/捐赠 |
| **用户期望** | 免费使用 | 符合期望 |
| **竞争环境** | 12,970+ 免费技能 | 免费更有竞争力 |

---

**结论：采用免费 + 付费支持模式，符合 ClawHub 生态！** ✅

---

_Report Generated: March 2, 2026 01:25 GMT+8_  
_Version: 1.0.0_  
_Status: Research Complete_
