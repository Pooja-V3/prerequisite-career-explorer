"""
test_cases.py
--------------
Implements and runs the 5 required test / failure cases from the problem
statement:

    1. Missing prerequisite
    2. Schedule conflict
    3. Course with low career relevance
    4. Multiple missing prerequisites
    5. Student with no completed courses

Each test states an EXPECTED result and compares it with the ACTUAL result
produced by the system. Run with:  python -m tests.test_cases
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import data_loader as dl
from src.prerequisite_checker import check_prerequisites
from src.schedule_checker import check_schedule_conflicts
from src.career_analyzer import analyze_course_for_career
from src.scoring import compute_quality_score

PASS = "PASS"
FAIL = "FAIL"

courses_df = dl.load_courses()
prereq_df = dl.load_prerequisites()
schedules_df = dl.load_schedules()
career_df = dl.load_career_pathways()
outcomes_df = dl.load_course_outcomes()
req_df = dl.load_career_required_skills()


def _report(name, expected, actual, passed):
    print(f"\n[{PASS if passed else FAIL}] {name}")
    print(f"   Expected: {expected}")
    print(f"   Actual:   {actual}")
    return passed


def test_1_missing_prerequisite():
    """Spring Boot (C011) requires Java (C001) and OOP (C002).
    Student has Java but NOT OOP -> should be flagged ineligible."""
    result = check_prerequisites("C011", ["C001"], courses_df, prereq_df)
    expected = "Ineligible; OOP missing"
    actual = f"{'Eligible' if result.is_eligible else 'Ineligible'}; missing={[m['name'] for m in result.missing]}"
    passed = (not result.is_eligible) and any(m["id"] == "C002" for m in result.missing)
    return _report("Test 1: Missing prerequisite (Spring Boot needs OOP)", expected, actual, passed)


def test_2_schedule_conflict():
    """Java (C001, Mon 09:00-11:00) and Computer Networks (C005, Mon 09:00-11:00)
    are scheduled at the same time -> a conflict should be detected."""
    conflicts = check_schedule_conflicts(["C001", "C005"], courses_df, schedules_df)
    expected = "1 conflict detected between Java Programming and Computer Networks"
    actual = f"{len(conflicts)} conflict(s): {[c.message for c in conflicts]}"
    passed = len(conflicts) >= 1
    return _report("Test 2: Schedule conflict (Java vs Computer Networks, both Mon 9-11)", expected, actual, passed)


def test_3_low_career_relevance():
    """UI/UX Design Principles (C038) has low relevance for a Cybersecurity
    Analyst career goal -> should score low and be explained as such."""
    result = analyze_course_for_career("C038", "Cybersecurity Analyst", [], courses_df, career_df, req_df)
    expected = "Relevance score below 45 (marginally/not relevant)"
    actual = f"Relevance score = {result.relevance_score}; explanation: {result.explanation}"
    passed = result.relevance_score < 45
    return _report("Test 3: Course with low career relevance (UI/UX for Cybersecurity Analyst)", expected, actual, passed)


def test_4_multiple_missing_prerequisites():
    """Deep Learning (C015) requires Machine Learning (C014), which itself
    requires Python, Statistics and Linear Algebra. A student with NONE of
    these completed should see multiple/chained missing prerequisites."""
    result = check_prerequisites("C015", [], courses_df, prereq_df)
    expected = "Ineligible; C014 (Machine Learning) missing"
    actual = f"{'Eligible' if result.is_eligible else 'Ineligible'}; missing={[m['name'] for m in result.missing]}"
    passed = (not result.is_eligible) and len(result.missing) >= 1

    from src.prerequisite_checker import suggest_prerequisite_path
    path = suggest_prerequisite_path("C015", [], courses_df, prereq_df)
    path_names = [p["name"] for p in path]
    expected2 = "Suggested path includes Python, Statistics, Linear Algebra and Machine Learning"
    actual2 = f"Suggested path: {path_names}"
    passed2 = len(path) >= 3  # at minimum ML + two of its own prerequisites

    ok1 = _report("Test 4a: Multiple missing prerequisites (Deep Learning chain)", expected, actual, passed)
    ok2 = _report("Test 4b: Chained prerequisite path suggestion", expected2, actual2, passed2)
    return ok1 and ok2


def test_5_no_completed_courses():
    """A brand-new student with zero completed courses should still get a
    usable, non-crashing quality score and clear prerequisite warnings
    rather than an error."""
    quality = compute_quality_score(
        "C011", "Backend Developer", [], [], [],
        courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
    )
    expected = "Runs without error; prerequisite_readiness = 0.0 (0 of 2 satisfied)"
    actual = f"overall={quality.overall}, prerequisite_readiness={quality.prerequisite_readiness}"
    passed = quality.prerequisite_readiness == 0.0 and quality.overall is not None
    return _report("Test 5: Student with no completed courses (cold start)", expected, actual, passed)


def run_all():
    results = []
    results.append(test_1_missing_prerequisite())
    results.append(test_2_schedule_conflict())
    results.append(test_3_low_career_relevance())
    results.append(test_4_multiple_missing_prerequisites())
    results.append(test_5_no_completed_courses())

    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(1 for r in results if r)
    print(f"TEST SUMMARY: {passed}/{total} test cases passed")
    print("=" * 60)
    return results


if __name__ == "__main__":
    run_all()
