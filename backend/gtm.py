"""
GTM Generator Module
Contains: GTM models, validation, feedback processing, final prompt generation, AgentDB integration
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import logging
import json
import re

from login import User, get_current_user
from gtm_agentdb import GTMAgentDB
from gtm_conversation_db import get_conversation_db
from groq_api import groq_client,generate_llm_response
logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["gtm"])

# Database reference - will be set from server.py
db = None

# Case study manager reference - will be set from server.py
case_study_manager = None

# Initialize AgentDB-based GTM Assistant (per-user instances stored in dict)
gtm_agents = {}

def set_db(database):
    global db
    db = database

def set_llm_helper(llm_func):
    global generate_llm_response
    generate_llm_response = llm_func

def set_groq_client(client):
    global groq_client
    groq_client = client

def set_case_study_manager(manager):
    global case_study_manager
    case_study_manager = manager

def get_or_create_gtm_agent(user_id: str) -> GTMAgentDB:
    """Get or create GTM agent instance for user"""
    if user_id not in gtm_agents:
        gtm_agents[user_id] = GTMAgentDB()
    return gtm_agents[user_id]

# ============== MODELS ==============

class GTMRequest(BaseModel):
    company_name: str
    linkedin_url: Optional[str] = None
    offering: str
    pain_points: List[str]
    personas: List[str]
    target_persons: List[str]

class GTMValidateRequest(BaseModel):
    company_name: str
    industry: str
    linkedin_url: Optional[str] = None
    offering: str
    pain_points: List[str]
    target_personas: List[str]
    use_cases: Optional[List[str]] = []
    key_features: Optional[List[str]] = []

class GTMValidationResponse(BaseModel):
    has_use_cases: bool
    use_case_count: int
    industry_match: bool
    validation_notes: List[str]
    suggestions: List[str]
    relevant_use_cases: Optional[List[Dict[str, Any]]] = []

class GTMFeedbackRequest(BaseModel):
    feedback: str
    validation_result: Dict[str, Any]
    form_data: Dict[str, Any]

class GTMFinalPromptRequest(BaseModel):
    form_data: Dict[str, Any]
    validation_result: Dict[str, Any]

class GTMResponse(BaseModel):
    id: str
    prompt: str
    status: str

# ============== HELPER FUNCTIONS ==============

async def get_industry_use_cases_from_db(industry: str) -> List[Dict[str, Any]]:
    """Fetch industry-specific use cases from document_files collection"""
    try:
        docs = await db.document_files.find(
            {"$or": [
                {"category": {"$regex": industry, "$options": "i"}},
                {"summary": {"$regex": industry, "$options": "i"}}
            ]},
            {"_id": 0, "filename": 1, "summary": 1, "category": 1}
        ).limit(5).to_list(5)

        use_cases = []
        for doc in docs:
            use_cases.append({
                'title': doc.get('filename', 'Case Study').replace('.pdf', ''),
                'description': doc.get('summary', '')[:100],
                'impact': f"Reference: {doc.get('category', 'General')}"
            })

        return use_cases
    except Exception as e:
        logger.error(f"Error fetching industry use cases: {str(e)}")
        return []

async def extract_information_with_llm_full_context(
        user_message: str,
        conversation_history: List[Dict],
        current_context: Dict
) -> Optional[Dict]:
    """
    Use LLM to intelligently extract information WITH FULL CONVERSATION CONTEXT
    """
    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history[-10:]
    ])

    extraction_prompt = f"""You are an INTELLIGENT AI assistant for extracting and organizing microsite content from natural language commands.

CONVERSATION HISTORY:
{conversation_text}

CURRENT USER MESSAGE:
"{user_message}"

ACCUMULATED CONTEXT SO FAR:
{json.dumps(current_context, indent=2)}

Your task is to INTELLIGENTLY understand user commands and extract structured information:

=== COMMAND PATTERNS YOU MUST RECOGNIZE ===

1. **ADD commands** (append to existing content):
   - "add offering as 24*7 support" → Add "24*7 support" to key_features section
   - "add manual process in pain points" → Add "manual process" to pain_points section
   - "include agent ai" → Add "agent ai" to appropriate section based on context
   - "also add CEO details" → Extract CEO info and add to ceo_details section

