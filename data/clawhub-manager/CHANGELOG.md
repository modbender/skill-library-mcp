# ClawHub Manager 更新日志

All notable changes to the clawhub-manager skill will be documented in this file.

## [1.1.0] - 2026-02-22

### 🚀 新增功能

#### 🔒 自动安全扫描
- **发布前自动安全检查**：在发布技能到 ClawHub 前，自动扫描是否存在密钥泄露
- **支持检测多种密钥格式**：
  - Tavily API Key (tvly-...)
  - OpenAI API Key (sk-...)
  - GitHub Tokens (ghp_, gho_, ghu_, ghs_)
  - Perplexity API Key (pplx-...)
  - Exa AI API Key (exa_...)
  - 通用 API Key 模式
- **检测敏感文件**：.env, .secrets, *.key, *.pem
- **检测环境变量硬编码**：export API_KEY=, export SECRET=

#### 🛠️ 新增脚本
- **security-check.sh**：独立的安全检查脚本，可在发布前手动运行
- **test-security-scan.sh**：测试脚本，验证安全扫描功能

#### 📚 新增文档
- **SECURITY.md**：安全扫描功能使用指南
- 更新 **SKILL.md**：添加安全注意事项章节
- 更新 **.gitignore**：添加敏感文件模式

### ⚙️ 改进

- **发布流程优化**：安全扫描失败时会阻止发布，并提供修复建议
- **跳过选项**：添加 `--skip-security` 参数（不推荐，仅用于测试）

### 🔧 技术细节

- 使用 grep 正则表达式匹配常见密钥格式
- 检测范围：*.md, *.sh, *.py, *.js 文件
- 排除占位符（YOUR_API_KEY_HERE, your-api-key）

### 📖 使用示例

```bash
# 正常发布（自动安全扫描）
bash publish.sh /path/to/skill --version 1.0.0

# 手动安全检查
bash security-check.sh /path/to/skill

# 测试安全扫描功能
bash test-security-scan.sh

# 跳过安全扫描（不推荐）
bash publish.sh /path/to/skill --version 1.0.0 --skip-security
```

---

## [1.0.0] - 2026-02-21

### 🎉 首次发布

#### 功能特性
- ✅ 发布技能到 ClawHub
- ✅ 删除技能（软删除）
- ✅ 查询技能信息和统计
- ✅ 搜索技能
- ✅ 列出本地已安装的技能

#### 脚本
- publish.sh - 发布脚本
- delete.sh - 删除脚本
- inspect.sh - 查询脚本
- search.sh - 搜索脚本
- list.sh - 列表脚本

#### 文档
- SKILL.md - 技能说明
- README.md - 项目说明
- EXAMPLES.md - 使用示例

---

## 📊 版本规划

### 未来计划
- [ ] 支持批量发布多个技能
- [ ] 添加技能版本回滚功能
- [ ] 集成更多安全检查规则
- [ ] 支持自定义安全扫描规则
- [ ] 添加技能依赖检查

---

**维护者**: franklu0819-lang
**许可证**: MIT
