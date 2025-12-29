import type { AskRequest, AskResponse, NewsResponse, PriceRange, PricesResponse } from "./types";

const API_BASE = "/api/v1";

export async function fetchPrices(ticker: string, range: PriceRange): Promise<PricesResponse> {
  const response = await fetch(`${API_BASE}/prices?ticker=${ticker}&range=${range}`);
  if (!response.ok) {
    throw new Error("Failed to load prices");
  }
  return response.json();
}

export async function fetchNews(ticker: string): Promise<NewsResponse> {
  const response = await fetch(`${API_BASE}/news?ticker=${ticker}`);
  if (!response.ok) {
    throw new Error("Failed to load news");
  }
  return response.json();
}

export async function askQuestion(payload: AskRequest): Promise<AskResponse> {
  const response = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to get answer");
  }
  return response.json();
}
