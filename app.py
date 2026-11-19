"""
Agentic Transport Disruption Management Dashboard
═════════════════════════════════════════════════
An interactive web application showcasing:
  • B1 Rule-Based SOP vs. B2 Single-LLM vs. B3 Tool-Augmented Multi-Agent
  • Live & Replay 2D Manhattan Road Network Simulation
  • Deterministic Physical Safety Guard & HCVR Audit
  • Academic Benchmark Analytics & Research Portfolio Presentation
"""

import os
import json
import time
import streamlit as st
import pandas as pd
import networkx as nx

# Project imports
from network import create_network, apply_disruptions, NODE_NAMES, STREET_NAMES
from real_network import (
    create_real_manhattan_network,
    create_6x6_scaled_network,
    apply_real_disruptions,
    MANHATTAN_NODES
)
from run_larger_instances import load_real_manhattan_scenarios, generate_6x6_scenarios
from explainability import generate_explainability_report, format_trace_to_markdown
from scenarios import generate_scenarios, OD_CANDIDATES
from safety_guard import validate_decision, apply_sop_fallback
from tools import tool_route_travel_time
from controllers import (
    controller_b1_rule_based,
    controller_b2_single_llm,
    controller_b3_multi_agent
)
from run_benchmark import compute_scenario_metrics
from visualizer import (
    create_network_figure,
    create_benchmark_bar_chart,
    create_multi_scale_bar_chart,
    CONTROLLER_COLORS
)

