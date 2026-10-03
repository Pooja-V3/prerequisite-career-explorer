"""
test_cases.py
-------------
Unit tests for the Prerequisite and Career-Consequence Explorer.

The tests cover:
1. Missing prerequisite
2. Schedule conflict
3. Low career relevance
4. Multiple/chained missing prerequisites
5. Student with no completed courses

Run:
    python -m pytest tests/
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import data_loader as dl
from src.prerequisite_checker import (
    check_prerequisites,
    suggest_prerequisite_path,
)
from src.schedule_checker import check_schedule_conflicts
from src.career_analyzer import analyze_course_for_career
from src.scoring import compute_quality_score


# Load shared test data once for all test cases.
courses_df = dl.load_courses()
prereq_df = dl.load_prerequisites()
schedules_df = dl.load_schedules()
career_df = dl.load_career_pathways()
outcomes_df = dl.load_course_outcomes()
req_df = dl.load_career_required_skills()


def test_1_missing_prerequisite():
    """
    Spring Boot requires Java and OOP.

    The student has completed Java but not OOP.
    The system must mark the course as ineligible and
    identify OOP as a missing prerequisite.
    """
    result = check_prerequisites(
        "C011",
        ["C001"],
        courses_df,
        prereq_df,
    )

    assert result.is_eligible is False
    assert any(m["id"] == "C002" for m in result.missing)


def test_2_schedule_conflict():
    """
    Java and Computer Networks have overlapping schedules.

    The system must detect at least one schedule conflict.
    """
    conflicts = check_schedule_conflicts(
        ["C001", "C005"],
        courses_df,
        schedules_df,
    )

    assert len(conflicts) >= 1


def test_3_low_career_relevance():
    """
    UI/UX Design Principles should have low relevance
    for a Cybersecurity Analyst career goal.
    """
    result = analyze_course_for_career(
        "C038",
        "Cybersecurity Analyst",
        [],
        courses_df,
        career_df,
        req_df,
    )

    assert result.relevance_score < 45
    assert result.explanation is not None


def test_4_multiple_missing_prerequisites():
    """
    Deep Learning requires Machine Learning and its prerequisite
    chain. A student with no completed courses should receive
    prerequisite warnings and a suggested learning path.
    """
    result = check_prerequisites(
        "C015",
        [],
        courses_df,
        prereq_df,
    )

    assert result.is_eligible is False
    assert len(result.missing) >= 1

    path = suggest_prerequisite_path(
        "C015",
        [],
        courses_df,
        prereq_df,
    )

    assert len(path) >= 3


def test_5_no_completed_courses():
    """
    A new student with no completed courses should still receive
    a valid quality score without crashing.
    """
    quality = compute_quality_score(
        "C011",
        "Backend Developer",
        [],
        [],
        [],
        courses_df,
        prereq_df,
        schedules_df,
        career_df,
        outcomes_df,
        req_df,
    )

    assert quality.prerequisite_readiness == 0.0
    assert quality.overall is not None


def test_invalid_course_is_handled_safely():
    """
    Invalid course input should be handled safely by the
    prerequisite checker instead of silently producing an
    incorrect eligible result.
    """
    result = check_prerequisites(
        "INVALID_COURSE",
        [],
        courses_df,
        prereq_df,
    )

    assert result.is_eligible is False