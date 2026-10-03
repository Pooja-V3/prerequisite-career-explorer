from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
@dataclass
class PrerequisiteResult:
    course_id: str
    course_name: str
    is_eligible: bool
    missing: List[Dict[str, Any]] | None = None
    message: str = ""
    readiness_score: float = 0.0


def check_prerequisites(
    course_id: str,
    completed_courses: List[str],
    courses_df,
    prereq_df,
) -> PrerequisiteResult:
    """
    Check whether a student has completed all prerequisites
    required for a selected course.
    """

    # Find the selected course.
    course_row = courses_df[courses_df["course_id"] == course_id]

    # Handle invalid or unknown course IDs safely.
    if course_row.empty:
        return PrerequisiteResult(
    course_id=course_id,
    course_name=course_id,
    is_eligible=False,
    missing=[],
    message=(
        f"Invalid course ID: {course_id}. "
        f"Please select a valid course."
    ),
    readiness_score=0.0,
)

    course_name = course_row.iloc[0]["course_name"]

    # Find prerequisites for the selected course.
    required = prereq_df[
        prereq_df["course_id"] == course_id
    ]

    missing = []

    for _, row in required.iterrows():
        prerequisite_id = row["prerequisite_id"]

        if prerequisite_id not in completed_courses:
            prerequisite_rows = courses_df[
                courses_df["course_id"] == prerequisite_id
            ]

            if not prerequisite_rows.empty:
                prerequisite_name = prerequisite_rows.iloc[0]["course_name"]
            else:
                prerequisite_name = prerequisite_id

            missing.append(
                {
                    "id": prerequisite_id,
                    "name": prerequisite_name,
                }
            )

    if missing:
      return PrerequisiteResult(
    course_id=course_id,
    course_name=course_name,
    is_eligible=False,
    missing=missing,
    message="Required prerequisite courses are missing.",
    readiness_score=0.0,
)

    return PrerequisiteResult(
    course_id=course_id,
    course_name=course_name,
    is_eligible=True,
    missing=[],
    message="All prerequisites are satisfied.",
    readiness_score=1.0,
)


def suggest_prerequisite_path(
    course_id: str,
    completed_courses: List[str],
    courses_df,
    prereq_df,
) -> List[str]:
    """
    Build a simple prerequisite learning path for a course.
    """

    path = []
    visited = set()

    def visit(current_course_id):
        if current_course_id in visited:
            return

        visited.add(current_course_id)

        required = prereq_df[
            prereq_df["course_id"] == current_course_id
        ]

        for _, row in required.iterrows():
            prerequisite_id = row["prerequisite_id"]

            if prerequisite_id not in completed_courses:
                visit(prerequisite_id)

        if current_course_id not in completed_courses:
            path.append(current_course_id)

    # Invalid course IDs should return an empty path.
    if courses_df[courses_df["course_id"] == course_id].empty:
        return []

    visit(course_id)

    return path


def batch_check(
    course_ids: List[str],
    completed_courses: List[str],
    courses_df,
    prereq_df,
):
    """
    Check prerequisites for multiple courses.
    """

    results = []

    for course_id in course_ids:
        results.append(
            check_prerequisites(
                course_id,
                completed_courses,
                courses_df,
                prereq_df,
            )
        )

    return results