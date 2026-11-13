"""
API Endpoints for CodeLite AI
Connects the frontend dashboard to all backend modules:
Agent execution, Bifrost gateway status, Benchmarking, History, and Token Analytics.
"""

import uuid
import time
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List

from bifrost.client import get_bifrost_client
from bifrost.config import get_config
from core.agent import CodeLiteAgent
from benchmarking.benchmark_engine import BenchmarkEngine
from benchmarking.dataset import BENCHMARK_TASKS
from benchmarking.history import HistoryStore
from core.stalia_verifier import StaliaVerifier
from .schemas import (
    TaskExecutionRequest,
    BenchmarkRunRequest,
    GatewayConfigUpdate,
    VerifyRequest,
    PluginVerifyRequest,
    MultiVerifyRequest
)

router = APIRouter(prefix="/api")
history_store = HistoryStore()


@router.get("/health")
def get_gateway_health():
    """
    Checks the connectivity and status of the official Bifrost LLM Gateway.
    """
    client = get_bifrost_client()
    health_info = client.check_gateway_health()
    return {
        "gateway": health_info,
        "config": {
            "base_url": client.config.base_url,
            "model": client.config.model,
            "demo_mode": client.config.demo_mode,
            "is_configured": client.config.is_configured()
        },
        "system": {
            "docker_available": CodeLiteAgent(client).code_executor.is_docker_active(),
            "timestamp": time.time()
        }
    }


@router.post("/task/run")
def run_task(req: TaskExecutionRequest):
    """
    Executes the full 10-step autonomous coding agent loop.
    """
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Task prompt cannot be empty.")

    client = get_bifrost_client()
    agent = CodeLiteAgent(client, enable_cache=req.enable_cache)
    task_id = f"task_{uuid.uuid4().hex[:8]}"

    # Execute agent
    result = agent.run(req.prompt, language=req.language)

    # Persist to history
    history_store.record_task(
        task_id=task_id,
        prompt=req.prompt,
        task_name=result.get("task_name", "Custom Task"),
        language=req.language,
        code=result.get("solution_code", ""),
        tests=result.get("test_code", ""),
        status="SUCCESS" if result.get("success") else "FAILED",
        metrics=result.get("metrics", {}),
        is_simulated=result.get("is_simulated", False)
    )

    result["task_id"] = task_id
    return result


@router.get("/benchmark/dataset")
def get_benchmark_dataset():
    """
    Returns the standard benchmark tasks for evaluation.
    """
    return {"tasks": BENCHMARK_TASKS}


@router.post("/benchmark/run")
def run_benchmark(req: BenchmarkRunRequest):
    """
    Runs head-to-head comparison between Standard Baseline Agent and CodeLite AI.
    """
    client = get_bifrost_client()
    engine = BenchmarkEngine(client)

    if req.custom_prompt:
        custom_task = {
            "id": f"custom_{uuid.uuid4().hex[:6]}",
            "name": req.custom_prompt[:30].title(),
            "prompt": req.custom_prompt,
            "language": req.language
        }
        res = engine.run_benchmark_on_task(custom_task)
        return {"results": [res]}

    if req.task_id == "all":
        results = engine.run_all_benchmarks()
        return {"results": results}

    # Find matching task in dataset
    target_task = None
    if req.task_id:
        for t in BENCHMARK_TASKS:
            if t["id"] == req.task_id:
                target_task = t
                break

    if not target_task:
        target_task = BENCHMARK_TASKS[0]

    res = engine.run_benchmark_on_task(target_task)
    return {"results": [res]}


@router.get("/benchmark/history")
def get_benchmark_history():
    """
    Returns historical benchmark executions.
    """
    runs = history_store.get_benchmark_history(limit=50)
    return {"history": runs}


@router.get("/history")
def get_tasks_history():
    """
    Returns completed task runs.
    """
    tasks = history_store.get_task_history(limit=50)
    return {"tasks": tasks}


