/**
 * Session Memory - Auto-generate and load session summaries
 * 
 * Features:
 * - Auto-summarize sessions when they end
 * - Store summaries with metadata (topics, mood, decisions)
 * - Load hot context on session start
 * - Track active projects and pending items
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const MEMORY_DIR = process.env.MEMORY_DIR || '/config/.openclaw/workspace/memory';
const STATE_FILE = path.join(MEMORY_DIR, '.session_state.json');
const HOT_MEMORY_FILE = path.join(MEMORY_DIR, '.hot_memory.md');
const CURRENT_SESSION_FILE = path.join(MEMORY_DIR, '.current_session.json');

/**
 * Get current session state (from file or fresh)
 */
function getCurrentSession() {
    if (fs.existsSync(CURRENT_SESSION_FILE)) {
        try {
            return JSON.parse(fs.readFileSync(CURRENT_SESSION_FILE, 'utf-8'));
        } catch {
            // ignore
        }
    }
    return {
        startTime: null,
        topics: [],
        decisions: [],
        openQuestions: [],
        mood: null,
        projectContext: null,
    };
}

/**
 * Save current session state
 */
function saveCurrentSession(session) {
    fs.writeFileSync(CURRENT_SESSION_FILE, JSON.stringify(session, null, 2));
}

/**
 * Clear current session
 */
function clearCurrentSession() {
    if (fs.existsSync(CURRENT_SESSION_FILE)) {
        fs.unlinkSync(CURRENT_SESSION_FILE);
    }
}

/**
 * Initialize a new session
 */
export function initSession() {
    const session = {
        startTime: new Date().toISOString(),
        topics: [],
        decisions: [],
        openQuestions: [],
        mood: null,
        projectContext: null,
    };
    saveCurrentSession(session);
    
    // Load hot memory if exists
    return loadHotMemory();
}

/**
 * Load hot memory for session start
 */
function loadHotMemory() {
    const hotContext = [];
    
    // 1. Load .hot_memory.md if exists
    if (fs.existsSync(HOT_MEMORY_FILE)) {
        const hotContent = fs.readFileSync(HOT_MEMORY_FILE, 'utf-8');
        hotContext.push({
            type: 'hot_memory',
            content: hotContent,
            source: '.hot_memory.md',
        });
    }
    
    // 2. Load last session summary if exists
    const summaries = getRecentSummaries(1);
    if (summaries.length > 0) {
        hotContext.push({
            type: 'last_session',
            content: summaries[0].content,
            source: summaries[0].file,
        });
    }
    
    // 3. Load active projects
    const projects = getActiveProjects();
    if (projects.length > 0) {
        hotContext.push({
            type: 'active_projects',
            content: projects.map(p => `- ${p.name}: ${p.status}`).join('\n'),
            source: 'project_state',
        });
    }
    
    return hotContext;
}

/**
 * Track something during the session
 */
export function trackDuringSession(type, content) {
    const session = getCurrentSession();
    
    if (!session.startTime) {
        session.startTime = new Date().toISOString();
    }
    
    switch (type) {
        case 'topic':
            if (!session.topics.includes(content)) {
                session.topics.push(content);
            }
            break;
        case 'decision':
            session.decisions.push({
                text: content,
                timestamp: new Date().toISOString(),
            });
            break;
        case 'open_question':
            session.openQuestions.push({
                text: content,
                timestamp: new Date().toISOString(),
            });
            break;
        case 'mood':
            session.mood = content;
            break;
        case 'project':
            session.projectContext = content;
            break;
    }
    
    saveCurrentSession(session);
}

/**
 * Generate session summary
 */
export function generateSummary() {
    const session = getCurrentSession();
    const endTime = new Date().toISOString();
    const duration = session.startTime 
        ? Math.round((new Date(endTime) - new Date(session.startTime)) / 60000)
        : 0;
    
    const summary = {
        startTime: session.startTime,
        endTime,
        durationMinutes: duration,
        topics: session.topics,
        decisions: session.decisions,
        openQuestions: session.openQuestions,
        mood: session.mood,
        projectContext: session.projectContext,
    };
    
    return summary;
}

/**
 * Save session summary to disk
 */
export function saveSessionSummary(summary) {
    const date = new Date().toISOString().split('T')[0];
    const time = new Date().toTimeString().slice(0, 5).replace(':', '');
    const filename = `${date}-${time}-summary.json`;
    const filepath = path.join(MEMORY_DIR, filename);
    
    fs.writeFileSync(filepath, JSON.stringify(summary, null, 2));
    
    // Also append to hot memory
    updateHotMemory(summary);
    
    // Clear current session
    clearCurrentSession();
    
    return filepath;
}

