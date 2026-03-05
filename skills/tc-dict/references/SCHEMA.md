# Dictionary Data Schema

## Overview

The MOE dictionaries are distributed as `.xlsx` files (Microsoft Excel format) containing structured dictionary entries. This document describes the typical schema for the "國語辭典簡編本" (Concised Mandarin Dictionary).

## File Format

- **Format**: `.xlsx` (Excel Workbook)
- **Sheet Name**: Usually `Sheet1` or named by content (e.g., "辭典內容")
- **Encoding**: UTF-8

## Column Structure

Based on MOE dictionary standards, typical columns include:

| Column | Name | Type | Example | Notes |
|--------|------|------|---------|-------|
| 1 | 字詞 (Word) | String | 蒼鷺 | Main lookup key; may contain spaces for multi-character words |
| 2 | 注音 (Pronunciation) | String | ㄘㄤ ㄌㄨˇ | Zhuyin/Bopomofo notation |
| 3 | 詞性 (Part of Speech) | String | 名詞 | noun, verb, adjective, etc. |
| 4 | 釋義 (Definition) | String | 一種大型水鳥，身體灰色... | Primary definition |
| 5 | 例句 (Examples) | String | 沼澤邊有蒼鷺在覓食。 | Usage examples (may be comma-separated) |
| 6 | 其他資訊 (Additional Info) | String (Optional) | - | References, related terms, historical notes |

## Data Characteristics

### Word Column (字詞)
- Contains both **single characters** (字) and **multi-character terms** (詞)
- May be normalized (traditional vs. simplified, though MOE uses traditional)
- Entries are generally in alphabetical/stroke order
- Duplicates may exist for words with multiple pronunciations or meanings

### Pronunciation Column (注音)
- Uses **Zhuyin (ㄅㄆㄇ)** notation (Taiwan standard)
- Multiple pronunciations separated by space or punctuation
- Each pronunciation may correspond to different definitions

### Definition Column (釋義)
- Usually contains **brief, concise definitions** (hence "簡編本")
- May include:
  - Category tag (e.g., "名詞", "動詞", "形容詞")
  - Literal explanation
  - Short context
- May be truncated in some dictionaries; check "Additional Info" for full definition

### Example Column (例句)
- Contains **actual usage examples** from literature or common phrases
- Multiple examples may be separated by punctuation (、or ；)
- Often paired with the definition for better understanding

## Common Issues & Edge Cases

### 1. Rows with Missing Data
- Some columns may be empty (`None` or empty string)
- Queries should handle gracefully: skip missing fields or use defaults

### 2. Multi-Pronunciation Entries
```
Word: 行
Pronunciation: ㄒㄧㄥˊ | ㄒㄧㄥˋ | ㄏㄢˊ
Definition: [corresponds to 1st pronunciation]
Definition: [corresponds to 2nd pronunciation]
Definition: [corresponds to 3rd pronunciation]
```
**Strategy**: Return all definitions under the same word entry, noting pronunciation differences

### 3. Compound Words vs. Single Characters
```
Word: 破曉       (compound)
Word: 破         (single character)
Word: 曉         (single character)
```
**Strategy**: When searching "破曉", prioritize exact matches; offer single-character matches as alternatives

### 4. Encoding Issues
- File is UTF-8 encoded
- Traditional Chinese characters: 繁體
- Zhuyin marks: Combining diacritics (may require special handling in some systems)

## Loading & Parsing

### Using pandas (Python)

```python
import pandas as pd

df = pd.read_excel('dict_concised_2014.xlsx', sheet_name=0)

# Column names (auto-detected or manual)
# Common: ['字詞', '注音', '詞性', '釋義', '例句', ...]

# Access a row
word = df.iloc[0]['字詞']
definition = df.iloc[0]['釋義']
```

### Data Cleaning
- Strip whitespace from all fields
- Handle NaN/None values gracefully
- Normalize pronunciation notation (some diacritics may render differently)

## Indexing Strategy

For efficient lookup, consider:

1. **In-Memory Index** (for smaller dictionaries like 簡編本):
   - Load entire xlsx into dictionary/dataframe on first use
   - Cache in memory during session
   - Reasonable for ~10,000+ entries

2. **Database Index** (for larger dictionaries like 修訂本):
   - Convert xlsx to SQLite or similar
   - Query by word, prefix, fuzzy match
   - Useful when frequent lookups needed

3. **Fuzzy Matching**:
   - Use `difflib.get_close_matches()` for typos
   - Use regex for prefix search
   - Rank by string distance + frequency

## Version Compatibility

Different MOE dictionaries may have slightly different schemas:

- **國語辭典簡編本**: Standard 5-6 columns (text, pronunciation, definition, examples)
- **重編國語辭典修訂本**: More detailed (might include etymology, usage notes)
- **國語小字典**: Simplified (fewer columns, simpler language)

When extending to other dictionaries, update this schema documentation accordingly.

## Example Row

```
字詞: 藍寶石
注音: ㄌㄢˊ ㄅㄠˇ ㄕˊ
詞性: 名詞
釋義: 寶石名。剛玉族礦物，硬度僅次於鑽石，常呈透明藍色，為貴重寶石。
例句: 她的戒指上鑲著一顆藍寶石。
```
