"""
prerequisite_checker.py
------------------------
Rule-based prerequisite verification. Given a course and the set of courses
a student has already completed, this determines which prerequisites are
satisfied (✓) and which are missing (✗), and produces a human-readable
explanation -- exactly the "Prerequisite Conflict" style message required
by the problem statement.
"""
from dataclasses import dataclass, field
from typing import List

from src import data_loader as dl


@dataclass
class PrerequisiteResult:
    course_id: str
    course_name: str
    satisfied: List[dict] = field(default_factory=list)   # [{"id":..,"name":..}]
    missing: List[dict] = field(default_factory=list)
    is_eligible: bool = True
    message: str = ""

    @property
    def readiness_score(self) -> float:
        """0-100 score: fraction of prerequisites satisfied."""
        total = len(self.satisfied) + len(self.missing)
        if total == 0:
            return 100.0
        return round(100.0 * len(self.satisfied) / total, 1)


def check_prerequisites(course_id: str, completed_courses: List[str],
                         courses_df=None, prereq_df=None) -> PrerequisiteResult:
    """
    Check whether `completed_courses` (list of course_ids) satisfy all
    prerequisites of `course_id`.
    """
    if courses_df is None:
        courses_df = dl.load_courses()
    if prereq_df is None:
        prereq_df = dl.load_prerequisites()

    course_row = dl.get_course_row(courses_df, course_id)
    course_name = course_row["course_name"] if course_row is not None else course_id

    prereq_ids = dl.get_prerequisites_for(prereq_df, course_id)
    completed_set = set(completed_courses or [])

    result = PrerequisiteResult(course_id=course_id, course_name=course_name)

    if not prereq_ids:
        result.message = f"{course_name} has no prerequisites. You are eligible to select it."
        return result

    for pid in prereq_ids:
        prow = dl.get_course_row(courses_df, pid)
        pname = prow["course_name"] if prow is not None else pid
        entry = {"id": pid, "name": pname}
        if pid in completed_set:
            result.satisfied.append(entry)
        else:
            result.missing.append(entry)

    result.is_eligible = len(result.missing) == 0

    if result.is_eligible:
        result.message = (
            f"All prerequisites satisfied for {course_name}. "
            f"You are eligible to select this course."
        )
    else:
        missing_names = ", ".join(m["name"] for m in result.missing)
        result.message = (
            f"Prerequisite Conflict: {missing_names} "
            f"{'is' if len(result.missing) == 1 else 'are'} missing. "
            f"Complete {missing_names} before selecting {course_name}."
        )
    return result


def suggest_prerequisite_path(course_id: str, completed_courses: List[str],
                               courses_df=None, prereq_df=None) -> List[dict]:
    """
    Return an ordered list of prerequisite courses the student should take
    first, including transitive prerequisites (prerequisites-of-prerequisites),
    skipping anything already completed.
    """
    if courses_df is None:
        courses_df = dl.load_courses()
    if prereq_df is None:
        prereq_df = dl.load_prerequisites()

    completed_set = set(completed_courses or [])
    visited = set()
    ordered_path = []

    def visit(cid):
        if cid in visited:
            return
        visited.add(cid)
        for pid in dl.get_prerequisites_for(prereq_df, cid):
            visit(pid)
        if cid != course_id and cid not in completed_set:
            prow = dl.get_course_row(courses_df, cid)
            ordered_path.append({
                "id": cid,
                "name": prow["course_name"] if prow is not None else cid,
            })

    visit(course_id)
    return ordered_path


def batch_check(course_ids: List[str], completed_courses: List[str],
                 courses_df=None, prereq_df=None) -> List[PrerequisiteResult]:
    if courses_df is None:
        courses_df = dl.load_courses()
    if prereq_df is None:
        prereq_df = dl.load_prerequisites()
    return [check_prerequisites(cid, completed_courses, courses_df, prereq_df) for cid in course_ids]
