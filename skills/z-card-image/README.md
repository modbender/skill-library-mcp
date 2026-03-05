# z-card-image

文字卡片图片生成器，把文案渲染成 PNG，支持公众号、小红书等多种配色风格。

## 效果

- 输入一段文字，自动排版成精美卡片图
- 支持多行文字 + 高亮、品牌 footer、顶部图标
- 默认模板：3:4 竖版（900×1200）

## 依赖

- Python 3
- Google Chrome（macOS：`/Applications/Google Chrome.app`）

## 自定义品牌信息

默认配色和 footer 是「早早集市」的风格，改成你自己的只需修改 `SKILL.md` 里的**平台预设**表格：

```markdown
## 平台预设

| 平台 | `--footer` | `--bg` | `--highlight` |
|------|-----------|--------|--------------|
| 公众号（默认） | `公众号 · 你的名字` | `#e6f5ef` | `#22a854` |
| 小红书 | `小红书 · 你的名字` | `#fdecea` | `#e53935` |
```

`render_card.py` 支持的所有参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--footer` | 底部署名文字 | `公众号 · 早早集市` |
| `--bg` | 背景色（hex） | `#e6f5ef` |
| `--highlight` | 高亮色（hex） | `#22a854` |
| `--icon` | 顶部图标路径 | 自动判断 |
| `--template` | 模板名 | `xiaolvs-cover` |

把 `--footer` 改成你的公众号名，`--bg` / `--highlight` 改成你的品牌色，就是你的专属风格了。

## 替换 Logo

顶部图标在 `assets/icons/` 目录，替换对应 SVG/JPG 文件即可，文件名保持一致。

## 新增模板

1. 新建 `assets/templates/<name>.html`
2. 在 `scripts/render_card.py` 的 `size_map` 里注册尺寸
3. 在 `SKILL.md` 模板索引中添加一行
4. 创建 `references/<name>.md` 记录参数和字数上限
