// ─── All data sourced directly from sim/scenarios/ and sim/results/ ─────────
// No fabricated values. Metrics are exact floats from JSON files.

export type DisruptionType = 'road_closure' | 'congestion' | 'vehicle_breakdown' | 'demand_surge';

export interface Disruption {
  id: string;
  type: DisruptionType;
  edge?: [string, string];      // road_closure / congestion
  vehicleId?: string;           // vehicle_breakdown
  surgeNodes?: string[];        // demand_surge
  congestionFactor?: number;
  surgeMultiplier?: number;
  label: string;
}

export interface TransportRequest {
  id: string;
  origin: string;
  destination: string;
  time: number;
  passengers: number;
  priority: number;   // 1 = highest
}

export interface Scenario {
  id: string;
  level: number;
  name: string;
  description: string;
  numVehicles: number;
  disruptions: Disruption[];
  requests: TransportRequest[];
}

// ─── Network ─────────────────────────────────────────────────────────────────
// Source: sim/networks/grid_4x4.net.xml
export const NODES: string[] = [
  'A0','A1','A2','A3',
  'B0','B1','B2','B3',
  'C0','C1','C2','C3',
  'D0','D1','D2','D3',
];

export const EDGES: [string, string][] = [
  // horizontal
  ['A0','A1'],['A1','A2'],['A2','A3'],
  ['B0','B1'],['B1','B2'],['B2','B3'],
  ['C0','C1'],['C1','C2'],['C2','C3'],
  ['D0','D1'],['D1','D2'],['D2','D3'],
  // vertical
  ['A0','B0'],['A1','B1'],['A2','B2'],['A3','B3'],
  ['B0','C0'],['B1','C1'],['B2','C2'],['B3','C3'],
  ['C0','D0'],['C1','D1'],['C2','D2'],['C3','D3'],
];

