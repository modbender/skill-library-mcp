const fs = require('fs').promises;
const path = require('path');

// 从内存文件中提取工作记录（修复版：去除重复和多余格式）
async function extractWorkFromMemoryFiles() {
    const workRecords = [];
    try {
        // 读取 memory 目录
        const memoryDir = '/home/admin/openclaw/workspace/memory';
        const files = await fs.readdir(memoryDir);
        
        // 过滤出日期格式的文件（YYYY-MM-DD.md）
        const dateFiles = files.filter(file => 
            file.match(/^\d{4}-\d{2}-\d{2}\.md$/) && 
            file !== 'heartbeat-state.json'
        );
        
        // 按日期排序，最新的在前
        dateFiles.sort((a, b) => {
            const dateA = new Date(a.replace('.md', ''));
            const dateB = new Date(b.replace('.md', ''));
            return dateB - dateA;
        });
        
        // 只处理最近的几个文件
        const recentFiles = dateFiles.slice(0, 5);
        
        for (const file of recentFiles) {
            try {
                const filePath = path.join(memoryDir, file);
                const content = await fs.readFile(filePath, 'utf8');
                const workItems = parseMemoryFile(content, file);
                workRecords.push(...workItems);
            } catch (error) {
                console.warn(`无法读取内存文件 ${file}:`, error.message);
            }
        }
    } catch (error) {
        console.warn('无法读取 memory 目录:', error.message);
    }
    
    return workRecords;
}

// 解析内存文件内容，提取工作记录（修复版：清理格式）
function parseMemoryFile(content, filename) {
    const workItems = [];
    const lines = content.split('\n');
    let inWorkSection = false;
    
    // 从文件名提取日期
    const dateMatch = filename.match(/^(\d{4}-\d{2}-\d{2})\.md$/);
    const fileDate = dateMatch ? new Date(dateMatch[1]) : new Date();
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        
        // 检查是否是工作相关的标题
        if (line.startsWith('## ') || line.startsWith('### ')) {
            const sectionTitle = line.replace(/^#+\s*/, '').trim();
            if (sectionTitle.includes('工作') || sectionTitle.includes('开发') || 
                sectionTitle.includes('任务') || sectionTitle.includes('Todo')) {
                inWorkSection = true;
                continue;
            } else {
                inWorkSection = false;
            }
        }
        
        // 在工作相关章节中，提取列表项
        if (inWorkSection && (line.startsWith('- ') || line.startsWith('* ') || line.match(/^\d+\./))) {
            let itemText = line.replace(/^[-*]\s*|\d+\.\s*/, '').trim();
            if (itemText) {
                // 清理多余的星号和格式
                itemText = itemText.replace(/\*\*/g, ''); // 去除加粗标记
                itemText = itemText.replace(/\s+$/, ''); // 去除尾部空格
                
                // 移除标题中的完成度信息（因为描述中会显示）
                if (itemText.includes('完成度') || itemText.includes('进度')) {
                    // 提取完成度数字
                    const percentMatch = itemText.match(/(\d+)%/);
                    const completion = percentMatch ? parseInt(percentMatch[1]) : 100;
                    
                    // 从标题中移除完成度部分
                    itemText = itemText.replace(/[-—–]\s*完成度.*$/i, '');
                    itemText = itemText.replace(/[-—–]\s*\d+%.*$/i, '');
                    itemText = itemText.trim().replace(/[-—–]$/, '').trim();
                    
                    workItems.push({
                        id: workItems.length + 1,
                        title: itemText.substring(0, 50),
                        description: `小雨自评完成度：${completion}%`,
                        timestamp: fileDate.toISOString(),
                        status: completion === 100 ? "completed" : "in_progress",
                        type: "development",
                        completion: completion
                    });
                } else {
                    // 默认已完成
                    workItems.push({
                        id: workItems.length + 1,
                        title: itemText.substring(0, 50),
                        description: `小雨自评完成度：100%`,
                        timestamp: fileDate.toISOString(),
                        status: "completed",
                        type: "development",
                        completion: 100
                    });
                }
            }
        }
    }
    
    return workItems;
}

// 主函数：获取最近的工作任务（修复版）
async function getRecentWorkTasksFixed() {
    try {
        // 优先从内存文件中获取工作记录
        let workRecords = await extractWorkFromMemoryFiles();
        
        // 去重：基于标题去重
        const uniqueRecords = [];
        const seenTitles = new Set();
        
        for (const record of workRecords) {
            if (!seenTitles.has(record.title)) {
                seenTitles.add(record.title);
                uniqueRecords.push(record);
            }
        }
        
        // 如果还是没有记录，返回一些默认记录
        if (uniqueRecords.length === 0) {
            uniqueRecords.push({
                id: 1,
                title: "系统初始化",
                description: "小雨自评完成度：100%",
                timestamp: new Date().toISOString(),
                status: "completed",
                type: "system",
                completion: 100
            });
        }
        
        // 确保只返回最近的3个记录
        return uniqueRecords.slice(0, 3);
    } catch (error) {
        console.error('获取工作记录时出错:', error);
        // 返回安全的默认值
        return [
            {
                id: 1,
                title: "数据加载中...",
                description: "小雨自评完成度：0%",
                timestamp: new Date().toISOString(),
                status: "in_progress",
                type: "system",
                completion: 0
            }
        ];
    }
}

module.exports = { getRecentWorkTasksFixed };