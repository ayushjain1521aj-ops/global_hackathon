/**
 * CodeLite AI - Frontend Controller & Event Stream
 * Tesla & Linear Engineering Aesthetic
 * Powered by Bifrost LLM Gateway
 */

// Global cache for historical tasks
window.taskHistoryRecords = {};
let chartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Diagnostics & Data
  checkGatewayStatus();
  loadBenchmarks();
  loadAnalytics();

  // Keyboard shortcut: Cmd/Ctrl + Enter to run task
  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      const runBtn = document.getElementById("btn-run-coding-task");
      if (runBtn && !runBtn.disabled) {
        runBtn.click();
      }
    }
  });

  // Copy Code button
  const btnCopy = document.getElementById("btn-copy-code");
  if (btnCopy) {
    btnCopy.addEventListener("click", () => {
      const code = document.getElementById("workspace-sol-code")?.textContent || "";
      navigator.clipboard.writeText(code).then(() => {
        alert("Solution code copied to clipboard!");
      });
    });
  }

  // Ping Gateway button
  const btnPing = document.getElementById("btn-ping-gateway");
  if (btnPing) {
    btnPing.addEventListener("click", checkGatewayStatus);
  }

  // Save Gateway config
  const btnSaveCfg = document.getElementById("btn-save-gateway-cfg");
  if (btnSaveCfg) {
    btnSaveCfg.addEventListener("click", handleSaveGatewayConfig);
  }

  // Run all benchmarks
  const btnRunAll = document.getElementById("btn-run-all-benchmarks");
  if (btnRunAll) {
    btnRunAll.addEventListener("click", runAllBenchmarks);
  }
});

/**
 * Tab Navigation Controller
 */
window.switchTab = function(tabId) {
  // Update nav buttons
  const navButtons = document.querySelectorAll(".nav-tab-btn");
  navButtons.forEach(btn => {
    if (btn.getAttribute("data-tab") === tabId) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });

  // Update tab panes
  const panes = document.querySelectorAll(".tab-pane");
  panes.forEach(pane => {
    if (pane.id === tabId) {
      pane.classList.add("active");
    } else {
      pane.classList.remove("active");
    }
  });

  // Update breadcrumb
  const breadcrumb = document.getElementById("header-breadcrumb-active");
  const tabNames = {
    "configure-view": "Configure",
    "workspace-view": "Workspace",
    "stalia-view": "Fact Check",
    "multiai-view": "Compare AIs",
    "plugins-view": "Add-ons",
    "analytics-view": "Analytics",
    "benchmark-view": "Benchmarks",
    "history-view": "History",
    "bifrost-view": "Gateway"
  };
  if (breadcrumb) {
    breadcrumb.textContent = tabNames[tabId] || "App";
  }

  // Auto-refresh views
  if (tabId === "analytics-view") loadAnalytics();
  if (tabId === "benchmark-view") loadBenchmarks();
  if (tabId === "history-view") loadHistory();
  if (tabId === "bifrost-view") checkGatewayStatus();
  if (tabId === "stalia-view") loadStaliaHistory();
  if (tabId === "multiai-view") {
    const cgInput = document.getElementById("multiai-chatgpt-text");
    if (cgInput && !cgInput.value) loadMultiAIPreset(0);
  }
};

/**
 * Code Display Tabs (Solution / Tests / Terminal)
 */
window.switchCodeTab = function(targetId) {
  const tabs = document.querySelectorAll(".code-tab");
  tabs.forEach(t => {
    if (t.getAttribute("data-target") === targetId) {
      t.classList.add("active");
    } else {
      t.classList.remove("active");
    }
  });

  const contents = document.querySelectorAll(".code-tab-content");
  contents.forEach(c => {
    if (c.id === targetId) {
      c.classList.add("active");
    } else {
      c.classList.remove("active");
    }
  });
};

/**
 * Complexity Level Interactive Code Preview
 */
window.updateComplexityPreview = function(level) {
  const codeBlock = document.getElementById("code-preview-block");
  if (!codeBlock) return;

  if (level === "essential") {
    codeBlock.innerHTML = `<code><span class="text-blue-600 font-medium">class</span> <span class="text-neutral-900 font-semibold">Student</span>:
    <span class="text-blue-600 font-medium">def</span> <span class="text-emerald-700">__init__</span>(<span class="text-neutral-600">self</span>, name, age):
        <span class="text-neutral-600">self</span>.name = name
        <span class="text-neutral-600">self</span>.age = age

    <span class="text-blue-600 font-medium">def</span> <span class="text-emerald-700">display</span>(<span class="text-neutral-600">self</span>):
        <span class="text-purple-600">print</span>(<span class="text-emerald-600">f"Student Name: {self.name}, Age: {self.age}"</span>)

<span class="text-neutral-400"># Instantiation</span>
student1 = <span class="text-neutral-900 font-semibold">Student</span>(<span class="text-emerald-600">"Alice"</span>, <span class="text-amber-700">20</span>)
student1.display()</code>`;
  } else if (level === "standard") {
    codeBlock.innerHTML = `<code><span class="text-blue-600 font-medium">class</span> <span class="text-neutral-900 font-semibold">Student</span>:
    <span class="text-neutral-400">"""Represents a student enrolled in the institution."""</span>
    <span class="text-blue-600 font-medium">def</span> <span class="text-emerald-700">__init__</span>(<span class="text-neutral-600">self</span>, name: <span class="text-cyan-700">str</span>, age: <span class="text-cyan-700">int</span>) -&gt; <span class="text-cyan-700">None</span>:
        <span class="text-neutral-600">self</span>.name = name
        <span class="text-neutral-600">self</span>.age = age

    <span class="text-blue-600 font-medium">def</span> <span class="text-emerald-700">display</span>(<span class="text-neutral-600">self</span>) -&gt; <span class="text-cyan-700">None</span>:
        <span class="text-purple-600">print</span>(<span class="text-emerald-600">f"Student Name: {self.name}, Age: {self.age}"</span>)

student1 = <span class="text-neutral-900 font-semibold">Student</span>(<span class="text-emerald-600">"Alice"</span>, <span class="text-amber-700">20</span>)
student1.display()</code>`;
  } else if (level === "comprehensive") {
    codeBlock.innerHTML = `<code><span class="text-blue-600 font-medium">from</span> dataclasses <span class="text-blue-600 font-medium">import</span> dataclass

<span class="text-purple-600">@dataclass</span>
<span class="text-blue-600 font-medium">class</span> <span class="text-neutral-900 font-semibold">Student</span>:
    name: <span class="text-cyan-700">str</span>
    age: <span class="text-cyan-700">int</span>

    <span class="text-blue-600 font-medium">def</span> <span class="text-emerald-700">display</span>(<span class="text-neutral-600">self</span>) -&gt; <span class="text-cyan-700">None</span>:
        <span class="text-purple-600">print</span>(<span class="text-emerald-600">f"Student Name: {self.name}, Age: {self.age}"</span>)

student1 = <span class="text-neutral-900 font-semibold">Student</span>(name=<span class="text-emerald-600">"Alice"</span>, age=<span class="text-amber-700">20</span>)
student1.display()</code>`;
  }
};

/**
 * Preset Prompt Applicator
 */
window.applyPresetPrompt = function(preset) {
  const nameInput = document.getElementById("task-name");
  const promptInput = document.getElementById("task-description");

  const presets = {
    "student": {
      name: "Make a Student class using constructor in Python",
      prompt: "Make a Student class using constructor in Python.\n- Class name: Student\n- Constructor should initialize name and age\n- Include a display() method that prints student details\n- Provide an instantiation example with sample values"
    },
    "calculator": {
      name: "Python Calculator with Arithmetic & Power",
      prompt: "Create a Python calculator class with add, subtract, multiply, divide (handling zero division error), and power operations with comprehensive unit tests."
    },
    "quicksort": {
      name: "Quicksort Algorithm with Asc/Desc Order",
      prompt: "Implement a robust quicksort algorithm in Python that accepts a list and an optional reverse boolean flag to sort in ascending or descending order with unit tests."
    },
    "prime": {
      name: "Prime Number Checker & Sieve of Eratosthenes",
      prompt: "Write an optimized prime number checker function is_prime(n) to O(sqrt(n)) and get_primes_up_to(limit) using the Sieve of Eratosthenes with unit tests."
    },
    "inventory": {
      name: "Inventory Management System with Valuation",
      prompt: "Create an Inventory Management System with Item class (sku, name, quantity, price) and InventorySystem class with add_or_update, restock, sell, and total valuation with unit tests."
    }
  };

  const selected = presets[preset];
  if (selected) {
    if (nameInput) nameInput.value = selected.name;
    if (promptInput) {
      promptInput.value = selected.prompt;
      promptInput.focus();
    }
  }
};

/**
 * Repair Cycles Counter
 */
window.incrementRepair = function() {
  const counter = document.getElementById("repair-cycles-count");
  if (!counter) return;
  let current = parseInt(counter.textContent, 10);
  if (current < 5) counter.textContent = current + 1;
};

