/**
 * Structured Data Skill — CSV parsing, JSON-to-CSV conversion, and SVG chart generation
 *
 * Zero external dependencies — pure TypeScript implementations.
 */

interface ToolDef {
  name: string;
  description: string;
  parameters: { type: 'object'; required?: string[]; properties: Record<string, unknown> };
  handler: (params: any) => Promise<unknown>;
}

interface SkillApi {
  registerTool(tool: ToolDef): void;
  getConfig(): Record<string, unknown>;
}

// ── CSV Parser ──────────────────────────────────

function detectDelimiter(text: string): string {
  const firstLine = text.split('\n')[0] || '';
  const counts: Record<string, number> = { ',': 0, '\t': 0, ';': 0, '|': 0 };
  // Count delimiters outside quotes
  let inQuote = false;
  for (const ch of firstLine) {
    if (ch === '"') { inQuote = !inQuote; continue; }
    if (!inQuote && ch in counts) counts[ch]++;
  }
  // Pick the delimiter with the highest count
  let best = ',';
  let bestCount = 0;
  for (const [delim, count] of Object.entries(counts)) {
    if (count > bestCount) { best = delim; bestCount = count; }
  }
  return best;
}

function parseCSVLine(line: string, delimiter: string): string[] {
  const fields: string[] = [];
  let current = '';
  let inQuote = false;
  let i = 0;

  while (i < line.length) {
    const ch = line[i];

    if (inQuote) {
      if (ch === '"') {
        // Check for escaped quote ("")
        if (i + 1 < line.length && line[i + 1] === '"') {
          current += '"';
          i += 2;
        } else {
          inQuote = false;
          i++;
        }
      } else {
        current += ch;
        i++;
      }
    } else {
      if (ch === '"') {
        inQuote = true;
        i++;
      } else if (ch === delimiter) {
        fields.push(current.trim());
        current = '';
        i++;
      } else {
        current += ch;
        i++;
      }
    }
  }
  fields.push(current.trim());
  return fields;
}

function parseCSVText(
  csv: string,
  options: { delimiter?: string; headers?: boolean; limit?: number },
): { data: Record<string, string>[]; columns: string[] } {
  const delimiter = options.delimiter || detectDelimiter(csv);
  const useHeaders = options.headers !== false;

  // Split into lines, handling quoted newlines
  const lines: string[] = [];
  let current = '';
  let inQuote = false;
  for (const ch of csv) {
    if (ch === '"') inQuote = !inQuote;
    if (ch === '\n' && !inQuote) {
      if (current.trim()) lines.push(current);
      current = '';
    } else if (ch === '\r') {
      // Skip carriage returns
    } else {
      current += ch;
    }
  }
  if (current.trim()) lines.push(current);

  if (lines.length === 0) return { data: [], columns: [] };

  let columns: string[];
  let startRow: number;

  if (useHeaders) {
    columns = parseCSVLine(lines[0], delimiter);
    startRow = 1;
  } else {
    const firstRow = parseCSVLine(lines[0], delimiter);
    columns = firstRow.map((_, i) => `col_${i}`);
    startRow = 0;
  }

  const maxRows = options.limit || Infinity;
  const data: Record<string, string>[] = [];

  for (let i = startRow; i < lines.length && data.length < maxRows; i++) {
    const fields = parseCSVLine(lines[i], delimiter);
    const row: Record<string, string> = {};
    for (let j = 0; j < columns.length; j++) {
      row[columns[j]] = fields[j] || '';
    }
    data.push(row);
  }

  return { data, columns };
}

// ── JSON to CSV ─────────────────────────────────

