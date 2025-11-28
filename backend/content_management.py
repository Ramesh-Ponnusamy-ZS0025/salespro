"""
Content Management Module
Handles Zuci Wins and GTM entries
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid
import logging

from login import User, get_current_user

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["content-management"])

# Database reference - will be set from server.py
db = None

def set_db(database):
    global db
    db = database

# ============== ZUCI WINS MODELS ==============

class Contributor(BaseModel):
    name: str
    email: str
    designation: str

class ZuciWinCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=500)
    description: str = Field(..., min_length=1)
    win_date: str  # ISO format date string
    contributions: List[Contributor] = []

class ZuciWinUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    win_date: Optional[str] = None
    contributions: Optional[List[Contributor]] = None

class ZuciWin(BaseModel):
    id: str
    company_name: str
    description: str
    win_date: str
    contributions: List[Contributor]
    created_by: str
    created_at: str
    updated_at: str

# ============== GTM MODELS ==============

class GTMEntryCreate(BaseModel):
    gtm_link: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    prospect_name: str = Field(..., min_length=1, max_length=500)
    date: str  # ISO format date string

class GTMEntryUpdate(BaseModel):
    gtm_link: Optional[str] = None
    description: Optional[str] = None
    prospect_name: Optional[str] = None
    date: Optional[str] = None

class GTMEntry(BaseModel):
    id: str
    gtm_link: str
    description: str
    prospect_name: str
    date: str
    created_by: str
    created_at: str
    updated_at: str

# ============== ZUCI WINS ROUTES ==============

@router.post("/zuci-wins", response_model=ZuciWin)
async def create_zuci_win(win_data: ZuciWinCreate, current_user: User = Depends(get_current_user)):
    """Create a new Zuci Win entry"""
    win = {
        "id": str(uuid.uuid4()),
        "company_name": win_data.company_name,
        "description": win_data.description,
        "win_date": win_data.win_date,
        "contributions": [c.model_dump() for c in win_data.contributions],
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.zuci_wins.insert_one(win)
    logger.info(f"Created Zuci Win: {win['company_name']}")

    return win

@router.get("/zuci-wins", response_model=List[ZuciWin])
async def get_all_zuci_wins(current_user: User = Depends(get_current_user)):
    """Get all Zuci Win entries, sorted by win_date descending"""
    wins = await db.zuci_wins.find(
        {},
        {"_id": 0}
    ).sort("win_date", -1).to_list(None)

    return wins

@router.get("/zuci-wins/{win_id}", response_model=ZuciWin)
async def get_zuci_win(win_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific Zuci Win entry"""
    win = await db.zuci_wins.find_one({"id": win_id}, {"_id": 0})

    if not win:
        raise HTTPException(status_code=404, detail="Win not found")

    return win

@router.put("/zuci-wins/{win_id}", response_model=ZuciWin)
async def update_zuci_win(
    win_id: str,
    win_data: ZuciWinUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a Zuci Win entry"""
    existing_win = await db.zuci_wins.find_one({"id": win_id}, {"_id": 0})

    if not existing_win:
        raise HTTPException(status_code=404, detail="Win not found")

    # Build update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

    if win_data.company_name is not None:
        update_data["company_name"] = win_data.company_name
    if win_data.description is not None:
        update_data["description"] = win_data.description
    if win_data.win_date is not None:
        update_data["win_date"] = win_data.win_date
    if win_data.contributions is not None:
        update_data["contributions"] = [c.model_dump() for c in win_data.contributions]

    await db.zuci_wins.update_one(
        {"id": win_id},
        {"$set": update_data}
    )

    # Fetch updated document
    updated_win = await db.zuci_wins.find_one({"id": win_id}, {"_id": 0})
    logger.info(f"Updated Zuci Win: {updated_win['company_name']}")

    return updated_win

@router.delete("/zuci-wins/{win_id}")
async def delete_zuci_win(win_id: str, current_user: User = Depends(get_current_user)):
    """Delete a Zuci Win entry"""
    result = await db.zuci_wins.delete_one({"id": win_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Win not found")

    logger.info(f"Deleted Zuci Win: {win_id}")
    return {"message": "Win deleted successfully"}

# ============== GTM ROUTES ==============

@router.post("/gtm-entries", response_model=GTMEntry)
async def create_gtm_entry(gtm_data: GTMEntryCreate, current_user: User = Depends(get_current_user)):
    """Create a new GTM entry"""
    gtm = {
        "id": str(uuid.uuid4()),
        "gtm_link": gtm_data.gtm_link,
        "description": gtm_data.description,
        "prospect_name": gtm_data.prospect_name,
        "date": gtm_data.date,
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }

    await db.gtm_entries.insert_one(gtm)
    logger.info(f"Created GTM entry: {gtm['prospect_name']}")

    return gtm

@router.get("/gtm-entries", response_model=List[GTMEntry])
async def get_all_gtm_entries(current_user: User = Depends(get_current_user)):
    """Get all GTM entries, sorted by date descending"""
    entries = await db.gtm_entries.find(
        {},
        {"_id": 0}
    ).sort("date", -1).to_list(None)

    return entries

@router.get("/gtm-entries/{entry_id}", response_model=GTMEntry)
async def get_gtm_entry(entry_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific GTM entry"""
    entry = await db.gtm_entries.find_one({"id": entry_id}, {"_id": 0})

    if not entry:
        raise HTTPException(status_code=404, detail="GTM entry not found")

    return entry

@router.put("/gtm-entries/{entry_id}", response_model=GTMEntry)
async def update_gtm_entry(
    entry_id: str,
    gtm_data: GTMEntryUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a GTM entry"""
    existing_entry = await db.gtm_entries.find_one({"id": entry_id}, {"_id": 0})

    if not existing_entry:
        raise HTTPException(status_code=404, detail="GTM entry not found")

    # Build update data
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}

    if gtm_data.gtm_link is not None:
        update_data["gtm_link"] = gtm_data.gtm_link
    if gtm_data.description is not None:
        update_data["description"] = gtm_data.description
    if gtm_data.prospect_name is not None:
        update_data["prospect_name"] = gtm_data.prospect_name
    if gtm_data.date is not None:
        update_data["date"] = gtm_data.date

    await db.gtm_entries.update_one(
        {"id": entry_id},
        {"$set": update_data}
    )

    # Fetch updated document
    updated_entry = await db.gtm_entries.find_one({"id": entry_id}, {"_id": 0})
    logger.info(f"Updated GTM entry: {updated_entry['prospect_name']}")

    return updated_entry

@router.delete("/gtm-entries/{entry_id}")
async def delete_gtm_entry(entry_id: str, current_user: User = Depends(get_current_user)):
    """Delete a GTM entry"""
    result = await db.gtm_entries.delete_one({"id": entry_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="GTM entry not found")

    logger.info(f"Deleted GTM entry: {entry_id}")
    return {"message": "GTM entry deleted successfully"}
