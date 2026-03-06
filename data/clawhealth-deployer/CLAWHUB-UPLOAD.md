# ClawHub 上传 Skill 所需材料与步骤

在 ClawHub 上传 **ClawHealth Deployer** 时，按下面准备和执行即可。

---

## 一、上传前你要准备的东西

| 材料 | 说明 | 状态 |
|------|------|------|
| **ClawHub 账号** | 在 [clawhub.ai](https://clawhub.ai/) 注册并登录 | 需自行完成 |
| **GitHub 账号** | 账号注册时间 ≥ 7 天才能发布（ClawHub 要求） | 需自行确认 |
| **Node.js 环境** | 用于执行 `clawhub` CLI（建议 Node 18+） | 需本机已安装 |
| **本 skill 目录** | 即 `clawhub/clawhealth-deployer/` 整个文件夹 | 已就绪 |

---

## 二、Skill 包里会包含的文件（无需再改）

这些都会被打包上传，保持现状即可：

```
clawhub/clawhealth-deployer/
├── SKILL.md              # 必填：技能说明与 frontmatter（name, description, metadata）
├── README.md             # 推荐：用户/开发者说明
├── scripts/
│   ├── install.sh       # 安装脚本（clone + deploy-openclaw + merge MCP）
│   └── merge-mcp.js     # 合并 MCP 配置到 clawdbot.json5
├── package.json         # merge-mcp.js 的依赖（json5）
├── .gitignore           # 忽略 node_modules
└── CLAWHUB-UPLOAD.md    # 本说明（可选，不影响发布）
```

**注意：** 发布前不要提交 `node_modules/`（已在 `.gitignore` 中）。

---

## 三、发布命令（在仓库根目录或 skill 目录执行）

### 1. 安装 ClawHub CLI 并登录

```bash
npm i -g clawhub
# 或: pnpm add -g clawhub

clawhub login
```

按提示在浏览器完成登录（或使用 `clawhub login --token <token>`）。

### 2. 进入 skill 目录并发布

```bash
cd clawhub/clawhealth-deployer

clawhub publish . \
  --slug clawhealth-deployer \
  --name "ClawHealth Deployer" \
  --version 1.0.0 \
  --tags latest
```

如需写一句版本说明（changelog）：

```bash
clawhub publish . \
  --slug clawhealth-deployer \
  --name "ClawHealth Deployer" \
  --version 1.0.0 \
  --tags latest \
  --changelog "Initial release: deploy ClawHealth backend and connect MCP for OpenClaw."
```

### 3. 之后更新版本

改版本号再发一次即可，例如：

```bash
clawhub publish . \
  --slug clawhealth-deployer \
  --name "ClawHealth Deployer" \
  --version 1.0.1 \
  --tags latest \
  --changelog "Fix merge path on Windows."
```

---

## 四、SKILL.md 里已写明的信息（供审核参考）

- **name:** `clawhealth-deployer`
- **description:** 部署 ClawHealth 并接入 OpenClaw；用户通过 iOS App（SDK）连接数据；不安装 OpenClaw，需用户已有 OpenClaw。
- **metadata.openclaw.requires.bins:** `docker`, `git`, `make`, `node`
- **metadata.openclaw.emoji:** ❤️

ClawHub 会解析 `SKILL.md` 的 frontmatter 做展示和校验。

---

## 五、发布后建议检查

1. 在 [clawhub.ai](https://clawhub.ai/) 搜索 **ClawHealth** 或 **clawhealth-deployer**，确认技能已上架。
2. 在另一台已装 OpenClaw 的机器上执行：  
   `clawhub install clawhealth-deployer`  
   确认能安装且目录、脚本完整。
3. 在 OpenClaw 对话里说「部署 ClawHealth」或「install ClawHealth」，确认 agent 能按 SKILL.md 执行 `scripts/install.sh`。

---

## 六、若发布失败

- **权限 / 安全扫描**：ClawHub 可能做 VirusTotal 等扫描，确保脚本无恶意命令、不下载未信任二进制。
- **GitHub 账号年龄**：不满 7 天会限制发布，等满 7 天再试。
- **slug 冲突**：若提示 slug 已被占用，可改用 `clawhealth-deploy` 或加后缀（如 `clawhealth-deployer-ow`），并同步改 README 里的安装命令。

以上即上传 ClawHub 所需的全部材料和步骤。
