# MiniMax MCP Search Skill

## 功能

使用 MiniMax MCP 进行网络搜索和图像理解。通过 mcporter 调用 MiniMax Coding Plan MCP 服务。

## 工具

### 1. web_search - 网络搜索

使用 MiniMax MCP 进行实时网络搜索，返回搜索结果和相关链接。

**参数：**
- `query` (string, 必需): 搜索关键词，建议 3-5 个关键词

**返回：** 搜索结果列表，包含标题、链接、摘要和日期

### 2. understand_image - 图像理解

使用 MiniMax MCP 分析图片内容，支持本地文件路径和 HTTP/HTTPS URL。

**参数：**
- `image_path` (string, 必需): 图片路径，支持本地路径或 URL
- `prompt` (string, 必需): 分析要求

**支持格式：** JPEG、PNG、WebP

## 使用方法

**网络搜索示例：**
```
搜索：最新AI新闻
```

**图像理解示例：**
```
分析图片：/path/to/image.jpg，描述图片内容
```

## 注意事项

- 需要先安装 mcporter：`npm install -g mcporter`
- 首次使用需配置 MiniMax API Key（已在配置文件中设置）
- 图像理解支持本地文件和 HTTP/HTTPS URL
