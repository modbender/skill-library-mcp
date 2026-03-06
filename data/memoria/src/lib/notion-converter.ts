import type { BlockObjectRequest } from '@notionhq/client/build/src/api-endpoints.js';

type RichTextItem = {
  type: 'text';
  text: { content: string; link?: { url: string } | null };
  annotations?: {
    bold?: boolean;
    italic?: boolean;
    strikethrough?: boolean;
    underline?: boolean;
    code?: boolean;
  };
};

export function markdownToBlocks(markdown: string): BlockObjectRequest[] {
  const lines = markdown.split('\n');
  const blocks: BlockObjectRequest[] = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.trim() === '') {
      i++;
      continue;
    }

    const h1 = line.match(/^# (.+)$/);
    if (h1) {
      blocks.push({
        object: 'block',
        type: 'heading_1',
        heading_1: { rich_text: parseInlineMarkdown(h1[1]) },
      } as BlockObjectRequest);
      i++;
      continue;
    }

    const h2 = line.match(/^## (.+)$/);
    if (h2) {
      blocks.push({
        object: 'block',
        type: 'heading_2',
        heading_2: { rich_text: parseInlineMarkdown(h2[1]) },
      } as BlockObjectRequest);
      i++;
      continue;
    }

    const h3 = line.match(/^### (.+)$/);
    if (h3) {
      blocks.push({
        object: 'block',
        type: 'heading_3',
        heading_3: { rich_text: parseInlineMarkdown(h3[1]) },
      } as BlockObjectRequest);
      i++;
      continue;
    }

    if (line.match(/^```/)) {
      const langMatch = line.match(/^```(\w*)$/);
      const language = langMatch?.[1] || 'plain text';
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].match(/^```$/)) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      blocks.push({
        object: 'block',
        type: 'code',
        code: {
          rich_text: [{ type: 'text', text: { content: codeLines.join('\n') } }],
          language: mapLanguage(language),
        },
      } as BlockObjectRequest);
      continue;
    }

    if (line.match(/^> /)) {
      const quoteLines: string[] = [];
      while (i < lines.length && lines[i].match(/^> /)) {
        quoteLines.push(lines[i].replace(/^> /, ''));
        i++;
      }
      blocks.push({
        object: 'block',
        type: 'quote',
        quote: { rich_text: parseInlineMarkdown(quoteLines.join('\n')) },
      } as BlockObjectRequest);
      continue;
    }

    if (line.match(/^[-*] /)) {
      blocks.push({
        object: 'block',
        type: 'bulleted_list_item',
        bulleted_list_item: { rich_text: parseInlineMarkdown(line.replace(/^[-*] /, '')) },
      } as BlockObjectRequest);
      i++;
      continue;
    }

    const numMatch = line.match(/^\d+\. (.+)$/);
    if (numMatch) {
      blocks.push({
        object: 'block',
        type: 'numbered_list_item',
        numbered_list_item: { rich_text: parseInlineMarkdown(numMatch[1]) },
      } as BlockObjectRequest);
      i++;
      continue;
    }

    if (line.match(/^(-{3,}|_{3,}|\*{3,})$/)) {
      blocks.push({
        object: 'block',
        type: 'divider',
        divider: {},
      } as BlockObjectRequest);
      i++;
      continue;
    }

    blocks.push({
      object: 'block',
      type: 'paragraph',
      paragraph: { rich_text: parseInlineMarkdown(line) },
    } as BlockObjectRequest);
    i++;
  }

  return blocks;
}

export function blocksToMarkdown(blocks: unknown[]): string {
  const lines: string[] = [];

  for (const block of blocks) {
    const b = block as Record<string, unknown>;
    const type = b.type as string;

    switch (type) {
      case 'paragraph':
        lines.push(richTextToMarkdown(getBlockRichText(b, 'paragraph')));
        lines.push('');
        break;
      case 'heading_1':
        lines.push(`# ${richTextToMarkdown(getBlockRichText(b, 'heading_1'))}`);
        lines.push('');
        break;
      case 'heading_2':
        lines.push(`## ${richTextToMarkdown(getBlockRichText(b, 'heading_2'))}`);
        lines.push('');
        break;
      case 'heading_3':
        lines.push(`### ${richTextToMarkdown(getBlockRichText(b, 'heading_3'))}`);
        lines.push('');
        break;
      case 'bulleted_list_item':
        lines.push(`- ${richTextToMarkdown(getBlockRichText(b, 'bulleted_list_item'))}`);
        break;
      case 'numbered_list_item':
        lines.push(`1. ${richTextToMarkdown(getBlockRichText(b, 'numbered_list_item'))}`);
        break;
      case 'code': {
        const codeData = b.code as Record<string, unknown>;
        const lang = (codeData.language as string) || '';
        const text = richTextToMarkdown(
          (codeData.rich_text as RichTextItem[]) || [],
        );
        lines.push(`\`\`\`${lang}`);
        lines.push(text);
        lines.push('```');
        lines.push('');
        break;
      }
      case 'quote':
        lines.push(
          richTextToMarkdown(getBlockRichText(b, 'quote'))
            .split('\n')
            .map((l) => `> ${l}`)
            .join('\n'),
        );
        lines.push('');
        break;
      case 'divider':
        lines.push('---');
        lines.push('');
        break;
      default:
        break;
    }
  }

  return lines.join('\n').trim();
}

function getBlockRichText(
  block: Record<string, unknown>,
  type: string,
): RichTextItem[] {
  const data = block[type] as Record<string, unknown> | undefined;
  return (data?.rich_text as RichTextItem[]) || [];
}

function parseInlineMarkdown(text: string): RichTextItem[] {
  const items: RichTextItem[] = [];
  const regex = /(\*\*(.+?)\*\*|__(.+?)__|_(.+?)_|\*(.+?)\*|`(.+?)`|\[(.+?)\]\((.+?)\))/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      items.push({
        type: 'text',
        text: { content: text.slice(lastIndex, match.index) },
      });
    }

    if (match[2] || match[3]) {
      items.push({
        type: 'text',
        text: { content: match[2] || match[3] },
        annotations: { bold: true },
      });
    } else if (match[4] || match[5]) {
      items.push({
        type: 'text',
        text: { content: match[4] || match[5] },
        annotations: { italic: true },
      });
    } else if (match[6]) {
      items.push({
        type: 'text',
        text: { content: match[6] },
        annotations: { code: true },
      });
    } else if (match[7] && match[8]) {
      items.push({
        type: 'text',
        text: { content: match[7], link: { url: match[8] } },
      });
    }

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    items.push({
      type: 'text',
      text: { content: text.slice(lastIndex) },
    });
  }

  if (items.length === 0) {
    items.push({ type: 'text', text: { content: text } });
  }

  return items;
}

function richTextToMarkdown(richText: RichTextItem[]): string {
  return richText
    .map((item) => {
      let text = item.text.content;
      const a = item.annotations;
      if (a?.bold) text = `**${text}**`;
      if (a?.italic) text = `_${text}_`;
      if (a?.code) text = `\`${text}\``;
      if (item.text.link?.url) text = `[${text}](${item.text.link.url})`;
      return text;
    })
    .join('');
}

function mapLanguage(lang: string): string {
  const map: Record<string, string> = {
    js: 'javascript',
    ts: 'typescript',
    py: 'python',
    rb: 'ruby',
    sh: 'bash',
    yml: 'yaml',
    '': 'plain text',
  };
  return map[lang] || lang;
}