2. **REMOVE commands** (delete from content):
   - "remove data engineering case studies" → Mark for removal from case_studies section
   - "don't include pricing" → Remove pricing from key_features
   - "take out the team section" → Remove from customer_profile

3. **MODIFY commands** (update existing):
   - "change color to blue" → Update ui_personalization section
   - "make it more technical" → Update tone in design_requirements
   - "update pain points to focus on speed" → Modify pain_points section

4. **IMPLICIT additions** (no explicit command):
   - "our CEO is John Smith" → Add to ceo_details
   - "we offer 24*7 support" → Add to key_features
   - "customers struggle with manual processes" → Add to pain_points

=== SECTION MAPPING (CRITICAL) ===

Target sections and what belongs there:
- **key_features**: Offerings, capabilities, services, features, "what we offer", "24*7 support", etc.
- **pain_points**: Problems, challenges, issues, struggles, "manual process", "slow", etc.
- **solution**: Solutions, how we solve problems, "agent ai", "our approach", etc.
- **ceo_details**: Leadership, CEO, founder, executive information
- **ui_personalization**: Design, colors, styles, UI preferences
- **customer_profile**: Target customers, personas, buying behavior
- **design_requirements**: Technical design specs, layout preferences
- **case_studies**: Case study references, social proof (can be removed)

=== OUTPUT FORMAT ===

Respond in JSON format:
{{
  "action": "add" | "remove" | "modify" | "unclear",
  "extracted": {{
    "company_info": {{}},
    "people": [],
    "features": [],
    "pain_points": [],
    "metrics": [],
    "design_preferences": [],
    "customer_insights": [],
    "case_study_actions": {{"add": [], "remove": []}}
  }},
  "target_section": "section_key_where_this_belongs",
  "content": "cleaned and formatted content for that section",
  "is_substantial": true,
  "summary": "brief summary of what was extracted",
  "references_previous": false,
  "removal_targets": []
}}

=== CRITICAL RULES ===

1. **Be LIBERAL with extraction** - if user mentions ANYTHING relevant, extract it
2. **Understand CONTEXT** - "add that" refers to previous messages
3. **Map INTELLIGENTLY** - "24*7 support" is clearly a feature, "manual process" is clearly a pain point
4. **Handle COMMANDS** - "add", "remove", "include", "don't include" are action verbs
5. **Clean CONTENT** - Format professionally: "24*7 support" → "24/7 Support Service"
6. **Set action field** - Use "add", "remove", "modify" based on user intent
7. **For removals** - Populate removal_targets array with items to remove

=== EXAMPLES ===

Input: "add offering as 24*7 support"
Output: {{"action": "add", "extracted": {{"features": ["24/7 Support Service"]}}, "target_section": "key_features", "content": "24/7 Support Service", "is_substantial": true, "summary": "Added 24/7 support to offerings"}}

Input: "add manual process in pain points"
Output: {{"action": "add", "extracted": {{"pain_points": ["Manual processes creating bottlenecks"]}}, "target_section": "pain_points", "content": "Manual processes creating bottlenecks and inefficiency", "is_substantial": true, "summary": "Added manual process pain point"}}

Input: "remove data engineering case studies"
Output: {{"action": "remove", "target_section": "case_studies", "removal_targets": ["data engineering"], "is_substantial": true, "summary": "Removed data engineering case studies"}}
"""

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured information from conversations with full context awareness."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content

        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        print(json_match)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")

    return None

# ============== GTM ROUTES ==============

@router.post("/gtm/validate", response_model=GTMValidationResponse)
async def validate_gtm_data(request: GTMValidateRequest, current_user: User = Depends(get_current_user)):
    """Validate GTM data and check for relevant use cases - DYNAMIC from DB"""
    industry = request.industry

    relevant_use_cases = await get_industry_use_cases_from_db(industry)
    has_use_cases = len(relevant_use_cases) > 0
    use_case_count = len(relevant_use_cases)

    validation_notes = []
    suggestions = []

    if has_use_cases:
        validation_notes.append(f"Found {use_case_count} industry-specific case studies for {industry} from your document library")
    else:
        validation_notes.append(f"No specific case studies for {industry} in database. Will use general best practices.")
        suggestions.append("Consider uploading industry-specific case studies to strengthen your microsite")

    if len(request.pain_points) < 2:
        suggestions.append("Adding more pain points will create a more compelling narrative")

    if not request.key_features or len(request.key_features) < 3:
        suggestions.append("Include at least 3 key features to highlight your solution's capabilities")

    # AI-powered validation
    validation_prompt = f"""
