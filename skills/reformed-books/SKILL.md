---
name: reformed-books
description: 在改革宗书籍乐园 (https.ng) 搜索和下载改革宗/基督教神学书籍。优先返回 PDF 格式。使用场景：当用户想要查找或下载改革宗、加尔文主义、基督教神学相关书籍时触发此技能。
user-invocable: true
metadata: {"openclaw": {"emoji": "📚", "requires": {"bins": ["python"]}}}
---

# 改革宗书籍乐园搜索 (Reformed Books Search)

在 **改革宗书籍乐园** (http://www.https.ng) 搜索基督教神学书籍。

## 方法一：浏览器自动化搜索（推荐）

使用 OpenClaw 的 browser 工具直接搜索：

### 步骤

1. **打开搜索页面**
```
browser action=navigate profile=openclaw targetUrl="http://www.https.ng:1234"
```

2. **输入搜索关键词**（在搜索框 ref=e12 输入）
```
browser action=act profile=openclaw request={"kind":"type","ref":"e12","text":"关键词1 关键词2 pdf"}
```

3. **点击搜索按钮**（ref=e14）
```
browser action=act profile=openclaw request={"kind":"click","ref":"e14"}
```

4. **截图查看结果**
```
browser action=screenshot profile=openclaw
```

### 搜索技巧

- **拆分关键词**: 用空格分隔核心词
  - 《伯克富系统神学》→ `伯克富 系统神学 pdf`
  - 《基督教要义》→ `加尔文 要义 pdf`
  
- **格式优先**: 在关键词后加 `pdf` 优先获取 PDF

- **拼音搜索**: 不确定简繁体时用拼音
  - `bokefu xitong shenxue pdf`

- **避免符号**: 不要输入 `《》()?.` 等标点

## 方法二：命令行脚本

```bash
python "{baseDir}/scripts/search.py" "关键词1 关键词2" [--format pdf|epub|mobi|doc]
```

### 示例

```bash
# 搜索系统神学相关 PDF
python "{baseDir}/scripts/search.py" "系统神学"

# 搜索加尔文基督教要义
python "{baseDir}/scripts/search.py" "加尔文 要义" --format pdf
```

## 网站信息

| 资源 | 链接 |
|------|------|
| 主站 | http://www.https.ng |
| 搜索引擎 | http://www.https.ng:1234 |
| 高级搜索 | http://www.https.ng:5757 |
| 资源导航 | http://www.https.ng:1234/0.html |

## 下载说明

搜索结果页面：
- 点击 **文件名** 直接下载
- 点击表头（名称/大小/日期）可排序
- PDF 格式推荐优先下载

## 常用搜索词

- 系统神学：`系统神学`、`教义`、`神学导论`
- 加尔文：`加尔文`、`基督教要义`、`日内瓦`
- 改革宗信条：`威斯敏斯特`、`海德堡`、`比利时`、`多特`
- 清教徒：`清教徒`、`巴克斯特`、`欧文`、`爱德华兹`
- 讲道：`讲道`、`释经`、`注释`