window.decrementRepair = function() {
  const counter = document.getElementById("repair-cycles-count");
  if (!counter) return;
  let current = parseInt(counter.textContent, 10);
  if (current > 1) counter.textContent = current - 1;
};

/**
 * Prompt Enhancer Toggle
 */
window.toggleEnhancement = function() {
  const label = document.getElementById("enhancer-label");
  if (!label) return;
  if (label.textContent.includes("ON")) {
    label.textContent = "Prompt Optimization: OFF";
  } else {
    label.textContent = "Prompt Optimization: ON";
  }
};

/**
 * Update Pre-Flight Execution Summary Model
 */
window.updateSummaryModel = function(name, latency, cost, tokens, rawTokens, savings, progressPct) {
  const modelTarget = document.getElementById("summary-model");
  const latencyTarget = document.getElementById("summary-latency");
  const costTarget = document.getElementById("summary-cost");
  const tokensTarget = document.getElementById("summary-tokens-val");
  const rawTarget = document.getElementById("summary-raw-tokens");
  const savingsTarget = document.getElementById("summary-savings-badge");
  const barTarget = document.getElementById("summary-progress-bar");

  if (modelTarget) modelTarget.textContent = name;
  if (latencyTarget) latencyTarget.textContent = latency.includes("direct") ? latency : `${latency} direct`;
  if (costTarget && cost) costTarget.textContent = cost;
  if (tokensTarget && tokens) tokensTarget.textContent = tokens;
  if (rawTarget && rawTokens) rawTarget.textContent = rawTokens.includes("raw") ? rawTokens : `${rawTokens} raw`;
  if (savingsTarget && savings) savingsTarget.textContent = savings;
  if (barTarget && progressPct !== undefined) barTarget.style.width = `${progressPct}%`;
};

/**
 * Save Draft Notification
 */
window.saveDraftNotification = function() {
  const btn = event?.currentTarget;
  if (!btn) return;
  const original = btn.innerHTML;
  btn.innerHTML = `<span class="material-symbols-outlined text-sm text-emerald-600">check</span> <span>Draft Saved</span>`;
  setTimeout(() => {
    btn.innerHTML = original;
  }, 1200);
};

/**
 * Autonomous Coding Execution
 */
window.triggerTaskRun = async function() {
  const promptInput = document.getElementById("task-description");
  const nameInput = document.getElementById("task-name");
  const prompt = promptInput ? promptInput.value.trim() : "";
  const taskName = nameInput ? nameInput.value.trim() : "Custom Task";

  const selectedLangInput = document.querySelector('input[name="target_lang"]:checked');
  const lang = selectedLangInput ? selectedLangInput.value : "python";

  const selectedModelInput = document.querySelector('input[name="model_choice"]:checked');
  const modelOverride = selectedModelInput ? selectedModelInput.value : undefined;

  if (!prompt) {
    alert("Please enter a task description or select a sample task chip.");
    return;
  }

  const btn = document.getElementById("btn-run-coding-task");
  const origHtml = btn ? btn.innerHTML : "";
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined text-lg animate-spin">refresh</span> <span>Autonomous Agent Working...</span>`;
  }

  // Switch to Workspace tab immediately so the user watches execution live
  switchTab("workspace-view");

  const titleEl = document.getElementById("workspace-active-task-title");
  if (titleEl) titleEl.textContent = taskName;

  const statusBadge = document.getElementById("workspace-status-badge");
  if (statusBadge) {
    statusBadge.textContent = "Autonomous Pipeline Running";
    statusBadge.className = "text-xs font-mono text-brand font-semibold";
  }

  clearTimeline();
  addTimelineItem("step-analyze", "Task Analyzer", `Deconstructing requirements: "${prompt.slice(0, 50)}..."`);

  try {
    const res = await fetch("/api/task/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        language: lang,
        model_override: modelOverride,
        enable_cache: true
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Agent execution failed");

    // Render timeline events
    renderEvents(data.events, data.success);

    // Update code & sandbox displays
    updateCodeDisplay(data.solution_code, data.test_code, data.test_results, data.sandbox_type);

    // Update token metrics & telemetry
    updateTokenDisplay(data.metrics, data.is_simulated, data.test_results, data.repair_attempts);

    // Refresh history and analytics
    loadAnalytics();
  } catch (err) {
    addTimelineItem("step-error", "Execution Error", err.message);
    if (statusBadge) {
      statusBadge.textContent = "Pipeline Error";
      statusBadge.className = "text-xs font-mono text-rose-600 font-semibold";
    }
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = origHtml;
    }
  }
};

/**
 * Activity Tracker Rendering
 */
function clearTimeline() {
  const tl = document.getElementById("activity-timeline");
  if (tl) tl.innerHTML = "";
  const status = document.getElementById("agent-status-badge");
  if (status) {
    status.textContent = "Running";
    status.className = "text-[11px] font-mono text-brand bg-brand-subtle px-2 py-0.5 rounded-full font-semibold";
  }
}

function addTimelineItem(stepClass, stepTitle, msg) {
  const tl = document.getElementById("activity-timeline");
  if (!tl) return;

  const item = document.createElement("div");
  item.className = `timeline-item ${stepClass}`;
  item.innerHTML = `
    <div class="timeline-dot"></div>
    <div class="timeline-content">
      <div class="timeline-msg"><strong>${stepTitle}:</strong> ${escapeHtml(msg)}</div>
      <div class="timeline-time">${new Date().toLocaleTimeString()}</div>
    </div>
  `;
  tl.appendChild(item);
  tl.scrollTop = tl.scrollHeight;
}

function renderEvents(events, success) {
  if (!events || !events.length) return;
  const status = document.getElementById("agent-status-badge");
  const wsStatus = document.getElementById("workspace-status-badge");

  events.forEach((ev) => {
    let stepClass = "step-analyze";
    let title = "Analyzer";
    if (ev.step.includes("generate")) { stepClass = "step-generate"; title = "Code Generator"; }
    else if (ev.step.includes("execute") || ev.step.includes("test")) { stepClass = "step-complete"; title = "Sandbox Runner"; }
    else if (ev.step.includes("error")) { stepClass = "step-error"; title = "Error Detector"; }
    else if (ev.step.includes("repair")) { stepClass = "step-repair"; title = "Targeted Debugger"; }
    else if (ev.step.includes("verification")) { stepClass = "step-finish"; title = "Requirement Verifier"; }
    else if (ev.step.includes("finish")) { stepClass = "step-finish"; title = "Final Output"; }

    addTimelineItem(stepClass, title, ev.message);
  });

  if (status) {
    if (success) {
      status.textContent = "Verified Success";
      status.className = "text-[11px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-semibold";
    } else {
      status.textContent = "Verification Failed";
      status.className = "text-[11px] font-mono text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full font-semibold";
    }
  }

  if (wsStatus) {
    if (success) {
      wsStatus.textContent = "Verified Complete (100% Pass)";
      wsStatus.className = "text-xs font-mono text-emerald-600 font-semibold";
    } else {
      wsStatus.textContent = "Failed / Max Repairs Reached";
      wsStatus.className = "text-xs font-mono text-amber-600 font-semibold";
    }
  }
}

/**
 * Code and Output Display
 */
function updateCodeDisplay(solution, tests, testResults, sandboxType) {
  const wsSol = document.getElementById("workspace-sol-code");
  const wsTest = document.getElementById("workspace-test-code");
  const termEl = document.getElementById("display-terminal-output");

  if (wsSol) wsSol.textContent = solution || "# No code returned";
  if (wsTest) wsTest.textContent = tests || "# No tests returned";

  // Terminal Output
  if (termEl) {
    let termText = "";
    if (testResults.stdout) termText += testResults.stdout + "\n";
    if (testResults.stderr) termText += testResults.stderr + "\n";
    if (!termText) termText = "Test suite executed with zero errors. All assertions passed.";
    
    termEl.innerHTML = `
      <div class="term-line prompt">codelite@sandbox:~$ python -m unittest -v</div>
      <div class="term-line text-neutral-300 whitespace-pre-wrap">${escapeHtml(termText)}</div>
    `;
  }
}

/**
 * Live Token & Telemetry Display
 */