function escapeCSVField(value: string, delimiter: string): string {
  if (
    value.includes(delimiter) ||
    value.includes('"') ||
    value.includes('\n') ||
    value.includes('\r')
  ) {
    return '"' + value.replace(/"/g, '""') + '"';
  }
  return value;
}

function jsonToCSVText(
  data: Record<string, unknown>[],
  options: { columns?: string[]; delimiter?: string },
): string {
  if (data.length === 0) return '';

  const delimiter = options.delimiter || ',';

  // Determine columns
  let columns: string[];
  if (options.columns && options.columns.length > 0) {
    columns = options.columns;
  } else {
    // Collect all keys from all rows
    const keySet = new Set<string>();
    for (const row of data) {
      for (const key of Object.keys(row)) keySet.add(key);
    }
    columns = [...keySet];
  }

  const lines: string[] = [];

  // Header row
  lines.push(columns.map(c => escapeCSVField(c, delimiter)).join(delimiter));

  // Data rows
  for (const row of data) {
    const fields = columns.map(col => {
      const val = row[col];
      if (val === null || val === undefined) return '';
      if (typeof val === 'object') return escapeCSVField(JSON.stringify(val), delimiter);
      return escapeCSVField(String(val), delimiter);
    });
    lines.push(fields.join(delimiter));
  }

  return lines.join('\n');
}

// ── SVG Chart Generator ─────────────────────────

const DEFAULT_COLORS = ['#4285F4', '#EA4335', '#FBBC04', '#34A853', '#FF6D01', '#46BDC6', '#7B1FA2', '#C2185B'];

function escapeXml(text: string): string {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

interface ChartData {
  labels: string[];
  values?: number[];
  series?: Array<{ name: string; values: number[] }>;
}

function generateBarChart(
  data: ChartData,
  title: string,
  width: number,
  height: number,
  colors: string[],
): string {
  const margin = { top: title ? 50 : 30, right: 20, bottom: 60, left: 60 };
  const chartW = width - margin.left - margin.right;
  const chartH = height - margin.top - margin.bottom;

  const series = data.series || [{ name: 'Value', values: data.values || [] }];
  const allValues = series.flatMap(s => s.values);
  const maxVal = Math.max(...allValues, 0) || 1;
  const minVal = Math.min(0, ...allValues);
  const range = maxVal - minVal || 1;

  const groupCount = data.labels.length;
  const seriesCount = series.length;
  const groupWidth = chartW / groupCount;
  const barWidth = Math.min((groupWidth * 0.8) / seriesCount, 50);
  const groupPad = (groupWidth - barWidth * seriesCount) / 2;

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" style="font-family:system-ui,sans-serif">`;

  // Background
  svg += `<rect width="${width}" height="${height}" fill="white"/>`;

  // Title
  if (title) {
    svg += `<text x="${width / 2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">${escapeXml(title)}</text>`;
  }

  // Y-axis gridlines and labels
  const ySteps = 5;
  for (let i = 0; i <= ySteps; i++) {
    const val = minVal + (range * i) / ySteps;
    const y = margin.top + chartH - (chartH * (val - minVal)) / range;
    svg += `<line x1="${margin.left}" y1="${y}" x2="${margin.left + chartW}" y2="${y}" stroke="#eee" stroke-width="1"/>`;
    const label = Math.abs(val) >= 1000 ? `${(val / 1000).toFixed(1)}k` : val % 1 === 0 ? String(val) : val.toFixed(1);
    svg += `<text x="${margin.left - 8}" y="${y + 4}" text-anchor="end" font-size="11" fill="#666">${label}</text>`;
  }

  // Bars
  const zeroY = margin.top + chartH - (chartH * (0 - minVal)) / range;
  for (let g = 0; g < groupCount; g++) {
    for (let s = 0; s < seriesCount; s++) {
      const val = series[s].values[g] || 0;
      const barH = (chartH * Math.abs(val)) / range;
      const x = margin.left + g * groupWidth + groupPad + s * barWidth;
      const y = val >= 0 ? zeroY - barH : zeroY;
      const color = colors[s % colors.length];
      svg += `<rect x="${x}" y="${y}" width="${barWidth}" height="${barH}" fill="${color}" rx="2"/>`;
    }
    // X-axis label
    const labelX = margin.left + g * groupWidth + groupWidth / 2;
    const label = data.labels[g].length > 12 ? data.labels[g].slice(0, 11) + '\u2026' : data.labels[g];
    svg += `<text x="${labelX}" y="${margin.top + chartH + 18}" text-anchor="middle" font-size="11" fill="#666">${escapeXml(label)}</text>`;
  }

  // Axes
  svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + chartH}" stroke="#ccc" stroke-width="1"/>`;
  svg += `<line x1="${margin.left}" y1="${zeroY}" x2="${margin.left + chartW}" y2="${zeroY}" stroke="#ccc" stroke-width="1"/>`;

  // Legend for multi-series
  if (seriesCount > 1) {
    const legendY = height - 15;
    let legendX = margin.left;
    for (let s = 0; s < seriesCount; s++) {
      const color = colors[s % colors.length];
      svg += `<rect x="${legendX}" y="${legendY - 8}" width="12" height="12" fill="${color}" rx="2"/>`;
      svg += `<text x="${legendX + 16}" y="${legendY + 2}" font-size="11" fill="#666">${escapeXml(series[s].name)}</text>`;
      legendX += 16 + series[s].name.length * 7 + 16;
    }
  }

  svg += '</svg>';
  return svg;
}

function generateLineChart(
  data: ChartData,
  title: string,
  width: number,
  height: number,
  colors: string[],
): string {
  const margin = { top: title ? 50 : 30, right: 20, bottom: 60, left: 60 };
  const chartW = width - margin.left - margin.right;
  const chartH = height - margin.top - margin.bottom;

  const series = data.series || [{ name: 'Value', values: data.values || [] }];
  const allValues = series.flatMap(s => s.values);
  const maxVal = Math.max(...allValues, 0) || 1;
  const minVal = Math.min(...allValues, 0);
  const range = maxVal - minVal || 1;
  // Add 10% padding
  const paddedMin = minVal - range * 0.05;
  const paddedRange = range * 1.1;

  const pointCount = data.labels.length;

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" style="font-family:system-ui,sans-serif">`;
  svg += `<rect width="${width}" height="${height}" fill="white"/>`;

  if (title) {
    svg += `<text x="${width / 2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">${escapeXml(title)}</text>`;
  }

  // Y-axis gridlines
  const ySteps = 5;
  for (let i = 0; i <= ySteps; i++) {
    const val = paddedMin + (paddedRange * i) / ySteps;
    const y = margin.top + chartH - (chartH * i) / ySteps;
    svg += `<line x1="${margin.left}" y1="${y}" x2="${margin.left + chartW}" y2="${y}" stroke="#eee" stroke-width="1"/>`;
    const label = Math.abs(val) >= 1000 ? `${(val / 1000).toFixed(1)}k` : val % 1 === 0 ? String(Math.round(val)) : val.toFixed(1);
    svg += `<text x="${margin.left - 8}" y="${y + 4}" text-anchor="end" font-size="11" fill="#666">${label}</text>`;
  }

  // Lines and points
  for (let s = 0; s < series.length; s++) {
    const color = colors[s % colors.length];
    const points: Array<{ x: number; y: number }> = [];

    for (let i = 0; i < pointCount; i++) {
      const val = series[s].values[i] || 0;
      const x = margin.left + (i / Math.max(pointCount - 1, 1)) * chartW;
      const y = margin.top + chartH - (chartH * (val - paddedMin)) / paddedRange;
      points.push({ x, y });
    }

    // Line path
    if (points.length > 0) {
      const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
      svg += `<path d="${pathD}" fill="none" stroke="${color}" stroke-width="2.5" stroke-linejoin="round"/>`;
    }

    // Points
    for (const p of points) {
      svg += `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="3.5" fill="${color}" stroke="white" stroke-width="1.5"/>`;
    }
  }

  // X-axis labels
  for (let i = 0; i < pointCount; i++) {
    const x = margin.left + (i / Math.max(pointCount - 1, 1)) * chartW;
    const label = data.labels[i].length > 12 ? data.labels[i].slice(0, 11) + '\u2026' : data.labels[i];
    svg += `<text x="${x}" y="${margin.top + chartH + 18}" text-anchor="middle" font-size="11" fill="#666">${escapeXml(label)}</text>`;
  }

  // Axes
  svg += `<line x1="${margin.left}" y1="${margin.top}" x2="${margin.left}" y2="${margin.top + chartH}" stroke="#ccc" stroke-width="1"/>`;
  svg += `<line x1="${margin.left}" y1="${margin.top + chartH}" x2="${margin.left + chartW}" y2="${margin.top + chartH}" stroke="#ccc" stroke-width="1"/>`;

  // Legend
  if (series.length > 1) {
    const legendY = height - 15;
    let legendX = margin.left;
    for (let s = 0; s < series.length; s++) {
      const color = colors[s % colors.length];
      svg += `<rect x="${legendX}" y="${legendY - 8}" width="12" height="12" fill="${color}" rx="2"/>`;
      svg += `<text x="${legendX + 16}" y="${legendY + 2}" font-size="11" fill="#666">${escapeXml(series[s].name)}</text>`;
      legendX += 16 + series[s].name.length * 7 + 16;
    }
  }

  svg += '</svg>';
  return svg;
}

function generatePieChart(
  data: ChartData,
  title: string,
  width: number,
  height: number,
  colors: string[],
): string {
  const values = data.values || [];
  const total = values.reduce((sum, v) => sum + Math.abs(v), 0) || 1;

  const cx = width / 2;
  const cy = (height - (title ? 30 : 0)) / 2 + (title ? 40 : 0);
  const radius = Math.min(width, height - (title ? 60 : 20)) / 2 - 40;

  let svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}" width="${width}" height="${height}" style="font-family:system-ui,sans-serif">`;
  svg += `<rect width="${width}" height="${height}" fill="white"/>`;

  if (title) {
    svg += `<text x="${width / 2}" y="25" text-anchor="middle" font-size="16" font-weight="bold" fill="#333">${escapeXml(title)}</text>`;
  }

  let startAngle = -Math.PI / 2;
  for (let i = 0; i < values.length; i++) {
    const sliceAngle = (Math.abs(values[i]) / total) * 2 * Math.PI;
    const endAngle = startAngle + sliceAngle;
    const color = colors[i % colors.length];

    const x1 = cx + radius * Math.cos(startAngle);
    const y1 = cy + radius * Math.sin(startAngle);
    const x2 = cx + radius * Math.cos(endAngle);
    const y2 = cy + radius * Math.sin(endAngle);
    const largeArc = sliceAngle > Math.PI ? 1 : 0;

    if (values.length === 1) {
      // Full circle
      svg += `<circle cx="${cx}" cy="${cy}" r="${radius}" fill="${color}"/>`;
    } else {
      svg += `<path d="M${cx},${cy} L${x1.toFixed(2)},${y1.toFixed(2)} A${radius},${radius} 0 ${largeArc},1 ${x2.toFixed(2)},${y2.toFixed(2)} Z" fill="${color}" stroke="white" stroke-width="2"/>`;
    }

    // Percentage label on slice
    const midAngle = startAngle + sliceAngle / 2;
    const pct = ((Math.abs(values[i]) / total) * 100).toFixed(1);
    if (parseFloat(pct) >= 3) {
      const labelR = radius * 0.65;
      const lx = cx + labelR * Math.cos(midAngle);
      const ly = cy + labelR * Math.sin(midAngle);
      svg += `<text x="${lx.toFixed(1)}" y="${ly.toFixed(1)}" text-anchor="middle" dominant-baseline="central" font-size="12" font-weight="bold" fill="white">${pct}%</text>`;
    }

    startAngle = endAngle;
  }

  // Legend
  const legendStartY = height - 20 - Math.ceil(data.labels.length / 3) * 18;
  const colWidth = width / 3;
  for (let i = 0; i < data.labels.length; i++) {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const lx = 20 + col * colWidth;
    const ly = legendStartY + row * 18;
    const color = colors[i % colors.length];
    const label = data.labels[i].length > 16 ? data.labels[i].slice(0, 15) + '\u2026' : data.labels[i];
    svg += `<rect x="${lx}" y="${ly}" width="10" height="10" fill="${color}" rx="2"/>`;
    svg += `<text x="${lx + 14}" y="${ly + 9}" font-size="11" fill="#666">${escapeXml(label)}</text>`;
  }

  svg += '</svg>';
  return svg;
}

