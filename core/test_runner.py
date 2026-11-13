"""
Module 9: Test Runner
Executes automated unit tests against the generated code inside the sandbox.
Evaluates test pass rates, execution times, and failure traces.
Accurately reports test counts and never assumes success without verified execution.
"""

import re
from typing import Dict, Any, Optional
from sandbox.executor import CodeExecutor, ExecutionResult


class TestSuiteResult:
    def __init__(
        self,
        total_tests: int,
        passed_tests: int,
        failed_tests: int,
        error_tests: int,
        execution_time_ms: float,
        stdout: str,
        stderr: str,
        all_passed: bool
    ):
        self.total_tests = total_tests
        self.passed_tests = passed_tests
        self.failed_tests = failed_tests
        self.error_tests = error_tests
        self.execution_time_ms = round(execution_time_ms, 2)
        self.stdout = stdout
        self.stderr = stderr
        self.all_passed = all_passed
        self.pass_rate = round((passed_tests / total_tests * 100.0) if total_tests > 0 else 0.0, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "error_tests": self.error_tests,
            "pass_rate": self.pass_rate,
            "all_passed": self.all_passed,
            "execution_time_ms": self.execution_time_ms,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


class TestRunner:
    """
    Automates test execution and result parsing.
    """

    def __init__(self, executor: Optional[CodeExecutor] = None):
        self.executor = executor or CodeExecutor()

    def run_tests(self, solution_code: str, test_code: str) -> TestSuiteResult:
        """
        Runs unit tests against solution code in sandbox.
        Accurately parses outputs and handles import/syntax failures.
        """
        # Execute in sandbox
        res: ExecutionResult = self.executor.execute_python(
            code=solution_code,
            test_code=test_code
        )

        combined_output = (res.stderr + "\n" + res.stdout).strip()

        # Count defined test functions or asserts in test_code
        defined_test_methods = len(re.findall(r"\bdef test_\w+", test_code))
        defined_asserts = len(re.findall(r"\bassert\b", test_code))
        expected_test_count = max(1, defined_test_methods if defined_test_methods > 0 else defined_asserts)

        total_tests = 0
        failed_tests = 0
        error_tests = 0

        # Parse standard unittest runner output: "Ran X tests in ...s"
        ran_match = re.search(r"Ran (\d+) tests?", combined_output)
        if ran_match:
            total_tests = int(ran_match.group(1))

        failures_match = re.search(r"failures=(\d+)", combined_output)
        if failures_match:
            failed_tests = int(failures_match.group(1))

        errors_match = re.search(r"errors=(\d+)", combined_output)
        if errors_match:
            error_tests = int(errors_match.group(1))

        # Check if pytest format was used: "5 passed"
        pytest_pass = re.search(r"(\d+) passed", combined_output)
        if pytest_pass and total_tests == 0:
            total_tests = int(pytest_pass.group(1))

        pytest_fail = re.search(r"(\d+) failed", combined_output)
        if pytest_fail:
            failed_tests += int(pytest_fail.group(1))

        # Evaluate execution outcome
        if res.exit_code != 0:
            # Test script encountered an error (assertion failure, runtime error, import error)
            if total_tests == 0:
                total_tests = expected_test_count
            if failed_tests == 0 and error_tests == 0:
                failed_tests = total_tests
            passed_tests = max(0, total_tests - failed_tests - error_tests)
            all_passed = False
        else:
            # Exit code was 0
            if total_tests > 0:
                passed_tests = max(0, total_tests - failed_tests - error_tests)
                all_passed = (failed_tests == 0 and error_tests == 0 and passed_tests == total_tests)
            elif defined_asserts > 0 or defined_test_methods > 0:
                total_tests = expected_test_count
                passed_tests = expected_test_count
                all_passed = True
            else:
                total_tests = 0
                passed_tests = 0
                all_passed = False

        return TestSuiteResult(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            error_tests=error_tests,
            execution_time_ms=res.execution_time_ms,
            stdout=res.stdout,
            stderr=res.stderr,
            all_passed=all_passed
        )
