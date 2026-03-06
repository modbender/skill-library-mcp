// ── 輕量 Markdown → HTML 渲染 ──
// 支援：粗體、斜體、行內程式碼、程式碼區塊、列表、連結、表格

// 處理程式碼區塊（先提取，避免內部被解析）
function extractCodeBlocks(text) {
  const blocks = [];
  const placeholder = (i) => `\x00CB${i}\x00`;
  const result = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    blocks.push({ lang, code: code.trimEnd() });
    return placeholder(blocks.length - 1);
  });
  return { text: result, blocks, placeholder };
}

// 渲染行內 markdown
function renderInline(text) {
  return text
    // 行內程式碼（先處理，避免內部被其他規則影響）
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // 粗斜體
    .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
    // 粗體
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // 斜體
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // 連結
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
}

// 檢查是否為表格分隔行（|---|---|）
function isTableSeparator(line) {
  return /^\|?[\s-:|]+\|[\s-:|]+\|?$/.test(line.trim());
}

// 檢查是否為表格行（| xxx | xxx |）
function isTableRow(line) {
  return /^\|(.+)\|$/.test(line.trim());
}

// 解析表格行的 cells
function parseTableCells(line) {
  return line.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
}

// 主渲染函數
export function renderMarkdown(text) {
  if (!text) return '';

  const { text: processed, blocks, placeholder } = extractCodeBlocks(text);

  const lines = processed.split('\n');
  const html = [];
  let inList = false;
  let listType = null; // 'ul' or 'ol'

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // 程式碼區塊 placeholder
    const cbMatch = line.match(/\x00CB(\d+)\x00/);
    if (cbMatch) {
      if (inList) { html.push(`</${listType}>`); inList = false; }
      const block = blocks[parseInt(cbMatch[1])];
      html.push(`<pre><code${block.lang ? ` class="lang-${block.lang}"` : ''}>${escapeHtml(block.code)}</code></pre>`);
      continue;
    }

    // 表格偵測：當前行是表格行，下一行是分隔行
    if (isTableRow(line) && i + 1 < lines.length && isTableSeparator(lines[i + 1])) {
      if (inList) { html.push(`</${listType}>`); inList = false; }

      // 表頭
      const headers = parseTableCells(line);
      html.push('<table><thead><tr>');
      headers.forEach(h => html.push(`<th>${renderInline(h)}</th>`));
      html.push('</tr></thead><tbody>');

      i++; // 跳過分隔行

      // 表格內容行
      while (i + 1 < lines.length && isTableRow(lines[i + 1])) {
        i++;
        const cells = parseTableCells(lines[i]);
        html.push('<tr>');
        cells.forEach(c => html.push(`<td>${renderInline(c)}</td>`));
        html.push('</tr>');
      }

      html.push('</tbody></table>');
      continue;
    }

    // 無序列表
    const ulMatch = line.match(/^[\s]*[-*+]\s+(.+)/);
    if (ulMatch) {
      if (!inList || listType !== 'ul') {
        if (inList) html.push(`</${listType}>`);
        html.push('<ul>');
        inList = true;
        listType = 'ul';
      }
      html.push(`<li>${renderInline(ulMatch[1])}</li>`);
      continue;
    }

    // 有序列表
    const olMatch = line.match(/^[\s]*\d+[.)]\s+(.+)/);
    if (olMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) html.push(`</${listType}>`);
        html.push('<ol>');
        inList = true;
        listType = 'ol';
      }
      html.push(`<li>${renderInline(olMatch[1])}</li>`);
      continue;
    }

    // 非列表行 → 關閉列表
    if (inList) {
      html.push(`</${listType}>`);
      inList = false;
    }

    // 標題
    const headingMatch = line.match(/^(#{1,3})\s+(.+)/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      html.push(`<h${level + 2}>${renderInline(headingMatch[2])}</h${level + 2}>`);
      continue;
    }

    // 空行
    if (line.trim() === '') {
      continue;
    }

    // 一般段落
    html.push(`<p>${renderInline(line)}</p>`);
  }

  if (inList) html.push(`</${listType}>`);

  return html.join('');
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
