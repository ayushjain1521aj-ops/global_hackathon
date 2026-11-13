"""
Module 7: Error Detector
Parses compiler and runtime output, classifies Python exceptions,
and pinpoints failing code lines and traceback frames.
"""

import re
from typing import Dict, Any, Optional, List


class DetectedError:
    def __init__(
        self,
        error_type: str,
        message: str,
        line_number: Optional[int] = None,
        failing_line_code: str = "",
        traceback_snippet: str = "",
        is_test_failure: bool = False
    ):
        self.error_type = error_type
        self.message = message
        self.line_number = line_number
        self.failing_line_code = failing_line_code
        self.traceback_snippet = traceback_snippet
        self.is_test_failure = is_test_failure

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "message": self.message,
            "line_number": self.line_number,
            "failing_line_code": self.failing_line_code,
            "traceback_snippet": self.traceback_snippet,
            "is_test_failure": self.is_test_failure
        }


class ErrorDetector:
    """
    Scans stderr and stdout from sandbox execution to identify errors.
    """

    KNOWN_EXCEPTIONS = [
        "SyntaxError",
        "IndentationError",
        "TabError",
        "TypeError",
        "NameError",
        "AttributeError",
        "ValueError",
        "IndexError",
        "KeyError",
        "ZeroDivisionError",
        "AssertionError",
        "TimeoutError",
        "FileNotFoundError",
        "ImportError",
        "ModuleNotFoundError",
        "RecursionError",
        "SecurityViolation",
    ]

    @classmethod
    def detect(cls, stderr: str, stdout: str = "", source_code: str = "") -> Optional[DetectedError]:
        """
        Extracts structured error info from execution logs.
        """
        combined = (stderr + "\n" + stdout).strip()
        if not combined:
            return None

        # Check for SecurityViolation
        if "Security Sandbox Violation" in combined:
            return DetectedError(
                error_type="SecurityViolation",
                message=combined.split("\n")[0],
                line_number=1,
                traceback_snippet=combined
            )

        # Check for Timeout
        if "timed out after" in combined.lower():
            return DetectedError(
                error_type="TimeoutError",
                message="Execution exceeded timeout threshold (potential infinite loop)",
                line_number=None,
                traceback_snippet=combined
            )

        # Match Python Standard Traceback
        # e.g.: File "run.py", line 14, in <module>
        #       File "solution.py", line 8, in divide
        line_matches = re.findall(r'File ".*?", line (\d+)(?:, in (\w+))?', combined)
        line_num = None
        if line_matches:
            # Prefer last frame in traceback (nearest to failure)
            line_num = int(line_matches[-1][0])

        # Match Exception Type & Message
        # e.g.: ZeroDivisionError: division by zero
        #       AssertionError: 5.0 != 4.0
        err_type = "RuntimeError"
        err_msg = ""

        for exc in cls.KNOWN_EXCEPTIONS:
            pattern = rf"\b{exc}:?\s*(.*)"
            match = re.search(pattern, combined)
            if match:
                err_type = exc
                err_msg = match.group(1).strip()
                break

        # Check for unittest test failures (FAILED (failures=1, errors=0))
        is_test_fail = "FAILED" in combined or "AssertionError" in err_type

        # Extract offending code line if line number is available
        failing_line_code = ""
        if line_num and source_code:
            lines = source_code.splitlines()
            if 0 < line_num <= len(lines):
                failing_line_code = lines[line_num - 1].strip()

        # Capture concise traceback frame (last 4 lines only)
        lines = [ln for ln in combined.splitlines() if ln.strip()]
        concise_tb = "\n".join(lines[-4:]) if len(lines) >= 4 else "\n".join(lines)

        return DetectedError(
            error_type=err_type,
            message=err_msg or "Execution failed with non-zero exit code",
            line_number=line_num,
            failing_line_code=failing_line_code,
            traceback_snippet=concise_tb,
            is_test_failure=is_test_fail
        )