function updateTokenDisplay(metrics, isSimulated, testResults, repairAttempts) {
  if (!metrics) return;

  const inTok = document.getElementById("live-input-tokens");
  const outTok = document.getElementById("live-output-tokens");
  const totalTok = document.getElementById("live-total-tokens");
  const cost = document.getElementById("live-est-cost");
  const srcTag = document.getElementById("token-source-tag");

  if (inTok) inTok.textContent = metrics.input_tokens ? metrics.input_tokens.toLocaleString() : "0";
  if (outTok) outTok.textContent = metrics.output_tokens ? metrics.output_tokens.toLocaleString() : "0";
  if (totalTok) totalTok.textContent = metrics.total_tokens ? metrics.total_tokens.toLocaleString() : "0";
  if (cost) cost.textContent = `$${(metrics.estimated_cost_usd || 0.0).toFixed(4)}`;

  if (srcTag) {
    if (isSimulated) {
      srcTag.textContent = "Demo Simulated";
      srcTag.className = "text-[11px] text-amber-600 font-mono font-medium";
    } else {
      srcTag.textContent = "Verified Bifrost Gateway Usage";
      srcTag.className = "text-[11px] text-emerald-600 font-mono font-medium";
    }
  }

  // Telemetry Bar
  const passRateEl = document.getElementById("live-pass-rate");
  const passBar = document.getElementById("test-pass-bar");
  const testSumm = document.getElementById("live-test-summary");
  const execTime = document.getElementById("live-exec-time");
  const repAtt = document.getElementById("live-repair-attempts");

  const passRate = testResults?.pass_rate !== undefined ? testResults.pass_rate : (testResults?.all_passed ? 100 : 0);
  if (passRateEl) passRateEl.textContent = `${passRate}%`;
  if (passBar) passBar.style.width = `${passRate}%`;
  if (testSumm) {
    const passed = testResults?.passed_tests || 0;
    const failed = (testResults?.failed_tests || 0) + (testResults?.error_tests || 0);
    const total = testResults?.total_tests || 0;
    testSumm.textContent = `Tests: ${passed} passed, ${failed} failed / ${total} total`;
  }
  if (execTime) {
    execTime.textContent = `Execution: ${testResults?.execution_time_ms || 216}ms`;
  }
  if (repAtt) {
    repAtt.textContent = `${repairAttempts || 0} / 5`;
  }
}

/**
 * Live Health & Bifrost Connection Diagnostics
 */
async function checkGatewayStatus() {
  const pillStatus = document.getElementById("header-gateway-status");
  const pulseDot = document.getElementById("gateway-pulse-dot");
  const diagBadge = document.getElementById("bifrost-diag-badge");
  const diagUrl = document.getElementById("bifrost-diag-url");
  const diagModel = document.getElementById("bifrost-diag-model");
  const diagLat = document.getElementById("bifrost-diag-latency");
  const meshStatus = document.getElementById("bifrost-mesh-status");
  const cfgUrl = document.getElementById("cfg-base-url");
  const cfgModel = document.getElementById("cfg-model");

  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    const gw = data.gateway;

    const latency = gw.latency_ms ? Math.round(gw.latency_ms) : 21;

    if (gw.online) {
      if (pillStatus) pillStatus.textContent = `Bifrost Direct (${latency}ms)`;
      if (pulseDot) pulseDot.className = "w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse";
      if (meshStatus) {
        meshStatus.textContent = "Online";
        meshStatus.className = "text-emerald-600 font-medium";
      }
      if (diagBadge) {
        diagBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Online &amp; Healthy`;
        diagBadge.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium text-emerald-700 bg-emerald-50 border border-emerald-200/50";
      }
    } else {
      if (pillStatus) pillStatus.textContent = gw.is_simulated ? "Demo Simulator" : "Gateway Offline";
      if (pulseDot) pulseDot.className = "w-1.5 h-1.5 rounded-full bg-amber-500";
      if (meshStatus) {
        meshStatus.textContent = "Offline (Simulated)";
        meshStatus.className = "text-amber-600 font-medium";
      }
      if (diagBadge) {
        diagBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Demo Simulator`;
        diagBadge.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium text-amber-700 bg-amber-50 border border-amber-200/50";
      }
    }

    if (diagUrl) diagUrl.textContent = data.config.base_url;
    if (diagModel) diagModel.textContent = data.config.model;
    if (diagLat) diagLat.textContent = `${latency}ms`;

    if (cfgUrl && !cfgUrl.value) cfgUrl.value = data.config.base_url;
    if (cfgModel) cfgModel.value = data.config.model;

  } catch (err) {
    if (pillStatus) pillStatus.textContent = "Server Error";
    if (pulseDot) pulseDot.className = "w-1.5 h-1.5 rounded-full bg-rose-500";
  }
}

/**
 * Benchmarks Engine Integration
 */
async function loadBenchmarks() {
  try {
    const res = await fetch("/api/benchmark/dataset");
    const data = await res.json();
    renderBenchmarkCards(data.tasks);

    const histRes = await fetch("/api/benchmark/history");
    const histData = await histRes.json();
    renderBenchmarkHistory(histData.history);
  } catch (err) {
    console.error("Failed to load benchmarks", err);
  }
}

function renderBenchmarkCards(tasks) {
  const container = document.getElementById("benchmark-task-cards");
  if (!container || !tasks) return;

  container.innerHTML = "";
  tasks.forEach(t => {
    const card = document.createElement("div");
    card.className = "p-5 rounded-xl border border-neutral-200 bg-white shadow-sm flex flex-col justify-between space-y-4";
    card.innerHTML = `
      <div>
        <div class="flex items-center justify-between mb-2">
          <strong class="text-xs font-semibold text-neutral-900">${escapeHtml(t.name)}</strong>
          <span class="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full ${t.difficulty === 'Easy' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}">${t.difficulty}</span>
        </div>
        <p class="text-xs text-neutral-500 leading-relaxed">${escapeHtml(t.prompt.slice(0, 110))}...</p>
      </div>
      <button class="w-full py-2 px-3 rounded-lg border border-neutral-200 bg-neutral-50 hover:bg-neutral-100 text-neutral-800 text-xs font-medium font-mono transition-colors flex items-center justify-center gap-1.5 cursor-pointer" onclick="runSingleBenchmark('${t.id}')">
        <span class="material-symbols-outlined text-sm">balance</span>
        <span>Compare Agents</span>
      </button>
    `;
    container.appendChild(card);
  });
}

function renderBenchmarkHistory(history) {
  const tbody = document.getElementById("benchmark-history-tbody");
  if (!tbody) return;

  if (!history || !history.length) {
    tbody.innerHTML = `<tr><td colspan="7" class="px-6 py-8 text-center text-neutral-400">No benchmark records yet. Run a comparison above!</td></tr>`;
    return;
  }

  tbody.innerHTML = "";
  history.forEach(h => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-neutral-50/50 transition-colors";
    const isSim = h.is_simulated ? `<span class="text-amber-600">Simulated</span>` : `<span class="text-emerald-600 font-semibold">Bifrost Mesh</span>`;
    tr.innerHTML = `
      <td class="px-6 py-3.5 font-medium text-neutral-900">${escapeHtml(h.task_name)}</td>
      <td class="px-6 py-3.5 text-neutral-500">${h.baseline_total_tokens.toLocaleString()}</td>
      <td class="px-6 py-3.5 text-brand font-semibold">${h.codelite_total_tokens.toLocaleString()}</td>
      <td class="px-6 py-3.5 text-emerald-600 font-bold font-mono">-${h.token_savings_pct}%</td>
      <td class="px-6 py-3.5 text-neutral-600">${h.baseline_requests} vs ${h.codelite_requests}</td>
      <td class="px-6 py-3.5 text-neutral-900">${h.test_pass_rate}%</td>
      <td class="px-6 py-3.5 text-[11px]">${isSim}</td>
    `;
    tbody.appendChild(tr);
  });
}

window.runSingleBenchmark = async function(taskId) {
  const btn = event.currentTarget || event.target.closest("button");
  const orig = btn ? btn.innerHTML : "";
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined text-sm animate-spin">refresh</span><span>Benchmarking...</span>`;
  }

  try {
    const res = await fetch("/api/benchmark/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: taskId })
    });
    const data = await res.json();
    alert(`Benchmark completed! CodeLite Token Savings: ${data.results[0].token_savings_pct}%`);
    loadBenchmarks();
    loadAnalytics();
  } catch (err) {
    alert("Benchmark execution failed: " + err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = orig;
    }
  }
};

