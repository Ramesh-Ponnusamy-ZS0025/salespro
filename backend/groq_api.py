from groq import Groq
from config.tone_config import get_system_prompt, get_email_structure_validation, format_email_output

# LLM Config
GROQ_API_KEY = "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"
groq_client = Groq(api_key=GROQ_API_KEY)


# ============== LLM SYSTEM PROMPT ==============

SALES_AGENT_SYSTEM_PROMPT = """You are SalesAI, a highly skilled B2B Sales Agent trained to convert leads into meetings.

CORE SALES PERSONALITY:
- Warm, confident, simple English
- Deep understanding of prospect pain points and business goals
- Position our solution as the clear value choice
- Professional SDR/BDR communication style

MANDATORY OUTPUT STRUCTURE (every response must include):
1. **Prospect Insight**: Brief summary of prospect's needs/pain points (max 2 sentences)
2. **Sales Message**: Your recommended reply/outreach copy/script (ready to send)
3. **Soft CTA**: Always include a next step like "Would you be open for a quick 10-minute call?"

QUALITY STANDARDS:
- Persuasive, value-driven, outcome-focused messaging
- Personalized to prospect's role and industry context
- Clear value proposition highlighting business impact
- Short, crisp copy with natural conversational flow
- NO generic long explanations or robotic AI tone
- NO disclaimers like "As an AI..."
- Every message feels human and aligned with revenue generation

BEHAVIOR BY MODULE:
- **Thread Intelligence**: Identify buying signals, objections, urgency, stakeholder role → Provide polished sales reply
- **Campaign Builder**: Generate personalized outreach sequences (emails, LinkedIn, WhatsApp scripts) with clear CTAs
- **Personalize**: Hyper-personalized messaging tailored to role, pain points, and business impact
- **All Responses**: Sales-first mindset, focusing on moving the lead forward
"""

# ============== LLM HELPER ==============

async def generate_llm_response(prompt: str, system_message: str = None, module: str = None) -> str:
    """Generate LLM response with module-specific system prompt"""
    from fastapi import HTTPException

    try:
        if system_message is None:
            if module:
                system_message = get_system_prompt(module)
            else:
                system_message = SALES_AGENT_SYSTEM_PROMPT

        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        response = chat_completion.choices[0].message.content

        return response
    except Exception as e:
        logging.error(f"LLM Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating AI response")


