'use client';
import { useState } from 'react';
import dynamic from 'next/dynamic';
import { Info } from 'lucide-react';
import { B1_RESULTS, B2_PROJECTED, B3_PROJECTED, SCENARIOS } from '@/lib/data';
import { MetricsRow } from '@/components/MetricCard';
import DecisionLog from '@/components/DecisionLog';

const ComparisonChart = dynamic(() => import('@/components/ComparisonChart'), { ssr: false });
const ComplexityCurve = dynamic(() => import('@/components/ComplexityCurve'), { ssr: false });

type System    = 'B1' | 'B2' | 'B3';
type MetricKey = 'hcvr' | 'rfr' | 'adif' | 'latency' | 'idr';

const SYSTEMS: { id: System; label: string; color: string; projected?: boolean }[] = [
  { id: 'B1', label: 'B1 — Rule-Based',  color: '#00d4ff' },
  { id: 'B2', label: 'B2 — Single-LLM', color: '#f59e0b', projected: true },
  { id: 'B3', label: 'B3 — Multi-Agent',color: '#8b5cf6', projected: true },
];

const METRIC_OPTIONS: { key: MetricKey; label: string }[] = [
  { key: 'hcvr',    label: 'HCVR %'  },
  { key: 'rfr',     label: 'RFR %'   },
  { key: 'adif',    label: 'ADIF'    },
  { key: 'latency', label: 'Latency' },
  { key: 'idr',     label: 'IDR %'   },
];

const B1_METRICS = Object.fromEntries(
  Object.entries(B1_RESULTS).map(([k, v]) => [k, v.metrics])
);

export default function ResultsPage() {
  const [system,   setSystem]   = useState<System>('B1');
  const [scenario, setScenario] = useState('L1');
  const [metric,   setMetric]   = useState<MetricKey>('rfr');

  const currentMetrics =
    system === 'B1' ? B1_METRICS[scenario] :
    system === 'B2' ? B2_PROJECTED[scenario] :
    B3_PROJECTED[scenario];

  const isProjected = system !== 'B1';
  const currentDecisions = system === 'B1' ? B1_RESULTS[scenario]?.decisions ?? [] : [];

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 24px', display: 'flex', flexDirection: 'column', gap: 32 }}>

      <div>
        <div className="section-label">Benchmark Results</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', marginBottom: 8 }}>3-System Comparison</h1>
        <p style={{ color: '#64748b', fontSize: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
          <Info size={13} strokeWidth={2} color="#475569" />
          B1 data is real (from sim/results/). B2 & B3 values are projected from Wu & Zeng 2026 benchmarks.
        </p>
      </div>

      {/* Selectors */}
      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <div className="glass-static" style={{ padding: '6px', display: 'flex', gap: 4, borderRadius: 12 }}>
          {SYSTEMS.map(s => (
            <button key={s.id} id={`system-${s.id.toLowerCase()}`} onClick={() => setSystem(s.id)} style={{
              padding: '8px 18px', borderRadius: 8, border: 'none', cursor: 'pointer',
              fontWeight: 600, fontSize: 13, fontFamily: 'Inter,sans-serif',
              background: system === s.id ? `${s.color}20` : 'transparent',
              color: system === s.id ? s.color : '#64748b',
              borderBottom: system === s.id ? `2px solid ${s.color}` : '2px solid transparent',
              transition: 'all 0.2s ease',
            }}>
              {s.label}
              {s.projected && <span style={{ marginLeft: 6, fontSize: 9, background: 'rgba(245,158,11,0.2)', color: '#f59e0b', padding: '1px 5px', borderRadius: 4 }}>PROJ</span>}
            </button>
          ))}
        </div>

        <div className="glass-static" style={{ padding: '6px', display: 'flex', gap: 4, borderRadius: 12 }}>
          {SCENARIOS.map(s => (
            <button key={s.id} id={`scenario-result-${s.id.toLowerCase()}`} onClick={() => setScenario(s.id)} style={{
              padding: '8px 14px', borderRadius: 8, border: 'none', cursor: 'pointer',
              fontWeight: 600, fontSize: 12, fontFamily: 'Inter,sans-serif',
              background: scenario === s.id ? 'rgba(0,212,255,0.15)' : 'transparent',
              color: scenario === s.id ? '#00d4ff' : '#64748b',
              transition: 'all 0.2s ease',
            }}>{s.id}</button>
          ))}
        </div>
      </div>

      {currentMetrics && <MetricsRow metrics={currentMetrics} projected={isProjected} />}

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="glass-static" style={{ padding: '20px 22px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9' }}>All Systems — All Scenarios</div>
            <div style={{ display: 'flex', gap: 4 }}>
              {METRIC_OPTIONS.map(m => (
                <button key={m.key} id={`metric-${m.key}`} onClick={() => setMetric(m.key)} style={{
                  padding: '4px 10px', borderRadius: 6, border: 'none', cursor: 'pointer',
                  fontSize: 11, fontFamily: 'Inter,sans-serif', fontWeight: 600,
                  background: metric === m.key ? 'rgba(0,212,255,0.15)' : 'rgba(255,255,255,0.04)',
                  color: metric === m.key ? '#00d4ff' : '#475569', transition: 'all 0.2s ease',
                }}>{m.label}</button>
              ))}
            </div>
          </div>
          <ComparisonChart b1={B1_METRICS} b2={B2_PROJECTED} b3={B3_PROJECTED} selectedMetric={metric} selectedScenario={scenario} />
        </div>

        <div className="glass-static" style={{ padding: '20px 22px' }}>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>RFR vs Scenario Complexity</div>
          <div style={{ fontSize: 12, color: '#475569', marginBottom: 16 }}>Request Fulfillment Rate as disruption level increases L1→L5</div>
          <ComplexityCurve b1={B1_METRICS} b2={B2_PROJECTED} b3={B3_PROJECTED} />
        </div>
      </div>

      {/* Decision Log */}
      <div className="glass-static" style={{ padding: '20px 22px' }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>Decision Log — {scenario} {system === 'B1' ? '(Real)' : ''}</div>
        {system !== 'B1' ? (
          <div style={{ padding: '32px', textAlign: 'center', color: '#475569', fontSize: 13, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
            <Info size={15} strokeWidth={2} color="#475569" />
            Per-request decisions are only available for B1 (real simulation data). B2 & B3 are projected aggregate metrics.
          </div>
        ) : (
          <DecisionLog decisions={currentDecisions} />
        )}
      </div>
    </div>
  );
}
