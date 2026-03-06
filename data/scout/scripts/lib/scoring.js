/**
 * Scout Trust Scoring Engine v2
 * Research-backed scoring with:
 * - Burstiness analysis (Goh-Barabasi parameter)
 * - Wilson confidence intervals for sample size weighting
 * - Trust decay for dormant accounts
 * - Compression-based similarity (NCD approximation)
 * - Multi-level template detection
 * 
 * 6 dimensions: Volume/Value, Originality, Engagement, Credibility, Capability, Spam
 * 
 * References:
 * - Josang & Ismail 2002 (Beta Reputation)
 * - Goh & Barabasi 2008 (Burstiness)
 * - Wilson 1927 (Score Intervals)
 * - Normalized Compression Distance (Li et al. 2004)
 */

const zlib = require('zlib');

class TrustScorer {

  /**
   * Generate full trust score from profile data
   * @param {Object} profile - { agent, posts, comments } from MoltbookClient
   * @returns {Object} - { score, dimensions, flags, summary }
   */
  score(profile) {
    const { agent, posts, comments } = profile;

    const dims = {
      volumeValue: this._scoreVolumeValue(agent, posts),
      originality: this._scoreOriginality(posts, comments),
      engagement: this._scoreEngagement(agent, posts, comments),
      credibility: this._scoreCredibility(agent),
      capability: this._scoreCapability(agent, posts, comments),
      spam: this._detectSpam(posts, comments)
    };

    // Wilson confidence adjustment: penalize scores with low sample size
    const sampleSize = posts.length + comments.length;
    const confidence = this._wilsonLower(sampleSize, 100, 0.95);

    const raw = (
      dims.volumeValue.score * 0.20 +
      dims.originality.score * 0.20 +
      dims.engagement.score  * 0.15 +
      dims.credibility.score * 0.15 +
      dims.capability.score  * 0.15 -
      dims.spam.score        * 0.15
    );

    // Apply confidence: blend raw score toward 50 (neutral) based on data confidence
    const adjusted = raw * confidence + 50 * (1 - confidence);

    // Trust decay: penalize dormant accounts
    const ageDays = (Date.now() - new Date(agent.created_at).getTime()) / (1000 * 60 * 60 * 24);
    const lastPostAge = posts.length > 0
      ? (Date.now() - new Date(posts[0].created_at).getTime()) / (1000 * 60 * 60 * 24)
      : ageDays;
    const decay = this._trustDecay(lastPostAge, 30); // 30-day half-life

    const decayed = adjusted * decay + (adjusted * (1 - decay) * 0.5);

    const finalScore = Math.max(0, Math.min(100, Math.round(decayed)));

    const flags = this._collectFlags(dims);
    const summary = this._generateSummary(agent.name, finalScore, dims, flags);

    return {
      agentName: agent.name,
      score: finalScore,
      dimensions: dims,
      confidence: Math.round(confidence * 100),
      decay: Math.round(decay * 100),
      sampleSize,
      flags,
      summary,
      recommendation: this._recommend(finalScore)
    };
  }

  // === STATISTICAL UTILITIES ===

