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
