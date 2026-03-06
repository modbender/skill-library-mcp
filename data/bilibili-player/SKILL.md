---
name: bilibili-player
description: B 站视频播放器。用 Playwright 搜索 B 站视频并获取准确链接，然后用 open 命令在当前浏览器打开播放。Use when users request to play Bilibili videos or search for specific content.
---

# B 站视频播放器

## 功能

用 Playwright 无头浏览器搜索 B 站视频，获取准确链接后用系统 open 命令在用户当前浏览器打开播放。

## 使用场景

- 播放电影/电视剧（如：三国演义、电影名称）
- 播放音乐/MV（如：伍佰 突然的自我）
- 播放纪录片/教程
- 任何需要在 B 站搜索并播放视频的场景

## 优势

- ✅ **准确** - Playwright 直接解析页面获取视频链接
- ✅ **快速** - 无头模式搜索，不阻塞用户界面
- ✅ **稳定** - 用用户浏览器播放，有音频、有登录状态、有 Cookie
- ✅ **简单** - 一个命令完成搜索 + 打开

## 使用方法

### 基本用法

```bash
bilibili-player.sh "搜索关键词"
```

### 示例

```bash
# 播放电视剧
bilibili-player.sh "三国演义 1994 火烧赤壁"
bilibili-player.sh "西游记 央视版"

# 播放音乐
bilibili-player.sh "伍佰 突然的自我"
bilibili-player.sh "李宇春 蜀绣"

# 播放电影
bilibili-player.sh "流浪地球"
```

## 工作流程

```
用户请求 → Playwright 搜索 → 提取视频链接 → open 命令打开 → 浏览器播放
```

### 详细步骤

1. **Playwright 搜索** - 无头 Chromium 访问 B 站搜索页面
2. **解析页面** - 提取第一个视频卡片的链接
3. **open 打开** - 用 macOS open 命令在默认浏览器打开
4. **播放** - 用户在浏览器中观看（有声音、有登录状态）

## 脚本说明

### bilibili-player.py

Python 脚本，执行搜索和打开操作。

**依赖：**
- Python 3
- Playwright (`pip3 install playwright`)

**用法：**
```bash
python3 bilibili-player.py "搜索关键词"
```

### bilibili-player.sh

Shell 封装脚本，方便直接调用。

**用法：**
```bash
./bilibili-player.sh "搜索关键词"
```

## 技术细节

### Playwright 选择器

脚本使用以下选择器查找视频链接（按优先级）：

```python
selectors = [
    "a[href*='/video/']",      # 最准确：包含/video/的链接
    ".bili-video-card a",      # 备选：视频卡片的链接
]
```

### 链接处理

- 相对链接自动补全为完整 URL
- 支持 `//` 开头的协议相对链接

### 错误处理

- 如果找不到视频，打开搜索页面
- 超时时间：60 秒
- 等待页面加载：3 秒

## 限制

- 仅支持 macOS（依赖 open 命令）
- 需要安装 Playwright
- 需要网络连接

## 扩展建议

如需支持其他平台：

- **Linux**: 用 `xdg-open` 替代 `open`
- **Windows**: 用 `start` 替代 `open`

## 相关文件

- `scripts/bilibili-player.py` - 主脚本
- `scripts/bilibili-player.sh` - Shell 封装
