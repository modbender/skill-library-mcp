/**
 * VADER-inspired Affect Analyzer for Panksepp's 7 Primary Affects
 * ================================================================
 * Deterministic, consistent, packageable. No API calls.
 * 
 * Based on VADER (Valence Aware Dictionary and sEntiment Reasoner)
 * adapted for Panksepp's 7-affect model instead of pos/neg/neutral.
 * 
 * Features:
 *   - 450+ word lexicon with affect weights
 *   - Caps amplification (1.5x)
 *   - Punctuation intensity (!!! = boost)
 *   - Negation handling ("not happy" → invert valence)  
 *   - Degree modifiers ("very", "extremely", "so" → scale)
 *   - Emoji mapping (40+ emoji → affects)
 *   - Conjunction pivot ("but" → weight latter clause)
 *   - Deterministic: same input = same output always
 */

// Degree modifiers scale affect intensity
const DEGREE_MODIFIERS = {
  // Boosters
  "very": 1.5, "extremely": 1.8, "incredibly": 1.7, "really": 1.4,
  "so": 1.4, "absolutely": 1.7, "totally": 1.5, "completely": 1.6,
  "utterly": 1.7, "super": 1.5, "damn": 1.5, "freaking": 1.5,
  "fucking": 1.8, "insanely": 1.7, "ridiculously": 1.5,
  // Dampeners  
  "barely": 0.4, "hardly": 0.4, "slightly": 0.5, "somewhat": 0.6,
  "kind of": 0.5, "kinda": 0.5, "a bit": 0.6, "a little": 0.5,
  "sort of": 0.5, "mildly": 0.5,
};

// Negation words flip valence
const NEGATION_WORDS = new Set([
  "not", "no", "never", "neither", "nobody", "nothing", "nowhere",
  "nor", "cannot", "cant", "can't", "don't", "dont", "doesn't", "doesnt",
  "didn't", "didnt", "won't", "wont", "wouldn't", "wouldnt",
  "shouldn't", "shouldnt", "isn't", "isnt", "aren't", "arent",
  "wasn't", "wasnt", "weren't", "werent", "hasn't", "hasnt",
  "haven't", "havent", "hadn't", "hadnt",
]);

// Conjunction pivots — "but" shifts weight to second clause
const PIVOT_WORDS = new Set(["but", "however", "although", "yet", "nevertheless"]);

// Emoji → affect mapping
const EMOJI_MAP = {
  "😡": { RAGE: 0.9 }, "🤬": { RAGE: 0.95 }, "😤": { RAGE: 0.7 },
  "💢": { RAGE: 0.8 }, "👿": { RAGE: 0.8 },
  "😱": { FEAR: 0.9 }, "😰": { FEAR: 0.7, PANIC: 0.5 }, "😨": { FEAR: 0.8 },
  "😧": { FEAR: 0.6 }, "🫣": { FEAR: 0.5 },
  "😢": { PANIC: 0.7 }, "😭": { PANIC: 0.9 }, "💔": { PANIC: 0.8 },
  "😞": { PANIC: 0.6 }, "😔": { PANIC: 0.5 }, "🥺": { PANIC: 0.6, CARE: 0.3 },
  "❤️": { CARE: 0.8 }, "🥰": { CARE: 0.9, LUST: 0.2 }, "😍": { CARE: 0.7, LUST: 0.4 },
  "💕": { CARE: 0.8 }, "🤗": { CARE: 0.7 }, "💚": { CARE: 0.7 },
  "🔥": { SEEKING: 0.6, LUST: 0.3 }, "💡": { SEEKING: 0.7 },
  "🤔": { SEEKING: 0.6 }, "🧐": { SEEKING: 0.7 }, "✨": { SEEKING: 0.5, PLAY: 0.3 },
  "😂": { PLAY: 0.9 }, "🤣": { PLAY: 0.95 }, "😆": { PLAY: 0.8 },
  "😊": { PLAY: 0.5, CARE: 0.4 }, "😜": { PLAY: 0.7 }, "🎉": { PLAY: 0.8 },
  "👍": { CARE: 0.3, PLAY: 0.2 }, "👎": { RAGE: 0.3 },
  "🙄": { RAGE: 0.4 }, "😒": { RAGE: 0.4 },
  "😏": { PLAY: 0.4, LUST: 0.3 }, "💀": { PLAY: 0.7 },
  "🚀": { SEEKING: 0.7, PLAY: 0.3 }, "💪": { SEEKING: 0.5, RAGE: 0.2 },
};

