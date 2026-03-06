/**
 * Agent Interaction Graph & SybilRank Analysis
 * 
 * Builds a directed interaction graph from Moltbook data:
 * - A -> B edge when A comments on B's post
 * - Edge weight = number of interactions
 * 
 * Implements simplified SybilRank (Cao et al. 2012):
 * - Propagate trust from seed nodes through the graph
 * - Early-stopping power iteration
 * - Agents isolated from trusted seeds get low scores
 * 
 * Also detects:
 * - Reciprocal comment rings
 * - Unusually dense clusters (potential Sybil farms)
 * - Interaction diversity metrics
 */

class InteractionGraph {
  constructor() {
    // adjacency: { agent: { target: weight } }
    this.outEdges = {};  // who this agent comments on
    this.inEdges = {};   // who comments on this agent
    this.agents = new Set();
  }

  /**
   * Add an interaction: commenter commented on postAuthor's post
   */
  addInteraction(commenter, postAuthor, weight = 1) {
    if (!commenter || !postAuthor || commenter === postAuthor) return;

    this.agents.add(commenter);
    this.agents.add(postAuthor);

    if (!this.outEdges[commenter]) this.outEdges[commenter] = {};
    this.outEdges[commenter][postAuthor] = (this.outEdges[commenter][postAuthor] || 0) + weight;

    if (!this.inEdges[postAuthor]) this.inEdges[postAuthor] = {};
    this.inEdges[postAuthor][commenter] = (this.inEdges[postAuthor][commenter] || 0) + weight;
  }

  /**
   * Build graph from a batch of posts with their comments
   * @param {Array} posts - Posts with author and comments
   */
  buildFromPosts(posts) {
    for (const post of posts) {
      const postAuthor = post.author?.name;
      if (!postAuthor) continue;

      this.agents.add(postAuthor);

      for (const comment of (post.comments || [])) {
        const commenter = comment.author?.name;
        if (commenter) {
          this.addInteraction(commenter, postAuthor);
        }
      }
    }
  }

  /**
   * SybilRank - propagate trust from seed nodes
   * Reference: Cao et al. 2012, "Aiding the Detection of Fake Accounts in Large Scale Social Online Services"
   * 
   * @param {Array} seeds - Known trusted agent names
   * @param {number} iterations - Power iteration rounds (default: log2(|V|))
   * @param {number} damping - Random walk restart probability (0.85 standard)
   * @returns {Object} - { agent: trustScore }
   */
  sybilRank(seeds = [], iterations = null, damping = 0.85) {
    const nodes = [...this.agents];
    const n = nodes.length;
    if (n === 0) return {};

    // Default iterations: O(log n) for early stopping
    if (!iterations) {
      iterations = Math.max(3, Math.ceil(Math.log2(n)));
    }

    // Initialize trust: seeds get 1/|seeds|, others get 0
    const trust = {};
    const seedSet = new Set(seeds.map(s => s.toLowerCase()));

    for (const node of nodes) {
      if (seedSet.has(node.toLowerCase())) {
        trust[node] = 1.0 / Math.max(1, seeds.length);
      } else {
        trust[node] = 0;
      }
    }

    // If no seeds provided, use degree-based initialization
    // (high in-degree nodes are more likely legitimate)
    if (seeds.length === 0) {
      for (const node of nodes) {
        const inDegree = Object.keys(this.inEdges[node] || {}).length;
        trust[node] = (inDegree + 1) / (n * 2);
      }
    }

    // Power iteration
    for (let iter = 0; iter < iterations; iter++) {
      const newTrust = {};

      for (const node of nodes) {
        let incoming = 0;

        // Sum trust from incoming edges (weighted by out-degree of source)
        const inbound = this.inEdges[node] || {};
        for (const [source, weight] of Object.entries(inbound)) {
          const sourceOutDegree = Object.values(this.outEdges[source] || {})
            .reduce((a, b) => a + b, 0);
          if (sourceOutDegree > 0) {
            incoming += (trust[source] || 0) * weight / sourceOutDegree;
          }
        }

        // Damping: blend incoming trust with uniform distribution
        newTrust[node] = damping * incoming + (1 - damping) / n;
      }

      // Normalize
      const total = Object.values(newTrust).reduce((a, b) => a + b, 0);
      if (total > 0) {
        for (const node of nodes) {
          trust[node] = newTrust[node] / total;
        }
      }
    }

    // Normalize to 0-100 scale
    const maxTrust = Math.max(...Object.values(trust));
    const minTrust = Math.min(...Object.values(trust));
    const range = maxTrust - minTrust || 1;

    const scores = {};
    for (const node of nodes) {
      scores[node] = Math.round(((trust[node] - minTrust) / range) * 100);
    }

    return scores;
  }

  /**
   * Detect reciprocal comment rings
   * A -> B and B -> A with similar weights suggests coordination
   */
  findReciprocals(minWeight = 2) {
    const rings = [];

    for (const [a, targets] of Object.entries(this.outEdges)) {
      for (const [b, weightAB] of Object.entries(targets)) {
        if (weightAB < minWeight) continue;
        const weightBA = this.outEdges[b]?.[a] || 0;
        if (weightBA >= minWeight) {
          // Only add each pair once
          if (a < b) {
            rings.push({
              agents: [a, b],
              weightAB,
              weightBA,
              symmetry: Math.min(weightAB, weightBA) / Math.max(weightAB, weightBA)
            });
          }
        }
      }
    }

    return rings.sort((a, b) => b.symmetry - a.symmetry);
  }

  /**
   * Interaction diversity for a specific agent
   * How many unique agents do they interact with, vs total interactions?
   */
  diversity(agentName) {
    const out = this.outEdges[agentName] || {};
    const inbound = this.inEdges[agentName] || {};

    const uniqueOut = Object.keys(out).length;
    const totalOut = Object.values(out).reduce((a, b) => a + b, 0);

    const uniqueIn = Object.keys(inbound).length;
    const totalIn = Object.values(inbound).reduce((a, b) => a + b, 0);

    // Gini coefficient of interaction distribution (0 = even, 1 = concentrated)
    const outWeights = Object.values(out).sort((a, b) => a - b);
    const gini = this._gini(outWeights);

    return {
      uniqueOutgoing: uniqueOut,
      totalOutgoing: totalOut,
      uniqueIncoming: uniqueIn,
      totalIncoming: totalIn,
      outgoingConcentration: gini,
      diversityScore: Math.round(
        (uniqueOut > 0 ? Math.min(1, uniqueOut / 10) : 0) * 50 +
        (uniqueIn > 0 ? Math.min(1, uniqueIn / 10) : 0) * 30 +
        (1 - gini) * 20
      ),
    };
  }

  _gini(sorted) {
    if (sorted.length === 0) return 0;
    const n = sorted.length;
    const total = sorted.reduce((a, b) => a + b, 0);
    if (total === 0) return 0;

    let num = 0;
    for (let i = 0; i < n; i++) {
      num += (2 * (i + 1) - n - 1) * sorted[i];
    }
    return num / (n * total);
  }

  /**
   * Get graph statistics
   */
  stats() {
    const nodes = this.agents.size;
    let edges = 0;
    let totalWeight = 0;

    for (const targets of Object.values(this.outEdges)) {
      for (const w of Object.values(targets)) {
        edges++;
        totalWeight += w;
      }
    }

    return {
      nodes,
      edges,
      totalWeight,
      density: nodes > 1 ? edges / (nodes * (nodes - 1)) : 0,
      avgDegree: nodes > 0 ? Math.round(edges / nodes * 10) / 10 : 0,
    };
  }
}

module.exports = { InteractionGraph };
