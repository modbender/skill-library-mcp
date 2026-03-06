# 提示词模板菜单

根据用户需求选择对应的提示词模板。

## 模板列表

| 类型 | 文件 | 宽高比 | 子代理 | 适用场景 |
|------|------|--------|--------|----------|
| 手绘信息图 | `stacks/infographic.md` | 16:9 | - | 知识点总结、概念可视化、学习笔记 |
| 角色信息图 | `stacks/character-sheet.md` | 16:9 | ✓ | 角色三视图、换装、表情、动态姿势 |
| 电商详情页 | `stacks/ecommerce.md` | 9:16 | ✓ | 产品详情页12图、卖点展示、转化页面 |
| 浮世绘闪卡 | `stacks/ukiyo-e-card.md` | 9:16 | - | 鬼灭风格卡牌、浮世绘角色卡、收藏卡设计 |
| 拍立得 | `stacks/polaroid.md` | 3:4 | - | instax mini 风格照片、需上传参考图 |
| 乐高小人 | `stacks/lego.md` | 3:4 | - | 乐高包装盒风格、人物玩具化、需参考图 |
| 极简线条图 | `stacks/minimal-comic.md` | 16:9 | - | 黑白漫画、极简速写、多格分镜 |
| 8位像素 | `stacks/pixel-art.md` | 1:1 | - | 像素logo、拼豆图案、复古街机风格 |
| 美妆分镜 | `stacks/beauty-storyboard.md` | 1:1 | ✓ | 九宫格分镜、美妆广告、产品使用流程 |

> **子代理列**：✓ 表示需要委派子代理生成提示词，- 表示直接填写模板占位符即可

## 选择指南

- **用户提到信息图、知识可视化、手绘风格** → infographic.md
- **用户提到角色三视图、角色信息图** → character-sheet.md
- **用户提到产品详情页** → ecommerce.md
- **用户提到浮世绘、闪卡** → ukiyo-e-card.md
- **用户提到拍立得、胶片照片** → polaroid.md
- **用户提到乐高小人** → lego.md
- **用户提到极简线条图** → minimal-comic.md
- **用户提到像素、8-bit、拼豆** → pixel-art.md
- **用户提到美妆、九宫格、广告分镜** → beauty-storyboard.md
- **其他场景** → 直接根据用户描述构造提示词
