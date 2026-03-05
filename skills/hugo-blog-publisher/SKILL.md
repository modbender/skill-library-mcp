---
name: hugo-blog-publisher
version: 1.0.0
description: 发布文章到 Hugo 博客。用于当用户说"发布博客"、"推送到blog"、"post to blog"、"发布文章"等。自动完成 front matter 渲染、<!--more--> 标记添加、git 推送流程。
---

# Hugo Blog Publisher

将 Markdown 文章发布到 Hugo 博客并推送到 GitHub。

## 自动读取配置

此 Skill 会自动尝试从以下位置读取博客配置：
1. 用户记忆文件（MEMORY.md / USER.md）中的博客域名、路径等
2. 博客目录下的 .git 配置

如果未找到配置，才询问用户。

## 使用前提

1. **本地运行**：此 Skill 需要在能够访问博客目录的机器上运行
2. **Git 配置**：确保机器上有 Git 和 GitHub 访问权限

## 发布流程

### 1. 分析内容

从用户提供的文章内容中自动提取：
- **标题**：从 front matter 或内容中提取
- **标签**：根据内容主题自动判断（如 AI → ["AI", "技术"]）
- **分类**：根据内容类型判断（如技术文章 → "技术"）

### 2. 生成文件名

- 格式: `content/posts/{date}-{slug}.md`
- 日期格式: `YYYY-MM-DD`
- slug: 标题转为 URL 友好格式（小写、连字符、去除特殊字符）

### 3. 渲染 Front Matter

```yaml
---
title: "文章标题"
date: YYYY-MM-DD
draft: false
tags: ["标签1", "标签2"]
categories: ["分类"]
---
```

**常用标签参考**（根据内容选择）:
- 技术: `AI`, `技术`, `编程`, `RAG`, `LLM`, `Agent`
- 生活: `生活`, `随想`, `摄影`, `旅行`
- 热点: `翻译`, `名人名言`, `Hacker News`, `科技`

**常用分类**: `技术`, `生活`, `思考`, `翻译`, `资源`

### 4. 添加 <!--more--> 截断标记

在第一段或导言后添加 `<!--more-->`，让列表页显示摘要。

位置通常在：
- 第一段结束后的空行
- 导言和正文之间

### 5. Git 推送

从博客目录自动检测 git 状态并推送：

```bash
cd {博客路径}
git add content/posts/{文件名}
git commit -m "新增：{文章标题}"
git push
```

如果 git push 需要认证，确保用户已配置 SSH key 或 git credentials。

### 6. 返回部署链接

告知用户文章已发布成功。

注意：不要硬编码域名，应该根据用户提供的博客信息返回相应链接。

## 使用示例

```
用户：帮我发布这篇blog（附文章内容）

系统自动完成：
1. 分析内容，提取标题、标签、分类
2. 生成文件名（日期+slug）
3. 添加 front matter 和 <!--more--> 标记
4. 检测博客目录并推送
5. 返回部署链接
```

## 注意事项

- slug 生成：英文直接用，中文可用拼音或英文关键词
- <!--more--> 位置：根据文章结构选择合适位置
- commit message：建议用 "新增:" 前缀
- 如果用户没有提供博客路径，默认用当前目录的 blog 子目录
