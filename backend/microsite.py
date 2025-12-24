"""
Microsite Generator Module
Generates and deploys complete, runnable microsite projects
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import logging
import json
import re
import time
import asyncio
import os
import subprocess
from pathlib import Path
import random

from login import User, get_current_user
import microsite_server
from microsite_themes import detect_theme, get_theme_config, generate_theme_css, get_theme_prompt_enhancement
from microsite_ai_agent_prompt import SUPER_INTELLIGENT_MICROSITE_PROMPT, get_ai_generation_prompt
from microsite_intelligent_agent import IntelligentMicrositeAgent, regenerate_with_intelligent_feedback
from microsite_emergent_agent import EmergentMicrositeAgent, regenerate_with_emergent_feedback

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/microsite", tags=["microsite"])

# Global references (set from server.py)
db = None
generate_llm_response = None
case_study_manager = None

# Single port for all microsites
MICROSITE_PORT = 3001

# Track running microsites
running_microsites = {}  # {microsite_id: {url, project_name, path}}

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

class AutoPickRequest(BaseModel):
    service: str
    sub_service: Optional[str] = None
    personas: List[str] = []
    pain_points: List[str] = []

class AutoPickResponse(BaseModel):
    case_studies: List[Dict[str, Any]]

class MicrositeGenerateRequest(BaseModel):
    company_name: str
    industry: str
    linkedin_url: Optional[str] = ""
    offering: str
    pain_points: List[str] = []
    target_personas: List[str] = []
    use_cases: List[str] = []
    key_features: List[str] = []
    customer_profile_details: Optional[str] = ""
    selected_documents: List[str] = []
    auto_pick_documents: bool = False
    use_emergent_agent: bool = True  # Use Emergent-level intelligent agent by default

class MicrositeRegenerateRequest(BaseModel):
    microsite_id: str
    feedback: str
    company_name: str
    industry: str
    offering: str
    pain_points: List[str] = []
    target_personas: List[str] = []
    use_cases: List[str] = []
    key_features: List[str] = []
    use_emergent_agent: bool = True  # Use Emergent agent for regeneration

class MicrositeGenerateResponse(BaseModel):
    microsite_id: str
    microsite_url: str
    project_name: str
    description: str
    tech_stack: Dict[str, Any]
    generation_time_ms: int
    status: str

class MicrositeHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    company_name: str
    industry: str
    offering: str
    pain_points: List[str]
    target_personas: List[str]
    case_study_ids: List[str]
    microsite_json: Dict[str, Any]
    microsite_url: Optional[str] = None
    port: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============== SYSTEM PROMPT ==============
# Enhanced version based on analysis of Ciklum, Lovable.ai, and modern B2B sales microsites

MICROSITE_SYSTEM_PROMPT = """You are an elite full-stack engineer and UX designer specializing in creating POWERFUL, SALES-FOCUSED microsites that educate, build trust, and convert.

Your task is to create a polished, interactive microsite with RICH UI, TRUST INDICATORS, and CLICKABLE USE CASES.

═══════════════════════════════════════════════════════════════════════════════
CRITICAL RULES
═══════════════════════════════════════════════════════════════════════════════

1. Output ONLY valid JSON (no markdown, no explanations)
2. Create INTERACTIVE demonstrations with clickable use case galleries
3. Use Tailwind CSS CDN for modern, beautiful UI
4. Include TRUST INDICATORS (client logos, case studies, testimonials, metrics)
5. Include brand-consistent colors, fonts, and visual elements
6. Make use cases CLICKABLE with expandable mini-demos
7. Add METRICS and ROI visualizations with real numbers
8. All code must be production-ready and runnable
9. Include smooth animations and modern interactions
10. Strategic CTAs (context-appropriate: explore, demo, consult)

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (STRICT JSON)
═══════════════════════════════════════════════════════════════════════════════

{
  "project_name": "company-transformation-microsite",
  "description": "Interactive microsite showcasing digital transformation journey",
  "tech_stack": {
    "frontend": "HTML/CSS/JS with Tailwind CDN",
    "backend": "None",
    "runtime": "Static"
  },
  "ports": {
    "app": 3000
  },
  "files": [
    {
      "path": "index.html",
      "content": "<!-- Complete HTML with all sections -->"
    },
    {
      "path": "script.js",
      "content": "// Interactive use case gallery, animations, modal handlers"
    }
  ],
  "run_commands": {
    "install": "echo 'No dependencies to install'",
    "start": "python -m http.server $PORT"
  }
}

═══════════════════════════════════════════════════════════════════════════════
MICROSITE STRUCTURE (MANDATORY SECTIONS)
═══════════════════════════════════════════════════════════════════════════════

1. **HERO SECTION** ⭐
   - Bold 3-PART HEADLINE (Pattern: "X. Y. Z." like "Engineering Precision. AI Ingenuity. Experience Reimagined.")
   - Supporting tagline emphasizing TRANSFORMATION over services
   - Company logo/brand elements (use provided brand colors)
   - Primary CTA button (context-aware: "Explore the Journey", "See It in Action", "Book a Discovery Call")
   - Gradient background with brand colors
   - Optional: Subtle parallax or animated background elements

2. **TRUST BAR** ⭐ NEW
   - "Trusted by leading organizations" heading
   - Client logo carousel (6-12 placeholder logos if real ones not available)
   - Logos in grayscale with color on hover (hover:grayscale-0)
   - Auto-scrolling or static grid layout
   - Use generic company names/icons as placeholders

