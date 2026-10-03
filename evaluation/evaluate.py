"""
evaluate.py
------------
Runs the BASELINE recommender and the PROPOSED rule-based engine against
every sample student in data/students.csv, then compares them on:

    - Average course choice quality (0-100)
    - Number of prerequisite conflicts among recommended courses
    - Number of schedule conflicts among recommended courses
    - Career misalignment (recommended courses with relevance < 60)
    - Recommendation success rate (% of recommended courses that are
      actually safe to take: prerequisites met, no schedule clash,
      relevance >= 60)

Run with:  python -m evaluation.evaluate
Produces:  evaluation/evaluation_results.csv  and prints a summary table.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd

from src import data_loader as dl
from src.prerequisite_checker import check_prerequisites
from src.schedule_checker import check_schedule_conflicts
from src.scoring import compute_quality_score
from baseline.baseline_recommender import baseline_recommend_courses

TOP_N = 5


def _evaluate_course_set(course_ids, career_role, completed_courses, student_skills,
                          courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df):
    """Shared metric computation for a list of recommended course_ids."""
    if not course_ids:
        return {
            "avg_quality": 0.0, "prereq_conflicts": 0, "schedule_conflicts": 0,
            "career_misaligned": 0, "success_rate": 0.0,
        }

    qualities = []
    prereq_conflicts = 0
    career_misaligned = 0

    for cid in course_ids:
        other = [c for c in course_ids if c != cid]
        q = compute_quality_score(
            cid, career_role, completed_courses, student_skills, other,
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )
        qualities.append(q.overall)

        pr = check_prerequisites(cid, completed_courses, courses_df, prereq_df)
        if not pr.is_eligible:
            prereq_conflicts += 1

        if q.career_alignment < 60:
            career_misaligned += 1

    conflicts = check_schedule_conflicts(course_ids, courses_df, schedules_df)
    schedule_conflicts = len(conflicts)

    successful = 0
    for cid in course_ids:
        pr = check_prerequisites(cid, completed_courses, courses_df, prereq_df)
        relevance = dl.get_relevance(career_df, career_role, cid)
        has_conflict = any(cid in (c.course_a, c.course_b) for c in conflicts)
        if pr.is_eligible and not has_conflict and relevance >= 60:
            successful += 1

    return {
        "avg_quality": round(sum(qualities) / len(qualities), 1),
        "prereq_conflicts": prereq_conflicts,
        "schedule_conflicts": schedule_conflicts,
        "career_misaligned": career_misaligned,
        "success_rate": round(100.0 * successful / len(course_ids), 1),
    }


def run_evaluation() -> pd.DataFrame:
    courses_df = dl.load_courses()
    prereq_df = dl.load_prerequisites()
    schedules_df = dl.load_schedules()
    career_df = dl.load_career_pathways()
    outcomes_df = dl.load_course_outcomes()
    req_df = dl.load_career_required_skills()
    students_df = dl.load_students()

    rows = []
    for _, student in students_df.iterrows():
        career_role = student["career_goal"]
        completed = dl.split_list(student["completed_courses"])
        skills = dl.split_list(student["skills"])

        # --- Baseline: naive top-N by relevance only ---
        baseline_courses = [r["course_id"] for r in baseline_recommend_courses(career_role, courses_df, career_df, TOP_N)]
        baseline_metrics = _evaluate_course_set(
            baseline_courses, career_role, completed, skills,
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )

        # --- Proposed: top-N by full explainable score ---
        # Only courses the engine actually labels "Recommended" or
        # "Recommended with caution" count as real recommendations for this
        # comparison -- courses it explicitly flags "Not Recommended" (e.g.
        # missing prerequisites) are shown to the student but are NOT
        # counted as something the system recommended, which is the whole
        # point of the explainable engine vs. the naive baseline.
        from src.recommender import top_recommendations_for_role
        proposed_recs_raw = top_recommendations_for_role(
            career_role, completed, skills, TOP_N,
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )
        proposed_recs = [r for r in proposed_recs_raw if r.verdict != "Not Recommended"]
        proposed_courses = [r.course_id for r in proposed_recs]
        proposed_metrics = _evaluate_course_set(
            proposed_courses, career_role, completed, skills,
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )
        proposed_metrics["courses_actually_recommended"] = len(proposed_courses)

        rows.append({
            "student_id": student["student_id"], "name": student["name"], "career_goal": career_role,
            "baseline_avg_quality": baseline_metrics["avg_quality"],
            "proposed_avg_quality": proposed_metrics["avg_quality"],
            "baseline_prereq_conflicts": baseline_metrics["prereq_conflicts"],
            "proposed_prereq_conflicts": proposed_metrics["prereq_conflicts"],
            "baseline_schedule_conflicts": baseline_metrics["schedule_conflicts"],
            "proposed_schedule_conflicts": proposed_metrics["schedule_conflicts"],
            "baseline_career_misaligned": baseline_metrics["career_misaligned"],
            "proposed_career_misaligned": proposed_metrics["career_misaligned"],
            "baseline_success_rate": baseline_metrics["success_rate"],
            "proposed_success_rate": proposed_metrics["success_rate"],
            "proposed_courses_actually_recommended": proposed_metrics.get("courses_actually_recommended", 0),
        })

    return pd.DataFrame(rows)


def summarize(results_df: pd.DataFrame) -> pd.DataFrame:
    summary = {
        "Metric": [
            "Average Course Choice Quality",
            "Total Prerequisite Conflicts",
            "Total Schedule Conflicts",
            "Total Career Misalignments",
            "Average Recommendation Success Rate (%)",
        ],
        "Baseline": [
            round(results_df["baseline_avg_quality"].mean(), 1),
            int(results_df["baseline_prereq_conflicts"].sum()),
            int(results_df["baseline_schedule_conflicts"].sum()),
            int(results_df["baseline_career_misaligned"].sum()),
            round(results_df["baseline_success_rate"].mean(), 1),
        ],
        "Proposed System": [
            round(results_df["proposed_avg_quality"].mean(), 1),
            int(results_df["proposed_prereq_conflicts"].sum()),
            int(results_df["proposed_schedule_conflicts"].sum()),
            int(results_df["proposed_career_misaligned"].sum()),
            round(results_df["proposed_success_rate"].mean(), 1),
        ],
    }
    return pd.DataFrame(summary)


if __name__ == "__main__":
    results = run_evaluation()
    out_path = os.path.join(os.path.dirname(__file__), "evaluation_results.csv")
    results.to_csv(out_path, index=False)
    print("Per-student results saved to:", out_path)
    print()
    print(results.to_string(index=False))
    print()
    print("=== Baseline vs Proposed System Summary ===")
    print(summarize(results).to_string(index=False))
