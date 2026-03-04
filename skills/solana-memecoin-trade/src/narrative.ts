import fs from "node:fs";
import YAML from "yaml";
import { logger } from "./logger.js";
import { XStreamEvent } from "./providers/xFilteredStream.js";

export type Narrative = {
  id: string;
  description?: string;
  x_rules?: string[];
  keywords?: string[];
  mints?: string[];
  boost?: { score_bonus?: number };
};

export type NarrativeConfig = { narratives: Narrative[] };
export type HotMint = { mint: string; hypeScore: number; reasons: string[]; lastSeenTs: number };

export function loadNarratives(path = "config/narratives.yaml"): NarrativeConfig {
  const raw = fs.readFileSync(path, "utf-8");
  return (YAML.parse(raw) || { narratives: [] }) as NarrativeConfig;
}

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/https?:\/\/\S+/g, " ")
    .replace(/[^a-z0-9$#_\s]/g, " ")
    .split(/\s+/)
    .filter(Boolean);
}

function baseHypeFromMetrics(m: any): number {
  const like = Number(m?.like_count || 0);
  const rt = Number(m?.repost_count || m?.retweet_count || 0);
  const reply = Number(m?.reply_count || 0);
  const quote = Number(m?.quote_count || 0);
  const raw = like + 2 * rt + 1.5 * reply + 2 * quote;
  return Math.round(Math.min(25, Math.log10(1 + raw) * 10));
}

export class NarrativeTracker {
  private hot = new Map<string, HotMint>();

  constructor(private cfg: any, private narratives: Narrative[]) {}

  ingestX(e: XStreamEvent) {
    const text = e.text || "";
    const tokens = tokenize(text);
    if (!tokens.length) return;

    const base = baseHypeFromMetrics(e.public_metrics || {});

    for (const n of this.narratives) {
      const kws = (n.keywords || []).map(k => k.toLowerCase());
      const hit = kws.some(k => tokens.includes(k) || text.toLowerCase().includes(k));
      if (!hit) continue;

      const bonus = n.boost?.score_bonus ?? 0;
      const hype = base + 5 + bonus;

      for (const mint of (n.mints || [])) {
        if (!mint) continue;
        const prev = this.hot.get(mint);
        const reason = `X:${n.id}`;
        const reasons = prev?.reasons || [];
        const next: HotMint = {
          mint,
          hypeScore: Math.min(100, (prev?.hypeScore || 0) + hype),
          reasons: reasons.includes(reason) ? reasons : [...reasons, reason],
          lastSeenTs: Date.now(),
        };
        this.hot.set(mint, next);
        logger.info({ mint, hypeScore: next.hypeScore, reason }, "Narrative HOT mint updated");
      }
    }
  }

  getHotMints(): HotMint[] {
    const winMin = this.cfg.narrative?.scoring?.hot_window_minutes ?? 60;
    const minScore = this.cfg.narrative?.scoring?.min_hype_score ?? 10;
    const cutoff = Date.now() - winMin * 60_000;

    const out: HotMint[] = [];
    for (const v of this.hot.values()) {
      if (v.lastSeenTs < cutoff) continue;
      if (v.hypeScore < minScore) continue;
      out.push(v);
    }
    out.sort((a, b) => b.hypeScore - a.hypeScore);
    const cap = this.cfg.narrative?.scoring?.max_hot_mints ?? 20;
    return out.slice(0, cap);
  }
}
