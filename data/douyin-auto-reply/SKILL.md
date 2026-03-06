---
name: douyin-auto-reply
description: 抖音自动回复助手 - 自动回复抖音评论、发送引荐码、引导私信。使用 DouyinBot API 实现评论监控、智能回复和私信引流。适用于抖音创作者、电商卖家、知识付费从业者。
---

# 抖音自动回复助手

自动化抖音评论管理和私信引流工具。

## 功能

1. **自动回复评论** - 监控新评论并自动回复
2. **发送引荐码** - 根据关键词自动发送引荐码/优惠码
3. **引导私信** - 智能引导用户私信转化

## 快速开始

### 配置

在 `config.json` 中设置你的抖音账号和 API 信息：

```json
{
  "douyin_cookie": "your_session_cookie",
  "keywords": {
    "怎么买": "添加微信：xxx 领取优惠",
    "价格": "私信我获取专属优惠",
    "链接": "已私信发送链接"
  },
  "reply_delay": 30,
  "daily_limit": 100
}
```

### 启动

```bash
python scripts/douyin_bot.py start
```

### 查看状态

```bash
python scripts/douyin_bot.py status
```

## 使用场景

- 电商卖家自动回复商品咨询
- 知识付费自动发送课程信息
- 创作者自动引导粉丝私信
- 品牌方自动发送优惠活动

## 脚本说明

### 核心脚本

- `scripts/douyin_bot.py` - 主程序，负责评论监控和自动回复
- `scripts/config_manager.py` - 配置管理工具
- `scripts/analytics.py` - 数据统计和分析

### 配置文件

- `config.json` - 主配置文件
- `keywords.json` - 关键词回复规则（可选独立配置）

## 注意事项

1. 遵守抖音平台规则，避免频繁操作导致封号
2. 设置合理的回复延迟（建议 30-60 秒）
3. 设置每日回复上限（建议 100-200 条）
4. 定期更新抖音 cookie 避免失效

## API 参考

详见 `references/api_docs.md` - 抖音开放平台 API 文档和调用示例

## 故障排查

详见 `references/troubleshooting.md` - 常见问题和解决方案
