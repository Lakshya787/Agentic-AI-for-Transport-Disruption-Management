#!/usr/bin/env python3
"""Test DecisionCard Pydantic validation."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.safety.decision_card import DecisionCard
from pydantic import ValidationError

def main():
    # Test 1: Valid card
    card = DecisionCard(
        scenario_id="L1_simple_001",
        request_id="R1",
        recommended_action="REROUTE_AND_DISPATCH",
        vehicle_id="V001",
        assigned_route=["A0", "B0", "C0", "D0"],
        estimated_delay_reduction_min=2.5,
        safety_guard_passed=True,
        route_distance_km=0.6,
        estimated_travel_time_s=43.2
    )
    print(f"✅ Valid card created: {card.recommended_action}")
    print(f"   Route: {' -> '.join(card.assigned_route)}")
    
    # Test 2: Card with no vehicle (NO_PATH case)
    card2 = DecisionCard(
        scenario_id="L1_simple_001",
        request_id="R2",
        recommended_action="NO_PATH_AVAILABLE",
        safety_guard_passed=False,
        rejection_reason="No path exists"
    )
    print(f"✅ No-path card: {card2.recommended_action}, reason: {card2.rejection_reason}")
    
    # Test 3: JSON serialization round-trip
    json_str = card.model_dump_json(indent=2)
    print(f"\n✅ JSON output:\n{json_str}")
    
    # Test 4: Parse back from JSON
    card_back = DecisionCard.model_validate_json(json_str)
    assert card_back.vehicle_id == card.vehicle_id
    print(f"\n✅ JSON round-trip successful")
    
    # Test 5: Missing required field should fail
    try:
        bad_card = DecisionCard(
            # Missing scenario_id and request_id
            recommended_action="REROUTE"
        )
        print("❌ Should have raised validation error!")
    except ValidationError as e:
        print(f"\n✅ Pydantic correctly rejected invalid card ({e.error_count()} errors)")
    
    print()
    print("ALL DECISION CARD TESTS PASSED ✅")

if __name__ == "__main__":
    main()
