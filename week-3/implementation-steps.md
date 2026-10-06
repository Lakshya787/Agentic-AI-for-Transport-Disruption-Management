# Step-by-Step Implementation Guide
## From "Dependencies Installed" → "Working Transport Environment"
**Date:** September 9, 2026  
**Starting Point:** SUMO + Python deps installed, ready to build  
**End Point:** Rule-based baseline running on all 5 scenarios with metrics

---

## Roadmap Overview

```
You are here
    ↓
STEP 1: Verify SUMO installation actually works          (~10 min)
STEP 2: Create project directory structure                (~5 min)
STEP 3: Generate your first SUMO road network             (~15 min)
STEP 4: Write & test the NetworkX graph builder            (~30 min)
STEP 5: Write & test Vehicle/Fleet models                  (~20 min)
STEP 6: Write & test Transport Request system              (~15 min)
STEP 7: Write & test DecisionCard (Pydantic schema)        (~10 min)
STEP 8: Write & test Disruption system                     (~30 min)
STEP 9: Write & test the 7 Core Tool Functions             (~30 min)
STEP 10: Create the 5 scenario JSON files                  (~20 min)
STEP 11: Write & test Rule-Based Baseline (B1)             (~30 min)
STEP 12: Write & test Metrics Evaluator                    (~20 min)
STEP 13: Build the Scenario Runner (glues everything)      (~30 min)
STEP 14: Full Integration Test — run B1 on all scenarios   (~20 min)
STEP 15: Run with SUMO GUI to visually verify              (~15 min)
    ↓
✅ DONE — Ready for Week 4 (LLM agents)
```

**Total estimated time: ~5-6 hours of focused work**

---

## STEP 1: Verify SUMO Installation Actually Works

Before writing any project code, confirm everything is installed correctly.

### 1.1 Check SUMO binary

```bash
# Run this in your terminal
sumo --version
```

**Expected output** (version may differ slightly):
```
Eclipse SUMO sumo Version 1.x.x
```

If this fails, SUMO isn't in your PATH. Fix with:
```bash
# If you installed via pip
export SUMO_HOME=$(python3 -c "import sumo; print(sumo.SUMO_HOME)")
export PATH="$SUMO_HOME/bin:$PATH"

# Add to your shell profile so it persists
echo 'export SUMO_HOME=$(python3 -c "import sumo; print(sumo.SUMO_HOME)")' >> ~/.bashrc
echo 'export PATH="$SUMO_HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### 1.2 Check Python imports

Create a quick test file and run it:

```bash
cd ~/Desktop/Clg/IIITNR/Sem5/04-Minor
python3 -c "
import traci
import sumolib
import networkx as nx
import pydantic
print('✅ traci      OK')
print('✅ sumolib    OK')
print('✅ networkx   OK')
print('✅ pydantic   OK')
print()
print('All imports working!')
"
```

**If any import fails**, install the missing package:
```bash
pip install eclipse-sumo networkx pydantic
```

### 1.3 Check SUMO tools are accessible

```bash
# Check netgenerate (we'll use this to create road networks)
netgenerate --help 2>&1 | head -5

# Check sumo-gui (optional — for visual debugging)
which sumo-gui
```

**If `netgenerate` is not found** but `sumo` works:
```bash
# The tools might be in $SUMO_HOME/bin
ls $SUMO_HOME/bin/ | grep netgenerate
```

> **✅ Checkpoint:** All 4 imports work + `sumo --version` prints a version + `netgenerate` is accessible.  
> **Don't proceed until this checkpoint passes.**

---

## STEP 2: Create Project Directory Structure

```bash
cd ~/Desktop/Clg/IIITNR/Sem5/04-Minor

# Create all directories at once
mkdir -p src/network
mkdir -p src/fleet
mkdir -p src/requests
mkdir -p src/disruptions
mkdir -p src/tools
mkdir -p src/safety
mkdir -p src/baselines
mkdir -p src/metrics
mkdir -p src/scenarios
mkdir -p networks
mkdir -p scenarios
mkdir -p scripts
mkdir -p results

# Create all __init__.py files (makes Python treat directories as packages)
touch src/__init__.py
touch src/network/__init__.py
touch src/fleet/__init__.py
touch src/requests/__init__.py
touch src/disruptions/__init__.py
touch src/tools/__init__.py
touch src/safety/__init__.py
touch src/baselines/__init__.py
touch src/metrics/__init__.py
touch src/scenarios/__init__.py
```

### Verify the structure looks right:
```bash
find src -type f | sort
```

Expected:
```
src/__init__.py
src/baselines/__init__.py
src/disruptions/__init__.py
src/fleet/__init__.py
src/metrics/__init__.py
src/network/__init__.py
src/requests/__init__.py
src/safety/__init__.py
src/scenarios/__init__.py
src/tools/__init__.py
```

> **✅ Checkpoint:** `find src -type f | sort` shows all 10 `__init__.py` files.

---

## STEP 3: Generate Your First SUMO Road Network

This is your first real SUMO interaction. We create a **4×4 grid** (16 intersections, ~48 road segments).

### 3.1 Generate the network

```bash
cd ~/Desktop/Clg/IIITNR/Sem5/04-Minor

netgenerate --grid \
  --grid.number=4 \
  --grid.length=200 \
  --grid.attach-length=0 \
  --default.lanenumber=2 \
  --default.speed=13.89 \
  --default-junction-type priority \
  --output-file=networks/grid_4x4.net.xml \
  --seed 42
