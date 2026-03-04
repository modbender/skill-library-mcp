---
name: moments-writer-lite
version: 1.0.0
description: 朋友圈文案生成器（精简版），基于私域变现核心方法论
tags: [wechat, moments, copywriting, 朋友圈, 私域, 文案]
author: Claude Code Assistant
commands:
  - name: moments
    description: 生成朋友圈文案
    parameters:
      - name: type
        description: 文案类型
        required: true
      - name: topic
        description: 文案主题
        required: false
    examples:
      - usage: /moments professional 咨询场景
        description: 专业型
      - usage: /moments warm 亲子时光
        description: 温暖型
      - usage: /moments counter 补课谎言
        description: 反认知
---

# 朋友圈写作助手 Lite

基于**麦肯锡信任公式**的朋友圈文案生成器：

```
信任 = (专业度 × 可靠度 × 亲密度) / 自身利益
```

## 支持的文案类型

| 命令 | 说明 | 公式 |
|------|------|------|
| `/moments professional` | 专业型：建立权威 | 故事案例 + 细节 + 美好结果 |
| `/moments reliable` | 靠谱型：建立信任 | 失败故事 + 不服输过程 + 成功结果 |
| `/moments warm` | 温暖型：建立亲密度 | 生活场景 + 真实互动 + 情感连接 |
| `/moments altruistic` | 利他型：降低防御 | 事件 + 细节 + 解释 + 价值观/金句 |
| `/moments counter` | 反认知破圈 | 打破认知 + 植入理念 |
| `/moments target` | 圈用户 | 筛选目标人群 + 建立边界 |
| `/moments intro_100` | 自我介绍100字 | 深耕领域 + 踩坑经验 + 价值钩子 |

## 排版规范

- 第一段：20-25字以内，场景化切入
- 段落：每段不超过3行，段间空一行
- 配图：使用1、4、9张图
- 评论区：营销信息放评论区

## 使用示例

```
/moments professional 户外咨询场景
/moments warm 孩子说妈妈真好
/moments counter 补课就能提分是谎言
/moments intro_100 我的核心价值
```
