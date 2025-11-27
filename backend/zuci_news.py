"""
Zuci News Module
Handles creation, retrieval, and management of Zuci company news
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import logging

from login import User, get_current_user

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["zuci-news"])

# Database reference - will be set from server.py
db = None

def set_db(database):
    global db
    db = database

# ============== MODELS ==============

class ZuciNewsCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    published_date: str  # ISO format date string
    news_link: Optional[str] = None  # URL to the news article/announcement

class ZuciNewsUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = Field(None, min_length=1)
    published_date: Optional[str] = None
    news_link: Optional[str] = None

class ZuciNews(BaseModel):
    id: str
    title: str
    description: str
    published_date: str
    news_link: Optional[str] = None
    created_by: str
    created_at: str
    updated_at: str

# ============== ROUTES ==============

@router.post("/zuci-news", response_model=ZuciNews)
async def create_zuci_news(news_data: ZuciNewsCreate, current_user: User = Depends(get_current_user)):
    """Create a new Zuci news entry"""
    news = {
        "id": str(uuid.uuid4()),
        "title": news_data.title,
        "description": news_data.description,
        "published_date": news_data.published_date,
        "news_link": news_data.news_link,
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.zuci_news.insert_one(news)
    logger.info(f"Created Zuci news: {news['title']}")

    return news

@router.get("/zuci-news", response_model=List[ZuciNews])
async def get_all_zuci_news(current_user: User = Depends(get_current_user)):
    """Get all Zuci news entries, sorted by published_date descending"""
    news_items = await db.zuci_news.find(
        {},
        {"_id": 0}
    ).sort("published_date", -1).to_list(None)

    return news_items

@router.get("/zuci-news/{news_id}", response_model=ZuciNews)
async def get_zuci_news(news_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific Zuci news entry"""
    news = await db.zuci_news.find_one({"id": news_id}, {"_id": 0})

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news

@router.put("/zuci-news/{news_id}", response_model=ZuciNews)
async def update_zuci_news(
    news_id: str,
    news_data: ZuciNewsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a Zuci news entry"""
    existing_news = await db.zuci_news.find_one({"id": news_id}, {"_id": 0})

    if not existing_news:
        raise HTTPException(status_code=404, detail="News not found")

    # Build update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

    if news_data.title is not None:
        update_data["title"] = news_data.title
    if news_data.description is not None:
        update_data["description"] = news_data.description
    if news_data.published_date is not None:
        update_data["published_date"] = news_data.published_date
    if news_data.news_link is not None:
        update_data["news_link"] = news_data.news_link

    await db.zuci_news.update_one(
        {"id": news_id},
        {"$set": update_data}
    )

    # Fetch updated document
    updated_news = await db.zuci_news.find_one({"id": news_id}, {"_id": 0})
    logger.info(f"Updated Zuci news: {updated_news['title']}")

    return updated_news

@router.delete("/zuci-news/{news_id}")
async def delete_zuci_news(news_id: str, current_user: User = Depends(get_current_user)):
    """Delete a Zuci news entry"""
    result = await db.zuci_news.delete_one({"id": news_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="News not found")

    logger.info(f"Deleted Zuci news: {news_id}")
    return {"message": "News deleted successfully"}