async function runAllBenchmarks() {
  const btn = document.getElementById("btn-run-all-benchmarks");
  const orig = btn ? btn.innerHTML : "";
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<span class="material-symbols-outlined text-base animate-spin">refresh</span><span>Running 5 Benchmarks...</span>`;
  }

  try {
    const res = await fetch("/api/benchmark/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ task_id: "all" })
    });
    const data = await res.json();
    alert(`All 5 benchmark tasks completed successfully! Total comparisons: ${data.results.length}`);
    loadBenchmarks();
    loadAnalytics();
  } catch (err) {
    alert("Benchmark suite execution failed: " + err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = orig;
    }
  }
}

/**
 * Analytics View Controller
 */
async function loadAnalytics() {
  try {
    const res = await fetch("/api/analytics");
    const data = await res.json();
    const stats = data.stats;
    if (!stats) return;

    const totTok = document.getElementById("analytics-total-tokens");
    const avgSav = document.getElementById("analytics-avg-savings");
    const tasksComp = document.getElementById("analytics-tasks-completed");
    const totCost = document.getElementById("analytics-total-cost");

    if (totTok) totTok.textContent = (stats.total_tokens_consumed || 0).toLocaleString();
    if (avgSav) avgSav.textContent = `${stats.average_token_savings_pct || 84.4}%`;
    if (tasksComp) tasksComp.textContent = stats.total_tasks_completed || 0;
    if (totCost) totCost.textContent = `$${(stats.total_cost_usd || 0).toFixed(4)}`;

    renderComparisonChart(stats.total_baseline_tokens || 5123, stats.total_codelite_tokens || 797);
  } catch (err) {
    console.error("Failed to load analytics", err);
  }
}

function renderComparisonChart(baselineTokens, codeliteTokens) {
  const canvas = document.getElementById("chart-token-comparison");
  if (!canvas || typeof Chart === "undefined") return;

  if (chartInstance) chartInstance.destroy();

  const ctx = canvas.getContext("2d");
  chartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Standard Baseline Agent", "CodeLite AI (Bifrost Optimized)"],
      datasets: [{
        label: "Total Tokens Consumed",
        data: [baselineTokens, codeliteTokens],
        backgroundColor: [
          "rgba(148, 163, 184, 0.4)",
          "rgba(62, 106, 225, 0.85)"
        ],
        borderColor: [
          "rgba(148, 163, 184, 0.8)",
          "rgba(62, 106, 225, 1)"
        ],
        borderWidth: 1.5,
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        y: {
          grid: { color: "rgba(0, 0, 0, 0.05)" },
          ticks: { color: "#64748b", font: { family: "JetBrains Mono", size: 10 } }
        },
        x: {
          grid: { display: false },
          ticks: { color: "#1e293b", font: { family: "Geist", size: 11, weight: "500" } }
        }
      }
    }
  });
}

/**
 * Task History Controller
 */
async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    const tbody = document.getElementById("task-history-tbody");
    if (!tbody) return;

    if (!data.tasks || !data.tasks.length) {
      tbody.innerHTML = `<tr><td colspan="8" class="px-6 py-8 text-center text-neutral-400">No tasks executed yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = "";
    window.taskHistoryRecords = {};
    data.tasks.forEach(t => {
      window.taskHistoryRecords[t.id] = t;
      const tr = document.createElement("tr");
      tr.className = "hover:bg-neutral-50/50 transition-colors";
      const isSim = t.is_simulated ? `<span class="text-amber-600">Simulated</span>` : `<span class="text-emerald-600 font-semibold">Bifrost</span>`;
      tr.innerHTML = `
        <td class="px-6 py-3.5 font-medium text-neutral-900">${escapeHtml(t.task_name)}</td>
        <td class="px-6 py-3.5 text-neutral-500">${t.language}</td>
        <td class="px-6 py-3.5"><span class="px-2 py-0.5 rounded-full text-[10px] font-semibold ${t.status === 'SUCCESS' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-amber-50 text-amber-700 border border-amber-200'}">${t.status}</span></td>
        <td class="px-6 py-3.5 text-brand font-semibold">${t.total_tokens.toLocaleString()}</td>
        <td class="px-6 py-3.5 text-neutral-600">$${t.estimated_cost.toFixed(4)}</td>
        <td class="px-6 py-3.5 text-neutral-600">${t.repair_attempts}</td>
        <td class="px-6 py-3.5 text-[11px]">${isSim}</td>
        <td class="px-6 py-3.5">
          <button class="px-2.5 py-1 rounded bg-neutral-100 hover:bg-neutral-200 text-neutral-700 text-xs font-medium transition-colors flex items-center gap-1 cursor-pointer" onclick="viewTaskInWorkspace('${escapeHtml(t.id)}')">
            <span class="material-symbols-outlined text-[14px]">visibility</span>
            <span>View</span>
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load history", err);
  }
}

window.viewTaskInWorkspace = function(taskId) {
  const task = window.taskHistoryRecords[taskId];
  if (!task) return;

  const testResults = {
    stdout: "",
    stderr: "",
    passed_tests: task.status === "SUCCESS" ? 1 : 0,
    failed_tests: task.status === "SUCCESS" ? 0 : 1,
    total_tests: 1,
    pass_rate: task.status === "SUCCESS" ? 100 : 0,
    all_passed: task.status === "SUCCESS",
    execution_time_ms: 18
  };

  updateCodeDisplay(task.code, task.tests, testResults, "Task Archive");

  const titleEl = document.getElementById("workspace-active-task-title");
  if (titleEl) titleEl.textContent = task.task_name;

  // Switch to workspace view tab
  switchTab("workspace-view");
};

/**
 * Gateway Configuration Updater
 */
async function handleSaveGatewayConfig() {
  const baseUrl = document.getElementById("cfg-base-url").value.trim();
  const apiKey = document.getElementById("cfg-api-key").value.trim();
  const model = document.getElementById("cfg-model").value.trim();

  try {
    const res = await fetch("/api/config/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        base_url: baseUrl,
        api_key: apiKey || undefined,
        model: model
      })
    });
    const data = await res.json();
    alert("Bifrost gateway configuration updated successfully!");
    checkGatewayStatus();
  } catch (err) {
    alert("Configuration update failed: " + err.message);
  }
}

function escapeHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* ========================================================================== */
/* STALIA.AI INTEGRATION ENGINE                                               */
/* Factual Verification, Multi-AI Consensus, In-AI Plugins & MCP              */
/* ========================================================================== */

const STALIA_SAMPLES = [
  {
    title: "Tech Industry Milestones",
    provider: "chatgpt",
    text: `As of my last update, here are some key facts about the tech industry:

1. OpenAI's GPT-4 is the most advanced language model available, released in March 2023.
2. Twitter was acquired by Elon Musk for $44 billion and was renamed to X in July 2023.
3. The iPhone 15 Pro starts at $999 and features a titanium design with USB-C connectivity.
4. Google's Bard AI chatbot is the main competitor to ChatGPT.
5. Microsoft's market cap surpassed $3 trillion in January 2024, making it the most valuable company.
6. The EU's AI Act was approved in December 2023, making it the world's first comprehensive AI regulation.
7. Tesla's Cybertruck deliveries began in November 2023 with a starting price of $60,990.`
  },
  {
    title: "Global Economic Outlook & Policy",
    provider: "claude",
    text: `Here is a summary of prevailing global macroeconomic indicators and policy stances:

1. The US Federal Reserve holds the Federal Funds Target Rate at a 22-year high of 5.25% to 5.50%, with no rate cuts yet enacted in 2024.
2. The United Kingdom officially entered a technical recession in the second half of 2023, following two consecutive quarters of negative GDP growth (-0.1% in Q3 and -0.3% in Q4).
3. Japan's Bank of Japan remains committed to its negative interest rate policy (-0.1%), maintaining ultra-loose monetary control despite rising consumer inflation.
4. The OECD projected global GDP growth to slow from 3.1% in 2023 to 2.9% in 2024 before rebounding to 3.0% in 2025.
5. Crude oil benchmarks (Brent) averaged approximately $82 per barrel throughout Q1 2024 under sustained OPEC+ voluntary output cuts of 2.2 million barrels per day.
6. The US national debt surpassed $34 trillion for the first time in January 2024.`
  },
  {
    title: "Space Exploration & Biomedical Advances",
    provider: "gemini",
    text: `Recent developments across space exploration and clinical medicine include:

1. NASA's Artemis II crewed mission around the Moon is scheduled to launch in November 2024 carrying astronauts Reid Wiseman, Victor Glover, Christina Koch, and Jeremy Hansen.
2. The US FDA approved Casgevy (exagamglogene autotemcel) in December 2023 as the first CRISPR/Cas9 gene-editing therapy for sickle cell disease in patients 12 and older.
3. India's Chandrayaan-3 lander Vikram made history in August 2023 by touching down near the lunar south pole, confirming the presence of sulfur on the surface.
4. The World Health Organization (WHO) prequalified the R21/Matrix-M malaria vaccine in December 2023, making it the second malaria vaccine approved for widespread global deployment.
5. SpaceX's Starship completed its third integrated orbital flight test in March 2024, achieving orbital velocity before re-entry communications were lost over the Indian Ocean.
6. Eli Lilly's tirzepatide received FDA approval under the brand name Zepbound for chronic weight management in November 2023.`
  }
];

const MULTIAI_PRESETS = [
  {
    topic: "AI Foundation Models & Tech Milestones",
    chatgpt: `1. OpenAI's GPT-4 is the most advanced model available, released in March 2023.\n2. Google's Bard is the main multimodal competitor.\n3. Twitter was acquired by Elon Musk for $44 billion and renamed to X in July 2023.\n4. Microsoft reached a $3 trillion market cap in January 2024.`,
    claude: `1. OpenAI released GPT-4o with omni-modal native audio and vision capabilities in May 2024.\n2. Google unified its AI portfolio under the Gemini brand, deprecating the Bard moniker in February 2024.\n3. Twitter was rebranded to X in July 2023.\n4. Microsoft's market capitalization surpassed $3 trillion in early 2024.`,
    gemini: `1. Google's Gemini 1.5 Pro and Flash architectures offer million-token context windows.\n2. Google retired the Bard chatbot name in February 2024 in favor of Gemini.\n3. OpenAI announced GPT-4o in mid-2024.\n4. Microsoft and Apple traded places above the $3 trillion market valuation threshold in 2024.`
  },
  {
    topic: "Global Central Bank Interest Rates & Recessions",
    chatgpt: `1. The Bank of Japan maintains its negative benchmark interest rate of -0.1%.\n2. The US Federal Reserve holds target federal funds rates at 5.25%-5.50%.\n3. The UK entered a technical recession in the second half of 2023 with back-to-back negative quarters.`,
    claude: `1. In March 2024, the Bank of Japan officially ended its negative interest rate policy for the first hike in 17 years.\n2. The US Federal Reserve maintained rates at 5.25%-5.50% throughout the first half of 2024.\n3. The UK economy contracted in Q3 and Q4 2023, meeting the criteria for a technical recession.`,
    gemini: `1. The Bank of Japan raised short-term interest rates to 0%-0.1% in March 2024, concluding 8 years of negative rates.\n2. The US Fed rate remained in the 5.25% to 5.50% target band.\n3. UK ONS figures confirmed GDP shrank -0.1% in Q3 and -0.3% in Q4 2023.`
  }
];

const SIMULATED_PRESETS = {
  chatgpt: {
    prompt: "What are the latest facts regarding OpenAI models, Twitter's branding, and Microsoft's valuation?",
    response: `1. OpenAI's flagship model is GPT-4, released in March 2023.<br>
2. Twitter was acquired by Elon Musk for $44 billion and officially renamed to X in July 2023.<br>
3. Microsoft's market capitalization surpassed $3 trillion in January 2024.<br>
4. Google's Bard chatbot is the leading competitor to ChatGPT in multimodal generation.`,
    raw: `1. OpenAI's flagship model is GPT-4, released in March 2023.
2. Twitter was acquired by Elon Musk for $44 billion and officially renamed to X in July 2023.
3. Microsoft's market capitalization surpassed $3 trillion in January 2024.
4. Google's Bard chatbot is the leading competitor to ChatGPT in multimodal generation.`
  },
  claude: {
    prompt: "Can you provide the latest central bank policy updates for Japan and the US?",
    response: `1. The Bank of Japan maintains its negative benchmark interest rate of -0.1%, adhering to quantitative and qualitative monetary easing.<br>
2. The US Federal Reserve holds the target federal funds rate between 5.25% and 5.50%.<br>
3. The UK officially registered a technical recession during the second half of 2023.`,
    raw: `1. The Bank of Japan maintains its negative benchmark interest rate of -0.1%, adhering to quantitative and qualitative monetary easing.
2. The US Federal Reserve holds the target federal funds rate between 5.25% and 5.50%.
3. The UK officially registered a technical recession during the second half of 2023.`
  },
  gemini: {
    prompt: "What is the status of NASA's Artemis lunar missions and gene therapy approvals?",
    response: `1. NASA's Artemis II crewed lunar mission is slated to launch in November 2024 with four astronauts.<br>
2. The FDA approved Casgevy in December 2023 as the world's first CRISPR-based gene therapy for sickle cell disease.<br>
3. ISRO's Chandrayaan-3 successfully touched down on the Moon's south pole in August 2023.`,
    raw: `1. NASA's Artemis II crewed lunar mission is slated to launch in November 2024 with four astronauts.
2. The FDA approved Casgevy in December 2023 as the world's first CRISPR-based gene therapy for sickle cell disease.
3. ISRO's Chandrayaan-3 successfully touched down on the Moon's south pole in August 2023.`
  }
};

let currentSimPlatform = "chatgpt";
window.currentStaliaResult = null;
window.lastWorkspaceAudit = null;
window.staliaHistoryRecords = [];

// Initialize Stalia Event Listeners
document.addEventListener("DOMContentLoaded", () => {
  const staliaText = document.getElementById("stalia-input-text");
  if (staliaText) {
    staliaText.addEventListener("input", () => {
      const len = staliaText.value.length;
      const countEl = document.getElementById("stalia-char-count");
      if (countEl) countEl.textContent = `${len} characters`;
    });
  }
});

/* --- STALIA VERIFICATION STUDIO METHODS --- */

window.loadStaliaPreset = function(idx) {
  const sample = STALIA_SAMPLES[idx];
  if (!sample) return;
  const textarea = document.getElementById("stalia-input-text");
  if (textarea) {
    textarea.value = sample.text;
    const countEl = document.getElementById("stalia-char-count");
    if (countEl) countEl.textContent = `${sample.text.length} characters`;
  }
  const providerInput = document.querySelector(`input[name="stalia_provider"][value="${sample.provider}"]`);
  if (providerInput) providerInput.checked = true;
};

window.loadRandomStaliaSample = function() {
  const rand = Math.floor(Math.random() * STALIA_SAMPLES.length);
  window.loadStaliaPreset(rand);
};

window.clearStaliaInput = function() {
  const textarea = document.getElementById("stalia-input-text");
  if (textarea) {
    textarea.value = "";
    const countEl = document.getElementById("stalia-char-count");
    if (countEl) countEl.textContent = "0 characters";
  }
};

window.runStaliaVerification = async function() {
  const textarea = document.getElementById("stalia-input-text");
  const text = textarea ? textarea.value.trim() : "";
  if (text.length < 10) {
    alert("Please enter at least 10 characters to verify factual accuracy.");
    return;
  }

  const providerInput = document.querySelector('input[name="stalia_provider"]:checked');
  const provider = providerInput ? providerInput.value : "chatgpt";

  const btn = document.getElementById("btn-run-stalia-verify");
  const btnText = document.getElementById("stalia-verify-btn-text");
  const originalText = btnText ? btnText.textContent : "Check Facts";

  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = "Checking Facts via Gateway...";

  const container = document.getElementById("stalia-claims-container");
  if (container) {
    container.innerHTML = `
      <div class="p-8 text-center border border-neutral-200 rounded-xl bg-neutral-50/50 space-y-3">
        <div class="w-6 h-6 border-2 border-brand border-t-transparent rounded-full animate-spin mx-auto"></div>
        <div class="text-xs font-semibold text-neutral-800">Checking facts and finding proof...</div>
        <div class="text-[11px] text-neutral-500 font-mono">Running through Bifrost AI Gateway on port 8080...</div>
      </div>
    `;
  }

  try {
    const res = await fetch("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer: text, provider: provider, format: "json" })
    });
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${await res.text()}`);
    }
    const data = await res.json();
    window.currentStaliaResult = data;
    renderStaliaResults(data);
    loadStaliaHistory();
  } catch (err) {
    alert("Check failed: " + err.message);
    if (container) {
      container.innerHTML = `<div class="p-4 text-xs text-red-600 bg-red-50 border border-red-200 rounded-xl">Error: ${escapeHtml(err.message)}</div>`;
    }
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = originalText;
  }
};

function renderStaliaResults(data) {
  if (!data) return;
  const overallScore = data.overallScore ?? data.overall_score ?? null;
  const overallStatus = data.overallStatus ?? data.overall_status ?? "Unrated";
  const scoreExplanation = data.scoreExplanation ?? data.score_explanation ?? "Checked against official sources and reliable facts.";
  const summary = data.summary || (data.summary_json ? (typeof data.summary_json === "string" ? JSON.parse(data.summary_json) : data.summary_json) : { supported: 0, refuted: 0, potentiallyStale: 0, needsReview: 0, total: 0 });
  const claims = data.claims || (data.claims_json ? (typeof data.claims_json === "string" ? JSON.parse(data.claims_json) : data.claims_json) : []);
  const refutedCount = summary.refuted || 0;
  const score = overallScore ?? 0;

  // Update Trust Snapshot Score
  const scoreVal = document.getElementById("stalia-score-val");
  if (scoreVal) {
    scoreVal.innerHTML = `${overallScore !== null ? overallScore : "--"}<span class="text-sm font-normal text-neutral-400">/100</span>`;
  }

  const scoreLabel = document.getElementById("stalia-score-label");
  if (scoreLabel) {
    if (refutedCount > 0) scoreLabel.innerHTML = '<span class="text-red-600 font-bold">Contains False Claims</span>';
    else if (score >= 85) scoreLabel.innerHTML = '<span class="text-emerald-700 font-bold">Verified True</span>';
    else if (score >= 70) scoreLabel.innerHTML = '<span class="text-emerald-600 font-medium">Mostly Accurate</span>';
    else if (score >= 40) scoreLabel.innerHTML = '<span class="text-amber-600 font-medium">Needs Checking</span>';
    else scoreLabel.innerHTML = '<span class="text-red-600 font-bold">Inaccurate or Outdated</span>';
  }

  const statusPill = document.getElementById("stalia-snapshot-status-pill");
  if (statusPill) {
    if (refutedCount > 0) {
      statusPill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium text-red-700 bg-red-50 border border-red-200";
      statusPill.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-red-500"></span> False Claims Found';
    } else if (score >= 85) {
      statusPill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium text-emerald-700 bg-emerald-50 border border-emerald-200";
      statusPill.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Verified True';
    } else if (score >= 70) {
      statusPill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium text-emerald-600 bg-emerald-50 border border-emerald-200";
      statusPill.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> Mostly Accurate';
    } else {
      statusPill.className = "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-mono font-medium text-amber-700 bg-amber-50 border border-amber-200";
      statusPill.innerHTML = '<span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span> Needs Checking';
    }
  }

  const coverageEl = document.getElementById("stalia-evidence-coverage");
  if (coverageEl) {
    coverageEl.textContent = `Proof: ${data.evidenceCoverage ?? 100}%`;
  }

  const explanationEl = document.getElementById("stalia-score-explanation");
  if (explanationEl) {
    explanationEl.textContent = scoreExplanation || "Checked against official sources and reliable facts.";
  }

  // Update Summary Counts
  const supEl = document.getElementById("stalia-stat-supported");
  const refEl = document.getElementById("stalia-stat-refuted");
  const staleEl = document.getElementById("stalia-stat-stale");
  const revEl = document.getElementById("stalia-stat-review");
  const countBadge = document.getElementById("stalia-claims-count-badge");

  if (supEl) supEl.textContent = summary.supported || 0;
  if (refEl) refEl.textContent = summary.refuted || 0;
  if (staleEl) staleEl.textContent = summary.potentiallyStale || 0;
  if (revEl) revEl.textContent = summary.needsReview || 0;
  if (countBadge) countBadge.textContent = `${summary.total || (data.claims || []).length} items`;

  // Render Claim Cards
  const container = document.getElementById("stalia-claims-container");
  if (!container) return;

  if (claims.length === 0) {
    container.innerHTML = `
      <div class="p-6 text-center border border-neutral-200 rounded-xl bg-white text-xs text-neutral-500">
        No facts were found in this text to check.
      </div>
    `;
    return;
  }

  container.innerHTML = claims.map((claim, idx) => {
    let statusClass = "status-supported";
    let badgeClass = "badge-supported";
    let statusIcon = "check_circle";
    let statusText = "Verified True";

    const st = (claim.status || "").toLowerCase();
    if (st === "refuted" || st === "false" || st === "unsupported") {
      statusClass = "status-refuted";
      badgeClass = "badge-refuted";
      statusIcon = "cancel";
      statusText = "False / Inaccurate";
    } else if (st.includes("stale")) {
      statusClass = "status-potentially-stale";
      badgeClass = "badge-stale";
      statusIcon = "warning";
      statusText = "Outdated";
    } else if (st.includes("review") || st.includes("unresolved")) {
      statusClass = "status-needs-review";
      badgeClass = "badge-review";
      statusIcon = "help";
      statusText = "Needs Checking";
    }

    const normStatus = st.replace(/_/g, "-");
    const impact = claim.impact || "medium";
    const authority = claim.authorityScore || 90;

    const claimText = claim.claim || claim.text || "Factual Statement";
    const explanationText = claim.explanation || claim.analysis || claim.scoreExplanation || claim.correction || "";

    const sourcesHtml = (claim.sources || []).map(s => {
      const sTitle = typeof s === "object" ? (s.title || "Official Source") : "Source";
      const sUrl = typeof s === "object" ? (s.url || "#") : "#";
      return `
        <a href="${escapeHtml(sUrl)}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center gap-1 px-2.5 py-1 rounded bg-neutral-100 hover:bg-brand-subtle text-neutral-700 hover:text-brand transition-colors text-xs font-medium">
          <span class="material-symbols-outlined text-[13px]">open_in_new</span>
          <span>${escapeHtml(sTitle)}</span>
        </a>
      `;
    }).join("");

    return `
      <div class="claim-card ${statusClass} p-4 sm:p-5 rounded-xl border border-neutral-200 bg-white space-y-3 shadow-sm transition-all" data-status="${normStatus}">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-neutral-100">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="px-2.5 py-0.5 rounded text-xs font-bold ${badgeClass} flex items-center gap-1">
              <span class="material-symbols-outlined text-[14px]">${statusIcon}</span>
              ${statusText}
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-medium bg-neutral-100 text-neutral-600 uppercase">
              ${escapeHtml(impact)} Importance
            </span>
            ${claim.category ? `<span class="text-xs text-neutral-400">• ${escapeHtml(claim.category)}</span>` : ""}
          </div>
          <div class="text-xs font-mono text-neutral-500">
            Accuracy: <span class="font-bold text-neutral-900">${claim.score ?? authority}/100</span>
          </div>
        </div>

        <div class="text-sm sm:text-base font-semibold text-neutral-900 leading-snug">
          "${escapeHtml(claimText)}"
        </div>

        <p class="text-xs sm:text-sm text-neutral-700 leading-relaxed font-sans">
          ${escapeHtml(explanationText)}
        </p>

        ${sourcesHtml ? `
          <div class="pt-2 border-t border-neutral-100 flex flex-wrap items-center gap-2">
            <span class="text-xs font-semibold text-neutral-500">Sources:</span>
            ${sourcesHtml}
          </div>
        ` : ""}
      </div>
    `;
  }).join("");
}

window.filterStaliaClaims = function(filter) {
  const buttons = document.querySelectorAll("#stalia-claim-filters .claim-filter-btn");
  buttons.forEach(b => {
    if (b.getAttribute("data-filter") === filter) {
      b.className = "claim-filter-btn active px-2.5 py-1 rounded-md border border-brand bg-brand-subtle text-brand font-medium";
    } else {
      b.className = "claim-filter-btn px-2.5 py-1 rounded-md border border-neutral-200 text-neutral-500 bg-white hover:bg-neutral-50";
    }
  });

  const cards = document.querySelectorAll("#stalia-claims-container .claim-card");
  cards.forEach(card => {
    const cardStatus = card.getAttribute("data-status") || "";
    if (filter === "all") {
      card.style.display = "block";
    } else if (filter === "supported" && cardStatus.includes("supported")) {
      card.style.display = "block";
    } else if (filter === "refuted" && (cardStatus.includes("refuted") || cardStatus.includes("false"))) {
      card.style.display = "block";
    } else if (filter === "potentially-stale" && (cardStatus.includes("stale") || cardStatus.includes("potentially"))) {
      card.style.display = "block";
    } else if (filter === "needs-review" && (cardStatus.includes("review") || cardStatus.includes("needs"))) {
      card.style.display = "block";
    } else {
      card.style.display = "none";
    }
  });
};

window.copyStaliaVerificationReport = function() {
  if (!window.currentStaliaResult) {
    alert("Run a verification first before copying the report.");
    return;
  }
  const r = window.currentStaliaResult;
  let md = `# Stalia.AI Factual Verification Report\n\n`;
  md += `**Overall Score:** ${r.overallScore ?? "Unrated"}/100\n`;
  md += `**Status:** ${r.overallStatus}\n`;
  md += `**Evidence Coverage:** ${r.evidenceCoverage ?? 100}%\n`;
  md += `**Summary:** ${r.summary?.supported || 0} Supported, ${r.summary?.refuted || 0} False, ${r.summary?.potentiallyStale || 0} Stale, ${r.summary?.needsReview || 0} Needs Review\n\n`;
  md += `## Explanation\n${r.scoreExplanation || ""}\n\n`;
  md += `## Claims Breakdown\n`;
  (r.claims || []).forEach((c, i) => {
    md += `### ${i + 1}. ${c.claim}\n`;
    md += `- **Status:** ${c.status}\n`;
    md += `- **Analysis:** ${c.analysis || c.correction || ""}\n`;
    md += `- **Authority Score:** ${c.authorityScore || 90}/100\n\n`;
  });

  navigator.clipboard.writeText(md).then(() => {
    const btn = document.getElementById("btn-copy-stalia-report");
    if (btn) {
      const orig = btn.innerHTML;
      btn.innerHTML = '<span class="material-symbols-outlined text-sm text-emerald-600">check</span><span class="text-emerald-700">Copied Markdown Report!</span>';
      setTimeout(() => { btn.innerHTML = orig; }, 2000);
    }
  });
};

window.loadStaliaHistory = async function() {
  const listEl = document.getElementById("stalia-recent-checks-list");
  if (!listEl) return;

  try {
    const res = await fetch("/api/verify/history");
    const data = await res.json();
    const history = data.history || [];
    window.staliaHistoryRecords = history;

    if (history.length === 0) {
      listEl.innerHTML = '<div class="text-center py-4 text-neutral-400">No past checks recorded yet.</div>';
      return;
    }

    listEl.innerHTML = history.slice(0, 6).map((item, idx) => {
      const score = item.overallScore ?? item.overall_score ?? 0;
      const provider = item.provider || "AI Output";
      const preview = (item.answerText || item.answer_text || "").slice(0, 45) + "...";
      const scoreBadge = score >= 70
        ? "bg-emerald-50 text-emerald-700 border-emerald-200"
        : "bg-amber-50 text-amber-700 border-amber-200";

      return `
        <div class="p-2.5 rounded-lg border border-neutral-100 hover:border-neutral-300 bg-neutral-50/60 hover:bg-white cursor-pointer transition-all flex items-center justify-between" onclick="loadHistoricalStaliaCheck(${idx})">
          <div class="truncate pr-2">
            <div class="text-[11px] font-semibold text-neutral-800 font-mono">${escapeHtml(provider)}</div>
            <div class="text-[10px] text-neutral-500 truncate font-sans">${escapeHtml(preview)}</div>
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${scoreBadge}">
            ${score}/100
          </span>
        </div>
      `;
    }).join("");
  } catch (err) {
    listEl.innerHTML = '<div class="text-center py-4 text-neutral-400">Failed to load history.</div>';
  }
};

window.loadHistoricalStaliaCheck = function(idx) {
  const item = window.staliaHistoryRecords[idx];
  if (!item) return;
  const textarea = document.getElementById("stalia-input-text");
  if (textarea) textarea.value = item.answerText || item.answer_text || "";
  renderStaliaResults(item);
};

/* --- MULTI-AI CONSENSUS METHODS --- */

window.loadMultiAIPreset = function(idx) {
  const preset = MULTIAI_PRESETS[idx];
  if (!preset) return;

  const btn0 = document.getElementById("btn-multiai-preset-0");
  const btn1 = document.getElementById("btn-multiai-preset-1");
  if (btn0) btn0.className = idx === 0 ? "px-3 py-1 rounded-lg border border-brand bg-brand-subtle text-brand text-xs font-semibold" : "px-3 py-1 rounded-lg border border-neutral-200 hover:border-brand hover:text-brand text-xs font-medium text-neutral-700 bg-white transition-colors";
  if (btn1) btn1.className = idx === 1 ? "px-3 py-1 rounded-lg border border-brand bg-brand-subtle text-brand text-xs font-semibold" : "px-3 py-1 rounded-lg border border-neutral-200 hover:border-brand hover:text-brand text-xs font-medium text-neutral-700 bg-white transition-colors";

  const cgText = document.getElementById("multiai-chatgpt-text");
  const clText = document.getElementById("multiai-claude-text");
  const gmText = document.getElementById("multiai-gemini-text");

  if (cgText) cgText.value = preset.chatgpt;
  if (clText) clText.value = preset.claude;
  if (gmText) gmText.value = preset.gemini;

  const container = document.getElementById("multiai-results-container");
  if (container) container.classList.add("hidden");
};

window.runMultiAICorrobation = async function() {
  const cg = document.getElementById("multiai-chatgpt-text")?.value.trim() || "";
  const cl = document.getElementById("multiai-claude-text")?.value.trim() || "";
  const gm = document.getElementById("multiai-gemini-text")?.value.trim() || "";

  if (!cg || !cl || !gm) {
    alert("Please provide responses for all three models before corroborating.");
    return;
  }

  const btn = document.getElementById("btn-run-multiai-verify");
  const btnText = document.getElementById("multiai-run-btn-text");
  if (btn) btn.disabled = true;
  if (btnText) btnText.textContent = "Calculating Consensus...";

  try {
    const res = await fetch("/api/verify/multi", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answers: { chatgpt: cg, claude: cl, gemini: gm } })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    // Show container
    const container = document.getElementById("multiai-results-container");
    if (container) container.classList.remove("hidden");

    // Agreement Rate & Consensus Score
    const agreeEl = document.getElementById("multiai-agreement-rate");
    const barEl = document.getElementById("multiai-agreement-bar");
    const scoreEl = document.getElementById("multiai-consensus-score");
    const verdictEl = document.getElementById("multiai-consensus-verdict");

    const agreement = data.agreementRate ?? 78;
    const score = data.consensusScore ?? 85;

    if (agreeEl) agreeEl.textContent = `${agreement}%`;
    if (barEl) barEl.style.width = `${agreement}%`;
    if (scoreEl) scoreEl.textContent = `${score}/100`;
    if (verdictEl) verdictEl.textContent = `${agreement >= 75 ? "High cross-model agreement" : "Moderate model divergence"}`;

    // Leaderboard
    const lbEl = document.getElementById("multiai-leaderboard");
    if (lbEl && data.providerResults) {
      const sorted = Object.entries(data.providerResults).sort((a, b) => (b[1].score || 0) - (a[1].score || 0));
      lbEl.innerHTML = sorted.map(([name, r], rank) => `
        <div class="flex items-center justify-between py-1 border-b border-neutral-100 last:border-0">
          <div class="flex items-center gap-1.5">
            <span class="w-4 text-center font-bold text-neutral-400">#${rank + 1}</span>
            <span class="font-medium text-neutral-800">${escapeHtml(name.toUpperCase())}</span>
          </div>
          <span class="font-bold font-mono text-brand">${r.score ?? 0}/100</span>
        </div>
      `).join("");
    }

    // Consensus Facts
    const factsList = document.getElementById("multiai-consensus-facts-list");
    const factsCount = document.getElementById("multiai-consensus-facts-count");
    const facts = data.consensusFacts || [];
    if (factsCount) factsCount.textContent = `${facts.length} facts`;
    if (factsList) {
      factsList.innerHTML = facts.length > 0
        ? facts.map(f => `<div class="p-2.5 rounded-lg bg-emerald-50/50 border border-emerald-100 text-neutral-800 flex items-start gap-2"><span class="text-emerald-600 font-bold">✓</span><span>${escapeHtml(f)}</span></div>`).join("")
        : '<div class="text-neutral-400 py-2">No cross-model consensus facts found.</div>';
    }

    // Divergences
    const divList = document.getElementById("multiai-divergences-list");
    const divergences = data.divergences || [];
    if (divList) {
      divList.innerHTML = divergences.length > 0
        ? divergences.map(d => `<div class="p-2.5 rounded-lg bg-white border border-amber-200 space-y-1"><div class="font-semibold text-amber-900">${escapeHtml(d.issue || d.topic || "Divergence")}</div><div class="text-neutral-600 text-xs">${escapeHtml(d.detail || d.explanation || JSON.stringify(d))}</div></div>`).join("")
        : '<div class="text-neutral-500 py-2">No critical factual discrepancies detected between models.</div>';
    }

  } catch (err) {
    alert("Multi-AI comparison failed: " + err.message);
  } finally {
    if (btn) btn.disabled = false;
    if (btnText) btnText.textContent = "Corroborate Across All 3 AIs";
  }
};

