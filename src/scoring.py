"""
scoring.py
-----------
Computes the explainable "Course Choice Quality Score" (0-100) for a
course, given a student profile and the rest of their current selection.
The overall score is a weighted blend of five sub-scores, all of which are
shown to the student individually so the number is never a black box.

    Career Alignment      (weight 0.30)
    Prerequisite Readiness (weight 0.25)
    Schedule Compatibility (weight 0.20)
    Skill Coverage         (weight 0.15)
    Outcome Alignment      (weight 0.10)
"""
from dataclasses import dataclass
from typing import List

from src import data_loader as dl
from src.prerequisite_checker import check_prerequisites
from src.schedule_checker import check_schedule_conflicts
from src.career_analyzer import analyze_course_for_career

WEIGHTS = {
    "career_alignment": 0.30,
    "prerequisite_readiness": 0.25,
    "schedule_compatibility": 0.20,
    "skill_coverage": 0.15,
    "outcome_alignment": 0.10,
}


@dataclass
class QualityScore:
    course_id: str
    course_name: str
    career_alignment: float
    prerequisite_readiness: float
    schedule_compatibility: float
    skill_coverage: float
    outcome_alignment: float
    overall: float
    explanation: List[str]


def _outcome_alignment_score(course_id: str, career_role: str, outcomes_df, career_df) -> float:
    """
    Proxy for how well a course's stated outcomes align with the career role:
    derived from the same relevance score used for career alignment, since
    course outcomes are the mechanism through which a course delivers that
    relevance. We damp it slightly so it is not a pure duplicate signal.
    """
    relevance = dl.get_relevance(career_df, career_role, course_id)
    has_outcomes = not outcomes_df[outcomes_df["course_id"] == course_id].empty
    if not has_outcomes:
        return round(relevance * 0.5, 1)
    return round(min(100, relevance * 0.9 + 10), 1)


def compute_quality_score(course_id: str, student_career_role: str,
                           completed_courses: List[str], student_skills: List[str],
                           other_selected_courses: List[str] = None,
                           courses_df=None, prereq_df=None, schedules_df=None,
                           career_df=None, outcomes_df=None, req_df=None) -> QualityScore:
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

    other_selected_courses = other_selected_courses or []
    course_row = dl.get_course_row(courses_df, course_id)
    course_name = course_row["course_name"] if course_row is not None else course_id

    explanation = []

    # 1. Career alignment
    align_result = analyze_course_for_career(
        course_id, student_career_role, student_skills, courses_df, career_df, req_df
    )
    career_alignment = float(align_result.relevance_score)
    explanation.append(align_result.explanation)

    # 2. Prerequisite readiness
    prereq_result = check_prerequisites(course_id, completed_courses, courses_df, prereq_df)
    prereq_readiness = prereq_result.readiness_score
    explanation.append(prereq_result.message)

    # 3. Schedule compatibility
    all_courses_to_check = list(other_selected_courses) + [course_id]
    conflicts = check_schedule_conflicts(all_courses_to_check, courses_df, schedules_df)
    relevant_conflicts = [c for c in conflicts if course_id in (c.course_a, c.course_b)]
    if relevant_conflicts:
        schedule_compat = 0.0
        explanation.append(relevant_conflicts[0].message)
    else:
        schedule_compat = 100.0
        explanation.append(f"No schedule conflicts detected for {course_name}.")

    # 4. Skill coverage: proportion of the course's skills that are NEW to the student
    course_skills = dl.split_list(course_row["skills_gained"]) if course_row is not None else []
    student_skill_set = set(student_skills or [])
    if course_skills:
        new_skills = [s for s in course_skills if s not in student_skill_set]
        skill_coverage = round(100.0 * len(new_skills) / len(course_skills), 1)
    else:
        skill_coverage = 0.0
    explanation.append(
        f"{course_name} teaches {len(course_skills)} skill(s); "
        f"{len([s for s in course_skills if s not in student_skill_set])} are new to you."
    )

    # 5. Outcome alignment
    outcome_alignment = _outcome_alignment_score(course_id, student_career_role, outcomes_df, career_df)

    overall = (
        career_alignment * WEIGHTS["career_alignment"]
        + prereq_readiness * WEIGHTS["prerequisite_readiness"]
        + schedule_compat * WEIGHTS["schedule_compatibility"]
        + skill_coverage * WEIGHTS["skill_coverage"]
        + outcome_alignment * WEIGHTS["outcome_alignment"]
    )

    return QualityScore(
        course_id=course_id,
        course_name=course_name,
        career_alignment=round(career_alignment, 1),
        prerequisite_readiness=round(prereq_readiness, 1),
        schedule_compatibility=round(schedule_compat, 1),
        skill_coverage=round(skill_coverage, 1),
        outcome_alignment=round(outcome_alignment, 1),
        overall=round(overall, 1),
        explanation=explanation,
    )
