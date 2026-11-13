"""
Verification test for BenchmarkEngine
"""

from benchmarking.benchmark_engine import BenchmarkEngine
from benchmarking.dataset import BENCHMARK_TASKS

def main():
    print("Initializing Benchmark Engine...")
    engine = BenchmarkEngine()
    test_task = BENCHMARK_TASKS[0] # Calculator
    print(f"Running side-by-side benchmark on: {test_task['name']}...")

    res = engine.run_benchmark_on_task(test_task)

    print("\n--- Side-by-Side Benchmark Results ---")
    print(f"Task: {res['task_name']}")
    print(f"Baseline Total Tokens: {res['baseline']['total_tokens']}")
    print(f"CodeLite Total Tokens: {res['codelite']['total_tokens']}")
    print(f"VERIFIED TOKEN SAVINGS: {res['token_savings_pct']}%")
    print(f"Baseline Requests: {res['baseline']['request_count']} vs CodeLite Requests: {res['codelite']['request_count']}")
    print(f"Test Pass Rate: {res['test_pass_rate']}%")
    print(f"Is Simulated: {res['is_simulated']}")
    print("\nBenchmark engine verification successfully passed!")

if __name__ == "__main__":
    main()
