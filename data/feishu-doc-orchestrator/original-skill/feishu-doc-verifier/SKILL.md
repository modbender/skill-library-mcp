---
name: feishu-doc-verifier
description: 文档验证子技能 - 使用 Playwright 验证飞书文档是否创建成功。
---

# 文档验证子技能

## 职责
使用 Playwright 访问飞书文档，验证文档是否创建成功并可正常访问。

## 输入
- `doc_info.json` - 由 feishu-doc-creator-v2 生成

## 输出
- `output/verify_result.json` - 验证结果

## 工作流程

### 第一步：加载文档信息
从 `doc_info.json` 加载文档 ID 和 URL。

### 第二步：检查登录状态
检查是否存在已保存的登录状态（`.claude/playwright_state/state.json`）：
- **首次运行**：显示浏览器窗口，提示用户使用飞书APP扫码登录
- **后续运行**：使用保存的登录状态，自动访问文档（无头模式）

### 第三步：启动 Playwright
使用持久化上下文启动浏览器：
- 首次运行：`headless=False`（显示浏览器窗口）
- 后续运行：`headless=True`（无头模式）
- 登录状态保存在 `.claude/playwright_state/`

### 第四步：访问文档
导航到文档 URL，等待页面加载：
- 首次运行时等待最多 2 分钟供用户扫码登录
- 后续运行快速加载（使用已保存的登录态）

### 第五步：验证结果
检查页面标题和内容，确认文档可访问。

### 第六步：保存结果
保存验证结果到 `output/verify_result.json`。
首次登录成功后，自动保存登录状态到 `.claude/playwright_state/state.json`。

## 数据格式

### verify_result.json 格式
```json
{
  "success": true,
  "document_id": "U2wNd2rMkot6fzxr67ScN7hJn7c",
  "document_url": "https://feishu.cn/docx/U2wNd2rMkot6fzxr67ScN7hJn7c",
  "page_loaded": true,
  "page_title": "文档标题",
  "screenshot": "output/screenshot.png",
  "verified_at": "2026-01-22T10:40:00"
}
```

## 使用方式

### 命令行
```bash
python scripts/doc_verifier.py workflow/step2_create/doc_info.json output
```

### 作为子技能被调用
```python
result = call_skill("feishu-doc-verifier", {
    "doc_info_file": "workflow/step2_create/doc_info.json",
    "output_dir": "workflow/step5_verify"
})
```

## 与其他技能的协作
- 接收来自 `feishu-permission-manager-v2` 的文档信息
- 输出给 `feishu-logger`

## 飞书登录状态管理 ⭐

### 首次运行
当第一次运行验证器时：
1. 浏览器窗口会自动打开
2. 显示飞书登录页面
3. 使用飞书APP扫码登录
4. 登录成功后，状态自动保存到 `.claude/playwright_state/state.json`

### 后续运行
登录状态保存后：
- 自动使用保存的登录状态
- 无头模式运行（不显示浏览器窗口）
- 快速验证文档可访问性

### 登录状态存储位置
```
项目根目录/
└── .claude/
    └── playwright_state/
        ├── state.json      # 登录状态
        └── ...             # 其他浏览器数据
```

### 重新登录
如果需要重新登录（如登录过期）：
```bash
# 删除登录状态
rm -rf .claude/playwright_state

# 再次运行验证器，会提示重新扫码
python .claude/skills/feishu-doc-verifier/scripts/doc_verifier.py <doc_info.json>
```
