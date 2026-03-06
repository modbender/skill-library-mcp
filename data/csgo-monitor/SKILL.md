---
name: CSGO 饰品智能监控 Skill
description: 编辑 config.json 文件：
---

# CSGO 饰品智能监控 Skill

> 基于 CSQAQ API 的 CSGO 饰品价格监控、数据分析和智能预警系统

## 📋 功能特性

### 1. 智能盯盘与自动预警
- ✅ **价格突破预警**：设定目标价格，跌破/涨到自动通知
- ✅ **波幅异常监测**：1小时内价格涨跌超过阈值自动预警
- ✅ **平台价差提醒**：BUFF/YYYP/Steam 平台价差超过3%自动提醒
- ✅ **租赁收益分析**：自动计算日化收益、年化收益和回本周期

### 2. 数据分析与可视化
- ✅ **日报/周报生成**：每日/每周自动生成市场分析报告
- ✅ **价格走势分析**：最高、最低、涨跌幅、波动率计算
- ✅ **均线分析**：MA7、MA30 均线计算
- ✅ **市场情绪分析**：上涨/下跌统计、整体趋势判断

### 3. 自然语言交互
- ✅ **口语化查询**：支持自然语言查询饰品价格
- ✅ **智能摘要**：自动分析市场趋势
- ✅ **上下文对话**：支持多轮对话查询

### 4. 多渠道通知
- ✅ **钉钉通知**：支持 Markdown 格式消息
- ✅ **飞书通知**：支持富文本消息（待实现）
- ✅ **企业微信通知**：支持图文消息（待实现）

## 🚀 快速开始

### 1. 安装依赖

```bash
npm install
```

### 2. 配置 API Token

编辑 `config.json` 文件：

```json
{
  "apiToken": "你的CSQAQ_API_TOKEN"
}
```

### 3. 配置通知渠道

编辑通知配置：

```javascript
const CONFIG = {
  notification: {
    dingtalk: {
      enabled: true,
      webhook: "https://oapi.dingtalk.com/robot/send?access_token=你的TOKEN"
    }
  }
};
```

### 4. 测试功能

```bash
# 测试API连接
node test-api.js

# 测试钉钉通知
node csgo-monitor-dingtalk.js test-dingtalk
```

## 💬 自然语言命令

### 查询饰品价格

```
查询爪子刀现在的价格
```

**返回：**
```
📦 爪子刀（★） | 外表生锈 (战痕累累)
BUFF价格：¥3580.00
YYYP价格：¥3530.00
24h涨跌：-0.14%
7日涨跌：2.34%
BUFF在售：161 件
BUFF在求：27 件
```

### 查询排行榜

```
查询热门饰品排行
```

**返回：**
```
📈 热门饰品排行 TOP 10

1. 爪子刀（★） | 外表生锈 (战痕累累) - ¥3580.00 (-0.14%)
2. AK-47 | 红线 (崭新出厂) - ¥1250.00 (+2.5%)
3. AWP | 龙狙 (略有磨损) - ¥5800.00 (+1.2%)
...
```

### 生成市场简报

```
生成市场简报
```

**返回：**
```
📊 CSGO市场简报

【热门排行TOP5】
1. 爪子刀（★） | 外表生锈 (战痕累累)
   BUFF价格：¥3580.00 | 24h涨跌：-0.14%

2. AK-47 | 红线 (崭新出厂)
   BUFF价格：¥1250.00 | 24h涨跌：+2.5%

【市场总结】
上涨饰品：35 个 (70.0%)
下跌饰品：15 个 (30.0%)
平均涨跌：+1.25%

市场情绪：🟢 看涨
```

### 添加监控饰品

```
监控爪子刀，低于5000提醒我
```

**返回：**
```
✅ 已添加监控

饰品：爪子刀（★） | 外表生锈 (战痕累累）
预警价格：低于 ¥5000.00
监控状态：已启用
```

### 查询监控列表

```
查看我的监控列表
```

**返回：**
```
📋 监控列表

1. 爪子刀（★） | 外表生锈 (战痕累累）
   预警价格：< ¥5000.00
   状态：✅ 监控中

2. AK-47 | 红线 (崭新出厂）
   预警价格：> ¥1200.00
   状态：✅ 监控中
```

## ⚙️ 定时任务配置

### 默认定时任务

```typescript
cron: {
  // 每小时生成市场简报
  '0 * * * *': 'generateMarketReport',
  
  // 每30分钟检查所有监控饰品
  '*/30 * * * *': 'checkAllMonitors',
  
  // 每日早上9点生成日报
  '0 9 * * *': 'generateDailyReport'
}
```

### 自定义定时任务

在 `config.json` 中配置：