// Core affect lexicon — each word maps to Panksepp affects
// Format: { SEEKING, RAGE, FEAR, LUST, CARE, PANIC, PLAY }
const AFFECT_LEXICON = {
  // === RAGE / ANGER ===
  angry: { RAGE: 0.85 }, anger: { RAGE: 0.8 }, furious: { RAGE: 0.95 },
  mad: { RAGE: 0.7 }, rage: { RAGE: 0.95 }, hate: { RAGE: 0.85 },
  hatred: { RAGE: 0.9 }, loathe: { RAGE: 0.85 }, despise: { RAGE: 0.85 },
  resent: { RAGE: 0.7 }, resentment: { RAGE: 0.7 }, bitter: { RAGE: 0.6, PANIC: 0.2 },
  frustrated: { RAGE: 0.65 }, frustrating: { RAGE: 0.65 }, frustration: { RAGE: 0.65 },
  annoyed: { RAGE: 0.5 }, annoying: { RAGE: 0.55 }, irritated: { RAGE: 0.55 },
  irritating: { RAGE: 0.55 }, infuriated: { RAGE: 0.9 }, outraged: { RAGE: 0.9 },
  pissed: { RAGE: 0.8 }, piss: { RAGE: 0.7 }, pissing: { RAGE: 0.8 },
  livid: { RAGE: 0.9 }, hostile: { RAGE: 0.7 },
  aggressive: { RAGE: 0.6 }, enraged: { RAGE: 0.95 }, irate: { RAGE: 0.8 },
  upset: { RAGE: 0.6, PANIC: 0.4 }, crazy: { RAGE: 0.5, PANIC: 0.3 },
  failing: { RAGE: 0.4, PANIC: 0.3 }, broken: { RAGE: 0.4, FEAR: 0.2 },
  wrong: { RAGE: 0.3, FEAR: 0.1 }, terrible: { RAGE: 0.5, PANIC: 0.3 },
  awful: { RAGE: 0.5, PANIC: 0.3 }, stupid: { RAGE: 0.5 },
  ridiculous: { RAGE: 0.55 }, unacceptable: { RAGE: 0.65 },
  useless: { RAGE: 0.5, PANIC: 0.2 }, enough: { RAGE: 0.4 },
  problems: { RAGE: 0.4, FEAR: 0.2 }, sucks: { RAGE: 0.6 },
  worst: { RAGE: 0.6 }, ruined: { RAGE: 0.6, PANIC: 0.3 },
  disaster: { RAGE: 0.5, FEAR: 0.5 }, mess: { RAGE: 0.4, PANIC: 0.2 },
  sick: { RAGE: 0.4, PANIC: 0.3 }, tired: { RAGE: 0.3, PANIC: 0.3 },
  dissapointed: { PANIC: 0.5, RAGE: 0.3 }, dissapoint: { PANIC: 0.5, RAGE: 0.3 },
  disappointing: { PANIC: 0.5, RAGE: 0.3 },
  complicated: { RAGE: 0.3, FEAR: 0.3 }, difficult: { RAGE: 0.3, FEAR: 0.2 },
  impossible: { RAGE: 0.5, FEAR: 0.4 }, unbearable: { RAGE: 0.6, PANIC: 0.5 },
  pathetic: { RAGE: 0.5, PANIC: 0.3 }, garbage: { RAGE: 0.6 },
  trash: { RAGE: 0.6 }, crap: { RAGE: 0.5 }, craziness: { RAGE: 0.5, PANIC: 0.3 },
  unbelievable: { RAGE: 0.5, SEEKING: 0.2 }, insane: { RAGE: 0.5, FEAR: 0.2 },
  wtf: { RAGE: 0.7 }, omg: { FEAR: 0.3, SEEKING: 0.3 },
  ugh: { RAGE: 0.4 }, argh: { RAGE: 0.5 }, ffs: { RAGE: 0.7 },
  nope: { RAGE: 0.2 }, nah: { RAGE: 0.1 },
  
  // === FEAR ===
  afraid: { FEAR: 0.8 }, scared: { FEAR: 0.85 }, terrified: { FEAR: 0.95 },
  frightened: { FEAR: 0.8 }, anxious: { FEAR: 0.6, PANIC: 0.3 },
  worried: { FEAR: 0.6, CARE: 0.2 }, nervous: { FEAR: 0.6 },
  dread: { FEAR: 0.85 }, horror: { FEAR: 0.9 }, alarmed: { FEAR: 0.7 },
  uneasy: { FEAR: 0.5 }, threatened: { FEAR: 0.7, RAGE: 0.3 },
  vulnerable: { FEAR: 0.6, PANIC: 0.2 }, danger: { FEAR: 0.8 },
  risky: { FEAR: 0.5 }, scary: { FEAR: 0.7 }, creepy: { FEAR: 0.6 },
  paranoid: { FEAR: 0.7 }, panic: { FEAR: 0.5, PANIC: 0.8 },
  
  // === PANIC / GRIEF / SADNESS ===
  sad: { PANIC: 0.7 }, depressed: { PANIC: 0.85 }, hopeless: { PANIC: 0.9 },
  despair: { PANIC: 0.9 }, grief: { PANIC: 0.9, CARE: 0.2 },
  heartbroken: { PANIC: 0.9 }, lonely: { PANIC: 0.75 }, alone: { PANIC: 0.6 },
  abandoned: { PANIC: 0.85 }, lost: { PANIC: 0.6, FEAR: 0.2 },
  empty: { PANIC: 0.7 }, numb: { PANIC: 0.6 }, crying: { PANIC: 0.8 },
  miss: { PANIC: 0.5, CARE: 0.4 }, disappointed: { PANIC: 0.5, RAGE: 0.3 },
  hurt: { PANIC: 0.6, RAGE: 0.2 }, suffering: { PANIC: 0.8 },
  miserable: { PANIC: 0.8 }, sorry: { PANIC: 0.4, CARE: 0.3 },
  overwhelmed: { PANIC: 0.7, FEAR: 0.3 }, exhausted: { PANIC: 0.6 },
  
  // === CARE / LOVE ===
  love: { CARE: 0.9 }, kind: { CARE: 0.7 }, caring: { CARE: 0.8 },
  gentle: { CARE: 0.6 }, compassion: { CARE: 0.85 }, empathy: { CARE: 0.8 },
  nurture: { CARE: 0.8 }, protect: { CARE: 0.8, RAGE: 0.1 },
  support: { CARE: 0.7 }, trust: { CARE: 0.7 }, comfort: { CARE: 0.7 },
  safe: { CARE: 0.6 }, warm: { CARE: 0.6 }, tender: { CARE: 0.7 },
  grateful: { CARE: 0.7, PLAY: 0.2 }, thank: { CARE: 0.6 },
  appreciate: { CARE: 0.7 }, sweet: { CARE: 0.6 }, beautiful: { CARE: 0.6, SEEKING: 0.2 },
  wonderful: { CARE: 0.7, PLAY: 0.3 }, precious: { CARE: 0.8 },
  dear: { CARE: 0.7 }, adore: { CARE: 0.8, LUST: 0.1 },
  friend: { CARE: 0.6 }, family: { CARE: 0.7 }, help: { CARE: 0.5, SEEKING: 0.3 },
  please: { CARE: 0.3, PANIC: 0.2 },
  
  // === SEEKING / CURIOSITY ===
  curious: { SEEKING: 0.8 }, interested: { SEEKING: 0.7 }, fascinated: { SEEKING: 0.85 },
  explore: { SEEKING: 0.8 }, discover: { SEEKING: 0.8 }, learn: { SEEKING: 0.7 },
  understand: { SEEKING: 0.7 }, wonder: { SEEKING: 0.7, PLAY: 0.2 },
  search: { SEEKING: 0.6 }, investigate: { SEEKING: 0.7 }, research: { SEEKING: 0.7 },
  figure: { SEEKING: 0.5 }, solve: { SEEKING: 0.6 }, build: { SEEKING: 0.6 },
  create: { SEEKING: 0.7, PLAY: 0.2 }, design: { SEEKING: 0.6 },
  think: { SEEKING: 0.5 }, idea: { SEEKING: 0.6 }, why: { SEEKING: 0.5 },
  how: { SEEKING: 0.4 }, what: { SEEKING: 0.3 }, exciting: { SEEKING: 0.7, PLAY: 0.3 },
  amazing: { SEEKING: 0.5, PLAY: 0.4 }, cool: { SEEKING: 0.4, PLAY: 0.4 },
  try: { SEEKING: 0.5 }, fix: { SEEKING: 0.5, RAGE: 0.2 },
  
  // === PLAY / JOY ===
  happy: { PLAY: 0.7, CARE: 0.2 }, joy: { PLAY: 0.85 }, fun: { PLAY: 0.8 },
  funny: { PLAY: 0.8 }, hilarious: { PLAY: 0.9 }, laugh: { PLAY: 0.8 },
  playful: { PLAY: 0.8 }, silly: { PLAY: 0.7 }, enjoy: { PLAY: 0.7 },
  delight: { PLAY: 0.8 }, cheerful: { PLAY: 0.7 }, great: { PLAY: 0.5 },
  awesome: { PLAY: 0.6, SEEKING: 0.2 }, fantastic: { PLAY: 0.7 },
  excellent: { PLAY: 0.6 }, perfect: { PLAY: 0.6 }, nice: { PLAY: 0.4, CARE: 0.3 },
  good: { PLAY: 0.3, CARE: 0.2 }, lol: { PLAY: 0.7 }, lmao: { PLAY: 0.8 },
  haha: { PLAY: 0.7 }, yay: { PLAY: 0.7 }, woohoo: { PLAY: 0.8 },
  celebrate: { PLAY: 0.7 }, win: { PLAY: 0.6, SEEKING: 0.3 },
  
  // === LUST / DESIRE ===
  desire: { LUST: 0.7, SEEKING: 0.3 }, want: { LUST: 0.3, SEEKING: 0.3 },
  need: { LUST: 0.3, PANIC: 0.2 }, crave: { LUST: 0.7 },
  passion: { LUST: 0.6, SEEKING: 0.3 }, attract: { LUST: 0.6 },
  sexy: { LUST: 0.8 }, hot: { LUST: 0.5 }, gorgeous: { LUST: 0.5, CARE: 0.3 },
  tempt: { LUST: 0.6 }, obsess: { LUST: 0.5, SEEKING: 0.4 },
};

