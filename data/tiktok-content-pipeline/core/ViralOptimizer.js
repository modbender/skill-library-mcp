/**
 * Viral Optimizer
 * 
 * Data-driven content optimization engine based on TikTok virality research (Feb 2026).
 * Integrates directly into the content pipeline to maximize reach and engagement.
 * 
 * Key research findings baked in:
 * - Completion rate 80%+ = 5x reach increase
 * - Save-to-view ratio 15%+ = high-value content
 * - Share rate 8%+ = viral potential
 * - Videos with music = 98% more views
 * - 3-4 posts/week optimal (NOT 3/day)
 * - Carousels get 3x more saves, 40% longer dwell time
 * - First 3 seconds determine everything
 */

const fs = require('fs');
const path = require('path');

class ViralOptimizer {
  constructor(config) {
    this.config = config;
    
    // Research-backed thresholds
    this.thresholds = {
      completionRate: { target: 0.80, viral: 0.90, poor: 0.40 },
      saveToViewRatio: { target: 0.15, viral: 0.25, poor: 0.03 },
      shareRate: { target: 0.08, viral: 0.15, poor: 0.02 },
      commentRate: { target: 0.05, viral: 0.10, poor: 0.01 },
      profileVisitRate: { target: 0.12, viral: 0.20, poor: 0.03 },
      followerConversion: { target: 0.08, viral: 0.15, poor: 0.02 }
    };

    // Optimal posting schedule (research-backed)
    this.optimalSchedule = {
      postsPerWeek: { min: 3, optimal: 4, max: 5 },
      // New accounts: daily for first 30 days
      newAccountDailyDays: 30,
      bestDays: ['wednesday', 'tuesday', 'thursday'],
      bestTimes: {
        tuesday: ['17:00'],
        wednesday: ['14:00', '15:00', '16:00', '17:00'],
        thursday: ['15:00', '16:00', '17:00'],
        // Fallback for other days
        default: ['12:00', '18:00']
      },
      // CRITICAL: 3x/day HURTS reach. Research says quality > quantity
      maxPerDay: 1,
      newAccountMaxPerDay: 2
    };
  }

  /**
   * Optimize content before posting
   * Validates against viral mechanics and suggests improvements
   */
  optimizeContent(content, contentType) {
    const issues = [];
    const suggestions = [];
    const score = { hook: 0, structure: 0, engagement: 0, total: 0 };

    // 1. Hook analysis (first slide / first 3 seconds)
    const hookAnalysis = this._analyzeHook(content);
    score.hook = hookAnalysis.score;
    issues.push(...hookAnalysis.issues);
    suggestions.push(...hookAnalysis.suggestions);

    // 2. Content structure analysis
    const structureAnalysis = this._analyzeStructure(content, contentType);
    score.structure = structureAnalysis.score;
    issues.push(...structureAnalysis.issues);
    suggestions.push(...structureAnalysis.suggestions);

    // 3. Engagement potential analysis
    const engagementAnalysis = this._analyzeEngagementPotential(content);
    score.engagement = engagementAnalysis.score;
    issues.push(...engagementAnalysis.issues);
    suggestions.push(...engagementAnalysis.suggestions);

    // Overall viral potential score (0-100)
    score.total = Math.round((score.hook * 0.4 + score.structure * 0.3 + score.engagement * 0.3));

    return {
      score,
      issues,
      suggestions,
      verdict: this._getVerdict(score.total),
      shouldPost: score.total >= 50
    };
  }

  /**
   * Generate optimized hook based on content type and proven patterns
   */
  generateOptimizedHook(contentType, context = {}) {
    const hookPatterns = this._getProvenHookPatterns();
    const nicheHooks = hookPatterns[contentType] || hookPatterns.default;

    // Select hook pattern based on rotation strategy
    const pattern = this._selectHookPattern(nicheHooks, context);

    // Apply viral mechanics
    return {
      text: this._applyPlaceholders(pattern.template, context),
      type: pattern.type,
      expectedPerformance: pattern.avgEngagement,
      slideText: pattern.slideText ? this._applyPlaceholders(pattern.slideText, context) : null
    };
  }

