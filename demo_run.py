#!/usr/bin/env python3
"""
CodeLite AI - Autonomous Agent Demonstration Runner
Runs the agent on a coding task directly in the console with live event tracing.
"""

import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bifrost.client import get_bifrost_client
from core.agent import CodeLiteAgent


def run_demo(prompt: str = "Create a Python calculator class with add, subtract, multiply, divide, and power methods."):
    client = get_bifrost_client()
    health = client.check_gateway_health()

    print("=" * 70)
    print("  CODELITE AI - TOKEN-EFFICIENT AUTONOMOUS CODING AGENT")
    print("  Powered by Bifrost LLM Gateway")
    print("=" * 70)
    print(f"[*] Gateway URL: {client.config.base_url}")
    print(f"[*] Active Model: {client.config.model}")
    print(f"[*] Gateway Status: {'ONLINE (Live Model)' if health['online'] and not health.get('is_simulated') else 'SIMULATED'}")
    print(f"[*] Latency: {health.get('latency_ms', 0)} ms")
    print("=" * 70)
    print(f"\n[?] Task Prompt: \"{prompt}\"\n")

    def on_agent_event(event):
        icons = {
            "start": "[INIT]",
            "analyze": "[ANALYSIS]",
            "analyze_complete": "[SPEC]",
            "generate": "[GENERATE]",
            "generate_complete": "[CODE READY]",
            "execute": "[SANDBOX]",
            "test": "[TESTS]",
            "error_detected": "[ERROR DETECTED]",
            "repair": "[REPAIR]",
            "re_execute": "[RE-EXECUTE]",
            "verification": "[VERIFIER]",
            "finish": "[FINALIZED]"
        }
        icon = icons.get(event.step, "[EVENT]")
        print(f"  {icon:<16} {event.message}")

    agent = CodeLiteAgent(client, enable_cache=False)
    result = agent.run(prompt, language="python", on_event=on_agent_event)

    print("\n" + "=" * 70)
    print("  FINAL AGENT RESULTS")
    print("=" * 70)
    print(f"  Task Status:        {'SUCCESS' if result['success'] else 'FAILED'}")
    print(f"  Repair Attempts:    {result['repair_attempts']} / 5")
    print(f"  Tests Executed:     {result['test_results'].get('total_tests', 0)}")
    print(f"  Tests Passed:       {result['test_results'].get('passed_tests', 0)}")
    print(f"  Tests Failed:       {result['test_results'].get('failed_tests', 0)}")
    print(f"  Pass Rate:          {result['test_results'].get('pass_rate', 0)}%")
    print(f"  Requirement Match:  {result.get('verification', {}).get('summary', 'N/A')}")
    print(f"  Input Tokens:       {result['metrics'].get('input_tokens', 0):,}")
    print(f"  Output Tokens:      {result['metrics'].get('output_tokens', 0):,}")
    print(f"  Total Tokens:       {result['metrics'].get('total_tokens', 0):,}")
    print(f"  Estimated Cost:     ${result['metrics'].get('estimated_cost_usd', 0.0):.6f}")
    print("=" * 70)

    print("\n[+] GENERATED SOLUTION CODE:")
    print("-" * 50)
    print(result["solution_code"])
    print("-" * 50)

    print("\n[+] VERIFIED UNIT TESTS:")
    print("-" * 50)
    print(result["test_code"])
    print("-" * 50)


if __name__ == "__main__":
    task = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Create a Python calculator class with add, subtract, multiply, divide, and power methods."
    run_demo(task)
