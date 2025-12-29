from __future__ import annotations

from typing import List

from app.models import NewsArticle
from app.services.llm import LlmClient

async def curate_news(
    ticker: str, articles: List[NewsArticle], limit: int
) -> List[NewsArticle]:
    llm = LlmClient()
    ranked = await llm.rerank_and_filter(ticker, articles, limit=limit)
    return ranked

async def summarize_news(ticker: str, articles: List[NewsArticle]) -> str:
    llm = LlmClient()
    return await llm.summarize(ticker, articles)


def score_article_match(ticker: str, title: str, summary: str) -> float:
    text = f"{title} {summary}".lower()
    ticker = ticker.lower()
    if not text.strip():
        return 0.0
    return 1.0 if ticker in text else 0.3
