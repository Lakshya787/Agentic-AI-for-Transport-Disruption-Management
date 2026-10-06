import Link from 'next/link';
import { Map, BarChart2, Target, GitBranch, Calendar, Lightbulb } from 'lucide-react';
import { HYPOTHESES, TIMELINE_WEEKS } from '@/lib/data';

export default function HomePage() {
  const colorMap: Record<string, { accent: string; dim: string }> = {
    cyan:    { accent: '#00d4ff', dim: 'rgba(0,212,255,0.1)'  },
    emerald: { accent: '#10b981', dim: 'rgba(16,185,129,0.1)' },
    amber:   { accent: '#f59e0b', dim: 'rgba(245,158,11,0.1)' },
    purple:  { accent: '#8b5cf6', dim: 'rgba(139,92,246,0.1)' },
    rose:    { accent: '#f43f5e', dim: 'rgba(244,63,94,0.1)'  },
  };

  const hypothesisIcons = [Target, GitBranch, Target, Lightbulb, Target];

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '48px 24px', display: 'flex', flexDirection: 'column', gap: 56 }}>

      {/* ── Hero ─────────────────────────────────── */}
      <section style={{ textAlign: 'center', position: 'relative' }}>
        <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: 600, height: 300, background: 'radial-gradient(ellipse, rgba(0,212,255,0.06) 0%, transparent 70%)', pointerEvents: 'none' }} />

        <div className="badge badge-cyan" style={{ marginBottom: 20, display: 'inline-flex', gap: 6 }}>
          <Calendar size={11} strokeWidth={2} /> Minor Research Project · Oct 2026
        </div>

        <h1 style={{
          fontSize: 'clamp(28px, 5vw, 52px)', fontWeight: 900, lineHeight: 1.15, marginBottom: 20,
          background: 'linear-gradient(135deg, #f1f5f9 30%, #00d4ff 70%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>
          Agentic AI for Transport<br />Disruption Management
        </h1>

        <p style={{ fontSize: 18, color: '#64748b', maxWidth: 640, margin: '0 auto 28px', lineHeight: 1.7 }}>
          Can a structured multi-agent LLM system outperform rule-based and single-LLM baselines
          in transport disruption management while maintaining hard-constraint safety?
        </p>

        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/simulator" style={{ textDecoration: 'none' }}>
            <button style={{
              padding: '12px 28px', borderRadius: 10, border: 'none', cursor: 'pointer',
              background: 'linear-gradient(135deg, #00d4ff, #0077ff)', color: '#020817',
              fontWeight: 700, fontSize: 14, fontFamily: 'Inter,sans-serif',
              boxShadow: '0 0 24px rgba(0,212,255,0.4)', transition: 'all 0.2s ease',
              display: 'flex', alignItems: 'center', gap: 7,
            }}>
              <Map size={15} strokeWidth={2.5} /> Try Network Simulator
            </button>
          </Link>
          <Link href="/results" style={{ textDecoration: 'none' }}>
            <button style={{
              padding: '12px 28px', borderRadius: 10, cursor: 'pointer',
              background: 'rgba(255,255,255,0.06)', color: '#f1f5f9',
              border: '1px solid rgba(255,255,255,0.12)', fontWeight: 600, fontSize: 14,
              fontFamily: 'Inter,sans-serif', transition: 'all 0.2s ease',
              display: 'flex', alignItems: 'center', gap: 7,
            }}>
              <BarChart2 size={15} strokeWidth={2} /> View Results
            </button>
          </Link>
        </div>
      </section>

      {/* ── Hypothesis Cards ─────────────────────── */}
      <section>
        <div className="section-label">Research Hypotheses</div>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: '#f1f5f9', marginBottom: 20 }}>What We&apos;re Testing</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
          {HYPOTHESES.map((h, i) => {
            const c = colorMap[h.color];
            const HIcon = hypothesisIcons[i] ?? Target;
            return (
              <div key={h.id} className="glass" style={{ padding: '20px 22px', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${c.accent}, transparent)` }} />
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 7, background: c.dim, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <HIcon size={14} color={c.accent} strokeWidth={2.5} />
                  </div>
                  <span style={{ fontSize: 11, fontWeight: 800, letterSpacing: '0.1em', color: c.accent, textTransform: 'uppercase' }}>{h.label}</span>
                </div>
                <p style={{ fontSize: 13, color: '#94a3b8', lineHeight: 1.6, marginBottom: 12 }}>{h.text}</p>
                <div style={{ display: 'inline-flex', padding: '4px 12px', borderRadius: 999, background: c.dim, color: c.accent, fontSize: 12, fontWeight: 700 }}>
                  Target: {h.target}
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* ── Timeline ─────────────────────────────── */}
      <section>
        <div className="section-label">Project Timeline</div>
        <h2 style={{ fontSize: 22, fontWeight: 700, color: '#f1f5f9', marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
          <Calendar size={20} color="#00d4ff" strokeWidth={2} /> 8-Week Research Plan
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(8, 1fr)', gap: 8 }}>
          {TIMELINE_WEEKS.map(w => (
            <div key={w.week} style={{
              background: w.done ? 'rgba(16,185,129,0.12)' : 'rgba(255,255,255,0.03)',
              border: `1px solid ${w.done ? 'rgba(16,185,129,0.3)' : 'rgba(255,255,255,0.08)'}`,
              borderRadius: 12, padding: '16px 12px', textAlign: 'center', position: 'relative', overflow: 'hidden',
            }}>
              {w.done && <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: 'linear-gradient(90deg, transparent, #10b981, transparent)' }} />}
              <div style={{ fontSize: 11, fontWeight: 700, color: w.done ? '#10b981' : '#475569', marginBottom: 8 }}>{w.week}</div>
              <div style={{ fontSize: 10, color: w.done ? '#10b981' : '#475569', lineHeight: 1.4 }}>{w.label}</div>
              <div style={{ marginTop: 10, display: 'flex', justifyContent: 'center' }}>
                {w.done
                  ? <div style={{ width: 16, height: 16, borderRadius: '50%', background: 'rgba(16,185,129,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#10b981' }} />
                    </div>
                  : <div style={{ width: 16, height: 16, borderRadius: '50%', border: '2px solid #334155' }} />
                }
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* ── Research Gap ─────────────────────────── */}
      <section>
        <div className="glass-static" style={{ padding: '28px 32px', borderLeft: '3px solid #00d4ff' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <Lightbulb size={16} color="#00d4ff" strokeWidth={2} />
            <div className="section-label" style={{ marginBottom: 0 }}>Open Research Gap</div>
          </div>
          <p style={{ fontSize: 16, color: '#94a3b8', lineHeight: 1.8, maxWidth: 800 }}>
            Existing work addresses either{' '}
            <span style={{ color: '#00d4ff', fontWeight: 600 }}>rule-based transport routing</span>{' '}
            or{' '}
            <span style={{ color: '#f59e0b', fontWeight: 600 }}>single-LLM decision-making</span>,
            but none combine a{' '}
            <span style={{ color: '#8b5cf6', fontWeight: 600 }}>structured multi-agent architecture</span>{' '}
            with formal constraint enforcement via a{' '}
            <span style={{ color: '#f43f5e', fontWeight: 600 }}>Safety Guard</span>{' '}
            for real-time transport disruption scenarios.
          </p>
        </div>
      </section>

    </div>
  );
}
