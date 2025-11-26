"""
Thread Intelligence Module
Contains: Thread analysis models and routes for analyzing email threads
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime, timezone
import logging
import json

from login import User, get_current_user

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api", tags=["thread_intelligence"])

# Database reference - will be set from server.py
db = None

# LLM helper reference - will be set from server.py
generate_llm_response = None

# Case study manager reference - will be set from server.py
case_study_manager = None

# Tone descriptions for LLM prompts - consistent with Agent Builder and Personalization Assistant
TONE_DESCRIPTIONS = {
    'professional': 'Formal, polished business communication. Respectful and direct.',
    'data-driven': 'Lead with metrics, ROI, quantifiable outcomes. Use specific numbers and percentages.',
    'formal-human': 'Professional yet personable. Balance formality with warmth and authenticity.',
    'cxo-pitch': 'Strategic, executive-level language. Address business priorities like cost reduction, revenue growth, competitive advantage.',
    'cxo-focused': 'Strategic, executive-level language. Address business priorities like cost reduction, revenue growth, competitive advantage.',  # Legacy support
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

class ThreadAnalyzeRequest(BaseModel):
    thread_text: str
    custom_inputs: str = ""
    agent_id: Optional[str] = None
    tone: str = "professional"  # All tone options from Agent Builder
    selected_case_studies: List[str] = []
    auto_pick_case_studies: bool = True

class ThreadAnalysisResponse(BaseModel):
    id: str
    summary: str
    detected_stage: str
    sentiment: str
    response: str
    ai_followup: Optional[str] = None

# ============== THREAD INTELLIGENCE ROUTES ==============

@router.post("/thread/analyze", response_model=ThreadAnalysisResponse)
async def analyze_thread(request: ThreadAnalyzeRequest, current_user: User = Depends(get_current_user)):
    # Get tone description
    tone_desc = TONE_DESCRIPTIONS.get(request.tone, TONE_DESCRIPTIONS['professional'])

    # Get case studies - either auto-pick or use selected
    case_study_text = ""
    case_study_references = []

    if case_study_manager:
        if request.auto_pick_case_studies:
            # Auto-pick based on thread context
            logger.info("Attempting auto-pick case studies...")
            case_study_ids = await case_study_manager.get_recommended_case_studies_for_thread(
                thread_context=request.thread_text,
                objection_type=None,
                service=None
            )

            if case_study_ids:
                case_studies = await case_study_manager.get_case_study_details(case_study_ids)
                logger.info(f"Auto-pick found {len(case_studies)} case studies")
                for cs in case_studies[:2]:
                    source_url = cs.get('metadata', {}).get('source_url', '')
                    logger.info(f"Processing case study: {cs.get('title')} - URL: {source_url}")
                    # Only include case studies with valid URLs
                    if source_url and source_url.strip():
                        case_study_references.append({
                            'title': cs.get('title', 'Case Study'),
                            'url': source_url,
                            'summary': cs.get('summary', '')[:200]
                        })
                        logger.info(f"Added case study: {cs.get('title')}")
                    else:
                        logger.warning(f"Skipping case study '{cs.get('title')}' - no valid source URL")
            else:
                logger.warning("Auto-pick found no matching case studies - trying to get any available case studies")

            # Always try fallback if we don't have case studies yet
            if not case_study_references:
                # Fallback: Get any available case studies from document_files collection
                try:
                    # Query document_files collection (not documents)
                    # Filter for documents with valid titles and summaries
                    all_docs = await db.document_files.find({
                        'title': {'$ne': 'Untitled'},
                        'summary': {'$exists': True, '$ne': ''}
                    }).limit(3).to_list(3)

                    logger.info(f"Fallback found {len(all_docs)} case studies in database")
                    for doc in all_docs:
                        source_url = doc.get('metadata', {}).get('source_url', '')
                        title = doc.get('title', 'Case Study')
                        logger.info(f"Fallback processing: {title} - URL: {source_url}")
                        if source_url and source_url.strip() and title and title != 'Untitled':
                            case_study_references.append({
                                'title': title,
                                'url': source_url,
                                'summary': doc.get('summary', '')[:200]
                            })
                            logger.info(f"Fallback added: {title}")
                        else:
                            logger.warning(f"Skipping case study '{title}' - no valid source URL or title")
                except Exception as e:
                    logger.error(f"Error in fallback case study fetch: {e}")
                    import traceback
                    logger.error(f"Traceback: {traceback.format_exc()}")

        elif request.selected_case_studies:
            # Use manually selected case studies
            logger.info(f"Using {len(request.selected_case_studies)} manually selected case studies")
            case_studies = await case_study_manager.get_case_study_details(request.selected_case_studies)
            for cs in case_studies[:2]:
                source_url = cs.get('metadata', {}).get('source_url', '')
                logger.info(f"Processing case study: {cs.get('title')} - URL: {source_url}")
                # Only include case studies with valid URLs
                if source_url and source_url.strip():
                    case_study_references.append({
                        'title': cs.get('title', 'Case Study'),
                        'url': source_url,
                        'summary': cs.get('summary', '')[:200]
                    })
                    logger.info(f"Added case study: {cs.get('title')}")
                else:
                    logger.warning(f"Skipping case study '{cs.get('title')}' - no valid source URL")
        else:
            logger.info("No case studies selected (auto-pick disabled and no manual selection)")
    else:
        logger.error("case_study_manager is None - cannot fetch case studies")

    # Build case study text for prompt
    logger.info(f"Final case_study_references count: {len(case_study_references)}")
    #print('case_study_references',case_study_references)

    if case_study_references:
        case_study_text = "\n=== AVAILABLE CASE STUDIES - USE THESE EXACT LINKS ===\n"
        for idx, cs in enumerate(case_study_references, 1):
           # print('case_study_text',case_study_text)
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
6. Include at least one case study link in your response
"""
    else:
        case_study_text = """
=== NO CASE STUDIES AVAILABLE ===
CRITICAL: There are NO case studies available for this thread.
DO NOT create any case study links.
DO NOT mention case studies.
DO NOT include any URLs like "https://example.com/..." or similar.
Write your response WITHOUT any case study references.
"""
        logger.warning("No case studies available - instructing LLM to skip case study references")

    prompt = f"""You are an email-thread analysis assistant. Follow ALL rules carefully.

        TASKS:
        1. Read and understand the entire email thread.
        2. Produce:
           - A concise summary
           - Stage: "Cold", "Warm", or "Hot"
           - Sentiment: "Positive", "Neutral", or "Negative"
           - A professional response following the EMAIL-COPYWRITING STRUCTURE below
        
        === RESPONSE TONE (MANDATORY) ===
        Tone: {request.tone.upper()}
        Style: {tone_desc}
        
        === EMAIL-COPYWRITING STRUCTURE FOR RESPONSE ===
        1. HOOK: 1-2 sentences acknowledging the thread context
        2. BODY: 2-3 paragraphs
           - Address the key points from the thread
           - CRITICAL: Include case study reference using EXACT PDF link from list above
           - Format: "We recently helped [company] achieve [result]. See the details: [Use exact case study title](Use exact PDF URL)"
           - Lead with data/metrics where appropriate
        3. CTA: Clear, low-commitment next step
        4. SIGNATURE: ALWAYS end with this exact signature:

        Best regards,
        Tamil Bharathi
        Manager - Growth
        +1 647 404 2503
        Toronto, ON
        Zuci Systems
        {case_study_text}
        
        CRITICAL RULES:
        - Do NOT invent emails not present in the thread
        - Do NOT echo the user's draft message verbatim
        - MUST follow the specified tone: {request.tone}
        - CASE STUDY RULE: Only include case study links if they appear in "AVAILABLE CASE STUDIES" section above
        - If "NO CASE STUDIES AVAILABLE" is shown above, DO NOT mention or create any case study links
        - NEVER create fake URLs like "https://example.com/case-study.pdf" or similar placeholders
        - If case studies ARE available, use EXACT title and EXACT PDF URL from above
        - Example format (only if case studies provided): "See how we helped [client]: [Exact Case Study Title from above](Exact PDF URL from above)"
        - Output ONLY valid JSON
        - No extra text outside JSON
        
        === HARD RULES ===
        - Output ONLY valid JSON.
        - No markdown.
        - No unescaped newlines.
        - No unescaped double quotes.
        - No trailing commas.
        - CRITICAL: Do NOT use backslash-single-quote (\\') - single quotes do not need escaping in JSON
        - CRITICAL: Do NOT use backslash-backtick (\\`) - backticks do not need escaping in JSON
        - Only valid JSON escape sequences: \\" \\ \\/ \\b \\f \\n \\r \\t \\uXXXX
        - If you include a link, ensure no forbidden escape characters appear.
        - DO NOT create fake or placeholder URLs.
        - If no case studies available, give response without case study.
        
        INPUT:
        Email Thread:
        {request.thread_text}
        
        User Draft Message/Intent:
        {request.custom_inputs}
        
        OUTPUT FORMAT (STRICT JSON):
        Follow this EXACT format:

        {{
          "summary": "<brief summary of the thread>",
          "stage": "Cold" | "Warm" | "Hot",
          "sentiment": "Positive" | "Neutral" | "Negative",
          "response": "<professionally written response with proper email copywriting structure. Escape all line breaks as \\n and escape double quotes inside the text. Include a case study link only if provided in the input. MUST end with the signature: Best regards,\\nTamil Bharathi\\nManager - Growth\\n+1 647 404 2503\\nToronto, ON\\nZuci Systems>"
        }}
        
        
         
        Rules:
        - DO NOT include any newline characters except escaped \\n inside string values.
        - DO NOT include unescaped double quotes.
        - DO NOT break JSON structure.
        - DO NOT add trailing commas.
        - ALWAYS return valid JSON only.
        This prompt *guarantees* valid JSON, because:
        - Forces a JSON code block  
        - Completely bans multiline and raw quotes  
        - Forces escaping  
        - Removes ANY ambiguity       """

    # Log final analysis summary
    if case_study_references:
        logger.info(f"Analyzing thread with {len(case_study_references)} case studies:")
        for cs in case_study_references:
            logger.info(f"  - {cs['title']}: {cs['url']}")
    else:
        logger.warning("Analyzing thread with NO case studies - case_study_references is empty")
        logger.warning(f"Auto-pick: {request.auto_pick_case_studies}, Selected: {request.selected_case_studies}")

    logger.info(f"Tone: {request.tone}, Auto-pick: {request.auto_pick_case_studies}")
    # print(prompt)
    response_text = await  generate_llm_response(prompt)
    logger.info(f"LLM response length: {len(response_text)} characters")

    if not response_text or not response_text.strip():
        logger.error("LLM returned empty response!")
        raise HTTPException(status_code=500, detail="Failed to generate analysis - empty response from AI")

    try:
        # Extract JSON from response
        # First, try to extract from ```json code block
        if "```json" in response_text:
            json_block = response_text.split("```json", 1)[1]
            json_block = json_block.split("```", 1)[0].strip()
        else:
            # fallback – extract raw braces
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                json_block = response_text[start:end]
            else:
                raise ValueError("No JSON object found in response")

        # Clean the JSON string to fix common LLM escaping issues
        # Replace invalid escape sequences
        json_block = json_block.replace("\\'", "'")  # Fix invalid \' escape
        json_block = json_block.replace("\\`", "`")  # Fix invalid \` escape

        # Log the cleaned JSON for debugging
        logger.info(f"Cleaned JSON block length: {len(json_block)} characters")
        print("Cleaned JSON block:")
        # print(json_block)

        # Parse the JSON
        analysis = json.loads(json_block)
        logger.info("Successfully parsed JSON response")

        # Validate required fields
        if not analysis.get('response'):
            logger.warning("Response field is empty in parsed JSON")
    except json.JSONDecodeError as e:
        raise e
        logger.error(f"JSON parsing error: {e}")
        logger.error(f"Raw response: {response_text[:500]}")
        analysis = {
            "summary": "Analysis completed but response parsing failed",
            "stage": "Warm",
            "sentiment": "Neutral",
            "response": response_text[:500] if response_text else "Unable to generate response"
        }
    except Exception as e:
        logger.error(f"Unexpected error in JSON parsing: {e}")
        analysis = {
            "summary": "Error during analysis",
            "stage": "Warm",
            "sentiment": "Neutral",
            "response": "Unable to generate response due to error"
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
        "response": analysis.get("response"),
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
        response=analysis.get('response', ''),
        ai_followup=followup
    )