  /**
   * Generate optimized caption with hashtags
   */
  generateOptimizedCaption(hook, contentType, context = {}) {
    const caption = [];

    // Hook text (keep short — TikTok truncates at ~150 chars visible)
    caption.push(hook);

    // CTA — research shows specific questions > generic
    const cta = this._getOptimalCTA(contentType, context);
    if (cta) caption.push(cta);

    // Hashtags — mix of niche + discovery
    const hashtags = this._getOptimalHashtags(contentType);
    caption.push(hashtags.join(' '));

    return caption.join('\n\n');
  }

  /**
   * Get optimal posting time for next post
   */
  getNextPostingSlot(accountAge = 30, recentPosts = []) {
    const isNewAccount = accountAge < this.optimalSchedule.newAccountDailyDays;
    const maxPerDay = isNewAccount ? 
      this.optimalSchedule.newAccountMaxPerDay : 
      this.optimalSchedule.maxPerDay;

    const now = new Date();
    const today = now.toISOString().split('T')[0];
    
    // Count posts today
    const postsToday = recentPosts.filter(p => 
      p.publishDate?.startsWith(today)
    ).length;

    if (postsToday >= maxPerDay) {
      // Schedule for tomorrow
      return this._getNextDayOptimalTime(now);
    }

    // Find next optimal time today
    return this._getNextOptimalTimeToday(now);
  }

  /**
   * Analyze post performance against viral thresholds
   */
  analyzePerformance(postMetrics) {
    const analysis = {
      metrics: {},
      diagnosis: '',
      actions: []
    };

    // Map metrics against thresholds
    for (const [metric, thresholds] of Object.entries(this.thresholds)) {
      const value = postMetrics[metric] || 0;
      let status = 'poor';
      
      if (value >= thresholds.viral) status = 'viral';
      else if (value >= thresholds.target) status = 'good';
      else if (value >= thresholds.poor) status = 'ok';

      analysis.metrics[metric] = { value, status, target: thresholds.target };
    }

    // Diagnostic matrix (from research)
    const views = postMetrics.views || 0;
    const engagement = (postMetrics.likes + postMetrics.comments + postMetrics.shares) / Math.max(views, 1);
    const saves = (postMetrics.saves || 0) / Math.max(views, 1);

    if (views > 1000 && engagement > 0.05) {
      analysis.diagnosis = 'SCALE';
      analysis.actions.push('Create 3 variations of this content');
      analysis.actions.push('Test same hook with different visuals');
    } else if (views > 1000 && engagement < 0.03) {
      analysis.diagnosis = 'FIX_CTA';
      analysis.actions.push('Hook is working — add stronger call-to-action');
      analysis.actions.push('Add opinion-split or challenge in caption');
    } else if (views < 500 && saves > 0.10) {
      analysis.diagnosis = 'FIX_HOOK';
      analysis.actions.push('Content converts — needs better opening hook');
      analysis.actions.push('Test with trending audio');
      analysis.actions.push('Stronger first-slide text overlay');
    } else if (views < 500 && engagement < 0.03) {
      analysis.diagnosis = 'FULL_RESET';
      analysis.actions.push('Try radically different content format');
      analysis.actions.push('Research what top creators in niche are doing');
      analysis.actions.push('Test different posting time');
    }

    return analysis;
  }

  /**
   * Get engagement-driving CTA for content type
   * Research: specific questions > generic "what do you think?"
   */
  _getOptimalCTA(contentType, context = {}) {
    const ctaPatterns = {
      'remember-this-card': [
        'What rating would you give this card? 👇',
        'Drop your best memory with this card 💬',
        'Who was YOUR favourite in {game} {year}? 🤔',
        'Save this if you used {player} 🔖'
      ],
      'card-evolution': [
        'Which version was the best? Comment below 👇',
        'Send this to someone who remembers 📤',
        'Save this evolution — it\'s insane 🔖'
      ],
      'cheat-code': [
        'Was {player} the biggest cheat code? 🎮',
        'Tag someone who abused this card 😂',
        'Like if you scored sweaty goals with {player} ⚽'
      ],
      'luxury-showcase': [
        'Would you live here? Yes or no 👇',
        'Save this for your dream home board 🏡',
        'What would you change about this place? 🤔'
      ],
      'coin-explainer': [
        'Save this before your next investment 📌',
        'Which crypto are you most bullish on? 👇',
        'Send this to someone who needs to understand {coin} 📤'
      ],
      default: [
        'Thoughts? 👇',
        'Save for later 🔖',
        'Share with someone who needs this 📤'
      ]
    };

    const ctas = ctaPatterns[contentType] || ctaPatterns.default;
    const cta = ctas[Math.floor(Math.random() * ctas.length)];
    return this._applyPlaceholders(cta, context);
  }

