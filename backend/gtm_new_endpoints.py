"""
NEW GTM ENDPOINTS - ADD TO server.py
Insert these after the existing GTM endpoints (around line 2500+)
"""

from gtm_lovable_generator import create_lovable_prompt, LovablePromptGenerator
import aiohttp
from bs4 import BeautifulSoup

# ============== NEW MODELS ==============

class LinkedInFetchRequest(BaseModel):
    linkedin_url: str

class ProspectAnalysisRequest(BaseModel):
    company_name: str
    industry: str
    linkedin_url: Optional[str] = None
    prospect_name: Optional[str] = None
    prospect_title: Optional[str] = None

class DemoSuggestionRequest(BaseModel):
    industry: str
    pain_points: List[str]
    company_size: Optional[str] = None

class LovablePromptRequest(BaseModel):
    # Prospect Information
    prospect_name: str
    prospect_title: str
    prospect_photo_url: Optional[str] = None
    company_name: str
    company_logo_url: Optional[str] = None
    industry: str
    
    # Meeting Context
    meeting_date: Optional[str] = None
    meeting_duration: Optional[str] = "15 minutes"
    meeting_location: Optional[str] = None
    
    # Business Context
    pain_points: List[str]
    portfolio_size: Optional[str] = None
    current_focus: Optional[str] = None
    
    # Demo Configuration
    demo_type: str  # 'mortgage_underwriting', 'credit_risk', 'payments_reconciliation', 'real_estate_closing'
    kpis: Optional[List[str]] = None
    
    # Proof Points
    selected_case_studies: List[str] = []  # IDs of case studies to include
    figma_urls: List[str] = []
    
    # Additional Context
    user_adjustments: Optional[str] = None

class MeetingPrepRequest(BaseModel):
    prospect_name: str
    prospect_title: str
    company_name: str
    industry: str
    linkedin_url: Optional[str] = None
    demo_type: str
    meeting_date: str
    meeting_duration: str

# ============== LINKEDIN SCRAPER ==============

@api_router.post("/gtm/fetch-linkedin")
async def fetch_linkedin_profile(request: LinkedInFetchRequest, current_user: User = Depends(get_current_user)):
    """
    Scrape LinkedIn profile to extract prospect information
    
    NOTE: This is a simplified version. In production, use LinkedIn API or Apify/Bright Data
    """
    try:
        # In production, you'd use LinkedIn API or a scraping service
        # For now, we'll return a mock response structure
        
        # Extract company name from URL
        url_parts = request.linkedin_url.split('/')
        company_slug = url_parts[-1] if url_parts[-1] else url_parts[-2]
        
        # Mock data - replace with actual scraper
        mock_data = {
            "name": "John Smith",  # Would be scraped
            "title": "VP of Technology",
            "company": company_slug.replace('-', ' ').title(),
            "photo_url": f"https://via.placeholder.com/400x400?text={company_slug}",
            "industry": "Financial Services",
            "location": "Toronto, ON",
            "recent_posts": [
                "Discussing AI transformation in lending",
                "Thoughts on modern underwriting systems"
            ],
            "company_info": {
                "size": "500-1000 employees",
                "founded": "2005",
                "specialties": ["Lending", "Fintech", "Risk Management"]
            }
        }
        
        return {
            "success": True,
            "data": mock_data,
            "message": "LinkedIn profile fetched successfully (mock data for demo)"
        }
    
    except Exception as e:
        logger.error(f"Error fetching LinkedIn profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch LinkedIn profile: {str(e)}")

# ============== PROSPECT ANALYSIS ==============

@api_router.post("/gtm/analyze-prospect")
async def analyze_prospect(request: ProspectAnalysisRequest, current_user: User = Depends(get_current_user)):
    """
    AI-powered analysis of prospect context to extract pain points and suggest approach
    """
    analysis_prompt = f"""You are an expert B2B sales analyst. Analyze this prospect:

Company: {request.company_name}
Industry: {request.industry}
{f"Prospect: {request.prospect_name} - {request.prospect_title}" if request.prospect_name else ""}

Based on the industry and any available context, identify:

1. **Top 3 Likely Pain Points** (specific to {request.industry})
2. **Key Decision Drivers** (what matters most to executives in this space)
3. **Recommended Demo Approach** (which type of solution would resonate)
4. **Suggested KPIs to Highlight** (metrics that matter to them)

Output as JSON:
{{
  "pain_points": ["pain1", "pain2", "pain3"],
  "decision_drivers": ["driver1", "driver2"],
  "recommended_demo_type": "mortgage_underwriting" or "credit_risk" or "payments_reconciliation",
  "suggested_kpis": ["kpi1", "kpi2", "kpi3", "kpi4"],
  "talking_points": ["point1", "point2", "point3"]
}}

Be specific to {request.industry}. Use industry terminology."""
    
    try:
        ai_response = await generate_llm_response(analysis_prompt)
        
        # Parse JSON from response
        import json
        import re
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
        
        if json_match:
            analysis = json.loads(json_match.group())
            
            return {
                "success": True,
                "analysis": analysis,
                "message": "Prospect analysis complete"
            }
        else:
            raise ValueError("Could not parse AI response as JSON")
    
    except Exception as e:
        logger.error(f"Error analyzing prospect: {str(e)}")
        # Fallback to default analysis
        return {
            "success": True,
            "analysis": {
                "pain_points": ["Manual processes", "Slow decision-making", "High operational costs"],
                "decision_drivers": ["ROI", "Speed", "Accuracy"],
                "recommended_demo_type": "credit_risk",
                "suggested_kpis": ["Time-to-Decision ↓65%", "Accuracy ↑40%", "Cost Savings $500K+"],
                "talking_points": [
                    "Focus on operational efficiency",
                    "Emphasize proven ROI",
                    "Highlight integration ease"
                ]
            },
            "message": "Using default analysis (AI parsing failed)"
        }

