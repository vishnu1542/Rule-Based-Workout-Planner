from .exercise_database import EXERCISES, WARMUP, WARMUP_LOW_IMPACT, COOLDOWN, STRETCHES

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

GOAL_PARAMS = {
    "Weight Loss": {"sets": 3, "reps": "12-15", "rest": "30 sec"},
    "Fat Loss": {"sets": 3, "reps": "12-15", "rest": "30 sec"},
    "Muscle Gain": {"sets": 4, "reps": "8-12", "rest": "60 sec"},
    "Strength": {"sets": 5, "reps": "3-6", "rest": "150 sec"},
    "Endurance": {"sets": 3, "reps": "15-20", "rest": "30 sec"},
    "General Fitness": {"sets": 3, "reps": "10-12", "rest": "60 sec"},
}

DIFFICULTY_RANK = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}

SPLIT_TEMPLATES = {
    1: [("Full Body", ["Full Body", "Legs", "Chest", "Back"])],
    2: [("Upper Body", ["Chest", "Back", "Shoulders", "Arms"]),
        ("Lower Body + Core", ["Legs", "Core"])],
    3: [("Push (Chest, Shoulders, Triceps)", ["Chest", "Shoulders", "Arms"]),
        ("Pull (Back, Biceps)", ["Back", "Arms"]),
        ("Legs + Core", ["Legs", "Core"])],
    4: [("Chest + Triceps", ["Chest", "Arms"]),
        ("Back + Biceps", ["Back", "Arms"]),
        ("Legs", ["Legs"]),
        ("Shoulders + Core", ["Shoulders", "Core"])],
    5: [("Chest + Triceps", ["Chest", "Arms"]),
        ("Back + Biceps", ["Back", "Arms"]),
        ("Legs", ["Legs"]),
        ("Shoulders + Core", ["Shoulders", "Core"]),
        ("Cardio + Full Body", ["Cardio", "Full Body"])],
    6: [("Chest + Triceps", ["Chest", "Arms"]),
        ("Back + Biceps", ["Back", "Arms"]),
        ("Legs", ["Legs"]),
        ("Shoulders", ["Shoulders"]),
        ("Cardio + Core", ["Cardio", "Core"]),
        ("Full Body", ["Full Body"])],
    7: [("Chest + Triceps", ["Chest", "Arms"]),
        ("Back + Biceps", ["Back", "Arms"]),
        ("Legs", ["Legs"]),
        ("Shoulders", ["Shoulders"]),
        ("Cardio + Core", ["Cardio", "Core"]),
        ("Full Body", ["Full Body"]),
        ("Active Recovery + Mobility", ["Yoga", "Core"])],
}


def _max_difficulty(fitness_level: str) -> int:
    return {"Beginner": 2, "Intermediate": 3, "Advanced": 3}[fitness_level]


def _available_equipment_set(equipment_list):
    names = {e.value if hasattr(e, "value") else e for e in equipment_list}
    names.add("None")
    return names


def _filter_pool(category, equipment_set, location, max_difficulty, conditions, style):
    pool = EXERCISES.get(category, [])
    result = []
    for ex in pool:
        if not any(eq in equipment_set for eq in ex["equipment"]):
            continue
        if location not in ex["location"]:
            continue
        if DIFFICULTY_RANK[ex["difficulty"]] > max_difficulty:
            continue
        if any(cond in ex["contraindications"] for cond in conditions):
            continue
        result.append(ex)
    return result


def _calorie_scale(weight_kg: float) -> float:
    return max(0.7, min(1.6, weight_kg / 70))


def _build_exercise_entry(ex, goal, weight_kg, override_reps=None, override_sets=None, override_rest=None):
    params = GOAL_PARAMS[goal]
    sets = override_sets or params["sets"]
    reps = override_reps or params["reps"]
    rest = override_rest or params["rest"]
    scale = _calorie_scale(weight_kg)
    calories = round(ex["base_cal"] * sets * scale)
    return {
        "name": ex["name"],
        "sets": str(sets),
        "reps": reps,
        "rest": rest,
        "difficulty": ex["difficulty"],
        "target_muscle": ex.get("muscle", ""),
        "estimated_calories": f"{calories} kcal",
        "description": ex["description"],
    }


def _exercises_per_day(duration_minutes, warmup_cooldown_minutes=15):
    training_minutes = max(duration_minutes - warmup_cooldown_minutes, 15)
    return max(3, min(8, round(training_minutes / 7)))


def _select_day_style_params(goal, style, day_categories, conditions, fitness_level, is_beginner_diabetic):
    if "Cardio" in day_categories and (goal in ("Weight Loss", "Fat Loss") or style in ("HIIT", "Cardio")):
        if style == "HIIT" and not is_beginner_diabetic:
            return {"sets": 4, "reps": "40 sec work / 20 sec rest", "rest": "20 sec"}
        return {"sets": 3, "reps": "15-20 min steady pace", "rest": "60 sec"}
    return None


