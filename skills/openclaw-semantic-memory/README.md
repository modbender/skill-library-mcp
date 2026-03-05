# openclaw-semantic-memory

OpenClaw 本地语义记忆插件，基于向量搜索和 Transformers.js 实现零配置的语义搜索。

**📦 ClawHub**: https://clawhub.ai/skills/semantic-memory

## 特性

- 🧠 **本地语义搜索** - 使用 Transformers.js 在本地生成 embeddings
- 💾 **磁盘持久化** - 默认保存到磁盘，重启后数据不丢失
- 🔄 **自动捕获** - 通过 lifecycle hooks 自动记录重要信息
- 🎯 **智能召回** - 根据上下文自动检索相关记忆

## 安装

### 通过 ClawHub（推荐）

```bash
clawhub install semantic-memory
```

### 手动安装

```bash
cd ~/.openclaw/plugins
git clone https://github.com/zuiho-kai/openclaw-semantic-memory.git semantic-memory
cd semantic-memory
npm install
```

### 安装要求

**首次运行准备：**

1. **Node.js 版本**: 需要 Node.js ≥18.17
   ```bash
   node --version  # 检查版本
   ```

2. **构建工具**（用于编译原生依赖）:
   - **Windows**: Visual Studio Build Tools
     ```powershell
     npm install --global windows-build-tools
     ```
   - **macOS**: Xcode Command Line Tools
     ```bash
     xcode-select --install
     ```
   - **Linux**: build-essential
     ```bash
     sudo apt-get install build-essential  # Debian/Ubuntu
     sudo yum groupinstall "Development Tools"  # RHEL/CentOS
     ```

3. **网络访问**:
   - 安装时需要访问 npmjs.com 下载依赖包
   - 首次运行时会从 huggingface.co 下载 embedding 模型（约 25MB）
   - 如果配置了外部 Qdrant 服务器，需要能访问该服务器

4. **原生依赖**:
   - `sharp`: 图像处理库（可能需要编译）
   - `onnxruntime`: ML 推理引擎（可能需要编译）
   - `undici`: HTTP 客户端（通过 @qdrant/js-client-rest 引入）

### 推荐安装方式

```bash
# 使用 npm ci 确保可重现的安装（推荐用于生产环境）
npm ci

# 或者分步安装（用于调试）
npm install --ignore-scripts  # 跳过 post-install 脚本
npm rebuild                    # 然后重新构建原生模块
```

### 故障排除

**问题: 原生模块编译失败**
- 确保已安装对应平台的构建工具
- 尝试清理缓存: `npm cache clean --force`
- 删除 node_modules 重新安装: `rm -rf node_modules && npm install`

**问题: 模型下载失败**
- 检查网络连接和防火墙设置
- 确保能访问 huggingface.co
- 模型会缓存在 `~/.cache/huggingface/` 目录

**问题: Node 版本不兼容**
- 升级到 Node.js 18.17 或更高版本
- 使用 nvm 管理多个 Node 版本: `nvm install 18 && nvm use 18`

## 配置

在 OpenClaw 配置文件中启用插件：

```json
{
  "plugins": {
    "semantic-memory": {
      "enabled": true,
      "autoCapture": false,  // 默认关闭，需要时手动开启
      "autoRecall": true,
      "captureMaxChars": 500
    }
  }
}
```

### 配置选项

- **qdrantUrl** (可选): 外部 Qdrant 服务地址，留空使用内存模式
- **persistToDisk** (默认 true): 在内存模式下将记忆保存到磁盘
  - 数据存储在 `~/.openclaw-memory/` 目录（或自定义路径）
  - 重启后数据不会丢失
  - 设置为 false 使用纯内存模式（重启后清空）
  - 仅在内存模式下生效（未配置 qdrantUrl 时）
- **storagePath** (可选): 自定义存储目录
  - 留空使用默认路径 `~/.openclaw-memory/`
  - 支持 `~` 符号表示用户主目录
  - 仅在 `persistToDisk: true` 时生效
- **autoCapture** (默认 false): 自动记录对话内容
  - ⚠️ **隐私保护**: 默认会跳过包含 PII（邮箱、电话号码）的文本
  - 需要配合 `allowPIICapture` 才能捕获 PII
