/**
 * DataMaster Pro - 数据可视化脚本
 * 支持多种图表类型，输出 SVG/PNG/HTML
 */

const fs = require('fs');
const path = require('path');

// 解析命令行参数
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    input: null,
    output: 'chart',
    type: 'bar',
    title: 'Data Chart',
    xColumn: null,
    yColumn: null,
    width: 800,
    height: 400,
    colors: ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#00BCD4'],
    format: 'svg'
  };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--input':
      case '-i':
        options.input = args[++i];
        break;
      case '--output':
      case '-o':
        options.output = args[++i];
        break;
      case '--type':
      case '-t':
        options.type = args[++i];
        break;
      case '--title':
        options.title = args[++i];
        break;
      case '--x':
        options.xColumn = args[++i];
        break;
      case '--y':
        options.yColumn = args[++i];
        break;
      case '--width':
        options.width = parseInt(args[++i]);
        break;
      case '--height':
        options.height = parseInt(args[++i]);
        break;
      case '--colors':
        options.colors = args[++i].split(',');
        break;
      case '--format':
        options.format = args[++i];
        break;
    }
  }

  return options;
}

// 读取数据
function readData(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const content = fs.readFileSync(filePath, 'utf-8');

  if (ext === '.json') {
    return JSON.parse(content);
  } else if (ext === '.csv') {
    return parseCSV(content);
  }
  throw new Error(`不支持的文件格式: ${ext}`);
}

// 解析CSV
function parseCSV(content) {
  const lines = content.trim().split('\n');
  if (lines.length < 2) return [];

  const headers = parseCSVLine(lines[0]);
  const data = [];

  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]);
    const row = {};
    headers.forEach((header, index) => {
      const val = values[index] || '';
      row[header] = isNaN(val) ? val : parseFloat(val);
    });
    data.push(row);
  }

  return data;
}

function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];
    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim());
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current.trim());
  return result;
}

