"""课程 05：认识图形

课时设计（共 3 课）：
    41. 认识基本图形 (圆、方、三角、长方形)
    42. 多边形家族 (五边形、六边形)
    43. 图形辨认综合

运行:
    python -m tools.seeders.course_05_geometry
"""
import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from models import get_db
from tools._common import (
    upsert_course, upsert_lesson, insert_exercise, JD,
    anim_shape_show,
)

CID = "course-geometry"


async def seed(db):
    await upsert_course(db, CID, "认识图形",
                        "圆、方、三角，我们身边的图形朋友",
                        grade="6-8", order=5)

    # Lesson 41: 基本图形
    shapes_basic = [
        ("circle", 0, 0, ["太阳", "车轮", "披萨"]),
        ("square", 4, 4, ["魔方", "QQ糖", "窗户"]),
        ("triangle", 3, 3, ["红领巾", "屋顶", "警示牌"]),
        ("rectangle", 4, 4, ["门", "书本", "手机"]),
    ]
    L41_default = anim_shape_show(*shapes_basic[0])
    L41_variants = [anim_shape_show(*s) for s in shapes_basic[1:]]
    await upsert_lesson(db, "lesson-41", CID, "认识基本图形",
                        "圆形、正方形、三角形、长方形", order=1,
                        methods=["shape_show"],
                        default_anim=L41_default, variants=L41_variants)

    # Lesson 42: 多边形家族
    shapes_poly = [
        ("pentagon", 5, 5, ["五角星中间", "房子外形"]),
        ("hexagon", 6, 6, ["蜜蜂巢", "足球黑块"]),
    ]
    await upsert_lesson(db, "lesson-42", CID, "多边形家族",
                        "五边形、六边形也来了！", order=2,
                        methods=["shape_show"],
                        default_anim=anim_shape_show(*shapes_poly[0]),
                        variants=[anim_shape_show(*s) for s in shapes_poly[1:]])

    # Lesson 43: 综合
    await upsert_lesson(db, "lesson-43", CID, "图形辨认综合",
                        "眼睛亮一亮，认出是什么形状！", order=3,
                        methods=["shape_show"],
                        default_anim=anim_shape_show("circle", 0, 0, ["月饼", "硬币", "饼干"]),
                        variants=[anim_shape_show(*s) for s in (shapes_basic + shapes_poly)])

    # ========== EXERCISES ==========
    # 这里的题目用 choice 类型，问"哪个是XXX形"或"XXX有几条边"

    def _shape_ex(eid, lid, question, correct, options, diff, hints):
        """Build a shape choice question."""
        # NOTE: insert_exercise already calls JD() internally, so pass raw Python objects here
        return (eid, lid, "choice", question, "", str(correct), 0,
                [], hints, options, diff)

    # Lesson 41 题目：基础识别
    ex_41 = [
        ("圆形有几条边？", "0", ["0", "1", "3", "4"], 1, ["圆形是弯弯的"]),
        ("正方形有几条边？", "4", ["2", "3", "4", "5"], 1, ["数一数"]),
        ("三角形有几个角？", "3", ["2", "3", "4", "6"], 1, ["三角形=3角"]),
        ("长方形有几条边？", "4", ["3", "4", "5", "6"], 1, ["和正方形一样！"]),
        ("下面哪个图形没有角？", "圆形", ["圆形", "三角形", "正方形", "长方形"], 1, ["弯弯的那个"]),
        ("下面哪个图形有 3 条边？", "三角形", ["圆形", "三角形", "正方形", "长方形"], 1, ["三=3"]),
        ("太阳像什么形状？", "圆形", ["圆形", "三角形", "正方形", "长方形"], 1, ["圆圆的"]),
        ("红领巾是什么形状？", "三角形", ["圆形", "三角形", "正方形", "长方形"], 1, ["三个角"]),
        ("书本封面是什么形状？", "长方形", ["圆形", "三角形", "正方形", "长方形"], 1, ["长长的"]),
        ("正方形的四条边怎么样？", "一样长", ["一样长", "都不同", "两长两短", "只有两条"], 2, ["正方形=正的"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_41):
        await insert_exercise(db, *_shape_ex(f"ex-41-{i+1:02d}", "lesson-41",
                                              q, ans, opts, diff, hints))

    # Lesson 42 题目
    ex_42 = [
        ("五边形有几条边？", "5", ["3", "4", "5", "6"], 2, ["五=5"]),
        ("六边形有几个角？", "6", ["4", "5", "6", "7"], 2, ["六=6"]),
        ("蜂巢是什么形状？", "六边形", ["圆形", "正方形", "五边形", "六边形"], 2, ["小蜜蜂造的"]),
        ("下面哪个图形有 5 条边？", "五边形", ["三角形", "长方形", "五边形", "六边形"], 2, ["五=5"]),
        ("五边形和六边形谁的边更多？", "六边形", ["五边形", "六边形", "一样多", "不确定"], 2, ["6 > 5"]),
        ("下面哪个不是多边形？", "圆形", ["三角形", "五边形", "六边形", "圆形"], 2, ["圆形没有直边"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_42):
        await insert_exercise(db, *_shape_ex(f"ex-42-{i+1:02d}", "lesson-42",
                                              q, ans, opts, diff, hints))

    # Lesson 43 综合
    ex_43 = [
        ("什么图形有 4 条一样长的边？", "正方形", ["圆形", "三角形", "正方形", "长方形"], 2, ["正=整齐的"]),
        ("什么图形有 4 条边但两长两短？", "长方形", ["正方形", "三角形", "长方形", "五边形"], 2, ["长长的"]),
        ("披萨切一半看起来像什么？", "半圆", ["圆形", "半圆", "三角形", "长方形"], 3, ["圆的一半"]),
        ("三角尺 +三角尺 = ？", "长方形", ["圆形", "正方形", "长方形", "五边形"], 3, ["拼一拼"]),
        ("3 个 正方形 拼成...", "长方形", ["圆形", "三角形", "正方形", "长方形"], 3, ["拼长了"]),
    ]
    for i, (q, ans, opts, diff, hints) in enumerate(ex_43):
        await insert_exercise(db, *_shape_ex(f"ex-43-{i+1:02d}", "lesson-43",
                                              q, ans, opts, diff, hints))


async def main():
    db = await get_db()
    await seed(db)
    await db.commit()
    await db.close()
    print("✅ course-05 (认识图形) 已 seed")


if __name__ == "__main__":
    asyncio.run(main())
