'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Home, Map, BarChart2, Cpu, BookOpen, TrafficCone } from 'lucide-react';

const NAV = [
  { href: '/',             label: 'Home',         Icon: Home,     id: 'nav-home'         },
  { href: '/simulator',    label: 'Simulator',    Icon: Map,      id: 'nav-simulator'    },
  { href: '/results',      label: 'Results',      Icon: BarChart2,id: 'nav-results'      },
  { href: '/architecture', label: 'Architecture', Icon: Cpu,      id: 'nav-architecture' },
  { href: '/research',     label: 'Research',     Icon: BookOpen, id: 'nav-research'     },
];

export default function NavBar() {
  const pathname = usePathname();

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(2, 8, 23, 0.85)',
      backdropFilter: 'blur(20px)',
      WebkitBackdropFilter: 'blur(20px)',
      borderBottom: '1px solid rgba(255,255,255,0.07)',
    }}>
      <div style={{
        maxWidth: 1280, margin: '0 auto', padding: '0 24px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: 64,
      }}>
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 34, height: 34, borderRadius: 9,
            background: 'linear-gradient(135deg, #00d4ff, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            boxShadow: '0 0 16px rgba(0,212,255,0.35)',
          }}>
            <TrafficCone size={18} color="#020817" strokeWidth={2.5} />
          </div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9', lineHeight: 1 }}>AgentTransit</div>
            <div style={{ fontSize: 10, color: '#475569', lineHeight: 1, marginTop: 2 }}>Transport Disruption AI</div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 4 }}>
          {NAV.map(({ href, label, Icon, id }) => {
            const active = pathname === href;
            return (
              <Link key={href} href={href} id={id} style={{ textDecoration: 'none' }}>
                <button className={`tab-btn${active ? ' active' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: 6, fontFamily: 'Inter, sans-serif' }}>
                  <Icon size={14} strokeWidth={2} />
                  {label}
                </button>
              </Link>
            );
          })}
        </div>

        {/* Status pill */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 6, padding: '4px 12px',
          borderRadius: 999, background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.2)',
        }}>
          <div style={{
            width: 6, height: 6, borderRadius: '50%', background: '#10b981',
            boxShadow: '0 0 6px #10b981', animation: 'pulse-dot 2s ease-in-out infinite',
          }} />
          <span style={{ fontSize: 11, fontWeight: 600, color: '#10b981' }}>W3 Complete</span>
        </div>
      </div>
    </nav>
  );
}
