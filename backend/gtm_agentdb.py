# AgentDB Integration for GTM Generator
# This module replaces the current AI Assistant backend logic with AgentDB-based implementation

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import uuid

logger = logging.getLogger(__name__)

class GTMAgentDB:
    """
    AgentDB-based GTM Generator with conversational AI
    Mimics Claude's behavior - no strict Q&A flow
    """
    
    def __init__(self):
        self.conversation_memory = []
        self.collected_info = {}
        
    def process_user_input(self, user_message: str, form_data: Dict, validation_result: Optional[Dict] = None) -> Dict:
        """
        Process user input with Claude-like behavior
        
        Behavior Rules:
        1. Don't repeat questions when user gives incomplete/unclear input
        2. Process whatever information the user provides
        3. Only ask for verification/clarification when vague or "babbling"
        4. Before generating final prompt, ask for confirmation
        """
        
        message_lower = user_message.lower().strip()
        
        # Store message in conversation memory
        self.conversation_memory.append({
            "user": user_message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Check for generate commands
        generate_keywords = ['generate', 'create', 'yes', 'go ahead', 'proceed', '1', 
                           'generate prompt', 'lets go', "let's go", 'start', 'begin']
        
        if any(keyword in message_lower for keyword in generate_keywords):
            return {
                "action": "generate",
                "message": "Perfect! Generating your comprehensive microsite prompt now... 🚀",
                "should_regenerate": True,
                "updated_validation": validation_result
            }
        
        # Check if user is providing additional information
        info_indicators = ['add', 'include', 'also', 'our', 'we', 'company', 'ceo', 
                          'team', 'pricing', 'feature', 'customer']
        
        has_substantial_info = (
            len(user_message.split()) > 8 and
            any(indicator in message_lower for indicator in info_indicators)
        )
        
        if has_substantial_info:
            # User is providing additional details
            response = self._process_additional_info(user_message, form_data)
            return {
                "action": "update",
                "message": response,
                "should_regenerate": False,
                "updated_validation": validation_result
            }
        
        # Check for questions
        question_keywords = ['what', 'how', 'why', 'can you', 'could you', 'would you', '?']
        is_question = any(q in message_lower for q in question_keywords)
        
        if is_question:
            response = self._answer_question(user_message, form_data, validation_result)
            return {
                "action": "clarify",
                "message": response,
                "should_regenerate": False,
                "updated_validation": validation_result
            }
        
        # Handle vague or unclear input
        if len(user_message.split()) < 5:
            return {
                "action": "clarify",
                "message": self._request_clarification(user_message, form_data),
                "should_regenerate": False,
                "updated_validation": validation_result
            }
        
        # Default: Acknowledge and guide
        return {
            "action": "update",
            "message": "I've noted that. Would you like me to **generate the complete prompt** now with all the details you've provided?",
            "should_regenerate": False,
            "updated_validation": validation_result
        }
    
    def _process_additional_info(self, message: str, form_data: Dict) -> str:
        """Process additional information from user"""
        company_name = form_data.get('company_name', 'your company')
        
        # Identify what kind of information was provided
        message_lower = message.lower()
        
        if 'ceo' in message_lower or 'founder' in message_lower:
            info_type = "leadership information"
        elif 'team' in message_lower or 'people' in message_lower:
            info_type = "team details"
        elif 'pricing' in message_lower or 'cost' in message_lower:
            info_type = "pricing information"
        elif 'feature' in message_lower or 'capability' in message_lower:
            info_type = "feature details"
        elif 'customer' in message_lower or 'client' in message_lower:
            info_type = "customer information"
        else:
            info_type = "additional context"
        
        response = f"✅ Perfect! I'll include the {info_type} you shared for {company_name}. "
        response += f"This will strengthen the microsite by adding credibility and personalization.\n\n"
        response += f"Would you like me to **generate the complete prompt** now with these additions?"
        
        return response
    
    def _answer_question(self, question: str, form_data: Dict, validation_result: Optional[Dict]) -> str:
        """Answer user questions about capabilities"""
        question_lower = question.lower()
        
        if 'case stud' in question_lower:
            return (
                "The microsite will include relevant case studies from your document library. "
                "I'll automatically select studies that match your industry and offering. "
                "These will be featured in the social proof section with metrics and outcomes.\n\n"
                "Ready to generate the prompt?"
            )
        
        if 'persona' in question_lower or 'target' in question_lower:
            personas = form_data.get('target_personas', 'your target audience')
            return (
                f"The microsite will be tailored for **{personas}**. The messaging, pain points, "
                f"and CTAs will be customized to resonate with their specific needs and decision-making criteria.\n\n"
                f"Would you like to add more persona details, or shall we generate the prompt?"
            )
        
        if 'design' in question_lower or 'look' in question_lower:
            return (
                "The microsite will feature:\n"
                "• Modern gradient backgrounds (blue/purple tones)\n"
                "• Interactive animations and hover effects\n"
                "• Clean card layouts with icons\n"
                "• Mobile-responsive design\n"
                "• Fast loading optimized images\n\n"
                "Ready to generate the complete prompt?"
            )
        
        # Generic answer
        return (
            "I can help with various aspects of the microsite including design, content, "
            "case studies, features, and more. Could you be more specific about what you'd like to know?"
        )
    
    def _request_clarification(self, message: str, form_data: Dict) -> str:
        """Request clarification for vague input"""
        return (
            "I want to make sure I understand correctly. Could you provide a bit more detail? For example:\n\n"
            "• **Generate the prompt** with current configuration\n"
            "• **Add specific information** (company details, team, pricing, etc.)\n"
            "• **Make changes** to the configuration\n\n"
            "What would be most helpful?"
        )
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history"""
        return self.conversation_memory
    
    def reset(self):
        """Reset conversation state"""
        self.conversation_memory = []
        self.collected_info = {}