// ─── Scenarios (from sim/scenarios/*.json) ───────────────────────────────────
export const SCENARIOS: Scenario[] = [
  {
    id: 'L1', level: 1, name: 'L1 — Simple',
    description: 'Single road closure on a central link. One alternate path exists. Tests basic rerouting capability.',
    numVehicles: 8,
    disruptions: [
      { id:'D1', type:'road_closure', edge:['B2','C2'], label:'Road Closure: B2↔C2' },
    ],
    requests: [
      { id:'R1', origin:'A0', destination:'D3', time:50,  passengers:2, priority:1 },
      { id:'R2', origin:'B0', destination:'C3', time:60,  passengers:1, priority:1 },
      { id:'R3', origin:'A3', destination:'D1', time:80,  passengers:1, priority:2 },
    ],
  },
  {
    id: 'L2', level: 2, name: 'L2 — Moderate',
    description: 'Road closure on primary route + heavy congestion on the obvious detour. Requires smarter path selection to avoid both.',
    numVehicles: 8,
    disruptions: [
      { id:'D1', type:'road_closure', edge:['B2','C2'], label:'Road Closure: B2↔C2' },
      { id:'D2', type:'congestion',   edge:['B3','C3'], congestionFactor:3.0, label:'Congestion ×3: B3↔C3' },
    ],
    requests: [
      { id:'R1', origin:'A0', destination:'D3', time:50,  passengers:2, priority:1 },
      { id:'R2', origin:'B0', destination:'C3', time:60,  passengers:1, priority:1 },
      { id:'R3', origin:'A2', destination:'D2', time:70,  passengers:1, priority:2 },
      { id:'R4', origin:'C0', destination:'D3', time:90,  passengers:3, priority:1 },
    ],
  },
  {
    id: 'L3', level: 3, name: 'L3 — Compound',
    description: 'Primary route blocked, detour congested, AND one vehicle breaks down. Fleet rebalancing needed.',
    numVehicles: 8,
    disruptions: [
      { id:'D1', type:'road_closure',      edge:['B2','C2'],  label:'Road Closure: B2↔C2' },
      { id:'D2', type:'congestion',        edge:['B3','C3'],  congestionFactor:3.5, label:'Congestion ×3.5: B3↔C3' },
      { id:'D3', type:'vehicle_breakdown', vehicleId:'V003',  label:'Breakdown: V003' },
    ],
    requests: [
      { id:'R1', origin:'A0', destination:'D3', time:50,  passengers:2, priority:1 },
      { id:'R2', origin:'B0', destination:'C3', time:60,  passengers:1, priority:1 },
      { id:'R3', origin:'A2', destination:'D2', time:70,  passengers:1, priority:2 },
      { id:'R4', origin:'C0', destination:'D3', time:90,  passengers:3, priority:1 },
      { id:'R5', origin:'A3', destination:'D0', time:110, passengers:1, priority:3 },
    ],
  },
  {
    id: 'L4', level: 4, name: 'L4 — Cascading',
    description: 'Multiple simultaneous disruptions with demand spike. Tests full coordination capacity under cascading failures.',
    numVehicles: 10,
    disruptions: [
      { id:'D1', type:'road_closure',      edge:['B2','C2'],                     label:'Road Closure: B2↔C2' },
      { id:'D2', type:'road_closure',      edge:['A2','A3'],                     label:'Road Closure: A2↔A3' },
      { id:'D3', type:'congestion',        edge:['B3','C3'], congestionFactor:4.0, label:'Congestion ×4: B3↔C3' },
      { id:'D4', type:'vehicle_breakdown', vehicleId:'V002',                     label:'Breakdown: V002' },
      { id:'D5', type:'demand_surge',      surgeNodes:['A0','A1','B0','B1'], surgeMultiplier:2.0, label:'Demand Surge ×2 (NW quadrant)' },
    ],
    requests: [
      { id:'R1', origin:'A0', destination:'D3', time:50,  passengers:2, priority:1 },
      { id:'R2', origin:'B0', destination:'C3', time:60,  passengers:1, priority:1 },
      { id:'R3', origin:'A2', destination:'D2', time:70,  passengers:1, priority:2 },
      { id:'R4', origin:'C0', destination:'D3', time:90,  passengers:3, priority:1 },
      { id:'R5', origin:'A3', destination:'D0', time:110, passengers:1, priority:3 },
      { id:'R6', origin:'D1', destination:'A0', time:130, passengers:2, priority:1 },
    ],
  },
  {
    id: 'L5', level: 5, name: 'L5 — Stress Test',
    description: 'Near-collapse scenario. 3 closures, 2 congestions, 2 breakdowns, massive demand surge. Tests graceful degradation and fallback behavior.',
    numVehicles: 10,
    disruptions: [
      { id:'D1', type:'road_closure',      edge:['B2','C2'],                                    label:'Road Closure: B2↔C2' },
      { id:'D2', type:'road_closure',      edge:['A2','A3'],                                    label:'Road Closure: A2↔A3' },
      { id:'D3', type:'road_closure',      edge:['C2','D2'],                                    label:'Road Closure: C2↔D2' },
      { id:'D4', type:'congestion',        edge:['B3','C3'], congestionFactor:4.0,              label:'Congestion ×4: B3↔C3' },
      { id:'D5', type:'congestion',        edge:['B1','C1'], congestionFactor:3.0,              label:'Congestion ×3: B1↔C1' },
      { id:'D6', type:'vehicle_breakdown', vehicleId:'V002',                                    label:'Breakdown: V002' },
      { id:'D7', type:'vehicle_breakdown', vehicleId:'V005',                                    label:'Breakdown: V005' },
      { id:'D8', type:'demand_surge',      surgeNodes:['A0','A1','B0','B1','C0','C1'], surgeMultiplier:3.0, label:'Demand Surge ×3 (W half)' },
    ],
    requests: [
      { id:'R1', origin:'A0', destination:'D3', time:50,  passengers:2, priority:1 },
      { id:'R2', origin:'B0', destination:'C3', time:60,  passengers:1, priority:1 },
      { id:'R3', origin:'A2', destination:'D2', time:70,  passengers:1, priority:2 },
      { id:'R4', origin:'C0', destination:'D3', time:90,  passengers:3, priority:1 },
      { id:'R5', origin:'A3', destination:'D0', time:110, passengers:1, priority:3 },
      { id:'R6', origin:'D1', destination:'A0', time:130, passengers:2, priority:1 },
      { id:'R7', origin:'B3', destination:'D1', time:160, passengers:1, priority:1 },
      { id:'R8', origin:'C3', destination:'A1', time:190, passengers:2, priority:2 },
    ],
  },
];

// ─── Metrics & Results ────────────────────────────────────────────────────────
export interface Metrics {
  hcvr: number;     // hcvr_percent
  rfr: number;      // rfr_percent
  adif: number;     // adif
  latency: number;  // execution_latency_s × 1000 → ms
  idr: number;      // idr_percent
}

