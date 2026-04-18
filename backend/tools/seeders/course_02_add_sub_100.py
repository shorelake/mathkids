"""课程 02：100 以内加减法 【短期重点课程】

这门课是闺女 20 以内学完后的直接延续，设计最精细。

课时设计（共 8 课）：
    11. 整十数加减                10+20, 50-30
    12. 整十数 + 一位数            20+3, 40+7
    13. 两位数 + 一位数 (不进位)   24+5, 31+6
    14. 两位数 + 一位数 (进位)     27+8, 35+9
    15. 两位数 - 一位数 (不退位)   28-6, 35-3
    16. 两位数 - 一位数 (退位)     32-7, 51-8
    17. 两位数 + 两位数            24+35, 26+37
    18. 两位数 - 两位数            46-23, 52-38

教学方法：
    - 数位盒（place_value） - 用"十根小棒 + 一颗珠子"直观展示
    - 竖式（column_add/sub） - 开始接触正式竖式
    - 大数轴（number_line） - 可视化整十跳跃

运行:
    python -m tools.seeders.course_02_add_sub_100
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise,
    make_ex_100,
    anim_tens_addsub, anim_col_add_noc, anim_col_add_carry,
    anim_col_sub_noc, anim_col_sub_borrow,
)

CID = "course-add-sub-100"


async def seed(db):
    await upsert_course(db, CID, "100 以内加减法",
                        "从 20 以内升级到 100 以内，学会竖式和数位",
                        grade="7-9", order=2)

    # ========== Lesson 11: 整十数加减 ==========
    L11_pairs = [(10,20,"+"),(30,10,"+"),(20,40,"+"),(50,30,"-"),
                 (40,20,"-"),(60,10,"+"),(80,30,"-")]
    await upsert_lesson(db, "lesson-11", CID, "整十数加减",
                        "10+20 怎么算？用十棒看一看！", order=1,
                        methods=["place_value", "number_line"],
                        default_anim=anim_tens_addsub(10, 20, "+"),
                        variants=[anim_tens_addsub(a,b,op) for a,b,op in L11_pairs[1:]])

    # ========== Lesson 12: 整十数 + 一位数 ==========
    L12_pairs = [(20,3),(30,5),(40,7),(50,2),(60,4),(70,6),(10,8),(80,3)]
    await upsert_lesson(db, "lesson-12", CID, "整十加一位",
                        "20+3 = 23，懂了吗？就是十位写 2，个位写 3！", order=2,
                        methods=["place_value"],
                        default_anim=anim_col_add_noc(20, 3),
                        variants=[anim_col_add_noc(a,b) for a,b in L12_pairs[1:]])

    # ========== Lesson 13: 两位数 + 一位数（不进位）==========
    L13_pairs = [(24,5),(31,6),(42,3),(53,4),(25,4),(34,5),(62,7),(73,6)]
    await upsert_lesson(db, "lesson-13", CID, "两位数 + 一位数（不进位）",
                        "个位加个位，十位不变！", order=3,
                        methods=["column_add", "place_value"],
                        default_anim=anim_col_add_noc(24, 5),
                        variants=[anim_col_add_noc(a,b) for a,b in L13_pairs[1:]])

    # ========== Lesson 14: 两位数 + 一位数（进位）【重点】==========
    L14_pairs = [(27,8),(35,9),(48,6),(56,7),(29,5),(38,9),(67,8),(74,9),(46,8)]
    await upsert_lesson(db, "lesson-14", CID, "两位数 + 一位数（进位）",
                        "⭐ 重点：个位满 10，向十位进 1！", order=4,
                        methods=["column_add", "place_value"],
                        default_anim=anim_col_add_carry(27, 8),
                        variants=[anim_col_add_carry(a,b) for a,b in L14_pairs[1:]])

    # ========== Lesson 15: 两位数 - 一位数（不退位）==========
    L15_pairs = [(28,6),(35,3),(47,5),(56,4),(39,7),(48,6),(27,5),(85,3)]
    await upsert_lesson(db, "lesson-15", CID, "两位数 - 一位数（不退位）",
                        "个位减个位，十位不变！", order=5,
                        methods=["column_sub"],
                        default_anim=anim_col_sub_noc(28, 6),
                        variants=[anim_col_sub_noc(a,b) for a,b in L15_pairs[1:]])

    # ========== Lesson 16: 两位数 - 一位数（退位）【重点】==========
    L16_pairs = [(32,7),(51,8),(43,9),(62,5),(71,4),(83,7),(94,8),(35,9),(54,6)]
    await upsert_lesson(db, "lesson-16", CID, "两位数 - 一位数（退位）",
                        "⭐ 重点：个位不够减，向十位借 1 当 10！", order=6,
                        methods=["column_sub"],
                        default_anim=anim_col_sub_borrow(32, 7),
                        variants=[anim_col_sub_borrow(a,b) for a,b in L16_pairs[1:]])

    # ========== Lesson 17: 两位数 + 两位数 ==========
    # Mix of carry and no-carry
    L17_pairs = [(24,35,False),(26,37,True),(31,42,False),(35,46,True),
                 (23,14,False),(48,37,True),(17,52,False),(29,58,True)]
    def _add2d(a, b, carry):
        return anim_col_add_carry(a, b) if carry else anim_col_add_noc(a, b)
    await upsert_lesson(db, "lesson-17", CID, "两位数 + 两位数",
                        "两个两位数相加，竖式派上大用场！", order=7,
                        methods=["column_add"],
                        default_anim=_add2d(24, 35, False),
                        variants=[_add2d(a,b,c) for a,b,c in L17_pairs[1:]])

    # ========== Lesson 18: 两位数 - 两位数 ==========
    L18_pairs = [(46,23,False),(52,38,True),(67,34,False),(71,29,True),
                 (85,43,False),(62,47,True),(94,51,False),(83,57,True)]
    def _sub2d(a, b, borrow):
        return anim_col_sub_borrow(a, b) if borrow else anim_col_sub_noc(a, b)
    await upsert_lesson(db, "lesson-18", CID, "两位数 - 两位数",
                        "两个两位数相减，竖式真厉害！", order=8,
                        methods=["column_sub"],
                        default_anim=_sub2d(46, 23, False),
                        variants=[_sub2d(a,b,c) for a,b,c in L18_pairs[1:]])

    # ==========  EXERCISES  ==========
    # 给每课塞一些精选的种子题，`generate_exercises.py` 会按配置再扩充大批量

    # Lesson 11: 整十加减
    ex11 = [(10,20,"+"),(30,10,"+"),(20,20,"+"),(40,30,"-"),(50,20,"-"),
            (60,40,"+"),(70,30,"-"),(80,50,"-"),(10,70,"+"),(90,60,"-"),
            (30,40,"+"),(50,50,"-"),(40,40,"+"),(60,30,"+"),(90,40,"-")]
    for i, (a, b, op) in enumerate(ex11):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-11-{i+1:02d}", "lesson-11", a, b, op, 1, t))

    # Lesson 12: 整十 + 一位
    ex12 = [(20,3),(30,5),(40,7),(50,2),(60,4),(70,6),(80,1),(90,3),(10,8),
            (20,9),(40,5),(60,3),(80,7),(30,2),(50,6)]
    for i, (a, b) in enumerate(ex12):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-12-{i+1:02d}", "lesson-12", a, b, "+", 1, t))

    # Lesson 13: 两位 + 一位不进位
    ex13 = [(24,5),(31,6),(42,3),(53,4),(25,4),(34,5),(62,7),(73,6),(14,3),
            (22,6),(45,2),(61,8),(71,4),(82,6),(35,2)]
    for i, (a, b) in enumerate(ex13):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-13-{i+1:02d}", "lesson-13", a, b, "+", (i%3)+1, t))

    # Lesson 14: 两位 + 一位进位（重点课程：30题）
    ex14 = [(27,8),(35,9),(48,6),(56,7),(29,5),(38,9),(67,8),(74,9),(46,8),
            (19,3),(25,6),(34,8),(47,7),(59,2),(63,9),(76,5),(82,9),(28,7),
            (36,6),(44,8),(55,7),(68,9),(77,4),(87,5),(89,9),(17,5),(24,9),
            (39,4),(48,9),(65,7)]
    for i, (a, b) in enumerate(ex14):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-14-{i+1:02d}", "lesson-14", a, b, "+", (i%3)+1, t))

    # Lesson 15: 两位 - 一位不退位
    ex15 = [(28,6),(35,3),(47,5),(56,4),(39,7),(48,6),(27,5),(85,3),(73,2),
            (64,1),(92,1),(45,2),(88,6),(76,4),(59,8)]
    for i, (a, b) in enumerate(ex15):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-15-{i+1:02d}", "lesson-15", a, b, "-", (i%3)+1, t))

    # Lesson 16: 两位 - 一位退位（重点：30题）
    ex16 = [(32,7),(51,8),(43,9),(62,5),(71,4),(83,7),(94,8),(35,9),(54,6),
            (22,3),(41,4),(52,6),(63,8),(74,9),(85,7),(91,2),(24,5),(33,8),
            (42,7),(55,9),(64,9),(76,8),(87,9),(93,6),(21,4),(32,9),(44,5),
            (56,8),(65,7),(82,4)]
    for i, (a, b) in enumerate(ex16):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-16-{i+1:02d}", "lesson-16", a, b, "-", (i%3)+1, t))

    # Lesson 17: 两位 + 两位
    ex17 = [(24,35),(26,37),(31,42),(35,46),(23,14),(48,37),(17,52),(29,58),
            (12,23),(34,45),(56,12),(43,28),(67,15),(18,26),(25,47),(53,38),
            (64,27),(39,24),(45,36),(28,49)]
    for i, (a, b) in enumerate(ex17):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-17-{i+1:02d}", "lesson-17", a, b, "+", (i%3)+1, t))

    # Lesson 18: 两位 - 两位
    ex18 = [(46,23),(52,38),(67,34),(71,29),(85,43),(62,47),(94,51),(83,57),
            (75,28),(63,41),(88,39),(92,56),(54,27),(76,48),(81,35),(57,24),
            (96,47),(68,52),(73,46),(84,29)]
    for i, (a, b) in enumerate(ex18):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await insert_exercise(db, *make_ex_100(f"ex-18-{i+1:02d}", "lesson-18", a, b, "-", (i%3)+1, t))


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-02 (100以内加减法) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
