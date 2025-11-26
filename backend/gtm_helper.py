# GTM Helper Functions for Server.py
# Add these functions to your server.py file

import json
import re
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

async def extract_information_with_llm(user_message: str, current_context: Dict) -> Optional[Dict]:
    """
    Use LLM to intelligently extract and classify information from user messages
    Returns structured data about what was said and where it should go
    """
    extraction_prompt = f"""You are an expert at extracting structured information from conversational text for a microsite builder.

User just said:
"{user_message}"

Current context:
{json.dumps(current_context, indent=2)}

Your task:
1. Extract ANY relevant information from the user's message
2. Classify it into appropriate categories
3. Identify the target section where this info belongs

Categories to extract:
- company_info: company details, facts, background
- people: CEO, founders, team members (with roles and descriptions)
- features: product/service features, capabilities
- pain_points: problems, challenges, issues
- metrics: numbers, statistics, ROI, performance data
- design_preferences: colors, styles, UI preferences
- customer_insights: target audience, personas, buying behavior
- ui_elements: specific UI components or sections requested

Available sections:
- ceo_details: Leadership information
- ui_personalization: Design and UI preferences
- key_features: Product features
- pain_points: Challenges to address
- customer_profile: Customer information
- solution: Solution description
- design_requirements: Design specifications

Respond in JSON format:
{{
  "extracted": {{
    "company_info": {{}},
    "people": [],
    "features": [],
    "pain_points": [],
    "metrics": [],
    "design_preferences": [],
    "customer_insights": []
  }},
  "target_section": "section_key_where_this_belongs",
  "content": "cleaned and formatted content for that section",
  "is_substantial": true/false,
  "summary": "brief summary of what was extracted"
}}

Rules:
- If message is vague or unclear, set is_substantial to false
- Clean up the content to be professional and concise
- Only extract information that's actually present
- Be generous in interpretation - don't be too strict
"""
    
    try:
        from groq import Groq
        import os
        
        GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
        groq_client = Groq(api_key=GROQ_API_KEY)
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at extracting structured information from conversational text."
                },
                {
                    "role": "user",
                    "content": extraction_prompt
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content
        
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
    
    return None


# REPLACE THE EXISTING @api_router.post("/gtm/process-feedback") with this:

"""
@api_router.post("/gtm/process-feedback")
async def process_gtm_feedback(request: GTMFeedbackRequest, current_user: User = Depends(get_current_user)):
    
    INTELLIGENT: GTM AI Assistant with dynamic context management
    - Uses AgentDB for structured conversation management
    - Extracts and organizes information intelligently
    - Places info in correct sections automatically
    - Refines user input instead of just appending
    
    feedback = request.feedback.strip()
    form_data = request.form_data
    validation = request.validation_result
    
    # Get or create GTM agent for this user
    agent = get_or_create_gtm_agent(current_user.id)
    
    # Create async-safe LLM extraction wrapper
    async def llm_extract_async(message: str, context: Dict):
        return await extract_information_with_llm(message, context)
    
    # Process user input with intelligent extraction
    extraction_result = await llm_extract_async(feedback, agent._get_current_context())
    
    result = agent.process_user_input(
        user_message=feedback,
        form_data=form_data,
        validation_result=validation,
        llm_extract_func=lambda msg, ctx: extraction_result  # Pass the result directly
    )
    
    # If we should regenerate, use the agent's build_final_prompt method
    if result.get("should_regenerate"):
        # Fetch case studies from database
        offering_keywords = form_data.get('offering', '').lower()
        industry = form_data.get('industry', '').lower()
        
        # Build search terms
        search_terms = [industry]
        common_tech_terms = ['ai', 'automation', 'analytics', 'cloud', 'machine learning',
                            'data', 'rpa', 'crm', 'saas', 'platform']
        
        for term in common_tech_terms:
            if term in offering_keywords or term in industry:
                search_terms.append(term)
        
        # Query case studies
        search_conditions = []
        for term in search_terms:
            search_conditions.append({"summary": {"$regex": term, "$options": "i"}})
            search_conditions.append({"category": {"$regex": term, "$options": "i"}})
        
        fetched_case_studies = []
        if search_conditions:
            case_studies_cursor = db.document_files.find(
                {"$or": search_conditions},
                {"_id": 0, "id": 1, "filename": 1, "summary": 1, "category": 1, "metadata": 1}
            ).limit(5)
            fetched_case_studies = await case_studies_cursor.to_list(5)
        
        # Build final prompt using agent
        final_prompt_text = agent.build_final_prompt(
            form_data=form_data,
            validation_result=validation,
            case_studies=fetched_case_studies
        )
        
        # Save to database
        gtm_id = str(uuid.uuid4())
        gtm_record = {
            "id": gtm_id,
            "company_name": form_data.get('company_name'),
            "industry": form_data.get('industry'),
            "offering": form_data.get('offering'),
            "prompt": final_prompt_text,
            "validation_data": validation,
            "case_studies_used": [cs.get('filename', '') for cs in fetched_case_studies],
            "status": "prompt_generated",
            "created_by": current_user.id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.gtm_assets.insert_one(gtm_record)
        
        result['final_prompt'] = {
            "id": gtm_id,
            "prompt": final_prompt_text,
            "status": "prompt_generated",
            "case_studies_count": len(fetched_case_studies)
        }
    
    return result
"""
