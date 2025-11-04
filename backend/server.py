from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
from passlib.context import CryptContext
# from emergentintegrations.llm.chat import LlmChat, UserMessage
from docx import Document
from docx.shared import Pt, Inches
from io import BytesIO
import base64

ROOT_DIR = Path(__file__).parent
print('ROOT_DIR',ROOT_DIR)
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT and password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

JWT_SECRET = os.environ.get('JWT_SECRET','mysecret')
JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))

# LLM Config
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ============== MODELS ==============

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

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
    methodologies: List[str] = []
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
    methodologies: List[str] = []
    example_copies: List[str] = []

class Campaign(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_name: str
    agent_id: str
    service: str
    stage: str  # TOFU/MOFU/BOFU
    icp: List[str] = []
    methodologies: List[str] = []
    tone: str
    resources: List[str] = []
    status: str = "draft"  # draft/review/published
    ai_content: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CampaignCreate(BaseModel):
    campaign_name: str
    agent_id: str
    service: str
    stage: str
    icp: List[str] = []
    methodologies: List[str] = []
    tone: str
    resources: List[str] = []

class SenderProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    position: str
    company: str
    email: EmailStr
    phone: Optional[str] = None
    signature_template: str
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SenderProfileCreate(BaseModel):
    name: str
    position: str
    company: str
    email: EmailStr
    phone: Optional[str] = None
    signature_template: str

class PersonalizationRequest(BaseModel):
    origin_url: str
    agent_id: str
    sender_profile_id: str
    keywords: List[str] = []
    notes: Optional[str] = None

class PersonalizationResponse(BaseModel):
    id: str
    message: str
    char_count: int

class ThreadAnalyzeRequest(BaseModel):
    thread_text: str
    agent_id: Optional[str] = None

class ThreadAnalysisResponse(BaseModel):
    id: str
    summary: str
    detected_stage: str
    sentiment: str
    suggestions: List[str]
    ai_followup: Optional[str] = None

class DocumentRequest(BaseModel):
    template_type: str  # nda/msa/sow
    engagement_model: str  # t&m/dedicated/fixed_bid
    variables: Dict[str, Any]

class DocumentResponse(BaseModel):
    id: str
    doc_url: str
    template_type: str

class GTMRequest(BaseModel):
    company_name: str
    linkedin_url: Optional[str] = None
    offering: str
    pain_points: List[str]
    personas: List[str]
    target_persons: List[str]

class GTMResponse(BaseModel):
    id: str
    prompt: str
    status: str

class FeedbackCreate(BaseModel):
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    feedback_text: str
    rating: int
    tags: List[str] = []

class Feedback(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    user_id: str
    feedback_text: str
    rating: int
    tags: List[str] = []
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class InsightResponse(BaseModel):
    id: str
    campaign_id: Optional[str] = None
    metric: str
    observation: str
    suggested_action: str
    status: str
    created_at: datetime

# ============== AUTH HELPERS ==============

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user_data = await db.users.find_one({"id": user_id}, {"_id": 0})
        if user_data is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return User(**user_data)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ============== LLM HELPER ==============

async def generate_llm_response(prompt: str, system_message: str = "You are a helpful AI assistant for sales and marketing.") -> str:
   pass
   '''
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=system_message
        ).with_model("openai", "gpt-4o")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logging.error(f"LLM Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating AI response")
    '''

# ============== AUTH ROUTES ==============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.users.insert_one(doc)
    
    # Create token
    access_token = create_access_token({"sub": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user={"id": user.id, "email": user.email, "username": user.username}
    )

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user_data = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user = User(**user_data)
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token({"sub": user.id, "email": user.email})
    
    return TokenResponse(
        access_token=access_token,
        user={"id": user.id, "email": user.email, "username": user.username}
    )

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "username": current_user.username}

# ============== AGENT ROUTES ==============

@api_router.post("/agents", response_model=Agent)
async def create_agent(agent_data: AgentCreate, current_user: User = Depends(get_current_user)):
    agent = Agent(**agent_data.model_dump(), created_by=current_user.id)
    doc = agent.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.agents.insert_one(doc)
    return agent

@api_router.get("/agents", response_model=List[Agent])
async def get_agents(current_user: User = Depends(get_current_user)):
    agents = await db.agents.find({}, {"_id": 0}).to_list(1000)
    for agent in agents:
        if isinstance(agent.get('created_at'), str):
            agent['created_at'] = datetime.fromisoformat(agent['created_at'])
        if isinstance(agent.get('updated_at'), str):
            agent['updated_at'] = datetime.fromisoformat(agent['updated_at'])
    return agents

@api_router.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    if isinstance(agent.get('created_at'), str):
        agent['created_at'] = datetime.fromisoformat(agent['created_at'])
    if isinstance(agent.get('updated_at'), str):
        agent['updated_at'] = datetime.fromisoformat(agent['updated_at'])
    return Agent(**agent)

@api_router.put("/agents/{agent_id}", response_model=Agent)
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

@api_router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    result = await db.agents.delete_one({"id": agent_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}

@api_router.get("/agents/{agent_id}/preview")
async def preview_agent(agent_id: str, current_user: User = Depends(get_current_user)):
    agent = await db.agents.find_one({"id": agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    prompt = f"""Generate a sample sales message using this agent profile:
    Service: {agent['service']}
    Tone: {agent['tone']}
    Value Props: {', '.join(agent.get('value_props', []))}
    Pain Points: {', '.join(agent.get('pain_points', []))}
    
    Create a brief, engaging message (max 150 words)."""
    
    preview_text = await generate_llm_response(prompt)
    return {"preview": preview_text}

# ============== CAMPAIGN ROUTES ==============

@api_router.post("/campaigns", response_model=Campaign)
async def create_campaign(campaign_data: CampaignCreate, current_user: User = Depends(get_current_user)):
    # Verify agent exists
    agent = await db.agents.find_one({"id": campaign_data.agent_id}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    campaign = Campaign(**campaign_data.model_dump(), created_by=current_user.id)
    doc = campaign.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.campaigns.insert_one(doc)
    
    # Increment agent usage
    await db.agents.update_one({"id": campaign_data.agent_id}, {"$inc": {"usage_count": 1}})
    
    return campaign

@api_router.get("/campaigns", response_model=List[Campaign])
async def get_campaigns(current_user: User = Depends(get_current_user)):
    campaigns = await db.campaigns.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    for campaign in campaigns:
        if isinstance(campaign.get('created_at'), str):
            campaign['created_at'] = datetime.fromisoformat(campaign['created_at'])
        if isinstance(campaign.get('updated_at'), str):
            campaign['updated_at'] = datetime.fromisoformat(campaign['updated_at'])
    return campaigns

@api_router.get("/campaigns/{campaign_id}", response_model=Campaign)
async def get_campaign(campaign_id: str, current_user: User = Depends(get_current_user)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if isinstance(campaign.get('created_at'), str):
        campaign['created_at'] = datetime.fromisoformat(campaign['created_at'])
    if isinstance(campaign.get('updated_at'), str):
        campaign['updated_at'] = datetime.fromisoformat(campaign['updated_at'])
    return Campaign(**campaign)

@api_router.post("/campaigns/{campaign_id}/generate")
async def generate_campaign_copy(campaign_id: str, current_user: User = Depends(get_current_user)):
    campaign = await db.campaigns.find_one({"id": campaign_id}, {"_id": 0})
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    agent = await db.agents.find_one({"id": campaign['agent_id']}, {"_id": 0})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    methodology_text = ", ".join(campaign.get('methodologies', []))
    
    prompt = f"""Generate sales campaign copy with the following details:
    
    Service: {campaign['service']}
    Stage: {campaign['stage']}
    Target ICP: {', '.join(campaign.get('icp', []))}
    Tone: {campaign['tone']}
    Methodologies: {methodology_text}
    
    Agent Profile:
    - Value Propositions: {', '.join(agent.get('value_props', []))}
    - Pain Points: {', '.join(agent.get('pain_points', []))}
    - Personas: {', '.join(agent.get('personas', []))}
    
    Create compelling, personalized campaign copy (200-300 words) that addresses the pain points and highlights value propositions."""
    
    ai_content = await generate_llm_response(prompt)
    
    # Update campaign with generated content
    await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"ai_content": ai_content, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"content": ai_content}

@api_router.put("/campaigns/{campaign_id}/status")
async def update_campaign_status(campaign_id: str, status: str, current_user: User = Depends(get_current_user)):
    result = await db.campaigns.update_one(
        {"id": campaign_id},
        {"$set": {"status": status, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return {"message": "Status updated successfully"}

# ============== SENDER PROFILE ROUTES ==============

@api_router.post("/sender-profiles", response_model=SenderProfile)
async def create_sender_profile(profile_data: SenderProfileCreate, current_user: User = Depends(get_current_user)):
    profile = SenderProfile(**profile_data.model_dump(), created_by=current_user.id)
    doc = profile.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.sender_profiles.insert_one(doc)
    return profile

@api_router.get("/sender-profiles", response_model=List[SenderProfile])
async def get_sender_profiles(current_user: User = Depends(get_current_user)):
    profiles = await db.sender_profiles.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    for profile in profiles:
        if isinstance(profile.get('created_at'), str):
            profile['created_at'] = datetime.fromisoformat(profile['created_at'])
    return profiles

# ============== PERSONALIZATION ROUTES ==============

@api_router.post("/personalize/generate", response_model=PersonalizationResponse)
async def generate_personalization(request: PersonalizationRequest, current_user: User = Depends(get_current_user)):
    # Get agent and sender profile
    agent = await db.agents.find_one({"id": request.agent_id}, {"_id": 0})
    sender = await db.sender_profiles.find_one({"id": request.sender_profile_id}, {"_id": 0})
    
    if not agent or not sender:
        raise HTTPException(status_code=404, detail="Agent or Sender Profile not found")
    
    keywords_text = ", ".join(request.keywords) if request.keywords else "general outreach"
    notes_text = request.notes or ""
    
    prompt = f"""Generate a personalized 1:1 sales message with these details:
    
    Target URL/Context: {request.origin_url}
    Keywords: {keywords_text}
    Additional Notes: {notes_text}
    
    Agent Profile:
    - Service: {agent['service']}
    - Tone: {agent['tone']}
    - Value Props: {', '.join(agent.get('value_props', []))}
    
    Sender Profile:
    - Name: {sender['name']}
    - Position: {sender['position']}
    - Company: {sender['company']}
    
    Requirements:
    - Keep it under 500 characters
    - Highly personalized and relevant
    - Professional and engaging
    - Include a clear call-to-action
    
    Generate ONLY the message content, no additional formatting or explanation."""
    
    message = await generate_llm_response(prompt)
    message = message.strip()
    
    # Save personalization
    person_id = str(uuid.uuid4())
    personalization = {
        "id": person_id,
        "origin_url": request.origin_url,
        "agent_id": request.agent_id,
        "sender_profile_id": request.sender_profile_id,
        "keywords": request.keywords,
        "notes": request.notes,
        "message": message,
        "char_count": len(message),
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.personalizations.insert_one(personalization)
    
    return PersonalizationResponse(
        id=person_id,
        message=message,
        char_count=len(message)
    )

# ============== THREAD INTELLIGENCE ROUTES ==============

@api_router.post("/thread/analyze", response_model=ThreadAnalysisResponse)
async def analyze_thread(request: ThreadAnalyzeRequest, current_user: User = Depends(get_current_user)):
    prompt = f"""Analyze this email thread and provide:
    1. A brief summary
    2. Detected stage (Cold/Warm/Hot)
    3. Sentiment (Positive/Neutral/Negative)
    4. Key suggestions for next steps
    
    Thread:
    {request.thread_text}
    
    Respond in this exact JSON format:
    {{
        "summary": "brief summary here",
        "stage": "Cold/Warm/Hot",
        "sentiment": "Positive/Neutral/Negative",
        "suggestions": ["suggestion 1", "suggestion 2"]
    }}"""
    
    response_text = await generate_llm_response(prompt)
    
    # Parse response (simplified - in production, use proper JSON parsing)
    import json
    try:
        # Try to extract JSON from response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end > start:
            json_str = response_text[start:end]
            analysis = json.loads(json_str)
        else:
            # Fallback if no JSON found
            analysis = {
                "summary": response_text[:200],
                "stage": "Warm",
                "sentiment": "Neutral",
                "suggestions": ["Follow up with additional information", "Schedule a call"]
            }
    except:
        analysis = {
            "summary": "Analysis completed",
            "stage": "Warm",
            "sentiment": "Neutral",
            "suggestions": ["Follow up with additional information"]
        }
    
    # Generate follow-up if agent provided
    followup = None
    if request.agent_id:
        agent = await db.agents.find_one({"id": request.agent_id}, {"_id": 0})
        if agent:
            followup_prompt = f"""Based on this email thread analysis, generate a follow-up email:
            
            Summary: {analysis['summary']}
            Stage: {analysis['stage']}
            Sentiment: {analysis['sentiment']}
            
            Agent Profile:
            - Service: {agent['service']}
            - Tone: {agent['tone']}
            
            Generate a professional follow-up email (150-200 words)."""
            
            followup = await generate_llm_response(followup_prompt)
    
    # Save analysis
    thread_id = str(uuid.uuid4())
    thread_doc = {
        "id": thread_id,
        "summary": analysis['summary'],
        "detected_stage": analysis['stage'],
        "sentiment": analysis['sentiment'],
        "suggestions": analysis['suggestions'],
        "ai_followup": followup,
        "raw_thread_data": request.thread_text,
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.thread_analyses.insert_one(thread_doc)
    
    return ThreadAnalysisResponse(
        id=thread_id,
        summary=analysis['summary'],
        detected_stage=analysis['stage'],
        sentiment=analysis['sentiment'],
        suggestions=analysis['suggestions'],
        ai_followup=followup
    )

# ============== DOCUMENT GENERATOR ROUTES ==============

def create_doc_template(template_type: str, variables: Dict[str, Any]) -> BytesIO:
    """Create a document from template with mail merge fields"""
    doc = Document()
    
    # Set document title
    title = doc.add_heading(template_type.upper(), 0)
    
    if template_type == "nda":
        doc.add_heading('Non-Disclosure Agreement', level=1)
        doc.add_paragraph(f"This Agreement is made on {variables.get('date', 'DATE')}")
        doc.add_paragraph(f"Between: {variables.get('party1_name', 'PARTY_1_NAME')} ('{variables.get('party1_short', 'Party 1')}')") 
        doc.add_paragraph(f"And: {variables.get('party2_name', 'PARTY_2_NAME')} ('{variables.get('party2_short', 'Party 2')}')") 
        doc.add_paragraph('\n')
        doc.add_heading('1. Confidential Information', level=2)
        doc.add_paragraph(variables.get('confidential_info', 'The parties agree to protect confidential information shared during business discussions.'))
        doc.add_heading('2. Obligations', level=2)
        doc.add_paragraph(variables.get('obligations', 'Both parties agree not to disclose confidential information to third parties without prior written consent.'))
        doc.add_heading('3. Term', level=2)
        doc.add_paragraph(f"This agreement shall remain in effect for {variables.get('term', 'TERM_PERIOD')}.")
        
    elif template_type == "msa":
        doc.add_heading('Master Service Agreement', level=1)
        doc.add_paragraph(f"Effective Date: {variables.get('effective_date', 'EFFECTIVE_DATE')}")
        doc.add_paragraph(f"Client: {variables.get('client_name', 'CLIENT_NAME')}")
        doc.add_paragraph(f"Service Provider: {variables.get('provider_name', 'PROVIDER_NAME')}")
        doc.add_paragraph('\n')
        doc.add_heading('1. Services', level=2)
        doc.add_paragraph(variables.get('services_desc', 'Services to be provided as per Statement of Work.'))
        doc.add_heading('2. Payment Terms', level=2)
        doc.add_paragraph(variables.get('payment_terms', 'Payment terms as specified in individual SOWs.'))
        doc.add_heading('3. Term and Termination', level=2)
        doc.add_paragraph(f"Initial term: {variables.get('term', 'TERM_PERIOD')}")
        
    elif template_type == "sow":
        doc.add_heading('Statement of Work', level=1)
        doc.add_paragraph(f"Project: {variables.get('project_name', 'PROJECT_NAME')}")
        doc.add_paragraph(f"Client: {variables.get('client_name', 'CLIENT_NAME')}")
        doc.add_paragraph(f"Engagement Model: {variables.get('engagement_model', 'ENGAGEMENT_MODEL')}")
        doc.add_paragraph('\n')
        doc.add_heading('1. Scope of Work', level=2)
        doc.add_paragraph(variables.get('scope', 'Project scope and deliverables.'))
        doc.add_heading('2. Timeline', level=2)
        doc.add_paragraph(f"Duration: {variables.get('duration', 'DURATION')}")
        doc.add_paragraph(f"Start Date: {variables.get('start_date', 'START_DATE')}")
        doc.add_heading('3. Resources', level=2)
        doc.add_paragraph(variables.get('resources', 'Team composition and resource allocation.'))
        doc.add_heading('4. Cost', level=2)
        doc.add_paragraph(f"Total Cost: ${variables.get('total_cost', '0.00')}")
        doc.add_paragraph(variables.get('cost_breakdown', 'Cost breakdown as per engagement model.'))
    
    # Add signatures section
    doc.add_page_break()
    doc.add_heading('Signatures', level=2)
    doc.add_paragraph('\n\n')
    doc.add_paragraph(f"{variables.get('signatory1_name', 'SIGNATORY_1')}")
    doc.add_paragraph(f"{variables.get('signatory1_title', 'Title')}")
    doc.add_paragraph(f"Date: {variables.get('signature_date', '_____________')}")
    doc.add_paragraph('\n\n')
    doc.add_paragraph(f"{variables.get('signatory2_name', 'SIGNATORY_2')}")
    doc.add_paragraph(f"{variables.get('signatory2_title', 'Title')}")
    doc.add_paragraph(f"Date: {variables.get('signature_date', '_____________')}")
    
    # Save to BytesIO
    file_stream = BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

@api_router.post("/documents/generate", response_model=DocumentResponse)
async def generate_document(request: DocumentRequest, current_user: User = Depends(get_current_user)):
    doc_id = str(uuid.uuid4())
    
    # Generate document
    doc_stream = create_doc_template(request.template_type, request.variables)
    
    # In production, save to object storage. For now, convert to base64
    doc_base64 = base64.b64encode(doc_stream.read()).decode('utf-8')
    doc_url = f"data:application/vnd.openxmlformats-officedocument.wordprocessingml.document;base64,{doc_base64}"
    
    # Save document metadata
    doc_record = {
        "id": doc_id,
        "template_type": request.template_type,
        "engagement_model": request.engagement_model,
        "variables": request.variables,
        "doc_url": "generated",  # In production, save actual file URL
        "status": "generated",
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.documents.insert_one(doc_record)
    
    return DocumentResponse(
        id=doc_id,
        doc_url=doc_url,
        template_type=request.template_type
    )

@api_router.get("/documents")
async def get_documents(current_user: User = Depends(get_current_user)):
    docs = await db.documents.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    return docs

# ============== GTM GENERATOR ROUTES ==============

@api_router.post("/gtm/generate-prompt", response_model=GTMResponse)
async def generate_gtm_prompt(request: GTMRequest, current_user: User = Depends(get_current_user)):
    gtm_id = str(uuid.uuid4())
    
    pain_points_text = ", ".join(request.pain_points)
    personas_text = ", ".join(request.personas)
    targets_text = ", ".join(request.target_persons)
    
    prompt = f"""Create a prospect-specific microsite prompt for Lovable/Emergent:
    
    Company: {request.company_name}
    LinkedIn: {request.linkedin_url or 'N/A'}
    Offering: {request.offering}
    Pain Points: {pain_points_text}
    Target Personas: {personas_text}
    Key Decision Makers: {targets_text}
    
    Generate a detailed prompt for creating a personalized landing page that:
    1. Addresses the specific pain points
    2. Showcases our offering's value
    3. Speaks directly to the target personas
    4. Includes clear CTAs for {targets_text}
    5. Uses professional design with company branding
    
    Make it comprehensive and ready to use with Lovable/Emergent for microsite generation."""
    
    generated_prompt = await generate_llm_response(prompt, "You are an expert at creating website prompts for landing page builders.")
    
    # Save GTM record
    gtm_record = {
        "id": gtm_id,
        "company_name": request.company_name,
        "offering": request.offering,
        "prompt": generated_prompt,
        "status": "prompt_generated",
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.gtm_assets.insert_one(gtm_record)
    
    return GTMResponse(
        id=gtm_id,
        prompt=generated_prompt,
        status="prompt_generated"
    )

@api_router.get("/gtm")
async def get_gtm_assets(current_user: User = Depends(get_current_user)):
    assets = await db.gtm_assets.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    return assets

# ============== FEEDBACK ROUTES ==============

@api_router.post("/feedback", response_model=Feedback)
async def submit_feedback(feedback_data: FeedbackCreate, current_user: User = Depends(get_current_user)):
    feedback = Feedback(**feedback_data.model_dump(), user_id=current_user.id)
    doc = feedback.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.feedback.insert_one(doc)
    return feedback

@api_router.get("/feedback", response_model=List[Feedback])
async def get_feedback(current_user: User = Depends(get_current_user)):
    feedback_list = await db.feedback.find({}, {"_id": 0}).to_list(1000)
    for fb in feedback_list:
        if isinstance(fb.get('created_at'), str):
            fb['created_at'] = datetime.fromisoformat(fb['created_at'])
    return feedback_list

# ============== INSIGHTS ROUTES ==============

@api_router.get("/insights", response_model=List[InsightResponse])
async def get_insights(current_user: User = Depends(get_current_user)):
    # Get feedback and campaigns for analysis
    feedback_list = await db.feedback.find({}, {"_id": 0}).to_list(1000)
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)
    
    insights = []
    
    # Generate insights based on feedback patterns
    if len(feedback_list) > 5:
        avg_rating = sum(f['rating'] for f in feedback_list) / len(feedback_list)
        
        insight_id = str(uuid.uuid4())
        insight = {
            "id": insight_id,
            "campaign_id": None,
            "metric": "average_rating",
            "observation": f"Average feedback rating is {avg_rating:.1f}/5 based on {len(feedback_list)} responses",
            "suggested_action": "Continue current approach" if avg_rating >= 4 else "Review and improve messaging strategies",
            "status": "active",
            "created_at": datetime.now(timezone.utc)
        }
        insights.append(InsightResponse(**insight))
    
    # Campaign performance insights
    if len(campaigns) > 0:
        published_count = len([c for c in campaigns if c.get('status') == 'published'])
        draft_count = len([c for c in campaigns if c.get('status') == 'draft'])
        
        insight_id = str(uuid.uuid4())
        insight = {
            "id": insight_id,
            "campaign_id": None,
            "metric": "campaign_status",
            "observation": f"{published_count} campaigns published, {draft_count} in draft",
            "suggested_action": "Review draft campaigns and move to production" if draft_count > published_count else "Great campaign momentum!",
            "status": "active",
            "created_at": datetime.now(timezone.utc)
        }
        insights.append(InsightResponse(**insight))
    
    return insights

@api_router.post("/insights/run")
async def run_insights_engine(current_user: User = Depends(get_current_user)):
    """Trigger AI-powered insights generation"""
    campaigns = await db.campaigns.find({}, {"_id": 0}).to_list(1000)
    feedback_list = await db.feedback.find({}, {"_id": 0}).to_list(1000)
    
    prompt = f"""Analyze this sales platform data and provide actionable insights:
    
    Total Campaigns: {len(campaigns)}
    Total Feedback: {len(feedback_list)}
    
    Feedback ratings: {[f['rating'] for f in feedback_list[:10]]}
    Campaign stages: {[c.get('stage') for c in campaigns[:10]]}
    
    Provide 3 key insights with specific recommendations for improving sales effectiveness."""
    
    insights_text = await generate_llm_response(prompt)
    
    return {"insights": insights_text}

# ============== DASHBOARD STATS ==============

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    agents_count = await db.agents.count_documents({})
    campaigns_count = await db.campaigns.count_documents({"created_by": current_user.id})
    feedback_count = await db.feedback.count_documents({})
    documents_count = await db.documents.count_documents({"created_by": current_user.id})
    
    # Get recent activity
    recent_campaigns = await db.campaigns.find(
        {"created_by": current_user.id},
        {"_id": 0}
    ).sort("created_at", -1).limit(5).to_list(5)
    
    return {
        "agents_count": agents_count,
        "campaigns_count": campaigns_count,
        "feedback_count": feedback_count,
        "documents_count": documents_count,
        "recent_campaigns": recent_campaigns
    }

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
