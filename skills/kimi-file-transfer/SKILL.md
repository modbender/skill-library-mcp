---
name: Kimi文件传输 | kimi-file-transfer
description: 将本地文件发送到Kimi对话中供用户下载。
---

# Kimi文件传输 | kimi-file-transfer

将本地文件发送到Kimi对话中供用户下载。

---

## 作者
**SC&Chongjie**

---

## 功能
- 将本地文件发送到当前Kimi对话
- 支持任意文件类型
- 每次最多5个文件

---

## 触发词
```
"发送文件给我"
"传输文件"
"文件到Kimi"
"上传文件到对话"
```

---

## 使用方法

### 方式1: 直接对话中请求
```
用户: SC，把 memory/db-ai-agent-strategy.md 发给我
SC: (自动调用工具传输文件)
```

### 方式2: 指定多个文件
```
用户: 把 these files 发给我: file1.md, file2.pdf
```

---

## 技术实现

```python
# 使用 kimi_upload_file 工具
kimi_upload_file(paths=["/path/to/file.md"])
```

---

## 适用场景

1. **文档共享**: 将本地Markdown/文档发送到对话
2. **素材传输**: 图片、PDF等文件快速传输
3. **代码分享**: 直接发送代码文件到对话

---

## 限制
- 每次最多5个文件
- 文件必须在本地可访问
- 支持任意文件类型

---

## 更新日志

### v1.0.0 (2026-02-28)
- 初始版本发布
- 支持单文件/多文件传输

---

## 联系作者
如有问题或建议，欢迎反馈！

*Skill by SC&Chongjie* 🤖
