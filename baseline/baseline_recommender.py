"""
baseline_recommender.py
-------------------------
A deliberately NAIVE baseline recommender, used only as a comparison point
for the proposed (rule-based, multi-factor) recommender in src/recommender.py.

By design, the baseline:
    - Recommends courses purely by career-relevance / "popularity" score.
    - Does NOT check prerequisites.
    - Does NOT check schedule conflicts.
    - Does NOT look at the student's existing skills.

This mirrors how many real course-selection tools behave today (recommend
"popular" or "relevant" electives without checking feasibility), and is the
system the proposed engine is benchmarked against in evaluation/evaluate.py.
"""
from typing import List

from src import data_loader as dl


def baseline_recommend(career_role: str, top_n: int = 5, career_df=None) -> List[dict]:
    """Return the top-N courses by raw relevance score for a career role.
    No prerequisite or schedule awareness -- this is the point."""
    if career_df is None:
        career_df = dl.load_career_pathways()

    subset = career_df[career_df["career_role"] == career_role]
    subset = subset.sort_values("relevance_score", ascending=False).head(top_n)
    return subset.to_dict("records")


def baseline_recommend_courses(career_role: str, courses_df=None, career_df=None, top_n: int = 5) -> List[dict]:
    """Same as baseline_recommend but joined with course names for display."""
    if courses_df is None:
        courses_df = dl.load_courses()
    if career_df is None:
        career_df = dl.load_career_pathways()

    raw = baseline_recommend(career_role, top_n, career_df)
    output = []
    for row in raw:
        crow = dl.get_course_row(courses_df, row["course_id"])
        output.append({
            "course_id": row["course_id"],
            "course_name": crow["course_name"] if crow is not None else row["course_id"],
            "relevance_score": row["relevance_score"],
        })
    return output
