from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import List

import httpx

from app.models import NewsArticle, PricePoint, PriceRange
from app.services.env_utils import read_env_key
from app.services.news import score_article_match

class AlphaVantageClient:
    def __init__(self) -> None:
        self.api_key = os.getenv("ALPHAVANTAGE_API_KEY", "").strip()
        if not self.api_key:
            self.api_key = (read_env_key("ALPHAVANTAGE_API_KEY") or "").strip()
        if not self.api_key:
            raise ValueError("Missing ALPHAVANTAGE_API_KEY")

    async def fetch_prices(self, ticker: str, range: PriceRange) -> List[PricePoint]:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": ticker.upper(),
            "outputsize": "compact",
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://www.alphavantage.co/query", params=params)
        data = _parse_alpha_response(response)
        series = data.get("Time Series (Daily)")
        if not series:
            raise ValueError("Alpha Vantage returned no time series data")

        cutoff = _range_cutoff(range)
        points: List[PricePoint] = []
        for day, values in series.items():
            day_date = datetime.strptime(day, "%Y-%m-%d").date()
            if day_date < cutoff:
                continue
            points.append(
                PricePoint(
                    date=day_date,
                    open=float(values.get("1. open", 0)),
                    high=float(values.get("2. high", 0)),
                    low=float(values.get("3. low", 0)),
                    close=float(values.get("4. close", 0)),
                    volume=int(float(values.get("5. volume", 0))),
                )
            )

        points.sort(key=lambda item: item.date)
        return points

    async def fetch_news(self, ticker: str) -> List[NewsArticle]:
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": ticker.upper(),
            "limit": "50",
            "apikey": self.api_key,
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get("https://www.alphavantage.co/query", params=params)
        data = _parse_alpha_response(response)
        feed = data.get("feed")
        if not feed:
            raise ValueError("Alpha Vantage returned no news data")

        articles: List[NewsArticle] = []
        for item in feed:
            title = item.get("title", "").strip()
            url = item.get("url", "").strip()
            summary = item.get("summary", "").strip()
            relevance = score_article_match(ticker, title, summary)
            articles.append(
                NewsArticle(
                    title=title,
                    url=url,
                    source=item.get("source"),
                    published_at=item.get("time_published"),
                    summary=summary,
                    relevance_score=relevance,
                    relevance_reason="Keyword match score",
                )
            )

        return articles


def _range_cutoff(range: PriceRange) -> datetime.date:
    today = datetime.utcnow().date()
    if range == PriceRange.ONE_WEEK:
        return today - timedelta(days=7)
    if range == PriceRange.ONE_MONTH:
        return today - timedelta(days=31)
    if range == PriceRange.ONE_HUNDRED_DAYS:
        return today - timedelta(days=100)
    return today - timedelta(days=31)


def _parse_alpha_response(response: httpx.Response) -> dict:
    try:
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError(f"Alpha Vantage request failed: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ValueError("Alpha Vantage returned invalid JSON") from exc

    for key in ("Error Message", "Note", "Information"):
        message = data.get(key)
        if message:
            raise ValueError(f"Alpha Vantage error: {message}")

    return data
