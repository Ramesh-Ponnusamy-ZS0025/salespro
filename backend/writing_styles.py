"""
Writing Styles Configuration for TaRaZ
Each style has a unique prompt that guides the AI's tone and approach
"""

WRITING_STYLES = {
    "data-driven": {
        "name": "Data-Driven",
        "description": "Focus on metrics, statistics, and quantifiable results",
        "system_addition": """
Use a data-driven approach:
- Lead with compelling statistics and metrics
- Reference specific numbers and percentages
- Use phrases like "X% improvement", "reduced by Y", "increased ROI by Z"
- Back claims with quantifiable evidence
- Structure content around measurable outcomes
- Use industry benchmarks when relevant
"""
    },

    "formal-human": {
        "name": "Formal / Human",
        "description": "Professional yet warm, balancing formality with authenticity",
        "system_addition": """
Write in a formal yet human style:
- Maintain professional language but avoid being stuffy
- Use complete sentences and proper grammar
- Show genuine interest and empathy
- Balance business context with personal connection
- Use "I" and "you" to create warmth
- Avoid overly casual language while staying approachable
"""
    },

    "cxo-pitch": {
        "name": "CXO Pitch",
        "description": "Executive-level communication focusing on strategic value",
        "system_addition": """
Write for C-level executives:
- Focus on strategic value and business outcomes
- Lead with bottom-line impact (revenue, cost, efficiency)
- Keep it concise and high-level
- Avoid technical jargon - use business language
- Frame solutions in terms of competitive advantage
- Address board-level concerns: growth, risk, innovation
- Use executive-appropriate tone - confident but not salesy
"""
    },

    "challenger": {
        "name": "Challenger-Style Persuasion",
        "description": "Challenge assumptions and reframe thinking",
        "system_addition": """
Use the Challenger Sale approach:
- Lead with an unexpected insight or contrarian view
- Challenge their current thinking or assumptions
- Reframe their problem in a new light
- Teach them something they didn't know
- Use phrases like "What if...", "Most companies think X, but...", "The real issue isn't..."
- Build credibility through insight, not features
- Create constructive tension
"""
    },

    "basho": {
        "name": "BASHO-Style",
        "description": "Highly personalized with specific, relevant observations",
        "system_addition": """
Follow the BASHO methodology:
- Start with a highly specific, relevant observation about them
- Reference something unique to their situation (recent post, company news, role change)
- Make it extremely clear you've done your homework
- Connect your observation to a specific pain point
- Keep it brief and punchy
- Avoid generic statements - every sentence should be personalized
- Use their language and industry terminology
"""
    },

    "poet": {
        "name": "Z Poet",
        "description": "Creative, engaging, and memorable",
        "system_addition": """
Write in an creative, engaging style:
- Use vivid language and metaphors
- Create memorable phrases
- Show personality and creativity
- Use storytelling elements
- Make complex ideas simple and visual
- Break conventional patterns
- Be bold and different
- Keep it professional but interesting
"""
    },

    "urgency": {
        "name": "Urgency-Framing Conversion Style",
        "description": "Create urgency and drive immediate action",
        "system_addition": """
Create urgency and drive action:
- Highlight time-sensitive opportunities or risks
- Use phrases like "Now is the time...", "Before...", "While..."
- Reference market changes, competitive threats, or windows closing
- Show cost of inaction or delay
- Include specific, time-bound calls-to-action
- Create FOMO (Fear of Missing Out) around value
- Balance urgency with authenticity - no false scarcity
"""
    },

    "executive": {
        "name": "Executive Briefing Style",
        "description": "Concise, structured executive summary format",
        "system_addition": """
Write as an executive briefing:
- Start with the key takeaway upfront
- Use structured format (Situation, Implication, Action)
- Bullet points for easy scanning
- Maximum clarity, minimum words
- Focus on "So what?" - why this matters
- End with clear next steps
- Professional, neutral tone
- Respect their time - get to the point
"""
    }
}

MESSAGE_LENGTH_CONFIGS = {
    "<100": {
        "name": "Below 100 words",
        "max_tokens": 150,
        "guidance": "Keep it very brief and punchy - under 100 words total"
    },
    "100-200": {
        "name": "100-200 words",
        "max_tokens": 300,
        "guidance": "Write 100-200 words - concise but with room for detail"
    },
    "200-300": {
        "name": "200-300 words",
        "max_tokens": 450,
        "guidance": "Write 200-300 words - balanced depth and brevity"
    },
    "500": {
        "name": "500 words",
        "max_tokens": 750,
        "guidance": "Write approximately 500 words - detailed and comprehensive"
    },
    "long": {
        "name": "Long paragraph",
        "max_tokens": 1024,
        "guidance": "Write a longer, detailed message - 500+ words with full context"
    }
}

def get_writing_style(style_key: str) -> dict:
    """Get writing style configuration"""
    return WRITING_STYLES.get(style_key, WRITING_STYLES["data-driven"])

def get_message_length_config(length_key: str) -> dict:
    """Get message length configuration"""
    return MESSAGE_LENGTH_CONFIGS.get(length_key, MESSAGE_LENGTH_CONFIGS["100-200"])

def get_all_writing_styles():
    """Get list of all available writing styles"""
    return [
        {"key": key, "name": value["name"], "description": value["description"]}
        for key, value in WRITING_STYLES.items()
    ]

def get_all_message_lengths():
    """Get list of all available message lengths"""
    return [
        {"key": key, "name": value["name"]}
        for key, value in MESSAGE_LENGTH_CONFIGS.items()
    ]
