# A 股每日精选技能

📈 每日自动获取 A 股新股发行信息和 20 元以下精选股票，通过邮件发送。

## 功能

- ✅ 获取最新新股发行数据（代码、名称、申购日期、发行价、上市日期）
- ✅ 筛选 20 元以下的活跃股票（按成交量排序）
- ✅ 生成精美的 HTML 邮件
- ✅ 支持 SMTP 和系统 mail 命令发送邮件
- ✅ 自动保存数据到本地 JSON 文件

## 安装

```bash
cd skills/astock-daily
npm install
```

依赖：
- nodemailer（可选，用于 SMTP 发送邮件）

## 配置

### 📧 1. SMTP 邮箱配置（阿里云企业邮箱）

编辑 `.env` 文件，填入你的邮箱密码：

```bash
# 编辑文件
vi .env

# 将 YOUR_PASSWORD_HERE 替换为你的邮箱密码
SMTP_CONFIG={"host":"smtp.qiye.aliyun.com","port":465,"secure":true,"user":"8@batype.com","pass":"你的密码","from":"8@batype.com"}
```

**其他邮箱配置参考：**
| 邮箱 | SMTP 服务器 | 端口 | SSL |
|------|------------|------|-----|
| QQ | smtp.qq.com | 587/465 | 推荐 465 |
| Gmail | smtp.gmail.com | 587/465 | 推荐 465 |
| 163 | smtp.163.com | 587/465 | 推荐 465 |
| Outlook | smtp-mail.outlook.com | 587 | 否 |

### ⏰ 2. 定时任务配置

```bash
crontab -e
```

添加（每个交易日 9:30 运行）：
```
30 9 * * 1-5 cd /Users/batype/.openclaw/workspace-work/skills/astock-daily && /opt/homebrew/bin/node index.js >> /tmp/astock-daily.log 2>&1
```

详见 `CONFIG.md` 完整配置指南。

### 3. 系统 mail 命令（备选）

确保系统已配置 mail 命令：
```bash
# macOS 安装
brew install mailutils

# Ubuntu/Debian
sudo apt-get install mailutils
```

## 使用

### 手动运行

```bash
cd skills/astock-daily
node index.js
```

### 定时运行（每天 9 点）

#### 方式一：cron

```bash
crontab -e
```

添加：
```
0 9 * * * cd /Users/batype/.openclaw/workspace-work/skills/astock-daily && node index.js >> /tmp/astock-daily.log 2>&1
```

#### 方式二：OpenClaw Heartbeat

在 `HEARTBEAT.md` 中添加：
```markdown
- 每天 09:00 运行 A 股股票筛选技能
```

然后在主会话中运行：
```bash
node skills/astock-daily/index.js
```

## 输出示例

邮件包含两个部分：

### 1. 新股发行
| 代码 | 名称 | 申购日期 | 发行价 | 上市日期 |
|------|------|----------|--------|----------|
| 301234 | 某某科技 | 2026-02-25 | 15.80 | 2026-03-05 |

### 2. 20 元以下精选股票
| 代码 | 名称 | 现价 | 涨跌幅 | 成交量 |
|------|------|------|--------|--------|
| 000123 | 某某股份 | ¥8.50 | +2.35% | 123,456 |

## 数据源

- 新股数据：东方财富网
- 股票行情：东方财富行情中心

## 注意事项

⚠️ **免责声明**：以上数据仅供参考，不构成投资建议。股市有风险，投资需谨慎。

## 自定义

修改 `index.js` 中的 `CONFIG` 对象：

```javascript
const CONFIG = {
  email: '8@batype.com',     // 目标邮箱
  priceLimit: 20,            // 价格上限（元）
  maxStocks: 50,             // 最多返回的股票数量
};
```

## 故障排除

### 邮件发送失败

1. 检查 SMTP 配置是否正确
2. 确认邮箱已开启 SMTP 服务
3. 如使用 Gmail，需要使用应用专用密码
4. 检查防火墙是否阻止 SMTP 端口

### 数据获取失败

1. 检查网络连接
2. API 可能有访问频率限制，稍后再试
3. 查看控制台错误信息

## 文件结构

```
astock-daily/
├── index.js          # 主程序
├── package.json      # 依赖配置
├── SKILL.md          # 技能说明
├── README.md         # 使用文档
└── data-*.json       # 每日数据备份（自动生成）
```

## 更新日志

- v1.0.0 (2026-02-27): 初始版本
  - 新股发行数据获取
  - 20 元以下股票筛选
  - HTML 邮件发送
  - 本地数据备份
