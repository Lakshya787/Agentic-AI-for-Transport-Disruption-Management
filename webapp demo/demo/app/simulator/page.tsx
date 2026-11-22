'use client';
import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Play, Square, AlertTriangle, Zap, AlertCircle, Navigation, Users, Clock, Radio } from 'lucide-react';
import { SCENARIOS, Disruption } from '@/lib/data';
import FleetPanel from '@/components/FleetPanel';

const NetworkCanvas = dynamic(() => import('@/components/NetworkCanvas'), { ssr: false });

const DISRUPTION_META: Record<string, { color: string; Icon: React.ComponentType<{size?:number;strokeWidth?:number;color?:string;style?:React.CSSProperties}> }> = {
  road_closure:      { color: '#f43f5e', Icon: AlertTriangle },
  congestion:        { color: '#f59e0b', Icon: AlertCircle   },
  vehicle_breakdown: { color: '#f59e0b', Icon: Zap           },
  demand_surge:      { color: '#00d4ff', Icon: Navigation    },
};

const PRIORITY_COLOR: Record<number, { color: string; label: string }> = {
  1: { color: '#f43f5e', label: 'P1 — High'   },
  2: { color: '#f59e0b', label: 'P2 — Medium' },
  3: { color: '#10b981', label: 'P3 — Low'    },
};

function DisruptionDetail({ d }: { d: Disruption }) {
  const meta = DISRUPTION_META[d.type] ?? DISRUPTION_META.road_closure;
  const { Icon } = meta;
  const extras: string[] = [];
  if (d.edge)              extras.push(`Edge: ${d.edge[0]}↔${d.edge[1]}`);
  if (d.vehicleId)         extras.push(`Vehicle: ${d.vehicleId}`);
  if (d.congestionFactor)  extras.push(`Factor: ×${d.congestionFactor}`);
  if (d.surgeMultiplier)   extras.push(`Multiplier: ×${d.surgeMultiplier}`);
  if (d.surgeNodes?.length) extras.push(`Nodes: ${d.surgeNodes.join(', ')}`);

  return (
    <div style={{
      display: 'flex', gap: 10, padding: '8px 12px', borderRadius: 10,
      background: `${meta.color}0d`, border: `1px solid ${meta.color}30`,
    }}>
      <Icon size={14} color={meta.color} strokeWidth={2} style={{ flexShrink: 0, marginTop: 2 }} />
      <div>
        <div style={{ fontSize: 12, color: meta.color, fontWeight: 600, marginBottom: 2 }}>{d.label}</div>
        {extras.length > 0 && (
          <div style={{ fontSize: 10, color: '#475569' }}>{extras.join(' · ')}</div>
        )}
      </div>
    </div>
  );
}

