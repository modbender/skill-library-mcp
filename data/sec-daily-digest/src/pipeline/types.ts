import type { Article } from "../rss/parse";

export type CategoryId = "ai-ml" | "security" | "engineering" | "tools" | "opinion" | "other";

export interface ScoringResultItem {
  index: number;
  relevance: number;
  quality: number;
  timeliness: number;
  security: number;
  ai: number;
  category: CategoryId;
  keywords: string[];
}

export interface SummaryResultItem {
  index: number;
  titleZh: string;
  summaryZh: string;
  reasonZh: string;
}

export interface ScoredArticle extends Article, ScoringResultItem {
  score: number;
}

export interface FinalArticle extends ScoredArticle, SummaryResultItem {}
