'use client';
import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement, LineElement, PointElement,
  Title, Tooltip, Legend, Filler,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { Metrics } from '@/lib/data';

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Title, Tooltip, Legend, Filler);

type MetricKey = keyof Metrics;

interface Props {
  b1: Record<string, Metrics>;
  b2: Record<string, Metrics>;
  b3: Record<string, Metrics>;
  selectedMetric: MetricKey;
  selectedScenario: string;
}

const METRIC_LABELS: Record<MetricKey, string> = {
  hcvr: 'HCVR (%)',
  rfr: 'RFR (%)',
  adif: 'ADIF',
  latency: 'Latency (ms)',
  idr: 'IDR (%)',
};

export default function ComparisonChart({ b1, b2, b3, selectedMetric, selectedScenario }: Props) {
  const scenarios = ['L1', 'L2', 'L3', 'L4', 'L5'];

  const data = {
    labels: scenarios,
    datasets: [
      {
        label: 'B1 Rule-Based',
        data: scenarios.map(s => b1[s]?.[selectedMetric] ?? 0),
        backgroundColor: 'rgba(0,212,255,0.25)',
        borderColor: '#00d4ff',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      },
      {
        label: 'B2 Single-LLM ⟨Projected⟩',
        data: scenarios.map(s => b2[s]?.[selectedMetric] ?? 0),
        backgroundColor: 'rgba(245,158,11,0.25)',
        borderColor: '#f59e0b',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
      },
      {
        label: 'B3 Multi-Agent ⟨Projected⟩',
        data: scenarios.map(s => b3[s]?.[selectedMetric] ?? 0),
        backgroundColor: 'rgba(139,92,246,0.25)',
        borderColor: '#8b5cf6',
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false,
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
          padding: 20,
          usePointStyle: true,
          pointStyleWidth: 10,
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
          label: (ctx: { dataset: { label: string }; parsed: { y: number } }) =>
            ` ${ctx.dataset.label}: ${ctx.parsed.y}${selectedMetric === 'adif' ? '' : selectedMetric === 'latency' ? ' ms' : '%'}`,
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 12 } },
        border: { color: 'rgba(255,255,255,0.06)' },
      },
      y: {
        grid: { color: 'rgba(255,255,255,0.04)' },
        ticks: { color: '#64748b', font: { family: 'Inter', size: 12 } },
        border: { color: 'rgba(255,255,255,0.06)' },
        title: {
          display: true,
          text: METRIC_LABELS[selectedMetric],
          color: '#475569',
          font: { family: 'Inter', size: 11 },
        },
      },
    },
  };

  return (
    <div style={{ height: 300 }}>
      <Bar data={data} options={options} />
    </div>
  );
}
