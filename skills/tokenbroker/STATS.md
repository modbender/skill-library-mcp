# STATS.md - Builder Reputation System

**Trust but verify. Analyze the builder behind the token.**

This module defines how to fetch and display reputation metrics for a wallet address or project owner. This increases trust for potential buyers.

## Metrics to Track

| Metric | Description | Why it matters |
| :--- | :--- | :--- |
| **Total Launches** | Number of tokens created by the agent via nad.fun. | Experience level |
| **Graduation Rate** | Percentage of launched tokens that successfully migrate to Uniswap V3. | Success track record |
| **Total Volume** | Cumulative trading volume across all tokens launched by this agent. | Market interest |
| **Trust Score** | Multi-factor metric based on historical performance. | Overall reliability and success |

## Data Sources

1.  **On-Chain Events**: Query `BondingCurveRouter` logs for `CurveCreate` events indexed by `creator`.
2.  **NadFun API**: User profile stats (points, rank).
3.  **Local History**: `.tokenbroker/history.json` (if available for local backtests).

## Agent Instructions

When asked "Is this builder trustworthy?" or "Show builder stats":

1.  **Identify Address**: Get the `creator` address from the user or current wallet.
2.  **Fetch Data**:
    *   Query Indexer or scan logs.
    *   *Mock Data (for Hackathon Demo)*: Use the `getBuilderStats` mock function.
3.  **Calculate Score**:
    *   `Score = (Graduations * 10) + (Launches * 2)`
4.  **Report**:

> **Builder Report: 0x123...**
> 🦞 **Trust Score**: 85/100
> *   🚀 **Launches**: 5
> *   🎓 **Graduated**: 3 (60%)
> *   💰 **Total Vol**: 42,000 MON
>
> *Verdict: Experienced builder with a solid track record.*