// SVG 生成器
class SVGChart {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.margin = { top: 40, right: 30, bottom: 50, left: 60 };
    this.elements = [];
  }

  header() {
    return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${this.width} ${this.height}" width="${this.width}" height="${this.height}">
  <style>
    .axis-label { font-family: Arial, sans-serif; font-size: 12px; fill: #666; }
    .axis-title { font-family: Arial, sans-serif; font-size: 14px; fill: #333; font-weight: bold; }
    .chart-title { font-family: Arial, sans-serif; font-size: 18px; fill: #333; font-weight: bold; }
    .legend { font-family: Arial, sans-serif; font-size: 11px; fill: #666; }
    .grid { stroke: #e0e0e0; stroke-width: 1; }
    .tick { stroke: #ccc; stroke-width: 1; }
  </style>`;
  }

  footer() {
    return '</svg>';
  }

  title(text) {
    return `<text x="${this.width / 2}" y="25" class="chart-title" text-anchor="middle">${this.escape(text)}</text>`;
  }

  escape(text) {
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  rect(x, y, w, h, fill, options = {}) {
    const attrs = Object.entries(options)
      .map(([k, v]) => `${k}="${this.escape(v)}"`)
      .join(' ');
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" ${attrs}/>`;
  }

  circle(cx, cy, r, fill, options = {}) {
    const attrs = Object.entries(options)
      .map(([k, v]) => `${k}="${this.escape(v)}"`)
      .join(' ');
    return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${fill}" ${attrs}/>`;
  }

  line(x1, y1, x2, y2, options = {}) {
    const attrs = Object.entries(options)
      .map(([k, v]) => `${k}="${this.escape(v)}"`)
      .join(' ');
    return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" ${attrs}/>`;
  }

  text(x, y, content, options = {}) {
    const attrs = Object.entries(options)
      .map(([k, v]) => `${k}="${this.escape(v)}"`)
      .join(' ');
    return `<text x="${x}" y="${y}" ${attrs}>${this.escape(content)}</text>`;
  }

  path(d, options = {}) {
    const attrs = Object.entries(options)
      .map(([k, v]) => `${k}="${this.escape(v)}"`)
      .join(' ');
    return `<path d="${d}" ${attrs}/>`;
  }
}

// 柱状图
function generateBarChart(data, options) {
  const chart = new SVGChart(options.width, options.height);
  const { margin, width, height } = chart;
  
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  // 获取数据
  const keys = Object.keys(data[0] || {});
  const xKey = options.xColumn || keys[0];
  const yKey = options.yColumn || keys.find(k => typeof data[0][k] === 'number') || keys[1];

  const xValues = data.map(d => d[xKey]);
  const yValues = data.map(d => parseFloat(d[yKey]) || 0);
  const maxY = Math.max(...yValues) * 1.1;

  // SVG 头部
  let svg = chart.header();
  svg += chart.title(options.title);

  // Y轴网格线
  const yTicks = 5;
  for (let i = 0; i <= yTicks; i++) {
    const y = margin.top + (chartHeight / yTicks) * i;
    svg += chart.line(margin.left, y, width - margin.right, y, { class: 'grid' });
    const val = (maxY - (maxY / yTicks) * i).toFixed(0);
    svg += chart.text(margin.left - 10, y + 4, val, { class: 'axis-label', 'text-anchor': 'end' });
  }

  // 绘制柱状图
  const barWidth = (chartWidth / data.length) * 0.7;
  const gap = (chartWidth / data.length) * 0.3;

  data.forEach((d, i) => {
    const x = margin.left + i * (barWidth + gap) + gap / 2;
    const barHeight = (yValues[i] / maxY) * chartHeight;
    const y = margin.top + chartHeight - barHeight;
    const color = options.colors[i % options.colors.length];

    svg += chart.rect(x, y, barWidth, barHeight, color, { rx: '3' });

    // X轴标签
    svg += chart.text(x + barWidth / 2, height - margin.bottom + 20, String(xValues[i]).slice(0, 10), {
      class: 'axis-label',
      'text-anchor': 'middle',
      transform: `rotate(-45 ${x + barWidth / 2} ${height - margin.bottom + 20})`
    });

    // 数值标签
    svg += chart.text(x + barWidth / 2, y - 5, yValues[i].toFixed(0), {
      class: 'axis-label',
      'text-anchor': 'middle'
    });
  });

  // Y轴标题
  svg += chart.text(15, height / 2, yKey, {
    class: 'axis-title',
    transform: `rotate(-90 15 ${height / 2})`,
    'text-anchor': 'middle'
  });

  svg += chart.footer();
  return svg;
}

// 折线图
function generateLineChart(data, options) {
  const chart = new SVGChart(options.width, options.height);
  const { margin, width, height } = chart;
  
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const keys = Object.keys(data[0] || {});
  const xKey = options.xColumn || keys[0];
  const yKey = options.yColumn || keys.find(k => typeof data[0][k] === 'number') || keys[1];

  const yValues = data.map(d => parseFloat(d[yKey]) || 0);
  const maxY = Math.max(...yValues) * 1.1;

  let svg = chart.header();
  svg += chart.title(options.title);

  // Y轴网格线
  const yTicks = 5;
  for (let i = 0; i <= yTicks; i++) {
    const y = margin.top + (chartHeight / yTicks) * i;
    svg += chart.line(margin.left, y, width - margin.right, y, { class: 'grid' });
    const val = (maxY - (maxY / yTicks) * i).toFixed(0);
    svg += chart.text(margin.left - 10, y + 4, val, { class: 'axis-label', 'text-anchor': 'end' });
  }

  // 计算点坐标
  const points = data.map((d, i) => {
    const x = margin.left + (chartWidth / (data.length - 1 || 1)) * i;
    const y = margin.top + chartHeight - (yValues[i] / maxY) * chartHeight;
    return { x, y, label: d[xKey] };
  });

  // 绘制折线
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  svg += chart.path(pathD, { fill: 'none', stroke: options.colors[0], 'stroke-width': '2' });

  // 绘制点
  points.forEach((p, i) => {
    svg += chart.circle(p.x, p.y, 4, options.colors[0]);
    svg += chart.text(p.x, height - margin.bottom + 20, String(p.label).slice(0, 8), {
      class: 'axis-label',
      'text-anchor': 'middle'
    });
  });

  svg += chart.footer();
  return svg;
}

// 饼图
function generatePieChart(data, options) {
  const chart = new SVGChart(options.width, options.height);
  const { width, height } = chart;
  
  const keys = Object.keys(data[0] || {});
  const labelKey = options.xColumn || keys[0];
  const valueKey = options.yColumn || keys.find(k => typeof data[0][k] === 'number') || keys[1];

  const values = data.map(d => ({ label: d[labelKey], value: parseFloat(d[valueKey]) || 0 }));
  const total = values.reduce((sum, v) => sum + v.value, 0);

  const cx = width / 2;
  const cy = height / 2;
  const r = Math.min(width, height) / 2 - 60;

  let svg = chart.header();
  svg += chart.title(options.title);

  let startAngle = -Math.PI / 2;
  
  values.forEach((v, i) => {
    const angle = (v.value / total) * 2 * Math.PI;
    const endAngle = startAngle + angle;
    const color = options.colors[i % options.colors.length];

    // 计算路径
    const x1 = cx + r * Math.cos(startAngle);
    const y1 = cy + r * Math.sin(startAngle);
    const x2 = cx + r * Math.cos(endAngle);
    const y2 = cy + r * Math.sin(endAngle);

    const largeArc = angle > Math.PI ? 1 : 0;
    const pathD = `M ${cx} ${cy} L ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    svg += chart.path(pathD, { fill: color, stroke: '#fff', 'stroke-width': '2' });

    // 标签
    const midAngle = startAngle + angle / 2;
    const labelR = r * 0.7;
    const labelX = cx + labelR * Math.cos(midAngle);
    const labelY = cy + labelR * Math.sin(midAngle);

    const pct = ((v.value / total) * 100).toFixed(1);
    if (pct > 5) {
      svg += chart.text(labelX, labelY + 4, `${pct}%`, {
        class: 'axis-label',
        'text-anchor': 'middle',
        fill: '#fff',
        'font-weight': 'bold'
      });
    }

    startAngle = endAngle;
  });

  // 图例
  values.forEach((v, i) => {
    const legendX = width - 120;
    const legendY = 60 + i * 20;
    const color = options.colors[i % options.colors.length];

    svg += chart.rect(legendX, legendY - 8, 12, 12, color);
    svg += chart.text(legendX + 18, legendY, String(v.label).slice(0, 15), { class: 'legend' });
  });

  svg += chart.footer();
  return svg;
}

// 散点图
function generateScatterChart(data, options) {
  const chart = new SVGChart(options.width, options.height);
  const { margin, width, height } = chart;
  
  const chartWidth = width - margin.left - margin.right;
  const chartHeight = height - margin.top - margin.bottom;

  const keys = Object.keys(data[0] || {});
  const numericKeys = keys.filter(k => typeof data[0][k] === 'number');
  const xKey = options.xColumn || numericKeys[0] || keys[0];
  const yKey = options.yColumn || numericKeys[1] || keys[1];

  const xValues = data.map(d => parseFloat(d[xKey]) || 0);
  const yValues = data.map(d => parseFloat(d[yKey]) || 0);

  const maxX = Math.max(...xValues) * 1.1;
  const maxY = Math.max(...yValues) * 1.1;

  let svg = chart.header();
  svg += chart.title(options.title);

  // 网格
  for (let i = 0; i <= 5; i++) {
    const y = margin.top + (chartHeight / 5) * i;
    svg += chart.line(margin.left, y, width - margin.right, y, { class: 'grid' });
    svg += chart.text(margin.left - 10, y + 4, ((maxY / 5) * (5 - i)).toFixed(0), { class: 'axis-label', 'text-anchor': 'end' });

    const x = margin.left + (chartWidth / 5) * i;
    svg += chart.line(x, margin.top, x, height - margin.bottom, { class: 'grid' });
    svg += chart.text(x, height - margin.bottom + 20, ((maxX / 5) * i).toFixed(0), { class: 'axis-label', 'text-anchor': 'middle' });
  }

  // 绘制点
  data.forEach((d, i) => {
    const x = margin.left + (xValues[i] / maxX) * chartWidth;
    const y = margin.top + chartHeight - (yValues[i] / maxY) * chartHeight;
    svg += chart.circle(x, y, 5, options.colors[i % options.colors.length], { opacity: '0.7' });
  });

  svg += chart.footer();
  return svg;
}

// 生成 HTML 包装
function wrapInHTML(svg, title) {
  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    body { 
      margin: 0; 
      padding: 20px; 
      background: #f5f5f5; 
      font-family: Arial, sans-serif;
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }
    .chart-container {
      background: white;
      padding: 20px;
      border-radius: 8px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
  </style>
</head>
<body>
  <div class="chart-container">
    ${svg}
  </div>
</body>
</html>`;
}

// 主函数
async function main() {
  console.log('╔════════════════════════════════════╗');
  console.log('║   DataMaster Pro - 数据可视化工具  ║');
  console.log('╚════════════════════════════════════╝\n');

  const options = parseArgs();

  if (!options.input) {
    console.log('使用方法:');
    console.log('  node data-viz.js --input <文件> [选项]');
    console.log('\n选项:');
    console.log('  --type, -t       图表类型: bar/line/pie/scatter (默认: bar)');
    console.log('  --output, -o     输出文件名 (默认: chart)');
    console.log('  --title          图表标题');
    console.log('  --x              X轴列名');
    console.log('  --y              Y轴列名');
    console.log('  --width          图表宽度 (默认: 800)');
    console.log('  --height         图表高度 (默认: 400)');
    console.log('  --format         输出格式: svg/html (默认: svg)');
    console.log('\n示例:');
    console.log('  node data-viz.js -i data.csv -t bar --title "销售数据"');
    console.log('  node data-viz.js -i data.json -t pie --x category --y amount');
    return;
  }

  try {
    console.log(`📂 读取数据: ${options.input}`);
    const data = readData(options.input);
    console.log(`✅ 读取 ${data.length} 条数据\n`);

    let svg;
    console.log(`📊 生成${options.type === 'bar' ? '柱状' : options.type === 'line' ? '折线' : options.type === 'pie' ? '饼' : '散点'}图...`);

    switch (options.type) {
      case 'bar':
        svg = generateBarChart(data, options);
        break;
      case 'line':
        svg = generateLineChart(data, options);
        break;
      case 'pie':
        svg = generatePieChart(data, options);
        break;
      case 'scatter':
        svg = generateScatterChart(data, options);
        break;
      default:
        svg = generateBarChart(data, options);
    }

    // 保存文件
    const ext = options.format === 'html' ? 'html' : 'svg';
    const outputFile = `${options.output}.${ext}`;
    const content = options.format === 'html' ? wrapInHTML(svg, options.title) : svg;

    fs.writeFileSync(outputFile, content);
    console.log(`💾 图表已保存到: ${outputFile}`);
    console.log('✨ 可视化完成！');

  } catch (error) {
    console.error('\n❌ 可视化失败:', error.message);
    process.exit(1);
  }
}

main();