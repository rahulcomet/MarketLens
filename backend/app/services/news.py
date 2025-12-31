from __future__ import annotations

"""News curation helpers and simple relevance scoring."""

from typing import List

from app.models import NewsArticle
from app.services.llm import LlmClient

async def curate_news(
    ticker: str, articles: List[NewsArticle], limit: int
) -> List[NewsArticle]:
    """Rank and trim articles using the LLM client."""
    llm = LlmClient()
    ranked = await llm.rerank_and_filter(ticker, articles, limit=limit)
    return ranked

async def summarize_news(ticker: str, articles: List[NewsArticle]) -> str:
    """Summarize a set of curated articles."""
    try:
        llm = LlmClient()
        return await llm.summarize(ticker, articles)
    except Exception:
        # Fall back when the LLM is unavailable or misconfigured.
        if not articles:
            return f"No high-confidence news found for {ticker.upper()}."
        return f"Top {ticker.upper()} headlines summarized."


def score_article_match(ticker: str, title: str, summary: str) -> float:
    """Heuristic relevance score based on ticker mentions."""
    text = f"{title} {summary}".lower()
    ticker = ticker.lower()
    if not text.strip():
        return 0.0
    return 1.0 if ticker in text else 0.3
