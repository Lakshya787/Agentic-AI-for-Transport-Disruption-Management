'use client';
import { useRef, useEffect, useCallback } from 'react';
import { Scenario, NODES, EDGES } from '@/lib/data';

interface Props { scenario: Scenario; playing: boolean; }

// N0–N15 in a 4×4 grid: row = Math.floor(i/4), col = i%4
// Also keep A0–D3 legacy aliases so old data still works
const NODE_POS: Record<string, { x: number; y: number }> = {};
for (let i = 0; i < 16; i++) {
  const row = Math.floor(i / 4);
  const col = i % 4;
  NODE_POS[`N${i}`] = { x: col, y: row };
}
// Legacy A0–D3 aliases
['A','B','C','D'].forEach((r, ri) => {
  [0,1,2,3].forEach(ci => { NODE_POS[`${r}${ci}`] = { x: ci, y: ri }; });
});

// Fixed vehicle starting positions from scenarios.py DEFAULT_FLEET_POSITIONS
const VEHICLE_POSITIONS: Record<string, string> = {
  V0: 'A0', V1: 'A3', V2: 'B0', V3: 'B3', V4: 'D0', V5: 'C0',
  // legacy ids used in old data
  V001: 'A0', V002: 'A3', V003: 'B0', V004: 'B3', V005: 'D0', V006: 'C0',
  V007: 'A1', V008: 'B1', V009: 'C1', V010: 'D1',
};

const VEHICLE_COLORS = ['#00d4ff','#10b981','#f59e0b','#8b5cf6','#f43f5e','#06b6d4'];

const PAD  = 55;
const CELL = 105;

function gridXY(x: number, y: number) {
  return { cx: PAD + x * CELL, cy: PAD + y * CELL };
}

