# Agent Traveler

An AI travel planner built for travelers holding ordinary Colombian passports.

Instead of jumping straight into speculative hotel searches, Agent Traveler follows a structured, step-by-step workflow: it interviews you to clarify your travel preferences, checks Colombian visa and border requirements, maps realistic transit routes, and calculates indicative budgets in Colombian Pesos (COP).

It does not book flights or process payments. Its goal is to deliver an accurate, actionable travel dossier you can use to plan your trip safely.

---

## Architecture: How It Works

Agent Traveler uses a primary coordinator that delegates tasks to focused specialist agents and tools:

- **Trip Supervisor ([`.agents/agents/travel-supervisor.md`](.agents/agents/travel-supervisor.md))**: The orchestrator. When you share a trip idea, it checks whether your requirements are complete. If not, it launches an interactive **Spec-Driven Development (SDD)** interview to nail down lodging preferences, target cities, preferred climate, dates, and budget. Once defined, it freezes your requirements into a validated `trip-spec` YAML contract.
- **Visa & Entry Checker ([`.agents/agents/cancilleria-scanner.md`](.agents/agents/cancilleria-scanner.md))**: Verifies travel permissions for Colombian passport holders using official Cancillería guidelines, embassy policies, and layover rules. If a destination is legally unfeasible, it alerts you before planning routes.
- **Route & Sights Planner ([`.agents/agents/destination-researcher.md`](.agents/agents/destination-researcher.md))**: Orders stops logically, highlights local culture and food, and generates clean, clickable Google Maps links.
- **Weather & Local Transport ([`.agents/agents/weather-transport-researcher.md`](.agents/agents/weather-transport-researcher.md))**: Compares destination weather against your preferences, recommends seasonal packing, and explains metro, bus, and reliable taxi options.
- **Price & Live Currency Scout ([`.agents/skills/travel-price-scouting`](.agents/skills/travel-price-scouting/SKILL.md))**: Pulls indicative price ranges for flights and lodging (Booking, Airbnb, Kayak) matching your exact room and price filters, with live USD/EUR to COP exchange rates.

---

## Spec-Driven Development (SDD) Gate

Agent Traveler prevents wasted tokens and hallucinated itineraries by enforcing an explicit validation gate:

1. **Interview**: If your prompt lacks key details (e.g., "I want to visit the US for 2 weeks"), the agent pauses at Step 1 and asks for missing parameters (lodging style, bathroom preference, star rating, nightly price cap, cities, weather, origin airport).
2. **Contract Freeze**: Answers are saved as a structured `trip-spec` defined in [`.agents/specs/trip-spec-schema.md`](.agents/specs/trip-spec-schema.md).
3. **Execution**: Downstream research (visas, routes, flights, pricing) only runs once the spec is valid.

---

## ADK Execution (4-Agent A2A Architecture)

Agent Traveler runs on **Google ADK** using a decoupled **4-Agent Agent-to-Agent (A2A)** cluster ([`adk_agents/run_a2a_cluster.py`](adk_agents/run_a2a_cluster.py)). Each specialist agent runs as an isolated A2A JSON-RPC service (`/.well-known/agent-card.json`) with zero sibling package imports, while the user interacts exclusively with the customer-facing **Orchestrator** on port `8000`:

- **Orchestrator (`:8000` — [`adk_agents/orchestrator`](adk_agents/orchestrator/agent.py))**: Single customer-facing entrypoint in the ADK Web UI. Manages session state and coordinates the specialist agents over A2A JSON-RPC.
- **Builder (`:8001` — [`adk_agents/builder`](adk_agents/builder/agent.py))**: Conducts the interactive SDD interview until all required parameters are confirmed and freezes the validated `trip-spec` YAML contract.
- **Executioner (`:8002` — [`adk_agents/executioner`](adk_agents/executioner/agent.py))**: Consumes the validated `trip-spec` to run Cancillería visa verification, Google Maps route generation, flight corridor analysis, and live currency/price scouting.
- **Revisor (`:8003` — [`adk_agents/revisor`](adk_agents/revisor/agent.py))**: Audits the generated `TripReport` against the `trip-spec` contract and rubric rules before returning an `APPROVE` verdict to the customer.

