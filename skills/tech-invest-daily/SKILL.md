---
name: tech-invest-daily
description: 科技行业投资日报生成与推送。当用户要求生成科技投资日报、发送每日投资报告、或cron定时触发日报任务时使用。自动抓取财联社实时新闻、获取涉及上市公司股价、生成深度分析报告并通过飞书一条消息发送完整Markdown报告，同时生成PDF附件。
---

# 科技投资日报 Skill

## 执行流程

### 1. 抓取新闻
```
web_fetch → https://www.cls.cn/telegraph
```
筛选科技相关条目（AI/芯片/半导体/智能/机器人/算力/大模型/融资/上市公司公告）。
重要新闻用 `web_fetch https://www.cls.cn/detail/{id}` 获取详情。

### 2. 获取股价
识别涉及的上市公司，执行：
```bash
python3 ~/.openclaw/workspace/skills/tech-invest-daily/scripts/report.py prices usNVDA,sz000338,...
```
返回 JSON：`{code: {name, price, prev, change, pct, high, low}}`

### 3. 生成完整报告

报告必须包含以下结构，**每个公司单独一节，内容详实不得简化**：

```
# 📊 科技投资日报 · YYYY-MM-DD

---

## 🔴/🟢 公司名 代码 · 涨跌幅%

**今日新闻**
原文摘要（2-3句，说清楚发生了什么）

**深度分析**
- 赛道逻辑：这条新闻为什么重要，行业趋势是什么（3-4句）
- 市场分析：资金动向、估值水位、竞争格局、近期催化剂（3-4句）

**关键财务数据**
现价：XX | 昨收：XX | 涨跌：XX（XX%）| 最高：XX | 最低：XX
PE：XX | 52周区间：XX~XX | 市值：XX

**投资建议**
建仓区间：XX~XX | 目标价：XX | 止损：XX | 持有周期：XX
操作策略：具体说明分几批建仓、什么条件加仓、什么条件止盈止损

---

## 一级市场信号（如有融资新闻）
融资事件 + 对应二级市场联动标的分析

---

## 今日操作清单
| 标的 | 代码 | 现价 | 建议 | 建仓区间 | 目标价 | 止损 |
|------|------|------|------|---------|--------|------|
...

⚠️ 以上内容仅供参考，不构成投资建议，投资有风险。
```

### 4. 飞书发送

**文字报告**：使用 message action=send，将完整 Markdown 放入单个 message 字段，**必须一条消息发完，不得分段**。

**PDF附件**：先将 Markdown 报告写入 `/tmp/tech-invest-YYYYMMDD.md`，再用 md2pdf-weasyprint 转换，最后用飞书 API 上传发送。

**步骤1：生成 PDF**
```bash
bash /root/.openclaw/workspace/skills/md2pdf-weasyprint/scripts/convert-weasyprint.sh \
  /tmp/tech-invest-YYYYMMDD.md \
  /tmp/tech-invest-YYYYMMDD.pdf
```

**步骤2：上传并发送**，用 exec 执行以下 Python 脚本：

```python
import requests, json
from pathlib import Path

cfg = json.load(open("/root/.openclaw/openclaw.json"))["channels"]["feishu"]
app_id, app_secret = cfg["appId"], cfg["appSecret"]
user_id = "ou_159cbb6a3791ff5a98f3a2a4b38e7d4c"
pdf_path = "/tmp/tech-invest-YYYYMMDD.pdf"

token = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": app_id, "app_secret": app_secret}
).json()["tenant_access_token"]

with open(pdf_path, "rb") as f:
    file_key = requests.post(
        "https://open.feishu.cn/open-apis/im/v1/files",
        headers={"Authorization": f"Bearer {token}"},
        data={"file_type": "pdf", "file_name": Path(pdf_path).name},
        files={"file": f}
    ).json()["data"]["file_key"]

requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    json={"receive_id": user_id, "msg_type": "file", "content": json.dumps({"file_key": file_key})}
)
```

## 数据源
| 用途 | 地址 |
|------|------|
| 实时新闻流 | `https://www.cls.cn/telegraph` |
| 新闻详情 | `https://www.cls.cn/detail/{id}` |
| 股价行情 | `http://qt.gtimg.cn/q=代码1,代码2` |

## 股票代码格式
- A股：`sz000338`、`sh603019`
- 美股：`usNVDA`、`usAAPL`
- 港股：`hk00700`、`hk00981`
