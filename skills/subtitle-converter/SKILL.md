---
name: subtitle-converter
description: 字幕格式转换工具，支持 VTT、SRT、ASS、LRC 四种格式互转，以及时间轴偏移和双语字幕合并。当用户需要转换字幕格式（如 VTT 转 SRT 用于剪映）、调整字幕时间、合并双语字幕、或批量处理字幕文件时使用此技能。触发词：字幕转换、vtt转srt、srt转vtt、剪映字幕、字幕格式、时间轴偏移、双语字幕、字幕合并。
---

# 字幕格式转换

支持 VTT、SRT、ASS、LRC 四种字幕格式的相互转换，以及时间轴偏移和双语字幕合并功能。

## 支持格式

| 格式 | 用途 | 特点 |
|------|------|------|
| **VTT** | 网络视频（YouTube等） | 支持样式、定位 |
| **SRT** | 通用格式（剪映支持） | 简单、兼容性好 |
| **ASS** | 高级字幕（动画、卡拉OK） | 完整样式控制 |
| **LRC** | 歌词同步 | 行级时间戳 |

## 工作流

### 格式转换

1. 确定源文件格式和目标格式
2. 运行转换脚本：
   ```bash
   python scripts/convert.py <输入文件> --format <目标格式>
   ```
3. 输出文件默认在同目录，使用 `.srt`/`.vtt` 等扩展名

### 批量转换

1. 确定目标目录和格式
2. 运行批量转换：
   ```bash
   python scripts/convert.py <目录> --batch --format <目标格式>
   ```

### 时间轴偏移

1. 确定偏移秒数（正数延后，负数提前）
2. 运行偏移命令：
   ```bash
   python scripts/convert.py <文件> --shift <秒数>
   ```

### 双语字幕合并

1. 准备两个字幕文件（不同语言）
2. 运行合并命令：
   ```bash
   python scripts/convert.py <文件1> <文件2> --merge
   ```

## 命令参考

```bash
# 格式转换
python scripts/convert.py input.vtt --format srt
python scripts/convert.py input.vtt --output output.srt

# 批量转换
python scripts/convert.py ./subs --batch --format srt
python scripts/convert.py ./subs --batch --format srt --output ./output

# 时间轴偏移
python scripts/convert.py input.srt --shift 2.5    # 延后2.5秒
python scripts/convert.py input.srt --shift -1.0   # 提前1秒

# 双语字幕合并
python scripts/convert.py zh.srt en.srt --merge
python scripts/convert.py zh.srt en.srt --merge --output bilingual.srt
```

## 常见场景

### YouTube VTT 转 剪映 SRT

YouTube 自动生成的 VTT 字幕包含滚动显示和逐词时间戳，转换时会自动清理：

```bash
python scripts/convert.py video.zh-Hans.vtt --format srt
```

### 批量转换目录下的 VTT 文件

```bash
python scripts/convert.py /path/to/subs --batch --format srt
```

### 字幕与视频不同步

如果字幕整体提前或延后，使用时间轴偏移：

```bash
# 字幕提前了3秒，需要延后
python scripts/convert.py subtitle.srt --shift 3

# 字幕延后了2秒，需要提前
python scripts/convert.py subtitle.srt --shift -2
```

### 制作中英双语字幕

```bash
python scripts/convert.py chinese.srt english.srt --merge --output bilingual.srt
```

## 技术细节

详见 [references/formats.md](references/formats.md)：
- 四种格式的语法规范
- 时间格式差异（毫秒分隔符、精度）
- 转换注意事项（标签清理、编码处理）

## 注意事项

1. **YouTube VTT**：自动合并滚动块、清理逐词标签
2. **SRT 必须有序号**：转换到 SRT 时自动生成
3. **ASS 精度损失**：毫秒转厘秒时会四舍五入
4. **LRC 无结束时间**：自动设为下一行开始时间
5. **编码统一**：输出文件使用 UTF-8 编码
