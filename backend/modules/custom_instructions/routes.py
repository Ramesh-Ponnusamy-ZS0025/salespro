"""
Custom Instructions Module
Handles saving and retrieving custom instructions for content generation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
from login import User, get_current_user

# Router
router = APIRouter(prefix="/api", tags=["custom-instructions"])

# Database reference
db = None

def set_db(database):
    global db
    db = database

# Models
class CustomInstructionCreate(BaseModel):
    """Request model for creating custom instruction (only name and content needed)"""
    name: str
    content: str

class CustomInstruction(BaseModel):
    """Full custom instruction model (for storage)"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

@router.post("/custom-instructions")
async def save_custom_instruction(
    request: CustomInstructionCreate,  # Changed to only require name and content
    current_user: User = Depends(get_current_user)
):
    """Save a custom instruction for reuse"""
    user = await db.users.find_one({"email": current_user.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create full instruction object with user_id
    instruction = CustomInstruction(
        user_id=user['id'],
        name=request.name,
        content=request.content
    )

    await db.custom_instructions.insert_one(instruction.dict())

    return {"message": "Instruction saved successfully", "id": instruction.id}

@router.get("/custom-instructions")
async def get_custom_instructions(
    current_user: User = Depends(get_current_user)
):
    """Get user's saved custom instructions"""
    user = await db.users.find_one({"email": current_user.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    instructions = await db.custom_instructions.find(
        {"user_id": user['id']},
        {"_id": 0}  # Exclude MongoDB's _id field to avoid serialization error
    ).sort("created_at", -1).to_list(100)

    return {"instructions": instructions}

@router.delete("/custom-instructions/{instruction_id}")
async def delete_custom_instruction(
    instruction_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a custom instruction"""
    user = await db.users.find_one({"email": current_user.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    result = await db.custom_instructions.delete_one({
        "id": instruction_id,
        "user_id": user['id']
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Instruction not found")

    return {"message": "Instruction deleted successfully"}
