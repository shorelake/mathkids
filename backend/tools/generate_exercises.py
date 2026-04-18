"""
题库扩充脚本 (append-only, idempotent)
========================================

用法:
    python -m tools.generate_exercises               # 默认: 为所有有配置的课时补齐
    python -m tools.generate_exercises --dry-run     # 只预览，不写入
    python -m tools.generate_exercises --lesson 14   # 只处理 lesson-14
    python -m tools.generate_exercises --course 02   # 只处理课程 02 下所有课时
    python -m tools.generate_exercises --count 50    # 覆盖默认目标数量
    python -m tools.generate_exercises --force       # 先清除旧的"生成"题目再重新生成
    python -m tools.generate_exercises --seed 42     # 指定随机种子（结果可复现）

设计:
    1. **追加式** - INSERT OR IGNORE，不覆盖已有题目
    2. **幂等** - 稳定 ID 规则 (见 _gen_id)，重复运行不产生重复
    3. **与 seed 题共存** - 种子题 ID 形如 `ex-14-01`，生成题 ID 形如 `ex-14-g-p2708`
    4. **配置驱动** - LESSON_SPECS 按课时声明 (a,b) 候选池
    5. **多题型支持** - addsub / mult / div / triple_add / custom
"""

import argparse
import asyncio
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import get_db
from tools._common import (
    JD, make_ex_addsub, make_ex_100, make_ex_mult, make_ex_div, _options_for,
)


# ==========================================================
# 每个课时的题库配置
# ==========================================================
#
# kind:
#   "addsub20"  - 20 以内加减，使用 make_ex_addsub
#   "addsub100" - 100 以内加减，使用 make_ex_100
#   "mult"      - 乘法，使用 make_ex_mult
#   "div"       - 除法，使用 make_ex_div
#   "triple"    - 三数连加（特殊处理）
#   "mixed"     - 混合加减（pool 返回 (a,b,op) 三元组）
#
# pool: lambda → list of tuples
# count: 目标题数（若 pool 不足则取全部）
# choice_ratio: 选择题比例
# difficulty: [1], [1,2,3] 等，循环使用