  /**
   * Get optimal hashtag mix
   * Research: niche community hashtags > broad hashtags
   */
  _getOptimalHashtags(contentType) {
    // Strategy: 2-3 niche community hashtags + 1-2 discovery hashtags
    const nicheHashtags = this.config.content?.hashtagSets?.[contentType] || 
                          this.config.content?.hashtagSets?.default || [];
    
    const discoveryHashtags = ['#fyp', '#viral'];
    
    // Max 5 hashtags total (research shows diminishing returns beyond this)
    const combined = [...nicheHashtags.slice(0, 3), ...discoveryHashtags.slice(0, 2)];
    return [...new Set(combined)].slice(0, 5);
  }

  /**
   * Proven hook patterns from research
   */
  _getProvenHookPatterns() {
    return {
      // Gaming nostalgia hooks
      'remember-this-card': [
        { template: 'Remember this card? 🔥', type: 'nostalgia', avgEngagement: 0.06, slideText: '{player} — the one that got away' },
        { template: 'Only real ones remember {player} in {game} {year}', type: 'gatekeeping', avgEngagement: 0.08, slideText: 'If you know, you know 🐐' },
        { template: 'This card was different 💯', type: 'mystery', avgEngagement: 0.05, slideText: 'Wait for it...' },
        { template: 'POV: You just packed {player} in {game} {year} 😱', type: 'pov', avgEngagement: 0.07, slideText: 'That feeling >>> everything' },
        { template: 'Everyone used {player}. Nobody talks about it.', type: 'contradiction', avgEngagement: 0.09, slideText: 'The most OP card nobody mentions' }
      ],
      'card-evolution': [
        { template: '{player}\'s glow up across {game} 📈', type: 'progression', avgEngagement: 0.06 },
        { template: 'Watch {player} become a monster 💪', type: 'transformation', avgEngagement: 0.07 }
      ],
      'cheat-code': [
        { template: '{player} was literally a cheat code 🎮', type: 'exaggeration', avgEngagement: 0.07 },
        { template: 'This card broke the game and nobody stopped it', type: 'controversy', avgEngagement: 0.09 },
        { template: 'If you used {player} in {game} {year}, you had no skill 😂', type: 'challenge', avgEngagement: 0.11 }
      ],
      'luxury-showcase': [
        { template: '£{price} gets you this in {location} 🏡', type: 'price-anchor', avgEngagement: 0.06 },
        { template: 'Would you live here? 👀', type: 'question', avgEngagement: 0.08 },
        { template: 'This {location} home is insane 🤯', type: 'reaction', avgEngagement: 0.05 }
      ],
      'coin-explainer': [
        { template: 'Let me explain {coin} like you\'re 5 🧵', type: 'simplification', avgEngagement: 0.06 },
        { template: 'This one mistake costs people £10K in {coin} 💸', type: 'fear', avgEngagement: 0.09 },
        { template: 'What {coin} actually does (no jargon) 💡', type: 'clarity', avgEngagement: 0.07 }
      ],
      default: [
        { template: 'Wait for it... 👀', type: 'curiosity', avgEngagement: 0.04 },
        { template: 'Nobody talks about this 🤫', type: 'exclusivity', avgEngagement: 0.06 }
      ]
    };
  }

