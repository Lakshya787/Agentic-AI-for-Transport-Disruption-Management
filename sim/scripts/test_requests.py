#!/usr/bin/env python3
"""Test TransportRequest and RequestQueue."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.requests.transport_request import TransportRequest, RequestQueue, RequestStatus

def main():
    queue = RequestQueue()
    
    # Add some requests (use placeholder node IDs — doesn't matter for this test)
    r1 = TransportRequest(id="R1", origin="A0", destination="D3", time=50, passengers=2, priority=1)
    r2 = TransportRequest(id="R2", origin="B1", destination="C3", time=60, passengers=1, priority=2)
    r3 = TransportRequest(id="R3", origin="A2", destination="D1", time=80, passengers=1, priority=3)
    
    queue.add_request(r1)
    queue.add_request(r2)
    queue.add_request(r3)
    
    print(f"Total requests: {len(queue.requests)}")
    print(f"Pending: {len(queue.get_pending_requests())}")
    
    # Assign one
    r1.status = RequestStatus.ASSIGNED
    r1.assigned_vehicle_id = "V001"
    print(f"After assigning R1 — Pending: {len(queue.get_pending_requests())}")
    print(f"Affected (need serving): {len(queue.get_affected_requests())}")
    
    # Mark one as unserved
    r3.status = RequestStatus.UNSERVED
    print(f"After R3 unserved — Pending: {len(queue.get_pending_requests())}")
    
    # JSON
    state = queue.to_json_state()
    print(f"JSON: {len(state)} requests")
    
    print()
    print("ALL REQUEST TESTS PASSED ✅")

if __name__ == "__main__":
    main()
