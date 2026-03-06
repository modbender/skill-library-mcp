---
name: bird-info
description: Query bird information from dongniao.net using web_fetch. Automatically search and extract detailed information about any bird species.
emoji: 🐦
metadata:
  openclaw:
    requires:
      bins: ["python3"]
    version: "2.0.0"
    author: "OpenClaw"
    category: "knowledge"
    tags: ["bird", "wildlife", "taxonomy", "nature", "dongniao"]
---

# Bird Info Skill v2.0

Query bird information from [Dongniao](https://dongniao.net) - China's comprehensive bird taxonomy website.

**Updated**: Now uses `web_fetch` for lightweight, reliable data extraction without browser automation.

## What This Skill Does

Automatically finds and extracts detailed information about any bird species from the Dongniao taxonomy database.

### Workflow

1. **Receive Query**: User provides bird name (Chinese or English)
2. **Fetch Taxonomy**: Downloads the dongniao.net taxonomy page
3. **Search**: Finds the matching bird entry using fuzzy matching
4. **Extract**: Fetches the bird's detail page
5. **Parse**: Extracts structured information (basic info, features, habitat, distribution, conservation)
6. **Format**: Returns clean, readable output

### Core Capabilities

#### 1. Multi-Language Support
- **Chinese names**: 麻雀，喜鹊，丹顶鹤
- **English names**: Sparrow, Magpie, Red-crowned Crane
- **Scientific names**: Passer domesticus, Pica pica

#### 2. Smart Matching
- Fuzzy matching for partial names
- Case-insensitive comparison
- Handles name variations
- Prioritizes Chinese name matches

#### 3. Information Extraction
Extracts from detail pages:
- **Basic Info**: 中文名，英文名，学名，科属
- **Features**: 外形特征，鸣叫特征
- **Habitat**: 生活习性，栖息环境
- **Distribution**: 分布区域，地理分布
- **Conservation**: 保护状况，IUCN 评级

#### 4. Clean Output
- Structured sections with emoji headers
- Concise summaries (truncated if too long)
- Source attribution

## Usage

### Via Conversation (Recommended)

Simply ask in natural language:

```
请帮我查一下麻雀的详细信息
```

```
绿孔雀的分布区域是什么？
```

```
丹顶鹤的保护状况如何？
```

```
查询 Aquila chrysaetos 的信息
```

### Command Line

```bash
# Query by Chinese name
python3 scripts/bird_info_skill.py 麻雀

# Query by English name
python3 scripts/bird_info_skill.py Sparrow

# Query by scientific name
python3 scripts/bird_info_skill.py "Passer domesticus"
```

### Example Output

```
==================================================
🐦 非洲鸵鸟 - 鸟类详细信息
   Common Ostrich (Struthio camelus)
==================================================

📌 基本信息
------------------------------
   中文名：非洲鸵鸟
   英文名：Common Ostrich
   学名：Struthio camelus
   科属：鸵鸟科

📖 形态特征
------------------------------
   外形特征：雄性非洲鸵鸟高达 2.75 米，重达 156 千克；雌鸟较小，高约 1.9 米...
   鸣叫特征：雄性非洲鸵鸟发出深沉的"boom"声，用于宣告领地和展示...

🌿 生活习性
------------------------------
   非洲鸵鸟栖息于多种开阔地带，包括沙漠到稀树草原。它们可能定居或游荡...

🌍 分布区域
------------------------------
   非洲鸵鸟广泛分布于非洲的西部、中部、东部和西南部，包括干旱、半干旱地区...

⚠️ 保护状况
------------------------------
   IUCN：LC (无危)

==================================================
📊 数据来源：懂鸟 (https://dongniao.net)
```

## Technical Implementation

### Architecture

```
┌─────────────────┐
│   User Query    │
│  (bird name)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  BirdInfoSkill  │
│   (Python)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   web_fetch     │
│  (taxonomy)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Search & Match │
│  (fuzzy logic)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   web_fetch     │
│   (details)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse & Format │
│   (regex)       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Formatted Output│
└─────────────────┘
```

### Key Components

**bird_info_skill.py**: Main implementation
- `BirdInfoSkill` class
- `web_fetch()` integration
- Fuzzy matching algorithm
- Content parser
- Output formatter

### Page Structure

**Taxonomy Page** (`/taxonomy.html`):
```
[中文名](/nd/id/中文名/英文名/英文名)
[英文名](/nd/id/中文名/英文名/英文名)
[学名](/nd/id/中文名/英文名/英文名)
```

**Detail Page** (`/nd/id/...`):
- Title: 中文名 - 英文名 - 学名
- First paragraph: Basic info (中文名，英文名，学名，科属)
- Sections: 外形特征，鸣叫特征，生活习性，生长繁殖，区别辨识，保护现状，地理分布

### Matching Algorithm

1. Normalize input (remove punctuation, lowercase)
2. Parse taxonomy page for all bird entries
3. For each entry:
   - Check Chinese name match (weight: 10)
   - Check English name match (weight: 8)
   - Check scientific name match (weight: 8)
4. Return highest scoring match

## Error Handling

### Common Issues

**Bird Not Found**
```
❌ 未找到鸟类 'xxx'

建议：
1. 检查鸟名拼写
2. 尝试使用中文名或英文名
3. 该鸟可能不在懂鸟数据库中
```

**Network Error**
```
❌ 无法获取分类页面
```

**Parse Error**
```
❌ 无法获取 xxx 的详细信息
```

### User Feedback

- Clear error messages in Chinese
- Actionable suggestions
- Source attribution

## Integration

### With Other Skills

**Combine with Image Generation**
```
请帮我查一下丹顶鹤的信息，然后生成一张它的图片
```

**Combine with Translation**
```
请查一下绿孔雀的详细信息，然后把关键点翻译成英文
```

## Limitations

### Current Constraints

- **Database Scope**: Only covers birds in Dongniao database (IOC 14.1)
- **Coverage**: ~10,000+ species, but not 100% of all birds
- **Update Frequency**: Depends on Dongniao updates
- **Language**: Primarily Chinese/English content

### Data Quality

- Information from public sources
- Not verified by ornithological experts
- For educational purposes
- Cross-reference for research/conservation work

## Comparison: v1 vs v2

| Feature | v1 (Browser) | v2 (web_fetch) |
|---------|-------------|----------------|
| Method | Browser automation | HTTP fetch |
| Speed | Slow (~10s) | Fast (~2s) |
| Reliability | Low (browser deps) | High (no deps) |
| Resource Usage | High | Low |
| Setup Complexity | High | Low |
| Works in Sandbox | No | Yes |

## Best Practices

### Usage Guidelines

1. **Be Specific**
   - "红嘴蓝鹊" > "蓝鹊"
   - "绿孔雀" > "孔雀"

2. **Try Alternative Names**
   - If Chinese fails, try English
   - If common name fails, try scientific name

3. **Verify Critical Info**
   - Cross-check with multiple sources
   - Consult experts for research/conservation

4. **Respect Wildlife**
   - Bird watching should not disturb birds
   - Follow local regulations

## Examples

### Example 1: Common Bird
```
请帮我查一下麻雀的详细信息
```
**Result**: House Sparrow info with distribution, habitat, and conservation status.

### Example 2: Rare Bird
```
请查一下褐马鸡的详细信息
```
**Result**: Endangered Chinese endemic species info from Shanxi province.

### Example 3: Scientific Name
```
请查一下 Aquila chrysaetos 的信息
```
**Result**: Golden Eagle information using scientific name lookup.

### Example 4: English Name
```
查询 Red-crowned Crane
```
**Result**: 丹顶鹤 information with Chinese and English details.

## Troubleshooting

### Issue: Bird not found

**Possible Causes**:
- Typo in name
- Bird not in database
- Name in different language

**Solutions**:
1. Check spelling
2. Try Chinese name
3. Try English name
4. Try scientific name

### Issue: Slow response

**Possible Causes**:
- Network delay
- First-time taxonomy fetch (cached after)

**Solutions**:
1. Wait for completion
2. Check network connection
3. Subsequent queries are faster (cached)

## References

- **Dongniao Website**: https://dongniao.net
- **Database**: IOC 14.1 World Bird List
- **Coverage**: Comprehensive bird taxonomy
- **Updates**: Regular as species are described

---

**Note**: This skill provides information from the Dongniao database. For scientific research or conservation work, always cross-reference with primary sources and expert literature.
