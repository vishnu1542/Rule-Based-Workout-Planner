# AI Fitness Workout Planner API

A FastAPI service that generates a personalized, evidence-based weekly workout plan
from a user profile (age, goal, fitness level, equipment, medical conditions, etc.).

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger UI): http://127.0.0.1:8000/docs

## Endpoint

`POST /generate-workout-plan`

Send a JSON body matching the `UserProfile` schema (see `/docs` for the full field list
and enum values). Example:

```json
{
  "age": 24,
  "gender": "Male",
  "height_cm": 175,
  "weight_kg": 78,
  "bmi": 25.5,
  "body_fat_pct": 22,
  "fitness_level": "Beginner",
  "goal": "Weight Loss",
  "medical_conditions": ["Knee Pain"],
  "workout_location": "Home",
  "available_equipment": ["Dumbbells"],
  "workout_days_per_week": 4,
  "workout_duration_minutes": 45,
  "preferred_style": "Mixed",
  "target_muscle_groups": ["Legs", "Core"],
  "sleep_hours": 6,
  "daily_activity_level": "Light",
  "experience": "Beginner",
  "previous_injuries": "Minor knee strain 2023"
}
```

Response: JSON object with `weekly_plan`, `warmup`, `cooldown`, `stretching`,
`notes`, and `estimated_weekly_calories`, matching the format specified in the spec.

## Project structure

```
fitness_planner/
├── main.py                    # FastAPI app + route
├── app/
│   ├── models.py               # Pydantic request schema (UserProfile) + enums
│   ├── exercise_database.py    # Exercise library tagged by muscle, equipment, difficulty, contraindications
│   └── plan_generator.py       # Split templates, filtering, goal-based sets/reps/rest, notes
├── requirements.txt
└── README.md
```

## Rule logic implemented

- **Weekly split**: chosen from `SPLIT_TEMPLATES` based on `workout_days_per_week` (1-7),
  following the standard bro-split pattern (Chest+Tri / Back+Bi / Legs / Shoulders+Core / Cardio+Full Body / ...),
  with remaining days marked `Rest`.
- **Exercise filtering**: each exercise is tagged with required equipment, valid location
  (Gym/Home), difficulty, and medical contraindications. Only exercises matching the user's
  equipment, location, fitness level, and health profile are selected.
- **Goal-based sets/reps/rest**:
  - Weight Loss / Fat Loss → 3 sets, 12-15 reps, 30s rest, cardio/HIIT days emphasized
  - Muscle Gain → 4 sets, 8-12 reps, 60s rest (progressive overload)
  - Strength → 5 sets, 3-6 reps, 150s rest
  - Endurance → 3 sets, 15-20 reps, 30s rest
  - General Fitness → 3 sets, 10-12 reps, 60s rest
- **Medical condition rules**:
  - Diabetes + Beginner → HIIT avoided, moderate steady-state cardio used instead
  - Knee Pain → jumping/heavy-squat exercises excluded; cycling & leg extensions favored
  - Back Pain → heavy deadlifts/bent-over rows excluded; machine-supported exercises favored
  - High Blood Pressure → low-impact warmup, heavy-strain notes
- **Calorie estimate**: per-exercise calories scaled by the user's bodyweight, summed into
  `estimated_weekly_calories`.
