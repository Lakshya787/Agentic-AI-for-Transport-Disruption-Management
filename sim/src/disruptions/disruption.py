# src/disruptions/disruption.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class DisruptionType(str, Enum):
    ROAD_CLOSURE = "road_closure"
    CONGESTION = "congestion"
    VEHICLE_BREAKDOWN = "vehicle_breakdown"
    DEMAND_SURGE = "demand_surge"

class Disruption(BaseModel):
    """A single disruption event."""
    id: str
    type: DisruptionType
    time: int                                     # Simulation step when disruption occurs
    duration: Optional[int] = None                # Duration in steps (None = permanent)
    
    # Road closure / congestion params
    edge_from: Optional[str] = None               # From node
    edge_to: Optional[str] = None                 # To node
    congestion_factor: Optional[float] = None     # Travel time multiplier (for congestion)
    
    # Vehicle breakdown params
    vehicle_id: Optional[str] = None
    
    # Demand surge params
    surge_multiplier: Optional[float] = None
    surge_area_nodes: Optional[list[str]] = None  # Affected area nodes
    surge_num_requests: Optional[int] = None      # Number of extra requests
