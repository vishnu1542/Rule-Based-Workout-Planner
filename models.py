from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class Gender(str, Enum):
    male = "Male"
    female = "Female"
    other = "Other"


class FitnessLevel(str, Enum):
    beginner = "Beginner"
    intermediate = "Intermediate"
    advanced = "Advanced"


class Goal(str, Enum):
    weight_loss = "Weight Loss"
    fat_loss = "Fat Loss"
    muscle_gain = "Muscle Gain"
    strength = "Strength"
    endurance = "Endurance"
    general_fitness = "General Fitness"


class MedicalCondition(str, Enum):
    diabetes = "Diabetes"
    high_bp = "High Blood Pressure"
    knee_pain = "Knee Pain"
    back_pain = "Back Pain"
    none = "None"


class WorkoutLocation(str, Enum):
    gym = "Gym"
    home = "Home"


class Equipment(str, Enum):
    none = "None"
    dumbbells = "Dumbbells"
    bands = "Resistance Bands"
    full_gym = "Full Gym"


class WorkoutStyle(str, Enum):
    cardio = "Cardio"
    strength = "Strength"
    hiit = "HIIT"
    yoga = "Yoga"
    mixed = "Mixed"


class ActivityLevel(str, Enum):
    sedentary = "Sedentary"
    light = "Light"
    moderate = "Moderate"
    active = "Active"


class UserProfile(BaseModel):
    age: int = Field(..., ge=13, le=90)
    gender: Gender
    height_cm: float
    weight_kg: float
    bmi: Optional[float] = None
    body_fat_pct: Optional[float] = None
    fitness_level: FitnessLevel
    goal: Goal
    medical_conditions: List[MedicalCondition] = [MedicalCondition.none]
    workout_location: WorkoutLocation
    available_equipment: List[Equipment] = [Equipment.none]
    workout_days_per_week: int = Field(..., ge=1, le=7)
    workout_duration_minutes: int = Field(..., ge=15, le=120)
    preferred_style: WorkoutStyle
    target_muscle_groups: List[str] = []
    sleep_hours: Optional[float] = None
    daily_activity_level: ActivityLevel
    experience: FitnessLevel
    previous_injuries: Optional[str] = None
    heart_rate: Optional[int] = None
