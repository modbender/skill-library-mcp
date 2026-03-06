# SRT Subtitle Format Specification

## Overview

SRT (SubRip Text) is a simple subtitle format consisting of sequential subtitle blocks separated by blank lines.

## Format Structure

```
1
00:00:01,000 --> 00:00:03,000
Hello, world!

2
00:00:04,000 --> 00:00:06,000
This is the second subtitle.
It can have multiple lines.
```

## Block Components

### 1. Sequence Number
- Integer starting from 1
- Increments by 1 for each subtitle
- Must be unique and sequential

### 2. Timecode
Format: `HH:MM:SS,mmm --> HH:MM:SS,mmm`
- Start time --> End time
- Hours: 2 digits (00-99)
- Minutes: 2 digits (00-59)
- Seconds: 2 digits (00-59)
- Milliseconds: 3 digits (000-999)
- Separator: comma (`,`) not period (`.`)

### 3. Subtitle Text
- One or more lines
- No blank lines within text
- Supports basic HTML tags: `<b>`, `<i>`, `<u>`, `<font>`

## Bilingual Format

When outputting bilingual subtitles (translation above original):

```
1
00:00:01,000 --> 00:00:03,000
你好，世界！
Hello, world!

2
00:00:04,000 --> 00:00:06,000
这是第二句字幕。
This is the second subtitle.
```

## Validation Rules

1. **Sequence numbers**: Must be sequential (1, 2, 3...)
2. **Timecodes**: Must be valid format and non-overlapping
3. **Blank lines**: Separate blocks with exactly one blank line
4. **File ending**: Should end with a blank line

## Common Issues

- **Timecode format**: Use comma (`,`) not period (`.`) for milliseconds
- **Line endings**: Use LF (`\n`) not CRLF (`\r\n`) for compatibility
- **Encoding**: UTF-8 is recommended
