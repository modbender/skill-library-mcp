# 发布 session-memory 到 ClawHub

## 1. 登录 ClawHub（首次发布前）

```bash
clawhub login
clawhub whoami
```

按提示在浏览器完成登录。

## 2. 发布

在 **skills 目录的上一级**（即 `~/.openclaw/workspace`）执行：

```bash
cd ~/.openclaw/workspace

clawhub publish ./skills/session-memory \
  --slug session-memory \
  --name "Session Memory" \
  --version 1.0.0 \
  --changelog "首次发布：会话摘要写入每日 memory 文件，支持按关键词/日期搜索会话历史"
```

说明：

- `./skills/session-memory`：当前目录下的 skill 文件夹（不要进到 session-memory 里再 publish）。
- `--slug session-memory`：其他人安装时用 `clawhub install session-memory`。
- 若 ClawHub 上已有官方 `session-memory` 且你想区分，可改用 `--slug session-memory-workspace` 等。

## 3. 其他人安装

```bash
clawhub install session-memory
# 或指定版本
clawhub install session-memory --version 1.0.0
```

默认会安装到 OpenClaw 的 skills 目录（或 `CLAWHUB_WORKDIR` 指定路径）。

## 4. 之后更新版本

改完代码后，提高版本号再发布，例如：

```bash
clawhub publish ./skills/session-memory \
  --slug session-memory \
  --name "Session Memory" \
  --version 1.1.0 \
  --changelog "增加 xxx 功能"
```

用户侧更新：`clawhub update session-memory`。
