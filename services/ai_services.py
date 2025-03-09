from openai import OpenAI
from elevenlabs.client import ElevenLabs
import os
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import Optional

logger = logging.getLogger(__name__)

class AIServiceManager:
    """
    Singleton class to manage AI service clients with lazy initialization
    and proper environment validation
    """
    _instance = None
    _openai_client = None
    _el_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIServiceManager, cls).__new__(cls)
            cls._validate_environment()
        return cls._instance

    @classmethod
    def _validate_environment(cls):
        """Validate required environment variables"""
        required_vars = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY"]
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

    @property
    def openai(self):
        """Lazy-loaded OpenAI client"""
        if not self._openai_client:
            self._openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        return self._openai_client

    @property
    def elevenlabs(self):
        """Lazy-loaded ElevenLabs client"""
        if not self._el_client:
            self._el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        return self._el_client

# Configuration (now with type hints)
AI_CONFIG = {
    'openai': {
        'model': 'gpt-4-turbo',
        'max_tokens': 500,
        'temperature': 0.3,
        'system_prompt': '''You're an expert meeting assistant. Create a structured summary including:
- Key discussion topics
- Important decisions made
- Action items with owners
- Next steps
Format using markdown bullet points.'''
    },
    'elevenlabs': {
        'voice': 'Rachel',
        'model': 'eleven_multilingual_v2',
        'stability': 0.7,
        'similarity_boost': 0.5,
        'max_text_length': 1000
    }
}

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def generate_summary(text: str) -> str:
    """Generate structured meeting summary with enhanced error handling"""
    try:
        if not text.strip():
            return "No content provided for summary generation."
            
        service = AIServiceManager()
        
        response = service.openai.chat.completions.create(
            model=AI_CONFIG['openai']['model'],
            messages=[
                {"role": "system", "content": AI_CONFIG['openai']['system_prompt']},
                {"role": "user", "content": f"Meeting notes:\n{text[:3000]}"}
            ],
            temperature=AI_CONFIG['openai']['temperature'],
            max_tokens=AI_CONFIG['openai']['max_tokens']
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return f"⚠️ Summary generation failed: {str(e)}"

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
def text_to_speech(text: str) -> Optional[bytes]:
    """Convert text to speech with safety limits and better error handling"""
    try:
        if not text:
            return None
            
        service = AIServiceManager()
        
        return service.elevenlabs.generate(
            text=text[:AI_CONFIG['elevenlabs']['max_text_length']],
            voice=AI_CONFIG['elevenlabs']['voice'],
            model=AI_CONFIG['elevenlabs']['model'],
            stability=AI_CONFIG['elevenlabs']['stability'],
            similarity_boost=AI_CONFIG['elevenlabs']['similarity_boost']
        )
    except Exception as e:
        logger.error(f"ElevenLabs API Error: {str(e)}")
        return None