# CodeLite AI & Stalia.AI — Token-Efficient Coding Agent & Factual Verification Engine

[![Bifrost Priority Track](https://img.shields.io/badge/Bifrost%20Track-Priority%20Submission-3E6AE1?style=for-the-badge&logo=fastapi)](https://github.com/maximhq/bifrost)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Token Savings](https://img.shields.io/badge/Token%20Savings-52.5%25%20to%2084.4%25-06b6d4?style=for-the-badge)](docs/features.md)
[![Factual Grounding](https://img.shields.io/badge/Stalia.AI-Grounded%20Verification-10b981?style=for-the-badge)](docs/tech_spec.md)

> **"Code smarter, spend fewer tokens, and eliminate AI hallucinations."**  
> CodeLite AI is an autonomous, self-healing developer agent and factual grounding platform engineered specifically for the **Bifrost Priority Track**. It executes programming jobs with minimal token footprint through AST context pruning, surgical localized repairs, deterministic caching, and unified routing via the official [Maxim Bifrost LLM Gateway](https://github.com/maximhq/bifrost).

---

## 📚 Complete Project Documentation

- **[Product Requirements Document (PRD.md)](docs/PRD.md)** — Vision, personas, architecture, and success KPIs.
- **[Features & Capabilities Catalog (features.md)](docs/features.md)** — In-depth breakdown of all 9 dashboard modules.
- **[Pitch Deck & Presentation Guide (presentation_deck.md)](docs/presentation_deck.md)** — 12-slide presentation deck with speaker notes and a 2-minute live demo script.
- **[Technical Specifications (tech_spec.md)](docs/tech_spec.md)** — REST API contracts, SQLite database schema, and scoring algorithms.

---

## 🎯 The Dual Crisis in Autonomous AI Development

1. **Severe Token Bloat & Economic Inefficiency**: Standard agents dump raw codebases and repetitive conversation histories back and forth to LLMs, burning 10x–20x unnecessary tokens.
2. **Confident Hallucinations & Stale Technical Knowledge**: LLMs frequently invent non-existent APIs, reference deprecated library versions, or assert falsehoods with high confidence.

### How CodeLite AI Solves This:
- **Zero Hallucinated Metrics**: Direct extraction of prompt and completion token counts from Bifrost gateway response usage headers.
- **AST-Based Requirement Pruning**: Strips non-invoked modules and context boilerplate before execution.
- **Targeted Error Correction**: Surgically patches only failing lines without code mutilation.
- **Stalia.AI Factual Verification**: Real-time extraction of factual claims, corroborated against live official documentation with a deterministic **0–100 Trust Score**.
- **Multi-AI Consensus Studio**: Direct side-by-side comparison across ChatGPT, Claude, and Gemini with automated agreement rate metering.
- **Isolated Sandbox Execution**: Runs generated code and test suites inside a hardened process sandbox with strict memory and CPU limits.

---

## ⚡ Bifrost LLM Gateway Integration

All external LLM requests route exclusively through the **official Bifrost LLM Gateway** on port `8080`:

```
+-------------------------------------------------------------------------+
|                              CodeLite AI                                |
|  [Task Analyzer] -> [Context Optimizer] -> [Stalia Factual Verifier]   |
+------------------------------------+------------------------------------+
                                     |
                                     v (OpenAI SDK via BIFROST_BASE_URL)
             +-----------------------------------------------+
             |         Official Bifrost LLM Gateway          |
             |       (http://localhost:8080/v1)              |
             |  - Model & Provider Routing (24ms direct)     |
             |  - Observability & Tracing (x-request-id)     |
             |  - Dynamic Model Hot-Swapping                |
             |  - Unified Token Accounting                   |
             +-------+---------------+---------------+-------+
                     |               |               |
                     v               v               v
           [ Gemini Flash Lite ]  [ Claude 3.5 ]   [ GPT-4o ]
```

---

## 🏗️ 9 Core Application Modules

| # | Module | Description |
|---|--------|-------------|
| 1 | **Configure Coding Task** | Directive specification, AST preview, target runtime (Python, TS, Go, Rust), complexity calibrator, and pre-flight token load estimation. |
| 2 | **Code Workspace & Live Run** | Live telemetry bar (pass rate, tokens in/out, auto-fix cycles, cost), 3-tab code viewer (`solution.py`, `test_solution.py`, terminal), and 4-step autonomous timeline. |
| 3 | **Stalia.AI Fact Check Studio** | Question-to-assertion converter, 4 status classifications (`Verified True`, `False / Inaccurate`, `Outdated`, `Needs Checking`), and 1-click Markdown export. |
| 4 | **Multi-AI Consensus Studio** | 3-column comparative view across ChatGPT, Claude, and Gemini with agreement rate meter and discrepancy analysis. |
| 5 | **Add-ons & Integration Hub** | Interactive in-chat simulator, 1-click browser bookmarklet, Claude Desktop/Cursor MCP server (`/api/mcp`), and Custom GPT Action. |
| 6 | **Token Analytics & Cost Observability** | Empirical savings dashboard, comparison bar charts, and reduction mechanism breakdowns. |
| 7 | **Agent Benchmarks** | Head-to-head empirical evaluations comparing standard coding agents against CodeLite AI on 5 standard challenges. |
| 8 | **Task Execution History** | Comprehensive audit log of all completed coding tasks with replay inspection. |
| 9 | **Bifrost LLM Gateway Configuration** | Gateway diagnostics, health status, ping tests, and dynamic model routing without server restart. |

---

## 🔬 Empirical Benchmarks & Token Savings

| Benchmark Task | Standard Agent | CodeLite AI | Token Savings (%) | Pass Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Python Calculator** | 1,420 tokens | 340 tokens | **76.1%** | 5/5 (100%) |
| **Student Management** | 1,890 tokens | 547 tokens | **71.1%** | 100% |
| **Quicksort Algorithm** | 1,650 tokens | 410 tokens | **75.2%** | 100% |
| **Prime Sieve (Eratosthenes)** | 1,380 tokens | 320 tokens | **76.8%** | 100% |
| **Inventory System** | 2,100 tokens | 580 tokens | **72.4%** | 100% |
| **Cumulative Average** | **8,440 tokens** | **2,197 tokens** | **74.0% AVG** | **100% PASS** |

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.10+
- [Maxim Bifrost Gateway](https://github.com/maximhq/bifrost) installed or running on port 8080

### 1. Clone & Configure Environment

```bash
git clone https://github.com/your-username/codelite-ai.git
cd codelite-ai
cp .env.example .env
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Bifrost Gateway

```bash
bifrost -port 8080
```

### 4. Launch CodeLite AI

```bash
python run.py
```

Open your browser to: **`http://localhost:8082`**

---

## 📁 Repository Structure

```
codelite-ai/
├── .env.example                  # Environment configuration template
├── .gitignore                    # Excludes secrets, databases, and build artifacts
├── requirements.txt              # Production dependencies
├── Dockerfile                    # Container definition
├── docker-compose.yml            # Multi-container setup (Bifrost + CodeLite)
├── run.py                        # Server launcher (FastAPI on port 8082)
├── docs/                         # Comprehensive Product Documentation
│   ├── PRD.md                    # Product Requirements Document
│   ├── features.md               # 9-module capabilities catalog
│   ├── presentation_deck.md      # 12-slide Pitch Deck & Live Demo Script
│   └── tech_spec.md              # Technical specifications & database DDL
├── bifrost/                      # Bifrost LLM Gateway Integration
│   ├── config.py                 # Gateway configuration model
│   ├── client.py                 # OpenAI SDK wrapper for Bifrost
│   └── mock_gateway.py           # Transparent Demo Mode simulator
├── core/                         # Autonomous Agent & Verification Core
│   ├── task_analyzer.py          # Requirement deconstruction
│   ├── context_optimizer.py      # Prompt boilerplate elimination
│   ├── token_optimizer.py        # Token Optimization Engine
│   ├── code_generator.py         # Algorithm & test synthesizer
│   ├── error_detector.py         # Traceback & exception classifier
│   ├── auto_debugger.py          # Surgical localized repair engine
│   ├── test_runner.py            # Unit test execution harness
│   ├── verifier.py               # AST semantic requirement verifier
│   ├── stalia_verifier.py        # Stalia factual verification & grounding engine
│   └── agent.py                  # 10-step Autonomous Agent Orchestrator
├── sandbox/                      # Secure Execution
│   ├── security.py               # AST safety scanning
│   └── executor.py               # Docker & Process Sandbox
├── benchmarking/                 # Benchmarking Engine
│   ├── dataset.py                # 5 standard coding challenges
│   ├── history.py                # SQLite metrics database
│   └── benchmark_engine.py       # Baseline vs CodeLite comparison runner
├── api/                          # Backend API & Gateway Endpoints
│   ├── schemas.py                # Pydantic data contracts
│   ├── routes.py                 # REST & telemetry endpoints
│   └── main.py                   # FastAPI server
└── frontend/                     # Modern Engineering Dashboard
    ├── index.html                # Single-page Tesla/Linear UI
    ├── styles.css                # Custom CSS, badges, and animations
    └── app.js                    # Reactive event & chart controller
```

---

## 📄 License

MIT License. Designed and built for the **Bifrost Priority Track Hackathon**.
