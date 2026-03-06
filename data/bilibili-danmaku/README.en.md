# bilibili-danmaku

A practical skill project for **Bilibili danmaku collection + word cloud + sentiment analysis + public-opinion report**.

It supports both `b23.tv` short links and regular `bilibili.com/video/BV...` links, then outputs files that are ready for operations/content review.

---

## Demo Results

### Input / Output Diagram

![Input Output Diagram](bilibili-danmaku/img/输入输出图.jpg)

### Word Cloud Example

![Word Cloud](bilibili-danmaku/img/词云图.jpg)

> The images above are from the project's `img/` folder for ClawHub / GitHub preview.
> Runtime outputs are generated under the `output/` directory.

---

## Features

- ✅ **Danmaku Fetching**: auto resolve `BVID -> CID`, download danmaku XML, export CSV/JSON/TXT
- ✅ **Segmentation & Cleaning**: `jieba` tokenization + noise-word filtering + high-doc-frequency short-token filtering
- ✅ **Word Cloud**: dense Chinese PNG word cloud via `wordcloud`
- ✅ **Sentiment**: `SnowNLP` positive/neutral/negative distribution + average score
- ✅ **Public-Opinion Report**: auto-generated Markdown report for business usage

---

## Project Structure

```text
bilibili-danmaku/
├── SKILL.md
├── README.md
├── README.en.md
├── requirements.txt
├── scripts/
│   ├── ensure_env.sh
│   ├── fetch_danmaku.py
│   ├── fetch.sh
│   ├── analyze_danmaku.py
│   └── analyze.sh
├── references/
│   ├── methodology.md
│   └── stopwords.default.txt
└── output/
```

---

## Requirements

- Python 3.9+
- macOS / Linux recommended
- Network access to public Bilibili endpoints

---

## Quick Start

### 1) Install dependencies

```bash
cd bilibili-danmaku
bash scripts/ensure_env.sh
```

### 2) Fetch danmaku

```bash
python3 scripts/fetch_danmaku.py \
  --url "https://www.bilibili.com/video/BV17JfuBqEqg" \
  --outdir "./output"
```

You can also pass a short link:

```bash
python3 scripts/fetch_danmaku.py --url "https://b23.tv/gO0nMGs" --outdir "./output"
```

Or use BVID + page:

```bash
python3 scripts/fetch_danmaku.py --bvid "BV17JfuBqEqg" --page 1 --outdir "./output"
```

### 3) Run analysis

```bash
bash scripts/analyze.sh \
  "./output/<xxx>_danmaku.csv" \
  "./output/<xxx>_meta.json" \
  "./output" \
  "task_name"
```

Outputs:
- `task_name_top_words.json`
- `task_name_sentiment.json`
- `task_name_wordcloud.png`
- `task_name_report.md`

---

## Cleaning Controls

The analyzer includes practical cleaning steps for danmaku text:

1. Stopword filtering (default + custom)
2. Noise filtering (`哈哈`, `233`, symbols, etc.)
3. Token normalization (alias merge + repeated-character compression)
4. High document-frequency short-token filtering

Example with custom cleaning:

```bash
./.venv/bin/python scripts/analyze_danmaku.py \
  --csv "./output/<xxx>_danmaku.csv" \
  --meta "./output/<xxx>_meta.json" \
  --outdir "./output" \
  --name "task_clean" \
  --extra-stopwords "mom,relative,newyear" \
  --min-token-len 2 \
  --min-word-freq 2 \
  --max-doc-freq-ratio 0.65
```

---

## Sentiment (SnowNLP)

Each danmaku gets a sentiment score in `[0,1]`:
- closer to `1.0` => more positive
- closer to `0.0` => more negative

Default thresholds:
- `>= 0.60` => positive
- `<= 0.40` => negative
- otherwise => neutral

---

## FAQ

**Q: Why do some background words still appear in word cloud?**  
A: Add them via `--extra-stopwords` or edit `references/stopwords.default.txt`, then rerun analysis.

**Q: Is sentiment analysis fully accurate?**  
A: SnowNLP is good for fast trend judgment, but key business decisions should still be manually reviewed.

**Q: Why no danmaku fetched?**  
A: Possible causes: danmaku disabled, API throttling, network/region restrictions, or short-link resolution issues.

---

## Compliance Note

Please follow Bilibili platform rules and local laws.  
This project is for analysis/research of public data only.
