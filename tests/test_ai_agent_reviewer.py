"""Kiểm thử cho AI-Agent Reviewer."""

from pathlib import Path
import sys

import pytest

THU_MUC_GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(THU_MUC_GOC / "src"))

from ai_agent_reviewer import GreenShipReviewerAgent


def test_reviewer_directory_structure():
    reviewer = GreenShipReviewerAgent()
    res = reviewer.review_directory_structure()
    assert res["status"] in ["PASS", "WARN_OUTPUTS_INCOMPLETE"]
    assert res["directories"]["existing"] == res["directories"]["total"]
    assert res["required_files"]["valid"] == res["required_files"]["total"]


def test_reviewer_loop_integrity():
    reviewer = GreenShipReviewerAgent()
    res = reviewer.review_loops()
    assert res["status"] == "PASS"
    assert res["sog_break_test"]["safe_break"] is True
    # Kiểm tra vòng lặp mô phỏng trên các tuyến R01, R03
    eval_loops = res.get("evaluator_simulation_loops", {})
    if "R01" in eval_loops:
        assert eval_loops["R01"]["time_progression_strictly_monotonic"] is True
        assert eval_loops["R01"]["spatial_continuity_preserved"] is True
        assert eval_loops["R01"]["duration_accumulation_matches"] is True


def test_reviewer_step_5_criteria():
    reviewer = GreenShipReviewerAgent()
    # Kiểm tra đánh giá 16 tiêu chí
    crit = reviewer._evaluate_16_acceptance_criteria(passed_tests=33, table_valid=True)
    assert crit["total_criteria"] == 16
    assert crit["passed_count"] == 16
    assert crit["all_passed"] is True
