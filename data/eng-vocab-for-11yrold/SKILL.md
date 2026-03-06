---
name: vocab-master
description: >
  小升初英语单词深度学习系统。当用户提供单词列表、时限和可用时间，或想要帮助孩子学习英语单词、制定单词学习计划、设计单词故事记忆法、出单词考核题目、查看复习提醒时，必须使用此skill。涵盖：单词故事串联、直接生成图文教学卡PNG、分级考核（听写/发音/用法）、遗忘曲线复习提醒、学习进度追踪与下一课调整。只要用户涉及"单词学习计划"、"单词故事"、"单词考核"、"复习提醒"、"小升初英语"等场景，必须触发此skill。
compatibility: "requires bash, create_file, present_files; pip: pillow matplotlib"
---

# Vocab Master — 小升初英语单词深度学习系统

## 核心理念

**故事串联 + 多感官记忆 + 科学间隔复习**，让孩子真正能：
1. **默写**（拼写正确）
2. **正确发音**（音标掌握）
3. **知道含义、词性、用法**（语境中使用）

---

## 第一步：收集输入参数

```
必填：
- 单词列表
- 总时限（如"3周后考试"）
- 每次可用时间（如"每天30分钟"）

选填：
- 孩子年龄/年级（默认：小学5-6年级）
- 薄弱环节（拼写/发音/记忆/用法）
- 过去测试成绩
```

---

## 第二步：制定学习计划总览

### 2.1 分析单词，构建故事世界

将所有单词按**语义场**分组（每组5-8个），为每组设计一个迷你故事场景：

```
故事设计原则：
- 场景具体有趣，贴近孩子生活（冒险、校园、科技、自然等）
- 每个单词在故事中都有"戏份"（动词做动作、名词是角色/道具）
- 故事结尾设悬念，引出下一组单词的故事
- 故事中的单词用【】标注
```

### 2.2 计算课时安排

```
总单词数 ÷ 每课单词数(5-8) = 总课数
总时限天数 ÷ 总课数 = 课间隔
每课时间分配：新课学习60% / 复习回顾30% / 自测10%
```

输出：**学习日历表**（日期、学习内容、复习内容、测验类型）

---

## 第三步：单节课教学内容

### 3.1 生成故事文本

输出完整故事（500-800字），所有本课单词用【word】标注，故事末设悬念。

### 3.2 直接生成教学卡图片（关键步骤）

**为每个单词用Python直接生成一张精美教学卡PNG，无需任何外部工具。**

#### 字体资源
字体文件位于 `/mnt/skills/examples/canvas-design/canvas-fonts/`，使用：
- 标题/单词：`BricolageGrotesque-Bold.ttf`
- 正文/例句：`WorkSans-Regular.ttf`（Bold变体也可用）
- 音标/标注：`DMMono-Regular.ttf`

> **中文字体**：场景图标题/预览文字中的中文，必须使用系统字体：
> `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`
> 在 matplotlib 中：
> ```python
> from matplotlib import font_manager
> font_manager.fontManager.addfont('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
> prop_cn = font_manager.FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')
> # 然后对所有中文text使用 fontproperties=prop_cn
> ```
> 在 Pillow 中，单词卡的中文（含义等）需同样使用此字体路径调用 `ImageFont.truetype`。

#### 教学卡设计规范（800×520px）

```
┌────────────────────────────────────────────┐
│ [8px顶部色条]                               │
│ [6px左侧竖条]                               │
│                                            │
│  WORD（64px加粗）   /音标/（DMMono）  [词性] │
│                                            │
│  ──────────────── 分割线 ─────────────────  │
│  ✦ ad-ven-ture（拼写分组）                  │
│  ★ 记忆联想（趣味拆字/故事法）               │
│                                            │
│  ──────────────── 分割线 ─────────────────  │
│  中文含义（26px加粗，主色）                  │
│  ① 简单例句                                │
│  ② 稍难例句                                │
│                                            │
│  ──────────────── 分割线 ─────────────────  │
│  📖 在本课故事中的角色                       │
│  ⚠ 易错提醒（红色）                         │
│                                            │
│ [6px底部色条]                               │
└────────────────────────────────────────────┘
```

