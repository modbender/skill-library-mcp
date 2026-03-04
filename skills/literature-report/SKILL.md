---
name: literature-report
description: 自动科研文献汇报系统。每天自动检索顶级期刊最新论文，AI辅助筛选，生成双语摘要，推送到飞书。使用方法：1. 用户说"设置文献汇报"或"每天推送论文"时激活；2. 用户要求自定义研究主题时激活；3. 用户要求文献检索和推送时激活。
---

# 自动科研文献汇报系统

自动化的科研文献检索与汇报系统，让科研人员轻松追踪最新研究动态。

---

## 🔑 所需凭据

### 必须凭据

**LLM API Key**（必需）
- **获取方式：**
  - OpenAI: https://platform.openai.com
  - Claude: https://console.anthropic.com
  - 硅基流动（推荐）: https://cloud.siliconflow.cn
- **用途：** 语义理解和内容生成
- **费用：** 约0.01元/篇论文
- **安全提示：** 
  - 请勿将API Key提交到公开仓库
  - 确保base_url指向可信的API提供商
  - 论文标题和摘要将发送到配置的LLM服务

### 可选凭据

**飞书用户ID**（可选，用于推送）
- **获取方式：** 在飞书中打开个人资料，查看"用户ID"或"open_id"
- **用途：** 推送每日文献报告
- **安全提示：** 用户ID不会产生费用，但请勿泄露

---

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- LLM API Key（OpenAI / Claude / 硅基流动等）
- 飞书账号（可选，用于推送）

### 2. 安装

```bash
# 安装
bash install.sh

# 验证安装
python3 scripts/verify_install.py
```

### 3. 配置

1. 复制配置文件模板：
```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml`，填入你的配置：

```yaml
# LLM API配置（必须）
api:
  api_key: "YOUR_API_KEY"        # 你的LLM API Key
  base_url: "https://api.siliconflow.cn/v1"  # API基础URL
  model: "deepseek-ai/DeepSeek-V3.2"  # 模型名称

# 推送配置（可选）
feishu:
  enabled: true
  target: "YOUR_USER_ID"          # 你的飞书用户ID

# 研究主题
research:
  topic: "你的研究领域"
  max_papers: 5                    # 每天推送数量
```

### 4. 测试

```bash
# 验证配置
python3 scripts/validate_config.py

# 测试运行
python3 scripts/fetch_papers.py
python3 scripts/generate_summary.py
```

### 5. 运行

```bash
# 手动执行
python3 scripts/fetch_papers.py      # 抓取论文
python3 scripts/generate_summary.py  # 生成摘要
python3 scripts/send_to_feishu.py    # 推送

# 设置定时任务（每天早上9点）
openclaw cron add literature-report --time '0 9 * * *'
```

---

## 🔧 安装验证

运行验证脚本检查环境：

```bash
python3 scripts/verify_install.py
```

**检查项目：**
- ✅ Python版本
- ✅ 依赖库安装
- ✅ 配置文件存在
- ✅ API Key格式
- ✅ 网络连接

---

## ❓ 故障排除

### 问题1: API Key无效

**错误信息：** `API Key无效或账户余额不足`

**解决方案：**
1. 检查API Key是否正确复制
2. 确认账户有余额
3. 确认API Key有权限访问指定模型
4. 确认base_url指向正确的API端点

### 问题2: 找不到论文

**错误信息：** `未找到符合条件的论文`

**解决方案：**
1. 放宽关键词设置
2. 添加更多期刊
3. 调整研究主题描述
4. 检查网络连接

### 问题3: 推送失败

**错误信息：** `飞书推送失败`

**解决方案：**
1. 确认飞书用户ID正确
2. 确认网络连接正常
3. 检查飞书服务状态
4. 注意：当前飞书推送为占位符实现，仅打印消息

---

## 📚 期刊覆盖

### RSS期刊（10个）
Nature, Nature Biotechnology, Nature Materials, Nature Communications, Nature Nanotechnology, Nature Sustainability, Nature Reviews Drug Discovery, Nature Reviews Materials, Advanced Materials, Advanced Science

### PubMed API期刊（16个）
Nature Biomedical Engineering, Nature Electronics, Nature Machine Intelligence, Nature Sensors, Nature Reviews Bioengineering, Science, Science Translational Medicine, Science Advances, Biomaterials, Journal of Controlled Release, ACS Nano, Biosensors and Bioelectronics, Nano Letters, Advanced Healthcare Materials

---

## ⚙️ 自定义配置

### 修改研究主题

```yaml
research:
  topic: "你的研究领域"
  description: |
    研究方向包括：
    - 方向1
    - 方向2
```

### 添加自定义期刊

```yaml
journals:
  custom_journals:
    - name: "Your Journal"
      type: "pubmed"
      query: '"Journal Name"[Journal]'
```

---

## 🔒 安全提示

1. **不要将config.yaml提交到公开仓库**
2. **API Key请妥善保管**
3. **用户ID不要泄露**
4. **建议使用环境变量存储敏感信息**
5. **确保base_url指向可信的API提供商**
6. **论文标题和摘要将发送到配置的LLM服务**

---

## 📞 支持

如有问题或建议，请提交Issue或Pull Request。

---

## 📜 许可证

MIT License

---

*版本: 1.0.4*  
*更新时间: 2026-03-02*