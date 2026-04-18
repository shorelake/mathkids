"""课程 04：除法启蒙

课时设计（共 4 课）：
    31. 认识除法（平均分）
    32. 除法与乘法的关系
    33. 常用除法口诀
    34. 除法综合

教学方法：
    - 平均分 (share_equally) - 把 N 个东西分给 M 个人
    - 连减法 (repeated_sub)

运行:
    python -m tools.seeders.course_04_division
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise,
    make_ex_div,
    anim_share_equally,
)

CID = "course-division"


async def seed(db):
    await upsert_course(db, CID, "除法启蒙",
                        "把饼干平均分给小伙伴，学会除法！",
                        grade="7-10", order=4)

    # Lesson 31: 认识除法
    L31_pairs = [(6,2),(8,2),(6,3),(9,3),(10,2),(12,3),(15,3)]
    await upsert_lesson(db, "lesson-31", CID, "认识除法",
                        "6 个苹果分给 2 个人，每人几个？这就是除法！", order=1,
                        methods=["share_equally", "repeated_sub"],
                        default_anim=anim_share_equally(6, 2),
                        variants=[anim_share_equally(a,b) for a,b in L31_pairs[1:]])

    # Lesson 32: 除法与乘法的关系
    L32_pairs = [(8,4),(12,4),(16,4),(20,4),(15,5),(20,5),(25,5),(30,5)]
    await upsert_lesson(db, "lesson-32", CID, "除法与乘法是好朋友",
                        "知道 4×3=12，就知道 12÷3=4！", order=2,
                        methods=["share_equally"],
                        default_anim=anim_share_equally(8, 4),
                        variants=[anim_share_equally(a,b) for a,b in L32_pairs[1:]])

    # Lesson 33: 常用除法口诀
    L33_pairs = [(12,3),(18,3),(24,3),(14,7),(21,7),(24,8),(27,9),(36,9)]
    await upsert_lesson(db, "lesson-33", CID, "常用除法口诀",
                        "用乘法口诀反过来想！", order=3,
                        methods=["share_equally"],
                        default_anim=anim_share_equally(12, 3),
                        variants=[anim_share_equally(a,b) for a,b in L33_pairs[1:]])

    # Lesson 34: 综合
    L34_pairs = [(18,6),(28,4),(35,7),(45,9),(42,6),(56,8)]
    await upsert_lesson(db, "lesson-34", CID, "除法综合练习",
                        "分苹果，分糖果，分什么都不怕！", order=4,
                        methods=["share_equally"],
                        default_anim=anim_share_equally(18, 6),
                        variants=[anim_share_equally(a,b) for a,b in L34_pairs[1:]])

    # ========== EXERCISES ==========

    # Lesson 31: 用 2、3 除
    ex31 = [(a,b) for a in range(4,21) for b in (2,3) if a % b == 0][:20]
    for i, (a, b) in enumerate(ex31):
        t = "choice" if i % 4 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_div(f"ex-31-{i+1:02d}", "lesson-31", a, b, 1, t))

    # Lesson 32: 4、5 的除法
    ex32 = [(a,b) for a in range(8,41) for b in (4,5) if a % b == 0][:20]
    for i, (a, b) in enumerate(ex32):
        t = "choice" if i % 4 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_div(f"ex-32-{i+1:02d}", "lesson-32", a, b, 2, t))

    # Lesson 33: 6、7、8、9 的除法
    ex33 = [(a,b) for a in range(12,73) for b in (6,7,8,9) if a % b == 0][:30]
    for i, (a, b) in enumerate(ex33):
        t = "choice" if i % 4 == 0 else "fill_blank"
        diff = 2 if b <= 7 else 3
        await insert_exercise(db, *make_ex_div(f"ex-33-{i+1:02d}", "lesson-33", a, b, diff, t))

    # Lesson 34: 综合
    ex34 = [(a,b) for a in range(6,81) for b in range(2,10) if a % b == 0][::4][:25]
    for i, (a, b) in enumerate(ex34):
        t = "choice" if i % 5 == 0 else "fill_blank"
        diff = 1 if b <= 3 else 2 if b <= 6 else 3
        await insert_exercise(db, *make_ex_div(f"ex-34-{i+1:02d}", "lesson-34", a, b, diff, t))


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-04 (除法启蒙) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