### Launching the 4-Agent A2A Cluster

```bash
# Start Builder (:8001), Executioner (:8002), Revisor (:8003), and Orchestrator Web UI (:8000)
python -m adk_agents.run_a2a_cluster
```

### Step-by-Step Execution Flow in ADK Web UI

#### 1. Builder Agent (`:8001`) — Validated `trip-spec` Contract
Once all SDD interview parameters are collected, the Builder freezes the `trip-spec` (`status: validated`) and hands control back to the Orchestrator:

![ADK Execution - Step 1: Validated Trip Specification](assets/adk-step1-builder-spec.png)

#### 2. Executioner Agent (`:8002`) — Unified Trip Report Generation
The Orchestrator forwards the validated `trip-spec` over A2A to the Executioner, which verifies Cancillería entry policies, maps the ordered route, and builds the complete trip report:

![ADK Execution - Step 2: Unified Trip Report](assets/adk-step2-executioner-report.png)

#### 3. Revisor Agent (`:8003`) — Automated SDD Audit & Approval
Before presenting the final output, the Orchestrator dispatches the report over A2A to the Revisor (`:8003`) to verify compliance with every `trip-spec` constraint (`APPROVE` — Score `100/100`):

![ADK Execution - Step 3: SDD Revisor A2A Audit](assets/adk-step3-revisor-audit.png)

---

## Codebase Architecture & Graph Explorer

Agent Traveler uses [Grafeando](.agents/skills/grafeando/SKILL.md) powered by LadybugDB to map AST entities, dependency relationships, call graphs, and blast radius across agents, skills, and schemas.

![Grafeando Explorer - AST Graph View](assets/test1.png)

![Grafeando Explorer - Node Details](assets/test2.png)

To explore or update the graph:

```bash
# Re-index AST entities into LadybugDB
grafeando index .

# Generate interactive standalone HTML graph explorer
grafeando html
```

---

## Setup & Running the Evaluation Suite

We use the Google Antigravity Python SDK (`google-antigravity`) to run automated evaluation test cases against the supervisor's interview gate and guardrails.

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Credentials

Create a `.env` file in the project root:

```bash
GEMINI_KEY="your_api_key_here"
GEMINI_MODEL="gemini-3.5-flash-lite"
```

The runner supports both `GEMINI_KEY` and `GEMINI_API_KEY`.

### 3. Run the Evals

Run the test cases in `evals/test_cases.json`:

```bash
# Run all test cases live using the model in .env
python -m evals.run_evals

# Run in offline mock mode (no API calls, validates rubric engine)
python -m evals.run_evals --mock

# Run a specific test case without updating test_cases.json
python -m evals.run_evals --test-id tc-001-usa-2-weeks-incomplete-interview --no-update

# Override model or key on the command line
python -m evals.run_evals --model gemini-3.8-flash --api-key YOUR_KEY
```

Every run logs execution history in [`evals/test_cases.json`](evals/test_cases.json) and writes a markdown summary to `evals/reports/report_v<version>.md` (for example, [`evals/reports/report_v1.0.0.md`](evals/reports/report_v1.0.0.md)).

---

## Roadmap

- [x] **Spec-Driven Development (SDD)**: Interactive interview protocol and validated `trip-spec` schema contract ([`.agents/specs/trip-spec-schema.md`](.agents/specs/trip-spec-schema.md)).
- [x] **Antigravity SDK Test Harness**: Automated evaluation runner that verifies the Step 1 interview gate and blocks premature route/pricing actions ([`evals/run_evals.py`](evals/run_evals.py)).
- [x] **Google ADK & A2A Migration**: 4-agent isolated A2A architecture (`orchestrator`, `builder`, `executioner`, `revisor`) with deterministic state handoffs and automated SDD auditing ([`adk_agents/run_a2a_cluster.py`](adk_agents/run_a2a_cluster.py)).
