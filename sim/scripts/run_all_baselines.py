#!/usr/bin/env python3
"""Run rule-based baseline on ALL scenarios, print comparison table."""

import sys, os, glob
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from scripts.run_scenario import run_scenario

def main():
    files = sorted(glob.glob("scenarios/L*.json"))
    if not files:
        print("No scenarios found!"); return
    
    results = []
    for sf in files:
        try:
            m = run_scenario(sf, "rule_based")
            if m: results.append(m)
        except Exception as e:
            print(f"❌ {sf}: {e}")
    
    if results:
        print(f"\n{'='*80}")
        print(f"  COMPARISON TABLE — Rule-Based Baseline")
        print(f"{'='*80}")
        print(f"{'Scenario':<25} {'HCVR%':>8} {'RFR%':>8} {'ADIF':>8} {'Latency':>10} {'IDR%':>8}")
        print("-" * 73)
        for m in results:
            print(f"{m.scenario_id:<25} {m.hcvr_percent:>7.1f}% {m.rfr_percent:>7.1f}% "
                  f"{m.adif:>7.2f}x {m.execution_latency_s:>9.3f}s {m.idr_percent:>7.1f}%")
        print(f"{'='*80}")

if __name__ == "__main__":
    main()
