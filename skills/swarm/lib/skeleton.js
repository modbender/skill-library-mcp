/**
 * Skeleton-of-Thought (SoT) for Swarm
 * 
 * Three-phase execution for long-form content:
 * 1. SKELETON: Generate an outline (single, fast)
 * 2. EXPAND: Flesh out each section in parallel (fan-out, the speed win)
 * 3. MERGE: Combine into coherent final output (single, reduce)
 * 
 * Why it's fast: Phase 2 runs N sections simultaneously instead of
 * generating them sequentially. For a 10-section doc, that's ~10x speedup
 * on the content generation phase.
 * 
 * Why it's good: Each section gets full LLM attention instead of being
 * generated as part of a declining-quality long generation.
 */

const { securePrompt } = require('./security');

const SKELETON_PROMPT = securePrompt(
  `You are an expert outliner. Given a task, produce a clear, numbered outline of sections.
Each section should be a single line: "N. Section Title: Brief description of what this section covers"
Output ONLY the outline, nothing else. No introduction, no conclusion about the outline itself.
Aim for 4-8 sections depending on topic complexity.`
);

const EXPAND_PROMPT = securePrompt(
  `You are a subject matter expert writing one section of a larger document.
Write thorough, high-quality content for your assigned section.
Do NOT include the section number or title as a header — just write the content.
Be specific, use data/examples where relevant, and maintain a professional tone.
Do NOT reference other sections or say "as mentioned above/below".`
);

const MERGE_PROMPT = securePrompt(
  `You are an expert editor assembling a document from individually written sections.
Combine the sections into a coherent, well-flowing document.
Add smooth transitions between sections. Fix any redundancy or contradictions.
Add a brief introduction and conclusion if appropriate.
Preserve the substance of each section — don't summarize or shorten them.
Output the final document directly, no meta-commentary.`
);

/**
 * Parse an outline into sections
 * Handles formats like:
 *   1. Title: Description
 *   1. Title
 *   - Title: Description
 */
function parseOutline(outlineText) {
  const lines = outlineText.split('\n').map(l => l.trim()).filter(Boolean);
  const sections = [];
  
  for (const line of lines) {
    // Match "N. Title" or "N. Title: Description" or "- Title"
    const match = line.match(/^(?:\d+[\.\)]\s*|-\s*|\*\s*)(.+)/);
    if (match) {
      const full = match[1].trim();
      const [title, ...descParts] = full.split(':');
      sections.push({
        title: title.trim(),
        description: descParts.join(':').trim() || title.trim(),
        raw: line,
      });
    }
  }
  
  return sections;
}

/**
 * Build chain phases for Skeleton-of-Thought execution
 * 
 * @param {string} task - What to write
 * @param {string} data - Optional context/data to incorporate
 * @param {object} opts - { maxSections, expandPrompt, style }
 * @returns {Array} Phases for dispatcher.orchestrate()
 */
function buildSkeletonPhases(task, data = '', opts = {}) {
  const maxSections = opts.maxSections || 8;
  const style = opts.style || '';
  const styleNote = style ? `\nWriting style: ${style}` : '';
  
  return [
    // Phase 1: Generate skeleton/outline
    {
      name: 'Skeleton',
      required: true,
      tasks: () => [{
        nodeType: 'analyze',
        instruction: `Create an outline for: ${task}\n${data ? `\nContext/data to incorporate:\n${data.substring(0, 2000)}` : ''}${styleNote}\n\nGenerate ${maxSections} or fewer focused sections.`,
        input: '',
        _systemPrompt: SKELETON_PROMPT,
        label: 'skeleton',
      }],
    },
    
    // Phase 2: Expand each section in parallel (THE SPEED WIN)
    {
      name: 'Expand',
      required: true,
      tasks: (prevPhases) => {
        const outlineText = prevPhases[0]?.results?.[0]?.result?.response || '';
        const sections = parseOutline(outlineText);
        
        if (sections.length === 0) {
          // Fallback: if outline parsing fails, just do a single expansion
          return [{
            nodeType: 'analyze',
            instruction: `Write comprehensive content for: ${task}`,
            input: data || '',
            _systemPrompt: EXPAND_PROMPT,
            label: 'expand-fallback',
          }];
        }
        
        // One task per section — all run in parallel
        return sections.map((section, i) => ({
          nodeType: 'analyze',
          instruction: `Write section ${i + 1} of ${sections.length}: "${section.title}"${section.description !== section.title ? `\nSection scope: ${section.description}` : ''}${styleNote}\n\nOverall document topic: ${task}${data ? `\n\nAvailable data/context:\n${data.substring(0, 1500)}` : ''}`,
          input: '',
          _systemPrompt: EXPAND_PROMPT,
          label: `expand [${i + 1}/${sections.length}] ${section.title}`,
        }));
      },
    },
    
    // Phase 3: Merge into coherent document
    {
      name: 'Merge',
      required: true,
      tasks: (prevPhases) => {
        // Get the outline for structure reference
        const outline = prevPhases[0]?.results?.[0]?.result?.response || '';
        const sections = parseOutline(outline);
        
        // Get expanded sections
        const expanded = prevPhases[1]?.results
          ?.filter(r => r.success)
          ?.map((r, i) => {
            const title = sections[i]?.title || `Section ${i + 1}`;
            const content = r.result?.response || '';
            return `## ${title}\n\n${content}`;
          }) || [];
        
        const mergedSections = expanded.join('\n\n---\n\n');
        
        // Truncate if massive
        const maxChars = opts.maxMergeChars || 12000;
        const truncated = mergedSections.length > maxChars
          ? mergedSections.substring(0, maxChars) + '\n\n[... remaining sections truncated]'
          : mergedSections;
        
        return [{
          nodeType: 'analyze',
          instruction: `Assemble this ${sections.length}-section document about: ${task}\n\nOriginal outline:\n${outline}${styleNote}`,
          input: truncated,
          _systemPrompt: MERGE_PROMPT,
          label: 'merge',
        }];
      },
    },
  ];
}

module.exports = {
  buildSkeletonPhases,
  parseOutline,
  SKELETON_PROMPT,
  EXPAND_PROMPT,
  MERGE_PROMPT,
};