Analyze this GTM data and provide validation insights:

Company: {request.company_name}
Industry: {industry}
Offering: {request.offering}
Pain Points: {', '.join(request.pain_points)}

Provide 2-3 specific suggestions to improve the microsite effectiveness.
Format: Simple bullet points, each under 15 words.
"""

    try:
        ai_suggestions = await generate_llm_response(validation_prompt)
        for line in ai_suggestions.split('\n'):
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                clean_suggestion = line.lstrip('-•0123456789. ').strip()
                if clean_suggestion and len(clean_suggestion) > 10:
                    suggestions.append(clean_suggestion)
    except:
        pass

    return GTMValidationResponse(
        has_use_cases=has_use_cases,
        use_case_count=use_case_count,
        industry_match=True,
        validation_notes=validation_notes,
        suggestions=suggestions[:5],
        relevant_use_cases=relevant_use_cases
    )

@router.post("/gtm/process-feedback")
async def process_gtm_feedback(request: GTMFeedbackRequest, current_user: User = Depends(get_current_user)):
    """INTELLIGENT GTM AI Assistant with FULL CONVERSATION HISTORY"""
    feedback = request.feedback.strip()
    form_data = request.form_data
    validation = request.validation_result

    conv_db = get_conversation_db()
    session_id = conv_db.get_or_create_active_session(current_user.id, form_data)
    full_context = conv_db.get_full_context(session_id)
    conversation_history = full_context.get('conversation_history', [])

    user_msg_id = conv_db.add_message(
        session_id=session_id,
        user_id=current_user.id,
        role='user',
        content=feedback
    )

    conversation_history.append({
        'role': 'user',
        'content': feedback
    })

    agent = get_or_create_gtm_agent(current_user.id)

    # Load previous section states from database
    if full_context.get('section_states'):
        for section_key, section_data in full_context['section_states'].items():
            if section_key in agent.prompt_sections:
                agent.prompt_sections[section_key].content = section_data.get('content', '')
                agent.prompt_sections[section_key].subsections = section_data.get('subsections', {})

    # Load extracted entities from database
    if full_context.get('extracted_entities'):
        for entity in full_context['extracted_entities']:
            entity_type = entity.get('entity_type')
            entity_data = entity.get('entity_data', {})

            if entity_type in agent.extracted_entities:
                if isinstance(agent.extracted_entities[entity_type], list):
                    if entity_data not in agent.extracted_entities[entity_type]:
                        agent.extracted_entities[entity_type].append(entity_data)
                elif isinstance(agent.extracted_entities[entity_type], dict):
                    agent.extracted_entities[entity_type].update(entity_data)

    extraction_result = await extract_information_with_llm_full_context(
        user_message=feedback,
        conversation_history=conversation_history,
        current_context=agent._get_current_context()
    )

    if extraction_result:
        conv_db.add_message(
            session_id=session_id,
            user_id=current_user.id,
            role='system',
            content='[Extraction performed]',
            extraction_data=extraction_result
        )

        if extraction_result.get('extracted'):
            for entity_type, entity_data in extraction_result['extracted'].items():
                if entity_data:
                    conv_db.add_extracted_entity(
                        session_id=session_id,
                        user_id=current_user.id,
                        entity_type=entity_type,
                        entity_data=entity_data,
                        source_message_id=user_msg_id
                    )

    result = agent.process_user_input(
        user_message=feedback,
        form_data=form_data,
        validation_result=validation,
        llm_extract_func=lambda msg, ctx: extraction_result
    )

    # Save updated section states to database
    section_states = {}
    for section_key, section_obj in agent.prompt_sections.items():
        if section_obj.content or section_obj.subsections:
            section_states[section_key] = {
                'content': section_obj.content,
                'subsections': section_obj.subsections,
                'priority': section_obj.priority
            }

    conv_db.update_section_states(session_id, section_states)

    conv_db.add_message(
        session_id=session_id,
        user_id=current_user.id,
        role='assistant',
        content=result.get('message', ''),
        section_updates=section_states
    )

    if result.get("should_regenerate"):
        logger.info(f"Generating final prompt for session {session_id} with full context")

        offering_keywords = form_data.get('offering', '').lower()
        industry = form_data.get('industry', '').lower()

        search_terms = [industry]
        common_tech_terms = ['ai', 'automation', 'analytics', 'cloud', 'machine learning',
                             'data', 'rpa', 'crm', 'saas', 'platform', 'api', 'integration',
                             'workflow', 'optimization', 'fintech', 'healthcare', 'ecommerce']

        for term in common_tech_terms:
            if term in offering_keywords or term in industry:
                search_terms.append(term)

        search_conditions = []
        for term in search_terms:
            search_conditions.append({"summary": {"$regex": term, "$options": "i"}})
            search_conditions.append({"category": {"$regex": term, "$options": "i"}})
            search_conditions.append({"filename": {"$regex": term, "$options": "i"}})

        fetched_case_studies = []
        if search_conditions:
            case_studies_cursor = db.document_files.find(
                {"$or": search_conditions},
                {"_id": 0, "id": 1, "filename": 1, "summary": 1, "category": 1, "metadata": 1}
            ).limit(5)
            fetched_case_studies = await case_studies_cursor.to_list(5)

        logger.info(f"Found {len(fetched_case_studies)} case studies for {industry}")

        # Fetch latest Zuci news
        zuci_news_text = ""
        if case_study_manager:
            zuci_news_items = await case_study_manager.get_latest_zuci_news(max_results=2)
            if zuci_news_items:
                zuci_news_text = "\n\n## 📰 Latest Company News\n"
                zuci_news_text += "**Include these recent achievements to build credibility:**\n\n"
                for idx, news in enumerate(zuci_news_items, 1):
                    news_link = news.get('news_link', '')
                    zuci_news_text += f"### {idx}. {news.get('title', 'News Update')}\n"
                    zuci_news_text += f"- **Description**: {news.get('description', '')}\n"
                    zuci_news_text += f"- **Published**: {news.get('published_date', '')}\n"
                    if news_link:
                        zuci_news_text += f"- **Link**: {news_link}\n"
                        zuci_news_text += f"- **Markdown Format**: [{news.get('title', 'News')}]({news_link})\n"
                    zuci_news_text += "\n"
                zuci_news_text += "**INSTRUCTION**: Include at least one news item naturally in the microsite (preferably in the credibility/about section or footer) with a clickable link.\n"
                logger.info(f"Added {len(zuci_news_items)} Zuci news items to GTM prompt")

        final_prompt_text = agent.build_final_prompt(
            form_data=form_data,
            validation_result=validation,
            case_studies=fetched_case_studies
        )

        # Append zuci_news to final prompt
        if zuci_news_text:
            final_prompt_text += zuci_news_text

        user_adjustments = []
        for msg in conversation_history:
            if msg['role'] == 'user' and msg['content'] not in ['1', '2', '3', 'yes', 'generate', 'go ahead']:
                user_adjustments.append(msg['content'])

        user_adjustments_text = "\n\n".join([f"- {adj}" for adj in user_adjustments if len(adj) > 10])

        if user_adjustments_text:
            final_prompt_text += f"\n\n## 💬 User-Provided Context & Requirements\n\n{user_adjustments_text}\n"

        gtm_id = str(uuid.uuid4())
        gtm_record = {
            "id": gtm_id,
            "session_id": session_id,
            "company_name": form_data.get('company_name'),
            "industry": form_data.get('industry'),
            "offering": form_data.get('offering'),
            "prompt": final_prompt_text,
            "validation_data": validation,
            "case_studies_used": [cs.get('filename', '') for cs in fetched_case_studies],
            "conversation_history": conversation_history,
            "user_adjustments": user_adjustments,
            "extracted_context": agent._build_extracted_context(),
            "section_states": section_states,
            "status": "prompt_generated",
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        await db.gtm_assets.insert_one(gtm_record)
        conv_db.close_session(session_id)

        result['final_prompt'] = {
            "id": gtm_id,
            "prompt": final_prompt_text,
            "status": "prompt_generated",
            "case_studies_count": len(fetched_case_studies),
            "conversation_messages": len(conversation_history),
            "user_adjustments_count": len(user_adjustments)
        }

        logger.info(f"Generated prompt with {len(conversation_history)} messages and {len(user_adjustments)} user adjustments")

    return result

@router.post("/gtm/reset-conversation")
async def reset_gtm_conversation(current_user: User = Depends(get_current_user)):
    """Reset conversation history for current user"""
    conv_db = get_conversation_db()
    conv_db.clear_user_sessions(current_user.id)

    if current_user.id in gtm_agents:
        del gtm_agents[current_user.id]

    return {
        "success": True,
        "message": "Conversation history reset successfully"
    }

@router.get("/gtm/conversation-history")
async def get_gtm_conversation_history(current_user: User = Depends(get_current_user)):
    """Get conversation history for current user's active session"""
    conv_db = get_conversation_db()

    conn = conv_db.get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT session_id FROM sessions
        WHERE user_id = ? AND status = 'active'
        ORDER BY updated_at DESC
        LIMIT 1
    """, (current_user.id,))

    row = cursor.fetchone()

    if not row:
        return {
            "session_id": None,
            "conversation_history": [],
            "message_count": 0
        }

    session_id = row['session_id']
    full_context = conv_db.get_full_context(session_id)

    return {
        "session_id": session_id,
        "conversation_history": full_context.get('conversation_history', []),
        "message_count": full_context.get('message_count', 0),
        "section_states": full_context.get('section_states', {}),
        "status": full_context.get('status', 'unknown')
    }

@router.post("/gtm/generate-final-prompt")
async def generate_final_gtm_prompt(request: GTMFinalPromptRequest, current_user: User = Depends(get_current_user)):
    """Generate final optimized prompt for microsite creation with ALL user inputs."""
    form_data = request.form_data
    validation = request.validation_result

    user_adjustments = form_data.get('user_adjustments', '')
    print(user_adjustments)
    user_adjustments_section = ""

    conv_db = get_conversation_db()
    session_id = conv_db.get_or_create_active_session(current_user.id, form_data)
    full_context = conv_db.get_full_context(session_id)
    conversation_history = full_context.get('conversation_history', [])

    user_adjustments_list = []
    for msg in conversation_history:
        if msg['role'] == 'user' and msg['content'] not in ['1', '2', '3', 'yes', 'generate', 'go ahead']:
            user_adjustments_list.append(msg['content'])

    if user_adjustments or user_adjustments_list:
        refinement_prompt = f"""You are an expert at refining user input into professional microsite requirements.

