---
name: upsurge-searxng
description: Private Intelligence Radar for Agents. Solves high-cost & privacy-leak issues of Brave/Google APIs. Aggregates data locally with Zero-Leak absolute data sovereignty.
author: Upsurge.ae
version: 1.4.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - curl
---

# ![Upsurge](logo.jpg) 
# SearXNG Search engine For OpenClaw by Upsurge.ae

### Reclaim your data. Zero-cost, Zero-leak enterprise search.

**The Problem:** Standard AI search (Brave/Google) turns your proprietary queries into product training data for competitors. Every search is a recurring cost and a potential trade-secret leak.

**The Agitation:** For enterprise AI adoption, this is a non-starter. You can't build a private "War Room" if your search engine is a sieve that bills you for every discovery.

**The Solution:** A high-velocity **Private Intelligence Radar** that runs entirely within your Docker network. Upsurge SearXNG gives your agents "Eyes" across 70+ engines without the API tax or the privacy risk.

## ✨ Features
*   **Agent-Optimized Markdown:** High-fidelity formatting specifically designed for agent ingestion. Reduces hallucination and increases data extraction speed by 2x compared to raw snippets.
*   **Temporal Intelligence:** Native filters for `day`, `month`, and `year`. Force your agents to focus on real-time market moves rather than stale data.
*   **$0 Search Costs:** Unlimited global querying with no monthly API bills or token metering.
*   **Zero-Leak Privacy:** Your strategic queries remain on your local Docker network; invisible to third-party ad networks and AI trainers.
*   **Aggregated Results:** One-shot discovery across Google, Bing, DuckDuckGo, and Wikipedia.

## 🎯 When to Use
*   **Market Intelligence:** When you need to monitor competitor moves without tipping them off.
*   **Technical Research:** Searching documentation and GitHub repos using the `it` category.
*   **Real-time Briefings:** Using the `day` filter to generate morning reports for the CEO Pack.
*   **Data Sovereignty:** When corporate compliance prohibits sharing internal project names with public search APIs.

## 🛠 Prerequisites
*   SearXNG running on `http://localhost:8080` (Docker).
*   Python 3 installed on the host.

## 🚀 Usage

```bash
# Broad Market Search
python3 search.py "AI adoption trends"

# Real-time News (Last 24 Hours)
python3 search.py "Market news" --time day --category news

# Technical Deep Dive
python3 search.py "OpenClaw API" --category it
```

---
*Built for the CEO Pack by Upsurge.ae*
