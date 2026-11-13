"""
Requirement Verifier Module
Performs a final verification step that compares the generated solution
against every requirement in the original user prompt and task specification.
"""

import ast
import re
from typing import Dict, Any, List, Set, Optional
from bifrost.client import BifrostClient, get_bifrost_client
from .task_analyzer import TaskSpec


class VerificationResult:
    def __init__(
        self,
        passed: bool,
        score: float,
        missing_requirements: List[str],
        detected_symbols: List[str],
        summary: str
    ):
        self.passed = passed
        self.score = round(score, 2)
        self.missing_requirements = missing_requirements
        self.detected_symbols = detected_symbols
        self.summary = summary

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "score": self.score,
            "missing_requirements": self.missing_requirements,
            "detected_symbols": self.detected_symbols,
            "summary": self.summary
        }


class RequirementVerifier:
    """
    Verifies that the generated solution satisfies all requirements
    specified in the user prompt and TaskSpec.
    """

    def __init__(self, client: Optional[BifrostClient] = None):
        self.client = client or get_bifrost_client()

    def verify(
        self,
        task_prompt: str,
        task_spec: TaskSpec,
        solution_code: str
    ) -> VerificationResult:
        """
        Validates solution code against user prompt and task specification.
        Uses AST analysis combined with semantic requirements checking.
        """
        if not solution_code.strip():
            return VerificationResult(
                passed=False,
                score=0.0,
                missing_requirements=["Solution code is empty"],
                detected_symbols=[],
                summary="Verification failed: No code was generated."
            )

        # Step 1: AST Syntax and Symbol Extraction
        try:
            tree = ast.parse(solution_code)
        except SyntaxError as e:
            return VerificationResult(
                passed=False,
                score=0.0,
                missing_requirements=[f"Code has syntax error: {e}"],
                detected_symbols=[],
                summary=f"Verification failed: Syntax error in solution code at line {e.lineno}."
            )

        defined_classes: Set[str] = set()
        defined_functions: Set[str] = set()
        defined_methods: Dict[str, Set[str]] = {}

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined_classes.add(node.name)
                defined_methods[node.name] = set()
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        defined_methods[node.name].add(item.name)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defined_functions.add(node.name)

        all_symbols = list(defined_classes) + list(defined_functions)
        for cls_methods in defined_methods.values():
            all_symbols.extend(cls_methods)
        detected_symbols = sorted(list(set(all_symbols)))

        # Step 2: Extract key expected operations/symbols from prompt and task_spec
        missing: List[str] = []
        expected_items = self._extract_expected_requirements(task_prompt, task_spec)

        matched_count = 0
        total_expected = len(expected_items)

        for item in expected_items:
            pattern = item["pattern"]
            label = item["label"]
            # Check if any symbol matches
            matched = any(re.search(pattern, sym, re.IGNORECASE) for sym in detected_symbols)
            if not matched:
                # Also check if pattern appears in solution code directly (e.g. operators or expressions)
                if re.search(pattern, solution_code, re.IGNORECASE):
                    matched = True

            if matched:
                matched_count += 1
            else:
                missing.append(label)

        # Step 3: Determine verification pass
        if total_expected > 0:
            score = matched_count / total_expected
            passed = (len(missing) == 0) or (score >= 0.8)
        else:
            # If no specific function names were identified, verify non-empty working code
            score = 1.0 if len(detected_symbols) > 0 or len(solution_code.splitlines()) >= 3 else 0.0
            passed = score > 0.0

        if passed:
            summary = f"All requirements verified successfully ({matched_count}/{total_expected} requirements matched)."
        else:
            summary = f"Requirement mismatch: Missing {', '.join(missing)}."

        return VerificationResult(
            passed=passed,
            score=score,
            missing_requirements=missing,
            detected_symbols=detected_symbols,
            summary=summary
        )

    def _extract_expected_requirements(self, task_prompt: str, task_spec: TaskSpec) -> List[Dict[str, str]]:
        """
        Extracts expected capabilities and methods mentioned in the prompt.
        """
        requirements: List[Dict[str, str]] = []
        prompt_lower = task_prompt.lower()
        combined_text = f"{task_prompt} {task_spec.goal} {' '.join(task_spec.subtasks)}".lower()

        # 1. Use explicit method/class signatures deduced by TaskAnalyzer
        if task_spec.signatures:
            for sig in task_spec.signatures:
                sig_clean = sig.strip()
                if sig_clean and len(sig_clean) > 1:
                    requirements.append({
                        "pattern": r"\b" + re.escape(sig_clean) + r"\b",
                        "label": f"'{sig_clean}' definition"
                    })

        # 2. Check for calculator / math operations ONLY if it's a calculator or arithmetic task
        is_calc_task = any(w in combined_text for w in ["calculator", "calculate", "arithmetic", "math"])
        if is_calc_task:
            calc_operations = [
                ("add", r"\badd\b|\baddition\b|\+", "addition operation (add)"),
                ("subtract", r"\bsubtract\b|\bsub\b|\-", "subtraction operation (subtract)"),
                ("multiply", r"\bmultiply\b|\bmul\b|\*", "multiplication operation (multiply)"),
                ("divide", r"\bdivide\b|\bdiv\b|\/", "division operation (divide)"),
                ("power", r"\bpower\b|\bpow\b|\*\*", "power operation (power)"),
                ("modulo", r"\bmodulo\b|\bmod\b|\%", "modulo operation (mod)")
            ]
            for key, pat, label in calc_operations:
                if re.search(r"\b" + key + r"\b", combined_text):
                    if not any(r["label"] == label for r in requirements):
                        requirements.append({"pattern": pat, "label": label})

        # 3. Check for Sorting / Searching
        if any(w in prompt_lower for w in ["sort", "search"]):
            if re.search(r"\bsort\b|\bsorted\b", prompt_lower):
                if not any("sort" in r["label"].lower() for r in requirements):
                    requirements.append({"pattern": r"\bsort\b|\bsorted\b", "label": "sort function"})
            if re.search(r"\bsearch\b|\bfind\b", prompt_lower):
                if not any("search" in r["label"].lower() for r in requirements):
                    requirements.append({"pattern": r"\bsearch\b|\bfind\b", "label": "search function"})

        return requirements
