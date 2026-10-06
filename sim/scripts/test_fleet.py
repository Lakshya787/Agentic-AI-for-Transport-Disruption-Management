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
