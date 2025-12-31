from __future__ import annotations

"""API route handlers for prices and news."""

from fastapi import APIRouter, HTTPException, Query

from app.models import HealthResponse, NewsResponse, PriceRange, PricesResponse
from app.services.alpha_vantage import AlphaVantageClient
from app.services.news import curate_news, summarize_news

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Lightweight health check for uptime monitoring."""
    return HealthResponse(status="ok")

@router.get("/prices", response_model=PricesResponse)
async def get_prices(
    ticker: str = Query(..., min_length=1, max_length=10),
    range: PriceRange = Query(PriceRange.ONE_MONTH, alias="range"),
) -> PricesResponse:
    """Fetch daily price series for a ticker within a range."""
    client = AlphaVantageClient()
    try:
        points = await client.fetch_prices(ticker, range)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return PricesResponse(
        ticker=ticker.upper(),
        range=range,
        points=points,
    )

@router.get("/news", response_model=NewsResponse)
async def get_news(
    ticker: str = Query(..., min_length=1, max_length=10),
    limit: int = Query(3, ge=1, le=10),
) -> NewsResponse:
    """Fetch and summarize curated news for a ticker."""
    client = AlphaVantageClient()
    try:
        raw_articles = await client.fetch_news(ticker)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    curated = await curate_news(ticker, raw_articles, limit=limit)
    summary = await summarize_news(ticker, curated)

    return NewsResponse(
        ticker=ticker.upper(),
        summary=summary,
        articles=curated,
    )

