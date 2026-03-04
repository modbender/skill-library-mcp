---
name: feishu-block-adder
description: 块添加子技能 - 将解析后的块数据添加到飞书文档，分批处理，支持表格和普通块，**现在支持图片上传**。
---

# 块添加子技能

## 职责
将解析后的块数据添加到飞书文档，分批处理以避免 API 限制。

## 输入
- `blocks.json` - 由 feishu-md-parser 生成
- `doc_info.json` - 由 feishu-doc-creator-with-permission 生成

## 输出
- `output/add_result.json` - 添加结果统计

## 工作流程

### 第一步：加载块数据
从 `blocks.json` 加载解析后的块列表。

### 第二步：加载文档信息
从 `doc_info.json` 加载文档 ID。

### 第三步：分批添加块
每批最多 20 个块，避免触发 API 限流。

### 第四步：保存结果
保存添加结果到 `output/add_result.json`。

## 支持的块类型（13种）

| block_type | 名称 | 状态 | 说明 |
|------------|------|------|
| 2 | text | ✅ | 普通文本 |
| 3-8 | heading1-6 | ✅ | 一到六级标题 |
| 12 | bullet | ✅ 无序列表 |
| 13 | ordered | ✅ | 有序列表 |
| 14 | code | ✅ | 代码块 |
| 15 | quote | ✅ | 引用块 |
| 17 | todo | ✅ | 待办事项 |
| 19 | callout | ✅ | 高亮块 |
| 22 | divider | ✅ | 分割线 |
| 27 | image | ✅ **图片块（支持本地图片上传）** |

---

## 图片上传功能说明

### 新增功能
现在支持 Markdown 中的本地图片上传到飞书文档。

### 支持的图片格式

#### 1. 本地图片（会上传）
```markdown
![测试图片](D:/00-work_study/AIsthdy/test-claude/test_upload.png)
```
- `local_path` 字段会被保存到图片块数据中
- 图片会通过三步流程自动上传到飞书服务器

#### 2. 网络图片（仅显示 URL）
```markdown
![测试图片](https://example.com/image.png)
```
- 不会上传文件，只在文档中显示链接

### 实现细节

#### md_parser.py 解析
- 识别 `![alt](url)` 语法
- 提取 `local_path`：`D:\00-work_study\path\to\image.png`
- 如果是本地路径且文件存在，保存到 `local_path` 字段

#### block_adder.py 上传流程
1. **创建图片块**：调用 API 创建空图片块（block_type: 27）
2. **上传图片文件**：使用 `upload_image_file()` 函数上传到飞书
3. **设置图片 token**：使用 `update_image_block_token()` 函数设置 token

### API 端点

#### 创建图片块
```
POST /open-apis/docx/v1/documents/{doc_id}/blocks/{parent_id}/children
{
  "children": [{
    "block_type": 27,
    "image": {}
  }]
}
```

#### 上传图片
```
POST /open-apis/drive/v1/medias/upload_all
Content-Type: multipart/form-data

file=@D:/00-work_study/AIsthdy/test-claude/test_upload.png; filename=test_upload.png
file_name=test_upload.png
parent_type=docx_image
parent_node={image_block_id}
size=1024
```

#### 设置图片 Token
```
PATCH /open-apis/docx/v1/documents/{doc_id}/blocks/{image_block_id}
{
  "replace_image": {
    "token": "{file_token}"
  }
}
```

### 使用示例
```markdown
# 我的图片测试

![本地图片](D:\00-work_study\AIsthdy\test-claude/test_upload.png)

---
上传成功后，图片将在飞书文档中显示！
```

### 注意事项
1. **图片路径必须是绝对路径或正确相对路径**，否则无法找到文件
2. **网络图片不会上传**，只在文档中显示 URL
3. **确保图片文件存在**，否则跳过上传步骤
4. **最大文件大小限制**：飞书 API 限制为 10MB

---

**更新时间**：2025-02-13
