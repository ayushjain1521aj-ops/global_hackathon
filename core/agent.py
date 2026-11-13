"""
CodeLite Autonomous Coding Agent
Coordinates the complete 10-step autonomous loop:
Analyze -> Subtasks -> Generate -> Sandbox Execute -> Error Detect ->
Targeted Repair -> Re-execute -> Test Verification -> Requirement Verification -> Final Output.
"""

import time
from typing import Dict, Any, Optional, Callable, List
from bifrost.client import BifrostClient, get_bifrost_client
from .task_analyzer import TaskAnalyzer, TaskSpec
from .token_optimizer import TokenOptimizationEngine, TokenMetrics
from .code_generator import CodeGenerator
from .error_detector import ErrorDetector, DetectedError
from .auto_debugger import AutomaticDebugger
from .test_runner import TestRunner, TestSuiteResult
from .verifier import RequirementVerifier, VerificationResult
from sandbox.executor import CodeExecutor


class AgentEvent:
    def __init__(self, step: str, message: str, data: Optional[Dict[str, Any]] = None):
        self.step = step
        self.message = message
        self.data = data or {}
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp
        }


class CodeLiteAgent:
    """
    Token-efficient autonomous coding agent powered by Bifrost LLM Gateway.
    """

    def __init__(
        self,
        client: Optional[BifrostClient] = None,
        max_repair_attempts: int = 5,
        enable_cache: bool = True
    ):
        self.client = client or get_bifrost_client()
        self.token_engine = TokenOptimizationEngine()
        self.task_analyzer = TaskAnalyzer(self.client)
        self.code_generator = CodeGenerator(self.client, self.token_engine)
        self.code_executor = CodeExecutor()
        self.error_detector = ErrorDetector()
        self.auto_debugger = AutomaticDebugger(self.client, self.token_engine, max_attempts=max_repair_attempts)
        self.test_runner = TestRunner(self.code_executor)
        self.verifier = RequirementVerifier(self.client)
        self.max_repair_attempts = max_repair_attempts
        self.enable_cache = enable_cache

    def run(
        self,
        task_prompt: str,
        language: str = "python",
        on_event: Optional[Callable[[AgentEvent], None]] = None
    ) -> Dict[str, Any]:
        """
        Executes the autonomous coding workflow.
        """
        events: List[AgentEvent] = []
        metrics = TokenMetrics()

        def emit(step: str, message: str, data: Optional[Dict[str, Any]] = None):
            ev = AgentEvent(step, message, data)
            events.append(ev)
            if on_event:
                try:
                    on_event(ev)
                except Exception:
                    pass

        emit("start", f"CodeLite AI initialized for task: '{task_prompt[:50]}...'", {
            "language": language,
            "model": self.client.config.model,
            "gateway_url": self.client.config.base_url
        })

        # Step 1 & 2: Understand requirements and subtask breakdown
        emit("analyze", "Analyzing requirements and deriving minimal specification...")
        task_spec, analyzer_meta = self.task_analyzer.analyze(task_prompt, language=language)
        metrics.add_call(
            analyzer_meta.get("prompt_tokens", 0),
            analyzer_meta.get("completion_tokens", 0),
            analyzer_meta.get("model", self.client.config.model)
        )
        emit("analyze_complete", f"Specification ready: {task_spec.task_name} ({task_spec.complexity})", task_spec.to_dict())

        # Step 3: Generate code using Bifrost
        emit("generate", "Generating solution and automated unit tests via Bifrost Gateway...")
        gen_result = self.code_generator.generate(task_spec, metrics=metrics, enable_cache=self.enable_cache)
        current_code = gen_result["code"]
        current_tests = gen_result["tests"]

        emit("generate_complete", "Initial code generation completed.", {
            "from_cache": gen_result["from_cache"],
            "code_lines": len(current_code.splitlines()),
            "tests_lines": len(current_tests.splitlines()),
            "tokens": gen_result["metadata"]["total_tokens"],
            "is_simulated": gen_result["metadata"].get("is_simulated", False)
        })

        # Step 4: Execute code in isolated sandbox
        sandbox_badge = "Docker Sandbox" if self.code_executor.is_docker_active() else "Secure Process Sandbox"
        emit("execute", f"Dispatching program to {sandbox_badge}...")
        exec_result = self.code_executor.execute_python(current_code)

        attempt = 0
        tests_passed = False
        test_suite_res = None
        error_info: Optional[DetectedError] = None

        # Check for immediate runtime / syntax failure in main execution
        if not exec_result.success:
            error_info = self.error_detector.detect(exec_result.stderr, exec_result.stdout, current_code)

        # If main execution succeeded, run the test runner
        if exec_result.success:
            emit("test", "Executing unit test suite in sandbox...")
            test_suite_res = self.test_runner.run_tests(current_code, current_tests)
            tests_passed = test_suite_res.all_passed
            if not tests_passed:
                error_info = self.error_detector.detect(test_suite_res.stderr, test_suite_res.stdout, current_code)

        # Step 5 to 9: Targeted Error Correction and Repair Loop (max 5 attempts)
        while not tests_passed and attempt < self.max_repair_attempts:
            attempt += 1
            err_type = error_info.error_type if error_info else "ExecutionError"
            err_msg = error_info.message if error_info else "Tests failed"
            err_line = error_info.line_number if error_info else None

            emit("error_detected", f"Detected {err_type} at line {err_line or '?'}: {err_msg[:60]}", {
                "attempt": attempt,
                "error": error_info.to_dict() if error_info else {}
            })

            # Check stop condition (Section 4.E)
            should_stop, reason = self.token_engine.should_stop(tests_passed, attempt, self.max_repair_attempts)
            if should_stop:
                emit("stop_condition", reason)
                break

            emit("repair", f"Generating targeted correction (Attempt {attempt}/{self.max_repair_attempts})...")
            repaired_code, repair_meta = self.auto_debugger.debug_and_repair(
                current_code=current_code,
                error=error_info,
                attempt_number=attempt,
                metrics=metrics,
                language=language,
                task_goal=task_spec.goal
            )
            current_code = repaired_code

            # Re-execute in sandbox
            emit("re_execute", f"Re-executing corrected code in sandbox (Attempt {attempt})...")
            exec_result = self.code_executor.execute_python(current_code)

            if exec_result.success:
                test_suite_res = self.test_runner.run_tests(current_code, current_tests)
                tests_passed = test_suite_res.all_passed
                if not tests_passed:
                    error_info = self.error_detector.detect(test_suite_res.stderr, test_suite_res.stdout, current_code)
                else:
                    error_info = None
            else:
                tests_passed = False
                error_info = self.error_detector.detect(exec_result.stderr, exec_result.stdout, current_code)

        # Step 10: Requirement Verification Step
        emit("verification", "Verifying solution against original prompt requirements...")
        verification_result = self.verifier.verify(task_prompt, task_spec, current_code)

        # Strict success evaluation: tests must have run and passed, and requirements must be verified
        has_tests_run = bool(test_suite_res and test_suite_res.total_tests > 0)
        has_tests_passed = bool(has_tests_run and test_suite_res.all_passed and test_suite_res.failed_tests == 0 and test_suite_res.error_tests == 0)
        is_successful = has_tests_passed and verification_result.passed

        final_pass_rate = test_suite_res.pass_rate if test_suite_res else 0.0

        if is_successful:
            emit("finish", "Autonomous coding task finalized successfully.", {
                "success": True,
                "pass_rate": final_pass_rate,
                "total_tokens": metrics.total_tokens,
                "repair_attempts": attempt,
                "verification": verification_result.to_dict()
            })
        else:
            failure_reason = ""
            if not has_tests_run:
                failure_reason = "Tests could not execute or were not generated."
            elif not has_tests_passed:
                failure_reason = f"Test suite failures ({test_suite_res.failed_tests + test_suite_res.error_tests} failed/errored out of {test_suite_res.total_tests})."
            elif not verification_result.passed:
                failure_reason = f"Requirement mismatch: {verification_result.summary}"

            emit("finish", f"Task incomplete: {failure_reason}", {
                "success": False,
                "pass_rate": final_pass_rate,
                "total_tokens": metrics.total_tokens,
                "repair_attempts": attempt,
                "error": error_info.to_dict() if error_info else {"message": failure_reason},
                "verification": verification_result.to_dict()
            })

        return {
            "success": is_successful,
            "task_name": task_spec.task_name,
            "language": language,
            "solution_code": current_code,
            "test_code": current_tests,
            "execution_result": exec_result.to_dict(),
            "test_results": test_suite_res.to_dict() if test_suite_res else {
                "total_tests": 1,
                "passed_tests": 1 if is_successful else 0,
                "failed_tests": 0 if is_successful else 1,
                "error_tests": 0 if is_successful else 1,
                "pass_rate": final_pass_rate,
                "all_passed": is_successful,
                "stdout": exec_result.stdout,
                "stderr": exec_result.stderr,
                "execution_time_ms": exec_result.execution_time_ms
            },
            "verification": verification_result.to_dict(),
            "repair_attempts": attempt,
            "metrics": metrics.to_dict(),
            "events": [e.to_dict() for e in events],
            "sandbox_type": exec_result.sandbox_type,
            "is_simulated": gen_result["metadata"].get("is_simulated", False)
        }
