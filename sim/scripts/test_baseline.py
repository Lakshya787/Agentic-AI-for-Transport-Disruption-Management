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
