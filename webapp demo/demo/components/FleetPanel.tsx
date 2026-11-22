// Fleet Panel — shows V0–V5 (or V001–V010) status per scenario
import { Scenario } from '@/lib/data';
import { Battery, MapPin, Users, AlertTriangle, CheckCircle2 } from 'lucide-react';

// Static fleet state derived from scenarios.py DEFAULT_FLEET_POSITIONS & LEVEL_CONFIG
// position, capacity from: DEFAULT_FLEET_POSITIONS = ["N0","N3","N4","N7","N12","N8"]
// Using the grid A/B/C/D legacy names that match current SCENARIOS data
const BASE_FLEET = [
  { id: 'V001', position: 'A0', capacity: 4, label: 'Van 1' },
  { id: 'V002', position: 'A3', capacity: 6, label: 'Bus 2' },
  { id: 'V003', position: 'B0', capacity: 4, label: 'Van 3' },
  { id: 'V004', position: 'B3', capacity: 6, label: 'Bus 4' },
  { id: 'V005', position: 'D0', capacity: 4, label: 'Van 5' },
  { id: 'V006', position: 'C0', capacity: 6, label: 'Bus 6' },
];

// SoC ranges from scenarios.py: L1–L3 → 35–95%, L4–L5 → 25–80%
const SOC_BY_LEVEL: Record<number, number[]> = {
  1: [82, 91, 67, 78, 55, 88],
  2: [75, 85, 62, 71, 48, 79],
  3: [68, 77, 55, 63, 42, 72],
  4: [45, 62, 38, 55, 28, 59],
  5: [38, 55, 30, 48, 25, 52],
};

function SocBar({ soc }: { soc: number }) {
  const color = soc >= 60 ? '#10b981' : soc >= 30 ? '#f59e0b' : '#f43f5e';
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
      <div style={{ flex: 1, height: 6, background: 'rgba(255,255,255,0.08)', borderRadius: 999, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${soc}%`, background: `linear-gradient(90deg, ${color}80, ${color})`, borderRadius: 999, transition: 'width 0.5s ease' }} />
      </div>
      <span style={{ fontSize: 11, fontWeight: 700, color, minWidth: 32, textAlign: 'right' }}>{soc}%</span>
    </div>
  );
}

interface Props { scenario: Scenario; }

export default function FleetPanel({ scenario }: Props) {
  const level = scenario.level ?? 1;
  const socs = SOC_BY_LEVEL[level] ?? SOC_BY_LEVEL[1];

  // Which vehicles are broken in this scenario
  const brokenIds = new Set(
    scenario.disruptions
      .filter(d => d.type === 'vehicle_breakdown' && d.vehicleId)
      .map(d => d.vehicleId!)
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      {BASE_FLEET.map((v, idx) => {
        const isBroken = brokenIds.has(v.id);
        const soc = socs[idx] ?? 50;
        const statusColor = isBroken ? '#f43f5e' : '#10b981';

        return (
          <div key={v.id} style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '8px 12px', borderRadius: 10,
            background: isBroken ? 'rgba(244,63,94,0.06)' : 'rgba(255,255,255,0.03)',
            border: `1px solid ${isBroken ? 'rgba(244,63,94,0.2)' : 'rgba(255,255,255,0.07)'}`,
          }}>
            {/* Status icon */}
            <div style={{ flexShrink: 0 }}>
              {isBroken
                ? <AlertTriangle size={13} color="#f43f5e" strokeWidth={2.5} />
                : <CheckCircle2  size={13} color="#10b981" strokeWidth={2.5} />
              }
            </div>

            {/* Vehicle ID */}
            <code style={{ fontSize: 11, fontWeight: 700, color: statusColor, flexShrink: 0, minWidth: 36 }}>
              {v.id}
            </code>

            {/* Position */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
              <MapPin size={10} strokeWidth={2} color="#475569" />
              <span style={{ fontSize: 10, color: '#475569' }}>{v.position}</span>
            </div>

            {/* Capacity */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 4, flexShrink: 0 }}>
              <Users size={10} strokeWidth={2} color="#475569" />
              <span style={{ fontSize: 10, color: '#475569' }}>{v.capacity}</span>
            </div>

            {/* SoC bar */}
            {isBroken ? (
              <span style={{ fontSize: 10, color: '#f43f5e', fontWeight: 600, marginLeft: 'auto' }}>OUT OF SERVICE</span>
            ) : (
              <div style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 6 }}>
                <Battery size={10} strokeWidth={2} color="#475569" />
                <SocBar soc={soc} />
              </div>
            )}
          </div>
        );
      })}

      {/* SoC range note */}
      <div style={{ fontSize: 10, color: '#334155', paddingTop: 4, lineHeight: 1.5 }}>
        SoC range for L{level}: {level <= 3 ? '35–95%' : '25–80%'} &nbsp;·&nbsp;
        SoC needed = route_min × 1.0% × 1.15 buffer
      </div>
    </div>
  );
}
