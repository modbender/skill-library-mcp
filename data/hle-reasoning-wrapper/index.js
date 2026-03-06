const fs = require('fs');
const path = require('path');

const CACHE_FILE = path.resolve(__dirname, 'cache.json');

function loadCache() {
    try {
        if (fs.existsSync(CACHE_FILE)) {
            return JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
        }
    } catch (e) {
        console.warn('Failed to load cache:', e.message);
    }
    return {};
}

function saveCache(cache) {
    try {
        fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
    } catch (e) {
        console.warn('Failed to save cache:', e.message);
    }
}

function formatPrompt(question, context = "") {
    return `
You are a reasoning engine solving a hard logic problem.
Question: ${question}
Context: ${context}

You MUST follow this format:
--- REASONING ---
(Your step-by-step logic here)
--- FINAL ANSWER ---
(Your concise final answer here)
`;
}

function validateOutput(text) {
    if (!text || typeof text !== 'string') return false;
    const hasReasoning = text.includes("--- REASONING ---");
    const hasAnswer = text.includes("--- FINAL ANSWER ---");
    return hasReasoning && hasAnswer;
}

function getCachedAnswer(question) {
    const cache = loadCache();
    // Simple key normalization
    const key = Buffer.from(question).toString('base64').slice(0, 64);
    return cache[key] || null;
}

function cacheAnswer(question, answer) {
    const cache = loadCache();
    const key = Buffer.from(question).toString('base64').slice(0, 64);
    cache[key] = answer;
    saveCache(cache);
}

function main() {
    console.log("HLE Reasoning Wrapper Loaded (with Cache).");
    return true;
}

module.exports = {
    formatPrompt,
    validateOutput,
    getCachedAnswer,
    cacheAnswer,
    main
};