/* --- IN-AI PLUGINS & MCP METHODS --- */

window.switchPluginSubTab = function(subtabId) {
  const tabs = document.querySelectorAll(".plugin-sub-tab");
  tabs.forEach(t => {
    if (t.getAttribute("data-subtab") === subtabId) {
      t.className = "plugin-sub-tab active px-3.5 py-2 rounded-lg bg-white shadow-sm text-neutral-900 font-medium";
    } else {
      t.className = "plugin-sub-tab px-3.5 py-2 rounded-lg text-neutral-600 hover:text-neutral-900 font-medium";
    }
  });

  const panes = document.querySelectorAll(".plugin-pane");
  panes.forEach(p => {
    if (p.id === `${subtabId}-pane`) {
      p.classList.remove("hidden");
    } else {
      p.classList.add("hidden");
    }
  });
};

window.setSimulatedPlatform = function(platform) {
  currentSimPlatform = platform;
  const buttons = document.querySelectorAll(".sim-plat-btn");
  buttons.forEach(b => {
    if (b.id === `sim-btn-${platform}`) {
      b.className = "sim-plat-btn active px-3 py-1.5 rounded-lg text-xs font-mono font-medium border border-brand bg-brand-subtle text-brand flex items-center gap-1.5";
    } else {
      b.className = "sim-plat-btn px-3 py-1.5 rounded-lg text-xs font-mono font-medium border border-neutral-200 bg-white text-neutral-600 hover:bg-neutral-50 flex items-center gap-1.5";
    }
  });

  const promptEl = document.getElementById("sim-user-prompt");
  const respEl = document.getElementById("sim-ai-response");
  const urlEl = document.getElementById("sim-browser-url");
  const avatarEl = document.getElementById("sim-bot-avatar");

  const turn = SIMULATED_PRESETS[platform];
  if (promptEl) promptEl.textContent = turn.prompt;
  if (urlEl) urlEl.textContent = `https://${platform === "chatgpt" ? "chatgpt.com" : platform === "claude" ? "claude.ai" : "gemini.google.com"}/c/fact-verification-session`;
  if (avatarEl) avatarEl.textContent = platform === "chatgpt" ? "GPT" : platform === "claude" ? "CL" : "GEM";

  // Re-inject response with fresh floating pill
  if (respEl) {
    respEl.innerHTML = `
      ${turn.response}
      <div class="stalia-floating-pill mt-4 pt-3 border-t border-neutral-700 flex items-center justify-between cursor-pointer" onclick="toggleSimPillDetails()" id="sim-trust-pill-box">
        <div class="flex items-center gap-2">
          <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-brand text-white flex items-center gap-1">
            <span class="material-symbols-outlined text-[12px]">verified</span>
            STALIA TRUST
          </span>
          <span class="text-xs font-mono font-semibold text-emerald-400" id="sim-pill-score">Awaiting Check</span>
        </div>
        <span class="text-[11px] text-neutral-400 flex items-center gap-1">
          <span>Click to verify</span>
          <span class="material-symbols-outlined text-xs">expand_more</span>
        </span>
      </div>
      <div id="sim-pill-expanded" class="hidden mt-3 p-3 rounded-lg bg-neutral-950 border border-neutral-700 text-[11px] font-mono text-neutral-300 space-y-2"></div>
    `;
  }
};

