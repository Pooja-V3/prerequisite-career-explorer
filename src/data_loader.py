"""
data_loader.py
---------------
Central place that loads every CSV in data/ into pandas DataFrames.
All other modules should read data through this module (never open CSVs
directly) so the whole app has one consistent, cache-friendly data layer.
"""
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)


def load_courses() -> pd.DataFrame:
    return pd.read_csv(_path("courses.csv"))


def load_prerequisites() -> pd.DataFrame:
    return pd.read_csv(_path("prerequisites.csv"))


def load_course_outcomes() -> pd.DataFrame:
    return pd.read_csv(_path("course_outcomes.csv"))


def load_schedules() -> pd.DataFrame:
    return pd.read_csv(_path("schedules.csv"))


def load_career_pathways() -> pd.DataFrame:
    return pd.read_csv(_path("career_pathways.csv"))


def load_career_required_skills() -> pd.DataFrame:
    return pd.read_csv(_path("career_required_skills.csv"))


def load_students() -> pd.DataFrame:
    return pd.read_csv(_path("students.csv"))


def load_all() -> dict:
    """Convenience loader returning every table in one dict."""
    return {
        "courses": load_courses(),
        "prerequisites": load_prerequisites(),
        "outcomes": load_course_outcomes(),
        "schedules": load_schedules(),
        "career_pathways": load_career_pathways(),
        "career_required_skills": load_career_required_skills(),
        "students": load_students(),
    }


# ---------------------------------------------------------------------------
# Small helpers used throughout the app
# ---------------------------------------------------------------------------
def split_list(value) -> list:
    """Split a ';'-separated CSV cell into a clean list of strings."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    value = str(value).strip()
    if not value:
        return []
    return [v.strip() for v in value.split(";") if v.strip()]


def get_course_row(courses_df: pd.DataFrame, course_id: str):
    row = courses_df[courses_df["course_id"] == course_id]
    if row.empty:
        return None
    return row.iloc[0]


def get_prerequisites_for(prereq_df: pd.DataFrame, course_id: str) -> list:
    return prereq_df[prereq_df["course_id"] == course_id]["prerequisite_id"].tolist()


def get_outcomes_for(outcomes_df: pd.DataFrame, course_id: str) -> list:
    return outcomes_df[outcomes_df["course_id"] == course_id]["outcome"].tolist()


def get_schedule_for(schedules_df: pd.DataFrame, course_id: str):
    row = schedules_df[schedules_df["course_id"] == course_id]
    if row.empty:
        return None
    return row.iloc[0]


def get_relevance(career_df: pd.DataFrame, career_role: str, course_id: str) -> int:
    row = career_df[(career_df["career_role"] == career_role) & (career_df["course_id"] == course_id)]
    if row.empty:
        return 0
    return int(row.iloc[0]["relevance_score"])


def get_required_skills(req_df: pd.DataFrame, career_role: str) -> list:
    row = req_df[req_df["career_role"] == career_role]
    if row.empty:
        return []
    return split_list(row.iloc[0]["required_skills"])
