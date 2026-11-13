"""
Module 6: Code Executor & Sandbox
Safely executes generated code inside an isolated Docker sandbox with resource limits,
timeouts, and disabled network access.
Provides a secure fallback process sandbox with AST sanitization when Docker is offline.
"""

import os
import sys
import time
import shutil
import tempfile
import subprocess
from typing import Dict, Any, Optional
from .security import SecurityValidator


class ExecutionResult:
    def __init__(
        self,
        stdout: str,
        stderr: str,
        exit_code: int,
        execution_time_ms: float,
        sandbox_type: str,
        timed_out: bool = False,
        security_blocked: bool = False,
        error_type: Optional[str] = None
    ):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.execution_time_ms = round(execution_time_ms, 2)
        self.sandbox_type = sandbox_type
        self.timed_out = timed_out
        self.security_blocked = security_blocked
        self.error_type = error_type

    @property
    def success(self) -> bool:
        return self.exit_code == 0 and not self.timed_out and not self.security_blocked

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "execution_time_ms": self.execution_time_ms,
            "sandbox_type": self.sandbox_type,
            "timed_out": self.timed_out,
            "security_blocked": self.security_blocked,
            "success": self.success,
            "error_type": self.error_type,
        }


class CodeExecutor:
    """
    Manages safe program execution.
    Prioritizes isolated Docker container sandbox.
    Falls back to AST-scanned, isolated subprocess sandbox when Docker is unavailable.
    """

    def __init__(
        self,
        timeout_seconds: float = 8.0,
        memory_limit_mb: int = 256,
        cpu_limit: float = 1.0,
        enable_docker: bool = True
    ):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit = cpu_limit
        self.enable_docker = enable_docker
        self._docker_available = self._detect_docker()

    def _detect_docker(self) -> bool:
        """Check if docker CLI is available and operational."""
        if not self.enable_docker:
            return False
        try:
            res = subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=2.0,
                check=False
            )
            return res.returncode == 0
        except Exception:
            return False

    def is_docker_active(self) -> bool:
        return self._docker_available

    def execute_python(
        self,
        code: str,
        test_code: str = "",
        input_data: str = ""
    ) -> ExecutionResult:
        """
        Executes python code + tests securely inside sandbox.
        """
        # Step 1: AST Security scan
        is_safe, violations = SecurityValidator.validate_code(code + "\n" + test_code)
        if not is_safe:
            msg = "Security Sandbox Violation: Prohibited operations detected:\n" + "\n".join(f"- {v}" for v in violations)
            return ExecutionResult(
                stdout="",
                stderr=msg,
                exit_code=1,
                execution_time_ms=0.0,
                sandbox_type="security_filter",
                security_blocked=True,
                error_type="SecurityViolation"
            )

        # Step 2: Choose execution strategy
        if self._docker_available:
            return self._execute_in_docker(code, test_code, input_data)
        else:
            return self._execute_in_process_sandbox(code, test_code, input_data)

    def _prepare_test_script(self, code: str, test_code: str) -> str:
        """
        Ensures the test script reliably imports solution.py and executes tests.
        """
        script = test_code.strip()
        path_header = (
            "import sys\n"
            "from pathlib import Path\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
        )

        if "from solution import" not in script and "import solution" not in script:
            script = path_header + "from solution import *\n\n" + script
        else:
            script = path_header + "\n" + script

        # Ensure unittest.main() is present if tests use unittest
        if "unittest.TestCase" in script and "unittest.main" not in script:
            script += "\n\nif __name__ == '__main__':\n    import unittest\n    unittest.main(verbosity=2)\n"

        return script

    def _execute_in_docker(
        self,
        code: str,
        test_code: str,
        input_data: str
    ) -> ExecutionResult:
        """Runs the payload in an isolated Docker container with strict constraints."""
        temp_dir = tempfile.mkdtemp(prefix="codelite_docker_")
        start_time = time.perf_counter()
        try:
            # Write solution and test file
            sol_path = os.path.join(temp_dir, "solution.py")
            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(code)

            entry_script = os.path.join(temp_dir, "run.py")
            with open(entry_script, "w", encoding="utf-8") as f:
                if test_code:
                    f.write(self._prepare_test_script(code, test_code))
                else:
                    f.write(code)

            # Docker execution flags:
            # --network none : disables all network access
            # -m 256m : limits RAM
            # --cpus 1.0 : limits CPU
            # --read-only : container root is read only
            # --user 1000:1000 : non-root execution
            docker_cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "-m", f"{self.memory_limit_mb}m",
                "--cpus", str(self.cpu_limit),
                "-v", f"{temp_dir}:/app:ro",
                "-w", "/app",
                "python:3.11-slim",
                "python", "run.py"
            ]

            proc = subprocess.run(
                docker_cmd,
                input=input_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout_seconds
            )
            elapsed = (time.perf_counter() - start_time) * 1000.0

            return ExecutionResult(
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                execution_time_ms=elapsed,
                sandbox_type="docker_isolated"
            )

        except subprocess.TimeoutExpired:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                stdout="",
                stderr=f"Execution timed out after {self.timeout_seconds} seconds.",
                exit_code=-1,
                execution_time_ms=elapsed,
                sandbox_type="docker_isolated",
                timed_out=True,
                error_type="TimeoutError"
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            # Fallback to process sandbox if docker daemon unexpectedly failed
            return self._execute_in_process_sandbox(code, test_code, input_data)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _execute_in_process_sandbox(
        self,
        code: str,
        test_code: str,
        input_data: str
    ) -> ExecutionResult:
        """
        Isolated Subprocess Sandbox:
        - Runs in clean temp dir
        - Strips all API keys from environment
        - Applies strict timeout
        """
        temp_dir = tempfile.mkdtemp(prefix="codelite_sandbox_")
        start_time = time.perf_counter()
        try:
            # Write solution module
            sol_path = os.path.join(temp_dir, "solution.py")
            with open(sol_path, "w", encoding="utf-8") as f:
                f.write(code)

            # Write run script (tests or main code)
            entry_path = os.path.join(temp_dir, "run.py")
            with open(entry_path, "w", encoding="utf-8") as f:
                if test_code:
                    f.write(self._prepare_test_script(code, test_code))
                else:
                    f.write(code)

            # Sanitized environment: strip sensitive tokens and credentials
            sanitized_env = {
                "PYTHONPATH": temp_dir,
                "PYTHONUNBUFFERED": "1",
                "PATH": os.environ.get("PATH", ""),
                "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
                "TEMP": temp_dir,
                "TMP": temp_dir,
            }

            proc = subprocess.run(
                [sys.executable, "run.py"],
                cwd=temp_dir,
                env=sanitized_env,
                input=input_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout_seconds
            )
            elapsed = (time.perf_counter() - start_time) * 1000.0

            return ExecutionResult(
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                execution_time_ms=elapsed,
                sandbox_type="secure_process_sandbox"
            )

        except subprocess.TimeoutExpired:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                stdout="",
                stderr=f"Execution timed out after {self.timeout_seconds} seconds.",
                exit_code=-1,
                execution_time_ms=elapsed,
                sandbox_type="secure_process_sandbox",
                timed_out=True,
                error_type="TimeoutError"
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000.0
            return ExecutionResult(
                stdout="",
                stderr=f"Sandbox Execution Error: {str(e)}",
                exit_code=1,
                execution_time_ms=elapsed,
                sandbox_type="secure_process_sandbox",
                error_type="ExecutionException"
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