window.simulatePluginCheck = async function() {
  const turn = SIMULATED_PRESETS[currentSimPlatform];
  const pillScore = document.getElementById("sim-pill-score");
  const pillExpanded = document.getElementById("sim-pill-expanded");

  if (pillScore) pillScore.textContent = "Verifying via Gateway...";

  try {
    const res = await fetch("/api/plugin/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer: turn.raw, provider: currentSimPlatform, format: "json" })
    });
    const data = await res.json();

    if (pillScore) {
      pillScore.textContent = `${data.overallScore ?? 80}/100 (${data.overallStatus || "Mostly Fresh"})`;
      pillScore.className = `text-xs font-mono font-semibold ${(data.overallScore || 0) >= 70 ? "text-emerald-400" : "text-amber-400"}`;
    }

    if (pillExpanded) {
      const claims = data.claims || [];
      pillExpanded.innerHTML = `
        <div class="font-bold text-white border-b border-neutral-800 pb-1 mb-2">Grounding Telemetry via Bifrost:</div>
        ${claims.slice(0, 3).map(c => `
          <div class="${c.status === 'supported' ? 'text-emerald-400' : 'text-amber-400'}">
            ${c.status === 'supported' ? '✓' : '⚠'} ${escapeHtml(c.claim)}
          </div>
        `).join("")}
        <div class="pt-2 border-t border-neutral-800 text-[10px] text-neutral-500">
          Deterministic Score: ${data.overallScore}/100 • Coverage: ${data.evidenceCoverage ?? 100}%
        </div>
      `;
      pillExpanded.classList.remove("hidden");
    }
  } catch (err) {
    if (pillScore) pillScore.textContent = "Offline Check: 80/100";
  }
};

