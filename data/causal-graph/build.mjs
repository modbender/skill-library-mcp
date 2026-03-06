#!/usr/bin/env node
/**
 * Causal Graph Builder
 * 从记忆文件自动构建因果图谱
 */

import fs from 'fs';
import path from 'path';

const WORKSPACE = process.env.OPENCLAW_WORKSPACE || process.cwd();

// 实体类型
const ENTITY_PATTERNS = {
  project: /AgentAwaken|NeuroBoost|ClawWork|Conway|RMN Soul/gi,
  tool: /GitHub|Vercel|ClawHub|Cloudflare|pnpm|npm|git/gi,
  person: /瓜农|龙虾|Jason Zuo/gi,
  concept: /永续记忆|三层架构|P0标记|记忆健康度|因果图谱/gi
};

// 因果关系模式
const CAUSAL_PATTERNS = {
  causes: /导致|造成|引起|所以/g,
  enables: /使得|让|允许|可以/g,
  requires: /需要|依赖|基于|要求/g,
  relates: /相关|关于|涉及/g
};

// 提取实体
function extractEntities(text) {
  const entities = new Map();
  
  Object.entries(ENTITY_PATTERNS).forEach(([type, pattern]) => {
    const matches = text.match(pattern) || [];
    matches.forEach(match => {
      const id = match.toLowerCase().replace(/\s+/g, '-');
      if (!entities.has(id)) {
        entities.set(id, { id, type, label: match, mentions: 0 });
      }
      entities.get(id).mentions++;
    });
  });
  
  return Array.from(entities.values());
}

// 提取事件
function extractEvents(text) {
  const events = [];
  const lines = text.split('\n');
  
  lines.forEach(line => {
    // 匹配日期格式: [2026-03-01], 2026-03-01, 2026/03/01
    const dateMatch = line.match(/\[?(\d{4}[-/]\d{2}[-/]\d{2})\]?/);
    if (dateMatch) {
      const timestamp = dateMatch[1].replace(/\//g, '-');
      // 提取动作词
      const actionMatch = line.match(/(创建|发布|部署|实施|完成|更新|添加|删除|修复)/);
      if (actionMatch) {
        events.push({
          id: `event-${timestamp}-${events.length}`,
          type: 'event',
          label: line.trim().substring(0, 50),
          timestamp,
          action: actionMatch[1]
        });
      }
    }
  });
  
  return events;
}

// 提取因果关系
function extractCausalRelations(text, entities) {
  const relations = [];
  const sentences = text.split(/[。！？\n]/);
  
  sentences.forEach(sentence => {
    // 查找句子中的实体
    const foundEntities = entities.filter(e => 
      sentence.includes(e.label)
    );
    
    if (foundEntities.length >= 2) {
      // 检查因果关系词
      Object.entries(CAUSAL_PATTERNS).forEach(([relType, pattern]) => {
        if (pattern.test(sentence)) {
          relations.push({
            from: foundEntities[0].id,
            to: foundEntities[1].id,
            type: relType,
            context: sentence.trim().substring(0, 100)
          });
        }
      });
    }
  });
  
  return relations;
}

// 构建图谱
function buildGraph() {
  const graph = { nodes: [], edges: [] };
  
  // 读取记忆文件
  const files = [
    'MEMORY.md',
    'memory/INDEX.md',
    ...fs.readdirSync(path.join(WORKSPACE, 'memory'))
      .filter(f => /^\d{4}-\d{2}-\d{2}\.md$/.test(f))
      .slice(-7) // 最近 7 天
      .map(f => `memory/${f}`)
  ];
  
  let allText = '';
  files.forEach(file => {
    const filePath = path.join(WORKSPACE, file);
    if (fs.existsSync(filePath)) {
      allText += fs.readFileSync(filePath, 'utf-8') + '\n';
    }
  });
  
  // 提取实体和事件
  const entities = extractEntities(allText);
  const events = extractEvents(allText);
  graph.nodes = [...entities, ...events];
  
  // 提取关系
  graph.edges = extractCausalRelations(allText, entities);
  
  // 统计
  const stats = {
    totalNodes: graph.nodes.length,
    entities: entities.length,
    events: events.length,
    relations: graph.edges.length,
    byType: {}
  };
  
  graph.nodes.forEach(n => {
    stats.byType[n.type] = (stats.byType[n.type] || 0) + 1;
  });
  
  return { graph, stats };
}

// 主函数
const { graph, stats } = buildGraph();

console.log('=== Causal Graph Built ===');
console.log(JSON.stringify(stats, null, 2));
console.log('\n=== Sample Nodes ===');
console.log(JSON.stringify(graph.nodes.slice(0, 5), null, 2));
console.log('\n=== Sample Edges ===');
console.log(JSON.stringify(graph.edges.slice(0, 5), null, 2));

// 保存
const outputPath = path.join(WORKSPACE, 'memory/causal-graph.json');
fs.writeFileSync(outputPath, JSON.stringify(graph, null, 2));
console.log(`\n✅ Graph saved to ${outputPath}`);