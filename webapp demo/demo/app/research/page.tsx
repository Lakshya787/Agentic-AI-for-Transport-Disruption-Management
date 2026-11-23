import { BookOpen, Target, CheckCircle2, XCircle, FlaskConical } from 'lucide-react';
import { PAPERS, HYPOTHESES } from '@/lib/data';
import PaperCard from '@/components/PaperCard';

export default function ResearchPage() {
  const colorMap: Record<string, { accent: string; dim: string }> = {
    cyan:    { accent: '#00d4ff', dim: 'rgba(0,212,255,0.1)'  },
    emerald: { accent: '#10b981', dim: 'rgba(16,185,129,0.1)' },
    amber:   { accent: '#f59e0b', dim: 'rgba(245,158,11,0.1)' },
    purple:  { accent: '#8b5cf6', dim: 'rgba(139,92,246,0.1)' },
    rose:    { accent: '#f43f5e', dim: 'rgba(244,63,94,0.1)'  },
  };

  const verdictMeta: Record<string, { label: string; color: string; bg: string }> = {
    confirmed: { label: 'Confirmed ✓',  color: '#10b981', bg: 'rgba(16,185,129,0.12)' },
    refuted:   { label: 'Refuted ✗',   color: '#f43f5e', bg: 'rgba(244,63,94,0.12)'  },
    partial:   { label: 'Partial ~',   color: '#f59e0b', bg: 'rgba(245,158,11,0.12)' },
  };

  const gapRows = [
    { name: 'Mahmud 2024',    multi: false, llm: false, guard: false, realtime: true,  transport: true,  star: false },
    { name: 'Nie 2023',       multi: false, llm: false, guard: false, realtime: true,  transport: true,  star: false },
    { name: 'Wandelt 2024',   multi: false, llm: false, guard: false, realtime: false, transport: true,  star: false },
    { name: 'Wu & Zeng 2026', multi: false, llm: true,  guard: false, realtime: false, transport: true,  star: false },
    { name: 'Cemri 2025',     multi: true,  llm: true,  guard: false, realtime: false, transport: false, star: false },
    { name: 'This Work',      multi: true,  llm: true,  guard: true,  realtime: true,  transport: true,  star: true  },
  ];

  // Real benchmark data for the results table (from results/RESULTS.md)
  const benchmarkRows = [
    { metric: 'RFR (%) — L1',   b1: '100.0', b2: '100.0', b3: '100.0', winner: 'B1/B2/B3' },
    { metric: 'RFR (%) — L2',   b1: '100.0', b2: '100.0', b3: '100.0', winner: 'B1/B2/B3' },
    { metric: 'RFR (%) — L3',   b1:  '83.3', b2:  '88.9', b3:  '77.8', winner: 'B2'       },
    { metric: 'RFR (%) — L4',   b1:  '75.0', b2:  '41.7', b3:  '58.3', winner: 'B1'       },
    { metric: 'RFR (%) — L5',   b1:  '44.4', b2:  '61.5', b3:  '50.0', winner: 'B2'       },
    { metric: 'HCVR (%) — L1',  b1:   '0.0', b2:  '83.3', b3:   '0.0', winner: 'B1/B3'    },
    { metric: 'HCVR (%) — L2',  b1:   '0.0', b2:  '75.0', b3:  '25.0', winner: 'B1'       },
    { metric: 'HCVR (%) — L3',  b1:   '0.0', b2:  '60.0', b3:  '40.0', winner: 'B1'       },
    { metric: 'HCVR (%) — L4',  b1:   '0.0', b2: '100.0', b3:  '70.0', winner: 'B1'       },
    { metric: 'HCVR (%) — L5',  b1:   '0.0', b2: '100.0', b3:  '75.0', winner: 'B1'       },
    { metric: 'Latency — L1',   b1:  '4 ms', b2: '3100 ms',b3:'3500 ms',winner: 'B1'      },
    { metric: 'Latency — L5',   b1:  '8 ms', b2: '2000 ms',b3:'4600 ms',winner: 'B1'      },
    { metric: 'Tokens — L5',    b1:     '0', b2:   '1118', b3:   '2654', winner: 'B1'     },
    { metric: 'Post-guard violations', b1: '0', b2: '0', b3: '0', winner: 'All' },
  ];

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 24px', display: 'flex', flexDirection: 'column', gap: 48 }}>

      {/* Header */}
      <div>
        <div className="section-label">Research Foundation</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', marginBottom: 8 }}>Literature & Hypotheses</h1>
        <p style={{ color: '#64748b', fontSize: 14 }}>Five core papers ground this research. Each identifies a gap this project directly addresses.</p>
      </div>

      {/* Paper cards */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <BookOpen size={18} color="#00d4ff" strokeWidth={2} /> Core Literature
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 20 }}>
          {PAPERS.map(paper => <PaperCard key={paper.id} paper={paper} />)}
        </div>
      </section>

      {/* Gap matrix */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20 }}>Research Gap Matrix</h2>
        <div className="glass-static" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Paper</th>
                <th style={{ textAlign: 'center' }}>Multi-Agent</th>
                <th style={{ textAlign: 'center' }}>LLM-Based</th>
                <th style={{ textAlign: 'center' }}>Safety Guard</th>
                <th style={{ textAlign: 'center' }}>Real-time</th>
                <th style={{ textAlign: 'center' }}>Transport</th>
              </tr>
            </thead>
            <tbody>
              {gapRows.map((row, i) => (
                <tr key={i} style={{ background: row.star ? 'rgba(0,212,255,0.04)' : undefined }}>
                  <td style={{ fontWeight: row.star ? 700 : 400, color: row.star ? '#00d4ff' : '#94a3b8' }}>
                    {row.star ? '★ ' : ''}{row.name}
                  </td>
                  {[row.multi, row.llm, row.guard, row.realtime, row.transport].map((v, j) => (
                    <td key={j} style={{ textAlign: 'center' }}>
                      {v
                        ? <CheckCircle2 size={15} color="#10b981" strokeWidth={2.5} style={{ display:'inline-block' }} />
                        : <XCircle      size={15} color="#334155" strokeWidth={2}   style={{ display:'inline-block' }} />
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Real benchmark results table */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 8 }}>
          <FlaskConical size={18} color="#8b5cf6" strokeWidth={2} /> Benchmark Results (from results/RESULTS.md)
        </h2>
        <p style={{ fontSize: 13, color: '#475569', marginBottom: 20 }}>
          Real simulation results across all 5 disruption levels. Lower HCVR &amp; latency is better. Higher RFR is better.
          Post-guard violations = 0 for all controllers.
        </p>
        <div className="glass-static" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Metric</th>
                <th style={{ color: '#00d4ff', textAlign: 'right' }}>B1 Rule-Based</th>
                <th style={{ color: '#f59e0b', textAlign: 'right' }}>B2 Single-LLM</th>
                <th style={{ color: '#8b5cf6', textAlign: 'right' }}>B3 Multi-Agent</th>
                <th style={{ textAlign: 'center' }}>Best</th>
              </tr>
            </thead>
            <tbody>
              {benchmarkRows.map((row, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 600, color: '#64748b', fontSize: 11 }}>{row.metric}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: row.winner.includes('B1') ? '#10b981' : '#94a3b8', fontFamily: 'monospace' }}>{row.b1}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: row.winner.includes('B2') ? '#10b981' : '#94a3b8', fontFamily: 'monospace' }}>{row.b2}</td>
                  <td style={{ textAlign: 'right', fontWeight: 700, color: row.winner.includes('B3') ? '#10b981' : '#94a3b8', fontFamily: 'monospace' }}>{row.b3}</td>
                  <td style={{ textAlign: 'center', fontSize: 11, color: '#475569' }}>{row.winner}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Hypotheses with verdict badges */}
      <section>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Target size={18} color="#8b5cf6" strokeWidth={2} /> All 5 Hypotheses — Empirical Verdicts
        </h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {HYPOTHESES.map((h, i) => {
            const c = colorMap[h.color];
            const verdict = verdictMeta[h.verdict ?? 'partial'];
            return (
              <div key={h.id} className="glass-static" style={{
                padding: '18px 22px', display: 'flex', alignItems: 'flex-start', gap: 18,
                borderLeft: `3px solid ${c.accent}`,
                animation: `fade-in-up 0.4s ease ${i * 0.08}s both`,
              }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, flexShrink: 0, background: c.dim, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Target size={15} color={c.accent} strokeWidth={2.5} />
                </div>
                <div style={{ flex: 1 }}>
                  <span style={{ fontSize: 11, fontWeight: 800, color: c.accent, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 4, display: 'block' }}>{h.label}</span>
                  <p style={{ fontSize: 14, color: '#94a3b8', lineHeight: 1.6 }}>{h.text}</p>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, alignItems: 'flex-end', flexShrink: 0 }}>
                  <div style={{ padding: '4px 14px', borderRadius: 999, background: c.dim, color: c.accent, fontSize: 12, fontWeight: 700, whiteSpace: 'nowrap' }}>
                    {h.target}
                  </div>
                  <div style={{ padding: '4px 12px', borderRadius: 999, background: verdict.bg, color: verdict.color, fontSize: 11, fontWeight: 700, whiteSpace: 'nowrap', border: `1px solid ${verdict.color}30` }}>
                    {verdict.label}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </section>

    </div>
  );
}