def build_weekly_plan(profile):
    goal = profile.goal.value
    style = profile.preferred_style.value
    fitness_level = profile.fitness_level.value
    conditions = [c.value for c in profile.medical_conditions if c.value != "None"]
    is_beginner_diabetic = "Diabetes" in conditions and fitness_level == "Beginner"
    equipment_set = _available_equipment_set(profile.available_equipment)
    location = profile.workout_location.value
    max_difficulty = _max_difficulty(fitness_level)
    days = profile.workout_days_per_week
    exercises_target = _exercises_per_day(profile.workout_duration_minutes)

    template = SPLIT_TEMPLATES[days]
    weekly_plan = []
    total_calories = 0

    for i, day_name in enumerate(DAY_NAMES):
        if i >= len(template):
            weekly_plan.append({"day": day_name, "focus": "Rest", "exercises": []})
            continue

        focus_label, categories = template[i]
        day_style_override = _select_day_style_params(goal, style, categories, conditions, fitness_level, is_beginner_diabetic)

        pools = []
        for cat in categories:
            pools.extend(_filter_pool(cat, equipment_set, location, max_difficulty, conditions, style))

        seen = set()
        unique_pool = []
        for ex in pools:
            if ex["name"] not in seen:
                seen.add(ex["name"])
                unique_pool.append(ex)

        chosen = unique_pool[:exercises_target] if unique_pool else []

        day_exercises = []
        for ex in chosen:
            if day_style_override:
                entry = _build_exercise_entry(ex, goal, profile.weight_kg,
                                               override_sets=day_style_override["sets"],
                                               override_reps=day_style_override["reps"],
                                               override_rest=day_style_override["rest"])
            else:
                entry = _build_exercise_entry(ex, goal, profile.weight_kg)
            entry["target_muscle"] = _infer_muscle_label(ex, categories)
            day_exercises.append(entry)
            total_calories += int(entry["estimated_calories"].split()[0])

        weekly_plan.append({"day": day_name, "focus": focus_label, "exercises": day_exercises})

    return weekly_plan, total_calories


def _infer_muscle_label(ex, categories):
    for cat, group in EXERCISES.items():
        if ex in group:
            return cat
    return categories[0] if categories else ""


def build_warmup(conditions):
    if "Knee Pain" in conditions or "Back Pain" in conditions or "High Blood Pressure" in conditions:
        return WARMUP_LOW_IMPACT
    return WARMUP


def build_cooldown():
    return COOLDOWN


def build_stretching(conditions):
    stretches = list(STRETCHES)
    if "Back Pain" in conditions:
        stretches = [s for s in stretches if s["name"] != "Seated Forward Bend"]
    return stretches


def build_notes(profile):
    notes = []
    goal = profile.goal.value
    conditions = [c.value for c in profile.medical_conditions if c.value != "None"]
    fitness_level = profile.fitness_level.value

    if goal in ("Weight Loss", "Fat Loss"):
        notes.append("Prioritize a calorie deficit through diet alongside this plan; training alone rarely drives fat loss.")
        notes.append("Compound movements and cardio/HIIT are emphasized to maximize calorie burn.")
    if goal == "Muscle Gain":
        notes.append("Apply progressive overload by gradually increasing weight or reps each week.")
        notes.append("Eat in a slight calorie surplus with adequate protein (~1.6-2.2 g/kg bodyweight) to support growth.")
    if goal == "Strength":
        notes.append("Use heavier loads with longer rest periods; prioritize form and progressive overload over volume.")
    if goal == "Endurance":
        notes.append("Focus on higher reps and shorter rest to build muscular and cardiovascular endurance.")

    if "Diabetes" in conditions:
        if fitness_level == "Beginner":
            notes.append("Diabetes: excessive HIIT is avoided for beginners; moderate steady-state cardio is prioritized instead.")
        notes.append("Monitor blood glucose before and after workouts, and keep a fast-acting carb source on hand.")
    if "High Blood Pressure" in conditions:
        notes.append("Avoid heavy straining/breath-holding lifts; favor moderate intensity and controlled breathing.")
    if "Knee Pain" in conditions:
        notes.append("Knee Pain: jumping and heavy squat movements are excluded; cycling and leg extensions are prioritized instead.")
    if "Back Pain" in conditions:
        notes.append("Back Pain: heavy deadlifts and bent-over rows are excluded; machine-supported exercises are prioritized instead.")

    if profile.sleep_hours is not None and profile.sleep_hours < 7:
        notes.append("Aim for 7-9 hours of sleep per night to support recovery and results.")

    notes.append("Always warm up before and cool down after every session, and stay hydrated throughout.")
    notes.append("This plan is a general recommendation; consult a physician before starting if you have any medical concerns.")
    return notes
