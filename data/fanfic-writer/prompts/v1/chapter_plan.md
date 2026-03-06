基于以下大纲，规划详细的章节列表：

书名: {book_title}
总字数: {total_words}
大纲: {main_outline}

【要求】
1. 每章控制在 2000-5000 字
2. 每章一个独立的小高潮或情节推进
3. 章节之间有连贯性，伏笔前后照应
4. 每章都要有卡点或钩子
5. 重要剧情章节字数要充足（4000+）
6. 过渡章节可以适当简短（2000-3000）

【输出格式】JSON
{
  "chapters": [
    {
      "number": 1,
      "title": "章节名（吸引眼球）",
      "summary": "简略内容（100字内）",
      "target_words": 3500,
      "key_event": "本章核心事件",
      "cliffhanger": "章节卡点"
    },
    ...
  ],
  "total_chapters": N,
  "volume_breakdown": [
    {"volume": 1, "name": "卷名", "chapters": "1-X", "key_plot": "卷核心剧情"}
  ],
  "notes": "特别说明（如哪些章节是高潮、哪些是过渡）"
}
