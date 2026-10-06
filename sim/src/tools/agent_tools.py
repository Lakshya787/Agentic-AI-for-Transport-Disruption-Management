# src/tools/agent_tools.py

"""
Seven core tool functions for the transport disruption environment.
These functions provide the interface between decision-makers (Rule-Based / LLM agents)
and the simulation state. All three systems use the SAME functions.
"""

from typing import Optional, List
from ..network.graph_builder import TransportNetwork
from ..fleet.vehicle import Fleet, Vehicle, VehicleStatus
from ..requests.transport_request import RequestQueue, TransportRequest, RequestStatus
from ..disruptions.disruption_manager import DisruptionManager
import networkx as nx


class AgentTools:
    """Unified tool interface for all agent types."""
    
    def __init__(self, network: TransportNetwork, fleet: Fleet, 
                 request_queue: RequestQueue, disruption_manager: DisruptionManager):
        self.network = network
        self.fleet = fleet
        self.request_queue = request_queue
        self.disruption_manager = disruption_manager
    
    # ─────────────────────────────────────────────
    # TOOL 1: get_network_state()
    # Used by: Traffic Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_network_state(self) -> dict:
        """Return current road network state including topology, capacities, and disruptions.
        
        Returns:
            dict with keys: nodes, edges, disrupted_edges, total_nodes, total_edges, open_edges
        """
        state = self.network.to_json_state()
        disrupted = self.disruption_manager.get_disrupted_edges()
        
        open_edges = sum(1 for _, _, d in self.network.graph.edges(data=True) if d['capacity'] > 0)
        
        return {
            "nodes": state["nodes"],
            "edges": state["edges"],
            "disrupted_edges": disrupted,
            "total_nodes": self.network.graph.number_of_nodes(),
            "total_edges": self.network.graph.number_of_edges(),
            "open_edges": open_edges,
            "closed_edges": self.network.graph.number_of_edges() - open_edges
        }
    
    # ─────────────────────────────────────────────
    # TOOL 2: get_vehicle_status()
    # Used by: Fleet Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_vehicle_status(self) -> dict:
        """Return current fleet status including all vehicle positions, SoC, and assignments.
        
        Returns:
            dict with keys: vehicles, total_vehicles, available_vehicles, broken_vehicles
        """
        vehicles = self.fleet.to_json_state()
        available = self.fleet.get_available_vehicles()
        broken = [v for v in self.fleet.vehicles.values() if v.status == VehicleStatus.BROKEN]
        
        return {
            "vehicles": vehicles,
            "total_vehicles": len(self.fleet.vehicles),
            "available_vehicles": len(available),
            "broken_vehicles": len(broken),
            "available_vehicle_ids": [v.id for v in available]
        }
    
    # ─────────────────────────────────────────────
    # TOOL 3: get_disrupted_edges()
    # Used by: Traffic Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_disrupted_edges(self) -> list[dict]:
        """Return list of all currently disrupted edges with their status and remaining capacity.
        
        Returns:
            list of dicts, each with: from, to, edge_id, status, capacity, travel_time
        """
        return self.disruption_manager.get_disrupted_edges()
    
    # ─────────────────────────────────────────────
    # TOOL 4: get_available_vehicles()
    # Used by: Fleet Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def get_available_vehicles(self) -> list[dict]:
        """Return list of vehicles that are idle, operational, and have sufficient SoC.
        
        Returns:
            list of dicts with: id, current_node, capacity, soc, remaining_range_km
        """
        available = self.fleet.get_available_vehicles()
        return [{
            "id": v.id,
            "current_node": v.current_node,
            "capacity": v.capacity,
            "current_passengers": v.current_passengers,
            "soc": round(v.soc, 1),
            "remaining_range_km": round(v.remaining_range_km(), 1)
        } for v in available]
    
    # ─────────────────────────────────────────────
    # TOOL 5: shortest_path()
    # Used by: Routing Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def shortest_path(self, origin: str, destination: str) -> dict:
        """Find shortest path between two nodes on the open (non-disrupted) subgraph.
        
        Args:
            origin: Source node ID
            destination: Target node ID
        
        Returns:
            dict with: path (list of nodes), distance_km, estimated_travel_time, reachable (bool)
        """
        path = self.network.shortest_path(origin, destination, weight='travel_time')
        
        if path is None:
            return {
                "origin": origin,
                "destination": destination,
                "reachable": False,
                "path": None,
                "distance_km": None,
                "estimated_travel_time": None,
                "num_hops": None
            }
        
        # Calculate total distance and travel time
        total_distance = 0.0
        total_time = 0.0
        for i in range(len(path) - 1):
            edge_data = self.network.graph[path[i]][path[i+1]]
            total_distance += edge_data['length']
            total_time += edge_data['travel_time']
        
        return {
            "origin": origin,
            "destination": destination,
            "reachable": True,
            "path": path,
            "distance_km": round(total_distance / 1000, 2),
            "estimated_travel_time": round(total_time, 1),
            "num_hops": len(path) - 1
        }
    
    # ─────────────────────────────────────────────
    # TOOL 6: assign_vehicle()
    # Used by: Coordinator Agent / Single-LLM / Rule-Based
    # ─────────────────────────────────────────────
    def assign_vehicle(self, vehicle_id: str, request_id: str, route: list[str]) -> dict:
        """Assign a vehicle to a transport request with a specific route.
        
        Args:
            vehicle_id: Vehicle to assign
            request_id: Request to fulfill
            route: List of node IDs forming the route
        
        Returns:
            dict with: success (bool), message, assignment details
        """
        vehicle = self.fleet.get_vehicle(vehicle_id)
        request = self.request_queue.requests.get(request_id)
        
        if not vehicle:
            return {"success": False, "message": f"Vehicle {vehicle_id} not found"}
        if not request:
            return {"success": False, "message": f"Request {request_id} not found"}
        if vehicle.status != VehicleStatus.IDLE:
            return {"success": False, "message": f"Vehicle {vehicle_id} is {vehicle.status.value}, not idle"}
        if request.status != RequestStatus.PENDING:
            return {"success": False, "message": f"Request {request_id} is {request.status.value}, not pending"}
        
        # Calculate route distance
        total_distance = 0.0
        for i in range(len(route) - 1):
            if self.network.graph.has_edge(route[i], route[i+1]):
                total_distance += self.network.graph[route[i]][route[i+1]]['length']
            else:
                return {"success": False, "message": f"Edge {route[i]}->{route[i+1]} does not exist"}
        
        distance_km = total_distance / 1000
        
        # Check capacity
        if vehicle.capacity < request.passengers + vehicle.current_passengers:
            return {"success": False, "message": f"Vehicle {vehicle_id} capacity ({vehicle.capacity}) insufficient for {request.passengers} passengers"}
        
        # Update state
        vehicle.status = VehicleStatus.EN_ROUTE
        vehicle.assigned_request_id = request_id
        vehicle.route = route
        
        request.status = RequestStatus.ASSIGNED
        request.assigned_vehicle_id = vehicle_id
        request.assigned_route = route
        
        return {
            "success": True,
            "message": f"Vehicle {vehicle_id} assigned to request {request_id}",
            "vehicle_id": vehicle_id,
            "request_id": request_id,
            "route": route,
            "distance_km": round(distance_km, 2)
        }
    
    # ─────────────────────────────────────────────
    # TOOL 7: validate_plan() — Safety-Review Guard
    # Used by: All systems (applied to all outputs)
    # ─────────────────────────────────────────────
    def validate_plan(self, vehicle_id: str, route: list[str], 
                      request_id: str) -> dict:
        """Deterministic Safety-Review Guard. Validates a proposed plan against hard constraints.
        
        Checks:
        1. BFS Reachability: Every edge in route has capacity > 0
        2. SoC Sufficiency: Vehicle has enough charge (+ 15% margin)
        3. Capacity Check: Vehicle can carry the passengers
        4. Route Existence: All edges in route exist in graph
        
        Returns:
            dict with: valid (bool), checks_passed (list), checks_failed (list), rejection_reason
        """
        checks_passed = []
        checks_failed = []
        
        vehicle = self.fleet.get_vehicle(vehicle_id)
        request = self.request_queue.requests.get(request_id)
        
        if not vehicle:
            return {"valid": False, "checks_passed": [], "checks_failed": ["Vehicle not found"], "rejection_reason": f"Vehicle {vehicle_id} does not exist"}
        if not request:
            return {"valid": False, "checks_passed": [], "checks_failed": ["Request not found"], "rejection_reason": f"Request {request_id} does not exist"}
        
        # CHECK 1: Route Existence — every consecutive pair must be a valid edge
        total_distance = 0.0
        total_travel_time = 0.0
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if not self.network.graph.has_edge(u, v):
                checks_failed.append(f"Edge {u}->{v} does not exist in graph")
            else:
                edge = self.network.graph[u][v]
                total_distance += edge['length']
                total_travel_time += edge['travel_time']
        
        if not checks_failed:
            checks_passed.append("Route existence: All edges exist")
        
        # CHECK 2: BFS Reachability — no edge has capacity = 0 (closed)
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            if self.network.graph.has_edge(u, v):
                if self.network.graph[u][v]['capacity'] <= 0:
                    checks_failed.append(f"BFS: Edge {u}->{v} is closed (capacity=0)")
        
        if not any("BFS" in f for f in checks_failed):
            checks_passed.append("BFS reachability: All edges operational")
        
        # CHECK 3: SoC Sufficiency (+15% safety margin)
        distance_km = total_distance / 1000
        if vehicle.can_reach(distance_km, safety_margin=0.15):
            checks_passed.append(f"SoC check: {vehicle.soc:.1f}% sufficient for {distance_km:.1f}km")
        else:
            required = distance_km * vehicle.soc_consumption_per_km * 1.15
            checks_failed.append(
                f"SoC insufficient: have {vehicle.soc:.1f}%, need {required:.1f}% for {distance_km:.1f}km + 15% margin"
            )
        
        # CHECK 4: Passenger Capacity
        needed = request.passengers + vehicle.current_passengers
        if vehicle.capacity >= needed:
            checks_passed.append(f"Capacity check: {vehicle.capacity} >= {needed} passengers")
        else:
            checks_failed.append(
                f"Capacity insufficient: vehicle has {vehicle.capacity} seats, needs {needed}"
            )
        
        valid = len(checks_failed) == 0
        
        return {
            "valid": valid,
            "checks_passed": checks_passed,
            "checks_failed": checks_failed,
            "rejection_reason": checks_failed[0] if checks_failed else None,
            "route_distance_km": round(distance_km, 2),
            "estimated_travel_time": round(total_travel_time, 1)
        }
