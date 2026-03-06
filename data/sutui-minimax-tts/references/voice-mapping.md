# 音色匹配规则

MiniMax 提供 **303 个系统音色**，支持多种语言和角色类型。

## 获取完整音色列表

调用 MCP 工具获取实时音色列表：

```json
{
  "server": "user-速推AI",
  "toolName": "list_voices",
  "arguments": {}
}
```

本地数据源：[minimax_voices.json](minimax_voices.json)（同目录下）

## 音色统计

| 分类 | 数量 | 说明 |
|-----|------|-----|
| 男性音色 | 76 | 包含青年、中年、老年 |
| 女性音色 | 60 | 包含少女、御姐、成熟女性 |
| 儿童音色 | 11 | 男童、女童 |
| 多语言 | 156+ | 韩文、日文、英文、粤语等 |

## 常用中文音色（快速参考）

### 男性音色

| 音色 ID | 音色名称 | 适用角色 |
|---------|---------|---------|
| `male-qn-qingse` | 青涩青年音色 | 年轻男性、学生 |
| `male-qn-jingying` | 精英青年音色 | 成熟男性、职场精英 |
| `male-qn-badao` | 霸道青年音色 | 霸道总裁、强势男 |
| `male-qn-daxuesheng` | 青年大学生音色 | 大学生 |
| `junlang_nanyou` | 俊朗男友 | 恋爱男主 |
| `chunzhen_xuedi` | 纯真学弟 | 学弟、阳光男生 |
| `lengdan_xiongzhang` | 冷淡学长 | 高冷学长 |
| `badao_shaoye` | 霸道少爷 | 霸道少爷、富二代 |
| `bingjiao_didi` | 病娇弟弟 | 病娇角色 |
| `Chinese (Mandarin)_Gentleman` | 温润男声 | 温柔绅士 |
| `Chinese (Mandarin)_Humorous_Elder` | 搞笑大爷 | 老年幽默角色 |
| `Chinese (Mandarin)_Male_Announcer` | 播报男声 | 新闻播报 |

### 女性音色

| 音色 ID | 音色名称 | 适用角色 |
|---------|---------|---------|
| `female-shaonv` | 少女音色 | 少女、年轻女性 |
| `female-yujie` | 御姐音色 | 御姐、成熟职场女 |
| `female-chengshu` | 成熟女性音色 | 成熟女性、妈妈 |
| `female-tianmei` | 甜美女性音色 | 甜美女生 |
| `tianxin_xiaoling` | 甜心小玲 | 甜心女生 |
| `qiaopi_mengmei` | 俏皮萌妹 | 俏皮活泼女生 |
| `wumei_yujie` | 妩媚御姐 | 妩媚成熟女性 |
| `diadia_xuemei` | 嗲嗲学妹 | 撒娇学妹 |
| `danya_xuejie` | 淡雅学姐 | 温柔学姐 |
| `Chinese (Mandarin)_Warm_Bestie` | 温暖闺蜜 | 闺蜜角色 |
| `Chinese (Mandarin)_Gentle_Senior` | 温柔学姐 | 温柔学姐 |

### 儿童音色

| 音色 ID | 音色名称 | 适用角色 |
|---------|---------|---------|
| `clever_boy` | 聪明男童 | 聪明小男孩 |
| `cute_boy` | 可爱男童 | 可爱小男孩 |
| `lovely_girl` | 萌萌女童 | 可爱小女孩 |

### 特殊音色

| 音色 ID | 音色名称 | 适用场景 |
|---------|---------|---------|
| `cartoon_pig` | 卡通猪小琪 | 卡通动画配音 |
| `Robot_Armor` | 机械战甲 | 机器人、科幻角色 |
| `Chinese (Mandarin)_Radio_Host` | 电台男主播 | 电台播音 |
| `Chinese (Mandarin)_News_Anchor` | 新闻女声 | 新闻播报 |

## 多语言音色

| 语言 | 数量 | 示例音色 |
|-----|------|---------|
| 韩文 | 49 | 包含各年龄段 |
| 日文 | 15 | 包含男女声 |
| 英文 | 6 | 英式、美式发音 |
| 粤语 | 6 | 港式粤语 |
| 西班牙文 | 47 | 拉丁美洲口音 |
| 葡萄牙文 | 73 | 巴西口音为主 |

## 匹配策略

### 按年龄匹配

- **儿童** (child): `clever_boy`, `cute_boy`, `lovely_girl`
- **青年** (young): `male-qn-qingse`, `female-shaonv`, `chunzhen_xuedi`, `danya_xuejie`
- **中年** (middle): `male-qn-jingying`, `female-yujie`, `female-chengshu`
- **老年** (elder): `Chinese (Mandarin)_Humorous_Elder`, `Chinese (Mandarin)_Kind-hearted_Elder`

### 按性格匹配

- **活泼开朗**: `male-qn-qingse`, `female-shaonv`, `qiaopi_mengmei`
- **稳重成熟**: `male-qn-jingying`, `female-yujie`, `lengdan_xiongzhang`
- **霸气强势**: `male-qn-badao`, `badao_shaoye`, `wumei_yujie`
- **温柔甜美**: `female-tianmei`, `tianxin_xiaoling`, `diadia_xuemei`
- **冷淡高冷**: `lengdan_xiongzhang`, `danya_xuejie`

### 按场景匹配

| 场景 | 推荐男性音色 | 推荐女性音色 |
|-----|-------------|-------------|
| 校园对话 | `male-qn-daxuesheng`, `chunzhen_xuedi` | `female-shaonv`, `danya_xuejie` |
| 商务会议 | `male-qn-jingying`, `Chinese (Mandarin)_Reliable_Executive` | `female-yujie` |
| 恋爱甜蜜 | `junlang_nanyou` | `tianxin_xiaoling`, `diadia_xuemei` |
| 家庭对话 | `male-qn-jingying` | `female-chengshu` |
| 儿童故事 | `clever_boy`, `cute_boy` | `lovely_girl` |
| 新闻播报 | `Chinese (Mandarin)_Male_Announcer` | `Chinese (Mandarin)_News_Anchor` |
| 电台主播 | `Chinese (Mandarin)_Radio_Host` | `Chinese (Mandarin)_Warm_Bestie` |
