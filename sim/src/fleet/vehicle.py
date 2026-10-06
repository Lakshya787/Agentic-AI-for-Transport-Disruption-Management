# src/fleet/vehicle.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class VehicleStatus(str, Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    PICKUP = "pickup"
    DELIVERING = "delivering"
    BROKEN = "broken"
    CHARGING = "charging"

class Vehicle(BaseModel):
    """Single vehicle in the fleet."""
    id: str
    current_node: str                          # Current position (node ID)
    current_edge: Optional[str] = None         # Current edge (if mid-transit)
    capacity: int = 4                          # Max passenger capacity
    current_passengers: int = 0
    soc: float = Field(default=100.0, ge=0, le=100)  # State of Charge (%)
    soc_consumption_per_km: float = 2.0        # % SoC consumed per km
    status: VehicleStatus = VehicleStatus.IDLE
    assigned_request_id: Optional[str] = None
    route: Optional[List[str]] = None          # Planned route (list of node IDs)
    
    def can_reach(self, distance_km: float, safety_margin: float = 0.15) -> bool:
        """Check if vehicle has enough SoC to cover distance + 15% safety margin."""
        required_soc = distance_km * self.soc_consumption_per_km * (1 + safety_margin)
        return self.soc >= required_soc
    
    def remaining_range_km(self, safety_margin: float = 0.15) -> float:
        """Maximum distance vehicle can travel with safety margin."""
        return self.soc / (self.soc_consumption_per_km * (1 + safety_margin))
    
    def consume_soc(self, distance_km: float):
        """Consume SoC for a given distance."""
        self.soc = max(0, self.soc - distance_km * self.soc_consumption_per_km)


class Fleet(BaseModel):
    """Collection of vehicles."""
    vehicles: dict[str, Vehicle] = {}
    
    def add_vehicle(self, vehicle: Vehicle):
        self.vehicles[vehicle.id] = vehicle
    
    def get_available_vehicles(self) -> list[Vehicle]:
        """Get all vehicles that are idle and operational."""
        return [v for v in self.vehicles.values() 
                if v.status == VehicleStatus.IDLE and v.soc > 10.0]
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        return self.vehicles.get(vehicle_id)
    
    def break_vehicle(self, vehicle_id: str):
        """Simulate vehicle breakdown."""
        if vehicle_id in self.vehicles:
            self.vehicles[vehicle_id].status = VehicleStatus.BROKEN
            self.vehicles[vehicle_id].assigned_request_id = None
            self.vehicles[vehicle_id].route = None
    
    def to_json_state(self) -> list[dict]:
        """Serialize fleet state for LLM context."""
        return [v.model_dump() for v in self.vehicles.values()]