#### 主题配色方案

```python
THEMES = {
    "adventure":  {"bg": "#1a1a2e", "accent": "#e94560", "text": "#eaeaea", "tag": "#f5a623"},
    "school":     {"bg": "#f0f4ff", "accent": "#3b5bdb", "text": "#1a1a2e", "tag": "#40c057"},
    "nature":     {"bg": "#e8f5e9", "accent": "#2e7d32", "text": "#1b2e1b", "tag": "#ff8f00"},
    "technology": {"bg": "#0d1117", "accent": "#58a6ff", "text": "#c9d1d9", "tag": "#3fb950"},
    "character":  {"bg": "#fff8f0", "accent": "#e67700", "text": "#2c1810", "tag": "#7048e8"},
}
```

#### 教学卡Python代码（完整实现）

```python
from PIL import Image, ImageDraw, ImageFont
import os

FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"

def load_font(name, size):
    path = os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, size)

def generate_word_card(word_data, theme, output_path):
    """
    word_data dict 必须包含：
      word, phonetic, pos, meaning, syllables,
      memory_tip, example1, example2, story_role,
      easy_error (可为空字符串)
    """
    W, H = 800, 520
    img = Image.new("RGB", (W, H), color=theme["bg"])
    draw = ImageDraw.Draw(img)

    accent = theme["accent"]
    text_col = theme["text"]
    tag_col = theme["tag"]

    # 顶部/底部色条
    draw.rectangle([0, 0, W, 8], fill=accent)
    draw.rectangle([0, H-6, W, H], fill=accent)
    # 左侧竖条
    draw.rectangle([0, 0, 6, H], fill=accent)

    # 单词
    f_word = load_font("BricolageGrotesque-Bold.ttf", 62)
    draw.text((44, 28), word_data["word"].upper(), font=f_word, fill=accent)

    # 音标
    f_phon = load_font("DMMono-Regular.ttf", 21)
    draw.text((46, 108), word_data["phonetic"], font=f_phon, fill=text_col)

    # 词性标签（圆角矩形）
    f_tag = load_font("WorkSans-Regular.ttf", 17)
    tag_text = word_data["pos"]
    draw.rounded_rectangle([672, 34, 758, 66], radius=10, fill=tag_col)
    draw.text((680, 42), tag_text, font=f_tag, fill="#ffffff")

    # 分割线
    def hline(y): draw.line([40, y, W-40, y], fill=accent, width=1)
    hline(143)

    # 拼写分组 & 记忆联想
    f_body = load_font("WorkSans-Regular.ttf", 19)
    draw.text((44, 156), "✦  " + word_data["syllables"], font=f_body, fill=text_col)
    draw.text((44, 184), "★  " + word_data["memory_tip"], font=f_body, fill=text_col)

    hline(222)

    # 中文含义
    f_cn = load_font("WorkSans-Regular.ttf", 25)
    draw.text((44, 234), word_data["meaning"], font=f_cn, fill=accent)

    # 例句
    f_ex = load_font("WorkSans-Regular.ttf", 16)
    draw.text((44, 272), "①  " + word_data["example1"], font=f_ex, fill=text_col)
    draw.text((44, 298), "②  " + word_data["example2"], font=f_ex, fill=text_col)

    hline(330)

    # 故事角色
    draw.text((44, 342), "📖  " + word_data["story_role"], font=f_ex, fill=text_col)

    # 易错提醒
    if word_data.get("easy_error"):
        draw.text((44, 370), "⚠  " + word_data["easy_error"], font=f_ex, fill="#ff6b6b")

    img.save(output_path, "PNG")
    return output_path
```

#### 故事场景插图（900×500px，matplotlib绘制）

