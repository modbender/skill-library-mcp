/**
 * 初中数学教学资源查找功能
 * 根据年级、章节、知识点快速定位教学资源
 */

const fs = require('fs');
const path = require('path');

class MathResourceFinder {
  constructor() {
    this.basePath = 'E:\\教学资料';
    this.resourceIndex = {
      '七年级': this.loadIndex('七年级资源索引.md'),
      '八年级': this.loadIndex('八年级资源索引.md'),
      '九年级': this.loadIndex('九年级资源索引.md')
    };
  }

  /**
   * 加载资源索引
   */
  loadIndex(indexName) {
    try {
      const indexPath = path.join(__dirname, '..', 'resources', indexName);
      if (fs.existsSync(indexPath)) {
        return fs.readFileSync(indexPath, 'utf-8');
      }
      return '';
    } catch (error) {
      console.error(`加载索引失败: ${indexName}`, error);
      return '';
    }
  }

  /**
   * 查找资源
   * @param {string} grade 年级
   * @param {string} chapter 章节
   * @param {string} keyword 关键词
   */
  findResources(grade, chapter = '', keyword = '') {
    const indexContent = this.resourceIndex[grade];
    if (!indexContent) {
      return {
        success: false,
        message: `未找到${grade}的资源索引`
      };
    }

    let results = [];
    const lines = indexContent.split('\n');
    
    // 简单的内容匹配
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      let match = false;
      
      if (chapter && line.includes(chapter)) {
        match = true;
      }
      
      if (keyword && line.includes(keyword)) {
        match = true;
      }
      
      if (match) {
        // 获取相关上下文
        const context = [];
        for (let j = Math.max(0, i - 2); j < Math.min(lines.length, i + 3); j++) {
          context.push(lines[j]);
        }
        results.push({
          line: line.trim(),
          context: context.join('\n'),
          lineNumber: i + 1
        });
      }
    }

    return {
      success: true,
      grade,
      chapter,
      keyword,
      count: results.length,
      results: results.slice(0, 10) // 限制结果数量
    };
  }

  /**
   * 获取年级所有章节
   */
  getChapters(grade) {
    const indexContent = this.resourceIndex[grade];
    if (!indexContent) {
      return [];
    }

    const chapters = [];
    const lines = indexContent.split('\n');
    
    // 查找章节标题（以#或##开头）
    for (const line of lines) {
      if (line.startsWith('### ') || line.startsWith('## ') || line.startsWith('# ')) {
        const chapter = line.replace(/^#+\s*/, '').trim();
        if (chapter && !chapter.includes('资源位置') && !chapter.includes('教学特点')) {
          chapters.push(chapter);
        }
      }
    }

    return [...new Set(chapters)]; // 去重
  }

  /**
   * 获取资源详情
   */
  getResourceDetails(grade, resourceName) {
    const indexContent = this.resourceIndex[grade];
    if (!indexContent) {
      return null;
    }

    const lines = indexContent.split('\n');
    let inTargetSection = false;
    let details = [];
    
    for (const line of lines) {
      if (line.includes(resourceName)) {
        inTargetSection = true;
      }
      
      if (inTargetSection) {
        details.push(line);
        
        // 如果遇到下一个章节标题，停止收集
        if (line.startsWith('### ') && !line.includes(resourceName)) {
          break;
        }
      }
    }

    return details.length > 0 ? details.join('\n') : null;
  }
}

// 导出模块
module.exports = {
  MathResourceFinder,
  
  // 快捷函数
  find: (grade, chapter, keyword) => {
    const finder = new MathResourceFinder();
    return finder.findResources(grade, chapter, keyword);
  },
  
  listChapters: (grade) => {
    const finder = new MathResourceFinder();
    return finder.getChapters(grade);
  },
  
  getDetails: (grade, resourceName) => {
    const finder = new MathResourceFinder();
    return finder.getResourceDetails(grade, resourceName);
  }
};