// ── Skill entry point ───────────────────────────

export default function structuredDataSkill(api: SkillApi): void {
  // ── parse_csv ──
  api.registerTool({
    name: 'parse_csv',
    description: [
      'Parse CSV text into a JSON array of objects.',
      'Auto-detects delimiter (comma, tab, semicolon, pipe).',
      'Handles quoted fields with embedded commas and newlines.',
      'Returns data, columns, row_count, and preview (first 5 rows).',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['csv'],
      properties: {
        csv: { type: 'string', description: 'CSV text to parse.' },
        delimiter: { type: 'string', description: 'Delimiter character. Auto-detected if not specified.' },
        headers: { type: 'boolean', description: 'Whether first row is headers (default true).' },
        limit: { type: 'number', description: 'Maximum number of data rows to parse.' },
      },
    },
    handler: async ({ csv, delimiter, headers, limit }: {
      csv: string; delimiter?: string; headers?: boolean; limit?: number;
    }) => {
      if (!csv || typeof csv !== 'string') {
        return { error: 'csv parameter is required and must be a string' };
      }

      try {
        const result = parseCSVText(csv, { delimiter, headers, limit });
        return {
          data: result.data,
          columns: result.columns,
          row_count: result.data.length,
          preview: result.data.slice(0, 5),
        };
      } catch (err: any) {
        return { error: `CSV parse error: ${err.message}` };
      }
    },
  });

  // ── json_to_csv ──
  api.registerTool({
    name: 'json_to_csv',
    description: [
      'Convert a JSON array of objects to CSV text.',
      'Auto-quotes fields containing delimiters, newlines, or quotes.',
      'Handles nested values via JSON.stringify.',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['data'],
      properties: {
        data: { type: 'array', description: 'Array of objects to convert to CSV.' },
        columns: { type: 'array', description: 'Optional array of column names to include/reorder.' },
        delimiter: { type: 'string', description: 'Delimiter character (default ",").' },
      },
    },
    handler: async ({ data, columns, delimiter }: {
      data: Record<string, unknown>[]; columns?: string[]; delimiter?: string;
    }) => {
      if (!Array.isArray(data)) {
        return { error: 'data parameter must be an array of objects' };
      }
      if (data.length === 0) {
        return { csv: '', row_count: 0, column_count: 0 };
      }

      try {
        const csvText = jsonToCSVText(data, { columns, delimiter });
        const usedColumns = columns && columns.length > 0
          ? columns
          : [...new Set(data.flatMap(row => Object.keys(row)))];

        return {
          csv: csvText,
          row_count: data.length,
          column_count: usedColumns.length,
        };
      } catch (err: any) {
        return { error: `CSV conversion error: ${err.message}` };
      }
    },
  });

  // ── generate_chart ──
  api.registerTool({
    name: 'generate_chart',
    description: [
      'Generate an SVG chart from data. Supports bar, line, and pie charts.',
      'Single series: { labels: ["A","B"], values: [10,20] }.',
      'Multi-series: { labels: ["Q1","Q2"], series: [{ name: "2024", values: [10,20] }] }.',
      'Returns svg (raw) and data_uri (base64 for markdown embedding).',
    ].join(' '),
    parameters: {
      type: 'object',
      required: ['type', 'data'],
      properties: {
        type: { type: 'string', description: 'Chart type: "bar", "line", or "pie".' },
        data: { description: 'Chart data: { labels, values } or { labels, series: [{ name, values }] }.' },
        title: { type: 'string', description: 'Optional chart title.' },
        width: { type: 'number', description: 'Chart width in pixels (default 600).' },
        height: { type: 'number', description: 'Chart height in pixels (default 400).' },
        colors: { type: 'array', description: 'Optional array of hex color strings.' },
      },
    },
    handler: async ({ type, data, title, width, height, colors }: {
      type: string;
      data: ChartData;
      title?: string;
      width?: number;
      height?: number;
      colors?: string[];
    }) => {
      if (!type || !['bar', 'line', 'pie'].includes(type)) {
        return { error: 'type must be "bar", "line", or "pie"' };
      }
      if (!data || !Array.isArray(data.labels)) {
        return { error: 'data must include a labels array' };
      }
      if (!data.values && !data.series) {
        return { error: 'data must include values (single series) or series (multi-series)' };
      }

      const w = Math.min(Math.max(width || 600, 200), 2000);
      const h = Math.min(Math.max(height || 400, 150), 2000);
      const palette = colors || DEFAULT_COLORS;
      const chartTitle = title || '';

      let svg: string;
      try {
        switch (type) {
          case 'bar':
            svg = generateBarChart(data, chartTitle, w, h, palette);
            break;
          case 'line':
            svg = generateLineChart(data, chartTitle, w, h, palette);
            break;
          case 'pie':
            svg = generatePieChart(data, chartTitle, w, h, palette);
            break;
          default:
            return { error: `Unknown chart type: ${type}` };
        }
      } catch (err: any) {
        return { error: `Chart generation error: ${err.message}` };
      }

      const dataUri = `data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`;

      return { svg, data_uri: dataUri };
    },
  });
}