User provided these additional details:
{user_adjustments}
{chr(10).join(user_adjustments_list)}

Your task:
1. Extract key information about design preferences, content requirements, features, or any specific requests
2. Organize them into clear, actionable points
3. Remove any conversational filler
4. Keep technical terms and specific requirements intact
5. Format as bullet points under relevant categories

Categories to use (only include if relevant):
- Design & UI: visual preferences, layout, colors, style
- Content: specific text, messaging, tone adjustments
- Features: interactive elements, functionality requests
- Personalization: company-specific details (CEO, team, pricing, etc.)
- Technical: integrations, performance requirements

Output format:
## Category Name
- Specific requirement 1
- Specific requirement 2

Only include categories that have content. Be concise and professional."""

        try:
            refined_adjustments = await generate_llm_response(refinement_prompt)
            user_adjustments_section = f"\n\n## 📝 Additional Requirements\n{refined_adjustments}\n"
        except Exception as e:
            logger.error(f"Error refining user adjustments: {str(e)}")
            user_adjustments_section = f"\n\n## 📝 Additional Details from User\n{user_adjustments}\n"

    # Process pain points
    pain_points = form_data.get('pain_points', '')
    if isinstance(pain_points, str):
        pain_points_list = [pp.strip() for pp in pain_points.split(',') if pp.strip()]
    else:
        pain_points_list = pain_points
    pain_points_text = "\n".join([f"- {pp}" for pp in pain_points_list])

    # Process customer profile details
    customer_profile_details = form_data.get('customer_profile_details', '')
    customer_profile_section = ""
    if customer_profile_details:
        profile_refinement_prompt = f"""Refine this customer profile information into clear, professional bullet points.

