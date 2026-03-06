# X 运营自动化 Skill v4.0

完整的 X/Twitter 运营自动化解决方案。

## 特性

- ✅ 完整 Onboarding 流程
- ✅ Persona 学习（抓取100条推文）
- ✅ 人类行为模拟（随机延迟、滚动模式）
- ✅ 记忆系统（评论历史、用户事实、避免矛盾）
- ✅ 定时任务（每日热点总结）
- ✅ 智能评论生成（语言匹配、风格应用）

## 快速开始

### 1. 安装

```bash
cd ~/.agents/skills
git clone [repo-url] x-engagement
```

### 2. 首次运行

```
用户: 刷推
Bot: 开始 Onboarding...
```

### 3. 后续使用

```
用户: 刷推半小时
Bot: 读取配置... 开始刷推...
```

## 文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 主入口 |
| [docs/onboarding.md](docs/onboarding.md) | Onboarding 流程 |
| [docs/human-behavior.md](docs/human-behavior.md) | 人类行为模拟 |
| [docs/memory-system.md](docs/memory-system.md) | 记忆系统 |
| [docs/cron-jobs.md](docs/cron-jobs.md) | 定时任务 |
| [docs/comment-generation.md](docs/comment-generation.md) | 评论生成 |

## 目录结构

```
x-engagement/
├── SKILL.md                    # 主入口
├── README.md                   # 说明文档
├── docs/                       # 详细文档
│   ├── onboarding.md
│   ├── human-behavior.md
│   ├── memory-system.md
│   ├── cron-jobs.md
│   └── comment-generation.md
├── templates/                  # 模板文件
│   ├── persona.md
│   ├── config.json
│   └── daily-log.md
└── scripts/                    # 脚本
    ├── setup-cron.sh
    ├── check-cron.sh
    └── cleanup-memory.sh
```

## 核心功能

### 1. Onboarding

首次运行自动引导：
- 浏览器连接 + 登录检查
- 选择 Persona（自己或其他账号）
- 学习 Persona（抓取100条）
- 配置刷推习惯

### 2. 人类行为模拟

模拟真人行为：
- 随机延迟（正态分布）
- 人类滚动模式（小/中/大）
- 鼠标轨迹模拟
- 频率限制
- 评论间隔（3-6分钟）

### 3. 记忆系统

三层记忆：
- 评论历史（避免重复、矛盾）
- 用户事实（记住用户说过的话）
- 每日日志（活动记录）

### 4. 定时任务

- 每日热点总结（10:00）
- 记忆清理（每周日 03:00）
- 刷推提醒（用户自定义）

**刷推提醒支持：**
- 固定时间："早上9点、下午3点、晚上9点"
- 随机时间："每天3次，随机时间"
- 随机范围："每天随机2-4次"
- 工作日/周末："工作日晚上8点，周末随机3次"

### 5. 智能评论

- 语言匹配（中文/英文）
- Persona 风格应用
- 历史检查（避免矛盾）
- 用户事实检查

## 使用示例

### 示例 1：正常评论

```
推文: "今天市场大涨！"
评论: "确实，趋势起来了。"
```

### 示例 2：避免矛盾

```
用户昨天说: "出去吃饭了"
推文: "最近都在家做饭"
评论: "做饭不错，偶尔出去换换口味也好"（避免说"你都在家"）
```

### 示例 3：跳过政治

```
推文: "特朗普最新政策"
结果: 跳过（政治内容）
```

## 配置

### 刷推习惯

```json
{
  "forYou": {
    "followNewAccounts": true,
    "followCriteria": ["views_1m+", "crypto", "ai"]
  },
  "following": {
    "commentWithin": "2h",
    "avoidTopics": ["politics", "war"]
  }
}
```

### 频率限制

| 操作 | 每小时上限 |
|------|-----------|
| 关注 | 10 |
| 点赞 | 30 |
| 评论 | 10 |

## 故障排除

### 浏览器连接失败

```
1. 打开 Chrome
2. 打开 x.com
3. 点击 OpenClaw 扩展图标（确保 badge 绿色 ON）
```

### 评论被检测为机器人

```
1. 增加评论间隔（3-6分钟）
2. 降低频率（每小时 < 10条）
3. 增加随机延迟
```

### 记忆系统不工作

```
1. 检查目录是否存在: memory/daily/hotspots/
2. 检查文件权限
3. 运行: ./scripts/check-cron.sh
```

## 更新日志

### v4.0.0 (2026-03-02)
- 结构化设计
- 记忆系统（评论历史、用户事实）
- 定时任务（每日热点）
- 人类行为模拟规范
- 智能评论生成

### v3.0.0 (2026-03-01)
- 完整 Onboarding 流程
- Persona 学习

### v2.0.0 (2026-02-28)
- 人类行为模拟
- 频率限制

### v1.0.0 (2026-02-27)
- 初始版本

## 许可证

MIT

---

*版本: 4.0.0*
*更新: 2026-03-02*
