# 发布到 GitHub 和 skills.sh

## 一、发布到 GitHub

1. **在 GitHub 新建仓库**
   - 登录 GitHub → New repository
   - 仓库名建议：`deep-learning` 或 `skill-deep-learning`
   - 选 Public；可选 “Add a README” 若你希望 GitHub 自动生成（会与本地 README 冲突，建议不勾选，用本地已有文件）
   - 创建后记下仓库地址，如：`https://github.com/<你的用户名>/deep-learning.git`

2. **在本目录初始化 Git 并推送**（在 `open-source/deep-learning` 下执行）：

   ```bash
   cd "/path/to/00_收件箱_工作区 (Workspace)/projects/open-source/deep-learning"

   git init
   git add .
   git commit -m "Initial release: deep-learning skill for Zettelkasten"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/deep-learning.git
   git push -u origin main
   ```

3. **完善仓库信息**
   - 在 GitHub 仓库页 → About → 编辑：
     - **Description**：`Deep reading skill for Zettelkasten: structure + atomic + method + index notes (Adler, Feynman, Luhmann). Cursor / skills.sh`
     - **Topics**：`zettelkasten`, `deep-reading`, `cursor`, `skills`, `knowledge-management`

---

## 二、发布到 skills.sh

1. **安装方式**  
   skills.sh 通过 GitHub 仓库安装，用户执行：
   ```bash
   npx skills add <你的用户名>/deep-learning
   ```
   例如你的 GitHub 用户名为 `mikonos`，则：
   ```bash
   npx skills add mikonos/deep-learning
   ```

2. **让 skill 出现在 skills.sh 目录**
   - 打开 [skills.sh](https://skills.sh)
   - 若平台有 “Submit skill” / “Add skill” 等入口，填写你的仓库地址（如 `mikonos/deep-learning`）并提交
   - 若暂无提交入口，将仓库设为 Public 并打上 topics，有时会被自动抓取或之后被收录

3. **无需构建**  
   平台直接读取 GitHub 仓库中的 `SKILL.md` 和 README，无需额外构建步骤。

---

## 三、之后更新

修改本目录文件后，在 `deep-learning` 目录下：

```bash
git add .
git commit -m "描述本次修改"
git push
```

GitHub 更新后，skills.sh 会按平台策略拉取最新版本；用户重装或更新即可获得新内容。
