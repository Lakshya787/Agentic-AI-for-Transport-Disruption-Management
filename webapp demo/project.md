# 🚦 Agentic AI for Transport Disruption Management
## Interactive Web Dashboard — Build Plan

> **Target Audience:** College Evaluators  
> **Stack:** Next.js 15 · TypeScript · Tailwind CSS · Chart.js  
> **Status:** 🟡 Planning Complete → Ready to Build  
> **Date:** October 5, 2026

---

## 📌 Project Overview

A **Next.js + TypeScript** interactive web dashboard (`demo/`) that lets evaluators explore the full research system end-to-end — road network topology, live disruption scenarios, multi-agent architecture, and real benchmark results.

**Research Question:**  
> Can a structured multi-agent LLM system outperform rule-based and single-LLM baselines in transport disruption management while maintaining hard-constraint safety?

**Hypotheses Being Demonstrated:**

| # | Hypothesis | Target |
|---|---|---|
| H1 | Multi-agent reduces HCVR vs B1 rule-based | ≤ 2% HCVR |
| H2 | Multi-agent improves RFR vs B1 | ≥ 85% RFR |
| H3 | Safety Guard eliminates infeasible decisions | IDR = 0% |

---

## 🗂️ Pages / Tabs

### 1. 🏠 Home — Research Overview
| Element | Details |
|---|---|
| Hero | Project title, institution, mentors |
| Research question | One-line statement, clearly displayed |
| Hypothesis cards | H1, H2, H3 — color-coded (cyan / amber / emerald) |
| Timeline | W1–W8 Gantt-style, current progress marker highlighted |
| Research Gap | "Open gap" statement with citation |

---

### 2. 🗺️ Network Simulator — Interactive Grid
| Element | Details |
|---|---|
| Canvas | Animated **4×4 road network** (nodes A0–D3), HTML5 Canvas |
| Vehicles | Moving dots along computed routes |
| Scenario selector | L1 Simple → L5 Stress Test dropdown |
| Disruption rendering | 🔴 Road Closure (red dashed edge), 🟡 Congestion (yellow edge), 💥 Breakdown (broken icon), 🔵 Demand Surge (pulse) |
| Request arrows | Origin → Destination arrows per transport request |
| Play button | Animates vehicle routes from B1 results |
| Info panel | Scenario description: disruptions active, total requests |

---

### 3. 📊 Results — 3-System Comparison
| Element | Details |
|---|---|
| System tabs | B1 Rule-Based · B2 Single-LLM · B3 Multi-Agent |
| Metric cards | HCVR % · RFR % · ADIF · Latency (ms) · IDR % |
| Bar chart | All 3 systems side-by-side for the selected metric |
| Complexity curve | RFR vs complexity L1 → L5 (line chart) |
| Decision log | Per-request outcome table with status badges |

> **Data note:** B1 data is **real** (from `sim/results/`). B2 & B3 are **projected** values based on Wu & Zeng 2026 benchmarks — clearly labeled `[Projected]`.

---

### 4. 🤖 Architecture — System Design
| Element | Details |
|---|---|
| Agent pipeline | SVG/CSS flow: Traffic → Fleet → Routing → Coordinator → Safety Guard |
| Agent cards | Role · Information scope · Tools available |
| Safety Guard detail | BFS check + Pydantic schema validation + SoC check |
| DecisionCard | JSON example with syntax highlighting |
| MAST taxonomy | 3-segment failure bar (Constraint / Routing / Communication) |

---

### 5. 📚 Research Foundation
| Element | Details |
|---|---|
| Paper cards | 5 core papers: Mahmud, Nie, Wandelt, Wu & Zeng, Cemri |
| Gap matrix | Research gap comparison table |
| Hypotheses | 5 hypotheses with measurable targets listed |

---

## 📁 File Structure

```
04-Minor/
├── project.md                          ← high-level plan (parent)
└── webapp demo/
    ├── project.md                      ← this file (build plan)
    └── demo/                           ← Next.js app root
        ├── app/
        │   ├── layout.tsx              ← root layout, Inter font, metadata
        │   ├── page.tsx                ← Home tab
        │   ├── simulator/
        │   │   └── page.tsx            ← Network Simulator tab
        │   ├── results/
        │   │   └── page.tsx            ← Results & Charts tab
        │   ├── architecture/
        │   │   └── page.tsx            ← Architecture diagram tab
        │   └── research/
        │       └── page.tsx            ← Research Foundation tab
        ├── components/
        │   ├── NavBar.tsx              ← top nav with active tab indicator
        │   ├── NetworkCanvas.tsx       ← animated 4×4 grid (Canvas API)
        │   ├── MetricCard.tsx          ← HCVR / RFR / ADIF / Latency cards
        │   ├── ComparisonChart.tsx     ← Chart.js bar chart (3 systems)
        │   ├── ComplexityCurve.tsx     ← RFR vs L1–L5 line chart
        │   ├── AgentPipeline.tsx       ← agent flow diagram (SVG/CSS)
        │   ├── DecisionLog.tsx         ← per-request decision table
        │   └── PaperCard.tsx           ← literature paper cards
        ├── lib/
        │   └── data.ts                 ← all scenario + results data (typed)
        ├── public/
        └── package.json
```

---

## 🗃️ Data Sources

### Real Data (B1 Rule-Based Results)

