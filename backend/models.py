from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, timezone
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LinkedInProfile(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    about: Optional[str] = None
    experience: Optional[List[dict]] = []
    education: Optional[List[dict]] = []
    posts: Optional[List[dict]] = []  # Changed to dict to include engagement
    skills: Optional[List[str]] = []
    profile_url: Optional[str] = None
    # Enhanced fields
    shared_experiences: Optional[List[dict]] = []
    years_at_company: Optional[float] = None
    num_roles_at_company: Optional[int] = None
    shared_customers: Optional[List[str]] = []
    personality_type: Optional[str] = None
    company_description: Optional[str] = None
    company_headcount: Optional[int] = None
    target_industries: Optional[List[str]] = []
    # NEW FIELDS
    business_model: Optional[str] = None
    work_milestones: Optional[List[str]] = []

class Insight(BaseModel):
    category: str  # shared-experience, linkedin-post, professional-background, etc.
    title: str
    content: str
    icon: Optional[str] = None
    metadata: Optional[dict] = {}
    selected: bool = True

class CaseStudy(BaseModel):
    title: str
    excerpt: str
    url: str
    categories: List[str]
    keywords: List[str]
    industry: str
    technologies: Optional[List[str]] = []
    results: Optional[str] = None
    relevance_score: float = 0.0

class CustomInstruction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    name: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContentGenerationRequest(BaseModel):
    linkedin_data: LinkedInProfile
    selected_insights: Optional[List[Insight]] = []
    content_type: str = "email"  # email, linkedin_dm, opener
    writing_style: str = "data-driven"  # 8 different styles
    value_proposition: Optional[str] = None
    additional_context: Optional[str] = None
    case_studies: Optional[List] = []  # List of case study objects or titles
    message_length: str = "100-200"  # <100, 100-200, 200-300, 500, long

class ContentGenerationRequestV2(BaseModel):
    linkedin_data: LinkedInProfile
    selected_insights: List[Insight]
    content_type: str = "email"
    writing_style: str = "data-driven"
    value_proposition_id: Optional[str] = None
    custom_instruction: Optional[str] = None
    case_study_ids: List[str] = []
    message_length: str = "100-200"

class GeneratedContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    linkedin_data: LinkedInProfile
    generated_text: str
    content_type: str
    tone: str
    insights_used: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    score: Optional[int] = None

class GeneratedContentResponse(BaseModel):
    id: str
    generated_text: str
    insights_used: List[str]
    score: int
    created_at: datetime

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
    submitted_by_leaders: bool = False
    usage_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))