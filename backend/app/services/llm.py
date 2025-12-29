from __future__ import annotations

import asyncio
import os
from typing import List

import google.generativeai as genai

from app.models import AskAnswer, AskRequest, NewsArticle, PricePoint
from app.services.env_utils import read_env_key

class LlmClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            self.api_key = (read_env_key("GEMINI_API_KEY") or "").strip()
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY")
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    async def _generate(self, prompt: str) -> str:
        def _call() -> str:
            response = self.model.generate_content(prompt)
            return response.text or ""

        return await asyncio.to_thread(_call)

    async def rerank_and_filter(
        self, ticker: str, articles: List[NewsArticle], limit: int
    ) -> List[NewsArticle]:
        # Keep the heuristic ranking for now to avoid extra latency/cost.
        ranked = sorted(articles, key=lambda item: item.relevance_score, reverse=True)
        return ranked[:limit]

    async def summarize(self, ticker: str, articles: List[NewsArticle]) -> str:
        if not articles:
            return f"No high-confidence news found for {ticker.upper()}."
        items = "\n".join(
            f"- {article.title}: {article.summary or 'No summary provided.'}"
            for article in articles[:5]
        )
        prompt = (
            "Summarize the most important themes in these news headlines and summaries "
            f"for {ticker.upper()} in 2-3 sentences.\n\n{items}"
        )
        text = await self._generate(prompt)
        return text.strip() or f"Top {ticker.upper()} headlines summarized."

    async def answer_question(
        self, request: AskRequest, prices: List[PricePoint], articles: List[NewsArticle]
    ) -> AskAnswer:
        sources = [article.url for article in articles if article.url][:3]
        if not prices:
            return AskAnswer(
                text="I couldn't retrieve recent price data. Please try again later.",
                sources=sources,
            )
        latest = prices[-1]
        headlines = "\n".join(
            f"- {article.title} ({article.url})" for article in articles[:5]
        )
        prompt = (
            "You are a helpful market assistant. Answer the user's question briefly "
            "using the latest price and the headlines provided. If data is missing, "
            "say so. Provide a concise answer in 2-4 sentences.\n\n"
            f"Question: {request.question}\n"
            f"Latest close: {latest.close:.2f} on {latest.date}\n"
            f"Headlines:\n{headlines}"
        )
        text = await self._generate(prompt)
        cleaned = text.strip()
        text = cleaned or (
            f"Latest close is {latest.close:.2f} on {latest.date}. "
            "No additional context available."
        )
        return AskAnswer(text=text, sources=sources)
