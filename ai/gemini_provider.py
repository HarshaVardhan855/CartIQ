"""
Gemini LLM Provider Implementation for CartIQ.
Primary LLM Provider.
"""

import os
import json
import re
from typing import Optional, Dict, Any
from ai.llm import BaseLLMProvider, RetryableProviderError
from utils.logger import logger

class GeminiProvider(BaseLLMProvider):
    """
    Primary LLM provider using Google Gemini API.
    Catches 429 Rate Limit, Quota Exhaustion, and Outage errors to trigger RetryableProviderError.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GEMINI_API_KEY")
        super().__init__("gemini", key)
        self.client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not configured.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            self.client = genai
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.client = None

    def generate_text(self, prompt: str, system_prompt: Optional[str] = None, force_fail: bool = False) -> str:
        """
        Generates text using Gemini.
        If force_fail is True (for testing), raises RetryableProviderError immediately.
        """
        if force_fail:
            logger.warning("[GeminiProvider] Simulated rate limit failure (HTTP 429).")
            raise RetryableProviderError("gemini", "Simulated Rate Limit Exceeded (HTTP 429)", 429)

        if not self.api_key or not self.client:
            raise RetryableProviderError("gemini", "Gemini API key missing or uninitialized", 401)

        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            response = self.model.generate_content(full_prompt)
            if hasattr(response, "text") and response.text:
                return response.text
            raise Exception("Empty response from Gemini")
        except Exception as e:
            err_msg = str(e).lower()
            if "429" in err_msg or "quota" in err_msg or "rate" in err_msg or "resourceexhausted" in err_msg:
                logger.error(f"[Gemini] Rate limit hit: {e}")
                raise RetryableProviderError("gemini", f"Gemini Rate Limit (429): {e}", 429)
            elif "503" in err_msg or "timeout" in err_msg or "unavailable" in err_msg:
                logger.error(f"[Gemini] Outage or timeout: {e}")
                raise RetryableProviderError("gemini", f"Gemini Temporary Outage: {e}", 503)
            else:
                logger.error(f"[Gemini] Generic error: {e}")
                raise RetryableProviderError("gemini", f"Gemini Execution Error: {e}", 500)

    def generate_json(self, prompt: str, system_prompt: Optional[str] = None, force_fail: bool = False) -> Dict[str, Any]:
        """
        Generates structured JSON object.
        """
        json_prompt = f"{prompt}\n\nIMPORTANT: Return ONLY a valid, raw JSON object. Do not include markdown code block formatting like ```json."
        raw_text = self.generate_text(json_prompt, system_prompt, force_fail=force_fail)
        
        # Clean markdown wrappers if any
        cleaned = re.sub(r'^```(?:json)?\s*', '', raw_text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.MULTILINE).strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"[Gemini] JSON parsing error: {e}. Raw: {raw_text[:200]}")
            # Try regex extraction for JSON object
            match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError(f"Failed to parse JSON response from Gemini: {raw_text[:100]}")
