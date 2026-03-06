# 角色信息图

三列式角色设计表，包含配色、三视图、换装、动态姿势和表情集。

## 规格

- **宽高比**: 16:9

## 必填信息

| 占位符 | 说明 | 必填 |
|--------|------|------|
| `{{gender}}` | 角色性别 | ✓ |
| `{{hair_color}}` | 发色 | ✓ |
| `{{eye_color}}` | 眼睛颜色 | ✓ |

## 使用要求

- **无需参考图片**：纯文生图模式
- 子代理需输出指定 JSON 格式，`layout` 部分保持不变

## 提示词模板

```
Character reference sheet, three-column layout, {{gender}} character with {{hair_color}} hair and {{eye_color}} eyes, grid paper background, clean anime style, professional design sheet
```

## 输出格式

子代理必须输出以下 JSON 格式：

```json
{
  "template": {
    "name": "三列式角色设计表",
    "layout": {
      "type": "三列布局",
      "columns": {
        "左列": {
          "width": "20%",
          "sections": [
            {
              "区域": "左上角",
              "name": "COLOR_PALETTE",
              "count": 6,
              "items": ["发色", "眼睛色", "肤色", "主服装色", "配饰色", "中性色"],
              "description": "角色核心配色方案"
            },
            {
              "区域": "左下角",
              "name": "ACCESSORIES",
              "count": 4,
              "items": ["头部配饰", "耳饰", "鞋履", "包袋"],
              "description": "标志性配饰单品展示"
            }
          ]
        },
        "中列": {
          "width": "50%",
          "sections": [
            {
              "区域": "主视觉区",
              "name": "MAIN_VIEWS",
              "count": 3,
              "items": ["正面", "侧面", "背面"],
              "description": "角色标准三视图，占比最大"
            }
          ]
        },
        "右列": {
          "width": "30%",
          "sections": [
            {
              "区域": "右上角",
              "name": "NEW_OUTFITS",
              "count": 2,
              "sub_count": 3,
              "items": ["换装A(正/侧/背)", "换装B(正/侧/背)"],
              "description": "两套替代服装，每套含三视图"
            },
            {
              "区域": "右中部",
              "name": "ACTION_POSES",
              "count": 3,
              "items": ["跳跃", "伸展", "行走"],
              "description": "动态姿势展示角色活力"
            },
            {
              "区域": "右下角",
              "name": "EXPRESSIONS",
              "count": 5,
              "items": ["微笑", "生气", "悲伤", "惊讶", "眨眼"],
              "description": "基础情绪表情集"
            }
          ]
        }
      }
    },
    "style": {
      "background": "方格纸底纹",
      "labels": "圆角青色标签栏",
      "art_style": "日系赛璐璐/平涂风格",
      "line_art": "清晰线稿，柔和阴影"
    }
  },
  "prompt_template": "Character reference sheet, three-column layout, {{gender}} character with {{hair_color}} hair and {{eye_color}} eyes, grid paper background, clean anime style, professional design sheet"
}
```
