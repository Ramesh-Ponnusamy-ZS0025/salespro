"""
Agent Builder Module
Contains: Agent models, agent CRUD routes, agent preview
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging

from login import User, get_current_user

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["agents"])

# Database reference - will be set from server.py
db = None

# LLM helper reference - will be set from server.py
generate_llm_response = None

def set_db(database):
    global db
    db = database

def set_llm_helper(llm_func):
    global generate_llm_response
    generate_llm_response = llm_func

# ============== MODELS ==============

class Agent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    service: str
    sub_service: Optional[str] = None
    value_props: List[str] = []
    pain_points: List[str] = []
    personas: List[str] = []
    tone: str = "professional"
    example_copies: List[str] = []
    version: str = "1.0"
    created_by: str
    usage_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AgentCreate(BaseModel):
    agent_name: str
    service: str
    sub_service: Optional[str] = None
    value_props: List[str] = []
    pain_points: List[str] = []
    personas: List[str] = []
    tone: str = "professional"
    example_copies: List[str] = []

# ============== AGENT ROUTES ==============

@router.post("/agents", response_model=Agent)
async def create_agent(agent_data: AgentCreate, current_user: User = Depends(get_current_user)):
    agent = Agent(**agent_data.model_dump(), created_by=current_user.id)
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.agents.insert_one(doc)
    return agent

@router.get("/agents", response_model=List[Agent])
async def get_agents(current_user: User = Depends(get_current_user)):
    agents = await db.agents.find({}, {"_id": 0}).to_list(1000)
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
        if isinstance(agent.get('updated_at'), str):
            agent['updated_at'] = datetime.fromisoformat(agent['updated_at'])
    return agents

@router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if isinstance(agent.get('created_at'), str):
        agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    if isinstance(agent.get('updated_at'), str):
        agent['updated_at'] = datetime.fromisoformat(agent['updated_at'])
    return Agent(**agent)

@router.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent_data: AgentCreate, current_user: User = Depends(get_current_user)):
    existing = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Agent not found")

    updated_data = agent_data.model_dump()
    updated_data['updated_at'] = datetime.now(timezone.utc).isoformat()

    await db.agents.update_one({"id": agent_id}, {"$set": updated_data})

    updated_agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if isinstance(updated_agent.get('created_at'), str):
        updated_agent['created_at'] = datetime.fromisoformat(updated_agent['created_at'])
    if isinstance(updated_agent.get('updated_at'), str):
        updated_agent['updated_at'] = datetime.fromisoformat(updated_agent['updated_at'])
    return Agent(**updated_agent)

@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    result = await db.agents.delete_one({"id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}

@router.get("/agents/{agent_id}/preview")
async def preview_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    prompt = f"""**MODULE: Agent Preview**

Generate a sample sales outreach message using this agent profile:

Agent Profile:
- Service: {agent['service']}
- Tone: {agent['tone']}
- Value Propositions: {', '.join(agent.get('value_props', []))}
- Pain Points: {', '.join(agent.get('pain_points', []))}

Target Persona: Mid-level manager in relevant industry

Requirements:
- Create a compelling, personalized outreach message (max 150 words)
- Follow the mandatory output structure: Prospect Insight + Sales Message + Soft CTA
- Make it ready to send immediately"""

    preview_text = await generate_llm_response(prompt)
    return {"preview": preview_text}
