# Contributing to SafeExec

感谢你有兴趣贡献 SafeExec！🎉

## 如何贡献

### 报告问题

在 [GitHub Issues](https://github.com/OTTTTTO/safe-exec/issues) 中报告 bug 或提出功能请求。

**报告问题时请包含：**
- OpenClaw 版本
- SafeExec 版本
- 操作系统
- 重现步骤
- 期望行为 vs 实际行为

### 提交代码

1. **Fork 仓库**
   ```bash
   git clone https://github.com/OTTTTTO/safe-exec.git
   cd safe-exec
   ```

2. **创建功能分支**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **进行更改**
   - 遵循现有代码风格
   - 添加注释说明复杂逻辑
   - 更新相关文档

4. **测试**
   ```bash
   bash test.sh
   ```

5. **提交**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

6. **推送**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **开启 Pull Request**
   - 描述你的更改
   - 引用相关 issue
   - 确保所有测试通过

## 代码风格

- 使用 2 空格缩进
- 变量名使用小写+下划线
- 函数名使用小写+下划线
- 常量使用大写+下划线
- 添加注释说明复杂逻辑

## 测试

在提交 PR 前，请确保：
- [ ] 所有测试通过
- [ ] 代码符合风格指南
- [ ] 文档已更新（如果需要）
- [ ] README 已更新（如果添加了新功能）

## 许可证

提交代码即表示你同意将代码以 MIT 许可证发布。

---

再次感谢你的贡献！🙏
