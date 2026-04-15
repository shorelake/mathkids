from datetime import datetime
from models import get_db


async def get_progress(user_id: str):
    db = await get_db()
    rows = await db.execute(
        "SELECT up.*, l.title as lesson_title, l.course_id FROM user_progress up JOIN lessons l ON up.lesson_id = l.id WHERE up.user_id=?",
        (user_id,)
    )
    progress = [dict(r) for r in await rows.fetchall()]
    await db.close()
    return progress


async def update_progress(user_id: str, lesson_id: str, data: dict):
    db = await get_db()
    now = datetime.now().isoformat()

    existing = await db.execute(
        "SELECT * FROM user_progress WHERE user_id=? AND lesson_id=?",
        (user_id, lesson_id)
    )
    row = await existing.fetchone()

    stars = data.get("stars", 0)
    correct = data.get("correct_count", 0)
    total = data.get("total_count", 0)
    time_spent = data.get("time_spent", 0)

    if row:
        old = dict(row)
        stars = max(old["stars"], stars)
        await db.execute(
            "UPDATE user_progress SET stars=?, correct_count=?, total_count=?, time_spent=?, completed_at=? WHERE user_id=? AND lesson_id=?",
            (stars, correct, total, time_spent, now, user_id, lesson_id)
        )
    else:
        await db.execute(
            "INSERT INTO user_progress (user_id, lesson_id, stars, correct_count, total_count, time_spent, completed_at) VALUES (?,?,?,?,?,?,?)",
            (user_id, lesson_id, stars, correct, total, time_spent, now)
        )

    await db.commit()
    await db.close()
    return {"user_id": user_id, "lesson_id": lesson_id, "stars": stars}


async def unlock_lessons(user_id: str, course_id: str, unlock_to_lesson_id: str = None):
    """解锁到指定课时（含），并将之后的课时进度重置为0星（加锁）。
    unlock_to_lesson_id=None 时解锁全部已发布课时（不做加锁）。
    已有更高星级的解锁范围内的课时不会被降级。
    """
    db = await get_db()
    rows = await db.execute(
        'SELECT id FROM lessons WHERE course_id=? AND status="published" ORDER BY "order"',
        (course_id,)
    )
    all_ids = [r["id"] for r in await rows.fetchall()]

    if unlock_to_lesson_id and unlock_to_lesson_id in all_ids:
        idx = all_ids.index(unlock_to_lesson_id)
        unlock_ids = all_ids[: idx + 1]
        lock_ids   = all_ids[idx + 1 :]
    else:
        unlock_ids = all_ids
        lock_ids   = []

    now = datetime.now().isoformat()

    # 解锁：星级不足1的设为1，已有更高星级的保持不变
    for lid in unlock_ids:
        existing = await db.execute(
            "SELECT stars FROM user_progress WHERE user_id=? AND lesson_id=?",
            (user_id, lid)
        )
        row = await existing.fetchone()
        if row:
            if row["stars"] == 0:
                await db.execute(
                    "UPDATE user_progress SET stars=1, completed_at=? WHERE user_id=? AND lesson_id=?",
                    (now, user_id, lid)
                )
        else:
            await db.execute(
                "INSERT INTO user_progress (user_id, lesson_id, stars, correct_count, total_count, time_spent, completed_at) VALUES (?,?,1,0,0,0,?)",
                (user_id, lid, now)
            )

    # 加锁：将解锁范围之后的课时进度重置为0星
    for lid in lock_ids:
        await db.execute(
            "UPDATE user_progress SET stars=0 WHERE user_id=? AND lesson_id=?",
            (user_id, lid)
        )

    await db.commit()
    await db.close()
    return {"unlocked": len(unlock_ids), "locked": len(lock_ids), "lesson_ids": unlock_ids}


async def get_analytics():
    """Get aggregate analytics for admin dashboard."""
    db = await get_db()

    total_users = await db.execute("SELECT COUNT(DISTINCT user_id) as c FROM user_progress")
    total_users_row = await total_users.fetchone()

    lesson_stats = await db.execute("""
        SELECT l.id, l.title, l."order",
            COUNT(up.user_id) as attempts,
            AVG(up.stars) as avg_stars,
            AVG(CASE WHEN up.total_count > 0 THEN up.correct_count * 100.0 / up.total_count ELSE 0 END) as avg_accuracy,
            AVG(up.time_spent) as avg_time
        FROM lessons l
        LEFT JOIN user_progress up ON l.id = up.lesson_id
        GROUP BY l.id
        ORDER BY l."order"
    """)
    stats = [dict(r) for r in await lesson_stats.fetchall()]

    await db.close()
    return {
        "total_users": total_users_row["c"],
        "lesson_stats": stats,
    }
