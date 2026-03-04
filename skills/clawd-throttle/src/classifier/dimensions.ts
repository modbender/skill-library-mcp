interface Breakpoint {
  value: number;
  score: number;
}

function interpolateBreakpoints(value: number, breakpoints: Breakpoint[]): number {
  if (value <= breakpoints[0]!.value) return breakpoints[0]!.score;
  if (value >= breakpoints[breakpoints.length - 1]!.value) return breakpoints[breakpoints.length - 1]!.score;

  for (let i = 0; i < breakpoints.length - 1; i++) {
    const low = breakpoints[i]!;
    const high = breakpoints[i + 1]!;
    if (value >= low.value && value <= high.value) {
      const ratio = (value - low.value) / (high.value - low.value);
      return low.score + ratio * (high.score - low.score);
    }
  }

  return breakpoints[breakpoints.length - 1]!.score;
}

export function scoreTokenCount(text: string): number {
  const estimatedTokens = Math.ceil(text.length / 4);

  return interpolateBreakpoints(estimatedTokens, [
    { value: 50, score: 0.00 },
    { value: 200, score: 0.15 },
    { value: 500, score: 0.30 },
    { value: 1000, score: 0.50 },
    { value: 3000, score: 0.70 },
    { value: 8000, score: 0.85 },
    { value: 16000, score: 1.00 },
  ]);
}