  _analyzeHook(content) {
    const result = { score: 50, issues: [], suggestions: [] };
    
    const hook = content.hook || content.caption || '';
    
    // Check hook length (research: short hooks win)
    if (hook.length > 100) {
      result.issues.push('Hook too long — keep under 100 chars for first-slide text');
      result.score -= 15;
    }
    
    // Check for proven patterns
    const hasQuestion = hook.includes('?');
    const hasEmoji = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}]/u.test(hook);
    const hasNumbers = /\d/.test(hook);
    const hasPowerWords = /remember|secret|never|always|only|best|worst|insane|crazy|cheat|broken/i.test(hook);
    
    if (hasQuestion) result.score += 10;
    if (hasEmoji) result.score += 5;
    if (hasPowerWords) result.score += 15;
    if (hasNumbers) result.score += 5;
    
    if (!hasEmoji) result.suggestions.push('Add emoji — increases visual stopping power');
    if (!hasPowerWords) result.suggestions.push('Use power words (remember, secret, insane, cheat code)');
    if (!hasQuestion && !hasPowerWords) result.suggestions.push('Consider question format or contradiction hook');

    return result;
  }

  _analyzeStructure(content, contentType) {
    const result = { score: 60, issues: [], suggestions: [] };
    
    const slideCount = content.slides?.length || content.media?.length || 0;
    
    // Research: 5-7 slides optimal for carousels
    if (slideCount >= 5 && slideCount <= 7) {
      result.score += 20;
    } else if (slideCount < 5) {
      result.issues.push(`Only ${slideCount} slides — research shows 5-7 is optimal`);
      result.score -= 10;
    } else if (slideCount > 8) {
      result.suggestions.push('Consider trimming — engagement drops after 7 slides');
      result.score -= 5;
    }

    // Check for music/audio
    if (!content.audio && !content.music) {
      result.issues.push('No audio attached — videos with music get 98% more views');
      result.score -= 20;
    }

    return result;
  }

  _analyzeEngagementPotential(content) {
    const result = { score: 50, issues: [], suggestions: [] };
    
    const caption = content.caption || '';
    
    // Check for CTA
    const hasCTA = /\?|comment|save|share|tag|send|drop|tell|rate/i.test(caption);
    if (hasCTA) {
      result.score += 20;
    } else {
      result.suggestions.push('Add a specific CTA — "Rate this 1-10" outperforms "What do you think?"');
    }
    
    // Check for opinion-split potential (drives comments)
    const hasOpinionSplit = /or|vs|better|worse|team|choose/i.test(caption);
    if (hasOpinionSplit) result.score += 15;
    
    // Check hashtag count (research: max 5 effective)
    const hashtagCount = (caption.match(/#/g) || []).length;
    if (hashtagCount > 5) {
      result.suggestions.push('Reduce hashtags to 5 max — diminishing returns beyond that');
      result.score -= 5;
    } else if (hashtagCount >= 3 && hashtagCount <= 5) {
      result.score += 10;
    }

    return result;
  }

  _getVerdict(score) {
    if (score >= 80) return '🔥 HIGH VIRAL POTENTIAL — Post immediately';
    if (score >= 65) return '✅ GOOD — Ready to post';
    if (score >= 50) return '⚠️ DECENT — Consider optimizing before posting';
    if (score >= 35) return '🔧 NEEDS WORK — Apply suggestions before posting';
    return '❌ LOW POTENTIAL — Rethink approach';
  }

  _selectHookPattern(patterns, context) {
    // Weight selection by average engagement
    const totalWeight = patterns.reduce((sum, p) => sum + p.avgEngagement, 0);
    let random = Math.random() * totalWeight;
    
    for (const pattern of patterns) {
      random -= pattern.avgEngagement;
      if (random <= 0) return pattern;
    }
    
    return patterns[0];
  }

  _applyPlaceholders(text, context) {
    return text.replace(/\{(\w+)\}/g, (match, key) => context[key] || match);
  }

  _getNextOptimalTimeToday(now) {
    const dayName = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
    const times = this.optimalSchedule.bestTimes[dayName] || this.optimalSchedule.bestTimes.default;
    const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    
    const nextTime = times.find(t => t > currentTime);
    if (nextTime) {
      const [h, m] = nextTime.split(':');
      const slot = new Date(now);
      slot.setHours(parseInt(h), parseInt(m), 0, 0);
      return slot;
    }
    
    return this._getNextDayOptimalTime(now);
  }

  _getNextDayOptimalTime(now) {
    const tomorrow = new Date(now);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dayName = tomorrow.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
    const times = this.optimalSchedule.bestTimes[dayName] || this.optimalSchedule.bestTimes.default;
    
    const [h, m] = times[0].split(':');
    tomorrow.setHours(parseInt(h), parseInt(m), 0, 0);
    return tomorrow;
  }
}

module.exports = ViralOptimizer;