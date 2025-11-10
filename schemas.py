"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogpost" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Pressrelease(BaseModel):
    """
    Company press releases aggregated from trusted sources.
    Collection name: "pressrelease"
    """
    source: str = Field(..., description="Source site name")
    title: str = Field(..., description="Press release headline")
    url: str = Field(..., description="Canonical link to the press release")
    published_at: Optional[datetime] = Field(None, description="UTC datetime the article was published")
    summary: Optional[str] = Field(None, description="Short summary or description")
    ticker: Optional[str] = Field(None, description="Detected stock ticker symbol, if any")
    exchange: Optional[str] = Field(None, description="Detected exchange such as NASDAQ, NYSE")
    sentiment: Optional[str] = Field(None, description="negative | neutral | positive")
    sentiment_score: Optional[float] = Field(None, description="Score in [-1,1]")

class Signal(BaseModel):
    """
    Trading signal inferred from a press release sentiment.
    Collection name: "signal"
    """
    ticker: str = Field(..., description="Ticker symbol, e.g., AAPL")
    action: str = Field(..., description="buy | hold | sell")
    confidence: float = Field(..., ge=0, le=1, description="0..1 confidence score")
    reason: str = Field(..., description="Short explanation of why the signal was generated")
    source_title: str = Field(..., description="Related press release title")
    source_url: str = Field(..., description="Related press release URL")
    published_at: Optional[datetime] = Field(None, description="UTC datetime of the press release")
    sentiment_score: float = Field(..., description="Underlying sentiment score in [-1,1]")
    sentiment_label: str = Field(..., description="negative | neutral | positive")

# Example schemas kept for reference; not used by the app but safe to keep
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
