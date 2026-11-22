import { Metrics } from '@/lib/data';
import { AlertTriangle, CheckCircle2, Timer, Zap, XCircle, TrendingUp } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: number | string;
  unit?: string;
  color: 'cyan' | 'amber' | 'emerald' | 'rose' | 'purple';
  description?: string;
  projected?: boolean;
  Icon?: React.ComponentType<{ size?: number; strokeWidth?: number; color?: string }>;
}

const COLOR_MAP = {
  cyan:    { accent: '#00d4ff', dim: 'rgba(0,212,255,0.12)',  glow: 'rgba(0,212,255,0.20)'  },
  amber:   { accent: '#f59e0b', dim: 'rgba(245,158,11,0.12)', glow: 'rgba(245,158,11,0.20)' },
  emerald: { accent: '#10b981', dim: 'rgba(16,185,129,0.12)', glow: 'rgba(16,185,129,0.20)' },
  rose:    { accent: '#f43f5e', dim: 'rgba(244,63,94,0.12)',  glow: 'rgba(244,63,94,0.20)'  },
  purple:  { accent: '#8b5cf6', dim: 'rgba(139,92,246,0.12)', glow: 'rgba(139,92,246,0.20)' },
};

export default function MetricCard({ label, value, unit, color, description, projected, Icon }: MetricCardProps) {
  const c = COLOR_MAP[color];
  return (
    <div className="glass" style={{ padding: '20px 22px', position: 'relative', overflow: 'hidden' }}>
      {/* Top accent bar */}
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 2, background: `linear-gradient(90deg, transparent, ${c.accent}, transparent)` }} />
      {/* Glow blob */}
      <div style={{ position: 'absolute', bottom: -30, right: -30, width: 80, height: 80, borderRadius: '50%', background: c.glow, filter: 'blur(20px)', pointerEvents: 'none' }} />

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <span style={{ fontSize: 11, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#475569' }}>{label}</span>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          {Icon && <Icon size={15} color={c.accent} strokeWidth={2} />}
          {projected && (
            <span style={{
              fontSize: 9, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase',
              padding: '2px 7px', borderRadius: 999,
              background: 'rgba(245,158,11,0.15)', color: '#f59e0b', border: '1px solid rgba(245,158,11,0.2)',
            }}>Projected</span>
          )}
        </div>
      </div>

      {/* Value */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 4, marginBottom: 6 }}>
        <span style={{ fontSize: 32, fontWeight: 800, lineHeight: 1, color: c.accent, textShadow: `0 0 20px ${c.glow}` }}>{value}</span>
        {unit && <span style={{ fontSize: 14, color: '#475569', fontWeight: 500 }}>{unit}</span>}
      </div>
      {description && <p style={{ fontSize: 12, color: '#475569', lineHeight: 1.5, marginTop: 4 }}>{description}</p>}
    </div>
  );
}

export function MetricsRow({ metrics, projected }: { metrics: Metrics; projected?: boolean }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
      <MetricCard label="HCVR"    value={metrics.hcvr.toFixed(1)}          unit="%"  color="rose"    description="Hard Constraint Violation Rate" projected={projected} Icon={AlertTriangle} />
      <MetricCard label="RFR"     value={metrics.rfr.toFixed(1)}           unit="%"  color="emerald" description="Request Fulfillment Rate"       projected={projected} Icon={CheckCircle2}  />
      <MetricCard label="ADIF"    value={metrics.adif.toFixed(3)}                    color="amber"   description="Avg Delay Inflation Factor"   projected={projected} Icon={TrendingUp}    />
      <MetricCard label="Latency" value={metrics.latency.toFixed(0)}       unit="ms" color="cyan"    description="Execution Latency"            projected={projected} Icon={Zap}          />
      <MetricCard label="IDR"     value={metrics.idr.toFixed(1)}           unit="%"  color="purple"  description="Infeasible Decision Rate"     projected={projected} Icon={XCircle}      />
      <MetricCard label="Tokens"  value={metrics.tokens ? metrics.tokens.toLocaleString() : '0'} unit="tk" color="cyan" description="LLM Tokens (Total)" projected={projected} Icon={Zap} />
      <MetricCard label="Cost"    value={metrics.costUsd ? `$${metrics.costUsd.toFixed(4)}` : '$0.00'} color="amber" description="API Cost Estimate" projected={projected} Icon={Timer} />
    </div>
  );
}
