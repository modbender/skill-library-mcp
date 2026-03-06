---
name: hd-infoimage
description: 高密度信息大图生成技能。根据文章/内容生成高信息密度的视觉大图，适合知识干货、笔记分享、课程内容可视化。支持8种风格：坐标蓝图波普实验室、复古波普网格、文件夹风、色块热敏纸、复古手帐、档案混合媒介、色块酸性风、票据剧场戏票风。使用 Imagen 3（ZenMux API，建议4K）生成。当用户提供文章/内容并要求生成信息大图、干货图、知识图、高密度配图时触发此技能。
---

# 高密度信息大图（hd-infoimage）

根据用户提供的文章或内容，生成高信息密度的视觉大图。

## 使用方式

用户提供文章内容后，告知龙虾：
> 根据给你的文章和这个 prompt，生成适合数量的高信息密度大图

## 风格选项（8种）

从 `references/` 中选择对应风格文件，将提示词 + 用户文章内容一起发给图像模型。

| # | 风格名称 | 特征 | 文件 |
|---|---------|------|------|
| 1 | 坐标蓝图·波普实验室 | 实验室精密感，视觉坐标系，高密度数据 | `style-01-坐标蓝图·波普实验室.md` |
| 2 | 复古波普网格风 | 70年代复古波普，Swiss Grid，6-7模块 | `style-02-复古波普网格风.md` |
| 3 | 文件夹·热敏纸风 | 文件夹质感，打印热敏纸，英文版 | `style-03-文件夹风格（打印热敏.md` |
| 4 | 色块·热敏纸风 | 高对比色块框架+中性纸张，英文详细版 | `style-04-色块·热敏纸风（英文.md` |
| 5 | 复古手帐·档案风 | 侦探证据板美学，手帐剪贴风 | `style-05-复古手帐·档案风.md` |
| 6 | 档案·混合媒介风 | 牛皮纸+深黑，证书徽章，英文版 | `style-06-档案·混合媒介风（英.md` |
| 7 | 色块·复古未来酸性风 | 酸性涂鸦，复古未来主义，高对比 | `style-07-色块·复古未来酸性风.md` |
| 8 | 票据·剧场戏票风 | 五幕剧叙事，剧场票据，粒状纹理 | `style-08-票据·剧场戏票风.md` |

未指定风格时，默认推荐风格2（复古波普网格）或风格1（坐标蓝图）。

## 生成图片

```bash
cd /root/.openclaw/workspace/skills/zenmux-image-generation
ZENMUX_API_KEY="<key>" python3 scripts/generate.py \
  --output /root/myfiles/<filename>.png \
  --prompt "<风格提示词> + <文章内容>"
```

建议生成4K质量（Imagen 3 默认支持）。

## 注意事项

- 复古风提示词里如出现"小红书" logo，可删掉提示词中的"小红书"字样
- 每张图建议包含 6-7 个子主题模块，信息密度要高
- 生成后用 `send_to_feishu.sh` 发送（见 sketch-illustration skill）
- API Key 读取：`cat ~/.openclaw/openclaw.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['models']['providers']['ZenMux']['apiKey'])"`
