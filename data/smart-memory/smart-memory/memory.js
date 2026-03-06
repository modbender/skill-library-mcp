#!/usr/bin/env node
/**
 * OpenClaw Memory Tool Integration
 * Drop-in replacement for built-in memory_search using local vector embeddings
 * 
 * Features:
 * - Checks .hot_memory.md FIRST (instant)
 * - Falls back to vector search (semantic + BM25)
 * - 100% local, no API keys needed
 * - Compatible with OpenClaw memory tool interface
 */

import { execSync } from 'child_process';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WORKSPACE = '/config/.openclaw/workspace';
const HOT_MEMORY_PATH = path.join(WORKSPACE, 'memory', '.hot_memory.md');

/**
 * Read hot memory file for instant context
 */
function readHotMemory() {
    try {
        if (!fs.existsSync(HOT_MEMORY_PATH)) {
            return null;
        }
        return fs.readFileSync(HOT_MEMORY_PATH, 'utf-8');
    } catch (err) {
        return null;
    }
}

/**
 * Search hot memory for relevant context (simple keyword matching)
 */
function searchHotMemory(query) {
    const content = readHotMemory();
    if (!content) return null;
    
    const queryLower = query.toLowerCase();
    const lines = content.split('\n');
    const matches = [];
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line.toLowerCase().includes(queryLower)) {
            matches.push({
                path: 'memory/.hot_memory.md',
                line: i + 1,
                content: line.trim(),
                source: 'hot_memory',
            });
        }
    }
    
    return matches.length > 0 ? matches : null;
}

/**
 * Search memory using vector embeddings
 * Checks hot memory FIRST, then does vector search
 */
export async function memorySearch(query, maxResults = 5) {
    // First, check hot memory (instant)
    const hotMatches = searchHotMemory(query);
    
    try {
        // Run vector search
        const result = execSync(
            `node ${path.join(__dirname, 'smart_memory.js')} --search ${JSON.stringify(query)} --max-results ${maxResults} --no-hot`,
            { 
                cwd: WORKSPACE, 
                encoding: 'utf-8',
                timeout: 60000 // 60 second timeout for model loading
            }
        );
        
        const parsed = JSON.parse(result);
        
        // If we have hot memory matches, prepend them
        if (hotMatches && hotMatches.length > 0) {
            const hotResults = hotMatches.map(m => ({
                path: m.path,
                lines: `${m.line}`,
                score: 1.0, // Hot memory gets highest priority
                snippet: m.content,
                source: 'hot_memory',
            }));
            
            // Combine: hot memory first, then vector results
            parsed.results = [...hotResults, ...parsed.results.slice(0, maxResults - hotResults.length)];
        }
        
        // Convert to OpenClaw-compatible format
        return parsed.results.map(r => ({
            path: r.path,
            lines: typeof r.lines === 'number' ? `${r.from}-${r.from + r.lines - 1}` : r.lines,
            score: r.score,
            snippet: r.snippet,
            source: r.source || 'vector',
        }));
    } catch (error) {
        console.error('Vector memory search failed:', error.message);
        
        // Fallback to hot memory only
        if (hotMatches) {
            return hotMatches.map(m => ({
                path: m.path,
                lines: `${m.line}`,
                score: 0.9,
                snippet: m.content,
                source: 'hot_memory',
            }));
        }
        
        return [];
    }
}

/**
 * Get full content from a memory file
 * SECURE: Prevents path traversal by resolving and validating path
 */
export function memoryGet(filePath, from, lines) {
    try {
        // Resolve to absolute path and normalize
        const requestedPath = path.resolve(WORKSPACE, filePath);
        const workspaceRoot = path.resolve(WORKSPACE);
        
        // SECURITY: Ensure the resolved path is within the workspace
        if (!requestedPath.startsWith(workspaceRoot)) {
            console.error('Security: Path traversal attempt blocked:', filePath);
            return null;
        }
        
        // Only allow .md files from memory/ or MEMORY.md
        const relativePath = path.relative(workspaceRoot, requestedPath);
        const isAllowed = relativePath === 'MEMORY.md' || 
                          relativePath.startsWith('memory/') ||
                          relativePath.startsWith('.hot_memory.md');
        
        if (!isAllowed) {
            console.error('Security: Path outside allowed memory directories:', filePath);
            return null;
        }
        
        if (!fs.existsSync(requestedPath)) {
            return null;
        }
        
        const content = fs.readFileSync(requestedPath, 'utf-8');
        const allLines = content.split('\n');
        const slice = allLines.slice(from - 1, from - 1 + lines);
        
        return {
            path: filePath,
            from,
            content: slice.join('\n')
        };
    } catch (error) {
        console.error('Memory get failed:', error.message);
        return null;
    }
}

/**
 * Sync memory files to vector index
 */
export function memorySync() {
    try {
        execSync(
            `node ${path.join(__dirname, 'smart_memory.js')} --sync`,
            { 
                cwd: WORKSPACE, 
                stdio: 'inherit'
            }
        );
        return true;
    } catch (error) {
        console.error('Memory sync failed:', error.message);
        return false;
    }
}

/**
 * Check memory status
 */
export function memoryStatus() {
    try {
        const result = execSync(
            `node ${path.join(__dirname, 'smart_memory.js')} --status`,
            { 
                cwd: WORKSPACE, 
                encoding: 'utf-8'
            }
        );
        return JSON.parse(result);
    } catch (error) {
        return { status: 'error', error: error.message };
    }
}

/**
 * Read hot memory directly
 */
export function memoryHot() {
    const content = readHotMemory();
    return {
        found: !!content,
        content: content,
    };
}

// CLI interface for direct usage
if (process.argv[1] === new URL(import.meta.url).pathname) {
    const args = process.argv.slice(2);
    const command = args[0];
    
    if (command === '--search') {
        const query = args[1];
        const maxResults = parseInt(args.find((a, i) => args[i-1] === '--max-results') || '5');
        
        if (!query) {
            console.error('Usage: --search "query" [--max-results 5]');
            process.exit(1);
        }
        
        const results = await memorySearch(query, maxResults);
        console.log(JSON.stringify(results, null, 2));
        
    } else if (command === '--get') {
        const filePath = args[1];
        const from = parseInt(args[2]);
        const lines = parseInt(args[3]);
        
        if (!filePath || !from || !lines) {
            console.error('Usage: --get <file-path> <from-line> <line-count>');
            process.exit(1);
        }
        
        const result = memoryGet(filePath, from, lines);
        console.log(JSON.stringify(result, null, 2));
        
    } else if (command === '--sync') {
        memorySync();
        
    } else if (command === '--status') {
        const status = memoryStatus();
        console.log(JSON.stringify(status, null, 2));
        
    } else if (command === '--hot') {
        const hot = memoryHot();
        console.log(JSON.stringify(hot, null, 2));
        
    } else {
        console.log(`
Smart Memory - OpenClaw Integration

Features:
  • Checks .hot_memory.md FIRST (instant)
  • Falls back to vector search (semantic + BM25)
  • 100% local, no API keys

Usage:
  node memory.js --search "query" [--max-results 5]
  node memory.js --get <file-path> <from-line> <line-count>
  node memory.js --sync
  node memory.js --status
  node memory.js --hot

Examples:
  node memory.js --search "James values"
  node memory.js --get MEMORY.md 1 20
  node memory.js --sync
  node memory.js --hot
`);
    }
}
