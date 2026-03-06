#!/usr/bin/env node
/**
 * Memory Deduplication Tool
 * 记忆去重与合并
 */

import fs from 'fs';
import path from 'path';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || process.cwd();
const DRY_RUN = process.argv.includes('--dry-run');
const BACKUP = process.argv.includes('--backup') || !DRY_RUN;

// Jaccard 相似度
function similarity(text1, text2) {
  const words1 = new Set(text1.toLowerCase().split(/\s+/));
  const words2 = new Set(text2.toLowerCase().split(/\s+/));
  const intersection = new Set([...words1].filter(x => words2.has(x)));
  const union = new Set([...words1, ...words2]);
  return intersection.size / union.size;
}

// 解析 MEMORY.md
function parseMemory(content) {
  const sections = [];
  let currentSection = null;
  
  content.split('\n').forEach(line => {
    if (line.startsWith('###')) {
      if (currentSection) sections.push(currentSection);
      currentSection = {
        title: line.replace(/^###\s*/, ''),
        content: [],
        priority: line.match(/\[P(\d)\]/) ? parseInt(line.match(/\[P(\d)\]/)[1]) : 9
      };
    } else if (currentSection && line.trim()) {
      currentSection.content.push(line);
    }
  });
  if (currentSection) sections.push(currentSection);
  
  return sections;
}

// 查找重复
function findDuplicates(sections) {
  const duplicates = [];
  
  for (let i = 0; i < sections.length; i++) {
    for (let j = i + 1; j < sections.length; j++) {
      const sim = similarity(sections[i].title, sections[j].title);
      if (sim > 0.5) {
        duplicates.push({
          index1: i,
          index2: j,
          similarity: sim,
          section1: sections[i],
          section2: sections[j]
        });
      }
    }
  }
  
  return duplicates.sort((a, b) => b.similarity - a.similarity);
}

// 合并两个 section
function mergeSections(s1, s2) {
  return {
    title: s1.priority <= s2.priority ? s1.title : s2.title,
    content: [...new Set([...s1.content, ...s2.content])],
    priority: Math.min(s1.priority, s2.priority)
  };
}

// 去重
function deduplicate(sections) {
  const duplicates = findDuplicates(sections);
  const toRemove = new Set();
  const merged = new Map();
  
  duplicates.forEach(dup => {
    if (dup.similarity > 0.8) {
      // 完全重复，删除一个
      toRemove.add(dup.index2);
    } else if (dup.similarity > 0.5) {
      // 部分重复，合并
      if (!toRemove.has(dup.index1) && !toRemove.has(dup.index2)) {
        const mergedSection = mergeSections(dup.section1, dup.section2);
        merged.set(dup.index1, mergedSection);
        toRemove.add(dup.index2);
      }
    }
  });
  
  // 应用合并和删除
  const result = sections
    .map((s, i) => merged.get(i) || s)
    .filter((s, i) => !toRemove.has(i));
  
  return {
    sections: result,
    stats: {
      original: sections.length,
      duplicates: duplicates.length,
      merged: merged.size,
      removed: toRemove.size,
      final: result.length
    }
  };
}

// 重建 MEMORY.md
function rebuildMemory(sections) {
  let content = '# MEMORY.md — 龙虾的长期记忆\n\n';
  
  sections.forEach(section => {
    const priority = section.priority < 9 ? `[P${section.priority}] ` : '';
    content += `### ${priority}${section.title}\n`;
    section.content.forEach(line => {
      content += `${line}\n`;
    });
    content += '\n';
  });
  
  return content;
}

// 主函数
const memoryPath = path.join(WORKSPACE, 'MEMORY.md');

if (!fs.existsSync(memoryPath)) {
  console.error('❌ MEMORY.md not found');
  process.exit(1);
}

const originalContent = fs.readFileSync(memoryPath, 'utf-8');
const sections = parseMemory(originalContent);
const { sections: dedupedSections, stats } = deduplicate(sections);
const newContent = rebuildMemory(dedupedSections);

console.log('=== Memory Deduplication Report ===\n');
console.log('📊 统计:');
console.log(`- 原始条目: ${stats.original}`);
console.log(`- 重复条目: ${stats.duplicates}`);
console.log(`- 合并条目: ${stats.merged}`);
console.log(`- 删除条目: ${stats.removed}`);
console.log(`- 最终条目: ${stats.final}`);

if (DRY_RUN) {
  console.log('\n🔍 预览模式，未修改文件');
  console.log('\n--- 新内容预览 (前 500 字符) ---');
  console.log(newContent.substring(0, 500));
} else {
  if (BACKUP) {
    const backupPath = path.join(
      WORKSPACE,
      'memory',
      `MEMORY-backup-${new Date().toISOString().split('T')[0]}.md`
    );
    fs.mkdirSync(path.dirname(backupPath), { recursive: true });
    fs.writeFileSync(backupPath, originalContent);
    console.log(`\n💾 备份保存到: ${backupPath}`);
  }
  
  fs.writeFileSync(memoryPath, newContent);
  console.log('\n✅ MEMORY.md 已优化');
}