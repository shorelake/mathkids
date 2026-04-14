import aiosqlite
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "mathkids.db")

async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db

async def init_db():
    db = await get_db()
    await db.executescript("""
    CREATE TABLE IF NOT EXISTS courses (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        grade_range TEXT DEFAULT '6-10',
        "order" INTEGER DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','published','archived')),
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS lessons (
        id TEXT PRIMARY KEY,
        course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        "order" INTEGER DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','published')),
        teaching_methods TEXT DEFAULT '[]',
        animation_data TEXT DEFAULT '{}',
        created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS exercises (
        id TEXT PRIMARY KEY,
        lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
        type TEXT DEFAULT 'fill_blank' CHECK(type IN ('choice','fill_blank','drag_drop','true_false')),
        question TEXT NOT NULL,
        expression TEXT DEFAULT '',
        options TEXT DEFAULT '[]',
        correct_answer TEXT NOT NULL,
        solutions TEXT DEFAULT '[]',
        hints TEXT DEFAULT '[]',
        difficulty INTEGER DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 3),
        "order" INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
        stars INTEGER DEFAULT 0 CHECK(stars BETWEEN 0 AND 3),
        correct_count INTEGER DEFAULT 0,
        total_count INTEGER DEFAULT 0,
        time_spent INTEGER DEFAULT 0,
        completed_at TEXT,
        UNIQUE(user_id, lesson_id)
    );

    CREATE TABLE IF NOT EXISTS ai_config (
        id INTEGER PRIMARY KEY CHECK(id = 1),
        provider TEXT DEFAULT 'openai',
        api_key TEXT DEFAULT '',
        base_url TEXT DEFAULT 'https://api.openai.com/v1',
        model TEXT DEFAULT 'gpt-4o-mini'
    );

    INSERT OR IGNORE INTO ai_config (id) VALUES (1);
    """)
    await db.commit()
    await db.close()


