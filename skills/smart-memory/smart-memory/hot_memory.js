#!/usr/bin/env node
/**
 * Hot Memory - Working Memory for Active Context
 * 
 * Reads and parses .hot_memory.md for quick access to:
 * - Active projects
 * - Recent decisions
 * - Open questions
 * - Recent topics
 * 
 * Hot memory is checked FIRST before expensive vector searches.
 */

import fs from 'fs';
import path from 'path';

const HOT_MEMORY_PATH = process.env.HOT_MEMORY_PATH || '/config/.openclaw/workspace/memory/.hot_memory.md';

/**
 * Parse hot memory file content into structured data
 */
function parseHotMemory(content) {
    const data = {
        lastUpdated: null,
        recentDecisions: [],
        openQuestions: [],
        recentTopics: [],
        activeProject: null,
        raw: content,
    };
    
    // Extract last updated timestamp
    const updatedMatch = content.match(/Last Updated:\s*([^\n]+)/);
    if (updatedMatch) {
        data.lastUpdated = updatedMatch[1].trim();
    }
    
    // Extract sections
    const sections = {
        'Recent Decisions': 'recentDecisions',
        'Open Questions': 'openQuestions',
        'Recent Topics': 'recentTopics',
        'Active Project': 'activeProject',
    };
    
    for (const [sectionName, key] of Object.entries(sections)) {
        const sectionRegex = new RegExp(`##\\s*${sectionName}\\s*\\n([^#]*)`, 'i');
        const match = content.match(sectionRegex);
        
        if (match) {
            const sectionContent = match[1].trim();
            
            if (key === 'activeProject') {
                // Active project is typically a single line
                data[key] = sectionContent.split('\n')[0].trim();
            } else {
                // Other sections are lists
                const items = sectionContent
                    .split('\n')
                    .map(line => line.trim())
                    .filter(line => line.startsWith('-') || line.startsWith('*'))
                    .map(line => line.replace(/^[-*]\s*/, '').trim())
                    .filter(line => line.length > 0);
                data[key] = items;
            }
        }
    }
    
    return data;
}

/**
 * Read hot memory file
 * @returns {Object} { found: boolean, data: Object|null, lastUpdated: string|null }
 */
export function readHotMemory() {
    try {
        if (!fs.existsSync(HOT_MEMORY_PATH)) {
            return {
                found: false,
                data: null,
                lastUpdated: null,
                message: 'No .hot_memory.md file found',
            };
        }
        
        const content = fs.readFileSync(HOT_MEMORY_PATH, 'utf-8');
        const data = parseHotMemory(content);
        
        return {
            found: true,
            data,
            lastUpdated: data.lastUpdated,
            path: HOT_MEMORY_PATH,
        };
    } catch (err) {
        return {
            found: false,
            data: null,
            lastUpdated: null,
            error: err.message,
        };
    }
}

/**
 * Search hot memory for relevant context
 * Simple keyword matching against all text content
 * @param {string} query - Search query
 * @returns {Object} { found: boolean, matches: Array, context: Object }
 */
export function searchHotMemory(query) {
    const hotMemory = readHotMemory();
    
    if (!hotMemory.found) {
        return {
            found: false,
            matches: [],
            context: null,
        };
    }
    
    const queryLower = query.toLowerCase();
    const queryWords = queryLower.split(/\s+/).filter(w => w.length > 2);
    const matches = [];
    
    // Search in active project
    if (hotMemory.data.activeProject) {
        const projectLower = hotMemory.data.activeProject.toLowerCase();
        const score = calculateRelevance(projectLower, queryLower, queryWords);
        if (score > 0) {
            matches.push({
                type: 'activeProject',
                content: hotMemory.data.activeProject,
                score,
            });
        }
    }
    
    // Search in recent decisions
    for (const decision of hotMemory.data.recentDecisions) {
        const decisionLower = decision.toLowerCase();
        const score = calculateRelevance(decisionLower, queryLower, queryWords);
        if (score > 0) {
            matches.push({
                type: 'recentDecision',
                content: decision,
                score,
            });
        }
    }
    
    // Search in open questions
    for (const question of hotMemory.data.openQuestions) {
        const questionLower = question.toLowerCase();
        const score = calculateRelevance(questionLower, queryLower, queryWords);
        if (score > 0) {
            matches.push({
                type: 'openQuestion',
                content: question,
                score,
            });
        }
    }
    
    // Search in recent topics
    for (const topic of hotMemory.data.recentTopics) {
        const topicLower = topic.toLowerCase();
        const score = calculateRelevance(topicLower, queryLower, queryWords);
        if (score > 0) {
            matches.push({
                type: 'recentTopic',
                content: topic,
                score,
            });
        }
    }
    
    // Sort by relevance score
    matches.sort((a, b) => b.score - a.score);
    
    return {
        found: true,
        matches: matches.slice(0, 5), // Top 5 matches
        context: {
            activeProject: hotMemory.data.activeProject,
            hasRecentDecisions: hotMemory.data.recentDecisions.length > 0,
            hasOpenQuestions: hotMemory.data.openQuestions.length > 0,
        },
    };
}

/**
 * Calculate simple relevance score
 */
function calculateRelevance(text, query, queryWords) {
    let score = 0;
    
    // Exact match gets highest score
    if (text.includes(query)) {
        score += 10;
    }
    
    // Word matches
    for (const word of queryWords) {
        if (text.includes(word)) {
            score += 1;
        }
    }
    
    return score;
}

/**
 * Get quick context for session start
 * Returns essential info without full parsing
 */
export function getQuickContext() {
    const hotMemory = readHotMemory();
    
    if (!hotMemory.found) {
        return null;
    }
    
    return {
        activeProject: hotMemory.data.activeProject,
        recentDecisions: hotMemory.data.recentDecisions.slice(0, 3),
        openQuestions: hotMemory.data.openQuestions.slice(0, 2),
    };
}

// CLI interface
if (process.argv[1] === new URL(import.meta.url).pathname) {
    const args = process.argv.slice(2);
    const command = args[0];
    
    if (command === '--read') {
        const result = readHotMemory();
        console.log(JSON.stringify(result, null, 2));
    } else if (command === '--search') {
        const query = args[1];
        if (!query) {
            console.error('Usage: --search "query"');
            process.exit(1);
        }
        const result = searchHotMemory(query);
        console.log(JSON.stringify(result, null, 2));
    } else {
        console.log(`
Hot Memory - Quick Context Access

Usage:
  node hot_memory.js --read
    Read and parse .hot_memory.md

  node hot_memory.js --search "query"
    Search hot memory for relevant context

This module provides instant access to active context
before running expensive vector searches.
`);
    }
}
