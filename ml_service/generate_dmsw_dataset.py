"""
generate_dmsw_dataset.py — Enhanced Synthetic Dataset Generator
===============================================================
Generates a richer synthetic dataset (5000 students × 20 weeks) with:
  - Realistic dropout triggers (attendance cliff, grade spiral, financial crisis)
  - 6 student archetypes: Dropout, Non-Dropout, Late Bloomer,
    Burned Out, Recovering, Edge Case
  - Diverse behavioral comment vocabulary for richer text embeddings
"""

import pandas as pd
import numpy as np
import random

# Constants
NUM_STUDENTS = 5000
WEEKS = 20
OUTPUT_FILE = "dmsw_student_data.csv"
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Behavioral comment vocabularies (expanded)
# ---------------------------------------------------------------------------
POSITIVE_COMMENTS = [
    "Active participation in class",
    "Submitted assignment on time",
    "Showed great improvement this week",
    "Helped peers with coursework",
    "Asked insightful questions during lecture",
    "Perfect attendance this week",
    "Demonstrated strong leadership in group project",
    "Consistent high performance maintained",
    "Enthusiastic about the topic discussed",
    "Completed extra credit work voluntarily",
    "Excellent presentation skills displayed",
    "Strong problem-solving ability shown",
    "Engaged actively in group discussions",
    "Outstanding project submission received",
    "Showed initiative in independent learning",
    "Top scorer in mid-semester assessment",
    "Proactively sought feedback from professor",
    "Mentored struggling classmates effectively",
    "Submitted assignment ahead of deadline",
    "Demonstrated mastery of course concepts",
]

NEUTRAL_COMMENTS = [
    "Regular attendance maintained",
    "Submitted assignment as required",
    "Quiet in class but attentive",
    "Average performance observed this week",
    "Met the basic course requirements",
    "Present but participation was passive",
    "No significant behavioural changes noted",
    "Followed all instructions appropriately",
    "Standard participation level maintained",
    "Completed the quiz with average score",
    "Attended class but appeared disengaged",
    "Moderate effort observed this week",
    "On-time submission with minor errors",
    "Adequate performance noted overall",
    "Satisfactory attendance record maintained",
    "Completed coursework without distinction",
    "Unremarkable but consistent attendance",
    "Mid-range scores on recent assessments",
    "Participating minimally in discussions",
    "Following syllabus at expected pace",
]

NEGATIVE_COMMENTS = [
    "Absent without notifying the instructor",
    "Late submission of assignment",
    "Disruptive behavior noted during class",
    "Failed the weekly quiz",
    "Did not pay attention during lecture",
    "Sleeping during class session",
    "Rude to classmates during group work",
    "Incomplete homework submitted",
    "Struggling with core course concepts",
    "Needs improvement in academic discipline",
    "Missed multiple assignment deadlines",
    "Frequently arriving late to class",
    "No homework submitted this week",
    "Declined to participate in activities",
    "Showing clear signs of academic distress",
    "Stopped attending lab sessions",
    "Grade dropped sharply this week",
    "Unresponsive to instructor communication",
    "Warning issued for attendance violation",
    "Failed to schedule required advising meeting",
]

# ---------------------------------------------------------------------------
# Student arche-types
# ---------------------------------------------------------------------------
ARCHETYPES = {
    "dropout":      0.25,  # Clearly at-risk students
    "non_dropout":  0.45,  # Clearly succeeding students
    "late_bloomer": 0.08,  # Start poorly, improve significantly
    "burned_out":   0.08,  # Start great, deteriorate rapidly
    "recovering":   0.07,  # Brief dip mid-semester, recover
    "edge_case":    0.07,  # Contradictory signals (hard to classify)
}


def pick_archetype():
    choices = list(ARCHETYPES.keys())
    weights = list(ARCHETYPES.values())
    return random.choices(choices, weights=weights, k=1)[0]