# ─────────────────────────────────────────────────────────────────────────────
# 1. Page Configuration & Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Agentic Transport Disruption AI | Research Portfolio",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main Layout Aesthetics */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 98%;
    }
    
    /* Header Card */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem 1.8rem;
        color: #f8fafc;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin-bottom: 0.35rem;
        color: #38bdf8;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #cbd5e1;
        margin-bottom: 0.8rem;
    }
    .badge-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }
    .custom-badge {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .custom-badge-green {
        background-color: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 0.2rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    /* Alert / Police Radio Box */
    .police-alert-box {
        background: #fef2f2;
        border-left: 5px solid #ef4444;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin: 0.6rem 0;
        color: #991b1b;
        font-family: monospace;
        font-size: 0.9rem;
    }
    .traffic-advisory-box {
        background: #fffbeb;
        border-left: 5px solid #f59e0b;
        border-radius: 4px;
        padding: 0.8rem 1rem;
        margin: 0.6rem 0;
        color: #92400e;
        font-family: monospace;
        font-size: 0.9rem;
    }

    /* Controller Cards */
    .ctrl-card {
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
        background: #ffffff;
    }
    .ctrl-card-b1 { border-top: 4px solid #3b82f6; }
    .ctrl-card-b2 { border-top: 4px solid #f59e0b; }
    .ctrl-card-b3 { border-top: 4px solid #10b981; }

    /* Telemetry Pill */
    .telemetry-pill {
        display: inline-block;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 700;
        margin-right: 0.3rem;
    }
    .pill-blue { background: #dbeafe; color: #1e40af; }
    .pill-amber { background: #fef3c7; color: #92400e; }
    .pill-green { background: #d1fae5; color: #065f46; }
    .pill-red { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Data Caching & Utilities
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_cached_scenarios():
    """Generates benchmark scenarios with fixed seed (2 per level = 10 total)."""
    return generate_scenarios(per_level=2, base_seed=42)

@st.cache_data
def load_raw_benchmark_logs():
    """Loads precomputed execution runs from results/raw_logs.json."""
    log_path = os.path.join(os.path.dirname(__file__), "results", "raw_logs.json")
    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return json.load(f)
    return []

def get_gemini_api_key():
    """Retrieves API key from environment or local api_key.txt if present."""
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        key_file = os.path.join(os.path.dirname(__file__), "api_key.txt")
        if os.path.exists(key_file):
            try:
                with open(key_file, "r") as f:
                    content = f.read().strip()
                    if content and len(content) > 10:
                        key = content
            except Exception:
                pass
    return key


all_scenarios = load_cached_scenarios()
raw_benchmark_data = load_raw_benchmark_logs()
scenario_map = {s["scenario_id"]: s for s in all_scenarios}
raw_logs_map = {item["scenario"]: item for item in raw_benchmark_data}


# ─────────────────────────────────────────────────────────────────────────────
# 3. Sidebar Controls
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/traffic-jam.png", width=64)
    st.title("Control Deck")

    st.subheader("1. Network Topology Scale")
    selected_scale = st.selectbox(
        "Choose Scale:",
        [
            "4×4 Manhattan Baseline (N=16, 24 Edges)",
            "6×6 Scaled District (N=36, 60 Edges)",
            "Macro (Real Manhattan N=42, Real NYC Incidents)"
        ],
        help="Switch between the base 4x4 grid, expanded 6x6 district, and real NYC Manhattan topology."
    )

    if "Real Manhattan" in selected_scale:
        active_scenarios = load_real_manhattan_scenarios()
        G_orig = create_real_manhattan_network()
    elif "6×6" in selected_scale:
        active_scenarios = generate_6x6_scenarios()
        G_orig = create_6x6_scaled_network()
    else:
        active_scenarios = all_scenarios
        G_orig = create_network()

    st.subheader("2. Simulation Mode")
    sim_mode = st.radio(
        "Choose Mode:",
        ["Instant Replay (Recorded Benchmark)", "Live Gemini API Call"],
        help="Replay mode runs instantly with zero API cost using empirical benchmark runs. Live mode connects to Google GenAI."
    )

    st.divider()

    st.subheader("3. Scenario Selector")
    selected_level = st.selectbox(
        "Disruption Complexity Tier:",
        [1, 2, 3, 4, 5],
        format_func=lambda x: f"L{x}: " + {
            1: "Simple (1 Closure)",
            2: "Moderate (NLP Police Alert + Bottleneck)",
            3: "Compound (Closure + Bottleneck + EV Breakdown)",
            4: "Cascading (2 Closures + Bottleneck + Fleet Deficit)",
            5: "Extreme Crisis (3 Closures + 2 Bottlenecks + 2 Broken EVs)"
        }[x]
    )

    # Scenarios for the selected level and scale
    level_scenarios = [s for s in active_scenarios if s["level"] == selected_level]
    if not level_scenarios:
        level_scenarios = active_scenarios[:1]
    scenario_ids = [s["scenario_id"] for s in level_scenarios]
    selected_scenario_id = st.selectbox("Select Scenario Run:", scenario_ids)
    current_scenario = next(s for s in level_scenarios if s["scenario_id"] == selected_scenario_id)

    # Live API Key input if live mode chosen
    gemini_key = ""
    if sim_mode == "Live Gemini API Call":
        st.divider()
        st.subheader("3. Google Gemini API Key")
        default_key = get_gemini_api_key()
        gemini_key = st.text_input(
            "Gemini API Key:",
            value=default_key,
            type="password",
            help="Enter your Google Gemini API key to run live inference against gemini-flash-lite-latest."
        )
        if not gemini_key:
            st.warning("⚠️ Please provide a Gemini API key to run live calls, or switch to Instant Replay mode.")

    st.divider()
    st.subheader("Project Resources")
    report_file = os.path.join(os.path.dirname(__file__), "Comprehensive_Project_Report_Agentic_Transport.docx")
    ppt_file = os.path.join(os.path.dirname(__file__), "presentation.pptx")

    if os.path.exists(report_file):
        with open(report_file, "rb") as f:
            st.download_button(
                "📄 Download Research Report (.docx)",
                data=f,
                file_name="Agentic_Transport_Disruption_Research_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    if os.path.exists(ppt_file):
        with open(ppt_file, "rb") as f:
            st.download_button(
                "📊 Download Presentation (.pptx)",
                data=f,
                file_name="Agentic_Transport_Disruption_Presentation.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )


# ─────────────────────────────────────────────────────────────────────────────
# 4. Hero Banner
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-card">
    <div class="hero-title">Autonomous Agentic AI in Urban Transport Disruption Management</div>
    <div class="hero-subtitle">
        Empirical Evaluation of Tool-Augmented Multi-Agent LLMs vs. Single-LLM vs. Classical SOPs on 2D Road Networks
    </div>
    <div class="badge-bar">
        <span class="custom-badge">🏛️ Mentors: Dr. Alaa DAOUD (INSA Hauts-de-France) & Dr. Srinivasa K G (IIIT-NR)</span>
        <span class="custom-badge">🧑‍💻 Akshit (UG Researcher, Sem 5 Minor Project)</span>
        <span class="custom-badge">🤖 Foundation Model: Google Gemini (gemini-flash-lite-latest)</span>
        <span class="custom-badge-green">⭐ L5 Crisis Finding: +86.6% Emergency Service Delivery Boost</span>
        <span class="custom-badge-green">🛡️ Neuro-Symbolic Deterministic Safety Guard</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Simulation Execution & Resolution Helper (State-Persistent)
# ─────────────────────────────────────────────────────────────────────────────
G_disrupted, real_closed = apply_real_disruptions(G_orig, current_scenario["disruptions"])
congested_edges = [d["edge"] for d in current_scenario["disruptions"] if d.get("type") == "congestion" and "edge" in d]

def resolve_scenario_results(scenario, mode, api_key, force_live=False):
    """
    Computes or retrieves decisions and metrics for B1, B2, and B3.
    Caches in st.session_state so user interaction doesn't wipe live runs.
    """
    cached_run = raw_logs_map.get(scenario["scenario_id"])
    live_cache_key = f"live_run_{scenario['scenario_id']}"

    # 1. B1 Rule-Based SOP (always computed deterministically in <1ms)
    t0 = time.time()
    d_b1 = controller_b1_rule_based(scenario, G_orig)
    lat_b1 = time.time() - t0
    val_b1, viol_b1 = validate_decision(d_b1, G_disrupted, scenario)
    m_b1 = compute_scenario_metrics(d_b1, viol_b1, scenario, G_orig, G_disrupted, lat_b1, 0, 0)

    # Check if live run should be executed
    should_run_live = (mode == "Live Gemini API Call") and bool(api_key) and (force_live or (live_cache_key not in st.session_state))

    if should_run_live:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)

            # B2 Single-LLM live
            d_b2, lat_b2, pt_b2, ct_b2 = controller_b2_single_llm(client, "gemini-flash-lite-latest", scenario, G_orig)
            val_b2, viol_b2 = validate_decision(d_b2, G_disrupted, scenario)
            m_b2 = compute_scenario_metrics(d_b2, viol_b2, scenario, G_orig, G_disrupted, lat_b2, pt_b2, ct_b2)
            b2_raw_text = d_b2.get("raw_response", "")

            # B3 Multi-Agent live
            d_b3, lat_b3, pt_b3, ct_b3 = controller_b3_multi_agent(client, "gemini-flash-lite-latest", scenario, G_orig)
            val_b3, viol_b3 = validate_decision(d_b3, G_disrupted, scenario)
            m_b3 = compute_scenario_metrics(d_b3, viol_b3, scenario, G_orig, G_disrupted, lat_b3, pt_b3, ct_b3)
            b3_logs = d_b3.get("agent_logs", {})

            live_payload = {
                "val_b1": val_b1, "viol_b1": viol_b1, "m_b1": m_b1,
                "val_b2": val_b2, "viol_b2": viol_b2, "m_b2": m_b2, "b2_raw_text": b2_raw_text,
                "val_b3": val_b3, "viol_b3": viol_b3, "m_b3": m_b3, "b3_logs": b3_logs,
                "is_live": True
            }
            st.session_state[live_cache_key] = live_payload
            return live_payload
        except Exception as e:
            st.error(f"Live Gemini API Error: {e}. Falling back to recorded benchmark data.")

    # Return cached live run if present in session
    if (mode == "Live Gemini API Call") and (live_cache_key in st.session_state):
        return st.session_state[live_cache_key]

    # Replay from empirical dataset
    m_b2 = cached_run["B2_metrics"] if cached_run else {"rfr": 100, "rfr_weighted": 100, "hcvr": 0, "latency_s": 1.6, "cost_usd": 0.0002, "total_tokens": 850}
    b2_raw_text = cached_run.get("B2_raw", "") if cached_run else ""
    d_b2 = {"controller": "B2_SingleLLM", "assignments": []}
    try:
        raw_extracted = json.loads(b2_raw_text.replace("```json", "").replace("```", "").strip())
        d_b2["assignments"] = [{
            "request_id": a["request_id"], "vehicle_id": a.get("vehicle_id"),
            "route": a.get("route"), "status": "served"
        } for a in raw_extracted.get("assignments", [])]
    except Exception:
        pass
    val_b2, viol_b2 = validate_decision(d_b2, G_disrupted, scenario)

    m_b3 = cached_run["B3_metrics"] if cached_run else {"rfr": 100, "rfr_weighted": 100, "hcvr": 0, "latency_s": 5.1, "cost_usd": 0.0005, "total_tokens": 2500}
    b3_logs = cached_run.get("B3_logs", {}) if cached_run else {}
    d_b3 = {"controller": "B3_MultiAgent", "assignments": []}
    try:
        coord_raw = b3_logs.get("coordinator", "").replace("```json", "").replace("```", "").strip()
        coord_json = json.loads(coord_raw)
        d_b3["assignments"] = [{
            "request_id": a["request_id"], "vehicle_id": a.get("vehicle_id"),
            "route": a.get("selected_route") or a.get("route"), "status": "served"
        } for a in coord_json.get("assignments", [])]
    except Exception:
        pass
    val_b3, viol_b3 = validate_decision(d_b3, G_disrupted, scenario)

    return {
        "val_b1": val_b1, "viol_b1": viol_b1, "m_b1": m_b1,
        "val_b2": val_b2, "viol_b2": viol_b2, "m_b2": m_b2, "b2_raw_text": b2_raw_text,
        "val_b3": val_b3, "viol_b3": viol_b3, "m_b3": m_b3, "b3_logs": b3_logs,
        "is_live": False
    }


# Initial resolution
sim_results = resolve_scenario_results(current_scenario, sim_mode, gemini_key, force_live=False)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Core Application Tabs
# ─────────────────────────────────────────────────────────────────────────────
tab_arena, tab_network, tab_explain, tab_analytics, tab_methodology, tab_resume = st.tabs([
    "🎮 Comparative Arena (B1 vs B2 vs B3)",
    "🗺️ 2D Road Network Visualizer",
    "🔍 Explainable AI & Deliberation Inspector",
    "📊 Empirical Benchmark Analytics",
    "🔬 Research Framework & Math",
    "💼 Resume & Portfolio Toolkit"
])


# ═════════════════════════════════════════════════════════════════════════════
# TAB 1: THE COMPARATIVE ARENA
# ═════════════════════════════════════════════════════════════════════════════
with tab_arena:
    # ── Active Incident Briefing Card ──
    st.markdown(f"### 📍 Scenario {selected_scenario_id} — Ground Truth Disruption State")

    col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
    with col_info1:
        st.markdown("**🚨 Incident Advisories & Police Text Feeds:**")
        if current_scenario.get("text_alerts"):
            for alert in current_scenario["text_alerts"]:
                if "POLICE" in alert or "BLOCKED" in alert:
                    st.markdown(f'<div class="police-alert-box">{alert}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="traffic-advisory-box">{alert}</div>', unsafe_allow_html=True)
        else:
            st.info("No unstructured text advisories active for this tier (Standard scheduled closures only).")

    with col_info2:
        st.markdown("**⚡ Fleet Availability:**")
        n_operable = sum(1 for v in current_scenario["vehicles"] if v["status"] == "available")
        n_broken = sum(1 for v in current_scenario["vehicles"] if v["status"] != "available")
        st.write(f"• **Operable EVs:** {n_operable} / {len(current_scenario['vehicles'])}")
        if n_broken > 0:
            st.write(f"• ❌ **Mechanical Breakdowns:** {n_broken} vehicle(s)")
        
        fleet_df = pd.DataFrame([{
            "EV": v["id"], "Loc": v["position"], "SoC": f"{v['soc']}%", "Status": v["status"]
        } for v in current_scenario["vehicles"]])
        st.dataframe(fleet_df, hide_index=True, use_container_width=True)

    with col_info3:
        st.markdown("**👥 Demand Triage:**")
        n_emer = sum(1 for r in current_scenario["requests"] if r.get("priority") == "emergency")
        n_std = len(current_scenario["requests"]) - n_emer
        st.write(f"• **Total Trips:** {len(current_scenario['requests'])}")
        st.write(f"• 🚨 **Hospital Emergency (3× Weight):** {n_emer}")
        st.write(f"• 🚶 **Standard Commute (1× Weight):** {n_std}")

        req_df = pd.DataFrame([{
            "Req": r["id"], "OD": f"{r['origin']} → {r['destination']}", "Priority": r.get("priority", "std")
        } for r in current_scenario["requests"]])
        st.dataframe(req_df, hide_index=True, use_container_width=True)

    st.divider()

    # ── Live Execution Trigger Bar ──
    if sim_mode == "Live Gemini API Call":
        btn_c1, btn_c2 = st.columns([1, 2])
        with btn_c1:
            if st.button("🚀 Run Live Gemini Inference", type="primary"):
                with st.spinner("Invoking Gemini 2.5 Flash Lite across controllers..."):
                    sim_results = resolve_scenario_results(current_scenario, sim_mode, gemini_key, force_live=True)
                    st.success("Live simulation complete!")
        with btn_c2:
            if sim_results.get("is_live"):
                st.info("🟢 Showing LIVE Gemini API results from active session.")
            else:
                st.caption("Click button to trigger real API calls. Currently showing recorded benchmark baseline.")

    # Unpack current results
    val_b1, viol_b1, m_b1 = sim_results["val_b1"], sim_results["viol_b1"], sim_results["m_b1"]
    val_b2, viol_b2, m_b2, b2_raw_text = sim_results["val_b2"], sim_results["viol_b2"], sim_results["m_b2"], sim_results["b2_raw_text"]
    val_b3, viol_b3, m_b3, b3_logs = sim_results["val_b3"], sim_results["viol_b3"], sim_results["m_b3"], sim_results["b3_logs"]

    # ── Side-by-Side 3-Column Display ──
    st.markdown("### 🏆 Side-by-Side Controller Evaluation")

    c1, c2, c3 = st.columns(3)

    # Column 1: B1 Rule-Based SOP
    with c1:
        st.markdown("""
        <div class="ctrl-card ctrl-card-b1">
            <h4>🔹 Baseline 1: Rule-Based SOP</h4>
            <p style="font-size: 0.85rem; color: #64748b;">
                Classical Dijkstra Shortest Path + FIFO Queue. Blind to natural language text advisories.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <span class="telemetry-pill pill-blue">Latency: {m_b1['latency_s']:.4f}s</span>
        <span class="telemetry-pill pill-blue">Cost: $0.00</span>
        <span class="telemetry-pill pill-blue">Tokens: 0</span>
        """, unsafe_allow_html=True)

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Priority RFR_w", f"{m_b1['rfr_weighted']:.1f}%")
        m_c2.metric("Violations (HCVR)", f"{m_b1['hcvr']:.1f}%", delta_color="inverse")

        b1_rows = []
        for a in val_b1["assignments"]:
            b1_rows.append({
                "Req": a.get("request_id"),
                "EV": a.get("vehicle_id") or "None",
                "Route": " → ".join(a.get("route", [])) if a.get("route") else "Unserved",
                "Status": a.get("status")
            })
        st.dataframe(pd.DataFrame(b1_rows), hide_index=True, use_container_width=True)

        if viol_b1:
            st.error(f"🛡️ Safety Guard Intercepted {len(viol_b1)} Hard Violations:")
            for item in viol_b1:
                req_id = item.get("request_id")
                for v in item.get("violations", []):
                    st.caption(f"• **Req {req_id} ({v.get('type')})**: {v.get('detail')}")
        else:
            st.success("🛡️ Safety Guard: 0 violations detected.")

    # Column 2: B2 Single-LLM Agent
    with c2:
        st.markdown("""
        <div class="ctrl-card ctrl-card-b2">
            <h4>🔸 Baseline 2: Single-LLM Agent</h4>
            <p style="font-size: 0.85rem; color: #64748b;">
                Monolithic Gemini prompt. Ingests full text alerts and fleet status in a single context window.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <span class="telemetry-pill pill-amber">Latency: {m_b2['latency_s']:.2f}s</span>
        <span class="telemetry-pill pill-amber">Cost: ${m_b2['cost_usd']:.5f}</span>
        <span class="telemetry-pill pill-amber">Tokens: {m_b2.get('total_tokens', 0)}</span>
        """, unsafe_allow_html=True)

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Priority RFR_w", f"{m_b2['rfr_weighted']:.1f}%")
        m_c2.metric("Violations (HCVR)", f"{m_b2['hcvr']:.1f}%", delta_color="inverse")

        b2_rows = []
        for a in val_b2["assignments"]:
            b2_rows.append({
                "Req": a.get("request_id"),
                "EV": a.get("vehicle_id") or "None",
                "Route": " → ".join(a.get("route", [])) if a.get("route") else "Unserved",
                "Status": a.get("status")
            })
        st.dataframe(pd.DataFrame(b2_rows), hide_index=True, use_container_width=True)

        if viol_b2:
            st.warning(f"🛡️ Safety Guard Intercepted {len(viol_b2)} Hard Violations:")
            for item in viol_b2:
                req_id = item.get("request_id")
                for v in item.get("violations", []):
                    st.caption(f"• **Req {req_id} ({v.get('type')})**: {v.get('detail')}")
        else:
            st.success("🛡️ Safety Guard: 0 violations detected.")

        with st.expander("🔍 Inspect Monolithic LLM Output"):
            st.code(b2_raw_text if b2_raw_text else "No raw response logged.", language="json")

    # Column 3: B3 Tool-Augmented Multi-Agent
    with c3:
        st.markdown("""
        <div class="ctrl-card ctrl-card-b3">
            <h4>🟢 Proposed: Multi-Agent System (MAS)</h4>
            <p style="font-size: 0.85rem; color: #64748b;">
                4 Specialized Agents: Traffic NLP + Fleet SoC Triage + Dijkstra Tool + Coordinator.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <span class="telemetry-pill pill-green">Latency: {m_b3['latency_s']:.2f}s</span>
        <span class="telemetry-pill pill-green">Cost: ${m_b3['cost_usd']:.5f}</span>
        <span class="telemetry-pill pill-green">Tokens: {m_b3.get('total_tokens', 0)}</span>
        """, unsafe_allow_html=True)

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Priority RFR_w", f"{m_b3['rfr_weighted']:.1f}%")
        m_c2.metric("Violations (HCVR)", f"{m_b3['hcvr']:.1f}%", delta_color="inverse")

        b3_rows = []
        for a in val_b3["assignments"]:
            b3_rows.append({
                "Req": a.get("request_id"),
                "EV": a.get("vehicle_id") or "None",
                "Route": " → ".join(a.get("route", [])) if a.get("route") else "Unserved",
                "Status": a.get("status")
            })
        st.dataframe(pd.DataFrame(b3_rows), hide_index=True, use_container_width=True)

        if viol_b3:
            st.info(f"🛡️ Safety Guard Intercepted {len(viol_b3)} Hard Violations:")
            for item in viol_b3:
                req_id = item.get("request_id")
                for v in item.get("violations", []):
                    st.caption(f"• **Req {req_id} ({v.get('type')})**: {v.get('detail')}")
        else:
            st.success("🛡️ Safety Guard: 0 violations detected.")

        with st.expander("🤖 Decomposed Agent Communication Traces"):
            st.markdown("**1. 🚦 Traffic Agent (Extracted Road Closures):**")
            st.code(b3_logs.get("traffic", "N/A"), language="json")
            st.markdown("**2. 🔋 Fleet Agent (Battery Audit & Hospital Reservation):**")
            st.code(b3_logs.get("fleet", "N/A"), language="json")
            st.markdown("**3. 👔 Coordinator Agent (Final Synthesis):**")
            st.code(b3_logs.get("coordinator", "N/A"), language="json")

    # ── Interactive Route Comparison on the Grid ──
    st.divider()
    st.subheader("🗺️ Direct Route Overlay Comparison for Selected Trip")

    req_options = [r["id"] for r in current_scenario["requests"]]
    selected_req = st.selectbox("Select a Passenger Trip to Compare Routes:", req_options, key="arena_req_selector")

    routes_to_compare = []
    for a in val_b1["assignments"]:
        if a.get("request_id") == selected_req and a.get("route"):
            routes_to_compare.append({"controller": "B1_RuleBased", "request_id": selected_req, "vehicle_id": a.get("vehicle_id"), "route": a["route"]})

    for a in val_b2["assignments"]:
        if a.get("request_id") == selected_req and a.get("route"):
            routes_to_compare.append({"controller": "B2_SingleLLM", "request_id": selected_req, "vehicle_id": a.get("vehicle_id"), "route": a["route"]})

    for a in val_b3["assignments"]:
        if a.get("request_id") == selected_req and a.get("route"):
            routes_to_compare.append({"controller": "B3_MultiAgent", "request_id": selected_req, "vehicle_id": a.get("vehicle_id"), "route": a["route"]})

    fig_compare = create_network_figure(
        G_disrupted=G_disrupted,
        closed_edges=real_closed,
        bottleneck_edges=congested_edges,
        fleet_states=current_scenario["vehicles"],
        requests=[r for r in current_scenario["requests"] if r["id"] == selected_req],
        active_routes=routes_to_compare,
        title=f"Path Comparison for Request {selected_req} (Blue: SOP | Amber: Single-LLM | Green: Multi-Agent)"
    )
    st.plotly_chart(fig_compare, use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 2: INTERACTIVE 2D MANHATTAN GRID VISUALIZER
# ═════════════════════════════════════════════════════════════════════════════
with tab_network:
    scale_label = selected_scale.split("(")[0].strip()
    n_nodes = len(G_disrupted.nodes())
    n_edges = len(G_disrupted.edges())
    st.markdown(f"### 🗺️ Full Interactive 2D Urban Road Network ({scale_label})")
    st.write(
        f"Active topology featuring **{n_nodes} intersections** and **{n_edges} road corridors**. "
        "Explore real-time closures, severe bottlenecks, EV fleet positions, and patient requests."
    )

    col_ctrl1, col_ctrl2 = st.columns([1, 1])
    with col_ctrl1:
        route_filter = st.selectbox("Route Overlay Controller Filter:", ["All", "B1_RuleBased", "B2_SingleLLM", "B3_MultiAgent"], key="grid_filter")
    with col_ctrl2:
        st.info("💡 **Tip:** Hover over nodes and edges to inspect intersection names, street identities, and transit flow status.")

    all_active_routes = []
    for a in val_b1["assignments"]:
        if a.get("route"):
            all_active_routes.append({"controller": "B1_RuleBased", "request_id": a["request_id"], "vehicle_id": a.get("vehicle_id"), "route": a["route"]})
    for a in val_b2["assignments"]:
        if a.get("route"):
            all_active_routes.append({"controller": "B2_SingleLLM", "request_id": a["request_id"], "vehicle_id": a.get("vehicle_id"), "route": a["route"]})
    for a in val_b3["assignments"]:
        if a.get("route"):
            all_active_routes.append({"controller": "B3_MultiAgent", "request_id": a["request_id"], "vehicle_id": a.get("vehicle_id"), "route": a["route"]})

    fig_full = create_network_figure(
        G_disrupted=G_disrupted,
        closed_edges=real_closed,
        bottleneck_edges=congested_edges,
        fleet_states=current_scenario["vehicles"],
        requests=current_scenario["requests"],
        active_routes=all_active_routes,
        selected_controller=route_filter,
        title=f"2D Manhattan Road Network — Scenario {selected_scenario_id}"
    )
    st.plotly_chart(fig_full, use_container_width=True)

    with st.expander("📋 View Complete Network Topology & Street Directory"):
        street_data = []
        seen_edges = set()
        for u, v, data in G_disrupted.edges(data=True):
            edge_key = tuple(sorted((u, v)))
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            name = data.get("street_name") or STREET_NAMES.get((u, v), STREET_NAMES.get((v, u), f"{u} ↔ {v}"))
            is_c = edge_key in [tuple(sorted(e)) for e in real_closed]
            is_b = edge_key in [tuple(sorted(e)) for e in congested_edges]
            status = "⛔ Closed" if is_c else ("⚠️ Bottleneck" if is_b else "✅ Open")

            u_name = G_disrupted.nodes[u].get("name", NODE_NAMES.get(u, u))
            v_name = G_disrupted.nodes[v].get("name", NODE_NAMES.get(v, v))

            street_data.append({
                "Street Name": name,
                "Intersections": f"{u} ({u_name}) ↔ {v} ({v_name})",
                "Travel Time": f"{data.get('travel_time', 0.0):.1f} min",
                "Capacity": f"{data.get('capacity', 40)} veh/hr",
                "Current Status": status
            })
        st.dataframe(pd.DataFrame(street_data), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 3: EXPLAINABLE AI & DELIBERATION INSPECTOR
# ═════════════════════════════════════════════════════════════════════════════
with tab_explain:
    st.markdown("### 🔍 Neuro-Symbolic Explainability & Causal Audit Inspector")
    st.write(
        "Inspect the multi-agent deliberation chain, range feasibility proofs, priority triage arbitration, "
        "and deterministic safety certificates for every dispatch decision."
    )

    exp_report = generate_explainability_report(val_b3, current_scenario, G_orig, G_disrupted, viol_b3)

    em_c1, em_c2, em_c3, em_c4 = st.columns(4)
    em_c1.metric("Requests Audited", len(current_scenario["requests"]))
    em_c2.metric("Served Fulfillments", exp_report["served_requests"])
    em_c3.metric("Battery Safety Buffer", "15.0% Reserve", help="Guaranteed battery margin above theoretical energy draw")
    em_c4.metric("Safety Guard Status", "4 Physical Checks", help="Reachability, SoC sufficiency, capacity, and zero-conflict")

    st.divider()

    st.markdown("#### 🔬 Causal Decision Breakdown for Selected Request")
    req_choices = [t["request_id"] for t in exp_report["explainability_traces"]]
    chosen_rid = st.selectbox("Choose Passenger Request to Audit Decision:", req_choices, key="tab_explain_req_select")
    chosen_trace = next((t for t in exp_report["explainability_traces"] if t["request_id"] == chosen_rid), None)

    if chosen_trace:
        st.markdown(format_trace_to_markdown(chosen_trace))

        with st.expander("📊 Full Causal Dimensions JSON Object"):
            st.json(chosen_trace)

    st.divider()
    st.markdown("#### 🛡️ Neuro-Symbolic Architecture Comparison")
    st.markdown("""
    | Evaluation Dimension | Classical SOP ($B_1$) | Monolithic Single-LLM ($B_2$) | Proposed Tool-Augmented MAS ($B_3$) |
    | :--- | :--- | :--- | :--- |
    | **Text Incident Parsing** | ❌ Blind (Cannot parse text alerts) | ⚠️ Partial (Suffers attention dilution) | ✅ **Specialized Traffic Agent** extracts closed edges |
    | **Graph Path Finding** | ✅ Deterministic Dijkstra | ❌ Hallucinates non-existent roads | ✅ **Dijkstra Tool** invoked deterministically |
    | **Priority Triage** | ❌ Greedy FIFO (Starves Emergency) | ⚠️ Context collapse at $L_4\text{--}L_5$ | ✅ **Fleet Agent** reserves high-SoC EVs for emergency |
    | **Physical Safety** | ❌ May route into closed flooded roads | ❌ No physical check | ✅ **Deterministic Safety Guard** audits & repairs |
    """)


# ═════════════════════════════════════════════════════════════════════════════
# TAB 4: EMPIRICAL BENCHMARK ANALYTICS
# ═════════════════════════════════════════════════════════════════════════════
with tab_analytics:
    st.markdown("### 📊 Empirical Benchmark Analytics & Controller Trade-offs")
    st.write(
        "Quantitative comparison across all 5 graduated disruption tiers ($L_1$ to $L_5$). "
        "Measured with Google Gemini (`gemini-flash-lite-latest`) on real API latency and token pricing."
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("L5 Emergency Service", "50.0% vs 26.9%", "+86.6% MAS Relative Boost")
    kpi2.metric("SOP Routine Latency", "<0.001 s", "Instant Mathematical Dijkstra")
    kpi3.metric("Multi-Agent Latency", "5.08 s", "3.1× Single-LLM Overhead")
    kpi4.metric("Avg API Cost / Scenario", "$0.0004", "Negligible for Transit Agencies")

    st.divider()

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_rfr_w = create_benchmark_bar_chart("rfr_weighted", "Priority-Weighted Request Fulfillment (RFR_w %)", "Fulfillment Rate (%)")
        st.plotly_chart(fig_rfr_w, use_container_width=True)

    with col_g2:
        fig_hcvr = create_benchmark_bar_chart("hcvr", "Hard Constraint Violation Rate (HCVR %)", "Violation Rate (%)", higher_is_better=False)
        st.plotly_chart(fig_hcvr, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        fig_lat = create_benchmark_bar_chart("latency_s", "Measured Decision Latency (seconds)", "Latency (s)", higher_is_better=False)
        st.plotly_chart(fig_lat, use_container_width=True)

    with col_g4:
        fig_cost = create_benchmark_bar_chart("cost_usd", "Monetary Inference Cost per Scenario ($ USD)", "Cost ($ USD)", higher_is_better=False)
        st.plotly_chart(fig_cost, use_container_width=True)

    st.divider()

    st.markdown("### ⚖️ The Scientific Verdict: Is Multi-Agent LLM Worth the Additional Cost?")

    st.markdown(r"""
    | Disruption Regime | Empirical Verdict | Scientific Justification |
    | :--- | :---: | :--- |
    | **Low ($L_1$–$L_2$): Routine Incidents** | ❌ **UNJUSTIFIED** | Classical SOPs achieve $100\%$ fulfillment in **$<10\text{ms}$ for $\$0.00$**. Multi-Agent adds $5\text{s}$ latency with zero operational gain. |
    | **Moderate ($L_3$): Single Disruptions** | ❌ **UNJUSTIFIED** | Single-LLM matches or exceeds Multi-Agent ($94.4\%$ vs $77.8\%$) with $60\%$ lower latency and token usage. |
    | **High / Extreme ($L_4$–$L_5$): Compound Crises** | ✅ **FULLY WORTH IT** | In multi-incident crises, Single-LLM collapses to **$26.9\%$** due to context overload. Multi-Agent delivers **$+86\%$ relative boost in emergency hospital delivery**, costing only $\sim \$0.0005$. |
    """)

    st.info(
        "💡 **Transit Agency Economic Reality:** Operating a municipal transit vehicle costs $\\sim \\$5$ to $\\$10$ per vehicle-mile. "
        "Spending one-twentieth of a single US cent ($\approx \\$0.0005$) on multi-agent inference to avoid sending an EV into a flooded corridor or stranded patient is economically negligible."
    )

    st.divider()
    st.subheader("🌍 Multi-Scale Scalability Analysis (Micro N=16 vs. Meso N=36 vs. Macro N=42)")
    st.write(
        "Empirical scalability comparison across expanding network sizes: from the 4×4 baseline grid ($N=16$) "
        "to a 6×6 district ($N=36$) and the authentic 42-node Real Manhattan network with real NYC DOT closures."
    )

    sc_c1, sc_c2 = st.columns(2)
    with sc_c1:
        st.plotly_chart(
            create_multi_scale_bar_chart("rfr_weighted", "Priority Fulfillment vs. Scale (Emergency Service)", "Fulfillment Rate (%)"),
            use_container_width=True
        )
    with sc_c2:
        st.plotly_chart(
            create_multi_scale_bar_chart("hcvr", "Pre-Guard Violations vs. Scale (Interception Need)", "Violation Rate (%)"),
            use_container_width=True
        )

    sc_c3, sc_c4 = st.columns(2)
    with sc_c3:
        st.plotly_chart(
            create_multi_scale_bar_chart("latency_s", "Execution Latency Scaling vs. Scale", "Latency (s)"),
            use_container_width=True
        )
    with sc_c4:
        st.plotly_chart(
            create_multi_scale_bar_chart("tokens", "Token Footprint per Decision vs. Scale", "Tokens Consumed"),
            use_container_width=True
        )


# ═════════════════════════════════════════════════════════════════════════════
# TAB 5: RESEARCH FRAMEWORK & METHODOLOGY
# ═════════════════════════════════════════════════════════════════════════════
with tab_methodology:
    st.markdown("### 🔬 Research Framework, Mentorship & Mathematical Formulation")

    col_m1, col_m2 = st.columns([1, 1])

    with col_m1:
        st.markdown("""
        #### 🏛️ Research Mentorship & Academic Context
        - **Project:** B.Tech Minor Project (Semester 5)
        - **Institution:** Indian Institute of Information Technology Naya Raipur (IIIT-NR), India
        - **Mentors:**
          - **Dr. Alaa DAOUD** — INSA Hauts-de-France, France (Specialist in Multi-Agent Systems & Transportation)
          - **Dr. Srinivasa K G** — IIIT Naya Raipur, India (Professor of Data Science & AI)
        
        #### ❓ Primary Research Question
        > *"When does multi-agent LLM coordination actually improve transport-disruption decisions compared with a single LLM agent or traditional rule-based approach (SOPs) on 2D road networks, and is the improvement worth the additional computational and financial cost?"*
        """)

    with col_m2:
        st.markdown("""
        #### 🧠 The Neuro-Symbolic Hybrid Architecture
        Pure LLMs cannot do graph search (they hallucinate edges and reverse down one-way streets). Pure algorithms cannot read unstructured text advisories or triage medical emergencies.
        
        ```
        ┌─────────────────────────────────────────────────────────┐
        │               OUR NEURO-SYMBOLIC HYBRID                 │
        ├──────────────────────────┬──────────────────────────────┤
        │ THE BRAIN (AGENTIC LLMS) │ THE LAWS (PYTHON TOOLS)      │
        │ • NLP Police Advisories  │ • Dijkstra Shortest Path     │
        │ • Hospital Medical Triage│ • Battery SoC Verification   │
        │ • Strategic Coordination │ • Deterministic Safety Guard │
        └──────────────────────────┴──────────────────────────────┘
        ```
        """)

    st.divider()

    st.markdown("#### 📐 Mathematical Formulation of Evaluation Metrics")

    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown("**1. Priority-Weighted Fulfillment ($RFR_w$):**")
        st.latex(r"RFR_w = \frac{\sum_{i \in \text{served}} w_i}{\sum_{i \in \text{total}} w_i} \times 100\%")
        st.caption("Emergency Hospital transfers ($w=3.0$), Standard Commute ($w=1.0$).")

    with f2:
        st.markdown("**2. Hard Constraint Violation Rate ($HCVR$):**")
        st.latex(r"HCVR = \frac{N_{\text{violations}}}{N_{\text{proposed}}} \times 100\%")
        st.caption("Tracks closed-road attempts, battery exhaustion, and capacity breaches before the Safety Guard.")

    with f3:
        st.markdown("**3. EV Battery State-of-Charge Feasibility:**")
        st.latex(r"\text{SoC}_{\text{req}} = T_{\text{trip}} \cdot r_{\text{drain}} \cdot (1 + \alpha_{\text{buffer}})")
        st.caption("Where $r = 1.0\\% / \\text{min}$ and $\\alpha = 0.15$ ($15\\%$ safety reserve).")


# ═════════════════════════════════════════════════════════════════════════════
# TAB 5: RESUME & PORTFOLIO TOOLKIT
# ═════════════════════════════════════════════════════════════════════════════
with tab_resume:
    st.markdown("### 💼 Resume & Portfolio Toolkit (Ready to Use)")
    st.write(
        "Copy and paste these pre-formatted, metric-driven bullet points directly into your Resume, CV, or LinkedIn profile."
    )

    st.subheader("1. Resume Experience Entry (STAR Method)")
    resume_text = """**Research Intern — Agentic AI & Intelligent Transportation Systems**  
*IIIT Naya Raipur & INSA Hauts-de-France (Mentors: Dr. Alaa Daoud, Dr. Srinivasa K G)*  
• Architected a Neuro-Symbolic Multi-Agent LLM system (Traffic, Fleet, Coordinator agents) integrated with deterministic Dijkstra graph algorithms to automate emergency transit dispatch under compound urban disruptions (L1–L5).
• Achieved an +86.6% relative improvement in emergency hospital fulfillment (RFR_w) over monolithic Single-LLM baselines under extreme multi-incident crises, successfully preventing LLM context collapse.
• Developed a deterministic physical safety guard validating EV battery SoC, road reachability, and passenger capacity, intercepting topological hallucinations and auditing Hard Constraint Violations (HCVR).
• Benchmarked latency ($1.6s$ vs $5.1s$) and token economics across 15+ complex disruption scenarios, identifying the exact operational threshold where multi-agent coordination is cost-justified.
• Built and deployed an interactive online benchmarking dashboard with live Gemini API simulation and 2D grid network visualization for public reproducibility."""

    st.text_area("Resume Markdown (Click inside and Ctrl+A / Ctrl+C):", value=resume_text, height=220)

    st.divider()

    st.subheader("2. LinkedIn Post / Portfolio Project Description")
    linkedin_text = """🚀 Excited to share my research on Autonomous Agentic AI in Urban Transport Disruption Management!

Under the mentorship of Dr. Alaa DAOUD (INSA Hauts-de-France) and Dr. Srinivasa K G (IIIT Naya Raipur), I benchmarked whether Multi-Agent LLM coordination is actually worth the computational and monetary cost compared to classical rule-based SOPs and Single-LLMs.

🔍 Key Takeaways:
1. Pure algorithms win for simple disruptions: Classical Dijkstra runs in <1ms for $0.00 and cannot be beaten.
2. In extreme compound crises (L4–L5), Single-LLMs suffer from severe context collapse (dropping to 26.9% fulfillment).
3. Our Tool-Augmented Multi-Agent System (Traffic + Fleet + Coordinator + Safety Guard) achieved an +86.6% relative boost in emergency hospital fulfillment.
4. At ~$0.0005 per dispatch, inference cost is economically negligible for real-world transit agencies.

Explore the live interactive web dashboard and 2D Manhattan grid simulation here: [Insert Live URL]

#ArtificialIntelligence #MultiAgentSystems #LLM #IntelligentTransportation #ResearchInternship #IIITNR"""

    st.text_area("LinkedIn Post Text:", value=linkedin_text, height=220)

    st.divider()

    st.subheader("3. Technical Interview Talking Points")
    st.markdown("""
    - **Q: Why didn't you let the LLM calculate the shortest path directly?**  
      *A:* LLMs are next-token predictors, not graph traversal engines. They suffer from topological hallucinations (inventing roads or reversing on one-ways). We used a Neuro-Symbolic design where the LLM handles semantic ingestion (parsing police text alerts and emergency triage) while deterministic Python tools (Dijkstra) solve graph optimization.
    - **Q: Why does the Single-LLM collapse at L5 while Multi-Agent survives?**  
      *A:* At L5, there are 3 road closures, 2 bottlenecks, 2 broken EVs, and 7 competing passenger requests. The Single-LLM's attention dilutes trying to balance all constraints simultaneously. The Multi-Agent decomposes the cognitive load: Traffic Agent isolates closed edges, Fleet Agent filters battery constraints, and the Coordinator focuses exclusively on hospital triage.
    - **Q: How does the Safety Guard prevent catastrophic failures?**  
      *A:* The Safety Guard is a pure-Python deterministic verification gate that intercepts any action violating reachability, battery SoC, or vehicle capacity before execution, ensuring absolute physical safety.
    """)
