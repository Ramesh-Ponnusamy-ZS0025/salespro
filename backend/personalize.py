"""
Personalization Module
Contains: Personalization models and routes for generating personalized outreach messages
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
import logging

from login import User, get_current_user

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["personalize"])

# Database reference - will be set from server.py
db = None

# LLM helper reference - will be set from server.py
generate_llm_response = None

# Case study manager reference - will be set from server.py
case_study_manager = None

# Tone descriptions - consistent with Agent Builder
TONE_DESCRIPTIONS = {
    'professional': 'Formal, polished business communication. Respectful and direct.',
    'data-driven': 'Lead with metrics, ROI, quantifiable outcomes. Use specific numbers and percentages.',
    'formal-human': 'Professional yet personable. Balance formality with warmth and authenticity.',
    'cxo-pitch': 'Strategic, executive-level language. Address business priorities like cost reduction, revenue growth, competitive advantage.',
    'challenger-style': 'Challenge status quo. Teach, tailor, and take control. Introduce new perspectives.',
    'basho-style': 'Build rapport first. Personalized, research-driven. Focus on recipient\'s interests before business.',
    'z-poet': 'Creative, memorable messaging. Use metaphors and storytelling while maintaining professionalism.',
    'urgency-framing': 'Create time-sensitive value. Emphasize FOMO, limited opportunities, and immediate benefits.',
    'executive-briefing': 'Concise, high-level strategic communication. Bottom-line focused, data-backed recommendations.',
    'casual': 'Conversational and approachable. Friendly tone while maintaining respect.',
    'friendly': 'Warm and personable. Build connection through empathy and positive language.',
    'authoritative': 'Confident and expert-driven. Establish credibility and thought leadership.',
    'consultative': 'Advisory approach. Position as trusted partner offering solutions.',
    'concise': 'Brief, direct messaging. Clear value proposition in minimal words.',
}

def set_db(database):
    global db
    db = database

def set_llm_helper(llm_func):
    global generate_llm_response
    generate_llm_response = llm_func

def set_case_study_manager(manager):
    global case_study_manager
    case_study_manager = manager

# ============== MODELS ==============

class PersonalizationRequest(BaseModel):
    origin_url: Optional[str] = None
    keywords: Optional[List[str]] = []
    notes: Optional[str] = None
    tone: Optional[str] = Field(default="professional")  # data-driven, cxo-focused, professional, concise, consultative
    length: Optional[str] = Field(default="medium")
    style: Optional[str] = Field(default="linkedin")
    selected_case_studies: Optional[List[str]] = []
    auto_pick_case_studies: Optional[bool] = True
    company_context: Optional[str] = None  # Company/user specific context

class PersonalizationResponse(BaseModel):
    id: str
    message: str
    char_count: int

# ============== HELPER FUNCTIONS ==============

def extract_embedded_fields(notes: str):
    """Extract embedded fields from notes string"""
    base_message = ""
    tone = ""
    length = ""
    style = ""

    for line in notes.splitlines():
        line = line.strip()
        if line.lower().startswith("base message:"):
            base_message = line.split(":", 1)[1].strip()
        elif line.lower().startswith("tone:"):
            tone = line.split(":", 1)[1].strip()
        elif line.lower().startswith("length:"):
            length = line.split(":", 1)[1].strip()
        elif line.lower().startswith("style:"):
            style = line.split(":", 1)[1].strip()

    return base_message, tone, length, style

# ============== PERSONALIZATION ROUTES ==============

@router.post("/personalize/generate", response_model=PersonalizationResponse)
async def generate_personalization(request: PersonalizationRequest, current_user: User = Depends(get_current_user)):
    """
    Generates a personalized message with case studies, Zuci News, and company context.
    """

    # Extract inputs safely
    origin_url = request.origin_url or "custom_message"
    keywords_text = ", ".join(request.keywords) if request.keywords else "general outreach"
    notes_text = request.notes or ""
    tone = getattr(request, "tone", "professional")
    length = getattr(request, "length", "medium")
    style = getattr(request, "style", "linkedin")
    # print(style)
    base_message, embedded_tone, embedded_length, embedded_style = extract_embedded_fields(notes_text)
    tone = embedded_tone or tone
    length = embedded_length or length
    # style = embedded_style or style

    # Get tone description
    tone_desc = TONE_DESCRIPTIONS.get(tone, TONE_DESCRIPTIONS['professional'])

    # Get case studies - either auto-pick or use selected
    case_study_text = ""
    case_study_references = []

    if case_study_manager:
        if request.auto_pick_case_studies:
            # Auto-pick based on keywords and notes context
            context_for_matching = f"{keywords_text} {notes_text} {request.company_context or ''}"
            case_study_ids = await case_study_manager.get_recommended_case_studies_for_thread(
                thread_context=context_for_matching,
                objection_type=None,
                service=None
            )
            if case_study_ids:
                case_studies = await case_study_manager.get_case_study_details(case_study_ids)
                for cs in case_studies[:2]:
                    source_url = cs.get('metadata', {}).get('source_url', '')
                    # Only include case studies with valid URLs
                    if source_url and source_url.strip():
                        case_study_references.append({
                            'title': cs.get('title', 'Case Study'),
                            'url': source_url,
                            'summary': cs.get('summary', '')[:150]
                        })
                    else:
                        logger.warning(f"Skipping case study '{cs.get('title')}' - no source URL")
        elif request.selected_case_studies:
            case_studies = await case_study_manager.get_case_study_details(request.selected_case_studies)
            for cs in case_studies[:2]:
                source_url = cs.get('metadata', {}).get('source_url', '')
                # Only include case studies with valid URLs
                if source_url and source_url.strip():
                    case_study_references.append({
                        'title': cs.get('title', 'Case Study'),
                        'url': source_url,
                        'summary': cs.get('summary', '')[:150]
                    })
                else:
                    logger.warning(f"Skipping case study '{cs.get('title')}' - no source URL")

    # Build case study text for prompt
    if case_study_references:
        print('case_study_references')
        case_study_text = "\n=== AVAILABLE CASE STUDIES - USE THESE EXACT LINKS ===\n"
        for idx, cs in enumerate(case_study_references, 1):
            # print(cs)
            case_study_text += f"""
