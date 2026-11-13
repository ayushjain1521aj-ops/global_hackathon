"""
Module 2: Context Optimizer
Implements Smart Context Management to drastically reduce input token consumption.
Strips boilerplate, eliminates repetitive conversational filler, prunes history,
and extracts localized code slices.
"""

import re
from typing import List, Dict, Any, Optional


class ContextOptimizer:
    """
    Cleans and optimizes prompt payloads before routing to the Bifrost LLM Gateway.
    """

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Accurate heuristic token estimation (~3.8 characters per token for code & technical English)."""
        if not text:
            return 0
        return max(1, int(len(text) / 3.8))

    @classmethod
    def prune_conversation_history(
        cls,
        messages: List[Dict[str, str]],
        max_turns: int = 2,
        preserve_system: bool = True
    ) -> List[Dict[str, str]]:
        """
        Keeps only the system instruction and the most recent N turns.
        Avoids accumulating giant message arrays across repair loops.
        """
        if len(messages) <= (max_turns * 2 + (1 if preserve_system else 0)):
            return messages

        system_msg = None
        if preserve_system and messages and messages[0].get("role") == "system":
            system_msg = messages[0]
            working_msgs = messages[1:]
        else:
            working_msgs = messages

        # Keep last (max_turns * 2) user/assistant messages
        tail_count = max_turns * 2
        trimmed = working_msgs[-tail_count:]

        if system_msg:
            return [system_msg] + trimmed
        return trimmed

    @classmethod
    def strip_prompt_redundancy(cls, text: str) -> str:
        """
        Eliminates conversational filler and repetitive pleasantries.
        """
        # List of bloat phrases commonly injected by standard agents
        bloat_patterns = [
            r"please make sure to write clean, maintainable, production ready code",
            r"as an expert software engineer and senior python developer",
            r"make sure you think step-by-step before answering",
            r"here is the complete program you requested:",
            r"i would be happy to help you with this task",
            r"sure, here is the solution:",
            r"let me know if you need any further modifications",
        ]

        cleaned = text
        for pat in bloat_patterns:
            cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)

        # Collapse excess whitespace
        cleaned = re.sub(r"\n\s*\n\s*\n+", "\n\n", cleaned)
        return cleaned.strip()

    @classmethod
    def extract_localized_context(
        cls,
        full_code: str,
        failing_line: Optional[int] = None,
        context_radius: int = 8
    ) -> str:
        """
        Instead of sending 500 lines of code to fix 1 line, extracts only the
        target function or a window of lines around the failing line.
        """
        if failing_line is None or failing_line <= 0:
            return full_code

        lines = full_code.splitlines()
        total_lines = len(lines)
        if total_lines <= 20:
            return full_code

        start = max(0, failing_line - context_radius - 1)
        end = min(total_lines, failing_line + context_radius)

        snippet_lines = []
        snippet_lines.append(f"# Snippet (Lines {start + 1} to {end} of {total_lines}):")
        for idx in range(start, end):
            prefix = ">>> " if (idx + 1 == failing_line) else "    "
            snippet_lines.append(f"{prefix}{idx + 1}: {lines[idx]}")

        return "\n".join(snippet_lines)

    @classmethod
    def compress_code(cls, code: str, strip_comments: bool = False) -> str:
        """
        Minifies code representation for prompts:
        Removes blank lines and optionally non-docstring inline comments.
        """
        lines = code.splitlines()
        result = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if strip_comments and stripped.startswith("#"):
                continue
            result.append(line)
        return "\n".join(result)
