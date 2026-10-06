# Project Demo Plan
## Agentic AI for Transport Disruption Management
**Target:** Interactive Web Dashboard for College Evaluation  
**Stack:** Next.js 15 + TypeScript + Tailwind CSS  
**Status:** Planning → Ready to Build  
**Date:** October 5, 2026

---

## What We're Building

A **Next.js + TypeScript** web app (`demo/`) that lets evaluators explore the full research system — road network, disruptions, agent architecture, and real benchmark results. Built with extensibility in mind: when Week 4 LLM agents are ready, real API calls can be wired in directly.

---

## Demo Sections (Pages / Tabs)

### 1. 🏠 Home — Research Overview
- Project title, institution, mentors
- One-line research question
- 3 hypothesis cards (H1, H2, H3 highlighted)
- Project timeline (W1–W8) with current progress marker
- "Open Research Gap" statement

### 2. 🗺️ Network Simulator — Interactive Grid
- Animated **4×4 road network canvas** (nodes A0–D3)
- Vehicle dots shown on the grid
- **Scenario selector** (L1 Simple → L5 Stress Test)
- Disruptions rendered live:
  - 🔴 Red dashed edge = Road Closure
  - 🟡 Yellow edge = Congestion
  - 💥 Broken vehicle icon = Vehicle Breakdown
  - 🔵 Surge pulse = Demand Surge
- Transport requests shown as origin→destination arrows
- **Play button** → animates vehicle routes from B1 results
- Scenario description panel (what disruptions, how many requests)

### 3. 📊 Results — 3-System Comparison
- **System selector tabs**: B1 Rule-Based | B2 Single-LLM | B3 Multi-Agent
- Metric cards for selected scenario:
  - HCVR % (Hard Constraint Violation Rate)
  - RFR % (Request Fulfillment Rate)
  - ADIF (Delay Inflation Factor)
  - Execution Latency (ms)
  - IDR % (Infeasible Decision Rate)
- **Bar chart**: All 3 systems side-by-side for selected metric
- **Complexity curve chart**: Performance vs L1→L5 (RFR)
- Decision log table: per-request outcomes

> **Note:** B1 data is real (from sim/results/). B2 and B3 are projected/estimated values based on literature (Wu & Zeng 2026 benchmarks) for demo purposes — clearly labeled as "Projected."

### 4. 🤖 Architecture — System Design
- Visual agent pipeline diagram (Traffic → Fleet → Routing → Coordinator → Safety Guard)
- Each agent card shows: role, information scope, tools available
- Safety Guard detail: BFS check + Pydantic schema + SoC check
- DecisionCard JSON example (syntax-highlighted)
- MAST failure taxonomy breakdown (3-segment bar)

### 5. 📚 Research Foundation
- 5 core paper cards (Mahmud, Nie, Wandelt, Wu & Zeng, Cemri)
- Research gap matrix table
- 5 hypotheses with measurable targets

---

## Data Used (All Real)

| Source File | Used For |
|---|---|
| `sim/results/L1_simple_001_rule_based.json` | B1 metrics & decisions for L1 |
| `sim/results/L2_moderate_001_rule_based.json` | B1 metrics & decisions for L2 |
| `sim/results/L3_compound_001_rule_based.json` | B1 metrics & decisions for L3 |
| `sim/results/L4_cascading_001_rule_based.json` | B1 metrics & decisions for L4 |
| `sim/results/L5_stress_001_rule_based.json` | B1 metrics & decisions for L5 |
| `sim/scenarios/L1–L5.json` | Disruption types, requests, network |

**B2 & B3 projected values** (clearly labeled, based on literature):
- B2 Single-LLM: ~15–25% HCVR, ~70–85% RFR (hallucination-prone without guard)
- B3 Multi-Agent: ~0% HCVR (with guard), ~85–95% RFR, 3–4× latency vs B1

---

## File Structure

```
04-Minor/
├── project.md                      ← this file
└── demo/                           ← Next.js app root
    ├── app/
    │   ├── layout.tsx              ← root layout, fonts, metadata
    │   ├── page.tsx                ← Home tab
    │   ├── simulator/page.tsx      ← Network Simulator tab
    │   ├── results/page.tsx        ← Results & Charts tab
    │   ├── architecture/page.tsx   ← Architecture diagram tab
    │   └── research/page.tsx       ← Research foundation tab
    ├── components/
    │   ├── NavBar.tsx              ← top nav with tab switching
    │   ├── NetworkCanvas.tsx       ← animated 4×4 grid (Canvas API)
    │   ├── MetricCard.tsx          ← HCVR / RFR / ADIF cards
    │   ├── ComparisonChart.tsx     ← Chart.js bar chart (3 systems)
    │   ├── ComplexityCurve.tsx     ← RFR vs L1–L5 line chart
    │   ├── AgentPipeline.tsx       ← agent flow diagram (pure CSS/SVG)
    │   ├── DecisionLog.tsx         ← per-request decision table
    │   └── PaperCard.tsx           ← literature paper cards
    ├── lib/
    │   └── data.ts                 ← all scenario + results data typed
    ├── public/
    └── package.json
```

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | Next.js 15 (App Router) | File-based routing, SSR ready, easy API routes for future LLM calls |
| Language | TypeScript | Type-safe scenario/results data |
| Styling | Tailwind CSS + custom CSS | Rapid dark-mode UI, glassmorphism utilities |
| Charts | Chart.js + react-chartjs-2 | Bar + line charts, easy React integration |
| Network Graph | HTML5 Canvas (React ref) | Custom animated 4×4 grid drawing |
| Fonts | next/font (Inter) | Optimized font loading |

---

## Design Aesthetic

- **Dark mode** (deep navy/slate background)
- **Glassmorphism** cards with subtle borders
- **Accent colors**: Cyan `#00d4ff` (network), Amber `#f59e0b` (warnings), Emerald `#10b981` (success), Rose `#f43f5e` (violations)
- **Smooth transitions** on tab switch and scenario change
- **Animated** vehicle movement on canvas
- Google Font: **Inter**

---

## Projected Build Time

| Section | Effort |
|---|---|
| Next.js scaffold + Tailwind setup | 15 min |
| `lib/data.ts` — typed scenario data | 20 min |
| NavBar + layout | 15 min |
| NetworkCanvas + disruption rendering | 45 min |
| Metrics cards + DecisionLog table | 20 min |
| Chart.js comparison charts | 20 min |
| Architecture diagram (SVG/CSS) | 20 min |
| Research section + paper cards | 15 min |
| **Total** | ~2.5 hours |

---

## Build Checklist

- [x] Project plan written (`project.md`)
- [ ] Next.js app scaffolded (`demo/`)
- [ ] `lib/data.ts` — all real B1 results + B2/B3 projected data typed
- [ ] `NavBar.tsx` + root layout
- [ ] `app/page.tsx` — Home (research overview, timeline)
- [ ] `app/simulator/page.tsx` — Network canvas + scenario player
- [ ] `app/results/page.tsx` — Metrics + charts
- [ ] `app/architecture/page.tsx` — Agent pipeline diagram
- [ ] `app/research/page.tsx` — Papers + hypotheses
- [ ] `npm run dev` tested & working
