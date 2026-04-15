import aiosqlite, json, os
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
        id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT DEFAULT '',
        grade_range TEXT DEFAULT '6-10', "order" INTEGER DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','published','archived')),
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS lessons (
        id TEXT PRIMARY KEY, course_id TEXT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
        title TEXT NOT NULL, description TEXT DEFAULT '', "order" INTEGER DEFAULT 0,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft','published')),
        teaching_methods TEXT DEFAULT '[]', animation_data TEXT DEFAULT '{}',
        animation_variants TEXT DEFAULT '[]',
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS exercises (
        id TEXT PRIMARY KEY, lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
        type TEXT DEFAULT 'fill_blank' CHECK(type IN ('choice','fill_blank','drag_drop','true_false')),
        question TEXT NOT NULL, expression TEXT DEFAULT '', options TEXT DEFAULT '[]',
        correct_answer TEXT NOT NULL, solutions TEXT DEFAULT '[]', hints TEXT DEFAULT '[]',
        difficulty INTEGER DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 3), "order" INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS user_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL,
        lesson_id TEXT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
        stars INTEGER DEFAULT 0 CHECK(stars BETWEEN 0 AND 3),
        correct_count INTEGER DEFAULT 0, total_count INTEGER DEFAULT 0,
        time_spent INTEGER DEFAULT 0, completed_at TEXT, UNIQUE(user_id, lesson_id)
    );
    CREATE TABLE IF NOT EXISTS ai_config (
        id INTEGER PRIMARY KEY CHECK(id = 1), provider TEXT DEFAULT 'openai',
        api_key TEXT DEFAULT '', base_url TEXT DEFAULT 'https://api.openai.com/v1',
        model TEXT DEFAULT 'gpt-4o-mini'
    );
    INSERT OR IGNORE INTO ai_config (id) VALUES (1);
    """)
    await db.commit()
    await db.close()

JD = lambda x: json.dumps(x, ensure_ascii=False)

# ===== Animation generators =====

def _counting_add(a, b):
    """Simple counting addition animation."""
    s = a + b
    seq = list(range(a + 1, s + 1))
    return {"expression": f"{a} + {b} = {s}", "methods": [
        {"type": "counting", "title": "数数法", "steps": [
            {"action": "show_objects", "left": a, "right": b, "shape": "random",
             "narration": f"左边 {a} 个，右边 {b} 个"},
            {"action": "count_on", "start": a, "count": b, "sequence": seq,
             "narration": f"从 {a} 接着数：{', '.join(str(x) for x in seq)}"},
            {"action": "show_result", "result": s,
             "narration": f"数到 {s}！所以 {a} + {b} = {s}"}
        ]}
    ]}

def _counting_sub(a, b):
    """Counting subtraction animation (remove method)."""
    r = a - b
    return {"expression": f"{a} - {b} = {r}", "methods": [
        {"type": "subtraction", "title": "拿走法", "steps": [
            {"action": "show_total", "total": a, "shape": "random",
             "narration": f"一共有 {a} 个"},
            {"action": "remove", "count": b,
             "narration": f"拿走 {b} 个..."},
            {"action": "show_result", "total": a, "removed": b, "result": r,
             "narration": f"还剩 {r} 个！所以 {a} - {b} = {r}"}
        ]},
        {"type": "number_line", "title": "数轴法", "steps": [
            {"action": "draw_line", "from": 0, "to": 10, "narration": "看这条数轴"},
            {"action": "mark_start", "position": a, "narration": f"从 {a} 出发"},
            {"action": "jump", "count": b, "direction": "left",
             "narration": f"往左跳 {b} 步：{', '.join(str(a - i) for i in range(1, b + 1))}"},
            {"action": "mark_end", "position": r, "narration": f"到 {r}！所以 {a} - {b} = {r}"}
        ]}
    ]}

def _nl_add(a, b, line_max=10):
    """Number line addition."""
    s = a + b
    return {"expression": f"{a} + {b} = {s}", "methods": [
        {"type": "number_line", "title": "数轴法", "steps": [
            {"action": "draw_line", "from": 0, "to": line_max, "narration": "看这条数轴"},
            {"action": "mark_start", "position": a, "narration": f"从 {a} 出发"},
            {"action": "jump", "count": b, "direction": "right",
             "narration": f"往右跳 {b} 步：{', '.join(str(a + i) for i in range(1, b + 1))}"},
            {"action": "mark_end", "position": s, "narration": f"到 {s}！所以 {a} + {b} = {s}"}
        ]}
    ]}

def _mt(a, b):
    """Make-ten animation for a+b where a+b > 10."""
    s = a + b; need = 10 - a; rm = b - need
    return {"expression": f"{a} + {b} = {s}", "methods": [
        {"type": "make_ten", "title": "凑十法", "steps": [
            {"action": "show_objects", "left": a, "right": b, "shape": "random",
             "narration": f"左边 {a} 个，右边 {b} 个"},
            {"action": "think_split", "target": "right", "need": need,
             "narration": f"{a} 凑成 10 还差 {need}，把 {b} 拆成 {need} 和 {rm}"},
            {"action": "split", "target": "right", "parts": [need, rm],
             "narration": f"{b} = {need} + {rm}"},
            {"action": "move_to_left", "count": need,
             "narration": f"移 {need} 个过去凑成 10"},
            {"action": "highlight_ten", "value": 10,
             "narration": f"{a} + {need} = 10"},
            {"action": "combine", "values": [10, rm], "result": s,
             "narration": f"10 + {rm} = {s}，答对啦！"}
        ]},
        {"type": "number_line", "title": "数轴法", "steps": [
            {"action": "draw_line", "from": 0, "to": 20, "narration": "看这条数轴"},
            {"action": "mark_start", "position": a, "narration": f"从 {a} 出发"},
            {"action": "jump_split", "first_jump": need, "second_jump": rm, "via": 10,
             "narration": f"先跳 {need} 步到 10，再跳 {rm} 步"},
            {"action": "mark_end", "position": s, "narration": f"到达 {s}！"}
        ]},
        {"type": "counting", "title": "数数法", "steps": [
            {"action": "show_objects", "left": a, "right": b, "shape": "random",
             "narration": f"左边 {a} 个，右边 {b} 个"},
            {"action": "count_on", "start": a, "count": b,
             "sequence": list(range(a + 1, s + 1)),
             "narration": f"从 {a} 接着数：{', '.join(str(x) for x in range(a + 1, s + 1))}"},
            {"action": "show_result", "result": s, "narration": f"数到 {s}！棒棒的！"}
        ]}
    ]}

def _bt(t, b):
    """Break-ten for t-b where t > 10 and needs borrowing."""
    r = t - b; ones = t - 10
    return {"expression": f"{t} - {b} = {r}", "methods": [
        {"type": "break_ten", "title": "破十法", "steps": [
            {"action": "show_total", "total": t, "shape": "random",
             "narration": f"一共 {t} 个"},
            {"action": "decompose", "number": t, "tens": 10, "ones": ones,
             "narration": f"把 {t} 拆成 10 和 {ones}"},
            {"action": "subtract_from_ten", "ten": 10, "sub": b, "result": 10 - b,
             "narration": f"先从 10 里减去 {b}，得到 {10 - b}"},
            {"action": "combine", "values": [10 - b, ones], "result": r,
             "narration": f"{10 - b} + {ones} = {r}！所以 {t} - {b} = {r}"}
        ]},
        {"type": "number_line", "title": "数轴法", "steps": [
            {"action": "draw_line", "from": 0, "to": 20, "narration": "看数轴"},
            {"action": "mark_start", "position": t, "narration": f"从 {t} 出发"},
            {"action": "jump", "count": b, "direction": "left",
             "narration": f"往左跳 {b} 步：{', '.join(str(t - i) for i in range(1, b + 1))}"},
            {"action": "mark_end", "position": r, "narration": f"到 {r}！"}
        ]}
    ]}

# ===== Exercise generator (with CORRECT hints) =====

def _ex(eid, lid, a, b, op, diff=1, typ="fill_blank"):
    ans = a + b if op == "+" else a - b
    expr = f"{a}{op}{b}"; q = f"{a} {op} {b} = ?"

    if op == "+":
        if a + b > 10 and a < 10 and b < 10:
            # 进位加法 → 凑十法提示
            big, small = (a, b) if a >= b else (b, a)
            need = 10 - big; rm = small - need
            h = [f"{big} 凑 10 还差 {need}", f"把 {small} 拆成 {need} 和 {rm}"]
            s = [{"method": "make_ten", "steps": [f"{small}拆成{need}和{rm}", f"{big}+{need}=10", f"10+{rm}={ans}"]}]
        else:
            # 简单加法 → 数数法提示
            h = [f"从 {a} 开始往后数 {b} 个", f"试试在数轴上跳一跳"]
            s = [{"method": "counting", "steps": [f"从{a}开始数：{','.join(str(a+i) for i in range(1,b+1))}"]}]
    else:
        if a > 10 and b > a - 10:
            # 退位减法 → 破十法提示
            ones = a - 10
            h = [f"把 {a} 拆成 10 和 {ones}", f"先算 10 - {b} = {10 - b}"]
            s = [{"method": "break_ten", "steps": [f"{a}=10+{ones}", f"10-{b}={10-b}", f"{10-b}+{ones}={ans}"]}]
        else:
            # 10以内减法 / 不退位减法 → 拿走法/数数法提示
            h = [f"从 {a} 个里拿走 {b} 个", f"在数轴上从 {a} 往左跳 {b} 步"]
            s = [{"method": "counting", "steps": [f"从{a}拿走{b}个，还剩{ans}个"]}]

    opts = sorted(set([ans, max(0,ans-1), ans+1, ans+2]))[:4] if typ == "choice" else []
    return (eid, lid, typ, q, expr, str(ans), diff,
            JD(s), JD(h), JD(opts), diff)

# ===== Seed data =====

async def seed_data():
    db = await get_db()
    existing = await db.execute("SELECT COUNT(*) as c FROM courses")
    row = await existing.fetchone()
    if row["c"] > 0:
        await db.close()
        return

    now = datetime.now().isoformat()
    cid = "course-add-sub-20"
    await db.execute(
        'INSERT INTO courses (id,title,description,grade_range,"order",status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?)',
        (cid, "20以内加减法", "适合6-8岁儿童的20以内加减法启蒙课程", "6-8", 1, "published", now, now))

    # ======== Lesson Definitions ========

    # --- Lesson 01: 认识加法 (6 variants) ---
    L01_pairs = [(2,3),(1,2),(3,1),(1,4),(4,1),(2,2),(3,2)]
    L01_default = _counting_add(2, 3)
    L01_variants = [_counting_add(a,b) for a,b in L01_pairs[1:]]

    # --- Lesson 02: 10以内加法 (7 variants, 2 methods each) ---
    L02_pairs = [(4,3),(3,5),(6,2),(5,4),(2,7),(3,6),(8,1)]
    def _add10(a,b):
        base = _counting_add(a,b)
        nl = _nl_add(a,b,10)
        base["methods"].append(nl["methods"][0])
        return base
    L02_default = _add10(4, 3)
    L02_variants = [_add10(a,b) for a,b in L02_pairs[1:]]

    # --- Lesson 03: 10以内减法 (7 variants, 2 methods each) ---
    L03_pairs = [(7,3),(5,2),(8,3),(9,4),(6,2),(10,5),(8,5)]
    L03_default = _counting_sub(7, 3)
    L03_variants = [_counting_sub(a,b) for a,b in L03_pairs[1:]]

    # --- Lesson 04: 20以内不进位加法 (6 variants) ---
    L04_pairs = [(12,3),(11,5),(14,2),(13,4),(15,3),(10,6)]
    def _add20_noc(a,b):
        s = a + b
        return {"expression": f"{a} + {b} = {s}", "methods": [
            {"type": "step_by_step", "title": "分步法", "steps": [
                {"action": "decompose", "number": a, "parts": [10, a-10],
                 "narration": f"把 {a} 拆成 10 和 {a-10}"},
                {"action": "add_ones", "values": [a-10, b], "result": a-10+b,
                 "narration": f"个位：{a-10} + {b} = {a-10+b}"},
                {"action": "combine", "values": [10, a-10+b], "result": s,
                 "narration": f"10 + {a-10+b} = {s}！"}]},
            {"type": "number_line", "title": "数轴法", "steps": [
                {"action": "draw_line", "from": 0, "to": 20, "narration": "看数轴"},
                {"action": "mark_start", "position": a, "narration": f"从 {a} 出发"},
                {"action": "jump", "count": b, "direction": "right",
                 "narration": f"往右跳 {b} 步"},
                {"action": "mark_end", "position": s, "narration": f"到 {s}！"}]}
        ]}
    L04_default = _add20_noc(12, 3)
    L04_variants = [_add20_noc(a,b) for a,b in L04_pairs[1:]]

    # --- Lesson 05: 进位加法 (19 variants, 3 methods each) ---
    L05_pairs = [(8,5),(7,6),(9,4),(8,6),(7,5),(9,3),(6,7),(8,4),(5,8),(9,5),
                 (6,8),(7,9),(8,7),(9,6),(6,9),(8,9),(9,7),(5,9),(6,6)]
    L05_default = _mt(8, 5)
    L05_variants = [_mt(a,b) for a,b in L05_pairs[1:]]

    # --- Lesson 06: 退位减法 (19 variants, 2 methods each) ---
    L06_pairs = [(13,8),(15,7),(12,9),(14,6),(11,8),(16,9),(13,5),(15,8),
                 (12,7),(14,9),(17,8),(11,5),(13,6),(16,7),(12,8),(18,9),
                 (15,6),(14,8),(13,9)]
    L06_default = _bt(13, 8)
    L06_variants = [_bt(t,b) for t,b in L06_pairs[1:]]

    # --- Lesson 07: 混合 ---
    L07_default = _mt(9, 6)
    L07_variants = [_mt(8,7), _bt(14,8), _mt(6,9), _bt(16,7), _bt(15,6)]

    # --- Lesson 08: 三个数 ---
    L08_default = {"expression": "3 + 5 + 2 = 10", "methods": [{"type": "step_by_step", "title": "分步法", "steps": [
        {"action": "highlight_first_pair", "values": [3,5], "narration": "先算 3 + 5"},
        {"action": "compute", "expression": "3 + 5", "result": 8, "narration": "3 + 5 = 8"},
        {"action": "compute", "expression": "8 + 2", "result": 10, "narration": "8 + 2 = 10！"}]}]}

    lessons_data = [
        ("lesson-01", "认识加法", "通过可爱小动物学习加法概念", 1, "published", '["counting"]',
         L01_default, L01_variants),
        ("lesson-02", "10以内加法", "数数法和数轴法双管齐下", 2, "published", '["counting","number_line"]',
         L02_default, L02_variants),
        ("lesson-03", "10以内减法", "拿走法和数轴回跳学减法", 3, "published", '["subtraction","number_line"]',
         L03_default, L03_variants),
        ("lesson-04", "20以内不进位加法", "个位直接加", 4, "published", '["step_by_step","number_line"]',
         L04_default, L04_variants),
        ("lesson-05", "20以内进位加法（凑十法）", "重点凑十法，一题三解", 5, "published", '["make_ten","number_line","counting"]',
         L05_default, L05_variants),
        ("lesson-06", "20以内退位减法（破十法）", "破十法处理退位减法", 6, "published", '["break_ten","number_line"]',
         L06_default, L06_variants),
        ("lesson-07", "加减混合练习", "综合运用多种方法", 7, "published", '["make_ten","break_ten"]',
         L07_default, L07_variants),
        ("lesson-08", "三个数连算", "从左到右分步算", 8, "published", '["step_by_step"]',
         L08_default, []),
    ]

    for lid, title, desc, order, status, methods, default_anim, variants in lessons_data:
        await db.execute(
            'INSERT INTO lessons (id,course_id,title,description,"order",status,teaching_methods,animation_data,animation_variants,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (lid, cid, title, desc, order, status, methods, JD(default_anim), JD(variants), now, now))

    # ======== Exercises ========
    INS = 'INSERT INTO exercises (id,lesson_id,type,question,expression,correct_answer,"order",solutions,hints,options,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)'

    # Lesson 01: 12 exercises (simple add ≤ 5+5)
    for i, (a,b) in enumerate([(1,1),(2,1),(1,3),(2,2),(3,1),(2,3),(1,4),(3,2),(4,1),(3,3),(1,5),(5,1)]):
        await db.execute(INS, _ex(f"ex-01-{i+1:02d}", "lesson-01", a, b, "+", 1))

    # Lesson 02: 15 exercises (add within 10)
    for i, (a,b) in enumerate([(3,4),(5,5),(6,3),(4,5),(2,7),(8,2),(1,6),(5,4),(7,3),(6,4),(3,7),(4,6),(2,8),(1,9),(9,1)]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-02-{i+1:02d}", "lesson-02", a, b, "+", (i%3)+1, t))

    # Lesson 03: 15 exercises (sub within 10) ← FIXED hints
    for i, (a,b) in enumerate([(5,2),(8,3),(10,4),(7,5),(9,3),(6,1),(8,5),(10,7),(9,6),(7,4),(6,3),(5,3),(8,2),(10,6),(9,5)]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-03-{i+1:02d}", "lesson-03", a, b, "-", (i%3)+1, t))

    # Lesson 04: 15 exercises (add within 20, no carry)
    for i, (a,b) in enumerate([(12,3),(11,5),(14,2),(13,4),(10,6),(15,3),(11,7),(12,5),(14,5),(10,8),(16,2),(13,3),(11,4),(17,1),(12,6)]):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-04-{i+1:02d}", "lesson-04", a, b, "+", (i%3)+1, t))

    # Lesson 05: 30 exercises (carry addition) ← LARGEST pool
    p05 = [(8,5),(7,6),(9,4),(8,6),(7,5),(9,3),(6,7),(8,4),(5,8),(9,5),
           (6,8),(7,9),(8,7),(9,6),(6,9),(8,9),(7,8),(9,7),(5,9),(6,6),
           (8,8),(9,9),(7,7),(5,7),(4,9),(3,8),(4,8),(5,6),(3,9),(6,5)]
    for i, (a,b) in enumerate(p05):
        t = "choice" if i % 4 == 0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-05-{i+1:02d}", "lesson-05", a, b, "+", (i%3)+1, t))

    # Lesson 06: 25 exercises (borrow subtraction) ← BIG pool
    p06 = [(13,8),(15,7),(12,9),(14,6),(11,8),(16,9),(13,5),(15,8),(12,7),(14,9),
           (17,8),(11,5),(13,6),(16,7),(12,8),(18,9),(11,3),(15,6),(14,8),(13,9),
           (11,4),(12,6),(15,9),(16,8),(17,9)]
    for i, (a,b) in enumerate(p06):
        t = "choice" if i % 4 == 0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-06-{i+1:02d}", "lesson-06", a, b, "-", (i%3)+1, t))

    # Lesson 07: 20 mixed exercises
    p07 = [(9,6,"+"),(13,7,"-"),(8,5,"+"),(15,9,"-"),(7,8,"+"),(12,5,"-"),
           (6,9,"+"),(14,6,"-"),(9,4,"+"),(11,8,"-"),(8,7,"+"),(16,8,"-"),
           (7,6,"+"),(13,4,"-"),(5,9,"+"),(17,9,"-"),(6,8,"+"),(15,7,"-"),
           (9,5,"+"),(14,9,"-")]
    for i, (a,b,op) in enumerate(p07):
        t = "choice" if i % 5 == 0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-07-{i+1:02d}", "lesson-07", a, b, op, (i%3)+1, t))

    # Lesson 08: 16 exercises (three addends)
    h3 = JD(["先算前两个数", "把结果再加上最后一个数"])
    s3 = JD([{"method": "step_by_step", "steps": ["先算前两个数之和", "再加上第三个数"]}])
    p08 = [
        (3,5,2,1,"choice"), (4,3,2,1,"choice"), (2,6,1,1,"choice"), (5,3,4,1,"choice"),
        (1,7,3,1,"choice"), (6,2,3,1,"choice"), (3,4,5,2,"choice"), (2,5,6,2,"choice"),
        (4,4,4,1,"fill_blank"), (3,3,3,1,"fill_blank"), (5,5,5,2,"fill_blank"),
        (6,7,3,2,"fill_blank"), (7,5,2,2,"fill_blank"), (8,3,4,2,"fill_blank"),
        (6,6,5,3,"fill_blank"), (9,4,3,3,"fill_blank"),
    ]
    for i, (a,b,c,diff,typ) in enumerate(p08):
        ans = a + b + c
        opts = JD(sorted(set([ans, ans-1, ans+1, ans+2]))[:4]) if typ == "choice" else JD([])
        await db.execute(INS, (f"ex-08-{i+1:02d}", "lesson-08", typ,
                               f"{a} + {b} + {c} = ?", f"{a}+{b}+{c}",
                               str(ans), i+1, s3, h3, opts, diff))

    await db.commit()
    await db.close()
    print("✅ Seed data inserted (v3 fixed)")
