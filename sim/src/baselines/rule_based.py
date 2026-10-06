# src/baselines/rule_based.py

"""
Baseline 1: Rule-Based SOP Controller
Uses deterministic heuristics — no LLM involved.
Serves as the performance floor.
"""

from typing import Optional
from ..tools.agent_tools import AgentTools
from ..network.graph_builder import TransportNetwork
from ..fleet.vehicle import Fleet, VehicleStatus
from ..requests.transport_request import RequestQueue, RequestStatus
from ..safety.decision_card import DecisionCard
import networkx as nx


class RuleBasedController:
    """Deterministic rule-based disruption response controller."""
    
    def __init__(self, tools: AgentTools):
        self.tools = tools
        self.decisions_proposed = 0
        self.decisions_rejected = 0
    
    def respond_to_disruption(self) -> list[DecisionCard]:
        """Execute rule-based disruption response.
        
        Algorithm:
        1. Get all pending requests
        2. For each request, compute shortest path on open subgraph
        3. Find nearest available vehicle with sufficient SoC
        4. Validate via Safety Guard
        5. If valid -> assign; if invalid -> mark as UNSERVED
        """
        decisions = []
        pending = self.tools.request_queue.get_pending_requests()
        
        # Sort by priority (higher first) then by time (earlier first)
        pending.sort(key=lambda r: (-r.priority, r.time))
        
        for request in pending:
            decision = self._handle_request(request)
            if decision:
                decisions.append(decision)
        
        return decisions
    
    def _handle_request(self, request) -> Optional[DecisionCard]:
        """Handle a single transport request using rule-based heuristics."""
        
        # Step 1: Find shortest path
        path_result = self.tools.shortest_path(request.origin, request.destination)
        
        if not path_result['reachable']:
            request.status = RequestStatus.UNSERVED
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="NO_PATH_AVAILABLE",
                vehicle_id=None,
                assigned_route=None,
                estimated_delay_reduction_min=0,
                safety_guard_passed=False,
                rejection_reason="No path exists between origin and destination"
            )
        
        route = path_result['path']
        distance_km = path_result['distance_km']
        
        # Step 2: Find nearest available vehicle with sufficient SoC
        available = self.tools.get_available_vehicles()
        best_vehicle = None
        best_distance = float('inf')
        
        for v_info in available:
            # Check if vehicle can reach the request origin
            origin_path = self.tools.shortest_path(v_info['current_node'], request.origin)
            if origin_path['reachable']:
                pickup_distance = origin_path['distance_km']
                total_distance = pickup_distance + distance_km
                
                # Check SoC for total trip
                vehicle = self.tools.fleet.get_vehicle(v_info['id'])
                if vehicle.can_reach(total_distance) and v_info['capacity'] >= request.passengers:
                    if pickup_distance < best_distance:
                        best_distance = pickup_distance
                        best_vehicle = v_info
        
        if not best_vehicle:
            request.status = RequestStatus.UNSERVED
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="NO_VEHICLE_AVAILABLE",
                vehicle_id=None,
                assigned_route=None,
                estimated_delay_reduction_min=0,
                safety_guard_passed=False,
                rejection_reason="No available vehicle with sufficient SoC and capacity"
            )
        
        # Step 3: Validate via Safety Guard
        self.decisions_proposed += 1
        validation = self.tools.validate_plan(
            vehicle_id=best_vehicle['id'],
            route=route,
            request_id=request.id
        )
        
        if validation['valid']:
            # Step 4: Execute assignment
            self.tools.assign_vehicle(best_vehicle['id'], request.id, route)
            
            # Calculate undisrupted free-flow time for ADIF baseline
            try:
                ideal_path = nx.shortest_path(self.tools.network.graph, request.origin, request.destination, weight='length')
                free_flow_time = sum(
                    self.tools.network.graph[ideal_path[i]][ideal_path[i+1]]['length'] / 
                    self.tools.network.graph[ideal_path[i]][ideal_path[i+1]]['speed_limit']
                    for i in range(len(ideal_path) - 1)
                )
            except Exception:
                free_flow_time = sum(
                    self.tools.network.graph[route[i]][route[i+1]]['length'] / 
                    self.tools.network.graph[route[i]][route[i+1]]['speed_limit']
                    for i in range(len(route) - 1)
                )
            actual_time = validation.get('estimated_travel_time', free_flow_time)
            
            # Store on request for ADIF metric calculation
            request.free_flow_travel_time = free_flow_time
            request.actual_travel_time = actual_time
            
            delay_reduction = max(0, (actual_time - free_flow_time) / 60)
            
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="REROUTE_AND_DISPATCH",
                vehicle_id=best_vehicle['id'],
                assigned_route=route,
                estimated_delay_reduction_min=round(delay_reduction, 1),
                safety_guard_passed=True,
                route_distance_km=validation.get('route_distance_km'),
                estimated_travel_time_s=validation.get('estimated_travel_time')
            )
        else:
            self.decisions_rejected += 1
            request.status = RequestStatus.UNSERVED
            return DecisionCard(
                scenario_id="",
                request_id=request.id,
                recommended_action="FALLBACK_SOP",
                vehicle_id=best_vehicle['id'],
                assigned_route=route,
                estimated_delay_reduction_min=0,
                safety_guard_passed=False,
                rejection_reason=validation.get('rejection_reason')
            )