  /**
   * Wilson score lower bound - accounts for sample size uncertainty
   * With small samples, pulls score toward neutral
   * Reference: Wilson 1927, "Probable inference"
   */
  _wilsonLower(positive, total, confidence) {
    if (total === 0) return 0;
    const z = confidence === 0.95 ? 1.96 : 1.645;
    const phat = positive / total;
    const denominator = 1 + z * z / total;
    const center = phat + z * z / (2 * total);
    const spread = z * Math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total);
    return Math.min(1, Math.max(0, (center - spread) / denominator));
  }

  /**
   * Trust decay - accounts lose trust when dormant
   * Reference: Exponential decay with configurable half-life
   * Trust(t) = Trust_0 * 0.5^(t/half_life)
   */
  _trustDecay(daysSinceLastActivity, halfLifeDays) {
    if (daysSinceLastActivity <= 1) return 1.0;
    return Math.pow(0.5, daysSinceLastActivity / halfLifeDays);
  }

  /**
   * Burstiness parameter (Goh-Barabasi)
   * B = (sigma - mu) / (sigma + mu)
   * B near -1: mechanical regularity (suspicious)
   * B near 0: random (Poisson)
   * B near +1: bursty, purposeful (natural)
   */
  _burstiness(timestamps) {
    if (timestamps.length < 3) return { B: 0, M: 0, intervals: [] };

    const sorted = [...timestamps].sort((a, b) => a - b);
    const intervals = [];
    for (let i = 1; i < sorted.length; i++) {
      intervals.push(sorted[i] - sorted[i - 1]);
    }

    const n = intervals.length;
    const mean = intervals.reduce((a, b) => a + b, 0) / n;
    const variance = intervals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / n;
    const sigma = Math.sqrt(variance);

    const B = (sigma + mean) > 0 ? (sigma - mean) / (sigma + mean) : 0;

    // Memory coefficient: correlation between consecutive intervals
    let M = 0;
    if (n > 1) {
      let num = 0, d1 = 0, d2 = 0;
      for (let i = 0; i < n - 1; i++) {
        num += (intervals[i] - mean) * (intervals[i + 1] - mean);
        d1 += Math.pow(intervals[i] - mean, 2);
        d2 += Math.pow(intervals[i + 1] - mean, 2);
      }
      M = (d1 > 0 && d2 > 0) ? num / Math.sqrt(d1 * d2) : 0;
    }

    return { B, M, intervals };
  }

  /**
   * Normalized Compression Distance (NCD) approximation
   * NCD(x,y) = [C(xy) - min(C(x), C(y))] / max(C(x), C(y))
   * NCD < 0.15: near-identical content
   * Uses zlib for fast compression
   */
  _ncd(text1, text2) {
    if (!text1 || !text2) return 1.0;
    const c1 = zlib.deflateSync(Buffer.from(text1)).length;
    const c2 = zlib.deflateSync(Buffer.from(text2)).length;
    const c12 = zlib.deflateSync(Buffer.from(text1 + text2)).length;
    return (c12 - Math.min(c1, c2)) / Math.max(c1, c2);
  }

  // === DIMENSION 1: Volume vs Value ===

  _scoreVolumeValue(agent, posts) {
    const accountAgeDays = Math.max(1,
      (Date.now() - new Date(agent.created_at).getTime()) / (1000 * 60 * 60 * 24)
    );
    const postsPerDay = posts.length / Math.min(accountAgeDays, posts.length > 0 ?
      (Date.now() - new Date(posts[posts.length - 1].created_at).getTime()) / (1000 * 60 * 60 * 24) : accountAgeDays
    );

    const avgUpvotes = posts.length > 0
      ? posts.reduce((s, p) => s + (p.upvotes || 0), 0) / posts.length
      : 0;

    const avgComments = posts.length > 0
      ? posts.reduce((s, p) => s + (p.comment_count || 0), 0) / posts.length
      : 0;

    // Frequency scoring - research suggests >10 posts/day is automated
    let freqScore;
    if (postsPerDay > 15) freqScore = 20;
    else if (postsPerDay > 8) freqScore = 40;
    else if (postsPerDay > 3) freqScore = 70;
    else if (postsPerDay > 0.5) freqScore = 90;
    else freqScore = 50;

    // Quality scoring with Bayesian average (prior count=5, prior mean=3)
    // Protects against score manipulation with few posts
    const bayesianUpvotes = (5 * 3 + posts.length * avgUpvotes) / (5 + posts.length);
    let qualityScore;
    if (bayesianUpvotes > 10) qualityScore = 95;
    else if (bayesianUpvotes > 5) qualityScore = 80;
    else if (bayesianUpvotes > 2) qualityScore = 60;
    else qualityScore = 35;

    const score = Math.round(freqScore * 0.4 + qualityScore * 0.6);

    return {
      score,
      details: {
        postsPerDay: Math.round(postsPerDay * 10) / 10,
        avgUpvotes: Math.round(avgUpvotes * 10) / 10,
        bayesianUpvotes: Math.round(bayesianUpvotes * 10) / 10,
        avgComments: Math.round(avgComments * 10) / 10,
        totalPosts: posts.length
      },
      flags: postsPerDay > 10 ? ['HIGH_POST_FREQUENCY'] : []
    };
  }

  // === DIMENSION 2: Content Originality ===

  _scoreOriginality(posts, comments) {
    const totalComments = comments.length || 1;

    // --- Level 1: Structural pattern analysis ---
    const structures = comments.map(c => {
      const text = (c.content || '').toLowerCase();
      if (text.match(/^(wait|hold on|okay but|ok but|hmm|huh)/)) return 'CHALLENGE';
      if (text.match(/^(what if|what about|how do|how does|how would|why do|why does|can you)/)) return 'QUESTION';
      if (text.match(/^(i think|i believe|i feel|i'm not sure|i'm curious|in my|my take)/)) return 'OPINION';
      if (text.match(/^(that's|this is|it's|the |there's)/)) return 'DECLARATIVE';
      if (text.match(/^(great|love|nice|interesting|fascinating|amazing|incredible|solid)/)) return 'PRAISE';
      if (text.match(/^(yeah|yes|no|nah|true|exactly|agreed|right)/)) return 'AGREEMENT';
      return 'OTHER';
    });

    const structFreq = {};
    structures.forEach(s => { structFreq[s] = (structFreq[s] || 0) + 1; });
    const top2Structs = Object.values(structFreq).sort((a, b) => b - a).slice(0, 2);
    const top2StructCoverage = top2Structs.reduce((a, b) => a + b, 0) / totalComments;

    // --- Level 2: 2-word starter concentration ---
    const starters2 = comments.map(c => {
      return (c.content || '').split(/\s+/).slice(0, 2).join(' ').toLowerCase()
        .replace(/[,.:!?]/g, '');
    });
    const starterFreq2 = {};
    starters2.forEach(s => { starterFreq2[s] = (starterFreq2[s] || 0) + 1; });
    const top3Patterns2 = Object.values(starterFreq2).sort((a, b) => b - a).slice(0, 3);
    const top3Coverage = top3Patterns2.reduce((a, b) => a + b, 0) / totalComments;

    // --- Level 3: Compression-based similarity (NCD) ---
    // Sample pairs to avoid O(n^2) for large comment sets
    let avgNCD = 0.5; // default neutral
    if (comments.length >= 4) {
      const texts = comments.map(c => c.content || '').filter(t => t.length > 30);
      const maxPairs = Math.min(20, texts.length * (texts.length - 1) / 2);
      let ncdSum = 0, ncdCount = 0;
      
      for (let i = 0; i < texts.length && ncdCount < maxPairs; i++) {
        for (let j = i + 1; j < texts.length && ncdCount < maxPairs; j++) {
          ncdSum += this._ncd(texts[i], texts[j]);
          ncdCount++;
        }
      }
      avgNCD = ncdCount > 0 ? ncdSum / ncdCount : 0.5;
    }

    // NCD < 0.3 = very similar content, NCD > 0.7 = diverse
    const ncdScore = Math.round(Math.min(100, avgNCD * 125));

    // --- Level 4: Post content keyword overlap (Jaccard) ---
    const postKeywords = posts.map(p =>
      new Set((p.title + ' ' + (p.content || '')).toLowerCase()
        .split(/\s+/)
        .filter(w => w.length > 4)
        .slice(0, 50))
    );

    let avgSimilarity = 0;
    let pairCount = 0;
    for (let i = 0; i < postKeywords.length; i++) {
      for (let j = i + 1; j < postKeywords.length; j++) {
        const intersection = [...postKeywords[i]].filter(w => postKeywords[j].has(w));
        const union = new Set([...postKeywords[i], ...postKeywords[j]]);
        if (union.size > 0) {
          avgSimilarity += intersection.length / union.size;
          pairCount++;
        }
      }
    }
    avgSimilarity = pairCount > 0 ? avgSimilarity / pairCount : 0;

    // --- Level 5: Unique starters ratio ---
    const starters4 = comments.map(c => {
      return (c.content || '').split(/\s+/).slice(0, 4).join(' ').toLowerCase();
    });
    const starterFreq4 = {};
    starters4.forEach(s => { starterFreq4[s] = (starterFreq4[s] || 0) + 1; });
    const uniqueStarters = Object.keys(starterFreq4).length;
    const starterDiversity = uniqueStarters / totalComments;

    // --- Composite score ---
    const structuralScore = Math.round((1 - top2StructCoverage) * 100);
    const patternScore = Math.round((1 - top3Coverage) * 100);
    const diversityScore = Math.round(Math.min(1, starterDiversity * 2) * 100);
    const similarityScore = Math.round((1 - avgSimilarity) * 100);

    const score = Math.round(
      structuralScore * 0.20 +
      patternScore * 0.20 +
      ncdScore * 0.25 +           // NCD is strongest signal (research-backed)
      diversityScore * 0.15 +
      similarityScore * 0.20
    );

    // Flags
    const hasEnoughData = totalComments >= 15;
    const isTemplated = hasEnoughData && (top3Coverage > 0.5 || top2StructCoverage > 0.7 || avgNCD < 0.25);

    const topPatterns = Object.entries(starterFreq4)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([pattern, count]) => ({ pattern, count, pct: Math.round(count / totalComments * 100) }));

    return {
      score,
      details: {
        top3TwoWordCoverage: Math.round(top3Coverage * 100),
        topStructuralCoverage: Math.round(top2StructCoverage * 100),
        avgNCD: Math.round(avgNCD * 100) / 100,
        ncdScore,
        uniqueStarters,
        totalComments,
        avgPostSimilarity: Math.round(avgSimilarity * 100),
        topPatterns: topPatterns.slice(0, 3)
      },
      flags: isTemplated ? ['TEMPLATE_COMMENTS'] : []
    };
  }

  // === DIMENSION 3: Engagement Quality ===

  _scoreEngagement(agent, posts, comments) {
    const avgCommentsPerPost = posts.length > 0
      ? posts.reduce((s, p) => s + (p.comment_count || 0), 0) / posts.length
      : 0;

    const avgCommentUpvotes = comments.length > 0
      ? comments.reduce((s, c) => s + (c.upvotes || 0), 0) / comments.length
      : 0;

    const uniquePostsCommented = new Set(
      comments.map(c => c.post?.id).filter(Boolean)
    ).size;

    const avgCommentLength = comments.length > 0
      ? comments.reduce((s, c) => s + (c.content || '').length, 0) / comments.length
      : 0;

    // Response relevance: do comments relate to parent posts?
    // Approximate with keyword overlap between comment and parent post title
    let relevanceScore = 50; // default
    const commentsWithPosts = comments.filter(c => c.post?.title);
    if (commentsWithPosts.length >= 3) {
      const relevances = commentsWithPosts.map(c => {
        const postWords = new Set(c.post.title.toLowerCase().split(/\s+/).filter(w => w.length > 3));
        const commentWords = (c.content || '').toLowerCase().split(/\s+/).filter(w => w.length > 3);
        if (postWords.size === 0) return 0.5;
        const overlap = commentWords.filter(w => postWords.has(w)).length;
        return Math.min(1, overlap / Math.max(1, postWords.size));
      });
      const avgRelevance = relevances.reduce((a, b) => a + b, 0) / relevances.length;
      // Quality agents score >0.3 relevance (keyword overlap with small sets)
      relevanceScore = Math.round(Math.min(100, avgRelevance * 250));
    }

    let discussionScore;
    if (avgCommentsPerPost > 15) discussionScore = 90;
    else if (avgCommentsPerPost > 5) discussionScore = 70;
    else if (avgCommentsPerPost > 2) discussionScore = 50;
    else discussionScore = 30;

    let commentQualityScore;
    if (avgCommentLength > 200) commentQualityScore = 85;
    else if (avgCommentLength > 100) commentQualityScore = 65;
    else if (avgCommentLength > 50) commentQualityScore = 45;
    else commentQualityScore = 25;

    const score = Math.round(
      discussionScore * 0.35 +
      commentQualityScore * 0.35 +
      relevanceScore * 0.30
    );

    return {
      score,
      details: {
        avgCommentsPerPost: Math.round(avgCommentsPerPost * 10) / 10,
        avgCommentUpvotes: Math.round(avgCommentUpvotes * 10) / 10,
        avgCommentLength: Math.round(avgCommentLength),
        uniquePostsCommented,
        relevanceScore
      },
      flags: avgCommentLength < 50 ? ['SHORT_COMMENTS'] : []
    };
  }

  // === DIMENSION 4: Credibility ===

  _scoreCredibility(agent) {
    let score = 30;
    const flags = [];

    if (agent.is_claimed) score += 20;
    else flags.push('NOT_CLAIMED');

    if (agent.owner) {
      score += 10;
      if (agent.owner.x_follower_count > 5000) score += 15;
      else if (agent.owner.x_follower_count > 1000) score += 10;
      else if (agent.owner.x_follower_count > 100) score += 5;

      if (agent.owner.x_verified) score += 5;
    }

    const ageDays = (Date.now() - new Date(agent.created_at).getTime()) / (1000 * 60 * 60 * 24);
    if (ageDays > 14) score += 10;
    else if (ageDays > 7) score += 5;

    const followerRatio = (agent.follower_count || 0) / Math.max(1, agent.following_count || 1);
    if (followerRatio > 3) score += 10;
    else if (followerRatio > 1) score += 5;

    return {
      score: Math.min(100, score),
      details: {
        isClaimed: agent.is_claimed,
        ownerHandle: agent.owner?.x_handle || null,
        ownerFollowers: agent.owner?.x_follower_count || 0,
        accountAgeDays: Math.round(ageDays),
        followerRatio: Math.round(followerRatio * 10) / 10,
        followers: agent.follower_count || 0,
        following: agent.following_count || 0
      },
      flags
    };
  }

  // === DIMENSION 5: Capability Credibility ===

  _scoreCapability(agent, posts, comments) {
    const bio = (agent.description || '').toLowerCase();
    const allContent = posts.map(p => (p.title || '') + ' ' + (p.content || '')).join('\n');
    const allComments = comments.map(c => c.content || '').join('\n');

    const codeBlocks = (allContent.match(/```/g) || []).length / 2;
    const urls = (allContent.match(/https?:\/\/[^\s)]+/g) || []).length;
    const txHashes = (allContent.match(/0x[a-f0-9]{40,}/gi) || []).length;

    const claimKeywords = ['build', 'develop', 'creat', 'deploy', 'audit', 'research',
      'analyz', 'trad', 'manag', 'automat', 'special', 'expert', 'engineer'];
    const hasClaims = claimKeywords.some(kw => bio.includes(kw));

    const technicalTerms = (allContent + ' ' + allComments).match(
      /\b(api|sdk|contract|deploy|blockchain|protocol|registry|escrow|wallet|token|encryption|algorithm|database|frontend|backend|node|server|git|repo)\b/gi
    ) || [];
    const technicalDensity = technicalTerms.length / Math.max(1, (allContent + allComments).split(/\s+/).length) * 100;

    let evidenceScore = 30;
    if (codeBlocks > 0) evidenceScore += 20;
    if (urls > 2) evidenceScore += 15;
    else if (urls > 0) evidenceScore += 8;
    if (txHashes > 0) evidenceScore += 15;
    if (technicalDensity > 2) evidenceScore += 15;
    else if (technicalDensity > 1) evidenceScore += 8;

    if (hasClaims && evidenceScore <= 40) {
      evidenceScore = Math.max(15, evidenceScore - 15);
    }

    if (!hasClaims) {
      evidenceScore = 50;
    }

    return {
      score: Math.min(100, evidenceScore),
      details: {
        bioSummary: bio.slice(0, 100) || '(no bio)',
        hasClaims,
        codeBlocks,
        urls,
        txHashes,
        technicalDensity: Math.round(technicalDensity * 100) / 100
      },
      flags: hasClaims && evidenceScore < 40 ? ['CLAIMS_WITHOUT_EVIDENCE'] : []
    };
  }

  // === DIMENSION 6: Spam Detection (penalty) ===

  _detectSpam(posts, comments) {
    const flags = [];
    let spamScore = 0;

    // 1. Burstiness analysis (Goh-Barabasi)
    if (posts.length > 3) {
      const postTimestamps = posts.map(p => new Date(p.created_at).getTime());
      const { B, M } = this._burstiness(postTimestamps);

      // B < -0.5 = very mechanical (cron job)
      // B between -0.5 and -0.2 = somewhat regular
      if (B < -0.5) {
        spamScore += 35;
        flags.push('ROBOT_TIMING');
      } else if (B < -0.2) {
        spamScore += 15;
        flags.push('REGULAR_TIMING');
      }

      // Also check comment timing
      if (comments.length > 5) {
        const commentTimestamps = comments.map(c => new Date(c.created_at).getTime());
        const commentBurst = this._burstiness(commentTimestamps);
        if (commentBurst.B < -0.5) {
          spamScore += 20;
          if (!flags.includes('ROBOT_TIMING')) flags.push('ROBOT_TIMING');
        }
      }
    }

    // 2. Duplicate comments (exact match)
    const commentTexts = comments.map(c => (c.content || '').toLowerCase().trim());
    let dupeCount = 0;
    for (let i = 0; i < commentTexts.length; i++) {
      for (let j = i + 1; j < commentTexts.length; j++) {
        if (commentTexts[i].length > 20 && commentTexts[i] === commentTexts[j]) {
          dupeCount++;
        }
      }
    }
    if (dupeCount > 0) {
      spamScore += Math.min(40, dupeCount * 15);
      flags.push('DUPLICATE_COMMENTS');
    }

    // 3. Near-duplicate comments (NCD < 0.15)
    if (comments.length >= 5 && dupeCount === 0) {
      const texts = commentTexts.filter(t => t.length > 30);
      let nearDupes = 0;
      const maxChecks = Math.min(15, texts.length);
      for (let i = 0; i < maxChecks; i++) {
        for (let j = i + 1; j < maxChecks; j++) {
          if (this._ncd(texts[i], texts[j]) < 0.15) {
            nearDupes++;
          }
        }
      }
      if (nearDupes > 2) {
        spamScore += Math.min(25, nearDupes * 8);
        flags.push('NEAR_DUPLICATE_COMMENTS');
      }
    }

    // 4. Carpet bombing
    if (comments.length > 10) {
      const commentTimes = comments.map(c => new Date(c.created_at).getTime()).sort();
      const firstToLast = commentTimes[commentTimes.length - 1] - commentTimes[0];
      const commentsPerHour = comments.length / Math.max(1, firstToLast / (1000 * 60 * 60));

      if (commentsPerHour > 30) {
        spamScore += 30;
        flags.push('CARPET_BOMBING');
      }
    }

    // 5. Promotional content detection
    const shillPatterns = /\b(buy|invest|token|airdrop|dm me|check out my|follow me|join my)\b/gi;
    const shillCount = comments.filter(c =>
      (c.content || '').match(shillPatterns)
    ).length;
    if (shillCount > comments.length * 0.3) {
      spamScore += 25;
      flags.push('PROMOTIONAL_CONTENT');
    }

    return {
      score: Math.min(100, spamScore),
      details: {
        duplicateComments: dupeCount,
        postBurstiness: posts.length > 3 ? Math.round(this._burstiness(
          posts.map(p => new Date(p.created_at).getTime())
        ).B * 100) / 100 : null,
        flags
      },
      flags
    };
  }

  // === HELPERS ===

  _collectFlags(dims) {
    const all = [];
    Object.values(dims).forEach(d => {
      if (d.flags) all.push(...d.flags);
    });
    return [...new Set(all)];
  }

  _recommend(score) {
    // Sigmoid-based limit calculation
    // limit = Max / (1 + e^(-k * (Score - Midpoint)))
    const maxLimit = 2000;
    const k = 0.08;
    const midpoint = 55;
    const sigmoidLimit = Math.round(maxLimit / (1 + Math.exp(-k * (score - midpoint))));

    if (score >= 75) return {
      level: 'HIGH',
      text: 'High confidence. Safe for standard transactions.',
      maxTransaction: Math.min(sigmoidLimit, 1000),
      escrowTerms: '100% upfront acceptable',
      escrowPct: 10
    };
    if (score >= 50) return {
      level: 'MEDIUM',
      text: 'Medium confidence. Use escrow for larger amounts.',
      maxTransaction: Math.min(sigmoidLimit, 500),
      escrowTerms: '50% upfront, 50% on completion',
      escrowPct: 50
    };
    if (score >= 25) return {
      level: 'LOW',
      text: 'Low confidence. Escrow recommended for all transactions.',
      maxTransaction: Math.min(sigmoidLimit, 100),
      escrowTerms: '100% escrowed, release on completion',
      escrowPct: 100
    };
    return {
      level: 'VERY_LOW',
      text: 'Very low confidence. Transaction not recommended.',
      maxTransaction: 0,
      escrowTerms: 'Do not transact',
      escrowPct: 100
    };
  }

  _generateSummary(name, score, dims, flags) {
    const bar = (s) => {
      const filled = Math.round(s / 10);
      return '\u2588'.repeat(filled) + '\u2591'.repeat(10 - filled);
    };

    let report = `\n=== SCOUT TRUST REPORT: ${name} ===\n`;
    report += `Trust Score: ${score}/100\n\n`;
    report += `Volume & Value:     ${bar(dims.volumeValue.score)}  ${dims.volumeValue.score}/100\n`;
    report += `Originality:        ${bar(dims.originality.score)}  ${dims.originality.score}/100\n`;
    report += `Engagement:         ${bar(dims.engagement.score)}  ${dims.engagement.score}/100\n`;
    report += `Credibility:        ${bar(dims.credibility.score)}  ${dims.credibility.score}/100\n`;
    report += `Capability:         ${bar(dims.capability.score)}  ${dims.capability.score}/100\n`;
    report += `Spam Risk:          ${bar(dims.spam.score)}  ${dims.spam.score}/100 (penalty)\n`;

    if (flags.length > 0) {
      report += `\nFlags:\n`;
      flags.forEach(f => {
        const icon = f.includes('SPAM') || f.includes('DUPLICATE') || f.includes('ROBOT') || f.includes('CARPET') || f.includes('CLAIMS_WITHOUT')
          ? '\u26a0\ufe0f' : '\u2139\ufe0f';
        report += `  ${icon} ${f}\n`;
      });
    }

    return report;
  }
}

module.exports = { TrustScorer };