```json
{
  "cron": {
    "marketReport": "0 * * * *",
    "monitorCheck": "*/30 * * * *",
    "dailyReport": "0 9 * * *"
  }
}
```

## 📊 数据持久化

### 存储位置

```typescript
// 价格历史数据
openclaw.memory.set('csgo_price_history_7246', data);

// 监控配置
openclaw.memory.set('csgo_monitor_config', monitors);

// 通知记录
openclaw.memory.set('csgo_notification_log', logs);
```

### 数据保留策略

- 价格历史：默认保留 7 天
- 监控配置：永久保留
- 通知日志：默认保留 30 天

## 🔧 高级配置

### 监控参数配置

```typescript
{
  id: '7246',
  name: '爪子刀（★） | 外表生锈 (战痕累累)',
  enabled: true,
  
  // 价格预警
  priceAlert: {
    enabled: true,
    targetPriceLow: 5000,    // 低于5000提醒
    targetPriceHigh: 4000,   // 高于4000提醒
    direction: 'both'        // 双向提醒
  },
  
  // 波幅预警
  volatilityAlert: {
    enabled: true,
    threshold: 5,            // 1小时内涨跌超过5%
    timeWindow: 60          // 时间窗口（分钟）
  },
  
  // 平台价差预警
  priceGapAlert: {
    enabled: true,
    gapPercent: 3,           // 价差超过3%
    checkBuffYYYP: true,     // 检查BUFF vs YYYP
    checkYYYPSteam: true     // 检查YYYP vs Steam
  }
}
```

### 通知配置

```typescript
{
  notification: {
    enabled: true,
    channels: {
      dingtalk: {
        enabled: true,
        webhook: 'https://oapi.dingtalk.com/robot/send?access_token=XXX',
        useMarkdown: true
      },
      feishu: {
        enabled: false,
        webhook: 'https://open.feishu.cn/open-apis/bot/v2/hook/XXX'
      }
    },
    notificationCooldown: 60,  // 同一饰品60分钟内最多通知一次
    quietHours: {
      enabled: false,
      start: '23:00',
      end: '08:00'
    }
  }
}
```

## 📝 配置文件说明

### config.json

```json
{
  "apiToken": "你的CSQAQ_API_TOKEN",
  "baseURL": "https://api.csqaq.com/api/v1",
  "requestDelay": 30000,
  "monitor": {
    "checkInterval": 1800000,
    "volatilityCheckInterval": 600000
  },
  "notification": {
    "enabled": true,
    "channels": {
      "dingtalk": {
        "enabled": true,
        "webhook": ""
      }
    }
  },
  "cron": {
    "marketReport": "0 * * * *",
    "monitorCheck": "*/30 * * * *",
    "dailyReport": "0 9 * * *"
  }
}
```

## 🎯 使用场景

### 场景1：低价捡漏

设定目标价格，系统自动监控并提醒。

```
监控爪子刀，低于5000提醒我
```

### 场景2：套利机会

监控多个平台价差，发现套利机会。

```
监控BUFF和YYYP的价差，超过3%提醒我
```

### 场景3：异常波动预警

捕捉价格异常波动，及时发现"大货"出货。

```
监控爪子刀的波幅，1小时内涨跌超过5%提醒我
```

### 场景4：投资分析

自动计算租赁收益，辅助投资决策。

```
分析爪子刀的租赁收益
```

**返回：**
```
💰 租赁收益分析

饰品：爪子刀（★） | 外表生锈 (战痕累累）
租赁价格：¥2.14/天
饰品价格：¥3580.00

收益计算：
- 日化收益：0.0606%
- 月化收益：1.82%
- 年化收益：22.12%
- 回本周期：1650.0 天

投资建议：租赁收益一般，建议观望
```

## ⚠️ 注意事项

### API 限制

- CSQAQ API 要求 **30秒请求间隔**
- 程序已内置延迟处理
- 避免频繁手动触发检查

### 通知频率限制

- 钉钉机器人每分钟最多发送 **20条消息**
- 建议增加检查间隔或减少监控饰品数量
- 可设置静默时段避免打扰

### 数据清理

- 价格历史默认保留 **7天**
- 通知日志默认保留 **30天**
- 可通过配置调整保留时间

## 🔮 未来计划

- [ ] 飞书通知支持
- [ ] 企业微信通知支持
- [ ] 邮件通知支持
- [ ] K线图生成
- [ ] 自动交易建议
- [ ] Web界面查看
- [ ] 多币种支持
- [ ] 跨平台套利建议

## 📞 问题反馈

如有问题或建议，请通过以下方式联系：
- 在 ClawHub 提交 Issue
- 发送邮件至开发者

## 📄 许可证

MIT License

---

**版本：** 1.0.0  
**更新日期：** 2026-03-01  
**兼容模型：** 混元、GPT-4、Claude 3 等