/**
 * Update hot memory file with recent context
 */
function updateHotMemory(summary) {
    const sections = [];
    
    sections.push(`# Hot Memory - Last Updated: ${summary.endTime}\n`);
    
    if (summary.decisions.length > 0) {
        sections.push(`## Recent Decisions\n`);
        summary.decisions.forEach(d => {
            sections.push(`- ${d.text}`);
        });
        sections.push('');
    }
    
    if (summary.openQuestions.length > 0) {
        sections.push(`## Open Questions\n`);
        summary.openQuestions.forEach(q => {
            sections.push(`- ${q.text}`);
        });
        sections.push('');
    }
    
    if (summary.topics.length > 0) {
        sections.push(`## Recent Topics\n`);
        summary.topics.forEach(t => {
            sections.push(`- ${t}`);
        });
        sections.push('');
    }
    
    if (summary.projectContext) {
        sections.push(`## Active Project\n`);
        sections.push(summary.projectContext);
        sections.push('');
    }
    
    fs.writeFileSync(HOT_MEMORY_FILE, sections.join('\n'));
}

/**
 * Get recent session summaries
 */
function getRecentSummaries(count = 5) {
    if (!fs.existsSync(MEMORY_DIR)) return [];
    
    return fs.readdirSync(MEMORY_DIR)
        .filter(f => f.endsWith('-summary.json'))
        .sort()
        .reverse()
        .slice(0, count)
        .map(f => ({
            file: f,
            content: fs.readFileSync(path.join(MEMORY_DIR, f), 'utf-8'),
        }));
}

/**
 * Get active projects from state
 */
function getActiveProjects() {
    if (!fs.existsSync(STATE_FILE)) return [];
    
    try {
        const state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
        return state.projects || [];
    } catch {
        return [];
    }
}

/**
 * Set project state
 */
export function setProjectState(projectName, status, details = {}) {
    let state = { projects: [] };
    
    if (fs.existsSync(STATE_FILE)) {
        try {
            state = JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
        } catch {
            // ignore
        }
    }
    
    const existingIndex = state.projects.findIndex(p => p.name === projectName);
    const project = {
        name: projectName,
        status,
        lastUpdated: new Date().toISOString(),
        ...details,
    };
    
    if (existingIndex >= 0) {
        state.projects[existingIndex] = project;
    } else {
        state.projects.push(project);
    }
    
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

/**
 * Format hot memory for loading into context
 */
export function formatHotMemoryForContext() {
    const hot = loadHotMemory();
    
    const parts = ['## Hot Memory Context\n'];
    
    hot.forEach(item => {
        switch (item.type) {
            case 'hot_memory':
                parts.push(`### Current State\n${item.content}\n`);
                break;
            case 'last_session':
                const summary = JSON.parse(item.content);
                parts.push(`### Last Session (${summary.startTime})\n`);
                if (summary.decisions.length) {
                    parts.push('**Decisions:** ' + summary.decisions.map(d => d.text).join('; '));
                }
                if (summary.openQuestions.length) {
                    parts.push('**Open:** ' + summary.openQuestions.map(q => q.text).join('; '));
                }
                parts.push('');
                break;
            case 'active_projects':
                parts.push(`### Active Projects\n${item.content}\n`);
                break;
        }
    });
    
    return parts.join('\n');
}

// CLI interface
if (import.meta.url === `file://${process.argv[1]}`) {
    const args = process.argv.slice(2);
    const command = args[0];
    
    switch (command) {
        case '--init':
            initSession();
            console.log('Session initialized');
            break;
            
        case '--track':
            const type = args[1];
            const content = args.slice(2).join(' ');
            trackDuringSession(type, content);
            console.log(`Tracked: ${type} = ${content}`);
            break;
            
        case '--summary':
            const summary = generateSummary();
            const filepath = saveSessionSummary(summary);
            console.log(`Summary saved: ${filepath}`);
            console.log(JSON.stringify(summary, null, 2));
            break;
            
        case '--hot':
            console.log(formatHotMemoryForContext());
            break;
            
        case '--project':
            const projectName = args[1];
            const status = args[2];
            setProjectState(projectName, status);
            console.log(`Project ${projectName}: ${status}`);
            break;
            
        default:
            console.log(`
Session Memory - Context Management

Usage:
  node session_memory.js --init
    Initialize a new session (load hot memory)

  node session_memory.js --track <type> <content>
    Track something during session (topic|decision|open_question|mood|project)

  node session_memory.js --summary
    Generate and save session summary

  node session_memory.js --hot
    Show formatted hot memory for context loading

  node session_memory.js --project <name> <status>
    Set project status
`);
    }
}
