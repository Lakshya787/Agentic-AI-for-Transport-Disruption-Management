# src/requests/transport_request.py

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class RequestStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    UNSERVED = "unserved"

class TransportRequest(BaseModel):
    """A passenger/cargo transport request (OD pair)."""
    id: str
    origin: str                              # Origin node ID
    destination: str                         # Destination node ID
    time: int                                # Request arrival time (simulation step)
    passengers: int = 1                      # Number of passengers
    priority: int = Field(default=1, ge=1, le=3)  # 1=normal, 2=high, 3=emergency
    status: RequestStatus = RequestStatus.PENDING
    assigned_vehicle_id: Optional[str] = None
    assigned_route: Optional[list[str]] = None
    actual_travel_time: Optional[float] = None
    free_flow_travel_time: Optional[float] = None  # For ADIF calculation


class RequestQueue(BaseModel):
    """Queue of transport requests."""
    requests: dict[str, TransportRequest] = {}
    
    def add_request(self, request: TransportRequest):
        self.requests[request.id] = request
    
    def get_pending_requests(self) -> list[TransportRequest]:
        return [r for r in self.requests.values() if r.status == RequestStatus.PENDING]
    
    def get_affected_requests(self) -> list[TransportRequest]:
        """All requests that need serving (pending + assigned but not completed)."""
        return [r for r in self.requests.values() 
                if r.status in (RequestStatus.PENDING, RequestStatus.ASSIGNED)]
    
    def to_json_state(self) -> list[dict]:
        return [r.model_dump() for r in self.requests.values()]