def generate_static_features(archetype: str) -> dict:
    """Generate static (time-invariant) student features based on archetype."""
    if archetype == "dropout":
        return {
            "age": random.randint(18, 30),
            "gender": random.choice([0, 1]),
            "scholarship": 0 if random.random() < 0.75 else 1,
            "debt": 1 if random.random() < 0.65 else 0,
            "tuition_up_to_date": 0 if random.random() < 0.55 else 1,
            "courses_enrolled": random.randint(3, 6),
            "courses_passed": random.randint(0, 2),
        }
    elif archetype == "non_dropout":
        return {
            "age": random.randint(18, 25),
            "gender": random.choice([0, 1]),
            "scholarship": 1 if random.random() < 0.45 else 0,
            "debt": 0 if random.random() < 0.85 else 1,
            "tuition_up_to_date": 1 if random.random() < 0.92 else 0,
            "courses_enrolled": random.randint(4, 7),
            "courses_passed": random.randint(4, 7),
        }
    elif archetype == "late_bloomer":
        return {
            "age": random.randint(18, 22),
            "gender": random.choice([0, 1]),
            "scholarship": 0 if random.random() < 0.5 else 1,
            "debt": 1 if random.random() < 0.4 else 0,
            "tuition_up_to_date": 1 if random.random() < 0.7 else 0,
            "courses_enrolled": random.randint(4, 6),
            "courses_passed": random.randint(2, 5),
        }
    elif archetype == "burned_out":
        return {
            "age": random.randint(19, 26),
            "gender": random.choice([0, 1]),
            "scholarship": 1 if random.random() < 0.6 else 0,
            "debt": 0 if random.random() < 0.6 else 1,
            "tuition_up_to_date": 1 if random.random() < 0.75 else 0,
            "courses_enrolled": random.randint(5, 7),
            "courses_passed": random.randint(2, 5),
        }
    elif archetype == "recovering":
        return {
            "age": random.randint(19, 24),
            "gender": random.choice([0, 1]),
            "scholarship": 0 if random.random() < 0.45 else 1,
            "debt": 1 if random.random() < 0.35 else 0,
            "tuition_up_to_date": 1 if random.random() < 0.8 else 0,
            "courses_enrolled": random.randint(4, 6),
            "courses_passed": random.randint(3, 6),
        }
    else:  # edge_case
        return {
            "age": random.randint(20, 35),
            "gender": random.choice([0, 1]),
            "scholarship": random.choice([0, 1]),
            "debt": random.choice([0, 1]),
            "tuition_up_to_date": random.choice([0, 1]),
            "courses_enrolled": random.randint(3, 7),
            "courses_passed": random.randint(0, 7),
        }


def simulate_timeseries(archetype: str, static: dict):
    """Simulate attendance and grade across WEEKS with archetype-specific dynamics."""
    if archetype == "dropout":
        att_base   = random.uniform(35, 70)
        grade_base = random.uniform(30, 65)
        crisis_week = random.randint(5, 12)  # when financial/personal crisis hits

        def step(week, att, grade):
            att   -= random.uniform(1, 4)   # steady decline
            grade -= random.uniform(0.5, 3)
            if week == crisis_week:          # sudden attendance cliff
                att -= random.uniform(10, 20)
                grade -= random.uniform(5, 12)
            return att, grade

    elif archetype == "non_dropout":
        att_base   = random.uniform(72, 100)
        grade_base = random.uniform(65, 95)

        def step(week, att, grade):
            att   += random.uniform(-2, 2)
            grade += random.uniform(-1.5, 2)
            return att, grade

    elif archetype == "late_bloomer":
        att_base   = random.uniform(40, 65)    # starts poorly
        grade_base = random.uniform(30, 55)
        turnaround = random.randint(8, 13)      # week improvement starts

        def step(week, att, grade):
            if week < turnaround:
                att   -= random.uniform(0, 2)
                grade -= random.uniform(0, 2)
            else:
                att   += random.uniform(2, 5)   # marked improvement
                grade += random.uniform(2, 6)
            return att, grade

    elif archetype == "burned_out":
        att_base   = random.uniform(80, 98)    # starts excellently
        grade_base = random.uniform(75, 95)
        burnout_week = random.randint(7, 12)   # burnout hits

        def step(week, att, grade):
            if week <= burnout_week:
                att   += random.uniform(-1, 1)
                grade += random.uniform(-1, 1)
            else:
                att   -= random.uniform(3, 7)   # rapid drop
                grade -= random.uniform(4, 9)
            return att, grade

    elif archetype == "recovering":
        att_base   = random.uniform(65, 85)
        grade_base = random.uniform(55, 75)
        dip_start  = random.randint(6, 9)
        dip_end    = dip_start + random.randint(2, 4)

        def step(week, att, grade):
            if dip_start <= week <= dip_end:
                att   -= random.uniform(4, 9)    # temporary dip
                grade -= random.uniform(3, 7)
            elif week > dip_end:
                att   += random.uniform(1, 4)    # recovery
                grade += random.uniform(1, 5)
            else:
                att   += random.uniform(-1, 1.5)
                grade += random.uniform(-1, 1.5)
            return att, grade

    else:  # edge_case: contradictory signals
        # High attendance, terrible grades OR poor attendance, great grades
        if random.random() < 0.5:
            att_base   = random.uniform(80, 98)
            grade_base = random.uniform(20, 45)
        else:
            att_base   = random.uniform(25, 50)
            grade_base = random.uniform(70, 92)

        def step(week, att, grade):
            att   += random.uniform(-1.5, 1.5)
            grade += random.uniform(-2, 2)
            return att, grade

    return att_base, grade_base, step


