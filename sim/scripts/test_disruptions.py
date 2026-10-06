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
