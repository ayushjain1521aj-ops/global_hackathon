"""
Benchmark Dataset
Standard coding challenges for measuring token efficiency across agents.
"""

from typing import List, Dict, Any

BENCHMARK_TASKS: List[Dict[str, Any]] = [
    {
        "id": "calculator",
        "name": "Python Calculator with Arithmetic & Power",
        "prompt": "Create a Python calculator class with add, subtract, multiply, divide (handling zero division error), and power operations.",
        "language": "python",
        "difficulty": "Easy",
        "expected_functions": ["add", "subtract", "multiply", "divide", "power"]
    },
    {
        "id": "student_management",
        "name": "Student Management System",
        "prompt": "Build a Student Management System with Student class (id, name, gpa, courses) and System class (add, remove, get_student, list_all, average_gpa).",
        "language": "python",
        "difficulty": "Medium",
        "expected_functions": ["add_student", "get_student", "remove_student", "average_gpa"]
    },
    {
        "id": "prime_checker",
        "name": "Prime Number Checker & Sieve",
        "prompt": "Write a prime number checker function is_prime(n) optimized to O(sqrt(n)) and a function get_primes_up_to(limit) using the Sieve of Eratosthenes.",
        "language": "python",
        "difficulty": "Easy-Medium",
        "expected_functions": ["is_prime", "get_primes_up_to"]
    },
    {
        "id": "sorting_algorithm",
        "name": "Quicksort Algorithm with Asc/Desc",
        "prompt": "Implement a robust quicksort algorithm in Python that accepts a list and an optional reverse boolean flag to sort in ascending or descending order.",
        "language": "python",
        "difficulty": "Medium",
        "expected_functions": ["quicksort"]
    },
    {
        "id": "inventory_management",
        "name": "Inventory Management System",
        "prompt": "Create an Inventory Management System with Item class (sku, name, quantity, price) and InventorySystem class (add_or_update, restock, sell, get_total_inventory_value).",
        "language": "python",
        "difficulty": "Medium-Hard",
        "expected_functions": ["add_or_update_item", "restock", "sell", "get_total_inventory_value"]
    }
]