3. **PROBLEM SPACE** (Pain Points)
   - Section title: "Current Challenges" or "The Problem"
   - 3-6 pain point cards with icons/emojis
   - Each card: icon + bold title + 1-2 sentence description
   - Optional: Statistics if available
   - Visual cards with hover effects (hover:shadow-xl hover:-translate-y-1)
   - "Sound familiar?" messaging

4. **VALUE PROPOSITION** (What We Offer)
   - Section title: "How We Transform" or "Our Approach"
   - 3-4 key differentiators in icon-driven cards
   - Benefit-focused messaging (outcomes, not features)
   - Interactive hover states with gradient backgrounds

5. **CLICKABLE USE CASE GALLERY** ⭐⭐⭐ MOST IMPORTANT
   - Create gallery of clickable cards
   - Each card expands into mini demo/interactive flow
   - Include 5-7 use cases based on pain points:
     * Process simplification (3-step flow with progress indicator)
     * Digital transformation (before/after comparison)
     * Omni-channel experience (dashboard demo)
     * AI-powered features (chatbot simulation)
     * Automation (workflow visualization)
     * Analytics (dashboard with charts)
   - Each modal demo includes:
     * Title and description
     * Visual representation (mockup UI with realistic data)
     * Interactive elements (clickable buttons, form fields, animations)
     * BENEFIT CALLOUT: "✨ Result: X% faster, Y% cost reduction"
     * Before/After comparison when relevant
     * Close button with smooth animation

6. **CASE STUDIES SHOWCASE** ⭐ NEW
   - Section title: "Proven Results"
   - 2-4 case study cards with:
     * Client logo (use provided or placeholders)
     * Industry tag
     * Project title
     * KEY METRICS grid (3 metrics: "40% Cost Reduction", "3x Faster", "95% Satisfaction")
     * Brief description (2-3 sentences)
     * "Read Full Case Study →" link
   - Hover effect: shadow-2xl transform hover:-translate-y-2

7. **ROI & METRICS VISUALIZATION** ⭐ NEW
   - Section title: "The Impact" or "By the Numbers"
   - 4-6 key metrics in large cards with:
     * Large number (text-5xl font-bold)
     * Metric label
     * Short description
     * Icon
     * Gradient background (from-blue-50 to-indigo-50)

8. **ARCHITECTURE & TECHNOLOGY**
   - Compare current vs future architecture (side-by-side diagram)
   - Show transformation pathways in visual matrix
   - Use brand-consistent icons and colors
   - Interactive hover states

9. **WHY CHOOSE US** (Partner Credibility)
   - Section title: "Why Partner With Us"
   - 4-6 credibility elements (experience, certifications, expertise, success rate)
   - Consultative tone (trusted advisor, not vendor)
   - Mini-testimonials if available

10. **SOCIAL PROOF** ⭐ NEW
    - Section title: "What Our Clients Say"
    - 3-4 testimonial cards with:
      * Client photo (placeholder if needed)
      * Quote (2-3 sentences, results-focused)
      * Name, title, company
      * 5-star rating
    - Optional: Video testimonial embed
    - Optional: G2/Clutch ratings

11. **CALL TO ACTION** (Strategic CTA)
    - Section title: "Ready to Transform?"
    - Multiple CTA options:
      * Primary: "Book a Discovery Call" (prominent button)
      * Secondary: "Request a Demo" (outline button)
      * Tertiary: "Download Resources" (link)
    - Simple contact form (Name, Email, Company, Message)
    - Privacy assurance text
    - Consultative approach, not pushy

12. **FOOTER**
    - Company tagline
    - Contact information
    - Social media links
    - Legal links (Privacy, Terms)
    - Copyright notice

═══════════════════════════════════════════════════════════════════════════════
UI/UX REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

**VISUAL DESIGN:**
- Tailwind CSS CDN: <script src="https://cdn.tailwindcss.com"></script>
- Brand-consistent color palette (extract from company context)
- Modern typography with clear hierarchy
- Clean layouts with generous white space
- Rounded cards with subtle gradients
- Glass morphism effects (backdrop-blur-lg bg-white/10)

**ANIMATIONS:**
- Smooth transitions (transition-all duration-300)
- Hover effects on cards (hover:scale-105 hover:shadow-2xl)
- Fade-in on scroll (Intersection Observer)
- Modal slide-in animations
- Progress indicators for multi-step flows
- Smooth scroll navigation

**INTERACTIVE ELEMENTS:**
- Sticky nav bar with section jump links
- Clickable use case cards that expand into modals
- Interactive diagrams with hover tooltips
- Collapsible sections for detailed info
- Smooth scrolling between sections
- Mobile-responsive hamburger menu

**USE CASE MODAL STRUCTURE:**
```html
<!-- Use case card -->
<div class="use-case-card cursor-pointer" onclick="openUseCase('loan-journey')">
  <div class="p-6 bg-white/10 rounded-xl hover:scale-105">
    <h3>Loan Journey Simplification</h3>
    <p>3-step flow reducing approval time by 75%</p>
  </div>
</div>

<!-- Modal (hidden by default) -->
<div id="loan-journey-modal" class="modal hidden">
  <div class="modal-content">
    <h2>Loan Journey Simplification</h2>
    <div class="demo-flow">
      <!-- Step 1: Pre-screening -->
      <div class="step">
        <div class="step-indicator">1</div>
        <h4>Pre-screening</h4>
        <div class="mockup-ui">
          <!-- Interactive form mockup -->
        </div>
      </div>
      <!-- Step 2: Smart form -->
      <!-- Step 3: Real-time status -->
    </div>
    <p class="benefit">✨ Reduces wait times from days to minutes</p>
  </div>
</div>
```