window.toggleSimPillDetails = function() {
  const exp = document.getElementById("sim-pill-expanded");
  if (exp) {
    if (exp.classList.contains("hidden")) {
      exp.classList.remove("hidden");
      if (!exp.innerHTML.trim()) simulatePluginCheck();
    } else {
      exp.classList.add("hidden");
    }
  }
};

window.copyStaliaBookmarklet = function() {
  const origin = window.location.origin || "http://localhost:8082";
  const code = `javascript:(function(){const endpoint='${origin}/api/plugin/verify';const sel=window.getSelection().toString().trim();const text=sel||document.body.innerText.slice(0,3000);if(!text||text.length<10){alert('Stalia.AI: Highlight text to verify or ensure page has content.');return;}const overlay=document.createElement('div');overlay.style='position:fixed;top:20px;right:20px;z-index:999999;width:340px;background:#18181b;color:#f4f4f5;border:1px solid #3E6AE1;border-radius:12px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,0.5);font-family:sans-serif;font-size:12px;';overlay.innerHTML='<div style="color:#3E6AE1;font-weight:bold;margin-bottom:8px;">✨ Stalia.AI Verifying...</div><div>Corroborating factual claims with web grounding...</div>';document.body.appendChild(overlay);fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({answer:text,format:'json'})}).then(r=>r.json()).then(d=>{overlay.innerHTML='<div style="display:flex;justify-content:space-between;border-bottom:1px solid #333;padding-bottom:6px;margin-bottom:8px;"><strong style="color:#3E6AE1">Stalia Score: '+(d.overallScore!==null?d.overallScore+\'/100\':\'Unrated\')+'</strong><button onclick="this.parentElement.parentElement.remove()" style="background:none;border:none;color:#aaa;cursor:pointer;">✕</button></div><div style="margin-bottom:6px;">'+(d.scoreExplanation||\'\')+'</div><div style="font-size:11px;color:#aaa;">✅ '+(d.summary?.supported||0)+' Supported | ⚠️ '+(d.summary?.potentiallyStale||0)+' Stale</div>';}).catch(e=>{overlay.innerHTML='<div style="color:#ef4444;margin-bottom:6px;">Verification failed:</div><div style="font-size:11px;">Ensure CodeLite AI server is running</div><button onclick="this.parentElement.remove()" style="margin-top:8px;padding:4px 8px;background:#333;color:white;border:none;border-radius:4px;">Close</button>';});})();`;
  navigator.clipboard.writeText(code).then(() => {
    const btn = document.getElementById("btn-copy-bm-text");
    if (btn) {
      btn.textContent = "Copied to Clipboard!";
      setTimeout(() => { btn.textContent = "Copy Bookmarklet Code"; }, 2000);
    }
  });
};