export default function SimulatorPage() {
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const scenario = SCENARIOS[scenarioIdx];

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 24px' }}>
      <div style={{ marginBottom: 32 }}>
        <div className="section-label">Network Simulator</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', marginBottom: 8 }}>Interactive Road Network</h1>
        <p style={{ color: '#64748b', fontSize: 14 }}>Select a disruption scenario and watch the 4×4 road network respond. Data sourced directly from <code style={{ color: '#00d4ff', fontSize: 12 }}>sim/scenarios/</code>.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '460px 1fr', gap: 24, alignItems: 'start' }}>

        {/* ── Canvas Panel ─────────────────────────────────────────────── */}
        <div className="glass-static" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '12px 18px', borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: 12, fontWeight: 600, color: '#64748b' }}>4×4 Grid Network · {scenario.numVehicles} vehicles</span>
            <button id="play-btn" onClick={() => setPlaying(p => !p)} style={{
              padding: '6px 16px', borderRadius: 8, border: 'none', cursor: 'pointer',
              background: playing ? 'rgba(244,63,94,0.2)' : 'linear-gradient(135deg, #00d4ff, #0077ff)',
              color: playing ? '#f43f5e' : '#020817',
              fontWeight: 700, fontSize: 12, fontFamily: 'Inter,sans-serif',
              boxShadow: playing ? 'none' : '0 0 14px rgba(0,212,255,0.3)',
              transition: 'all 0.2s ease', display: 'flex', alignItems: 'center', gap: 6,
            }}>
              {playing ? <><Square size={12} strokeWidth={2.5} /> Stop</> : <><Play size={12} strokeWidth={2.5} /> Animate Requests</>}
            </button>
          </div>

          <div style={{ background: 'rgba(0,0,0,0.35)', padding: 10 }}>
            <NetworkCanvas scenario={scenario} playing={playing} />
          </div>

          {/* Legend */}
          <div style={{ padding: '10px 16px', borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', flexWrap: 'wrap', gap: 14 }}>
            {Object.entries(DISRUPTION_META).map(([type, { color, Icon }]) => (
              <div key={type} style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, color: '#475569' }}>
                <Icon size={11} color={color} strokeWidth={2} />
                {type.replace(/_/g,' ')}
              </div>
            ))}
            <div style={{ display: 'flex', alignItems: 'center', gap: 5, fontSize: 10, color: '#475569' }}>
              <div style={{ width: 16, height: 1, background: '#f43f5e', opacity: 0.5 }} /> P1 request
            </div>
          </div>
        </div>

        {/* ── Control Panel ────────────────────────────────────────────── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Scenario selector */}
          <div className="glass-static" style={{ padding: '18px 20px' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: '#475569', marginBottom: 10 }}>Scenario</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {SCENARIOS.map((s, i) => (
                <button key={s.id} id={`scenario-${s.id.toLowerCase()}`}
                  onClick={() => { setScenarioIdx(i); setPlaying(false); }}
                  style={{
                    padding: '10px 14px', borderRadius: 10, border: 'none', cursor: 'pointer', textAlign: 'left',
                    background: scenarioIdx === i ? 'rgba(0,212,255,0.1)' : 'rgba(255,255,255,0.03)',
                    borderLeft: `3px solid ${scenarioIdx === i ? '#00d4ff' : 'transparent'}`,
                    transition: 'all 0.2s ease', fontFamily: 'Inter,sans-serif',
                  }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: scenarioIdx === i ? '#00d4ff' : '#94a3b8', marginBottom: 2 }}>{s.name}</div>
                  <div style={{ fontSize: 11, color: '#475569' }}>
                    {s.disruptions.length} disruption{s.disruptions.length !== 1 ? 's' : ''} · {s.requests.length} requests · {s.numVehicles} vehicles
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Active scenario info */}
          <div className="glass-static" style={{ padding: '18px 20px' }}>
            <div style={{ fontSize: 11, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#475569', marginBottom: 6 }}>Active Scenario</div>
            <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>{scenario.name}</h3>
            <p style={{ fontSize: 12, color: '#64748b', lineHeight: 1.6, marginBottom: 14 }}>{scenario.description}</p>

            {/* Disruptions */}
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#475569', marginBottom: 8 }}>
              Disruptions ({scenario.disruptions.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, marginBottom: 16 }}>
              {scenario.disruptions.map(d => <DisruptionDetail key={d.id} d={d} />)}
            </div>

            {/* NLP Text Alerts / B1 Limitation */}
            {scenario.textAlerts && scenario.textAlerts.length > 0 && (
              <div style={{ marginBottom: 16, display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#f59e0b' }}>
                  Unstructured Text Alerts (NLP Required)
                </div>
                {scenario.textAlerts.map((alert, i) => (
                  <div key={i} style={{
                    padding: '8px 12px', borderRadius: 8,
                    background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.25)',
                    display: 'flex', gap: 8, alignItems: 'center', fontSize: 11, color: '#f59e0b', fontStyle: 'italic',
                  }}>
                    <Radio size={14} color="#f59e0b" style={{ flexShrink: 0 }} />
                    <span>{alert}</span>
                  </div>
                ))}
                <div style={{
                  padding: '8px 12px', borderRadius: 8,
                  background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.2)',
                  display: 'flex', gap: 8, alignItems: 'flex-start',
                }}>
                  <AlertTriangle size={13} color="#f43f5e" strokeWidth={2} style={{ flexShrink: 0, marginTop: 1 }} />
                  <div style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.4 }}>
                    <span style={{ color: '#f43f5e', fontWeight: 700 }}>B1 Blind Spot: </span>
                    Rule-based SOP cannot parse unstructured text broadcasts and routes directly through closed links, triggering constraint violations.
                  </div>
                </div>
              </div>
            )}

            {/* Electric Fleet Panel */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#475569', marginBottom: 8 }}>
                Electric Vehicle Fleet &amp; SoC
              </div>
              <FleetPanel scenario={scenario} />
            </div>

            {/* Requests */}
            <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#475569', marginBottom: 8 }}>
              Transport Requests ({scenario.requests.length})
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
              {scenario.requests.map(r => {
                const pMeta = PRIORITY_COLOR[r.priority] ?? PRIORITY_COLOR[3];
                return (
                  <div key={r.id} style={{
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    padding: '7px 12px', borderRadius: 8,
                    background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.06)',
                    gap: 8,
                  }}>
                    <code style={{ fontSize: 11, fontWeight: 700, color: '#475569', flexShrink: 0 }}>{r.id}</code>
                    <span style={{ fontSize: 12, color: '#94a3b8', flex: 1, display:'flex', alignItems:'center', gap:4 }}>
                      <Navigation size={10} strokeWidth={2} color="#475569" /> {r.origin} → {r.destination}
                    </span>
                    <span style={{ fontSize: 10, color: '#64748b', display:'flex', alignItems:'center', gap:3 }}>
                      <Users size={10} strokeWidth={2} /> {r.passengers}
                    </span>
                    <span style={{ fontSize: 10, color: '#64748b', display:'flex', alignItems:'center', gap:3 }}>
                      <Clock size={10} strokeWidth={2} /> t={r.time}s
                    </span>
                    <span style={{
                      fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 999,
                      background: `${pMeta.color}18`, color: pMeta.color,
                      flexShrink: 0,
                    }}>{pMeta.label}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
