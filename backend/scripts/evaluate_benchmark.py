"""
Run a small manually labeled benchmark suite against the bias detector.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.services.bias_detector import detect_bias

LEVEL_ORDER = {"LOW": 1, "MODERATE": 2, "HIGH": 3, "CRITICAL": 4}


def main() -> None:
    benchmark_path = REPO_ROOT / "data" / "benchmarks" / "policy_clause_benchmark.json"
    cases = json.loads(benchmark_path.read_text(encoding="utf-8"))

    total = len(cases)
    correct_flagging = 0
    correct_types = 0
    correct_levels = 0
    correct_groups = 0

    print("PolicyLens benchmark run")
    print("=" * 72)

    for case in cases:
        result = detect_bias(
            {
                "clauses": [{"clause_id": case["id"], "text": case["text"], "index": 0}],
                "full_text": case["text"],
            }
        )
        flagged_clause = result["flagged_clauses"][0] if result["flagged_clauses"] else None
        was_flagged = flagged_clause is not None

        flag_ok = was_flagged == case["should_flag"]
        correct_flagging += int(flag_ok)

        type_ok = False
        level_ok = False
        group_ok = False
        observed_level = "LOW"
        observed_type = "NONE"
        observed_groups = []

        if flagged_clause:
            observed_type = flagged_clause["bias_type"]
            observed_level = _score_to_level(flagged_clause["bias_score"])
            observed_groups = flagged_clause.get("impacted_groups", [])
            type_ok = observed_type == case["expected_bias_type"]
            level_ok = LEVEL_ORDER[observed_level] >= LEVEL_ORDER[case["expected_min_level"]]
            expected_groups = {group.lower() for group in case.get("expected_impacted_groups", [])}
            observed_group_set = {group.lower() for group in observed_groups}
            group_ok = expected_groups.issubset(observed_group_set) if expected_groups else True
        else:
            type_ok = not case["should_flag"]
            level_ok = case["expected_min_level"] == "LOW"
            group_ok = len(case.get("expected_impacted_groups", [])) == 0

        correct_types += int(type_ok)
        correct_levels += int(level_ok)
        correct_groups += int(group_ok)

        print(f"{case['id']}: flagged={was_flagged} type={observed_type} level={observed_level} groups={observed_groups}")

    print("\nSummary")
    print("-" * 72)
    print(f"Correctly surfaced flag / no-flag outcome: {correct_flagging}/{total}")
    print(f"Correct bias-type match: {correct_types}/{total}")
    print(f"Correct minimum severity match: {correct_levels}/{total}")
    print(f"Correct impacted-group coverage: {correct_groups}/{total}")


def _score_to_level(score: int) -> str:
    if score >= 75:
        return "CRITICAL"
    if score >= 55:
        return "HIGH"
    if score >= 35:
        return "MODERATE"
    return "LOW"


if __name__ == "__main__":
    main()