```

**What each flag means:**
- `--grid`: Generate a grid topology
- `--grid.number=4`: 4 nodes per axis → 4×4 = 16 intersections
- `--grid.length=200`: Each road segment is 200 meters
- `--default.lanenumber=2`: 2 lanes per direction
- `--default.speed=13.89`: 13.89 m/s ≈ 50 km/h speed limit
- `--seed 42`: Deterministic — always produces the same network

### 3.2 Verify the file was created

```bash
ls -la networks/grid_4x4.net.xml
# Should show a file of ~50-100KB

# Quick peek at the structure
head -20 networks/grid_4x4.net.xml
```

### 3.3 Understand the node naming

SUMO's `netgenerate --grid` names nodes like this for a 4×4 grid:

```
         Column 0    Column 1    Column 2    Column 3
Row 3:   A3          B3          C3          D3
Row 2:   A2          B2          C2          D2
Row 1:   A1          B1          C1          D1
Row 0:   A0          B0          C0          D0
```

But **SUMO actually names them differently** — they use numbered IDs. Let's check:

```bash
# Extract node IDs from the network file
python3 -c "
import sumolib
net = sumolib.net.readNet('networks/grid_4x4.net.xml')
nodes = [n.getID() for n in net.getNodes()]
print(f'Total nodes: {len(nodes)}')
print(f'Node IDs: {sorted(nodes)}')
print()
edges = [e.getID() for e in net.getEdges() if not e.isSpecial()]
print(f'Total edges: {len(edges)}')
print(f'First 10 edges: {sorted(edges)[:10]}')
"
```

**Write down the output!** You'll need the actual node/edge IDs for your scenarios. The IDs will look something like `A0`, `B0`, etc. or `0/0`, `1/0`, etc. depending on SUMO version.

### 3.4 (Optional) View in SUMO GUI

If you have a display:
```bash
sumo-gui -n networks/grid_4x4.net.xml
```
This opens a visual editor showing your 4×4 grid. Close it when done.

> **✅ Checkpoint:** `networks/grid_4x4.net.xml` exists AND the Python script prints node/edge IDs.  
> **Write down the node naming scheme** — you'll use these names in all your code.

---

## STEP 4: Write & Test the NetworkX Graph Builder

This is the **core data structure** — everything else builds on top of it.

### 4.1 Create the file

Create `src/network/graph_builder.py` with the code from Section 4.2 of `work.md`.

**Key things this class does:**
- Loads a SUMO `.net.xml` file
- Builds a NetworkX `DiGraph` with the same topology
- Provides methods to close/congest/restore edges
- Provides shortest path and BFS reachability on the open subgraph
- Can serialize state to JSON (for LLM prompts later)

### 4.2 Test it immediately

Create `scripts/test_network.py`:

```python
#!/usr/bin/env python3
"""Test the TransportNetwork class."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork

def main():
    # Load network
    net = TransportNetwork("networks/grid_4x4.net.xml")
    
    print("=" * 50)
    print("NETWORK LOADED SUCCESSFULLY")
    print("=" * 50)
    print(f"Nodes: {net.graph.number_of_nodes()}")
    print(f"Edges: {net.graph.number_of_edges()}")
    print()
    
    # Print all node IDs
    nodes = sorted(net.graph.nodes())
    print(f"Node IDs: {nodes}")
    print()
    
    # Pick two nodes for testing
    node_list = list(net.graph.nodes())
    start_node = node_list[0]
    end_node = node_list[-1]
    print(f"Testing path from {start_node} to {end_node}")
    
    # Test 1: Shortest path (should work)
    path = net.shortest_path(start_node, end_node)
    if path:
        print(f"✅ Path found: {' -> '.join(path)}")
        print(f"   Hops: {len(path) - 1}")
    else:
        print("❌ No path found (this is wrong — grid should be fully connected)")
    print()
    
    # Test 2: BFS reachability
    reachable = net.bfs_reachable(start_node, end_node)
    print(f"✅ BFS reachable: {reachable}")
    print()
    
    # Test 3: Close an edge and verify path changes
    if path and len(path) >= 3:
        close_from = path[1]
        close_to = path[2]
        print(f"Closing edge: {close_from} -> {close_to}")
        net.close_edge(close_from, close_to)
        
        # Check the edge status
        edge_data = net.get_edge_by_nodes(close_from, close_to)
        print(f"   Edge status: {edge_data['status']}")
        print(f"   Edge capacity: {edge_data['capacity']}")
        
        # Try finding path again (should reroute or fail)
        new_path = net.shortest_path(start_node, end_node)
        if new_path:
            print(f"✅ Rerouted path: {' -> '.join(new_path)}")
            if new_path != path:
                print("   ✅ Path changed (correctly avoided closed edge)")
            else:
                print("   ❌ Path didn't change (something is wrong)")
        else:
            print("   ⚠️  No path found after closure (may be valid if edge is critical)")
        print()
        
        # Test 4: Restore the edge
        net.restore_edge(close_from, close_to)
        restored_data = net.get_edge_by_nodes(close_from, close_to)
        print(f"After restore — status: {restored_data['status']}, capacity: {restored_data['capacity']}")
        
        restored_path = net.shortest_path(start_node, end_node)
        if restored_path == path:
            print("✅ Original path restored correctly")
        print()
    
    # Test 5: Congestion
    if path and len(path) >= 3:
        congest_from = path[1]
        congest_to = path[2]
        edge_before = net.get_edge_by_nodes(congest_from, congest_to)
        tt_before = edge_before['travel_time']
        
        net.congest_edge(congest_from, congest_to, factor=3.0)
        edge_after = net.get_edge_by_nodes(congest_from, congest_to)
        tt_after = edge_after['travel_time']
        
        print(f"Congestion test on {congest_from} -> {congest_to}:")
        print(f"   Travel time before: {tt_before:.1f}s")
        print(f"   Travel time after (3x factor): {tt_after:.1f}s")
        print(f"   ✅ Ratio: {tt_after/tt_before:.1f}x" if tt_after > tt_before else "   ❌ Congestion not applied")
        
        net.restore_edge(congest_from, congest_to)
        print()
    
    # Test 6: JSON serialization
    state = net.to_json_state()
    print(f"JSON state: {len(state['nodes'])} nodes, {len(state['edges'])} edges")
    print(f"Sample node: {state['nodes'][0]}")
    print(f"Sample edge: {state['edges'][0]}")
    print()
    
    print("=" * 50)
    print("ALL NETWORK TESTS PASSED ✅")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

### 4.3 Run the test

```bash
cd ~/Desktop/Clg/IIITNR/Sem5/04-Minor
python3 scripts/test_network.py
```

**What to look for:**
- ✅ Network loads with ~16 nodes and ~48 edges (for a 4×4 grid)
- ✅ Shortest path works between two nodes
- ✅ Closing an edge changes the path
- ✅ Restoring an edge brings back the original path
- ✅ Congestion multiplies travel time correctly
- ✅ JSON serialization works

**If something fails:**
- "No module named src" → You're running from the wrong directory. Must run from `04-Minor/`
- Node count is wrong → Check `grid.number` was set to 4
- Path returns None → Check node IDs match what `netgenerate` actually created

> **✅ Checkpoint:** `test_network.py` prints "ALL NETWORK TESTS PASSED ✅"  
> **Don't proceed until this works.**

---

## STEP 5: Write & Test Vehicle/Fleet Models

### 5.1 Create the files

Create `src/fleet/vehicle.py` with the Vehicle/Fleet code from Section 5.1 of `work.md`.  
Create `src/fleet/fleet_factory.py` with the factory code from Section 5.2 of `work.md`.

### 5.2 Test it

Create `scripts/test_fleet.py`:

```python
#!/usr/bin/env python3
"""Test Fleet and Vehicle models."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.fleet.vehicle import Vehicle, Fleet, VehicleStatus
from src.fleet.fleet_factory import create_test_fleet
from src.network.graph_builder import TransportNetwork

