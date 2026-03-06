/**
 * Memory Bridge - OpenClaw Integration
 * 
 * Call this at session start to load hot memory
 * Track things during session
 * Generate summary at end
 */

import { initSession, trackDuringSession, generateSummary, saveSessionSummary, setProjectState, formatHotMemoryForContext } from './session_memory.js';

/**
 * Initialize session and return hot memory for context
 */
export function loadSessionContext() {
    const hotMemory = initSession();
    
    // Format as string for OpenClaw context
    const parts = ['# Session Context\n'];
    
    hotMemory.forEach(item => {
        switch (item.type) {
            case 'hot_memory':
                parts.push(item.content);
                break;
            case 'last_session':
                const summary = JSON.parse(item.content);
                parts.push(`## Previous Session (${summary.startTime})`);
                parts.push(`Topics: ${summary.topics.join(', ')}`);
                if (summary.decisions.length) {
                    parts.push(`Key decisions: ${summary.decisions.map(d => d.text).join('; ')}`);
                }
                if (summary.openQuestions.length) {
                    parts.push(`Still open: ${summary.openQuestions.map(q => q.text).join('; ')}`);
                }
                break;
            case 'active_projects':
                parts.push('## Active Projects');
                parts.push(item.content);
                break;
        }
    });
    
    return parts.join('\n\n');
}

/**
 * Track a decision during the session
 */
export function recordDecision(text) {
    trackDuringSession('decision', text);
}

/**
 * Track an open question
 */
export function recordQuestion(text) {
    trackDuringSession('open_question', text);
}

/**
 * Track current topic
 */
export function recordTopic(text) {
    trackDuringSession('topic', text);
}

/**
 * Track mood/context
 */
export function recordMood(text) {
    trackDuringSession('mood', text);
}

/**
 * Track active project
 */
export function recordProject(name, status) {
    trackDuringSession('project', name);
    setProjectState(name, status);
}

/**
 * End session and save summary
 */
export function endSession() {
    const summary = generateSummary();
    const filepath = saveSessionSummary(summary);
    return {
        summary,
        filepath,
        formatted: `Session ended. Duration: ${summary.durationMinutes} minutes. ` +
                   `Topics: ${summary.topics.join(', ')}. ` +
                   `Decisions made: ${summary.decisions.length}`,
    };
}

// Export for use in other modules
export { initSession, trackDuringSession, generateSummary, saveSessionSummary, setProjectState };
