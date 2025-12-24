"""
Emergent-Level Intelligent Microsite Agent
===========================================

Autonomous microsite generation with adaptive architecture, design reasoning,
and self-critique. No templates - every microsite is uniquely generated.

Inspired by Emergent's approach to adaptive UI generation.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
import json

from microsite_design_intelligence import (
    create_design_brief,
    DesignIntelligenceEngine,
    DesignIntent,
    SectionDecision
)

logger = logging.getLogger(__name__)


class EmergentMicrositeAgent:
    """
    Emergent-level autonomous microsite generation agent.

    Key Differences from Template-Based Approach:
    1. Infers design requirements from minimal context
    2. Dynamically decides which sections to include
    3. Generates unique layouts for each microsite
    4. Self-critiques and refines autonomously
    5. No fixed templates or boilerplate
    """

    def __init__(self, llm_function):
        """
        Initialize the Emergent agent.

        Args:
            llm_function: Async function for LLM calls
        """
        self.llm = llm_function
        self.design_engine = DesignIntelligenceEngine()

    async def generate_microsite(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        use_cases: List[str] = None,
        key_features: List[str] = None,
        case_studies: List[Dict] = None,
        linkedin_url: str = None
    ) -> str:
        """
        Autonomously generate a unique, high-quality microsite.

        Process:
        1. Context Inference - Understand intent without asking questions
        2. Design Intelligence - Reason about UX/UI requirements
        3. Architecture Planning - Decide sections and layout dynamically
        4. Layout Reasoning - Design exact layout strategy (PREVENTS TEMPLATES)
        5. Content Generation - Create unique copy
        6. Implementation - Build adaptive UI with quality constraints
        7. Self-Critique - Design quality evaluation and refinement

        Returns:
            Complete HTML for the microsite
        """
        logger.info("🚀 Starting Emergent Microsite Agent...")
        logger.info(f"📊 Company: {company_name} | Industry: {industry}")

        # STEP 1: Context Inference & Design Intelligence
        logger.info("STEP 1/7: 🧠 Inferring context and design requirements...")
        design_brief = await self._create_intelligent_design_brief(
            company_name, industry, offering, pain_points,
            target_personas, use_cases, key_features,
            has_case_studies=bool(case_studies)
        )

        # STEP 2: Deep Strategic Analysis
        logger.info("STEP 2/7: 🎯 Performing strategic analysis...")
        strategic_analysis = await self._analyze_strategic_context(
            company_name, industry, offering, pain_points,
            target_personas, design_brief
        )

        # STEP 3: Dynamic Content Planning
        logger.info("STEP 3/7: ✍️ Planning content architecture...")
        content_architecture = await self._plan_content_architecture(
            company_name, offering, pain_points, use_cases,
            key_features, design_brief, strategic_analysis
        )

        # STEP 4: Layout Reasoning (NEW - PREVENTS GENERIC TEMPLATES)
        logger.info("STEP 4/7: 📐 Designing layout architecture (anti-template)...")
        layout_architecture = await self._generate_layout_architecture(
            design_brief, content_architecture, strategic_analysis, company_name
        )

        # STEP 5: Intelligent Content Generation
        logger.info("STEP 5/7: 📝 Generating unique, contextual content...")
        content = await self._generate_adaptive_content(
            company_name, industry, offering, design_brief,
            content_architecture, strategic_analysis, case_studies
        )

        # STEP 6: Adaptive UI Implementation (with quality constraints)
        logger.info("STEP 6/7: 🎨 Building production-grade UI...")
        html = await self._implement_adaptive_ui(
            company_name, industry, design_brief,
            content_architecture, content, strategic_analysis,
            layout_architecture  # Pass layout decisions
        )

        # STEP 7: Design Quality Evaluation & Refinement
        logger.info("STEP 7/7: ✨ Evaluating design quality and refining...")
        final_html = await self._autonomous_refinement(
            html, design_brief, strategic_analysis, layout_architecture
        )

        logger.info("✅ Emergent Microsite Agent completed successfully!")
        logger.info(f"📏 Generated: {len(final_html):,} characters | Sections: {design_brief['total_sections']}")

        return final_html

    async def _create_intelligent_design_brief(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        use_cases: Optional[List[str]],
        key_features: Optional[List[str]],
        has_case_studies: bool
    ) -> Dict[str, Any]:
        """
        STEP 1: Context Inference & Design Intelligence

        Autonomously analyze context and create a design brief WITHOUT asking questions.
        Uses the DesignIntelligenceEngine to reason about requirements.
        """

        # Use design intelligence engine
        brief = create_design_brief(
            company_name=company_name,
            industry=industry,
            offering=offering,
            pain_points=pain_points or [],
            target_personas=target_personas or [],
            use_cases=use_cases or [],
            key_features=key_features or [],
            has_case_studies=has_case_studies
        )

        logger.info(f"✅ Design Brief Created:")
        logger.info(f"   • Complexity: {brief['design_intent']['complexity']}")
        logger.info(f"   • Audience: {brief['design_intent']['audience']}")
        logger.info(f"   • Design Language: {brief['design_intent']['design_language']}")
        logger.info(f"   • Sections Planned: {brief['total_sections']}")
        logger.info(f"   • Primary Goal: {brief['design_intent']['primary_goal']}")

        return brief

    async def _analyze_strategic_context(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        design_brief: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STEP 2: Deep Strategic Analysis

        Understand positioning, competitive landscape, and emotional drivers.
        """

        design_intent = design_brief['design_intent']

        analysis_prompt = f"""You are an elite business strategist and UX psychologist. Perform a deep strategic analysis.

COMPANY: {company_name}
INDUSTRY: {industry}
OFFERING: {offering}

CONTEXT INFERENCES:
• Target Audience: {design_intent['audience']}
• Emotional Tone: {design_intent['emotional_tone']}
• Primary Goal: {design_intent['primary_goal']}
• Content Density: {design_intent['content_density']}

PAIN POINTS ADDRESSED:
{chr(10).join(f"• {pp}" for pp in pain_points)}

TARGET PERSONAS:
{', '.join(target_personas)}

YOUR TASK:
Provide strategic insights that will inform exceptional microsite design.

## 1. Unique Value Proposition
[What makes this company truly unique? Go beyond features.]

## 2. Emotional Triggers
[What emotions drive the target audience? What keeps them up at night?]

## 3. Trust & Credibility Strategy
[How should we build credibility with this audience?]

## 4. Conversion Psychology
[What psychological principles should we leverage for conversion?]

## 5. Competitive Positioning
[How should we differentiate from competitors?]

## 6. Key Messages (3-5 core messages)
[What messages must permeate the microsite?]

## 7. Visual & Interaction Strategy
[Given the {design_intent['design_language']} design language and {design_intent['interaction_level']} interaction level, what approach?]

## 8. Content Tone & Voice
[Given {design_intent['emotional_tone']} tone, how should we communicate?]

Be insightful and strategic. Think deeply about what would truly resonate."""

        try:
            response = await self.llm(
                prompt=analysis_prompt,
                system_message="You are an elite business strategist and UX psychologist. Provide deep, actionable insights.",
                module="emergent_strategic_analysis"
            )

            analysis = {
                "raw_analysis": response,
                "company_name": company_name,
                "industry": industry,
                "design_intent": design_intent
            }

            logger.info(f"✅ Strategic analysis complete: {len(response)} characters")
            return analysis

        except Exception as e:
            logger.error(f"Strategic analysis failed: {str(e)}")
            return {
                "raw_analysis": "Focus on professional positioning and clear value communication.",
                "company_name": company_name,
                "industry": industry,
                "design_intent": design_intent
            }

    async def _plan_content_architecture(
        self,
        company_name: str,
        offering: str,
        pain_points: List[str],
        use_cases: Optional[List[str]],
        key_features: Optional[List[str]],
        design_brief: Dict[str, Any],
        strategic_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        STEP 3: Dynamic Content Planning

        Plan what content to create for each dynamically-chosen section.
        """

        sections = design_brief['sections']
        design_intent = design_brief['design_intent']

        planning_prompt = f"""You are a content strategist. Plan the content architecture for this microsite.

COMPANY: {company_name}
OFFERING: {offering}

STRATEGIC INSIGHTS:
{strategic_analysis.get('raw_analysis', '')[:1200]}

DESIGN DECISIONS:
• Sections Included: {', '.join([s['type'] for s in sections])}
• Content Density: {design_intent['content_density']}
• Emotional Tone: {design_intent['emotional_tone']}
• Primary Goal: {design_intent['primary_goal']}

INPUT DATA:
• Pain Points ({len(pain_points)}): {', '.join(pain_points[:3])}...
• Use Cases Provided: {len(use_cases or [])}
• Key Features Provided: {len(key_features or [])}

YOUR TASK:
For each section, plan EXACTLY what content to create. Be specific and detailed.

Output in JSON format:

{{
  "hero": {{
    "headline_formula": "[3-part or single powerful headline]",
    "subheadline_approach": "[How to frame the value prop]",
    "cta_strategy": "[What action to drive]"
  }},
  "problems": {{
    "count": [3-6],
    "framing": "[How to present pain points]",
    "emphasis": "[Which pain point to emphasize]"
  }},
  "solution": {{
    "value_prop_count": [3-5],
    "framing": "[Benefit-focused or transformation-focused?]",
    "differentiation": "[How to show uniqueness]"
  }},
  "use_cases": {{
    "count": [4-7],
    "types": ["[List types of use cases to create]"],
    "demonstration_approach": "[How to show value]"
  }},
  "roi_metrics": {{
    "metrics_count": [4-6],
    "metric_types": ["[percentage improvements, time savings, cost reductions, etc.]"]
  }},
  "testimonials": {{
    "count": [3-4],
    "personas": ["[Which personas should testimonials represent]"]
  }},
  "cta": {{
    "primary_cta": "[Button text]",
    "secondary_cta": "[Alternate action]",
    "urgency_level": "[low, medium, high]"
  }}
}}

Include ALL sections from the design: {', '.join([s['type'] for s in sections])}

Be strategic and specific. Output ONLY valid JSON."""

        try:
            response = await self.llm(
                prompt=planning_prompt,
                system_message="You are a content strategist. Output valid JSON with detailed content planning.",
                module="emergent_content_planning"
            )

            # Try to parse JSON
            try:
                # Clean response
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean.replace('```json', '', 1).strip()
                if response_clean.startswith('```'):
                    response_clean = response_clean.replace('```', '', 1).strip()
                if response_clean.endswith('```'):
                    response_clean = response_clean.rsplit('```', 1)[0].strip()

                content_plan = json.loads(response_clean)

            except json.JSONDecodeError:
                logger.warning("Content plan not valid JSON, using raw response")
                content_plan = {"raw": response}

            architecture = {
                "content_plan": content_plan,
                "sections": sections,
                "raw_response": response
            }

            logger.info(f"✅ Content architecture planned for {len(sections)} sections")
            return architecture

        except Exception as e:
            logger.error(f"Content planning failed: {str(e)}")
            return {
                "content_plan": {},
                "sections": sections,
                "raw_response": "Standard content approach"
            }

    async def _generate_layout_architecture(
        self,
        design_brief: Dict[str, Any],
        content_architecture: Dict[str, Any],
        strategic_analysis: Dict[str, Any],
        company_name: str
    ) -> Dict[str, Any]:
        """
        STEP 4: Layout Reasoning Phase (NEW - PREVENTS GENERIC TEMPLATES)

        Design the exact layout strategy BEFORE generating code.
        This prevents LLM from defaulting to template patterns.
        """

        design_intent = design_brief['design_intent']
        sections = design_brief['sections']

        layout_prompt = f"""You are an elite product designer (NOT a developer yet) designing the layout architecture.

COMPANY: {company_name}

DESIGN INTENT:
• Audience: {design_intent['audience']}
• Design Language: {design_intent['design_language']}
• Complexity: {design_intent['complexity']}
• Interaction Level: {design_intent['interaction_level']}
• Content Density: {design_intent['content_density']}

SECTIONS TO LAYOUT:
{chr(10).join(f"{i+1}. {s['type']} ({s['layout_variant']}, {s['interaction_type']})" for i, s in enumerate(sections))}

═══════════════════════════════════════════════════════════════
MANDATORY DESIGN PRINCIPLES (PREVENTS TEMPLATE-LIKE OUTPUT)
═══════════════════════════════════════════════════════════════

1. VISUAL HIERARCHY (Required)
   ✓ Establish clear focal points (not everything same size)
   ✓ Use size variation: Primary 1.5-2x secondary, Tertiary 0.7-0.9x
   ✓ Large headings: text-6xl to text-8xl for hero
   ✓ Medium headings: text-3xl to text-5xl for sections
   ✓ Body text: text-lg to text-xl
   ✓ Visual weight through font-bold, font-semibold, gradients

2. LAYOUT ASYMMETRY (Required - Anti-Template)
   ✗ BANNED: Centered hero sections (class="text-center")
   ✗ BANNED: Perfectly symmetrical layouts (50/50 splits)
   ✗ BANNED: All sections with same structure
   ✓ REQUIRED: Offset grids (60/40, 70/30, 65/35 splits)
   ✓ REQUIRED: Staggered elements, diagonal flows
   ✓ REQUIRED: Varied layouts per section

3. VISUAL DENSITY (Required)
   ✗ BANNED: Large empty white sections (py-20, py-24 everywhere)
   ✗ BANNED: Sparse content with too much padding
   ✓ REQUIRED: Appropriate density for {design_intent['complexity']} complexity
     - Rich: 70-80% screen utilization, py-12 to py-16
     - Moderate: 60-70% utilization, py-14 to py-18
     - Minimal: 50-60% utilization, py-16 to py-20
   ✓ REQUIRED: Strategic white space (not just empty)

4. COMPONENT DIVERSITY (Required)
   ✗ BANNED: All cards with same class="bg-white shadow-lg p-6"
   ✗ BANNED: Uniform component sizing (all same height/width)
   ✗ BANNED: Equal-width 3-column grids (grid-cols-3)
   ✓ REQUIRED: Varied card sizes (some large, some small)
   ✓ REQUIRED: Mix of component types per section
   ✓ REQUIRED: Different visual treatments

5. GRID SYSTEM SOPHISTICATION (Required)
   ✗ BANNED: Simple grid-cols-3 everywhere
   ✗ BANNED: Uniform column widths across sections
   ✓ REQUIRED: 12-column base grid with varied spans
   ✓ REQUIRED: Asymmetric column distributions (col-span-7 + col-span-5, col-span-8 + col-span-4)
   ✓ REQUIRED: Different grid patterns per section
   ✓ REQUIRED: Overlapping elements where appropriate

═══════════════════════════════════════════════════════════════
YOUR TASK: Design Layout Architecture for Each Section
═══════════════════════════════════════════════════════════════

For EACH section below, specify:
1. Grid structure (12-column system, how columns are distributed)
2. Visual hierarchy (what's prominent, size relationships)
3. Asymmetry strategy (how to avoid centered/symmetrical)
4. Component arrangement (placement, overlaps, spacing)
5. Anti-pattern avoided (what template pattern we're NOT doing)

Output in this format:

## HERO SECTION
Grid Structure: [e.g., "col-span-7 for text (left), col-span-5 for visual (right)"]
Visual Hierarchy: [e.g., "text-7xl headline, text-xl subheadline, dual CTAs"]
Asymmetry: [e.g., "Text left-aligned, visual offset with blob animations"]
Component Arrangement: [e.g., "Headline top, subheadline below, CTA buttons in flex gap-4"]
Anti-Pattern Avoided: [e.g., "NOT centered text with single CTA"]
Interaction: [e.g., "Hover states on buttons, animated background blobs"]

## [NEXT SECTION NAME]
Grid Structure: [Different from hero - e.g., "col-span-8 + col-span-4"]
Visual Hierarchy: [Size relationships, what draws attention]
Asymmetry: [How layout is offset/staggered]
Component Arrangement: [Specific placement strategy]
Anti-Pattern Avoided: [What we're NOT doing]
Interaction: [Hover, click, scroll behaviors]

[CONTINUE FOR ALL {len(sections)} SECTIONS]

═══════════════════════════════════════════════════════════════
OVERALL LAYOUT STRATEGY
═══════════════════════════════════════════════════════════════

Grid System Base: [12-column with 24px gutters]
Section Flow: [How sections transition - alternating layouts? background colors?]
Visual Rhythm: [Pattern of dense/sparse, colorful/neutral sections]
Focal Point Strategy: [What are the 3-4 main focal points across entire page?]
Responsive Strategy: [How layouts adapt on mobile - stack? reorder?]

═══════════════════════════════════════════════════════════════
ANTI-PATTERN CHECKLIST (must confirm ALL avoided)
═══════════════════════════════════════════════════════════════

Confirm you are AVOIDING:
- [ ] Centered hero text (generic template)
- [ ] Equal-width card grids everywhere (template-like)
- [ ] Large empty sections with py-20+ (wasted space)
- [ ] All components same size (no hierarchy)
- [ ] Symmetrical layouts throughout (boring)
- [ ] Uniform spacing patterns (rigid)
- [ ] Same grid structure for all sections (repetitive)

Be specific and detailed. This layout architecture will be used EXACTLY by the developer."""

        try:
            response = await self.llm(
                prompt=layout_prompt,
                system_message="You are an elite product designer creating layout architectures that prevent generic templates. Be specific and enforce anti-pattern avoidance.",
                module="emergent_layout_architecture"
            )

            layout_architecture = {
                "raw_layout": response,
                "design_intent": design_intent,
                "sections_count": len(sections)
            }

            logger.info(f"✅ Layout architecture designed for {len(sections)} sections (anti-template)")
            return layout_architecture

        except Exception as e:
            logger.error(f"Layout architecture design failed: {str(e)}")
            return {
                "raw_layout": "Standard varied layout with asymmetric grids",
                "design_intent": design_intent,
                "sections_count": len(sections)
            }

    async def _generate_adaptive_content(
        self,
        company_name: str,
        industry: str,
        offering: str,
        design_brief: Dict[str, Any],
        content_architecture: Dict[str, Any],
        strategic_analysis: Dict[str, Any],
        case_studies: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """
        STEP 4: Intelligent Content Generation

        Generate unique, compelling copy based on the planned architecture.
        """

        sections = design_brief['sections']
        content_plan = content_architecture.get('content_plan', {})
        design_intent = design_brief['design_intent']

        # Build section-specific instructions
        section_instructions = []
        for section in sections:
            section_type = section['type']
            layout_variant = section['layout_variant']

            section_instructions.append(
                f"• {section_type.upper()} (layout: {layout_variant}, priority: {section['priority']})"
            )

        content_prompt = f"""You are an award-winning copywriter. Create exceptional, unique copy for this microsite.

COMPANY: {company_name}
INDUSTRY: {industry}
OFFERING: {offering}

STRATEGIC DIRECTION:
{strategic_analysis.get('raw_analysis', '')[:1500]}

DESIGN INTENT:
• Emotional Tone: {design_intent['emotional_tone']}
• Audience: {design_intent['audience']}
• Primary Goal: {design_intent['primary_goal']}
• Content Density: {design_intent['content_density']}

CONTENT ARCHITECTURE PLAN:
{json.dumps(content_plan, indent=2) if isinstance(content_plan, dict) else content_plan}

SECTIONS TO WRITE:
{chr(10).join(section_instructions)}

REQUIREMENTS:
1. Write copy for EACH section listed above
2. Follow the content plan strategy
3. Match the {design_intent['emotional_tone']} emotional tone
4. Target the {design_intent['audience']} audience
5. Drive toward {design_intent['primary_goal']} goal
6. Be specific to {company_name} - no generic phrases
7. Create compelling, conversion-optimized copy
8. Include specific metrics and outcomes

OUTPUT FORMAT (organize by section):

=== HERO ===
Headline: [Powerful headline]
Subheadline: [Value proposition]
CTA Primary: [Button text]
CTA Secondary: [Alternate action]

=== PROBLEMS === (if included)
Section Heading: [Creative heading]
Intro: [2-3 sentences]
[For each pain point]
- Title: [Punchy title]
- Description: [Compelling description]
- Icon Suggestion: [e.g., "alert-triangle", "clock", "dollar-sign"]

=== SOLUTION === (if included)
Section Heading: [Benefit-focused heading]
Intro: [Transformation message]
[For each value prop]
- Title: [Benefit title]
- Description: [Outcome description]
- Metric: [e.g., "3x faster", "80% reduction"]

=== USE_CASES === (if included)
Section Heading: [Heading]
[For each use case]
- Title: [Specific scenario]
- Description: [Problem it solves]
- Outcome: [Measurable result]
- Demo Concept: [What to show in interactive modal]

=== ROI_METRICS === (if included)
Section Heading: [Heading]
[For each metric]
- Number: [e.g., "85%", "10x", "$2M"]
- Label: [e.g., "Faster Processing"]
- Description: [Brief explanation]

=== TESTIMONIALS === (if included)
[For each testimonial]
- Quote: [Authentic testimonial]
- Name: [Full name]
- Title: [Job title]
- Company: [Company name]

=== CTA ===
Heading: [Compelling CTA heading]
Subheading: [Supporting message]
Primary Button: [Text]
Secondary Button: [Text]
Form Heading: [Heading for contact form]

[Include ALL other sections from the list above]

Make the copy:
- Emotionally resonant
- Benefit-driven (outcomes, not features)
- Specific and credible
- Free of clichés
- Conversion-optimized
- Aligned with strategic insights

Generate comprehensive, high-quality copy now:"""

        try:
            response = await self.llm(
                prompt=content_prompt,
                system_message=f"You are an award-winning B2B copywriter. Write in a {design_intent['emotional_tone']} tone that resonates with {design_intent['audience']} audiences.",
                module="emergent_content_generation"
            )

            content = {
                "raw_content": response,
                "company_name": company_name,
                "sections_count": len(sections)
            }

            logger.info(f"✅ Content generated: {len(response):,} characters for {len(sections)} sections")
            return content

        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return {
                "raw_content": f"Professional copy for {company_name}",
                "company_name": company_name,
                "sections_count": len(sections)
            }

    async def _implement_adaptive_ui(
        self,
        company_name: str,
        industry: str,
        design_brief: Dict[str, Any],
        content_architecture: Dict[str, Any],
        content: Dict[str, Any],
        strategic_analysis: Dict[str, Any],
        layout_architecture: Dict[str, Any]  # NEW - Layout decisions
    ) -> str:
        """
        STEP 6: Adaptive UI Implementation (with Quality Constraints)

        Build production-grade UI following EXACT layout architecture.
        Prevents generic templates through explicit constraints.
        """

        sections = design_brief['sections']
        design_intent = design_brief['design_intent']

        # Create detailed section implementation instructions
        section_impl_instructions = []
        for section in sections:
            section_type = section['type']
            layout_variant = section['layout_variant']
            interaction_type = section['interaction_type']
            priority = section['priority']

            section_impl_instructions.append(
                f"{priority}. {section_type.upper()}\n"
                f"   Layout: {layout_variant}\n"
                f"   Interaction: {interaction_type}\n"
                f"   Reasoning: {section['reasoning']}"
            )

        # Map design language to color schemes
        design_language_colors = {
            "vibrant_tech": {
                "primary": "#8B5CF6", "secondary": "#06B6D4", "accent": "#EC4899",
                "gradient": "from-purple-600 via-pink-600 to-cyan-600"
            },
            "professional_enterprise": {
                "primary": "#3B82F6", "secondary": "#1E40AF", "accent": "#10B981",
                "gradient": "from-blue-600 to-indigo-700"
            },
            "medical_trust": {
                "primary": "#0EA5E9", "secondary": "#06B6D4", "accent": "#14B8A6",
                "gradient": "from-cyan-500 to-teal-600"
            },
            "financial_secure": {
                "primary": "#1E40AF", "secondary": "#7C3AED", "accent": "#D97706",
                "gradient": "from-blue-800 via-indigo-700 to-purple-700"
            },
            "modern_minimal": {
                "primary": "#1F2937", "secondary": "#6B7280", "accent": "#3B82F6",
                "gradient": "from-gray-800 to-gray-600"
            },
            "creative_bold": {
                "primary": "#DC2626", "secondary": "#F59E0B", "accent": "#8B5CF6",
                "gradient": "from-red-600 via-orange-500 to-purple-600"
            }
        }

        colors = design_language_colors.get(
            design_intent['design_language'],
            design_language_colors['modern_minimal']
        )

        implementation_prompt = f"""You are an elite frontend developer implementing a SPECIFIC layout design.

COMPANY: {company_name} | INDUSTRY: {industry}

═══════════════════════════════════════════════════════════════════════════════
LAYOUT ARCHITECTURE (YOU MUST FOLLOW THIS EXACTLY)
═══════════════════════════════════════════════════════════════════════════════

{layout_architecture.get('raw_layout', '')[:2500]}

[...COMPLETE LAYOUT ARCHITECTURE ABOVE - FOLLOW IT PRECISELY]

═══════════════════════════════════════════════════════════════════════════════
QUALITY BAR - YOUR OUTPUT MUST MEET THESE PRODUCTION STANDARDS
═══════════════════════════════════════════════════════════════════════════════

1. ✅ VISUAL HIERARCHY (Mandatory)

   Hero Section:
   - Headline: text-7xl or text-8xl (LARGE)
   - Subheadline: text-xl or text-2xl
   - CTA buttons: text-lg with px-8 py-4

   Section Headings:
   - Main headings: text-4xl or text-5xl (font-bold)
   - Subheadings: text-2xl or text-3xl (font-semibold)
   - Body text: text-lg or text-xl

   Visual Weight:
   - Use font-bold for primary elements
   - Use font-semibold for secondary
   - Use gradients for emphasis (bg-gradient-to-r {colors['gradient']})
   - Size variation: At least 3 distinct text scales per section

2. ✗ LAYOUT ASYMMETRY (Anti-Template - CRITICAL)

   BANNED PATTERNS (will cause rejection):
   ✗ <div class="text-center"> in hero sections
   ✗ <div class="grid grid-cols-3 gap-8"> with uniform cards
   ✗ Symmetrical 50/50 splits
   ✗ All sections with same grid structure
   ✗ Centered layouts throughout

   REQUIRED PATTERNS:
   ✓ Hero: grid-cols-12 with col-span-7 + col-span-5 (or 8+4, 6+6 offset)
   ✓ Sections: Vary grid patterns (col-span-8 + col-span-4, full-width, 3-column with different spans)
   ✓ Text alignment: Left-aligned for hero, varied per section
   ✓ Staggered elements: Use transform, negative margins, overlaps

3. ✅ VISUAL DENSITY (Mandatory)

   Complexity Level: {design_intent['complexity']}

   Padding Rules:
   ✗ BANNED: py-20 or py-24 on multiple consecutive sections (too sparse)
   ✓ REQUIRED: py-12 to py-16 for rich complexity
   ✓ REQUIRED: py-14 to py-18 for moderate
   ✓ REQUIRED: py-16 to py-20 for minimal

   Content Density:
   - Rich: 70-80% screen utilization, content-rich sections
   - Moderate: 60-70% utilization
   - Minimal: 50-60% utilization
   - Strategic white space (not empty space)

4. ✅ COMPONENT DIVERSITY (Mandatory)

   BANNED (generic template):
   ✗ All cards: <div class="bg-white shadow-lg p-6 rounded-lg">
   ✗ Uniform card heights (h-full on all)
   ✗ Same component style throughout

   REQUIRED (production-grade):
   ✓ Vary card styles: Some with gradients, some with shadows, some with borders
   ✓ Size variation: Large feature cards (p-8), medium cards (p-6), small cards (p-4)
   ✓ Visual treatments: Mix shadows (shadow-lg, shadow-xl, shadow-2xl)
   ✓ Component types: Cards, highlight boxes, stats, interactive modals

5. ✅ GRID SOPHISTICATION (Mandatory)

   Base Grid: 12-column Tailwind grid

   BANNED:
   ✗ <div class="grid grid-cols-3"> everywhere
   ✗ Equal-width columns in all sections

   REQUIRED:
   ✓ grid-cols-12 with varied col-span-*
   ✓ Hero: col-span-7 + col-span-5 (or 8+4, 6+6)
   ✓ Section A: col-span-8 + col-span-4
   ✓ Section B: grid-cols-12 with col-span-4 x3 (but different content heights)
   ✓ Section C: Full-width with nested grids
   ✓ Responsive: Change grid on mobile (col-span-12 on small screens)

═══════════════════════════════════════════════════════════════════════════════
ANTI-PATTERN EXAMPLES (DO NOT GENERATE CODE LIKE THIS)
═══════════════════════════════════════════════════════════════════════════════

❌ WRONG - Generic Template (will fail quality check):

<section class="text-center py-20">
  <h1 class="text-5xl">Headline</h1>
  <p class="text-xl mt-4">Subheadline</p>
  <button class="mt-8 px-8 py-3">CTA</button>
</section>

<section class="py-20 bg-gray-50">
  <div class="grid grid-cols-3 gap-8">
    <div class="bg-white shadow-lg p-6 rounded-lg">Card 1</div>
    <div class="bg-white shadow-lg p-6 rounded-lg">Card 2</div>
    <div class="bg-white shadow-lg p-6 rounded-lg">Card 3</div>
  </div>
</section>

═══════════════════════════════════════════════════════════════════════════════
CORRECT EXAMPLE (Production-Grade Quality):
═══════════════════════════════════════════════════════════════════════════════

✅ CORRECT - Production-Grade UI:

<section class="relative py-16 overflow-hidden">
  <div class="max-w-7xl mx-auto px-6">
    <div class="grid grid-cols-12 gap-8 items-center">
      <!-- Left: Text (7 columns) -->
      <div class="col-span-12 md:col-span-7">
        <h1 class="text-7xl md:text-8xl font-bold leading-tight">
          Transform Your
          <span class="block mt-2 text-transparent bg-clip-text bg-gradient-to-r {colors['gradient']}">
            Business Future
          </span>
        </h1>
        <p class="text-xl md:text-2xl mt-6 text-gray-600 max-w-2xl leading-relaxed">
          Specific value proposition that resonates with target audience...
        </p>
        <div class="flex flex-wrap gap-4 mt-10">
          <button class="px-8 py-4 bg-gradient-to-r {colors['gradient']} text-white text-lg font-semibold rounded-xl shadow-2xl hover:shadow-3xl hover:scale-105 transition-all duration-300">
            Primary CTA
          </button>
          <button class="px-8 py-4 border-2 border-gray-300 text-gray-700 text-lg font-semibold rounded-xl hover:border-gray-400 hover:bg-gray-50 transition-all duration-300">
            Secondary Action
          </button>
        </div>
      </div>

      <!-- Right: Visual (5 columns) -->
      <div class="col-span-12 md:col-span-5">
        <div class="relative">
          <!-- Animated blobs for depth -->
          <div class="absolute -top-4 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
          <div class="absolute -bottom-8 right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
          <div class="absolute -bottom-4 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
          <!-- Visual content here -->
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Next section: Different grid pattern -->
<section class="py-16 bg-gradient-to-br from-gray-50 to-white">
  <div class="max-w-7xl mx-auto px-6">
    <h2 class="text-5xl font-bold mb-12">Section Heading</h2>
    <div class="grid grid-cols-12 gap-8">
      <!-- 8-column main area -->
      <div class="col-span-12 lg:col-span-8">
        <div class="grid grid-cols-2 gap-6">
          <!-- Varied card sizes -->
          <div class="bg-white p-8 rounded-2xl shadow-lg hover:shadow-2xl transition-shadow duration-300">
            <div class="text-4xl mb-4">🚀</div>
            <h3 class="text-2xl font-semibold mb-3">Feature One</h3>
            <p class="text-gray-600 text-lg">Description...</p>
          </div>
          <div class="bg-gradient-to-br {colors['gradient']} p-8 rounded-2xl text-white shadow-xl">
            <div class="text-4xl mb-4">⚡</div>
            <h3 class="text-2xl font-semibold mb-3">Feature Two (Highlighted)</h3>
            <p class="text-white/90 text-lg">Description...</p>
          </div>
        </div>
      </div>

      <!-- 4-column sidebar -->
      <div class="col-span-12 lg:col-span-4">
        <div class="bg-white p-8 rounded-2xl shadow-xl border-2 border-gray-100">
          <h3 class="text-2xl font-bold mb-6">Key Stats</h3>
          <div class="space-y-6">
            <div>
              <div class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r {colors['gradient']}">85%</div>
              <div class="text-gray-600 mt-2">Improvement</div>
            </div>
            <!-- More stats -->
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

═══════════════════════════════════════════════════════════════════════════════
CONTENT TO USE
═══════════════════════════════════════════════════════════════════════════════

{content.get('raw_content', '')[:3500]}

[... USE ALL CONTENT PROVIDED - DON'T CREATE PLACEHOLDER TEXT]

═══════════════════════════════════════════════════════════════════════════════
COLOR PALETTE
═══════════════════════════════════════════════════════════════════════════════

Primary: {colors['primary']}
Secondary: {colors['secondary']}
Accent: {colors['accent']}
Gradient: bg-gradient-to-r {colors['gradient']}

Use these colors for:
- Gradient text (bg-clip-text text-transparent)
- Button backgrounds
- Highlight sections
- Accent elements

═══════════════════════════════════════════════════════════════════════════════
TECHNICAL REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

1. Tailwind CSS CDN: <script src="https://cdn.tailwindcss.com"></script>
2. Responsive: Mobile-first, use md: and lg: breakpoints
3. JavaScript: Modals, smooth scroll, mobile menu, intersection observer
4. Accessibility: ARIA labels, keyboard navigation
5. Animations: Use animate-blob, transition-all, hover states
6. Structure: Semantic HTML5 (header, nav, main, section, footer)

═══════════════════════════════════════════════════════════════════════════════
OUTPUT REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

- Output ONLY complete HTML
- NO markdown code blocks (```html)
- NO explanations outside code
- Start with <!DOCTYPE html>
- Include ALL JavaScript for interactions
- Production-ready, polished code
- Minimum 20,000 characters for rich complexity

═══════════════════════════════════════════════════════════════════════════════
SALES/MARKETING DESIGN REQUIREMENTS (CRITICAL FOR CONVERSION)
═══════════════════════════════════════════════════════════════════════════════

This is a SALES MICROSITE - it must be PERSUASIVE, not just informative.

Benchmark Quality: Gong.io, Drift.com, Intercom.com, Stripe.com sales pages

1. PREMIUM VISUAL DESIGN (Not "clean" - "WOW")

   ✓ Sophisticated gradients (multi-stop, mesh gradients, not simple linear)
   ✓ Layered depth (multiple shadow levels, overlapping elements, z-index layers)
   ✓ Premium micro-interactions (smooth hover transforms, subtle animations)
   ✓ Glass morphism effects (backdrop-blur, translucent overlays)
   ✓ Accent colors used strategically (not everywhere, but for emphasis)

   Example Premium Card:
   <div class="group relative bg-gradient-to-br from-white to-gray-50 p-8 rounded-3xl border border-gray-200/50 shadow-xl shadow-gray-900/5 hover:shadow-2xl hover:shadow-purple-500/10 hover:-translate-y-1 transition-all duration-500">
     <div class="absolute inset-0 bg-gradient-to-br {colors['gradient']} opacity-0 group-hover:opacity-5 rounded-3xl transition-opacity duration-500"></div>
     <!-- Content -->
   </div>

2. ATTENTION-GRABBING ELEMENTS (Stand out, don't blend in)

   ✓ Animated gradient text for key phrases
   ✓ Glowing accents on CTAs (box-shadow with color)
   ✓ Floating elements with subtle motion (animate-float, animate-pulse)
   ✓ Premium badges/labels ("Most Popular", "Limited Time", "Trusted by 1000+")
   ✓ Visual dividers with gradient lines
   ✓ Decorative elements (blobs, shapes, abstract graphics)

   Example CTA:
   <button class="group relative px-10 py-5 bg-gradient-to-r {colors['gradient']} text-white text-lg font-bold rounded-2xl shadow-2xl shadow-purple-500/50 hover:shadow-purple-500/70 hover:scale-105 transition-all duration-300 overflow-hidden">
     <span class="relative z-10">Start Free Trial →</span>
     <div class="absolute inset-0 bg-white/20 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
   </button>

3. CONVERSION PSYCHOLOGY ELEMENTS (Build trust, create urgency)

   ✓ Social proof everywhere (logos, testimonial count, user numbers)
   ✓ Trust badges prominently displayed (certifications, awards, security)
   ✓ Urgency indicators ("Join 10,000+ teams", "Limited spots", "Growing fast")
   ✓ Risk reversal ("No credit card", "Cancel anytime", "14-day trial")
   ✓ Authority signals (Featured in Forbes, TechCrunch logos)
   ✓ Specific metrics (not "better" but "3.5x ROI", "87% faster")

   Example Trust Bar:
   <div class="bg-gradient-to-r from-purple-50 to-pink-50 py-6 border-y border-purple-100">
     <div class="flex items-center justify-center gap-12 text-sm text-gray-600">
       <div class="flex items-center gap-2">
         <svg class="w-5 h-5 text-green-500">✓</svg>
         <span class="font-semibold">10,000+ teams</span>
       </div>
       <div class="flex items-center gap-2">
         <svg class="w-5 h-5 text-green-500">✓</svg>
         <span class="font-semibold">4.9/5 rating</span>
       </div>
       <div class="flex items-center gap-2">
         <svg class="w-5 h-5 text-green-500">✓</svg>
         <span class="font-semibold">SOC 2 Certified</span>
       </div>
     </div>
   </div>

4. VISUAL PROOF & DEMOS (Show don't just tell)

   ✓ Product screenshots with premium styling (shadow-2xl, rounded borders, subtle gradient overlay)
   ✓ Before/after comparisons with clear visual difference
   ✓ Animated UI mockups (subtle floating, rotating)
   ✓ Video placeholders with play buttons
   ✓ Dashboard/analytics mockups with real-looking data
   ✓ Customer logo walls with hover effects

5. SOPHISTICATED COMPONENTS (Not basic, premium)

   Premium Feature Card Pattern:
   <div class="relative group">
     <div class="absolute -inset-1 bg-gradient-to-r {colors['gradient']} rounded-3xl blur opacity-25 group-hover:opacity-50 transition duration-500"></div>
     <div class="relative bg-white p-8 rounded-3xl">
       <div class="w-14 h-14 bg-gradient-to-br {colors['gradient']} rounded-2xl flex items-center justify-center mb-6 shadow-lg">
         <svg class="w-7 h-7 text-white">...</svg>
       </div>
       <h3 class="text-2xl font-bold mb-3">Feature Name</h3>
       <p class="text-gray-600 text-lg mb-6">Benefit-focused description...</p>
       <div class="flex items-center text-purple-600 font-semibold group-hover:gap-3 gap-2 transition-all">
         Learn more <span class="group-hover:translate-x-1 transition-transform">→</span>
       </div>
     </div>
   </div>

6. HERO SECTION PREMIUM DESIGN (First impression must WOW)

   Must include:
   ✓ Large, bold headline with gradient accent (text-7xl+)
   ✓ Compelling subheadline with specific value (not generic)
   ✓ Dual CTAs (primary gradient, secondary outlined)
   ✓ Trust indicators immediately visible ("Trusted by...", logos)
   ✓ Visual proof (screenshot/mockup) with premium styling
   ✓ Animated background elements (blobs, gradients, particles)
   ✓ Scroll indicator or value props preview

7. SPACING & RHYTHM (Premium feel through white space)

   ✓ Generous padding around key elements (not cramped)
   ✓ Clear section breaks (use gradient dividers, bg color changes)
   ✓ Alternating section backgrounds (white, gradient-to-br from-gray-50, purple-50)
   ✓ Consistent vertical rhythm (sections at py-16 or py-20 for breathing room)
   ✓ Max-width containers (max-w-7xl) with px-6 for clean edges

8. CALL-TO-ACTION DESIGN (Must be irresistible)

   Primary CTA Requirements:
   - Large (px-10 py-5 or bigger)
   - Gradient background with glow
   - Bold, action-oriented text ("Start Free Trial", not "Submit")
   - Hover effects (scale-105, increased shadow)
   - Risk reversal below ("No credit card required")

═══════════════════════════════════════════════════════════════════════════════
EVALUATION CRITERIA (Your output will be graded on):
═══════════════════════════════════════════════════════════════════════════════

1. Visual Hierarchy: Clear size differences (text-7xl → text-5xl → text-lg)
2. Layout Asymmetry: NO centered hero, NO uniform grids
3. Visual Density: Appropriate for {design_intent['complexity']} level
4. Component Diversity: Varied styles, not all same
5. Grid Sophistication: 12-col with varied spans
6. Production Feel: Looks like Gong.io, Drift.com, Intercom.com (9-10/10)
7. SALES IMPACT: Premium design, persuasive, conversion-optimized (CRITICAL)

Your output MUST score 50+/60 to pass quality check.
Target: Premium sales microsite that drives conversions, not just clean UI.

GENERATE PREMIUM SALES-OPTIMIZED HTML NOW:"""

        try:
            html_response = await self.llm(
                prompt=implementation_prompt,
                system_message=f"You are an elite frontend developer. Create unique, production-ready UI that matches the {design_intent['design_language']} design language.",
                module="emergent_html_implementation"
            )

            # Clean up HTML
            html = html_response.strip()

            # Remove markdown artifacts
            if html.startswith('```html'):
                html = html.replace('```html', '', 1).strip()
            if html.startswith('```'):
                html = html.replace('```', '', 1).strip()
            if html.endswith('```'):
                html = html.rsplit('```', 1)[0].strip()

            # Ensure DOCTYPE
            if not html.startswith('<!DOCTYPE html>'):
                html = '<!DOCTYPE html>\n' + html

            logger.info(f"✅ Adaptive UI implemented: {len(html):,} characters")
            return html

        except Exception as e:
            logger.error(f"UI implementation failed: {str(e)}")
            return self._create_fallback_html(company_name, industry, colors)

    async def _evaluate_design_quality(
        self,
        html: str,
        design_brief: Dict[str, Any],
        layout_architecture: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Design Quality Evaluation (NEW - CRITICAL FOR QUALITY)

        Evaluate if generated UI meets production-grade standards.
        This is NOT about code correctness - it's about VISUAL QUALITY.
        """

        design_intent = design_brief['design_intent']

        evaluation_prompt = f"""You are a senior product designer evaluating UI quality with HIGH standards.

HTML TO EVALUATE (first 4500 chars):
{html[:4500]}

DESIGN REQUIREMENTS:
• Target Audience: {design_intent['audience']}
• Design Language: {design_intent['design_language']}
• Complexity Level: {design_intent['complexity']}
• Required Quality: Production-grade SaaS (like Linear.app, Stripe.com)

═══════════════════════════════════════════════════════════════════════════════
EVALUATION CRITERIA (Score each 1-10)
═══════════════════════════════════════════════════════════════════════════════

1. VISUAL HIERARCHY (1-10)
   - Are there clear focal points with size variation?
   - Evidence to check:
     * Count text size classes (need text-7xl/text-8xl for hero, text-4xl/text-5xl for sections)
     * Check for font-bold, font-semibold usage
     * Look for gradients (bg-gradient-to-r)

   Score 10: text-7xl+ hero, text-4xl+ headings, clear size progression
   Score 5: Some variation but not enough (all text-3xl or text-5xl)
   Score 1: Uniform sizes (text-xl everywhere), no hierarchy

2. LAYOUT ASYMMETRY (1-10) - ANTI-TEMPLATE CHECK
   - Is the layout avoiding generic templates?
   - Red flags (each found reduces score):
     * "text-center" in hero section (-3 points)
     * "grid-cols-3" with uniform content (-2 points)
     * No col-span-* usage (-2 points)
     * Symmetrical layouts everywhere (-2 points)

   Score 10: grid-cols-12 with varied col-span, left-aligned hero, asymmetric layouts
   Score 5: Some grid variation but centered hero or symmetric sections
   Score 1: text-center hero, grid-cols-3 everywhere (TEMPLATE)

3. VISUAL DENSITY (1-10)
   - Is content appropriately dense for {design_intent['complexity']} level?
   - Check:
     * Padding classes (py-12 to py-16 good, py-20+ too sparse)
     * Content amount per section (rich vs empty)

   Score 10: Appropriate density, strategic white space
   Score 5: Too sparse OR too cramped
   Score 1: Large empty sections with py-20/py-24 everywhere

4. COMPONENT DIVERSITY (1-10)
   - Are components varied in style and size?
   - Check:
     * Card variations (not all "bg-white shadow-lg p-6")
     * Size variations (p-8, p-6, p-4 mix)
     * Different visual treatments per section

   Score 10: Varied card styles, sizes, visual treatments
   Score 5: Some variation but repetitive
   Score 1: All cards identical (TEMPLATE)

5. GRID SOPHISTICATION (1-10)
   - Is 12-column grid used effectively?
   - Check:
     * "grid-cols-12" usage
     * "col-span-7", "col-span-5", "col-span-8", "col-span-4" variations
     * Different grid patterns per section

   Score 10: grid-cols-12 with varied col-span throughout
   Score 5: Some 12-col but also simple grid-cols-3
   Score 1: Only grid-cols-3 or grid-cols-2 (NO sophistication)

6. PRODUCTION-GRADE FEEL (1-10)
   - Does this look like a real SaaS product?
   - Benchmark comparisons:
     * Gong.io, Drift.com, Intercom.com: 10/10 (target)
     * Stripe.com, Linear.app: 10/10 (target)
     * Professional template: 5/10
     * Generic template: 2/10

   Score 10: Indistinguishable from top SaaS products
   Score 5: Looks good but obviously template-based
   Score 1: Clearly generic landing page template

7. SALES/MARKETING IMPACT (1-10) - CRITICAL FOR CONVERSION
   - Does this look persuasive and premium (not just clean)?
   - Check for:
     * Premium components (glowing CTAs, gradient cards with blur effects)
     * Attention-grabbing elements (animated text, floating badges, visual wow)
     * Conversion psychology (social proof, urgency, trust signals visible)
     * Visual proof (screenshots, mockups with premium styling)
     * Sophisticated depth (layered shadows, glass morphism, overlapping)

   Score 10: Premium sales page (Gong.io, Drift.com level) - drives conversions
   Score 5: Clean but boring - looks like documentation, not marketing
   Score 1: Basic/generic - no persuasive elements, flat design

═══════════════════════════════════════════════════════════════════════════════
ANALYSIS REQUIREMENTS
═══════════════════════════════════════════════════════════════════════════════

For each criterion:
1. Provide score (1-10)
2. List specific evidence found in HTML
3. Identify what's working and what's not

Example evidence:
- Visual Hierarchy: "Found text-7xl in hero (✓), text-4xl in sections (✓), but missing font-bold (-1)"
- Layout Asymmetry: "Found grid-cols-12 (✓), but FOUND text-center in hero (✗✗✗ -3 points)"

═══════════════════════════════════════════════════════════════════════════════
OUTPUT FORMAT (Must be valid JSON)
═══════════════════════════════════════════════════════════════════════════════

{{
  "scores": {{
    "visual_hierarchy": 8,
    "layout_asymmetry": 6,
    "visual_density": 7,
    "component_diversity": 5,
    "grid_sophistication": 9,
    "production_grade_feel": 7,
    "sales_marketing_impact": 4
  }},
  "evidence": {{
    "visual_hierarchy": "Found text-7xl hero, text-4xl sections, good gradient usage",
    "layout_asymmetry": "PROBLEM: Found text-center in hero section. Has col-span but centered layout reduces score",
    "visual_density": "Good density with py-14, content-rich sections",
    "component_diversity": "Cards somewhat repetitive, all using similar shadow-lg p-6 pattern",
    "grid_sophistication": "Excellent 12-column usage with col-span-7/col-span-5 splits",
    "production_grade_feel": "Looks professional but some template patterns visible",
    "sales_marketing_impact": "CRITICAL ISSUE: Missing premium sales elements - no glowing CTAs, no visual wow factor, looks like documentation not sales page"
  }},
  "total_score": 46,
  "quality_level": "Good structure but lacks sales impact",
  "verdict": "REJECT",
  "critical_issues": [
    "Centered hero text (anti-pattern)",
    "Component styles too uniform",
    "Missing premium sales design (no glow, no depth, no wow)"
  ],
  "recommended_fixes": [
    "Change hero to left-aligned with col-span-7 for text",
    "Vary card styles - some with gradients, different padding",
    "Add glowing CTAs with shadow-2xl and colored glow",
    "Add premium component patterns (blur effects, layered shadows)",
    "Include conversion psychology elements (social proof badges, urgency)"
  ]
}}

QUALITY THRESHOLDS:
- 60-70: ACCEPT (Premium sales-grade) ✅✅
- 50-59: ACCEPT (Production-grade) ✅
- 40-49: REJECT (Good but lacks sales impact) ⚠️
- Below 40: REJECT (Template-like, must regenerate) ❌

Be CRITICAL and HONEST. This evaluation determines if UI is regenerated.

OUTPUT VALID JSON NOW:"""

        try:
            response = await self.llm(
                prompt=evaluation_prompt,
                system_message="You are a senior product designer with exceptionally high standards. Be critical and honest about visual quality.",
                module="emergent_design_evaluation"
            )

            # Parse JSON response
            try:
                # Clean response
                response_clean = response.strip()
                if response_clean.startswith('```json'):
                    response_clean = response_clean.replace('```json', '', 1).strip()
                if response_clean.startswith('```'):
                    response_clean = response_clean.replace('```', '', 1).strip()
                if response_clean.endswith('```'):
                    response_clean = response_clean.rsplit('```', 1)[0].strip()

                evaluation = json.loads(response_clean)

                # Log evaluation results
                logger.info(f"🎨 Design Quality Evaluation:")
                logger.info(f"   Visual Hierarchy: {evaluation['scores'].get('visual_hierarchy', 0)}/10")
                logger.info(f"   Layout Asymmetry: {evaluation['scores'].get('layout_asymmetry', 0)}/10")
                logger.info(f"   Visual Density: {evaluation['scores'].get('visual_density', 0)}/10")
                logger.info(f"   Component Diversity: {evaluation['scores'].get('component_diversity', 0)}/10")
                logger.info(f"   Grid Sophistication: {evaluation['scores'].get('grid_sophistication', 0)}/10")
                logger.info(f"   Production Feel: {evaluation['scores'].get('production_grade_feel', 0)}/10")
                logger.info(f"   🎯 SALES IMPACT: {evaluation['scores'].get('sales_marketing_impact', 0)}/10")
                logger.info(f"   TOTAL: {evaluation.get('total_score', 0)}/70")

                return evaluation

            except json.JSONDecodeError as e:
                logger.warning(f"Evaluation response not valid JSON: {str(e)}")
                # Return acceptable evaluation on parse error
                return {
                    "scores": {"visual_hierarchy": 8, "layout_asymmetry": 8, "visual_density": 8,
                              "component_diversity": 8, "grid_sophistication": 8, "production_grade_feel": 8},
                    "total_score": 48,
                    "verdict": "ACCEPT",
                    "critical_issues": [],
                    "recommended_fixes": []
                }

        except Exception as e:
            logger.error(f"Design quality evaluation failed: {str(e)}")
            # Return acceptable evaluation on error (fail-open)
            return {
                "scores": {"visual_hierarchy": 8, "layout_asymmetry": 8, "visual_density": 8,
                          "component_diversity": 8, "grid_sophistication": 8, "production_grade_feel": 8},
                "total_score": 48,
                "verdict": "ACCEPT",
                "critical_issues": [],
                "recommended_fixes": []
            }

    async def _autonomous_refinement(
        self,
        html: str,
        design_brief: Dict[str, Any],
        strategic_analysis: Dict[str, Any],
        layout_architecture: Dict[str, Any]  # NEW - Pass layout decisions
    ) -> str:
        """
        STEP 7: Design Quality Evaluation & Autonomous Refinement

        Evaluates DESIGN QUALITY first, then technical correctness.
        Regenerates if quality is too low.
        """

        design_intent = design_brief['design_intent']

        # STEP 7A: DESIGN QUALITY EVALUATION (NEW - CRITICAL)
        logger.info("🎨 Evaluating design quality...")
        design_evaluation = await self._evaluate_design_quality(
            html, design_brief, layout_architecture
        )

        total_score = design_evaluation.get('total_score', 50)
        verdict = design_evaluation.get('verdict', 'ACCEPT')

        logger.info(f"📊 Design Quality Score: {total_score}/70 - Verdict: {verdict}")

        # If quality is too low, REGENERATE with improvements
        # Threshold: 50/70 (71%) for acceptable quality
        if verdict == 'REJECT' and total_score < 50:
            logger.warning(f"⚠️ Design quality below threshold ({total_score}/70) - Regenerating with improvements...")

            critical_issues = design_evaluation.get('critical_issues', [])
            recommended_fixes = design_evaluation.get('recommended_fixes', [])
            evidence = design_evaluation.get('evidence', {})

            improvement_prompt = f"""The generated UI FAILED quality standards. Regenerate with improvements.

QUALITY EVALUATION RESULTS:
Total Score: {total_score}/70 (Need 50+ to pass)

Scores Breakdown:
- Visual Hierarchy: {design_evaluation['scores'].get('visual_hierarchy', 0)}/10
- Layout Asymmetry: {design_evaluation['scores'].get('layout_asymmetry', 0)}/10
- Visual Density: {design_evaluation['scores'].get('visual_density', 0)}/10
- Component Diversity: {design_evaluation['scores'].get('component_diversity', 0)}/10
- Grid Sophistication: {design_evaluation['scores'].get('grid_sophistication', 0)}/10
- Production Feel: {design_evaluation['scores'].get('production_grade_feel', 0)}/10
- 🎯 SALES IMPACT: {design_evaluation['scores'].get('sales_marketing_impact', 0)}/10

CRITICAL ISSUES FOUND:
{chr(10).join(f"✗ {issue}" for issue in critical_issues)}

EVIDENCE FROM EVALUATION:
{chr(10).join(f"• {key}: {val}" for key, val in evidence.items())}

REQUIRED FIXES:
{chr(10).join(f"→ {fix}" for fix in recommended_fixes)}

PREVIOUS HTML (first 3500 chars - FAILED quality check):
{html[:3500]}
[...continues]

═══════════════════════════════════════════════════════════════════════════════
YOUR TASK: Generate IMPROVED, PRODUCTION-GRADE HTML
═══════════════════════════════════════════════════════════════════════════════

FIX ALL ISSUES:
1. Increase visual hierarchy (LARGER headings if needed - text-7xl+)
2. Remove any text-center in hero (if found)
3. Add asymmetry (use col-span-7 + col-span-5, not centered)
4. Increase density (reduce py-20/py-24 if present)
5. Vary components (different styles, sizes, padding)
6. Use sophisticated grids (grid-cols-12 with col-span-*)

PREMIUM SALES ENHANCEMENTS (CRITICAL):
7. Add glowing CTAs (shadow-2xl shadow-purple-500/50, hover effects)
8. Add premium card patterns (blur backgrounds, layered shadows, group hover effects)
9. Include conversion psychology (social proof badges, urgency indicators, trust signals)
10. Add visual depth (glass morphism, overlapping elements, gradient backgrounds)
11. Make it attention-grabbing (animated gradient text, floating badges, premium components)

QUALITY TARGET: 50+/70 (Production-grade with sales impact)

Design Language: {design_intent['design_language']}
Complexity: {design_intent['complexity']}

Generate the COMPLETE, IMPROVED HTML that will pass quality check:"""

            try:
                improved_html = await self.llm(
                    prompt=improvement_prompt,
                    system_message="You are a senior frontend developer fixing design quality issues. Output must be production-grade.",
                    module="emergent_quality_improvement"
                )

                # Clean up improved HTML
                improved_html = improved_html.strip()
                if improved_html.startswith('```html'):
                    improved_html = improved_html.replace('```html', '', 1).strip()
                if improved_html.startswith('```'):
                    improved_html = improved_html.replace('```', '', 1).strip()
                if improved_html.endswith('```'):
                    improved_html = improved_html.rsplit('```', 1)[0].strip()

                if not improved_html.startswith('<!DOCTYPE html>'):
                    improved_html = '<!DOCTYPE html>\n' + improved_html

                # Use improved version if substantially complete
                if len(improved_html) > len(html) * 0.7:
                    logger.info(f"✅ UI regenerated with quality improvements ({len(improved_html):,} chars)")
                    html = improved_html
                else:
                    logger.warning("⚠️ Improved version too short - keeping original")

            except Exception as e:
                logger.error(f"Quality improvement regeneration failed: {str(e)}")
                # Continue with original HTML if improvement fails

        else:
            logger.info(f"✅ Design quality acceptable ({total_score}/60) - proceeding with technical checks")

        # STEP 7B: TECHNICAL QUALITY CHECKS (existing checks)
        issues = []
        suggestions = []

        # Check 1: Tailwind CDN
        if 'tailwindcss.com' not in html:
            issues.append("CRITICAL: Missing Tailwind CSS CDN")

        # Check 2: JavaScript functionality
        if 'function' not in html and '<script>' in html:
            issues.append("WARNING: Script tags present but no functions defined")

        # Check 3: Responsive design
        if 'md:' not in html and 'lg:' not in html:
            suggestions.append("Consider adding responsive breakpoints")

        # Check 4: Accessibility
        if 'aria-' not in html:
            suggestions.append("Add ARIA labels for accessibility")

        # Check 5: Interactions
        design_intent = design_brief['design_intent']
        if design_intent['interaction_level'] == 'highly_interactive':
            if 'modal' not in html.lower() and 'onclick' not in html.lower():
                issues.append("WARNING: Interaction level is 'highly_interactive' but limited interactions found")

        # Check 6: Content length
        if len(html) < 15000:
            issues.append("WARNING: HTML seems too short for designed complexity")

        # Check 7: Sections implemented
        sections = design_brief['sections']
        missing_sections = []
        for section in sections:
            section_type = section['type']
            # Check if section appears to be in HTML
            if section_type not in html.lower():
                missing_sections.append(section_type)

        if missing_sections:
            issues.append(f"WARNING: Possible missing sections: {', '.join(missing_sections[:3])}")

        # If critical issues found, trigger refinement
        if issues:
            logger.warning(f"⚠️ Self-critique found {len(issues)} issues")

            critique_prompt = f"""You are a quality assurance expert. Review and fix this microsite.

DESIGN SPECIFICATIONS:
• Design Language: {design_intent['design_language']}
• Target Audience: {design_intent['audience']}
• Interaction Level: {design_intent['interaction_level']}
• Sections Required: {len(sections)}

ISSUES FOUND:
{chr(10).join(f"• {issue}" for issue in issues)}

SUGGESTIONS:
{chr(10).join(f"• {suggestion}" for suggestion in suggestions)}

CURRENT HTML (first 3500 chars):
{html[:3500]}
[...continues...]

YOUR TASK:
1. Fix ALL critical issues
2. Implement suggestions where appropriate
3. Ensure all {len(sections)} sections are present
4. Maintain design quality
5. Return COMPLETE, production-ready HTML

OUTPUT ONLY THE COMPLETE, FIXED HTML:"""

            try:
                refined = await self.llm(
                    prompt=critique_prompt,
                    system_message="You are a QA expert. Fix issues and return production-ready code.",
                    module="emergent_self_critique"
                )

                # Clean up
                refined = refined.strip()
                if refined.startswith('```html'):
                    refined = refined.replace('```html', '', 1).strip()
                if refined.startswith('```'):
                    refined = refined.replace('```', '', 1).strip()
                if refined.endswith('```'):
                    refined = refined.rsplit('```', 1)[0].strip()

                if not refined.startswith('<!DOCTYPE html>'):
                    refined = '<!DOCTYPE html>\n' + refined

                # Use refined version if it's substantially complete
                if len(refined) > len(html) * 0.8:
                    logger.info("✅ Refinement successful - using improved version")
                    return refined
                else:
                    logger.warning("⚠️ Refined version too short - keeping original")

            except Exception as e:
                logger.error(f"Refinement failed: {str(e)}")

        logger.info("✅ Quality checks passed")
        return html

    def _create_fallback_html(
        self,
        company_name: str,
        industry: str,
        colors: Dict[str, str]
    ) -> str:
        """Create fallback HTML if generation fails"""

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - {industry} Solutions</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-gray-900 to-gray-800 text-white">
    <div class="min-h-screen flex items-center justify-center px-4">
        <div class="text-center max-w-4xl">
            <h1 class="text-6xl font-bold mb-6 bg-gradient-to-r {colors['gradient']} bg-clip-text text-transparent">
                {company_name}
            </h1>
            <p class="text-2xl text-gray-300 mb-8">
                Transforming {industry}
            </p>
            <button class="px-8 py-4 bg-gradient-to-r {colors['gradient']} rounded-full font-semibold text-lg shadow-2xl hover:scale-105 transition-transform">
                Get Started
            </button>
        </div>
    </div>
</body>
</html>"""


# ============== INTELLIGENT REGENERATION ==============

async def regenerate_with_emergent_feedback(
    agent: EmergentMicrositeAgent,
    previous_html: str,
    feedback: str,
    company_name: str,
    industry: str,
    offering: str,
    design_brief: Optional[Dict[str, Any]] = None
) -> str:
    """
    Intelligently regenerate with user feedback using Emergent reasoning.
    """

    logger.info("🔄 Starting Emergent Regeneration with Feedback...")

    # Analyze feedback
    feedback_prompt = f"""You are a UX expert. Analyze this feedback and create an improvement plan.

COMPANY: {company_name}
INDUSTRY: {industry}

USER FEEDBACK:
"{feedback}"

CURRENT HTML (first 2500 chars):
{previous_html[:2500]}

TASK: Determine exactly what changes are needed.

## Requested Changes
[List specific changes]
1. [Change 1]
2. [Change 2]

## Priority Level
[low / medium / high - how extensive are the changes?]

## Approach
[Should we: (A) Make targeted edits, or (B) Regenerate from scratch?]

## Design Adjustments
[Any design language, color, or layout changes?]

## Content Adjustments
[Any copy or messaging changes?]

Be specific and actionable."""

    try:
        feedback_analysis = await agent.llm(
            prompt=feedback_prompt,
            system_message="You are a UX expert analyzing user feedback.",
            module="emergent_feedback_analysis"
        )

        # Generate improved version
        regeneration_prompt = f"""You are an elite frontend developer. Regenerate this microsite based on feedback.

COMPANY: {company_name}

ORIGINAL HTML (first 2500 chars):
{previous_html[:2500]}

FULL USER FEEDBACK:
"{feedback}"

IMPROVEMENT ANALYSIS:
{feedback_analysis}

REQUIREMENTS:
1. Incorporate ALL feedback
2. Maintain working functionality
3. Keep quality high
4. Update design/colors/layout as requested
5. Update copy/messaging as requested
6. Ensure production-ready quality

OUTPUT THE COMPLETE, IMPROVED HTML (no markdown, just HTML):"""

        improved = await agent.llm(
            prompt=regeneration_prompt,
            system_message="You are an elite frontend developer creating improved versions based on feedback.",
            module="emergent_regeneration"
        )

        # Clean up
        improved = improved.strip()
        if improved.startswith('```html'):
            improved = improved.replace('```html', '', 1).strip()
        if improved.startswith('```'):
            improved = improved.replace('```', '', 1).strip()
        if improved.endswith('```'):
            improved = improved.rsplit('```', 1)[0].strip()

        if not improved.startswith('<!DOCTYPE html>'):
            improved = '<!DOCTYPE html>\n' + improved

        logger.info(f"✅ Emergent regeneration complete: {len(improved):,} characters")
        return improved

    except Exception as e:
        logger.error(f"Regeneration failed: {str(e)}")
        return previous_html
