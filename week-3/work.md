# Week 3: Building the Transport Simulation Environment
## Agentic AI for Transport Disruption Management
**Date:** September 9, 2026 | **Status:** Phase 2 — Environment Implementation  
**Prerequisite:** Week 2 Research Gap & Experimental Design (Approved)  
**Goal:** Build a fully functional, LLM-ready transport simulation environment before any LLM code is written.

---

## Table of Contents
1. [Simulator Evaluation — All 6 Options Assessed](#1-simulator-evaluation--all-6-options-assessed)
2. [Final Recommendation: Eclipse SUMO](#2-final-recommendation-eclipse-sumo)
3. [Environment Setup & Installation](#3-environment-setup--installation)
4. [Task 1: Road Network Creation](#4-task-1-road-network-creation)
5. [Task 2: Vehicle Fleet Model](#5-task-2-vehicle-fleet-model)
6. [Task 3: Transport Request System](#6-task-3-transport-request-system)
7. [Task 4: Disruption Injection Mechanisms](#7-task-4-disruption-injection-mechanisms)
8. [Task 5: Reproducible Scenario JSON Files (L1–L5)](#8-task-5-reproducible-scenario-json-files-l1l5)
9. [Task 6: Seven Core Tool Functions](#9-task-6-seven-core-tool-functions)
10. [Task 7: Rule-Based Baseline (B1)](#10-task-7-rule-based-baseline-b1)
11. [Task 8: Auto-Calculated Metrics](#11-task-8-auto-calculated-metrics)
12. [Project File Structure](#12-project-file-structure)
13. [Verification Checklist](#13-verification-checklist)

---

## 1. Simulator Evaluation — All 6 Options Assessed

Dr. Daoud and Dr. Srinivasa suggested evaluating: **RinSim, MATSim + SUMO, AnyLogic, RideGym, and Veins**. Below is a comprehensive comparison based on deep research of each tool.

### 1.1 Full Comparison Matrix

| Simulator | Language | Python API | Road Disruptions | Fleet Mgmt | LLM Integration | Open Source | Maintenance | Learning Curve | **Verdict** |
|-----------|----------|-----------|-----------------|-----------|----------------|-------------|------------|----------------|-------------|
| **Eclipse SUMO** | C++ | ✅ **10/10** (`traci` / `libsumo`) | ✅ Native (closures, congestion, accidents) | ✅ Taxi device + custom dispatch | ✅ **Ideal** (lock-step execution) | ✅ Eclipse Foundation | ✅ Active (v1.27.1, Jun 2026) | Moderate (3–5 days) | **✅ SELECTED** |
| **MATSim** | Java | ❌ **2/10** (post-processing only) | ⚠️ XML-based batch only | ✅ DRT module (Java) | ❌ No interactive Python loop | ✅ Open Source | ✅ Active (v2026.0) | Very Steep (3–5 weeks) | ❌ Wrong paradigm |
| **MATSim + SUMO** | Java + C++ | ⚠️ Mixed | ✅ Combined | ✅ Combined | ❌ Multi-language nightmare | ✅ Both open | ✅ Both active | Impractical (6–8+ weeks) | ❌ Overkill |
| **AnyLogic** | Java | ✅ **7.5/10** (Alpyne) | ✅ Native statecharts | ✅ GIS + agents | ✅ Good (via REST/Alpyne) | ❌ **Proprietary** (free PLE limited) | ✅ Active (v8.9+) | Moderate (1–2 weeks) | ⚠️ Viable but proprietary |
| **RinSim** | Java | ❌ **0/10** (none) | ❌ No built-in support | ✅ PDPTW dispatch | ❌ Extremely poor | ✅ Apache 2.0 | ❌ **Abandoned** (last release June 2018) | Severe | ❌ Dead project |
| **RideGym** | Python | ✅ **9/10** (native Gym) | ❌ **Static matrices only** | ✅ Ride-hail dispatch | ⚠️ Fair (dispatch only) | ✅ Open Source | ✅ New (Jul 2026) | Low | ❌ No disruption support |
| **Veins** | C++ / OMNeT++ | ❌ **1/10** | ⚠️ Via SUMO only | ❌ No fleet concept | ❌ Unusable | ✅ Open Source | ✅ Active | Very High | ❌ Wrong domain (V2X radio) |

### 1.2 Detailed Elimination Rationale

#### ❌ RinSim — ELIMINATED (Abandoned)
- Last release **v4.4.6 in June 2018** — 8 years unmaintained
- Zero Python bindings; requires custom PyJNIus/socket wrappers
- No built-in road disruption mechanisms (closures, congestion)
- Would waste 80%+ of project time debugging legacy Java 7/8 code
- Citing abandoned software in a 2026 paper hurts credibility

#### ❌ MATSim — ELIMINATED (Wrong Paradigm)
- **Batch iterative equilibrium simulator** — runs 50–100 full-day iterations to converge
- No native interactive Python runtime loop; controlling it requires JPype/gRPC Java bridges
- Within-day replanning exists but is deeply embedded in Java internals
- Perfect for city-wide demand modeling, but **wrong tool for step-by-step LLM agent interaction**

#### ❌ MATSim + SUMO Together — ELIMINATED (Overkill)
- Coupling introduces: network coordinate alignment, cross-boundary vehicle sync, multi-language debugging
- Would convert our LLM research project into an infrastructure plumbing project
- 6–8+ weeks just for the coupling — longer than our entire project timeline

#### ❌ RideGym — ELIMINATED (No Disruption Support)
- Uses **precomputed static shortest-path matrices** — cannot dynamically close roads
- Designed for ride-hailing dispatch optimization, not network-level disruption management
- Great for Uber/Lyft dispatch RL research, but architecturally incompatible with our disruption scenarios
- *Note:* Could be useful for a future sub-experiment on ride-hailing resilience

#### ❌ Veins — ELIMINATED (Wrong Domain)
- Simulates **vehicular radio communication** (802.11p / DSRC / 5G V2X), not transport operations
- Core value is electromagnetic propagation, packet loss, and channel contention
- No fleet dispatch, no passenger demand, no operational decision-support
- Unless our question is *"How does radio packet drop affect detour adoption?"* — irrelevant

#### ⚠️ AnyLogic — VIABLE BUT NOT SELECTED
- **Strong visual environment** with GIS maps, statecharts, and fleet animation
- Good Python connectivity via **Alpyne** (Gymnasium-style step/reset/action loop)
- **Problem:** Proprietary software. Free PLE has limits (10 agent types, 5-hour runtime, 50K agents)
- AI/ML venue reviewers (NeurIPS, AAAI) push back on proprietary tools for reproducibility
- **Verdict:** Would be excellent for a systems engineering thesis; risky for an AI research paper

---

## 2. Final Recommendation: Eclipse SUMO

### Why SUMO Wins Decisively

| Requirement | How SUMO Delivers |
|------------|-------------------|
| **Python API** | First-class `traci` (TCP client-server) and `libsumo` (10–20× faster in-process). Full read/write control over every simulation element. |
| **Lock-Step Execution** | Simulation clock advances ONLY when `traci.simulationStep()` is called. LLM agents can take 3–5 seconds to reason without simulation time drift. |
| **Dynamic Disruptions** | Native API: `traci.lane.setDisallowed()`, `traci.edge.adaptTraveltime()`, `traci.vehicle.slowDown()`, `traci.vehicle.setStop()` |
| **Fleet Management** | Built-in taxi device (`device.taxi`) with custom external dispatch via TraCI. Full control over vehicle spawn, routing, and state. |
| **NetworkX Integration** | `sumolib.net.readNet()` → NetworkX `DiGraph` conversion is straightforward. Enables BFS/Dijkstra safety verification on the same graph. |
| **Custom Networks** | `netgenerate` for synthetic grids/spider/random; `netconvert` for OpenStreetMap; `netedit` GUI for manual editing |
| **Reproducibility** | Deterministic with `--seed <int>`. All configs are text XML — fully version-controllable. |
| **Academic Standard** | Eclipse Foundation (100% open source). Dominant benchmark in LLM+traffic research (ChatSUMO, SUMO-RL, LLM digital twins). |
| **Installation** | `pip install eclipse-sumo` — bundles binaries, tools, and Python packages. |

### Architecture: SUMO as LLM Agent Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    LLM AGENT LAYER (Week 4+)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Rule-Based   │  │ Single-LLM   │  │ Multi-Agent LLM  │   │
│  │ Controller   │  │ Agent        │  │ (Traffic, Fleet,  │   │
│  │ (Baseline 1) │  │ (Baseline 2) │  │  Routing, Coord.) │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────────┘   │
│         │                 │                  │               │
│         └────────────┬────┴──────────────────┘               │
│                      │                                       │
│                      ▼                                       │
│  ┌───────────────────────────────────────────────────────┐   │
│  │          7 Core Tool Functions (Python API)           │   │
│  │  get_network_state() | get_vehicle_status()           │   │
│  │  get_disrupted_edges() | get_available_vehicles()     │   │
│  │  shortest_path() | assign_vehicle() | validate_plan() │   │
│  └──────────────────────┬────────────────────────────────┘   │
└──────────────────────────┼───────────────────────────────────┘
                           │ TraCI / libsumo API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Eclipse SUMO (v1.27.1)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Road Network │  │ Background   │  │ Taxi Fleet       │   │
│  │ (.net.xml)   │  │ Traffic      │  │ (device.taxi)    │   │
│  │              │  │ (.rou.xml)   │  │                  │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Disruption Injection (via TraCI at specific steps)  │   │
│  │  • Road Closure  • Congestion  • Breakdown  • Surge  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Environment Setup & Installation

### 3.1 Install SUMO

```bash
# Option A: pip install (recommended — bundles everything)
pip install eclipse-sumo

# Verify installation
sumo --version
# Expected: Eclipse SUMO sumo Version 1.27.1

# Set SUMO_HOME environment variable
export SUMO_HOME=$(python -c "import sumo; print(sumo.SUMO_HOME)")
echo "export SUMO_HOME=$SUMO_HOME" >> ~/.bashrc
```

```bash
# Option B: System package manager (Ubuntu/Debian)
sudo add-apt-repository ppa:sumo/stable
sudo apt-get update
sudo apt-get install sumo sumo-tools sumo-gui
```

### 3.2 Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install eclipse-sumo       # SUMO simulator + TraCI + sumolib
pip install networkx           # Graph algorithms (BFS, Dijkstra, etc.)
pip install pydantic           # JSON schema validation (DecisionCard)
pip install numpy pandas       # Data processing & metrics
pip install matplotlib         # Visualization & plots
pip install osmnx              # OpenStreetMap network extraction (Phase 2)
```

### 3.3 Verify TraCI Works

```python
# test_traci.py — Run this to verify your setup
import traci
import sumolib

print(f"TraCI version: {traci.constants.TRACI_VERSION}")
print(f"sumolib loaded successfully")
print("✅ SUMO + TraCI setup verified!")
```

---

## 4. Task 1: Road Network Creation

### 4.1 Phase 1: Synthetic Grid Network (Start Here)
Per Dr. Daoud's directive — start with a controlled 5–20 node synthetic graph, not full SUMO/OSMnx.

**Why start synthetic:**
- Controlled environment for debugging agent logic
- Fast iteration (no simulator overhead for initial development)
- Known graph properties (we can verify BFS/Dijkstra results by hand)
- Exact reproducibility

```bash
# Generate a 4×4 grid network (16 intersections, ~48 road segments)
netgenerate --grid \
  --grid.number=4 \
  --grid.length=200 \
  --grid.attach-length=0 \
  --default.lanenumber=2 \
  --default-junction-type priority \
  --output-file=networks/grid_4x4.net.xml \
  --seed 42
```

### 4.2 NetworkX Dual Representation
We maintain BOTH a SUMO network (for microscopic simulation) and a NetworkX graph (for agent reasoning & safety verification):

```python
# src/network/graph_builder.py

import sumolib
import networkx as nx
from typing import Dict, Tuple, Optional

class TransportNetwork:
    """Dual representation: SUMO network + NetworkX graph."""
    
    def __init__(self, net_file: str):
        self.net_file = net_file
        self.sumo_net = sumolib.net.readNet(net_file)
        self.graph = self._build_networkx_graph()
        self._base_capacities: Dict[str, float] = {}
        self._initialize_capacities()
    
    def _build_networkx_graph(self) -> nx.DiGraph:
        """Convert SUMO network to NetworkX DiGraph."""
        G = nx.DiGraph()
        
        for node in self.sumo_net.getNodes():
            x, y = node.getCoord()
            G.add_node(node.getID(), pos=(x, y), type=str(node.getType()))
        
        for edge in self.sumo_net.getEdges():
            if not edge.isSpecial():  # Skip internal junction edges
                G.add_edge(
                    edge.getFromNode().getID(),
                    edge.getToNode().getID(),
                    edge_id=edge.getID(),
                    length=edge.getLength(),
                    speed_limit=edge.getSpeed(),
                    lanes=edge.getLaneNumber(),
                    travel_time=edge.getLength() / edge.getSpeed(),
                    capacity=1.0,  # Normalized: 1.0 = full capacity
                    status="open"
                )
        return G
    
    def _initialize_capacities(self):
        """Store baseline edge capacities for disruption simulation."""
        for u, v, data in self.graph.edges(data=True):
            self._base_capacities[data['edge_id']] = data['capacity']
    
    def get_edge_by_nodes(self, from_node: str, to_node: str) -> Optional[dict]:
        """Get edge data between two nodes."""
        if self.graph.has_edge(from_node, to_node):
            return dict(self.graph[from_node][to_node])
        return None
    
    def close_edge(self, from_node: str, to_node: str):
        """Simulate road closure: set capacity to 0."""
        if self.graph.has_edge(from_node, to_node):
            self.graph[from_node][to_node]['capacity'] = 0.0
            self.graph[from_node][to_node]['status'] = "closed"
            self.graph[from_node][to_node]['travel_time'] = float('inf')
    
    def congest_edge(self, from_node: str, to_node: str, factor: float):
        """Simulate congestion: multiply travel time by factor."""
        if self.graph.has_edge(from_node, to_node):
            base_tt = self.graph[from_node][to_node]['length'] / self.graph[from_node][to_node]['speed_limit']
            self.graph[from_node][to_node]['travel_time'] = base_tt * factor
            self.graph[from_node][to_node]['capacity'] = max(0.1, 1.0 / factor)
            self.graph[from_node][to_node]['status'] = "congested"
    
    def restore_edge(self, from_node: str, to_node: str):
        """Restore edge to original capacity."""
        if self.graph.has_edge(from_node, to_node):
            edge_id = self.graph[from_node][to_node]['edge_id']
            self.graph[from_node][to_node]['capacity'] = self._base_capacities[edge_id]
            self.graph[from_node][to_node]['status'] = "open"
            self.graph[from_node][to_node]['travel_time'] = (
                self.graph[from_node][to_node]['length'] / 
                self.graph[from_node][to_node]['speed_limit']
            )
    
    def get_open_subgraph(self) -> nx.DiGraph:
        """Return subgraph containing only open/operational edges."""
        open_edges = [
            (u, v) for u, v, d in self.graph.edges(data=True)
            if d['capacity'] > 0
        ]
        return self.graph.edge_subgraph(open_edges).copy()
    
    def shortest_path(self, origin: str, destination: str, weight: str = 'travel_time') -> Optional[list]:
        """Find shortest path on the open subgraph."""
        open_graph = self.get_open_subgraph()
        try:
            return nx.shortest_path(open_graph, origin, destination, weight=weight)
        except nx.NetworkXNoPath:
            return None
    
    def bfs_reachable(self, origin: str, destination: str) -> bool:
        """BFS reachability check on open edges only (for Safety Guard)."""
        open_graph = self.get_open_subgraph()
        try:
            path = nx.shortest_path(open_graph, origin, destination)
            return True
        except nx.NetworkXNoPath:
            return False
    
    def to_json_state(self) -> dict:
        """Serialize network state for LLM context / scenario files."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            nodes.append({"id": node_id, "pos": data.get("pos", (0, 0))})
        
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append({
                "from": u, "to": v,
                "edge_id": data['edge_id'],
                "length": round(data['length'], 2),
                "speed_limit": round(data['speed_limit'], 2),
                "travel_time": round(data['travel_time'], 2),
                "capacity": round(data['capacity'], 2),
                "status": data['status'],
                "lanes": data['lanes']
            })
        
        return {"nodes": nodes, "edges": edges}
```

### 4.3 Phase 2: Real-World Network via OSMnx (Later)
```python
# For scaling up after synthetic validation (Week 5+)
import osmnx as ox

# Download a small city area (e.g., 1km radius around a point)
G = ox.graph_from_point((48.8566, 2.3522), dist=1000, network_type='drive')

# Export to SUMO format
ox.save_graph_xml(G, filepath='networks/paris_1km.osm')
# Then convert: netconvert --osm-files paris_1km.osm -o paris_1km.net.xml
```

---

## 5. Task 2: Vehicle Fleet Model

### 5.1 Vehicle Data Model

```python
# src/fleet/vehicle.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class VehicleStatus(str, Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    PICKUP = "pickup"
    DELIVERING = "delivering"
    BROKEN = "broken"
    CHARGING = "charging"

class Vehicle(BaseModel):
    """Single vehicle in the fleet."""
    id: str
    current_node: str                          # Current position (node ID)
    current_edge: Optional[str] = None         # Current edge (if mid-transit)
    capacity: int = 4                          # Max passenger capacity
    current_passengers: int = 0
    soc: float = Field(default=100.0, ge=0, le=100)  # State of Charge (%)
    soc_consumption_per_km: float = 2.0        # % SoC consumed per km
    status: VehicleStatus = VehicleStatus.IDLE
    assigned_request_id: Optional[str] = None
    route: Optional[List[str]] = None          # Planned route (list of node IDs)
    
    def can_reach(self, distance_km: float, safety_margin: float = 0.15) -> bool:
        """Check if vehicle has enough SoC to cover distance + 15% safety margin."""
        required_soc = distance_km * self.soc_consumption_per_km * (1 + safety_margin)
        return self.soc >= required_soc
    
    def remaining_range_km(self, safety_margin: float = 0.15) -> float:
        """Maximum distance vehicle can travel with safety margin."""
        return self.soc / (self.soc_consumption_per_km * (1 + safety_margin))
    
    def consume_soc(self, distance_km: float):
        """Consume SoC for a given distance."""
        self.soc = max(0, self.soc - distance_km * self.soc_consumption_per_km)


class Fleet(BaseModel):
    """Collection of vehicles."""
    vehicles: dict[str, Vehicle] = {}
    
    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles[vehicle.id] = vehicle
    
    def get_available_vehicles(self) -> list[Vehicle]:
        """Get all vehicles that are idle and operational."""
        return [v for v in self.vehicles.values() 
                if v.status == VehicleStatus.IDLE and v.soc > 10.0]
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        return self.vehicles.get(vehicle_id)
    
    def break_vehicle(self, vehicle_id: str):
        """Simulate vehicle breakdown."""
        if vehicle_id in self.vehicles:
            self.vehicles[vehicle_id].status = VehicleStatus.BROKEN
            self.vehicles[vehicle_id].assigned_request_id = None
            self.vehicles[vehicle_id].route = None
    
    def to_json_state(self) -> list[dict]:
        """Serialize fleet state for LLM context."""
        return [v.model_dump() for v in self.vehicles.values()]
```

### 5.2 Fleet Initialization (Default Test Fleet)

```python
# src/fleet/fleet_factory.py

from .vehicle import Vehicle, Fleet, VehicleStatus

def create_test_fleet(network_nodes: list[str], num_vehicles: int = 8, seed: int = 42) -> Fleet:
    """Create a test fleet distributed across the network."""
    import random
    rng = random.Random(seed)
    
    fleet = Fleet()
    for i in range(num_vehicles):
        vehicle = Vehicle(
            id=f"V{i+1:03d}",
            current_node=rng.choice(network_nodes),
            capacity=rng.choice([2, 4, 6]),        # Small, medium, large
            soc=rng.uniform(40.0, 100.0),           # 40-100% charge
            soc_consumption_per_km=rng.uniform(1.5, 3.0),
            status=VehicleStatus.IDLE
        )
        fleet.add_vehicle(vehicle)
    
    return fleet
```

---

## 6. Task 3: Transport Request System

```python
# src/requests/transport_request.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class RequestStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    UNSERVED = "unserved"

class TransportRequest(BaseModel):
    """A passenger/cargo transport request (OD pair)."""
    id: str
    origin: str                              # Origin node ID
    destination: str                         # Destination node ID
    time: int                                # Request arrival time (simulation step)
    passengers: int = 1                      # Number of passengers
    priority: int = Field(default=1, ge=1, le=3)  # 1=normal, 2=high, 3=emergency
    status: RequestStatus = RequestStatus.PENDING
    assigned_vehicle_id: Optional[str] = None
    assigned_route: Optional[list[str]] = None
    actual_travel_time: Optional[float] = None
    free_flow_travel_time: Optional[float] = None  # For ADIF calculation


class RequestQueue(BaseModel):
    """Queue of transport requests."""
    requests: dict[str, TransportRequest] = {}
    
    def add_request(self, request: TransportRequest):
        self.requests[request.id] = request
    
    def get_pending_requests(self) -> list[TransportRequest]:
        return [r for r in self.requests.values() if r.status == RequestStatus.PENDING]
    
    def get_affected_requests(self) -> list[TransportRequest]:
        """All requests that need serving (pending + assigned but not completed)."""
        return [r for r in self.requests.values() 
                if r.status in (RequestStatus.PENDING, RequestStatus.ASSIGNED)]
    
    def to_json_state(self) -> list[dict]:
        return [r.model_dump() for r in self.requests.values()]
```

---

## 7. Task 4: Disruption Injection Mechanisms

### 7.1 Disruption Data Model

```python
# src/disruptions/disruption.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class DisruptionType(str, Enum):
    ROAD_CLOSURE = "road_closure"
    CONGESTION = "congestion"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    DEMAND_SURGE = "demand_surge"

class Disruption(BaseModel):
    """A single disruption event."""
    id: str
    type: DisruptionType
    time: int                                     # Simulation step when disruption occurs
    duration: Optional[int] = None                # Duration in steps (None = permanent)
    
    # Road closure / congestion params
    edge_from: Optional[str] = None               # From node
    edge_to: Optional[str] = None                 # To node
    congestion_factor: Optional[float] = None     # Travel time multiplier (for congestion)
    
    # Vehicle breakdown params
    vehicle_id: Optional[str] = None
    
    # Demand surge params
    surge_multiplier: Optional[float] = None
    surge_area_nodes: Optional[list[str]] = None  # Affected area nodes
    surge_num_requests: Optional[int] = None      # Number of extra requests
```

### 7.2 Disruption Manager

```python
# src/disruptions/disruption_manager.py

import traci
from typing import List
from .disruption import Disruption, DisruptionType
from ..network.graph_builder import TransportNetwork
from ..fleet.vehicle import Fleet
from ..requests.transport_request import TransportRequest, RequestQueue, RequestStatus
import random

class DisruptionManager:
    """Applies and tracks disruptions in both SUMO and NetworkX."""
    
    def __init__(self, network: TransportNetwork, fleet: Fleet, request_queue: RequestQueue):
        self.network = network
        self.fleet = fleet
        self.request_queue = request_queue
        self.active_disruptions: list[Disruption] = []
        self.disruption_log: list[dict] = []
    
    def apply_disruption(self, disruption: Disruption, current_step: int):
        """Apply a disruption to both SUMO and NetworkX graph."""
        
        if disruption.type == DisruptionType.ROAD_CLOSURE:
            self._apply_road_closure(disruption)
        elif disruption.type == DisruptionType.CONGESTION:
            self._apply_congestion(disruption)
        elif disruption.type == DisruptionType.VEHICLE_BREAKDOWN:
            self._apply_vehicle_breakdown(disruption)
        elif disruption.type == DisruptionType.DEMAND_SURGE:
            self._apply_demand_surge(disruption, current_step)
        
        self.active_disruptions.append(disruption)
        self.disruption_log.append({
            "disruption_id": disruption.id,
            "type": disruption.type.value,
            "applied_at_step": current_step
        })
    
    def _apply_road_closure(self, d: Disruption):
        """Close a road in both SUMO and NetworkX."""
        # NetworkX side
        self.network.close_edge(d.edge_from, d.edge_to)
        
        # SUMO side — disallow all vehicle classes on all lanes of the edge
        edge_data = self.network.get_edge_by_nodes(d.edge_from, d.edge_to)
        if edge_data:
            edge_id = edge_data['edge_id']
            try:
                for lane_idx in range(edge_data.get('lanes', 1)):
                    lane_id = f"{edge_id}_{lane_idx}"
                    traci.lane.setDisallowed(lane_id, 
                        ["passenger", "bus", "truck", "delivery", "taxi", "emergency"])
                # Also set massive travel time to trigger rerouting
                traci.edge.adaptTraveltime(edge_id, time=100000)
            except traci.TraCIException as e:
                print(f"Warning: Could not apply SUMO closure for {edge_id}: {e}")
    
    def _apply_congestion(self, d: Disruption):
        """Increase travel time on an edge."""
        # NetworkX side
        self.network.congest_edge(d.edge_from, d.edge_to, d.congestion_factor)
        
        # SUMO side — reduce max speed
        edge_data = self.network.get_edge_by_nodes(d.edge_from, d.edge_to)
        if edge_data:
            edge_id = edge_data['edge_id']
            try:
                original_speed = edge_data['speed_limit']
                new_speed = max(1.0, original_speed / d.congestion_factor)
                traci.edge.setMaxSpeed(edge_id, new_speed)
            except traci.TraCIException as e:
                print(f"Warning: Could not apply SUMO congestion for {edge_id}: {e}")
    
    def _apply_vehicle_breakdown(self, d: Disruption):
        """Mark a vehicle as broken down."""
        self.fleet.break_vehicle(d.vehicle_id)
        
        # SUMO side — stop the vehicle
        try:
            edge_id = traci.vehicle.getRoadID(d.vehicle_id)
            pos = traci.vehicle.getLanePosition(d.vehicle_id)
            traci.vehicle.setStop(d.vehicle_id, edgeID=edge_id, pos=pos, duration=100000)
        except traci.TraCIException as e:
            print(f"Warning: Could not stop SUMO vehicle {d.vehicle_id}: {e}")
    
    def _apply_demand_surge(self, d: Disruption, current_step: int, seed: int = 42):
        """Inject additional transport requests in a specific area."""
        rng = random.Random(seed + current_step)
        nodes = d.surge_area_nodes or list(self.network.graph.nodes())
        
        for i in range(d.surge_num_requests or 5):
            origin = rng.choice(nodes)
            dest_candidates = [n for n in nodes if n != origin]
            if dest_candidates:
                destination = rng.choice(dest_candidates)
                request = TransportRequest(
                    id=f"SURGE_{d.id}_{i}",
                    origin=origin,
                    destination=destination,
                    time=current_step,
                    passengers=rng.randint(1, 3),
                    priority=1
                )
                self.request_queue.add_request(request)
    
    def check_expirations(self, current_step: int):
        """Remove expired disruptions and restore network state."""
        still_active = []
        for d in self.active_disruptions:
            if d.duration and (current_step - d.time) >= d.duration:
                # Restore
                if d.type in (DisruptionType.ROAD_CLOSURE, DisruptionType.CONGESTION):
                    self.network.restore_edge(d.edge_from, d.edge_to)
                self.disruption_log.append({
                    "disruption_id": d.id,
                    "type": d.type.value,
                    "expired_at_step": current_step
                })
            else:
                still_active.append(d)
        self.active_disruptions = still_active
    
    def get_disrupted_edges(self) -> list[dict]:
        """Return list of currently disrupted edges (for agent queries)."""
        disrupted = []
        for u, v, data in self.network.graph.edges(data=True):
            if data['status'] != "open":
                disrupted.append({
                    "from": u, "to": v,
                    "edge_id": data['edge_id'],
                    "status": data['status'],
                    "capacity": data['capacity'],
                    "travel_time": data['travel_time']
                })
        return disrupted
```

---

## 8. Task 5: Reproducible Scenario JSON Files (L1–L5)

### 8.1 Scenario Schema

```python
# src/scenarios/scenario.py

from pydantic import BaseModel
from typing import List, Optional
from ..disruptions.disruption import Disruption
from ..requests.transport_request import TransportRequest

class ScenarioConfig(BaseModel):
    """Fully reproducible scenario definition."""
    scenario_id: str
    complexity_level: str                    # L1, L2, L3, L4, L5
    description: str
    network_file: str                        # Path to .net.xml
    network_seed: int = 42
    simulation_duration: int = 600           # Total steps (seconds)
    disruption_time: int = 100               # When disruptions are injected
    
    # Fleet configuration
    num_vehicles: int = 8
    fleet_seed: int = 42
    
    # Disruptions & Requests
    disruptions: List[Disruption]
    requests: List[TransportRequest]
```

### 8.2 Five Scenario Files

Create these in `scenarios/`:

**scenarios/L1_simple.json**
```json
{
  "scenario_id": "L1_simple_001",
  "complexity_level": "L1",
  "description": "Single road closure. One alternate path exists. Basic rerouting.",
  "network_file": "networks/grid_4x4.net.xml",
  "network_seed": 42,
  "simulation_duration": 600,
  "disruption_time": 100,
  "num_vehicles": 8,
  "fleet_seed": 42,
  "disruptions": [
    {
      "id": "D1",
      "type": "road_closure",
      "time": 100,
      "edge_from": "B2",
      "edge_to": "C2",
      "duration": null
    }
  ],
  "requests": [
    {"id": "R1", "origin": "A1", "destination": "D4", "time": 50, "passengers": 2, "priority": 1},
    {"id": "R2", "origin": "B1", "destination": "C3", "time": 60, "passengers": 1, "priority": 1},
    {"id": "R3", "origin": "A3", "destination": "D2", "time": 80, "passengers": 1, "priority": 2}
  ]
}
```

**scenarios/L2_moderate.json**
```json
{
  "scenario_id": "L2_moderate_001",
  "complexity_level": "L2",
  "description": "Closure on primary route + congestion on obvious detour. Smarter path selection required.",
  "network_file": "networks/grid_4x4.net.xml",
  "network_seed": 42,
  "simulation_duration": 600,
  "disruption_time": 100,
  "num_vehicles": 8,
  "fleet_seed": 42,
  "disruptions": [
    {"id": "D1", "type": "road_closure", "time": 100, "edge_from": "B2", "edge_to": "C2"},
    {"id": "D2", "type": "congestion", "time": 100, "edge_from": "B3", "edge_to": "C3", "congestion_factor": 3.0}
  ],
  "requests": [
    {"id": "R1", "origin": "A1", "destination": "D4", "time": 50, "passengers": 2, "priority": 1},
    {"id": "R2", "origin": "B1", "destination": "C4", "time": 60, "passengers": 1, "priority": 1},
    {"id": "R3", "origin": "A2", "destination": "D3", "time": 70, "passengers": 1, "priority": 2},
    {"id": "R4", "origin": "C1", "destination": "D4", "time": 90, "passengers": 3, "priority": 1}
  ]
}
```

**scenarios/L3_compound.json**
```json
{
  "scenario_id": "L3_compound_001",
  "complexity_level": "L3",
  "description": "Primary route blocked, detour congested, AND one vehicle unavailable. Fleet rebalancing needed.",
  "network_file": "networks/grid_4x4.net.xml",
  "network_seed": 42,
  "simulation_duration": 600,
  "disruption_time": 100,
  "num_vehicles": 8,
  "fleet_seed": 42,
  "disruptions": [
    {"id": "D1", "type": "road_closure", "time": 100, "edge_from": "B2", "edge_to": "C2"},
    {"id": "D2", "type": "congestion", "time": 100, "edge_from": "B3", "edge_to": "C3", "congestion_factor": 3.5},
    {"id": "D3", "type": "vehicle_breakdown", "time": 120, "vehicle_id": "V003"}
  ],
  "requests": [
    {"id": "R1", "origin": "A1", "destination": "D4", "time": 50, "passengers": 2, "priority": 1},
    {"id": "R2", "origin": "B1", "destination": "C4", "time": 60, "passengers": 1, "priority": 1},
    {"id": "R3", "origin": "A2", "destination": "D3", "time": 70, "passengers": 1, "priority": 2},
    {"id": "R4", "origin": "C1", "destination": "D4", "time": 90, "passengers": 3, "priority": 1},
    {"id": "R5", "origin": "A4", "destination": "D1", "time": 110, "passengers": 1, "priority": 3}
  ]
}
```

**scenarios/L4_cascading.json**
```json
{
  "scenario_id": "L4_cascading_001",
  "complexity_level": "L4",
  "description": "Multiple simultaneous disruptions with demand spike. Tests full coordination capacity.",
  "network_file": "networks/grid_4x4.net.xml",
  "network_seed": 42,
  "simulation_duration": 900,
  "disruption_time": 100,
  "num_vehicles": 10,
  "fleet_seed": 42,
  "disruptions": [
    {"id": "D1", "type": "road_closure", "time": 100, "edge_from": "B2", "edge_to": "C2"},
    {"id": "D2", "type": "road_closure", "time": 150, "edge_from": "A3", "edge_to": "A4"},
    {"id": "D3", "type": "congestion", "time": 100, "edge_from": "B3", "edge_to": "C3", "congestion_factor": 4.0},
    {"id": "D4", "type": "vehicle_breakdown", "time": 130, "vehicle_id": "V002"},
    {"id": "D5", "type": "demand_surge", "time": 200, "surge_multiplier": 2.0, "surge_num_requests": 6, "surge_area_nodes": ["A1", "A2", "B1", "B2"]}
  ],
  "requests": [
    {"id": "R1", "origin": "A1", "destination": "D4", "time": 50, "passengers": 2, "priority": 1},
    {"id": "R2", "origin": "B1", "destination": "C4", "time": 60, "passengers": 1, "priority": 1},
    {"id": "R3", "origin": "A2", "destination": "D3", "time": 70, "passengers": 1, "priority": 2},
    {"id": "R4", "origin": "C1", "destination": "D4", "time": 90, "passengers": 3, "priority": 1},
    {"id": "R5", "origin": "A4", "destination": "D1", "time": 110, "passengers": 1, "priority": 3},
    {"id": "R6", "origin": "D2", "destination": "A1", "time": 130, "passengers": 2, "priority": 1}
  ]
}
```

**scenarios/L5_stress.json**
```json
{
  "scenario_id": "L5_stress_001",
  "complexity_level": "L5",
  "description": "Near-collapse scenario. Tests graceful degradation and fallback behavior.",
  "network_file": "networks/grid_4x4.net.xml",
  "network_seed": 42,
  "simulation_duration": 1200,
  "disruption_time": 100,
  "num_vehicles": 10,
  "fleet_seed": 42,
  "disruptions": [
    {"id": "D1", "type": "road_closure", "time": 100, "edge_from": "B2", "edge_to": "C2"},
    {"id": "D2", "type": "road_closure", "time": 120, "edge_from": "A3", "edge_to": "A4"},
    {"id": "D3", "type": "road_closure", "time": 180, "edge_from": "C3", "edge_to": "D3"},
    {"id": "D4", "type": "congestion", "time": 100, "edge_from": "B3", "edge_to": "C3", "congestion_factor": 4.0},
    {"id": "D5", "type": "congestion", "time": 150, "edge_from": "B4", "edge_to": "C4", "congestion_factor": 3.0},
    {"id": "D6", "type": "vehicle_breakdown", "time": 130, "vehicle_id": "V002"},
    {"id": "D7", "type": "vehicle_breakdown", "time": 200, "vehicle_id": "V005"},
    {"id": "D8", "type": "demand_surge", "time": 250, "surge_multiplier": 3.0, "surge_num_requests": 10, "surge_area_nodes": ["A1", "A2", "B1", "B2", "C1", "C2"]}
  ],
  "requests": [
    {"id": "R1", "origin": "A1", "destination": "D4", "time": 50, "passengers": 2, "priority": 1},
    {"id": "R2", "origin": "B1", "destination": "C4", "time": 60, "passengers": 1, "priority": 1},
    {"id": "R3", "origin": "A2", "destination": "D3", "time": 70, "passengers": 1, "priority": 2},
    {"id": "R4", "origin": "C1", "destination": "D4", "time": 90, "passengers": 3, "priority": 1},
    {"id": "R5", "origin": "A4", "destination": "D1", "time": 110, "passengers": 1, "priority": 3},
    {"id": "R6", "origin": "D2", "destination": "A1", "time": 130, "passengers": 2, "priority": 1},
    {"id": "R7", "origin": "B4", "destination": "D2", "time": 160, "passengers": 1, "priority": 1},
    {"id": "R8", "origin": "C4", "destination": "A2", "time": 190, "passengers": 2, "priority": 2}
  ]
}
```

---

## 9. Task 6: Seven Core Tool Functions

These are the **exact same functions** that will be called by all 3 systems: Rule-Based (directly), Single-LLM (via tool-use), and Multi-Agent LLM (via scoped tool-use).

```python
# src/tools/agent_tools.py

"""
Seven core tool functions for the transport disruption environment.
These functions provide the interface between decision-makers (Rule-Based / LLM agents)
and the simulation state. All three systems use the SAME functions.
"""

from typing import Optional, List
from ..network.graph_builder import TransportNetwork
from ..fleet.vehicle import Fleet, Vehicle, VehicleStatus
from ..requests.transport_request import RequestQueue, TransportRequest, RequestStatus
from ..disruptions.disruption_manager import DisruptionManager
import networkx as nx


class AgentTools:
    """Unified tool interface for all agent types."""
    
    def __init__(self, network: TransportNetwork, fleet: Fleet, 
                 request_queue: RequestQueue, disruption_manager: DisruptionManager):
        self.network = network
        self.fleet = fleet
        self.request_queue = request_queue
        self.disruption_manager = disruption_manager
    
    # ─────────────────────────────────────────────
    # TOOL 1: get_network_state()
    # Used by: Traffic Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_network_state(self) -> dict:
        """Return current road network state including topology, capacities, and disruptions.
        
        Returns:
            dict with keys: nodes, edges, disrupted_edges, total_nodes, total_edges, open_edges
        """
        state = self.network.to_json_state()
        disrupted = self.disruption_manager.get_disrupted_edges()
        
        open_edges = sum(1 for _, _, d in self.network.graph.edges(data=True) if d['capacity'] > 0)
        
        return {
            "nodes": state["nodes"],
            "edges": state["edges"],
            "disrupted_edges": disrupted,
            "total_nodes": self.network.graph.number_of_nodes(),
            "total_edges": self.network.graph.number_of_edges(),
            "open_edges": open_edges,
            "closed_edges": self.network.graph.number_of_edges() - open_edges
        }
    
    # ─────────────────────────────────────────────
    # TOOL 2: get_vehicle_status()
    # Used by: Fleet Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_vehicle_status(self) -> dict:
        """Return current fleet status including all vehicle positions, SoC, and assignments.
        
        Returns:
            dict with keys: vehicles, total_vehicles, available_vehicles, broken_vehicles
        """
        vehicles = self.fleet.to_json_state()
        available = self.fleet.get_available_vehicles()
        broken = [v for v in self.fleet.vehicles.values() if v.status == VehicleStatus.BROKEN]
        
        return {
            "vehicles": vehicles,
            "total_vehicles": len(self.fleet.vehicles),
            "available_vehicles": len(available),
            "broken_vehicles": len(broken),
            "available_vehicle_ids": [v.id for v in available]
        }
    
    # ─────────────────────────────────────────────
    # TOOL 3: get_disrupted_edges()
    # Used by: Traffic Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_disrupted_edges(self) -> list[dict]:
        """Return list of all currently disrupted edges with their status and remaining capacity.
        
        Returns:
            list of dicts, each with: from, to, edge_id, status, capacity, travel_time
        """
        return self.disruption_manager.get_disrupted_edges()
    
    # ─────────────────────────────────────────────
    # TOOL 4: get_available_vehicles()
    # Used by: Fleet Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_available_vehicles(self) -> list[dict]:
        """Return list of vehicles that are idle, operational, and have sufficient SoC.
        
        Returns:
            list of dicts with: id, current_node, capacity, soc, remaining_range_km
        """
        available = self.fleet.get_available_vehicles()
        return [{
            "id": v.id,
            "current_node": v.current_node,
            "capacity": v.capacity,
            "current_passengers": v.current_passengers,
            "soc": round(v.soc, 1),
            "remaining_range_km": round(v.remaining_range_km(), 1)
        } for v in available]
    
    # ─────────────────────────────────────────────
    # TOOL 5: shortest_path()
    # Used by: Routing Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def shortest_path(self, origin: str, destination: str) -> dict:
        """Find shortest path between two nodes on the open (non-disrupted) subgraph.
        
        Args:
            origin: Source node ID
            destination: Target node ID
        
        Returns:
            dict with: path (list of nodes), distance_km, estimated_travel_time, reachable (bool)
        """
        path = self.network.shortest_path(origin, destination, weight='travel_time')
        
        if path is None:
            return {
                "origin": origin,
                "destination": destination,
                "reachable": False,
                "path": None,
                "distance_km": None,
                "estimated_travel_time": None,
                "num_hops": None
            }
        
        # Calculate total distance and travel time
        total_distance = 0.0
        total_time = 0.0
        for i in range(len(path) - 1):
            edge_data = self.network.graph[path[i]][path[i+1]]
            total_distance += edge_data['length']
            total_time += edge_data['travel_time']
        
        return {
            "origin": origin,
            "destination": destination,
            "reachable": True,
            "path": path,
            "distance_km": round(total_distance / 1000, 2),
            "estimated_travel_time": round(total_time, 1),
            "num_hops": len(path) - 1
        }
    
    # ─────────────────────────────────────────────
    # TOOL 6: assign_vehicle()
    # Used by: Coordinator Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def assign_vehicle(self, vehicle_id: str, request_id: str, route: list[str]) -> dict:
        """Assign a vehicle to a transport request with a specific route.
        
        Args:
            vehicle_id: Vehicle to assign
            request_id: Request to fulfill
            route: List of node IDs forming the route
        
        Returns:
            dict with: success (bool), message, assignment details
        """
        vehicle = self.fleet.get_vehicle(vehicle_id)
        request = self.request_queue.requests.get(request_id)
        
        if not vehicle:
            return {"success": False, "message": f"Vehicle {vehicle_id} not found"}
        if not request:
            return {"success": False, "message": f"Request {request_id} not found"}
        if vehicle.status != VehicleStatus.IDLE:
            return {"success": False, "message": f"Vehicle {vehicle_id} is {vehicle.status.value}, not idle"}
        if request.status != RequestStatus.PENDING:
            return {"success": False, "message": f"Request {request_id} is {request.status.value}, not pending"}
        
        # Calculate route distance
        total_distance = 0.0
        for i in range(len(route) - 1):
            if self.network.graph.has_edge(route[i], route[i+1]):
                total_distance += self.network.graph[route[i]][route[i+1]]['length']
            else:
                return {"success": False, "message": f"Edge {route[i]}->{route[i+1]} does not exist"}
        
        distance_km = total_distance / 1000
        
        # Check capacity
        if vehicle.capacity < request.passengers + vehicle.current_passengers:
            return {"success": False, "message": f"Vehicle {vehicle_id} capacity ({vehicle.capacity}) insufficient for {request.passengers} passengers"}
        
        # Update state
        vehicle.status = VehicleStatus.EN_ROUTE
        vehicle.assigned_request_id = request_id
        vehicle.route = route
        
        request.status = RequestStatus.ASSIGNED
        request.assigned_vehicle_id = vehicle_id
        request.assigned_route = route
        
        return {
            "success": True,
            "message": f"Vehicle {vehicle_id} assigned to request {request_id}",
            "vehicle_id": vehicle_id,
            "request_id": request_id,
            "route": route,
            "distance_km": round(distance_km, 2)
        }
    
    # ─────────────────────────────────────────────
    # TOOL 7: validate_plan() — Safety-Review Guard
    # Used by: All systems (applied to all outputs)
    # ─────────────────────────────────────────────
    def validate_plan(self, vehicle_id: str, route: list[str], 
                      request_id: str) -> dict:
        """Deterministic Safety-Review Guard. Validates a proposed plan against hard constraints.
        
        Checks:
        1. BFS Reachability: Every edge in route has capacity > 0
        2. SoC Sufficiency: Vehicle has enough charge (+ 15% margin)
        3. Capacity Check: Vehicle can carry the passengers
        4. Route Existence: All edges in route exist in graph
        
        Returns:
            dict with: valid (bool), checks_passed (list), checks_failed (list), rejection_reason
        """
        checks_passed = []
        checks_failed = []
        
        vehicle = self.fleet.get_vehicle(vehicle_id)
        request = self.request_queue.requests.get(request_id)
        
        if not vehicle:
            return {"valid": False, "checks_passed": [], "checks_failed": ["Vehicle not found"], "rejection_reason": f"Vehicle {vehicle_id} does not exist"}
        if not request:
            return {"valid": False, "checks_passed": [], "checks_failed": ["Request not found"], "rejection_reason": f"Request {request_id} does not exist"}
        
        # CHECK 1: Route Existence — every consecutive pair must be a valid edge
        total_distance = 0.0
        total_travel_time = 0.0
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if not self.network.graph.has_edge(u, v):
                checks_failed.append(f"Edge {u}->{v} does not exist in graph")
            else:
                edge = self.network.graph[u][v]
                total_distance += edge['length']
                total_travel_time += edge['travel_time']
        
        if not checks_failed:
            checks_passed.append("Route existence: All edges exist")
        
        # CHECK 2: BFS Reachability — no edge has capacity = 0 (closed)
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if self.network.graph.has_edge(u, v):
                if self.network.graph[u][v]['capacity'] <= 0:
                    checks_failed.append(f"BFS: Edge {u}->{v} is closed (capacity=0)")
        
        if not any("BFS" in f for f in checks_failed):
            checks_passed.append("BFS reachability: All edges operational")
        
        # CHECK 3: SoC Sufficiency (+15% safety margin)
        distance_km = total_distance / 1000
        if vehicle.can_reach(distance_km, safety_margin=0.15):
            checks_passed.append(f"SoC check: {vehicle.soc:.1f}% sufficient for {distance_km:.1f}km")
        else:
            required = distance_km * vehicle.soc_consumption_per_km * 1.15
            checks_failed.append(
                f"SoC insufficient: have {vehicle.soc:.1f}%, need {required:.1f}% for {distance_km:.1f}km + 15% margin"
            )
        
        # CHECK 4: Passenger Capacity
        needed = request.passengers + vehicle.current_passengers
        if vehicle.capacity >= needed:
            checks_passed.append(f"Capacity check: {vehicle.capacity} >= {needed} passengers")
        else:
            checks_failed.append(
                f"Capacity insufficient: vehicle has {vehicle.capacity} seats, needs {needed}"
            )
        
        valid = len(checks_failed) == 0
        
        return {
            "valid": valid,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "rejection_reason": checks_failed[0] if checks_failed else None,
            "route_distance_km": round(distance_km, 2),
            "estimated_travel_time": round(total_travel_time, 1)
        }
```

---

## 10. Task 7: Rule-Based Baseline (B1)

```python
# src/baselines/rule_based.py

"""
Baseline 1: Rule-Based SOP Controller
Uses deterministic heuristics — no LLM involved.
Serves as the performance floor.
"""

from typing import Optional
from ..tools.agent_tools import AgentTools
from ..network.graph_builder import TransportNetwork
from ..fleet.vehicle import Fleet, VehicleStatus
from ..requests.transport_request import RequestQueue, RequestStatus
from ..safety.decision_card import DecisionCard
import networkx as nx


class RuleBasedController:
    """Deterministic rule-based disruption response controller."""
    
    def __init__(self, tools: AgentTools):
        self.tools = tools
        self.decisions_proposed = 0
        self.decisions_rejected = 0
    
    def respond_to_disruption(self) -> list[DecisionCard]:
        """Execute rule-based disruption response.
        
        Algorithm:
        1. Get all pending requests
        2. For each request, compute shortest path on open subgraph
        3. Find nearest available vehicle with sufficient SoC
        4. Validate via Safety Guard
        5. If valid -> assign; if invalid -> mark as UNSERVED
        """
        decisions = []
        pending = self.tools.request_queue.get_pending_requests()
        
        # Sort by priority (higher first) then by time (earlier first)
        pending.sort(key=lambda r: (-r.priority, r.time))
        
        for request in pending:
            decision = self._handle_request(request)
            if decision:
                decisions.append(decision)
        
        return decisions
    
    def _handle_request(self, request) -> Optional[DecisionCard]:
        """Handle a single transport request using rule-based heuristics."""
        
        # Step 1: Find shortest path
        path_result = self.tools.shortest_path(request.origin, request.destination)
        
        if not path_result['reachable']:
            request.status = RequestStatus.UNSERVED
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="NO_PATH_AVAILABLE",
                vehicle_id=None,
                assigned_route=None,
                estimated_delay_reduction_min=0,
                safety_guard_passed=False,
                rejection_reason="No path exists between origin and destination"
            )
        
        route = path_result['path']
        distance_km = path_result['distance_km']
        
        # Step 2: Find nearest available vehicle with sufficient SoC
        available = self.tools.get_available_vehicles()
        best_vehicle = None
        best_distance = float('inf')
        
        for v_info in available:
            # Check if vehicle can reach the request origin
            origin_path = self.tools.shortest_path(v_info['current_node'], request.origin)
            if origin_path['reachable']:
                pickup_distance = origin_path['distance_km']
                total_distance = pickup_distance + distance_km
                
                # Check SoC for total trip
                vehicle = self.tools.fleet.get_vehicle(v_info['id'])
                if vehicle.can_reach(total_distance) and v_info['capacity'] >= request.passengers:
                    if pickup_distance < best_distance:
                        best_distance = pickup_distance
                        best_vehicle = v_info
        
        if not best_vehicle:
            request.status = RequestStatus.UNSERVED
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="NO_VEHICLE_AVAILABLE",
                vehicle_id=None,
                assigned_route=None,
                estimated_delay_reduction_min=0,
                safety_guard_passed=False,
                rejection_reason="No available vehicle with sufficient SoC and capacity"
            )
        
        # Step 3: Validate via Safety Guard
        self.decisions_proposed += 1
        validation = self.tools.validate_plan(
            vehicle_id=best_vehicle['id'],
            route=route,
            request_id=request.id
        )
        
        if validation['valid']:
            # Step 4: Execute assignment
            self.tools.assign_vehicle(best_vehicle['id'], request.id, route)
            
            # Calculate free-flow time for ADIF
            free_flow_time = sum(
                self.tools.network.graph[route[i]][route[i+1]]['length'] / 
                self.tools.network.graph[route[i]][route[i+1]]['speed_limit']
                for i in range(len(route) - 1)
            )
            actual_time = validation.get('estimated_travel_time', free_flow_time)
            delay_reduction = max(0, (actual_time - free_flow_time) / 60)
            
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="REROUTE_AND_DISPATCH",
                vehicle_id=best_vehicle['id'],
                assigned_route=route,
                estimated_delay_reduction_min=round(delay_reduction, 1),
                safety_guard_passed=True,
                route_distance_km=validation.get('route_distance_km'),
                estimated_travel_time_s=validation.get('estimated_travel_time')
            )
        else:
            self.decisions_rejected += 1
            request.status = RequestStatus.UNSERVED
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="FALLBACK_SOP",
                vehicle_id=best_vehicle['id'],
                assigned_route=route,
                estimated_delay_reduction_min=0,
                safety_guard_passed=False,
                rejection_reason=validation.get('rejection_reason')
            )
```

### DecisionCard Schema (Pydantic)

```python
# src/safety/decision_card.py

from pydantic import BaseModel
from typing import Optional, List

class DecisionCard(BaseModel):
    """Structured output format for all decision-makers.
    Must pass Pydantic validation before execution."""
    scenario_id: str
    request_id: str
    recommended_action: str            # REROUTE_AND_DISPATCH | NO_PATH | NO_VEHICLE | FALLBACK_SOP
    vehicle_id: Optional[str] = None
    assigned_route: Optional[List[str]] = None
    estimated_delay_reduction_min: float = 0.0
    safety_guard_passed: bool = False
    rejection_reason: Optional[str] = None
    route_distance_km: Optional[float] = None
    estimated_travel_time_s: Optional[float] = None
```

---

## 11. Task 8: Auto-Calculated Metrics

```python
# src/metrics/evaluator.py

"""
Automatic evaluation metrics computed after each scenario run.
Same metrics applied to all 3 systems for fair comparison.
"""

from dataclasses import dataclass, field
from typing import List
from ..safety.decision_card import DecisionCard
from ..requests.transport_request import RequestQueue, RequestStatus


@dataclass
class ScenarioMetrics:
    """All 6 evaluation metrics for a single scenario run."""
    scenario_id: str
    system_name: str                          # "rule_based" | "single_llm" | "multi_agent_llm"
    
    # Metric 1: Hard Constraint Violation Rate (HCVR %)
    total_proposed_actions: int = 0
    infeasible_actions: int = 0
    hcvr_percent: float = 0.0
    
    # Metric 2: Request Fulfillment Rate (RFR %)
    total_affected_requests: int = 0
    successfully_served: int = 0
    rfr_percent: float = 0.0
    
    # Metric 3: Average Delay Inflation Factor (ADIF)
    delay_factors: list = field(default_factory=list)
    adif: float = 1.0
    
    # Metric 4: Execution Latency (T_exec in seconds)
    execution_latency_s: float = 0.0
    
    # Metric 5: Token Cost ($/scenario) — only for LLM systems
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    token_cost_usd: float = 0.0
    
    # Metric 6: Infeasible Decision Rate (IDR %)
    total_decisions: int = 0
    rejected_by_guard: int = 0
    idr_percent: float = 0.0


class MetricsEvaluator:
    """Calculates all 6 metrics from scenario results."""
    
    def __init__(self, scenario_id: str, system_name: str):
        self.metrics = ScenarioMetrics(
            scenario_id=scenario_id,
            system_name=system_name
        )
    
    def evaluate(self, decisions: list[DecisionCard], request_queue: RequestQueue,
                 execution_time_s: float = 0.0, 
                 token_usage: dict = None) -> ScenarioMetrics:
        """Compute all metrics from a list of DecisionCards."""
        
        m = self.metrics
        
        # -- Metric 1: HCVR --
        m.total_proposed_actions = len(decisions)
        m.infeasible_actions = sum(
            1 for d in decisions 
            if not d.safety_guard_passed and d.recommended_action not in ("NO_PATH_AVAILABLE", "NO_VEHICLE_AVAILABLE")
        )
        m.hcvr_percent = (
            (m.infeasible_actions / m.total_proposed_actions * 100) 
            if m.total_proposed_actions > 0 else 0.0
        )
        
        # -- Metric 2: RFR --
        all_requests = list(request_queue.requests.values())
        m.total_affected_requests = len(all_requests)
        m.successfully_served = sum(
            1 for r in all_requests 
            if r.status in (RequestStatus.ASSIGNED, RequestStatus.IN_TRANSIT, RequestStatus.COMPLETED)
        )
        m.rfr_percent = (
            (m.successfully_served / m.total_affected_requests * 100)
            if m.total_affected_requests > 0 else 0.0
        )
        
        # -- Metric 3: ADIF --
        for r in all_requests:
            if r.actual_travel_time and r.free_flow_travel_time and r.free_flow_travel_time > 0:
                m.delay_factors.append(r.actual_travel_time / r.free_flow_travel_time)
        m.adif = (
            sum(m.delay_factors) / len(m.delay_factors)
            if m.delay_factors else 1.0
        )
        
        # -- Metric 4: Execution Latency --
        m.execution_latency_s = execution_time_s
        
        # -- Metric 5: Token Cost --
        if token_usage:
            m.prompt_tokens = token_usage.get('prompt_tokens', 0)
            m.completion_tokens = token_usage.get('completion_tokens', 0)
            m.total_tokens = m.prompt_tokens + m.completion_tokens
            # Approximate pricing (GPT-4o-mini as reference)
            m.token_cost_usd = (
                m.prompt_tokens * 0.00000015 + 
                m.completion_tokens * 0.0000006
            )
        
        # -- Metric 6: IDR --
        m.total_decisions = len(decisions)
        m.rejected_by_guard = sum(1 for d in decisions if not d.safety_guard_passed)
        m.idr_percent = (
            (m.rejected_by_guard / m.total_decisions * 100)
            if m.total_decisions > 0 else 0.0
        )
        
        return m
    
    @staticmethod
    def print_report(m: ScenarioMetrics):
        """Print a formatted metrics report."""
        print(f"\n{'='*60}")
        print(f"  SCENARIO METRICS REPORT")
        print(f"  Scenario: {m.scenario_id} | System: {m.system_name}")
        print(f"{'='*60}")
        print(f"  1. HCVR (Hard Constraint Violation Rate): {m.hcvr_percent:.1f}%")
        print(f"     ({m.infeasible_actions} infeasible / {m.total_proposed_actions} proposed)")
        print(f"  2. RFR  (Request Fulfillment Rate):       {m.rfr_percent:.1f}%")
        print(f"     ({m.successfully_served} served / {m.total_affected_requests} affected)")
        print(f"  3. ADIF (Avg Delay Inflation Factor):     {m.adif:.2f}x")
        print(f"  4. T_exec (Execution Latency):            {m.execution_latency_s:.2f}s")
        print(f"  5. Token Cost:                            ${m.token_cost_usd:.4f}")
        print(f"     (Prompt: {m.prompt_tokens} | Completion: {m.completion_tokens})")
        print(f"  6. IDR  (Infeasible Decision Rate):       {m.idr_percent:.1f}%")
        print(f"     ({m.rejected_by_guard} rejected / {m.total_decisions} total)")
        print(f"{'='*60}\n")
```

---

## 12. Project File Structure

```
04-Minor/
├── week-0/                          # Initial project docs
├── week-1/                          # Literature review & presentation
├── week-2/                          # Research gap & experimental design
├── week-3/                          # <-- YOU ARE HERE
│   └── work.md                      # This guide
│
├── src/                             # Main source code
│   ├── __init__.py
│   ├── network/
│   │   ├── __init__.py
│   │   └── graph_builder.py         # TransportNetwork (SUMO + NetworkX dual)
│   ├── fleet/
│   │   ├── __init__.py
│   │   ├── vehicle.py               # Vehicle, Fleet models
│   │   └── fleet_factory.py         # Test fleet generator
│   ├── requests/
│   │   ├── __init__.py
│   │   └── transport_request.py     # TransportRequest, RequestQueue
│   ├── disruptions/
│   │   ├── __init__.py
│   │   ├── disruption.py            # Disruption model
│   │   └── disruption_manager.py    # DisruptionManager
│   ├── tools/
│   │   ├── __init__.py
│   │   └── agent_tools.py           # 7 core tool functions
│   ├── safety/
│   │   ├── __init__.py
│   │   └── decision_card.py         # DecisionCard Pydantic schema
│   ├── baselines/
│   │   ├── __init__.py
│   │   └── rule_based.py            # Baseline 1: Rule-Based SOP Controller
│   └── metrics/
│       ├── __init__.py
│       └── evaluator.py             # MetricsEvaluator (6 metrics)
│
├── networks/                        # SUMO network files
│   └── grid_4x4.net.xml             # Synthetic 4x4 grid (generated)
│
├── scenarios/                       # Reproducible scenario JSON files
│   ├── L1_simple.json
│   ├── L2_moderate.json
│   ├── L3_compound.json
│   ├── L4_cascading.json
│   └── L5_stress.json
│
├── scripts/
│   ├── generate_network.sh          # Network generation command
│   ├── run_scenario.py              # Main scenario runner
│   └── run_baseline_test.py         # Test B1 on all scenarios
│
├── results/                         # Output metrics & logs
│   └── .gitkeep
│
├── requirements.txt
└── README.md
```

---

## 13. Verification Checklist

Before moving to Week 4 (LLM implementation), ALL of these must pass:

### Environment Core
- [ ] SUMO installed and `traci` imports work
- [ ] 4x4 grid network generated and loads in `sumo-gui`
- [ ] `TransportNetwork` builds NetworkX graph from SUMO `.net.xml`
- [ ] `shortest_path()` returns correct paths on the graph
- [ ] `bfs_reachable()` correctly identifies unreachable destinations after edge closures

### Fleet & Requests
- [ ] `Fleet` initializes 8 vehicles distributed across nodes
- [ ] `Vehicle.can_reach()` correctly validates SoC for given distances
- [ ] `RequestQueue` correctly tracks pending/assigned/unserved requests
- [ ] Pydantic validation catches malformed `DecisionCard` JSON

### Disruptions
- [ ] Road closure: Edge capacity -> 0, shortest path avoids it
- [ ] Congestion: Travel time increases by factor, routing prefers alternatives
- [ ] Vehicle breakdown: Vehicle status -> BROKEN, excluded from dispatch
- [ ] Demand surge: Extra requests injected into queue at specified time

### Scenarios
- [ ] All 5 scenario JSON files (L1-L5) parse without errors
- [ ] Same scenario produces identical results with same seed

### Safety Guard
- [ ] `validate_plan()` rejects routes through closed edges
- [ ] `validate_plan()` rejects plans where vehicle SoC is insufficient
- [ ] `validate_plan()` rejects plans where vehicle capacity is insufficient
- [ ] `validate_plan()` rejects routes with non-existent edges

### Baseline B1
- [ ] Rule-based controller produces DecisionCards for all pending requests
- [ ] Rule-based controller achieves 0% HCVR (all plans pass safety guard)
- [ ] Rule-based controller correctly marks unreachable requests as UNSERVED

### Metrics
- [ ] HCVR calculates correctly (should be 0% for B1 with guard)
- [ ] RFR calculates correctly
- [ ] MetricsEvaluator prints formatted report
- [ ] Results saved to `results/` directory

### Integration Test
- [ ] Run rule-based baseline on L1 scenario -> metrics printed
- [ ] Run rule-based baseline on L3 scenario -> metrics printed
- [ ] Run rule-based baseline on L5 scenario -> some requests UNSERVED (expected)

---

## References

1. Eclipse SUMO Documentation — https://sumo.dlr.de/docs/
2. TraCI Python API — https://sumo.dlr.de/docs/TraCI/Interfacing_TraCI_from_Python.html
3. SUMO netgenerate — https://sumo.dlr.de/docs/netgenerate.html
4. SUMO Taxi/DRT — https://sumo.dlr.de/docs/Simulation/Taxi.html
5. NetworkX Documentation — https://networkx.org/documentation/stable/
6. Pydantic v2 Documentation — https://docs.pydantic.dev/latest/
7. Week 2 Research Gap & Design — `../week-2/research-gap-and-design.md`
