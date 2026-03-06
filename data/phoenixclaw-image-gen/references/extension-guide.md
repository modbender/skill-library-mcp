# 扩展指南 (Image Generation Extension Guide)

本文档说明如何为图像生成技能扩展新的 Provider 适配器。

> **重要说明**: v1 版本仅支持 **OpenRouter only**。后续版本将根据本指南进行扩展。

---

## Provider 适配器接口 (Adapter Interface)

所有新增的 Provider 必须在 `scripts/cli/` 目录下实现一个适配器脚本，并遵循以下接口规范。

### 核心方法

#### 1. `generate(options)`
执行图像生成任务。
- **参数**:
  - `prompt` (String, 必填): 图像生成描述。
  - `model` (String, 可选): 指定模型 ID。
  - `size` (String, 可选): 分辨率等级 (`1K`|`2K`|`4K`)，非像素尺寸。
  - `output` (String, 可选): 输出文件路径。
- **返回值**:
  - 成功时返回包含文件路径的对象：`{ success: true, path: "..." }`。
  - 失败时抛出错误或返回错误对象。

#### 2. `test()`
用于环境检查和连通性测试。
- **行为**: 验证 API Key 有效性及网络可达性，不产生计费生成。
- **返回值**: `{ success: true, message: "..." }`。

---

## 接入步骤 (Registration Steps)

若要添加新的 Provider（例如 Replicate 或 Stability AI），请遵循以下步骤：

### 步骤 1: 创建适配器脚本
在 `scripts/cli/` 下创建新文件，例如 `replicate.js` (Stub Example):

```javascript
// scripts/cli/replicate.js (Stub)
async function generate(params) {
    // 1. 验证环境变量 (REPLICATE_API_TOKEN)
    // 2. 构造 Replicate API 请求
    // 3. 处理响应并保存图片到本地
    // 4. 返回结果
    console.log("Replicate provider not implemented in v1");
}

async function test() {
    // 验证 Token
}

module.exports = { generate, test };
```

### 步骤 2: 定义环境变量
在 `.env` 中定义该 Provider 所需的凭证字段，例如 `REPLICATE_API_TOKEN`。

### 步骤 3: 注册 Provider
在 `scripts/generate.js` 的 Provider 路由逻辑中添加映射：

```javascript
// scripts/generate.js (Logic Stub)
const providers = {
    'openrouter': require('./cli/openrouter'),
    // 'replicate': require('./cli/replicate'), // 未来扩展点
};
```

### 步骤 4: 更新文档
1. 在 `SKILL.md` 的支持列表中添加新 Provider。
2. 在 `references/extension-guide.md` 的更新日志中记录。

---

## 错误处理规范

所有适配器应返回统一的错误结构：
```json
{
  "success": false,
  "error": "PROVIDER_ERROR_CODE",
  "message": "Human readable message"
}
```

---

## 更新日志

| 日期 | 变更内容 |
|------|----------|
| 2025-02-25 | 初始版本，定义适配器接口规范 (adapter interface)，明确 v1 仅支持 OpenRouter only |
