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
        
        # SUMO side — disallow all vehicle classes on all lanes of the edge (if SUMO is running)
        if traci.isLoaded():
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
                except (traci.TraCIException, traci.exceptions.FatalTraCIError) as e:
                    print(f"Warning: Could not apply SUMO closure for {edge_id}: {e}")
    
    def _apply_congestion(self, d: Disruption):
        """Increase travel time on an edge."""
        # NetworkX side
        self.network.congest_edge(d.edge_from, d.edge_to, d.congestion_factor)
        
        # SUMO side — reduce max speed (if SUMO is running)
        if traci.isLoaded():
            edge_data = self.network.get_edge_by_nodes(d.edge_from, d.edge_to)
            if edge_data:
                edge_id = edge_data['edge_id']
                try:
                    original_speed = edge_data['speed_limit']
                    new_speed = max(1.0, original_speed / d.congestion_factor)
                    traci.edge.setMaxSpeed(edge_id, new_speed)
                except (traci.TraCIException, traci.exceptions.FatalTraCIError) as e:
                    print(f"Warning: Could not apply SUMO congestion for {edge_id}: {e}")
    
    def _apply_vehicle_breakdown(self, d: Disruption):
        """Mark a vehicle as broken down."""
        self.fleet.break_vehicle(d.vehicle_id)
        
        # SUMO side — stop the vehicle (if SUMO is running)
        if traci.isLoaded():
            try:
                edge_id = traci.vehicle.getRoadID(d.vehicle_id)
                pos = traci.vehicle.getLanePosition(d.vehicle_id)
                traci.vehicle.setStop(d.vehicle_id, edgeID=edge_id, pos=pos, duration=100000)
            except (traci.TraCIException, traci.exceptions.FatalTraCIError) as e:
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
