"""
Intelligent Microsite AI Agent
Multi-step reasoning agent that creates exceptional, unique microsites
Works like Claude/Emergent with deep analysis and strategic generation
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class IntelligentMicrositeAgent:
    """
    Advanced AI agent for generating high-quality microsites using multi-step reasoning.

    This agent mimics how Claude or Emergent would approach the task:
    1. Deep analysis of context
    2. Strategic planning
    3. Creative content generation
    4. Technical implementation
    5. Quality refinement
    """

    def __init__(self, llm_function):
        """
        Initialize the intelligent agent.

        Args:
            llm_function: Async function for LLM calls
        """
        self.llm = llm_function
        self.conversation_history = []

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
        Generate a high-quality microsite using multi-step intelligent reasoning.

        Returns:
            Complete HTML for the microsite
        """
        logger.info("🧠 Starting Intelligent Microsite Agent...")
        logger.info(f"📊 Generating for: {company_name} in {industry}")

        # STEP 1: Deep Analysis
        logger.info("STEP 1/5: 🔍 Performing deep analysis...")
        analysis = await self._analyze_context(
            company_name, industry, offering, pain_points,
            target_personas, linkedin_url
        )

        # STEP 2: Strategic Planning
        logger.info("STEP 2/5: 🎯 Creating strategic plan...")
        strategy = await self._create_strategy(
            company_name, industry, offering, pain_points,
            target_personas, analysis, use_cases, key_features
        )

        # STEP 3: Content Generation
        logger.info("STEP 3/5: ✍️ Generating unique content...")
        content = await self._generate_content(
            company_name, industry, offering, pain_points,
            target_personas, analysis, strategy, case_studies
        )

        # STEP 4: Design & Implementation
        logger.info("STEP 4/5: 🎨 Creating beautiful design...")
        html = await self._create_html_implementation(
            company_name, industry, content, strategy, analysis
        )

        # STEP 5: Quality Refinement
        logger.info("STEP 5/5: ✨ Polishing and refining...")
        final_html = await self._refine_and_polish(html, strategy)

        logger.info("✅ Intelligent Microsite Agent completed successfully!")
        return final_html

    async def _analyze_context(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        linkedin_url: Optional[str]
    ) -> Dict[str, Any]:
        """
        STEP 1: Deep contextual analysis
        Understand the company, industry, audience, and competitive landscape
        """

        analysis_prompt = f"""You are an elite business strategist and market analyst. Perform a deep analysis of this company.

COMPANY INFORMATION:
- Name: {company_name}
- Industry: {industry}
- Offering: {offering}
- LinkedIn: {linkedin_url or 'Not provided'}

PAIN POINTS THEY ADDRESS:
{chr(10).join(f"• {pp}" for pp in pain_points)}

TARGET AUDIENCE:
{', '.join(target_personas)}

YOUR TASK:
Analyze this company deeply and provide insights that will inform an exceptional microsite design.

Output a comprehensive analysis in the following format:

## Company Positioning
[2-3 sentences on how this company should position itself]

## Unique Value Proposition
[What makes them truly unique - go beyond obvious features]

## Emotional Drivers
[What emotions should the microsite evoke? Why would prospects care?]

## Industry Context
[Key industry trends, challenges, and how this offering fits]

## Target Audience Psychology
[What keeps these personas up at night? What do they really want?]

## Competitive Differentiation
[How should we differentiate from competitors in this space?]

## Key Messages
[3-5 core messages that should permeate the microsite]

## Design Direction
[What visual style, tone, and aesthetic would resonate?]

## Conversion Strategy
[What path should we lead prospects down? What's the goal?]

Be insightful, strategic, and creative. Think deeply about what would truly resonate."""

        try:
            response = await self.llm(
                prompt=analysis_prompt,
                system_message="You are an elite business strategist with deep expertise in positioning, messaging, and conversion psychology. Provide thoughtful, strategic insights.",
                module="microsite_analysis"
            )

            # Parse the response into structured data
            analysis = {
                "raw_analysis": response,
                "company_name": company_name,
                "industry": industry,
                "offering": offering
            }

            # Extract key insights for later use
            logger.info(f"✅ Analysis complete: {len(response)} characters of strategic insights")
            return analysis

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "raw_analysis": "Standard professional positioning",
                "company_name": company_name,
                "industry": industry,
                "offering": offering
            }

    async def _create_strategy(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        analysis: Dict[str, Any],
        use_cases: Optional[List[str]],
        key_features: Optional[List[str]]
    ) -> Dict[str, Any]:
        """
        STEP 2: Strategic Planning
        Create a strategic blueprint for the microsite
        """

        strategy_prompt = f"""You are an expert UX strategist and conversion specialist. Based on the analysis below, create a strategic blueprint for an exceptional microsite.

COMPANY: {company_name}
INDUSTRY: {industry}
OFFERING: {offering}

ANALYSIS INSIGHTS:
{analysis.get('raw_analysis', '')}

PAIN POINTS:
{chr(10).join(f"• {pp}" for pp in pain_points)}

TARGET PERSONAS:
{', '.join(target_personas)}

USE CASES PROVIDED:
{chr(10).join(f"• {uc}" for uc in (use_cases or [])) if use_cases else 'None - please create relevant ones'}

KEY FEATURES:
{chr(10).join(f"• {kf}" for kf in (key_features or [])) if key_features else 'None - derive from offering'}

YOUR TASK:
Create a strategic blueprint for the microsite. Be specific and creative.

Output in this format:

## Hero Section Strategy
Headline: [Powerful 3-part headline that captures attention]
Subheadline: [Compelling subheadline explaining the transformation]
Visual Concept: [What should the hero section look like?]
CTA: [What action should we drive?]

## Section Flow
[List 8-12 sections in order with brief purpose for each]
1. Section name - purpose
2. Section name - purpose
...

## Content Themes
[3-5 key themes that should flow through all content]

## Visual Style Direction
Color Scheme: [Primary, secondary, accent colors with rationale]
Typography: [Font personality - modern, classic, bold, etc.]
Imagery: [What type of visuals would work best?]
Overall Aesthetic: [Professional, futuristic, warm, bold, etc.]

## Interactive Elements Strategy
[What interactive elements would engage prospects?]
- Use case modals
- [Other interactive ideas]

## Conversion Optimization
Primary Goal: [What's the main conversion goal?]
Secondary Goals: [Other desired actions]
Trust Builders: [How do we build credibility?]

## Differentiation Strategy
[How will this microsite stand out from competitors?]

Be creative, strategic, and specific. Think about what would truly wow prospects."""

        try:
            response = await self.llm(
                prompt=strategy_prompt,
                system_message="You are an elite UX strategist and conversion expert. Create thoughtful, creative strategies that drive results.",
                module="microsite_strategy"
            )

            strategy = {
                "raw_strategy": response,
                "company_name": company_name,
                "industry": industry
            }

            logger.info(f"✅ Strategy complete: {len(response)} characters of strategic planning")
            return strategy

        except Exception as e:
            logger.error(f"Strategy creation failed: {str(e)}")
            return {
                "raw_strategy": "Standard microsite structure with hero, features, use cases, testimonials, and CTA sections",
                "company_name": company_name,
                "industry": industry
            }

    async def _generate_content(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        analysis: Dict[str, Any],
        strategy: Dict[str, Any],
        case_studies: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """
        STEP 3: Content Generation
        Create unique, compelling copy for all sections
        """

        content_prompt = f"""You are an award-winning copywriter specializing in B2B sales content. Create exceptional, unique copy for this microsite.

COMPANY: {company_name}
INDUSTRY: {industry}
OFFERING: {offering}

STRATEGIC INSIGHTS:
{analysis.get('raw_analysis', '')[:1000]}

STRATEGIC BLUEPRINT:
{strategy.get('raw_strategy', '')[:1000]}

PAIN POINTS TO ADDRESS:
{chr(10).join(f"• {pp}" for pp in pain_points)}

TARGET AUDIENCE:
{', '.join(target_personas)}

CASE STUDIES AVAILABLE:
{len(case_studies) if case_studies else 0} case studies available for reference

YOUR TASK:
Write compelling, unique copy for each section of the microsite. Make it resonate emotionally while being professional.

Output in this format:

## Hero Section
Headline: [Powerful, attention-grabbing headline]
Subheadline: [Compelling value proposition]
CTA Button Text: [Action-oriented button text]

## Trust Bar
Heading: [e.g., "Trusted by Industry Leaders"]

## Problem/Pain Points Section
Section Heading: [Creative heading]
Introduction: [2-3 sentences setting up the pain points]
Pain Point 1 - Title: [Short, punchy title]
Pain Point 1 - Description: [1-2 compelling sentences]
Pain Point 2 - Title: [Short, punchy title]
Pain Point 2 - Description: [1-2 compelling sentences]
[Continue for 3-6 pain points based on input]

## Solution/Value Props Section
Section Heading: [Creative heading]
Introduction: [2-3 sentences explaining the transformation]
Value Prop 1 - Title: [Benefit-focused title]
Value Prop 1 - Description: [Compelling description of the benefit]
Value Prop 2 - Title: [Benefit-focused title]
Value Prop 2 - Description: [Compelling description of the benefit]
[3-4 value propositions]

## Use Cases Section
Section Heading: [Creative heading]
Use Case 1 - Title: [Specific, relatable scenario]
Use Case 1 - Description: [What problem it solves]
Use Case 1 - Benefit: [Measurable outcome, e.g., "70% faster processing"]
[Create 4-6 relevant use cases]

## Results/Metrics Section
Section Heading: [Creative heading]
Metric 1 - Number: [e.g., "75%"]
Metric 1 - Label: [e.g., "Faster Processing"]
Metric 1 - Description: [Brief explanation]
[4 compelling metrics]

## Testimonials
Testimonial 1 - Quote: [Authentic-sounding testimonial]
Testimonial 1 - Name: [Professional name]
Testimonial 1 - Title: [Job title]
Testimonial 1 - Company: [Company name]
[3 testimonials]

## CTA Section
Heading: [Compelling call-to-action heading]
Subheading: [Supporting text]
Primary CTA: [Button text]
Secondary CTA: [Alternate button text]

## Form Fields
Contact Form Heading: [Heading for contact form]
Privacy Text: [Brief privacy assurance]

Make all copy:
- Unique and specific to {company_name}
- Emotionally resonant
- Benefit-focused (outcomes, not features)
- Professional yet warm
- Free of clichés and generic phrases
- Compelling and conversion-optimized"""

        try:
            response = await self.llm(
                prompt=content_prompt,
                system_message="You are an award-winning B2B copywriter. Create unique, compelling copy that drives action while building trust.",
                module="microsite_content"
            )

            content = {
                "raw_content": response,
                "company_name": company_name
            }

            logger.info(f"✅ Content generation complete: {len(response)} characters of unique copy")
            return content

        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return {
                "raw_content": "Standard professional copy",
                "company_name": company_name
            }

    async def _create_html_implementation(
        self,
        company_name: str,
        industry: str,
        content: Dict[str, Any],
        strategy: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> str:
        """
        STEP 4: HTML Implementation
        Create beautiful, modern, production-ready HTML
        """

        implementation_prompt = f"""You are an elite frontend developer and designer. Create a stunning, production-ready HTML microsite.

COMPANY: {company_name}
INDUSTRY: {industry}

STRATEGIC DIRECTION:
{strategy.get('raw_strategy', '')[:800]}

CONTENT (USE THIS COPY EXACTLY):
{content.get('raw_content', '')[:3000]}

REQUIREMENTS:
1. Use Tailwind CSS CDN
2. Modern, beautiful design with smooth animations
3. Fully responsive (mobile-first)
4. Interactive elements (modals, hover effects, smooth scrolling)
5. Use the content provided above - don't make up new content
6. Include proper semantic HTML5
7. Accessible (ARIA labels, keyboard navigation)
8. Professional color scheme appropriate for {industry}
9. Engaging visual hierarchy
10. Production-ready code

OUTPUT REQUIREMENTS:
- Output ONLY the complete HTML
- No markdown code blocks, no explanations
- Start with <!DOCTYPE html>
- Well-formatted and properly indented
- Include ALL JavaScript for interactions
- Include ALL CSS animations in <style> tag

STRUCTURE:
- Sticky navigation
- Hero section with gradient background
- Trust indicators/logos
- Pain points section (cards with icons)
- Solution/value props section (cards with gradients)
- Interactive use cases (clickable cards that open modals with demos)
- Results/metrics section (large numbers, visual impact)
- Testimonials (cards with stars and photos)
- CTA section with contact form
- Footer
- Modal structures for use case demos

DESIGN STANDARDS:
- Modern color palette (blues, purples, or industry-appropriate)
- Generous white space
- Card-based layouts with hover effects
- Smooth transitions and animations
- Glass morphism and gradient accents
- Rounded corners (rounded-2xl)
- Shadow elevations (shadow-lg, shadow-xl)

JAVASCRIPT FEATURES:
- Modal open/close
- Smooth scroll to sections
- Mobile menu toggle
- Fade-in on scroll (Intersection Observer)
- Form submission handling
- Scroll progress indicator

Make it absolutely stunning. This should look like a $50,000 professionally designed microsite.

OUTPUT ONLY THE HTML - START NOW:"""

        try:
            html_response = await self.llm(
                prompt=implementation_prompt,
                system_message="You are an elite frontend developer and designer. Create beautiful, production-ready code that wows users.",
                module="microsite_html"
            )

            # Clean up the HTML response
            html = html_response.strip()

            # Remove markdown code blocks if present
            if html.startswith('```html'):
                html = html.replace('```html', '', 1).strip()
            if html.startswith('```'):
                html = html.replace('```', '', 1).strip()
            if html.endswith('```'):
                html = html.rsplit('```', 1)[0].strip()

            # Ensure it starts with DOCTYPE
            if not html.startswith('<!DOCTYPE html>'):
                html = '<!DOCTYPE html>\n' + html

            logger.info(f"✅ HTML implementation complete: {len(html)} characters")
            return html

        except Exception as e:
            logger.error(f"HTML implementation failed: {str(e)}")
            # Return a basic fallback
            return self._create_fallback_html(company_name, industry)

    async def _refine_and_polish(
        self,
        html: str,
        strategy: Dict[str, Any]
    ) -> str:
        """
        STEP 5: Refinement & Polish
        Review and enhance the generated HTML for quality and completeness
        """

        # Check for common issues
        issues = []

        if '<script src="https://cdn.tailwindcss.com"></script>' not in html:
            issues.append("Missing Tailwind CDN")

        if 'function openModal' not in html and 'openModal' in html:
            issues.append("Modal functions referenced but not defined")

        if len(html) < 10000:
            issues.append("HTML seems too short")

        # If there are critical issues, try to fix them
        if issues:
            logger.warning(f"⚠️ Found issues in HTML: {', '.join(issues)}")

            refinement_prompt = f"""Review and fix this HTML microsite. Issues found:
{chr(10).join(f"- {issue}" for issue in issues)}

CURRENT HTML (first 3000 chars):
{html[:3000]}

Please provide the COMPLETE, FIXED HTML. Ensure:
1. Tailwind CDN is included
2. All JavaScript functions are properly defined
3. All modals work correctly
4. The HTML is complete and production-ready

OUTPUT ONLY THE COMPLETE HTML:"""

            try:
                refined = await self.llm(
                    prompt=refinement_prompt,
                    system_message="You are a quality assurance expert. Fix any issues and return production-ready code.",
                    module="microsite_refinement"
                )

                # Clean up
                refined = refined.strip()
                if refined.startswith('```html'):
                    refined = refined.replace('```html', '', 1).strip()
                if refined.startswith('```'):
                    refined = refined.replace('```', '', 1).strip()
                if refined.endswith('```'):
                    refined = refined.rsplit('```', 1)[0].strip()

                if len(refined) > len(html):
                    logger.info("✅ Refinement improved the HTML")
                    return refined

            except Exception as e:
                logger.error(f"Refinement failed: {str(e)}")

        logger.info("✅ HTML passed quality checks")
        return html

    def _create_fallback_html(self, company_name: str, industry: str) -> str:
        """Create a basic fallback HTML if generation fails"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{company_name} - Transforming {industry}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="min-h-screen flex items-center justify-center">
        <div class="text-center">
            <h1 class="text-5xl font-bold text-gray-900 mb-4">{company_name}</h1>
            <p class="text-xl text-gray-600">Transforming {industry}</p>
        </div>
    </div>
</body>
</html>"""


# ============== REGENERATION WITH FEEDBACK ==============

async def regenerate_with_intelligent_feedback(
    agent: IntelligentMicrositeAgent,
    previous_html: str,
    feedback: str,
    company_name: str,
    industry: str,
    offering: str,
    pain_points: List[str],
    target_personas: List[str],
    use_cases: Optional[List[str]] = None,
    key_features: Optional[List[str]] = None
) -> str:
    """
    Intelligently regenerate microsite based on user feedback.

    This function analyzes the feedback, understands what needs to change,
    and generates an improved version.
    """

    logger.info("🔄 Starting Intelligent Regeneration with Feedback...")

    feedback_analysis_prompt = f"""You are an expert UX designer and feedback analyst. Analyze this user feedback and create an improvement plan.

COMPANY: {company_name}
INDUSTRY: {industry}
OFFERING: {offering}

USER FEEDBACK:
{feedback}

PREVIOUS HTML (first 2000 chars):
{previous_html[:2000]}

YOUR TASK:
Analyze the feedback and create a detailed improvement plan.

Output in this format:

## Feedback Analysis
[What is the user asking for? Be specific.]

## Changes Required
[List specific changes to make]
1. [Change 1]
2. [Change 2]
...

## Visual Direction
[If feedback mentions design/colors/style, specify the new direction]

## Content Changes
[If feedback mentions copy/messaging, specify what to update]

## Structural Changes
[If feedback mentions layout/sections, specify what to rearrange]

## Key Priorities
[What are the top 3 most important changes?]

Be thorough and specific."""

    try:
        # Analyze the feedback
        analysis = await agent.llm(
            prompt=feedback_analysis_prompt,
            system_message="You are an expert at understanding user feedback and translating it into actionable improvements.",
            module="feedback_analysis"
        )

        logger.info("✅ Feedback analyzed")

        # Generate improved version
        regeneration_prompt = f"""You are an elite frontend developer. Regenerate this microsite incorporating the user's feedback.

COMPANY: {company_name}
INDUSTRY: {industry}

ORIGINAL HTML (first 2000 chars):
{previous_html[:2000]}

USER FEEDBACK:
{feedback}

IMPROVEMENT PLAN:
{analysis}

REQUIREMENTS:
1. Incorporate ALL feedback points
2. Maintain what was working well
3. Make improvements clearly visible
4. Keep the same structure unless feedback requests changes
5. Update colors, layout, copy as requested
6. Maintain all interactive functionality
7. Ensure production-ready quality

Pain Points: {', '.join(pain_points)}
Target Audience: {', '.join(target_personas)}

OUTPUT THE COMPLETE, IMPROVED HTML:"""

        improved_html = await agent.llm(
            prompt=regeneration_prompt,
            system_message="You are an elite frontend developer. Create the improved version based on feedback.",
            module="microsite_regeneration"
        )

        # Clean up
        improved_html = improved_html.strip()
        if improved_html.startswith('```html'):
            improved_html = improved_html.replace('```html', '', 1).strip()
        if improved_html.startswith('```'):
            improved_html = improved_html.replace('```', '', 1).strip()
        if improved_html.endswith('```'):
            improved_html = improved_html.rsplit('```', 1)[0].strip()

        if not improved_html.startswith('<!DOCTYPE html>'):
            improved_html = '<!DOCTYPE html>\n' + improved_html

        logger.info(f"✅ Intelligent regeneration complete: {len(improved_html)} characters")
        return improved_html

    except Exception as e:
        logger.error(f"Intelligent regeneration failed: {str(e)}")
        return previous_html  # Return original if regeneration fails
