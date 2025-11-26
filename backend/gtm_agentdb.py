# AgentDB Integration for GTM Generator
# Dynamic AI Assistant that refines, organizes, and structures user inputs intelligently

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import json
import re

logger = logging.getLogger(__name__)

class PromptSection:
    """Represents a structured section of the final prompt"""
    def __init__(self, name: str, title: str, content: str = "", priority: int = 0):
        self.name = name
        self.title = title
        self.content = content
        self.priority = priority
        self.subsections = {}
    
    def add_subsection(self, key: str, value: str):
        """Add or update a subsection"""
        self.subsections[key] = value
    
    def merge_content(self, new_content: str, llm_refine_func=None):
        """Merge new content with existing, optionally using LLM to refine"""
        if not self.content:
            self.content = new_content
        elif llm_refine_func:
            # Use LLM to intelligently merge
            self.content = llm_refine_func(self.content, new_content)
        else:
            # Simple append with formatting
            self.content = f"{self.content}\n\n{new_content}"
    
    def render(self) -> str:
        """Render section as formatted text"""
        output = f"## {self.title}\n"
        if self.content:
            output += f"{self.content}\n"
        for key, value in self.subsections.items():
            output += f"\n### {key}\n{value}\n"
        return output


class GTMAgentDB:
    """
    AgentDB-based GTM Generator with intelligent context management
    Mimics ChatGPT's iterative refinement approach from the reference conversation
    """
    
    SECTION_DEFINITIONS = {
        "objective": {"title": "🎯 Objective", "priority": 1},
        "prospect_profile": {"title": "🏢 Prospect Profile", "priority": 2},
        "solution": {"title": "💡 Our Solution", "priority": 3},
        "pain_points": {"title": "🎯 Pain Points to Address", "priority": 4},
        "key_features": {"title": "✨ Key Features to Highlight", "priority": 5},
        "customer_profile": {"title": "👥 Customer Profile", "priority": 6},
        "design_requirements": {"title": "🎨 Design Requirements", "priority": 7},
        "ui_personalization": {"title": "🎨 UI & Personalization Details", "priority": 8},
        "ceo_details": {"title": "👔 CEO & Leadership", "priority": 9},
        "technical_requirements": {"title": "🛠 Technical Requirements", "priority": 10},
        "conversion_elements": {"title": "🎯 Conversion Elements", "priority": 11},
        "interactive_features": {"title": "📱 Interactive Features", "priority": 12},
        "case_studies": {"title": "📚 Relevant Case Studies", "priority": 13},
        "key_metrics": {"title": "📊 Key Metrics to Display", "priority": 14},
        "tone_messaging": {"title": "💬 Tone & Messaging", "priority": 15},
    }
    
    def __init__(self):
        self.conversation_memory = []
        self.prompt_sections = {}
        self.extracted_entities = {
            "company_info": {},
            "people": [],
            "features": [],
            "pain_points": [],
            "metrics": [],
            "design_preferences": [],
        }
        self._initialize_sections()
    
    def _initialize_sections(self):
        """Initialize prompt sections structure"""
        for section_key, section_info in self.SECTION_DEFINITIONS.items():
            self.prompt_sections[section_key] = PromptSection(
                name=section_key,
                title=section_info["title"],
                priority=section_info["priority"]
            )
    
    def process_user_input(
        self, 
        user_message: str, 
        form_data: Dict, 
        validation_result: Optional[Dict],
        llm_extract_func=None
    ) -> Dict:
        """
        Process user input with intelligent extraction and organization
        
        Args:
            user_message: Raw user input
            form_data: Current form configuration
            validation_result: Validation data
            llm_extract_func: Function to call LLM for extraction (async)
        
        Returns:
            Response dict with action, message, and updated state
        """
        
        message_lower = user_message.lower().strip()
        
        # Store in conversation memory
        self.conversation_memory.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Check for generate commands
        generate_keywords = ['generate', 'create', 'yes', 'go ahead', 'proceed', 
                           'generate prompt', 'lets go', "let's go", 'ready', 'done']
        
        if any(keyword in message_lower for keyword in generate_keywords):
            # Check if we have enough information
            required_sections = ["prospect_profile", "solution", "pain_points"]
            missing = [s for s in required_sections if not self.prompt_sections[s].content]
            
            if missing and len(self.conversation_memory) < 3:
                # Too early to generate, need more context
                return {
                    "action": "clarify",
                    "message": (
                        "I'd love to generate the prompt, but I need a bit more information first. "
                        "Could you share details about:\n\n"
                        "• The prospect's pain points\n"
                        "• Your solution/offering\n"
                        "• Target decision makers\n\n"
                        "Feel free to provide these in any order!"
                    ),
                    "should_regenerate": False,
                    "updated_validation": validation_result
                }
            print(validation_result)
            print('self._build_extracted_context()',self._build_extracted_context())
            return {
                "action": "generate",
                "message": "Perfect! Generating your comprehensive microsite prompt now... 🚀",
                "should_regenerate": True,
                "updated_validation": validation_result,
                "extracted_context": self._build_extracted_context()
            }
        
        # Use LLM to extract structured information if function provided
        if llm_extract_func:
            extraction_result = llm_extract_func(user_message, self._get_current_context())
            print('llm llm_extract_func',extraction_result)
            if extraction_result:

                self._process_extraction(extraction_result)

        # Classify intent and respond accordingly
        intent = self._classify_intent(user_message, form_data)
        print('user_message',user_message)
        print('intent',intent)
        
        if intent == "add_information":
            # Check if extraction result has specific action type
            action_type = extraction_result.get("action", "add") if extraction_result else "add"
            summary = extraction_result.get("summary", "") if extraction_result else ""

            if action_type == "remove":
                response = f"✅ {summary}\n\nI've removed that from the microsite configuration. The final prompt will reflect these changes when generated."
            elif action_type == "modify":
                response = f"✅ {summary}\n\nI've updated the microsite configuration with the new details."
            else:
                response = self._handle_information_addition(user_message, form_data, summary)

            return {
                "action": "update",
                "message": response,
                "should_regenerate": False,
                "updated_validation": validation_result,
                "extracted_context": self._build_extracted_context()
            }
        
        elif intent == "ask_question":
            response = self._answer_question(user_message, form_data, validation_result)
            return {
                "action": "clarify",
                "message": response,
                "should_regenerate": False,
                "updated_validation": validation_result
            }
        
        elif intent == "modify_config":
            response = self._handle_configuration_change(user_message, form_data)
            return {
                "action": "update",
                "message": response,
                "should_regenerate": False,
                "updated_validation": validation_result
            }
        
        else:  # unclear
            return {
                "action": "clarify",
                "message": self._request_clarification(user_message, form_data),
                "should_regenerate": False,
                "updated_validation": validation_result
            }
    
    def _classify_intent(self, message: str, form_data: Dict) -> str:
        """Classify user intent from message"""
        message_lower = message.lower()
        
        # Check for information addition indicators
        info_indicators = ['add', 'include', 'also', 'our', 'we', 'company', 'ceo', 
                          'team', 'pricing', 'feature', 'customer', 'want', 'need',
                          'should', 'could', 'make', 'design', 'color', 'style']
        
        # Check for questions
        question_indicators = ['what', 'how', 'why', 'can you', 'could you', 
                              'would you', '?', 'explain', 'tell me']
        
        # Check for modifications
        modify_indicators = ['change', 'update', 'modify', 'adjust', 'different', 
                            'instead', 'rather', 'not']
        
        word_count = len(message.split())
        
        has_info_indicators = any(ind in message_lower.split() for ind in info_indicators)
        has_question_indicators = any(ind in message_lower.split() for ind in question_indicators)
        has_modify_indicators = any(ind in message_lower.split() for ind in modify_indicators)
        if has_question_indicators:
            return "ask_question"
        elif has_modify_indicators:
            return "modify_config"
        elif has_info_indicators:
            return "add_information"
        else:
            return "unclear"
    
    def _process_extraction(self, extraction: Dict):
        """Process LLM extraction results and update sections with support for add/remove/modify"""

        action = extraction.get("action", "add")

        # Handle REMOVE actions
        if action == "remove":
            section_key = extraction.get("target_section")
            removal_targets = extraction.get("removal_targets", [])

            if section_key in self.prompt_sections and removal_targets:
                # Remove matching content from section
                current_content = self.prompt_sections[section_key].content
                for target in removal_targets:
                    # Case-insensitive removal of lines containing target
                    lines = current_content.split('\n')
                    filtered_lines = [
                        line for line in lines
                        if target.lower() not in line.lower()
                    ]
                    current_content = '\n'.join(filtered_lines)
                self.prompt_sections[section_key].content = current_content
                logger.info(f"Removed '{removal_targets}' from section '{section_key}'")
            return

        # Update extracted entities (for ADD and MODIFY actions)
        extracted_data = extraction.get("extracted", {})

        if "company_info" in extracted_data:
            self.extracted_entities["company_info"].update(extracted_data["company_info"])

        if "people" in extracted_data:
            for person in extracted_data["people"]:
                if person not in self.extracted_entities["people"]:
                    self.extracted_entities["people"].append(person)

        if "features" in extracted_data:
            for feature in extracted_data["features"]:
                if feature not in self.extracted_entities["features"]:
                    self.extracted_entities["features"].append(feature)

        if "pain_points" in extracted_data:
            for pain in extracted_data["pain_points"]:
                if pain not in self.extracted_entities["pain_points"]:
                    self.extracted_entities["pain_points"].append(pain)

        if "metrics" in extracted_data:
            for metric in extracted_data["metrics"]:
                if metric not in self.extracted_entities["metrics"]:
                    self.extracted_entities["metrics"].append(metric)

        if "design_preferences" in extracted_data:
            for pref in extracted_data["design_preferences"]:
                if pref not in self.extracted_entities["design_preferences"]:
                    self.extracted_entities["design_preferences"].append(pref)

        # Handle case study actions
        if "case_study_actions" in extracted_data:
            cs_actions = extracted_data["case_study_actions"]
            if "remove" in cs_actions:
                # Store removed case studies in a special list
                if "removed_case_studies" not in self.extracted_entities:
                    self.extracted_entities["removed_case_studies"] = []
                self.extracted_entities["removed_case_studies"].extend(cs_actions["remove"])

        # Update prompt sections based on extraction
        if "target_section" in extraction:
            section_key = extraction["target_section"]
            content = extraction.get("content", "")

            if section_key in self.prompt_sections and content:
                if action == "modify":
                    # Replace content completely for modify actions
                    self.prompt_sections[section_key].content = content
                    logger.info(f"Modified section '{section_key}' with new content")
                else:
                    # Append content for add actions
                    self.prompt_sections[section_key].merge_content(content)
                    logger.info(f"Added content to section '{section_key}': {content[:50]}...")
    
    def _handle_information_addition(self, message: str, form_data: Dict, summary: str = "") -> str:
        """Handle user adding new information"""
        # Count total sections with content
        filled_sections = sum(1 for s in self.prompt_sections.values() if s.content)

        # Use LLM-provided summary if available, otherwise create generic message
        if summary:
            response = f"✅ {summary}\n\n"
        else:
            response = f"✅ Great! I've added that information to the microsite configuration.\n\n"

        response += f"**Current Progress**: {filled_sections}/{len(self.SECTION_DEFINITIONS)} sections filled\n\n"

        if filled_sections >= 5:
            response += "We have good coverage now. Would you like to:\n"
            response += "1. **Generate the prompt** with current details\n"
            response += "2. **Add more information** to any section\n"
        else:
            response += "Feel free to add more details, or let me know when you're ready to generate!"

        return response
    
    def _handle_configuration_change(self, message: str, form_data: Dict) -> str:
        """Handle user requesting configuration changes"""
        return (
            "I understand you'd like to make some changes. Could you be more specific? For example:\n\n"
            "• Change the target personas\n"
            "• Update pain points\n"
            "• Modify design preferences\n"
            "• Adjust technical requirements\n\n"
            "Let me know what you'd like to update!"
        )
    
    def _answer_question(self, question: str, form_data: Dict, validation_result: Optional[Dict]) -> str:
        """Answer user questions intelligently"""
        question_lower = question.lower()
        
        if any(keyword in question_lower for keyword in ['case stud', 'example', 'proof']):
            case_count = validation_result.get('use_case_count', 0) if validation_result else 0
            return (
                f"The microsite will include **{case_count} relevant case studies** from your document library. "
                "These will be automatically selected based on industry relevance and displayed in the social proof section "
                "with metrics, outcomes, and credibility indicators.\n\n"
                "Ready to generate?"
            )
        
        if any(keyword in question_lower for keyword in ['persona', 'target', 'audience', 'decision maker']):
            personas = form_data.get('target_personas', 'your target audience')
            return (
                f"The microsite will be tailored for **{personas}**. Every element—from messaging to CTAs—will be "
                "customized to resonate with their specific pain points, decision-making criteria, and business priorities.\n\n"
                "Would you like to refine the personas or generate the prompt?"
            )
        
        if any(keyword in question_lower for keyword in ['design', 'look', 'style', 'ui', 'visual']):
            return (
                "The microsite will feature:\n\n"
                "• **Modern gradient backgrounds** (blue/purple tones)\n"
                "• **Interactive animations** and smooth scroll effects\n"
                "• **Card-based layouts** with icons and imagery\n"
                "• **Mobile-first responsive design**\n"
                "• **Fast loading** with optimized assets\n\n"
                "Any specific design preferences you'd like to add?"
            )
        
        if any(keyword in question_lower for keyword in ['section', 'include', 'structure']):
            return (
                "The microsite will include these key sections:\n\n"
                "1. Hero with compelling headline\n"
                "2. Pain points grid (3-column)\n"
                "3. Solution overview with features\n"
                "4. Use cases and results\n"
                "5. Social proof (case studies, testimonials)\n"
                "6. Call-to-action sections\n"
                "7. Interactive elements\n\n"
                "Want to add any custom sections?"
            )
        
        # Generic helpful response
        return (
            "I can help with various aspects:\n\n"
            "• Design and visual style\n"
            "• Content and messaging\n"
            "• Case studies and social proof\n"
            "• Technical features\n"
            "• Conversion optimization\n\n"
            "What specific aspect would you like to know more about?"
        )
    
    def _request_clarification(self, message: str, form_data: Dict) -> str:
        """Request clarification for vague input"""
        return (
            "I want to make sure I understand what you need. Could you provide more detail? For example:\n\n"
            "• **Add specific information** (CEO details, team info, pricing, features)\n"
            "• **Describe design preferences** (colors, style, layout)\n"
            "• **Share customer insights** (personas, buying behavior)\n"
            "• **Generate the prompt** with current configuration\n\n"
            "What would be most helpful?"
        )
    
    def _get_current_context(self) -> Dict:
        """Get current conversation context for LLM"""
        return {
            "conversation_history": self.conversation_memory[-5:],  # Last 5 messages
            "filled_sections": [
                {"section": k, "content": v.content[:200]} 
                for k, v in self.prompt_sections.items() 
                if v.content
            ],
            "extracted_entities": self.extracted_entities
        }
    
    def _build_extracted_context(self) -> Dict:
        """Build extracted context for prompt generation"""
        return {
            "sections": {
                k: {
                    "title": v.title,
                    "content": v.content,
                    "subsections": v.subsections
                }
                for k, v in self.prompt_sections.items()
                if v.content or v.subsections
            },
            "entities": self.extracted_entities
        }
    
    def build_final_prompt(self, form_data: Dict, validation_result: Dict, case_studies: List[Dict]) -> str:
        """
        Build comprehensive final prompt with all collected information
        organized into proper sections
        """
        
        # Sort sections by priority
        sorted_sections = sorted(
            self.prompt_sections.values(),
            key=lambda x: x.priority
        )
        
        prompt_parts = []
        
        # Add objective (always present)
        company = form_data.get('company_name', 'the prospect')
        industry = form_data.get('industry', 'their industry')
        
        objective = (
            f"Create a high-converting, interactive microsite for prospecting **{company}** "
            f"in the **{industry}** industry.\n\n"
            f"Generate a modern, engaging single-page microsite that convinces decision-makers to book a meeting."
        )
        prompt_parts.append(f"## 🎯 Objective\n{objective}\n")
        
        # Add configured sections with content
        for section in sorted_sections:
            if section.content or section.subsections:
                prompt_parts.append(section.render())
        
        # Add case studies section
        if case_studies:
            case_studies_text = self._format_case_studies(case_studies)
            prompt_parts.append(f"## 📚 Relevant Case Studies\n{case_studies_text}\n")
        
        # Add standard technical requirements
        prompt_parts.append(self._get_technical_requirements())
        
        # Add deliverable section
        prompt_parts.append(self._get_deliverable_section(company))
        
        return "\n\n".join(prompt_parts)
    
    def _format_case_studies(self, case_studies: List[Dict]) -> str:
        """Format case studies for inclusion in prompt"""
        text = "**These are REAL case studies from your database. Use them to add credibility:**\n\n"
        
        for idx, cs in enumerate(case_studies, 1):
            title = cs.get('filename', 'Untitled').replace('.pdf', '').replace('_', ' ')
            summary = cs.get('summary', 'No summary available')[:300]
            category = cs.get('category', 'General')
            
            text += f"### {idx}. {title}\n"
            text += f"- **Category**: {category}\n"
            if summary:
                text += f"- **Summary**: {summary}...\n"
            text += "\n"
        
        return text
    
    def _get_technical_requirements(self) -> str:
        """Get standard technical requirements"""
        return """## 🛠 Technical Requirements

- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS with custom animations
- **Icons**: Lucide React
- **Interactions**: 
  * Smooth scroll
  * Fade-in animations on scroll
  * Hover effects
  * Interactive elements (tooltips, expandable sections)
- **Responsive**: Mobile-first design
- **Performance**: Fast loading, optimized images"""
    
    def _get_deliverable_section(self, company: str) -> str:
        """Get deliverable section"""
        return f"""## ✅ Deliverable

A complete, production-ready React component that can be deployed immediately. Include all necessary imports, proper TypeScript types, and inline comments for easy customization.

**Make it stunning, interactive, and conversion-focused. This microsite should make {company} excited to learn more!**"""
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.conversation_memory
    
    def get_prompt_preview(self) -> str:
        """Get current state of prompt as preview"""
        filled_sections = [s for s in self.prompt_sections.values() if s.content]
        
        preview = "**Current Prompt Structure:**\n\n"
        for section in sorted(filled_sections, key=lambda x: x.priority):
            preview += f"✓ {section.title}\n"
        
        return preview
    
    def reset(self):
        """Reset conversation state"""
        self.conversation_memory = []
        self.extracted_entities = {
            "company_info": {},
            "people": [],
            "features": [],
            "pain_points": [],
            "metrics": [],
            "design_preferences": [],
        }
        self._initialize_sections()
