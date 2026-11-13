# Technical Specifications & System Architecture
## CodeLite AI & Stalia.AI Technical Reference

---

### 1. Technology Stack Reference

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **API Server** | FastAPI / Uvicorn | 0.110.0+ | Asynchronous REST backend & static dashboard server |
| **Language Runtime** | Python | 3.11.x | Core agent orchestration, AST parsing, and sandboxing |
| **Inference Gateway**| Maxim Bifrost | 2.4.0 | Unified LLM Gateway on `http://localhost:8080/v1` |
| **Primary LLM** | Google Gemini 3.5 Flash Lite | Latest | Fast, cost-efficient inference via Bifrost |
| **Fallback Models** | Claude 3.5 Sonnet / GPT-4o | Tier 1 | Dynamic routing targets |
| **Database** | SQLite3 | 3.x | Persistent history, telemetry metrics, and benchmark logs |
| **Frontend Core** | Vanilla JavaScript (ES6+) | Modern | Reactive dashboard controllers with zero build step |
| **Styling** | Tailwind CSS CDN | 3.4.x | Tesla/Linear engineering design system |
| **Typography** | Geist Sans & JetBrains Mono | Google Fonts | Ultra-clean developer interface typography |

---

## 2. Bifrost LLM Gateway Integration

All external LLM requests made by CodeLite AI are routed exclusively through the local Bifrost proxy:

- **Base URL**: `http://localhost:8080/v1`
- **Virtual API Key**: `sk-bf-codelite-main-key`
- **Protocol**: OpenAI-compatible chat completion format (`POST /v1/chat/completions`)
- **Telemetry Extraction**: Bifrost response metadata headers are parsed to retrieve exact prompt tokens, completion tokens, model latency, and cost calculations.

---

## 3. Database Schema (SQLite)

The database file is stored at `codelite.db` and initialized on server startup:

### 3.1 `task_history`
```sql
CREATE TABLE IF NOT EXISTS task_history (
    id TEXT PRIMARY KEY,
    prompt TEXT NOT NULL,
    task_name TEXT,
    language TEXT DEFAULT 'python',
    code TEXT,
    tests TEXT,
    status TEXT,
    total_tokens INTEGER DEFAULT 0,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    estimated_cost REAL DEFAULT 0.0,
    repair_attempts INTEGER DEFAULT 0,
    is_simulated INTEGER DEFAULT 0,
    created_at REAL
);
```

### 3.2 `verification_history`
```sql
CREATE TABLE IF NOT EXISTS verification_history (
    id TEXT PRIMARY KEY,
    provider TEXT DEFAULT 'chatgpt',
    answer_preview TEXT,
    answer_text TEXT NOT NULL,
    overall_score INTEGER,
    overall_status TEXT,
    score_explanation TEXT,
    summary_json TEXT,
    claims_json TEXT,
    created_at REAL
);
```

### 3.3 `benchmark_runs`
```sql
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
    is_simulated INTEGER DEFAULT 0,
    created_at REAL
);
```

---

## 4. REST API Endpoint Specifications

| Method | Endpoint | Description | Request Body / Parameters |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/health` | Bifrost Gateway and sandbox status | None |
| `POST` | `/api/task/run` | Execute 10-step autonomous agent loop | `{ prompt, language, complexity, enable_cache }` |
| `POST` | `/api/verify` | Stalia claim extraction & verification | `{ answer, provider, format }` |
| `POST` | `/api/verify/multi`| Multi-AI 3-way consensus studio | `{ answers: { chatgpt, claude, gemini } }` |
| `POST` | `/api/plugin/verify`| Browser extension & bookmarklet endpoint | `{ answer, provider, format }` |
| `GET` | `/api/mcp` | Model Context Protocol server manifest | None |
| `GET` | `/api/analytics` | Aggregated token savings & cost metrics | None |
| `GET` | `/api/history` | Completed coding task log | Query: `limit=50` |
| `GET` | `/api/verify/history`| Stalia factual audit logs | Query: `limit=25` |
| `POST` | `/api/config/update` | Hot-swap Bifrost model or base URL | `{ base_url, api_key, model, demo_mode }` |

---

## 5. Mathematical Scoring & Trust Algorithm

Stalia.AI uses an impact-weighted deterministic algorithm:

### 5.1 Single Claim Score
Claim Score = Base ± CoverageMod ± ConfidenceMod + AuthorityBonus

- Base:
  - `supported`: 88 (Bounded: 78–100)
  - `refuted`: 8 (Bounded: 0–18)
  - `potentially-stale`: 35 (Bounded: 18–52)
  - `needs-review`: 55 (Bounded: 38–72)
- CoverageMod: +5 for strong evidence, -5 for limited.
- ConfidenceMod: +4 for high confidence, -4 for low.
- AuthorityBonus: +2 to +8 bonus points for verified `.gov`, `.edu`, `.org`, and official vendor domains (`apple.com`, `google.com`, `github.com`).

### 5.2 Overall Composite Trust Score
Weighted Average of all individual claim scores by impact:
- High Impact: 3x
- Medium Impact: 2x
- Low Impact: 1x
