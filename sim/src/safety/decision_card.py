# src/safety/decision_card.py

from pydantic import BaseModel
from typing import Optional, List

class DecisionCard(BaseModel):
    """Structured output format for all decision-makers.
    Must pass Pydantic validation before execution."""
    scenario_id: str
    request_id: str
    recommended_action: str            # REROUTE_AND_DISPATCH | NO_PATH | NO_VEHICLE | FALLBACK_SOP
    vehicle_id: Optional[str] = None
    assigned_route: Optional[List[str]] = None
    estimated_delay_reduction_min: float = 0.0
    safety_guard_passed: bool = False
    rejection_reason: Optional[str] = None
    route_distance_km: Optional[float] = None
    estimated_travel_time_s: Optional[float] = None
