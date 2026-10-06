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
