import os
import uuid
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class NoFeeBot:
    """AI Assistant for NoFeePlaces.com - helps users find apartments and get information"""
    
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            logger.warning("EMERGENT_LLM_KEY not found in environment variables")
            
        self.system_message = """You are NoFeeBot, the AI assistant for NoFeePlaces.com, NYC's premier no-fee apartment rental platform.

Your expertise:
- Helping users find no-fee apartments in NYC
- Providing information about neighborhoods, rent prices, and apartment features
- Assisting with apartment search criteria and preferences
- Explaining the benefits of no-fee rentals
- Guiding users through the platform features

Key information about NoFeePlaces.com:
- We specialize in NO BROKER FEE apartments across all NYC boroughs
- Our listings include studios, 1BR, 2BR, 3BR+ apartments
- We cover Manhattan, Brooklyn, Queens, Bronx, and Staten Island
- Price ranges typically from $1,900 to $28,750/month
- All listings are verified and real (no fake listings)
- Users can contact property owners directly
- We offer a "Post My Place" feature for tenants (sublets, roommates, lease transfers)

Tone: Professional, helpful, friendly, and knowledgeable about NYC rental market.

Always encourage users to browse our listings on the website and use our search filters to find their perfect apartment. If users ask about specific apartments, suggest they use our search features or contact us directly.

Keep responses concise but informative. If users need very specific help, suggest they contact our team at placesfirm@gmail.com."""

    async def get_chat_response(self, user_message: str, session_id: str) -> str:
        """Get AI response for user message"""
        try:
            if not self.api_key:
                return "I'm sorry, but the AI assistant is temporarily unavailable. Please contact us at placesfirm@gmail.com for assistance with your apartment search."
            
            # Initialize chat with session ID
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")  # Using cost-effective model
            
            # Create user message
            message = UserMessage(text=user_message)
            
            # Get response
            response = await chat.send_message(message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting chat response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment, or contact our team at placesfirm@gmail.com for immediate assistance with your apartment search."

    def generate_session_id(self) -> str:
        """Generate a unique session ID for the chat"""
        return str(uuid.uuid4())

# Global chatbot instance
nofeebbot = NoFeeBot()