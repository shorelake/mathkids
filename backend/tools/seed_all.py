"""一键调用所有课程 seeder。

用法:
    python -m tools.seed_all              # 运行全部
    python -m tools.seed_all --only 02    # 只运行 course-02
    python -m tools.seed_all --list       # 列出所有可用 seeder
"""
import argparse, asyncio, importlib, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models import init_db, get_db

# 课程 seeder 模块顺序
SEEDERS = [
    ("01", "tools.seeders.course_01_add_sub_20", "20 以内加减法"),
    ("02", "tools.seeders.course_02_add_sub_100", "100 以内加减法 ⭐"),
    ("03", "tools.seeders.course_03_multiplication", "乘法启蒙"),
    ("04", "tools.seeders.course_04_division", "除法启蒙"),
    ("05", "tools.seeders.course_05_geometry", "认识图形"),
    ("06", "tools.seeders.course_06_fractions", "分数启蒙"),
    ("07", "tools.seeders.course_07_time", "认识时间"),
]


async def run_all(only: str | None = None):
    await init_db()
    db = await get_db()
    for key, mod_name, label in SEEDERS:
        if only and only != key:
            continue
        mod = importlib.import_module(mod_name)
        print(f"→ seeding course-{key}: {label}")
        await mod.seed(db)
        await db.commit()
    await db.close()
    print("✅ All done.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="只运行指定编号的课程 seeder (e.g. 02)")
    ap.add_argument("--list", action="store_true", help="列出所有可用 seeder")
    args = ap.parse_args()

    if args.list:
        print("可用 seeder:")
        for k, _, label in SEEDERS:
            print(f"  {k}  {label}")
        return

    asyncio.run(run_all(args.only))


if __name__ == "__main__":
    main()
