# 科研文献汇报系统 - 使用指南

## 快速开始

### 1. 安装

```bash
# 克隆或下载项目
cd research/

# 运行安装脚本
bash install.sh
```

### 2. 配置

编辑 `config.yaml` 文件：

```yaml
# 必须配置的项：
api:
  api_key: "YOUR_API_KEY_HERE"  # 替换为你的硅基流动API Key

feishu:
  target: "YOUR_FEISHU_USER_ID_HERE"  # 替换为你的飞书用户ID
```

**获取API Key：**
1. 访问 https://cloud.siliconflow.cn
2. 注册并充值（最低10元即可）
3. 复制API Key

**获取飞书用户ID：**
1. 在飞书中打开个人资料
2. 查看"用户ID"或"open_id"

### 3. 测试运行

```bash
# 抓取论文
python3 scripts/fetch_papers.py

# 生成摘要
python3 scripts/generate_summary.py

# 推送到飞书
python3 scripts/send_to_feishu.py
```

### 4. 设置定时任务

**方法1：使用OpenClaw cron**

```bash
openclaw cron add literature-report --time '0 9 * * *' --script 'python3 /path/to/research/scripts/fetch_papers.py'
```

**方法2：使用系统cron**

```bash
crontab -e
# 添加以下行（每天早上9点执行）
0 9 * * * cd /path/to/research && python3 scripts/fetch_papers.py && python3 scripts/generate_summary.py
```

---

## 配置说明

### API配置

支持以下LLM提供商：
- **硅基流动**（推荐）：价格便宜，速度快
- **OpenAI**：需要API Key
- **Claude**：需要API Key

```yaml
api:
  provider: "siliconflow"
  api_key: "sk-xxx"
  model: "deepseek-ai/DeepSeek-V3.2"
```

### 研究主题配置

修改 `research.topic` 和 `research.description` 来自定义研究主题：

```yaml
research:
  topic: "医疗设备相关研究"
  description: |
    包括但不限于：
    - 可穿戴医疗设备
    - 药物递送设备
    - 生物传感器
```

### 期刊配置

**默认期刊列表：**

RSS期刊（10个）：
- Nature
- Nature Biotechnology
- Nature Materials
- Nature Communications
- Nature Nanotechnology
- Nature Sustainability
- Nature Reviews Drug Discovery
- Nature Reviews Materials
- Advanced Materials
- Advanced Science

PubMed API期刊（16个）：
- Nature Biomedical Engineering
- Nature Electronics
- Nature Machine Intelligence
- Nature Sensors
- Nature Reviews Bioengineering
- Nature Reviews Electrical Engineering
- Science
- Science Translational Medicine
- Science Advances
- Biomaterials
- Journal of Controlled Release
- ACS Nano
- Biosensors and Bioelectronics
- Nano Letters
- Advanced Healthcare Materials

**添加自定义期刊：**

```yaml
journals:
  custom_journals:
    - name: "Your Journal Name"
      type: "pubmed"
      query: '"Journal Name"[Journal]'
```

### 关键词配置

**添加自定义关键词：**

```yaml
keywords:
  custom_core_keywords:
    - "drug-device"
    - "wearable"
    - "biosensor"
  
  custom_exclude_keywords:
    - "review"
    - "editorial"
```

---

## 高级功能

### 1. 修改推送时间

编辑 `config.yaml`：

```yaml
schedule:
  time: "09:00"  # 改为你想要的时间
```

### 2. 修改推送数量

```yaml
research:
  max_papers: 5  # 改为你想要的数量
```

### 3. 关闭某些期刊

编辑 `scripts/fetch_papers.py`，注释掉不需要的期刊。

### 4. 添加新的推送渠道

目前支持：
- ✅ 飞书
- ⏳ 微信（待开发）
- ⏳ 钉钉（待开发）
- ⏳ 邮件（待开发）

---

## 常见问题

### Q1: API Key无效？

**A:** 请检查：
1. API Key是否正确复制
2. 账户是否有余额
3. API Key是否有权限访问指定模型

### Q2: 飞书推送失败？

**A:** 请检查：
1. 飞书用户ID是否正确
2. 是否有权限发送消息

### Q3: 找不到论文？

**A:** 可能原因：
1. 关键词过于严格，尝试放宽
2. 期刊列表需要调整
3. 最近14天没有符合条件的新论文

### Q4: 如何查看日志？

**A:** 查看日志文件：

```bash
tail -f logs/literature.log
```

---

## 文件结构

```
research/
├── README.md              # 项目说明
├── config.yaml            # 配置文件
├── install.sh             # 安装脚本
├── scripts/               # 脚本目录
│   ├── fetch_papers.py    # 论文抓取
│   ├── ai_filter.py       # AI筛选
│   ├── generate_summary.py # 生成摘要
│   └── send_to_feishu.py  # 推送飞书
├── data/                  # 数据目录
└── logs/                  # 日志目录
```

---

## 联系支持

如有问题，请联系：[你的联系方式]

---

*更新时间: 2026-03-02*