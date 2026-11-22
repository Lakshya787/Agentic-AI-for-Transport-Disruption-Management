import { Eye, Wrench, ShieldCheck } from 'lucide-react';
import AgentPipeline from '@/components/AgentPipeline';

export default function ArchitecturePage() {
  const cards = [
    {
      Icon: Eye,
      title: 'Information Scoping',
      desc: 'Each agent sees only its relevant slice of system state — preventing information overload and reducing hallucination risk.',
      color: '#00d4ff',
      dim: 'rgba(0,212,255,0.1)',
    },
    {
      Icon: Wrench,
      title: 'Tool-Augmented',
      desc: 'Agents have access to structured tools (BFS solver, Fleet registry, SoC checker) rather than relying purely on LLM recall.',
      color: '#8b5cf6',
      dim: 'rgba(139,92,246,0.1)',
    },
    {
      Icon: ShieldCheck,
      title: 'Constraint-First Safety',
      desc: 'The Safety Guard is not optional — it runs after every coordinator decision, blocking infeasible outputs before execution.',
      color: '#f43f5e',
      dim: 'rgba(244,63,94,0.1)',
    },
  ];

  return (
    <div style={{ maxWidth: 1280, margin: '0 auto', padding: '40px 24px', display: 'flex', flexDirection: 'column', gap: 32 }}>

      <div>
        <div className="section-label">System Architecture</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: '#f1f5f9', marginBottom: 8 }}>Multi-Agent Pipeline Design</h1>
        <p style={{ color: '#64748b', fontSize: 14, maxWidth: 680 }}>
          Three LLM agents + one deterministic routing tool work in sequence — each with a defined
          information scope and toolset — before a Safety Guard validates every decision.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16 }}>
        {cards.map(({ Icon, title, desc, color, dim }) => (
          <div key={title} className="glass" style={{ padding: '22px' }}>
            <div style={{ width: 42, height: 42, borderRadius: 12, background: dim, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 14 }}>
              <Icon size={20} color={color} strokeWidth={2} />
            </div>
            <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginBottom: 8 }}>{title}</div>
            <p style={{ fontSize: 12, color: '#64748b', lineHeight: 1.6 }}>{desc}</p>
          </div>
        ))}
      </div>

      <div className="glass-static" style={{ padding: '28px 24px' }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginBottom: 20 }}>Agent Pipeline · Detailed View</div>
        <AgentPipeline />
      </div>

    </div>
  );
}
