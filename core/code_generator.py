"""
Module 5: Code Generator
Generates clean, production-grade code and unit tests via Bifrost LLM Gateway,
utilizing prompt optimization and result caching.
"""

import re
import ast
from typing import Dict, Any, Tuple, Optional
from bifrost.client import BifrostClient, get_bifrost_client
from .task_analyzer import TaskSpec
from .token_optimizer import TokenOptimizationEngine, TokenMetrics
from .context_optimizer import ContextOptimizer


class CodeGenerator:
    """
    Produces code and test suites using Bifrost LLM Gateway.
    """

    def __init__(
        self,
        client: Optional[BifrostClient] = None,
        token_engine: Optional[TokenOptimizationEngine] = None
    ):
        self.client = client or get_bifrost_client()
        self.token_engine = token_engine or TokenOptimizationEngine()

    def generate(
        self,
        task_spec: TaskSpec,
        metrics: Optional[TokenMetrics] = None,
        enable_cache: bool = True,
        complexity: Optional[str] = None,
        optimize_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Generates code and unit tests for the given task specification.
        """
        metrics = metrics or self.token_engine.metrics

        # Step 1: Check Token Cache (Section 4.F Caching)
        cache_key_prompt = f"{task_spec.language}:{task_spec.task_name}:{task_spec.goal}:{complexity}"
        if enable_cache:
            cached = self.token_engine.cache.get(cache_key_prompt, self.client.config.model)
            if cached:
                metrics.record_cache_hit(
                    cached.get("prompt_tokens", 0),
                    cached.get("completion_tokens", 0)
                )
                return {
                    "code": cached["code"],
                    "tests": cached["tests"],
                    "from_cache": True,
                    "metadata": {
                        "request_id": f"cached-{cached['timestamp']}",
                        "model": self.client.config.model,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0,
                        "is_simulated": cached.get("is_simulated", False),
                        "latency_ms": 1.2
                    }
                }

        # Step 2: Build concise system directive and user prompt (Section 4.D Response Optimization)
        system_directive = self.token_engine.create_generation_directive(task_spec.to_dict())

        chosen_complexity = complexity or getattr(task_spec, "complexity", "essential") or "essential"
        if chosen_complexity == "standard":
            style_instruction = "Style: Standard Typed (adds PEP-484 type annotations and concise docstrings)."
        elif chosen_complexity in ("dataclass", "comprehensive"):
            style_instruction = "Style: Dataclass (declarative @dataclass decorators with concise methods)."
        else:
            style_instruction = "Style: Essential (idiomatic, clean __init__, strictly standard constructs without unnecessary wrappers)."

        # Construct optimized concise user prompt focused strictly on user requirements
        prompt_parts = [
            f"TASK: {task_spec.task_name}",
            f"REQUIREMENT: {task_spec.goal}"
        ]
        if task_spec.edge_cases:
            prompt_parts.append(f"EDGE CASES: {', '.join(task_spec.edge_cases)}")
        prompt_parts.append(f"INSTRUCTION: Generate simple, clean, readable Python code solving the exact task. {style_instruction} Do NOT add unnecessary validation or extra features. Include a complete runnable unittest suite.")
        user_prompt = "\n".join(prompt_parts)
        if optimize_prompt:
            user_prompt = ContextOptimizer.strip_prompt_redundancy(user_prompt)

        messages = [
            {"role": "system", "content": system_directive},
            {"role": "user", "content": user_prompt}
        ]

        # Step 3: Route through Bifrost LLM Gateway
        content, meta = self.client.chat_completion(
            messages=messages,
            temperature=0.2,
            max_tokens=1800
        )

        # Track actual token counts from Bifrost
        metrics.add_call(
            input_t=meta.get("prompt_tokens", 0),
            output_t=meta.get("completion_tokens", 0),
            model_name=meta.get("model", self.client.config.model)
        )

        # Step 4: Extract solution code and unit test blocks
        code, tests = self._extract_code_and_tests(content, task_spec.language)

        # Quick AST check on Python code
        syntax_ok = True
        syntax_err = ""
        if task_spec.language.lower() == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                syntax_ok = False
                syntax_err = f"SyntaxError: {e.msg} at line {e.lineno}"

        result = {
            "code": code,
            "tests": tests,
            "syntax_valid": syntax_ok,
            "syntax_error": syntax_err,
            "from_cache": False,
            "metadata": meta
        }

        # Store in cache if generation succeeded
        if enable_cache and syntax_ok:
            self.token_engine.cache.put(
                prompt=cache_key_prompt,
                model=self.client.config.model,
                data={
                    "code": code,
                    "tests": tests,
                    "timestamp": meta.get("latency_ms", 0),
                    "prompt_tokens": meta.get("prompt_tokens", 0),
                    "completion_tokens": meta.get("completion_tokens", 0),
                    "is_simulated": meta.get("is_simulated", False)
                }
            )

        return result

    def _extract_code_and_tests(self, response_text: Any, language: str) -> Tuple[str, str]:
        """
        Parses multi-block markdown code blocks into main code and test code.
        """
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

        if not blocks:
            # Fallback if model didn't use fences
            return response_text.strip(), ""

        if len(blocks) == 1:
            raw = blocks[0]
            # Check if tests and code are combined in one block
            if "class Test" in raw or "unittest.main" in raw or "def test_" in raw:
                # Split at unittest or test definitions if possible
                parts = re.split(r"(?=import unittest|class Test|\bdef test_)", raw, maxsplit=1)
                if len(parts) == 2:
                    return parts[0].strip(), parts[1].strip()
            return raw.strip(), ""

        # Multiple blocks: assign first as main code, second (or one mentioning test) as tests
        main_code = blocks[0].strip()
        tests_code = ""
        for blk in blocks[1:]:
            if "test" in blk.lower() or "unittest" in blk.lower() or "assert" in blk:
                tests_code = blk.strip()
                break

        if not tests_code and len(blocks) > 1:
            tests_code = blocks[1].strip()

        return main_code, tests_code
