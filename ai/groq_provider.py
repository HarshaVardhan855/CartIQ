"""
Groq LLM Provider Implementation for CartIQ.
Automatic Fallback LLM Provider.
"""

import os
import json
import re
from typing import Optional, Dict, Any
from ai.llm import BaseLLMProvider, RetryableProviderError
from utils.logger import logger

class GroqProvider(BaseLLMProvider):
    """
    Fallback LLM provider using Groq API.
    Activated automatically when Gemini experiences rate limit 429 or outages.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        super().__init__("groq", key)
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GROQ_API_KEY is not configured.")
            return

        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
            self.model = "qwen/qwen3.8-27b"
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            self.client = None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates text using Groq LLM.
        """
        if not self.api_key or not self.client:
            raise RetryableProviderError("groq", "Groq API key missing or uninitialized", 401)

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=1024
            )

            if completion.choices and completion.choices[0].message:
                return completion.choices[0].message.content or ""
            raise Exception("Empty response from Groq")
        except Exception as e:
            logger.error(f"[Groq] Error during generation: {e}")
            raise RetryableProviderError("groq", f"Groq Execution Error: {e}", 500)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates structured JSON object.
        """
        json_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY a valid, raw JSON object without markdown wrappers."
        raw_text = self.generate_text(json_prompt, system_prompt)
        
        cleaned = re.sub(r'^```(?:json)?\s*', '', raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse JSON response from Groq: {raw_text[:100]}")
