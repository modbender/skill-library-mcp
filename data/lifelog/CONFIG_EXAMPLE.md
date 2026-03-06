# 配置示例

将 `scripts/` 目录下的脚本中的占位符替换为你的实际配置：

```bash
# ===== 配置区域 =====
NOTION_KEY="你的Notion_API_Key"
DATABASE_ID="你的Database_ID"
# ====================
```

## 获取步骤

### 1. 创建 Notion Integration
1. 访问 https://www.notion.so/my-integrations
2. 点击 **New integration**
3. 填写名称（如 "LifeLog"）
4. 复制生成的 **Internal Integration Token**

### 2. 创建 Database
1. 在 Notion 中创建新 Database
2. 添加以下字段（全部为 rich_text 类型）：
   - 日期（title）
   - 原文
   - 情绪状态
   - 主要事件
   - 位置
   - 人员
3. 点击 Database 右上角的 **...** → **Connect to** → 选择你的 Integration

### 3. 获取 Database ID
- URL 中提取：`https://notion.so/{workspace}/{database_id}?v=...`
- database_id 是 32 位字符串（带 `-`）
