# Full Context Study Document
## Agentic AI for Transport Disruption Management
**IIITNR Semester 5 Minor Project** | In collaboration with INSA Hauts-de-France  
**Mentors:** Dr. Alaa DAOUD (INSA) & Dr. Srinivasa K G (IIITNR)  
**Status as of Week 3:** Simulation environment built, B1 (Rule-Based) complete, B2/B3 pending  
**Read this before touching any code.**

---

## Table of Contents
1. [The Big Picture — What & Why](#1-the-big-picture)
2. [Research Question & Hypotheses](#2-research-question--hypotheses)
3. [Literature Foundation (5 Core Papers)](#3-literature-foundation)
4. [Research Gaps We Fill](#4-research-gaps-we-fill)
5. [System Architecture](#5-system-architecture)
6. [Experimental Design](#6-experimental-design)
7. [Simulation Environment (What's Built)](#7-simulation-environment)
8. [Actual Results — B1 Real Data](#8-actual-results--b1-real-data)
9. [Codebase Map](#9-codebase-map)
10. [What Still Needs Building](#10-what-still-needs-building)
11. [Demo App Plan](#11-demo-app-plan)
12. [Key Numbers to Remember](#12-key-numbers-to-remember)

---

## 1. The Big Picture

### The Problem
When a sudden shock hits an urban road network (road collapse, flooding, severe accident), two existing approaches both fail:

| Approach | Why it Fails |
|---|---|
| **Rule-Based SOP (Dijkstra + lookup tables)** | Pre-programmed rules can't adapt when multiple simultaneous disruptions occur. No contextual reasoning for fleet battery state or passenger priority. |
| **Single Monolithic LLM** | Full road graph + fleet + congestion state in one prompt → context erosion and hallucinations. Regularly proposes routes on non-existent edges or violates vehicle capacity constraints. |

### Our Hypothesis
Decomposing disruption response into **role-isolated specialized LLM agents** (Traffic, Fleet, Routing, Coordinator) bound by a **deterministic Safety-Review Guard** can eliminate hard-constraint violations while staying within real-time latency and API token cost budgets.

### The Scientific Question
> *"When does multi-agent LLM coordination actually improve transport-disruption decisions compared to a single LLM or rule-based approach on 2D road networks — and is the improvement worth the additional cost?"*

This is NOT just "show that agents work." We are finding the **boundary conditions** where multi-agent coordination starts to pay off.

---

## 2. Research Question & Hypotheses

### 5 Testable Hypotheses

| ID | Hypothesis | Measurable Target | Test Method |
|---|---|---|---|
| **H₁** | Role specialization + safety guard eliminates hard constraint violations | **HCVR = 0%** for B3 vs >0% for B2 | Compare HCVR across all 3 systems on same scenarios |
| **H₂** | Multi-agent has latency and token overhead | **2.5–4× latency** vs rule-based; **1.5–2.5× token cost** vs single-LLM | Measure wall-clock time + token counts |
| **H₃** ⭐ | Multi-agent beats single-LLM on complex scenarios but NOT simple ones | Find **crossover point** in RFR as disruption complexity increases L1→L5 | Run all 5 levels, plot RFR curve |
| **H₄** | Role decomposition reduces per-agent prompt size | Token growth: **O(N·K)** for B3 vs **O(N²)** for B2 | Measure prompt token counts as network scales |
| **H₅** | MAST-guided architectural fixes improve success ≥10% | **≥10% RFR improvement** after targeted fixes | Log failures by MAST category, apply fixes, re-evaluate |

> **H₃ is the key scientific contribution.** The crossover point is what makes this paper publishable. If multi-agent is ALWAYS better or NEVER better, that's less interesting.

---

## 3. Literature Foundation

### The 5 Core Papers

#### Thread A: Domain Surveys (prove LLMs work in ITS, identify our gap)

**Paper 1 — Mahmud et al. (IEEE T-ITS, May 2025)**
- *Integrating Large Language Models with Intelligent Transportation Systems: A Survey*
- **Key finding:** LLMs have strong contextual reasoning for ITS but real-time inference latency and non-deterministic outputs are major deployment barriers.
- **Our use:** Justifies using LLMs for high-level decisions; mandates the deterministic Safety Guard.

**Paper 2 — Nie, Sun & Ma (Elsevier AIT / arXiv:2503.21411, June 2025)**
- *LLM4TR: Large Language Models for Transportation — A Survey and Taxonomy*
- **Key finding:** Defines 4 LLM roles: Info Processors, Knowledge Encoders, Component Generators, **Decision Facilitators**.
- **Our use:** Positions our entire project under the *Decision Facilitator* category — the most advanced and underexplored class.

**Paper 3 — Wandelt et al. (MDPI Applied Sciences, Aug 2024)**
- *Large Language Models in Intelligent Transportation Systems: A Review*
- **Key finding:** Systematic review of 130+ papers shows **>60% focus on single AV perception** — operational multi-vehicle disruption management is wide open.
- **Our use:** Quantifies and proves our research gap to mentors and reviewers.

#### Thread B: Multi-Agent Precedents (directly shape our design)

**Paper 4 — Wu & Zeng (MDPI Mathematics, Aug 2026) ← CLOSEST PRECEDENT**
- *LLM-Driven Multi-Agent Coordinated Control for Urban Rail Disruption Management*
- Tongji University & Peking University
- **Architecture:** 4-agent system (Dispatch, Station, Transfer, Information) + Safety-Review Agent + Coordinator on Shanghai Metro Line 2.
- **Results:** 58.9% total-delay reduction, 32.6% peak transfer-queue reduction vs rule-based baselines.
- **Critical limitation:** Gains REVERSED once transfer capacity dropped below 25% — multi-agent coordination cannot fix physical capacity bottlenecks without alternate path rerouting.
- **Our extension:** We move from 1D linear rail corridor → 2D urban road network graphs with time-varying edge capacities and dynamic detour loops.

**Paper 5 — Cemri et al. / UC Berkeley (NeurIPS 2025) — MAST**
- *Why Do Multi-Agent LLM Systems Fail? An Empirical Characterization of Failure Modes*
- arXiv:2503.13657
- **Data:** 1,642 execution traces across 7 MAS frameworks. 41–87% task-failure rate.
- **Key insight:** Targeted architectural fixes yielded +15.6% success using the **same underlying LLM** — failure is architectural, not model-limited.
- **Failure breakdown (210-trace sample):**
  - 41.8% → System Design Issues (prompt vagueness, redundant loops)
  - 36.9% → Inter-Agent Misalignment (misinterpreted messages)
  - 21.3% → Task Verification Failures (no validation layer)
- **Our use:** Justifies building the Pydantic JSON verification layer. Guides our MAST failure logging.

#### Thread C: Additional 2026 Works

| Paper | What It Proves | Our Takeaway |
|---|---|---|
| **TrafficGen (Frontiers 2026)** | Council-of-Agents with Gemini 2.5 Flash on single intersection — 46.9% wait-burden reduction | Proves multi-agent works at **micro-level**; we operate at **network level** |
| **Tran & Kiela (arXiv 2026)** | Single-agent matches multi-agent on reasoning tasks when **token budgets are equalized** | We MUST normalize token budgets in B2 vs B3 comparison — critical for scientific validity |
| **REALM-Bench (arXiv 2026)** | Benchmark for multi-agent logistics with disruption handling (LangGraph, AutoGen, CrewAI) | Closest benchmark but lacks hard physical constraints (no SoC, no BFS guard) |

---

## 4. Research Gaps We Fill

> **Formal Gap Statement:** No existing study evaluates multi-agent LLM systems against both single-LLM and rule-based baselines for real-time disruption management on 2D road-network graphs with time-varying capacities, fleet state constraints, and deterministic safety verification — while controlling for token budget and measuring cost-latency-quality trade-offs.

| Gap | Existing Work | What We Add |
|---|---|---|
| **Network Domain** | Rail corridors (Wu & Zeng), single intersections (TrafficGen) | **2D road-network graphs** with dynamic alternate detour loops |
| **3-Way Benchmark** | MAS vs rule-based only; or SAS vs MAS on reasoning tasks | **Rule-Based vs Single-LLM vs Multi-Agent** on identical transport scenarios |
| **Token Budget Control** | Normalized on reasoning benchmarks (Tran & Kiela) | First budget-controlled comparison on **transport tool-use tasks** |
| **Safety Verification** | Safety-Review Agent concept (Wu & Zeng) | **BFS + Pydantic guard benchmarked** with quantified HCVR |
| **MAST in Transport** | 14 failure modes across general MAS | First logging of MAST failures in a **transport decision-support** context |
| **Cost-Latency-Quality** | Acknowledged (Mahmud et al.) | Never quantified for transport disruption control |

---

## 5. System Architecture

### The 4-Agent Pipeline

```
DISRUPTION EVENT D(t)
        │
        ▼
┌───────────────────────────────────────────────────────┐
│                 SPECIALIZED AGENT LAYER                │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │ TRAFFIC      │  │ FLEET        │  │ ROUTING     │  │
│  │ AGENT        │  │ AGENT        │  │ AGENT       │  │
│  │              │  │              │  │             │  │
│  │ Scope:       │  │ Scope:       │  │ Scope:      │  │
│  │ Graph G=(V,E)│  │ Fleet S_v(t) │  │ Paths R_k   │  │
│  │ C(e,t)       │  │ SoC levels   │  │ detour calc │  │
│  │              │  │              │  │             │  │
│  │ Tools:       │  │ Tools:       │  │ Tools:      │  │
│  │ get_network  │  │ get_vehicles │  │ shortest    │  │
│  │ get_disrupted│  │ get_available│  │ _path()     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│         └─────────────────┼─────────────────┘         │
└───────────────────────────┼───────────────────────────┘
                            │ Proposals
                            ▼
            ┌──────────────────────────┐
            │     COORDINATOR AGENT    │
            │  (Synthesizes → emits    │
            │   DecisionCard JSON)     │
            │  Tools: assign_vehicle() │
            └─────────────┬────────────┘
                          │
                          ▼
            ┌──────────────────────────┐
            │   SAFETY-REVIEW GUARD    │
            │   (Pure Python, No LLM)  │
            │                          │
            │  ① BFS Reachability:     │
            │    C(e,t) > 0 on route   │
            │  ② SoC Sufficiency:      │
            │    charge ≥ dist + 15%   │
            │  ③ Capacity Check:       │
            │    seats ≥ passengers    │
            │  ④ Pydantic Schema:      │
            │    valid DecisionCard    │
            └──────────┬───────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       [PASS] Execute       [FAIL] Fallback
        DecisionCard         SOP Route
```

### The DecisionCard Schema (output format)
```json
{
  "scenario_id": "L3_compound_001",
  "request_id": "R2",
  "recommended_action": "REROUTE_AND_DISPATCH",
  "vehicle_id": "V002",
  "assigned_route": ["B0", "B1", "C1", "C2", "C3"],
  "estimated_delay_reduction_min": 0.0,
  "safety_guard_passed": true,
  "rejection_reason": null,
  "route_distance_km": 0.72,
  "estimated_travel_time_s": 51.6
}
```

### The 4 Agents — Scope & Tools

| Agent | Role | Info Scope | Tools |
|---|---|---|---|
| **Traffic Agent** | Network Monitor — tracks topology, edge capacities, congestion, identifies disrupted edges | Graph G=(V,E), C(e,t), congestion levels | `get_network_state()`, `get_disrupted_edges()` |
| **Fleet Agent** | Resource Manager — tracks vehicle positions, SoC, availability | Vehicle state matrix S_v(t), fleet positions, SoC | `get_vehicle_status()`, `get_available_vehicles()`, `check_vehicle_range()` |
| **Routing Agent** | Path Synthesizer — proposes detour routes, estimates travel times | Disrupted edges from Traffic Agent, vehicle locations from Fleet Agent | `shortest_path()`, `estimate_travel_time()` |
| **Coordinator Agent** | Arbitration Engine — synthesizes proposals into unified DecisionCard JSON | Proposals from all 3 agents | `assign_vehicle()`, `create_decision_card()`, `submit_to_safety_guard()` |

### Single-LLM Agent (B2) — For Comparison
Gets **all the same tools** but in a single prompt with the full graph + fleet + request state combined. Same Safety Guard applied to its output.

---

## 6. Experimental Design

### 3-Way System Comparison

| System | Decision Maker | Tools | Safety Guard |
|---|---|---|---|
| **B1: Rule-Based SOP** | Deterministic heuristic (shortest available path + nearest vehicle) | Same Python functions (called directly) | Same guard |
| **B2: Single-LLM Agent** | One LLM with full state + all tools | Same tools as function-calls | Same guard |
| **B3: Multi-Agent LLM** | 4 specialized agents with scoped tools | Tools partitioned by agent role | Same guard |

### Controlled Variables (critical for scientific validity)
- Same **scenario JSON files** for all 3 systems
- Same **Python tool functions** — B1 calls directly, B2/B3 via LLM tool-use
- Same **Safety Guard** applied to all outputs
- Same **LLM model** (e.g., GPT-4o-mini) for B2 and B3
- **Fixed random seeds** for reproducibility
- **Token budget tracked** — per Tran & Kiela 2026, must normalize for fair B2 vs B3 comparison

### 5 Disruption Scenario Levels (L1–L5)

| Level | Name | Disruptions | Hypothesis Tested |
|---|---|---|---|
| **L1** | Simple | 1 road closure | Basic rerouting capability |
| **L2** | Moderate | 1 closure + 1 congestion | Smarter path selection needed |
| **L3** | Compound | 1 closure + 1 congestion + 1 breakdown | Fleet rebalancing needed |
| **L4** | Cascading | 2 closures + 1 congestion + 1 breakdown + demand surge | Full coordination tested |
| **L5** | Stress Test | 3 closures + 2 congestions + 2 breakdowns + large surge | Graceful degradation |

> **H₃ crossover test:** Plot RFR of B2 vs B3 across L1→L5. The complexity level where B3 overtakes B2 is our key publishable finding.

### 6 Core Evaluation Metrics

| # | Metric | Formula | Target |
|---|---|---|---|
| 1 | **HCVR %** (Hard Constraint Violation Rate) | Infeasible actions ÷ Total actions × 100 | 0% for B3 w/ guard |
| 2 | **RFR %** (Request Fulfillment Rate) | Served requests ÷ Total requests × 100 | Higher = better |
| 3 | **ADIF** (Average Delay Inflation Factor) | Actual travel time ÷ Free-flow travel time | Closer to 1.0 = better |
| 4 | **T_exec** (Execution Latency) | Wall-clock seconds per scenario | Lower = better |
| 5 | **$/scenario** (Token Cost) | Prompt + completion tokens × API price | Measured, not targeted |
| 6 | **IDR %** (Infeasible Decision Rate) | Safety Guard rejections ÷ Total decisions × 100 | Lower = better |

---

## 7. Simulation Environment

### Network: 4×4 Grid (16 Nodes, ~48 Edges)
- **Nodes:** A0–D3 (rows A–D, columns 0–3)
- **Edges:** ~200m per segment, bidirectional
- **Tool:** Eclipse SUMO v1.27.1 + NetworkX dual representation
- **File:** `sim/networks/grid_4x4.net.xml`

### Why SUMO?
SUMO won the simulator evaluation over MATSim, AnyLogic, RinSim, RideGym, and Veins because:
- First-class Python API via `traci` / `libsumo`
- Lock-step execution (simulation pauses until LLM responds)
- Native disruption injection (lane closure, speed reduction, vehicle stop)
- Open source (Eclipse Foundation) — accepted at AI venues

### 4 Disruption Types

```python
# Road Closure → C(e, t) = 0
network.close_edge("B2", "C2")
traci.lane.setDisallowed(lane_id, ["passenger", "taxi", ...])
traci.edge.adaptTraveltime(edge_id, time=100000)

# Congestion → travel_time *= factor
network.congest_edge("B3", "C3", congestion_factor=4.0)
traci.edge.setMaxSpeed(edge_id, original_speed / factor)

# Vehicle Breakdown → status = "broken"
fleet.break_vehicle("V002")
traci.vehicle.setStop(vehicle_id, edgeID=edge_id, pos=pos, duration=100000)

# Demand Surge → inject extra TransportRequest objects
request_queue.add_request(TransportRequest(id="SURGE_D5_0", origin="A0", destination="B1", ...))
```

### 7 Core Tool Functions (shared across ALL 3 systems)

| # | Function | Used By |
|---|---|---|
| 1 | `get_network_state()` | Traffic Agent / Single-LLM / Rule-Based |
| 2 | `get_vehicle_status()` | Fleet Agent / Single-LLM / Rule-Based |
| 3 | `get_disrupted_edges()` | Traffic Agent / Single-LLM / Rule-Based |
| 4 | `get_available_vehicles()` | Fleet Agent / Single-LLM / Rule-Based |
| 5 | `shortest_path(origin, destination)` | Routing Agent / Single-LLM / Rule-Based |
| 6 | `assign_vehicle(vehicle_id, request_id, route)` | Coordinator / Single-LLM / Rule-Based |
| 7 | `validate_plan(vehicle_id, route, request_id)` | **All systems** — Safety Guard |

### Safety Guard — 4 Checks (in `validate_plan`)

```
1. Route Existence   → every edge (u,v) in route must exist in graph G
2. BFS Reachability  → every edge (u,v) must have C(e,t) > 0 (not closed)
3. SoC Sufficiency   → vehicle.soc >= distance_km × soc_per_km × 1.15
4. Passenger Capacity → vehicle.capacity >= passengers + current_passengers
```

If ANY check fails → plan rejected → fallback to SOP route.

---

## 8. Actual Results — B1 Real Data

These are **real measured values** from running the Rule-Based baseline (B1) on all 5 scenarios.

| Scenario | HCVR % | RFR % | ADIF | Latency (ms) | IDR % |
|---|---|---|---|---|---|
| **L1 Simple** | 0.0 | 100.0 | 1.000 | 4.2 | 0.0 |
| **L2 Moderate** | 0.0 | 100.0 | 1.167 | 4.7 | 0.0 |
| **L3 Compound** | 0.0 | 100.0 | 1.133 | 4.9 | 0.0 |
| **L4 Cascading** | 0.0 | **75.0** | 1.074 | 8.8 | **25.0** |
| **L5 Stress** | 0.0 | **44.4** | 1.229 | 8.4 | **55.6** |

### Key Observations from B1 Data
1. **HCVR is 0% for all scenarios** — rule-based never proposes physically invalid plans (it uses the Safety Guard too)
2. **RFR drops sharply at L4/L5** — demand surge + fleet exhaustion leaves 25–56% requests unserved
3. **IDR spikes at L4/L5** — when fleet runs out, the rule-based marks requests as `NO_VEHICLE_AVAILABLE`
4. **ADIF increases with complexity** — routes get longer as disruptions force detours
5. **Latency is tiny (4–9ms)** — rule-based is near-instant; this is the speed baseline B2/B3 will be compared against

### L4 Cascading — Failure Pattern
At L4, 3 out of 12 decisions are `NO_VEHICLE_AVAILABLE` (surge requests). At L5, 10 out of 18 decisions fail. This is exactly where we expect Multi-Agent (B3) to potentially do better — by being smarter about fleet pre-positioning and priority-based assignment.

### Result Files Location
```
sim/results/
├── L1_simple_001_rule_based.json
├── L2_moderate_001_rule_based.json
├── L3_compound_001_rule_based.json
├── L4_cascading_001_rule_based.json
└── L5_stress_001_rule_based.json
```

---

## 9. Codebase Map

```
04-Minor/
├── STUDY.md                        ← YOU ARE HERE
├── project.md                      ← demo build plan
│
├── week-0/
│   ├── student projects.pdf        ← original project brief (all student directions)
│   └── Student_Research_Vision_Multi_Agent_Transport.pdf
│
├── week-1/
│   ├── work.md                     ← full literature review, architecture, speaker scripts
│   ├── week-1.pptx                 ← Week 1 presentation
│   └── research-work/             ← raw paper notes
│
├── week-2/
│   ├── research-gap-and-design.md  ← research gap matrix + experimental design (BEST REFERENCE)
│   └── Research Gap & Design.pdf   ← PDF version
│
├── week-3/
│   ├── work.md                     ← ALL implementation code (1600+ lines, full source)
│   ├── implementation-steps.md     ← step-by-step guide
│   └── Figure_1.png / Screenshots  ← SUMO simulation screenshots
│
├── sim/                            ← ACTIVE PYTHON CODEBASE
│   ├── pyrightconfig.json
│   ├── networks/
│   │   └── grid_4x4.net.xml        ← 4×4 grid SUMO network
│   ├── scenarios/
│   │   ├── L1_simple.json
│   │   ├── L2_moderate.json
│   │   ├── L3_compound.json
│   │   ├── L4_cascading.json
│   │   └── L5_stress.json
│   ├── results/
│   │   ├── L1–L5 rule_based JSONs  ← REAL B1 DATA
│   │   └── gui_dashboard.png
│   ├── src/
│   │   ├── __init__.py
│   │   ├── network/                ← TransportNetwork, graph_builder.py
│   │   ├── fleet/                  ← Vehicle, Fleet, VehicleStatus, fleet_factory
│   │   ├── requests/               ← TransportRequest, RequestQueue
│   │   ├── disruptions/            ← Disruption types, DisruptionManager
│   │   ├── scenarios/              ← ScenarioConfig loader
│   │   ├── tools/                  ← AgentTools (7 functions)
│   │   ├── safety/                 ← DecisionCard schema (Pydantic)
│   │   ├── metrics/                ← HCVR, RFR, ADIF calculators
│   │   └── baselines/
│   │       └── rule_based.py       ← RuleBasedController ✅ DONE
│   └── scripts/
│       ├── run_scenario.py
│       ├── run_all_baselines.py
│       ├── test_*.py               ← unit tests
│       └── visualize_network.py
│
└── PPT_Report_templates/
    ├── Minor project...Report.docx
    ├── Progress PPT.ppt
    └── Project_Evaluation_Rubric.pdf
```

---

## 10. What Still Needs Building

### Priority Order for Week 4

#### Step 1: Single-LLM Agent (B2) — `sim/src/baselines/single_llm.py`
- One LLM instance (GPT-4o-mini or Llama 3.1 8B)
- Receives full state as one prompt
- Has access to all 7 tools as function-calls
- Same DecisionCard output schema
- Same Safety Guard applied

```python
# Rough structure
class SingleLLMAgent:
    def __init__(self, tools: AgentTools, model: str = "gpt-4o-mini"):
        ...
    def respond_to_disruption(self, scenario: ScenarioConfig) -> list[DecisionCard]:
        # Build one big prompt with network state + fleet state + requests
        # Call LLM with tools
        # Validate each decision via Safety Guard
        # Return DecisionCards
```

#### Step 2: Multi-Agent System (B3) — `sim/src/agents/`
- `traffic_agent.py` — scoped to network/disruption tools only
- `fleet_agent.py` — scoped to fleet tools only
- `routing_agent.py` — takes Traffic + Fleet proposals, runs path finding
- `coordinator_agent.py` — synthesizes all proposals → emits DecisionCard
- `multi_agent_pipeline.py` — orchestrates the 4-agent flow

#### Step 3: Full Comparison Runner — `sim/scripts/run_full_comparison.py`
- Run all 3 systems (B1, B2, B3) on all 5 scenarios (L1–L5)
- Collect HCVR, RFR, ADIF, Latency, Token Cost for each run
- Output comparison table + CSVs

#### Step 4: MAST Failure Logging (for B3 only)
- Log every B3 failure by category (System Design / Inter-Agent Misalignment / Task Verification)
- Apply targeted fixes
- Re-run and measure improvement (target: ≥10% RFR improvement → H₅)

### Framework Decision (Still Open)
The Week 1 slides asked mentors: **LangGraph or CrewAI?**
- **LangGraph** — graph-based orchestration, explicit state management, good for complex flows. Better control.
- **CrewAI** — higher abstraction, faster to prototype, built-in role/tool assignment.
- **Recommendation:** Start with LangGraph for the explicitness needed for research logging.

---

## 11. Demo App Plan

**Stack:** Next.js 15 + TypeScript + Tailwind CSS  
**Location:** `04-Minor/demo/`  
**See:** `project.md` for full detail

### 5 Pages
1. **Home** — research overview, timeline, hypotheses
2. **Simulator** — animated 4×4 grid canvas, scenario selector (L1–L5), disruption visualization, route playback
3. **Results** — 3-system comparison charts (B1 real, B2/B3 projected), HCVR/RFR/ADIF per scenario
4. **Architecture** — agent pipeline diagram, Safety Guard detail, DecisionCard example
5. **Research** — 5 paper cards, gap matrix, hypotheses

### Data Strategy
- **B1:** 100% real from `sim/results/` JSON files (hardcoded in `lib/data.ts`)
- **B2 projected:** ~20% HCVR, ~78% RFR (hallucination-prone without guard) — labeled "Projected"
- **B3 projected:** ~0% HCVR (guard eliminates violations), ~88% RFR, 3.5× latency — labeled "Projected"

---

## 12. Key Numbers to Remember

| Number | Context |
|---|---|
| **>60%** | Existing ITS research that focuses only on AV perception (Wandelt 2024) — proves our gap |
| **58.9%** | Delay reduction achieved by Wu & Zeng 2026 on rail with 4 LLM agents |
| **41–87%** | Task failure rate across unverified MAS frameworks (Cemri/MAST 2025) |
| **+15.6%** | Success improvement from architectural fixes alone, same LLM (MAST) |
| **41.8%** | MAS failures caused by System Design Issues (most common MAST category) |
| **1,642** | Execution traces analyzed in the MAST paper |
| **4×4** | Grid size of our synthetic test network (16 nodes, ~48 edges) |
| **L1–L5** | Our 5 graduated complexity levels (Simple → Stress Test) |
| **0%** | B1 HCVR across all scenarios (Safety Guard works) |
| **44.4%** | B1 RFR at L5 — rule-based breaks down under cascading disruptions |
| **4–9ms** | B1 latency (will be compared against B2/B3 which are orders of magnitude slower) |
| **15%** | SoC safety margin in the Safety Guard |
| **H₃** | The key hypothesis — finding the complexity crossover point where B3 > B2 |

---

## Quick Reference: Where to Find Things

| Question | Answer |
|---|---|
| What is the research question? | Section 2 of this doc; `week-2/research-gap-and-design.md` §4 |
| Why these 5 papers? | Section 3 of this doc; `week-1/work.md` §3 |
| What is the research gap? | Section 4 of this doc; `week-2/research-gap-and-design.md` §2–3 |
| How does the Safety Guard work? | Section 5 of this doc; `sim/src/tools/agent_tools.py` Tool 7 |
| What are the 5 disruption scenarios? | `sim/scenarios/*.json` |
| What are the B1 real results? | Section 8 of this doc; `sim/results/*.json` |
| How is B2 (single-LLM) different from B3? | Section 5 + Section 6 of this doc |
| What's the full Python implementation? | `week-3/work.md` (1600+ lines of documented code) |
| What's the demo app plan? | `project.md` |
| What needs to be built next? | Section 10 of this doc |
