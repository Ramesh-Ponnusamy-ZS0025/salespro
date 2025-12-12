# Quick fix script - run this to patch the refinement section
# This removes the problematic refinement that adds "No specific requirements"

import re

# Path to your server.py file
SERVER_PY_PATH = r"C:\workspace\taraz\salespro\backend\server.py"

# Read the file
with open(SERVER_PY_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to find and replace
old_pattern = r'''    # ============== 1\. EXTRACT AND REFINE USER ADJUSTMENTS ==============
    user_adjustments = form_data\.get\('user_adjustments', ''\)
    user_adjustments_section = ""
    
    if user_adjustments:
        # Use AI to refine and structure user adjustments
        refinement_prompt = f"""You are an expert at refining user input into professional microsite requirements\.

User provided these additional details:
"""\{user_adjustments\}"""

Your task:
1\. Extract key information about design preferences, content requirements, features, or any specific requests
2\. Organize them into clear, actionable points
3\. Remove any conversational filler \("please", "I want", "can you add", etc\.\)
4\. Keep technical terms and specific requirements intact
5\. Format as bullet points under relevant categories

Categories to use \(only include if relevant\):
- Design & UI: visual preferences, layout, colors, style
- Content: specific text, messaging, tone adjustments
- Features: interactive elements, functionality requests
- Personalization: company-specific details \(CEO, team, pricing, etc\.\)
- Technical: integrations, performance requirements

Output format:
## Category Name
- Specific requirement 1
- Specific requirement 2

Only include categories that have content\. Be concise and professional\."""
        
        try:
            refined_adjustments = await generate_llm_response\(refinement_prompt\)
            user_adjustments_section = f"\\n\\n## 📝 Additional Requirements\\n\{refined_adjustments\}\\n"
        except Exception as e:
            logger\.error\(f"Error refining user adjustments: \{str\(e\)\}"\)
            # Fallback to original if refinement fails
            user_adjustments_section = f"\\n\\n## 📝 Additional Details from User\\n\{user_adjustments\}\\n"'''

# New improved code
new_code = '''    # ============== 1. EXTRACT AND REFINE USER ADJUSTMENTS ==============
    user_adjustments = form_data.get('user_adjustments', '')
    user_adjustments_section = ""
    
    # SKIP refinement if user input is vague - just include generic requirements aren't needed
    if user_adjustments and user_adjustments.strip() and len(user_adjustments.strip()) > 20:
        # Only include if there's substantial content (more than just "make it responsive")
        vague_phrases = ['make it responsive', 'look nice', 'good ui', 'better design', 'more responsive']
        is_vague = any(phrase in user_adjustments.lower() for phrase in vague_phrases) and len(user_adjustments) < 100
        
        if not is_vague:
            user_adjustments_section = f"\\n\\n## 📝 Additional Requirements\\n{user_adjustments}\\n"'''

# Replace
content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)

# Write back
with open(SERVER_PY_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed! The AI refinement has been disabled.")
print("Now vague inputs like 'make it responsive' will be skipped entirely.")
print("Restart your backend server for changes to take effect.")
