"""
Benchmark & Task History Persistence
SQLite store for tracking comparative benchmarks, token metrics, and run history.
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "codelite.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Benchmark runs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS benchmark_runs (
        id TEXT PRIMARY KEY,
        task_id TEXT,
        task_name TEXT,
        baseline_input_tokens INTEGER,
        baseline_output_tokens INTEGER,
        baseline_total_tokens INTEGER,
        baseline_requests INTEGER,
        baseline_time_ms REAL,
        baseline_repair_attempts INTEGER,
        codelite_input_tokens INTEGER,
        codelite_output_tokens INTEGER,
        codelite_total_tokens INTEGER,
        codelite_requests INTEGER,
        codelite_time_ms REAL,
        codelite_repair_attempts INTEGER,
        token_savings_pct REAL,
        test_pass_rate REAL,
        is_simulated INTEGER,
        created_at REAL
    )
    """)

    # Task history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_history (
        id TEXT PRIMARY KEY,
        prompt TEXT,
        task_name TEXT,
        language TEXT,
        code TEXT,
        tests TEXT,
        status TEXT,
        total_tokens INTEGER,
        input_tokens INTEGER,
        output_tokens INTEGER,
        estimated_cost REAL,
        repair_attempts INTEGER,
        is_simulated INTEGER,
        created_at REAL
    )
    """)

    # Stalia Verification history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS verification_history (
        id TEXT PRIMARY KEY,
        provider TEXT,
        answer_preview TEXT,
        answer_text TEXT,
        overall_score INTEGER,
        overall_status TEXT,
        score_explanation TEXT,
        summary_json TEXT,
        claims_json TEXT,
        created_at REAL
    )
    """)

    conn.commit()
    conn.close()


class HistoryStore:
    def __init__(self):
        init_db()

    def record_benchmark(self, data: Dict[str, Any]):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO benchmark_runs (
            id, task_id, task_name,
            baseline_input_tokens, baseline_output_tokens, baseline_total_tokens,
            baseline_requests, baseline_time_ms, baseline_repair_attempts,
            codelite_input_tokens, codelite_output_tokens, codelite_total_tokens,
            codelite_requests, codelite_time_ms, codelite_repair_attempts,
            token_savings_pct, test_pass_rate, is_simulated, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data.get("task_id", ""),
            data.get("task_name", "Untitled Task"),
            data["baseline"]["input_tokens"],
            data["baseline"]["output_tokens"],
            data["baseline"]["total_tokens"],
            data["baseline"]["request_count"],
            data["baseline"]["execution_time_ms"],
            data["baseline"].get("repair_attempts", 0),
            data["codelite"]["input_tokens"],
            data["codelite"]["output_tokens"],
            data["codelite"]["total_tokens"],
            data["codelite"]["request_count"],
            data["codelite"]["execution_time_ms"],
            data["codelite"].get("repair_attempts", 0),
            data["token_savings_pct"],
            data.get("test_pass_rate", 100.0),
            1 if data.get("is_simulated", False) else 0,
            data.get("created_at", time.time())
        ))
        conn.commit()
        conn.close()

    def get_benchmark_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM benchmark_runs ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def record_task(self, task_id: str, prompt: str, task_name: str, language: str,
                    code: str, tests: str, status: str, metrics: Dict[str, Any], is_simulated: bool):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO task_history (
            id, prompt, task_name, language, code, tests, status,
            total_tokens, input_tokens, output_tokens, estimated_cost,
            repair_attempts, is_simulated, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task_id,
            prompt,
            task_name,
            language,
            code,
            tests,
            status,
            metrics.get("total_tokens", 0),
            metrics.get("input_tokens", 0),
            metrics.get("output_tokens", 0),
            metrics.get("estimated_cost_usd", 0.0),
            metrics.get("repair_attempts", 0),
            1 if is_simulated else 0,
            time.time()
        ))
        conn.commit()
        conn.close()

    def get_task_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM task_history ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def record_verification(self, res: Dict[str, Any]):
        """Persists Stalia factual verification results."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO verification_history
        (id, provider, answer_preview, answer_text, overall_score, overall_status, score_explanation, summary_json, claims_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            res.get("id", f"v_{int(time.time())}"),
            res.get("provider", "chatgpt"),
            res.get("answerPreview", ""),
            res.get("answerText", ""),
            res.get("overallScore"),
            res.get("overallStatus", "not-scored"),
            res.get("scoreExplanation", ""),
            json.dumps(res.get("summary", {})),
            json.dumps(res.get("claims", [])),
            time.time()
        ))
        conn.commit()
        conn.close()

    def get_verification_history(self, limit: int = 25) -> List[Dict[str, Any]]:
        """Retrieves recent Stalia verification records."""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM verification_history ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        results = []
        for r in rows:
            d = dict(r)
            try:
                d["summary"] = json.loads(d.get("summary_json") or "{}")
                d["claims"] = json.loads(d.get("claims_json") or "[]")
            except Exception:
                d["summary"] = {}
                d["claims"] = []
            d["overallScore"] = d.get("overall_score")
            d["overallStatus"] = d.get("overall_status")
            d["scoreExplanation"] = d.get("score_explanation")
            d["answerText"] = d.get("answer_text")
            d["answerPreview"] = d.get("answer_preview")
            results.append(d)
        return results

    def get_aggregate_stats(self) -> Dict[str, Any]:
        """Aggregate totals across all benchmark and task executions."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Benchmarks aggregate
        cursor.execute("""
        SELECT
            COUNT(*),
            AVG(token_savings_pct),
            SUM(baseline_total_tokens),
            SUM(codelite_total_tokens)
        FROM benchmark_runs
        """)
        bench_count, avg_savings, total_base, total_lite = cursor.fetchone()

        # Tasks aggregate
        cursor.execute("""
        SELECT
            COUNT(*),
            SUM(total_tokens),
            SUM(estimated_cost),
            AVG(repair_attempts)
        FROM task_history
        """)
        task_count, total_tokens, total_cost, avg_repairs = cursor.fetchone()
        conn.close()

        return {
            "total_benchmark_runs": bench_count or 0,
            "average_token_savings_pct": round(avg_savings or 0.0, 1),
            "total_baseline_tokens": total_base or 0,
            "total_codelite_tokens": total_lite or 0,
            "total_tasks_completed": task_count or 0,
            "total_tokens_consumed": total_tokens or 0,
            "total_cost_usd": round(total_cost or 0.0, 5),
            "average_repair_attempts": round(avg_repairs or 0.0, 2),
        }
