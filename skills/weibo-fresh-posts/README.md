# 微博关键信息不漏看（weibo-fresh-posts-skill）

这是一个面向中文用户的 OpenClaw Skill，核心要解决的痛点是：

- 关注的博主更新太快，经常错过关键微博
- 刷到的流不稳定，抓取结果不完整
- 记录里常把“抓取时间”误当“发帖时间”
- 发帖正文和摘要混在一起，后续复盘困难

本 Skill 的策略是：

- 强制先切到左侧「最新微博」时间线
- 以“发帖时间”入表（不是抓取时间）
- 发帖内容写原文正文，内容总结单独写摘要
- 按原始链接去重，按天写入本地 Markdown

## 本仓库内容

本仓库根目录就是 Skill 根目录，包含 `SKILL.md`。

## 本地安装（OpenClaw）

```bash
mkdir -p ~/.openclaw/workspace/skills
cp -R . ~/.openclaw/workspace/skills/weibo-fresh-posts
```

## 创建 10 分钟定时任务

```bash
./scripts/install_cron.sh 10m 20 weibo-fresh-posts
```

## 发布到 ClawHub

```bash
clawhub login
clawhub publish "$PWD" \
  --slug weibo-fresh-posts \
  --name "Weibo Timeline Monitor" \
  --version 0.1.4 \
  --tags latest,weibo,automation,zh-cn
```

说明：

- 在部分 `clawhub` CLI 版本里，`clawhub publish .` 可能误报 `SKILL.md required`。
- 使用绝对路径（`"$PWD"`）可规避这个问题。
