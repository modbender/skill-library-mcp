---
name: xiaohongshu-auto
description: 小红书自动化技能，自动发布笔记和管理内容
---

# 小红书自动发帖技能

🤖 **技能名称**: xiaohongshu-auto  
📝 **用途**: 自动登录小红书、发布笔记、管理内容  
🔐 **认证**: 需要手动登录一次（保存 Cookie）

---

## ⚠️ 路径说明

**技能路径**: `/root/.openclaw/workspace/skills/xiaohongshu-auto/`

### macOS / Linux 示例
```bash
cd /root/.openclaw/workspace/skills/xiaohongshu-auto
```

### Windows 示例
```powershell
cd C:\Users\用户名\.openclaw\workspace\skills\xiaohongshu-auto
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 确保 Chrome 已安装
google-chrome --version

# 安装必要的 Python 库（如果需要）
pip install selenium webdriver-manager
```

### 2. 配置浏览器

**方式 A：Chrome 扩展 Relay（推荐）**

1. 在 Chrome 中安装 **OpenClaw Browser Relay** 扩展
   - Chrome Web Store 搜索 "OpenClaw Browser Relay"
   - 或访问：https://chrome.google.com/webstore

2. 手动登录小红书
   - 打开 https://www.xiaohongshu.com
   - 扫码或账号密码登录
   - 保持登录状态

3. 点击扩展图标，启用 Relay 模式

**方式 B：独立浏览器**

```bash
# 启动 OpenClaw 管理的浏览器
openclaw browser start --profile openclaw
```

### 3. 使用技能

#### 发布笔记
```bash
# 调用技能发布笔记
openclaw skill xiaohongshu-auto publish \
  --title "笔记标题" \
  --content "笔记内容" \
  --image "/path/to/image.jpg"
```

#### 查看笔记列表
```bash
openclaw skill xiaohongshu-auto list
```

#### 分析数据
```bash
openclaw skill xiaohongshu-auto analytics
```

---

## 📋 配置文件

创建 `config.json`：

```json
{
  "account": {
    "loginMethod": "qrcode",
    "sessionFile": "~/.openclaw/workspace/skills/xiaohongshu-auto/session.json"
  },
  "browser": {
    "profile": "chrome",
    "headless": false,
    "userDataDir": "~/.openclaw/workspace/skills/xiaohongshu-auto/chrome-profile"
  },
  "posting": {
    "dailyLimit": 5,
    "randomDelay": true,
    "delayRange": [300, 1800],
    "autoHashtags": true,
    "imageQuality": 0.9
  },
  "analytics": {
    "trackViews": true,
    "trackLikes": true,
    "trackComments": true,
    "reportInterval": "daily"
  }
}
```

---

## 🔧 使用方式

### 基础用法

**发布图文笔记**：
```bash
openclaw skill xiaohongshu-auto publish \
  --title "今天分享一个超好用的 AI 助手" \
  --content "最近发现了一个超厉害的工具..." \
  --images "image1.jpg,image2.jpg,image3.jpg"
```

**发布视频笔记**：
```bash
openclaw skill xiaohongshu-auto publish \
  --title "Vlog | 我的一天" \
  --content "记录美好的一天" \
  --video "video.mp4"
```

### 高级用法

**定时发布**：
```bash
# 设置定时任务（每天早上 9 点发布）
0 9 * * * openclaw skill xiaohongshu-auto publish --scheduled
```

**批量发布**：
```bash
# 从 CSV 文件批量发布
openclaw skill xiaohongshu-auto batch-publish \
  --csv "posts.csv" \
  --image-dir "./images"
```

**数据分析**：
```bash
# 获取最近 7 天数据
openclaw skill xiaohongshu-auto analytics --days 7

# 导出报告
openclaw skill xiaohongshu-auto analytics --export report.pdf
```

---

## 📁 目录结构

```
xiaohongshu-auto/
├── SKILL.md              # 技能说明（本文件）
├── USAGE.md              # 详细使用文档
├── config.json           # 配置文件
├── config.example.json   # 配置示例
├── session.json          # 登录会话（自动生成）
├── scripts/
│   ├── publish.py        # 发布脚本
│   ├── login.py          # 登录脚本
│   └── analytics.py      # 数据分析脚本
├── templates/
│   ├── post-template.md  # 笔记模板
│   └── hashtag-list.txt  # 标签库
└── logs/
    └── activity.log      # 活动日志
```

---

## ⚠️ 注意事项

### 平台规则
1. **发布频率**：每天不超过 5 篇，避免被判定为营销号
2. **内容质量**：确保原创，不要抄袭
3. **图片要求**：分辨率不低于 1080x1440
4. **敏感词**：避免广告法禁用词

### 安全建议
1. **人工审核**：发布前人工确认内容
2. **随机延迟**：设置 5-30 分钟随机间隔
3. **账号保护**：不要频繁切换设备
4. **数据备份**：定期导出笔记数据

### 风险提醒
- ❌ 过度自动化可能导致限流
- ❌ 低质量内容会被降权
- ❌ 违规内容可能封号
- ⚠️ 本工具仅供学习研究，请遵守平台规则

---

## 🛠️ 故障排查

### 无法登录
```bash
# 清除会话重新登录
rm ~/.openclaw/workspace/skills/xiaohongshu-auto/session.json
openclaw skill xiaohongshu-auto login
```

### 浏览器启动失败
```bash
# 检查 Chrome 安装
google-chrome --version

# 重启浏览器服务
openclaw browser stop
openclaw browser start
```

### 发布失败
```bash
# 查看日志
tail -f ~/.openclaw/workspace/skills/xiaohongshu-auto/logs/activity.log

# 检查网络连接
curl -I https://www.xiaohongshu.com
```

---

## 📊 收益模式

### 流量分成
- 小红书创作者中心
- 笔记浏览量收益
- 约 ¥0.01-0.05/千次浏览

### 带货佣金
- 商品链接转化
- 佣金比例 5-30%

### 品牌合作
- 推广笔记
- 单篇 ¥500-5000+

### 引流变现
- 导流到私域
- 知识付费/咨询服务

---

## 📖 参考文档

- [小红书创作者中心](https://creator.xiaohongshu.com/)
- [小红书社区规范](https://www.xiaohongshu.com/community-guidelines)
- [OpenClaw 浏览器文档](https://docs.openclaw.ai/browser)

---

*最后更新：2026-02-27*
*版本：1.0.0*