**JAVASCRIPT FEATURES:**
- Smooth scroll behavior
- Modal open/close handlers
- Use case gallery interactions
- Intersection Observer for scroll animations
- Mobile menu toggle
- Form validation (for feedback form)
- Progress tracking for multi-step demos

**ACCESSIBILITY:**
- Keyboard accessible modals
- ARIA labels for interactive elements
- Sufficient color contrast
- Focus states for all interactive elements
- Alt text for images

═══════════════════════════════════════════════════════════════════════════════
EXAMPLE USE CASE DEMOS TO INCLUDE
═══════════════════════════════════════════════════════════════════════════════

Based on pain points, create interactive demos like:

1. **Loan Journey Simplification**
   - 3-step flow: pre-screening → smart form → real-time status
   - Show before (manual, 5 days) vs after (automated, 5 minutes)

2. **Digital Account Opening**
   - Full digital onboarding with ID scan mockup
   - Selfie verification simulation
   - Progress bar showing completion

3. **Omni-Channel Experience**
   - Member-360 dashboard mockup
   - Co-browse support demonstration
   - Continuity across mobile/web/branch

4. **Digital Cards & Payments**
   - Instant virtual card issuance demo
   - Wallet integration mockup
   - On-demand card controls interface

5. **AI-Powered Digital Teller (Chatbot)**
   - Conversational assistant demo
   - Sample Q&A flow
   - Next-best action suggestions

6. **Intelligent Process Automation**
   - RPA/AI document extraction demo
   - Underwriting workflow visualization
   - Before/after bottleneck comparison

7. **Personalized Member Insights**
   - Predictive analytics dashboard
   - Tailored offers based on transaction history
   - Interactive chart hover states

═══════════════════════════════════════════════════════════════════════════════
TECH STACK
═══════════════════════════════════════════════════════════════════════════════

**ALWAYS use pure HTML/CSS/JS with Tailwind CDN:**
- No build step required
- No dependencies to install
- Works immediately with Python HTTP server
- Perfect for interactive demonstrations

**INCLUDE:**
- Tailwind CSS CDN for styling
- Vanilla JavaScript for interactions
- HTML5 semantic structure
- CSS animations for smooth transitions

═══════════════════════════════════════════════════════════════════════════════
CRITICAL SUCCESS FACTORS
═══════════════════════════════════════════════════════════════════════════════

✅ Clickable use cases with expandable mini-demos
✅ Brand-consistent design (colors, fonts, visual style)
✅ Smooth animations and modern interactions
✅ Educational tone (not salesy, no "Book a Call" CTAs)
✅ Interactive elements (modals, progress bars, mockup UIs)
✅ Mobile responsive throughout
✅ Fast loading (no heavy dependencies)
✅ Keyboard accessible
✅ Production-ready code (no TODOs or placeholders)

