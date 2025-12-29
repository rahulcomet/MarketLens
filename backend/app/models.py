from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str

class PriceRange(str, Enum):
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

class AskRequest(BaseModel):
    ticker: str = Field(min_length=1, max_length=10)
    range: PriceRange = PriceRange.ONE_MONTH
    question: str = Field(min_length=5, max_length=500)

class AskAnswer(BaseModel):
    text: str
    sources: List[str]

class AskResponse(BaseModel):
    ticker: str
    question: str
    answer: str
    sources: List[str]
