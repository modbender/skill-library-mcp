# Git 推送指南

## 准备工作

确保已完成以下步骤：
1. ✅ 环境变量配置（BRAND_NAME 和 INVITE_CODE）
2. ✅ 代码已封装和整理
3. ✅ 文档已更新

## Git 推送命令

```bash
# 1. 进入项目目录
cd /Users/ai-efficient-center/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw/skills/openclaw-team

# 2. 查看当前状态
git status

# 3. 添加所有更改的文件
git add .

# 4. 提交更改
git commit -m "feat: 添加环境变量支持和白色极简UI

- 添加 BRAND_NAME 环境变量支持品牌名称自定义
- 添加 INVITE_CODE 环境变量支持邀请码自定义
- 重构前端为白色极简风格
- 添加独立的 index.html 文件
- 添加一键启动脚本 start.sh
- 添加 .env.example 配置示例
- 更新 README.md 文档
- 修复 upload.py 的 import 错误"

# 5. 推送到远程仓库
git push origin main

# 如果是首次推送或需要设置上游分支
# git push -u origin main
```

## 推送前检查清单

- [ ] 删除了 README-cn.md 和 README-en.md（已在 git status 中看到）
- [ ] 确认 .gitignore 正确配置
- [ ] 确认敏感信息（如 GATEWAY_TOKEN）不会被提交
- [ ] 确认 venv/ 目录不会被提交
- [ ] 测试过新的启动方式

## 可选：清理未跟踪的文件

```bash
# 查看将被删除的文件（不实际删除）
git clean -n

# 删除未跟踪的文件和目录
git clean -fd
```

## 验证推送

推送后访问你的 Git 仓库页面，确认：
1. 所有文件都已上传
2. README.md 显示正常
3. 没有敏感信息泄露
