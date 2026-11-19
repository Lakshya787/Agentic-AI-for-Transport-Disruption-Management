#!/usr/bin/env python3
"""
Publication-Quality Paper Figure Generator for AAMAS-2023 Template
══════════════════════════════════════════════════════════════════
Generates and organizes all formal figures into `paper_figures/` and `paper/paper_figures/`:
  • fig1_architecture.png       - Neuro-symbolic multi-agent architecture diagram
  • fig2_network_topologies.png - Side-by-side 4x4 baseline and Real Manhattan network with callouts
  • fig3_benchmark_results.png  - 4-panel empirical performance across L1-L5
  • fig4_scalability_multi_scale.png - Multi-scale scalability benchmark (Micro, Meso, Macro)
  • fig5_explainability_audit.png    - 5-dimensional causal explainability audit trace
"""

import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import networkx as nx

from network import create_network
from real_network import (
    create_real_manhattan_network,
    MANHATTAN_POSITIONS,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(PROJECT_ROOT, "paper_figures")
PAPER_OUT_DIR = os.path.join(PROJECT_ROOT, "paper", "paper_figures")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(PAPER_OUT_DIR, exist_ok=True)

# Clean matplotlib publication aesthetic
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Helvetica", "Arial"]
plt.rcParams["axes.edgecolor"] = "#334155"
plt.rcParams["axes.linewidth"] = 0.8


def sync_to_paper(filename):
    """Ensure both paper_figures/ and paper/paper_figures/ stay 100% in sync."""
    src = os.path.join(OUT_DIR, filename)
    dst = os.path.join(PAPER_OUT_DIR, filename)
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"  ↳ Synced to {dst}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. Figure 1: Neuro-Symbolic Multi-Agent Architecture Diagram
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig1_architecture():
    fig, ax = plt.subplots(figsize=(15, 6.2), dpi=300)
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    # Title
    ax.text(7.5, 5.85, "Neuro-Symbolic Multi-Agent Transport Disruption Architecture", 
            fontsize=14, fontweight="bold", ha="center", color="#0f172a")

    # 1. Stage 1: Inputs (Left)
    rect1 = patches.FancyBboxPatch((0.5, 0.5), 3.2, 4.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                                  facecolor="#f8fafc", edgecolor="#64748b", lw=1.8)
    ax.add_patch(rect1)

    # Header 1
    h1 = patches.FancyBboxPatch((0.7, 4.75), 2.8, 0.42, boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor="#334155", edgecolor="none")
    ax.add_patch(h1)
    ax.text(2.1, 4.96, "1. Multi-Modal Inputs", fontsize=9.5, fontweight="bold", ha="center", va="center", color="#ffffff")

    input_items = [
        ("Incident Text Advisories", "511NY & Police Radio Feeds\nUnstructured Traffic Bulletins", "#fee2e2", "#ef4444"),
        ("EV Fleet Telemetry", "Real-Time Battery SoC (%),\nSeating Capacity, Vehicle State", "#fef3c7", "#d97706"),
        ("Passenger Trip Requests", "Origin-Destination Pairs,\nEmergency Medical Priority Tiers", "#e0e7ff", "#4f46e5")
    ]
    y_in = 3.65
    for title, desc, bg, col in input_items:
        ibox = patches.FancyBboxPatch((0.7, y_in), 2.8, 0.85, boxstyle="round,pad=0.06,rounding_size=0.1",
                                     facecolor=bg, edgecolor=col, lw=1.2)
        ax.add_patch(ibox)
        ax.text(2.1, y_in + 0.62, title, fontsize=8.2, fontweight="bold", ha="center", va="center", color=col)
        ax.text(2.1, y_in + 0.28, desc, fontsize=6.8, ha="center", va="center", color="#1e293b")
        y_in -= 1.15

    # Arrow 1 -> 2
    ax.annotate("", xy=(4.2, 2.9), xytext=(3.7, 2.9),
                arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#334155", mutation_scale=14))

    # 2. Stage 2: MAS Deliberation (Center)
    rect2 = patches.FancyBboxPatch((4.2, 0.5), 6.1, 4.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                                  facecolor="#f0fdf4", edgecolor="#10b981", lw=1.8)
    ax.add_patch(rect2)

    # Header 2
    h2 = patches.FancyBboxPatch((4.5, 4.75), 5.5, 0.42, boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor="#059669", edgecolor="none")
    ax.add_patch(h2)
    ax.text(7.25, 4.96, "2. Tool-Augmented Multi-Agent Deliberation (B3)", 
            fontsize=9.5, fontweight="bold", ha="center", va="center", color="#ffffff")

    agents = [
        # Top-Left: Traffic Agent
        (4.5, 2.85, 2.5, 1.6, "Traffic Agent (LLM)", "Semantic Ingestion", 
         "Parses unstructured alerts\nExtracts severed edges E_closed\nUpdates belief graph", "#ecfdf5", "#059669"),
        # Top-Right: Fleet Agent
        (7.5, 2.85, 2.5, 1.6, "Fleet Agent (LLM)", "Battery & Triage Audit", 
         "Evaluates SoC sufficiency\nReserves premier EVs for\nemergency hospital trips", "#ecfdf5", "#059669"),
        # Bottom-Left: Routing Tool (Symbolic Python)
        (4.5, 0.85, 2.5, 1.6, "Routing Tool (Symbolic)", "Deterministic Dijkstra", 
         "Yen's K-Shortest Paths\non certified open graph\nZero token hallucination!", "#eff6ff", "#2563eb"),
        # Bottom-Right: Coordinator Agent
        (7.5, 0.85, 2.5, 1.6, "Coordinator Agent (LLM)", "Arbitration & Synthesis", 
         "Reconciles triage & routes\nEliminates double-booking\nDrafts decision card C_prop", "#ecfdf5", "#059669")
    ]

    for x, y, w, h, name, subtitle, desc, bg, col in agents:
        abox = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.06,rounding_size=0.1",
                                      facecolor=bg, edgecolor=col, lw=1.3)
        ax.add_patch(abox)
        ax.text(x + w/2, y + h - 0.28, name, fontsize=8.0, fontweight="bold", ha="center", va="center", color=col)
        ax.text(x + w/2, y + h - 0.58, subtitle, fontsize=7.2, fontweight="bold", ha="center", va="center", color="#334155")
        ax.plot([x + 0.2, x + w - 0.2], [y + h - 0.72, y + h - 0.72], color=col, lw=0.6, alpha=0.4)
        ax.text(x + w/2, y + 0.42, desc, fontsize=6.7, ha="center", va="center", color="#1e293b")

    # Internal arrows inside MAS
    ax.annotate("", xy=(5.75, 2.45), xytext=(5.75, 2.85),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#059669", mutation_scale=10))
    ax.annotate("", xy=(8.75, 2.45), xytext=(8.75, 2.85),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#059669", mutation_scale=10))
    ax.annotate("", xy=(7.5, 1.65), xytext=(7.0, 1.65),
                arrowprops=dict(arrowstyle="-|>", lw=1.8, color="#2563eb", mutation_scale=10))

    # Arrow 2 -> 3
    ax.annotate("", xy=(10.8, 2.9), xytext=(10.3, 2.9),
                arrowprops=dict(arrowstyle="-|>", lw=2.2, color="#334155", mutation_scale=14))

    # 3. Stage 3: Deterministic Safety Guard (Right)
    rect3 = patches.FancyBboxPatch((10.8, 0.5), 3.7, 4.8, boxstyle="round,pad=0.1,rounding_size=0.15",
                                  facecolor="#fef2f2", edgecolor="#ef4444", lw=1.8)
    ax.add_patch(rect3)

    # Header 3
    h3 = patches.FancyBboxPatch((11.0, 4.75), 3.3, 0.42, boxstyle="round,pad=0.05,rounding_size=0.1",
                                facecolor="#b91c1c", edgecolor="none")
    ax.add_patch(h3)
    ax.text(12.65, 4.96, "3. Deterministic Safety Guard", fontsize=9.5, fontweight="bold", ha="center", va="center", color="#ffffff")

    # Guard Invariant Card
    gbox = patches.FancyBboxPatch((11.0, 1.9), 3.3, 2.6, boxstyle="round,pad=0.08,rounding_size=0.1",
                                 facecolor="#ffffff", edgecolor="#fca5a5", lw=1.2)
    ax.add_patch(gbox)
    ax.text(12.65, 4.25, "Non-LLM Physical Barrier", fontsize=8.2, fontweight="bold", ha="center", va="center", color="#991b1b")
    ax.plot([11.2, 14.1], [4.05, 4.05], color="#fca5a5", lw=0.6)

    invariants = [
        ("Invariant 1: Topological Reachability", "Routes physically passable in reality"),
        ("Invariant 2: Battery Range + 15% Buffer", "Mandatory reserve energy buffer"),
        ("Invariant 3: Seating Capacity Limit", "Passenger party <= Vehicle capacity"),
        ("Invariant 4: Concurrency Verification", "Zero overlapping EV allocations")
    ]
    y_inv = 3.65
    for inv_t, inv_d in invariants:
        ax.text(11.2, y_inv, f"[Pass] {inv_t}", fontsize=6.8, fontweight="bold", color="#059669", va="center")
        ax.text(11.5, y_inv - 0.22, inv_d, fontsize=6.2, color="#475569", va="center")
        y_inv -= 0.52

    # Output Badge
    out_badge = patches.FancyBboxPatch((11.0, 0.8), 3.3, 0.85, boxstyle="round,pad=0.08,rounding_size=0.1",
                                      facecolor="#059669", edgecolor="#047857", lw=1.5)
    ax.add_patch(out_badge)
    ax.text(12.65, 1.35, "Certified Safe Dispatch Plan", fontsize=8.5, fontweight="bold", ha="center", va="center", color="#ffffff")
    ax.text(12.65, 1.02, "+ 5D Causal Explainability Audit", fontsize=7.5, ha="center", va="center", color="#d1fae5")

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "fig1_architecture.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated {out_path}")
    sync_to_paper("fig1_architecture.png")


# ─────────────────────────────────────────────────────────────────────────────
# 2. Figure 2: 2D Urban Road Network Topologies (4x4 vs Real Manhattan)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig2_network_topologies():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7.5), dpi=300)

    # Panel A: 4x4 Baseline Grid
    G_4x4 = create_network()
    pos_4x4 = {n: G_4x4.nodes[n]["pos"] for n in G_4x4.nodes}

    for u, v in G_4x4.edges:
        p1, p2 = pos_4x4[u], pos_4x4[v]
        is_closure = (u, v) in [("N4", "N5"), ("N5", "N4")]
        if not is_closure:
            ax1.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#94a3b8", lw=2.0, zorder=1)

    p_n4, p_n5 = pos_4x4["N4"], pos_4x4["N5"]
    ax1.plot([p_n4[0], p_n5[0]], [p_n4[1], p_n5[1]], color="#ef4444", lw=4.0, ls="--", zorder=2)
    ax1.text(0.5, 2.15, "Flooded Link\n(Text Alert Closure)", fontsize=7.5, fontweight="bold",
             color="#dc2626", ha="center", va="bottom",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#fef2f2", edgecolor="#ef4444", lw=1))

    for n, (x, y) in pos_4x4.items():
        if n == "N15":
            c = "#ef4444"
            sz = 360
        elif n == "N0":
            c = "#2563eb"
            sz = 360
        else:
            c = "#1e293b"
            sz = 300
        ax1.scatter(x, y, s=sz, color=c, edgecolors="#ffffff", lw=2.0, zorder=3)
        ax1.text(x, y, n, color="#ffffff", fontsize=8.5, fontweight="bold", ha="center", va="center", zorder=4)

    ax1.annotate("Fleet Depot (N0)", xy=(0, 3), xytext=(-0.3, 3.35),
                 arrowprops=dict(arrowstyle="->", color="#2563eb", lw=1.5),
                 fontsize=8.0, fontweight="bold", color="#1d4ed8",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="#eff6ff", edgecolor="#93c5fd"))

    ax1.annotate("Trauma Center (N15)", xy=(3, 0), xytext=(2.3, -0.4),
                 arrowprops=dict(arrowstyle="->", color="#ef4444", lw=1.5),
                 fontsize=8.0, fontweight="bold", color="#b91c1c",
                 bbox=dict(boxstyle="round,pad=0.2", facecolor="#fef2f2", edgecolor="#fca5a5"))

    ax1.set_title("(a) Synthetic 4×4 Manhattan Baseline (N=16, 24 Edges)", fontsize=11, fontweight="bold", pad=15)
    ax1.set_xlim(-0.6, 3.6)
    ax1.set_ylim(-0.6, 3.6)
    ax1.set_aspect("equal")
    ax1.axis("off")

    # Panel B: Authentic Real Manhattan Urban Network (N=42)
    G_man = create_real_manhattan_network()
    pos_man = {n: G_man.nodes[n]["pos"] for n in G_man.nodes}

    for u, v, data in G_man.edges(data=True):
        if u in pos_man and v in pos_man:
            p1, p2 = pos_man[u], pos_man[v]
            is_fdr = "FDR Drive" in data.get("street_name", "")
            is_closure = (u, v) in [("M19", "M21"), ("M21", "M19")]
            if is_closure:
                ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#ef4444", lw=4.0, ls="--", zorder=2)
            elif is_fdr:
                ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#0284c7", lw=3.2, ls="-", zorder=1)
            else:
                ax2.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#cbd5e1", lw=1.6, ls="-", zorder=1)

    hospitals = {"M20", "M21", "M28"}
    landmarks = {"M01", "M06", "M12", "M16", "M42"}

    for n, (x, y) in pos_man.items():
        if n in hospitals:
            c = "#dc2626"
            sz = 340
        elif n in landmarks:
            c = "#7c3aed"
            sz = 280
        else:
            c = "#334155"
            sz = 160
        ax2.scatter(x, y, s=sz, color=c, edgecolors="#ffffff", lw=1.5, zorder=3)
        ax2.text(x, y, n, color="#ffffff", fontsize=7.0 if n in hospitals else 6.0,
                 fontweight="bold", ha="center", va="center", zorder=4)

    callouts = [
        ("M20", (pos_man["M20"][0], pos_man["M20"][1]), (pos_man["M20"][0] + 0.6, pos_man["M20"][1] + 0.3),
         "Bellevue Hospital (M20)\nLevel 1 Trauma Center", "#b91c1c", "#fef2f2", "#fca5a5"),
        ("M21", (pos_man["M21"][0], pos_man["M21"][1]), (pos_man["M21"][0] - 0.2, pos_man["M21"][1] + 0.55),
         "NYU Langone (M21)", "#b91c1c", "#fef2f2", "#fca5a5"),
        ("M16", (pos_man["M16"][0], pos_man["M16"][1]), (pos_man["M16"][0] - 1.1, pos_man["M16"][1] + 0.35),
         "Penn Station (M16)\nKey Transit Origin", "#6d28d9", "#f5f3ff", "#ddd6fe"),
        ("M12", (pos_man["M12"][0], pos_man["M12"][1]), (pos_man["M12"][0] + 0.4, pos_man["M12"][1] + 0.55),
         "Grand Central (M12)", "#6d28d9", "#f5f3ff", "#ddd6fe"),
        ("M06", (pos_man["M06"][0], pos_man["M06"][1]), (pos_man["M06"][0] - 1.1, pos_man["M06"][1] + 0.35),
         "Times Sq (M06)", "#6d28d9", "#f5f3ff", "#ddd6fe"),
        ("M42", (pos_man["M42"][0], pos_man["M42"][1]), (pos_man["M42"][0] + 0.6, pos_man["M42"][1] - 0.3),
         "Wall St / Ferry (M42)", "#334155", "#f8fafc", "#cbd5e1")
    ]

    for nid, (nx_pt, ny_pt), (tx, ty), text, text_col, bg_col, border_col in callouts:
        ax2.annotate(text, xy=(nx_pt, ny_pt), xytext=(tx, ty),
                     arrowprops=dict(arrowstyle="-|>", color=text_col, lw=1.2, mutation_scale=8),
                     fontsize=6.8, fontweight="bold", color=text_col,
                     bbox=dict(boxstyle="round,pad=0.25", facecolor=bg_col, edgecolor=border_col, lw=1))

    ax2.text(4.4, 4.3, "E 34th St Flash Flood\n(Severed: M19 <-> M21)", fontsize=6.8, fontweight="bold",
             color="#dc2626", ha="center", va="center",
             bbox=dict(boxstyle="round,pad=0.2", facecolor="#fef2f2", edgecolor="#ef4444", lw=1))

    ax2.set_title("(b) Authentic Real Manhattan Urban Network (N=42, 70 Edges)", fontsize=11, fontweight="bold", pad=15)
    ax2.set_xlim(-0.2, 8.8)
    ax2.set_ylim(-1.8, 8.8)
    ax2.set_aspect("equal")
    ax2.axis("off")

    legend_elements = [
        patches.Patch(facecolor="#dc2626", edgecolor="none", label="Emergency Trauma Centers"),
        patches.Patch(facecolor="#7c3aed", edgecolor="none", label="Major Transit Hubs"),
        patches.Patch(facecolor="#334155", edgecolor="none", label="Urban Road Intersections"),
        plt.Line2D([0], [0], color="#0284c7", lw=3, label="FDR Drive Express Arterial"),
        plt.Line2D([0], [0], color="#ef4444", lw=3, ls="--", label="Active Road Closure (Flooded)")
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=5, fontsize=8.0, frameon=True,
               facecolor="#f8fafc", edgecolor="#cbd5e1", bbox_to_anchor=(0.5, 0.02))

    plt.tight_layout()
    plt.subplots_adjust(bottom=0.1)
    out_path = os.path.join(OUT_DIR, "fig2_network_topologies.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated {out_path}")
    sync_to_paper("fig2_network_topologies.png")


# ─────────────────────────────────────────────────────────────────────────────
# 3. Figure 3: Empirical Benchmark Results (Copy / Link from results/)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig3_benchmark_results():
    src = os.path.join(RESULTS_DIR, "real_benchmark.png")
    dst = os.path.join(OUT_DIR, "fig3_benchmark_results.png")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"✅ Synced {dst} from {src}")
        sync_to_paper("fig3_benchmark_results.png")
    else:
        print(f"⚠️ Source {src} not found!")


# ─────────────────────────────────────────────────────────────────────────────
# 4. Figure 4: Multi-Scale Scalability (Copy / Link from results/)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig4_scalability():
    src = os.path.join(RESULTS_DIR, "multi_scale_benchmark.png")
    dst = os.path.join(OUT_DIR, "fig4_scalability_multi_scale.png")
    if os.path.exists(src):
        shutil.copyfile(src, dst)
        print(f"✅ Synced {dst} from {src}")
        sync_to_paper("fig4_scalability_multi_scale.png")
    else:
        print(f"⚠️ Source {src} not found!")


# ─────────────────────────────────────────────────────────────────────────────
# 5. Figure 5: Causal Explainability Audit Flowchart (Redesigned)
# ─────────────────────────────────────────────────────────────────────────────
def generate_fig5_explainability():
    fig, ax = plt.subplots(figsize=(16, 5.2), dpi=300)
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    # Overall Figure Title
    ax.text(8.0, 4.85, "5-Dimensional Causal Explainability & Neuro-Symbolic Audit Trace",
            fontsize=14, fontweight="bold", ha="center", color="#0f172a")

    dimensions = [
        {
            "dim": "Dimension 1",
            "title": "Incident Reasoning",
            "role": "Semantic Road Exclusion",
            "items": [
                ("Alert Ingestion:", "511NY Police Bulletins"),
                ("NLP Mapping:", "'Flooding on 34th St' -> (M19, M21)"),
                ("Action:", "Edge severed in routing graph")
            ],
            "stamp": "Incident Verified ✓",
            "color": "#dc2626",
            "bg": "#fef2f2",
            "badge_bg": "#fee2e2"
        },
        {
            "dim": "Dimension 2",
            "title": "Battery Range Proof",
            "role": "Physical Energy Feasibility",
            "items": [
                ("Initial SoC:", "85.0% (EV_06)"),
                ("Needed SoC:", "20.1% (Trip + Detour)"),
                ("Reserve Buffer:", "15.0% Invariant Preserved")
            ],
            "stamp": "Range Certified ✓",
            "color": "#d97706",
            "bg": "#fffbeb",
            "badge_bg": "#fef3c7"
        },
        {
            "dim": "Dimension 3",
            "title": "Triage Arbitration",
            "role": "Ethical Priority Allocation",
            "items": [
                ("Request NYC_R01:", "Cardiac Transfer (Weight = 3.0)"),
                ("Vehicle Triage:", "High-SoC 6-seat EV allocated"),
                ("Routine Traffic:", "Commuters queued safely")
            ],
            "stamp": "Priority Approved ✓",
            "color": "#059669",
            "bg": "#ecfdf5",
            "badge_bg": "#d1fae5"
        },
        {
            "dim": "Dimension 4",
            "title": "Detour Overhead",
            "role": "Algorithmic Delay Accounting",
            "items": [
                ("Direct Path:", "14.0 min (Flooded/Blocked)"),
                ("Chosen Detour:", "17.5 min (Via 2nd Ave Corridor)"),
                ("Safety Overhead:", "+3.5 min (+25.0% delay)")
            ],
            "stamp": "Overhead Audited ✓",
            "color": "#4f46e5",
            "bg": "#eef2ff",
            "badge_bg": "#e0e7ff"
        },
        {
            "dim": "Dimension 5",
            "title": "Safety Certificate",
            "role": "Non-LLM Invariant Barrier",
            "items": [
                ("Topological Check:", "All route segments open ✓"),
                ("Capacity Check:", "Seating: 6 >= 2 passengers ✓"),
                ("Concurrency:", "0 double-booking conflicts ✓")
            ],
            "stamp": "Decision Certified ✓",
            "color": "#0284c7",
            "bg": "#f0f9ff",
            "badge_bg": "#e0f2fe"
        }
    ]

    card_w = 2.85
    card_h = 3.8
    y_card = 0.55

    for i, d in enumerate(dimensions):
        x = 0.45 + i * 3.1
        
        # Outer Card Patch
        card = patches.FancyBboxPatch(
            (x, y_card), card_w, card_h,
            boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=d["bg"], edgecolor=d["color"], lw=1.8
        )
        ax.add_patch(card)
        
        # Top Header Pill
        pill = patches.FancyBboxPatch(
            (x + 0.15, y_card + card_h - 0.55), card_w - 0.3, 0.42,
            boxstyle="round,pad=0.05,rounding_size=0.1",
            facecolor=d["color"], edgecolor="none"
        )
        ax.add_patch(pill)
        ax.text(x + card_w/2, y_card + card_h - 0.34, f"{d['dim']}: {d['title']}",
                fontsize=8.5, fontweight="bold", ha="center", va="center", color="#ffffff")
        
        # Subtitle / Role
        ax.text(x + card_w/2, y_card + card_h - 0.78, d["role"],
                fontsize=7.8, fontweight="bold", ha="center", va="center", color=d["color"])
        
        # Divider line
        ax.plot([x + 0.2, x + card_w - 0.2], [y_card + card_h - 0.95, y_card + card_h - 0.95],
                color=d["color"], lw=0.8, alpha=0.4)
        
        # Content Items (Key-Value pairs)
        y_text = y_card + card_h - 1.25
        for k, v in d["items"]:
            ax.text(x + 0.2, y_text, k, fontsize=7.2, fontweight="bold", color="#1e293b", va="center")
            ax.text(x + 0.2, y_text - 0.28, v, fontsize=7.0, color="#334155", va="center")
            y_text -= 0.65
            
        # Audit Stamp Badge (Bottom)
        stamp_pill = patches.FancyBboxPatch(
            (x + 0.3, y_card + 0.2), card_w - 0.6, 0.36,
            boxstyle="round,pad=0.05,rounding_size=0.1",
            facecolor=d["badge_bg"], edgecolor=d["color"], lw=1.0
        )
        ax.add_patch(stamp_pill)
        ax.text(x + card_w/2, y_card + 0.38, d["stamp"],
                fontsize=7.8, fontweight="bold", ha="center", va="center", color=d["color"])
        
        # Connecting Arrows between cards
        if i < 4:
            x_arrow_start = x + card_w + 0.04
            x_arrow_end = x_arrow_start + 0.17
            y_arrow = y_card + card_h / 2
            ax.annotate("", xy=(x_arrow_end, y_arrow), xytext=(x_arrow_start, y_arrow),
                        arrowprops=dict(arrowstyle="-|>", lw=2.0, color="#475569", mutation_scale=12))

    plt.tight_layout()
    out_path = os.path.join(OUT_DIR, "fig5_explainability_audit.png")
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"✅ Generated {out_path}")
    sync_to_paper("fig5_explainability_audit.png")


if __name__ == "__main__":
    print("Generating comprehensive publication-grade paper figures...")
    generate_fig1_architecture()
    generate_fig2_network_topologies()
    generate_fig3_benchmark_results()
    generate_fig4_scalability()
    generate_fig5_explainability()
    print("\n🎉 All 5 paper figures generated and synchronized successfully!")
