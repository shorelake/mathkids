import json
from datetime import datetime
from uuid import uuid4
from models import get_db


async def list_courses(status: str = None):
    db = await get_db()
    if status:
        rows = await db.execute('SELECT * FROM courses WHERE status=? ORDER BY "order"', (status,))
    else:
        rows = await db.execute('SELECT * FROM courses ORDER BY "order"')
    courses = [dict(r) for r in await rows.fetchall()]
    await db.close()
    return courses


async def get_course(course_id: str):
    db = await get_db()
    row = await db.execute("SELECT * FROM courses WHERE id=?", (course_id,))
    course = await row.fetchone()
    await db.close()
    return dict(course) if course else None


async def create_course(data: dict):
    db = await get_db()
    cid = f"course-{uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    await db.execute(
        'INSERT INTO courses (id, title, description, grade_range, "order", status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)',
        (cid, data["title"], data.get("description", ""), data.get("grade_range", "6-10"),
         data.get("order", 0), data.get("status", "draft"), now, now)
    )
    await db.commit()
    await db.close()
    return await get_course(cid)


async def update_course(course_id: str, data: dict):
    db = await get_db()
    fields = []
    values = []
    for k in ("title", "description", "grade_range", "order", "status"):
        if k in data:
            fields.append(f'"{k}"=?' if k == "order" else f"{k}=?")
            values.append(data[k])
    fields.append("updated_at=?")
    values.append(datetime.now().isoformat())
    values.append(course_id)
    await db.execute(f"UPDATE courses SET {','.join(fields)} WHERE id=?", values)
    await db.commit()
    await db.close()
    return await get_course(course_id)


async def delete_course(course_id: str):
    db = await get_db()
    await db.execute("DELETE FROM courses WHERE id=?", (course_id,))
    await db.commit()
    await db.close()


async def list_lessons(course_id: str):
    db = await get_db()
    rows = await db.execute('SELECT * FROM lessons WHERE course_id=? ORDER BY "order"', (course_id,))
    lessons = []
    for r in await rows.fetchall():
        d = dict(r)
        d["teaching_methods"] = json.loads(d["teaching_methods"])
        d["animation_data"] = json.loads(d["animation_data"])
        lessons.append(d)
    await db.close()
    return lessons


async def get_lesson(lesson_id: str):
    db = await get_db()
    row = await db.execute("SELECT * FROM lessons WHERE id=?", (lesson_id,))
    lesson = await row.fetchone()
    if not lesson:
        await db.close()
        return None
    d = dict(lesson)
    d["teaching_methods"] = json.loads(d["teaching_methods"])
    d["animation_data"] = json.loads(d["animation_data"])

    # Also fetch exercises
    ex_rows = await db.execute('SELECT * FROM exercises WHERE lesson_id=? ORDER BY "order"', (lesson_id,))
    exercises = []
    for e in await ex_rows.fetchall():
        ed = dict(e)
        ed["options"] = json.loads(ed["options"])
        ed["solutions"] = json.loads(ed["solutions"])
        ed["hints"] = json.loads(ed["hints"])
        exercises.append(ed)
    d["exercises"] = exercises
    await db.close()
    return d


async def create_lesson(data: dict):
    db = await get_db()
    lid = f"lesson-{uuid4().hex[:8]}"
    now = datetime.now().isoformat()
    await db.execute(
        'INSERT INTO lessons (id, course_id, title, description, "order", status, teaching_methods, animation_data, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
        (lid, data["course_id"], data["title"], data.get("description", ""),
         data.get("order", 0), data.get("status", "draft"),
         json.dumps(data.get("teaching_methods", []), ensure_ascii=False),
         json.dumps(data.get("animation_data", {}), ensure_ascii=False),
         now, now)
    )
    await db.commit()
    await db.close()
    return await get_lesson(lid)


async def update_lesson(lesson_id: str, data: dict):
    db = await get_db()
    fields = []
    values = []
    for k in ("title", "description", "order", "status"):
        if k in data:
            fields.append(f'"{k}"=?' if k == "order" else f"{k}=?")
            values.append(data[k])
    if "teaching_methods" in data:
        fields.append("teaching_methods=?")
        values.append(json.dumps(data["teaching_methods"], ensure_ascii=False))
    if "animation_data" in data:
        fields.append("animation_data=?")
        values.append(json.dumps(data["animation_data"], ensure_ascii=False))
    fields.append("updated_at=?")
    values.append(datetime.now().isoformat())
    values.append(lesson_id)
    await db.execute(f"UPDATE lessons SET {','.join(fields)} WHERE id=?", values)
    await db.commit()
    await db.close()
    return await get_lesson(lesson_id)


async def delete_lesson(lesson_id: str):
    db = await get_db()
    await db.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
    await db.commit()
    await db.close()