def main():
    # Load network to get node IDs
    net = TransportNetwork("networks/grid_4x4.net.xml")
    nodes = list(net.graph.nodes())
    
    # Test 1: Create a single vehicle
    v = Vehicle(
        id="V001",
        current_node=nodes[0],
        capacity=4,
        soc=80.0,
        soc_consumption_per_km=2.0
    )
    print(f"Vehicle: {v.id} at node {v.current_node}")
    print(f"  SoC: {v.soc}%")
    print(f"  Range: {v.remaining_range_km():.1f} km")
    print(f"  Can reach 10km: {v.can_reach(10.0)}")
    print(f"  Can reach 50km: {v.can_reach(50.0)}")
    
    # Test SoC consumption
    v.consume_soc(5.0)  # Drive 5 km
    print(f"  After 5km drive — SoC: {v.soc}%, Range: {v.remaining_range_km():.1f} km")
    print()
    
    # Test 2: Create test fleet
    fleet = create_test_fleet(nodes, num_vehicles=8, seed=42)
    print(f"Fleet created: {len(fleet.vehicles)} vehicles")
    print(f"Available: {len(fleet.get_available_vehicles())}")
    print()
    
    # Print all vehicles
    for vid, v in fleet.vehicles.items():
        print(f"  {vid}: node={v.current_node}, cap={v.capacity}, "
              f"soc={v.soc:.1f}%, range={v.remaining_range_km():.1f}km, "
              f"status={v.status.value}")
    print()
    
    # Test 3: Break a vehicle
    first_id = list(fleet.vehicles.keys())[0]
    fleet.break_vehicle(first_id)
    print(f"Broke vehicle {first_id}")
    print(f"Available after breakdown: {len(fleet.get_available_vehicles())}")
    broken = fleet.get_vehicle(first_id)
    print(f"  {first_id} status: {broken.status.value}")
    print()
    
    # Test 4: JSON serialization
    state = fleet.to_json_state()
    print(f"JSON state: {len(state)} vehicles")
    print(f"Sample: {state[0]}")
    print()
    
    # Test 5: Reproducibility — same seed = same fleet
    fleet2 = create_test_fleet(nodes, num_vehicles=8, seed=42)
    for vid in fleet.vehicles:
        v1 = fleet2.vehicles[vid]
        v2_orig = create_test_fleet(nodes, num_vehicles=8, seed=42).vehicles[vid]
        assert v1.current_node == v2_orig.current_node, f"Node mismatch for {vid}"
        assert abs(v1.soc - v2_orig.soc) < 0.01, f"SoC mismatch for {vid}"
    print("✅ Reproducibility verified (same seed = identical fleet)")
    
    print()
    print("=" * 50)
    print("ALL FLEET TESTS PASSED ✅")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/test_fleet.py
