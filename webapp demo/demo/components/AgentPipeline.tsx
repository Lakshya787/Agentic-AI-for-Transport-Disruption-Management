import {
  TrafficCone, Bus, Route, GitMerge, ShieldCheck,
  Search, Database, Battery, CheckCheck, Wrench,
  Bot, ClipboardList, BarChart3, Zap, AlertTriangle,
} from 'lucide-react';

export default function AgentPipeline() {
  // ── Real B3 pipeline from controllers.py ─────────────────────────────────
  // 3 LLM calls: Traffic → Fleet → Coordinator (+ 1 deterministic Routing Tool)
  const pipeline = [
    {
      id: 'traffic',
      name: 'Traffic Agent',
      badge: 'LLM Call 1',
      badgeColor: '#00d4ff',
      Icon: TrafficCone,
      color: '#00d4ff',
      dim: 'rgba(0,212,255,0.08)',
      input: 'textAlerts[] (NLP police/traffic radio)',
      output: 'closed_edges[]',
      prompt: '_TRAFFIC_PROMPT',
      tools: ['Reads all unstructured text alerts', 'Extracts impassable road segments', 'No tool access — pure NLP reasoning'],
      ToolIcons: [Search, AlertTriangle, Bot],
    },
    {
      id: 'fleet',
      name: 'Fleet Agent',
      badge: 'LLM Call 2',
      badgeColor: '#f59e0b',
      Icon: Bus,
      color: '#f59e0b',
      dim: 'rgba(245,158,11,0.08)',
      input: 'vehicles[] + requests[] (fleet & demands)',
      output: 'emergency_reservations[], standard_allocations[]',
      prompt: '_FLEET_PROMPT',
      tools: ['Audits V0–V5 battery & capacity', 'Reserves high-SoC for EMERGENCY requests', 'Prioritises hospital/medical trips (3× weight)'],
      ToolIcons: [Database, Battery, CheckCheck],
    },
    {
      id: 'routing',
      name: 'Routing Tool',
      badge: 'Deterministic',
      badgeColor: '#10b981',
      Icon: Route,
      color: '#10b981',
      dim: 'rgba(16,185,129,0.08)',
      input: 'G_verified (open graph after Traffic output)',
      output: 'k=2 candidate routes per request',
      prompt: 'tool_get_k_diverse_routes()',
      tools: ['Dijkstra shortest paths on verified graph', 'K-diverse loop-free alternatives', 'Exact travel time per edge sum'],
      ToolIcons: [Search, Route, BarChart3],
    },
    {
      id: 'coordinator',
      name: 'Coordinator',
      badge: 'LLM Call 3',
      badgeColor: '#8b5cf6',
      Icon: GitMerge,
      color: '#8b5cf6',
      dim: 'rgba(139,92,246,0.08)',
      input: 'traffic_report + fleet_report + candidate_routes',
      output: 'assignments[] {request_id, vehicle_id, selected_route}',
      prompt: '_COORDINATOR_PROMPT',
      tools: ['Synthesises all 3 agent outputs', 'Resolves vehicle conflicts (no duplicate assignment)', 'Selects best verified route per request'],
      ToolIcons: [GitMerge, CheckCheck, Bot],
    },
    {
      id: 'safety',
      name: 'Safety Guard',
      badge: 'Deterministic',
      badgeColor: '#f43f5e',
      Icon: ShieldCheck,
      color: '#f43f5e',
      dim: 'rgba(244,63,94,0.08)',
      input: 'assignments[] from Coordinator',
      output: 'validated_assignments[] + SOP fallback if needed',
      prompt: 'validate_decision() + apply_sop_fallback()',
      tools: ['Topological reachability (BFS edge check)', 'SoC sufficiency: soc ≥ time×1.0×1.15', 'Capacity: seats ≥ passengers', 'Concurrency: no vehicle double-assigned'],
      ToolIcons: [Search, Battery, CheckCheck, Wrench],
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* ── Pipeline flow ─────────────────────────────────────────────────── */}
      <div style={{ overflowX: 'auto', paddingBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 0, minWidth: 'max-content' }}>
          {pipeline.map((agent, i) => {
            const { Icon, ToolIcons } = agent;
            return (
              <div key={agent.id} style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
                <div style={{
                  background: agent.dim, border: `1px solid ${agent.color}30`, borderRadius: 16,
                  padding: '16px 18px', width: 200, position: 'relative', overflow: 'hidden',
                }}>
                  {/* Top accent */}
                  <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${agent.color}, transparent)` }} />

                  {/* Badge */}
                  <div style={{ marginBottom: 10, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 9, background: `${agent.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Icon size={16} color={agent.color} strokeWidth={2} />
                    </div>
                    <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', background: `${agent.color}20`, color: agent.color, padding: '2px 7px', borderRadius: 999 }}>
                      {agent.badge}
                    </span>
                  </div>

                  <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9', marginBottom: 8 }}>{agent.name}</div>

                  {/* IO */}
                  <div style={{ fontSize: 9, color: '#475569', marginBottom: 4 }}>
                    <span style={{ color: '#334155', fontWeight: 600 }}>IN: </span>{agent.input}
                  </div>
                  <div style={{ fontSize: 9, color: '#475569', marginBottom: 10 }}>
                    <span style={{ color: agent.color, fontWeight: 600 }}>OUT: </span>{agent.output}
                  </div>

                  {/* Tools */}
                  <div style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: agent.color, marginBottom: 6 }}>Actions</div>
                  {agent.tools.map((t, ti) => {
                    const TIcon = ToolIcons[ti] ?? Zap;
                    return (
                      <div key={t} style={{ fontSize: 9, color: '#475569', padding: '2px 0', display: 'flex', alignItems: 'flex-start', gap: 5, lineHeight: 1.4 }}>
                        <TIcon size={9} color={agent.color} strokeWidth={2} style={{ flexShrink: 0, marginTop: 1 }} /> {t}
                      </div>
                    );
                  })}
                </div>

                {i < pipeline.length - 1 && (
                  <div style={{ display: 'flex', alignItems: 'center', padding: '0 4px', flexShrink: 0 }}>
                    <div style={{ width: 20, height: 1, background: `linear-gradient(90deg, ${agent.color}50, ${pipeline[i+1].color}50)` }} />
                    <div style={{ width: 0, height: 0, borderTop: '5px solid transparent', borderBottom: '5px solid transparent', borderLeft: `7px solid ${pipeline[i+1].color}70` }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Safety Guard — 4 Invariant Checks ───────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div style={{ background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: 16, padding: '20px 22px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, fontSize: 13, fontWeight: 700, color: '#f43f5e', marginBottom: 16 }}>
            <ShieldCheck size={15} strokeWidth={2} /> Safety Guard — 4 Deterministic Invariants
          </div>
          {[
            { n:'1', label:'Topological Reachability', formula:'∀(u,v) ∈ route: G_disrupted.has_edge(u,v)', Icon: Search },
            { n:'2', label:'SoC Sufficiency (×1.15 buffer)', formula:'vehicle.soc ≥ route_minutes × 1.0 × 1.15', Icon: Battery },
            { n:'3', label:'Passenger Capacity', formula:'vehicle.capacity ≥ request.passengers', Icon: CheckCheck },
            { n:'4', label:'No Duplicate Assignment', formula:'vehicle_id ∉ already_assigned_set', Icon: Wrench },
          ].map(item => {
            const { Icon: SIcon } = item;
            return (
              <div key={item.n} style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
                <div style={{ width: 26, height: 26, borderRadius: '50%', flexShrink: 0, background: 'rgba(244,63,94,0.15)', border: '1px solid rgba(244,63,94,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <SIcon size={12} color="#f43f5e" strokeWidth={2.5} />
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: '#f1f5f9', marginBottom: 2 }}>{item.label}</div>
                  <code style={{ fontSize: 10, color: '#64748b', lineHeight: 1.4 }}>{item.formula}</code>
                </div>
              </div>
            );
          })}

          {/* Result */}
          <div style={{ marginTop: 8, padding: '8px 12px', borderRadius: 8, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#10b981' }}>✅ Result: 0 post-guard violations across all 50 assignments (all 5 tiers)</div>
          </div>
        </div>

        {/* DecisionCard JSON — updated with real N0–N15 format */}
        <div style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 16, padding: '20px 22px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, fontSize: 13, fontWeight: 700, color: '#94a3b8', marginBottom: 14 }}>
            <ClipboardList size={15} strokeWidth={2} /> Coordinator Output → Safety Guard Input
          </div>
          <pre style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: 10, lineHeight: 1.75, color: '#94a3b8', margin: 0, overflowX: 'auto' }}>
<span style={{color:'#475569'}}>{'{'}</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"request_id"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>"R0"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"vehicle_id"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>"V3"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"selected_route"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#f59e0b'}}>["N0","N4","N8","N9","N13","N14","N15"]</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"priority"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#f43f5e'}}>"emergency"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"estimated_time"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#8b5cf6'}}>38.5</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"guard_result"</span><span style={{color:'#475569'}}>:</span> {'{'}{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"topological"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"soc_check"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"capacity"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"concurrency"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span>{'\n'}
{'  '}{'}'}{'\n'}
<span style={{color:'#475569'}}>{'}'}</span>
          </pre>
        </div>
      </div>

      {/* ── Real Benchmark: Violation Breakdown ──────────────────────────────── */}
      <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 16, padding: '20px 24px' }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, fontSize: 13, fontWeight: 700, color: '#f1f5f9', marginBottom: 16 }}>
          <BarChart3 size={15} strokeWidth={2} color="#94a3b8" /> Pre-Guard Violations Intercepted (all 50 assignments)
        </div>
        {[
          { controller: 'B1 Rule-Based', color: '#00d4ff', topo: 6, soc: 0, cap: 0, dup: 0, postGuard: 0 },
          { controller: 'B2 Single-LLM', color: '#f59e0b', topo: 33, soc: 2, cap: 0, dup: 0, postGuard: 0 },
          { controller: 'B3 Multi-Agent', color: '#8b5cf6', topo: 4, soc: 15, cap: 0, dup: 0, postGuard: 0 },
        ].map(row => (
          <div key={row.controller} style={{ display: 'grid', gridTemplateColumns: '160px 1fr 1fr 1fr 1fr 120px', gap: 8, alignItems: 'center', marginBottom: 12 }}>
            <div style={{ fontSize: 12, color: row.color, fontWeight: 600 }}>{row.controller}</div>
            {[
              { label: 'Topological', val: row.topo },
              { label: 'SoC Deficit', val: row.soc },
              { label: 'Capacity', val: row.cap },
              { label: 'Duplicate', val: row.dup },
            ].map(({ label, val }) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 9, color: '#475569', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{label}</div>
                <span style={{
                  display: 'inline-block', fontSize: 13, fontWeight: 700, padding: '2px 10px',
                  borderRadius: 6, background: val > 0 ? `${row.color}20` : 'rgba(16,185,129,0.1)',
                  color: val > 0 ? row.color : '#10b981',
                }}>{val}</span>
              </div>
            ))}
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 9, color: '#475569', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Post-Guard</div>
              <span style={{ display: 'inline-block', fontSize: 13, fontWeight: 700, padding: '2px 10px', borderRadius: 6, background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>
                0 ✅
              </span>
            </div>
          </div>
        ))}
        <div style={{ fontSize: 11, color: '#334155', marginTop: 8, lineHeight: 1.5 }}>
          Source: <code style={{ color: '#475569', fontSize: 10 }}>results/RESULTS.md</code> · Safety Guard guarantees 0% post-guard violations across all tiers
        </div>
      </div>
    </div>
  );
}
