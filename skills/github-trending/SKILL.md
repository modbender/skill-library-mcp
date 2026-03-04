# github-trending - 获取 GitHub 热门项目

自动获取 GitHub Trending 热门项目信息，支持按时间范围筛选。

## 使用方法

### 基础用法
```bash
github-trending                     # 获取今日热门
github-trending daily               # 获取今日热门
github-trending weekly              # 获取本周热门
github-trending monthly             # 获取本月热门
github-trending json                # 输出 JSON 格式
```

### 示例
```bash
# 获取今日热门项目（人类可读格式）
github-trending

# 获取本周热门（JSON 格式，便于程序处理）
github-trending weekly json
```

## 输出格式

默认输出 Markdown 格式的表格，包含：
- 排名
- 项目名称
- 编程语言
- 今日 Stars
- 总 Stars
- 项目简介

## 配置信息

- **数据源**: `https://github.com/trending`
- **更新频率**: 实时（每次调用重新获取）
- **无需认证**: 使用公开页面抓取，无需 API Key

## 故障排除

1. **网络错误**: 检查网络连接
2. **解析失败**: GitHub 页面结构可能已变更
3. **限流**: 频繁调用可能被 GitHub 限流，建议间隔使用

## 相关技能

- `github`: GitHub API 操作（需要认证）
- `send-email`: 发送邮件（可将结果邮件通知）
