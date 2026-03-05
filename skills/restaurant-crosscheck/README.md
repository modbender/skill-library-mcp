# Restaurant Review Cross-Check Skill

交叉验证小红书和大众点评的餐厅推荐数据，提供可信的餐厅推荐。

## 功能特点

- 🔍 **多平台数据源**：同时查询大众点评和小红书
- 🔗 **智能匹配**：使用模糊匹配算法识别同一餐厅
- 📊 **交叉验证**：分析两个平台的一致性
- 🏆 **推荐评分**：综合多维度计算推荐指数 (0-10)
- ⚠️ **风险提示**：自动标注评价差异较大的餐厅

## 快速开始

### 安装依赖

```bash
cd scripts
pip install -r requirements.txt
```

### 基本使用

```bash
python crosscheck.py "上海静安区" "日式料理"
```

### 输出示例

```
📍 上海静安区 日式料理 餐厅推荐

============================================================

1. 银座寿司
   🏆 推荐指数: 8.7/10
   ⭐ 大众点评: 4.8⭐ (2300评价)
   💬 小红书: 4.6⭐ (342赞/89收藏)
   📍 地址: 上海静安区南京西路123号
   💰 人均: ¥200-300
   ✅ 一致性: 高 (0.75)

   📊 平台对比:
   - 大众点评标签: 美味, 环境好, 服务热情
   - 小红书热词: 好吃, 环境, 值得, 正宗

2. [更多餐厅...]
```

## 配置选项

编辑 `scripts/config.py` 来自定义：

```python
DEFAULT_THRESHOLDS = {
    "min_rating": 4.0,              # 最低评分
    "min_dianping_reviews": 50,     # 大众点评最少评价数
    "min_xhs_notes": 20,            # 小红书最少笔记数
    "max_results": 10,              # 最多显示结果数
    "similarity_threshold": 0.7     # 匹配相似度阈值
}
```

## 工作原理

### 1. 数据收集
- **大众点评**：抓取餐厅评分、评价数、价格区间
- **小红书**：抓取相关笔记，提取餐厅名称和互动数据

### 2. 智能匹配
使用模糊匹配算法 (Levenshtein distance) 匹配两个平台的餐厅：
- 处理名称变体（如"银座寿司" vs "银座寿司静安店"）
- 地址辅助验证
- 可配置相似度阈值

### 3. 一致性分析
计算平台间的一致性评分：
- 评分相关性 (0-1)
- 互动量验证 (0-1)
- 情感一致性 (0-1)

### 4. 推荐评分
综合多个维度计算最终推荐指数：
```
推荐指数 = (大众点评评分 × 40%) +
          (小红书互动归一化 × 30%) +
          (一致性评分 × 30%)
```

输出 0-10 分，>8.0 分为高推荐

## 评分解读

| 推荐指数 | 含义 | 一致性 |
|---------|------|--------|
| 8.0-10 | 强烈推荐 | 高 |
| 6.5-8.0 | 推荐 | 中-高 |
| 5.0-6.5 | 可考虑 | 中 |
| <5.0 | 需谨慎 | 低 |

⚠️ **一致性低** 的餐厅建议进一步了解后再决定

## 限制说明

### 数据源限制
- **大众点评**：无公开 API，需爬虫获取
- **小红书**：无公开 API，需爬虫 + Cookie 认证

### 技术限制
- 需要住宅代理 IP 以避免封禁
- 请求频率受限（大众点评 2 秒/次，小红书 3 秒/次）
- 动态内容需要 Selenium/Playwright 渲染

### 法律合规
⚠️ **重要**：本技能仅供个人研究使用，不得用于商业用途。使用前请阅读 [API 限制文档](references/api_limitations.md)

## 目录结构

```
restaurant-review-crosscheck/
├── SKILL.md                          # 技能说明（供 AI 读取）
├── README.md                         # 使用说明（供人类阅读）
├── scripts/
│   ├── config.py                     # 配置文件
│   ├── crosscheck.py                 # 主程序
│   ├── fetch_dianping.py             # 大众点评数据获取
│   ├── fetch_xiaohongshu.py          # 小红书数据获取
│   ├── match_restaurants.py          # 餐厅匹配算法
│   └── requirements.txt              # 依赖包
└── references/
    ├── data_schema.md                # 数据结构说明
    ├── sentiment_analysis.md         # 情感分析说明
    └── api_limitations.md            # API 限制说明
```

## 高级功能

### 自定义搜索

```python
from scripts.config import DEFAULT_THRESHOLDS
from scripts.crosscheck import RestaurantCrossChecker

# 自定义配置
config = DEFAULT_THRESHOLDS.copy()
config['min_rating'] = 4.5
config['max_results'] = 5

checker = RestaurantCrossChecker(config)
results = checker.search("北京朝阳区", "火锅")
output = checker.format_output(results, "北京朝阳区", "火锅")
print(output)
```

### 调试模式

启用详细日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 故障排除

### 问题 1：大众点评返回空结果
**原因**：IP 被封禁或请求过快
**解决**：
- 降低请求频率（增加 `dianping_delay`）
- 使用住宅代理 IP

### 问题 2：小红书无法获取数据
**原因**：Cookie 过期
**解决**：
- 重新获取小红书 Cookie
- 更新 `fetch_xiaohongshu.py` 中的认证信息

### 问题 3：匹配效果差
**原因**：相似度阈值不合适
**解决**：
- 调整 `similarity_threshold` (0.6-0.8)
- 检查餐厅名称是否需要标准化

## 未来改进

- [ ] 支持更多平台（美团、饿了么）
- [ ] 机器学习情感分析模型
- [ ] 地图可视化展示
- [ ] 价格趋势分析
- [ ] 自动化定时监控
- [ ] 移动端适配

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可

MIT License

## 免责声明

本技能仅供教育和研究目的。使用者需确保遵守相关法律法规和平台服务条款。作者不对滥用行为负责。

---

**最后更新**: 2026-02-09
