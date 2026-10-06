# src/metrics/evaluator.py

"""
Automatic evaluation metrics computed after each scenario run.
Same metrics applied to all 3 systems for fair comparison.
"""

from dataclasses import dataclass, field
from typing import List
from ..safety.decision_card import DecisionCard
from ..requests.transport_request import RequestQueue, RequestStatus


@dataclass
class ScenarioMetrics:
    """All 6 evaluation metrics for a single scenario run."""
    scenario_id: str
    system_name: str                          # "rule_based" | "single_llm" | "multi_agent_llm"
    
    # Metric 1: Hard Constraint Violation Rate (HCVR %)
    total_proposed_actions: int = 0
    infeasible_actions: int = 0
    hcvr_percent: float = 0.0
    
    # Metric 2: Request Fulfillment Rate (RFR %)
    total_affected_requests: int = 0
    successfully_served: int = 0
    rfr_percent: float = 0.0
    
    # Metric 3: Average Delay Inflation Factor (ADIF)
    delay_factors: list = field(default_factory=list)
    adif: float = 1.0
    
    # Metric 4: Execution Latency (T_exec in seconds)
    execution_latency_s: float = 0.0
    
    # Metric 5: Token Cost ($/scenario) — only for LLM systems
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    token_cost_usd: float = 0.0
    
    # Metric 6: Infeasible Decision Rate (IDR %)
    total_decisions: int = 0
    rejected_by_guard: int = 0
    idr_percent: float = 0.0


class MetricsEvaluator:
    """Calculates all 6 metrics from scenario results."""
    
    def __init__(self, scenario_id: str, system_name: str):
        self.metrics = ScenarioMetrics(
            scenario_id=scenario_id,
            system_name=system_name
        )
    
    def evaluate(self, decisions: list[DecisionCard], request_queue: RequestQueue,
                 execution_time_s: float = 0.0, 
                 token_usage: dict = None) -> ScenarioMetrics:
        """Compute all metrics from a list of DecisionCards."""
        
        m = self.metrics
        
        # -- Metric 1: HCVR --
        m.total_proposed_actions = len(decisions)
        m.infeasible_actions = sum(
            1 for d in decisions 
            if not d.safety_guard_passed and d.recommended_action not in ("NO_PATH_AVAILABLE", "NO_VEHICLE_AVAILABLE")
        )
        m.hcvr_percent = (
            (m.infeasible_actions / m.total_proposed_actions * 100) 
            if m.total_proposed_actions > 0 else 0.0
        )
        
        # -- Metric 2: RFR --
        all_requests = list(request_queue.requests.values())
        m.total_affected_requests = len(all_requests)
        m.successfully_served = sum(
            1 for r in all_requests 
            if r.status in (RequestStatus.ASSIGNED, RequestStatus.IN_TRANSIT, RequestStatus.COMPLETED)
        )
        m.rfr_percent = (
            (m.successfully_served / m.total_affected_requests * 100)
            if m.total_affected_requests > 0 else 0.0
        )
        
        # -- Metric 3: ADIF --
        for r in all_requests:
            if r.actual_travel_time and r.free_flow_travel_time and r.free_flow_travel_time > 0:
                m.delay_factors.append(r.actual_travel_time / r.free_flow_travel_time)
        m.adif = (
            sum(m.delay_factors) / len(m.delay_factors)
            if m.delay_factors else 1.0
        )
        
        # -- Metric 4: Execution Latency --
        m.execution_latency_s = execution_time_s
        
        # -- Metric 5: Token Cost --
        if token_usage:
            m.prompt_tokens = token_usage.get('prompt_tokens', 0)
            m.completion_tokens = token_usage.get('completion_tokens', 0)
            m.total_tokens = m.prompt_tokens + m.completion_tokens
            # Approximate pricing (GPT-4o-mini as reference)
            m.token_cost_usd = (
                m.prompt_tokens * 0.00000015 + 
                m.completion_tokens * 0.0000006
            )
        
        # -- Metric 6: IDR --
        m.total_decisions = len(decisions)
        m.rejected_by_guard = sum(1 for d in decisions if not d.safety_guard_passed)
        m.idr_percent = (
            (m.rejected_by_guard / m.total_decisions * 100)
            if m.total_decisions > 0 else 0.0
        )
        
        return m
    
    @staticmethod
    def print_report(m: ScenarioMetrics):
        """Print a formatted metrics report."""
        print(f"\n{'='*60}")
        print(f"  SCENARIO METRICS REPORT")
        print(f"  Scenario: {m.scenario_id} | System: {m.system_name}")
        print(f"{'='*60}")
        print(f"  1. HCVR (Hard Constraint Violation Rate): {m.hcvr_percent:.1f}%")
        print(f"     ({m.infeasible_actions} infeasible / {m.total_proposed_actions} proposed)")
        print(f"  2. RFR  (Request Fulfillment Rate):       {m.rfr_percent:.1f}%")
        print(f"     ({m.successfully_served} served / {m.total_affected_requests} affected)")
        print(f"  3. ADIF (Avg Delay Inflation Factor):     {m.adif:.2f}x")
        print(f"  4. T_exec (Execution Latency):            {m.execution_latency_s:.3f}s")
        print(f"  5. Token Cost:                            ${m.token_cost_usd:.4f}")
        print(f"     (Prompt: {m.prompt_tokens} | Completion: {m.completion_tokens})")
        print(f"  6. IDR  (Infeasible Decision Rate):       {m.idr_percent:.1f}%")
        print(f"     ({m.rejected_by_guard} rejected / {m.total_decisions} total)")
        print(f"{'='*60}\n")