export default function NetworkCanvas({ scenario, playing }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animRef   = useRef<number>(0);

  const draw = useCallback((t: number) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // ── Build disruption sets ─────────────────────────────────────────────────
    const closedEdges    = new Set<string>();
    const congestedEdges = new Set<string>();
    const congestFactor  = new Map<string, number>();
    const brokenVehicles = new Set<string>();

    scenario.disruptions.forEach(d => {
      if (d.edge) {
        const key = [...d.edge].sort().join('|');
        if (d.type === 'road_closure')  closedEdges.add(key);
        if (d.type === 'congestion') {
          congestedEdges.add(key);
          congestFactor.set(key, d.congestionFactor ?? 1);
        }
      }
      if (d.type === 'vehicle_breakdown' && d.vehicleId) {
        brokenVehicles.add(d.vehicleId);
      }
    });

    // ── Draw edges ────────────────────────────────────────────────────────────
    EDGES.forEach(([a, b]) => {
      const posA = NODE_POS[a];
      const posB = NODE_POS[b];
      if (!posA || !posB) return;
      const key = [a, b].sort().join('|');
      const pa = gridXY(posA.x, posA.y);
      const pb = gridXY(posB.x, posB.y);

      ctx.beginPath();
      ctx.moveTo(pa.cx, pa.cy);
      ctx.lineTo(pb.cx, pb.cy);

      if (closedEdges.has(key)) {
        // Red dashed = road closed
        ctx.strokeStyle = '#f43f5e';
        ctx.lineWidth   = 3;
        ctx.setLineDash([8, 6]);
        ctx.globalAlpha = 0.95;
      } else if (congestedEdges.has(key)) {
        const factor = congestFactor.get(key) ?? 1;
        ctx.strokeStyle = factor >= 4 ? '#ef4444' : '#f59e0b';
        ctx.lineWidth   = 3;
        ctx.setLineDash([]);
        ctx.globalAlpha = 0.85;
      } else {
        ctx.strokeStyle = 'rgba(0,212,255,0.22)';
        ctx.lineWidth   = 1.5;
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      }
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;

      // ── Congestion factor label ─────────────────────────────────────────────
      if (congestedEdges.has(key)) {
        const mx = (pa.cx + pb.cx) / 2;
        const my = (pa.cy + pb.cy) / 2;
        const factor = congestFactor.get(key) ?? 1;
        ctx.fillStyle = factor >= 4 ? '#ef4444' : '#f59e0b';
        ctx.font = 'bold 9px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`×${factor}`, mx, my - 5);
      }

      // ── Closed edge X marker ──────────────────────────────────────────────
      if (closedEdges.has(key)) {
        const mx = (pa.cx + pb.cx) / 2;
        const my = (pa.cy + pb.cy) / 2;
        ctx.fillStyle = '#f43f5e';
        ctx.font = 'bold 11px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('✕', mx, my + 4);
      }
    });

    // ── Draw route animation (if playing) ────────────────────────────────────
    if (playing) {
      scenario.requests.forEach((req, i) => {
        const po = NODE_POS[req.origin];
        const pd = NODE_POS[req.destination];
        if (!po || !pd) return;
        const pa = gridXY(po.x, po.y);
        const pb = gridXY(pd.x, pd.y);
        const progress = ((t / 2000 + i * 0.3) % 1);
        const vx = pa.cx + (pb.cx - pa.cx) * progress;
        const vy = pa.cy + (pb.cy - pa.cy) * progress;
        const priorityColor = req.priority === 1 ? '#f43f5e' : req.priority === 2 ? '#f59e0b' : '#10b981';

        // Animated vehicle dot
        ctx.beginPath();
        ctx.arc(vx, vy, 6, 0, Math.PI * 2);
        ctx.fillStyle = priorityColor;
        ctx.shadowBlur = 14;
        ctx.shadowColor = priorityColor;
        ctx.fill();
        ctx.shadowBlur = 0;

        // Trail
        ctx.beginPath();
        ctx.arc(vx, vy, 10, 0, Math.PI * 2);
        ctx.strokeStyle = `${priorityColor}40`;
        ctx.lineWidth = 1;
        ctx.stroke();
      });
    }

    // ── Draw nodes ────────────────────────────────────────────────────────────
    NODES.forEach(n => {
      const pos = NODE_POS[n];
      if (!pos) return;
      const { cx, cy } = gridXY(pos.x, pos.y);

      // Check if this is a request origin/destination
      const isOrigin = scenario.requests.some(r => r.origin === n);
      const isDest   = scenario.requests.some(r => r.destination === n);
      const isHospital = (n === 'D3' || n === 'N15'); // Central Hospital
      const accent = isHospital ? '#f43f5e' : isDest ? '#10b981' : isOrigin ? '#f59e0b' : '#00d4ff';

      // Pulse ring for active nodes
      if (isOrigin || isDest || isHospital) {
        const pulse = 0.5 + 0.5 * Math.sin(t / 500);
        ctx.beginPath();
        ctx.arc(cx, cy, 15 + pulse * 4, 0, Math.PI * 2);
        ctx.strokeStyle = `${accent}30`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Node fill
      ctx.beginPath();
      ctx.arc(cx, cy, 10, 0, Math.PI * 2);
      ctx.fillStyle = isOrigin || isDest || isHospital
        ? `${accent}20`
        : 'rgba(0,212,255,0.06)';
      ctx.shadowBlur = isHospital ? 12 : 0;
      ctx.shadowColor = accent;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Node ring
      ctx.beginPath();
      ctx.arc(cx, cy, 10, 0, Math.PI * 2);
      ctx.strokeStyle = accent;
      ctx.lineWidth = isOrigin || isDest || isHospital ? 2 : 1;
      ctx.stroke();

      // Node label
      ctx.fillStyle = isOrigin || isDest || isHospital ? accent : '#475569';
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(n, cx, cy + 23);
    });

    // ── Draw parked vehicle dots ──────────────────────────────────────────────
    if (!playing) {
      const vehicleIds = ['V001','V002','V003','V004','V005','V006','V007','V008','V009','V010',
                          'V0','V1','V2','V3','V4','V5'];
      // Count vehicles per node to offset overlapping dots
      const nodeVehicles: Record<string, string[]> = {};
      vehicleIds.forEach(vid => {
        const pos = VEHICLE_POSITIONS[vid];
        if (pos && NODE_POS[pos]) {
          if (!nodeVehicles[pos]) nodeVehicles[pos] = [];
          nodeVehicles[pos].push(vid);
        }
      });

      Object.entries(nodeVehicles).forEach(([node, vids]) => {
        const pos = NODE_POS[node];
        if (!pos) return;
        const { cx, cy } = gridXY(pos.x, pos.y);
        vids.forEach((vid, idx) => {
          const isBroken = brokenVehicles.has(vid);
          const angle = (idx / vids.length) * Math.PI * 2;
          const rx = cx + Math.cos(angle) * 18;
          const ry = cy + Math.sin(angle) * 18;
          ctx.beginPath();
          ctx.arc(rx, ry, 4, 0, Math.PI * 2);
          ctx.fillStyle = isBroken ? '#f43f5e' : VEHICLE_COLORS[idx % VEHICLE_COLORS.length];
          ctx.globalAlpha = isBroken ? 0.5 : 0.85;
          ctx.fill();
          ctx.globalAlpha = 1;
          if (isBroken) {
            ctx.font = '8px Inter';
            ctx.fillStyle = '#f43f5e';
            ctx.textAlign = 'center';
            ctx.fillText('✕', rx, ry + 3);
          }
        });
      });
    }

    // ── Draw request O→D faint arrows ─────────────────────────────────────────
    scenario.requests.forEach((req, i) => {
      const po = NODE_POS[req.origin];
      const pd = NODE_POS[req.destination];
      if (!po || !pd) return;
      const pa = gridXY(po.x, po.y);
      const pb = gridXY(pd.x, pd.y);
      const alpha = 0.15 + 0.1 * Math.sin(t / 800 + i);
      const priorityColor = req.priority === 1 ? '#f43f5e' : req.priority === 2 ? '#f59e0b' : '#10b981';

      ctx.globalAlpha = alpha;
      ctx.beginPath();
      ctx.moveTo(pa.cx, pa.cy);
      ctx.lineTo(pb.cx, pb.cy);
      ctx.strokeStyle = priorityColor;
      ctx.lineWidth = 1;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;

      // Origin dot marker
      ctx.beginPath();
      ctx.arc(pa.cx, pa.cy, 4, 0, Math.PI * 2);
      ctx.fillStyle = priorityColor;
      ctx.globalAlpha = 0.7;
      ctx.fill();
      ctx.globalAlpha = 1;
    });

    animRef.current = requestAnimationFrame(draw);
  }, [scenario, playing]);

  useEffect(() => {
    animRef.current = requestAnimationFrame(draw);
    return () => cancelAnimationFrame(animRef.current);
  }, [draw]);

  return (
    <canvas ref={canvasRef} width={460} height={460} style={{ display: 'block', maxWidth: '100%' }} />
  );
}