User input: {customer_profile_details}

Extract and organize:
- Customer demographics (company size, industry, location)
- Buying behavior and decision-making process
- Key stakeholders and their roles
- Pain points and challenges
- Budget considerations
- Timeline and urgency

Remove conversational language. Output as clean bullet points under relevant sub-headings.
Only include sub-headings that have content."""

        try:
            refined_profile = await generate_llm_response(profile_refinement_prompt)
            customer_profile_section = f"\n\n## 👥 Customer Profile\n{refined_profile}\n"
        except:
            customer_profile_section = f"\n\n## 👥 Customer Profile Details\n{customer_profile_details}\n"

    # Process key features
    key_features = form_data.get('key_features', '')
    if isinstance(key_features, str):
        features_list = [ft.strip() for ft in key_features.split(',') if ft.strip()]
    else:
        features_list = key_features
    features_text = "\n".join([f"- {ft}" for ft in features_list])

    # Process target personas
    target_personas = form_data.get('target_personas', '')
    if isinstance(target_personas, str):
        personas_list = [p.strip() for p in target_personas.split(',') if p.strip()]
    else:
        personas_list = target_personas
    personas_text = ", ".join(personas_list)

    # Process use cases
    user_use_cases = form_data.get('use_cases', '')
    user_use_cases_text = ""
    if user_use_cases:
        if isinstance(user_use_cases, str):
            use_cases_list = [uc.strip() for uc in user_use_cases.split(',') if uc.strip()]
        else:
            use_cases_list = user_use_cases
        if use_cases_list:
            user_use_cases_text = "\n\nUser-Specified Use Cases:\n"
            user_use_cases_text += "\n".join([f"- {uc}" for uc in use_cases_list])

    # Fetch case studies
    offering_keywords = form_data.get('offering', '').lower()
    industry = form_data.get('industry', '').lower()

    selected_doc_ids = form_data.get('selected_documents', [])
    auto_pick = form_data.get('auto_pick_documents', False)

    search_terms = [industry]
    common_tech_terms = ['ai', 'automation', 'analytics', 'cloud', 'machine learning', 'data', 'rpa',
                         'crm', 'saas', 'platform', 'api', 'integration', 'workflow', 'optimization',
                         'fintech', 'healthcare', 'ecommerce', 'retail', 'manufacturing']

    for term in common_tech_terms:
        if term in offering_keywords or term in industry:
            search_terms.append(term)

    fetched_case_studies = []
    try:
        if selected_doc_ids and not auto_pick:
            case_studies_cursor = db.document_files.find(
                {"id": {"$in": selected_doc_ids}},
                {"_id": 0, "id": 1, "filename": 1, "summary": 1, "category": 1, "metadata": 1}
            )
            fetched_case_studies = await case_studies_cursor.to_list(len(selected_doc_ids))
            logger.info(f"Using {len(fetched_case_studies)} user-selected case studies")
        else:
            search_conditions = []
            for term in search_terms:
                search_conditions.append({"summary": {"$regex": term, "$options": "i"}})
                search_conditions.append({"category": {"$regex": term, "$options": "i"}})
                search_conditions.append({"filename": {"$regex": term, "$options": "i"}})

            if search_conditions:
                case_studies_cursor = db.document_files.find(
                    {"$or": search_conditions},
                    {"_id": 0, "id": 1, "filename": 1, "summary": 1, "category": 1, "metadata": 1}
                ).limit(5)
                fetched_case_studies = await case_studies_cursor.to_list(5)

            logger.info(f"Auto-picked {len(fetched_case_studies)} case studies for {industry}")
    except Exception as e:
        logger.error(f"Error fetching case studies: {str(e)}")
        fetched_case_studies = []

    # Format case studies section
    case_studies_section = ""
    if fetched_case_studies:
        case_studies_section = "\n\n## 📚 Relevant Case Studies (Dynamically Fetched)\n"
        case_studies_section += "**These are REAL case studies from your database. Use them to add credibility:**\n\n"

        for idx, cs in enumerate(fetched_case_studies, 1):
            title = cs.get('filename', 'Untitled').replace('.pdf', '').replace('_', ' ')
            summary = cs.get('summary', 'No summary available')[:300]
            category = cs.get('category', 'General')
            metadata = cs.get('metadata', {})
            source_url = metadata.get('source_url', '')

            case_studies_section += f"### {idx}. {title}\n"
            case_studies_section += f"- **Category**: {category}\n"
            if summary:
                case_studies_section += f"- **Summary**: {summary}...\n"
            if source_url:
                case_studies_section += f"- **Link**: {source_url}\n"
            case_studies_section += "\n"
    else:
        case_studies_section = "\n\n## 📚 Case Studies\n"
        case_studies_section += "*Note: No relevant case studies found in database. Consider adding industry-specific examples manually.*\n\n"

    # Build industry-specific use cases section
    industry_use_cases_text = ""
    if validation.get('relevant_use_cases'):
        industry_use_cases_text = "\n\n## 💡 Industry-Specific Use Cases\n"
        for uc in validation['relevant_use_cases'][:3]:
            industry_use_cases_text += f"- **{uc['title']}**: {uc['description']} ({uc['impact']})\n"

    # Fetch latest Zuci news
    zuci_news_text = ""
    if case_study_manager:
        zuci_news_items = await case_study_manager.get_latest_zuci_news(max_results=2)
        if zuci_news_items:
            zuci_news_text = "\n\n## 📰 Latest Company News\n"
            zuci_news_text += "**Include these recent achievements to build credibility and trust:**\n\n"
            for idx, news in enumerate(zuci_news_items, 1):
                news_link = news.get('news_link', '')
                zuci_news_text += f"### {idx}. {news.get('title', 'News Update')}\n"
                zuci_news_text += f"- **Description**: {news.get('description', '')}\n"
                zuci_news_text += f"- **Published**: {news.get('published_date', '')}\n"
                if news_link:
                    zuci_news_text += f"- **Link**: {news_link}\n"
                    zuci_news_text += f"- **Markdown Format**: [{news.get('title', 'News')}]({news_link})\n"
                zuci_news_text += "\n"
            zuci_news_text += "**CRITICAL**: You MUST include at least ONE news item in the microsite with a clickable link. Best placement:\n"
            zuci_news_text += "- In the 'About Us' or company credibility section\n"
            zuci_news_text += "- In the footer as 'Recent News' or 'Latest Updates'\n"
            zuci_news_text += "- As a banner or announcement strip at the top\n"
            logger.info(f"Added {len(zuci_news_items)} Zuci news items to GTM final prompt")

    # Build final prompt
    final_prompt = f"""Create a high-converting, interactive microsite for prospecting **{form_data['company_name']}** in the **{form_data['industry']}** industry.

