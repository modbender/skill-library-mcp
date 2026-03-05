---
name: "image-process"
description: "Image processing tool for compression, background removal/replacement, and upscaling. Invoke when user wants to compress image, remove background, change background, or enlarge image."
---

# Image Process Skill

This skill provides image processing capabilities including compression, background removal, background replacement, and upscaling.

## Features

- **Image Compression**: Compress images to reduce file size with adjustable quality
- **Background Removal**: AI-powered background removal using `@imgly/background-removal`
- **Background Replacement**: Replace background with a custom color or another image
- **Image Upscaling**: Enlarge images to bigger dimensions

## Usage

### 1. Compress Image

```javascript
const { compressImage } = require('./index');

const result = await compressImage({
  input: './image.jpg',
  quality: 80,
  output: './compressed.jpg'
});
```

### 2. Remove Background

```javascript
const { removeBackground } = require('./index');

const result = await removeBackground({
  input: './person.jpg',
  output: './person-nobg.png'
});
```

### 3. Replace Background

```javascript
const { replaceBackground } = require('./index');

// Replace with solid color
const result = await replaceBackground({
  input: './person.jpg',
  background: '#ffffff',
  output: './result.jpg'
});

// Replace with another image
const result = await replaceBackground({
  input: './person.jpg',
  background: './background.jpg',
  output: './result.jpg'
});
```

### 4. Upscale Image

```javascript
const { upscaleImage } = require('./index');

// Scale by factor (2x)
const result = await upscaleImage({
  input: './image.jpg',
  scale: 2,
  output: './upscaled.jpg'
});

// Or specify exact dimensions
const result = await upscaleImage({
  input: './image.jpg',
  width: 2000,
  height: 3000,
  output: './upscaled.jpg'
});
```

## Parameters

### compressImage

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | string | Path to input image |
| `quality` | number | Compression quality (1-100), default 80 |
| `output` | string | Output file path |

### removeBackground

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | string/Buffer | Path or buffer of input image |
| `output` | string | Output file path (optional) |

### replaceBackground

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | string | Path to foreground image |
| `background` | string | Hex color (e.g. '#ffffff') or path to background image |
| `output` | string | Output file path |

### upscaleImage

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | string | Path to input image |
| `scale` | number | Scale factor (e.g. 2 for 2x), default 2 |
| `width` | number | Target width (overrides scale) |
| `height` | number | Target height (overrides scale) |
| `output` | string | Output file path |

## CLI Commands

```bash
# Compress
image-process compress ./photo.jpg -q 80

# Remove background
image-process remove-bg ./person.jpg

# Replace background
image-process replace-bg ./person.jpg "#ffffff"
image-process replace-bg ./person.jpg ./background.jpg

# Upscale
image-process upscale ./photo.jpg -s 2
image-process upscale ./photo.jpg -w 2000 -h 3000
```

## Installation

```bash
cd E:\cvte\skills\image-process
npm install
```

## Dependencies

- `@imgly/background-removal-node` - AI background removal
- `sharp` - High-performance image processing
