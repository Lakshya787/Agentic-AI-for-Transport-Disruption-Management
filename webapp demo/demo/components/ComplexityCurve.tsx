'use client';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, LineElement, PointElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { Metrics } from '@/lib/data';

ChartJS.register(CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend, Filler);

interface Props {
  b1: Record<string, Metrics>;
  b2: Record<string, Metrics>;
  b3: Record<string, Metrics>;
}

export default function ComplexityCurve({ b1, b2, b3 }: Props) {
  const labels = ['L1', 'L2', 'L3', 'L4', 'L5'];

  const data = {
    labels,
    datasets: [
      {
        label: 'B1 Rule-Based',
        data: labels.map(s => b1[s]?.rfr ?? 0),
        borderColor: '#00d4ff',
        backgroundColor: 'rgba(0,212,255,0.08)',
        borderWidth: 2,
        pointBackgroundColor: '#00d4ff',
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'B2 Single-LLM ⟨Projected⟩',
        data: labels.map(s => b2[s]?.rfr ?? 0),
        borderColor: '#f59e0b',
        backgroundColor: 'rgba(245,158,11,0.06)',
        borderWidth: 2,
        borderDash: [6, 3],
        pointBackgroundColor: '#f59e0b',
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.4,
      },
      {
        label: 'B3 Multi-Agent ⟨Projected⟩',
        data: labels.map(s => b3[s]?.rfr ?? 0),
        borderColor: '#8b5cf6',
        backgroundColor: 'rgba(139,92,246,0.08)',
        borderWidth: 2,
        borderDash: [6, 3],
        pointBackgroundColor: '#8b5cf6',
        pointRadius: 5,
        pointHoverRadius: 7,
        fill: true,
        tension: 0.4,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#94a3b8',
          font: { family: 'Inter', size: 12 },
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(2,8,23,0.9)',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        titleColor: '#f1f5f9',
        bodyColor: '#94a3b8',
        padding: 12,
        callbacks: {
          label: (ctx: any) =>
            ` ${ctx.dataset?.label ?? ''}: ${ctx.parsed?.y ?? 0}% RFR`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 12 } },
        border: { color: 'rgba(255,255,255,0.06)' },
        title: { display: true, text: 'Scenario Complexity', color: '#475569', font: { family: 'Inter', size: 11 } },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 12 }, callback: (v: number | string) => `${v}%` },
        border: { color: 'rgba(255,255,255,0.06)' },
        min: 40, max: 100,
        title: { display: true, text: 'RFR (%)', color: '#475569', font: { family: 'Inter', size: 11 } },
      },
    },
  };

  return (
    <div style={{ height: 260 }}>
      <Line data={data} options={options} />
    </div>
  );
}
