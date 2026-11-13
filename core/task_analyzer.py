"""
Module 1: Task Analyzer
Deconstructs natural language programming requests into structured specifications
while maintaining maximum token efficiency.
"""

import json
import re
from typing import Dict, Any, List, Optional
from bifrost.client import BifrostClient, get_bifrost_client


class TaskSpec:
    def __init__(
        self,
        task_name: str,
        goal: str,
        language: str = "python",
        complexity: str = "simple",
        subtasks: Optional[List[str]] = None,
        edge_cases: Optional[List[str]] = None,
        signatures: Optional[List[str]] = None,
        test_criteria: Optional[List[str]] = None,
        raw_prompt: str = ""
    ):
        self.task_name = task_name
        self.goal = goal
        self.language = language
        self.complexity = complexity
        self.subtasks = subtasks or [goal]
        self.edge_cases = edge_cases or []
        self.signatures = signatures or []
        self.test_criteria = test_criteria or []
        self.raw_prompt = raw_prompt

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_name": self.task_name,
            "goal": self.goal,
            "language": self.language,
            "complexity": self.complexity,
            "subtasks": self.subtasks,
            "edge_cases": self.edge_cases,
            "signatures": self.signatures,
            "test_criteria": self.test_criteria,
            "raw_prompt": self.raw_prompt
        }


class TaskAnalyzer:
    """
    Analyzes tasks using Bifrost LLM Gateway with minimal token overhead.
    """

    def __init__(self, client: Optional[BifrostClient] = None):
        self.client = client or get_bifrost_client()

    def analyze(self, user_request: str, language: str = "python") -> Tuple[TaskSpec, Dict[str, Any]]:
        """
        Extracts structured task spec from natural language with strict token-efficient prompting.
        """
        # Concise prompt: extract EXACT requirements without hallucinating speculative features
        system_prompt = (
            "You are CodeLite Task Analyzer. Extract the user's exact requirements without inventing extra validation or complexity.\n"
            "Output compact JSON only:\n"
            '{"name":"","goal":"","complexity":"simple|moderate|complex",'
            '"subtasks":[""],"required_symbols":[""],"edge_cases":[]}\n'
            "Rules: Only include edge cases explicitly mentioned by the user. Do NOT add unnecessary validation logic."
        )
        user_msg = f"Task: {user_request.strip()} | Lang: {language}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]

        content, meta = self.client.chat_completion(
            messages=messages,
            temperature=0.1,
            max_tokens=350
        )

        # Parse JSON from response
        try:
            # Extract JSON block if wrapped in fences
            clean_json = content
            if "```" in clean_json:
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_json, re.DOTALL)
                if match:
                    clean_json = match.group(1)
            parsed = json.loads(clean_json.strip())

            spec = TaskSpec(
                task_name=parsed.get("name") or user_request[:30],
                goal=parsed.get("goal") or user_request,
                language=language,
                complexity=parsed.get("complexity", "simple"),
                subtasks=parsed.get("subtasks") or [user_request],
                edge_cases=parsed.get("edge_cases") or [],
                signatures=parsed.get("required_symbols") or parsed.get("signatures") or [],
                raw_prompt=user_request
            )
        except Exception:
            # Deterministic fallback when JSON parsing fails
            words = user_request.strip().split()
            title = " ".join(words[:4]).title()
            complexity = "complex" if len(words) > 25 else ("moderate" if len(words) > 10 else "simple")
            spec = TaskSpec(
                task_name=title,
                goal=user_request,
                language=language,
                complexity=complexity,
                subtasks=[user_request],
                edge_cases=[],
                signatures=[],
                raw_prompt=user_request
            )

        return spec, meta
