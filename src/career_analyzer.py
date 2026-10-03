"""
career_analyzer.py
--------------------
Compares a course (or a set of selected courses) against a student's career
goal: relevance, skills covered vs missing, and a plain-English explanation
of the career consequence of taking / skipping the course.
"""
from dataclasses import dataclass, field
from typing import List

from src import data_loader as dl


@dataclass
class CareerAlignmentResult:
    course_id: str
    course_name: str
    career_role: str
    relevance_score: int
    skills_covered: List[str] = field(default_factory=list)
    skills_still_missing: List[str] = field(default_factory=list)
    explanation: str = ""
    consequence: str = ""


def analyze_course_for_career(course_id: str, career_role: str,
                               student_skills: List[str],
                               courses_df=None, career_df=None, req_df=None) -> CareerAlignmentResult:
    if courses_df is None:
        courses_df = dl.load_courses()
    if career_df is None:
        career_df = dl.load_career_pathways()
    if req_df is None:
        req_df = dl.load_career_required_skills()

    course_row = dl.get_course_row(courses_df, course_id)
    course_name = course_row["course_name"] if course_row is not None else course_id
    course_skills = dl.split_list(course_row["skills_gained"]) if course_row is not None else []

    relevance = dl.get_relevance(career_df, career_role, course_id)
    required = set(dl.get_required_skills(req_df, career_role))
    student_skill_set = set(student_skills or [])

    # Skills this course would newly add towards the required skill set
    newly_covered = [s for s in course_skills if s in required and s not in student_skill_set]
    # After taking the course, which required skills would still be missing
    projected_known = student_skill_set | set(course_skills)
    still_missing = sorted(required - projected_known)

    result = CareerAlignmentResult(
        course_id=course_id,
        course_name=course_name,
        career_role=career_role,
        relevance_score=relevance,
        skills_covered=newly_covered,
        skills_still_missing=still_missing,
    )

    # ---- Build a plain-English explanation (never just "recommended") ----
    if relevance >= 75:
        tier = "highly relevant"
    elif relevance >= 45:
        tier = "moderately relevant"
    elif relevance > 0:
        tier = "only marginally relevant"
    else:
        tier = "not directly relevant"

    if newly_covered:
        skills_txt = ", ".join(newly_covered)
        skill_clause = f"It fills the skill gap in {skills_txt}, which {career_role} roles typically require."
    else:
        skill_clause = "It does not add any new skill that this career path is currently missing from your profile."

    result.explanation = (
        f"{course_name} is {tier} to the {career_role} pathway "
        f"(relevance score: {relevance}/100). {skill_clause}"
    )

    if relevance >= 75:
        result.consequence = (
            f"Taking {course_name} strengthens your candidacy for {career_role} roles and "
            f"is a strategically sound elective choice."
        )
    elif relevance >= 45:
        result.consequence = (
            f"Taking {course_name} gives some benefit for {career_role}, but consider "
            f"pairing it with a higher-relevance elective to strengthen your profile faster."
        )
    else:
        result.consequence = (
            f"Choosing {course_name} for a {career_role} goal is likely to use up an elective "
            f"slot without meaningfully advancing the skills recruiters screen for in this role. "
            f"This may slow down your readiness for {career_role} positions."
        )

    return result


def analyze_selection(course_ids: List[str], career_role: str, student_skills: List[str],
                       courses_df=None, career_df=None, req_df=None) -> dict:
    """
    Analyze a whole selection of courses against a career goal.
    Returns recommended vs less-relevant course lists plus overall skill gap.
    """
    if courses_df is None:
        courses_df = dl.load_courses()
    if career_df is None:
        career_df = dl.load_career_pathways()
    if req_df is None:
        req_df = dl.load_career_required_skills()

    required = set(dl.get_required_skills(req_df, career_role))
    student_skill_set = set(student_skills or [])

    results = [
        analyze_course_for_career(cid, career_role, student_skills, courses_df, career_df, req_df)
        for cid in course_ids
    ]

    recommended = [r for r in results if r.relevance_score >= 60]
    less_relevant = [r for r in results if r.relevance_score < 60]

    # Aggregate skills covered by the whole selection
    all_new_skills = set()
    for cid in course_ids:
        crow = dl.get_course_row(courses_df, cid)
        if crow is not None:
            all_new_skills |= set(dl.split_list(crow["skills_gained"]))

    projected_known = student_skill_set | all_new_skills
    missing_after_selection = sorted(required - projected_known)

    return {
        "results": results,
        "recommended": recommended,
        "less_relevant": less_relevant,
        "missing_skills_after_selection": missing_after_selection,
        "required_skills": sorted(required),
    }


def recommend_courses_for_role(career_role: str, exclude_ids: List[str] = None,
                                career_df=None, top_n: int = 10) -> List[dict]:
    """Rank all courses relevant to a career role by relevance score."""
    if career_df is None:
        career_df = dl.load_career_pathways()
    exclude_ids = set(exclude_ids or [])
    subset = career_df[career_df["career_role"] == career_role]
    subset = subset[~subset["course_id"].isin(exclude_ids)]
    subset = subset.sort_values("relevance_score", ascending=False).head(top_n)
    return subset.to_dict("records")
