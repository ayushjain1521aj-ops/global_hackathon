# Features & Capabilities Catalog
## CodeLite AI & Stalia.AI — Complete Module Breakdown

---

### Overview
CodeLite AI is built with a modular architecture comprising **9 core functional modules** accessible via the top navigation bar. Every module is styled with the **Tesla / Linear minimal engineering design language** (`#FFFFFF` background, `#3E6AE1` electric blue accent, JetBrains Mono typography, clean borders, zero visual clutter).

---

## 1. Configure Coding Task (Directive Specification)

The pre-flight control center where developers configure prompts, calibrate code structure, and preview AST token savings before launching execution.

- **Directive Specification Field**: Multi-line directive editor with pre-set template chips (`Student System`, `Calculator`, `Quicksort`, `Prime Sieve`, `Inventory`).
- **Prompt Optimizer Toggle**: Live token load estimator comparing raw baseline prompt vs. AST-pruned directive load.
- **Target Runtime Selector**:
  - `Python 3.11` (Default)
  - `TypeScript 5.3`
  - `Go 1.22`
  - `Rust 1.77`
- **Code Style / Complexity Calibrator**:
  - **Simple**: Idiomatic standard code with zero boilerplate or wrappers.
  - **Standard Typed**: Type annotations (PEP-484) and docstrings.
  - **Dataclass**: Modern declarative classes with automatic representation methods.
- **Live Syntax Preview Block**: Displays syntax-highlighted preview of the target solution structure prior to execution.
- **Inference Engine Picker**:
  - `Claude 3.5 Sonnet` (Anthropic — 24ms direct, Tier 1 precision)
  - `GPT-4o` (OpenAI — 38ms, standard high-throughput)
  - `DeepSeek Coder V2` (Edge Cluster — $0.28/1M tokens)
- **Safe Running & Auto-Fix Policy**:
  - Target file injection (`/app/solution.py` added to PYTHONPATH).
  - Isolated memory ceiling (256MB) and timeout protection.
  - Max auto-repair cycle stepper (1 to 5 cycles).
- **Pre-Flight Run Summary Card**: Real-time token load progress bar (e.g. `5.6k tokens` vs `18.4k raw`, displaying `-69% SAVINGS`).

---

## 2. Code Workspace & Live Execution

The primary execution terminal where code is generated, tested in the sandbox, auto-debugged if needed, and displayed with real-time telemetry.

- **Live Execution Telemetry Bar**:
  - **Tests Passed**: Percentage indicator and visual progress bar (e.g. `100% — Tests: 5 passed, 0 failed`).
  - **AI Tokens**: Real-time Bifrost telemetry showing exact input and output token split (e.g. `281 in / 540 out`).
  - **Auto-Fix Cycles**: Attempt counter (e.g. `0 / 5`) and execution duration in milliseconds.
  - **Estimated Cost**: Dollar amount computed using actual model pricing (e.g. `$0.0003`).
- **3-Tab Code & Terminal Viewer**:
  - `solution.py`: The synthesized, clean code output.
  - `test_solution.py`: The automated unit test suite generated to verify solution correctness.
  - `Terminal Output`: Real-time stdout/stderr sandbox execution output with exit codes.
- **Real-Time Autonomous Agent Timeline**:
  - Step 1: **Analyzer** — Task requirements deconstructed into minimal signatures.
  - Step 2: **Code Generator** — Synthesized clean code routed through Bifrost.
  - Step 3: **Sandbox Runner** — Unit test assertions executed in isolated sub-process.
  - Step 4: **Requirement Verifier** — AST symbols validated against original user prompt directives.
- **In-Workspace Code Fact Check**: One-click button (`Audit Code with Stalia`) that runs factual grounding on generated functions and docstrings.

---

## 3. Stalia.AI Fact Check Studio

A real-time factual verification and hallucination detection studio that checks claims against live official sources.

- **Dual Mode Input**: Accepts questions (e.g., *"is apple company make mobile phones"*) or assertions (e.g., *"Apple makes refrigerators"*). Automatically turns natural questions into direct factual statements.
- **AI Source Selector**: Tag the source model being checked (`ChatGPT`, `Claude`, `Gemini`, `Perplexity`, `CodeLite`).
- **Sample Presets**: Quick-load buttons for `Tech`, `Economics`, and `Space & Health`.
- **4-Level Factual Status Classification**:
  - **Verified True** (`supported`): Backed by official primary sources (Score: 78–100).
  - **False / Inaccurate** (`refuted`): Proven untrue or contradicted by facts (Score: 0–18).
  - **Outdated** (`potentially-stale`): Was true previously but superseded (Score: 18–52).
  - **Needs Checking** (`needs-review`): Broad or lacking verified references (Score: 38–72).
