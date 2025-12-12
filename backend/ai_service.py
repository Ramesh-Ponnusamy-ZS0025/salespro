import os
from dotenv import load_dotenv
import logging
from typing import List, Dict
import asyncio
from groq import Groq

load_dotenv()

logger = logging.getLogger(__name__)

class AIContentGenerator:
    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY')
        if not self.api_key:
            logger.error("GROQ_API_KEY not found in environment variables")
            raise ValueError("GROQ_API_KEY not configured")
        self.client = Groq(api_key=self.api_key)
    
    def extract_insights(self, linkedin_data: Dict) -> List[str]:
        """Extract key insights from LinkedIn profile data"""
        insights = []
        
        # Name and title insights
        if linkedin_data.get('name'):
            insights.append(f"Name: {linkedin_data['name']}")
        
        if linkedin_data.get('title'):
            insights.append(f"Current Role: {linkedin_data['title']}")
        
        if linkedin_data.get('company'):
            insights.append(f"Company: {linkedin_data['company']}")
        
        # Location
        if linkedin_data.get('location'):
            insights.append(f"Location: {linkedin_data['location']}")
        
        # Recent posts analysis
        if linkedin_data.get('posts') and len(linkedin_data['posts']) > 0:
            insights.append(f"LinkedIn Activity: {len(linkedin_data['posts'])} recent posts")
            # Get content from post object
            post_content = linkedin_data['posts'][0].get('content', '') if isinstance(linkedin_data['posts'][0], dict) else str(linkedin_data['posts'][0])
            insights.append(f"Recent Topic: {post_content[:100]}...")
        
        # Experience insights
        if linkedin_data.get('experience') and len(linkedin_data['experience']) > 0:
            exp_count = len(linkedin_data['experience'])
            insights.append(f"Experience: {exp_count} previous roles")
        
        # Skills
        if linkedin_data.get('skills') and len(linkedin_data['skills']) > 0:
            top_skills = ', '.join(linkedin_data['skills'][:5])
            insights.append(f"Key Skills: {top_skills}")
        
        return insights
    
    async def generate_personalized_content(
        self,
        linkedin_data: Dict,
        selected_insights: List[Dict] = None,
        case_studies: List[Dict] = None,
        content_type: str = "email",
        tone: str = "professional",
        value_proposition: str = None,
        additional_context: str = None,
        message_length: str = "100-200"
    ):
        """Generate personalized content based on LinkedIn profile and selected insights"""

        # Extract insights (fallback if selected_insights not provided)
        if not selected_insights:
            insights = self.extract_insights(linkedin_data)
        else:
            insights = [f"{insight.get('category', '')}: {insight.get('title', '')} - {insight.get('content', '')}"
                       for insight in selected_insights]

        # Build system message
        system_message = f"""You are an expert sales AI assistant specialized in creating hyper-personalized outreach messages.
Your goal is to craft compelling, personalized {content_type}s that drive engagement and responses.

Key principles:
1. Use specific details from the prospect's LinkedIn profile and selected insights
2. Be conversational and authentic
3. Highlight relevant value propositions
4. Target length: {message_length} words
5. Include a clear call-to-action
6. Tone: {tone}
7. Incorporate relevant case studies if provided
8. Use psychological triggers and communication style insights if available
"""

        # Build user prompt
        user_prompt = f"""Create a personalized {content_type} for this prospect:

**Prospect Information:**
- Name: {linkedin_data.get('name', 'Unknown')}
- Title: {linkedin_data.get('title', 'Unknown')}
- Company: {linkedin_data.get('company', 'Unknown')}
- Location: {linkedin_data.get('location', 'Unknown')}
"""

        # Add selected insights organized by category
        if selected_insights:
            user_prompt += "\n**Selected Insights to Reference:**\n"

            # Group insights by category
            insights_by_category = {}
            for insight in selected_insights:
                category = insight.get('category', 'Other')
                if category not in insights_by_category:
                    insights_by_category[category] = []
                insights_by_category[category].append(insight)

            # Add each category
            for category, insights_list in insights_by_category.items():
                user_prompt += f"\n{category}:\n"
                for insight in insights_list:
                    user_prompt += f"- {insight.get('title', '')}: {insight.get('content', '')}\n"

        # Add case studies if provided
        if case_studies and len(case_studies) > 0:
            user_prompt += "\n\n**Relevant Case Studies to Reference:**\n"
            for cs in case_studies[:2]:  # Limit to top 2 most relevant
                user_prompt += f"- {cs.get('title', '')}: {cs.get('excerpt', '')}\n"
                if cs.get('relevance_score', 0) > 0:
                    user_prompt += f"  (Relevance: {int(cs['relevance_score'] * 100)}%)\n"

        if value_proposition:
            user_prompt += f"\n\n**Our Value Proposition:**\n{value_proposition}"

        if additional_context:
            user_prompt += f"\n\n**Additional Context:**\n{additional_context}"

        user_prompt += f"""

**Task:**
Generate a {content_type} that:
1. References specific details from their profile and the selected insights
2. Demonstrates you've done deep research
3. Uses their communication style and psychological triggers if identified
4. Incorporates relevant case studies naturally
5. Offers clear value aligned with their role and company
6. Includes a specific, actionable call-to-action
7. Feels authentic and personal (not templated)
8. Target length: {message_length} words"""
        
        try:
            # Generate content using Groq
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                model="llama-3.3-70b-versatile",  # Using Llama 3.3 70B for high quality
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9
            )

            # Extract generated text
            response = chat_completion.choices[0].message.content

            # Calculate personalization score (more sophisticated)
            score = self.calculate_personalization_score(
                insights=insights,
                has_value_prop=bool(value_proposition),
                has_context=bool(additional_context),
                profile_completeness=self.assess_profile_completeness(linkedin_data)
            )

            return response, insights, score

        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise Exception(f"Failed to generate content: {str(e)}")
    
    async def generate_multiple_variations(
        self,
        linkedin_data: Dict,
        count: int = 3,
        content_type: str = "email",
        tone: str = "professional"
    ):
        """Generate multiple content variations"""
        tasks = [
            self.generate_personalized_content(
                linkedin_data=linkedin_data,
                content_type=content_type,
                tone=tone
            )
            for _ in range(count)
        ]
        
        results = await asyncio.gather(*tasks)
        return results

    def assess_profile_completeness(self, linkedin_data: Dict) -> float:
        """Assess how complete the LinkedIn profile data is (0-1 scale)"""
        completeness_score = 0.0
        max_score = 0.0

        # Basic info (40% weight)
        if linkedin_data.get('name'):
            completeness_score += 10
        if linkedin_data.get('title'):
            completeness_score += 10
        if linkedin_data.get('company'):
            completeness_score += 10
        if linkedin_data.get('location'):
            completeness_score += 10
        max_score += 40

        # About section (20% weight)
        if linkedin_data.get('about'):
            completeness_score += 20
        max_score += 20

        # Experience (20% weight)
        if linkedin_data.get('experience') and len(linkedin_data['experience']) > 0:
            completeness_score += min(20, len(linkedin_data['experience']) * 5)
        max_score += 20

        # Posts/Activity (20% weight)
        if linkedin_data.get('posts') and len(linkedin_data['posts']) > 0:
            completeness_score += min(20, len(linkedin_data['posts']) * 7)
        max_score += 20

        return completeness_score / max_score if max_score > 0 else 0.0

    def calculate_personalization_score(
        self,
        insights: List[str],
        has_value_prop: bool,
        has_context: bool,
        profile_completeness: float
    ) -> int:
        """
        Calculate a personalization score (0-99) based on multiple factors

        Scoring breakdown:
        - Profile completeness: 0-40 points
        - Number of insights: 0-30 points (3 points per insight, max 10 insights)
        - Value proposition included: +15 points
        - Additional context provided: +14 points
        """
        score = 0

        # Profile completeness (0-40 points)
        score += int(profile_completeness * 40)

        # Insights count (0-30 points, max at 10 insights)
        insights_score = min(30, len(insights) * 3)
        score += insights_score

        # Value proposition (+15 points)
        if has_value_prop:
            score += 15

        # Additional context (+14 points)
        if has_context:
            score += 14

        # Cap at 99
        return min(99, score)