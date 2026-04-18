"""课程 01：20 以内加减法 (原始课程, 从 models.py 迁移过来)

运行:
    python -m tools.seeders.course_01_add_sub_20
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise, JD,
    make_ex_addsub,
    anim_counting_add, anim_counting_sub, anim_nl_add,
    anim_make_ten, anim_break_ten, anim_step_20_noc,
)

CID = "course-add-sub-20"


async def seed(db):
    await upsert_course(db, CID, "20 以内加减法",
                        "适合 6-8 岁儿童的 20 以内加减法启蒙课程",
                        grade="6-8", order=1)

    # ----- Lesson 01: 认识加法 -----
    L01_pairs = [(2,3),(1,2),(3,1),(1,4),(4,1),(2,2),(3,2)]
    await upsert_lesson(db, "lesson-01", CID, "认识加法",
                        "通过可爱小动物学习加法概念", order=1,
                        methods=["counting"],
                        default_anim=anim_counting_add(2, 3),
                        variants=[anim_counting_add(a,b) for a,b in L01_pairs[1:]])

    # ----- Lesson 02: 10以内加法 -----
    L02_pairs = [(4,3),(3,5),(6,2),(5,4),(2,7),(3,6),(8,1)]
    def _add10(a, b):
        base = anim_counting_add(a, b)
        nl = anim_nl_add(a, b, 10)
        base["methods"].append(nl["methods"][0])
        return base
    await upsert_lesson(db, "lesson-02", CID, "10 以内加法",
                        "数数法和数轴法双管齐下", order=2,
                        methods=["counting", "number_line"],
                        default_anim=_add10(4, 3),
                        variants=[_add10(a,b) for a,b in L02_pairs[1:]])

    # ----- Lesson 03: 10以内减法 -----
    L03_pairs = [(7,3),(5,2),(8,3),(9,4),(6,2),(10,5),(8,5)]
    await upsert_lesson(db, "lesson-03", CID, "10 以内减法",
                        "拿走法和数轴回跳学减法", order=3,
                        methods=["subtraction", "number_line"],
                        default_anim=anim_counting_sub(7, 3),
                        variants=[anim_counting_sub(a,b) for a,b in L03_pairs[1:]])

    # ----- Lesson 04: 20以内不进位加法 -----
    L04_pairs = [(12,3),(11,5),(14,2),(13,4),(15,3),(10,6)]
    await upsert_lesson(db, "lesson-04", CID, "20 以内不进位加法",
                        "个位直接加", order=4,
                        methods=["step_by_step", "number_line"],
                        default_anim=anim_step_20_noc(12, 3),
                        variants=[anim_step_20_noc(a,b) for a,b in L04_pairs[1:]])

    # ----- Lesson 05: 20以内进位加法 (重点) -----
    L05_pairs = [(8,5),(7,6),(9,4),(8,6),(7,5),(9,3),(6,7),(8,4),(5,8),(9,5),
                 (6,8),(7,9),(8,7),(9,6),(6,9),(8,9),(9,7),(5,9),(6,6)]
    await upsert_lesson(db, "lesson-05", CID, "20 以内进位加法（凑十法）",
                        "重点凑十法，一题三解", order=5,
                        methods=["make_ten", "number_line", "counting"],
                        default_anim=anim_make_ten(8, 5),
                        variants=[anim_make_ten(a,b) for a,b in L05_pairs[1:]])

    # ----- Lesson 06: 20以内退位减法 -----
    L06_pairs = [(13,8),(15,7),(12,9),(14,6),(11,8),(16,9),(13,5),(15,8),
                 (12,7),(14,9),(17,8),(11,5),(13,6),(16,7),(12,8),(18,9),
                 (15,6),(14,8),(13,9)]
    await upsert_lesson(db, "lesson-06", CID, "20 以内退位减法（破十法）",
                        "破十法处理退位减法", order=6,
                        methods=["break_ten", "number_line"],
                        default_anim=anim_break_ten(13, 8),
                        variants=[anim_break_ten(t,b) for t,b in L06_pairs[1:]])

    # ----- Lesson 07: 混合 -----
    await upsert_lesson(db, "lesson-07", CID, "加减混合练习",
                        "综合运用多种方法", order=7,
                        methods=["make_ten", "break_ten"],
                        default_anim=anim_make_ten(9, 6),
                        variants=[anim_make_ten(8,7), anim_break_ten(14,8),
                                  anim_make_ten(6,9), anim_break_ten(16,7),
                                  anim_break_ten(15,6)])

    # ----- Lesson 08: 三个数连算 -----
    L08_default = {"expression": "3 + 5 + 2 = 10", "methods": [
        {"type": "step_by_step", "title": "分步法", "steps": [
            {"action": "highlight_first_pair", "values": [3,5], "narration": "先算 3 + 5"},
            {"action": "compute", "expression": "3 + 5", "result": 8, "narration": "3 + 5 = 8"},
            {"action": "compute", "expression": "8 + 2", "result": 10, "narration": "8 + 2 = 10！"}
        ]}
    ]}
    await upsert_lesson(db, "lesson-08", CID, "三个数连算",
                        "从左到右分步算", order=8,
                        methods=["step_by_step"],
                        default_anim=L08_default)

    # ==========  EXERCISES  ==========

    # Lesson 01: 12 题 (≤ 5+5)
    for i, (a, b) in enumerate([(1,1),(2,1),(1,3),(2,2),(3,1),(2,3),(1,4),(3,2),(4,1),(3,3),(1,5),(5,1)]):
        await insert_exercise(db, *make_ex_addsub(f"ex-01-{i+1:02d}", "lesson-01", a, b, "+", 1))

    # Lesson 02: 15 题
    for i, (a, b) in enumerate([(3,4),(5,5),(6,3),(4,5),(2,7),(8,2),(1,6),(5,4),(7,3),
                                 (6,4),(3,7),(4,6),(2,8),(1,9),(9,1)]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_addsub(f"ex-02-{i+1:02d}", "lesson-02", a, b, "+", (i%3)+1, t))

    # Lesson 03: 15 题
    for i, (a, b) in enumerate([(5,2),(8,3),(10,4),(7,5),(9,3),(6,1),(8,5),(10,7),(9,6),
                                 (7,4),(6,3),(5,3),(8,2),(10,6),(9,5)]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_addsub(f"ex-03-{i+1:02d}", "lesson-03", a, b, "-", (i%3)+1, t))

    # Lesson 04: 15 题
    for i, (a, b) in enumerate([(12,3),(11,5),(14,2),(13,4),(10,6),(15,3),(11,7),(12,5),
                                 (14,5),(10,8),(16,2),(13,3),(11,4),(17,1),(12,6)]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_addsub(f"ex-04-{i+1:02d}", "lesson-04", a, b, "+", (i%3)+1, t))

    # Lesson 05: 30 题
    p05 = [(8,5),(7,6),(9,4),(8,6),(7,5),(9,3),(6,7),(8,4),(5,8),(9,5),
           (6,8),(7,9),(8,7),(9,6),(6,9),(8,9),(7,8),(9,7),(5,9),(6,6),
           (8,8),(9,9),(7,7),(5,7),(4,9),(3,8),(4,8),(5,6),(3,9),(6,5)]
    for i, (a, b) in enumerate(p05):
        t = "choice" if i % 4 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_addsub(f"ex-05-{i+1:02d}", "lesson-05", a, b, "+", (i%3)+1, t))

    # Lesson 06: 25 题
    p06 = [(13,8),(15,7),(12,9),(14,6),(11,8),(16,9),(13,5),(15,8),(12,7),(14,9),
           (17,8),(11,5),(13,6),(16,7),(12,8),(18,9),(11,3),(15,6),(14,8),(13,9),
           (11,4),(12,6),(15,9),(16,8),(17,9)]
    for i, (a, b) in enumerate(p06):
        t = "choice" if i % 4 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_addsub(f"ex-06-{i+1:02d}", "lesson-06", a, b, "-", (i%3)+1, t))

    # Lesson 07: 20 混合题
    p07 = [(9,6,"+"),(13,7,"-"),(8,5,"+"),(15,9,"-"),(7,8,"+"),(12,5,"-"),
           (6,9,"+"),(14,6,"-"),(9,4,"+"),(11,8,"-"),(8,7,"+"),(16,8,"-"),
           (7,6,"+"),(13,4,"-"),(5,9,"+"),(17,9,"-"),(6,8,"+"),(15,7,"-"),
           (9,5,"+"),(14,9,"-")]
    for i, (a, b, op) in enumerate(p07):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_addsub(f"ex-07-{i+1:02d}", "lesson-07", a, b, op, (i%3)+1, t))

    # Lesson 08: 16 三数连加
    h3 = ["先算前两个数", "把结果再加上最后一个数"]
    s3 = [{"method": "step_by_step", "steps": ["先算前两个数之和", "再加上第三个数"]}]
    p08 = [(3,5,2,1,"choice"),(4,3,2,1,"choice"),(2,6,1,1,"choice"),(5,3,4,1,"choice"),
           (1,7,3,1,"choice"),(6,2,3,1,"choice"),(3,4,5,2,"choice"),(2,5,6,2,"choice"),
           (4,4,4,1,"fill_blank"),(3,3,3,1,"fill_blank"),(5,5,5,2,"fill_blank"),
           (6,7,3,2,"fill_blank"),(7,5,2,2,"fill_blank"),(8,3,4,2,"fill_blank"),
           (6,6,5,3,"fill_blank"),(9,4,3,3,"fill_blank")]
    for i, (a, b, c, diff, typ) in enumerate(p08):
        ans = a + b + c
        opts = sorted(set([ans, max(0, ans-1), ans+1, ans+2]))[:4] if typ == "choice" else []
        await insert_exercise(db, f"ex-08-{i+1:02d}", "lesson-08", typ,
                              f"{a} + {b} + {c} = ?", f"{a}+{b}+{c}",
                              ans, i+1, s3, h3, opts, diff)


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-01 (20以内加减法) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
