# Master Project & Presentation Guide
## Agentic AI for Transport Disruption Management
**Project Theme:** Cooperative Multi-Agent Intelligence for Transportation (Direction 1 — Agentic AI)  
**Course / Level:** Semester 5 Minor Project (IIITNR)  
**Mentors:** Dr. Alaa DAOUD (INSA Hauts-de-France) & Dr. Srinivasa K G (IIITNR)  
**Target Presentation:** August 25, 2026  
**Presentation Files:** `cl.pptx` / `cl_presentation.pptx` (11 Slides) & `Week1_Presentation.pptx` (12 Slides)

---

## Table of Contents
1. [Executive Summary & The Big Picture](#1-executive-summary--the-big-picture)
2. [Problem Formulation & Operational Challenges](#2-problem-formulation--operational-challenges)
3. [Deep-Dive Literature Review (The 5 Core Papers)](#3-deep-dive-literature-review-the-5-core-papers)
4. [Literature Synthesis & The Research Gap](#4-literature-synthesis--the-research-gap)
5. [Proposed System Architecture & Safety Review Guard](#5-proposed-system-architecture--safety-review-guard)
6. [Experimental Design, Baselines & Evaluation Metrics](#6-experimental-design-baselines--evaluation-metrics)
7. [Data Plan & Candidate Benchmark Datasets](#7-data-plan--candidate-benchmark-datasets)
8. [8-Week Execution Roadmap](#8-8-week-execution-roadmap)
9. [Slide-by-Slide Speaker Script (For `cl.pptx`)](#9-slide-by-slide-speaker-script-for-clpptx)
10. [Anticipated Technical Questions & Bulletproof Answers](#10-anticipated-technical-questions--bulletproof-answers)

---

## 1. Executive Summary & The Big Picture

### The Elevator Pitch (30-Second Overview)
> *"When a sudden shock hits an urban road network—such as a multi-lane highway collapse, severe vehicle breakdown, or localized flood—traditional Standard Operating Procedures (SOPs) break down because they rely on rigid lookup tables. Conversely, prompting a single monolithic Large Language Model (LLM) leads to hallucinated routes on non-existent road links and unsafe vehicle dispatch commands due to context window overload.
>
> Our project investigates whether decomposing disruption response into **role-isolated specialized LLM agents** (Traffic, Fleet, Routing, and Coordinator) bound by a **deterministic Safety-Review Guard** can eliminate hard-constraint violations while operating under real-time latency and API token cost budgets."*

### Key Research Questions
* **Program Question:** *"When does cooperation improve transportation systems?"*
* **Our Specific Project Question:** *"Can specialized LLM agents make better transport-disruption decisions than a single LLM agent or a rule-based controller in dynamic road-network settings?"*

### Core Research Hypotheses
* **$H_1$ (Feasibility & Constraint Improvement):** Role specialization + deterministic safety verification reduces hard constraint violations by $>40\%$ compared to monolithic LLMs and static SOPs.
* **$H_2$ (Latency Overhead Trade-off):** Multi-agent coordination incurs a $2.5\times \text{ to } 4.0\times$ execution latency overhead compared to rule-based baselines, defining a real-time operational envelope.
* **$H_3$ (Token Efficiency):** Prompt context decomposition across specialized roles reduces cumulative prompt token growth from $O(N^2)$ to $O(N \cdot K)$, where $K$ is local agent context size.

---

## 2. Problem Formulation & Operational Challenges

### 2.1 Mathematical Network Graph Formulation
We model the urban road transport system as a time-dependent directed graph $G = (V, E, W)$:
* **$V$ (Vertices):** Intersections, transit hubs, and vehicle dispatch depots.
* **$E$ (Edges):** Road segments connecting intersections.
* **$C(e, t)$ (Time-varying Edge Capacity):** The maximum vehicle throughput per unit time on edge $e \in E$ at time $t$.
* **$S_v(t)$ (Vehicle State Matrix):** Fleet position, fuel/battery state of charge (SoC), and current task assignment for vehicle $v$.
* **$Q(t)$ (Passenger / Cargo Demand Queue):** Origin-destination (OD) pairs waiting for rerouting or dispatch.

### 2.2 Disruption Injection Vector $D(t)$
A disruption event $D(t)$ is modeled as a sudden parameter drop on network edges:
$$C(e_{\text{disrupted}}, t) \leftarrow 0 \quad \text{(Full Closure)}$$
$$C(e_{\text{congested}}, t) \leftarrow \gamma \cdot C(e, t_0) \quad \text{where } \gamma \in (0, 0.3] \quad \text{(Bottleneck/Capacity Reduction)}$$

### 2.3 Why Baseline Systems Fail
1. **Rule-Based SOP Controllers (Static Dijkstra / Fixed Lookup):**
   * Pre-programmed rules cannot adapt when multiple simultaneous disruptions occur (e.g., an accident on an alternate detour route).
   * They lack contextual reasoning regarding fleet battery state and passenger queue priority.
2. **Monolithic Single-LLM Agents:**
   * Feeding full road graph topologies, vehicle states, and congestion metrics into a single LLM prompt causes **context erosion** and **prompt clutter**.
   * The LLM regularly hallucinates non-existent edges or generates routes that violate physical vehicle capacity constraints.

---

## 3. Deep-Dive Literature Review (The 5 Core Papers)

We ground our project in 5 foundational research papers across two primary threads: **ITS Domain Surveys** and **Multi-Agent System Architecture & Failures**.

```
                           +----------------------------------+
                           |     LITERATURE FOUNDATION        |
                           +----------------------------------+
                                            |
         +----------------------------------+----------------------------------+
         |                                                                     |
[Domain & Taxonomy Surveys]                                           [Multi-Agent & Failure Engineering]
  1. Mahmud et al. (IEEE T-ITS 2025)                                    4. Wu & Zeng (MDPI Math 2026)
     - LLM context in ITS; latency bottlenecks                           - Rail corridor disruption precursor
  2. Nie et al. (Elsevier AIT 2025)                                    5. Cemri et al. (NeurIPS 2025 - MAST)
     - LLM4TR: Decision Facilitator role                                 - 1,642 trace failure taxonomy
  3. Wandelt et al. (MDPI App. Sci. 2024)
     - 130+ paper review: >60% AV perception gap
```

---

### Paper 1: Mahmud et al. (May 2025)
* **Full Title:** *Integrating Large Language Models with Intelligent Transportation Systems: A Survey*
* **Publication & Date:** *IEEE Transactions on Intelligent Transportation Systems (T-ITS)*, Vol. 26, No. 5, May 2025.
* **Discovery Platform / Source:** IEEE Xplore / Google Scholar / Scopus.
* **Core Contribution:** Provides an architecture-to-application survey evaluating foundation models (GPT-4, BERT, T5) across traffic control, route recommendation, and incident management.
* **Key Finding:** Proves LLMs possess strong contextual reasoning for complex transportation prompts, but highlights **real-time inference latency** and **non-deterministic outputs** as major deployment barriers.
* **Relevance to Our Work:** Justifies using LLMs for high-level decision support while highlighting the critical need for a deterministic verification guard.

---

### Paper 2: Nie, Sun & Ma (June 2025)
* **Full Title:** *LLM4TR: Large Language Models for Transportation — A Survey and Taxonomy*
* **Publication & Date:** *Artificial Intelligence for Transportation (Elsevier)*, June 2025 / `arXiv:2503.21411`.
* **Discovery Platform / Source:** Elsevier ScienceDirect / arXiv / Google Scholar / GitHub (`awesome-llm4tr`).
* **Core Contribution:** Establishes the canonical **LLM4TR taxonomy**, categorizing LLM transportation roles into 4 distinct dimensions:
  1. *Information Processors* (Parsing raw sensor/text data)
  2. *Knowledge Encoders* (Domain rule retention)
  3. *Component Generators* (Code/simulation generation)
  4. ***Decision Facilitators*** (Strategic disruption management & routing)
* **Relevance to Our Work:** Directly positions our project under the **Decision Facilitators** category.

---

### Paper 3: Wandelt et al. (August 2024)
* **Full Title:** *Large Language Models in Intelligent Transportation Systems: A Review*
* **Publication & Date:** *MDPI Applied Sciences*, Vol. 14, Issue 17, Art. 7455, August 2024.
* **Discovery Platform / Source:** MDPI Open Access / Web of Science (SCIE) / Google Scholar.
* **Core Contribution:** Systematic review of 130+ papers analyzing LLM applications across autonomous vehicles, traffic management, safety, and tourism.
* **Key Finding:** **Over 60% of existing research focuses on single autonomous vehicle perception or basic Q&A interaction.** Dynamic multi-vehicle road network disruption management remains wide open.
* **Relevance to Our Work:** Quantifies and proves our primary research gap to the mentors.

---

### Paper 4: Wu & Zeng (August 2026) — *Closest Precedent*
* **Full Title:** *LLM-Driven Multi-Agent Coordinated Control for Urban Rail Disruption Management*
* **Publication & Date:** *MDPI Mathematics*, Vol. 14, Issue 15, Art. 2839, August 2026 (Tongji University & Peking University).
* **Discovery Platform / Source:** MDPI Open Access / Google Scholar / Scopus.
* **Core Architecture:** Evaluated a 4-agent system (Dispatch, Station, Transfer, Information) on Shanghai Metro Line 2.
* **Quantitative Results:**
  * **$58.9\%$ average total-delay reduction** compared to standard rule-based controllers (Baseline B4).
  * **$32.6\%$ average peak transfer-queue reduction**.
* **Key Limitation Identified:** **Gains reversed once transfer capacity dropped below 25%** — proving that multi-agent coordination cannot fix physical capacity bottlenecks without alternative path rerouting.
* **Relevance to Our Work:** Serves as our primary architectural inspiration (Safety-Review Agent + DecisionCard payloads), but we extend their work from fixed 1D rail corridors to 2D urban road networks.

---

### Paper 5: Cemri et al. / UC Berkeley (October 2025) — *MAST Failure Taxonomy*
* **Full Title:** *Why Do Multi-Agent LLM Systems Fail? An Empirical Characterization of Failure Modes (MAST)*
* **Publication & Date:** *39th Conference on Neural Information Processing Systems (NeurIPS 2025)*, Datasets & Benchmarks Track, October 2025 / `arXiv:2503.13657`.
* **Discovery Platform / Source:** NeurIPS Proceedings (OpenReview) / arXiv / Google Scholar.
* **Key Empirical Data:**
  * Analyzed **1,642 execution traces** across 7 popular Multi-Agent System (MAS) frameworks.
  * Observed a shocking **$41\%$ to $87\%$ task-failure rate** across unverified multi-agent setups!
  * Showed a **$+9.4\%$ to $+15.6\%$ task-success improvement** purely by implementing targeted architectural fixes *without changing the underlying LLM model*.
* **Annotated Sample Failure Breakdown (210-trace sample):**
  * **$41.8\%$ System Design Issues** (Prompt vagueness, redundant loops, lack of role boundaries)
  * **$36.9\%$ Inter-Agent Misalignment** (Misinterpreted message passing, ignored agent inputs)
  * **$21.3\%$ Task Verification Failures** (Unverified execution, missing validation layer)
* **Relevance to Our Work:** Proves that **system failure is architectural, not a raw LLM limitation**. This justifies building our deterministic Pydantic JSON verification layer.

---

## 4. Literature Synthesis & The Research Gap

### 4.1 Comparative Literature Synthesis Matrix

| Paper & Authors | Publication & Source | Core Focus | Scientific Finding | Relevance to Our Project |
| :--- | :--- | :--- | :--- | :--- |
| **Mahmud et al.** (2025) | IEEE Trans. ITS<br>*(IEEE Xplore)* | LLMs in ITS Survey | Strong context reasoning; latency & hallucination are key challenges. | Justifies LLM usage; demands safety guard layer. |
| **Nie, Sun & Ma** (2025) | Elsevier AIT / arXiv<br>*(ScienceDirect)* | LLM4TR Taxonomy | Categorizes 4 LLM roles (Info, Knowledge, Generator, Facilitator). | Positions our work under *Decision Facilitators*. |
| **Wandelt et al.** (2024) | MDPI Applied Sci.<br>*(Web of Science)* | ITS Review (130+ papers) | >60% focus on AV perception; operational disruptions open. | Identifies and validates our core research gap. |
| **Wu & Zeng** (2026) | MDPI Mathematics<br>*(Tongji / PKU)* | Rail Disruption Control | 58.9% delay reduction using 4 agents + Safety Review on Metro Line 2. | Adopt Safety-Review Agent & DecisionCard JSON. |
| **Cemri et al.** (2025) | NeurIPS 2025<br>*(UC Berkeley / arXiv)* | MAST Failure Taxonomy | 1,642 traces show 41-87% failure rate; fixes yield +15.6% success. | Guides Pydantic schema validation & role isolation. |

---

### 4.2 The 4 Precise Research Gaps We Fill
1. **Network Domain Gap:** Existing multi-agent LLM disruption studies (e.g., Wu & Zeng 2026) focus exclusively on linear 1D rail corridors with fixed action libraries. No study evaluates multi-agent LLMs on **2D road-network graphs with time-varying edge capacities**.
2. **Comparative Benchmark Gap:** No open benchmark quantitatively compares **Rule-Based SOP Controllers**, **Monolithic Single LLMs**, and **Specialized Multi-Agent LLMs** under identical road network shocks.
3. **Failure Taxonomy Application Gap:** MAST's 14 multi-agent failure modes (Cemri et al. 2025) have never been measured or logged in a transportation decision-support context.
4. **Cost-Latency-Quality Quantification:** The trade-off between decision feasibility, real-time inference latency, and API token expense remains unquantified for road traffic disruption control.

---

## 5. Proposed System Architecture & Safety Review Guard

```
                                  USER DISRUPTION EVENT
                                            |
                                            v
              +-----------------------------------------------------------+
              |                  SPECIALIZED AGENT LAYER                  |
              |                                                           |
              |  +----------------+   +---------------+   +------------+  |
              |  | Traffic Agent  |   |  Fleet Agent  |   |Routing Ag. |  |
              |  | (Road Graph G) |   | (Fleet SoC S) |   |(Detours R) |  |
              |  +-------+--------+   +-------+-------+   +-----+------+  |
              +----------|--------------------|-----------------|---------+
                         |                    |                 |
                         +--------------------+-----------------+
                                              |
                                              v
                              +-------------------------------+
                              |       Coordinator Agent       |
                              |  (Synthesizes Joint Action)   |
                              +---------------+---------------+
                                              |
                                              v
                              +-------------------------------+
                              |    SAFETY-REVIEW GUARD        |
                              | (Deterministic BFS / Pydantic)|
                              +---------------+---------------+
                                              |
                               +--------------+--------------+
                               |                             |
                      [Passes Validation]           [Fails Validation]
                               |                             |
                               v                             v
                      Execute DecisionCard         Fallback SOP Reroute
```

### 5.1 The 4 Specialized Agents
1. **Traffic Agent (Network Monitor):** Tracks graph topology $G=(V,E)$, edge capacities $C(e,t)$, and pinpoints bottleneck congestion locations.
2. **Fleet Agent (Resource Manager):** Tracks vehicle positions, battery/fuel state-of-charge ($S_v(t)$), and fleet availability.
3. **Routing Agent (Path Synthesizer):** Proposes candidate detour paths ($R_k$) connecting origins and destinations around closed edges.
4. **Coordinator Agent (Arbitration Engine):** Reconciles proposals from Traffic, Fleet, and Routing agents into a unified, structured action plan.

### 5.2 Deterministic Safety-Review Guard
To guarantee zero hard-constraint violations, the Coordinator Agent's proposed JSON payload is passed to a **non-LLM Python Safety Guard**:
* **Breadth-First Search (BFS) Reachability Check:** Verifies that no edge $e$ in the proposed route $R_k$ has capacity $C(e, t) = 0$.
* **State-of-Charge (SoC) Check:** Verifies that vehicle battery energy is sufficient to complete route length $L(R_k)$ plus a $15\%$ safety margin.
* **Pydantic Schema Validation:** Ensures outputs adhere to a strict `DecisionCard` JSON schema:

```json
{
  "scenario_id": "DISRUPT_NYC_042",
  "recommended_action": "REROUTE_AND_DISPATCH",
  "vehicle_ids": ["V_102", "V_108"],
  "assigned_route": ["Node_12", "Node_45", "Node_89"],
  "estimated_delay_reduction_min": 14.5,
  "safety_guard_passed": true
}
```

---

## 6. Experimental Design, Baselines & Evaluation Metrics

### 6.1 Three Comparative Baselines
To rigorously evaluate performance, we compare three systems under a $3 \times 3$ grid of disruption scenarios (varying spatial scale $\times$ severity):

```
+-------------------------------------------------------------------------+
| SYSTEM 1: Baseline 1 (Standard SOP Controller)                          |
| - Static lookup table / standard Dijkstra re-routing                    |
+-------------------------------------------------------------------------+
| SYSTEM 2: Baseline 2 (Monolithic Single-LLM Agent)                      |
| - Single GPT-4o-mini prompt containing full graph & vehicle state       |
+-------------------------------------------------------------------------+
| SYSTEM 3: Proposed System (4-Agent LLM + Safety Review Guard)         |
| - Role-decomposed multi-agent system with Pydantic BFS validation      |
+-------------------------------------------------------------------------+
```

### 6.2 Four Quantitative Evaluation Metrics
1. **Hard Constraint Violation Rate (HCVR %):**
   $$\text{HCVR} = \frac{\text{Number of Infeasible Actions (Closed Edges / Empty Battery)}}{\text{Total Proposed Actions}} \times 100\%$$
   *(Target: $0\%$ for System 3 via Safety Guard)*
2. **Request Fulfillment Rate (RFR %):**
   $$\text{RFR} = \frac{\text{Successfully Rerouted Passenger Requests}}{\text{Total Affected Passenger Requests}} \times 100\%$$
3. **Average Delay Inflation Factor (ADIF):**
   $$\text{ADIF} = \frac{\text{Actual Travel Time under Disruption Response}}{\text{Free-Flow Un-disrupted Travel Time}}$$
4. **Execution Latency ($T_{\text{exec}}$) & Token Expense ($/scenario):**
   * Measures wall-clock decision latency (in seconds) and API token expenditure to quantify real-time operational viability.

---

## 7. Data Plan & Candidate Benchmark Datasets

### 7.1 Five Core Data Requirements
1. **Road Network Topology:** Intersections & link geometries to simulate routing.
2. **Demand / OD Matrices:** Origin-Destination passenger flow demand queues.
3. **Disruption Event Records:** Incident locations, closures, and breakdown durations.
4. **Fleet / Vehicle State Data:** Positions, battery SoC, vehicle capacity.
5. **Historical Dispatch Logs (Optional):** Ground-truth human operator response logs.

---

### 7.2 Eight Candidate Public Datasets (To Discuss with Mentors)

```
+-----------------------------------------------------------------------------+
| DATASET NAME                      | TYPE & CONTENT DESCRIPTION              |
+-----------------------------------+-----------------------------------------+
| 1. SUMO - LuST Scenario           | Full Luxembourg city network + demand.   |
| 2. SUMO - TAPASCologne            | Calibrated Cologne network + OD demand.  |
| 3. OpenStreetMap (OSMnx)          | Extract real road topology for any city.|
| 4. Caltrans PeMS                  | California highway sensor flow & events.|
| 5. Kaggle US Accidents            | 7.7M+ real incident location records.   |
| 6. FHWA WZDx                      | Live US road work zone closure feeds.   |
| 7. NYC TLC Trip Records           | Real taxi/ride-hail origin-destinations.|
| 8. GTFS Feeds (Mobility Database) | Transit schedules for multi-modal test. |
+-----------------------------------------------------------------------------+
```

---

## 8. 8-Week Execution Roadmap

```
W1: Finalize Research Question & Set Up Simulator
 W2: Build Scenario Generator, Metrics & Data Pipeline
  W3: Implement Rule-Based SOP Controller (Baseline 1)
   W4: Build Single-LLM (Baseline 2) & Multi-Agent System (System 3)
    W5: Execute First Full Comparison Run Across 3x3 Scenario Grid
     W6: Run Ablation Tests & MAST Failure Logging
      W7: Conduct Statistical Analysis & Draft Research Paper
       W8: Complete Final Runs & Release Open-Source Benchmark Repository
```

---

## 9. Slide-by-Slide Speaker Script (For `cl.pptx`)

Here is your exact word-for-word presentation script corresponding to the 11 slides in `cl.pptx` / `cl_presentation.pptx`.

---

### Slide 1 (1/11): Title Slide
* **Visual:** Dark slate background, title text, mentor names.
* **Speaker Script:**
> *"Good morning Dr. Alaa Daoud and Dr. Srinivasa K G. Today I am presenting our Week 1 progress and literature review for Batch 1 under Direction 1: Agentic AI for Transport Disruption Management.
>
> Our research systematically evaluates whether role-decomposed Multi-Agent LLM architectures can improve decision feasibility and operational constraint satisfaction during sudden transport network shocks, while quantitatively measuring execution latency and API token costs."*

---

### Slide 2 (2/11): Where We Are Starting From
* **Visual:** Shared program question, our specific question, hypothesis card, road network focus card.
* **Speaker Script:**
> *"To ground our work, we start from the shared program question: 'When does cooperation improve transportation systems?'
>
> We narrow this to our specific research question: Can specialized LLM agents make better transport-disruption decisions than a single LLM agent or a rule-based controller?
>
> Our hypothesis is that specialization improves decision feasibility and constraint satisfaction—at the cost of communication overhead and latency. Notably, our focus is on road-network disruptions such as road closures, breakdowns, and congestion spikes—a setting the multi-agent LLM literature has not yet tested, as existing work focuses primarily on rail corridors."*

---

### Slide 3 (3/11): Five Papers, Two Research Threads
* **Visual:** 5-row comparative literature table.
* **Speaker Script:**
> *"Our literature survey is built on 5 core papers across two main threads. 
>
> Three survey papers establish the broader landscape: Mahmud et al. in IEEE Transactions on ITS (May 2025), Nie et al. in Elsevier AI in Transportation (June 2025) establishing the LLM4TR taxonomy, and Wandelt et al. in MDPI Applied Sciences (August 2024).
>
> Two specific papers directly shape our system design: Wu & Zeng in MDPI Mathematics (August 2026) providing our rail precedent, and UC Berkeley’s MAST taxonomy by Cemri et al. at NeurIPS 2025 providing our multi-agent failure analysis."*

---

### Slide 4 (4/11): Multi-Agent Disruption Control on Rail (Closest Precedent)
* **Visual:** Wu & Zeng highlights, 58.9% and 32.6% metric cards, bottom limitation box.
* **Speaker Script:**
> *"Slide 4 highlights our closest direct precedent: Wu & Zeng’s 2026 study in MDPI Mathematics on the Shanghai Metro Line 2 corridor.
>
> They used 4 role-specific agents—dispatch, station, transfer, and information—paired with a safety-review agent and arbitration agent emitting structured DecisionCards. They achieved a 58.9% total-delay reduction and a 32.6% peak transfer-queue reduction compared to rule-based baselines.
>
> However, their critical limitation was that gains reversed once transfer capacity dropped by 25%—proving that agent coordination cannot fix physical capacity bottlenecks without alternate path routing."*

---

### Slide 5 (5/11): Why Multi-Agent LLM Systems Fail (MAST Taxonomy)
* **Visual:** 1,642 traces, 41-87% failure rate, +15.6% gain, 3-segment bar chart, takeaway card.
* **Speaker Script:**
> *"To prevent multi-agent design failures, Slide 5 draws on UC Berkeley's MAST paper presented at NeurIPS 2025 by Cemri et al.
>
> Analyzing 1,642 execution traces across 7 MAS frameworks, they observed task-failure rates between 41% and 87%. However, targeted architectural fixes yielded up to a +15.6% success gain using the exact same underlying LLM.
>
> Their breakdown shows that 41.8% of failures stem from system design issues, 36.9% from inter-agent misalignment, and 21.3% from task verification failures. Our main takeaway is that system failure is mostly architectural, not a model limit—meaning our agent design and verification layer matter as much as the LLM we choose."*

---

### Slide 6 (6/11): Research Gaps & Problems We Must Solve
* **Visual:** 2-column breakdown (Research Gaps vs Practical Problems).
* **Speaker Script:**
> *"This allows us to state our research gaps and practical problems side-by-side. 
>
> On the left, no multi-agent LLM disruption study targets 2D road networks, no shared benchmark compares rule-based vs single LLM vs multi-agent LLMs for road disruptions, MAST's failure modes haven't been measured on transport MAS, and cost-latency trade-offs remain unquantified.
>
> On the right, practical problems include LLM action infeasibility without bounded libraries, rising token costs, and coordination breakdowns."*

---

### Slide 7 (7/11): System Architecture & Evaluation
* **Visual:** 4-agent diagram + Safety-Review Agent dark box + 6 Evaluation Metrics.
* **Speaker Script:**
> *"Slide 7 presents our proposed approach. We decompose disruption response into 3 specialized agents—Traffic, Fleet, and Routing—reporting to a Coordinator Agent.
>
> Reconciled actions pass through a deterministic Safety-Review Guard that executes BFS graph reachability checks and fuel/battery state verification before emitting DecisionCard payloads.
>
> We benchmark this system against rule-based controllers and single-LLM agents across 6 key metrics: constraint violations, served requests, total delay, infeasible decisions, response time, and token API cost."*

---

### Slide 8 (8/11): What Data We Need
* **Visual:** 5 numbered data requirements circles.
* **Speaker Script:**
> *"Slide 8 outlines our 5 data requirements: road network topology, demand OD matrices, disruption event records, fleet vehicle state data, and optional historical dispatch logs."*

---

### Slide 9 (9/11): Candidate Public Datasets
* **Visual:** 8 dataset cards grid.
* **Speaker Script:**
> *"Slide 9 details candidate public datasets for discussion today: SUMO LuST and TAPASCologne for synthetic simulation testbeds, OpenStreetMap with SUMO netconvert for city road topologies, Caltrans PeMS and Kaggle US Accidents for incident calibration, and NYC TLC trip records for fleet vehicle demand proxies."*

---

### Slide 10 (10/11): Roadmap — Next 8 Weeks
* **Visual:** W1 to W8 horizontal timeline.
* **Speaker Script:**
> *"Slide 10 details our 8-week timeline: Weeks 1–2 for simulator setup and scenario generation; Weeks 3–4 for building baselines and multi-agent systems; Weeks 5–6 for full comparison runs and MAST failure logging; and Weeks 7–8 for statistical analysis, drafting, and open-source paper submission."*

---

### Slide 11 (11/11): Technical Guidance & Decisions Needed
* **Visual:** 4 discussion cards + Thank You banner.
* **Speaker Script:**
> *"Finally, Slide 11 outlines four specific choices where we seek your guidance today: 
> 1. Starting with a controlled 5–20 node synthetic JSON graph vs full SUMO/OSMnx subgraphs?
> 2. Using local open-source models (Llama 3.1 8B) vs cloud APIs (GPT-4o-mini)?
> 3. Framework selection between LangGraph and CrewAI?
> 4. Target milestone submission format and publication venue?
> 
> Thank you Dr. Alaa Daoud and Dr. Srinivasa K G. I look forward to your feedback and guidance."*

---

## 10. Anticipated Technical Questions & Bulletproof Answers

### Question 1: *"Why use LLMs for transport routing when classical algorithms (Dijkstra, A*, MILP) are exact and faster?"*
* **Bulletproof Answer:**
> *"Classical algorithms like Dijkstra or MILP excel at static shortest-path finding on fixed graphs. However, during sudden real-time disruptions, the challenge is not just path calculation—it involves multi-objective negotiation: prioritizing emergency vehicle access, rebalancing fleet battery states, negotiating multi-passenger queue trade-offs, and parsing unstructured incident feeds. 
> 
> Classical MILPs become computationally intractable (NP-hard) when real-time constraints dynamically shift. LLMs serve as high-level heuristic reasoning engines that propose candidate action bounds, while classical graph algorithms (like our BFS Safety Guard) verify physical constraint feasibility."*

---

### Question 2: *"How will you prevent LLM hallucinations from creating non-existent detours?"*
* **Bulletproof Answer:**
> *"We prevent hallucinations using a two-tier defense:
> 1. **Prompt & Output Guardrails:** We restrict LLM outputs to strict JSON schemas using Pydantic, enforcing explicit node and edge ID lists.
> 2. **Deterministic BFS Verification Guard:** Before any decision is executed, a non-LLM Python module runs a Breadth-First Search on the actual graph adjacency matrix $G=(V,E)$. If any proposed edge $e$ has capacity $C(e,t)=0$ or does not exist, the proposed action is rejected instantly and falls back to a deterministic SOP route."*

---

### Question 3: *"What is the difference between your work and Wu & Zeng (MDPI 2026)?"*
* **Bulletproof Answer:**
> *"Wu & Zeng evaluated a 4-agent LLM system on Shanghai Metro Line 2—which is a 1-dimensional, linear rail corridor with fixed transfer stations and a static action lookup library. 
> 
> Our project expands multi-agent LLM decision-making to **2-dimensional urban road network graphs**, where topology contains dynamic alternate detour loops, time-dependent edge capacities $C(e,t)$, dynamic fleet battery states, and continuous spatial-temporal vehicle routing."*

---

### Question 4: *"Why start with a synthetic 5–20 node JSON graph instead of full SUMO simulation immediately?"*
* **Bulletproof Answer:**
> *"Starting with a controlled synthetic JSON graph generator in Weeks 1–2 allows us to systematically benchmark baseline constraint violations, test Pydantic schema validation, and measure multi-agent token latency without simulator overhead. Once our multi-agent architecture and Safety Guard are validated, we scale to OSMnx and SUMO (LuST/TAPASCologne) in Phase 2."*