LESSON_SPECS = {
    # =============== COURSE-01: 20 以内加减法 ===============
    "lesson-01": {
        "kind": "addsub20", "op": "+",
        "pool": lambda: [(a, b) for a in range(1, 6) for b in range(1, 6) if a + b <= 5],
        "count": 40, "choice_ratio": 0.25, "difficulty": [1],
    },
    "lesson-02": {
        "kind": "addsub20", "op": "+",
        "pool": lambda: [(a, b) for a in range(1, 10) for b in range(1, 10) if 2 <= a + b <= 10],
        "count": 60, "choice_ratio": 0.25, "difficulty": [1, 2, 3],
    },
    "lesson-03": {
        "kind": "addsub20", "op": "-",
        "pool": lambda: [(a, b) for a in range(2, 11) for b in range(1, a + 1)],
        "count": 60, "choice_ratio": 0.25, "difficulty": [1, 2, 3],
    },
    "lesson-04": {
        "kind": "addsub20", "op": "+",
        "pool": lambda: [(a, b) for a in range(10, 20) for b in range(1, 10) if (a % 10) + b <= 9],
        "count": 50, "choice_ratio": 0.25, "difficulty": [1, 2, 3],
    },
    "lesson-05": {
        "kind": "addsub20", "op": "+",
        "pool": lambda: [(a, b) for a in range(2, 10) for b in range(2, 10) if 10 < a + b <= 18],
        "count": 80, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },
    "lesson-06": {
        "kind": "addsub20", "op": "-",
        "pool": lambda: [(a, b) for a in range(11, 19) for b in range(2, 10)
                         if b > (a % 10) and (a - b) >= 0],
        "count": 60, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },
    "lesson-07": {
        "kind": "mixed",
        "pool": lambda: (
            [(a, b, "+") for a in range(3, 10) for b in range(3, 10) if 10 < a + b <= 18] +
            [(a, b, "-") for a in range(11, 19) for b in range(2, 10)
             if b > (a % 10) and (a - b) >= 0]
        ),
        "count": 50, "choice_ratio": 0.25, "difficulty": [1, 2, 3],
    },
    "lesson-08": {
        "kind": "triple",
        "pool": lambda: [(a, b, c) for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)
                         if 3 <= a + b + c <= 20],
        "count": 40, "choice_ratio": 0.5, "difficulty": [1, 2, 3],
    },

    # =============== COURSE-02: 100 以内加减法 ===============
    "lesson-11": {  # 整十加减
        "kind": "addsub100",
        "pool": lambda: (
            [(a, b, "+") for a in range(10, 100, 10) for b in range(10, 100, 10) if a + b <= 100] +
            [(a, b, "-") for a in range(20, 100, 10) for b in range(10, a, 10)]
        ),
        "mixed_pool": True,  # pool 已包含 op
        "count": 40, "choice_ratio": 0.25, "difficulty": [1, 2],
    },
    "lesson-12": {  # 整十 + 一位
        "kind": "addsub100", "op": "+",
        "pool": lambda: [(a, b) for a in range(10, 100, 10) for b in range(1, 10)],
        "count": 50, "choice_ratio": 0.25, "difficulty": [1, 2],
    },
    "lesson-13": {  # 两位 + 一位不进位
        "kind": "addsub100", "op": "+",
        "pool": lambda: [(a, b) for a in range(11, 100) for b in range(1, 10)
                         if a % 10 != 0 and (a % 10) + b <= 9],
        "count": 60, "choice_ratio": 0.25, "difficulty": [1, 2, 3],
    },
    "lesson-14": {  # 两位 + 一位进位 ⭐
        "kind": "addsub100", "op": "+",
        "pool": lambda: [(a, b) for a in range(12, 100) for b in range(2, 10)
                         if a % 10 != 0 and (a % 10) + b >= 10 and a + b <= 100],
        "count": 100, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },
    "lesson-15": {  # 两位 - 一位不退位
        "kind": "addsub100", "op": "-",
        "pool": lambda: [(a, b) for a in range(11, 100) for b in range(1, 10)
                         if a % 10 >= b],
        "count": 60, "choice_ratio": 0.25, "difficulty": [1, 2, 3],
    },
    "lesson-16": {  # 两位 - 一位退位 ⭐
        "kind": "addsub100", "op": "-",
        "pool": lambda: [(a, b) for a in range(11, 100) for b in range(2, 10)
                         if a % 10 < b and a - b >= 10],
        "count": 100, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },
    "lesson-17": {  # 两位 + 两位
        "kind": "addsub100", "op": "+",
        "pool": lambda: [(a, b) for a in range(11, 100) for b in range(11, 100)
                         if a + b <= 100],
        "count": 80, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },
    "lesson-18": {  # 两位 - 两位
        "kind": "addsub100", "op": "-",
        "pool": lambda: [(a, b) for a in range(20, 100) for b in range(11, a)
                         if (a - b) < 100],
        "count": 80, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },

    # =============== COURSE-03: 乘法 ===============
    "lesson-21": {
        "kind": "mult",
        "pool": lambda: [(a, b) for a in range(2, 6) for b in range(2, 6)],
        "count": 20, "choice_ratio": 0.3, "difficulty": [1],
    },
    "lesson-22": {  # 2、3 的乘法
        "kind": "mult",
        "pool": lambda: [(a, b) for a in (2, 3) for b in range(2, 10)]
                        + [(b, a) for a in (2, 3) for b in range(2, 10)],
        "count": 40, "choice_ratio": 0.25, "difficulty": [1, 2],
    },
    "lesson-23": {  # 4、5 的乘法
        "kind": "mult",
        "pool": lambda: [(a, b) for a in (4, 5) for b in range(2, 10)]
                        + [(b, a) for a in (4, 5) for b in range(2, 10)],
        "count": 40, "choice_ratio": 0.25, "difficulty": [1, 2],
    },
    "lesson-24": {  # 6、7 的乘法
        "kind": "mult",
        "pool": lambda: [(a, b) for a in (6, 7) for b in range(2, 10)]
                        + [(b, a) for a in (6, 7) for b in range(2, 10)],
        "count": 40, "choice_ratio": 0.25, "difficulty": [2, 3],
    },
    "lesson-25": {  # 8、9 的乘法
        "kind": "mult",
        "pool": lambda: [(a, b) for a in (8, 9) for b in range(2, 10)]
                        + [(b, a) for a in (8, 9) for b in range(2, 10)],
        "count": 40, "choice_ratio": 0.25, "difficulty": [2, 3],
    },
    "lesson-26": {  # 乘法综合
        "kind": "mult",
        "pool": lambda: [(a, b) for a in range(2, 10) for b in range(2, 10)],
        "count": 60, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },

    # =============== COURSE-04: 除法 ===============
    "lesson-31": {  # 用 2、3 除
        "kind": "div",
        "pool": lambda: [(a, b) for a in range(4, 31) for b in (2, 3) if a % b == 0],
        "count": 40, "choice_ratio": 0.25, "difficulty": [1, 2],
    },
    "lesson-32": {  # 4、5 的除法
        "kind": "div",
        "pool": lambda: [(a, b) for a in range(8, 51) for b in (4, 5) if a % b == 0],
        "count": 40, "choice_ratio": 0.25, "difficulty": [2],
    },
    "lesson-33": {  # 6、7、8、9 的除法
        "kind": "div",
        "pool": lambda: [(a, b) for a in range(12, 82) for b in (6, 7, 8, 9) if a % b == 0],
        "count": 60, "choice_ratio": 0.25, "difficulty": [2, 3],
    },
    "lesson-34": {  # 综合
        "kind": "div",
        "pool": lambda: [(a, b) for a in range(6, 82) for b in range(2, 10) if a % b == 0],
        "count": 60, "choice_ratio": 0.3, "difficulty": [1, 2, 3],
    },
}