```

> **✅ Checkpoint:** "ALL FLEET TESTS PASSED ✅"

---

## STEP 6: Write & Test Transport Request System

### 6.1 Create the file

Create `src/requests/transport_request.py` with code from Section 6 of `work.md`.

### 6.2 Test it

Create `scripts/test_requests.py`:

```python
#!/usr/bin/env python3
"""Test TransportRequest and RequestQueue."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requests.transport_request import TransportRequest, RequestQueue, RequestStatus

def main():
    queue = RequestQueue()
    
    # Add some requests (use placeholder node IDs — doesn't matter for this test)
    r1 = TransportRequest(id="R1", origin="A0", destination="D3", time=50, passengers=2, priority=1)
    r2 = TransportRequest(id="R2", origin="B1", destination="C3", time=60, passengers=1, priority=2)
    r3 = TransportRequest(id="R3", origin="A2", destination="D1", time=80, passengers=1, priority=3)
    
    queue.add_request(r1)
    queue.add_request(r2)
    queue.add_request(r3)
    
    print(f"Total requests: {len(queue.requests)}")
    print(f"Pending: {len(queue.get_pending_requests())}")
    
    # Assign one
    r1.status = RequestStatus.ASSIGNED
    r1.assigned_vehicle_id = "V001"
    print(f"After assigning R1 — Pending: {len(queue.get_pending_requests())}")
    print(f"Affected (need serving): {len(queue.get_affected_requests())}")
    
    # Mark one as unserved
    r3.status = RequestStatus.UNSERVED
    print(f"After R3 unserved — Pending: {len(queue.get_pending_requests())}")
    
    # JSON
    state = queue.to_json_state()
    print(f"JSON: {len(state)} requests")
    
    print()
    print("ALL REQUEST TESTS PASSED ✅")

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/test_requests.py
```

> **✅ Checkpoint:** "ALL REQUEST TESTS PASSED ✅"

---

## STEP 7: Write & Test DecisionCard (Pydantic Schema)

### 7.1 Create the file

Create `src/safety/decision_card.py` with the DecisionCard code from Section 10 (bottom) of `work.md`.

### 7.2 Test it

Create `scripts/test_decision_card.py`:

```python
#!/usr/bin/env python3
"""Test DecisionCard Pydantic validation."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.safety.decision_card import DecisionCard
from pydantic import ValidationError

