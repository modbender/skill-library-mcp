---
name: nl2ms-ui
description: 根据自然语言通过midscene的api生成midscene脚本，可以生成web端、Android端、iOS端和PC端的midscene脚本。当用户提及生成脚本，android脚本、iOS脚本、web脚本、PC脚本时使用。
---

# Midscene 脚本生成技能

## 何时使用此技能

当用户需要生成以下类型的自动化测试脚本时使用此技能：
- **Android 脚本**：Android 移动端应用的自动化测试脚本
- **iOS 脚本**：iOS 移动端应用的自动化测试脚本
- **Web 脚本**：Web 浏览器的自动化测试脚本
- **PC 脚本**：桌面端应用的自动化测试脚本

## 平台支持

### 1. Android 端

- **YAML 示例**：`references/examples-android-yaml.md`
- **TypeScript 示例**：`references/examples-android-ts.md`

---

### 2. iOS 端

- **YAML 示例**：`references/examples-ios-yaml.md`
- **TypeScript 示例**：`references/examples-ios-ts.md`

---

### 3. Web 端

- **YAML 示例**：`references/examples-web-yaml.md`
- **TypeScript 示例**：`references/examples-web-ts.md`

---

### 4. PC 端

- **YAML 示例**：`references/examples-pc-yaml.md`
- **TypeScript 示例**：`references/examples-pc-ts.md`

---

## 最佳实践

1. **明确指定平台**：生成脚本时明确目标平台（Android/iOS/Web/PC）
2. **使用描述性步骤名称**：为每个步骤提供清晰的名称和描述
3. **合理使用等待**：优先使用 `aiWaitFor` 而非固定 `sleep`
4. **错误处理**：使用 `continueOnError: true` 或 try-catch 处理可选步骤
5. **验证断言**：在关键步骤后添加断言验证操作成功
6. **环境配置**：使用 `.env` 管理 API 密钥，设置合适的 `aiActionContext`

---

## 参考资源

- **API 参考**：`references/midscene-api`
- **详细示例**：
  - Android: 
    - YAML: `references/examples-android-yaml.md`
    - TypeScript: `references/examples-android-ts.md`
  - iOS: 
    - YAML: `references/examples-ios-yaml.md`
    - TypeScript: `references/examples-ios-ts.md`
  - Web: 
    - YAML: `references/examples-web-yaml.md`
    - TypeScript: `references/examples-web-ts.md`
  - PC: 
    - YAML: `references/examples-pc-yaml.md`
    - TypeScript: `references/examples-pc-ts.md`
- **常见场景**：`references/common-scenarios.md`
- **官方文档**：https://midscenejs.com/api.html
