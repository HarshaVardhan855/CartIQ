"""
Base LLM Provider Abstraction and Custom Exception definitions for CartIQ.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class RetryableProviderError(Exception):
    """
    Raised when an LLM provider encounters a retryable transient failure
    (e.g., 429 Rate Limit, Quota Exhaustion, Timeout, 503 Outage).
    """
    def __init__(self, provider_name: str, message: str, status_code: Optional[int] = None):
        self.provider_name = provider_name
        self.message = message
        self.status_code = status_code
        super().__init__(f"[{provider_name}] {message} (Status: {status_code})")

class BaseLLMProvider(ABC):
    """
    Abstract interface for LLM providers (Gemini, Groq, etc.).
    """

    def __init__(self, provider_name: str, api_key: Optional[str] = None):
        self.provider_name = provider_name
        self.api_key = api_key

    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates text completion.
        Raises RetryableProviderError on transient API limits or network failures.
        """
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates structured JSON object.
        Raises RetryableProviderError on transient API limits or network failures.
        """
        pass
