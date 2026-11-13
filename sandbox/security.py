"""
Security and Safety Verification Module for CodeLite AI
Performs AST pre-execution scanning to prevent host tampering, network calls,
and dangerous system execution.
"""

import ast
from typing import Tuple, List

# Blocked Python modules that should never be invoked in generated user algorithms
FORBIDDEN_MODULES = {
    "subprocess",
    "ctypes",
    "winreg",
    "shutil",
    "socket",
    "pysftp",
    "paramiko",
    "pty",
    "posix",
    "nt",
    "webbrowser",
}

# Dangerous call patterns
FORBIDDEN_CALLS = {
    "system",
    "popen",
    "spawn",
    "fork",
    "rmdir",
    "remove",
    "unlink",
    "eval",
    "exec",
    "__import__",
}


class SecurityValidator:
    """
    Validates Python source code against forbidden security operations prior to execution.
    """

    @classmethod
    def validate_code(cls, source_code: str) -> Tuple[bool, List[str]]:
        """
        Scans code AST. Returns (is_safe, list_of_violations).
        """
        violations = []

        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            # Syntax errors will be handled by ErrorDetector/AutomaticDebugger
            return True, []

        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod_name = alias.name.split(".")[0]
                    if mod_name in FORBIDDEN_MODULES:
                        violations.append(f"Forbidden module import detected: '{alias.name}'")

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod_name = node.module.split(".")[0]
                    if mod_name in FORBIDDEN_MODULES:
                        violations.append(f"Forbidden from-import detected: '{node.module}'")

            # Check function calls
            elif isinstance(node, ast.Call):
                func = node.func
                # e.g., os.system(...)
                if isinstance(func, ast.Attribute):
                    if func.attr in FORBIDDEN_CALLS:
                        violations.append(f"Potentially hazardous call detected: '.{func.attr}()'")
                elif isinstance(func, ast.Name):
                    if func.id in ("eval", "exec", "__import__"):
                        violations.append(f"Hazardous dynamic execution call: '{func.id}()'")

        return (len(violations) == 0, violations)