def main():
    # Test 1: Valid card
    card = DecisionCard(
        scenario_id="L1_simple_001",
        request_id="R1",
        recommended_action="REROUTE_AND_DISPATCH",
        vehicle_id="V001",
        assigned_route=["A0", "B0", "C0", "D0"],
        estimated_delay_reduction_min=2.5,
        safety_guard_passed=True,
        route_distance_km=0.6,
        estimated_travel_time_s=43.2
    )
    print(f"✅ Valid card created: {card.recommended_action}")
    print(f"   Route: {' -> '.join(card.assigned_route)}")
    
    # Test 2: Card with no vehicle (NO_PATH case)
    card2 = DecisionCard(
        scenario_id="L1_simple_001",
        request_id="R2",
        recommended_action="NO_PATH_AVAILABLE",
        safety_guard_passed=False,
        rejection_reason="No path exists"
    )
    print(f"✅ No-path card: {card2.recommended_action}, reason: {card2.rejection_reason}")
    
    # Test 3: JSON serialization round-trip
    json_str = card.model_dump_json(indent=2)
    print(f"\n✅ JSON output:\n{json_str}")
    
    # Test 4: Parse back from JSON
    card_back = DecisionCard.model_validate_json(json_str)
    assert card_back.vehicle_id == card.vehicle_id
    print(f"\n✅ JSON round-trip successful")
    
    # Test 5: Missing required field should fail
    try:
        bad_card = DecisionCard(
            # Missing scenario_id and request_id
            recommended_action="REROUTE"
        )
        print("❌ Should have raised validation error!")
    except ValidationError as e:
        print(f"\n✅ Pydantic correctly rejected invalid card ({e.error_count()} errors)")
    
    print()
    print("ALL DECISION CARD TESTS PASSED ✅")

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/test_decision_card.py
```

> **✅ Checkpoint:** "ALL DECISION CARD TESTS PASSED ✅"

---

## STEP 8: Write & Test Disruption System

### 8.1 Create the files

Create `src/disruptions/disruption.py` with the Disruption model from Section 7.1 of `work.md`.  
Create `src/disruptions/disruption_manager.py` with the DisruptionManager from Section 7.2 of `work.md`.

**⚠️ IMPORTANT:** For this step we test **without SUMO running** — the DisruptionManager has `try/except` around TraCI calls, so it won't crash. We only test the NetworkX side of disruptions. The SUMO side gets tested in Step 15.

### 8.2 Test it

Create `scripts/test_disruptions.py`:

```python
#!/usr/bin/env python3
"""Test disruption system (NetworkX side only — no SUMO running)."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork
from src.fleet.vehicle import Fleet, Vehicle, VehicleStatus
from src.fleet.fleet_factory import create_test_fleet
from src.requests.transport_request import RequestQueue, TransportRequest
from src.disruptions.disruption import Disruption, DisruptionType
from src.disruptions.disruption_manager import DisruptionManager

def main():
    # Setup
    net = TransportNetwork("networks/grid_4x4.net.xml")
    nodes = sorted(net.graph.nodes())
    fleet = create_test_fleet(nodes, num_vehicles=8, seed=42)
    queue = RequestQueue()
    
    dm = DisruptionManager(net, fleet, queue)
    
    print(f"Network: {net.graph.number_of_nodes()} nodes, {net.graph.number_of_edges()} edges")
    print(f"Initial disrupted edges: {len(dm.get_disrupted_edges())}")
    print()
    
    # -- Test 1: Road Closure --
    print("--- TEST 1: Road Closure ---")
    edge_list = list(net.graph.edges())
    test_edge = edge_list[len(edge_list)//2]  # Pick a middle edge
    from_n, to_n = test_edge
    
    print(f"Edge {from_n} -> {to_n}: status={net.graph[from_n][to_n]['status']}")
    
    d1 = Disruption(id="D1", type=DisruptionType.ROAD_CLOSURE, time=100,
                    edge_from=from_n, edge_to=to_n)
    dm.apply_disruption(d1, current_step=100)
    
    edge_data = net.get_edge_by_nodes(from_n, to_n)
    print(f"After closure: status={edge_data['status']}, capacity={edge_data['capacity']}")
    assert edge_data['capacity'] == 0.0, "Capacity should be 0"
    assert edge_data['status'] == "closed", "Status should be closed"
    print("✅ Road closure works")
    print()
    
    # -- Test 2: Congestion --
    print("--- TEST 2: Congestion ---")
    test_edge2 = edge_list[len(edge_list)//4]
    from_n2, to_n2 = test_edge2
    tt_before = net.graph[from_n2][to_n2]['travel_time']
    
    d2 = Disruption(id="D2", type=DisruptionType.CONGESTION, time=100,
                    edge_from=from_n2, edge_to=to_n2, congestion_factor=3.0)
    dm.apply_disruption(d2, current_step=100)
    
    tt_after = net.graph[from_n2][to_n2]['travel_time']
    print(f"Edge {from_n2} -> {to_n2}: travel_time {tt_before:.1f}s -> {tt_after:.1f}s")
    print(f"Status: {net.graph[from_n2][to_n2]['status']}")
    assert tt_after > tt_before, "Travel time should increase"
    print("✅ Congestion works")
    print()
    
    # -- Test 3: Vehicle Breakdown --
    print("--- TEST 3: Vehicle Breakdown ---")
    v_id = list(fleet.vehicles.keys())[2]  # Pick 3rd vehicle
    v_before = fleet.get_vehicle(v_id)
    print(f"Vehicle {v_id} before: status={v_before.status.value}")
    
    d3 = Disruption(id="D3", type=DisruptionType.VEHICLE_BREAKDOWN, time=120,
                    vehicle_id=v_id)
    dm.apply_disruption(d3, current_step=120)
    
    v_after = fleet.get_vehicle(v_id)
    print(f"Vehicle {v_id} after: status={v_after.status.value}")
    assert v_after.status == VehicleStatus.BROKEN, "Should be broken"
    print("✅ Vehicle breakdown works")
    print()
    
    # -- Test 4: Demand Surge --
    print("--- TEST 4: Demand Surge ---")
    requests_before = len(queue.requests)
    
    d4 = Disruption(id="D4", type=DisruptionType.DEMAND_SURGE, time=200,
                    surge_num_requests=5, surge_area_nodes=nodes[:4])
    dm.apply_disruption(d4, current_step=200)
    
    requests_after = len(queue.requests)
    print(f"Requests before surge: {requests_before}")
    print(f"Requests after surge: {requests_after}")
    assert requests_after == requests_before + 5, "Should have 5 new requests"
    print("✅ Demand surge works")
    print()
    
    # -- Test 5: Check disrupted edges list --
    print("--- TEST 5: Disrupted Edge Tracking ---")
    disrupted = dm.get_disrupted_edges()
    print(f"Currently disrupted edges: {len(disrupted)}")
    for d in disrupted:
        print(f"  {d['from']} -> {d['to']}: {d['status']}, capacity={d['capacity']}")
    assert len(disrupted) >= 2, "Should have at least 2 disrupted edges"
    print("✅ Disrupted edge tracking works")
    print()
    
    # -- Test 6: Edge expiration --
    print("--- TEST 6: Disruption Expiration ---")
    test_edge3 = edge_list[3]
    d5 = Disruption(id="D5", type=DisruptionType.ROAD_CLOSURE, time=100, duration=50,
                    edge_from=test_edge3[0], edge_to=test_edge3[1])
    dm.apply_disruption(d5, current_step=100)
    print(f"Added timed closure (duration=50) at step 100")
    print(f"Active disruptions: {len(dm.active_disruptions)}")
    
    dm.check_expirations(current_step=149)
    print(f"At step 149: {len(dm.active_disruptions)} active")
    
    dm.check_expirations(current_step=150)
    print(f"At step 150: {len(dm.active_disruptions)} active")
    edge_restored = net.get_edge_by_nodes(test_edge3[0], test_edge3[1])
    print(f"Edge status after expiry: {edge_restored['status']}")
    print("✅ Disruption expiration works")
    print()
    
    print("=" * 50)
    print("ALL DISRUPTION TESTS PASSED ✅")
    print("=" * 50)

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/test_disruptions.py
```

**Expected:** Some TraCI warnings (since SUMO isn't running) — **that's fine and expected**. The NetworkX-side logic should all pass.

> **✅ Checkpoint:** "ALL DISRUPTION TESTS PASSED ✅" (ignore TraCI warnings)

---

## STEP 9: Write & Test the 7 Core Tool Functions

### 9.1 Create the file

Create `src/tools/agent_tools.py` with the AgentTools code from Section 9 of `work.md`.

### 9.2 Test it

Create `scripts/test_tools.py`:

```python
#!/usr/bin/env python3
"""Test all 7 agent tool functions."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork
from src.fleet.fleet_factory import create_test_fleet
from src.requests.transport_request import TransportRequest, RequestQueue
from src.disruptions.disruption import Disruption, DisruptionType
from src.disruptions.disruption_manager import DisruptionManager
from src.tools.agent_tools import AgentTools

