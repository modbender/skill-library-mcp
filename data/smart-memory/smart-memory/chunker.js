/**
 * Token-based text chunking with overlap
 * Uses approximate word count as token proxy (~0.75 tokens/word)
 */

const TARGET_TOKENS = 300;
const OVERLAP_TOKENS = 80;
const WORDS_PER_TOKEN = 0.75;

const TARGET_WORDS = Math.round(TARGET_TOKENS * WORDS_PER_TOKEN); // ~225 words
const OVERLAP_WORDS = Math.round(OVERLAP_TOKENS * WORDS_PER_TOKEN); // ~60 words

/**
 * Split text into semantic chunks based on headers and token limits
 * @param {string} text - Full text content
 * @param {number} startLine - Starting line number (1-indexed)
 * @returns {Array<{content: string, startLine: number, endLine: number}>}
 */
export function createChunks(text, startLine = 1) {
    const lines = text.split('\n');
    const chunks = [];
    
    // First, split by headers to preserve semantic boundaries
    const sections = splitByHeaders(lines);
    
    for (const section of sections) {
        const sectionChunks = chunkSection(section.lines, section.startLine);
        chunks.push(...sectionChunks);
    }
    
    return chunks;
}

/**
 * Split lines into sections based on markdown headers
 */
function splitByHeaders(lines) {
    const sections = [];
    let currentSection = { lines: [], startLine: 1 };
    
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Check if this is a header line
        if (/^#{1,6}\s/.test(line)) {
            // Save previous section if it has content
            if (currentSection.lines.length > 0) {
                sections.push(currentSection);
            }
            // Start new section
            currentSection = { lines: [line], startLine: i + 1 };
        } else {
            currentSection.lines.push(line);
        }
    }
    
    // Don't forget the last section
    if (currentSection.lines.length > 0) {
        sections.push(currentSection);
    }
    
    return sections;
}

/**
 * Chunk a section into token-sized pieces with overlap
 */
function chunkSection(lines, sectionStartLine) {
    const chunks = [];
    const words = [];
    const wordLineMap = []; // Track which line each word came from
    
    // Convert lines to words with line tracking
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const lineWords = line.split(/\s+/).filter(w => w.length > 0);
        
        for (const word of lineWords) {
            words.push(word);
            wordLineMap.push(sectionStartLine + i);
        }
    }
    
    if (words.length === 0) {
        return [];
    }
    
    // Create overlapping chunks
    let pos = 0;
    while (pos < words.length) {
        const endPos = Math.min(pos + TARGET_WORDS, words.length);
        
        // Get words for this chunk
        const chunkWords = words.slice(pos, endPos);
        const chunkStartLine = wordLineMap[pos];
        const chunkEndLine = wordLineMap[endPos - 1] || chunkStartLine;
        
        // Reconstruct text preserving original line breaks where possible
        const chunkContent = reconstructText(lines, chunkStartLine - sectionStartLine, chunkEndLine - sectionStartLine);
        
        chunks.push({
            content: chunkContent,
            startLine: chunkStartLine,
            endLine: chunkEndLine,
        });
        
        // Move forward with overlap
        const advance = Math.max(1, TARGET_WORDS - OVERLAP_WORDS);
        pos += advance;
        
        // Avoid infinite loop on tiny chunks
        if (endPos >= words.length) break;
    }
    
    return chunks;
}

/**
 * Reconstruct text from original lines between start and end indices
 */
function reconstructText(lines, startIdx, endIdx) {
    const selectedLines = lines.slice(startIdx, endIdx + 1);
    return selectedLines.join('\n').trim();
}

/**
 * Estimate token count from text
 * @param {string} text
 * @returns {number}
 */
export function estimateTokens(text) {
    return Math.ceil(text.split(/\s+/).filter(w => w.length > 0).length / WORDS_PER_TOKEN);
}