## 🎯 Objective
Generate a modern, engaging single-page microsite that convinces decision-makers at {form_data['company_name']} to book a meeting. The site should be visually stunning, interactive, and mobile-responsive.

## 🏢 Prospect Profile
- **Company**: {form_data['company_name']}
- **Industry**: {form_data['industry']}
- **Decision Makers**: {personas_text}
- **LinkedIn**: {form_data.get('linkedin_url', 'N/A')}

## 💡 Our Solution
{form_data['offering']}
{user_adjustments_section}
{customer_profile_section}

## 🎯 Pain Points to Address
{pain_points_text}

## ✨ Key Features to Highlight
{features_text if features_text else '- Innovative technology\\n- Proven results\\n- Industry expertise'}
{user_use_cases_text}
{industry_use_cases_text}
{case_studies_section}
{zuci_news_text}

## 🎨 Design Requirements

### Hero Section
- Bold headline addressing their #1 pain point
- Subheadline explaining the solution
- Compelling CTA button: "Book a 15-Min Discovery Call"
- Background: Modern gradient (blue/purple tones) with subtle animations
- Include company logo placeholder

### Pain Points Section
- 3-column grid with icons
- Each pain point with: Icon, Title, Brief description, Hover effects

### Solution Overview
- Split layout (50/50)
- Left: Feature highlights with checkmarks
- Right: Interactive demo mockup or animated graphic

