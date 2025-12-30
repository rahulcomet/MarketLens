from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.models import (
    AskRequest,
    AskResponse,
    HealthResponse,
    NewsResponse,
    PriceRange,
    PricesResponse,
)
from app.services.alpha_vantage import AlphaVantageClient
from app.services.llm import LlmClient
from app.services.news import curate_news, summarize_news

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")

@router.get("/prices", response_model=PricesResponse)
async def get_prices(
    ticker: str = Query(..., min_length=1, max_length=10),
    range: PriceRange = Query(PriceRange.ONE_MONTH, alias="range"),
) -> PricesResponse:
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

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    client = AlphaVantageClient()
    llm = LlmClient()

    try:
        prices = await client.fetch_prices(request.ticker, request.range)
        raw_articles = await client.fetch_news(request.ticker)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    curated = await curate_news(request.ticker, raw_articles, limit=5)
    try:
        answer = await llm.answer_question(request, prices, curated)
    except Exception:
        # Return a safe fallback if the LLM fails.
        answer = None

    return AskResponse(
        ticker=request.ticker.upper(),
        question=request.question,
        answer=answer.text if answer else "Answer temporarily unavailable. Please try again.",
        sources=answer.sources if answer else [article.url for article in curated if article.url][:3],
    )
