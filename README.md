# Prerequisite & Career Consequence Explorer

A working prototype that helps students choose electives by **explaining**
whether a course fits their prerequisites, schedule, and career goal —
not just recommending it.

Built for a placement-cell scenario: students often pick electives without
understanding prerequisite chains or career consequences. This tool walks
them through the full decision:

```
Student Profile → Career Goal → Course Selection → Prerequisite Check →
Schedule Check → Course Outcome Analysis → Career Alignment →
Quality Score → Recommendation → Alternative Courses
```

---

## 1. Quick start

```bash
cd course_career_explorer
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`. All data ships pre-generated in
`data/` — no setup step is required before running.

To regenerate the synthetic datasets from scratch (optional):

```bash
python3 scripts/generate_data.py
```

To run the evaluation script and test suite from the command line (in
addition to the in-app pages that do the same thing):

```bash
python3 -m evaluation.evaluate
python3 -m tests.test_cases
```

---

## 2. Project structure

```
course_career_explorer/
├── app.py                       # Streamlit entrypoint (all 10 pages)
├── data/                        # Synthetic CSV datasets
│   ├── courses.csv
│   ├── prerequisites.csv
│   ├── course_outcomes.csv
│   ├── schedules.csv
│   ├── career_pathways.csv
│   ├── career_required_skills.csv
│   └── students.csv
├── src/                         # Core rule-based engine (the PROPOSED system)
│   ├── data_loader.py           # Single source of truth for reading CSVs
│   ├── prerequisite_checker.py  # ✓ / ✗ prerequisite logic + suggested path
│   ├── schedule_checker.py      # Timetable overlap detection + alternatives
│   ├── career_analyzer.py       # Career relevance & skill-gap explanations
│   ├── scoring.py               # Explainable 0-100 Course Choice Quality Score
│   ├── recommender.py           # Full recommendation engine (uses all of the above)
│   └── theme.py                 # Shared UI styling helpers
├── baseline/
│   └── baseline_recommender.py  # Naive "relevance only" baseline system
├── evaluation/
│   └── evaluate.py              # Baseline vs. Proposed metrics + CSV export
├── tests/
│   └── test_cases.py            # 5 required failure/edge-case tests
├── scripts/
│   └── generate_data.py         # Synthetic dataset generator (source of data/)
├── requirements.txt
└── README.md
```

---

## 3. The recommendation algorithm (explainable, rule-based — no ML)

Per course, the engine computes five sub-scores (0–100) and combines them
into an **overall Course Choice Quality Score**:

| Factor                  | Weight | What it measures |
|--------------------------|--------|-------------------|
| Career Alignment          | 30%   | The course's mapped relevance score for the student's chosen career role |
| Prerequisite Readiness    | 25%   | % of the course's prerequisites the student has already completed |
| Schedule Compatibility    | 20%   | 100 if no timetable clash with the rest of the student's selection, else 0 |
| Skill Coverage            | 15%   | % of the course's taught skills that are new to the student |
| Outcome Alignment         | 10%   | How well the course's stated learning outcomes serve the career role |

```
overall = 0.30·career_alignment + 0.25·prereq_readiness + 0.20·schedule_compat
        + 0.15·skill_coverage   + 0.10·outcome_alignment
```

**Verdict rules** (fully explicit, not a black box):

- If any prerequisite is missing → **Not Recommended** (with the missing
  course named and a suggested completion order).
- Else if there's a schedule clash with another selected course →
  **Not Recommended** (with alternative, non-clashing courses suggested).
- Else if `overall ≥ 70` → **Recommended**
- Else if `overall ≥ 50` → **Recommended with caution**
- Else → **Not Recommended** (weak career/skill fit)

Every verdict is accompanied by the individual sub-scores and a
plain-English explanation — the system never just says "recommended."

### Baseline (for comparison only)

`baseline/baseline_recommender.py` implements a deliberately naive system
that ranks courses **only** by their career-relevance score, exactly like
many real course-advisory tools. It ignores prerequisites, schedules, and
the student's existing skills entirely. This is the system the proposed
engine is benchmarked against on the **Evaluation** page.

---

## 4. Features implemented (mapped to the requirements)

1. **Student Profile** — name, career goal, completed courses, skills,
   preferred job role. Sample profiles included for quick testing.
2. **Course Explorer** — all 38 courses with description, prerequisites,
   outcomes, schedule, relevant career roles, and skills gained.
3. **Prerequisite Checker** — ✓/✗ per prerequisite, "Prerequisite
   Conflict" warning message, and a suggested completion path (including
   transitive/chained prerequisites).
4. **Career Consequence Explorer** — relevance, skills covered, skills
   still missing, and a plain-English career consequence statement for
   each course (not a bare "recommended"/"not recommended" label).
5. **Schedule Conflict Detection** — pairwise timetable overlap check with
   a "Schedule Conflict Detected" message and non-clashing alternatives.
6. **Course Choice Quality Score** — the 5-factor explainable 0–100 score
   described above, shown with every sub-score broken out.
