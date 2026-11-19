'use client';
import { DecisionEntry } from '@/lib/data';
import { CheckCircle2, XCircle, Navigation, Truck, Ruler, Clock } from 'lucide-react';

export default function DecisionLog({ decisions }: { decisions: DecisionEntry[] }) {
  if (!decisions || decisions.length === 0) {
    return <div style={{ textAlign: 'center', padding: '40px 20px', color: '#475569' }}>No decisions for this scenario.</div>;
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="data-table">
        <thead>
          <tr>
            <th>Request</th>
            <th>Vehicle</th>
            <th>Action</th>
            <th>Route</th>
            <th>Distance</th>
            <th>Travel Time</th>
            <th>Guard</th>
            <th>Rejection Reason</th>
          </tr>
        </thead>
        <tbody>
          {decisions.map((d, i) => {
            const dispatched = d.action === 'REROUTE_AND_DISPATCH';
            return (
              <tr key={i}>
                {/* Request ID */}
                <td>
                  <code style={{ fontSize: 11, color: '#94a3b8', background: 'rgba(255,255,255,0.05)', padding: '2px 6px', borderRadius: 4 }}>
                    {d.requestId}
                  </code>
                </td>

                {/* Vehicle */}
                <td>
                  {d.vehicleId
                    ? <span style={{ display:'inline-flex', alignItems:'center', gap:5, fontSize: 12, color: '#00d4ff' }}>
                        <Truck size={11} strokeWidth={2} /> {d.vehicleId}
                      </span>
                    : <span style={{ color:'#334155', fontSize: 12 }}>—</span>
                  }
                </td>

                {/* Action */}
                <td>
                  <span style={{
                    display: 'inline-flex', alignItems: 'center', gap: 5,
                    padding: '3px 10px', borderRadius: 999, fontSize: 11, fontWeight: 600,
                    background: dispatched ? 'rgba(16,185,129,0.15)' : 'rgba(244,63,94,0.15)',
                    color: dispatched ? '#10b981' : '#f43f5e',
                  }}>
                    {dispatched
                      ? <><CheckCircle2 size={11} strokeWidth={2.5} /> Dispatched</>
                      : <><XCircle size={11} strokeWidth={2.5} /> No Vehicle</>
                    }
                  </span>
                </td>

                {/* Route */}
                <td style={{ maxWidth: 220 }}>
                  {d.route
                    ? <div style={{ display:'flex', alignItems:'center', gap:4, fontSize: 11, color: '#64748b', flexWrap:'wrap' }}>
                        <Navigation size={10} strokeWidth={2} color="#475569" />
                        {d.route.join(' → ')}
                      </div>
                    : <span style={{ color:'#334155', fontSize: 12 }}>—</span>
                  }
                </td>

                {/* Distance */}
                <td>
                  {d.distanceKm != null
                    ? <span style={{ display:'inline-flex', alignItems:'center', gap:4, fontSize: 12, color: '#94a3b8' }}>
                        <Ruler size={11} strokeWidth={2} /> {d.distanceKm} km
                      </span>
                    : <span style={{ color:'#334155' }}>—</span>
                  }
                </td>

                {/* Travel Time */}
                <td>
                  {d.travelTimeS != null
                    ? <span style={{ display:'inline-flex', alignItems:'center', gap:4, fontSize: 12, color: '#00d4ff' }}>
                        <Clock size={11} strokeWidth={2} /> {d.travelTimeS}s
                      </span>
                    : <span style={{ color:'#334155' }}>—</span>
                  }
                </td>

                {/* Safety Guard */}
                <td style={{ textAlign: 'center' }}>
                  {d.safetyGuardPassed
                    ? <CheckCircle2 size={14} color="#10b981" strokeWidth={2.5} style={{ display:'inline-block' }} />
                    : <XCircle      size={14} color="#f43f5e" strokeWidth={2.5} style={{ display:'inline-block' }} />
                  }
                </td>

                {/* Rejection Reason */}
                <td style={{ fontSize: 11, color: '#475569', maxWidth: 180, lineHeight: 1.4 }}>
                  {d.rejectionReason ?? <span style={{ color:'#1e293b' }}>—</span>}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
