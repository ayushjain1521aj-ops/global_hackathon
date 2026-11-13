"""
Module 3: Token Optimization Engine
The core innovation of CodeLite AI. Orchestrates smart context management,
targeted error correction, response optimization, stop conditions, caching,
and exact token accounting.
"""

import hashlib
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field


# Reference pricing per 1M tokens (from official provider lists routed via Bifrost)
MODEL_PRICING = {
    "openai/gpt-4o-mini": {"input_per_million": 0.15, "output_per_million": 0.60},
    "openai/gpt-4o": {"input_per_million": 2.50, "output_per_million": 10.00},
    "anthropic/claude-3-5-haiku": {"input_per_million": 0.80, "output_per_million": 4.00},
    "anthropic/claude-3-5-sonnet": {"input_per_million": 3.00, "output_per_million": 15.00},
    "gemini/gemini-1.5-flash": {"input_per_million": 0.075, "output_per_million": 0.30},
}


@dataclass
class TokenMetrics:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    request_count: int = 0
    cache_hits: int = 0
    repair_attempts: int = 0
    estimated_cost_usd: float = 0.0

    def add_call(self, input_t: int, output_t: int, model_name: str = "openai/gpt-4o-mini"):
        self.input_tokens += input_t
        self.output_tokens += output_t
        self.total_tokens += (input_t + output_t)
        self.request_count += 1
        self.estimated_cost_usd += self._calculate_cost(input_t, output_t, model_name)

    def record_cache_hit(self, saved_input_t: int, saved_output_t: int):
        self.cache_hits += 1

    def _calculate_cost(self, in_tok: int, out_tok: int, model: str) -> float:
        # Match configured model prefix
        rates = MODEL_PRICING.get("openai/gpt-4o-mini")
        for key, val in MODEL_PRICING.items():
            if key in model:
                rates = val
                break
        cost_in = (in_tok / 1_000_000.0) * rates["input_per_million"]
        cost_out = (out_tok / 1_000_000.0) * rates["output_per_million"]
        return round(cost_in + cost_out, 6)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "request_count": self.request_count,
            "cache_hits": self.cache_hits,
            "repair_attempts": self.repair_attempts,
            "estimated_cost_usd": round(self.estimated_cost_usd, 6),
        }


class TokenCache:
    """
    Two-tier deterministic cache for prompts and generated subtask outputs.
    Saves 100% of LLM tokens when identical subtasks/contexts are requested.
    """

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds

    def _generate_key(self, prompt: str, model: str, context_hash: str = "") -> str:
        raw = f"{model}::{context_hash}::{prompt.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, prompt: str, model: str, context_hash: str = "") -> Optional[Dict[str, Any]]:
        key = self._generate_key(prompt, model, context_hash)
        entry = self._cache.get(key)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self.ttl:
            del self._cache[key]
            return None
        return entry["data"]

    def put(self, prompt: str, model: str, data: Dict[str, Any], context_hash: str = ""):
        key = self._generate_key(prompt, model, context_hash)
        self._cache[key] = {
            "timestamp": time.time(),
            "data": data
        }

    def clear(self):
        self._cache.clear()


class TokenOptimizationEngine:
    """
    Coordinates all token-saving optimizations for CodeLite AI.
    """

    def __init__(self):
        self.cache = TokenCache()
        self.metrics = TokenMetrics()

    def create_generation_directive(self, task_spec_dict: Dict[str, Any]) -> str:
        """
        Creates a clean, code-focused system directive.
        Strictly prioritizes user requirements without adding unnecessary bloat.
        """
        return (
            "You are CodeLite Code Generator. Generate simple, readable, direct Python code.\n"
            "CRITICAL RULES:\n"
            "1. Prioritize the EXACT requirements of the user's task. Do NOT add unnecessary classes, methods, speculative validation, or extra features.\n"
            "2. Keep the code minimal, correct, and readable.\n"
            "3. Output exactly TWO valid python code blocks:\n"
            "   Block 1: Pure solution code.\n"
            "   Block 2: Runnable unittest suite testing the exact requirements (must include if __name__ == '__main__': unittest.main()).\n"
            "4. Zero conversational chatter or explanations."
        )

    def create_targeted_repair_directive(
        self,
        full_code: str,
        error_type: str,
        error_line: int,
        error_message: str,
        task_goal: str = ""
    ) -> Tuple[str, str]:
        """
        Creates a targeted error correction prompt (Section 4.B).
        Sends the specific error traceback and code to fix the root cause while preserving all working code.
        """
        system_directive = (
            "You are CodeLite Surgical Debugger. Fix the targeted error.\n"
            "CRITICAL RULES:\n"
            "1. Fix the exact root cause of the error.\n"
            "2. Preserve all existing working classes, functions, and logic. Do NOT delete or truncate code.\n"
            "3. Do NOT add unnecessary validation or speculative features.\n"
            "4. Output the complete corrected code block. Zero conversational preamble."
        )

        user_content = (
            f"GOAL: {task_goal}\n"
            f"ERROR: {error_type} at line {error_line}: {error_message}\n\n"
            f"CURRENT CODE:\n{full_code}\n\n"
            "Provide the complete corrected version of the code that fixes the error:"
        )

        return system_directive, user_content

    def should_stop(self, tests_passed: bool, current_attempt: int, max_attempts: int = 5) -> Tuple[bool, str]:
        """
        Section 4.E Stop Conditions:
        Stops immediately when tests pass or when max repair limit is reached.
        """
        if tests_passed:
            return True, "All tests passed successfully. Terminating AI loop to conserve tokens."
        if current_attempt >= max_attempts:
            return True, f"Reached maximum allowed repair attempts ({max_attempts}). Stopping."
        return False, "Continue repair loop."