# ============== DEMO TYPE SUGGESTER ==============

@api_router.post("/gtm/suggest-demo-type")
async def suggest_demo_type(request: DemoSuggestionRequest, current_user: User = Depends(get_current_user)):
    """
    Suggest the best demo type based on industry and pain points
    """
    # Industry to demo type mapping
    industry_mappings = {
        "mortgage": "mortgage_underwriting",
        "lending": "credit_risk",
        "fintech": "payments_reconciliation",
        "banking": "credit_risk",
        "payments": "payments_reconciliation",
        "real estate": "real_estate_closing",
        "property": "real_estate_closing"
    }
    
    # Check industry keywords
    industry_lower = request.industry.lower()
    suggested_demo = None
    
    for keyword, demo_type in industry_mappings.items():
        if keyword in industry_lower:
            suggested_demo = demo_type
            break
    
    # If no match, analyze pain points
    if not suggested_demo:
        pain_keywords = " ".join(request.pain_points).lower()
        
        if any(kw in pain_keywords for kw in ["underwrit", "credit", "loan", "approv"]):
            suggested_demo = "mortgage_underwriting"
        elif any(kw in pain_keywords for kw in ["payment", "reconcil", "transact"]):
            suggested_demo = "payments_reconciliation"
        elif any(kw in pain_keywords for kw in ["closing", "title", "registry"]):
            suggested_demo = "real_estate_closing"
        else:
            suggested_demo = "credit_risk"  # Default
    
    # Get demo template details
    generator = LovablePromptGenerator()
    demo_info = generator.demo_templates.get(suggested_demo, {})
    
    return {
        "suggested_demo_type": suggested_demo,
        "demo_title": demo_info.get("title", "AI-Powered Platform"),
        "suggested_kpis": demo_info.get("kpis", []),
        "confidence": "high" if suggested_demo in industry_mappings.values() else "medium",
        "reason": f"Based on industry ({request.industry}) and pain points analysis"
    }

# ============== MAIN LOVABLE PROMPT GENERATOR ==============

