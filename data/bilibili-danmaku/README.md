# bilibili-danmaku

一个用于 **B站视频弹幕抓取 + 词云 + 情感分析 + 舆情分析** 的实用 Skill 项目。  
支持从 `b23.tv` 短链或 `bilibili.com/video/BV...` 链接抓取弹幕，并输出可直接用于运营研判的结果。

---

## 示例效果

### 输入 / 输出示意图

![输入输出图](bilibili-danmaku/img/输入输出图.jpg)

### 词云图示例

![词云图](bilibili-danmaku/img/词云图.jpg)

> 上述图片来自本项目 `img/` 目录，用于 ClawHub / GitHub 页面展示。
> 实际运行时，词云与报告会输出到 `output/` 目录。

---

## 功能特性

- ✅ **弹幕抓取**：自动解析 `BVID -> CID`，下载弹幕 XML 并导出 CSV/JSON/TXT
- ✅ **分词与清洗**：`jieba` 分词 + 干扰词过滤 + 高频短词干扰剔除
- ✅ **词云生成**：`wordcloud` 生成高密度中文词云 PNG
- ✅ **情感分析**：`SnowNLP` 输出正/中/负分布与平均情绪分
- ✅ **舆情报告**：自动生成 Markdown 报告（可直接发给业务方）

---

## 目录结构

```text
bilibili-danmaku/
├── SKILL.md
├── README.md
├── requirements.txt
├── scripts/
│   ├── ensure_env.sh          # 安装依赖到 .venv
│   ├── fetch_danmaku.py       # 抓取弹幕并导出
│   ├── fetch.sh               # 抓取快捷脚本
│   ├── analyze_danmaku.py     # 分词清洗+词云+情感+舆情
│   └── analyze.sh             # 分析快捷脚本
├── references/
│   ├── methodology.md         # 方法说明
│   └── stopwords.default.txt  # 默认干扰词表
└── output/                    # 运行产物目录（运行后生成）
```

---

## 环境要求

- Python 3.9+
- macOS / Linux（推荐）
- 可访问 B站公开接口

> 说明：
> - 抓取脚本使用标准库，不强依赖 requests。
> - 分析脚本依赖 `jieba/snownlp/wordcloud/pillow/numpy`，通过 `ensure_env.sh` 一键安装。

---

## 快速开始

### 1) 安装依赖

```bash
cd bilibili-danmaku
bash scripts/ensure_env.sh
```

### 2) 抓取弹幕

#### 方式A：视频链接（推荐）
```bash
python3 scripts/fetch_danmaku.py \
  --url "https://www.bilibili.com/video/BV17JfuBqEqg" \
  --outdir "./output"
```

#### 方式B：b23短链（先自动解短链再抓）
```bash
python3 scripts/fetch_danmaku.py \
  --url "https://b23.tv/gO0nMGs" \
  --outdir "./output"
```

#### 方式C：指定 BVID + 分P
```bash
python3 scripts/fetch_danmaku.py \
  --bvid "BV17JfuBqEqg" \
  --page 1 \
  --outdir "./output"
```

抓取完成后会产出：
- `*_danmaku.csv`
- `*_danmaku.json`
- `*_corpus.txt`
- `*_meta.json`

### 3) 运行分析

```bash
bash scripts/analyze.sh \
  "./output/<xxx>_danmaku.csv" \
  "./output/<xxx>_meta.json" \
  "./output" \
  "task_name"
```

默认产出：
- `task_name_top_words.json`
- `task_name_sentiment.json`
- `task_name_wordcloud.png`
- `task_name_report.md`

---

## 数据清洗说明（重点）

项目内置了针对弹幕场景的数据清洗逻辑：

1. **停用词过滤**（默认词表 + 可扩展词表）
2. **噪声词过滤**（如：哈哈哈、233、666、纯符号等）
3. **token 规范化**（别名合并、重复字符压缩）
4. **高文档频率短词剔除**（过滤“到处都出现但信息量低”的短词）

### 自定义清洗参数

```bash
./.venv/bin/python scripts/analyze_danmaku.py \
  --csv "./output/<xxx>_danmaku.csv" \
  --meta "./output/<xxx>_meta.json" \
  --outdir "./output" \
  --name "task_clean" \
  --extra-stopwords "妈妈,亲戚,那边,这边" \
  --min-token-len 2 \
  --min-word-freq 2 \
  --max-doc-freq-ratio 0.65
```

可选参数：
- `--stopwords-file`：追加停用词文件（可重复传）
- `--extra-stopwords`：临时追加停用词（逗号分隔）
- `--disable-docfreq-clean`：关闭高文档频率剔除

---

## 情感分析说明（SnowNLP）

- 每条弹幕得到一个 `0~1` 情感分：
  - 越接近 1 越偏正向
  - 越接近 0 越偏负向
- 默认阈值：
  - `>= 0.60` → positive
  - `<= 0.40` → negative
  - 其余 → neutral

可通过参数调整：
- `--pos-threshold`
- `--neg-threshold`

---

## 示例：一条命令跑完整链路

```bash
# 1) 抓取
python3 scripts/fetch_danmaku.py --url "https://b23.tv/hWaCnlL" --outdir ./output

# 2) 分析（假设抓取生成了对应 csv/meta）
bash scripts/analyze.sh "./output/<csv文件>" "./output/<meta文件>" ./output demo
```

---

## 常见问题（FAQ）

### Q1: 词云里为什么还有背景词？
A: 把这些词加入 `--extra-stopwords` 或 `references/stopwords.default.txt`，再重跑分析。

### Q2: 情感分析准确吗？
A: SnowNLP 适合中文快速研判，不等同于人工标注模型。用于运营趋势判断足够，关键决策建议人工复核。

### Q3: 为什么抓不到弹幕？
A: 可能是视频关闭弹幕、接口限流、网络区域限制或短链解析失败。可改用 `--bvid` 重试。

### Q4: 可以批量分析多个视频吗？
A: 可以，建议外层写批处理脚本循环调用 `fetch_danmaku.py + analyze_danmaku.py`。

---

## 结果解读建议（运营视角）

优先看三件事：
1. **情绪结构**：正/中/负占比是否异常
2. **高频关注点**：热词是否偏离内容定位
3. **负向样本**：负向代表弹幕里是否有集中抱怨点

如果你在做内容复盘，建议将多个视频结果并排对比（同类题材、同账号不同发布时间）。

---

## 免责声明

- 请遵守 B站平台规则与相关法律法规。
- 本项目仅用于公开数据分析与研究，不用于违规抓取和滥用。

---

## License

使用 MIT