Case Study {idx}:
Title: {cs['title']}
Summary: {cs['summary']}
PDF URL: {cs['url']}
How to include: [{cs['title']}]({cs['url']})

"""
        case_study_text += """
CRITICAL INSTRUCTIONS FOR CASE STUDY LINKS:
1. You MUST use the EXACT PDF URLs provided above
2. Do NOT create fake/placeholder URLs like "https://example.com/..."
3. Do NOT make up case study links
4. Copy the EXACT URL from the "PDF URL:" field above
5. Format as markdown: [Exact Title from above](Exact URL from above)
6. If no case studies provided above, do not mention case studies
"""

    # Company context section
    company_context_text = ""
    if request.company_context:
        company_context_text = f"\n=== COMPANY/USER CONTEXT ===\n{request.company_context}\n"

    # Build style-specific prompts
    if style == 'linkedin':
        print('linked in')
        prompt = f"""
        You generate personalized LinkedIn messages for sales outreach.
        Follow ALL rules strictly.

        === TONE (MANDATORY) ===
        Tone: {tone.upper()}
        Style: {tone_desc}
        Voice: Concise, formal, LinkedIn-appropriate business communication.

        === LINKEDIN MESSAGE STRUCTURE (MANDATORY – FINAL OUTPUT MUST FOLLOW EXACTLY) ===
        Your final output MUST contain ONLY these 5 sections, in this order:

        1. OPENER  
        2. VALUE  
        3. PROOF  
        4. CTA  
        5. CLOSE  

        Each section must be written as a natural LinkedIn message (NO section labels in output).  
        Combine them into one continuous LinkedIn DM.

        STRUCTURE DETAILS:
        1. OPENER: Personalized greeting + reference to their role/company (1 sentence)
        2. VALUE: 1–2 sentences offering an insight relevant to them (RPA / automation / efficiency)
        3. PROOF: MUST include one case study link from the list below.  
           Format EXACTLY:  
          "Here's how we helped [similar company]: [Use Case Study Title from above](Use exact PDF URL from above)"
        4. CTA: Soft, low-pressure ask (quick chat, 10-min call, explore ideas, etc.)
        5. CLOSE: Friendly, professional closing line

        CRITICAL REQUIREMENTS:
        - 120–150 words ONLY
        - Conversational but professional tone suitable for LinkedIn
        - INCLUDE EXACT case study title + URL from the list below
        - DO NOT create new or placeholder URLs
        - DO NOT output headings like "Prospect Insight", "Sales Message", etc.
        - Do NOT include section headers in the final message; write as a normal LinkedIn DM

        === AVAILABLE CASE STUDIES (USE ONLY THESE URLs) ===
        {case_study_text}

        === COMPANY CONTEXT (OPTIONAL FOR PERSONALIZATION) ===
        {company_context_text}

        === USER INPUT ===
        Intent/Draft: {base_message}
        Keywords: {keywords_text}
        Notes: {notes_text}

        === FINAL OUTPUT RULES ===
        - Start with "Hi," then a newline
        - Write a LinkedIn message using the 5-step structure
        - Do NOT include labels like "Opener:", "Value:", etc.
        - End with "Thanks"
        """

    elif style == 'email' or style == 'cold_email':
        prompt = f"""You generate personalized email outreach messages for sales.
Follow ALL rules strictly.

=== TONE (MANDATORY) ===
Tone: {tone.upper()}
Style: {tone_desc}

