"""
FIXED GTM PROCESS FEEDBACK ENDPOINT
====================================

Replace the existing @api_router.post("/gtm/process-feedback") function 
in your server.py with this fixed version.

Line location: Around line 2310 in server.py

PROBLEM FIXED:
- Backend was appending raw user input without refinement
- Not categorizing information properly
- Not rewriting user content clearly

NEW BEHAVIOR:
- Intelligently extracts and categorizes user input
- Rewrites content professionally
- Organizes by category (UI Requirements, Target Persons, etc.)
- Does NOT add summaries or new ideas
- Does NOT copy user's exact words
"""

@api_router.post("/gtm/process-feedback")
async def process_gtm_feedback(request: GTMFeedbackRequest, current_user: User = Depends(get_current_user)):
    """
    Process user feedback and intelligently categorize/refine information.
    
    RULES:
    1. Extract and categorize user input (NO raw appending)
    2. Rewrite clearly and professionally
    3. Place info in correct categories (UI Requirements, Target Persons, etc.)
    4. DO NOT add summaries or new ideas
    5. DO NOT repeat user's exact words
    """
    feedback = request.feedback.strip()
    feedback_lower = feedback.lower()
    form_data = request.form_data
    validation = request.validation_result

    # Check for generate command
    generate_keywords = ['generate', 'create', 'yes', 'go ahead', 'proceed', '1', 'generate prompt', 'lets go', "let's go", 'ready']
    if any(keyword in feedback_lower for keyword in generate_keywords):
        return {
            "action": "generate",
            "message": "Perfect! Generating your comprehensive microsite prompt now... 🚀",
            "updated_validation": validation,
            "should_regenerate": True
        }

    # Use AI to intelligently parse and categorize user input
    categorization_prompt = f"""You are an expert at parsing and categorizing information for microsite generation.

User provided this input:
\"\"\"{feedback}\"\"\"

Your task:
1. Extract ALL relevant information from the user's input
2. Categorize it into these sections (only use sections that apply):
   - ui_requirements: Design, layout, colors, interactivity, visual preferences
   - target_persons: CEO, CTO, specific decision makers, their roles/details
   - industry_details: Industry-specific information, market details
   - product_features: Specific features, capabilities, technical details
   - adjustments: Any other modifications or requirements
   - customer_profile: Customer demographics, behavior, challenges

3. CRITICAL RULES:
   - Rewrite content professionally (DO NOT copy user's exact words)
   - Extract meaning and intent, not literal phrases
   - Keep technical terms and domain keywords
   - Remove conversational filler ("please", "I want", "can you")
   - Be concise - 1-2 sentences per point
   - DO NOT add new ideas or suggestions
   - DO NOT create summaries

Output ONLY valid JSON in this format:
{{
  "categorized_info": {{
    "ui_requirements": ["point 1", "point 2"],
    "target_persons": ["point 1", "point 2"],
    "product_features": ["point 1"],
    ...
  }},
  "is_meaningful": true/false,
  "user_intent": "brief description of what user wants"
}}

Only include categories that have actual content. Empty categories should not appear."""

    try:
        ai_response = await generate_llm_response(categorization_prompt)
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
        if json_match:
            categorized_data = json.loads(json_match.group())
            
            if not categorized_data.get('is_meaningful', False):
                return {
                    "action": "clarify",
                    "message": "I want to make sure I understand correctly. Could you provide more specific details about what you'd like to include in the microsite? For example: design preferences, specific people to feature, product features, or customer information.",
                    "updated_validation": validation,
                    "should_regenerate": False
                }
            
            # Build formatted categories
            categorized_info = categorized_data.get('categorized_info', {})
            formatted_sections = []
            
            section_headers = {
                'ui_requirements': '## 🎨 UI & Design Requirements',
                'target_persons': '## 👤 Target Persons / Decision Makers',
                'industry_details': '## 🏢 Industry-Specific Details',
                'product_features': '## ✨ Product Features & Capabilities',
                'customer_profile': '## 👥 Customer Profile Details',
                'adjustments': '## 📝 Additional Requirements'
            }
            
            for section_key, section_header in section_headers.items():
                if section_key in categorized_info and categorized_info[section_key]:
                    formatted_sections.append(section_header)
                    for point in categorized_info[section_key]:
                        formatted_sections.append(f"- {point}")
                    formatted_sections.append("")  # Empty line between sections
            
            if formatted_sections:
                # Get existing adjustments and append new ones
                existing_adjustments = form_data.get('user_adjustments', '')
                new_adjustments = "\n".join(formatted_sections)
                
                # Combine without duplication
                if existing_adjustments:
                    combined_adjustments = f"{existing_adjustments}\n\n{new_adjustments}"
                else:
                    combined_adjustments = new_adjustments
                
                form_data['user_adjustments'] = combined_adjustments
                
                # Create user-friendly summary
                user_intent = categorized_data.get('user_intent', 'Additional details')
                num_sections = len([k for k, v in categorized_info.items() if v])
                
                response_msg = f"✅ **{user_intent.capitalize()}**\n\n"
                response_msg += f"I've organized your input into {num_sections} section(s):\n\n"
                
                for section_key in categorized_info:
                    if categorized_info[section_key]:
                        section_name = section_headers[section_key].replace('#', '').replace('🎨', '').replace('👤', '').replace('🏢', '').replace('✨', '').replace('👥', '').replace('📝', '').strip()
                        count = len(categorized_info[section_key])
                        response_msg += f"• {section_name}: {count} point(s)\n"
                
                response_msg += "\n✨ Ready to generate the microsite prompt with these details? Just say 'generate'!"
                
                return {
                    "action": "update",
                    "message": response_msg,
                    "updated_validation": validation,
                    "updated_form_data": form_data,
                    "should_regenerate": False
                }
            else:
                return {
                    "action": "clarify",
                    "message": "I couldn't extract any specific requirements from that input. Could you provide more details? For example:\n\n• Design preferences (colors, style, layout)\n• Specific people to feature (CEO, team members)\n• Product features or capabilities\n• Customer information",
                    "updated_validation": validation,
                    "should_regenerate": False
                }
    
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return {
            "action": "error",
            "message": "I had trouble processing that input. Could you rephrase or provide more specific details?",
            "updated_validation": validation,
            "should_regenerate": False
        }


"""
INSTALLATION INSTRUCTIONS:
=========================

1. Open C:\\workspace\\taraz\\salespro\\backend\\server.py

2. Find the function that starts with:
   @api_router.post("/gtm/process-feedback")
   async def process_gtm_feedback(...)

3. Replace the ENTIRE function (from @api_router.post to the end of the function)
   with the code above (lines 17-165)

4. Restart your backend server

5. Test by:
   - Filling out the GTM form
   - Clicking "Generate Prompt"
   - Adding adjustments like "add CEO profile" or "use dark theme"
   - The backend should now categorize and rewrite your input properly

"""
