from __future__ import annotations

"""Pydantic models and enums for API requests/responses."""

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str

class PriceRange(str, Enum):
    """Supported ranges for price queries."""
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"
    ONE_HUNDRED_DAYS = "100D"

class PricePoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

class PricesResponse(BaseModel):
    ticker: str
    range: PriceRange
    points: List[PricePoint]

class NewsArticle(BaseModel):
    """Normalized news article with relevance metadata."""
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    summary: Optional[str] = None
    relevance_score: float = Field(ge=0, le=1)
    relevance_reason: Optional[str] = None

class NewsResponse(BaseModel):
    ticker: str
    summary: str
    articles: List[NewsArticle]

