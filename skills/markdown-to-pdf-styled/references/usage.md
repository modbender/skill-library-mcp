# md-to-pdf 使用手册

## 1) 安装依赖（Ubuntu）

```bash
apt-get update
apt-get install -y pandoc wkhtmltopdf
```

## 2) 基本转换

```bash
bash scripts/md2pdf.sh ./doc.md
```

输出：`./doc.pdf`

## 3) 指定输出路径

```bash
bash scripts/md2pdf.sh ./doc.md ./out/result.pdf
```

## 4) 选择模板

```bash
bash scripts/md2pdf.sh ./doc.md --style clean
bash scripts/md2pdf.sh ./doc.md --style modern
bash scripts/md2pdf.sh ./doc.md --style paper
```

## 5) 自定义 CSS

```bash
bash scripts/md2pdf.sh ./doc.md ./doc.pdf --style /abs/path/custom.css
```

## 6) 常见问题

- 提示 `pandoc: command not found`：未安装 pandoc。
- 提示 `wkhtmltopdf: command not found`：未安装 wkhtmltopdf。
- 中文字体显示一般：在 CSS 中将字体改为系统已有中文字体（如 PingFang SC / Noto Sans CJK SC）。
