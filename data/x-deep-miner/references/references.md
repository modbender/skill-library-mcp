## X-Deep-Miner 替代方案

由于没有 Twitter API，可以使用以下方法：

### 方法1: Web 搜索 + 手动收集

```bash
# 手动搜索高热度推文链接
# 然后保存到 obsidian-output 目录
```

### 方法2: 浏览器自动化（推荐）

```bash
# 启动浏览器
openclaw browser start

# 打开 Twitter Explore
# https://x.com/explore

# 搜索关键词，筛选高热度内容
```

### 方法3: 使用 Nitter（开源 Twitter 前端）

```bash
# Nitter 实例列表:
# - nitter.net
# - nitter.poast.org
# - nitter.privacydev.net

# 可以尝试抓取这些站点
```

### 当前实现状态

| 功能 | 状态 |
|------|------|
| 定时扫描 | ✅ 已配置 |
| 自动抓取 | ⏳ 需要手动/浏览器 |
| 翻译 | ⏳ 需要 LLM API |

### 手动工作流

1. 每小时运行扫描（目前为模拟）
2. 手动打开 Twitter/X 查找高热度内容
3. 将链接保存到待处理列表
4. 使用浏览器获取内容并翻译

---

## TODO

- [ ] 接入 X API (Twitter API v2) - 需要 API Key
- [x] 基础框架已完成
- [x] 定时任务已配置
- [ ] 浏览器自动化抓取（可选）
- [ ] 接入 LLM 翻译 API（可用 GLM-4-Flash）

---

## 💡 替代方案

由于 X API 需要付费/申请，可以使用：

1. **手动收集**: 发现好文后保存链接
2. **Web 搜索**: 通过搜索引擎找高热度内容
3. **Nitter**: 开源 Twitter 前端（可能被封）
4. **RSS 订阅**: 关注账号的 RSS 输出
