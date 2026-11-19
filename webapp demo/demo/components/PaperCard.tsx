import { BookOpen, ExternalLink, CheckCircle2, Search } from 'lucide-react';
import { Paper } from '@/lib/data';

const COLOR_MAP = {
  cyan:    { accent: '#00d4ff', dim: 'rgba(0,212,255,0.08)',  border: 'rgba(0,212,255,0.2)'  },
  amber:   { accent: '#f59e0b', dim: 'rgba(245,158,11,0.08)', border: 'rgba(245,158,11,0.2)' },
  emerald: { accent: '#10b981', dim: 'rgba(16,185,129,0.08)', border: 'rgba(16,185,129,0.2)' },
  rose:    { accent: '#f43f5e', dim: 'rgba(244,63,94,0.08)',  border: 'rgba(244,63,94,0.2)'  },
  purple:  { accent: '#8b5cf6', dim: 'rgba(139,92,246,0.08)', border: 'rgba(139,92,246,0.2)' },
};

export default function PaperCard({ paper }: { paper: Paper }) {
  const c = COLOR_MAP[paper.color];
  return (
    <div className="glass" style={{ padding: '22px 24px', position: 'relative', overflow: 'hidden' }}>
      {/* Left accent strip */}
      <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: 3, background: `linear-gradient(180deg, ${c.accent}, transparent)`, borderRadius: '16px 0 0 16px' }} />

      <div style={{ marginLeft: 8 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
          <span style={{ fontSize: 10, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: c.accent, padding: '2px 8px', background: c.dim, borderRadius: 999 }}>{paper.year}</span>
          <span style={{ fontSize: 11, color: '#475569', display: 'flex', alignItems: 'center', gap: 4 }}>
            <ExternalLink size={11} strokeWidth={2} color="#475569" /> {paper.journal}
          </span>
        </div>

        <h3 style={{ fontSize: 15, fontWeight: 700, color: '#f1f5f9', marginBottom: 4, lineHeight: 1.4 }}>{paper.title}</h3>
        <p style={{ fontSize: 12, color: '#64748b', marginBottom: 14, display: 'flex', alignItems: 'center', gap: 5 }}>
          <BookOpen size={11} strokeWidth={2} color="#475569" /> {paper.authors}
        </p>

        <div className="divider" style={{ margin: '10px 0' }} />

        <div style={{ marginBottom: 10 }}>
          <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#10b981', marginBottom: 5, display: 'flex', alignItems: 'center', gap: 5 }}>
            <CheckCircle2 size={11} strokeWidth={2.5} color="#10b981" /> Contribution
          </div>
          <p style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.5 }}>{paper.contribution}</p>
        </div>

        <div>
          <div style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: '#f43f5e', marginBottom: 5, display: 'flex', alignItems: 'center', gap: 5 }}>
            <Search size={11} strokeWidth={2.5} color="#f43f5e" /> Research Gap
          </div>
          <p style={{ fontSize: 12, color: '#64748b', lineHeight: 1.5 }}>{paper.gap}</p>
        </div>
      </div>
    </div>
  );
}
