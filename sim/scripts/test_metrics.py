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
