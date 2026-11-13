"""
CodeLite AI - Comprehensive Test Suite
Validates all 11 required modules and Bifrost Gateway integrations.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bifrost.client import BifrostClient, get_bifrost_client
from bifrost.config import BifrostConfig
from core.task_analyzer import TaskAnalyzer, TaskSpec
from core.context_optimizer import ContextOptimizer
from core.token_optimizer import TokenOptimizationEngine, TokenMetrics, TokenCache
from core.code_generator import CodeGenerator
from core.error_detector import ErrorDetector, DetectedError
from core.auto_debugger import AutomaticDebugger
from core.test_runner import TestRunner
from core.agent import CodeLiteAgent
from core.verifier import RequirementVerifier, VerificationResult
from sandbox.security import SecurityValidator
from sandbox.executor import CodeExecutor
from benchmarking.dataset import BENCHMARK_TASKS
from benchmarking.benchmark_engine import BenchmarkEngine
from benchmarking.history import HistoryStore


class TestCodeLiteAI(unittest.TestCase):

    def setUp(self):
        self.client = get_bifrost_client()

    def test_01_bifrost_client_and_config(self):
        """Module 4: Bifrost Client verification."""
        self.assertIsNotNone(self.client)
        self.assertTrue(self.client.config.base_url.startswith("http"))
        # Test health check
        health = self.client.check_gateway_health()
        self.assertIn("online", health)
        self.assertIn("status", health)

        # Test completion
        messages = [{"role": "user", "content": "Write calculator"}]
        content, meta = self.client.chat_completion(messages)
        self.assertIsInstance(content, str)
        self.assertIn("prompt_tokens", meta)
        self.assertIn("completion_tokens", meta)
        self.assertIn("total_tokens", meta)
        self.assertGreater(meta["total_tokens"], 0)

    def test_02_task_analyzer(self):
        """Module 1: Task Analyzer verification."""
        analyzer = TaskAnalyzer(self.client)
        spec, meta = analyzer.analyze("Build a calculator in python", language="python")
        self.assertIsInstance(spec, TaskSpec)
        self.assertEqual(spec.language, "python")
        self.assertIn("calculator", spec.task_name.lower())
        self.assertGreater(meta["total_tokens"], 0)

    def test_03_context_optimizer(self):
        """Module 2: Context Optimizer verification."""
        raw_prompt = "Please make sure to write clean, maintainable, production ready code. Build a fibonacci function."
        cleaned = ContextOptimizer.strip_prompt_redundancy(raw_prompt)
        self.assertNotIn("production ready code", cleaned)
        self.assertIn("fibonacci", cleaned)

        # Test localized context extraction
        full_code = "\n".join([f"line_{i} = {i}" for i in range(1, 40)])
        localized = ContextOptimizer.extract_localized_context(full_code, failing_line=20, context_radius=5)
        self.assertIn("line_20", localized)
        self.assertNotIn("line_1 = 1", localized) # pruned distant lines

    def test_04_token_optimization_engine_and_cache(self):
        """Module 3: Token Optimization Engine & Caching verification."""
        engine = TokenOptimizationEngine()
        cache = engine.cache

        # Cache put and get
        cache.put("test_prompt", "model-1", {"result": "success"})
        cached = cache.get("test_prompt", "model-1")
        self.assertIsNotNone(cached)
        self.assertEqual(cached["result"], "success")

        # Stop condition checks (Section 4.E)
        stop, msg = engine.should_stop(tests_passed=True, current_attempt=1, max_attempts=5)
        self.assertTrue(stop)

        stop_max, msg_max = engine.should_stop(tests_passed=False, current_attempt=5, max_attempts=5)
        self.assertTrue(stop_max)

        stop_cont, _ = engine.should_stop(tests_passed=False, current_attempt=2, max_attempts=5)
        self.assertFalse(stop_cont)

    def test_05_code_generator(self):
        """Module 5: Code Generator verification."""
        generator = CodeGenerator(self.client)
        spec = TaskSpec("Calculator", "Simple calculator", "python")
        res = generator.generate(spec, enable_cache=False)
        self.assertIn("code", res)
        self.assertIn("tests", res)
        self.assertTrue(res["syntax_valid"])

    def test_06_security_and_sandbox_execution(self):
        """Module 6 & Security Sandbox verification."""
        # Security validator test
        safe_code = "def add(a, b): return a + b\nprint(add(2, 3))"
        is_safe, violations = SecurityValidator.validate_code(safe_code)
        self.assertTrue(is_safe)
        self.assertEqual(len(violations), 0)

        # Prohibited code test
        unsafe_code = "import subprocess\nsubprocess.run(['dir'])"
        is_safe_bad, violations_bad = SecurityValidator.validate_code(unsafe_code)
        self.assertFalse(is_safe_bad)
        self.assertGreater(len(violations_bad), 0)

        # Sandbox execution of safe code
        executor = CodeExecutor()
        exec_res = executor.execute_python(safe_code)
        self.assertTrue(exec_res.success)
        self.assertIn("5", exec_res.stdout)

    def test_07_error_detector(self):
        """Module 7: Error Detector verification."""
        simulated_err = (
            'Traceback (most recent call last):\n'
            '  File "solution.py", line 12, in divide\n'
            'ZeroDivisionError: division by zero\n'
        )
        detected = ErrorDetector.detect(simulated_err)
        self.assertIsNotNone(detected)
        self.assertEqual(detected.error_type, "ZeroDivisionError")
        self.assertEqual(detected.line_number, 12)

    def test_08_automatic_debugger_and_repair_limit(self):
        """Module 8: Automatic Debugger verification."""
        debugger = AutomaticDebugger(self.client, max_attempts=5)
        error = DetectedError(
            error_type="ZeroDivisionError",
            message="division by zero",
            line_number=8,
            failing_line_code="return a / b"
        )
        broken_code = "def divide(a, b):\n    return a / b\n"
        repaired, meta = debugger.debug_and_repair(broken_code, error, attempt_number=1)
        self.assertIsInstance(repaired, str)
        self.assertEqual(meta["attempt"], 1)

        # Max limit enforcement
        _, limit_meta = debugger.debug_and_repair(broken_code, error, attempt_number=6)
        self.assertFalse(limit_meta["success"])

    def test_09_test_runner(self):
        """Module 9: Test Runner verification."""
        runner = TestRunner()
        sol = "def add(a, b): return a + b"
        tests = (
            "import unittest\n"
            "from solution import add\n"
            "class TestAdd(unittest.TestCase):\n"
            "    def test_add(self):\n"
            "        self.assertEqual(add(2, 3), 5)\n"
            "if __name__ == '__main__':\n"
            "    unittest.main()\n"
        )
        res = runner.run_tests(sol, tests)
        self.assertTrue(res.all_passed)
        self.assertEqual(res.passed_tests, 1)
        self.assertEqual(res.pass_rate, 100.0)

    def test_10_autonomous_agent_loop(self):
        """Complete 10-step Autonomous Coding Agent verification."""
        agent = CodeLiteAgent(self.client, enable_cache=True)
        events_collected = []
        result = agent.run(
            "Create a Python calculator",
            language="python",
            on_event=lambda ev: events_collected.append(ev.step)
        )
        self.assertTrue(result["success"])
        self.assertIn("start", events_collected)
        self.assertIn("analyze", events_collected)
        self.assertIn("generate", events_collected)
        self.assertIn("finish", events_collected)
        self.assertGreater(result["metrics"]["total_tokens"], 0)

    def test_11_benchmark_engine_and_history(self):
        """Module 10: Benchmark Engine & Verified Token Savings."""
        engine = BenchmarkEngine(self.client)
        task = BENCHMARK_TASKS[0]
        res = engine.run_benchmark_on_task(task)
        self.assertIn("token_savings_pct", res)
        self.assertGreater(res["token_savings_pct"], 0.0)
        self.assertIn("baseline", res)
        self.assertIn("codelite", res)

        # Check SQLite store
        store = HistoryStore()
        history = store.get_benchmark_history(limit=5)
        self.assertGreater(len(history), 0)

    def test_12_requirement_verifier(self):
        """Requirement Verifier validation."""
        verifier = RequirementVerifier(self.client)
        spec = TaskSpec("Calculator", "Simple calculator with add and subtract", "python")
        good_code = (
            "class Calculator:\n"
            "    def add(self, a, b): return a + b\n"
            "    def subtract(self, a, b): return a - b\n"
        )
        res = verifier.verify("Build a calculator with add and subtract", spec, good_code)
        self.assertTrue(res.passed)
        self.assertEqual(len(res.missing_requirements), 0)
        self.assertIn("add", res.detected_symbols)

        bad_code = "def unrelated(): pass"
        res_bad = verifier.verify("Build a calculator with add and subtract", spec, bad_code)
        self.assertFalse(res_bad.passed)
        self.assertGreater(len(res_bad.missing_requirements), 0)


if __name__ == "__main__":
    unittest.main()