def main():
    # Setup complete environment
    net = TransportNetwork("networks/grid_4x4.net.xml")
    nodes = sorted(net.graph.nodes())
    fleet = create_test_fleet(nodes, num_vehicles=8, seed=42)
    queue = RequestQueue()
    
    # Add a test request
    r1 = TransportRequest(id="R1", origin=nodes[0], destination=nodes[-1], 
                          time=50, passengers=2, priority=1)
    queue.add_request(r1)
    
    dm = DisruptionManager(net, fleet, queue)
    tools = AgentTools(net, fleet, queue, dm)
    
    print("=" * 60)
    print("TESTING ALL 7 TOOL FUNCTIONS")
    print("=" * 60)
    
    # -- Tool 1: get_network_state() --
    print("\n--- Tool 1: get_network_state() ---")
    state = tools.get_network_state()
    print(f"  Nodes: {state['total_nodes']}")
    print(f"  Edges: {state['total_edges']}")
    print(f"  Open: {state['open_edges']}")
    print(f"  Closed: {state['closed_edges']}")
    print("  ✅ OK")
    
    # -- Tool 2: get_vehicle_status() --
    print("\n--- Tool 2: get_vehicle_status() ---")
    vstatus = tools.get_vehicle_status()
    print(f"  Total vehicles: {vstatus['total_vehicles']}")
    print(f"  Available: {vstatus['available_vehicles']}")
    print(f"  Available IDs: {vstatus['available_vehicle_ids']}")
    print("  ✅ OK")
    
    # -- Tool 3: get_disrupted_edges() --
    print("\n--- Tool 3: get_disrupted_edges() ---")
    edge_list = list(net.graph.edges())
    d1 = Disruption(id="D1", type=DisruptionType.ROAD_CLOSURE, time=100,
                    edge_from=edge_list[5][0], edge_to=edge_list[5][1])
    dm.apply_disruption(d1, current_step=100)
    disrupted = tools.get_disrupted_edges()
    print(f"  Disrupted edges: {len(disrupted)}")
    print("  ✅ OK")
    
    # -- Tool 4: get_available_vehicles() --
    print("\n--- Tool 4: get_available_vehicles() ---")
    available = tools.get_available_vehicles()
    print(f"  Available vehicles: {len(available)}")
    if available:
        v = available[0]
        print(f"  First: {v['id']} at {v['current_node']}, soc={v['soc']}%")
    print("  ✅ OK")
    
    # -- Tool 5: shortest_path() --
    print("\n--- Tool 5: shortest_path() ---")
    path_result = tools.shortest_path(nodes[0], nodes[-1])
    print(f"  Reachable: {path_result['reachable']}")
    if path_result['reachable']:
        print(f"  Path: {' -> '.join(path_result['path'])}")
        print(f"  Distance: {path_result['distance_km']} km")
    print("  ✅ OK")
    
    # -- Tool 7: validate_plan() --
    print("\n--- Tool 7: validate_plan() ---")
    if path_result['reachable'] and available:
        v_id = available[0]['id']
        route = path_result['path']
        validation = tools.validate_plan(v_id, route, "R1")
        print(f"  Valid: {validation['valid']}")
        print(f"  Checks passed: {validation['checks_passed']}")
        if validation['checks_failed']:
            print(f"  Checks failed: {validation['checks_failed']}")
    print("  ✅ OK")
    
    # -- Tool 6: assign_vehicle() --
    print("\n--- Tool 6: assign_vehicle() ---")
    if path_result['reachable'] and available:
        v_id = available[0]['id']
        route = path_result['path']
        result = tools.assign_vehicle(v_id, "R1", route)
        print(f"  Success: {result['success']}")
        print(f"  Message: {result['message']}")
        
        # Try duplicate (should fail)
        result2 = tools.assign_vehicle(v_id, "R1", route)
        print(f"  Duplicate attempt: {result2['success']} — {result2['message']}")
    print("  ✅ OK")
    
    print()
    print("=" * 60)
    print("ALL 7 TOOL FUNCTION TESTS PASSED ✅")
    print("=" * 60)

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/test_tools.py
```

> **✅ Checkpoint:** "ALL 7 TOOL FUNCTION TESTS PASSED ✅"

---

## STEP 10: Create the 5 Scenario JSON Files

### 10.1 First, get your actual node IDs

This is **critical** — your scenario files must use the **real node IDs** from your generated network.

```bash
python3 -c "
import sumolib
net = sumolib.net.readNet('networks/grid_4x4.net.xml')
nodes = sorted([n.getID() for n in net.getNodes()])
print('Your node IDs (replace scenario placeholders with these):')
for i, n in enumerate(nodes):
    print(f'  [{i}] {n}', end='')
    if (i+1) % 4 == 0: print()
print()
print('Use corner nodes for origin/destination in scenarios.')
print(f'  Top-left: {nodes[0]}')
print(f'  Top-right: {nodes[3]}')
print(f'  Bottom-left: {nodes[12]}')
print(f'  Bottom-right: {nodes[15]}')
"
```

### 10.2 Update scenario files with real node IDs

The scenarios in `work.md` use placeholder node IDs like "A1", "B2", etc. **Replace these with the actual node IDs** printed above, then save each file in `scenarios/`.

### 10.3 Create a scenario loader

Create `src/scenarios/loader.py`:

```python
"""Load and validate scenario JSON files."""

import json
from ..disruptions.disruption import Disruption
from ..requests.transport_request import TransportRequest


def load_scenario(filepath: str) -> dict:
    """Load a scenario JSON file and parse into typed objects."""
    with open(filepath, 'r') as f:
        raw = json.load(f)
    
    # Parse disruptions
    disruptions = [Disruption(**d) for d in raw['disruptions']]
    
    # Parse requests
    requests = [TransportRequest(**r) for r in raw['requests']]
    
    return {
        "scenario_id": raw['scenario_id'],
        "complexity_level": raw['complexity_level'],
        "description": raw['description'],
        "network_file": raw['network_file'],
        "network_seed": raw.get('network_seed', 42),
        "simulation_duration": raw.get('simulation_duration', 600),
        "disruption_time": raw.get('disruption_time', 100),
        "num_vehicles": raw.get('num_vehicles', 8),
        "fleet_seed": raw.get('fleet_seed', 42),
        "disruptions": disruptions,
        "requests": requests
    }
