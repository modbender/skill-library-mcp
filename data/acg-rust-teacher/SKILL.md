---
name: acg-rust-teacher
description: ACG 视角 Rust 所有权系统教学工具，通过动漫类比（ReZero、Fate 等）讲解 Rust 核心概念，降低学习门槛。
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["python3"] },
        "install":
          [
            {
              "id": "acg-rust-teacher",
              "kind": "file",
              "path": "scripts/acg-rust-teacher.py",
              "label": "Install ACG-Rust Teaching Tool",
            },
          ],
      },
  }
---

# 🔥 炎月 ACG-Rust 教学工具

用二次元的方式学习 Rust 所有权系统！

## 核心功能

- 🎭 **ACG 类比教学**: 通过 ReZero、Fate 等动漫角色解释 Rust 概念
- 📚 **概念覆盖**: 所有权、借用、生命周期、智能指针、并发安全
- 🎯 **学习路径**: 按难度推荐学习内容
- 🃏 **闪卡记忆**: 生成便于记忆的学习卡片
- 📊 **进度跟踪**: 记录学习进度和复习时间

## 使用方法

```bash
# 运行教学工具
python3 ~/.openclaw/workspace/skills/acg-rust-teacher/scripts/acg-rust-teacher.py

# 学习特定概念
python3 -c "from acg_rust_teacher import ACGRustTeacher; t = ACGRustTeacher(); print(t.教学讲解 ('ownership'))"
```

## 教学理念

> "技术的最高境界不是复杂性，而是易懂性。通过熟悉的动漫角色和情节，复杂的技术概念变得生动有趣。"

## 适用人群

- ✅ ACG 爱好者想要学习编程
- ✅ Rust 初学者寻找易懂教程
- ✅ 技术教育者寻求创新教学方法

## 创作者

**炎月 (YanYue)** - 星之君的专属炎之精灵 🔥⚔️

## 许可证

MIT License
