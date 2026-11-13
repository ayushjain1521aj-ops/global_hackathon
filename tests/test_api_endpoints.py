"""
API Integration Test Suite
Validates FastAPI endpoints, routing, and schema serialization.
"""

import unittest
import sys
from pathlib import Path
from starlette.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.main import app


class TestApiEndpoints(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_ping(self):
        res = self.client.get("/ping")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")

    def test_02_gateway_health(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("gateway", data)
        self.assertIn("config", data)
        self.assertIn("system", data)

    def test_03_benchmark_dataset(self):
        res = self.client.get("/api/benchmark/dataset")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tasks", data)
        self.assertEqual(len(data["tasks"]), 5)

    def test_04_task_run_endpoint(self):
        payload = {
            "prompt": "Create a Python calculator",
            "language": "python",
            "enable_cache": True
        }
        res = self.client.post("/api/task/run", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        self.assertIn("solution_code", data)
        self.assertIn("metrics", data)

    def test_05_benchmark_run_endpoint(self):
        payload = {"task_id": "calculator"}
        res = self.client.post("/api/benchmark/run", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("results", data)
        self.assertGreater(data["results"][0]["token_savings_pct"], 0)

    def test_06_analytics_and_history(self):
        res_ana = self.client.get("/api/analytics")
        self.assertEqual(res_ana.status_code, 200)
        self.assertIn("stats", res_ana.json())

        res_hist = self.client.get("/api/history")
        self.assertEqual(res_hist.status_code, 200)
        self.assertIn("tasks", res_hist.json())


if __name__ == "__main__":
    unittest.main()