@api_router.post("/gtm/generate-lovable-prompt")
async def generate_lovable_prompt_endpoint(request: LovablePromptRequest, current_user: User = Depends(get_current_user)):
    """
    Generate complete Lovable prompt with all 7 sections
    
    This is the main endpoint that replaces the old /gtm/generate-final-prompt
    """
    try:
        # Fetch selected case studies from database
        case_studies = []
        if request.selected_case_studies:
            studies = await db.document_files.find(
                {"id": {"$in": request.selected_case_studies}},
                {"_id": 0, "filename": 1, "summary": 1, "category": 1, "metadata": 1}
            ).to_list(len(request.selected_case_studies))
            
            for study in studies:
                metadata = study.get('metadata', {})
                case_studies.append({
                    "title": study.get('filename', '').replace('.pdf', ''),
                    "summary": study.get('summary', ''),
                    "category": study.get('category', 'Financial Services'),
                    "metric_time": "Decision time ↓65%",  # Could extract from summary
                    "metric_quality": "Exceptions ↓30%",
                    "savings": "$250-500K annually",
                    "roi": "10× in 9-12 months"
                })
        
        # If no case studies selected, use defaults
        if not case_studies:
            case_studies = [
                {
                    "title": "MCAN Financial - Underwriting Modernization",
                    "summary": "AI-driven underwriting automation with portfolio visibility",
                    "category": "Mortgage Lending",
                    "metric_time": "Decision time ↓65%",
                    "metric_quality": "Exceptions ↓30%",
                    "savings": "$400K annually",
                    "roi": "10× in 9 months"
                },
                {
                    "title": "Mariner Finance - Risk Analytics",
                    "summary": "Predictive analytics for consumer lending risk assessment",
                    "category": "Consumer Lending",
                    "metric_time": "Approval time ↓40%",
                    "metric_quality": "Default rate ↓25%",
                    "savings": "$300K annually",
                    "roi": "7× in 12 months"
                }
            ]
        
        # Build prospect data dictionary
        prospect_data = {
            "name": request.prospect_name,
            "title": request.prospect_title,
            "photo_url": request.prospect_photo_url or "https://via.placeholder.com/400x400",
            "company_name": request.company_name,
            "company_logo_url": request.company_logo_url,
            "industry": request.industry,
            "meeting_date": request.meeting_date or "TBD",
            "meeting_duration": request.meeting_duration,
            "meeting_location": request.meeting_location or "Virtual",
            "portfolio_size": request.portfolio_size,
            "current_focus": request.current_focus,
            "kpis": request.kpis or [],
            "tagline": f"Empowering {request.industry} with Agentic Intelligence"
        }
        
        # Generate the Lovable prompt
        lovable_prompt = create_lovable_prompt(
            prospect_data=prospect_data,
            demo_type=request.demo_type,
            case_studies=case_studies,
            figma_urls=request.figma_urls
        )
        
        # Save to database
        gtm_id = str(uuid.uuid4())
        gtm_record = {
            "id": gtm_id,
            "company_name": request.company_name,
            "prospect_name": request.prospect_name,
            "industry": request.industry,
            "demo_type": request.demo_type,
            "lovable_prompt": lovable_prompt,
            "case_studies_used": [cs["title"] for cs in case_studies],
            "figma_urls": request.figma_urls,
            "status": "lovable_prompt_generated",
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.gtm_assets.insert_one(gtm_record)
        
        return {
            "id": gtm_id,
            "lovable_prompt": lovable_prompt,
            "status": "success",
            "case_studies_count": len(case_studies),
            "figma_count": len(request.figma_urls),
            "message": "Lovable prompt generated successfully"
        }
    
    except Exception as e:
        logger.error(f"Error generating Lovable prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate Lovable prompt: {str(e)}")

# ============== MEETING PREP GENERATOR ==============

@api_router.post("/gtm/generate-meeting-prep")
async def generate_meeting_prep(request: MeetingPrepRequest, current_user: User = Depends(get_current_user)):
    """
    Generate comprehensive meeting prep document like ChatGPT workflow
    
    Includes:
    - Who is the prospect (background)
    - What their company does
    - Suggested talking points
    - Questions to ask
    - 1-minute pitch script
    - Follow-up email template
    """
    
    prep_prompt = f"""You are an expert sales strategist. Create a comprehensive meeting preparation guide.

PROSPECT:
- Name: {request.prospect_name}
- Title: {request.prospect_title}
- Company: {request.company_name}
- Industry: {request.industry}

MEETING:
- Date: {request.meeting_date}
- Duration: {request.meeting_duration}

DEMO TYPE: {request.demo_type}

Create a meeting prep document with these sections:

1. **WHO IS {request.prospect_name}**
   - Background and role
   - What they care about (based on title and industry)
   - Their likely priorities

2. **WHAT {request.company_name} DOES**
   - Brief company overview
   - Industry position
   - Current challenges (inferred from {request.industry})

3. **YOUR OPENING (30 seconds)**
   - Personal connection
   - Bridge to Zuci's value

4. **SMART QUESTIONS TO ASK** (5 questions)
   - Discovery questions specific to {request.industry}
   - Open-ended, consultative

5. **DEMO WALKTHROUGH SCRIPT** (90 seconds)
   - What to show
   - What to say at each screen
   - Key value props to emphasize

6. **CLOSING LINE**
   - How to transition to next step
   - Specific ask

7. **FOLLOW-UP EMAIL TEMPLATE**
   - Subject line
   - Body (3 paragraphs)
   - CTA

Make it natural, conversational, and specific to {request.industry}. Use real industry terminology."""
    
    try:
        meeting_prep = await generate_llm_response(prep_prompt)
        
        # Save to database
        prep_id = str(uuid.uuid4())
        prep_record = {
            "id": prep_id,
            "prospect_name": request.prospect_name,
            "company_name": request.company_name,
            "meeting_prep": meeting_prep,
            "meeting_date": request.meeting_date,
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.gtm_meeting_preps.insert_one(prep_record)
        
        return {
            "id": prep_id,
            "meeting_prep": meeting_prep,
            "status": "success",
            "message": "Meeting prep generated successfully"
        }
    
    except Exception as e:
        logger.error(f"Error generating meeting prep: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate meeting prep: {str(e)}")

# ============== GET ALL GTM ASSETS (Enhanced) ==============

@api_router.get("/gtm/assets")
async def get_gtm_assets_enhanced(current_user: User = Depends(get_current_user)):
    """
    Get all GTM assets including both old prompts and new Lovable prompts
    """
    try:
        # Get all GTM assets
        assets = await db.gtm_assets.find(
            {"created_by": current_user.id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(1000)
        
        # Get meeting preps
        preps = await db.gtm_meeting_preps.find(
            {"created_by": current_user.id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(1000)
        
        return {
            "gtm_assets": assets,
            "meeting_preps": preps,
            "total_assets": len(assets),
            "total_preps": len(preps)
        }
    
    except Exception as e:
        logger.error(f"Error fetching GTM assets: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")