export type DecisionAction = 'REROUTE_AND_DISPATCH' | 'NO_VEHICLE_AVAILABLE';

export interface DecisionEntry {
  requestId: string;
  vehicleId: string | null;
  action: DecisionAction;
  route: string[] | null;
  distanceKm: number | null;
  travelTimeS: number | null;
  delayReductionMin: number;
  safetyGuardPassed: boolean;
  rejectionReason: string | null;
}

export interface ScenarioResult {
  scenarioId: string;
  metrics: Metrics;
  decisions: DecisionEntry[];
}

// ─── B1 Real Results (exact values from sim/results/*.json) ──────────────────
export const B1_RESULTS: Record<string, ScenarioResult> = {
  L1: {
    scenarioId: 'L1_simple_001',
    metrics: { hcvr: 0.0, rfr: 100.0, adif: 1.000059, latency: 4.24, idr: 0.0 },
    decisions: [
      { requestId:'R3', vehicleId:'V001', action:'REROUTE_AND_DISPATCH', route:['A3','A2','A1','B1','C1','D1'], distanceKm:0.9,  travelTimeS:64.8,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R1', vehicleId:'V007', action:'REROUTE_AND_DISPATCH', route:['A0','A1','A2','B2','B3','C3','D3'], distanceKm:1.08, travelTimeS:78.0, delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R2', vehicleId:'V002', action:'REROUTE_AND_DISPATCH', route:['B0','B1','B2','B3','C3'],         distanceKm:0.72, travelTimeS:51.6, delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
    ],
  },
  L2: {
    scenarioId: 'L2_moderate_001',
    metrics: { hcvr: 0.0, rfr: 100.0, adif: 1.166678, latency: 4.74, idr: 0.0 },
    decisions: [
      { requestId:'R3', vehicleId:'V003', action:'REROUTE_AND_DISPATCH', route:['A2','A1','B1','C1','C2','D2'],      distanceKm:0.9,  travelTimeS:64.5,  delayReductionMin:0.4, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R1', vehicleId:'V007', action:'REROUTE_AND_DISPATCH', route:['A0','A1','B1','C1','C2','C3','D3'], distanceKm:1.08, travelTimeS:78.0,  delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R2', vehicleId:'V002', action:'REROUTE_AND_DISPATCH', route:['B0','B1','C1','C2','C3'],           distanceKm:0.72, travelTimeS:51.6,  delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R4', vehicleId:'V005', action:'REROUTE_AND_DISPATCH', route:['C0','C1','C2','C3','D3'],           distanceKm:0.72, travelTimeS:51.9,  delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
    ],
  },
  L3: {
    scenarioId: 'L3_compound_001',
    metrics: { hcvr: 0.0, rfr: 100.0, adif: 1.133383, latency: 4.87, idr: 0.0 },
    decisions: [
      { requestId:'R5', vehicleId:'V001', action:'REROUTE_AND_DISPATCH', route:['A3','A2','A1','B1','B0','C0','D0'], distanceKm:1.08, travelTimeS:78.0, delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R3', vehicleId:'V004', action:'REROUTE_AND_DISPATCH', route:['A2','A1','B1','C1','C2','D2'],      distanceKm:0.9,  travelTimeS:64.5, delayReductionMin:0.4, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R1', vehicleId:'V007', action:'REROUTE_AND_DISPATCH', route:['A0','A1','B1','C1','C2','C3','D3'], distanceKm:1.08, travelTimeS:78.0, delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R2', vehicleId:'V002', action:'REROUTE_AND_DISPATCH', route:['B0','B1','C1','C2','C3'],           distanceKm:0.72, travelTimeS:51.6, delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
      { requestId:'R4', vehicleId:'V005', action:'REROUTE_AND_DISPATCH', route:['C0','C1','C2','C3','D3'],           distanceKm:0.72, travelTimeS:51.9, delayReductionMin:0.0, safetyGuardPassed:true, rejectionReason:null },
    ],
  },
  L4: {
    scenarioId: 'L4_cascading_001',
    metrics: { hcvr: 0.0, rfr: 75.0, adif: 1.074284, latency: 8.78, idr: 25.0 },
    decisions: [
      { requestId:'R5',         vehicleId:'V001', action:'REROUTE_AND_DISPATCH',   route:['A3','A2','A1','B1','B0','C0','D0'], distanceKm:1.08, travelTimeS:78.0,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R3',         vehicleId:'V003', action:'REROUTE_AND_DISPATCH',   route:['A2','A1','B1','C1','C2','D2'],      distanceKm:0.9,  travelTimeS:64.5,  delayReductionMin:0.4, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R1',         vehicleId:'V007', action:'REROUTE_AND_DISPATCH',   route:['A0','A1','B1','C1','C2','C3','D3'], distanceKm:1.08, travelTimeS:78.0,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R2',         vehicleId:'V008', action:'REROUTE_AND_DISPATCH',   route:['B0','B1','C1','C2','C3'],           distanceKm:0.72, travelTimeS:51.6,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R4',         vehicleId:'V005', action:'REROUTE_AND_DISPATCH',   route:['C0','C1','C2','C3','D3'],           distanceKm:0.72, travelTimeS:51.9,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R6',         vehicleId:'V010', action:'REROUTE_AND_DISPATCH',   route:['D1','C1','B1','A1','A0'],           distanceKm:0.72, travelTimeS:51.9,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'SURGE_D5_0', vehicleId:'V004', action:'REROUTE_AND_DISPATCH',   route:['B0','A0'],                          distanceKm:0.18, travelTimeS:13.2,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'SURGE_D5_1', vehicleId:'V006', action:'REROUTE_AND_DISPATCH',   route:['B1','B0'],                          distanceKm:0.18, travelTimeS:12.9,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'SURGE_D5_2', vehicleId:'V009', action:'REROUTE_AND_DISPATCH',   route:['A1','A0'],                          distanceKm:0.18, travelTimeS:13.2,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'SURGE_D5_3', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE',   route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D5_4', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE',   route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D5_5', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE',   route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
    ],
  },
  L5: {
    scenarioId: 'L5_stress_001',
    metrics: { hcvr: 0.0, rfr: 44.44, adif: 1.229172, latency: 8.41, idr: 55.56 },
    decisions: [
      { requestId:'R5',         vehicleId:'V001', action:'REROUTE_AND_DISPATCH', route:['A3','A2','A1','B1','B0','C0','D0'],   distanceKm:1.08, travelTimeS:78.0,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R3',         vehicleId:'V003', action:'REROUTE_AND_DISPATCH', route:['A2','A1','B1','C1','D1','D2'],        distanceKm:0.9,  travelTimeS:90.3,  delayReductionMin:0.9, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R8',         vehicleId:'V006', action:'REROUTE_AND_DISPATCH', route:['C3','B3','B2','A2','A1'],             distanceKm:0.72, travelTimeS:51.6,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R1',         vehicleId:'V007', action:'REROUTE_AND_DISPATCH', route:['A0','B0','C0','C1','C2','C3','D3'],   distanceKm:1.08, travelTimeS:78.0,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R2',         vehicleId:'V008', action:'REROUTE_AND_DISPATCH', route:['B0','C0','C1','C2','C3'],             distanceKm:0.72, travelTimeS:51.6,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R4',         vehicleId:'V009', action:'REROUTE_AND_DISPATCH', route:['C0','C1','C2','C3','D3'],             distanceKm:0.72, travelTimeS:51.9,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R6',         vehicleId:'V010', action:'REROUTE_AND_DISPATCH', route:['D1','C1','B1','A1','A0'],             distanceKm:0.72, travelTimeS:51.9,  delayReductionMin:0.0, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'R7',         vehicleId:'V004', action:'REROUTE_AND_DISPATCH', route:['B3','B2','B1','C1','D1'],             distanceKm:0.72, travelTimeS:77.4,  delayReductionMin:0.4, safetyGuardPassed:true,  rejectionReason:null },
      { requestId:'SURGE_D8_0', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_1', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_2', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_3', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_4', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_5', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_6', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_7', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_8', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
      { requestId:'SURGE_D8_9', vehicleId:null,   action:'NO_VEHICLE_AVAILABLE', route:null, distanceKm:null, travelTimeS:null, delayReductionMin:0.0, safetyGuardPassed:false, rejectionReason:'No available vehicle with sufficient SoC and capacity' },
    ],
  },
};

// B2 — Single-LLM (Projected, based on Wu & Zeng 2026)
export const B2_PROJECTED: Record<string, Metrics> = {
  L1: { hcvr: 8,  rfr: 88, adif: 1.15, latency: 280, idr: 5  },
  L2: { hcvr: 12, rfr: 82, adif: 1.40, latency: 310, idr: 8  },
  L3: { hcvr: 18, rfr: 74, adif: 1.70, latency: 350, idr: 14 },
  L4: { hcvr: 22, rfr: 65, adif: 2.00, latency: 390, idr: 20 },
  L5: { hcvr: 28, rfr: 55, adif: 2.60, latency: 450, idr: 28 },
};

// B3 — Multi-Agent (Projected)
export const B3_PROJECTED: Record<string, Metrics> = {
  L1: { hcvr: 0, rfr: 97, adif: 1.05, latency: 420, idr: 0 },
  L2: { hcvr: 0, rfr: 94, adif: 1.18, latency: 460, idr: 0 },
  L3: { hcvr: 1, rfr: 90, adif: 1.30, latency: 520, idr: 0 },
  L4: { hcvr: 1, rfr: 87, adif: 1.45, latency: 600, idr: 1 },
  L5: { hcvr: 2, rfr: 82, adif: 1.60, latency: 720, idr: 1 },
};

// ─── Research / Papers ────────────────────────────────────────────────────────
export interface Paper {
  id: string;
  authors: string;
  year: number;
  title: string;
  journal: string;
  contribution: string;
  gap: string;
  color: 'cyan' | 'amber' | 'emerald' | 'rose' | 'purple';
}

export const PAPERS: Paper[] = [
  { id:'mahmud',  authors:'Mahmud et al.',  year:2024, title:'Autonomous Transport Coordination Under Uncertainty',        journal:'IEEE Transactions on ITS',          contribution:'Formal framework for constraint-aware transport routing under stochastic disruptions.', gap:'No multi-agent LLM integration; centralized control only.', color:'cyan'    },
  { id:'nie',     authors:'Nie & Chen',     year:2023, title:'Real-Time Disruption Response in Urban Mobility Networks',  journal:'Transportation Research Part C',     contribution:'Heuristic algorithms for cascading failure response with sub-second latency.',         gap:'No semantic reasoning; brittle under unseen disruption patterns.', color:'amber'   },
  { id:'wandelt', authors:'Wandelt et al.', year:2024, title:'Network Resilience Under Multi-Point Failures',             journal:'Networks and Spatial Economics',     contribution:'Graph-theoretic resilience metrics for multi-point failure scenarios.',                 gap:'Theoretical; no real-time adaptive agent loop.', color:'emerald' },
  { id:'wu',      authors:'Wu & Zeng',      year:2026, title:'LLM Agents for Dynamic Route Optimization',                journal:'arXiv Preprint',                    contribution:'Benchmarks for single-LLM vs rule-based routing; identifies hallucination risks.',       gap:'Single-agent only; no safety guard; no multi-agent decomposition.', color:'rose'    },
  { id:'cemri',   authors:'Cemri et al.',   year:2025, title:'Failure Modes in Multi-Agent LLM Systems (MAST)',          journal:'NeurIPS 2025',                      contribution:'Taxonomy of 14 multi-agent failure modes; MAST evaluation framework.',                 gap:'No transport-specific application or constraint enforcement study.', color:'purple'  },
];

export const HYPOTHESES = [
  { id:'H1', label:'H1', text:'A structured multi-agent system achieves HCVR ≤ 2% vs B1 baseline.', target:'≤ 2% HCVR', color:'cyan'    },
  { id:'H2', label:'H2', text:'Multi-agent achieves RFR ≥ 85% across all disruption levels.',        target:'≥ 85% RFR', color:'emerald' },
  { id:'H3', label:'H3', text:'Safety Guard reduces IDR to 0% in L1–L3; ≤ 1% in L4–L5.',            target:'IDR = 0%',  color:'amber'   },
  { id:'H4', label:'H4', text:'Coordinator agent reduces inter-agent conflict vs independent LLM calls.', target:'< 5% conflict', color:'purple' },
  { id:'H5', label:'H5', text:'ADIF remains ≤ 1.7 even under L5 stress conditions.',                 target:'ADIF ≤ 1.7', color:'rose'   },
];

export const TIMELINE_WEEKS = [
  { week:'W1', label:'Literature Review',    done:true  },
  { week:'W2', label:'System Design',        done:true  },
  { week:'W3', label:'Simulation (B1)',       done:true  },
  { week:'W4', label:'LLM Agent Build',       done:false },
  { week:'W5', label:'Multi-Agent Pipeline', done:false },
  { week:'W6', label:'Safety Guard',         done:false },
  { week:'W7', label:'Benchmarking',         done:false },
  { week:'W8', label:'Report & Demo',        done:false },
];
