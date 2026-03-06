---
name: creator-intel-v5
description: |
  创造者情报 V5 - 工程师视角技术情报聚合器
  
  严禁 VC 商业化话术，只关注底层技术实现。
  服务对象：硬科技工程师、极客产品经理、技术研究者。
  
  核心选品标准（按优先级）：
  1. 🥇 GitHub 开源项目与霸榜（新模型、新硬件图纸、开发工具库）
  2. 🥈 硬核技术原理解析（MoE、稀疏注意力、流匹配、新架构）
  3. 🥉 极客硬件与创新交互（ESP32、树莓派、Kickstarter 创意硬件）
  
  摘要必须包含：
  - 至少 2 个技术名词或具体参数
  - 架构/算法/材料/性能指标
  - 严禁："拓展商业化"、"规模化部署"、"生态布局" 等公关套话
  
  信源分布：
  - 国际：GitHub、IEEE、arXiv、Kickstarter、Hackaday（Tavily API 搜索）
  - 国内：机器之心、量子位、开源中国 RSS
  
  使用场景：
  - "生成今日技术情报"
  - "有什么硬核技术新闻"
  - "GitHub 上有啥新东西"
  
  输出格式：
  ```
  [YYYY-MM-DD] 创造者情报 🌍
  
  📦 [技术实体 + 动作 + 性能参数](URL)
  摘要：架构细节；关键性能指标；应用场景
  
  ⚛️ [技术实体 + 动作 + 性能参数](URL)
  摘要：...
  ```
---

# Creator Intel V5 - 创造者情报

## 使用方法

### 1. 手动生成今日技术情报

```bash
cd /path/to/creator-intel-v5 && python3 scripts/generate_intel.py
```

### 2. 设置定时任务

```bash
# 每天早上 9:00 自动推送
openclaw cron add \
  --name "creator-intel-morning" \
  --schedule "0 9 * * *" \
  --command "python3 /path/to/creator-intel-v5/scripts/generate_intel.py" \
  --channel feishu
```

## 配置说明

### Tavily API 密钥

在 `scripts/generate_intel.py` 中设置：
```python
TAVILY_API_KEY = "your-tavily-api-key"
```

### 搜索关键词

编辑 `ENGINEER_QUERIES` 列表自定义搜索方向：
- GitHub 开源机器人项目
- 医疗 AI 架构突破
- 极客硬件原型
- 算法与芯片架构

## 选品逻辑

### 🟢 最高权重（优先抓取）

1. **开源项目与 GitHub 霸榜**
   - 新底层模型（带代码）
   - 开源硬件图纸（PCB、机械结构）
   - 开发工具库（SDK、框架）

2. **硬核技术原理解析**
   - 新架构：MoE、稀疏注意力、流匹配
   - 新材料：柔性电子、神经形态芯片
   - 新算法：扩散模型替代方案、Transformer 变体

3. **极客产品与创新交互**
   - Kickstarter 创意硬件
   - ESP32/树莓派项目
   - 墨水屏、NFC 等小众应用

### 🔴 降权/警惕（过滤）

- 纯融资通稿（无技术细节）
- 纯政策审批（FDA/CE 但无原理）
- 空泛战略发布（"拓展商业化"、"生态布局"）
- 消费电子产品（手机、家电发布会）

## 摘要撰写规范

### 必须包含

- ✅ 架构/算法/材料细节
- ✅ 具体参数（tokens/s、Hz、GB/s、参数量）
- ✅ 解决的问题或应用场景

### 严禁使用

- ❌ "推动规模化部署"
- ❌ "拓展商业化落地"
- ❌ "生态布局"
- ❌ "战略发布"
- ❌ "赛道龙头"

### 示例对比

**❌ VC 视角（已废弃）：**
> 星海图获 10 亿元融资，从开发者市场向生产力市场拓展商业化落地

**✅ 工程师视角（V5 标准）：**
> 星海图灵巧手开源数据集，发布百万级操作数据集与强化学习训练框架，基于 Transformer 架构的动作预测模型在 6 自由度抓取任务中达到 85% 成功率，支持 Sim2Real 迁移

## Emoji 分类

| Emoji | 类别 | 示例 |
|-------|------|------|
| 📦 | GitHub 开源 | 开源机器人、工具库 |
| ⚛️ | 架构/算法 | MoE、稀疏注意力、扩散模型 |
| 🛠️ | 极客硬件 | ESP32、树莓派、NVMe |
| 🔬 | 手术机器人 | 医疗机器人、精密控制 |
| 🧠 | 脑机接口 | BCI、神经信号处理 |
| 💡 | 其他技术 | 创新应用 |

## 数据存储

- 历史记录：`~/.openclaw/creator-intel/history.json`
- 自动去重：基于 URL
- 保留数量：最近 500 条

## 依赖

```bash
pip install feedparser requests
```

## License

MIT
