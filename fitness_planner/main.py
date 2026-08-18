from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models import UserProfile
from app.plan_generator import build_weekly_plan, build_warmup, build_cooldown, build_stretching, build_notes

app = FastAPI(
    title="AI Fitness Workout Planner",
    description="Generates a personalized, evidence-based weekly workout plan from a user profile.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Fitness Workout Planner API is running"}


@app.post("/generate-workout-plan")
def generate_workout_plan(profile: UserProfile):
    conditions = [c.value for c in profile.medical_conditions if c.value != "None"]

    weekly_plan, total_calories = build_weekly_plan(profile)

    return {
        "goal": profile.goal.value,
        "weekly_plan": weekly_plan,
        "warmup": build_warmup(conditions),
        "cooldown": build_cooldown(),
        "stretching": build_stretching(conditions),
        "notes": build_notes(profile),
        "estimated_weekly_calories": f"{total_calories} kcal",
    }
