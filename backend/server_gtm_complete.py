# COMPLETE REPLACEMENT FOR GTM ENDPOINTS IN SERVER.PY
# This includes conversation history storage and full context passing to LLM

# Add these imports at the top of server.py
from gtm_conversation_db import get_conversation_db, GTMConversationDB

# Add this helper function before GTM routes (around line 1900)

async def extract_information_with_llm_full_context(
    user_message: str, 
    conversation_history: List[Dict],
    current_context: Dict
) -> Optional[Dict]:
    """
    Use LLM to intelligently extract information WITH FULL CONVERSATION CONTEXT
    This ensures the AI understands the entire conversation flow
    """
    
    # Format conversation history for LLM
    conversation_text = "\n".join([
        f"{msg['role'].upper()}: {msg['content']}"
        for msg in conversation_history[-10:]  # Last 10 messages for context
    ])
    
    extraction_prompt = f"""You are an expert at extracting structured information from conversational text for a microsite builder.

CONVERSATION HISTORY:
{conversation_text}

CURRENT USER MESSAGE:
"{user_message}"

ACCUMULATED CONTEXT SO FAR:
{json.dumps(current_context, indent=2)}

Your task:
1. Consider the ENTIRE conversation context, not just the current message
2. Extract ANY relevant information from the user's message
3. Classify it into appropriate categories
4. Identify the target section where this info belongs
5. If user is referring to previous messages ("that CEO", "the design I mentioned"), use context

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
  "summary": "brief summary of what was extracted",
  "references_previous": true/false
}}

Rules:
- Use conversation history to understand context and references
- If user says "add that" or "include the CEO", look at previous messages
- Clean up content to be professional and concise
- Only extract information that's actually present or clearly referenced
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
        
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
    
    return None


# REPLACE @api_router.post("/gtm/process-feedback") COMPLETELY WITH THIS:

@api_router.post("/gtm/process-feedback")
async def process_gtm_feedback(request: GTMFeedbackRequest, current_user: User = Depends(get_current_user)):
    """
    INTELLIGENT GTM AI Assistant with FULL CONVERSATION HISTORY
    - Stores every message in SQLite database
    - Passes entire conversation context to LLM
    - Accumulates extracted information across all messages
    - Includes ALL user feedback in final prompt generation
    """
    feedback = request.feedback.strip()
    form_data = request.form_data
    validation = request.validation_result
    
    # Get conversation database
    conv_db = get_conversation_db()
    
    # Get or create session for this user
    session_id = conv_db.get_or_create_active_session(current_user.id, form_data)
    
    # Get full conversation context
    full_context = conv_db.get_full_context(session_id)
    conversation_history = full_context.get('conversation_history', [])
    
    # Add user message to database
    user_msg_id = conv_db.add_message(
        session_id=session_id,
        user_id=current_user.id,
        role='user',
        content=feedback
    )
    
    # Update conversation history for LLM context
    conversation_history.append({
        'role': 'user',
        'content': feedback
    })
    
    # Get or create GTM agent for this user
    agent = get_or_create_gtm_agent(current_user.id)
    
    # Load previous section states from database
    if full_context.get('section_states'):
        # Restore agent sections from database
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
    
    # Extract information using LLM with FULL CONVERSATION CONTEXT
    extraction_result = await extract_information_with_llm_full_context(
        user_message=feedback,
        conversation_history=conversation_history,
        current_context=agent._get_current_context()
    )
    
    # Store extraction in database
    if extraction_result:
        conv_db.add_message(
            session_id=session_id,
            user_id=current_user.id,
            role='system',
            content='[Extraction performed]',
            extraction_data=extraction_result
        )
        
        # Store extracted entities
        if extraction_result.get('extracted'):
            for entity_type, entity_data in extraction_result['extracted'].items():
                if entity_data:  # Only store non-empty data
                    conv_db.add_extracted_entity(
                        session_id=session_id,
                        user_id=current_user.id,
                        entity_type=entity_type,
                        entity_data=entity_data,
                        source_message_id=user_msg_id
                    )
    
    # Process user input with intelligent extraction
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
    
    # Save AI response to database
    conv_db.add_message(
        session_id=session_id,
        user_id=current_user.id,
        role='assistant',
        content=result.get('message', ''),
        section_updates=section_states
    )
    
    # If we should regenerate, build final prompt with ALL accumulated context
    if result.get("should_regenerate"):
        logger.info(f"Generating final prompt for session {session_id} with full context")
        
        # Fetch case studies from database
        offering_keywords = form_data.get('offering', '').lower()
        industry = form_data.get('industry', '').lower()
        
        # Build search terms
        search_terms = [industry]
        common_tech_terms = ['ai', 'automation', 'analytics', 'cloud', 'machine learning',
                            'data', 'rpa', 'crm', 'saas', 'platform', 'api', 'integration',
                            'workflow', 'optimization', 'fintech', 'healthcare', 'ecommerce']
        
        for term in common_tech_terms:
            if term in offering_keywords or term in industry:
                search_terms.append(term)
        
        # Query document_files collection
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
        
        # Build final prompt using agent with ALL accumulated sections
        final_prompt_text = agent.build_final_prompt(
            form_data=form_data,
            validation_result=validation,
            case_studies=fetched_case_studies
        )
        
        # Create user adjustments summary from conversation history
        user_adjustments = []
        for msg in conversation_history:
            if msg['role'] == 'user' and msg['content'] not in ['1', '2', '3', 'yes', 'generate', 'go ahead']:
                user_adjustments.append(msg['content'])
        
        user_adjustments_text = "\n\n".join([f"- {adj}" for adj in user_adjustments if len(adj) > 10])
        
        # Add user adjustments section to prompt if exists
        if user_adjustments_text:
            final_prompt_text += f"\n\n## 💬 User-Provided Context & Requirements\n\n{user_adjustments_text}\n"
        
        # Save to database with full context
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
        
        # Mark session as completed
        conv_db.close_session(session_id)
        
        # Add final prompt to result
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


# ALSO ADD THIS NEW ENDPOINT FOR RESETTING CONVERSATION

@api_router.post("/gtm/reset-conversation")
async def reset_gtm_conversation(current_user: User = Depends(get_current_user)):
    """
    Reset conversation history for current user
    Allows starting fresh conversation
    """
    conv_db = get_conversation_db()
    conv_db.clear_user_sessions(current_user.id)
    
    # Also reset the in-memory agent
    if current_user.id in gtm_agents:
        del gtm_agents[current_user.id]
    
    return {
        "success": True,
        "message": "Conversation history reset successfully"
    }


# ADD THIS ENDPOINT TO VIEW CONVERSATION HISTORY

@api_router.get("/gtm/conversation-history")
async def get_gtm_conversation_history(current_user: User = Depends(get_current_user)):
    """
    Get conversation history for current user's active session
    """
    conv_db = get_conversation_db()
    
    # Get active session
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
