"""
Prerequisite & Career Consequence Explorer
============================================
Main Streamlit entrypoint. Run with:  streamlit run app.py

Helps students pick electives by explaining -- not just recommending --
whether a course fits their prerequisites, schedule, and career goal.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import theme
from src.prerequisite_checker import check_prerequisites, suggest_prerequisite_path, batch_check
from src.schedule_checker import check_schedule_conflicts, suggest_alternatives
from src.career_analyzer import analyze_course_for_career, analyze_selection, recommend_courses_for_role
from src.scoring import compute_quality_score
from src.recommender import recommend_for_student, top_recommendations_for_role
from baseline.baseline_recommender import baseline_recommend_courses

st.set_page_config(
    page_title="Prerequisite & Career Consequence Explorer",
    page_icon="🎓",
    layout="wide",
)
theme.inject_css()

CAREER_ROLES = [
    "Backend Developer", "Full Stack Developer", "Data Scientist",
    "Cloud Engineer", "Cybersecurity Analyst", "Software Developer",
]

PAGES = [
    "🏠 Home / Dashboard",
    "🧑‍🎓 Student Profile",
    "📚 Course Explorer",
    "⚖️ Course Comparison",
    "🧭 Career Pathway Explorer",
    "✅ Recommendation Results",
    "📊 Evaluation / Baseline Comparison",
    "🧪 Test Cases",
    "🛠️ Admin / Data Management",
    "⚠️ Risks & Limitations",
]


# ---------------------------------------------------------------------------
# Data loading (cached) + session state
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_data():
    return dl.load_all()


def init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = {
            "name": "",
            "career_goal": CAREER_ROLES[0],
            "completed_courses": [],
            "skills": [],
            "preferred_job_role": CAREER_ROLES[0],
        }
    if "selection" not in st.session_state:
        st.session_state.selection = []


init_state()
data = get_data()
courses_df = data["courses"]
prereq_df = data["prerequisites"]
outcomes_df = data["outcomes"]
schedules_df = data["schedules"]
career_df = data["career_pathways"]
req_df = data["career_required_skills"]
students_df = data["students"]

course_name_map = dict(zip(courses_df["course_id"], courses_df["course_name"]))


def course_label(cid: str) -> str:
    return f"{cid} — {course_name_map.get(cid, cid)}"


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.markdown("## 🎓 Prerequisite & Career\nConsequence Explorer")
st.sidebar.caption("Placement-cell elective advisory system")
page = st.sidebar.radio("Navigate", PAGES, label_visibility="collapsed")

st.sidebar.markdown("---")
profile = st.session_state.profile
if profile["name"]:
    st.sidebar.markdown(f"**Student:** {profile['name']}")
    st.sidebar.markdown(f"**Career goal:** {profile['career_goal']}")
    st.sidebar.markdown(f"**Completed:** {len(profile['completed_courses'])} course(s)")
else:
    st.sidebar.info("No profile set yet — visit **Student Profile** first.")

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Courses under consideration:** {len(st.session_state.selection)}")
if st.session_state.selection:
    for cid in st.session_state.selection:
        st.sidebar.caption(f"• {course_label(cid)}")
    if st.sidebar.button("Clear selection"):
        st.session_state.selection = []
        st.rerun()


# ===========================================================================
# PAGE 1 — HOME / DASHBOARD
# ===========================================================================
def page_home():
    st.title("🎓 Prerequisite & Career Consequence Explorer")
    st.markdown(
        "A placement-cell tool that helps students pick electives by explaining "
        "**why** a course fits — or doesn't — before they select it."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Electives", len(courses_df))
    c2.metric("Career Pathways", career_df["career_role"].nunique())
    c3.metric("Prerequisite Links", len(prereq_df))
    c4.metric("Students in Sample Data", len(students_df))

    st.markdown("### How the workflow fits together")
    st.markdown(
        "**Student Profile → Career Goal → Course Selection → Prerequisite Check → "
        "Schedule Check → Course Outcome Analysis → Career Alignment → Quality Score → "
        "Recommendation → Alternative Courses**"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Electives by Category")
        cat_counts = courses_df["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]
        fig = px.bar(cat_counts, x="category", y="count", color="category",
                     color_discrete_sequence=[theme.PRIMARY, theme.ACCENT])
        fig.update_layout(showlegend=False, plot_bgcolor="white", height=340)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Courses Mapped per Career Pathway")
        role_counts = career_df.groupby("career_role")["course_id"].count().reset_index()
        role_counts.columns = ["career_role", "count"]
        fig2 = px.bar(role_counts.sort_values("count"), x="count", y="career_role", orientation="h",
                      color_discrete_sequence=[theme.PRIMARY_LIGHT])
        fig2.update_layout(plot_bgcolor="white", height=340)
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### Get started")
    b1, b2, b3 = st.columns(3)
    b1.info("**1. Set up your profile**\n\nGo to *Student Profile* and enter your career goal, completed courses and skills.")
    b2.info("**2. Explore courses**\n\nBrowse *Course Explorer*, add electives you're considering to your selection.")
    b3.info("**3. Get your recommendation**\n\nOpen *Recommendation Results* for a full, explained verdict on each course.")


# ===========================================================================
# PAGE 2 — STUDENT PROFILE
# ===========================================================================
def page_profile():
    st.title("🧑‍🎓 Student Profile")
    st.markdown("Tell us about yourself so every recommendation can be personalised and explained.")

    with st.form("profile_form"):
        name = st.text_input("Student name", value=profile["name"])
        career_goal = st.selectbox("Career goal", CAREER_ROLES,
                                    index=CAREER_ROLES.index(profile["career_goal"]) if profile["career_goal"] in CAREER_ROLES else 0)
        preferred_role = st.selectbox("Preferred job role", CAREER_ROLES,
                                       index=CAREER_ROLES.index(profile["preferred_job_role"]) if profile["preferred_job_role"] in CAREER_ROLES else 0)

        course_options = courses_df["course_id"].tolist()
        completed = st.multiselect(
            "Completed courses",
            options=course_options,
            default=profile["completed_courses"],
            format_func=course_label,
        )

        all_skills = sorted({s for skills in courses_df["skills_gained"].apply(dl.split_list) for s in skills})
        skills = st.multiselect("Existing skills", options=all_skills, default=profile["skills"])

        submitted = st.form_submit_button("Save profile", type="primary")

    if submitted:
        st.session_state.profile = {
            "name": name.strip() or "Guest Student",
            "career_goal": career_goal,
            "completed_courses": completed,
            "skills": skills,
            "preferred_job_role": preferred_role,
        }
        st.success(f"Profile saved for {st.session_state.profile['name']}. "
                   f"Head to **Recommendation Results** to see your personalised analysis.")
        st.rerun()

    if profile["name"]:
        st.markdown("### Current profile")
        p1, p2 = st.columns(2)
        with p1:
            st.markdown(f"**Name:** {profile['name']}")
            st.markdown(f"**Career goal:** {profile['career_goal']}")
            st.markdown(f"**Preferred job role:** {profile['preferred_job_role']}")
        with p2:
            st.markdown("**Completed courses:**")
            if profile["completed_courses"]:
                st.markdown("".join(theme.tag(course_label(c)) for c in profile["completed_courses"]), unsafe_allow_html=True)
            else:
                st.markdown("_None yet_")
            st.markdown("**Skills:**")
            if profile["skills"]:
                st.markdown("".join(theme.tag(s) for s in profile["skills"]), unsafe_allow_html=True)
            else:
                st.markdown("_None yet_")

    st.markdown("---")
    st.markdown("#### Try a sample profile")
    sample_cols = st.columns(len(students_df))
    for i, (_, srow) in enumerate(students_df.iterrows()):
        with sample_cols[i]:
            if st.button(srow["name"], key=f"sample_{srow['student_id']}"):
                st.session_state.profile = {
                    "name": srow["name"],
                    "career_goal": srow["career_goal"],
                    "completed_courses": dl.split_list(srow["completed_courses"]),
                    "skills": dl.split_list(srow["skills"]),
                    "preferred_job_role": srow["preferred_job_role"],
                }
                st.rerun()


# ===========================================================================
# PAGE 3 — COURSE EXPLORER
# ===========================================================================
def page_course_explorer():
    st.title("📚 Course Explorer")
    st.markdown("Browse every elective. Add the ones you're considering to your selection for a full check later.")

    f1, f2, f3 = st.columns(3)
    category_filter = f1.selectbox("Category", ["All"] + sorted(courses_df["category"].unique().tolist()))
    role_filter = f2.selectbox("Relevant to career role", ["All"] + CAREER_ROLES)
    search = f3.text_input("Search by name")

    filtered = courses_df.copy()
    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]
    if search:
        filtered = filtered[filtered["course_name"].str.contains(search, case=False)]
    if role_filter != "All":
        relevant_ids = career_df[career_df["career_role"] == role_filter]["course_id"].tolist()
        filtered = filtered[filtered["course_id"].isin(relevant_ids)]

    st.caption(f"{len(filtered)} course(s) shown")

    for _, row in filtered.iterrows():
        cid = row["course_id"]
        with st.expander(f"**{row['course_name']}**  ·  {row['category']}  ·  {row['credits']} credits"):
            st.markdown(f"_{row['description']}_")

            colA, colB = st.columns(2)
            with colA:
                st.markdown("**Prerequisites**")
                prereqs = dl.get_prerequisites_for(prereq_df, cid)
                if prereqs:
                    for pid in prereqs:
                        st.markdown(f"- {course_label(pid)}")
                else:
                    st.markdown("_None_")

                st.markdown("**Schedule**")
                sched = dl.get_schedule_for(schedules_df, cid)
                if sched is not None:
                    st.markdown(f"{sched['day']}, {sched['start_time']}–{sched['end_time']} ({sched['room']})")

                st.markdown("**Skills gained**")
                st.markdown("".join(theme.tag(s) for s in dl.split_list(row["skills_gained"])), unsafe_allow_html=True)

            with colB:
                st.markdown("**Course outcomes**")
                for o in dl.get_outcomes_for(outcomes_df, cid):
                    st.markdown(f"- {o}")

                st.markdown("**Relevant career roles**")
                rel = career_df[career_df["course_id"] == cid].sort_values("relevance_score", ascending=False)
                if not rel.empty:
                    for _, r in rel.iterrows():
                        st.markdown(f"- {r['career_role']} ({r['relevance_score']}/100)")
                else:
                    st.markdown("_Not specifically mapped to a career pathway_")

            already_in = cid in st.session_state.selection
            if already_in:
                if st.button(f"Remove from selection", key=f"remove_{cid}"):
                    st.session_state.selection.remove(cid)
                    st.rerun()
            else:
                if st.button(f"Add to my selection", key=f"add_{cid}"):
                    st.session_state.selection.append(cid)
                    st.rerun()


# ===========================================================================
# PAGE 4 — COURSE COMPARISON
# ===========================================================================
def page_comparison():
    st.title("⚖️ Course Comparison")
    st.markdown("Compare 2–4 courses side by side against your career goal.")

    chosen = st.multiselect(
        "Choose courses to compare",
        options=courses_df["course_id"].tolist(),
        default=st.session_state.selection[:4],
        format_func=course_label,
        max_selections=4,
    )

    if len(chosen) < 2:
        st.info("Select at least 2 courses to compare.")
        return

    career_role = profile["career_goal"]
    completed = profile["completed_courses"]

    cols = st.columns(len(chosen))
    for i, cid in enumerate(chosen):
        row = dl.get_course_row(courses_df, cid)
        with cols[i]:
            st.markdown(f"#### {row['course_name']}")
            st.caption(row["category"])

            pr = check_prerequisites(cid, completed, courses_df, prereq_df)
            st.markdown("**Prerequisites**")
            if not dl.get_prerequisites_for(prereq_df, cid):
                st.markdown("_None_")
            else:
                for s in pr.satisfied:
                    st.markdown(f'<span class="pc-check">✓</span> {s["name"]}', unsafe_allow_html=True)
                for m in pr.missing:
                    st.markdown(f'<span class="pc-cross">✗</span> {m["name"]}', unsafe_allow_html=True)

            sched = dl.get_schedule_for(schedules_df, cid)
            st.markdown("**Schedule**")
            st.markdown(f"{sched['day']} {sched['start_time']}–{sched['end_time']}" if sched is not None else "_Not scheduled_")

            align = analyze_course_for_career(cid, career_role, profile["skills"], courses_df, career_df, req_df)
            st.markdown("**Career relevance**")
            st.metric(f"{career_role}", f"{align.relevance_score}/100")

            st.markdown("**Skills gained**")
            st.markdown("".join(theme.tag(s) for s in dl.split_list(row["skills_gained"])), unsafe_allow_html=True)

            st.markdown("**Outcomes**")
            for o in dl.get_outcomes_for(outcomes_df, cid):
                st.markdown(f"- {o}")

    st.markdown("### Relevance comparison")
    rel_data = []
    for cid in chosen:
        align = analyze_course_for_career(cid, career_role, profile["skills"], courses_df, career_df, req_df)
        rel_data.append({"Course": course_name_map[cid], "Relevance": align.relevance_score})
    fig = px.bar(pd.DataFrame(rel_data), x="Course", y="Relevance", color="Course",
                 color_discrete_sequence=px.colors.qualitative.Prism)
    fig.update_layout(showlegend=False, plot_bgcolor="white", yaxis_range=[0, 100])
    st.plotly_chart(fig, use_container_width=True)


# ===========================================================================
# PAGE 5 — CAREER PATHWAY EXPLORER
# ===========================================================================
def page_career_pathway():
    st.title("🧭 Career Pathway Explorer")
    role = st.selectbox("Choose a career role", CAREER_ROLES,
                         index=CAREER_ROLES.index(profile["career_goal"]))

    required = dl.get_required_skills(req_df, role)
    st.markdown("### Required skill set")
    st.markdown("".join(theme.tag(s) for s in required), unsafe_allow_html=True)

    st.markdown("### Mapped electives, ranked by relevance")
    subset = career_df[career_df["career_role"] == role].sort_values("relevance_score", ascending=False)
    subset = subset.merge(courses_df[["course_id", "course_name", "category", "credits"]], on="course_id")

    fig = px.bar(subset, x="relevance_score", y="course_name", orientation="h",
                 color="relevance_score", color_continuous_scale=["#EFE9DD", theme.ACCENT, theme.PRIMARY])
    fig.update_layout(height=max(400, len(subset) * 32), plot_bgcolor="white", yaxis_title="", xaxis_title="Relevance score")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Course details for this pathway")
    for _, row in subset.iterrows():
        cid = row["course_id"]
        prereqs = dl.get_prerequisites_for(prereq_df, cid)
        prereq_txt = ", ".join(course_name_map.get(p, p) for p in prereqs) if prereqs else "None"
        st.markdown(
            f'<div class="pc-card"><b>{row["course_name"]}</b> — relevance {row["relevance_score"]}/100'
            f'<br><span class="pc-muted">Prerequisites: {prereq_txt}</span></div>',
            unsafe_allow_html=True,
        )


# ===========================================================================
# PAGE 6 — RECOMMENDATION RESULTS  (core end-to-end workflow)
# ===========================================================================
def page_recommendations():
    st.title("✅ Recommendation Results")

    if not profile["name"]:
        st.warning("Please fill in your **Student Profile** first so recommendations can be personalised.")
        return

    career_role = profile["career_goal"]
    completed = profile["completed_courses"]
    skills = profile["skills"]

    st.markdown(
        f"Analysing for **{profile['name']}** — career goal: **{career_role}** — "
        f"{len(completed)} completed course(s), {len(skills)} skill(s)."
    )

    tab1, tab2 = st.tabs(["Your Selected Courses", "Top Recommendations for Your Career"])

    with tab1:
        if not st.session_state.selection:
            st.info("You haven't added any courses to your selection yet. Go to **Course Explorer** and add some, "
                     "or check the **Top Recommendations** tab.")
        else:
            recs = recommend_for_student(
                career_role, completed, skills, st.session_state.selection,
                courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
            )
            _render_recommendations(recs, completed)

    with tab2:
        st.caption("Courses ranked by the explainable engine among everything relevant to your career goal.")
        top_recs = top_recommendations_for_role(
            career_role, completed, skills, 8,
            courses_df, prereq_df, schedules_df, career_df, outcomes_df, req_df,
        )
        _render_recommendations(top_recs, completed, allow_add=True)


def _render_recommendations(recs, completed, allow_add=False):
    for rec in recs:
        q = rec.quality
        with st.container():
            st.markdown('<div class="pc-card">', unsafe_allow_html=True)
            top_col1, top_col2 = st.columns([3, 1])
            with top_col1:
                st.markdown(f"#### {rec.course_name}")
                st.markdown(theme.verdict_badge(rec.verdict), unsafe_allow_html=True)
            with top_col2:
                st.metric("Overall Quality", f"{q.overall}/100")

            sub_cols = st.columns(5)
            sub_cols[0].metric("Career Alignment", q.career_alignment)
            sub_cols[1].metric("Prereq Readiness", q.prerequisite_readiness)
            sub_cols[2].metric("Schedule Compat.", q.schedule_compatibility)
            sub_cols[3].metric("Skill Coverage", q.skill_coverage)
            sub_cols[4].metric("Outcome Alignment", q.outcome_alignment)

            st.markdown("**Why this verdict:**")
            for reason in rec.reasons:
                st.markdown(f"- {reason}")

            if not rec.prerequisite_ok:
                st.markdown("**Prerequisite status:**")
                pr = check_prerequisites(rec.course_id, completed, courses_df, prereq_df)
                for s in pr.satisfied:
                    st.markdown(f'<span class="pc-check">✓</span> {s["name"]}', unsafe_allow_html=True)
                for m in pr.missing:
                    st.markdown(f'<span class="pc-cross">✗</span> {m["name"]}', unsafe_allow_html=True)
                if rec.prerequisite_suggestions:
                    names = ", ".join(p["name"] for p in rec.prerequisite_suggestions)
                    st.warning(f"Suggested path: complete {names} first.")

            if rec.schedule_conflicts:
                st.markdown("**Schedule conflicts:**")
                for c in rec.schedule_conflicts:
                    st.error(c.message)
                if rec.alternative_courses:
                    st.markdown("**Suggested alternatives (no clash):**")
                    for alt in rec.alternative_courses:
                        st.markdown(f"- {alt['name']} — {alt['day']} {alt['time']} (relevance {alt['relevance']}/100)")

            if allow_add and rec.course_id not in st.session_state.selection:
                if st.button(f"Add to my selection", key=f"rec_add_{rec.course_id}"):
                    st.session_state.selection.append(rec.course_id)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)


# ===========================================================================
# PAGE 7 — EVALUATION / BASELINE COMPARISON
# ===========================================================================
def page_evaluation():
    st.title("📊 Evaluation: Baseline vs Proposed System")
    st.markdown(
        "The **baseline** recommends courses purely by career relevance/popularity, "
        "ignoring prerequisites and schedule conflicts — a naive approach common in "
        "many real course-advisory tools. The **proposed system** additionally checks "
        "prerequisite readiness, schedule compatibility, and skill coverage before "
        "recommending anything."
    )

    if st.button("Run evaluation on sample students", type="primary"):
        with st.spinner("Running baseline and proposed recommenders on all sample students..."):
            from evaluation.evaluate import run_evaluation, summarize
            results = run_evaluation()
            summary = summarize(results)
            st.session_state["eval_results"] = results
            st.session_state["eval_summary"] = summary

    if "eval_summary" in st.session_state:
        st.markdown("### Summary")
        st.dataframe(st.session_state["eval_summary"], use_container_width=True, hide_index=True)

        summary = st.session_state["eval_summary"]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Baseline", x=summary["Metric"], y=summary["Baseline"], marker_color=theme.MUTED))
        fig.add_trace(go.Bar(name="Proposed System", x=summary["Metric"], y=summary["Proposed System"], marker_color=theme.PRIMARY))
        fig.update_layout(barmode="group", plot_bgcolor="white", height=420, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Per-student results")
        st.dataframe(st.session_state["eval_results"], use_container_width=True, hide_index=True)
    else:
        st.info("Click the button above to run the comparison.")


# ===========================================================================
# PAGE 8 — TEST CASES
# ===========================================================================
def page_test_cases():
    st.title("🧪 Test Cases")
    st.markdown("Five required failure/edge cases, each with an **expected** and **actual** result.")

    if st.button("Run all test cases", type="primary"):
        import io
        from contextlib import redirect_stdout
        from tests.test_cases import run_all

        buf = io.StringIO()
        with redirect_stdout(buf):
            results = run_all()
        st.session_state["test_output"] = buf.getvalue()
        st.session_state["test_results"] = results

    if "test_output" in st.session_state:
        passed = sum(1 for r in st.session_state["test_results"] if r)
        total = len(st.session_state["test_results"])
        if passed == total:
            st.success(f"{passed}/{total} test cases passed")
        else:
            st.warning(f"{passed}/{total} test cases passed")
        st.code(st.session_state["test_output"], language="text")
    else:
        st.info("Click the button above to run the test suite.")


# ===========================================================================
# PAGE 9 — ADMIN / DATA MANAGEMENT
# ===========================================================================
def page_admin():
    st.title("🛠️ Admin / Data Management")
    st.caption("Simple CRUD for placement-cell staff to keep course data current.")

    tab1, tab2, tab3, tab4 = st.tabs(["Courses", "Prerequisites", "Schedules", "Career Pathways"])

    with tab1:
        st.markdown("#### All courses")
        st.dataframe(courses_df, use_container_width=True, hide_index=True)
        with st.form("add_course"):
            st.markdown("**Add a new course**")
            cid = st.text_input("Course ID (e.g. C039)")
            cname = st.text_input("Course name")
            desc = st.text_area("Description")
            credits = st.number_input("Credits", min_value=1, max_value=6, value=3)
            category = st.selectbox("Category", ["Foundational", "Elective"])
            skills = st.text_input("Skills gained (semicolon-separated)")
            if st.form_submit_button("Add course"):
                if not cid or not cname:
                    st.error("Course ID and name are required.")
                elif cid in courses_df["course_id"].values:
                    st.error(f"Course ID {cid} already exists.")
                else:
                    new_row = pd.DataFrame([{
                        "course_id": cid, "course_name": cname, "description": desc,
                        "credits": credits, "category": category, "skills_gained": skills,
                    }])
                    updated = pd.concat([courses_df, new_row], ignore_index=True)
                    updated.to_csv(os.path.join(dl.DATA_DIR, "courses.csv"), index=False)
                    st.cache_data.clear()
                    st.success(f"Added {cname} ({cid}).")
                    st.rerun()

    with tab2:
        st.markdown("#### All prerequisite links")
        st.dataframe(prereq_df, use_container_width=True, hide_index=True)
        with st.form("add_prereq"):
            st.markdown("**Add a prerequisite link**")
            c1, c2 = st.columns(2)
            course_id = c1.selectbox("Course", courses_df["course_id"].tolist(), format_func=course_label, key="prereq_course")
            prereq_id = c2.selectbox("Requires (prerequisite)", courses_df["course_id"].tolist(), format_func=course_label, key="prereq_prereq")
            if st.form_submit_button("Add prerequisite link"):
                if course_id == prereq_id:
                    st.error("A course cannot be its own prerequisite.")
                else:
                    new_row = pd.DataFrame([{"course_id": course_id, "prerequisite_id": prereq_id}])
                    updated = pd.concat([prereq_df, new_row], ignore_index=True).drop_duplicates()
                    updated.to_csv(os.path.join(dl.DATA_DIR, "prerequisites.csv"), index=False)
                    st.cache_data.clear()
                    st.success("Prerequisite link added.")
                    st.rerun()

    with tab3:
        st.markdown("#### All schedules")
        st.dataframe(schedules_df, use_container_width=True, hide_index=True)
        with st.form("edit_schedule"):
            st.markdown("**Set / update a course's schedule**")
            course_id = st.selectbox("Course", courses_df["course_id"].tolist(), format_func=course_label, key="sched_course")
            day = st.selectbox("Day", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
            c1, c2 = st.columns(2)
            start = c1.text_input("Start time (HH:MM)", value="09:00")
            end = c2.text_input("End time (HH:MM)", value="11:00")
            room = st.text_input("Room", value="Room 101")
            if st.form_submit_button("Save schedule"):
                updated = schedules_df[schedules_df["course_id"] != course_id]
                new_row = pd.DataFrame([{"course_id": course_id, "day": day, "start_time": start, "end_time": end, "room": room}])
                updated = pd.concat([updated, new_row], ignore_index=True)
                updated.to_csv(os.path.join(dl.DATA_DIR, "schedules.csv"), index=False)
                st.cache_data.clear()
                st.success("Schedule saved.")
                st.rerun()

    with tab4:
        st.markdown("#### Career pathway relevance mapping")
        st.dataframe(career_df, use_container_width=True, hide_index=True)
        with st.form("edit_pathway"):
            st.markdown("**Set / update career relevance for a course**")
            role = st.selectbox("Career role", CAREER_ROLES)
            course_id = st.selectbox("Course", courses_df["course_id"].tolist(), format_func=course_label, key="pathway_course")
            score = st.slider("Relevance score", 0, 100, 50)
            if st.form_submit_button("Save relevance"):
                updated = career_df[~((career_df["career_role"] == role) & (career_df["course_id"] == course_id))]
                new_row = pd.DataFrame([{"career_role": role, "course_id": course_id, "relevance_score": score}])
                updated = pd.concat([updated, new_row], ignore_index=True)
                updated.to_csv(os.path.join(dl.DATA_DIR, "career_pathways.csv"), index=False)
                st.cache_data.clear()
                st.success("Career relevance saved.")
                st.rerun()


# ===========================================================================
# PAGE 10 — RISKS & LIMITATIONS
# ===========================================================================
def page_risks():
    st.title("⚠️ Risks & Limitations")

    st.markdown("### Technology benefits")
    st.markdown(
        "- Rule-based scoring is fully explainable: every number traces back to a visible reason.\n"
        "- Runs entirely on lightweight CSV/pandas storage — no ML infrastructure needed.\n"
        "- Fast to extend: new courses, career roles, or scoring factors are simple additions."
    )

    st.markdown("### Operational benefits")
    st.markdown(
        "- Reduces placement-cell advisor workload for routine prerequisite/schedule questions.\n"
        "- Gives students a consistent, documented rationale for every course choice.\n"
        "- Baseline-vs-proposed evaluation gives the institution a concrete way to track improvement."
    )

    st.markdown("### Social risks")
    st.markdown(
        "- Students from under-resourced backgrounds may over-rely on the tool instead of seeking " 
        "human guidance, widening gaps if the data doesn't reflect their situation.\n"
        "- Career-role framing can subtly narrow students' sense of options if the tool's course list "
        "is incomplete."
    )

    st.markdown("### Privacy concerns")
    st.markdown(
        "- Student profiles include completed courses and career goals — sensitive academic data that "
        "must be access-controlled and not shared beyond the placement cell without consent.\n"
        "- This prototype stores data in local CSV files with no authentication; a production deployment "
        "needs proper access control and encryption at rest."
    )

    st.markdown("### Risk of outdated data leading to wrong recommendations")
    st.markdown(
        "- Course content, prerequisites, and job-market relevance change over time. If the admin data "
        "isn't refreshed each semester, recommendations can quietly go stale.\n"
        "- Relevance scores in this prototype are illustrative and were not derived from live labour-market data."
    )

    st.markdown("### Risk of students blindly trusting the system")
    st.markdown(
        "- A 0–100 quality score can look more authoritative than it is. Students may treat it as a "
        "verdict rather than one input among several.\n"
        "- The tool cannot account for a student's personal circumstances, interests, or non-quantifiable "
        "goals the way a human advisor can."
    )

    st.markdown("### Maintenance burden")
    st.markdown(
        "- Every new elective, prerequisite change, or career-pathway shift needs a data update via the "
        "**Admin / Data Management** page — someone has to own this ongoing task.\n"
        "- Score weights (career alignment, prerequisite readiness, etc.) may need periodic re-tuning as "
        "the curriculum evolves."
    )

    st.error(
        "**A human placement-cell advisor should remain involved in every final decision.** "
        "This system is a decision-support aid, not a replacement for academic and career counselling."
    )


# ===========================================================================
# ROUTER
# ===========================================================================
ROUTES = {
    PAGES[0]: page_home,
    PAGES[1]: page_profile,
    PAGES[2]: page_course_explorer,
    PAGES[3]: page_comparison,
    PAGES[4]: page_career_pathway,
    PAGES[5]: page_recommendations,
    PAGES[6]: page_evaluation,
    PAGES[7]: page_test_cases,
    PAGES[8]: page_admin,
    PAGES[9]: page_risks,
}

ROUTES[page]()
