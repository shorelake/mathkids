"""课程 03：乘法启蒙

课时设计（共 6 课）：
    21. 认识乘法 (3+3+3 = 3×3)
    22. 乘法口诀 1 (1 / 2 / 3 的乘法)
    23. 乘法口诀 2 (4 / 5 的乘法)
    24. 乘法口诀 3 (6 / 7 的乘法)
    25. 乘法口诀 4 (8 / 9 的乘法)
    26. 乘法综合练习

教学方法：
    - 方阵图 (multiply_array)
    - 相同加法 (repeated_add)
    - 跳数法数轴 (number_line)

运行:
    python -m tools.seeders.course_03_multiplication
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise,
    make_ex_mult,
    anim_multiply_array, anim_multiply_skip_count,
)

CID = "course-multiplication"


def _mult_both(a, b):
    """Combine array + skip-count into one lesson."""
    base = anim_multiply_array(a, b)
    skip = anim_multiply_skip_count(a, b)
    base["methods"].extend(skip["methods"])
    return base


async def seed(db):
    await upsert_course(db, CID, "乘法启蒙",
                        "从相同加法到乘法口诀，用方阵图玩转乘法",
                        grade="7-10", order=3)

    # Lesson 21: 认识乘法
    L21_pairs = [(3,3),(2,4),(3,2),(4,2),(2,5),(3,4),(5,2)]
    await upsert_lesson(db, "lesson-21", CID, "认识乘法",
                        "3 + 3 + 3 太累啦！用乘法来搞定！", order=1,
                        methods=["multiply_array", "repeated_add"],
                        default_anim=anim_multiply_array(3, 3),
                        variants=[anim_multiply_array(a,b) for a,b in L21_pairs[1:]])

    # Lesson 22: 1 / 2 / 3 的乘法
    L22_pairs = [(2,3),(2,5),(3,3),(3,5),(2,6),(3,4),(2,8)]
    await upsert_lesson(db, "lesson-22", CID, "2、3 的乘法口诀",
                        "二二得四，三三得九，念起来真顺口！", order=2,
                        methods=["multiply_array", "number_line"],
                        default_anim=_mult_both(2, 3),
                        variants=[_mult_both(a,b) for a,b in L22_pairs[1:]])

    # Lesson 23: 4 / 5 的乘法
    L23_pairs = [(4,3),(5,3),(4,5),(5,5),(4,4),(5,6),(4,7)]
    await upsert_lesson(db, "lesson-23", CID, "4、5 的乘法口诀",
                        "四五二十，五五二十五", order=3,
                        methods=["multiply_array", "number_line"],
                        default_anim=_mult_both(4, 3),
                        variants=[_mult_both(a,b) for a,b in L23_pairs[1:]])

    # Lesson 24: 6 / 7 的乘法
    L24_pairs = [(6,3),(7,3),(6,5),(7,5),(6,7),(6,6),(7,7),(7,8)]
    await upsert_lesson(db, "lesson-24", CID, "6、7 的乘法口诀",
                        "六七四十二，七七四十九", order=4,
                        methods=["multiply_array", "number_line"],
                        default_anim=_mult_both(6, 3),
                        variants=[_mult_both(a,b) for a,b in L24_pairs[1:]])

    # Lesson 25: 8 / 9 的乘法
    L25_pairs = [(8,3),(9,3),(8,5),(9,5),(8,7),(9,7),(8,8),(9,9),(9,8)]
    await upsert_lesson(db, "lesson-25", CID, "8、9 的乘法口诀",
                        "八九七十二，九九八十一", order=5,
                        methods=["multiply_array", "number_line"],
                        default_anim=_mult_both(8, 3),
                        variants=[_mult_both(a,b) for a,b in L25_pairs[1:]])

    # Lesson 26: 综合
    L26_pairs = [(3,7),(6,4),(8,2),(5,9),(7,6),(4,9)]
    await upsert_lesson(db, "lesson-26", CID, "乘法综合练习",
                        "九九乘法表大冲关！", order=6,
                        methods=["multiply_array"],
                        default_anim=anim_multiply_array(3, 7),
                        variants=[anim_multiply_array(a,b) for a,b in L26_pairs[1:]])

    # ========== EXERCISES ==========
    # Lesson 21: 认识乘法（配对选择）
    ex21 = [(2,3),(3,2),(2,4),(4,2),(3,3),(2,5),(5,2),(3,4),(4,3),(2,6),(6,2),(3,5)]
    for i, (a, b) in enumerate(ex21):
        t = "choice" if i < 4 else "fill_blank"
        await insert_exercise(db, *make_ex_mult(f"ex-21-{i+1:02d}", "lesson-21", a, b, 1, t))

    # Lesson 22-25: 按乘法口诀组
    def add_mult_ex(lesson, nums, prefix):
        """nums: list of (a,b) - will be saved as ex-{prefix}-XX"""
        for i, (a, b) in enumerate(nums):
            t = "choice" if i % 4 == 0 else "fill_blank"
            diff = 1 if max(a, b) <= 3 else 2 if max(a, b) <= 6 else 3
            yield make_ex_mult(f"ex-{prefix}-{i+1:02d}", lesson, a, b, diff, t)

    for args in add_mult_ex("lesson-22",
                            [(2,a) for a in range(2,10)] + [(3,a) for a in range(2,10)],
                            "22"):
        await insert_exercise(db, *args)

    for args in add_mult_ex("lesson-23",
                            [(4,a) for a in range(2,10)] + [(5,a) for a in range(2,10)],
                            "23"):
        await insert_exercise(db, *args)

    for args in add_mult_ex("lesson-24",
                            [(6,a) for a in range(2,10)] + [(7,a) for a in range(2,10)],
                            "24"):
        await insert_exercise(db, *args)

    for args in add_mult_ex("lesson-25",
                            [(8,a) for a in range(2,10)] + [(9,a) for a in range(2,10)],
                            "25"):
        await insert_exercise(db, *args)

    # Lesson 26: 综合大题
    ex26 = [(a, b) for a in range(2, 10) for b in range(2, 10)][::3]  # 采样一部分
    for i, (a, b) in enumerate(ex26[:16]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        diff = 1 if max(a, b) <= 3 else 2 if max(a, b) <= 6 else 3
        await insert_exercise(db, *make_ex_mult(f"ex-26-{i+1:02d}", "lesson-26", a, b, diff, t))


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-03 (乘法启蒙) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