# 课程 → 课时前缀映射 (用于 --course 过滤)
COURSE_LESSONS = {
    "01": ["lesson-01","lesson-02","lesson-03","lesson-04","lesson-05","lesson-06","lesson-07","lesson-08"],
    "02": ["lesson-11","lesson-12","lesson-13","lesson-14","lesson-15","lesson-16","lesson-17","lesson-18"],
    "03": ["lesson-21","lesson-22","lesson-23","lesson-24","lesson-25","lesson-26"],
    "04": ["lesson-31","lesson-32","lesson-33","lesson-34"],
}


GEN_ID_PREFIX = "-g-"


def _gen_id(lesson_id: str, op_token: str, *nums) -> str:
    """生成稳定的题目 ID。
    lesson-14 + 'p' + (27,8) → 'ex-14-g-p2708'
    lesson-33 + 'd' + (24,6) → 'ex-33-g-d2406'
    lesson-08 + 't' + (3,4,5) → 'ex-08-g-t030405'
    """
    lesson_num = lesson_id.split("-")[-1]
    nums_str = "".join(f"{n:02d}" for n in nums)
    return f"ex-{lesson_num}{GEN_ID_PREFIX}{op_token}{nums_str}"


def _op_token(op: str) -> str:
    return {"+": "p", "-": "m", "*": "x", "/": "d", "triple_add": "t"}.get(op, "?")


def _triple_row(eid, lid, a, b, c, diff, typ):
    ans = a + b + c
    opts = _options_for(ans) if typ == "choice" else []
    h = ["先算前两个数", "把结果再加上最后一个数"]
    s = [{"method": "step_by_step",
          "steps": [f"先算 {a}+{b}={a+b}", f"再算 {a+b}+{c}={ans}"]}]
    return (eid, lid, typ, f"{a} + {b} + {c} = ?", f"{a}+{b}+{c}",
            str(ans), diff, JD(s), JD(h), JD(opts), diff)


# ==========================================================
# 主流程
# ==========================================================

async def _count(db, lid):
    r = await db.execute("SELECT COUNT(*) as c FROM exercises WHERE lesson_id=?", (lid,))
    total = (await r.fetchone())["c"]
    r = await db.execute(
        "SELECT COUNT(*) as c FROM exercises WHERE lesson_id=? AND id LIKE ?",
        (lid, f"%{GEN_ID_PREFIX}%"))
    gen = (await r.fetchone())["c"]
    return total, gen


async def _delete_generated(db, lid):
    r = await db.execute(
        "SELECT COUNT(*) as c FROM exercises WHERE lesson_id=? AND id LIKE ?",
        (lid, f"%{GEN_ID_PREFIX}%"))
    n = (await r.fetchone())["c"]
    await db.execute(
        "DELETE FROM exercises WHERE lesson_id=? AND id LIKE ?",
        (lid, f"%{GEN_ID_PREFIX}%"))
    return n


