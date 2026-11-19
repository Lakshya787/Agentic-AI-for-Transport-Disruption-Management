import type { Metadata } from 'next';
import './globals.css';
import NavBar from '@/components/NavBar';

export const metadata: Metadata = {
  title: 'Agentic AI for Transport Disruption Management',
  description: 'Interactive research demo: Multi-agent LLM system vs rule-based baselines for transport disruption management. Explore network simulation, benchmark results, and agent architecture.',
  keywords: ['multi-agent AI', 'transport disruption', 'LLM routing', 'agentic systems', 'research demo'],
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>
        <NavBar />
        <main style={{ position: 'relative', zIndex: 1 }}>
          {children}
        </main>
      </body>
    </html>
  );
}
