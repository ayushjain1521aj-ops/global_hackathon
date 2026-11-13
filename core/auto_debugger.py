"""
Module 8: Automatic Debugger
Implements Targeted Error Correction (Section 4.B).
Sends targeted error context and full code to Bifrost LLM Gateway,
fixing the root cause while preserving all existing classes and functions.
Enforces the maximum 5 repair attempts limit.
"""

import ast
import re
from typing import Dict, Any, Tuple, Optional
from bifrost.client import BifrostClient, get_bifrost_client
from .error_detector import DetectedError
from .token_optimizer import TokenOptimizationEngine, TokenMetrics


class AutomaticDebugger:
    """
    Surgically fixes detected errors via Bifrost LLM Gateway.
    """

    def __init__(
        self,
        client: Optional[BifrostClient] = None,
        token_engine: Optional[TokenOptimizationEngine] = None,
        max_attempts: int = 5
    ):
        self.client = client or get_bifrost_client()
        self.token_engine = token_engine or TokenOptimizationEngine()
        self.max_attempts = max_attempts

    def debug_and_repair(
        self,
        current_code: str,
        error: Optional[DetectedError],
        attempt_number: int,
        metrics: Optional[TokenMetrics] = None,
        language: str = "python",
        task_goal: str = ""
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Generates a targeted repair for the failing code.
        Preserves all working code and fixes the exact root cause.
        """
        metrics = metrics or self.token_engine.metrics
        metrics.repair_attempts += 1

        if attempt_number > self.max_attempts:
            return current_code, {
                "success": False,
                "message": f"Maximum repair attempts limit ({self.max_attempts}) reached.",
                "tokens": 0
            }

        err_type = error.error_type if error else "RuntimeError"
        err_line = error.line_number or 0 if error else 0
        err_msg = error.message if error else "Execution/Test failure"

        # Formulate targeted repair prompt directives
        system_dir, user_dir = self.token_engine.create_targeted_repair_directive(
            full_code=current_code,
            error_type=err_type,
            error_line=err_line,
            error_message=err_msg,
            task_goal=task_goal
        )

        messages = [
            {"role": "system", "content": system_dir},
            {"role": "user", "content": user_dir}
        ]

        # Call Bifrost Gateway
        content, meta = self.client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=2000
        )

        # Record exact tokens consumed
        metrics.add_call(
            input_t=meta.get("prompt_tokens", 0),
            output_t=meta.get("completion_tokens", 0),
            model_name=meta.get("model", self.client.config.model)
        )

        # Extract repaired code and validate
        repaired_code = self._extract_code(content, fallback=current_code)

        repair_meta = {
            "attempt": attempt_number,
            "error_type": err_type,
            "failing_line": err_line,
            "metadata": meta,
            "repaired_code_length": len(repaired_code)
        }

        return repaired_code, repair_meta

    def _extract_code(self, response_text: Any, fallback: str) -> str:
        """Extracts code block from markdown response and validates Python syntax."""
        if isinstance(response_text, list):
            text_parts = []
            for part in response_text:
                if isinstance(part, dict):
                    text_parts.append(part.get("text", ""))
                elif hasattr(part, "text"):
                    text_parts.append(str(part.text))
                else:
                    text_parts.append(str(part))
            response_text = "".join(text_parts)
        else:
            response_text = str(response_text or "")

        blocks = re.findall(r"```(?:[a-zA-Z0-9_\-\+]+)?\s*\n(.*?)\n```", response_text, re.DOTALL)
        candidate = fallback
        if blocks:
            candidate = blocks[0].strip()
        else:
            cleaned = response_text.strip()
            if len(cleaned) > 20 and not cleaned.startswith("{"):
                candidate = cleaned

        # Validate syntax
        try:
            ast.parse(candidate)
            return candidate
        except SyntaxError:
            try:
                ast.parse(fallback)
                return fallback
            except Exception:
                return candidate
