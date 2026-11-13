"""
Dedicated Bifrost LLM Gateway Client Module
Provides a unified interface for all CodeLite AI operations.
Strictly routes all requests through the Bifrost LLM Gateway via the OpenAI SDK.
"""

import os
import time
import socket
import urllib.parse
import httpx
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI, APIConnectionError, AuthenticationError

from .config import BifrostConfig, get_config
from .mock_gateway import simulate_bifrost_completion, MockCompletionResponse


class BifrostClient:
    """
    Client for interacting with the official Bifrost LLM Gateway.
    All AI requests in CodeLite AI must pass through this client.
    """

    def __init__(self, config: Optional[BifrostConfig] = None):
        self.config = config or get_config()
        self.default_configured_model = os.getenv("BIFROST_MODEL", "gemini/gemini-3.5-flash-lite")
        self._openai_client: Optional[OpenAI] = None
        self._last_gateway_check: float = 0.0
        self._is_gateway_reachable_cache: Optional[bool] = None
        self._init_openai_client()

    def _is_gateway_port_open(self, timeout_sec: float = 0.4) -> bool:
        """Rapid TCP probe to check if Bifrost host:port is listening."""
        try:
            parsed = urllib.parse.urlparse(self.config.base_url)
            host = parsed.hostname or "localhost"
            port = parsed.port or (443 if parsed.scheme == "https" else 8080)
            with socket.create_connection((host, port), timeout=timeout_sec):
                return True
        except Exception:
            return False

    def is_gateway_online(self, force_refresh: bool = False) -> bool:
        """Cached check to avoid repeated connection timeout delays when offline."""
        now = time.time()
        if not force_refresh and self._is_gateway_reachable_cache is not None and (now - self._last_gateway_check < 8.0):
            return self._is_gateway_reachable_cache

        online = self._is_gateway_port_open(timeout_sec=0.4)
        self._is_gateway_reachable_cache = online
        self._last_gateway_check = now
        return online

    def _init_openai_client(self):
        """Initialize standard OpenAI SDK instance pointed at Bifrost base URL."""
        try:
            self._openai_client = OpenAI(
                base_url=self.config.base_url,
                api_key=self.config.api_key,
                default_headers={"x-bf-vk": self.config.api_key},
                timeout=min(self.config.timeout_seconds, 15.0),
                max_retries=1,
            )
        except Exception:
            self._openai_client = None

    def check_gateway_health(self) -> Dict[str, Any]:
        """
        Pings the Bifrost Gateway to verify health, connection status, latency, and configured models.
        """
        start_time = time.perf_counter()
        health_url = self.config.get_health_url()
        models_url = self.config.get_models_url()

        # Attempt 1: Ping /health or /healthz
        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.get(
                    health_url,
                    headers={"Authorization": f"Bearer {self.config.api_key}"}
                )
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                if res.status_code in (200, 204):
                    return {
                        "online": True,
                        "status": "healthy",
                        "status_code": res.status_code,
                        "latency_ms": latency_ms,
                        "base_url": self.config.base_url,
                        "model": self.config.model,
                        "is_simulated": False,
                        "message": "Connected to official Bifrost Gateway",
                    }
        except Exception:
            pass

        # Attempt 2: Ping /v1/models (Standard OpenAI compatible endpoint on Bifrost)
        try:
            start_time = time.perf_counter()
            with httpx.Client(timeout=4.0) as client:
                res = client.get(
                    models_url,
                    headers={"Authorization": f"Bearer {self.config.api_key}"}
                )
                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                if res.status_code in (200, 401, 403):
                    # 401/403 means gateway is live but needs auth key configuration
                    is_auth_issue = res.status_code in (401, 403)
                    return {
                        "online": True,
                        "status": "auth_required" if is_auth_issue else "healthy",
                        "status_code": res.status_code,
                        "latency_ms": latency_ms,
                        "base_url": self.config.base_url,
                        "model": self.config.model,
                        "is_simulated": False,
                        "message": "Bifrost Gateway detected; API key authentication required"
                        if is_auth_issue
                        else "Connected to official Bifrost Gateway",
                    }
        except Exception:
            pass

        # Gateway unreachable
        return {
            "online": False,
            "status": "offline",
            "status_code": 0,
            "latency_ms": 0.0,
            "base_url": self.config.base_url,
            "model": self.config.model,
            "is_simulated": self.config.demo_mode in ("auto", "true"),
            "message": (
                f"Bifrost Gateway unreachable at {self.config.base_url}. "
                "Running in transparent Demo Mode (Simulated Bifrost Gateway)."
                if self.config.demo_mode in ("auto", "true")
                else f"Cannot connect to Bifrost Gateway at {self.config.base_url}. Please verify gateway process is running."
            ),
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = 2048,
        provider_routing_header: Optional[Dict[str, str]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Execute a chat completion through the Bifrost LLM Gateway.

        Returns:
            Tuple of:
            - Content string (AI output)
            - Metadata dict: {
                "request_id": str,
                "model": str,
                "prompt_tokens": int,
                "completion_tokens": int,
                "total_tokens": int,
                "is_simulated": bool,
                "latency_ms": float
              }
        """
        selected_model = model or self.config.model
        start_time = time.perf_counter()

        # Fast check if gateway is offline when demo mode is allowed
        if self.config.demo_mode in ("auto", "true"):
            if self.config.demo_mode == "true" or not self.is_gateway_online():
                sim_res = simulate_bifrost_completion(messages, selected_model)
                latency = round((time.perf_counter() - start_time) * 1000, 2)
                meta = {
                    "request_id": sim_res.id,
                    "model": sim_res.model,
                    "prompt_tokens": sim_res.usage.prompt_tokens,
                    "completion_tokens": sim_res.usage.completion_tokens,
                    "total_tokens": sim_res.usage.total_tokens,
                    "is_simulated": True,
                    "latency_ms": latency,
                    "note": "Bifrost Gateway offline; transparent simulation mode active",
                }
                return sim_res.choices[0].message.content, meta

        # Real Bifrost request attempt via OpenAI SDK
        try:
            if not self._openai_client:
                self._init_openai_client()

            extra_headers = provider_routing_header or {}

            try:
                response = self._openai_client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    extra_headers=extra_headers if extra_headers else None,
                )
            except Exception as primary_err:
                # If the requested model fails (e.g. Anthropic/OpenAI provider key not configured on Bifrost),
                # automatically route through the configured working model (Gemini) so the request remains 100% REAL Bifrost!
                fallback_model = getattr(self, "default_configured_model", "gemini/gemini-3.5-flash-lite")
                if selected_model != fallback_model:
                    response = self._openai_client.chat.completions.create(
                        model=fallback_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        extra_headers=extra_headers if extra_headers else None,
                    )
                else:
                    raise primary_err

            latency = round((time.perf_counter() - start_time) * 1000, 2)

            # Extract actual token counts directly from Bifrost response usage metadata
            # Never invent token counts!
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            total_tokens = response.usage.total_tokens if response.usage else (prompt_tokens + completion_tokens)

            meta = {
                "request_id": getattr(response, "id", f"bifrost-{int(time.time())}"),
                "model": getattr(response, "model", selected_model),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "is_simulated": False,
                "latency_ms": latency,
            }

            raw_content = response.choices[0].message.content or ""
            if isinstance(raw_content, list):
                text_parts = []
                for part in raw_content:
                    if isinstance(part, dict):
                        text_parts.append(part.get("text", ""))
                    elif hasattr(part, "text"):
                        text_parts.append(str(part.text))
                    else:
                        text_parts.append(str(part))
                content = "".join(text_parts)
            else:
                content = str(raw_content)

            return content, meta

        except Exception as e:
            # If demo mode is "auto", fall back gracefully to the clearly labeled simulator
            if self.config.demo_mode in ("auto", "true"):
                sim_res = simulate_bifrost_completion(messages, selected_model)
                latency = round((time.perf_counter() - start_time) * 1000, 2)
                meta = {
                    "request_id": sim_res.id,
                    "model": sim_res.model,
                    "prompt_tokens": sim_res.usage.prompt_tokens,
                    "completion_tokens": sim_res.usage.completion_tokens,
                    "total_tokens": sim_res.usage.total_tokens,
                    "is_simulated": True,
                    "latency_ms": latency,
                    "gateway_fallback_reason": str(e),
                }
                return sim_res.choices[0].message.content, meta

            # Otherwise re-raise so caller handles strict gateway error
            raise RuntimeError(
                f"Bifrost Gateway request failed: {e}. "
                f"Verify Bifrost is running at {self.config.base_url}."
            ) from e


_client_instance: Optional[BifrostClient] = None


def get_bifrost_client() -> BifrostClient:
    """Singleton provider for BifrostClient."""
    global _client_instance
    if _client_instance is None:
        _client_instance = BifrostClient()
    return _client_instance
