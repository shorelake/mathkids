"""课程 07：认识时间

课时设计（共 3 课）：
    61. 认识时钟和整点   （3:00 / 6:00 / 9:00）
    62. 半点和几点几分   （3:30 / 7:15 / 8:45）
    63. 时间计算         (再过 1 小时几点？)

运行:
    python -m tools.seeders.course_07_time
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise, JD,
    anim_clock,
)

CID = "course-time"


async def seed(db):
    await upsert_course(db, CID, "认识时间",
                        "看得懂时钟，管得好时间",
                        grade="7-9", order=7)

    # Lesson 61: 整点
    hours = [(3, 0), (6, 0), (9, 0), (12, 0), (1, 0), (4, 0), (8, 0)]
    await upsert_lesson(db, "lesson-61", CID, "认识时钟和整点",
                        "短针=时针，长针=分针；分针指 12 就是整点！", order=1,
                        methods=["clock"],
                        default_anim=anim_clock(3, 0, "整点"),
                        variants=[anim_clock(h, m, "整点") for h, m in hours[1:]])

    # Lesson 62: 半点与几分
    times = [(3, 30), (7, 30), (8, 15), (2, 45), (10, 20), (5, 40), (11, 50)]
    await upsert_lesson(db, "lesson-62", CID, "半点和几点几分",
                        "分针指 6 = 半点；指 3 = 15 分；指 9 = 45 分", order=2,
                        methods=["clock"],
                        default_anim=anim_clock(3, 30, "半点"),
                        variants=[anim_clock(h, m) for h, m in times[1:]])

    # Lesson 63: 时间计算（动画数据简化，重点题目说明）
    await upsert_lesson(db, "lesson-63", CID, "时间计算",
                        "现在 3 点，再过 1 小时几点？", order=3,
                        methods=["clock"],
                        default_anim=anim_clock(3, 0, "起点"),
                        variants=[anim_clock(4, 0, "过 1 小时"),
                                  anim_clock(4, 30, "过 1.5 小时")])

    # ========== EXERCISES ==========
    def _time_ex(eid, lid, q, correct, options, diff, hints):
        return (eid, lid, "choice", q, "", str(correct), 0,
                [], hints, options, diff)

    ex_61 = [
        ("钟面上数字一共有几个？", "12", ["10", "11", "12", "24"], 1, ["1到12"]),
        ("时钟的短针叫什么？", "时针", ["时针", "分针", "秒针", "指针"], 1, ["短=时"]),
        ("时钟的长针叫什么？", "分针", ["时针", "分针", "秒针", "指针"], 1, ["长=分"]),
        ("分针指向 12，时针指向 3，现在几点？", "3:00", ["3:00", "12:00", "3:30", "12:03"], 1, ["整点"]),
        ("分针指 12，时针指 6，几点？", "6:00", ["12:06", "6:00", "6:12", "12:00"], 1, ["整点"]),
        ("12 点整，时针指向？", "12", ["1", "12", "6", "3"], 1, ["正上方"]),
        ("9 点整，时针指向？", "9", ["9", "12", "3", "6"], 1, ["左边"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_61):
        await insert_exercise(db, *_time_ex(f"ex-61-{i+1:02d}", "lesson-61",
                                             q, ans, opts, diff, hints))

    ex_62 = [
        ("分针指向 6，代表多少分？", "30", ["15", "30", "45", "60"], 1, ["半圈=30分"]),
        ("分针指 3，代表多少分？", "15", ["10", "15", "20", "30"], 1, ["1/4圈"]),
        ("分针指 9，代表多少分？", "45", ["30", "40", "45", "50"], 1, ["3/4圈"]),
        ("1 小时 = 多少分？", "60", ["30", "50", "60", "100"], 1, ["整圈"]),
        ("3:30 读作几点几分？", "3 点 30 分", ["3 点 3 分", "3 点 30 分", "30 点 3 分", "半 3 点"], 2,
         ["先时后分"]),
        ("时针指着 7 和 8 中间，分针指 6，几点？", "7:30", ["7:30", "8:30", "7:06", "8:06"], 2,
         ["时针还没到8"]),
        ("分针从 12 转到 6 用多久？", "30 分", ["15 分", "30 分", "45 分", "60 分"], 2, ["半圈"]),
        ("1 天有几小时？", "24", ["12", "24", "60", "100"], 2, ["白天12+晚上12"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_62):
        await insert_exercise(db, *_time_ex(f"ex-62-{i+1:02d}", "lesson-62",
                                             q, ans, opts, diff, hints))

    ex_63 = [
        ("现在 3 点，1 小时后几点？", "4:00", ["3:30", "4:00", "4:30", "2:00"], 2, ["+1小时"]),
        ("现在 7 点，2 小时后几点？", "9:00", ["8:00", "9:00", "10:00", "5:00"], 2, ["+2"]),
        ("现在 5:30，过 30 分几点？", "6:00", ["5:30", "6:00", "6:30", "5:00"], 2, ["+30分"]),
        ("现在 8:00，前 1 小时是几点？", "7:00", ["7:00", "9:00", "8:30", "7:30"], 2, ["-1"]),
        ("现在 10:15，30 分钟后几点？", "10:45", ["10:30", "10:45", "11:15", "10:15"], 2, ["+30"]),
        ("上午 10 点到中午 12 点，经过多久？", "2 小时", ["1 小时", "2 小时", "3 小时", "4 小时"], 3,
         ["12-10=2"]),
        ("1 小时 30 分 = 多少分？", "90", ["60", "70", "90", "120"], 3, ["60+30"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_63):
        await insert_exercise(db, *_time_ex(f"ex-63-{i+1:02d}", "lesson-63",
                                             q, ans, opts, diff, hints))


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-07 (认识时间) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