### Use Cases / Results
- Carousel or card grid showing specific use cases with expected outcomes

### Social Proof
- Client logos or testimonial cards
- Include metrics from case studies if available

### Call-to-Action Section
- Bold CTA: "Ready to Transform Your Operations?"
- Meeting scheduler or contact form

## 🛠 Technical Requirements
- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS with custom animations
- **Icons**: Lucide React
- **Responsive**: Mobile-first design

## 🎨 Color Palette
- Primary: Modern blue/indigo (#4F46E5)
- Secondary: Purple (#7C3AED)
- Accent: Green for success metrics (#10B981)
- Background: White with subtle gray sections (#F9FAFB)

## ✅ Deliverable
A complete, production-ready React component that can be deployed immediately.

**Make it stunning, interactive, and conversion-focused!**
"""

    gtm_id = str(uuid.uuid4())

    gtm_record = {
        "id": gtm_id,
        "company_name": form_data['company_name'],
        "industry": form_data['industry'],
        "offering": form_data['offering'],
        "prompt": final_prompt,
        "validation_data": validation,
        "case_studies_used": [cs.get('filename', '') for cs in fetched_case_studies],
        "user_adjustments": user_adjustments,
        "status": "prompt_generated",
        "created_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.gtm_assets.insert_one(gtm_record)

    return {
        "id": gtm_id,
        "prompt": final_prompt,
        "status": "prompt_generated",
        "case_studies_count": len(fetched_case_studies)
    }

@router.post("/gtm/generate-prompt", response_model=GTMResponse)
async def generate_gtm_prompt(request: GTMRequest, current_user: User = Depends(get_current_user)):
    gtm_id = str(uuid.uuid4())

    pain_points_text = ", ".join(request.pain_points)
    personas_text = ", ".join(request.personas)
    targets_text = ", ".join(request.target_persons)

    prompt = f"""
    You are an expert at creating prompts for AI-based landing page builders (like lovable.net).
    Your task is to generate a **ready-to-paste prompt** that a user can paste into a landing page builder to automatically create a microsite or interactive web app for the company {request.company_name} (LinkedIn: {request.linkedin_url}) with our offering "{request.offering}".

    Use the following details in your prompt for the builder:
    - **Target Personas / Decision Makers**: {targets_text}
    - **Pain Points**: {pain_points_text}
    - **Proposal / Solution**: {request.offering}
    - **Design Style**: modern, clean, professional, with subtle animations, cards, icons, or infographics
    - **Interaction**: allow interactivity like hover, accordion, tabs, or click-to-expand
    - **Call to Action**: clear CTA for scheduling a meeting or demo
    - **Personalization**: optionally show the company name in header or welcome message

    Your output should be **only the prompt text** that can be pasted into a landing page builder.
    Do NOT generate HTML, CSS, or JS.
    Make it clear, concise, and persuasive.
    """

    generated_prompt = await generate_llm_response(prompt, "You are an expert at creating website prompts for landing page builders.")

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

@router.get("/gtm")
async def get_gtm_assets(current_user: User = Depends(get_current_user)):
    assets = await db.gtm_assets.find({"created_by": current_user.id}, {"_id": 0}).to_list(1000)
    return assets