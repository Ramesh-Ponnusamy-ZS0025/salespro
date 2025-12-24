"""
Intelligent Theme Detection and Application System for Microsites
Auto-detects content type (AI, Enterprise, Healthcare, Finance, etc.) and applies appropriate themes
"""

# ============== THEME DEFINITIONS ==============

THEMES = {
    "ai_tech": {
        "name": "AI & Technology",
        "description": "Futuristic, high-tech theme with neural network visuals and cyberpunk aesthetics",
        "color_palette": {
            "primary": "#8B5CF6",  # Vibrant purple
            "secondary": "#06B6D4",  # Cyan
            "accent": "#EC4899",  # Pink
            "background": "#0F172A",  # Dark slate
            "surface": "#1E293B",  # Slate 800
            "text": "#F1F5F9",  # Light slate
            "gradient_from": "#6366F1",  # Indigo
            "gradient_via": "#8B5CF6",  # Purple
            "gradient_to": "#EC4899",  # Pink
        },
        "gradients": [
            "from-indigo-600 via-purple-600 to-pink-600",
            "from-cyan-500 via-blue-600 to-purple-700",
            "from-purple-600 to-pink-600",
            "from-blue-600 to-cyan-500",
        ],
        "visual_style": {
            "hero_effect": "Animated gradient with particle effects",
            "card_style": "Glass morphism with neon borders",
            "icons": "Line icons with glow effects",
            "imagery": "Neural networks, data flows, AI dashboards",
            "animations": "Smooth, futuristic transitions with glow effects",
        },
        "typography": {
            "heading_font": "Inter, system-ui, sans-serif",
            "body_font": "Inter, system-ui, sans-serif",
            "code_font": "Fira Code, monospace",
            "heading_weight": "font-bold",
            "body_weight": "font-normal",
        },
        "components": {
            "buttons": "Gradient background with glow hover effect",
            "cards": "backdrop-blur-xl bg-slate-800/50 border border-purple-500/20",
            "sections": "Dark background with gradient accents",
            "modals": "Glass morphism with animated borders",
        },
        "special_elements": [
            "Neural network visualization in hero",
            "Animated data particles background",
            "Code snippet previews",
            "AI dashboard mockups",
            "Glowing call-to-action buttons",
            "Interactive AI demos",
        ],
        "keywords": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning",
                     "neural", "automation", "intelligent", "predictive", "cognitive", "bot",
                     "chatbot", "nlp", "computer vision", "data science", "algorithm"]
    },

    "enterprise": {
        "name": "Enterprise Professional",
        "description": "Clean, professional theme for B2B enterprise solutions",
        "color_palette": {
            "primary": "#3B82F6",  # Blue
            "secondary": "#6366F1",  # Indigo
            "accent": "#10B981",  # Green
            "background": "#FFFFFF",  # White
            "surface": "#F9FAFB",  # Gray 50
            "text": "#111827",  # Gray 900
            "gradient_from": "#3B82F6",  # Blue
            "gradient_via": "#6366F1",  # Indigo
            "gradient_to": "#8B5CF6",  # Purple
        },
        "gradients": [
            "from-blue-600 to-indigo-600",
            "from-indigo-500 to-purple-600",
            "from-blue-500 to-cyan-500",
        ],
        "visual_style": {
            "hero_effect": "Subtle gradient with professional imagery",
            "card_style": "Clean shadows with rounded corners",
            "icons": "Solid professional icons",
            "imagery": "Business people, office environments, charts",
            "animations": "Smooth, professional transitions",
        },
        "typography": {
            "heading_font": "Inter, system-ui, sans-serif",
            "body_font": "Inter, system-ui, sans-serif",
            "code_font": "monospace",
            "heading_weight": "font-bold",
            "body_weight": "font-normal",
        },
        "components": {
            "buttons": "Solid colors with subtle hover effects",
            "cards": "bg-white shadow-lg rounded-xl",
            "sections": "White background with subtle gradients",
            "modals": "Clean white with shadows",
        },
        "special_elements": [
            "Professional testimonials",
            "Case study highlights",
            "ROI calculators",
            "Trust badges",
            "Enterprise logos",
        ],
        "keywords": ["enterprise", "business", "corporate", "b2b", "professional",
                     "solution", "platform", "saas", "software", "digital transformation"]
    },

    "fintech": {
        "name": "Financial Technology",
        "description": "Modern, trustworthy theme for financial services and fintech",
        "color_palette": {
            "primary": "#10B981",  # Green
            "secondary": "#3B82F6",  # Blue
            "accent": "#F59E0B",  # Amber
            "background": "#FFFFFF",  # White
            "surface": "#F9FAFB",  # Gray 50
            "text": "#111827",  # Gray 900
            "gradient_from": "#10B981",  # Green
            "gradient_via": "#3B82F6",  # Blue
            "gradient_to": "#6366F1",  # Indigo
        },
        "gradients": [
            "from-green-600 to-blue-600",
            "from-blue-600 to-indigo-600",
            "from-emerald-500 to-teal-600",
        ],
        "visual_style": {
            "hero_effect": "Professional with financial graphics",
            "card_style": "Clean with subtle borders",
            "icons": "Financial icons (charts, money, security)",
            "imagery": "Charts, dashboards, financial data",
            "animations": "Smooth, trustworthy transitions",
        },
        "typography": {
            "heading_font": "Inter, system-ui, sans-serif",
            "body_font": "Inter, system-ui, sans-serif",
            "code_font": "monospace",
            "heading_weight": "font-bold",
            "body_weight": "font-normal",
        },
        "components": {
            "buttons": "Green/blue with security badges",
            "cards": "bg-white shadow-lg border border-gray-200",
            "sections": "White with green/blue accents",
            "modals": "Professional with security indicators",
        },
        "special_elements": [
            "Security badges",
            "Compliance certifications",
            "Financial charts",
            "Transaction mockups",
            "ROI calculators",
        ],
        "keywords": ["fintech", "financial", "banking", "payment", "lending", "insurance",
                     "investment", "wealth", "credit", "transaction", "blockchain", "crypto"]
    },

    "healthcare": {
        "name": "Healthcare & Medical",
        "description": "Clean, trustworthy theme for healthcare and medical services",
        "color_palette": {
            "primary": "#3B82F6",  # Blue
            "secondary": "#10B981",  # Green
            "accent": "#06B6D4",  # Cyan
            "background": "#FFFFFF",  # White
            "surface": "#F9FAFB",  # Gray 50
            "text": "#111827",  # Gray 900
            "gradient_from": "#3B82F6",  # Blue
            "gradient_via": "#06B6D4",  # Cyan
            "gradient_to": "#10B981",  # Green
        },
        "gradients": [
            "from-blue-600 to-cyan-500",
            "from-cyan-500 to-green-500",
            "from-blue-500 to-teal-600",
        ],
        "visual_style": {
            "hero_effect": "Clean with medical imagery",
            "card_style": "Soft shadows, rounded corners",
            "icons": "Medical icons (heart, health, care)",
            "imagery": "Healthcare professionals, patients, medical tech",
            "animations": "Gentle, reassuring transitions",
        },
        "typography": {
            "heading_font": "Inter, system-ui, sans-serif",
            "body_font": "Inter, system-ui, sans-serif",
            "code_font": "monospace",
            "heading_weight": "font-semibold",
            "body_weight": "font-normal",
        },
        "components": {
            "buttons": "Blue with care-focused messaging",
            "cards": "bg-white shadow rounded-xl",
            "sections": "White with blue/green accents",
            "modals": "Clean, accessible design",
        },
        "special_elements": [
            "Patient testimonials",
            "Healthcare certifications",
            "Medical diagrams",
            "Treatment timelines",
            "HIPAA compliance badges",
        ],
        "keywords": ["healthcare", "medical", "health", "patient", "clinical", "hospital",
                     "telemedicine", "pharma", "diagnosis", "treatment", "care", "wellness"]
    }
}