export function scoreCodePresence(text: string): number {
  let score = 0;

  const fencedBlocks = (text.match(/```[\s\S]*?```/g) || []).length;
  score += Math.min(0.60, fencedBlocks * 0.30);

  const inlineCode = (text.match(/`[^`]+`/g) || []).length;
  score += Math.min(0.20, inlineCode * 0.05);

  const keywords = (text.match(
    /\b(function|const|let|var|class|import|export|return|async|await|def|fn|pub|struct|impl|enum|interface|type|module|require|yield|throw|catch|try|finally|for|while|if|else|switch|case)\b/g
  ) || []).length;
  score += Math.min(0.30, keywords * 0.03);

  const syntaxChars = (text.match(/[{}\[\]();=><|&]/g) || []).length;
  score += Math.min(0.20, syntaxChars * 0.005);

  const fileExts = (text.match(/\.\b(ts|tsx|js|jsx|py|rs|go|java|cpp|c|rb|sh|sql|css|html|json|yaml|yml|toml|xml)\b/g) || []).length;
  score += Math.min(0.30, fileExts * 0.10);

  return Math.min(1.0, score);
}

export function scoreReasoningMarkers(text: string): number {
  let score = 0;

  const analyticalHits = (text.match(
    /\b(explain|analyze|compare|evaluate|assess|critique|reason|trade-?offs?|pros?\s+and\s+cons?|implications?|consequences?|consider|weigh|differentiate|contrast|justify)\b/gi
  ) || []).length;
  score += Math.min(0.50, analyticalHits * 0.08);

  const cotHits = (text.match(
    /\b(step[- ]by[- ]step|think through|break down|work through|let'?s think|chain of thought|think carefully|think about this|reasoning)\b/gi
  ) || []).length;
  score += Math.min(0.60, cotHits * 0.20);

  const debugHits = (text.match(
    /\b(debug|diagnose|troubleshoot|root cause|investigate|figure out why|what went wrong|what's? causing)\b/gi
  ) || []).length;
  score += Math.min(0.40, debugHits * 0.12);

  const whyHowHits = (text.match(
    /\b(why\s+(does|did|is|are|do|would|should|doesn't|isn't|can't))\b|\b(how\s+does|how\s+do|how\s+would|how\s+can)\b/gi
  ) || []).length;
  score += Math.min(0.30, whyHowHits * 0.12);

  return Math.min(1.0, score);
}

export function scoreSimpleIndicators(text: string): number {
  const trimmed = text.trim();

  if (/^(hi|hello|hey|thanks|thank you|ok|okay|yes|no|sure|got it|sounds good|great|cool|nice|yep|nope|nah)[.!?\s]*$/i.test(trimmed)) {
    return 1.0;
  }

  let score = 0;

  if (trimmed.length < 40) score += 0.35;
  else if (trimmed.length < 80) score += 0.25;
  else if (trimmed.length < 150) score += 0.10;

  const simpleTaskHits = (trimmed.match(
    /\b(translate|convert|format|summarize|tldr|tl;dr|what is|define|list|name|spell|count|repeat|echo|quote)\b/gi
  ) || []).length;
  score += Math.min(0.60, simpleTaskHits * 0.15);

  const simpleAdjHits = (trimmed.match(
    /\b(quick|brief|short|simple|one-?liner|fast|easy|basic|straightforward)\b/gi
  ) || []).length;
  score += Math.min(0.40, simpleAdjHits * 0.10);

  if (!trimmed.includes('?')) {
    score += 0.05;
  }

  const sentenceCount = trimmed.split(/[.!?]+/).filter(s => s.trim().length > 0).length;
  if (sentenceCount <= 1) score += 0.10;

  return Math.min(1.0, score);
}

export function scoreMultiStepPatterns(text: string): number {
  let score = 0;

  const seqHits = (text.match(
    /\b(first|then|next|after that|finally|lastly|step\s*\d+|phase\s*\d+|part\s*\d+)\b/gi
  ) || []).length;
  score += Math.min(0.50, seqHits * 0.10);

  const addHits = (text.match(
    /\b(and then|also|additionally|furthermore|moreover|as well as|on top of that|in addition|plus)\b/gi
  ) || []).length;
  score += Math.min(0.30, addHits * 0.06);

  const numberedItems = (text.match(/^\s*\d+[.)]\s/gm) || []).length;
  score += Math.min(0.40, numberedItems * 0.08);

  const bulletItems = (text.match(/^\s*[-*+]\s/gm) || []).length;
  score += Math.min(0.30, bulletItems * 0.06);

  const buildHits = (text.match(
    /\b(implement|build|create|design|architect|refactor|migrate|restructure|rewrite|overhaul|set up|configure|deploy|integrate)\b/gi
  ) || []).length;
  score += Math.min(0.40, buildHits * 0.10);

  return Math.min(1.0, score);
}

export function scoreQuestionCount(text: string): number {
  const explicitQuestions = (text.match(/\?/g) || []).length;

  let score = interpolateBreakpoints(explicitQuestions, [
    { value: 0, score: 0.00 },
    { value: 1, score: 0.15 },
    { value: 2, score: 0.30 },
    { value: 3, score: 0.50 },
    { value: 4, score: 0.70 },
    { value: 5, score: 0.85 },
    { value: 7, score: 1.00 },
  ]);

  const implicitHits = (text.match(
    /(?:^|\.\s+)(how|why|what|when|where|which|who|whom|whose|can|could|would|should|is|are|do|does|did|will|shall)\s/gim
  ) || []).length;
  score += Math.min(0.30, implicitHits * 0.08);

  return Math.min(1.0, score);
}

export function scoreSystemPromptSignals(systemPrompt?: string): number {
  if (!systemPrompt || systemPrompt.trim().length === 0) {
    return 0.0;
  }

  let score = 0;
  const len = systemPrompt.length;

  if (len <= 100) score += 0.10;
  else if (len <= 500) score += 0.25;
  else if (len <= 2000) score += 0.45;
  else if (len <= 5000) score += 0.65;
  else score += 0.80;

  const structuredHits = (systemPrompt.match(
    /\b(json|schema|structured|format:|output format|xml|markdown table|csv|typescript interface|response format)\b/gi
  ) || []).length;
  score += Math.min(0.20, structuredHits * 0.08);

  const roleHits = (systemPrompt.match(
    /\b(you are|act as|your role|persona|character|behave as|you're a|you will act)\b/gi
  ) || []).length;
  score += Math.min(0.15, roleHits * 0.08);

  const constraintHits = (systemPrompt.match(
    /\b(you must|you must not|never|always|do not|don't|required|forbidden|mandatory|constraint|rule:|important:)\b/gi
  ) || []).length;
  score += Math.min(0.15, constraintHits * 0.04);

  return Math.min(1.0, score);
}

export function scoreConversationDepth(messageCount?: number): number {
  if (messageCount === undefined || messageCount <= 1) return 0.0;

  return interpolateBreakpoints(messageCount, [
    { value: 1, score: 0.00 },
    { value: 3, score: 0.10 },
    { value: 6, score: 0.25 },
    { value: 10, score: 0.45 },
    { value: 20, score: 0.65 },
    { value: 50, score: 0.85 },
    { value: 100, score: 1.00 },
  ]);
}
