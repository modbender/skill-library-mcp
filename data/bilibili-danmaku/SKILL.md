---
name: bilibili-danmaku
description: Fetch and analyze Bilibili video danmaku (bullet comments) from a Bilibili video URL/BVID, then output keyword frequency, SVG word cloud, sentiment distribution, and a public-opinion report. Use when the user asks to analyze B站弹幕, generate 词云图, run 情感分析, or produce 舆情分析 for one or more Bilibili videos.
---

# Bilibili Danmaku

## Quick Start

0) 安装依赖（首次必做）：
- `bash {baseDir}/scripts/ensure_env.sh`

1) 抓取弹幕：
- `python3 {baseDir}/scripts/fetch_danmaku.py --url "<bilibili_video_url>" --outdir "{baseDir}/output"`

2) 运行分析（jieba + 清洗 + SnowNLP + 高密度词云PNG）：
- `bash {baseDir}/scripts/analyze.sh "<danmaku_csv_path>" "<meta_json_path>" "{baseDir}/output" "<task_name>"`

3) 可选：增加自定义清洗词
- `--stopwords-file`：传入自定义停用词文件（可重复）
- `--extra-stopwords`：临时追加停用词（逗号分隔）
- 示例：
  - `"{baseDir}/.venv/bin/python" {baseDir}/scripts/analyze_danmaku.py --csv "<csv>" --meta "<meta>" --outdir "{baseDir}/output" --name task_clean --extra-stopwords "妈妈,亲戚,这边"`

## Workflow

### 1. 获取输入
- 输入支持：
  - B站视频 URL（推荐）
  - `--bvid` + `--page`（分P视频）
  - `--cid`（高级模式，直接指定分P）

### 2. 抓取弹幕
- 用 `fetch_danmaku.py` 自动完成：
  - `bvid -> cid` 解析
  - 下载 `comment.bilibili.com/{cid}.xml`
  - 导出：`*_danmaku.csv` / `*_danmaku.json` / `*_corpus.txt` / `*_meta.json`

### 3. 分析与产出
- 用 `analyze_danmaku.py` 对 CSV 弹幕文本执行：
  - `jieba` 分词关键词统计（JSON）
  - 数据清洗（停用词、噪声词、超高文档频率短词剔除）
  - `SnowNLP` 情感分布统计（JSON）
  - 高密度词云图（PNG）
  - 舆情报告（Markdown）

## Output Files

默认输出目录：`{baseDir}/output`

主要产物：
- `*_top_words.json`
- `*_sentiment.json`
- `*_wordcloud.png`
- `*_report.md`

## Recommended Usage Notes

- 先抓“单视频单P”验证链路，再做批量任务。
- SnowNLP 情感分析适合快速运营判断；高风险场景仍需人工复核。
- 若用户要“更稳健结论”，优先扩大样本（多P/多视频）再汇总。

## Resources

- `scripts/ensure_env.sh`：安装依赖（jieba/snownlp/wordcloud）
- `requirements.txt`：Python依赖清单
- `scripts/fetch_danmaku.py`：抓取与导出弹幕
- `scripts/analyze_danmaku.py`：jieba词频、清洗、SnowNLP情感、舆情报告
- `scripts/fetch.sh` / `scripts/analyze.sh`：便捷命令封装
- `references/stopwords.default.txt`：默认干扰词词表
- `references/methodology.md`：方法与局限说明
