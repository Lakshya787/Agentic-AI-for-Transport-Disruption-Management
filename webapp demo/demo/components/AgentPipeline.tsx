import {
  TrafficCone, Bus, MapPin, Bot, ShieldCheck,
  Wrench, Database, Route, GitMerge, CheckCheck,
  Search, ClipboardList, Battery, BarChart3
} from 'lucide-react';

export default function AgentPipeline() {
  const agents = [
    {
      id: 'traffic', name: 'Traffic Agent', Icon: TrafficCone, color: '#00d4ff', dim: 'rgba(0,212,255,0.1)',
      role: 'Monitors road network state',
      scope: 'Edge weights, closure status, congestion levels',
      tools: ['BFS path query', 'Edge status API', 'Real-time sensor feed'],
      ToolIcons: [Search, Database, Wrench],
    },
    {
      id: 'fleet', name: 'Fleet Agent', Icon: Bus, color: '#f59e0b', dim: 'rgba(245,158,11,0.1)',
      role: 'Tracks vehicle availability & SoC',
      scope: 'Vehicle positions, fuel/charge levels, capacity',
      tools: ['Fleet registry', 'SoC checker', 'Capacity validator'],
      ToolIcons: [Database, Battery, CheckCheck],
    },
    {
      id: 'routing', name: 'Routing Agent', Icon: Route, color: '#10b981', dim: 'rgba(16,185,129,0.1)',
      role: 'Computes feasible routes per request',
      scope: 'Network graph, disruption map, priority queue',
      tools: ['Dijkstra/A* solver', 'Detour calculator', 'Priority ranker'],
      ToolIcons: [MapPin, Route, BarChart3],
    },
    {
      id: 'coordinator', name: 'Coordinator', Icon: GitMerge, color: '#8b5cf6', dim: 'rgba(139,92,246,0.1)',
      role: 'Aggregates sub-agent outputs, resolves conflicts',
      scope: 'Full system state, all agent outputs',
      tools: ['Conflict resolver', 'Decision merger', 'LLM orchestrator'],
      ToolIcons: [GitMerge, CheckCheck, Bot],
    },
    {
      id: 'safety', name: 'Safety Guard', Icon: ShieldCheck, color: '#f43f5e', dim: 'rgba(244,63,94,0.1)',
      role: 'Validates every decision before execution',
      scope: 'DecisionCard schema, constraint rules, BFS graph',
      tools: ['BFS feasibility check', 'Pydantic schema validator', 'SoC constraint check'],
      ToolIcons: [Search, ClipboardList, Battery],
    },
  ];

  const mast = [
    { label: 'Constraint Violations', pct: 45, color: '#f43f5e' },
    { label: 'Routing Failures',      pct: 32, color: '#f59e0b' },
    { label: 'Communication Errors',  pct: 23, color: '#8b5cf6' },
  ];

  const safetySteps = [
    { step: '1', label: 'BFS Feasibility Check',      desc: 'Verifies path exists in current graph without closed edges.',          Icon: Search        },
    { step: '2', label: 'Pydantic Schema Validation',  desc: 'DecisionCard must match typed schema; rejects malformed outputs.',      Icon: ClipboardList  },
    { step: '3', label: 'SoC Constraint Check',        desc: 'Vehicle State-of-Charge must be sufficient for assigned route length.', Icon: Battery        },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>

      {/* Pipeline flow */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 0, overflowX: 'auto', padding: '8px 0' }}>
        {agents.map((agent, i) => {
          const { Icon, ToolIcons } = agent;
          return (
            <div key={agent.id} style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
              <div style={{
                background: agent.dim, border: `1px solid ${agent.color}40`, borderRadius: 16,
                padding: '18px 20px', width: 192, position: 'relative', overflow: 'hidden',
                transition: 'all 0.3s ease',
              }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${agent.color}, transparent)` }} />
                <div style={{ width: 36, height: 36, borderRadius: 10, background: `${agent.color}20`, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 10 }}>
                  <Icon size={18} color={agent.color} strokeWidth={2} />
                </div>
                <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>{agent.name}</div>
                <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.4, marginBottom: 12 }}>{agent.role}</div>
                <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: agent.color, marginBottom: 6 }}>Tools</div>
                {agent.tools.map((t, ti) => {
                  const TIcon = ToolIcons[ti];
                  return (
                    <div key={t} style={{ fontSize: 10, color: '#475569', padding: '2px 0', display: 'flex', alignItems: 'center', gap: 5 }}>
                      <TIcon size={10} color={agent.color} strokeWidth={2} /> {t}
                    </div>
                  );
                })}
              </div>
              {i < agents.length - 1 && (
                <div style={{ display: 'flex', alignItems: 'center', padding: '0 6px', flexShrink: 0 }}>
                  <div style={{ width: 24, height: 1, background: `linear-gradient(90deg, ${agent.color}60, ${agents[i+1].color}60)` }} />
                  <div style={{ width: 0, height: 0, borderTop: '5px solid transparent', borderBottom: '5px solid transparent', borderLeft: `7px solid ${agents[i+1].color}80` }} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Safety Guard detail + DecisionCard */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div style={{ background: 'rgba(244,63,94,0.06)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: 16, padding: '20px 22px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, fontSize: 13, fontWeight: 700, color: '#f43f5e', marginBottom: 14 }}>
            <ShieldCheck size={15} strokeWidth={2} /> Safety Guard — Validation Pipeline
          </div>
          {safetySteps.map(item => {
            const { Icon: SIcon } = item;
            return (
              <div key={item.step} style={{ display: 'flex', gap: 12, marginBottom: 14 }}>
                <div style={{ width: 28, height: 28, borderRadius: '50%', flexShrink: 0, background: 'rgba(244,63,94,0.2)', border: '1px solid rgba(244,63,94,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <SIcon size={13} color="#f43f5e" strokeWidth={2.5} />
                </div>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 600, color: '#f1f5f9', marginBottom: 2 }}>{item.label}</div>
                  <div style={{ fontSize: 11, color: '#64748b', lineHeight: 1.4 }}>{item.desc}</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* DecisionCard JSON */}
        <div style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 16, padding: '20px 22px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:8, fontSize: 13, fontWeight: 700, color: '#94a3b8', marginBottom: 14 }}>
            <ClipboardList size={15} strokeWidth={2} /> DecisionCard JSON Schema
          </div>
          <pre style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace", fontSize: 11, lineHeight: 1.7, color: '#94a3b8', margin: 0, overflowX: 'auto' }}>
<span style={{color:'#475569'}}>{'{'}</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"request_id"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>"R1"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"vehicle_id"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>"V-042"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"route"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#f59e0b'}}>["A0","B0","C0","D0"]</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"priority"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>"high"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"estimated_delay_s"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#8b5cf6'}}>45</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"soc_required"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#8b5cf6'}}>0.38</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"feasibility"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>"pass"</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'  '}<span style={{color:'#00d4ff'}}>"guard_checks"</span><span style={{color:'#475569'}}>:</span> {'{'}{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"bfs"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"schema"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span><span style={{color:'#475569'}}>,</span>{'\n'}
{'    '}<span style={{color:'#00d4ff'}}>"soc"</span><span style={{color:'#475569'}}>:</span> <span style={{color:'#10b981'}}>true</span>{'\n'}
{'  '}{'}'}{'\n'}
<span style={{color:'#475569'}}>{'}'}</span>
          </pre>
        </div>
      </div>

      {/* MAST failure taxonomy */}
      <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: 16, padding: '20px 24px' }}>
        <div style={{ display:'flex', alignItems:'center', gap:8, fontSize: 13, fontWeight: 700, color: '#f1f5f9', marginBottom: 16 }}>
          <BarChart3 size={15} strokeWidth={2} color="#94a3b8" /> MAST Failure Taxonomy — B1 Breakdown
        </div>
        {mast.map(m => (
          <div key={m.label} style={{ marginBottom: 14 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
              <span style={{ fontSize: 12, color: '#94a3b8' }}>{m.label}</span>
              <span style={{ fontSize: 12, fontWeight: 700, color: m.color }}>{m.pct}%</span>
            </div>
            <div style={{ height: 6, background: 'rgba(255,255,255,0.06)', borderRadius: 999, overflow: 'hidden' }}>
              <div style={{ height: '100%', width: `${m.pct}%`, background: `linear-gradient(90deg, ${m.color}80, ${m.color})`, borderRadius: 999 }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
