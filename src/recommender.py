"""
recommender.py
----------------
The PROPOSED explainable, rule-based recommendation engine. Unlike the
baseline (see baseline/baseline_recommender.py), this engine considers:
    - career relevance
    - prerequisite readiness
    - schedule conflicts against everything else the student has selected
    - skill coverage
    - course outcome alignment
and produces a full explanation for every recommendation, not just a score.
"""
from dataclasses import dataclass, field
from typing import List

from src import data_loader as dl
from src.scoring import compute_quality_score, QualityScore
from src.prerequisite_checker import check_prerequisites, suggest_prerequisite_path
from src.schedule_checker import check_schedule_conflicts, suggest_alternatives
from src.career_analyzer import analyze_course_for_career


@dataclass
class Recommendation:
    course_id: str
    course_name: str
    quality: QualityScore
    verdict: str                      # "Recommended" | "Not Recommended" | "Recommended with caution"
    reasons: List[str] = field(default_factory=list)
    prerequisite_ok: bool = True
    prerequisite_suggestions: List[dict] = field(default_factory=list)
    schedule_conflicts: list = field(default_factory=list)
    alternative_courses: List[dict] = field(default_factory=list)


def recommend_for_student(career_role: str, completed_courses: List[str],
                           student_skills: List[str], selected_course_ids: List[str],
                           courses_df=None, prereq_df=None, schedules_df=None,
                           career_df=None, outcomes_df=None, req_df=None) -> List[Recommendation]:
    """
    Evaluate every course the student has SELECTED (or is considering) and
    return a full, explainable recommendation for each one, taking the rest
    of the selection into account for schedule-conflict detection.
    """
    if courses_df is None:
        courses_df = dl.load_courses()
    if prereq_df is None:
        prereq_df = dl.load_prerequisites()
    if schedules_df is None:
        schedules_df = dl.load_schedules()
    if career_df is None:
        career_df = dl.load_career_pathways()
    if outcomes_df is None:
        outcomes_df = dl.load_course_outcomes()
    if req_df is None:
        req_df = dl.load_career_required_skills()

    recommendations = []

    for course_id in selected_course_ids:
        other_selected = [c for c in selected_course_ids if c != course_id]

        quality = compute_quality_score(
            course_id, career_role, completed_courses, student_skills, other_selected,
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )

        prereq_result = check_prerequisites(course_id, completed_courses, courses_df, prereq_df)
        conflicts = check_schedule_conflicts(selected_course_ids, courses_df, schedules_df)
        my_conflicts = [c for c in conflicts if course_id in (c.course_a, c.course_b)]

        reasons = list(quality.explanation)

        # ---- Verdict logic (explicit rules, fully explainable) ----
        if not prereq_result.is_eligible:
            verdict = "Not Recommended"
            reasons.append(prereq_result.message)
        elif my_conflicts:
            verdict = "Not Recommended"
            reasons.append(my_conflicts[0].message)
        elif quality.overall >= 70:
            verdict = "Recommended"
        elif quality.overall >= 50:
            verdict = "Recommended with caution"
        else:
            verdict = "Not Recommended"
            reasons.append(
                f"Overall Course Choice Quality ({quality.overall}/100) is too low, "
                f"mainly due to weak career alignment and/or skill coverage."
            )

        prereq_suggestions = []
        if not prereq_result.is_eligible:
            prereq_suggestions = suggest_prerequisite_path(course_id, completed_courses, courses_df, prereq_df)

        alternatives = []
        if my_conflicts:
            excluded = [c for c in selected_course_ids if c != course_id]
            alternatives = suggest_alternatives(course_id, career_role, excluded, courses_df, schedules_df, career_df)

        crow = dl.get_course_row(courses_df, course_id)
        recommendations.append(Recommendation(
            course_id=course_id,
            course_name=crow["course_name"] if crow is not None else course_id,
            quality=quality,
            verdict=verdict,
            reasons=reasons,
            prerequisite_ok=prereq_result.is_eligible,
            prerequisite_suggestions=prereq_suggestions,
            schedule_conflicts=my_conflicts,
            alternative_courses=alternatives,
        ))

    return recommendations


def top_recommendations_for_role(career_role: str, completed_courses: List[str],
                                  student_skills: List[str], top_n: int = 8,
                                  courses_df=None, prereq_df=None, schedules_df=None,
                                  career_df=None, outcomes_df=None, req_df=None) -> List[Recommendation]:
    """
    Instead of scoring a student-picked selection, this scores EVERY course
    relevant to the career role (that the student hasn't already completed)
    and returns the top-N by overall quality score -- used for the
    'Recommendation Results' page when the student hasn't chosen electives yet.
    """
    if courses_df is None:
        courses_df = dl.load_courses()
    if career_df is None:
        career_df = dl.load_career_pathways()

    completed_set = set(completed_courses or [])
    candidate_ids = career_df[career_df["career_role"] == career_role]["course_id"].tolist()
    candidate_ids = [c for c in candidate_ids if c not in completed_set]

    # Evaluate every relevant candidate INDEPENDENTLY (other_selected=[])
    # because the student hasn't committed to a concrete combination yet --
    # checking every candidate pairwise against every other candidate would
    # produce spurious conflicts between courses the student was never
    # going to pick together. Schedule conflicts are re-checked precisely
    # once the student actually adds courses to their real selection
    # (see recommend_for_student, used on the Course Explorer / selection
    # pages). Unlike the naive baseline (which sorts purely by relevance),
    # this ranking still actively filters out courses the student is NOT
    # eligible for due to missing prerequisites.
    recs = []
    for course_id in candidate_ids:
        quality = compute_quality_score(
            course_id, career_role, completed_courses, student_skills, [],
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )
        prereq_result = check_prerequisites(course_id, completed_courses, courses_df, prereq_df)
        reasons = list(quality.explanation)

        if not prereq_result.is_eligible:
            verdict = "Not Recommended"
            reasons.append(prereq_result.message)
        elif quality.overall >= 70:
            verdict = "Recommended"
        elif quality.overall >= 50:
            verdict = "Recommended with caution"
        else:
            verdict = "Not Recommended"
            reasons.append(
                f"Overall Course Choice Quality ({quality.overall}/100) is too low, "
                f"mainly due to weak career alignment and/or skill coverage."
            )

        prereq_suggestions = []
        if not prereq_result.is_eligible:
            prereq_suggestions = suggest_prerequisite_path(course_id, completed_courses, courses_df, prereq_df)

        crow = dl.get_course_row(courses_df, course_id)
        recs.append(Recommendation(
            course_id=course_id,
            course_name=crow["course_name"] if crow is not None else course_id,
            quality=quality,
            verdict=verdict,
            reasons=reasons,
            prerequisite_ok=prereq_result.is_eligible,
            prerequisite_suggestions=prereq_suggestions,
            schedule_conflicts=[],
            alternative_courses=[],
        ))

    eligible = [r for r in recs if r.verdict != "Not Recommended"]
    ineligible = [r for r in recs if r.verdict == "Not Recommended"]

    eligible.sort(key=lambda r: r.quality.overall, reverse=True)
    ineligible.sort(key=lambda r: r.quality.overall, reverse=True)

    # Prefer eligible courses; only fall back to ineligible ones (still
    # clearly labelled "Not Recommended") if there aren't enough eligible
    # candidates to fill top_n.
    ordered = eligible + ineligible
    return ordered[:top_n]
