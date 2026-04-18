"""课程 06：分数启蒙

课时设计（共 3 课）：
    51. 认识一半 (1/2)
    52. 认识 1/3、1/4、1/5
    53. 简单分数比较

运行:
    python -m tools.seeders.course_06_fractions
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise, JD,
    anim_fraction,
)

CID = "course-fractions"


async def seed(db):
    await upsert_course(db, CID, "分数启蒙",
                        "半块饼、三分之一蛋糕——分数其实很好懂",
                        grade="8-10", order=6)

    # Lesson 51: 一半
    await upsert_lesson(db, "lesson-51", CID, "认识一半（1/2）",
                        "一个苹果对半分，每份就是 1/2！", order=1,
                        methods=["fraction_pie"],
                        default_anim=anim_fraction(1, 2, "pie"),
                        variants=[anim_fraction(1, 2, "bar"),
                                  anim_fraction(1, 2, "pizza")])

    # Lesson 52: 1/3, 1/4, 1/5
    L52_variants = [anim_fraction(1, 3), anim_fraction(1, 4), anim_fraction(1, 5),
                    anim_fraction(2, 3), anim_fraction(3, 4), anim_fraction(2, 5)]
    await upsert_lesson(db, "lesson-52", CID, "1/3、1/4、1/5",
                        "分的份数变多，每份就变小", order=2,
                        methods=["fraction_pie"],
                        default_anim=anim_fraction(1, 3),
                        variants=L52_variants[1:])

    # Lesson 53: 比较
    await upsert_lesson(db, "lesson-53", CID, "分数比较",
                        "1/2 和 1/3 哪个大？分得少的反而大哦！", order=3,
                        methods=["fraction_pie"],
                        default_anim=anim_fraction(1, 2, "pie"),
                        variants=[anim_fraction(1, 3), anim_fraction(1, 4)])

    # ========== EXERCISES ==========
    def _frac_ex(eid, lid, q, correct, options, diff, hints):
        return (eid, lid, "choice", q, "", str(correct), 0,
                [], hints, options, diff)

    ex_51 = [
        ("一块饼干对半分，每份是多少？", "1/2", ["1/2", "1/3", "1/4", "2/2"], 1, ["平均分 2 份"]),
        ("把西瓜切成 2 份，吃了其中 1 份，吃了几分之几？", "1/2", ["1/4", "1/3", "1/2", "2/2"], 1, ["2份里的1份"]),
        ("1/2 表示平均分成几份？", "2", ["1", "2", "3", "4"], 1, ["分母=份数"]),
        ("下面哪个等于一半？", "1/2", ["1/3", "1/2", "2/3", "3/4"], 1, ["对半分"]),
        ("2 个 1/2 合起来是？", "1", ["1/2", "1", "2", "1/4"], 2, ["2份合起来=整体"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_51):
        await insert_exercise(db, *_frac_ex(f"ex-51-{i+1:02d}", "lesson-51",
                                             q, ans, opts, diff, hints))

    ex_52 = [
        ("把蛋糕平均分成 3 份，每份是？", "1/3", ["1/2", "1/3", "1/4", "3/3"], 1, ["分3份"]),
        ("1/4 表示几份里的 1 份？", "4", ["2", "3", "4", "5"], 1, ["分母"]),
        ("2/3 表示 3 份里的几份？", "2", ["1", "2", "3", "4"], 2, ["分子"]),
        ("把披萨切 5 份，吃了 2 份，吃了多少？", "2/5", ["1/5", "2/5", "3/5", "2/3"], 2, ["5份中吃2份"]),
        ("3 个 1/4 合起来是？", "3/4", ["1/4", "1/2", "3/4", "4/4"], 2, ["3份=3/4"]),
        ("4 个 1/4 合起来是？", "1", ["1/4", "3/4", "1", "4"], 2, ["=整体"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_52):
        await insert_exercise(db, *_frac_ex(f"ex-52-{i+1:02d}", "lesson-52",
                                             q, ans, opts, diff, hints))

    ex_53 = [
        ("1/2 和 1/4 哪个大？", "1/2", ["1/2", "1/4", "一样大", "不确定"], 2, ["分得越少每份越大"]),
        ("1/3 和 1/5 哪个大？", "1/3", ["1/3", "1/5", "一样大", "不确定"], 2, ["3<5所以1/3大"]),
        ("2/4 和 1/4 哪个大？", "2/4", ["1/4", "2/4", "一样大", "不确定"], 2, ["2份多"]),
        ("两个人分一个西瓜，一人一半；3 人分一个呢？谁分到的多？", "两个人",
         ["两个人", "三个人", "一样多", "看西瓜大小"], 3, ["人少每份大"]),
        ("1/2 = ？", "2/4", ["1/3", "2/4", "3/4", "2/6"], 3, ["对半分"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_53):
        await insert_exercise(db, *_frac_ex(f"ex-53-{i+1:02d}", "lesson-53",
                                             q, ans, opts, diff, hints))


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-06 (分数启蒙) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
