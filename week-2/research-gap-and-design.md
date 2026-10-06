# Research Gap Analysis & Experimental Design
## Agentic AI for Transport Disruption Management
**Document Purpose:** Narrow down existing work, identify the concrete research gap, and define every component needed before implementation begins.  
**Date:** September 3, 2026 | **Status:** Phase 1 Deliverable for Mentor Review

---

## Table of Contents
1. [Narrowed Literature Landscape](#1-narrowed-literature-landscape)
2. [What Exists vs What's Missing — The Gap Matrix](#2-what-exists-vs-whats-missing--the-gap-matrix)
3. [Concrete Research Gap Statement](#3-concrete-research-gap-statement)
4. [Research Question & Hypotheses](#4-research-question--hypotheses)
5. [Agent Roles & Architecture](#5-agent-roles--architecture)
6. [Disruption Scenarios](#6-disruption-scenarios)
7. [Baselines](#7-baselines)
8. [Evaluation Metrics](#8-evaluation-metrics)
9. [Implementation-Ready Summary](#9-implementation-ready-summary)

---

## 1. Narrowed Literature Landscape

We surveyed 5 core papers (in `research-work/`) plus 3 newly identified works from 2026. Below, we classify every relevant work into **what it actually does** and **where it stops** — because that boundary is our research gap.

### Thread A: Domain Surveys (What LLMs Can Do in ITS)

These papers prove LLMs are capable of transportation reasoning but do NOT build or benchmark multi-agent disruption systems on road networks.

| # | Paper | Venue | What It Proves | Where It Stops |
|---|-------|-------|----------------|----------------|
| 1 | **Mahmud et al.** (2025) — *Integrating LLMs with ITS* | IEEE T-ITS, Vol.26 No.5 | LLMs have strong contextual reasoning for ITS tasks (traffic control, route recommendation, incident management). | Identifies latency & hallucination barriers but builds NO multi-agent system. No benchmarks. |
| 2 | **Nie, Sun & Ma** (2025) — *LLM4TR Taxonomy* | Elsevier AIT / arXiv:2503.21411 | Establishes canonical 4-role taxonomy: Info Processors, Knowledge Encoders, Component Generators, **Decision Facilitators**. | Purely taxonomic — zero implementation, zero evaluation. |
| 3 | **Wandelt et al.** (2024) — *LLMs in ITS Review* | MDPI Applied Sciences, Vol.14 | Systematic review of 130+ papers. **>60% focus on AV perception**. Dynamic disruption management is wide open. | Quantifies the gap but fills none of it. |

**Takeaway from Thread A:** LLMs are proven capable of ITS reasoning, our project falls under the *Decision Facilitator* category (Nie et al.), and >60% of existing work ignores operational disruption management entirely (Wandelt et al.). The field is calling for exactly what we're building.

---

### Thread B: Multi-Agent Systems & Failure Engineering

These papers are the closest architectural precedents to our work.

| # | Paper | Venue | What It Builds | Where It Stops |
|---|-------|-------|----------------|----------------|
| 4 | **Wu & Zeng** (2026) — *LLM-Driven Multi-Agent Rail Disruption* | MDPI Mathematics, Vol.14 | 4-agent system (Dispatch, Station, Transfer, Information) + Safety-Review Agent on Shanghai Metro Line 2. **58.9% delay reduction, 32.6% queue reduction.** | **1D linear rail corridor only.** Fixed action library. Gains reverse at <25% transfer capacity. No road-network graph. No comparative baseline against single-LLM. |
| 5 | **Cemri et al.** (2025) — *MAST Failure Taxonomy* | NeurIPS 2025 (UC Berkeley) | Analyzed **1,642 traces** across 7 MAS frameworks. 41–87% task-failure rate. +15.6% success from architectural fixes alone. | General-purpose MAS failures — **never applied to transportation domain.** No domain-specific failure logging. |

**Takeaway from Thread B:** Wu & Zeng is our closest predecessor but is locked to 1D rail with no single-LLM comparison. MAST proves failures are architectural (not model-limited) but has never been measured in transport decision-support.

---

### Thread C: Newly Identified Related Works (2026)

Through additional literature search, we identified 3 more works that are adjacent to our project but still leave our gap open:

| # | Paper/System | Venue/Source | What It Does | Where It Stops |
|---|-------------|-------------|-------------|----------------|
| 6 | **TrafficGen** (2026) — *Multi-Agent Generative AI for Smart Mobility* | Frontiers (Aug 2026) | Council-of-Agents architecture using Gemini 2.5 Flash + LangGraph. 46.9% wait-burden reduction. 100% emergency vehicle pre-emption success. | **Single intersection, signal control only.** No fleet dispatch, no vehicle routing, no network-level disruption management. |
| 7 | **Tran & Kiela** (2026) — *Single-Agent LLMs Outperform Multi-Agent Under Equal Token Budgets* | arXiv (2026) | Budget-controlled comparison shows SAS matches/outperforms MAS on multi-hop reasoning when thinking-tokens are normalized. Uses Data Processing Inequality argument. | **General reasoning benchmarks only.** Never tested on domain-specific tool-use tasks like transport disruption where role-specialization may genuinely help. |
| 8 | **REALM-Bench** (2026) — *Reliable Multi-Agent Logistics Management Benchmark* | arXiv / GitHub (2026) | Benchmark suite including Urban Ride-Sharing (URS) scenarios with disruption handling. Tests LangGraph, AutoGen, CrewAI. | Evaluates agent frameworks on **logistics planning**, not on real-time disruption response with fleet state, battery constraints, and safety-guard verification. No rule-based baseline comparison. |

**Takeaway from Thread C:** 
- TrafficGen proves multi-agent LLM architectures work for traffic but only at the micro-level (single intersection). Our work operates at the **network level**.
- Tran & Kiela's budget-controlled finding is critical — we MUST normalize token budgets when comparing single vs multi-agent, otherwise our results are scientifically meaningless.
- REALM-Bench is the closest benchmark but doesn't test our specific disruption-response problem with hard physical constraints.

---

## 2. What Exists vs What's Missing — The Gap Matrix

| Dimension | What EXISTS in Literature | What is MISSING (Our Gap) |
|-----------|--------------------------|---------------------------|
| **Network Type** | Rail corridors (Wu & Zeng), single intersections (TrafficGen) | **2D road-network graphs** with time-varying edge capacities, dynamic alternate detour loops |
| **Comparison Methodology** | MAS vs rule-based only (Wu & Zeng); SAS vs MAS on reasoning tasks (Tran & Kiela) | **3-way comparison** (Rule-based vs Single-LLM vs Multi-Agent LLM) on **identical transport disruption scenarios** |
| **Token Budget Control** | Tran & Kiela normalize tokens on reasoning benchmarks | **No budget-controlled comparison exists for transport tool-use tasks** |
| **Safety Verification** | Wu & Zeng use a Safety-Review Agent concept | **No BFS + Pydantic deterministic guard** benchmarked with quantified HCVR on road networks |
| **Failure Taxonomy** | MAST catalogs 14 failure modes across general MAS | **MAST failure modes never logged/measured in transport MAS** |
| **Cost-Latency-Quality** | Acknowledged as important (Mahmud et al.) | **Never quantified** for transport disruption control specifically |
| **Disruption Complexity Scaling** | Single-disruption scenarios (Wu & Zeng) | **No graduated disruption complexity** (single → cascading → multi-modal) |

---

## 3. Concrete Research Gap Statement

> **No existing study evaluates multi-agent LLM systems against both single-LLM and rule-based baselines for real-time disruption management on 2D road-network graphs with time-varying capacities, fleet state constraints, and deterministic safety verification — while controlling for token budget and measuring cost-latency-quality trade-offs.**

### Sub-Gaps We Fill:
1. **Network Domain Gap:** First multi-agent LLM disruption study on 2D road networks (vs 1D rail / single intersection).
2. **3-Way Benchmark Gap:** First controlled comparison of Rule-Based vs Single-LLM vs Multi-Agent LLM under identical road disruptions.
3. **Budget-Controlled Transport Evaluation:** First to normalize token budgets when comparing SAS vs MAS on domain-specific transport tool-use.
4. **MAST Transport Application:** First to log and measure MAST's 14 multi-agent failure modes in a transportation decision-support context.
5. **Cost-Latency-Quality Quantification:** First to measure the trade-off surface between decision feasibility, inference latency, and API token cost for road disruption control.

---

## 4. Research Question & Hypotheses

### Primary Research Question

> ***"When does multi-agent LLM coordination actually improve transport-disruption decisions compared with a single LLM or traditional rule-based approach on 2D road networks, and is the improvement worth the additional computational and financial cost?"***

This directly answers Dr. Daoud's scientific framing — we are NOT just showing agents can communicate; we are finding the **boundary conditions** where multi-agent becomes worth it.

### Testable Hypotheses

| ID | Hypothesis | Measurable Target | How We Test |
|----|-----------|-------------------|-------------|
| **H₁** | Role specialization + deterministic safety guard reduces hard-constraint violations compared to both single-LLM and rule-based baselines. | **HCVR = 0%** for multi-agent w/ safety guard vs >0% for single-LLM | Compare HCVR across all 3 systems on same scenarios |
| **H₂** | Multi-agent coordination incurs a measurable latency and token overhead compared to single-LLM and rule-based. | **2.5× to 4.0× latency overhead** vs rule-based; **1.5× to 2.5× token cost** vs single-LLM | Measure wall-clock time and token counts per scenario |
| **H₃** | Multi-agent outperforms single-LLM on complex (cascading/multi-disruption) scenarios but NOT on simple (single-disruption) scenarios. | **Crossover point** in RFR and ADIF as disruption complexity increases | Run graduated complexity scenarios and plot performance curves |
| **H₄** | Prompt context decomposition across specialized roles reduces per-agent prompt size, enabling better reasoning on complex state. | Cumulative token growth: **O(N·K)** for multi-agent vs **O(N²)** for single-LLM, where K = local context size | Measure prompt token counts as network size scales |
| **H₅** | Architectural fixes guided by MAST failure categories improve multi-agent task success by ≥10%. | **≥10% improvement** in RFR after targeted fixes | Log failures by MAST category, apply fixes, re-evaluate |

### Why H₃ Is the Key Hypothesis
H₃ encodes Dr. Daoud's core scientific question. If multi-agent is ALWAYS better, that's interesting. If it's NEVER better, that's also interesting. But the most scientifically valuable finding is **identifying the complexity threshold** where multi-agent coordination begins to pay off — this is the contribution that makes the paper publishable.

---

## 5. Agent Roles & Architecture

### 5.1 The Three Specialized Agents + Coordinator

Each agent has a **single responsibility**, a **restricted information scope**, and access to **specific tools only**.

| Agent | Role | Information Scope | Tools Available |
|-------|------|-------------------|-----------------|
| **Traffic Agent** (Network Monitor) | Tracks road graph topology, edge capacities, congestion state. Identifies which edges are disrupted and which alternate paths exist. | Graph G=(V,E), edge capacities C(e,t), current congestion levels | `get_network_state()`, `get_disrupted_edges()`, `find_alternate_paths()` |
| **Fleet Agent** (Resource Manager) | Tracks vehicle positions, battery/fuel SoC, capacity, and availability. Identifies which vehicles can be dispatched. | Vehicle state matrix S_v(t), fleet positions, SoC levels | `get_vehicle_status()`, `get_available_vehicles()`, `check_vehicle_range()` |
| **Routing Agent** (Path Synthesizer) | Proposes candidate detour routes connecting origins to destinations, avoiding disrupted edges. Estimates travel times. | Receives disrupted-edge info from Traffic Agent, vehicle locations from Fleet Agent | `shortest_path()`, `estimate_travel_time()`, `propose_routes()` |
| **Coordinator Agent** (Arbitration) | Synthesizes proposals from all 3 agents into a unified action plan (DecisionCard JSON). Resolves conflicts. | Receives proposals from all agents | `assign_vehicle()`, `create_decision_card()`, `submit_to_safety_guard()` |

### 5.2 Deterministic Safety-Review Guard (Non-LLM)

This is a **pure Python module** — no LLM involved. It runs after the Coordinator emits a proposed DecisionCard:

| Check | What It Validates | Rejection Action |
|-------|-------------------|-----------------|
| **BFS Reachability** | Every edge in proposed route R_k has capacity C(e,t) > 0 and exists in graph G | Reject → Fallback to SOP route |
| **SoC Sufficiency** | Vehicle battery/fuel can cover route length L(R_k) + 15% safety margin | Reject → Assign different vehicle or fallback |
| **Capacity Check** | Vehicle passenger capacity ≥ assigned passenger count | Reject → Split assignment or fallback |
| **Pydantic Schema** | Output conforms to strict DecisionCard JSON schema | Reject → Request re-generation |

### 5.3 Information Flow Diagram

```
DISRUPTION EVENT D(t)
        │
        ▼
┌───────────────────────────────────────────────┐
│            SPECIALIZED AGENT LAYER            │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Traffic  │  │  Fleet   │  │ Routing  │    │
│  │  Agent   │  │  Agent   │  │  Agent   │    │
│  │          │  │          │  │          │    │
│  │ Scope:   │  │ Scope:   │  │ Scope:   │    │
│  │ Graph G  │  │ Fleet S  │  │ Paths R  │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
│       │              │              │          │
│       └──────────────┼──────────────┘          │
│                      │                         │
│                      ▼                         │
│          ┌───────────────────┐                 │
│          │   Coordinator     │                 │
│          │   Agent           │                 │
│          │   (Synthesize &   │                 │
│          │    Emit JSON)     │                 │
│          └────────┬──────────┘                 │
└───────────────────┼───────────────────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │  SAFETY-REVIEW GUARD  │
        │  (Deterministic)      │
        │  • BFS Reachability   │
        │  • SoC Check          │
        │  • Capacity Check     │
        │  • Pydantic Schema    │
        └────────┬──────────────┘
                 │
          ┌──────┴──────┐
          │             │
     [PASS]        [FAIL]
          │             │
          ▼             ▼
    Execute Plan   Fallback SOP
```

### 5.4 Single-LLM Agent (Baseline 2) Architecture
For fair comparison, the Single-LLM agent receives **all the same tools** as the multi-agent system, but in a single prompt with full graph + fleet + request state:

- Tools: `get_network_state()`, `get_vehicle_status()`, `get_requests()`, `shortest_path()`, `estimate_travel_time()`, `assign_vehicle()`, `validate_plan()`
- Same Safety-Review Guard applied to its output
- Same DecisionCard JSON schema required

---

## 6. Disruption Scenarios

### 6.1 Four Disruption Types

| Type | Mechanism in Simulation | Parameter |
|------|------------------------|-----------|
| **Road Closure** | Remove edge from graph: `G.remove_edge(u, v)` → C(e,t) = 0 | Which edge(s), duration |
| **Congestion** | Increase travel time: `G[u][v]['weight'] *= congestion_factor` | Factor γ ∈ [2.0, 5.0], affected edges |
| **Vehicle Breakdown** | Set vehicle status to unavailable: `vehicle.status = 'broken'` | Which vehicle(s), timing |
| **Demand Surge** | Inject additional OD requests in specific area/time | Surge multiplier, area, time window |

### 6.2 Graduated Complexity Levels

This is how we test H₃ (the crossover hypothesis):

| Level | Name | Disruptions | Description |
|-------|------|-------------|-------------|
| **L1** | Simple | 1 road closure | Single link removed. One alternate path exists. Basic rerouting. |
| **L2** | Moderate | 1 closure + 1 congestion | Closure on primary route + congestion on obvious detour. Requires smarter path selection. |
| **L3** | Compound | 1 closure + 1 congestion + 1 breakdown | Primary route blocked, detour congested, AND one vehicle unavailable. Fleet rebalancing needed. |
| **L4** | Cascading | 2 closures + 1 congestion + 1 breakdown + 1 demand surge | Multiple simultaneous disruptions with demand spike. Tests full coordination capacity. |
| **L5** | Stress Test | 3 closures + 2 congestion + 2 breakdowns + 1 surge | Near-collapse scenario. Tests graceful degradation and fallback behavior. |

### 6.3 Scenario Reproducibility
Each scenario is defined as a **deterministic JSON file** with fixed random seeds:
```json
{
  "scenario_id": "L3_compound_001",
  "network_seed": 42,
  "disruptions": [
    {"type": "road_closure", "edge": ["N5", "N12"], "time": 0},
    {"type": "congestion", "edge": ["N3", "N8"], "factor": 3.0, "time": 0},
    {"type": "vehicle_breakdown", "vehicle_id": "V3", "time": 2}
  ],
  "requests": [
    {"id": "R1", "origin": "N1", "destination": "N15", "time": 0},
    {"id": "R2", "origin": "N4", "destination": "N10", "time": 1}
  ]
}
```

---

## 7. Baselines

### 7.1 Three-System Comparison

| System | Decision Maker | Tools | Safety Guard | What It Tests |
|--------|---------------|-------|-------------|---------------|
| **B1: Rule-Based SOP** | Deterministic heuristic (shortest available path + nearest available vehicle) | Same Python functions (called directly, no LLM) | Same guard applied | Floor performance — what a simple algorithm achieves |
| **B2: Single-LLM Agent** | One LLM with full state in context + all tools available | Same tools as function-calls | Same guard applied | Whether one LLM with tools can reason about disruptions |
| **B3: Multi-Agent LLM** | 4 specialized LLM agents with scoped tools | Tools partitioned across agents | Same guard applied | Whether role decomposition improves decisions |

### 7.2 Controlled Variables (Critical for Scientific Validity)

| Variable | How We Control It |
|----------|------------------|
| **Scenarios** | Identical JSON scenario files run against all 3 systems |
| **Tools** | Exact same Python functions — B1 calls them directly, B2/B3 call them via LLM tool-use |
| **Safety Guard** | Same deterministic guard applied to outputs of all 3 systems |
| **LLM Model** | Same model (e.g., GPT-4o-mini) for both B2 and B3 |
| **Token Budget** | Measured and reported; budget-controlled analysis per Tran & Kiela (2026) |
| **Random Seeds** | Fixed for network generation and disruption injection |

### 7.3 Rule-Based Baseline (B1) Algorithm

```
FUNCTION rule_based_respond(disruption, network, fleet, requests):
    1. Update network graph (remove/modify disrupted edges)
    2. FOR each pending request R:
        a. Compute shortest_path(R.origin, R.destination) on updated graph
        b. IF no path exists → mark R as UNSERVED
        c. ELSE:
           i.   Find nearest available vehicle V with sufficient SoC
           ii.  IF no vehicle available → mark R as UNSERVED
           iii. ELSE → assign V to R via shortest path
    3. Validate all assignments via Safety Guard
    4. Return DecisionCard with assignments and metrics
```

---

## 8. Evaluation Metrics

### 8.1 Six Core Metrics

| # | Metric | Formula / Definition | What It Measures | Target |
|---|--------|---------------------|-----------------|--------|
| 1 | **Hard Constraint Violation Rate (HCVR %)** | (Infeasible actions ÷ Total proposed actions) × 100 | Safety — are proposed actions physically valid? | 0% for B3 w/ guard |
| 2 | **Request Fulfillment Rate (RFR %)** | (Successfully served requests ÷ Total affected requests) × 100 | Effectiveness — how many passengers get served? | Higher is better |
| 3 | **Average Delay Inflation Factor (ADIF)** | Actual travel time ÷ Free-flow undisrupted travel time | Quality — how much delay does the solution add? | Closer to 1.0 is better |
| 4 | **Execution Latency (T_exec)** | Wall-clock seconds from disruption input to DecisionCard output | Speed — can it respond in real-time? | Lower is better |
| 5 | **Token Cost ($/scenario)** | Total prompt + completion tokens × API pricing | Cost — is multi-agent economically viable? | Measured, not targeted |
| 6 | **Infeasible Decision Rate (IDR %)** | (Decisions rejected by Safety Guard ÷ Total decisions proposed) × 100 | LLM reliability — how often does the LLM propose invalid plans? | Lower is better |

### 8.2 MAST Failure Logging (For Multi-Agent System Only)

For every multi-agent run, we log failures by MAST category:

| MAST Category | % of Failures (Cemri et al.) | What We Log |
|--------------|------------------------------|-------------|
| System Design Issues | 41.8% | Prompt vagueness, redundant agent loops, unclear role boundaries |
| Inter-Agent Misalignment | 36.9% | Misinterpreted messages, ignored agent proposals, conflicting actions |
| Task Verification Failures | 21.3% | Unverified execution, missing validation, schema violations |

### 8.3 Budget-Controlled Analysis

Following Tran & Kiela (2026), we perform an additional analysis:
- **Plot:** RFR vs Total Tokens Used for both B2 (single-LLM) and B3 (multi-agent)
- **Question:** At equal token budgets, does multi-agent still outperform single-LLM?
- **Method:** Give single-LLM agent additional reasoning turns (chain-of-thought) to match multi-agent token consumption, then compare RFR and ADIF

---

## 9. Implementation-Ready Summary

### What We Have Locked Down (Ready for Implementation)

| Component | Status | Details |
|-----------|--------|---------|
| Research Question | ✅ Defined | "When does multi-agent LLM coordination improve transport-disruption decisions vs single-LLM/rule-based, and is it worth the cost?" |
| Hypotheses | ✅ 5 testable hypotheses | H₁–H₅ with measurable targets |
| Agent Roles | ✅ 4 agents defined | Traffic, Fleet, Routing, Coordinator + Safety Guard |
| Disruption Types | ✅ 4 types | Road closure, congestion, vehicle breakdown, demand surge |
| Complexity Levels | ✅ 5 levels (L1–L5) | Simple → Stress Test |
| Baselines | ✅ 3 systems | Rule-based, Single-LLM, Multi-Agent LLM |
| Metrics | ✅ 6 core + MAST logging | HCVR, RFR, ADIF, T_exec, $/scenario, IDR |
| Controlled Variables | ✅ Defined | Same tools, same guard, same model, same scenarios, token budget tracking |

### Next Step: Build the Transport Environment

Per Dr. Daoud's directive, the next implementation phase is:

1. **Build road network simulation** in Python/NetworkX (nodes, links, travel times)
2. **Add vehicles** (location, capacity, SoC, status)
3. **Add transport requests** (origin, destination, demand, time)
4. **Implement 4 disruption mechanisms** (closure, congestion, breakdown, surge)
5. **Create reproducible scenario JSON files** (L1–L5)
6. **Implement 7 core tool functions** (`get_network_state()`, `get_vehicle_status()`, etc.)
7. **Build rule-based baseline (B1)** that produces valid plans
8. **Auto-calculate metrics** (HCVR, RFR, ADIF) after each run

**DO NOT start LLM implementation until this environment works reliably.**

---

## References

1. Mahmud et al. (2025). *Integrating LLMs with ITS.* IEEE T-ITS, Vol.26, No.5.
2. Nie, Sun & Ma (2025). *LLM4TR: Large Language Models for Transportation.* Elsevier AIT. arXiv:2503.21411.
3. Wandelt et al. (2024). *Large Language Models in ITS: A Review.* MDPI Applied Sciences, Vol.14, Art.7455.
4. Wu & Zeng (2026). *LLM-Driven Multi-Agent Coordinated Control for Urban Rail Disruption.* MDPI Mathematics, Vol.14, Art.2839.
5. Cemri et al. (2025). *Why Do Multi-Agent LLM Systems Fail? (MAST).* NeurIPS 2025. arXiv:2503.13657.
6. TrafficGen (2026). *Multi-Agent Generative AI for Smart Mobility.* Frontiers, Aug 2026.
7. Tran & Kiela (2026). *Single-Agent LLMs Outperform Multi-Agent Under Equal Token Budgets.* arXiv.
8. REALM-Bench (2026). *Reliable Multi-Agent Logistics Management Benchmark.* arXiv / GitHub.