# ============== INTELLIGENT THEME DETECTION ==============

def detect_theme(service: str, pain_points: list, value_props: list, industry: str = "") -> str:
    """
    Intelligently detect the most appropriate theme based on content analysis

    Args:
        service: The service or solution being offered
        pain_points: List of pain points being addressed
        value_props: List of value propositions
        industry: Industry context

    Returns:
        Theme key (e.g., "ai_tech", "enterprise", "fintech", "healthcare")
    """
    # Combine all text for analysis
    all_text = " ".join([
        service.lower(),
        " ".join(pain_points).lower() if pain_points else "",
        " ".join(value_props).lower() if value_props else "",
        industry.lower()
    ])

    # Score each theme
    theme_scores = {}

    for theme_key, theme_data in THEMES.items():
        score = 0
        keywords = theme_data.get("keywords", [])

        # Count keyword matches
        for keyword in keywords:
            if keyword in all_text:
                score += 1

        theme_scores[theme_key] = score

    # Return theme with highest score, default to enterprise if tie
    if max(theme_scores.values()) == 0:
        return "enterprise"  # Default theme

    return max(theme_scores, key=theme_scores.get)


def get_theme_config(theme_key: str) -> dict:
    """Get the full theme configuration"""
    return THEMES.get(theme_key, THEMES["enterprise"])


