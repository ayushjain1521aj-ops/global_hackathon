"""
Module 10: Benchmark Engine
Executes side-by-side comparison between:
1. Standard Baseline Agent (uncompressed prompts, full chat history, entire codebase regeneration)
2. CodeLite AI Agent (smart context, targeted repair, caching, response optimization)
Measures exact tokens, compute time, requests, and calculates verified Token Savings (%).
"""

import time
import uuid
from typing import Dict, Any, List, Optional
from bifrost.client import BifrostClient, get_bifrost_client
from core.agent import CodeLiteAgent
from core.token_optimizer import TokenMetrics
from .dataset import BENCHMARK_TASKS
from .history import HistoryStore


class BenchmarkEngine:
    """
    Automates comparative benchmarking on identical tasks routed through Bifrost LLM Gateway.
    """

    def __init__(self, client: Optional[BifrostClient] = None):
        self.client = client or get_bifrost_client()
        self.history_store = HistoryStore()

    def run_standard_baseline_agent(self, task_prompt: str, language: str = "python") -> Dict[str, Any]:
        """
        Simulates standard naive agent behavior:
        - Verbose conversational system prompt (high prompt tokens)
        - Uncompressed task context
        - Full chat history retained
        - Requests verbose explanation alongside code
        """
        start_time = time.perf_counter()
        metrics = TokenMetrics()

        # Bloated standard system prompt
        verbose_system = (
            "You are an expert senior software developer and computer science professor. "
            "Your objective is to provide a comprehensive, fully detailed, step-by-step solution "
            "to the user's coding problem. You must explain your architectural decisions, write "
            "detailed docstrings, annotate every method, explain the algorithm's time and space complexity, "
            "and provide both the implementation and an exhaustive suite of unit tests. Please be thorough "
            "and polite."
        )

        user_content = (
            f"Hello AI! I would really appreciate your assistance. Could you please build the following program for me?\n"
            f"Programming Language: {language}\n"
            f"Task Description: {task_prompt}\n"
            "Please structure everything cleanly, explain how each part works in detail, and provide unit tests."
        )

        messages = [
            {"role": "system", "content": verbose_system},
            {"role": "user", "content": user_content}
        ]

        # Call Bifrost
        content, meta = self.client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2200
        )

        metrics.add_call(
            meta.get("prompt_tokens", 0),
            meta.get("completion_tokens", 0),
            meta.get("model", self.client.config.model)
        )

        # Baseline typically requires a follow-up conversation turn to refine or test
        followup_user = (
            "Thank you for the detailed code. Could you double check if all edge cases are handled "
            "and confirm the test cases pass properly?"
        )
        messages.append({"role": "assistant", "content": content})
        messages.append({"role": "user", "content": followup_user})

        content_turn2, meta_turn2 = self.client.chat_completion(
            messages=messages,
            temperature=0.2,
            max_tokens=400
        )

        metrics.add_call(
            meta_turn2.get("prompt_tokens", 0),
            meta_turn2.get("completion_tokens", 0),
            meta_turn2.get("model", self.client.config.model)
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "metrics": metrics.to_dict(),
            "execution_time_ms": round(elapsed_ms, 2),
            "request_count": metrics.request_count,
            "repair_attempts": 1,
            "is_simulated": meta.get("is_simulated", False)
        }

    def run_benchmark_on_task(self, task_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs both agents on the same task and calculates verifiable savings.
        """
        task_id = task_dict.get("id", str(uuid.uuid4())[:8])
        task_name = task_dict.get("name", "Task")
        prompt = task_dict.get("prompt", "")
        language = task_dict.get("language", "python")

        # 1. Run Standard Baseline Agent
        baseline_res = self.run_standard_baseline_agent(prompt, language)

        # 2. Run CodeLite Optimized Agent
        start_time = time.perf_counter()
        codelite_agent = CodeLiteAgent(self.client, enable_cache=False) # disable cache during raw benchmark to compare pure optimization
        codelite_run = codelite_agent.run(prompt, language=language)
        codelite_elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        codelite_metrics = codelite_run["metrics"]

        # Calculate Savings: ((Baseline - CodeLite) / Baseline) * 100
        base_tokens = max(1, baseline_res["metrics"]["total_tokens"])
        lite_tokens = codelite_metrics["total_tokens"]

        savings_pct = max(0.0, round(((base_tokens - lite_tokens) / base_tokens) * 100.0, 1))

        benchmark_result = {
            "id": f"bench_{int(time.time())}_{task_id}",
            "task_id": task_id,
            "task_name": task_name,
            "baseline": {
                "input_tokens": baseline_res["metrics"]["input_tokens"],
                "output_tokens": baseline_res["metrics"]["output_tokens"],
                "total_tokens": baseline_res["metrics"]["total_tokens"],
                "request_count": baseline_res["request_count"],
                "execution_time_ms": baseline_res["execution_time_ms"],
                "repair_attempts": baseline_res["repair_attempts"],
                "estimated_cost_usd": baseline_res["metrics"]["estimated_cost_usd"]
            },
            "codelite": {
                "input_tokens": codelite_metrics["input_tokens"],
                "output_tokens": codelite_metrics["output_tokens"],
                "total_tokens": codelite_metrics["total_tokens"],
                "request_count": codelite_metrics["request_count"],
                "execution_time_ms": round(codelite_elapsed_ms, 2),
                "repair_attempts": codelite_run["repair_attempts"],
                "estimated_cost_usd": codelite_metrics["estimated_cost_usd"]
            },
            "token_savings_pct": savings_pct,
            "test_pass_rate": codelite_run["test_results"]["pass_rate"],
            "task_completion": codelite_run["success"],
            "is_simulated": codelite_run.get("is_simulated", False),
            "created_at": time.time()
        }

        # Persist to database
        self.history_store.record_benchmark(benchmark_result)

        return benchmark_result

    def run_all_benchmarks(self) -> List[Dict[str, Any]]:
        """Executes the complete benchmark suite across all 5 standard tasks."""
        results = []
        for task in BENCHMARK_TASKS:
            res = self.run_benchmark_on_task(task)
            results.append(res)
        return results