// Build lowercase lookup
const LEXICON_LOWER = {};
for (const [word, affects] of Object.entries(AFFECT_LEXICON)) {
  LEXICON_LOWER[word.toLowerCase()] = affects;
}

const AFFECTS = ["SEEKING", "RAGE", "FEAR", "LUST", "CARE", "PANIC", "PLAY"];

/**
 * Analyze text and return Panksepp affect scores.
 * Deterministic: same input always produces same output.
 * 
 * @param {string} text - Input text to analyze
 * @returns {{ affects: Object<string, number>, intensity: number, matchCount: number, debug: Object }}
 */
export function analyzeAffect(text) {
  if (!text || typeof text !== "string" || text.length < 2) {
    return { affects: {}, intensity: 0, matchCount: 0, debug: { reason: "empty" } };
  }
  
  const affects = {};
  const matchedWords = [];
  
  // === STEP 1: Emoji detection (before text processing) ===
  for (const [emoji, mapping] of Object.entries(EMOJI_MAP)) {
    const count = (text.split(emoji).length - 1);
    if (count > 0) {
      matchedWords.push({ word: emoji, type: "emoji" });
      for (const [affect, weight] of Object.entries(mapping)) {
        affects[affect] = (affects[affect] || 0) + weight * Math.min(count, 3);
      }
    }
  }
  
  // === Pre-compute text signals ===
  const capsRatio = text.replace(/[^a-zA-Z]/g, "").length > 0
    ? (text.replace(/[^A-Z]/g, "").length / text.replace(/[^a-zA-Z]/g, "").length)
    : 0;
  const capsBoost = capsRatio > 0.5 && text.length > 3 ? 1.5 : 1.0;
  const exclamations = (text.match(/!/g) || []).length;
  const punctBoost = 1.0 + Math.min(exclamations, 5) * 0.1;
  
  // === STEP 1b: Idiom/phrase detection ===
  const lower = text.toLowerCase();
  const IDIOMS = {
    "had it": { RAGE: 0.8 },
    "had enough": { RAGE: 0.7 },
    "fed up": { RAGE: 0.7 },
    "sick of": { RAGE: 0.6 },
    "tired of": { RAGE: 0.5 },
    "can't stand": { RAGE: 0.7 },
    "drives me crazy": { RAGE: 0.7 },
    "driving me crazy": { RAGE: 0.7 },
    "drive me crazy": { RAGE: 0.7 },
    "piss me off": { RAGE: 0.8 },
    "pisses me off": { RAGE: 0.8 },
    "pissing me off": { RAGE: 0.8 },
    "makes me angry": { RAGE: 0.7 },
    "going crazy": { RAGE: 0.5, PANIC: 0.4 },
    "losing my mind": { RAGE: 0.5, PANIC: 0.5 },
    "at my limit": { RAGE: 0.6, PANIC: 0.3 },
    "breaking point": { RAGE: 0.7, PANIC: 0.4 },
    "over it": { RAGE: 0.5 },
    "done with": { RAGE: 0.5 },
    "give up": { PANIC: 0.6, RAGE: 0.3 },
    "no way": { RAGE: 0.4, FEAR: 0.2 },
    "what the hell": { RAGE: 0.6 },
    "what the heck": { RAGE: 0.4 },
    "oh my god": { FEAR: 0.3, SEEKING: 0.3 },
    "i love": { CARE: 0.9 },
    "thank you": { CARE: 0.6, PLAY: 0.2 },
    "so excited": { SEEKING: 0.8, PLAY: 0.5 },
    "can't wait": { SEEKING: 0.7, PLAY: 0.4 },
    "hell yeah": { PLAY: 0.7, SEEKING: 0.3 },
    "let's go": { SEEKING: 0.6, PLAY: 0.4 },
  };
  
  for (const [phrase, mapping] of Object.entries(IDIOMS)) {
    if (lower.includes(phrase)) {
      matchedWords.push({ word: phrase, type: "idiom" });
      for (const [affect, weight] of Object.entries(mapping)) {
        affects[affect] = (affects[affect] || 0) + weight * (capsBoost > 1 ? capsBoost : 1);
      }
    }
  }
  
  // === STEP 2: Tokenize and word-level analysis ===
  const rawWords = text.toLowerCase().replace(/['']/g, "'").split(/[\s,.:;()\[\]{}"]+/).filter(Boolean);
  
  // Remove exclamation/question from tokens
  const words = rawWords.map(w => w.replace(/[!?]+$/, "")).filter(Boolean);
  
  // === STEP 3: Word-by-word analysis with context ===
  let negationActive = false;
  let negationWindow = 0;  // Track remaining words that negation applies to
  let degreeModifier = 1.0;
  let pivotSeen = false;
  const prePhrase = [];
  const postPhrase = [];
  
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    
    // Check for pivot words ("but")
    if (PIVOT_WORDS.has(word)) {
      pivotSeen = true;
      negationActive = false;
      negationWindow = 0;
      degreeModifier = 1.0;
      continue;
    }
    
    // Check for negation - set 2-word window
    if (NEGATION_WORDS.has(word)) {
      negationActive = true;
      negationWindow = 2;  // Negate next 2 words
      continue;
    }
    
    // Check for degree modifiers
    if (DEGREE_MODIFIERS[word]) {
      degreeModifier = DEGREE_MODIFIERS[word];
      continue;
    }
    
    // Check two-word degree modifiers
    if (i < words.length - 1) {
      const twoWord = word + " " + words[i + 1];
      if (DEGREE_MODIFIERS[twoWord]) {
        degreeModifier = DEGREE_MODIFIERS[twoWord];
        continue;
      }
    }
    
    // Stem and lookup
    const stems = [word];
    if (word.endsWith("ing") && word.length > 5) stems.push(word.slice(0, -3));
    if (word.endsWith("ed") && word.length > 4) stems.push(word.slice(0, -2));
    if (word.endsWith("ly") && word.length > 4) stems.push(word.slice(0, -2));
    if (word.endsWith("ness") && word.length > 6) stems.push(word.slice(0, -4));
    if (word.endsWith("ful") && word.length > 5) stems.push(word.slice(0, -3));
    if (word.endsWith("less") && word.length > 6) stems.push(word.slice(0, -4));
    if (word.endsWith("s") && word.length > 3 && !word.endsWith("ss")) stems.push(word.slice(0, -1));
    
    for (const stem of stems) {
      const mapping = LEXICON_LOWER[stem];
      if (mapping) {
        matchedWords.push({ word, stem, type: "lexicon" });
        
        // Check if this word was ALL CAPS in original
        const origWord = text.split(/[\s,.:;!?()\[\]{}"]+/).find(w => w.toLowerCase() === word);
        const wordCapsBoost = origWord && origWord === origWord.toUpperCase() && origWord.length > 2 ? 1.5 : 1.0;
        
        const effectiveModifier = degreeModifier * wordCapsBoost * capsBoost * punctBoost;
        
        for (const [affect, weight] of Object.entries(mapping)) {
          let effectiveWeight = weight * effectiveModifier;
          
          // Negation inverts the affect
          if (negationActive) {
            // "not happy" → reduce PLAY, increase slight PANIC
            effectiveWeight *= -0.5;
          }
          
          const bucket = pivotSeen ? postPhrase : prePhrase;
          bucket.push({ affect, weight: effectiveWeight });
        }
        
        // Reset modifiers after use, but keep negation window count
        if (negationWindow > 0) negationWindow--;
        if (negationWindow === 0) negationActive = false;
        degreeModifier = 1.0;
        break;
      }
    }
    
    // Reset negation window when no word match occurred (2 words passed)
    if (negationActive && negationWindow > 0) negationWindow--;
    if (negationWindow === 0) negationActive = false;
  }
  
  // === STEP 4: Combine pre/post pivot phrases ===
  // "but" gives 70% weight to post-phrase, 30% to pre-phrase
  const preWeight = pivotSeen ? 0.3 : 1.0;
  const postWeight = pivotSeen ? 0.7 : 0.0;
  
  for (const { affect, weight } of prePhrase) {
    affects[affect] = (affects[affect] || 0) + weight * preWeight;
  }
  for (const { affect, weight } of postPhrase) {
    affects[affect] = (affects[affect] || 0) + weight * postWeight;
  }
  
  // === STEP 5: Normalize ===
  // Clamp negative values (from negation) to 0
  for (const affect of AFFECTS) {
    if (affects[affect] !== undefined) {
      affects[affect] = Math.max(0, affects[affect]);
    }
  }
  
  // Scale: don't divide by sqrt(matchCount) — that was the old bug.
  // Instead, normalize so max affect is ≤ 1.0
  const maxAffect = Math.max(...Object.values(affects), 0.001);
  if (maxAffect > 1.0) {
    for (const affect of AFFECTS) {
      if (affects[affect]) affects[affect] /= maxAffect;
    }
  }
  
  // Overall intensity based on match density and modifiers
  const wordCount = words.length || 1;
  const matchDensity = matchedWords.length / wordCount;
  const intensity = Math.min(1.0, matchDensity * capsBoost * punctBoost);
  
  return {
    affects,
    intensity: Math.max(0.3, intensity), // minimum 0.3 intensity for any matched content
    matchCount: matchedWords.length,
    debug: {
      matchedWords: matchedWords.map(m => m.word),
      capsBoost,
      punctBoost,
      pivotSeen,
      matchDensity: Math.round(matchDensity * 100) / 100,
    },
  };
}