| File | Used For |
|---|---|
| `sim/results/L1_simple_001_rule_based.json` | B1 metrics & decisions — L1 |
| `sim/results/L2_moderate_001_rule_based.json` | B1 metrics & decisions — L2 |
| `sim/results/L3_compound_001_rule_based.json` | B1 metrics & decisions — L3 |
| `sim/results/L4_cascading_001_rule_based.json` | B1 metrics & decisions — L4 |
| `sim/results/L5_stress_001_rule_based.json` | B1 metrics & decisions — L5 |
| `sim/scenarios/L1–L5.json` | Disruption types, requests, network topology |

### Projected Data (B2 & B3 — Literature-based, labeled `[Projected]`)

| System | HCVR | RFR | Notes |
|---|---|---|---|
| B2 Single-LLM | 15–25% | 70–85% | Hallucination-prone without guard |
| B3 Multi-Agent | ~0% | 85–95% | With Safety Guard; 3–4× latency vs B1 |

---

## 🛠️ Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | Next.js 15 (App Router) | File-based routing, SSR ready, easy future LLM API routes |
| Language | TypeScript | Type-safe scenario/results data |
| Styling | Tailwind CSS + custom CSS | Rapid dark-mode UI, glassmorphism |
| Charts | Chart.js + react-chartjs-2 | Bar + line charts, easy React integration |
| Network Graph | HTML5 Canvas (React ref) | Custom animated 4×4 grid drawing |
| Fonts | next/font (Inter) | Optimized font loading |

---

## 🎨 Design System

### Color Palette

| Token | Hex | Usage |
|---|---|---|
| Background | `#0a0f1e` | Deep navy — page background |
| Surface | `#111827` | Cards & panels |
| Border | `rgba(255,255,255,0.08)` | Glassmorphism borders |
| Cyan (Primary) | `#00d4ff` | Network edges, active states |
| Amber (Warning) | `#f59e0b` | Congestion, warnings |
| Emerald (Success) | `#10b981` | Fulfilled requests, success states |
| Rose (Violation) | `#f43f5e` | HCVR, road closures, violations |
| Purple (B3) | `#8b5cf6` | Multi-agent system accent |

### UI Principles
- **Dark mode** throughout — deep navy/slate backgrounds
- **Glassmorphism** cards: `backdrop-filter: blur(12px)`, subtle borders
- **Smooth transitions** on tab switch and scenario change (`300ms ease`)
- **Animated** vehicle movement on canvas
- **Inter** font from Google Fonts via `next/font`
- Micro-interactions: hover lift on cards, pulse on active nodes

---

## ⏱️ Projected Build Time

| Task | Est. Time |
|---|---|
| Next.js 15 scaffold + Tailwind config | 15 min |
| `lib/data.ts` — typed scenario + results data | 20 min |
| `NavBar.tsx` + root layout | 15 min |
| `NetworkCanvas.tsx` — 4×4 grid + disruption rendering | 45 min |
| `MetricCard.tsx` + `DecisionLog.tsx` | 20 min |
| `ComparisonChart.tsx` + `ComplexityCurve.tsx` (Chart.js) | 20 min |
| `AgentPipeline.tsx` — SVG flow diagram | 20 min |
| Research section + paper cards | 15 min |
| **Total** | **~2.5 hrs** |

---

## ✅ Build Checklist

### Setup
- [x] Project plan written (`project.md`)
- [ ] `webapp demo/` folder created
- [ ] Next.js 15 app scaffolded inside `demo/`
- [ ] Tailwind CSS configured with custom design tokens
- [ ] `lib/data.ts` — all real B1 results + B2/B3 projected data typed

### Core Components
- [ ] `NavBar.tsx` + root `layout.tsx`
- [ ] `NetworkCanvas.tsx` — animated 4×4 grid
- [ ] `MetricCard.tsx` — HCVR / RFR / ADIF / Latency
- [ ] `ComparisonChart.tsx` — bar chart (3 systems)
- [ ] `ComplexityCurve.tsx` — RFR vs L1–L5 line chart
- [ ] `AgentPipeline.tsx` — agent flow SVG
- [ ] `DecisionLog.tsx` — request outcome table
- [ ] `PaperCard.tsx` — literature cards

### Pages
- [ ] `app/page.tsx` — Home (overview, timeline, hypotheses)
- [ ] `app/simulator/page.tsx` — Network canvas + scenario player
- [ ] `app/results/page.tsx` — Metrics + comparison charts
- [ ] `app/architecture/page.tsx` — Agent pipeline diagram
- [ ] `app/research/page.tsx` — Papers + hypotheses

### QA
- [ ] `npm run dev` tested & working
- [ ] All 5 scenarios (L1–L5) selectable and rendering correctly
- [ ] Charts render with both real (B1) and projected (B2/B3) data
- [ ] Responsive layout verified (desktop + tablet)
- [ ] All `[Projected]` labels visible on B2/B3 data

---

## 🚀 Quick Start (Once Ready to Build)

```bash
# From 04-Minor/webapp demo/
npx create-next-app@latest demo --typescript --tailwind --app --no-src-dir --import-alias "@/*"
cd demo
npm install chart.js react-chartjs-2
npm run dev
```

---

*This plan is derived from the parent project.md. All data references point to `sim/` relative to `04-Minor/`.*
