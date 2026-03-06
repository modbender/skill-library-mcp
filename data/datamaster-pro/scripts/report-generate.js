#!/usr/bin/env node

/**
 * Data Analysis Skill - Report Generation
 * 自动生成数据报告
 * 
 * 功能：
 * - 从清洗后的数据生成分析报告
 * - 支持多种报告模板
 * - 输出PDF/HTML/Markdown格式
 * - 包含关键指标和洞察
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 配置文件路径
const CONFIG_PATH = path.join(__dirname, '..', 'config.json');
const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');
const OUTPUT_DIR = path.join(__dirname, '..', 'output');

// 确保输出目录存在
if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

class ReportGenerator {
    constructor() {
        this.config = this.loadConfig();
    }

    loadConfig() {
        try {
            const configContent = fs.readFileSync(CONFIG_PATH, 'utf8');
            return JSON.parse(configContent);
        } catch (error) {
            console.log('⚠️  未找到配置文件，使用默认配置');
            return {
                reportTemplate: 'default',
                outputFormat: 'html',
                includeCharts: true,
                language: 'zh-CN'
            };
        }
    }

    /**
     * 生成数据报告
     * @param {string} dataPath - 清洗后数据的路径
     * @param {string} reportName - 报告名称
     */
    generateReport(dataPath, reportName = 'data-report') {
        console.log('📊 开始生成数据报告...');
        
        // 读取清洗后的数据
        const rawData = fs.readFileSync(dataPath, 'utf8');
        let data;
        try {
            data = JSON.parse(rawData);
        } catch (error) {
            console.error('❌ 数据格式错误，无法解析JSON');
            return false;
        }

        // 执行数据分析
        const analysis = this.analyzeData(data);
        
        // 生成报告内容
        const reportContent = this.createReportContent(analysis, data);
        
        // 保存报告
        const timestamp = new Date().toISOString().split('T')[0];
        const outputBaseName = `${reportName}-${timestamp}`;
        
        if (this.config.outputFormat === 'pdf') {
            this.saveAsPDF(reportContent, outputBaseName);
        } else if (this.config.outputFormat === 'markdown') {
            this.saveAsMarkdown(reportContent, outputBaseName);
        } else {
            this.saveAsHTML(reportContent, outputBaseName);
        }
        
        console.log(`✅ 报告已生成: ${OUTPUT_DIR}/${outputBaseName}`);
        return true;
    }

    /**
     * 数据分析核心逻辑
     */
    analyzeData(data) {
        const analysis = {
            summary: {},
            insights: [],
            metrics: {},
            trends: []
        };

        // 基础统计信息
        analysis.summary.totalRecords = Array.isArray(data) ? data.length : Object.keys(data).length;
        analysis.summary.dataTypes = this.detectDataTypes(data);
        
        // 关键指标计算
        analysis.metrics = this.calculateMetrics(data);
        
        // 洞察发现
        analysis.insights = this.generateInsights(data, analysis.metrics);
        
        // 趋势分析（如果数据包含时间序列）
        if (this.hasTimeSeries(data)) {
            analysis.trends = this.analyzeTrends(data);
        }

        return analysis;
    }

    /**
     * 检测数据类型
     */
    detectDataTypes(data) {
        const types = {};
        if (Array.isArray(data) && data.length > 0) {
            const firstRecord = data[0];
            if (typeof firstRecord === 'object' && firstRecord !== null) {
                Object.keys(firstRecord).forEach(key => {
                    const value = firstRecord[key];
                    if (typeof value === 'number') {
                        types[key] = 'numeric';
                    } else if (typeof value === 'string') {
                        // 尝试判断是否为日期
                        if (this.isDateString(value)) {
                            types[key] = 'date';
                        } else {
                            types[key] = 'string';
                        }
                    } else if (typeof value === 'boolean') {
                        types[key] = 'boolean';
                    } else {
                        types[key] = typeof value;
                    }
                });
            }
        }
        return types;
    }

    /**
     * 判断字符串是否为日期格式
     */
    isDateString(str) {
        const datePatterns = [
            /^\d{4}-\d{2}-\d{2}$/,
            /^\d{4}\/\d{2}\/\d{2}$/,
            /^\d{2}\/\d{2}\/\d{4}$/,
            /^\d{1,2}-\d{1,2}-\d{4}$/
        ];
        return datePatterns.some(pattern => pattern.test(str));
    }

    /**
     * 计算关键指标
     */
    calculateMetrics(data) {
        const metrics = {};
        
        if (!Array.isArray(data) || data.length === 0) return metrics;

        // 获取数值字段
        const numericFields = [];
        const firstRecord = data[0];
        if (typeof firstRecord === 'object' && firstRecord !== null) {
            Object.keys(firstRecord).forEach(key => {
                if (typeof firstRecord[key] === 'number') {
                    numericFields.push(key);
                }
            });
        }

        // 为每个数值字段计算统计指标
        numericFields.forEach(field => {
            const values = data.map(record => record[field]).filter(val => !isNaN(val) && val !== null);
            if (values.length > 0) {
                metrics[field] = {
                    sum: values.reduce((a, b) => a + b, 0),
                    average: values.reduce((a, b) => a + b, 0) / values.length,
                    min: Math.min(...values),
                    max: Math.max(...values),
                    median: this.calculateMedian(values)
                };
            }
        });

        return metrics;
    }

    /**
     * 计算中位数
     */
    calculateMedian(values) {
        const sorted = [...values].sort((a, b) => a - b);
        const mid = Math.floor(sorted.length / 2);
        return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid];
    }

    /**
     * 生成业务洞察
     */
    generateInsights(data, metrics) {
        const insights = [];
        
        // 基于指标生成洞察
        Object.keys(metrics).forEach(field => {
            const metric = metrics[field];
            if (metric.max > metric.average * 2) {
                insights.push({
                    type: 'outlier',
                    message: `字段 "${field}" 存在显著异常值，最大值(${metric.max})是平均值(${metric.average.toFixed(2)})的${(metric.max/metric.average).toFixed(1)}倍`,
                    severity: 'high'
                });
            }
            
            if (metric.average > 0 && metric.min === 0) {
                insights.push({
                    type: 'zero_values',
                    message: `字段 "${field}" 包含零值，可能表示缺失数据或特殊状态`,
                    severity: 'medium'
                });
            }
        });

        // 数据完整性检查
        const totalRecords = data.length;
        const completeRecords = data.filter(record => {
            return Object.values(record).every(value => value !== null && value !== undefined && value !== '');
        }).length;
        
        const completeness = (completeRecords / totalRecords) * 100;
        if (completeness < 95) {
            insights.push({
                type: 'data_completeness',
                message: `数据完整性为 ${completeness.toFixed(1)}%，建议检查数据质量`,
                severity: 'medium'
            });
        }

        return insights;
    }

    /**
     * 检查是否包含时间序列数据
     */
    hasTimeSeries(data) {
        if (!Array.isArray(data) || data.length === 0) return false;
        
        const firstRecord = data[0];
        if (typeof firstRecord !== 'object' || firstRecord === null) return false;
        
        return Object.keys(firstRecord).some(key => {
            const value = firstRecord[key];
            return typeof value === 'string' && this.isDateString(value);
        });
    }

    /**
     * 时间序列趋势分析
     */
    analyzeTrends(data) {
        const trends = [];
        
        // 找到日期字段
        let dateField = null;
        const firstRecord = data[0];
        Object.keys(firstRecord).forEach(key => {
            if (typeof firstRecord[key] === 'string' && this.isDateString(firstRecord[key])) {
                dateField = key;
            }
        });
        
        if (!dateField) return trends;
        
        // 按日期排序
        const sortedData = [...data].sort((a, b) => {
            return new Date(a[dateField]) - new Date(b[dateField]);
        });
        
        // 分析数值字段的趋势
        Object.keys(firstRecord).forEach(key => {
            if (typeof firstRecord[key] === 'number') {
                const trend = this.calculateTrend(sortedData, dateField, key);
                if (trend) {
                    trends.push(trend);
                }
            }
        });
        
        return trends;
    }

    /**
     * 计算单个字段的趋势
     */
    calculateTrend(data, dateField, valueField) {
        if (data.length < 2) return null;
        
        const firstValue = data[0][valueField];
        const lastValue = data[data.length - 1][valueField];
        
        if (firstValue === null || lastValue === null || isNaN(firstValue) || isNaN(lastValue)) {
            return null;
        }
        
        const change = lastValue - firstValue;
        const changePercent = (change / firstValue) * 100;
        const direction = change > 0 ? '上升' : change < 0 ? '下降' : '稳定';
        
        return {
            field: valueField,
            direction: direction,
            change: change,
            changePercent: changePercent,
            period: `${data[0][dateField]} 至 ${data[data.length - 1][dateField]}`
        };
    }

    /**
     * 创建报告内容
     */
    createReportContent(analysis, rawData) {
        const templatePath = path.join(TEMPLATES_DIR, `${this.config.reportTemplate}.md`);
        let templateContent;
        
        try {
            templateContent = fs.readFileSync(templatePath, 'utf8');
        } catch (error) {
            console.log('⚠️  未找到模板文件，使用默认模板');
            templateContent = this.getDefaultTemplate();
        }
        
        // 替换模板变量
        let reportContent = templateContent
            .replace('{{REPORT_TITLE}}', '数据分析报告')
            .replace('{{GENERATION_DATE}}', new Date().toLocaleString('zh-CN'))
            .replace('{{TOTAL_RECORDS}}', analysis.summary.totalRecords)
            .replace('{{DATA_TYPES}}', JSON.stringify(analysis.summary.dataTypes, null, 2));
        
        // 添加关键指标
        let metricsContent = '';
        Object.keys(analysis.metrics).forEach(field => {
            const metric = analysis.metrics[field];
            metricsContent += `\n### ${field}\n`;
            metricsContent += `- 总计: ${metric.sum.toLocaleString()}\n`;
            metricsContent += `- 平均值: ${metric.average.toFixed(2)}\n`;
            metricsContent += `- 最小值: ${metric.min}\n`;
            metricsContent += `- 最大值: ${metric.max}\n`;
            metricsContent += `- 中位数: ${metric.median.toFixed(2)}\n`;
        });
        reportContent = reportContent.replace('{{KEY_METRICS}}', metricsContent);
        
        // 添加洞察
        let insightsContent = '';
        if (analysis.insights.length > 0) {
            insightsContent = '\n## 🔍 关键洞察\n';
            analysis.insights.forEach(insight => {
                const severityEmoji = insight.severity === 'high' ? '🔴' : insight.severity === 'medium' ? '🟡' : '🟢';
                insightsContent += `\n${severityEmoji} **${insight.message}**\n`;
            });
        }
        reportContent = reportContent.replace('{{INSIGHTS}}', insightsContent);
        
        // 添加趋势分析
        let trendsContent = '';
        if (analysis.trends.length > 0) {
            trendsContent = '\n## 📈 趋势分析\n';
            analysis.trends.forEach(trend => {
                const trendEmoji = trend.direction === '上升' ? '📈' : trend.direction === '下降' ? '📉' : '➡️';
                trendsContent += `\n${trendEmoji} **${trend.field}**: ${trend.direction} ${trend.changePercent > 0 ? '+' : ''}${trend.changePercent.toFixed(1)}% (${trend.period})\n`;
            });
        }
        reportContent = reportContent.replace('{{TRENDS}}', trendsContent);
        
        return reportContent;
    }

    /**
     * 默认报告模板
     */
    getDefaultTemplate() {
        return `# {{REPORT_TITLE}}

生成时间: {{GENERATION_DATE}}

## 📊 数据概览
- 总记录数: {{TOTAL_RECORDS}}
- 数据类型: 
\`\`\`json
{{DATA_TYPES}}
\`\`\`

## 📏 关键指标
{{KEY_METRICS}}

{{INSIGHTS}}

{{TRENDS}}

---
*本报告由 AI 数据分析技能包自动生成*
`;
    }

    /**
     * 保存为HTML格式
     */
    saveAsHTML(content, fileName) {
        const htmlContent = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>数据分析报告</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1, h2, h3 { color: #2c3e50; }
        h1 { border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        h2 { border-left: 4px solid #3498db; padding-left: 10px; margin-top: 30px; }
        pre { background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto; }
        code { background: #f1f1f1; padding: 2px 4px; border-radius: 3px; }
        .insight { margin: 10px 0; padding: 10px; border-left: 4px solid #f39c12; background: #fef9e7; }
        .trend-up { color: #27ae60; }
        .trend-down { color: #e74c3c; }
    </style>
</head>
<body>
${content}
</body>
</html>
        `;
        fs.writeFileSync(path.join(OUTPUT_DIR, `${fileName}.html`), htmlContent, 'utf8');
    }

    /**
     * 保存为Markdown格式
     */
    saveAsMarkdown(content, fileName) {
        fs.writeFileSync(path.join(OUTPUT_DIR, `${fileName}.md`), content, 'utf8');
    }

    /**
     * 保存为PDF格式（需要外部工具）
     */
    saveAsPDF(content, fileName) {
        // 先保存为HTML
        this.saveAsHTML(content, fileName);
        
        // 尝试使用外部工具转换为PDF
        try {
            const htmlPath = path.join(OUTPUT_DIR, `${fileName}.html`);
            const pdfPath = path.join(OUTPUT_DIR, `${fileName}.pdf`);
            
            // 检查是否安装了wkhtmltopdf或其他PDF工具
            execSync('wkhtmltopdf --version', { stdio: 'ignore' });
            execSync(`wkhtmltopdf "${htmlPath}" "${pdfPath}"`, { stdio: 'ignore' });
            console.log('📄 PDF报告已生成');
            
            // 删除临时HTML文件
            fs.unlinkSync(htmlPath);
        } catch (error) {
            console.log('⚠️  未安装PDF生成工具，仅生成HTML报告');
            console.log('💡 安装 wkhtmltopdf 可以生成PDF报告');
        }
    }
}

// 主函数
function main() {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('用法: node report-generate.js <数据文件路径> [报告名称]');
        console.log('示例: node report-generate.js ./data/cleaned-data.json 销售分析报告');
        process.exit(1);
    }
    
    const dataPath = args[0];
    const reportName = args[1] || 'data-report';
    
    if (!fs.existsSync(dataPath)) {
        console.error('❌ 数据文件不存在:', dataPath);
        process.exit(1);
    }
    
    const generator = new ReportGenerator();
    generator.generateReport(dataPath, reportName);
}

if (require.main === module) {
    main();
}

module.exports = ReportGenerator;