- **Accuracy Overview (Trust Snapshot)**:
  - Large **Score Display** (e.g. `100/100` or `17/100`).
  - Dynamic status label (`Verified True`, `Contains False Claims`, `Mostly Accurate`, `Needs Checking`).
  - **4-Box Metrics Grid**: Counts of True, False, Outdated, and Review statements.
  - **Proof Coverage**: Verified evidence percentage.
- **1-Click Filters**: Instant view toggling by `All`, `Verified True`, `False`, `Outdated`, or `Needs Checking`.
- **Export & History**:
  - `Copy Fact-Check Report`: Generates formatted Markdown report with citations.
  - `Recent Checks`: Clickable archive of recent factual verification runs.

---

## 4. Multi-AI Consensus & Corroboration Studio

Enables direct side-by-side comparison of answers generated by different leading AI models.

- **3-Model Input Deck**: Simultaneous input columns for `ChatGPT (OpenAI)`, `Claude (Anthropic)`, and `Gemini (Google)`.
- **Topic Presets**: Pre-populated examples for `AI Models & Tech` and `Interest Rates & Economy`.
- **Consensus Metrics**:
  - **AI Agreement Rate**: Bar meter showing the percentage of claims all three models agree on.
  - **Consensus Score**: Combined factual accuracy score computed across all models.
  - **AI Accuracy Leaderboard**: Ranks each AI model based on factual accuracy and freshness.
- **Discrepancy Highlighting**: Pinpoints exactly where models diverge or contradict one another.

---

## 5. Add-ons & Ecosystem Integrations

Brings Stalia factual verification into external developer workflows and browser environments.

- **Interactive In-Chat Trust Simulator**: Demonstrates how a floating trust badge appears inside ChatGPT or Claude interfaces.
- **1-Click Browser Bookmarklet**:
  - Zero-install verification tool: drag the bookmarklet button directly to the browser favorites bar.
  - Highlighting any text on Wikipedia, news sites, or AI chats and clicking the bookmarklet injects a floating verification card with live Stalia scores.
- **Model Context Protocol (MCP) Server**:
  - Serves an MCP-compliant endpoint at `GET /api/mcp`.
  - Copyable `claude_desktop_config.json` snippet for 1-click integration with Claude Desktop and Cursor.
- **OpenAI Custom GPT Action**:
  - OpenAPI 3.0 specification snippet for building a custom GPT with Stalia fact-checking capabilities.

---

## 6. Token Analytics & Cost Observability

Transparent, empirical telemetry proving CodeLite AI's token reduction efficiency.

- **4 Core Metrics Cards**:
  - Total Tokens Consumed (tracked across all agent operations).
  - Average Token Savings (typically 50%–85% over standard agents).
  - Tasks Completed (with 100% verified test pass rate).
  - Estimated Spend in USD (derived from live Bifrost rate headers).
- **Baseline vs. CodeLite Comparison Chart**: Bar chart comparing raw token consumption against CodeLite's optimized consumption.
- **Reduction Mechanisms Card**: Visual breakdown of AST pruning, state caching, and minimal specification derivation.

---

## 7. Agent Benchmarks

Head-to-head empirical evaluations comparing standard coding agents against CodeLite AI on equivalent programming tasks.

- **5 Standard Benchmark Challenges**:
  - Calculator Class (arithmetic, power, division by zero handling).
  - Student Management System (constructors, record management).
  - Quicksort Algorithm (in-place partitioning, edge cases).
  - Sieve of Eratosthenes (prime number generation, complexity limits).
  - Inventory System (stock tracking, transaction updates).
- **Run All Benchmarks Action**: Executes the complete suite with one click.
- **Persistent Benchmark History Table**: SQLite-backed history tracking token savings %, request count, and test pass rates.

---

## 8. Task Execution History

Comprehensive audit log of all completed coding tasks.

- **Table Columns**: Task Name, Programming Language, Status Badge (`SUCCESS`/`FAILED`), Token Count, Estimated Cost, Auto-Fix Attempts, Gateway Used.
- **Interactive Inspect**: Click any row to reload code, tests, and execution logs into the active workspace.

---

## 9. Bifrost LLM Gateway Configuration

The centralized AI communication layer powering CodeLite AI.

- **Live Gateway Health Diagnostics**:
  - Gateway Base URL (`http://localhost:8080/v1`).
  - Active Routed Model (`gemini/gemini-3.5-flash-lite`, `gpt-4o`, `claude-3-5-sonnet`).
  - Gateway Ping Latency (real-time millisecond timing).
  - Operational Mode (Direct Gateway Inference).
- **Dynamic Configuration Form**:
  - Update Gateway Base URL.
  - Update Bifrost Virtual API Key.
  - Switch active model router on the fly without restarting the server.
- **Live Ping Gateway Button**: Instant health-check verification.