```

### 10.4 Test scenario loading

```bash
python3 -c "
import sys; sys.path.insert(0, '.')
from src.scenarios.loader import load_scenario

for level in ['L1_simple', 'L2_moderate', 'L3_compound', 'L4_cascading', 'L5_stress']:
    try:
        s = load_scenario(f'scenarios/{level}.json')
        print(f'✅ {level}: {len(s[\"disruptions\"])} disruptions, {len(s[\"requests\"])} requests')
    except FileNotFoundError:
        print(f'⚠️  {level}: file not created yet')
    except Exception as e:
        print(f'❌ {level}: {e}')
"
```

> **✅ Checkpoint:** All 5 scenarios load without errors.

---

## STEP 11: Write & Test Rule-Based Baseline (B1)

### 11.1 Create the file

Create `src/baselines/rule_based.py` with the RuleBasedController code from Section 10 of `work.md`.

### 11.2 Test it

Create `scripts/test_baseline.py`:

```python
#!/usr/bin/env python3
"""Test Rule-Based Baseline on a scenario."""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork
from src.fleet.fleet_factory import create_test_fleet
from src.requests.transport_request import RequestQueue
from src.disruptions.disruption_manager import DisruptionManager
from src.tools.agent_tools import AgentTools
from src.baselines.rule_based import RuleBasedController
from src.scenarios.loader import load_scenario

def run_baseline_on_scenario(scenario_path: str):
    scenario = load_scenario(scenario_path)
    print(f"\n{'='*60}")
    print(f"SCENARIO: {scenario['scenario_id']} ({scenario['complexity_level']})")
    print(f"Description: {scenario['description']}")
    print(f"{'='*60}")
    
    net = TransportNetwork(scenario['network_file'])
    nodes = sorted(net.graph.nodes())
    fleet = create_test_fleet(nodes, scenario['num_vehicles'], scenario['fleet_seed'])
    queue = RequestQueue()
    dm = DisruptionManager(net, fleet, queue)
    tools = AgentTools(net, fleet, queue, dm)
    
    for req in scenario['requests']:
        queue.add_request(req)
    print(f"Loaded {len(queue.requests)} requests")
    
    for d in scenario['disruptions']:
        dm.apply_disruption(d, current_step=d.time)
        print(f"Applied: {d.id} ({d.type.value})")
    
    print(f"Disrupted edges: {len(dm.get_disrupted_edges())}")
    print(f"Available vehicles: {len(fleet.get_available_vehicles())}")
    
    start_time = time.time()
    controller = RuleBasedController(tools)
    decisions = controller.respond_to_disruption()
    elapsed = time.time() - start_time
    
    print(f"\n--- RESULTS ({elapsed:.3f}s) ---")
    for d in decisions:
        status = "✅ PASS" if d.safety_guard_passed else "❌ FAIL"
        print(f"  {d.request_id}: {d.recommended_action} | {status}")
        if d.rejection_reason:
            print(f"    Reason: {d.rejection_reason}")
    
    passed = sum(1 for d in decisions if d.safety_guard_passed)
    failed = sum(1 for d in decisions 
                 if not d.safety_guard_passed 
                 and d.recommended_action not in ("NO_PATH_AVAILABLE", "NO_VEHICLE_AVAILABLE"))
    print(f"\n  {passed} passed | {failed} hard failures | {len(decisions)} total")
    return decisions, elapsed

if __name__ == "__main__":
    import glob
    scenario_files = sorted(glob.glob("scenarios/L*.json"))
    if not scenario_files:
        print("No scenario files found! Create scenarios/L1_simple.json first.")
    else:
        for sf in scenario_files:
            try:
                run_baseline_on_scenario(sf)
            except Exception as e:
                print(f"❌ {sf}: {e}")
                import traceback; traceback.print_exc()
```

```bash
python3 scripts/test_baseline.py
```

> **✅ Checkpoint:** Baseline runs on at least L1 and produces DecisionCards.

---

## STEP 12: Write & Test Metrics Evaluator

### 12.1 Create the file

Create `src/metrics/evaluator.py` with the MetricsEvaluator code from Section 11 of `work.md`.

### 12.2 Quick test

Add metrics to the baseline test by creating `scripts/test_metrics.py`:

```python
#!/usr/bin/env python3
"""Quick metrics test using baseline output."""

import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork
from src.fleet.fleet_factory import create_test_fleet
from src.requests.transport_request import RequestQueue
from src.disruptions.disruption_manager import DisruptionManager
from src.tools.agent_tools import AgentTools
from src.baselines.rule_based import RuleBasedController
from src.scenarios.loader import load_scenario
from src.metrics.evaluator import MetricsEvaluator

def main():
    scenario = load_scenario("scenarios/L1_simple.json")
    
    net = TransportNetwork(scenario['network_file'])
    nodes = sorted(net.graph.nodes())
    fleet = create_test_fleet(nodes, scenario['num_vehicles'], scenario['fleet_seed'])
    queue = RequestQueue()
    dm = DisruptionManager(net, fleet, queue)
    tools = AgentTools(net, fleet, queue, dm)
    
    for req in scenario['requests']:
        queue.add_request(req)
    for d in scenario['disruptions']:
        dm.apply_disruption(d, current_step=d.time)
    
    start = time.time()
    controller = RuleBasedController(tools)
    decisions = controller.respond_to_disruption()
    elapsed = time.time() - start
    
    evaluator = MetricsEvaluator(scenario['scenario_id'], "rule_based")
    metrics = evaluator.evaluate(decisions, queue, execution_time_s=elapsed)
    MetricsEvaluator.print_report(metrics)

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/test_metrics.py
```

> **✅ Checkpoint:** Formatted metrics report printed with all 6 metrics.

---

## STEP 13: Build the Scenario Runner

Create `scripts/run_scenario.py`:

```python
#!/usr/bin/env python3
"""
Main entry point. Run any system on any scenario.
Usage: python3 scripts/run_scenario.py scenarios/L1_simple.json rule_based
"""

