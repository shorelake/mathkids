import json
from uuid import uuid4
from models import get_db
from validators import validate_exercise


async def get_exercises(lesson_id: str):
    db = await get_db()
    rows = await db.execute('SELECT * FROM exercises WHERE lesson_id=? ORDER BY "order"', (lesson_id,))
    exercises = []
    for r in await rows.fetchall():
        d = dict(r)
        d["options"] = json.loads(d["options"])
        d["solutions"] = json.loads(d["solutions"])
        d["hints"] = json.loads(d["hints"])
        exercises.append(d)
    await db.close()
    return exercises


async def create_exercise(data: dict):
    # Validate math correctness
    validation = validate_exercise(data["expression"], str(data["correct_answer"]))
    if not validation["valid"]:
        return {"error": validation["errors"]}

    db = await get_db()
    eid = f"ex-{uuid4().hex[:8]}"
    await db.execute(
        'INSERT INTO exercises (id, lesson_id, type, question, expression, correct_answer, "order", solutions, hints, options, difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (eid, data["lesson_id"], data.get("type", "fill_blank"),
         data["question"], data["expression"], str(data["correct_answer"]),
         data.get("order", 0),
         json.dumps(data.get("solutions", []), ensure_ascii=False),
         json.dumps(data.get("hints", []), ensure_ascii=False),
         json.dumps(data.get("options", []), ensure_ascii=False),
         data.get("difficulty", 1))
    )
    await db.commit()
    await db.close()
    return {"id": eid}


async def update_exercise(exercise_id: str, data: dict):
    db = await get_db()
    fields, values = [], []
    for k in ("type", "question", "expression", "correct_answer", "order", "difficulty"):
        if k in data:
            col = f'"{k}"' if k == "order" else k
            fields.append(f"{col}=?")
            values.append(str(data[k]) if k == "correct_answer" else data[k])
    for k in ("solutions", "hints", "options"):
        if k in data:
            fields.append(f"{k}=?")
            values.append(json.dumps(data[k], ensure_ascii=False))
    values.append(exercise_id)
    if fields:
        await db.execute(f"UPDATE exercises SET {','.join(fields)} WHERE id=?", values)
        await db.commit()
    await db.close()
    return {"id": exercise_id}


async def delete_exercise(exercise_id: str):
    db = await get_db()
    await db.execute("DELETE FROM exercises WHERE id=?", (exercise_id,))
    await db.commit()
    await db.close()


async def check_answer(exercise_id: str, user_answer: str):
    db = await get_db()
    row = await db.execute("SELECT * FROM exercises WHERE id=?", (exercise_id,))
    ex = await row.fetchone()
    await db.close()
    if not ex:
        return {"error": "Exercise not found"}

    ex_dict = dict(ex)
    correct = str(ex_dict["correct_answer"]).strip()
    answer = str(user_answer).strip()
    is_correct = correct == answer

    result = {
        "correct": is_correct,
        "correct_answer": correct,
        "hints": json.loads(ex_dict["hints"]) if not is_correct else [],
        "solutions": json.loads(ex_dict["solutions"]) if not is_correct else [],
    }
    return result


async def get_random_exercises(lesson_id: str, count: int = 10):
    """Get random subset of exercises for a lesson."""
    db = await get_db()
    rows = await db.execute(
        f'SELECT * FROM exercises WHERE lesson_id=? ORDER BY RANDOM() LIMIT ?',
        (lesson_id, count))
    exercises = []
    for r in await rows.fetchall():
        d = dict(r)
        d["options"] = json.loads(d["options"])
        d["solutions"] = json.loads(d["solutions"])
        d["hints"] = json.loads(d["hints"])
        exercises.append(d)
    await db.close()
    return exercises


async def batch_create_exercises(exercises: list):
    results = []
    for ex_data in exercises:
        r = await create_exercise(ex_data)
        results.append(r)
    return results
