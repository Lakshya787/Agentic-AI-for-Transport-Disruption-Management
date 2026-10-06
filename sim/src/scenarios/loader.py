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
