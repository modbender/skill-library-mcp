---
name: "image-process"
description: "图片处理工具，支持压缩、去背景、换背景、放大图片。当用户需要压缩图片、去除背景、更换背景或放大图片时调用。"
---

# 图片处理技能

提供图片处理功能，包括压缩、去背景、换背景和放大图片。

## 功能

- **图片压缩**: 压缩图片以减小文件大小，可调节压缩质量
- **去除背景**: 使用 AI 智能去除图片背景
- **更换背景**: 将背景替换为纯色或其他图片
- **图片放大**: 将图片放大到更大尺寸

## 使用方法

### 1. 压缩图片

```javascript
const { compressImage } = require('./index');

const result = await compressImage({
  input: './image.jpg',
  quality: 80,
  output: './compressed.jpg'
});
```

### 2. 去除背景

```javascript
const { removeBackground } = require('./index');

const result = await removeBackground({
  input: './person.jpg',
  output: './person-nobg.png'
});
```

### 3. 更换背景

```javascript
const { replaceBackground } = require('./index');

// 替换为纯色背景
const result = await replaceBackground({
  input: './person.jpg',
  background: '#ffffff',
  output: './result.jpg'
});

// 替换为其他图片背景
const result = await replaceBackground({
  input: './person.jpg',
  background: './background.jpg',
  output: './result.jpg'
});
```

### 4. 放大图片

```javascript
const { upscaleImage } = require('./index');

// 按倍数放大 (2倍)
const result = await upscaleImage({
  input: './image.jpg',
  scale: 2,
  output: './upscaled.jpg'
});

// 或指定具体尺寸
const result = await upscaleImage({
  input: './image.jpg',
  width: 2000,
  height: 3000,
  output: './upscaled.jpg'
});
```

## 参数说明

### compressImage 压缩图片

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `input` | string | 输入图片路径 |
| `quality` | number | 压缩质量 (1-100)，默认 80 |
| `output` | string | 输出文件路径 |

### removeBackground 去除背景

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `input` | string/Buffer | 输入图片路径或 Buffer |
| `output` | string | 输出文件路径 (可选) |

### replaceBackground 更换背景

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `input` | string | 前景图片路径 |
| `background` | string | 十六进制颜色 (如 '#ffffff') 或背景图片路径 |
| `output` | string | 输出文件路径 |

### upscaleImage 放大图片

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `input` | string | 输入图片路径 |
| `scale` | number | 放大倍数 (如 2 表示 2 倍)，默认 2 |
| `width` | number | 目标宽度 (设置后忽略 scale) |
| `height` | number | 目标高度 (设置后忽略 scale) |
| `output` | string | 输出文件路径 |

## 命令行使用

```bash
# 压缩图片
image-process compress ./photo.jpg -q 80

# 去除背景
image-process remove-bg ./person.jpg

# 更换背景
image-process replace-bg ./person.jpg "#ffffff"
image-process replace-bg ./person.jpg ./background.jpg

# 放大图片
image-process upscale ./photo.jpg -s 2
image-process upscale ./photo.jpg -w 2000 -h 3000
```

## 安装依赖

```bash
cd E:\cvte\skills\image-process
npm install
```

## 依赖库

- `@imgly/background-removal-node` - AI 背景去除
- `sharp` - 高性能图片处理
