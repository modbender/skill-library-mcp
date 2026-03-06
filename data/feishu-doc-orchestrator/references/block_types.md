# 飞书文档块类型参考

## 支持的块类型

### 基础块
- 标题 (Heading1-9) - block_type 3-11
- 文本 (Text) - block_type 2
- 无序列表 (Bullet) - block_type 12
- 有序列表 (Ordered) - block_type 13
- 引用 (Quote) - block_type 15
- 代码块 (Code) - block_type 14
- 分割线 (Divider) - block_type 22

### 高级块
- 表格 (Table) - block_type 31
- 图片 (Image) - block_type 27
- 高亮块 (Callout) - block_type 19
- 待办事项 (Todo) - block_type 17

## 块类型编号对照表

| 块类型 | block_type | 说明 |
|--------|-----------|------|
| Page | 1 | 页面根节点 |
| Text | 2 | 普通文本 |
| Heading1 | 3 | 一级标题 |
| Heading2 | 4 | 二级标题 |
| Heading3 | 5 | 三级标题 |
| Heading4 | 6 | 四级标题 |
| Heading5 | 7 | 五级标题 |
| Heading6 | 8 | 六级标题 |
| Heading7 | 9 | 七级标题 |
| Heading8 | 10 | 八级标题 |
| Heading9 | 11 | 九级标题 |
| Bullet | 12 | 无序列表 |
| Ordered | 13 | 有序列表 |
| Code | 14 | 代码块 |
| Quote | 15 | 引用块 |
| Todo | 17 | 待办事项 |
| Callout | 19 | 高亮块 |
| Divider | 22 | 分割线 |
| Image | 27 | 图片 |
| Table | 31 | 表格 |
| TableCell | 32 | 表格单元格 |

## Callout 样式

### 颜色值
- background_color: 1-15 (浅色系1-7, 中色系8-14, 浅灰15)
- border_color: 1-7 (红橙黄绿蓝紫灰)
- text_color: 1-7, 15 (红橙黄绿蓝紫灰, 白色15)

### 预定义样式
```json
{
  "info": {"emoji_id": "information_source", "background_color": 5, "border_color": 5},
  "tip": {"emoji_id": "bulb", "background_color": 3, "border_color": 3, "text_color": 3},
  "warning": {"emoji_id": "warning", "background_color": 1, "border_color": 1, "text_color": 1},
  "success": {"emoji_id": "white_check_mark", "background_color": 4, "border_color": 4, "text_color": 4},
  "note": {"emoji_id": "pushpin", "background_color": 7, "border_color": 7},
  "important": {"emoji_id": "fire", "background_color": 8, "border_color": 1, "text_color": 1}
}
```

## API 参考

- [飞书文档块类型 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/docx-v1/document-block/overview)
- [飞书权限管理 API](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/drive-v1/permission-member/create)
