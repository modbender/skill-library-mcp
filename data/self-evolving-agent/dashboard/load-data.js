/**
 * load-data.js — Data loader for SEA Dashboard
 *
 * Reads data-index.json (built by build-index.sh), then fetches
 * each proposal JSON file and normalizes the data for the charts.
 *
 * Exported API (attached to window.SEAData):
 *   loadAll()        → Promise<DashboardData>
 *   formatDate(str)  → "Feb 18"
 *   severityRank(s)  → number (for sorting)
 */

(function (global) {
  'use strict';

  // ── Helpers ──────────────────────────────────────────────────

  function formatDate(isoStr) {
    if (!isoStr) return '—';
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' });
  }

  function severityRank(s) {
    return { critical: 4, high: 3, medium: 2, low: 1, info: 0 }[s] ?? 0;
  }

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  // ── Core loader ──────────────────────────────────────────────

  async function loadAll() {
    // 1. Fetch index
    let index;
    try {
      const r = await fetch('./data-index.json');
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      index = await r.json();
    } catch (e) {
      console.warn('[SEAData] data-index.json missing or invalid:', e.message);
      return buildEmpty('Run build-index.sh first, then restart the server.');
    }

    if (!index.files || index.files.length === 0) {
      return buildEmpty('No proposal files found in data/proposals/.');
    }

    // 2. Fetch each proposal file (parallel, best-effort)
    const results = await Promise.allSettled(
      index.files.map(path =>
        fetch(path)
          .then(r => { if (!r.ok) throw new Error(`HTTP ${r.status}`); return r.json(); })
          .catch(e => { console.warn('[SEAData] Failed to load', path, e.message); return null; })
      )
    );

    const proposals = results
      .map(r => (r.status === 'fulfilled' ? r.value : null))
      .filter(Boolean)
      .sort((a, b) => new Date(a.generated_at) - new Date(b.generated_at));

    return buildDashboardData(proposals);
  }

  // ── Data builder ─────────────────────────────────────────────

  function buildEmpty(reason) {
    return {
      empty: true,
      reason,
      qualityTrend: [],
      proposalHistory: [],
      patternFrequency: {},
      rulesEffectiveness: [],
      agentsMdHealth: null,
    };
  }

  function buildDashboardData(proposals) {
    // ── 1. Quality Trend ────────────────────────────────────────
    const qualityTrend = proposals
      .filter(p => p.quality_score != null)
      .map(p => ({
        date: p.generated_at,
        dateLabel: formatDate(p.week_end || p.generated_at),
        score: p.quality_score,
        sessions: p.sessions_analyzed,
        status: p.status,
      }));

    // ── 2. Proposal History (flat list of all sub-proposals) ────
    const proposalHistory = [];
    for (const p of proposals) {
      const weekLabel = p.week_end
        ? `${formatDate(p.week_start)} – ${formatDate(p.week_end)}`
        : formatDate(p.generated_at);

      for (const sub of p.proposals || []) {
        proposalHistory.push({
          parentId: p.id,
          id: sub.id,
          title: sub.title,
          severity: sub.severity,
          status: p.status,       // applied / rejected / pending
          date: p.generated_at,
          dateLabel: weekLabel,
          effect: sub.effect,
          effectDelta: sub.effect_delta,
          evidence: sub.evidence,
        });
      }
    }
    // Most recent first
    proposalHistory.sort((a, b) => new Date(b.date) - new Date(a.date));

    // ── 3. Pattern Frequency ────────────────────────────────────
    // Merge pattern_frequencies across all proposals, keyed by date
    const patternKeys = new Set();
    const patternByDate = proposals
      .filter(p => p.pattern_frequencies)
      .map(p => {
        const pf = p.pattern_frequencies;
        Object.keys(pf).forEach(k => patternKeys.add(k));
        return { dateLabel: formatDate(p.week_end || p.generated_at), patterns: pf };
      });

    const patternFrequency = {
      dates: patternByDate.map(p => p.dateLabel),
      keys: Array.from(patternKeys),
      series: patternByDate.map(p => p.patterns),
    };

    // ── 4. Rules Effectiveness ──────────────────────────────────
    const rulesEffectiveness = [];
    for (const p of proposals) {
      for (const sub of p.proposals || []) {
        if (sub.effect === null) continue; // pending — no measurement yet
        rulesEffectiveness.push({
          id: sub.id,
          title: sub.title,
          severity: sub.severity,
          effect: sub.effect,         // "effective" | "neutral" | "regressed"
          delta: sub.effect_delta,
          before: sub.pattern_hits_before,
          after: sub.pattern_hits_after,
          date: p.generated_at,
          dateLabel: formatDate(p.week_end || p.generated_at),
        });
      }
    }
    rulesEffectiveness.sort((a, b) => new Date(b.date) - new Date(a.date));

    // ── 5. AGENTS.md Health ─────────────────────────────────────
    // Latest benchmark
    const withBench = proposals.filter(p => p.benchmarks?.agents_md_score != null);
    const latestBench = withBench.length > 0 ? withBench[withBench.length - 1].benchmarks : null;

    const agentsMdHealth = latestBench ? {
      score: latestBench.agents_md_score,
      label: latestBench.agents_md_label,
      missingSections: latestBench.missing_sections || [],
      githubStatus: latestBench.github_status,
      clawHubStatus: latestBench.clawhub_status,
      history: withBench.map(p => ({
        dateLabel: formatDate(p.week_end || p.generated_at),
        score: p.benchmarks.agents_md_score,
      })),
    } : null;

    // ── 6. Summary stats ────────────────────────────────────────
    const stats = {
      totalProposals: proposalHistory.length,
      applied: proposalHistory.filter(p => p.status === 'applied').length,
      rejected: proposalHistory.filter(p => p.status === 'rejected').length,
      pending: proposalHistory.filter(p => p.status === 'pending').length,
      effective: rulesEffectiveness.filter(r => r.effect === 'effective').length,
      neutral: rulesEffectiveness.filter(r => r.effect === 'neutral').length,
      regressed: rulesEffectiveness.filter(r => r.effect === 'regressed').length,
      latestScore: qualityTrend.length > 0 ? qualityTrend[qualityTrend.length - 1].score : null,
    };

    return {
      empty: false,
      qualityTrend,
      proposalHistory,
      patternFrequency,
      rulesEffectiveness,
      agentsMdHealth,
      stats,
      raw: proposals,
    };
  }

  // ── Export ───────────────────────────────────────────────────

  global.SEAData = {
    loadAll,
    formatDate,
    severityRank,
    clamp,
  };

})(window);