Output ONLY valid JSON. Make it visually stunning and highly interactive!
"""


# ============== HELPER FUNCTIONS ==============

def extract_json_from_response(llm_response: str) -> str:
    """Extract JSON from LLM response, handling markdown code blocks"""
    # Try to extract from ```json code block
    json_match = re.search(r'```json\s*\n(.*?)\n```', llm_response, re.DOTALL)
    if json_match:
        return json_match.group(1)

    # Try to extract from ``` code block
    code_match = re.search(r'```\s*\n(.*?)\n```', llm_response, re.DOTALL)
    if code_match:
        return code_match.group(1)

    # Try to find JSON object directly
    json_obj_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
    if json_obj_match:
        return json_obj_match.group(0)

    return llm_response


def validate_microsite_json(microsite_json: Dict[str, Any]) -> None:
    """Validate that microsite JSON has required fields"""
    required_fields = ["project_name", "description", "tech_stack", "files", "run_commands"]

    missing_fields = [field for field in required_fields if field not in microsite_json]

    if missing_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Generated microsite missing required fields: {', '.join(missing_fields)}"
        )

    if not isinstance(microsite_json.get("files"), list):
        raise HTTPException(status_code=400, detail="'files' must be an array")

    for i, file in enumerate(microsite_json.get("files", [])):
        if "path" not in file or "content" not in file:
            raise HTTPException(
                status_code=400,
                detail=f"File at index {i} missing 'path' or 'content'"
            )


def generate_microsite_from_template(
    company_name: str,
    industry: str,
    offering: str,
    pain_points: list,
    value_props: list,
    use_cases: list,
    case_studies: list,
    theme_key: str
) -> str:
    """Generate beautiful microsite HTML from template"""

    # Read template
    template_path = Path(__file__).parent / "microsite_template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # Get theme classes
    theme_classes = get_theme_classes(theme_key)

    # Generate hero headline (3-part format)
    hero_parts = ["Innovative", "Intelligent", "Transformative"]
    if "ai" in offering.lower() or "intelligent" in offering.lower():
        hero_parts = ["Intelligent", "Automated", "Revolutionary"]
    elif "health" in industry.lower():
        hero_parts = ["Advanced", "Compassionate", "Transformative"]
    elif "fin" in industry.lower():
        hero_parts = ["Secure", "Efficient", "Trustworthy"]

    hero_headline = f"{hero_parts[0]}. {hero_parts[1]}. {hero_parts[2]}."

    # Generate components
    pain_point_cards = []
    pain_icons = ["⚠️", "🔴", "❌", "⏱️", "💔", "📉"]
    for i, pp in enumerate(pain_points[:6]):
        pain_point_cards.append(generate_pain_point_card(
            title=pp.split('.')[0] if '.' in pp else pp[:50],
            description=pp,
            icon_emoji=pain_icons[i % len(pain_icons)]
        ))

    # Value props
    value_prop_cards = []
    for vp in value_props[:3]:
        value_prop_cards.append(generate_value_prop_card(
            title=vp.split('.')[0] if '.' in vp else vp[:50],
            description=vp
        ))

    # Use cases
    use_case_cards = []
    use_case_modals = []
    use_case_icons = ["🚀", "💡", "⚡", "🎯", "🔧", "📊", "🤖"]

    for i, uc in enumerate(use_cases[:6]):
        uc_id = f"use-case-{i+1}"
        use_case_cards.append(generate_use_case_card(
            use_case_id=uc_id,
            title=uc.split('.')[0] if '.' in uc else uc[:50],
            description=uc,
            icon=use_case_icons[i % len(use_case_icons)]
        ))

        # Generate simple demo content
        demo_steps = [
            {"title": "Step 1: Assessment", "description": "Analyze current state and identify opportunities"},
            {"title": "Step 2: Implementation", "description": "Deploy solution with minimal disruption"},
            {"title": "Step 3: Optimization", "description": "Fine-tune and maximize results"}
        ]
        demo_content = generate_demo_content_simple(demo_steps)

        use_case_modals.append(generate_use_case_modal(
            use_case_id=uc_id,
            title=uc.split('.')[0] if '.' in uc else uc[:50],
            description=uc,
            benefit="Result: 3x faster implementation, 50% cost reduction, 95% user satisfaction",
            demo_content=demo_content
        ))

    # Case studies
    case_study_cards = []
    for cs in case_studies[:2]:
        case_study_cards.append(generate_case_study_card(
            title=cs.get('filename', 'Success Story'),
            client_name=cs.get('client_name', 'Leading Organization'),
            industry=cs.get('category', industry),
            metrics=[
                {"value": "40%", "label": "Cost Reduction"},
                {"value": "3x", "label": "Faster Delivery"},
                {"value": "95%", "label": "Satisfaction"}
            ],
            description=cs.get('summary', 'Achieved remarkable transformation results')[:200]
        ))

    # If no case studies, generate placeholders
    if not case_study_cards:
        case_study_cards.append(generate_case_study_card(
            title="Digital Transformation Success",
            client_name="Leading Enterprise",
            industry=industry,
            metrics=[
                {"value": "50%", "label": "Efficiency Gain"},
                {"value": "2x", "label": "ROI"},
                {"value": "90%", "label": "Adoption"}
            ],
            description="Successfully transformed legacy systems into modern, scalable architecture"
        ))

    # Metrics
    metric_cards = [
        generate_metric_card("75%", "Faster", "Reduced processing time"),
        generate_metric_card("$2M+", "Saved", "Annual cost savings"),
        generate_metric_card("95%", "Satisfied", "Customer satisfaction rate"),
        generate_metric_card("3x", "Growth", "Revenue increase")
    ]

    # Testimonials
    testimonial_cards = [
        generate_testimonial_card(
            quote=f"The transformation exceeded our expectations. We saw measurable improvements in efficiency and customer satisfaction.",
            name="Sarah Johnson",
            title="VP of Technology",
            company="TechCorp"
        ),
        generate_testimonial_card(
            quote=f"Working with them was a game-changer. The solution delivered real business value from day one.",
            name="Michael Chen",
            title="CTO",
            company="InnovateCo"
        ),
        generate_testimonial_card(
            quote=f"Exceptional results and outstanding support. Highly recommended for any organization looking to modernize.",
            name="Emily Rodriguez",
            title="Director of Operations",
            company="Global Solutions"
        )
    ]

    # Replace template placeholders
    html = template
    replacements = {
        "{{COMPANY_NAME}}": company_name,
        "{{HERO_HEADLINE}}": hero_headline,
        "{{HERO_TAGLINE}}": f"Transforming {industry} through innovation and excellence",
        "{{CTA_TEXT}}": "Explore Our Solutions",
        "{{PRIMARY_COLOR}}": "#3B82F6",
        "{{SECONDARY_COLOR}}": "#6366F1",
        "{{ACCENT_COLOR}}": "#8B5CF6",
        "{{TRUST_LOGOS}}": generate_trust_logos(),
        "{{PAIN_POINT_CARDS}}": '\n'.join(pain_point_cards),
        "{{VALUE_PROP_CARDS}}": '\n'.join(value_prop_cards),
        "{{USE_CASE_CARDS}}": '\n'.join(use_case_cards),
        "{{CASE_STUDY_CARDS}}": '\n'.join(case_study_cards),
        "{{METRIC_CARDS}}": '\n'.join(metric_cards),
        "{{TESTIMONIAL_CARDS}}": '\n'.join(testimonial_cards),
        "{{MODALS}}": '\n'.join(use_case_modals),
        **theme_classes
    }

    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)

    return html


def ensure_microsite_server_running():
    """Ensure the single Flask server is running"""
    if not microsite_server.is_server_running():
        logger.info("Starting consolidated microsite server...")
        microsite_server.start_microsite_server(port=MICROSITE_PORT)
        time.sleep(2)  # Wait for server to start
        logger.info(f"Microsite server ready at http://localhost:{MICROSITE_PORT}")
    return MICROSITE_PORT


def create_microsite_files(microsite_json: Dict[str, Any], base_path: Path) -> None:
    """Create microsite files on disk"""
    base_path.mkdir(parents=True, exist_ok=True)

    files_created = []
    has_index = False

    for file in microsite_json.get("files", []):
        file_path = base_path / file["path"]
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file["content"])

        files_created.append(file["path"])
        if file["path"] == "index.html" or file["path"].endswith("/index.html"):
            has_index = True

    # If no index.html exists, create a basic one
    if not has_index:
        logger.warning("No index.html found, creating a basic one")
        index_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
    <div class="text-center text-white">
        <h1 class="text-6xl font-bold mb-4 bg-gradient-to-r from-pink-500 to-violet-500 bg-clip-text text-transparent">
            {}
        </h1>
        <p class="text-xl text-gray-300">
            {}
        </p>
    </div>
</body>
</html>""".format(
            microsite_json.get("project_name", "Microsite"),
            microsite_json.get("project_name", "Welcome"),
            microsite_json.get("description", "This is your generated microsite")
        )

        with open(base_path / "index.html", 'w', encoding='utf-8') as f:
            f.write(index_content)
        files_created.append("index.html")

    logger.info(f"Created {len(files_created)} files in {base_path}: {', '.join(files_created)}")


