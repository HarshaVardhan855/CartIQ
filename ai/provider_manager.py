"""
Provider Manager for CartIQ.
Controls LLM provider selection, retries with backoff, and automatic fallback (Gemini -> Groq -> Rule Fallback).
"""

import time
import re
from typing import Optional, Dict, Any, Tuple
from ai.llm import RetryableProviderError
from ai.gemini_provider import GeminiProvider
from ai.groq_provider import GroqProvider
from utils.logger import logger

class ProviderManager:
    """
    Orchestrates LLM requests across Gemini (Primary) and Groq (Fallback).
    Ensures provider transparency while maintaining maximum uptime.
    """

    def __init__(self, gemini_key: Optional[str] = None, groq_key: Optional[str] = None):
        self.gemini = GeminiProvider(api_key=gemini_key)
        self.groq = GroqProvider(api_key=groq_key)
        self.max_retries = 2
        self.backoff_factor = 0.5  # seconds

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        simulate_gemini_failure: bool = False
    ) -> Tuple[str, str]:
        """
        Generates text through Gemini -> Groq fallback chain.
        Returns Tuple[response_text, provider_used].
        """
        # 1. Attempt Primary Provider: Gemini
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"[ProviderManager] Trying Gemini (Attempt {attempt + 1})...")
                res = self.gemini.generate_text(
                    prompt, system_prompt=system_prompt, force_fail=(simulate_gemini_failure or attempt < 0)
                )
                logger.info("[ProviderManager] Gemini request succeeded.")
                return res, "gemini"
            except RetryableProviderError as e:
                logger.warning(f"[ProviderManager] Gemini attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries and not simulate_gemini_failure:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    break
            except Exception as e:
                logger.error(f"[ProviderManager] Unexpected Gemini error: {e}")
                break

        # 2. Fallback to Secondary Provider: Groq
        logger.info("[ProviderManager] Falling back to Groq...")
        try:
            res = self.groq.generate_text(prompt, system_prompt=system_prompt)
            logger.info("[ProviderManager] Groq fallback request succeeded.")
            return res, "groq"
        except (RetryableProviderError, Exception) as e:
            logger.error(f"[ProviderManager] Groq fallback failed: {e}")

        # 3. Graceful Fallback if BOTH AI providers fail
        logger.warning("[ProviderManager] Both Gemini and Groq are unavailable. Returning deterministic fallback.")
        
        if system_prompt and "AI Shopping Advisor" in system_prompt:
            fallback_msg = (
                "I am currently operating in offline mode. While I cannot generate a specific AI response right now, "
                "here is a general shopping checklist:\n\n"
                "1. **Compare Features:** Check key specifications (e.g., RAM, storage, battery life) against your needs.\n"
                "2. **Check Reviews:** Always read verified buyer reviews before making a purchase.\n"
                "3. **Verify Sellers:** Buy from official or highly-rated sellers on the platform.\n"
                "4. **Live Prices:** Please search directly on Amazon, Flipkart, or Meesho to check current prices and availability."
            )
        else:
            fallback_msg = "AI assistance is temporarily unavailable. Product search and price comparison are still available."
        
        return fallback_msg, "deterministic_fallback"

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        simulate_gemini_failure: bool = False
    ) -> Tuple[Dict[str, Any], str]:
        """
        Generates structured JSON object through Gemini -> Groq fallback chain.
        Returns Tuple[parsed_json, provider_used].
        """
        # 1. Primary: Gemini
        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"[ProviderManager] Trying Gemini JSON (Attempt {attempt + 1})...")
                res = self.gemini.generate_json(
                    prompt, system_prompt=system_prompt, force_fail=simulate_gemini_failure
                )
                logger.info("[ProviderManager] Gemini JSON request succeeded.")
                return res, "gemini"
            except RetryableProviderError as e:
                logger.warning(f"[ProviderManager] Gemini JSON attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries and not simulate_gemini_failure:
                    sleep_time = self.backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    break
            except Exception as e:
                logger.error(f"[ProviderManager] Unexpected Gemini JSON error: {e}")
                break

        # 2. Fallback: Groq
        logger.info("[ProviderManager] Falling back to Groq JSON...")
        try:
            res = self.groq.generate_json(prompt, system_prompt=system_prompt)
            logger.info("[ProviderManager] Groq JSON fallback succeeded.")
            return res, "groq"
        except (RetryableProviderError, Exception) as e:
            logger.error(f"[ProviderManager] Groq JSON fallback failed: {e}")

        # 3. Deterministic rule-based fallback for query parsing
        logger.warning("[ProviderManager] Using rule-based query parser fallback.")
        rule_json = self._rule_based_query_parser(prompt)
        return rule_json, "deterministic_fallback"

    def _rule_based_query_parser(self, query: str) -> Dict[str, Any]:
        """
        Deterministic regex fallback parser when no LLM is reachable.
        """
        q = query.lower()
        budget = None
        
        # Regex for rupees e.g. "under 1000", "under ₹1,000", "below 500", "within 500"
        budget_match = re.search(r'(?:under|below|less than|within|budget|rs\.?|₹)\s*([\d,]+)', q)
        if budget_match:
            try:
                budget = float(budget_match.group(1).replace(",", ""))
            except ValueError:
                budget = None

        category = "general"
        for cat in ["wireless earbuds", "earbuds", "headphones", "laptop", "smartwatch", "tv", "mobile", "phone"]:
            if cat in q:
                category = cat
                break

        return {
            "category": category,
            "budget": budget,
            "currency": "INR",
            "requirements": [w for w in ["battery", "noise cancellation", "anc", "fast charge"] if w in q]
        }
