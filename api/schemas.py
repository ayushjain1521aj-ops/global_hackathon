"""
API Schemas for CodeLite AI
Pydantic data models for requests, responses, and real-time streams.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class TaskExecutionRequest(BaseModel):
    prompt: str = Field(..., description="Natural language description of the coding task")
    language: str = Field(default="python", description="Programming language target")
    enable_cache: bool = Field(default=True, description="Enable prompt/context caching")
    model_override: Optional[str] = Field(default=None, description="Optional Bifrost model override")
    complexity: Optional[str] = Field(default="essential", description="Complexity style: essential, standard, dataclass")
    max_repair_cycles: Optional[int] = Field(default=3, description="Max autonomous repair attempts")
    optimize_prompt: Optional[bool] = Field(default=True, description="Enable prompt optimization")


class BenchmarkRunRequest(BaseModel):
    task_id: Optional[str] = Field(default=None, description="Benchmark task ID, or 'all'")
    custom_prompt: Optional[str] = Field(default=None, description="Custom prompt to benchmark")
    language: str = Field(default="python")


class GatewayConfigUpdate(BaseModel):
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    demo_mode: Optional[str] = None


class VerifyRequest(BaseModel):
    answer: str = Field(..., description="Answer or factual text to verify")
    provider: Optional[str] = Field(default="chatgpt", description="Origin AI provider")


class PluginVerifyRequest(BaseModel):
    answer: str = Field(..., description="Answer or highlighted text to verify")
    provider: Optional[str] = Field(default="browser-extension")
    format: Optional[str] = Field(default="json")


class MultiVerifyRequest(BaseModel):
    topic: Optional[str] = Field(default="General Factual Verification")
    answers: Dict[str, str] = Field(..., description="Dictionary mapping provider names to answers")