def deploy_microsite_to_server(microsite_json: Dict[str, Any], base_path: Path, microsite_id: str) -> str:
    """Deploy microsite to the consolidated Flask server"""

    # Ensure server is running
    ensure_microsite_server_running()

    # Register this microsite with the server
    microsite_server.register_microsite(microsite_id, str(base_path))

    # Build the URL
    microsite_url = f"http://localhost:{MICROSITE_PORT}/{microsite_id}/"

    logger.info(f"Microsite '{microsite_id}' deployed successfully")
    logger.info(f"Files in directory: {list(base_path.glob('*'))}")
    logger.info(f"Accessible at: {microsite_url}")

    return microsite_url


# ============== API ENDPOINTS ==============

@router.post("/auto-pick-case-studies", response_model=AutoPickResponse)
async def auto_pick_case_studies(
    request: AutoPickRequest,
    current_user: User = Depends(get_current_user)
):
    """Auto-pick relevant case studies based on agent configuration"""
    try:
        custom_inputs = []
        for persona in request.personas:
            custom_inputs.append({"key": "persona", "value": persona})
        for pain_point in request.pain_points:
            custom_inputs.append({"key": "pain_point", "value": pain_point})

        selected_ids = await case_study_manager.auto_pick_case_studies(
            service=request.service,
            stage="MOFU",
            icp=request.personas,
            custom_inputs=custom_inputs,
            max_results=3
        )

        case_studies = []
        for cs_id in selected_ids:
            doc = await db.document_files.find_one(
                {"id": cs_id},
                {"_id": 0, "id": 1, "filename": 1, "summary": 1, "category": 1}
            )
            if doc:
                case_studies.append(doc)

        logger.info(f"Auto-picked {len(case_studies)} case studies for service: {request.service}")
        return AutoPickResponse(case_studies=case_studies)

    except Exception as e:
        logger.error(f"Error auto-picking case studies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to auto-pick case studies")