- **allowPIICapture** (默认 false): 允许捕获包含 PII 的文本
  - ⚠️ **隐私风险**: 仅在理解隐私影响后启用
  - 需要 `autoCapture` 同时启用才生效
- **autoRecall** (默认 true): 自动注入相关记忆到对话
- **captureMaxChars** (默认 500): 单条记忆最大字符数
- **maxMemorySize** (默认 1000): 内存模式下的最大记忆条数
  - 仅在内存模式下生效（未配置 qdrantUrl 时）
  - 达到上限时自动删除最旧的记忆（LRU 淘汰策略）
  - 范围：100-1000000 条
  - 设置为 999999 表示无限制（不会自动删除旧记忆）
  - ⚠️ 无限制模式可能导致内存耗尽，请谨慎使用
  - 外部 Qdrant 模式不受此限制

## 隐私与安全

### 数据存储

- **磁盘持久化**（默认）: 数据保存到 `~/.openclaw-memory/` 并在重启后恢复
  - 设置 `persistToDisk: false` 可切换到纯内存模式（重启后清空）
- **Qdrant 模式**: 如果配置了 `qdrantUrl`，数据会发送到该服务器
  - ⚠️ 仅配置受信任的 Qdrant 服务器
  - 建议使用本地 Qdrant 实例或专用服务账户

### 网络访问

- **首次运行**: Transformers.js 会从 Hugging Face 下载模型文件（约 25MB）
- **运行时**: 内存模式无网络请求；Qdrant 模式会连接配置的服务器

### 自动捕获

- **autoCapture** 默认关闭，需要手动开启
- **PII 保护**: 默认情况下，即使启用 autoCapture，包含邮箱或电话号码的文本也会被自动跳过
- **allowPIICapture**: 设置为 true 才能捕获包含 PII 的文本
  - ⚠️ **仅在理解隐私风险后启用**
  - 适用场景：个人笔记、测试环境
  - 不适用场景：共享环境、生产环境、处理他人数据
- 建议仅在个人环境使用，避免在共享或生产环境开启

### 建议

1. 首次使用时在隔离环境测试
2. 审查 `index.js` 了解数据处理逻辑
3. 敏感环境建议锁定依赖版本（`npm ci`）
4. 定期检查存储的记忆内容

## 使用

插件提供三个工具：

### memory_store
保存重要信息到长期记忆：

```javascript
memory_store({
  text: "用户喜欢用 Opus 处理复杂任务",
  category: "preference",
  importance: 0.8
})
```

### memory_search
搜索相关记忆：

```javascript
memory_search({
  query: "工作流程",
  limit: 5
})
```

### memory_forget
删除特定记忆：

```javascript
memory_forget({
  memoryId: "uuid-here"
})
// 或通过搜索删除
memory_forget({
  query: "要删除的内容"
})
```

## 技术细节

### 架构

- **向量数据库**: Qdrant (内存模式)
- **Embedding 模型**: Xenova/all-MiniLM-L6-v2 (本地运行)
- **模块系统**: ES6 modules

### 关键实现

插件使用**工厂函数模式**导出工具，确保与 OpenClaw 的工具系统兼容：

```javascript
export default {
  name: 'semantic-memory',
  version: '1.0.0',
  tools: [
    () => ({
      name: 'memory_search',
      description: '...',
      parameters: { ... },
      execute: async (params) => { ... }
    })
  ]
}
```

### 常见问题

**Q: 为什么要用工厂函数？**

A: OpenClaw 的工具系统会调用 `tool.execute()`，直接导出对象会导致 `tool.execute is not a function` 错误。工厂函数确保每次调用都返回新的工具实例。

**Q: 为什么要用 ES6 modules？**

A: OpenClaw 的插件加载器期望 ES6 模块格式。需要在 `package.json` 中设置 `"type": "module"`。

**Q: 数据存储在哪里？**

A: 内存模式下数据仅在进程运行期间保存。重启后需要重新索引。未来版本会支持持久化存储。

## 开发

```bash
# 安装依赖
npm install

# 测试（需要 OpenClaw 环境）
openclaw gateway restart
```

## 许可证

MIT

## 致谢

- [Qdrant](https://qdrant.tech/) - 向量数据库
- [Transformers.js](https://huggingface.co/docs/transformers.js) - 本地 ML 推理
- [OpenClaw](https://openclaw.ai/) - AI 助手框架