# ---------------------------------------------------------------------------
# Dropout label assignment per archetype
# ---------------------------------------------------------------------------
DROPOUT_PROB = {
    "dropout":      0.90,
    "non_dropout":  0.05,
    "late_bloomer": 0.20,
    "burned_out":   0.55,
    "recovering":   0.15,
    "edge_case":    0.45,
}


def generate_student_data(student_id: str) -> list:
    archetype = pick_archetype()
    static    = generate_static_features(archetype)
    is_dropout = random.random() < DROPOUT_PROB[archetype]

    att_base, grade_base, step_fn = simulate_timeseries(archetype, static)

    current_att   = att_base
    current_grade = grade_base
    rows = []

    for week in range(1, WEEKS + 1):
        current_att, current_grade = step_fn(week, current_att, current_grade)
        current_att   = float(np.clip(current_att, 0, 100))
        current_grade = float(np.clip(current_grade, 0, 100))

        # Behavioral comment selection
        if current_grade < 40 or current_att < 40:
            comment = random.choice(NEGATIVE_COMMENTS)
        elif current_grade >= 80 and current_att >= 80:
            comment = random.choice(POSITIVE_COMMENTS)
        else:
            comment = random.choice(NEUTRAL_COMMENTS)

        rows.append({
            "student_id":         student_id,
            "archetype":          archetype,
            "week":               week,
            "attendance":         round(current_att, 1),
            "grade":              round(current_grade, 1),
            "behavior_text":      comment,
            "age":                static["age"],
            "gender":             static["gender"],
            "scholarship":        static["scholarship"],
            "debt":               static["debt"],
            "tuition_up_to_date": static["tuition_up_to_date"],
            "courses_enrolled":   static["courses_enrolled"],
            "courses_passed":     static["courses_passed"],
            "dropout_label":      int(is_dropout),
        })

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    print(f"Generating dataset: {NUM_STUDENTS} students × {WEEKS} weeks ...")
    all_data = []
    for i in range(NUM_STUDENTS):
        sid = f"STU{i+1:05d}"
        all_data.extend(generate_student_data(sid))

    df = pd.DataFrame(all_data)
    df.to_csv(OUTPUT_FILE, index=False)

    # --- Summary ---
    stu_df = df.groupby("student_id").first()
    total   = len(stu_df)
    dropout = int(stu_df["dropout_label"].sum())

    print(f"\nDataset generated: {len(df):,} rows ({total} students × {WEEKS} weeks)")
    print(f"  Dropout     : {dropout:,} ({dropout/total*100:.1f}%)")
    print(f"  Non-dropout : {total-dropout:,} ({(total-dropout)/total*100:.1f}%)")
    print(f"\nArchetype breakdown:")
    for arch in ARCHETYPES:
        n_arch = int((stu_df["archetype"] == arch).sum())
        d_arch = int(stu_df[stu_df["archetype"] == arch]["dropout_label"].sum())
        print(f"  {arch:<15}: {n_arch:>5} students | {d_arch:>4} dropout")

    print(f"\nSaved to {OUTPUT_FILE}")
