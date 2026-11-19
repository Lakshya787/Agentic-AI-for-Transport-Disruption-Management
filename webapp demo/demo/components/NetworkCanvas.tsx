'use client';
import { useRef, useEffect, useCallback } from 'react';
import { Scenario, NODES, EDGES } from '@/lib/data';

interface Props { scenario: Scenario; playing: boolean; }

const NODE_POS: Record<string, { x: number; y: number }> = {};
['A','B','C','D'].forEach((r, ri) => {
  [0,1,2,3].forEach(ci => { NODE_POS[`${r}${ci}`] = { x: ci, y: ri }; });
});

const PAD = 55;
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

    // ── Build disruption sets from real data ──────────────────────────────
    const closedEdges    = new Set<string>();
    const congestedEdges = new Set<string>(); // key → congestion factor
    const congestFactor  = new Map<string, number>();
    const surgeNodes     = new Set<string>();

    scenario.disruptions.forEach(d => {
      if ((d.type === 'road_closure' || d.type === 'congestion') && d.edge) {
        const key = [...d.edge].sort().join('|');
        if (d.type === 'road_closure') closedEdges.add(key);
        else {
          congestedEdges.add(key);
          congestFactor.set(key, d.congestionFactor ?? 1);
        }
      }
      if (d.type === 'demand_surge' && d.surgeNodes) {
        d.surgeNodes.forEach(n => surgeNodes.add(n));
      }
    });

    // ── Draw edges ────────────────────────────────────────────────────────
    EDGES.forEach(([a, b]) => {
      const key = [a, b].sort().join('|');
      const pa = gridXY(NODE_POS[a].x, NODE_POS[a].y);
      const pb = gridXY(NODE_POS[b].x, NODE_POS[b].y);

      ctx.beginPath();
      ctx.moveTo(pa.cx, pa.cy);
      ctx.lineTo(pb.cx, pb.cy);

      if (closedEdges.has(key)) {
        ctx.strokeStyle = '#f43f5e';
        ctx.lineWidth   = 3;
        ctx.setLineDash([8, 6]);
        ctx.globalAlpha = 0.9;
      } else if (congestedEdges.has(key)) {
        const factor = congestFactor.get(key) ?? 1;
        // brighter amber for higher congestion factor
        ctx.strokeStyle = factor >= 4 ? '#ef4444' : '#f59e0b';
        ctx.lineWidth   = 2.5;
        ctx.setLineDash([]);
        ctx.globalAlpha = 0.85;
      } else {
        ctx.strokeStyle = 'rgba(0,212,255,0.2)';
        ctx.lineWidth   = 1.5;
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
      }
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.globalAlpha = 1;
    });

    // ── Draw route paths (if playing) ─────────────────────────────────────
    if (playing) {
      const dispatched = scenario.requests;
      dispatched.forEach((req, i) => {
        const pa = gridXY(NODE_POS[req.origin]?.x ?? 0, NODE_POS[req.origin]?.y ?? 0);
        const pb = gridXY(NODE_POS[req.destination]?.x ?? 0, NODE_POS[req.destination]?.y ?? 0);
        const progress = ((t / 2400 + i * 0.22) % 1);
        const vx = pa.cx + (pb.cx - pa.cx) * progress;
        const vy = pa.cy + (pb.cy - pa.cy) * progress;
        ctx.beginPath();
        ctx.arc(vx, vy, 5, 0, Math.PI * 2);
        ctx.fillStyle = '#00d4ff';
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#00d4ff';
        ctx.fill();
        ctx.shadowBlur = 0;
      });
    }

    // ── Draw nodes ────────────────────────────────────────────────────────
    NODES.forEach(n => {
      const { cx, cy } = gridXY(NODE_POS[n].x, NODE_POS[n].y);
      const isSurge = surgeNodes.has(n);

      // Surge pulse ring
      if (isSurge) {
        const pulse = 0.5 + 0.5 * Math.sin(t / 400);
        ctx.beginPath();
        ctx.arc(cx, cy, 18 + pulse * 6, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(0,212,255,0.35)';
        ctx.lineWidth = 1;
        ctx.stroke();
      }

      // Node fill
      ctx.beginPath();
      ctx.arc(cx, cy, 10, 0, Math.PI * 2);
      if (isSurge) {
        ctx.fillStyle = 'rgba(0,212,255,0.25)';
        ctx.shadowBlur = 14; ctx.shadowColor = '#00d4ff';
      } else {
        ctx.fillStyle = 'rgba(0,212,255,0.08)';
        ctx.shadowBlur = 0;
      }
      ctx.fill();
      ctx.shadowBlur = 0;

      // Node ring
      ctx.beginPath();
      ctx.arc(cx, cy, 10, 0, Math.PI * 2);
      ctx.strokeStyle = isSurge ? '#00d4ff' : 'rgba(0,212,255,0.4)';
      ctx.lineWidth = isSurge ? 2 : 1;
      ctx.stroke();

      // Label
      ctx.fillStyle = '#64748b';
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(n, cx, cy + 23);
    });

    // ── Draw broken-down vehicle markers ──────────────────────────────────
    // vehicle_breakdown disruptions don't have a node position in the data,
    // so we show a legend-style marker in the info panel (see simulator page).
    // We do draw a small warning on any surge node.

    // ── Draw request O→D arrows ───────────────────────────────────────────
    scenario.requests.forEach((req, i) => {
      const po = NODE_POS[req.origin];
      const pd = NODE_POS[req.destination];
      if (!po || !pd) return;
      const pa = gridXY(po.x, po.y);
      const pb = gridXY(pd.x, pd.y);
      const alpha = 0.2 + 0.12 * Math.sin(t / 700 + i);
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

      // Origin dot
      ctx.beginPath();
      ctx.arc(pa.cx, pa.cy, 4, 0, Math.PI * 2);
      ctx.fillStyle = priorityColor;
      ctx.globalAlpha = 0.6;
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