async def seed_data():
    """Seed the database with the 20-within addition/subtraction course."""
    db = await get_db()

    existing = await db.execute("SELECT COUNT(*) as c FROM courses")
    row = await existing.fetchone()
    if row["c"] > 0:
        await db.close()
        return

    now = datetime.now().isoformat()
    course_id = "course-add-sub-20"

    await db.execute(
        'INSERT INTO courses (id, title, description, grade_range, "order", status, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?)',
        (course_id, "20以内加减法", "适合6-8岁儿童的20以内加减法启蒙课程，包含凑十法、破十法、数轴法等多种教学方法", "6-8", 1, "published", now, now)
    )

    lessons = [
        ("lesson-01", "认识加法", "通过实物动画演示简单加法概念", 1, "published",
         '["counting"]',
         json.dumps({
             "expression": "2 + 3 = 5",
             "methods": [{
                 "type": "counting", "title": "数数法",
                 "steps": [
                     {"action": "show_objects", "left": 2, "right": 3, "shape": "apple", "narration": "左边有 2 个苹果，右边有 3 个苹果"},
                     {"action": "count_all", "sequence": [1,2,3,4,5], "narration": "一个一个数：1, 2, 3, 4, 5"},
                     {"action": "show_result", "result": 5, "narration": "一共有 5 个苹果，所以 2 + 3 = 5"}
                 ]
             }]
         }, ensure_ascii=False)),
        ("lesson-02", "10以内加法", "用凑十法和数轴法学习10以内加法", 2, "published",
         '["counting", "number_line"]',
         json.dumps({
             "expression": "4 + 3 = 7",
             "methods": [
                 {"type": "counting", "title": "数数法", "steps": [
                     {"action": "show_objects", "left": 4, "right": 3, "shape": "star", "narration": "左边有 4 颗星，右边有 3 颗星"},
                     {"action": "count_on", "start": 4, "count": 3, "narration": "从 4 开始接着数：5, 6, 7"},
                     {"action": "show_result", "result": 7, "narration": "所以 4 + 3 = 7"}
                 ]},
                 {"type": "number_line", "title": "数轴法", "steps": [
                     {"action": "draw_line", "from": 0, "to": 10, "narration": "画一条从 0 到 10 的数轴"},
                     {"action": "mark_start", "position": 4, "narration": "先在 4 的位置标记起点"},
                     {"action": "jump", "count": 3, "direction": "right", "narration": "往右跳 3 步：5, 6, 7"},
                     {"action": "mark_end", "position": 7, "narration": "落在 7 上，所以 4 + 3 = 7"}
                 ]}
             ]
         }, ensure_ascii=False)),
        ("lesson-03", "10以内减法", "用拿走法和数轴回跳学习减法", 3, "published",
         '["counting", "number_line"]',
         json.dumps({
             "expression": "7 - 3 = 4",
             "methods": [
                 {"type": "counting", "title": "拿走法", "steps": [
                     {"action": "show_objects", "left": 7, "right": 0, "shape": "apple", "narration": "有 7 个苹果"},
                     {"action": "remove", "count": 3, "narration": "拿走 3 个"},
                     {"action": "show_result", "result": 4, "narration": "还剩 4 个，所以 7 - 3 = 4"}
                 ]},
                 {"type": "number_line", "title": "数轴法", "steps": [
                     {"action": "draw_line", "from": 0, "to": 10, "narration": "画一条从 0 到 10 的数轴"},
                     {"action": "mark_start", "position": 7, "narration": "先在 7 的位置标记起点"},
                     {"action": "jump", "count": 3, "direction": "left", "narration": "往左跳 3 步：6, 5, 4"},
                     {"action": "mark_end", "position": 4, "narration": "落在 4 上，所以 7 - 3 = 4"}
                 ]}
             ]
         }, ensure_ascii=False)),
        ("lesson-04", "20以内不进位加法", "个位直接相加，不需要进位", 4, "published",
         '["number_line", "step_by_step"]',
         json.dumps({
             "expression": "12 + 3 = 15",
             "methods": [
                 {"type": "step_by_step", "title": "分步法", "steps": [
                     {"action": "decompose", "number": 12, "parts": [10, 2], "narration": "把 12 拆成 10 和 2"},
                     {"action": "add_ones", "values": [2, 3], "result": 5, "narration": "先算个位：2 + 3 = 5"},
                     {"action": "combine", "values": [10, 5], "result": 15, "narration": "再加上十位：10 + 5 = 15"}
                 ]},
                 {"type": "number_line", "title": "数轴法", "steps": [
                     {"action": "draw_line", "from": 0, "to": 20, "narration": "画一条从 0 到 20 的数轴"},
                     {"action": "mark_start", "position": 12, "narration": "在 12 的位置出发"},
                     {"action": "jump", "count": 3, "direction": "right", "narration": "往右跳 3 步：13, 14, 15"},
                     {"action": "mark_end", "position": 15, "narration": "落在 15 上，所以 12 + 3 = 15"}
                 ]}
             ]
         }, ensure_ascii=False)),
        ("lesson-05", "20以内进位加法（凑十法）", "重点掌握凑十法，一题多解", 5, "published",
         '["make_ten", "number_line", "counting"]',
         json.dumps({
             "expression": "8 + 5 = 13",
             "methods": [
                 {"type": "make_ten", "title": "凑十法", "steps": [
                     {"action": "show_objects", "left": 8, "right": 5, "shape": "apple", "narration": "左边有 8 个苹果，右边有 5 个苹果"},
                     {"action": "think_split", "target": "right", "need": 2, "narration": "8 凑成 10 还差 2，所以把 5 拆成 2 和 3"},
                     {"action": "split", "target": "right", "parts": [2, 3], "narration": "5 = 2 + 3"},
                     {"action": "move_to_left", "count": 2, "narration": "把 2 移到左边和 8 凑成 10"},
                     {"action": "highlight_ten", "value": 10, "narration": "8 + 2 = 10"},
                     {"action": "combine", "values": [10, 3], "result": 13, "narration": "10 + 3 = 13，所以 8 + 5 = 13"}
                 ]},
                 {"type": "number_line", "title": "数轴法", "steps": [
                     {"action": "draw_line", "from": 0, "to": 20, "narration": "画一条 0 到 20 的数轴"},
                     {"action": "mark_start", "position": 8, "narration": "从 8 出发"},
                     {"action": "jump_split", "first_jump": 2, "second_jump": 3, "via": 10, "narration": "先跳 2 步到 10，再跳 3 步到 13"},
                     {"action": "mark_end", "position": 13, "narration": "所以 8 + 5 = 13"}
                 ]},
                 {"type": "counting", "title": "数数法", "steps": [
                     {"action": "show_objects", "left": 8, "right": 5, "shape": "star", "narration": "左边 8 颗星，右边 5 颗星"},
                     {"action": "count_on", "start": 8, "count": 5, "narration": "从 8 接着数：9, 10, 11, 12, 13"},
                     {"action": "show_result", "result": 13, "narration": "数到 13，所以 8 + 5 = 13"}
                 ]}
             ]
         }, ensure_ascii=False)),
        ("lesson-06", "20以内退位减法（破十法）", "学习破十法处理退位减法", 6, "published",
         '["break_ten", "number_line"]',
         json.dumps({
             "expression": "13 - 8 = 5",
             "methods": [
                 {"type": "break_ten", "title": "破十法", "steps": [
                     {"action": "show_objects", "total": 13, "shape": "apple", "narration": "有 13 个苹果"},
                     {"action": "decompose", "number": 13, "parts": [10, 3], "narration": "把 13 拆成 10 和 3"},
                     {"action": "subtract_from_ten", "minuend": 10, "subtrahend": 8, "result": 2, "narration": "先从 10 里减去 8，得到 2"},
                     {"action": "combine", "values": [2, 3], "result": 5, "narration": "2 + 3 = 5，所以 13 - 8 = 5"}
                 ]},
                 {"type": "number_line", "title": "数轴法", "steps": [
                     {"action": "draw_line", "from": 0, "to": 20, "narration": "画一条 0 到 20 的数轴"},
                     {"action": "mark_start", "position": 13, "narration": "从 13 出发"},
                     {"action": "jump_split", "first_jump": 3, "second_jump": 5, "via": 10, "direction": "left", "narration": "先往左跳 3 步到 10，再跳 5 步到 5"},
                     {"action": "mark_end", "position": 5, "narration": "所以 13 - 8 = 5"}
                 ]}
             ]
         }, ensure_ascii=False)),
        ("lesson-07", "加减混合练习", "综合运用多种方法做加减混合题", 7, "published",
         '["make_ten", "break_ten", "number_line"]',
         json.dumps({
             "expression": "9 + 6 = 15",
             "methods": [
                 {"type": "make_ten", "title": "凑十法", "steps": [
                     {"action": "show_objects", "left": 9, "right": 6, "shape": "apple", "narration": "左边 9 个，右边 6 个"},
                     {"action": "think_split", "target": "right", "need": 1, "narration": "9 凑成 10 还差 1，把 6 拆成 1 和 5"},
                     {"action": "split", "target": "right", "parts": [1, 5], "narration": "6 = 1 + 5"},
                     {"action": "move_to_left", "count": 1, "narration": "把 1 移过去凑成 10"},
                     {"action": "highlight_ten", "value": 10, "narration": "9 + 1 = 10"},
                     {"action": "combine", "values": [10, 5], "result": 15, "narration": "10 + 5 = 15"}
                 ]}
             ]
         }, ensure_ascii=False)),
        ("lesson-08", "三个数连算", "学习从左到右分步计算三个数", 8, "draft",
         '["step_by_step"]',
         json.dumps({
             "expression": "3 + 5 + 2 = 10",
             "methods": [
                 {"type": "step_by_step", "title": "分步法", "steps": [
                     {"action": "highlight_first_pair", "values": [3, 5], "narration": "先算前两个数：3 + 5"},
                     {"action": "compute", "expression": "3 + 5", "result": 8, "narration": "3 + 5 = 8"},
                     {"action": "replace", "old": "3 + 5", "new": 8, "narration": "用 8 替换 3 + 5"},
                     {"action": "compute", "expression": "8 + 2", "result": 10, "narration": "8 + 2 = 10，所以 3 + 5 + 2 = 10"}
                 ]}
             ]
         }, ensure_ascii=False)),
    ]

    for l in lessons:
        await db.execute(
            'INSERT INTO lessons (id, course_id, title, description, "order", status, teaching_methods, animation_data, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
            (l[0], course_id, l[1], l[2], l[3], l[4], l[5], l[6], now, now)
        )

    # Exercises for lesson-05 (20以内进位加法)
    exercises_05 = [
        ("ex-05-01", "fill_blank", "8 + 5 = ?", "8+5", "13", 1,
         json.dumps([{"method":"make_ten","steps":["5拆成2和3","8+2=10","10+3=13"]},{"method":"counting","steps":["从8接着数：9,10,11,12,13"]}], ensure_ascii=False),
         json.dumps(["想想8凑成10还差几？","把5拆开，先凑十"], ensure_ascii=False)),
        ("ex-05-02", "fill_blank", "7 + 6 = ?", "7+6", "13", 1,
         json.dumps([{"method":"make_ten","steps":["6拆成3和3","7+3=10","10+3=13"]}], ensure_ascii=False),
         json.dumps(["7凑成10还差3","把6拆成3和3"], ensure_ascii=False)),
        ("ex-05-03", "fill_blank", "9 + 4 = ?", "9+4", "13", 1,
         json.dumps([{"method":"make_ten","steps":["4拆成1和3","9+1=10","10+3=13"]}], ensure_ascii=False),
         json.dumps(["9凑成10只差1","把4拆成1和3"], ensure_ascii=False)),
        ("ex-05-04", "choice", "6 + 8 = ?", "6+8", "14", 2,
         json.dumps([{"method":"make_ten","steps":["8+2=10","10+4=14"]}], ensure_ascii=False),
         json.dumps(["可以把6拆成2和4"], ensure_ascii=False)),
        ("ex-05-05", "fill_blank", "5 + 7 = ?", "5+7", "12", 2,
         json.dumps([{"method":"make_ten","steps":["7+3=10","10+2=12"]}], ensure_ascii=False),
         json.dumps(["7凑成10还差3","把5拆成3和2"], ensure_ascii=False)),
        ("ex-05-06", "fill_blank", "8 + 8 = ?", "8+8", "16", 2,
         json.dumps([{"method":"make_ten","steps":["8拆成2和6","8+2=10","10+6=16"]},{"method":"counting","steps":["双倍数：8+8=16"]}], ensure_ascii=False),
         json.dumps(["8凑成10还差2","也可以想：双倍的8"], ensure_ascii=False)),
        ("ex-05-07", "choice", "9 + 7 = ?", "9+7", "16", 2,
         json.dumps([{"method":"make_ten","steps":["7拆成1和6","9+1=10","10+6=16"]}], ensure_ascii=False),
         json.dumps(["9凑成10只差1"], ensure_ascii=False)),
        ("ex-05-08", "fill_blank", "6 + 5 = ?", "6+5", "11", 1,
         json.dumps([{"method":"make_ten","steps":["5拆成4和1","6+4=10","10+1=11"]}], ensure_ascii=False),
         json.dumps(["6凑成10还差4"], ensure_ascii=False)),
        ("ex-05-09", "fill_blank", "7 + 8 = ?", "7+8", "15", 3,
         json.dumps([{"method":"make_ten","steps":["8+2=10","10+5=15"]}], ensure_ascii=False),
         json.dumps(["把7拆成2和5"], ensure_ascii=False)),
        ("ex-05-10", "fill_blank", "9 + 9 = ?", "9+9", "18", 3,
         json.dumps([{"method":"make_ten","steps":["9+1=10","10+8=18"]},{"method":"counting","steps":["双倍数：9+9=18"]}], ensure_ascii=False),
         json.dumps(["9+1=10","或者想：双倍的9"], ensure_ascii=False)),
    ]

    for e in exercises_05:
        opts = '["12","13","14","15"]' if e[2].startswith("6 + 8") else '["14","15","16","17"]' if e[2].startswith("9 + 7") else '[]'
        await db.execute(
            'INSERT INTO exercises (id, lesson_id, type, question, expression, correct_answer, "order", solutions, hints, options, difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (e[0], "lesson-05", e[1], e[2], e[3], e[4], e[5], e[6], e[7], opts, e[5] if e[5] <= 3 else 1)
        )

    # Also add exercises for other lessons
    basic_exercises = [
        # lesson-01
        ("ex-01-01", "lesson-01", "fill_blank", "1 + 1 = ?", "1+1", "2", 1, 1),
        ("ex-01-02", "lesson-01", "fill_blank", "2 + 1 = ?", "2+1", "3", 2, 1),
        ("ex-01-03", "lesson-01", "fill_blank", "2 + 3 = ?", "2+3", "5", 3, 1),
        # lesson-02
        ("ex-02-01", "lesson-02", "fill_blank", "3 + 4 = ?", "3+4", "7", 1, 1),
        ("ex-02-02", "lesson-02", "fill_blank", "5 + 5 = ?", "5+5", "10", 2, 1),
        ("ex-02-03", "lesson-02", "fill_blank", "6 + 3 = ?", "6+3", "9", 3, 2),
        # lesson-03
        ("ex-03-01", "lesson-03", "fill_blank", "5 - 2 = ?", "5-2", "3", 1, 1),
        ("ex-03-02", "lesson-03", "fill_blank", "8 - 3 = ?", "8-3", "5", 2, 1),
        ("ex-03-03", "lesson-03", "fill_blank", "10 - 4 = ?", "10-4", "6", 3, 2),
        # lesson-06
        ("ex-06-01", "lesson-06", "fill_blank", "13 - 8 = ?", "13-8", "5", 1, 2),
        ("ex-06-02", "lesson-06", "fill_blank", "15 - 7 = ?", "15-7", "8", 2, 2),
        ("ex-06-03", "lesson-06", "fill_blank", "12 - 9 = ?", "12-9", "3", 3, 3),
    ]
    for e in basic_exercises:
        await db.execute(
            'INSERT INTO exercises (id, lesson_id, type, question, expression, correct_answer, "order", difficulty, solutions, hints) VALUES (?,?,?,?,?,?,?,?,?,?)',
            (e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], '[]', '[]')
        )

    await db.commit()
    await db.close()
    print("✅ Seed data inserted successfully")
