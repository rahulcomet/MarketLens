export type PriceRange = "1W" | "1M" | "100D";

export interface PricePoint {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PricesResponse {
  ticker: string;
  range: PriceRange;
  points: PricePoint[];
}

export interface NewsArticle {
  title: string;
  url: string;
  source?: string | null;
  published_at?: string | null;
  summary?: string | null;
  relevance_score: number;
  relevance_reason?: string | null;
}

export interface NewsResponse {
  ticker: string;
  summary: string;
  articles: NewsArticle[];
}

