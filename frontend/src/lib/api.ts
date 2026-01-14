import type { NewsResponse, PriceRange, PricesResponse } from "./types";

// Relative base for the backend API.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api/v1";

function normalizeAlphaVantageError(message: string): string {
  if (message.includes("Alpha Vantage error:")) {
    if (message.includes("Invalid API call")) {
      return "Invalid ticker. Please check the symbol and try again.";
    }
    if (message.includes("Thank you for using Alpha Vantage")) {
      return "Rate limit reached. Please wait a moment and try again.";
    }
  }
  return message;
}

async function readErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const data = (await response.json()) as { detail?: string };
    return data.detail ? normalizeAlphaVantageError(data.detail) : fallback;
  } catch {
    return fallback;
  }
}

export async function fetchPrices(ticker: string, range: PriceRange): Promise<PricesResponse> {
  const response = await fetch(`${API_BASE}/prices?ticker=${ticker}&range=${range}`);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to load prices"));
  }
  return response.json();
}

export async function fetchNews(ticker: string): Promise<NewsResponse> {
  const response = await fetch(`${API_BASE}/news?ticker=${ticker}`);
  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Failed to load news"));
  }
  return response.json();
}

