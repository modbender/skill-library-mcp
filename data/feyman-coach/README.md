# 费曼学习法教练 - 安装和配置指南

## 快速开始

### 1. 安装依赖

```bash
# 可选：安装 toml 解析库以支持 .toml 配置文件
pip install tomli

# 可选：安装 win10toast 以获得更好的 Windows 通知体验
pip install win10toast
```

### 2. 配置自动触发

#### Windows (PowerShell)

以管理员身份运行 PowerShell：

```powershell
# 创建每日任务（上午9点执行）
$action = New-ScheduledTaskAction -Execute "python" -Argument "$PWD\skills\feynman-coach\scripts\daily_review.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "FeynmanDailyReview" -Description "每日费曼学习回顾"

# 验证任务是否创建成功
Get-ScheduledTask -TaskName "FeynmanDailyReview"
```

#### macOS/Linux (crontab)

```bash
# 编辑 crontab
crontab -e

# 添加每日9点执行（根据你的实际路径调整）
0 9 * * * cd /path/to/your/note/project && python skills/feynman-coach/scripts/daily_review.py

# 保存并退出
```

#### 使用 GitHub Actions（如果你的笔记在 GitHub 上）

创建 `.github/workflows/feynman-review.yml`：

```yaml
name: Daily Feynman Review

on:
  schedule:
    - cron: '0 9 * * *'  # 每天 UTC 9点
  workflow_dispatch:  # 允许手动触发

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Run Feynman Coach
        run: python skills/feynman-coach/scripts/daily_review.py
      
      - name: Commit and push if changed
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add Z_Utils/feynman-coach/daily-reviews/
          git diff --quiet && git diff --staged --quiet || git commit -m "Add daily Feynman review for $(date +%Y-%m-%d)"
          git push
```

### 3. 配置文件

在项目根目录创建 `.opencode/config.toml`：

```toml
[feynman-coach]
enabled = true
review_time = "09:00"
days_between_reviews = 1
review_scope = "recent_notes"  # 可选：recent_notes, random, tagged, weak_points
review_tags = ["#费曼回顾", "#学习", "#重要"]
max_daily_concepts = 3
output_format = "obsidian"  # obsidian 或 markdown
```

## 使用方法

### 手动触发回顾

```bash
# 基本用法
python skills/feynman-coach/scripts/daily_review.py

# 指定配置文件
python skills/feynman-coach/scripts/daily_review.py --config my-config.json

# 试运行（不保存文件）
python skills/feynman-coach/scripts/daily_review.py --dry-run

# 列出最近可回顾的笔记
python skills/feynman-coach/scripts/daily_review.py --list
```

### 在 Obsidian 中使用

1. 运行脚本生成每日回顾任务
2. 在 Obsidian 中打开生成的文件（位于 `Z_Utils/feynman-coach/daily-reviews/`）
3. 按照任务清单进行费曼学习回顾
4. 记录你的解释和理解自评

### 与 Opencode 集成

在 opencode 中使用：

```
用户：/feynman daily-review
```

或

```
用户：帮我用费曼技巧回顾一下[[机器学习]]
```

## 配置选项说明

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | bool | true | 是否启用自动回顾 |
| `review_time` | string | "09:00" | 每日回顾时间（24小时制） |
| `days_between_reviews` | int | 1 | 每隔几天回顾一次 |
| `review_scope` | string | "recent_notes" | 回顾范围：recent_notes（最近笔记）、random（随机）、tagged（按标签）、weak_points（薄弱点） |
| `review_tags` | list | ["#费曼回顾"] | 如果 review_scope 为 tagged，则回顾带这些标签的笔记 |
| `max_daily_concepts` | int | 3 | 每天最多回顾几个概念 |
| `output_format` | string | "obsidian" | 输出格式：obsidian 或 markdown |

## 文件结构

```
skills/feynman-coach/
├── SKILL.md                    # Skill 核心文档
├── README.md                   # 本文件
├── scripts/
│   └── daily_review.py        # 每日回顾脚本
└── examples/                   # 使用示例（待添加）

Z_Utils/feynman-coach/          # 运行时生成的数据
├── daily-reviews/             # 每日回顾任务
│   ├── review-2025-02-13.md
│   └── review-2025-02-14.md
└── history/                   # 回顾历史记录
    ├── 2025-02-13-决策树算法.json
    └── 2025-02-14-神经网络.json
```

## 故障排除

### 1. 脚本无法运行

**问题**：`python: can't open file 'daily_review.py'`

**解决**：确保你在项目根目录运行脚本，或使用完整路径：
```bash
python "D:\lhj\Note\Note\skills\feynman-coach\scripts\daily_review.py"
```

### 2. 没有生成回顾任务

**问题**：运行脚本后没有看到生成的文件

**解决**：
- 检查是否有最近的笔记（7天内修改的）
- 尝试使用 `--list` 参数查看可回顾的笔记
- 检查 `Z_Utils/feynman-coach/daily-reviews/` 目录是否存在

### 3. 定时任务没有触发

**问题**：配置了定时任务但没有自动运行

**解决**：
- Windows：检查任务计划程序中的任务状态
- macOS/Linux：检查 crontab 是否正确配置，运行 `crontab -l` 查看

### 4. 通知没有显示

**问题**：运行完成但没有收到通知

**解决**：
- Windows：确保在图形界面环境下运行（不是在纯 SSH 会话中）
- 这是可选功能，不影响核心功能

## 进阶用法

### 自定义问题模板

编辑 `daily_review.py` 中的 `generate_review_questions` 方法，添加你自己的问题模板。

### 集成 Anki

（待实现）将复习卡片导出到 Anki：

```bash
python skills/feynman-coach/scripts/export_anki.py [[决策树算法]]
```

### 生成学习报告

（待实现）查看学习统计：

```bash
python skills/feynman-coach/scripts/generate_report.py --month 2025-02
```

## 更新日志

- v1.0.0 (2025-02-13)
  - 初始版本
  - 支持基本的费曼学习回顾流程
  - 支持自动定时触发
  - 支持多种回顾模式

## 贡献

欢迎提交 Issue 和 PR！

## 许可证

MIT License
