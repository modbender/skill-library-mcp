# 字幕格式规范参考

## 目录

1. [格式对照表](#格式对照表)
2. [VTT (WebVTT)](#vtt-webvtt)
3. [SRT (SubRip)](#srt-subrip)
4. [ASS/SSA (Advanced SubStation Alpha)](#assssa-advanced-substation-alpha)
5. [LRC (歌词)](#lrc-歌词)
6. [转换注意事项](#转换注意事项)

---

## 格式对照表

| 特性 | VTT | SRT | ASS | LRC |
|------|-----|-----|-----|-----|
| 时间格式 | `HH:MM:SS.mmm` | `HH:MM:SS,mmm` | `H:MM:SS.cc` | `[mm:ss.xx]` |
| 毫秒分隔符 | `.` (点) | `,` (逗号) | `.` (点) | `.` (点) |
| 时间精度 | 毫秒 (3位) | 毫秒 (3位) | 厘秒 (2位) | 厘秒/毫秒 (2-3位) |
| 必须序号 | 否 | 是 | 否 | 否 |
| 头部要求 | `WEBVTT` | 无 | `[Script Info]` | 可选元数据 |
| 样式支持 | CSS类 | 基础HTML | 完整样式 | 无 |
| 编码 | UTF-8 | UTF-8/ANSI | UTF-8 | UTF-8 |

---

## VTT (WebVTT)

WebVTT 是 W3C 标准的 HTML5 视频字幕格式，广泛用于网络视频平台。

### 结构

```vtt
WEBVTT [可选描述]

NOTE
这是注释

[cue标识符]
时间戳行
字幕文本

时间戳行
字幕文本
```

### 时间戳格式

```
HH:MM:SS.mmm --> HH:MM:SS.mmm [定位参数]
```

- `HH`: 小时 (00-99)
- `MM`: 分钟 (00-59)
- `SS`: 秒 (00-59)
- `mmm`: 毫秒 (000-999)
- 分隔符: **点** (`.`)

### 定位参数 (可选)

```
align:start|center|end|left|right
line:0%|0
position:0%
size:100%
vertical:lr|rl
```

### 示例

```vtt
WEBVTT - 示例文件

NOTE 这是一个示例字幕文件

1
00:00:01.000 --> 00:00:04.500
第一句字幕内容

00:00:05.000 --> 00:00:09.000 align:center line:80%
第二句字幕内容
可以多行显示
```

### 特殊标签

- `<b>粗体</b>`
- `<i>斜体</i>`
- `<u>下划线</u>`
- `<c.class>带类名的文本</c>`
- `<v 说话者>对话标签</v>`
- `<00:00:00.000>` 逐词时间戳

---

## SRT (SubRip)

SRT 是最广泛支持的"传统"字幕格式，结构简单。

### 结构

```srt
序号
时间戳
字幕文本
(空行)
序号
时间戳
字幕文本
```

### 时间戳格式

```
HH:MM:SS,mmm --> HH:MM:SS,mmm
```

- 分隔符: **逗号** (`,`)
- 必须有序号

### 示例

```srt
1
00:00:01,000 --> 00:00:04,500
第一句字幕内容

2
00:00:05,000 --> 00:00:09,000
第二句字幕内容
可以多行
```

### 支持的标签 (部分播放器)

- `<b>粗体</b>`
- `<i>斜体</i>`
- `<u>下划线</u>`
- `<font color="#FF0000">彩色</font>`

---

## ASS/SSA (Advanced SubStation Alpha)

ASS 是功能最强大的字幕格式，支持复杂样式和动画效果。

### 结构

```ass
[Script Info]
; 脚本信息

[V4+ Styles]
; 样式定义

[Events]
; 字幕事件
```

### 时间戳格式

```
H:MM:SS.cc
```

- `H`: 小时 (无前导零)
- `MM`: 分钟
- `SS`: 秒
- `cc`: **厘秒** (2位，非毫秒)

### Script Info 示例

```ass
[Script Info]
Title: 字幕标题
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
```

### Styles 示例

```ass
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,20,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,1
```

### Events 示例

```ass
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:01.00,0:00:04.50,Default,,0,0,0,,第一句字幕内容
Dialogue: 0,0:00:05.00,0:00:09.00,Default,,0,0,0,,第二句字幕内容{\pos(320,240)}
```

### 常用标签

- `{\b1}粗体{\b0}`
- `{\i1}斜体{\i0}`
- `{\pos(x,y)}定位`
- `{\fad(淡入,淡出)}渐变`
- `{\k100}卡拉OK效果`
- `\N` 换行

---

## LRC (歌词)

LRC 是为音乐同步设计的简单格式。

### 结构

```lrc
[ti:歌曲标题]
[ar:艺术家]
[al:专辑]
[00:00.00]歌词第一行
[00:10.50]歌词第二行
```

### 时间戳格式

```
[mm:ss.xx]
```

- `mm`: 分钟
- `ss`: 秒
- `xx`: 厘秒或毫秒 (2-3位)

### 元数据标签

- `[ti:]` 标题
- `[ar:]` 艺术家
- `[al:]` 专辑
- `[by:]` 制作者
- `[offset:]` 时间偏移毫秒

### 增强 LRC (逐词同步)

```lrc
[00:15.00]<00:15.00>第<00:15.30>一<00:15.60>句
```

---

## 转换注意事项

### 1. 时间戳分隔符转换

| 源格式 | 目标格式 | 操作 |
|--------|----------|------|
| VTT | SRT | `.` → `,` |
| SRT | VTT | `,` → `.` |
| 任意 | ASS | 转为厘秒 (除以10) |
| 任意 | LRC | 转为 `[mm:ss.xx]` 格式 |

### 2. 精度损失

```
VTT/SRT 毫秒: 123ms
ASS 厘秒:     12cs (四舍五入)
```

### 3. 标签清理

| 源格式 | 清理内容 |
|--------|----------|
| VTT | `<c>`, `<v>`, 定位参数, 逐词时间戳 |
| SRT | HTML 标签 |
| ASS | `{...}` 覆盖标签, `\N` 转换为换行 |
| LRC | `<mm:ss.xx>` 逐词标签 |

### 4. YouTube VTT 特殊处理

YouTube 自动生成的 VTT 字幕包含：
- 滚动显示块 (重复内容)
- 逐词时间戳 `<00:00:00.400><c>文字</c>`

转换时需要：
1. 合并重复/滚动块
2. 清理逐词标签
3. 移除定位参数

### 5. 编码问题

- 统一使用 UTF-8 编码
- 处理 ANSI 编码的旧 SRT 文件
- BOM 头处理

### 6. 空行处理

- SRT 块之间必须有空行
- VTT 块之间用空行分隔
- ASS 每个 Dialogue 独占一行
- LRC 每行独立
