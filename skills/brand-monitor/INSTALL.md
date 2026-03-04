# 安装说明

## 必需文件

OpenClaw skill 只需要以下文件：

```
~/.openclaw/skills/brand-monitor/
├── SKILL.md              # Skill 元数据和文档
├── config.example.json   # 配置示例
└── prompts/              # 提示词目录
    ├── monitor.md        # 每日监控
    ├── alert.md          # 实时警报
    └── analyze-trend.md  # 趋势分析
```

**不需要复制的文件：**
- README.md（仅供参考）
- 部署指南.md（仅供参考）
- 使用指南.md（仅供参考）
- 其他文档文件

## 安装方法

### 方式 A：从 ClawHub 安装（最简单）

```bash
# 1. 安装 ClawHub CLI（如果还没安装）
npm i -g clawhub

# 2. 登录 ClawHub（可选，但推荐）
clawhub login

# 3. 搜索 skill
clawhub search "brand monitor"

# 4. 安装 skill
npx clawhub install brand-monitor

# 5. 创建配置文件
cd ~/.openclaw/skills/brand-monitor
cp config.example.json config.json
nano config.json  # 编辑配置

# 6. 重启 OpenClaw
openclaw restart
```

### 方式 B：使用安装脚本（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/your-repo/brand-monitor-skill.git
cd brand-monitor-skill

# 2. 运行安装脚本
chmod +x install.sh
./install.sh

# 3. 创建配置文件
cd ~/.openclaw/skills/brand-monitor
cp config.example.json config.json
nano config.json  # 编辑配置

# 4. 重启 OpenClaw
openclaw restart
```

### 方式 C：手动安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-repo/brand-monitor-skill.git
cd brand-monitor-skill

# 2. 创建目标目录
mkdir -p ~/.openclaw/skills/brand-monitor/prompts

# 3. 复制必需文件
cp SKILL.md ~/.openclaw/skills/brand-monitor/
cp config.example.json ~/.openclaw/skills/brand-monitor/
cp prompts/monitor.md ~/.openclaw/skills/brand-monitor/prompts/
cp prompts/alert.md ~/.openclaw/skills/brand-monitor/prompts/
cp prompts/analyze-trend.md ~/.openclaw/skills/brand-monitor/prompts/

# 4. 创建配置文件
cd ~/.openclaw/skills/brand-monitor
cp config.example.json config.json
nano config.json  # 编辑配置

# 5. 重启 OpenClaw
openclaw restart
```

## 验证安装

```bash
# 检查文件
ls -la ~/.openclaw/skills/brand-monitor/

# 应该看到：
# SKILL.md
# config.example.json
# config.json (你创建的)
# prompts/
#   monitor.md
#   alert.md
#   analyze-trend.md

# 验证 skill 已加载
openclaw skills list | grep brand-monitor

# 应该看到：
# ✓ brand-monitor v1.1.0
```

## 配置

编辑 `~/.openclaw/skills/brand-monitor/config.json`：

```json
{
  "brand_name": "你的品牌名",
  "brand_aliases": ["车型1", "车型2"],
  "platforms": [
    "xiaohongshu",
    "weibo",
    "autohome",
    "dongchedi",
    "yiche",
    "zhihu",
    "tieba",
    "douyin"
  ],
  "feishu_webhook": "https://open.feishu.cn/open-apis/bot/v2/hook/你的Webhook",
  
  "industry_specific": {
    "focus_keywords": [
      "续航", "充电", "智能驾驶", "电池", "安全"
    ],
    "kol_min_followers": 100000,
    "media_accounts": [
      "汽车之家", "懂车帝", "易车网"
    ]
  }
}
```

## 测试

```bash
# 测试每日监控
openclaw skill run brand-monitor monitor

# 或在 Telegram/WhatsApp 中：
# "执行品牌监控"
```

## 故障排查

### Skill 未加载

```bash
# 检查文件是否存在
ls ~/.openclaw/skills/brand-monitor/SKILL.md

# 重新加载 skills
openclaw skills reload

# 查看日志
tail -f ~/.openclaw/logs/gateway.log
```

### 配置错误

```bash
# 验证 JSON 格式
cat ~/.openclaw/skills/brand-monitor/config.json | jq

# 检查飞书 Webhook
curl -X POST "你的Webhook" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"测试"}}'
```

## 更多文档

安装完成后，查看仓库中的文档文件了解更多：

- `README.md` - 项目概述
- `快速开始.md` - 5分钟快速部署
- `部署指南.md` - 完整部署说明
- `使用指南.md` - 日常使用方法
- `新能源汽车品牌监控-完整指南.md` - 行业定制指南

---

**注意：** 这些文档文件不需要复制到 OpenClaw，它们只是供你参考。