@router.get("/analytics")
def get_analytics():
    """
    Returns aggregated token savings, request counts, and cost efficiency.
    """
    stats = history_store.get_aggregate_stats()
    client = get_bifrost_client()

    return {
        "stats": stats,
        "active_model": client.config.model,
        "gateway_url": client.config.base_url,
    }


@router.post("/config/update")
def update_gateway_config(cfg: GatewayConfigUpdate):
    """
    Updates Bifrost Gateway connection parameters (model, base_url, API key, demo mode).
    Demonstrates dynamic provider routing without restarting the app.
    """
    client = get_bifrost_client()
    if cfg.base_url:
        client.config.base_url = cfg.base_url.rstrip("/")
    if cfg.api_key:
        client.config.api_key = cfg.api_key
    if cfg.model:
        client.config.model = cfg.model
    if cfg.demo_mode:
        client.config.demo_mode = cfg.demo_mode.lower()

    # Reinitialize client with new parameters
    client._init_openai_client()
    client.is_gateway_online(force_refresh=True)

    return {
        "success": True,
        "message": f"Gateway configuration updated. Active model: {client.config.model}",
        "config": {
            "base_url": client.config.base_url,
            "model": client.config.model,
            "demo_mode": client.config.demo_mode,
        }
    }


# --------------------------------------------------------------------------
# Stalia.AI Factual Verification & Hallucination Detection Routes
# --------------------------------------------------------------------------

@router.post("/verify")
def verify_factual_answer(req: VerifyRequest):
    """
    Stalia.AI: Extracts claims from an answer, verifies each against grounded
    web & reference documentation, and computes an impact-weighted trust score.
    """
    if not req.answer or len(req.answer.strip()) < 10:
        raise HTTPException(status_code=400, detail="Answer text must be at least 10 characters long.")

    verifier = StaliaVerifier()
    result = verifier.verify_answer(req.answer, provider=req.provider or "chatgpt")
    history_store.record_verification(result)
    return result


@router.post("/plugin/verify")
def plugin_verify_answer(req: PluginVerifyRequest):
    """
    Endpoint for browser extension, bookmarklet, and external AI plugins.
    """
    if not req.answer or len(req.answer.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters long.")

    verifier = StaliaVerifier()
    result = verifier.verify_answer(req.answer, provider=req.provider or "browser-plugin")
    history_store.record_verification(result)

    if req.format == "text":
        score = f"{result['overallScore']}/100" if result['overallScore'] is not None else "Unrated"
        supp = result['summary']['supported']
        stale = result['summary']['potentiallyStale']
        review = result['summary']['needsReview']
        return {
            "text": f"Stalia.AI Trust Score: {score} | {supp} Supported, {stale} Stale, {review} Needs Review.\n{result['scoreExplanation']}"
        }

    return result


@router.post("/verify/multi")
def verify_multi_ai(req: MultiVerifyRequest):
    """
    Multi-AI Consensus Studio: Compares answers from ChatGPT, Claude, and Gemini,
    calculating agreement rate, cross-model consensus score, and claim divergence.
    """
    if not req.answers:
        raise HTTPException(status_code=400, detail="Must provide answers dictionary.")

    verifier = StaliaVerifier()
    return verifier.compare_providers(req.answers)


@router.get("/verify/history")
def get_verification_history():
    """Returns recent Stalia verification checks."""
    return {"history": history_store.get_verification_history(limit=25)}


@router.get("/mcp")
def get_mcp_manifest():
    """
    Model Context Protocol (MCP) server endpoint for Stalia.AI.
    Enables Claude Desktop, Cursor, and other MCP clients to verify AI claims.
    """
    return {
        "name": "stalia-freshness-checker",
        "version": "1.0.0",
        "description": "Real-time fact-checking and freshness detection tool for AI answers.",
        "tools": [
            {
                "name": "verifyAIAnswer",
                "description": "Verify factual claims, dates, and API versions in an AI answer.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "answer": {
                            "type": "string",
                            "description": "The AI response text to verify for factual accuracy."
                        },
                        "provider": {
                            "type": "string",
                            "description": "Optional model or provider name."
                        }
                    },
                    "required": ["answer"]
                }
            }
        ]
    }