=== EMAIL STRUCTURE (MANDATORY) ===
1. SUBJECT LINE: Compelling, 5-8 words, create curiosity
2. HOOK: 1-2 sentences, personalized opening
3. BODY: 150-200 words
   - Pain/Challenge acknowledgment
   - Solution with CASE STUDY reference using EXACT PDF link from list above (MANDATORY)
   - Results/outcomes with metrics
4. CTA: Single, clear, low-commitment action
5. SIGNATURE: Best regards,
        Tamil Bharathi
        Manager - Growth
        +1 647 404 2503
        Toronto, ON
        Zuci Systems

CRITICAL REQUIREMENTS:
- MUST include SUBJECT line at the top
- MUST include case study PDF link using EXACT URL from case studies list above
- Professional email format
- Data-driven where appropriate
- DO NOT create fake URLs
{case_study_text}
{company_context_text}

User Intent/Draft:
{base_message}

Additional Context:
- Keywords: {keywords_text}
- Notes: {notes_text}
- Length preference: {length}

OUTPUT INSTRUCTIONS:
- Generate email following structure above
- Start with "Hi," then a newline
- When including case study, select Case Study 1 or Case Study 2 from the list above
- Use the EXACT title and EXACT PDF URL provided
- Integrate the case study naturally in the solution paragraph
- Example format: "We recently helped [similar client] achieve X results. Here's the full story: [Exact Case Study Title from above](Exact PDF URL from above)"
- The P.S. can reference a second case study if multiple are provided
"""

    elif style == 'follow_up':
        prompt = f"""You generate personalized follow-up messages for sales.
Follow ALL rules strictly.

=== TONE (MANDATORY) ===
Tone: {tone.upper()}
Style: {tone_desc}

=== FOLLOW-UP MESSAGE STRUCTURE (MANDATORY) ===
1. SUBJECT LINE: Reference previous interaction, create urgency
2. REMINDER: Brief reference to previous conversation (1 sentence)
3. VALUE ADD: New information, case study, or insight
4. PROOF: Case study reference using EXACT PDF link from list above (MANDATORY)
5. CTA: Specific next step with timeline
6. SIGNATURE: Professional closing

CRITICAL REQUIREMENTS:
- Acknowledge previous interaction
- Provide new value (not just checking in)
- MUST include case study PDF link using EXACT URL from case studies list above
- Create gentle urgency
- 120-150 words
- DO NOT create fake URLs
{case_study_text}
{company_context_text}

User Intent/Draft:
{base_message}

Additional Context:
- Keywords: {keywords_text}
- Notes: {notes_text}

OUTPUT INSTRUCTIONS:
- Generate follow-up message following structure above
- When including case study, use Case Study 1 or Case Study 2 from the list above
- Use the EXACT title and EXACT PDF URL provided
- Integrate naturally as new value to share
- Example format: "Since we last spoke, we helped [company] with [challenge]. See the results: [Exact Case Study Title from above](Exact PDF URL from above)"
"""

    else:
        # Default general format
        prompt = f"""You generate personalized outreach messages for sales.
Follow ALL rules strictly.

=== TONE (MANDATORY) ===
Tone: {tone.upper()}
Style: {tone_desc}

=== MESSAGE STRUCTURE ===
1. Opening: Personalized, relevant
2. Body: Value proposition with case study link using EXACT URL from list above (MANDATORY)
3. Close: Clear CTA
4. Best regards,
        Tamil Bharathi
        Manager - Growth
        +1 647 404 2503
        Toronto, ON
        Zuci Systems

CRITICAL REQUIREMENTS:
- MUST include case study PDF link using EXACT URL from case studies list above
- DO NOT create fake/placeholder URLs
- Use the exact title and URL provided in the case studies section
{case_study_text}
{company_context_text}

User Intent: {base_message}
Keywords: {keywords_text}
Notes: {notes_text}

OUTPUT INSTRUCTIONS:
- Create a {length} {style} message following the tone: {tone}
- Include case study from the list above with exact title and PDF URL
- Format: [Exact Case Study Title](Exact PDF URL)
"""

    # Log case study information for debugging
    if case_study_references:
        logger.info(f"Generating personalization with {len(case_study_references)} case studies:")
        for cs in case_study_references:
            logger.info(f"  - {cs['title']}: {cs['url']}")
    else:
        logger.info("Generating personalization with NO case studies")

    logger.info(f"Tone: {tone}, Style: {style}, Auto-pick: {request.auto_pick_case_studies}")

    # Generate message using LLM helper
    # print(prompt)
    message = await generate_llm_response(prompt)
    # print(message)
    message = message.strip()

    # Prepare record
    person_id = str(uuid.uuid4())
    personalization = {
        "id": person_id,
        "origin_url": origin_url,
        "keywords": request.keywords,
        "notes": request.notes,
        "tone": tone,
        "length": length,
        "style": style,
        "message": message,
        "char_count": len(message),
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    # print(message)

    # Save in DB
    await db.personalizations.insert_one(personalization)

    # Return API response
    return PersonalizationResponse(
        id=person_id,
        message=message,
        char_count=len(message),
    )
