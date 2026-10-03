"""
schedule_checker.py
---------------------
Detects timetable overlaps between a set of selected courses and suggests
alternative (non-conflicting) courses that lead to the same career goal,
when available.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List

from src import data_loader as dl


def _to_minutes(hhmm: str) -> int:
    t = datetime.strptime(hhmm.strip(), "%H:%M")
    return t.hour * 60 + t.minute


def _overlaps(day1, start1, end1, day2, start2, end2) -> bool:
    if day1 != day2:
        return False
    s1, e1 = _to_minutes(start1), _to_minutes(end1)
    s2, e2 = _to_minutes(start2), _to_minutes(end2)
    return s1 < e2 and s2 < e1


@dataclass
class ScheduleConflict:
    course_a: str
    course_a_name: str
    course_b: str
    course_b_name: str
    day: str
    time_a: str
    time_b: str

    @property
    def message(self) -> str:
        return (
            f"Schedule Conflict Detected: {self.course_a_name} ({self.time_a}) "
            f"and {self.course_b_name} ({self.time_b}) both fall on {self.day}."
        )


def check_schedule_conflicts(course_ids: List[str], courses_df=None, schedules_df=None) -> List[ScheduleConflict]:
    if courses_df is None:
        courses_df = dl.load_courses()
    if schedules_df is None:
        schedules_df = dl.load_schedules()

    conflicts = []
    ids = list(dict.fromkeys(course_ids))  # de-dupe, preserve order

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            sched_a = dl.get_schedule_for(schedules_df, a)
            sched_b = dl.get_schedule_for(schedules_df, b)
            if sched_a is None or sched_b is None:
                continue
            if _overlaps(sched_a["day"], sched_a["start_time"], sched_a["end_time"],
                         sched_b["day"], sched_b["start_time"], sched_b["end_time"]):
                name_a = dl.get_course_row(courses_df, a)["course_name"]
                name_b = dl.get_course_row(courses_df, b)["course_name"]
                conflicts.append(ScheduleConflict(
                    course_a=a, course_a_name=name_a,
                    course_b=b, course_b_name=name_b,
                    day=sched_a["day"],
                    time_a=f"{sched_a['start_time']}-{sched_a['end_time']}",
                    time_b=f"{sched_b['start_time']}-{sched_b['end_time']}",
                ))
    return conflicts


def suggest_alternatives(conflicting_course_id: str, career_role: str,
                          excluded_ids: List[str], courses_df=None,
                          schedules_df=None, career_df=None, top_n: int = 3) -> List[dict]:
    """
    Suggest other courses relevant to the same career role that do NOT
    clash with any course in `excluded_ids` (the student's current
    selection minus the conflicting course itself).
    """
    if courses_df is None:
        courses_df = dl.load_courses()
    if schedules_df is None:
        schedules_df = dl.load_schedules()
    if career_df is None:
        career_df = dl.load_career_pathways()

    candidates = career_df[career_df["career_role"] == career_role].sort_values(
        "relevance_score", ascending=False
    )

    suggestions = []
    for _, row in candidates.iterrows():
        cid = row["course_id"]
        if cid == conflicting_course_id or cid in excluded_ids:
            continue
        sched = dl.get_schedule_for(schedules_df, cid)
        if sched is None:
            continue
        clashes = False
        for other in excluded_ids:
            other_sched = dl.get_schedule_for(schedules_df, other)
            if other_sched is None:
                continue
            if _overlaps(sched["day"], sched["start_time"], sched["end_time"],
                         other_sched["day"], other_sched["start_time"], other_sched["end_time"]):
                clashes = True
                break
        if not clashes:
            crow = dl.get_course_row(courses_df, cid)
            suggestions.append({
                "id": cid,
                "name": crow["course_name"],
                "relevance": int(row["relevance_score"]),
                "day": sched["day"],
                "time": f"{sched['start_time']}-{sched['end_time']}",
            })
        if len(suggestions) >= top_n:
            break
    return suggestions