def _build_rows(lid, spec, count, rng):
    pool = list(spec["pool"]())
    if not pool:
        return []
    rng.shuffle(pool)
    take = pool[:min(count, len(pool))]

    rows = []
    diffs = spec["difficulty"]
    ratio = spec["choice_ratio"]
    choice_every = max(1, int(round(1 / ratio))) if ratio > 0 else 10**9
    kind = spec["kind"]

    for i, item in enumerate(take):
        typ = "choice" if i % choice_every == 0 else "fill_blank"
        diff = diffs[i % len(diffs)]

        if kind == "triple":
            a, b, c = item
            eid = _gen_id(lid, "t", a, b, c)
            rows.append(_triple_row(eid, lid, a, b, c, diff, typ))
        elif kind == "mixed":
            a, b, op = item
            eid = _gen_id(lid, _op_token(op), a, b)
            rows.append(make_ex_addsub(eid, lid, a, b, op, diff, typ))
        elif kind == "addsub20":
            a, b = item
            op = spec["op"]
            eid = _gen_id(lid, _op_token(op), a, b)
            rows.append(make_ex_addsub(eid, lid, a, b, op, diff, typ))
        elif kind == "addsub100":
            if spec.get("mixed_pool"):  # pool 里带 op
                a, b, op = item
            else:
                a, b = item; op = spec["op"]
            eid = _gen_id(lid, _op_token(op), a, b)
            rows.append(make_ex_100(eid, lid, a, b, op, diff, typ))
        elif kind == "mult":
            a, b = item
            eid = _gen_id(lid, "x", a, b)
            rows.append(make_ex_mult(eid, lid, a, b, diff, typ))
        elif kind == "div":
            a, b = item
            eid = _gen_id(lid, "d", a, b)
            rows.append(make_ex_div(eid, lid, a, b, diff, typ))
    return rows


async def run(lesson_filter, course_filter, count_override, force, dry_run, seed):
    rng = random.Random(seed) if seed is not None else random.Random()
    db = await get_db()

    INS = ('INSERT OR IGNORE INTO exercises '
           '(id,lesson_id,type,question,expression,correct_answer,"order",'
           'solutions,hints,options,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)')

    # Determine which lessons to process
    if lesson_filter:
        key = lesson_filter if lesson_filter.startswith("lesson-") else f"lesson-{lesson_filter.zfill(2)}"
        if key not in LESSON_SPECS:
            print(f"❌ 未知或未配置课时: {key}"); return
        target_lessons = {key: LESSON_SPECS[key]}
    elif course_filter:
        allow = set(COURSE_LESSONS.get(course_filter, []))
        target_lessons = {k: v for k, v in LESSON_SPECS.items() if k in allow}
        if not target_lessons:
            print(f"❌ 课程 {course_filter} 下没有课时配置"); return
    else:
        target_lessons = LESSON_SPECS

    print(f"{'🔍 预览' if dry_run else '✍️  写入'} | seed={seed} | "
          f"处理 {len(target_lessons)} 个课时")
    print("=" * 68)

    total_added = 0
    for lid, spec in target_lessons.items():
        target = count_override or spec["count"]
        pool_size = len(list(spec["pool"]()))

        if force and not dry_run:
            deleted = await _delete_generated(db, lid)
            if deleted:
                print(f"  [{lid}] 清除旧生成 {deleted} 条")

        before_total, before_gen = await _count(db, lid)
        rows = _build_rows(lid, spec, target, rng)

        if dry_run:
            samples = [(r[3], r[5]) for r in rows[:3]]
            print(f"[{lid:10}] 池 {pool_size:4d} | 目标 {target:3d} | 现有 {before_total:3d} "
                  f"(生成 {before_gen}) | 将插入 {len(rows)}")
            if samples:
                print(f"              示例: {samples}")
            continue

        inserted = 0
        for r in rows:
            sr = list(r)
            for idx in (7, 8, 9):
                if isinstance(sr[idx], (list, dict)):
                    sr[idx] = JD(sr[idx])
            cur = await db.execute(INS, sr)
            inserted += cur.rowcount
        await db.commit()

        after_total, after_gen = await _count(db, lid)
        total_added += inserted
        marker = "⭐" if target >= 80 else "  "
        print(f"{marker}[{lid:10}] 池 {pool_size:4d} | 目标 {target:3d} | "
              f"新增 {inserted:3d} | 题目 {before_total:3d}→{after_total:3d} "
              f"(生成 {before_gen}→{after_gen})")

    await db.close()
    if not dry_run:
        print("=" * 68)
        print(f"✅ 完成，共新增 {total_added} 题")


def main():
    ap = argparse.ArgumentParser(description="题库扩充脚本")
    ap.add_argument("--lesson", help="只处理指定课时 (e.g. 14 或 lesson-14)")
    ap.add_argument("--course", help="只处理指定课程 (01/02/03/04)")
    ap.add_argument("--count", type=int, help="覆盖默认目标数量")
    ap.add_argument("--force", action="store_true", help="先删除已生成题目再重新生成")
    ap.add_argument("--dry-run", action="store_true", help="只预览，不写入")
    ap.add_argument("--seed", type=int, help="随机种子（复现）", default=42)
    args = ap.parse_args()

    asyncio.run(run(args.lesson, args.course, args.count, args.force, args.dry_run, args.seed))


if __name__ == "__main__":
    main()