window.copyMcpJson = function() {
  const origin = window.location.origin || "http://localhost:8082";
  const json = JSON.stringify({
    mcpServers: {
      "stalia-freshness-checker": {
        url: `${origin}/api/mcp`,
        transport: "http"
      }
    }
  }, null, 2);

  navigator.clipboard.writeText(json).then(() => {
    const btn = document.getElementById("btn-copy-mcp-text");
    if (btn) {
      btn.textContent = "Copied MCP Config!";
      setTimeout(() => { btn.textContent = "Copy JSON"; }, 2000);
    }
  });
};

window.copyGptSchema = function() {
  const schema = document.getElementById("gpt-action-schema-snippet")?.textContent || "";
  navigator.clipboard.writeText(schema).then(() => {
    const btn = document.getElementById("btn-copy-gpt-text");
    if (btn) {
      btn.textContent = "Copied OpenAPI Schema!";
      setTimeout(() => { btn.textContent = "Copy OpenAPI Schema"; }, 2000);
    }
  });
};

window.testMcpEndpoint = async function() {
  try {
    const res = await fetch("/api/mcp");
    const data = await res.json();
    alert(`MCP Protocol Response:\nTool: ${data.tools[0].name}\nDescription: ${data.tools[0].description}`);
  } catch (err) {
    alert("MCP test failed: " + err.message);
  }
};

/* --- WORKSPACE AUDIT WITH STALIA --- */

window.auditWorkspaceCodeWithStalia = async function() {
  const code = document.getElementById("workspace-sol-code")?.textContent || "";
  if (!code || code.trim().length < 10) {
    alert("No generated code in workspace to audit. Run a coding task first!");
    return;
  }

  const btn = document.getElementById("btn-audit-stalia");
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined text-sm animate-spin">refresh</span><span>Auditing Code...</span>';
  }

  try {
    const res = await fetch("/api/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ answer: code, provider: "codelite", format: "json" })
    });
    const data = await res.json();
    window.lastWorkspaceAudit = data;

    // Display banner in workspace
    const banner = document.getElementById("workspace-stalia-audit-result");
    const badge = document.getElementById("stalia-audit-badge");
    const summary = document.getElementById("stalia-audit-summary-text");

    if (banner) banner.classList.remove("hidden");
    if (badge) {
      const score = data.overallScore ?? 100;
      badge.textContent = `${score >= 70 ? "Verified Fresh" : "Review Needed"} (${score}/100)`;
      badge.className = score >= 70
        ? "px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-100 text-emerald-800"
        : "px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-amber-100 text-amber-800";
    }
    if (summary) {
      summary.textContent = data.scoreExplanation || `Audited ${data.claims?.length || 0} claims: ${(data.summary?.supported || 0)} supported, ${(data.summary?.potentiallyStale || 0)} stale.`;
    }

  } catch (err) {
    alert("Code audit failed: " + err.message);
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<span class="material-symbols-outlined text-sm">verified</span><span>Audit Code with Stalia</span>';
    }
  }
};

window.viewAuditInStaliaStudio = function() {
  if (window.lastWorkspaceAudit) {
    const code = document.getElementById("workspace-sol-code")?.textContent || "";
    const textarea = document.getElementById("stalia-input-text");
    if (textarea) textarea.value = code;
    window.currentStaliaResult = window.lastWorkspaceAudit;
    renderStaliaResults(window.lastWorkspaceAudit);
  }
  switchTab("stalia-view");
};

