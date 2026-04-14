import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from contextlib import asynccontextmanager

from models import init_db, seed_data
from services import course, exercise, progress, ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await seed_data()
    yield

app = FastAPI(title="MathKids API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== Pydantic Models =====

class CourseCreate(BaseModel):
    title: str
    description: str = ""
    grade_range: str = "6-10"
    order: int = 0
    status: str = "draft"

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    grade_range: Optional[str] = None
    order: Optional[int] = None
    status: Optional[str] = None

class LessonCreate(BaseModel):
    course_id: str
    title: str
    description: str = ""
    order: int = 0
    status: str = "draft"
    teaching_methods: list = []
    animation_data: dict = {}

class LessonUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    order: Optional[int] = None
    status: Optional[str] = None
    teaching_methods: Optional[list] = None
    animation_data: Optional[dict] = None

class ExerciseCreate(BaseModel):
    lesson_id: str
    type: str = "fill_blank"
    question: str
    expression: str
    correct_answer: str
    options: list = []
    solutions: list = []
    hints: list = []
    difficulty: int = 1
    order: int = 0

class ExerciseUpdate(BaseModel):
    type: Optional[str] = None
    question: Optional[str] = None
    expression: Optional[str] = None
    correct_answer: Optional[str] = None
    options: Optional[list] = None
    solutions: Optional[list] = None
    hints: Optional[list] = None
    difficulty: Optional[int] = None
    order: Optional[int] = None

class AnswerCheck(BaseModel):
    user_answer: str

class ProgressUpdate(BaseModel):
    lesson_id: str
    stars: int = 0
    correct_count: int = 0
    total_count: int = 0
    time_spent: int = 0

class AIConfigUpdate(BaseModel):
    provider: Optional[str] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None

class AIGenerateLesson(BaseModel):
    topic: str
    expression: Optional[str] = None

class AIGenerateExercises(BaseModel):
    topic: str
    count: int = 5
    difficulty: int = 1
    max_value: int = 20


# ===== Course Routes =====

@app.get("/api/courses")
async def api_list_courses(status: Optional[str] = None):
    return await course.list_courses(status)

@app.get("/api/courses/{course_id}")
async def api_get_course(course_id: str):
    c = await course.get_course(course_id)
    if not c:
        raise HTTPException(404, "Course not found")
    return c

@app.post("/api/courses")
async def api_create_course(data: CourseCreate):
    return await course.create_course(data.model_dump())

@app.put("/api/courses/{course_id}")
async def api_update_course(course_id: str, data: CourseUpdate):
    return await course.update_course(course_id, data.model_dump(exclude_none=True))

@app.delete("/api/courses/{course_id}")
async def api_delete_course(course_id: str):
    await course.delete_course(course_id)
    return {"ok": True}


# ===== Lesson Routes =====

@app.get("/api/courses/{course_id}/lessons")
async def api_list_lessons(course_id: str):
    return await course.list_lessons(course_id)

@app.get("/api/lessons/{lesson_id}")
async def api_get_lesson(lesson_id: str):
    l = await course.get_lesson(lesson_id)
    if not l:
        raise HTTPException(404, "Lesson not found")
    return l

@app.post("/api/lessons")
async def api_create_lesson(data: LessonCreate):
    return await course.create_lesson(data.model_dump())

@app.put("/api/lessons/{lesson_id}")
async def api_update_lesson(lesson_id: str, data: LessonUpdate):
    return await course.update_lesson(lesson_id, data.model_dump(exclude_none=True))

@app.delete("/api/lessons/{lesson_id}")
async def api_delete_lesson(lesson_id: str):
    await course.delete_lesson(lesson_id)
    return {"ok": True}


# ===== Exercise Routes =====

@app.get("/api/lessons/{lesson_id}/exercises")
async def api_list_exercises(lesson_id: str):
    return await exercise.get_exercises(lesson_id)

@app.post("/api/exercises")
async def api_create_exercise(data: ExerciseCreate):
    result = await exercise.create_exercise(data.model_dump())
    if "error" in result:
        raise HTTPException(400, result["error"])
    return result

@app.put("/api/exercises/{exercise_id}")
async def api_update_exercise(exercise_id: str, data: ExerciseUpdate):
    return await exercise.update_exercise(exercise_id, data.model_dump(exclude_none=True))

@app.delete("/api/exercises/{exercise_id}")
async def api_delete_exercise(exercise_id: str):
    await exercise.delete_exercise(exercise_id)
    return {"ok": True}

@app.post("/api/exercises/{exercise_id}/check")
async def api_check_answer(exercise_id: str, data: AnswerCheck):
    return await exercise.check_answer(exercise_id, data.user_answer)


# ===== Progress Routes =====

@app.get("/api/progress/{user_id}")
async def api_get_progress(user_id: str):
    return await progress.get_progress(user_id)

@app.post("/api/progress/{user_id}")
async def api_update_progress(user_id: str, data: ProgressUpdate):
    return await progress.update_progress(user_id, data.lesson_id, data.model_dump())

@app.get("/api/analytics")
async def api_get_analytics():
    return await progress.get_analytics()


# ===== AI Config & Generation Routes =====

@app.get("/api/ai/config")
async def api_get_ai_config():
    config = await ai.get_ai_config()
    # Mask API key for security
    if config.get("api_key"):
        key = config["api_key"]
        config["api_key_masked"] = key[:8] + "****" + key[-4:] if len(key) > 12 else "****"
    return config

@app.put("/api/ai/config")
async def api_update_ai_config(data: AIConfigUpdate):
    return await ai.update_ai_config(data.model_dump(exclude_none=True))

@app.get("/api/ai/providers")
async def api_get_providers():
    return ai.PROVIDER_DEFAULTS

@app.post("/api/ai/generate-lesson")
async def api_generate_lesson(data: AIGenerateLesson):
    result = await ai.generate_lesson_content(data.topic, data.expression)
    if not result.get("success"):
        raise HTTPException(400, result)
    return result

@app.post("/api/ai/generate-exercises")
async def api_generate_exercises(data: AIGenerateExercises):
    result = await ai.generate_exercises(data.topic, data.count, data.difficulty, data.max_value)
    if not result.get("success"):
        raise HTTPException(400, result)
    return result


# ===== Health Check =====

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
