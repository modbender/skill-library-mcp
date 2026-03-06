# White Stone Memory

记忆系统 - 包含常识记忆、项目记忆、错题本和每日回顾。按需加载，避免记忆污染。

## 特性

- 🧠 4 类记忆分类
- 📂 Markdown 文件存储
- 🔍 可选向量搜索
- ⚡️ 按需加载

## 快速开始

```bash
# 初始化目录
mkdir -p memory/knowledge memory/projects memory/errors memory/daily
```

## 配置向量搜索（可选）

```yaml
memory:
  vector_search:
    enabled: true
```

详见 [SKILL.md](./SKILL.md)
