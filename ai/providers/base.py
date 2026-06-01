from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.3,
    ):
        self.base_url = base_url
        self.model = model
        self.temperature = temperature
    
    @abstractmethod
    async def generate(self, prompt: str) -> AsyncGenerator[str, None]:
        """Generate a response from a prompt with streaming."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    def format_system_prompt(self, role: str, context: str) -> str:
        """Format a system prompt."""
        return f"""You are a senior SOC analyst at Trinetra, an AI-powered cybersecurity platform.

Role: {role}

Context:
{context}

Instructions:
- Be concise and technical
- Use bullet points where appropriate
- Reference MITRE ATT&CK techniques when relevant
- Prioritize actionable recommendations
- If unsure, indicate uncertainty
"""
    
    def format_user_prompt(self, task: str, data: str) -> str:
        """Format a user prompt."""
        return f"""Task: {task}

Data:
{data}

Provide a detailed response following the task requirements."""