@router.post("/generate", response_model=MicrositeGenerateResponse)
async def generate_microsite(
    request: MicrositeGenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """Generate and deploy a complete working microsite based on company details and pain points"""
    start_time = time.time()

    try:
        # 1. Auto-pick case studies if enabled
        case_study_ids = request.selected_documents
        if request.auto_pick_documents:
            logger.info("Auto-picking case studies based on industry and pain points...")
            try:
                custom_inputs = []
                for persona in request.target_personas:
                    custom_inputs.append({"key": "persona", "value": persona})
                for pain_point in request.pain_points:
                    custom_inputs.append({"key": "pain_point", "value": pain_point})

                auto_picked_ids = await case_study_manager.auto_pick_case_studies(
                    service=request.industry,
                    stage="MOFU",
                    icp=request.target_personas,
                    custom_inputs=custom_inputs,
                    max_results=3
                )
                case_study_ids = auto_picked_ids
                logger.info(f"Auto-picked {len(case_study_ids)} case studies")
            except Exception as e:
                logger.warning(f"Auto-pick failed, continuing without case studies: {str(e)}")
                case_study_ids = []

        # 2. Fetch case study details
        case_studies = []
        for cs_id in case_study_ids:
            doc = await db.document_files.find_one(
                {"id": cs_id},
                {"_id": 0, "id": 1, "filename": 1, "summary": 1, "category": 1, "content": 1}
            )
            if doc:
                case_studies.append(doc)

        # 2.5 INTELLIGENT THEME DETECTION
        logger.info("🎨 Detecting appropriate theme based on content...")
        detected_theme = detect_theme(
            service=request.offering,
            pain_points=request.pain_points,
            value_props=[request.offering] + (request.key_features if request.key_features else []),
            industry=request.industry
        )
        theme_config = get_theme_config(detected_theme)
        theme_enhancement = get_theme_prompt_enhancement(detected_theme)

        logger.info(f"✨ Theme detected: {theme_config['name']} ({detected_theme})")

        # 3. Build context for LLM
        company_context = f"""
COMPANY INFORMATION:
- Company Name: {request.company_name}
- Industry: {request.industry}
- LinkedIn URL: {request.linkedin_url if request.linkedin_url else 'N/A'}

OFFERING:
{request.offering}

PAIN POINTS:
{chr(10).join(f"• {pp}" for pp in request.pain_points)}

TARGET DECISION MAKERS:
{', '.join(request.target_personas)}
"""

        use_cases_context = ""
        if request.use_cases:
            use_cases_context = f"""
KEY USE CASES:
{chr(10).join(f"• {uc}" for uc in request.use_cases)}
"""

        features_context = ""
        if request.key_features:
            features_context = f"""
KEY FEATURES:
{chr(10).join(f"• {feat}" for feat in request.key_features)}
"""

        customer_profile_context = ""
        if request.customer_profile_details:
            customer_profile_context = f"""
CUSTOMER PROFILE DETAILS:
{request.customer_profile_details}
"""

        case_studies_context = ""
        if case_studies:
            case_studies_context = "RELEVANT CASE STUDIES:\n\n" + "\n\n".join([
                f"Case Study {i+1}: {cs.get('filename', 'Untitled')}\n"
                f"Category: {cs.get('category', 'N/A')}\n"
                f"Summary: {cs.get('summary', 'No summary')[:300]}..."
                for i, cs in enumerate(case_studies)
            ])

        # 4. Generate microsite using INTELLIGENT MULTI-STEP AI AGENT
        if request.use_emergent_agent:
            logger.info(f"🚀 Initializing EMERGENT Microsite Agent (autonomous, adaptive, no templates)...")
            logger.info(f"🎨 Theme hint: {theme_config['name']} (agent will reason autonomously)")

            # Create Emergent agent instance
            agent = EmergentMicrositeAgent(llm_function=generate_llm_response)

            # Call Emergent agent with autonomous reasoning
            try:
                logger.info(f"🧠 Starting Emergent-level autonomous generation...")

                microsite_html = await asyncio.wait_for(
                    agent.generate_microsite(
                        company_name=request.company_name,
                        industry=request.industry,
                        offering=request.offering,
                        pain_points=request.pain_points,
                        target_personas=request.target_personas,
                        use_cases=request.use_cases if request.use_cases else None,
                        key_features=request.key_features if request.key_features else None,
                        case_studies=case_studies if case_studies else None,
                        linkedin_url=request.linkedin_url if request.linkedin_url else None
                    ),
                    timeout=300.0  # 5 minutes for Emergent generation
                )

                logger.info(f"✅ Emergent Agent generated {len(microsite_html):,} characters of unique, adaptive HTML")

            except asyncio.TimeoutError:
                logger.error("Emergent generation timed out")
                raise HTTPException(status_code=504, detail="Generation took too long. Please try again.")
            except Exception as e:
                logger.error(f"Emergent generation error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to generate microsite: {str(e)}")
        else:
            logger.info(f"🤖 Initializing Classic Intelligent Microsite Agent...")
            logger.info(f"🎨 Theme: {theme_config['name']}")

            # Create intelligent agent instance
            agent = IntelligentMicrositeAgent(llm_function=generate_llm_response)

            # Call intelligent agent with multi-step reasoning
            try:
                logger.info(f"🧠 Starting multi-step intelligent generation...")

                microsite_html = await asyncio.wait_for(
                    agent.generate_microsite(
                        company_name=request.company_name,
                        industry=request.industry,
                        offering=request.offering,
                        pain_points=request.pain_points,
                        target_personas=request.target_personas,
                        use_cases=request.use_cases if request.use_cases else None,
                        key_features=request.key_features if request.key_features else None,
                        case_studies=case_studies if case_studies else None,
                        linkedin_url=request.linkedin_url if request.linkedin_url else None
                    ),
                    timeout=300.0  # 5 minutes for intelligent multi-step generation
                )

                logger.info(f"✅ Intelligent Agent generated {len(microsite_html)} characters of exceptional HTML")

            except asyncio.TimeoutError:
                logger.error("AI generation timed out")
                raise HTTPException(status_code=504, detail="Generation took too long. Please try again.")
            except Exception as e:
                logger.error(f"AI generation error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to generate microsite: {str(e)}")

        # Create microsite JSON structure
        microsite_json = {
            "project_name": f"{request.company_name.lower().replace(' ', '-')}-microsite",
            "description": f"AI-generated interactive microsite for {request.company_name}",
            "tech_stack": {
                "frontend": "HTML/CSS/JS with Tailwind CDN",
                "backend": "None",
                "runtime": "Static"
            },
            "files": [
                {
                    "path": "index.html",
                    "content": microsite_html
                }
            ],
            "run_commands": {
                "install": "echo 'No dependencies required'",
                "start": "python -m http.server $PORT"
            }
        }

        logger.info(f"✅ Microsite package created successfully")

        # 5. Create microsite files and deploy
        microsite_id = str(uuid.uuid4())[:8]
        project_name = microsite_json.get("project_name", request.company_name.lower().replace(" ", "-"))
        project_name = project_name.replace(" ", "-").lower()

        # Create microsites directory
        backend_path = Path(__file__).parent
        microsites_dir = backend_path / "microsites"
        microsite_path = microsites_dir / f"{project_name}-{microsite_id}"

        logger.info(f"Creating microsite at: {microsite_path}")

        # Create files
        create_microsite_files(microsite_json, microsite_path)

        # Deploy to consolidated server
        microsite_url = deploy_microsite_to_server(microsite_json, microsite_path, microsite_id)

        # Store running microsite info
        running_microsites[microsite_id] = {
            "url": microsite_url,
            "project_name": project_name,
            "path": str(microsite_path),
            "user_id": current_user.id
        }

        # 6. Save to history
        history_entry = MicrositeHistory(
            user_id=current_user.id,
            company_name=request.company_name,
            industry=request.industry,
            offering=request.offering,
            pain_points=request.pain_points,
            target_personas=request.target_personas,
            case_study_ids=case_study_ids,
            microsite_json=microsite_json,
            microsite_url=microsite_url,
            port=MICROSITE_PORT
        )

        history_doc = history_entry.model_dump()
        history_doc['created_at'] = history_doc['created_at'].isoformat()
        await db.microsite_history.insert_one(history_doc)

        generation_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Microsite deployed successfully at {microsite_url} in {generation_time_ms}ms")

        return MicrositeGenerateResponse(
            microsite_id=microsite_id,
            microsite_url=microsite_url,
            project_name=project_name,
            description=microsite_json.get("description", ""),
            tech_stack=microsite_json.get("tech_stack", {}),
            generation_time_ms=generation_time_ms,
            status="running"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating microsite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate microsite: {str(e)}")


@router.post("/regenerate", response_model=MicrositeGenerateResponse)
async def regenerate_microsite_with_feedback(
    request: MicrositeRegenerateRequest,
    current_user: User = Depends(get_current_user)
):
    """Regenerate microsite with user feedback using Intelligent Agent"""
    start_time = time.time()

    try:
        logger.info(f"🔄 Regenerating microsite {request.microsite_id} with INTELLIGENT feedback analysis...")

        # Get existing microsite info
        if request.microsite_id not in running_microsites:
            raise HTTPException(status_code=404, detail="Microsite not found")

        existing_microsite = running_microsites[request.microsite_id]

        # Read the existing HTML
        microsite_path = Path(existing_microsite["path"])
        index_path = microsite_path / "index.html"

        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                previous_html = f.read()
        except Exception as e:
            logger.error(f"Could not read previous HTML: {str(e)}")
            previous_html = ""

        # Choose agent based on request flag
        if request.use_emergent_agent:
            logger.info(f"🚀 Using EMERGENT Agent for regeneration...")
            agent = EmergentMicrositeAgent(llm_function=generate_llm_response)

            # Use Emergent feedback regeneration
            try:
                logger.info(f"🧠 Starting Emergent regeneration with autonomous feedback analysis...")

                microsite_html = await asyncio.wait_for(
                    regenerate_with_emergent_feedback(
                        agent=agent,
                        previous_html=previous_html,
                        feedback=request.feedback,
                        company_name=request.company_name,
                        industry=request.industry,
                        offering=request.offering,
                        design_brief=None  # Will be inferred
                    ),
                    timeout=300.0  # 5 minutes for Emergent regeneration
                )

                logger.info(f"✅ Emergent Agent regenerated {len(microsite_html):,} characters with feedback applied")

            except asyncio.TimeoutError:
                logger.error("Emergent regeneration timed out")
                raise HTTPException(status_code=504, detail="Regeneration took too long. Please try again.")
            except Exception as e:
                logger.error(f"Emergent regeneration error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to regenerate microsite: {str(e)}")
        else:
            logger.info(f"🤖 Using Classic Intelligent Agent for regeneration...")
            agent = IntelligentMicrositeAgent(llm_function=generate_llm_response)

            # Use intelligent feedback regeneration
            try:
                logger.info(f"🧠 Starting intelligent regeneration with feedback analysis...")

                microsite_html = await asyncio.wait_for(
                    regenerate_with_intelligent_feedback(
                        agent=agent,
                        previous_html=previous_html,
                        feedback=request.feedback,
                        company_name=request.company_name,
                        industry=request.industry,
                        offering=request.offering,
                        pain_points=request.pain_points,
                        target_personas=request.target_personas,
                        use_cases=request.use_cases if request.use_cases else None,
                        key_features=request.key_features if request.key_features else None
                    ),
                    timeout=300.0  # 5 minutes for intelligent regeneration
                )

                logger.info(f"✅ Intelligent Agent regenerated {len(microsite_html)} characters with feedback applied")

            except asyncio.TimeoutError:
                logger.error("Intelligent regeneration timed out")
                raise HTTPException(status_code=504, detail="Regeneration took too long. Please try again.")
            except Exception as e:
                logger.error(f"Intelligent regeneration error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Failed to regenerate microsite: {str(e)}")

        # Update microsite files
        microsite_path = Path(existing_microsite["path"])
        index_path = microsite_path / "index.html"

        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(microsite_html)

        logger.info(f"✅ Updated microsite files at {microsite_path}")

        generation_time_ms = int((time.time() - start_time) * 1000)

        logger.info(f"Microsite regenerated successfully in {generation_time_ms}ms")

        return MicrositeGenerateResponse(
            microsite_id=request.microsite_id,
            microsite_url=existing_microsite["url"],
            project_name=existing_microsite["project_name"],
            description=f"Regenerated with feedback: {request.feedback[:50]}...",
            tech_stack={"frontend": "HTML/CSS/JS with Tailwind CDN"},
            generation_time_ms=generation_time_ms,
            status="running"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating microsite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to regenerate microsite: {str(e)}")


@router.get("/list")
async def list_running_microsites(current_user: User = Depends(get_current_user)):
    """List all running microsites for the current user"""
    user_microsites = {
        mid: {
            "microsite_id": mid,
            "url": info["url"],
            "port": MICROSITE_PORT,
            "project_name": info["project_name"],
            "status": "running"  # Always running since it's on the shared server
        }
        for mid, info in running_microsites.items()
        if info["user_id"] == current_user.id
    }

    return {"microsites": list(user_microsites.values())}


@router.delete("/{microsite_id}")
async def stop_microsite(microsite_id: str, current_user: User = Depends(get_current_user)):
    """Stop a running microsite (unregister from server)"""
    if microsite_id not in running_microsites:
        raise HTTPException(status_code=404, detail="Microsite not found")

    info = running_microsites[microsite_id]

    # Check ownership
    if info["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to stop this microsite")

    # Unregister from the Flask server
    microsite_server.unregister_microsite(microsite_id)

    # Remove from running microsites
    del running_microsites[microsite_id]

    logger.info(f"Stopped microsite: {microsite_id}")

    return {"message": "Microsite stopped successfully"}


@router.get("/library")
async def get_microsite_library(current_user: User = Depends(get_current_user)):
    """Get all microsites created by the current user"""
    try:
        # Fetch all microsites from history for this user
        microsites = await db.microsite_history.find(
            {"user_id": current_user.id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(100)

        # Add running status
        for microsite in microsites:
            microsite_id = microsite.get("id")
            if microsite_id and microsite_id[:8] in running_microsites:
                microsite["status"] = "running"
                microsite["current_url"] = running_microsites[microsite_id[:8]]["url"]
            else:
                microsite["status"] = "stopped"
                microsite["current_url"] = None

        return {"microsites": microsites, "total": len(microsites)}

    except Exception as e:
        logger.error(f"Error fetching microsite library: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch microsite library")


@router.post("/restart/{history_id}")
async def restart_microsite(history_id: str, current_user: User = Depends(get_current_user)):
    """Restart a microsite from history"""
    try:
        # Fetch microsite from history
        microsite_history = await db.microsite_history.find_one(
            {"id": history_id, "user_id": current_user.id},
            {"_id": 0}
        )

        if not microsite_history:
            raise HTTPException(status_code=404, detail="Microsite not found in history")

        microsite_json = microsite_history["microsite_json"]
        project_name = microsite_json.get("project_name", "microsite").replace(" ", "-").lower()

        # Create new microsite ID
        microsite_id = str(uuid.uuid4())[:8]

        # Create microsites directory
        backend_path = Path(__file__).parent
        microsites_dir = backend_path / "microsites"
        microsite_path = microsites_dir / f"{project_name}-{microsite_id}"

        logger.info(f"Restarting microsite at: {microsite_path}")

        # Create files
        create_microsite_files(microsite_json, microsite_path)

        # Deploy to consolidated server
        microsite_url = deploy_microsite_to_server(microsite_json, microsite_path, microsite_id)

        # Store running microsite info
        running_microsites[microsite_id] = {
            "url": microsite_url,
            "project_name": project_name,
            "path": str(microsite_path),
            "user_id": current_user.id
        }

        logger.info(f"Microsite restarted successfully at {microsite_url}")

        return {
            "microsite_id": microsite_id,
            "microsite_url": microsite_url,
            "project_name": project_name,
            "status": "running"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restarting microsite: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restart microsite: {str(e)}")


@router.get("/download/{history_id}")
async def download_microsite(history_id: str, current_user: User = Depends(get_current_user)):
    """Download microsite files as JSON"""
    try:
        # Fetch microsite from history
        microsite_history = await db.microsite_history.find_one(
            {"id": history_id, "user_id": current_user.id},
            {"_id": 0}
        )

        if not microsite_history:
            raise HTTPException(status_code=404, detail="Microsite not found in history")

        return {
            "microsite_json": microsite_history["microsite_json"],
            "project_name": microsite_history["microsite_json"].get("project_name"),
            "created_at": microsite_history["created_at"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading microsite: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to download microsite")


@router.delete("/library/{history_id}")
async def delete_from_library(history_id: str, current_user: User = Depends(get_current_user)):
    """Delete a microsite from library"""
    try:
        # Check if microsite exists and belongs to user
        microsite = await db.microsite_history.find_one(
            {"id": history_id, "user_id": current_user.id}
        )

        if not microsite:
            raise HTTPException(status_code=404, detail="Microsite not found")

        # Delete from database
        await db.microsite_history.delete_one({"id": history_id})

        logger.info(f"Deleted microsite {history_id} from library")

        return {"message": "Microsite deleted from library"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting microsite: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete microsite")
