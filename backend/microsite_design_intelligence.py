"""
Microsite Design Intelligence Engine
====================================

This module provides autonomous design reasoning and decision-making for microsite generation.
It analyzes context and makes intelligent UX/UI decisions without relying on templates.

Inspired by Emergent's adaptive UI generation.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import re


class DesignComplexity(Enum):
    """UI complexity levels based on business context"""
    MINIMAL = "minimal"  # Single-page focus, few sections
    MODERATE = "moderate"  # Standard multi-section layout
    RICH = "rich"  # Complex interactions, multiple layers
    IMMERSIVE = "immersive"  # Full experience, storytelling


class AudienceType(Enum):
    """Target audience classification"""
    TECHNICAL = "technical"  # Developers, engineers
    EXECUTIVE = "executive"  # C-suite, decision makers
    BUSINESS = "business"  # Product managers, operations
    CONSUMER = "consumer"  # End users, general public
    MEDICAL = "medical"  # Healthcare professionals
    FINANCIAL = "financial"  # Finance professionals


class DesignLanguage(Enum):
    """Visual design systems"""
    MODERN_MINIMAL = "modern_minimal"  # Clean, spacious, monochrome
    VIBRANT_TECH = "vibrant_tech"  # Gradients, bold colors, futuristic
    PROFESSIONAL_ENTERPRISE = "professional_enterprise"  # Conservative, trustworthy
    CREATIVE_BOLD = "creative_bold"  # Artistic, unique, expressive
    MEDICAL_TRUST = "medical_trust"  # Calming, precise, credible
    FINANCIAL_SECURE = "financial_secure"  # Stable, authoritative


@dataclass
class DesignIntent:
    """Inferred design requirements from context"""
    complexity: DesignComplexity
    audience: AudienceType
    design_language: DesignLanguage
    primary_goal: str  # e.g., "lead_generation", "education", "conversion"
    interaction_level: str  # "static", "interactive", "highly_interactive"
    content_density: str  # "minimal", "moderate", "high"
    emotional_tone: str  # "professional", "friendly", "urgent", "inspiring"


@dataclass
class SectionDecision:
    """Decision about whether to include a section"""
    section_type: str
    include: bool
    priority: int  # 1-10, determines order
    reasoning: str
    layout_variant: str  # e.g., "grid", "list", "hero", "split"
    interaction_type: str  # "static", "hover", "click", "scroll"


class DesignIntelligenceEngine:
    """
    Autonomous design decision engine that reasons about UX/UI without templates.
    """

    # Keywords for audience detection
    AUDIENCE_KEYWORDS = {
        AudienceType.TECHNICAL: ["developers", "engineers", "api", "sdk", "code", "technical", "integration"],
        AudienceType.EXECUTIVE: ["c-suite", "executive", "leadership", "strategy", "roi", "growth"],
        AudienceType.BUSINESS: ["teams", "operations", "productivity", "workflow", "efficiency"],
        AudienceType.CONSUMER: ["users", "customers", "simple", "easy", "intuitive"],
        AudienceType.MEDICAL: ["healthcare", "medical", "clinical", "patients", "diagnosis"],
        AudienceType.FINANCIAL: ["finance", "trading", "investment", "banking", "compliance"],
    }

    # Keywords for design language selection
    DESIGN_LANGUAGE_KEYWORDS = {
        DesignLanguage.VIBRANT_TECH: ["ai", "ml", "automation", "innovative", "future", "digital"],
        DesignLanguage.PROFESSIONAL_ENTERPRISE: ["enterprise", "b2b", "corporate", "business", "professional"],
        DesignLanguage.MEDICAL_TRUST: ["healthcare", "medical", "clinical", "health", "wellness"],
        DesignLanguage.FINANCIAL_SECURE: ["finance", "banking", "investment", "secure", "compliance"],
        DesignLanguage.CREATIVE_BOLD: ["creative", "design", "agency", "marketing", "brand"],
    }

    def __init__(self):
        self.section_library = self._build_section_library()

    def analyze_context(
        self,
        company_name: str,
        industry: str,
        offering: str,
        pain_points: List[str],
        target_personas: List[str],
        use_cases: List[str],
        key_features: List[str],
    ) -> DesignIntent:
        """
        Analyze all available context and infer design requirements.
        This is autonomous - it doesn't ask questions, it reasons.
        """

        # Combine all text for analysis
        all_text = " ".join([
            company_name, industry, offering,
            " ".join(pain_points),
            " ".join(target_personas),
            " ".join(use_cases),
            " ".join(key_features),
        ]).lower()

        # Infer audience type
        audience = self._detect_audience(all_text, target_personas)

        # Infer design language
        design_language = self._detect_design_language(all_text, industry)

        # Determine complexity needed
        complexity = self._determine_complexity(
            offering, pain_points, use_cases, key_features
        )

        # Infer primary goal
        primary_goal = self._infer_primary_goal(all_text, industry)

        # Determine interaction level
        interaction_level = self._determine_interaction_level(
            complexity, audience, offering
        )

        # Determine content density
        content_density = self._determine_content_density(
            pain_points, use_cases, key_features
        )

        # Determine emotional tone
        emotional_tone = self._determine_emotional_tone(
            industry, audience, primary_goal
        )

        return DesignIntent(
            complexity=complexity,
            audience=audience,
            design_language=design_language,
            primary_goal=primary_goal,
            interaction_level=interaction_level,
            content_density=content_density,
            emotional_tone=emotional_tone,
        )

    def plan_architecture(
        self,
        design_intent: DesignIntent,
        company_name: str,
        offering: str,
        pain_points: List[str],
        use_cases: List[str],
        key_features: List[str],
        has_case_studies: bool = False,
    ) -> List[SectionDecision]:
        """
        Autonomously decide which sections to include and in what order.
        This replaces the fixed 12-section template approach.
        """

        decisions = []

        # Always include hero (but variant depends on context)
        hero_variant = self._choose_hero_variant(design_intent)
        decisions.append(SectionDecision(
            section_type="hero",
            include=True,
            priority=1,
            reasoning="Hero section is essential for first impression and value communication",
            layout_variant=hero_variant,
            interaction_type="scroll" if design_intent.interaction_level != "static" else "static",
        ))

        # Decide on trust indicators (logos, badges, etc.)
        if design_intent.audience in [AudienceType.EXECUTIVE, AudienceType.BUSINESS]:
            decisions.append(SectionDecision(
                section_type="trust_bar",
                include=True,
                priority=2,
                reasoning="Executive/business audience needs social proof early",
                layout_variant="logo_carousel",
                interaction_type="hover",
            ))

        # Problem/pain points section
        if len(pain_points) >= 3:
            layout = "grid" if len(pain_points) >= 4 else "list"
            decisions.append(SectionDecision(
                section_type="problems",
                include=True,
                priority=3,
                reasoning=f"Multiple pain points ({len(pain_points)}) justify dedicated section",
                layout_variant=layout,
                interaction_type="hover",
            ))

        # Solution/value proposition
        decisions.append(SectionDecision(
            section_type="solution",
            include=True,
            priority=4,
            reasoning="Core value proposition is critical for conversion",
            layout_variant=self._choose_solution_layout(design_intent, key_features),
            interaction_type="click" if design_intent.interaction_level == "highly_interactive" else "hover",
        ))

        # Use cases / How it works
        if len(use_cases) >= 2:
            uc_layout = self._choose_use_case_layout(design_intent, len(use_cases))
            decisions.append(SectionDecision(
                section_type="use_cases",
                include=True,
                priority=5,
                reasoning=f"Use cases ({len(use_cases)}) demonstrate practical value",
                layout_variant=uc_layout,
                interaction_type="click" if uc_layout == "interactive_cards" else "hover",
            ))

        # Features (if substantial)
        if len(key_features) >= 4:
            decisions.append(SectionDecision(
                section_type="features",
                include=True,
                priority=6,
                reasoning="Extensive feature list warrants dedicated showcase",
                layout_variant="grid" if design_intent.content_density == "high" else "highlight",
                interaction_type="hover",
            ))

        # Social proof / case studies
        if has_case_studies:
            decisions.append(SectionDecision(
                section_type="case_studies",
                include=True,
                priority=7,
                reasoning="Case studies available - crucial for credibility",
                layout_variant="cards_with_metrics",
                interaction_type="click",
            ))

        # Results / ROI
        if design_intent.audience in [AudienceType.EXECUTIVE, AudienceType.BUSINESS]:
            decisions.append(SectionDecision(
                section_type="roi_metrics",
                include=True,
                priority=8,
                reasoning="Business audience expects quantified outcomes",
                layout_variant="big_numbers",
                interaction_type="scroll",
            ))

        # Technical architecture (for technical audiences)
        if design_intent.audience == AudienceType.TECHNICAL:
            decisions.append(SectionDecision(
                section_type="architecture",
                include=True,
                priority=9,
                reasoning="Technical audience needs architecture details",
                layout_variant="diagram",
                interaction_type="interactive" if design_intent.interaction_level == "highly_interactive" else "static",
            ))

        # Why choose us / Differentiators
        if design_intent.complexity != DesignComplexity.MINIMAL:
            decisions.append(SectionDecision(
                section_type="why_us",
                include=True,
                priority=10,
                reasoning="Differentiation important for competitive positioning",
                layout_variant="icon_grid",
                interaction_type="hover",
            ))

        # Testimonials (if not already showing case studies)
        if not has_case_studies:
            decisions.append(SectionDecision(
                section_type="testimonials",
                include=True,
                priority=11,
                reasoning="Social proof via testimonials (no case studies available)",
                layout_variant="cards",
                interaction_type="static",
            ))

        # CTA
        cta_variant = "form" if design_intent.primary_goal == "lead_generation" else "buttons"
        decisions.append(SectionDecision(
            section_type="cta",
            include=True,
            priority=12,
            reasoning="Conversion point is mandatory",
            layout_variant=cta_variant,
            interaction_type="click",
        ))

        # Footer
        decisions.append(SectionDecision(
            section_type="footer",
            include=True,
            priority=13,
            reasoning="Footer provides navigation and legal info",
            layout_variant="standard",
            interaction_type="static",
        ))

        # Sort by priority and filter to only included sections
        included = [d for d in decisions if d.include]
        included.sort(key=lambda x: x.priority)

        return included

    def _detect_audience(self, text: str, personas: List[str]) -> AudienceType:
        """Detect primary audience from context"""
        scores = {audience: 0 for audience in AudienceType}

        # Score based on keywords
        for audience, keywords in self.AUDIENCE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[audience] += 1

        # Boost based on personas
        for persona in personas:
            persona_lower = persona.lower()
            if "developer" in persona_lower or "engineer" in persona_lower:
                scores[AudienceType.TECHNICAL] += 2
            elif "cto" in persona_lower or "ceo" in persona_lower or "executive" in persona_lower:
                scores[AudienceType.EXECUTIVE] += 2
            elif "manager" in persona_lower or "analyst" in persona_lower:
                scores[AudienceType.BUSINESS] += 2

        # Return highest scoring audience
        max_audience = max(scores.items(), key=lambda x: x[1])
        return max_audience[0] if max_audience[1] > 0 else AudienceType.BUSINESS

    def _detect_design_language(self, text: str, industry: str) -> DesignLanguage:
        """Detect appropriate design language"""
        scores = {lang: 0 for lang in DesignLanguage}

        # Score based on keywords
        for lang, keywords in self.DESIGN_LANGUAGE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text:
                    scores[lang] += 1

        # Industry-based boosting
        industry_lower = industry.lower()
        if "healthcare" in industry_lower or "medical" in industry_lower:
            scores[DesignLanguage.MEDICAL_TRUST] += 3
        elif "finance" in industry_lower or "banking" in industry_lower:
            scores[DesignLanguage.FINANCIAL_SECURE] += 3
        elif "technology" in industry_lower or "software" in industry_lower:
            scores[DesignLanguage.VIBRANT_TECH] += 2
        elif "enterprise" in industry_lower or "b2b" in industry_lower:
            scores[DesignLanguage.PROFESSIONAL_ENTERPRISE] += 2

        # Return highest scoring language
        max_lang = max(scores.items(), key=lambda x: x[1])
        return max_lang[0] if max_lang[1] > 0 else DesignLanguage.MODERN_MINIMAL

    def _determine_complexity(
        self,
        offering: str,
        pain_points: List[str],
        use_cases: List[str],
        key_features: List[str],
    ) -> DesignComplexity:
        """Determine required UI complexity"""

        # Count total content elements
        total_elements = len(pain_points) + len(use_cases) + len(key_features)

        # Check if offering is complex
        offering_complexity = len(offering.split()) > 20

        if total_elements >= 15 or offering_complexity:
            return DesignComplexity.RICH
        elif total_elements >= 8:
            return DesignComplexity.MODERATE
        elif total_elements <= 4:
            return DesignComplexity.MINIMAL
        else:
            return DesignComplexity.MODERATE

    def _infer_primary_goal(self, text: str, industry: str) -> str:
        """Infer the primary business goal"""

        if any(word in text for word in ["demo", "trial", "signup", "register"]):
            return "lead_generation"
        elif any(word in text for word in ["buy", "purchase", "pricing", "subscribe"]):
            return "direct_sale"
        elif any(word in text for word in ["learn", "discover", "understand", "explore"]):
            return "education"
        elif any(word in text for word in ["enterprise", "b2b", "partnership"]):
            return "enterprise_sale"
        else:
            return "lead_generation"  # Default

    def _determine_interaction_level(
        self,
        complexity: DesignComplexity,
        audience: AudienceType,
        offering: str,
    ) -> str:
        """Determine how interactive the UI should be"""

        # Technical audiences appreciate interactive demos
        if audience == AudienceType.TECHNICAL:
            return "highly_interactive"

        # Complex offerings benefit from interaction
        if complexity in [DesignComplexity.RICH, DesignComplexity.IMMERSIVE]:
            return "highly_interactive"

        # Executive audiences prefer clarity over interaction
        if audience == AudienceType.EXECUTIVE:
            return "interactive"

        return "interactive"

    def _determine_content_density(
        self,
        pain_points: List[str],
        use_cases: List[str],
        key_features: List[str],
    ) -> str:
        """Determine how dense the content should be"""

        total = len(pain_points) + len(use_cases) + len(key_features)

        if total >= 15:
            return "high"
        elif total >= 8:
            return "moderate"
        else:
            return "minimal"

    def _determine_emotional_tone(
        self,
        industry: str,
        audience: AudienceType,
        primary_goal: str,
    ) -> str:
        """Determine emotional tone of messaging"""

        industry_lower = industry.lower()

        if "healthcare" in industry_lower or "medical" in industry_lower:
            return "caring"
        elif "finance" in industry_lower:
            return "professional"
        elif audience == AudienceType.EXECUTIVE:
            return "authoritative"
        elif primary_goal == "lead_generation":
            return "inspiring"
        else:
            return "friendly"

    def _choose_hero_variant(self, design_intent: DesignIntent) -> str:
        """Choose appropriate hero section layout"""

        if design_intent.interaction_level == "highly_interactive":
            return "split_with_demo"
        elif design_intent.audience == AudienceType.EXECUTIVE:
            return "centered_bold"
        elif design_intent.design_language == DesignLanguage.VIBRANT_TECH:
            return "gradient_full"
        else:
            return "split_standard"

    def _choose_solution_layout(
        self,
        design_intent: DesignIntent,
        key_features: List[str],
    ) -> str:
        """Choose layout for solution section"""

        if len(key_features) >= 6:
            return "grid_compact"
        elif design_intent.interaction_level == "highly_interactive":
            return "interactive_tabs"
        else:
            return "cards_spacious"

    def _choose_use_case_layout(
        self,
        design_intent: DesignIntent,
        use_case_count: int,
    ) -> str:
        """Choose layout for use cases"""

        if design_intent.interaction_level == "highly_interactive":
            return "interactive_cards"
        elif use_case_count >= 5:
            return "grid"
        else:
            return "list_with_visuals"

    def _build_section_library(self) -> Dict[str, Any]:
        """Build library of available section types and their configurations"""

        return {
            "hero": {
                "variants": ["split_standard", "centered_bold", "gradient_full", "split_with_demo"],
                "required_data": ["headline", "subheadline", "cta"],
            },
            "trust_bar": {
                "variants": ["logo_carousel", "logo_grid", "badges"],
                "required_data": ["client_logos"],
            },
            "problems": {
                "variants": ["grid", "list", "comparison"],
                "required_data": ["pain_points"],
            },
            "solution": {
                "variants": ["cards_spacious", "grid_compact", "interactive_tabs"],
                "required_data": ["value_propositions"],
            },
            "use_cases": {
                "variants": ["interactive_cards", "grid", "list_with_visuals"],
                "required_data": ["use_cases"],
            },
            "features": {
                "variants": ["grid", "highlight", "comparison_table"],
                "required_data": ["key_features"],
            },
            "case_studies": {
                "variants": ["cards_with_metrics", "carousel", "detailed_list"],
                "required_data": ["case_studies"],
            },
            "roi_metrics": {
                "variants": ["big_numbers", "chart_dashboard", "comparison"],
                "required_data": ["metrics"],
            },
            "architecture": {
                "variants": ["diagram", "before_after", "interactive"],
                "required_data": ["tech_stack"],
            },
            "why_us": {
                "variants": ["icon_grid", "timeline", "comparison"],
                "required_data": ["differentiators"],
            },
            "testimonials": {
                "variants": ["cards", "carousel", "video"],
                "required_data": ["testimonials"],
            },
            "cta": {
                "variants": ["form", "buttons", "split"],
                "required_data": ["cta_text"],
            },
            "footer": {
                "variants": ["standard", "minimal", "rich"],
                "required_data": ["company_info"],
            },
        }


def create_design_brief(
    company_name: str,
    industry: str,
    offering: str,
    pain_points: List[str],
    target_personas: List[str],
    use_cases: List[str],
    key_features: List[str],
    has_case_studies: bool = False,
) -> Dict[str, Any]:
    """
    Main entry point: Analyze context and create a complete design brief.
    This is what the generation agent will use instead of a template.
    """

    engine = DesignIntelligenceEngine()

    # Analyze context
    design_intent = engine.analyze_context(
        company_name, industry, offering, pain_points,
        target_personas, use_cases, key_features
    )

    # Plan architecture
    architecture = engine.plan_architecture(
        design_intent, company_name, offering,
        pain_points, use_cases, key_features, has_case_studies
    )

    # Create brief
    brief = {
        "design_intent": {
            "complexity": design_intent.complexity.value,
            "audience": design_intent.audience.value,
            "design_language": design_intent.design_language.value,
            "primary_goal": design_intent.primary_goal,
            "interaction_level": design_intent.interaction_level,
            "content_density": design_intent.content_density,
            "emotional_tone": design_intent.emotional_tone,
        },
        "sections": [
            {
                "type": section.section_type,
                "priority": section.priority,
                "layout_variant": section.layout_variant,
                "interaction_type": section.interaction_type,
                "reasoning": section.reasoning,
            }
            for section in architecture
        ],
        "total_sections": len(architecture),
    }

    return brief