每课生成1张场景图，要求：
- 根据故事主题绘制有氛围感的几何艺术背景（城堡/森林/太空/校园/海洋等）
- 中央展示本课全部关键词（每词带半透明色块背景，随机微旋转±5°）
- 顶部显示课程标题，底部显示故事第一句预览
- 背景必须有具体的几何图形（星星、树形、城垛、波浪等）而非纯色

**scene_type到背景图形的映射**（必须完整实现）：
```
castle  → 城垛轮廓 + 圆形月亮 + 星星散布
forest  → 三角形树群 + 地面色带 + 月亮/太阳
space   → 椭圆星球 + 圆点星星 + 轨道弧线
school  → 矩形建筑轮廓 + 窗格 + 放射阳光
ocean   → 波浪曲线 + 三角帆船 + 圆形太阳
```

#### 图片生成执行顺序

1. `pip install pillow matplotlib --break-system-packages -q`
2. 生成故事场景图 → `/home/claude/lesson_N_scene.png`
3. 循环生成每个单词的教学卡 → `/home/claude/lesson_N_word_X.png`
4. 全部复制到 `/mnt/user-data/outputs/`
5. 调用 `present_files` 展示（场景图排第一位）

---

## 第四步：分级考核设计

### 三级考核体系

#### 🥉 Level 1（每课结束当天）
```
1. 遮住中文说出单词含义（口头，家长确认）
2. 单词-中文连线（文字输出）
3. 听故事片段，指出单词位置
通过：正确率 ≥ 70%
```

#### 🥈 Level 2（第2天）
```
1. 看中文默写英文
2. 根据音标写单词
3. 选择正确例句（辨析用法）
4. 造句1条
通过：正确率 ≥ 80% + 发音家长确认
```

#### 🥇 Level 3（单元末综合测）
```
1. 完型填空（新故事填词）
2. 看场景图用5个以上单词描述
3. 口述故事（≥5词，有完整情节）
通过：综合 ≥ 85%
```

---

## 第五步：根据考核调整下一课

| 错误类型 | 调整策略 |
|---------|---------|
| 拼写错误多 | 下节课前先默写上节错误词 |
| 发音问题 | 音节分解朗读；建议用在线字典听音 |
| 词义混淆 | 重讲故事戏份；增加对比例句 |
| 用法不会 | 下节课前做填空热身；新课减少1-2词 |
| 整体良好 | 加速进度或提前Level 3 |

进度规则：
- 连续2课Level 1失败 → 每课减为4-5词，增加游戏环节
- 连续2课Level 2通过 → 提前单元综合测
- Level 3 < 70% → 本单元复习后再进入下单元

---

## 第六步：遗忘曲线复习系统

复习节点（详细参数见 `references/ebbinghaus.md`）：
```
第 1 天  → 快速复习5分钟（Level 1简化版）
第 3 天  → 中度复习10分钟（Level 2）
第 7 天  → 深度复习15分钟（Level 2-3混合）
第 14 天 → 巩固复习10分钟
第 30 天 → 长期确认5分钟
```

### 每日复习清单输出格式

```
📅 今天 [日期] 复习清单

🔴 紧急（超7天）：word1, word2 → 默写测试
🟡 常规（第3天）：word3, word4 → 连线游戏
🟢 巩固（第1天）：word5, word6 → 重读故事

⏱️ 预计时间：___分钟
```

### 特别训练（连续3次出错的词）

- Day 1：**画出**这个词的意思
- Day 2：**造3个**不同场景的句子
- Day 3：不看提示默写5次
- Day 4：在日常对话中**说出**含该词的话并记录

---

## 图片生成质量自检（每次生成后必查）

- [ ] 字体路径正确，无回退默认字体
- [ ] 单词卡：大号单词清晰，配色与主题一致
- [ ] 故事场景图：有具体背景图形（不是纯色背景加文字）
- [ ] 关键词在场景图中全部展示
- [ ] 图片已复制到 outputs 并调用 present_files

---

## 参考文件

- `references/ebbinghaus.md` — 遗忘曲线详细参数
- `references/assessment-templates.md` — 各Level考核题模板库
- `references/story-themes.md` — 故事主题库与词汇分组建议
