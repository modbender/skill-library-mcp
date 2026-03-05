# 🎨 WeChat Image Generator

> 为公众号文章生成精美配图，零 Token 消耗，自动截图

## ✨ 特性

- 🎯 **三种模板**：封面图、对比图、数据图
- 🚀 **零依赖**：纯 Python + 预制 HTML 模板
- 💰 **零成本**：Token 消耗 ~650 vs DALL-E ~1000-5000
- ⚡ **快速**：生成 HTML <1 秒
- 🎨 **精美**：专业级排版和配色

## 🎯 使用场景

适用于以下需求：
- 公众号文章封面图
- 技术文章对比示意图
- 数据可视化图表
- 社交媒体配图

## 🚀 快速开始

### 1. 封面图（Cover）

```bash
python3 scripts/generate.py cover \
  --title "我的第一个开源项目" \
  --subtitle "Token 成本降低 90%" \
  --output output/cover.png
```

**效果**：
- 尺寸：1200×675（16:9）
- 渐变背景（紫色系）
- 标题 + 分隔线 + 副标题

### 2. 对比图（Comparison）

```bash
python3 scripts/generate.py compare \
  --left "# Markdown\n**Bold** text" \
  --right "🎨 精美 HTML" \
  --label "1 秒转换" \
  --output output/compare.png
```

**效果**：
- 左右对比布局
- 中间箭头 + 标签
- 白色卡片 + 阴影

### 3. 数据图（Chart）

```bash
python3 scripts/generate.py chart \
  --data "Token消耗:8000,650|生成耗时:20,1" \
  --labels "AI生成,预制模板" \
  --output output/chart.png
```

**效果**：
- 柱状图对比
- 支持多组数据
- 自动计算比例

## 📦 工作流程

```bash
# 1. 生成 HTML 文件
python3 scripts/generate.py <type> [options]

# 2. 启动本地服务器
cd output && python3 -m http.server 8765

# 3. 浏览器打开并截图
open http://localhost:8765/<filename>.html
```

## 🎨 输出效果

生成的 HTML 页面包含：
- 固定尺寸（1200×675，16:9）
- 精心设计的配色和排版
- 适合社交媒体分享

## 💰 Token 成本分析

| 操作 | Token 消耗 |
|------|-----------|
| 读取 SKILL.md | ~500（首次） |
| 执行脚本 | ~100 |
| 生成 HTML | 0 |
| **总计** | **~600** |

**vs AI 生成图片：**
- DALL-E/Midjourney: 1000-5000 tokens
- 节省超过 **80%** 的成本

## 📁 文件结构

```
wechat-image-generator/
├── SKILL.md              # 技能定义
├── README.md             # 使用文档（本文件）
├── scripts/
│   ├── generate.py       # 核心生成脚本
│   └── serve.py          # HTTP 服务器
├── assets/
│   ├── cover.html        # 封面图模板
│   ├── compare.html      # 对比图模板
│   └── chart.html        # 数据图模板
└── output/               # 输出目录
```

## 🔧 进阶用法

### 自定义样式

编辑 `assets/*.html` 中的 `<style>` 标签，修改：
- 背景颜色/渐变
- 字体大小/字重
- 间距/圆角

### 批量生成

```bash
# 生成多张封面
for title in "标题1" "标题2" "标题3"; do
  python3 scripts/generate.py cover \
    --title "$title" \
    --subtitle "副标题" \
    --output "output/${title}.png"
done
```

### 集成到工作流

```bash
# 生成 + 自动打开浏览器
python3 scripts/generate.py cover \
  --title "标题" \
  --subtitle "副标题" \
  --output output/cover.png

cd output && python3 -m http.server 8765 &
sleep 1 && open http://localhost:8765/cover.html
```

## 🤝 反馈与贡献

- 📮 公众号：**后端工程师的 AI 进化之路**
- 🐙 GitHub: [github.com/jingyu525](https://github.com/jingyu525)
- 🌟 即刻: [okjk.co/GaCNdY](https://okjk.co/GaCNdY)
- 💬 Issues: 欢迎反馈问题和建议

## 📝 许可证

MIT License - 自由使用和修改

---

**Made with ❤️ by @jingyu525**  
*如果这个工具帮到了你，考虑在 ClawHub 给它一个 ⭐*
