from __future__ import annotations

"""LLM client wrapper for summarization."""

import asyncio
import os
from typing import List

import google.generativeai as genai

from app.models import NewsArticle
from app.services.env_utils import read_env_key

class LlmClient:
    """Wraps Gemini API calls and prompt composition."""
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
        """Run a prompt against the model in a thread."""
        def _call() -> str:
            try:
                response = self.model.generate_content(prompt)
            except Exception as exc:
                raise ValueError(f"Gemini request failed: {exc}") from exc
            return response.text or ""

        return await asyncio.to_thread(_call)

    async def rerank_and_filter(
        self, ticker: str, articles: List[NewsArticle], limit: int
    ) -> List[NewsArticle]:
        """Order articles by heuristic relevance and trim."""
        # Keep the heuristic ranking for now to avoid extra latency/cost.
        ranked = sorted(articles, key=lambda item: item.relevance_score, reverse=True)
        return ranked[:limit]

    async def summarize(self, ticker: str, articles: List[NewsArticle]) -> str:
        """Summarize curated headlines for a ticker."""
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