def generate_theme_css(theme_key: str) -> str:
    """Generate custom CSS for the theme"""
    theme = get_theme_config(theme_key)
    colors = theme["color_palette"]

    css = f"""
    :root {{
        --color-primary: {colors['primary']};
        --color-secondary: {colors['secondary']};
        --color-accent: {colors['accent']};
        --color-background: {colors['background']};
        --color-surface: {colors['surface']};
        --color-text: {colors['text']};
    }}

    .theme-gradient {{
        background: linear-gradient(135deg, {colors['gradient_from']}, {colors['gradient_via']}, {colors['gradient_to']});
    }}

    .theme-text-gradient {{
        background: linear-gradient(135deg, {colors['gradient_from']}, {colors['gradient_to']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    """

    # Add AI-specific effects
    if theme_key == "ai_tech":
        css += """
        .glow-effect {
            box-shadow: 0 0 20px rgba(139, 92, 246, 0.5),
                        0 0 40px rgba(139, 92, 246, 0.3);
        }

        .glow-hover:hover {
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.7),
                        0 0 60px rgba(139, 92, 246, 0.5);
            transform: translateY(-2px);
        }

        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px rgba(139, 92, 246, 0.5); }
            50% { box-shadow: 0 0 40px rgba(236, 72, 153, 0.7); }
        }

        .animate-pulse-glow {
            animation: pulse-glow 3s ease-in-out infinite;
        }
        """

    return css


def get_theme_specific_sections(theme_key: str) -> list:
    """Get theme-specific sections and components to include"""
    theme = get_theme_config(theme_key)

    sections = {
        "ai_tech": [
            "neural_network_hero",
            "ai_capabilities_showcase",
            "interactive_ai_demo",
            "code_api_preview",
            "model_performance_metrics",
            "ai_powered_features",
        ],
        "enterprise": [
            "professional_hero",
            "business_value_proposition",
            "enterprise_features",
            "scalability_architecture",
            "security_compliance",
            "integration_ecosystem",
        ],
        "fintech": [
            "financial_hero",
            "security_first_approach",
            "compliance_certifications",
            "transaction_flow_demo",
            "roi_calculator",
            "regulatory_badges",
        ],
        "healthcare": [
            "healthcare_hero",
            "patient_outcomes",
            "hipaa_compliance",
            "clinical_workflow",
            "provider_testimonials",
            "medical_certifications",
        ]
    }

    return sections.get(theme_key, sections["enterprise"])


# ============== THEME-SPECIFIC PROMPTS ==============

AI_TECH_ENHANCEMENTS = """
ADDITIONAL REQUIREMENTS FOR AI/TECH THEME:

**Visual Style:**
- Dark mode design (bg-slate-900, text-white)
- Neon gradients (purple, cyan, pink)
- Glass morphism effects (backdrop-blur-xl)
- Glowing borders and hover effects
- Particle/neural network background animation

**Hero Section:**
- Animated gradient background with particle effects
- Bold tech-focused 3-part headline with "AI", "Intelligent", or "Automated"
- Neon glow on CTA buttons
- Code snippet or API preview

**Special Components:**
1. **Neural Network Visualization**
   - Animated nodes and connections
   - Glowing data flow paths
   - Interactive on hover

2. **AI Capabilities Cards**
   - Each with icon + glow effect
   - Hover reveals more details
   - Neon borders

3. **Interactive AI Demo Modal**
   - Chatbot simulation
   - Predictive analytics dashboard
   - Real-time data processing visualization

4. **Code/API Preview Section**
   - Dark code editor style
   - Syntax highlighting
   - Copy button with animation

5. **Model Performance Metrics**
   - Large percentage numbers with glow
   - Animated progress bars
   - Comparison charts (before AI vs after AI)

**Color Usage:**
- Primary backgrounds: slate-900, slate-800
- Accents: purple-600, cyan-500, pink-600
- Borders: purple-500/20, cyan-500/20
- Text: slate-100, white
- Gradients: from-indigo-600 via-purple-600 to-pink-600

**Animations:**
- Glow pulse on CTA buttons
- Particle floating in background
- Data flow animations
- Code typing effect
- Neural network pulse

**Typography:**
- Modern sans-serif (Inter)
- Monospace for code (Fira Code)
- Bold headings with gradient text

**Icons:**
- Line style with glow effects
- Tech-focused (brain, circuit, robot, data)
- Animated on hover
"""


def get_theme_prompt_enhancement(theme_key: str) -> str:
    """Get additional prompt instructions for specific theme"""

    enhancements = {
        "ai_tech": AI_TECH_ENHANCEMENTS,
        "enterprise": """
ADDITIONAL REQUIREMENTS FOR ENTERPRISE THEME:
- Professional, clean design
- Trust indicators prominent
- Blue/indigo color scheme
- Business-focused imagery
- ROI and metrics emphasis
- Case studies with logos
- Security and compliance badges
        """,
        "fintech": """
ADDITIONAL REQUIREMENTS FOR FINTECH THEME:
- Green (trust/money) and blue (security) colors
- Financial charts and graphs
- Security badges prominent
- Compliance certifications
- Transaction mockups
- Calculator components
- Trust and safety messaging
        """,
        "healthcare": """
ADDITIONAL REQUIREMENTS FOR HEALTHCARE THEME:
- Blue and green (care/health) colors
- Clean, accessible design
- Patient-focused messaging
- Medical imagery
- HIPAA compliance badges
- Testimonials from patients
- Care journey visualizations
        """
    }

    return enhancements.get(theme_key, "")
