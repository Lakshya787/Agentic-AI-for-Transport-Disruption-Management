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
