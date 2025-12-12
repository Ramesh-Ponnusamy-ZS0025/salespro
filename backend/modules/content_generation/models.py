from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class LinkedInProfile(BaseModel):
    name: str
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    about: Optional[str] = None
    experience: Optional[List[dict]] = []
    education: Optional[List[dict]] = []
    posts: Optional[List[dict]] = []
    skills: Optional[List[str]] = []
    profile_url: Optional[str] = None
    shared_experiences: Optional[List[dict]] = []
    years_at_company: Optional[float] = None
    num_roles_at_company: Optional[int] = None
    shared_customers: Optional[List[str]] = []
    personality_type: Optional[str] = None
    company_description: Optional[str] = None
    company_headcount: Optional[int] = None
    target_industries: Optional[List[str]] = []
    business_model: Optional[str] = None
    work_milestones: Optional[List[str]] = []

class Insight(BaseModel):
    category: str
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

class ContentGenerationRequest(BaseModel):
    linkedin_data: LinkedInProfile
    selected_insights: Optional[List[Insight]] = []
    content_type: str = "email"
    content_focus: str = "all"  # New field: all, recent_posts, skills, recommendations, geography, about, education, experience
    writing_style: str = "data-driven"
    value_proposition: Optional[str] = None
    additional_context: Optional[str] = None
    case_studies: Optional[List] = []
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
