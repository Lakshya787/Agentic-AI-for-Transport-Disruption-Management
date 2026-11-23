import { Microscope, Route, Battery, Siren, Shield, TrendingUp, CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-react';
import { SCENARIOS, B1_RESULTS, B2_PROJECTED, B3_PROJECTED, VIOLATION_BREAKDOWN } from '@/lib/data';

// ── Static explainability data derived from explainability.py logic ───────────
// Source: build_decision_explanation() in explainability.py

const DIMENSION_META = [
  {
    num: 1,
    icon: Route,
    color: '#00d4ff',
    dim: 'rgba(0,212,255,0.08)',
    title: 'Incident & Closure Rationale',
    subtitle: 'Naive path vs. disrupted graph. Which segments are blocked and why.',
    pyRef: 'dimensions["incident_reasoning"]',
  },
  {
    num: 2,
    icon: Battery,
    color: '#10b981',
    dim: 'rgba(16,185,129,0.08)',
    title: 'Energy & Range Feasibility Proof',
    subtitle: 'Battery consumption calculation with 15% safety buffer margin.',
    pyRef: 'dimensions["energy_proof"]',
  },
  {
    num: 3,
    icon: Siren,
    color: '#f59e0b',
    dim: 'rgba(245,158,11,0.08)',
    title: 'Priority Triage & Arbitration',
    subtitle: 'Emergency vs standard priority weighting. Vehicle allocation justification.',
    pyRef: 'dimensions["triage_arbitration"]',
  },
  {
    num: 4,
    icon: TrendingUp,
    color: '#8b5cf6',
    dim: 'rgba(139,92,246,0.08)',
    title: 'Detour Efficiency vs Naive Route',
    subtitle: 'Comparison of detour path time vs free-flow shortest path time.',
    pyRef: 'dimensions["detour_efficiency"]',
  },
  {
    num: 5,
    icon: Shield,
    color: '#f43f5e',
    dim: 'rgba(244,63,94,0.08)',
    title: 'Deterministic Safety Guard Audit',
    subtitle: 'Formal invariant certificate: topology, SoC, capacity, concurrency.',
    pyRef: 'dimensions["safety_audit_certificate"]',
  },
];

// Representative worked example from L3 scenario, R1 request (B3 decision)
const WORKED_EXAMPLE = {
  requestId: 'R1',
  vehicleId: 'V007',
  origin: 'A0',
  destination: 'D3',
  passengers: 2,
  priority: 'standard',
  selectedRoute: ['A0','A1','B1','C1','C2','C3','D3'],
  estimatedTimeMin: 13.0,
  scenarioId: 'L3',
  dimensions: {
    incident_reasoning: {
      naive_path: ['A0','A1','A2','B2','C2','C3','D3'],
      naive_time_min: 11.4,
      is_naive_path_blocked: true,
      blocked_segments: [['A2','B2'], ['B2','C2']],
      text_advisory: '"City alert: Utility works on North Avenue between A1 and B1. Eastbound lanes restricted until 18:00."',
    },
    energy_proof: {
      initial_soc: 68,
      needed_soc: 15.9,  // 13.0 min × 1.0% × 1.15 buffer
      projected_post_trip_soc: 52.1,
      verdict: 'VERIFIED_FEASIBLE',
    },
    triage_arbitration: {
      priority_tier: 'STANDARD_COMMUTE (Weight = 1.0)',
      justification: 'V007 (SoC: 68%) allocated to standard passenger R1 after fulfilling emergency reservations.',
    },
    detour_efficiency: {
      chosen_time: 13.0,
      naive_time: 11.4,
      overhead: 1.6,
      overhead_pct: '14.0%',
    },
    safety_audit: {
      status: 'PASSED_UNCONDITIONAL',
      topo: 'All 6 route edges confirmed open in disrupted graph',
      capacity: 'Vehicle capacity 4 ≥ Passengers 2',
      concurrency: 'V007 uniquely assigned — zero conflict',
    },
  },
};

// Per-controller audit summary table
const CONTROLLER_AUDIT = [
  {
    id: 'B1', label: 'B1 — Rule-Based', color: '#00d4ff',
    dim1: 'Blocked naive path detected via graph diff only. No text alert parsing.',
    dim2: 'SoC check skipped — vehicles assumed always available.',
    dim3: 'No priority differentiation — FIFO dispatch only.',
    dim4: 'Detour found by Dijkstra on structured edges only.',
    dim5: '6 topological violations pre-guard. All 0 post-guard (SOP fallback triggered).',
  },
  {
    id: 'B2', label: 'B2 — Single-LLM', color: '#f59e0b',
    dim1: 'LLM infers disruptions from full context in one pass. High hallucination risk on complex L4–L5.',
    dim2: 'SoC verified by tool_check_battery() after LLM route proposal.',
    dim3: 'Emergency priority recognized but inconsistently applied under token pressure.',
    dim4: 'Detour paths generally valid; 33 topological violations show LLM sometimes proposes closed roads.',
    dim5: '35 pre-guard violations (topo:33, soc:2). All 0 post-guard.',
  },
  {
    id: 'B3', label: 'B3 — Multi-Agent', color: '#8b5cf6',
    dim1: 'Traffic Agent (LLM 1) specializes in parsing closures + text alerts. Lowest topo violations (4).',
    dim2: 'Fleet Agent (LLM 2) performs explicit battery triage; 15 SoC violations still intercepted by guard.',
    dim3: 'Coordinator (LLM 3) balances priority against available capacity after Fleet Agent proposes.',
    dim4: 'Routing Tool (Dijkstra) guarantees shortest feasible detour — no LLM hallucination on paths.',
    dim5: '19 pre-guard violations. All 0 post-guard. Coordinator architecture reduces overall conflict.',
  },
];

export default function ExplainabilityPage() {
  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 24px', display: 'flex', flexDirection: 'column', gap: 48 }}>

      {/* Header */}
      <div>
        <div className="section-label">Decision Audit</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', marginBottom: 8 }}>Explainability & Causality</h1>
        <p style={{ color: '#64748b', fontSize: 14, maxWidth: 720, lineHeight: 1.6 }}>
          Every dispatch decision is decomposed into 5 human-auditable dimensions based on{' '}
          <code style={{ color: '#00d4ff', fontSize: 12 }}>explainability.py:build_decision_explanation()</code>.
          Each dimension is independently verifiable and grounded in the disrupted graph state.
        </p>
      </div>

      {/* 5-Dimension Overview */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Microscope size={18} color="#00d4ff" strokeWidth={2} />
          The 5 Explainability Dimensions
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: 16 }}>
          {DIMENSION_META.map(({ num, icon: Icon, color, dim, title, subtitle, pyRef }) => (
            <div key={num} className="glass" style={{ padding: '20px 22px', borderLeft: `3px solid ${color}`, position: 'relative', overflow: 'hidden' }}>
              <div style={{ position: 'absolute', bottom: -20, right: -20, width: 70, height: 70, borderRadius: '50%', background: `${color}18`, filter: 'blur(16px)', pointerEvents: 'none' }} />
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: dim, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                  <Icon size={17} color={color} strokeWidth={2} />
                </div>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color }}>Dimension {num}</span>
                  <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9', lineHeight: 1.3 }}>{title}</div>
                </div>
              </div>
              <p style={{ fontSize: 12, color: '#64748b', lineHeight: 1.6, marginBottom: 8 }}>{subtitle}</p>
              <code style={{ fontSize: 10, color: '#334155', background: 'rgba(255,255,255,0.03)', padding: '3px 8px', borderRadius: 4 }}>{pyRef}</code>
            </div>
          ))}
        </div>
      </section>

      {/* Worked Example */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Info size={18} color="#8b5cf6" strokeWidth={2} />
          Worked Example — Scenario L3, Request R1
        </h2>
        <p style={{ fontSize: 13, color: '#475569', marginBottom: 20 }}>
          R1: A0 → D3, 2 passengers. Vehicle V007 assigned. Naive path blocked at B2↔C2 closure.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>

          {/* Dim 1: Incident */}
          <div className="glass-static" style={{ padding: '18px 22px', borderLeft: '3px solid #00d4ff' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#00d4ff', marginBottom: 8 }}>
              1 · Incident & Closure Rationale
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, fontSize: 12, color: '#94a3b8' }}>
              <div>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 4 }}>NAIVE SHORTEST PATH (G_original)</div>
                <code style={{ color: '#f43f5e' }}>A0 → A1 → A2 → B2 → C2 → C3 → D3</code>
                <div style={{ marginTop: 4, color: '#f43f5e', fontSize: 11 }}>⚠ Blocked at: (A2↔B2), (B2↔C2)</div>
              </div>
              <div>
                <div style={{ fontSize: 10, color: '#475569', marginBottom: 4 }}>SELECTED ROUTE (G_disrupted)</div>
                <code style={{ color: '#10b981' }}>A0 → A1 → B1 → C1 → C2 → C3 → D3</code>
                <div style={{ marginTop: 4, color: '#10b981', fontSize: 11 }}>✓ All edges open in disrupted graph</div>
              </div>
            </div>
            {WORKED_EXAMPLE.dimensions.incident_reasoning.text_advisory && (
              <div style={{ marginTop: 10, padding: '8px 12px', borderRadius: 8, background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)', fontSize: 11, color: '#f59e0b', fontStyle: 'italic' }}>
                📡 Text Advisory: {WORKED_EXAMPLE.dimensions.incident_reasoning.text_advisory}
              </div>
            )}
          </div>

          {/* Dim 2: Energy */}
          <div className="glass-static" style={{ padding: '18px 22px', borderLeft: '3px solid #10b981' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10b981', marginBottom: 12 }}>
              2 · Energy & Range Feasibility Proof
            </div>
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
              {[
                { label: 'Initial SoC', value: `${WORKED_EXAMPLE.dimensions.energy_proof.initial_soc}%`, color: '#10b981' },
                { label: 'Needed (13.0m × 1.0% × 1.15)', value: `${WORKED_EXAMPLE.dimensions.energy_proof.needed_soc}%`, color: '#f59e0b' },
                { label: 'Post-trip Reserve', value: `${WORKED_EXAMPLE.dimensions.energy_proof.projected_post_trip_soc}%`, color: '#00d4ff' },
              ].map(({ label, value, color }) => (
                <div key={label}>
                  <div style={{ fontSize: 10, color: '#475569', marginBottom: 2 }}>{label}</div>
                  <div style={{ fontSize: 20, fontWeight: 800, color }}>{value}</div>
                </div>
              ))}
              <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 8, padding: '8px 16px', borderRadius: 999, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)' }}>
                <CheckCircle2 size={14} color="#10b981" strokeWidth={2.5} />
                <span style={{ fontSize: 12, fontWeight: 700, color: '#10b981' }}>VERIFIED_FEASIBLE</span>
              </div>
            </div>
          </div>

          {/* Dim 3: Triage */}
          <div className="glass-static" style={{ padding: '18px 22px', borderLeft: '3px solid #f59e0b' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#f59e0b', marginBottom: 8 }}>
              3 · Priority Triage & Arbitration
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
              <span style={{ padding: '4px 12px', borderRadius: 999, background: 'rgba(100,116,139,0.15)', fontSize: 11, fontWeight: 700, color: '#64748b' }}>
                STANDARD_COMMUTE (Weight = 1.0)
              </span>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>
                {WORKED_EXAMPLE.dimensions.triage_arbitration.justification}
              </span>
            </div>
          </div>

          {/* Dim 4: Detour */}
          <div className="glass-static" style={{ padding: '18px 22px', borderLeft: '3px solid #8b5cf6' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#8b5cf6', marginBottom: 12 }}>
              4 · Detour Efficiency vs Naive Route
            </div>
            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 10, color: '#475569' }}>Free-flow (naive)</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#94a3b8' }}>{WORKED_EXAMPLE.dimensions.detour_efficiency.naive_time} min</div>
              </div>
              <div style={{ fontSize: 20, color: '#334155' }}>→</div>
              <div>
                <div style={{ fontSize: 10, color: '#475569' }}>Chosen detour</div>
                <div style={{ fontSize: 20, fontWeight: 800, color: '#8b5cf6' }}>{WORKED_EXAMPLE.dimensions.detour_efficiency.chosen_time} min</div>
              </div>
              <div style={{ padding: '4px 12px', borderRadius: 999, background: 'rgba(139,92,246,0.1)', border: '1px solid rgba(139,92,246,0.25)', fontSize: 12, fontWeight: 700, color: '#8b5cf6' }}>
                +{WORKED_EXAMPLE.dimensions.detour_efficiency.overhead} min overhead ({WORKED_EXAMPLE.dimensions.detour_efficiency.overhead_pct})
              </div>
            </div>
          </div>

          {/* Dim 5: Safety Audit */}
          <div className="glass-static" style={{ padding: '18px 22px', borderLeft: '3px solid #f43f5e' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#f43f5e', marginBottom: 12 }}>
              5 · Deterministic Safety Guard Audit Certificate
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12, padding: '8px 14px', borderRadius: 10, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)', width: 'fit-content' }}>
              <Shield size={15} color="#10b981" strokeWidth={2.5} />
              <span style={{ fontSize: 13, fontWeight: 700, color: '#10b981' }}>PASSED_UNCONDITIONAL</span>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {[
                ['Topological', WORKED_EXAMPLE.dimensions.safety_audit.topo],
                ['SoC Feasibility', 'SoC 68% ≥ 15.9% required (route_min × 1.0% × 1.15)'],
                ['Capacity', WORKED_EXAMPLE.dimensions.safety_audit.capacity],
                ['Concurrency', WORKED_EXAMPLE.dimensions.safety_audit.concurrency],
              ].map(([label, detail]) => (
                <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12 }}>
                  <CheckCircle2 size={13} color="#10b981" strokeWidth={2.5} style={{ flexShrink: 0 }} />
                  <span style={{ color: '#475569', fontWeight: 600, minWidth: 100 }}>{label}:</span>
                  <span style={{ color: '#94a3b8' }}>{detail}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Per-controller audit summary */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20 }}>
          Controller Explainability Audit — B1 vs B2 vs B3
        </h2>
        <div className="glass-static" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Dimension</th>
                <th style={{ color: '#00d4ff' }}>B1 Rule-Based</th>
                <th style={{ color: '#f59e0b' }}>B2 Single-LLM</th>
                <th style={{ color: '#8b5cf6' }}>B3 Multi-Agent</th>
              </tr>
            </thead>
            <tbody>
              {(['dim1','dim2','dim3','dim4','dim5'] as const).map((dk, i) => (
                <tr key={dk}>
                  <td style={{ fontWeight: 600, color: '#64748b', fontSize: 11, whiteSpace: 'nowrap' }}>
                    {DIMENSION_META[i].title.split('&')[0].trim()}
                  </td>
                  {CONTROLLER_AUDIT.map(c => (
                    <td key={c.id} style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.5 }}>{c[dk]}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Violation breakdown */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20 }}>
          Pre-Guard vs Post-Guard Violations
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
          {VIOLATION_BREAKDOWN.map(c => {
            const total = c.topo + c.soc + c.cap + c.dup;
            return (
              <div key={c.controller} className="glass" style={{ padding: '20px 22px', borderTop: `2px solid ${c.color}` }}>
                <div style={{ fontSize: 13, fontWeight: 700, color: c.color, marginBottom: 16 }}>{c.controller}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 16 }}>
                  {[
                    { label: 'Topological', val: c.topo, color: '#f43f5e' },
                    { label: 'SoC Deficit',  val: c.soc,  color: '#f59e0b' },
                    { label: 'Capacity',     val: c.cap,  color: '#8b5cf6' },
                    { label: 'Concurrency',  val: c.dup,  color: '#00d4ff' },
                  ].map(({ label, val, color: vc }) => (
                    <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                      <span style={{ color: '#64748b' }}>{label}</span>
                      <span style={{ fontWeight: 700, color: val > 0 ? vc : '#334155' }}>{val}</span>
                    </div>
                  ))}
                  <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: 8, display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                    <span style={{ color: '#94a3b8', fontWeight: 700 }}>Total pre-guard</span>
                    <span style={{ fontWeight: 800, color: total > 0 ? '#f59e0b' : '#10b981' }}>{total}</span>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 12px', borderRadius: 8, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}>
                  <Shield size={13} color="#10b981" strokeWidth={2.5} />
                  <span style={{ fontSize: 11, fontWeight: 700, color: '#10b981' }}>Post-guard: {c.postGuard} violations</span>
                </div>
              </div>
            );
          })}
        </div>
      </section>

    </div>
  );
}