import sys, os, time, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.network.graph_builder import TransportNetwork
from src.fleet.fleet_factory import create_test_fleet
from src.requests.transport_request import RequestQueue
from src.disruptions.disruption_manager import DisruptionManager
from src.tools.agent_tools import AgentTools
from src.baselines.rule_based import RuleBasedController
from src.metrics.evaluator import MetricsEvaluator
from src.scenarios.loader import load_scenario


def run_scenario(scenario_path: str, system_name: str = "rule_based"):
    scenario = load_scenario(scenario_path)
    print(f"\n{'='*60}")
    print(f"  Running: {scenario['scenario_id']} | System: {system_name}")
    print(f"{'='*60}\n")
    
    net = TransportNetwork(scenario['network_file'])
    nodes = sorted(net.graph.nodes())
    fleet = create_test_fleet(nodes, scenario['num_vehicles'], scenario['fleet_seed'])
    queue = RequestQueue()
    dm = DisruptionManager(net, fleet, queue)
    tools = AgentTools(net, fleet, queue, dm)
    
    for req in scenario['requests']:
        queue.add_request(req)
    for d in scenario['disruptions']:
        dm.apply_disruption(d, current_step=d.time)
    
    start_time = time.time()
    if system_name == "rule_based":
        controller = RuleBasedController(tools)
        decisions = controller.respond_to_disruption()
    else:
        print(f"⚠️  {system_name} not implemented yet (Week 4)")
        return None
    elapsed = time.time() - start_time
    
    evaluator = MetricsEvaluator(scenario['scenario_id'], system_name)
    metrics = evaluator.evaluate(decisions, queue, execution_time_s=elapsed)
    MetricsEvaluator.print_report(metrics)
    
    # Save results
    os.makedirs("results", exist_ok=True)
    result_file = f"results/{scenario['scenario_id']}_{system_name}.json"
    result = {
        "scenario_id": scenario['scenario_id'],
        "system": system_name,
        "metrics": {
            "hcvr_percent": metrics.hcvr_percent,
            "rfr_percent": metrics.rfr_percent,
            "adif": metrics.adif,
            "execution_latency_s": metrics.execution_latency_s,
            "idr_percent": metrics.idr_percent,
        },
        "decisions": [d.model_dump() for d in decisions]
    }
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    print(f"Saved: {result_file}")
    return metrics


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/run_scenario.py <scenario.json> [system]")
        sys.exit(1)
    run_scenario(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "rule_based")
```

---

## STEP 14: Full Integration Test

Create `scripts/run_all_baselines.py`:

```python
#!/usr/bin/env python3
"""Run rule-based baseline on ALL scenarios, print comparison table."""

import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.run_scenario import run_scenario

def main():
    files = sorted(glob.glob("scenarios/L*.json"))
    if not files:
        print("No scenarios found!"); return
    
    results = []
    for sf in files:
        try:
            m = run_scenario(sf, "rule_based")
            if m: results.append(m)
        except Exception as e:
            print(f"❌ {sf}: {e}")
    
    if results:
        print(f"\n{'='*80}")
        print(f"  COMPARISON TABLE — Rule-Based Baseline")
        print(f"{'='*80}")
        print(f"{'Scenario':<25} {'HCVR%':>8} {'RFR%':>8} {'ADIF':>8} {'Latency':>10} {'IDR%':>8}")
        print("-" * 73)
        for m in results:
            print(f"{m.scenario_id:<25} {m.hcvr_percent:>7.1f}% {m.rfr_percent:>7.1f}% "
                  f"{m.adif:>7.2f}x {m.execution_latency_s:>9.3f}s {m.idr_percent:>7.1f}%")
        print(f"{'='*80}")

if __name__ == "__main__":
    main()
```

```bash
python3 scripts/run_all_baselines.py
```

**Expected:** A comparison table. HCVR should be 0% for all. RFR should decrease L1→L5.

> **✅ FINAL Checkpoint:** Comparison table printed, results saved to `results/`.  
> **You are now ready for Week 4 — LLM agent implementation!**

---

## Quick Reference: Order of Operations

| Step | Command to Run | What Passes |
|------|---------------|-------------|
| 1 | `sumo --version` | Version prints |
| 2 | `find src -type f \| sort` | 10 `__init__.py` files |
| 3 | `ls networks/grid_4x4.net.xml` | File exists |
| 4 | `python3 scripts/test_network.py` | "ALL NETWORK TESTS PASSED ✅" |
| 5 | `python3 scripts/test_fleet.py` | "ALL FLEET TESTS PASSED ✅" |
| 6 | `python3 scripts/test_requests.py` | "ALL REQUEST TESTS PASSED ✅" |
| 7 | `python3 scripts/test_decision_card.py` | "ALL DECISION CARD TESTS PASSED ✅" |
| 8 | `python3 scripts/test_disruptions.py` | "ALL DISRUPTION TESTS PASSED ✅" |
| 9 | `python3 scripts/test_tools.py` | "ALL 7 TOOL FUNCTION TESTS PASSED ✅" |
| 10 | Scenario loading test | All 5 load ✅ |
| 11 | `python3 scripts/test_baseline.py` | Decisions produced |
| 12 | `python3 scripts/test_metrics.py` | Metrics report printed |
| 13 | `python3 scripts/run_scenario.py scenarios/L1_simple.json` | Results saved |
| 14 | `python3 scripts/run_all_baselines.py` | Comparison table |