7. **Baseline comparison** — `evaluation/evaluate.py` + the in-app
   Evaluation page compare Baseline vs. Proposed on: average quality,
   prerequisite conflicts, schedule conflicts, career misalignment, and
   recommendation success rate.
8. **Testing / failure cases** — `tests/test_cases.py` implements and runs
   all 5 required cases with expected vs. actual results (see below).
9. **Dataset** — 38 synthetic courses, 6 career pathways, prerequisite
   graph, outcomes, schedules (including deliberate conflicts), and 6
   sample student profiles (`data/*.csv`).
10. **Admin/data maintenance** — the Admin page lets placement-cell staff
    add courses, prerequisite links, schedules, and career-relevance
    mappings, writing straight back to the CSV files.
11. **Risks & Limitations** — a dedicated page covering technology and
    operational benefits, social risks, privacy concerns, stale-data risk,
    over-trust risk, maintenance burden, and the need for a human advisor.

---

## 5. Sample output — test cases

Run with `python3 -m tests.test_cases`:

```
[PASS] Test 1: Missing prerequisite (Spring Boot needs OOP)
   Expected: Ineligible; OOP missing
   Actual:   Ineligible; missing=['Object Oriented Programming']

[PASS] Test 2: Schedule conflict (Java vs Computer Networks, both Mon 9-11)
   Expected: 1 conflict detected between Java Programming and Computer Networks
   Actual:   1 conflict(s): ['Schedule Conflict Detected: Java Programming (09:00-11:00)
             and Computer Networks (09:00-11:00) both fall on Monday.']

[PASS] Test 3: Course with low career relevance (UI/UX for Cybersecurity Analyst)
   Expected: Relevance score below 45 (marginally/not relevant)
   Actual:   Relevance score = 0; explanation: UI/UX Design Principles is not directly
             relevant to the Cybersecurity Analyst pathway (relevance score: 0/100)...

[PASS] Test 4a: Multiple missing prerequisites (Deep Learning chain)
   Expected: Ineligible; C014 (Machine Learning) missing
   Actual:   Ineligible; missing=['Machine Learning']

[PASS] Test 4b: Chained prerequisite path suggestion
   Expected: Suggested path includes Python, Statistics, Linear Algebra and Machine Learning
   Actual:   Suggested path: ['Python Programming', 'Statistics and Probability',
             'Linear Algebra', 'Machine Learning']

[PASS] Test 5: Student with no completed courses (cold start)
   Expected: Runs without error; prerequisite_readiness = 0.0 (0 of 2 satisfied)
   Actual:   overall=73.0, prerequisite_readiness=0.0

TEST SUMMARY: 5/5 test cases passed
```

## 6. Sample output — baseline vs. proposed evaluation

Run with `python3 -m evaluation.evaluate`:

```
=== Baseline vs Proposed System Summary ===
                                 Metric  Baseline  Proposed System
          Average Course Choice Quality      83.9             86.2
           Total Prerequisite Conflicts       8.0              0.0
               Total Schedule Conflicts       1.0              0.0
             Total Career Misalignments       0.0              7.0
Average Recommendation Success Rate (%)      66.7             70.0
```

**Reading these numbers honestly:** the proposed system drives prerequisite
and schedule conflicts among its actual recommendations to zero, because it
explicitly filters out courses a student isn't eligible for rather than
blindly ranking by relevance. Career misalignment can still occur when a
student's completed-course history leaves few *eligible* high-relevance
options — in that case the engine surfaces the best available choices
(clearly labelled) rather than silently recommending something the student
can't actually take. This is a genuine trade-off worth showing, not hidden
in the demo.

---

## 7. Sample student profiles (data/students.csv)

| Student | Career Goal | Completed Courses | Notes |
|---|---|---|---|
| Aditi Sharma | Backend Developer | Java, OOP, DBMS | Typical progressing student |
| Rohan Verma | Data Scientist | Python, Statistics | Missing Linear Algebra for ML track |
| Priya Nair | Cloud Engineer | Networks, OS, Cloud Fundamentals | Ready for AWS/DevOps/K8s |
| Karan Mehta | Cybersecurity Analyst | Networks, OS | Missing Network Security prerequisite |
| Sneha Iyer | Full Stack Developer | Web Dev, DBMS, OOP | Ready for Full Stack / React |
| Arjun Rao | Software Developer | *(none)* | Cold-start / edge case |

---

## 8. Notes & assumptions

- This is a **rule-based, explainable** system by design (per the
  requirements) — no ML model drives the recommendation. All scoring
  weights live in `src/scoring.py` and can be re-tuned.
- Relevance scores and schedules are **synthetic** for demonstration —
  see the Risks & Limitations page for why this matters in a real
  deployment.
- Data persistence uses plain CSV files (as permitted by the brief) rather
  than SQLite, to keep the Admin page's read/write path simple and
  transparent; swapping in SQLite would only require changing
  `src/data_loader.py`.
