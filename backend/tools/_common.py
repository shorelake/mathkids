"""Shared helpers used by every course seeder.

Animation generators produce the JSON data that gets stored in `lessons.animation_data`.
Each animation has a `type` (routed to a frontend component) and a list of `steps`
with `action` + narration that become "comic-book panels" in the UI.
"""
import json
from datetime import datetime

JD = lambda x: json.dumps(x, ensure_ascii=False)

# ==========================================================
# Generic SQL helpers
# ==========================================================

def now():
    return datetime.now().isoformat()


async def upsert_course(db, cid: str, title: str, desc: str, grade: str,
                        order: int, status: str = "published"):
    n = now()
    await db.execute('INSERT OR IGNORE INTO courses '
                     '(id,title,description,grade_range,"order",status,created_at,updated_at) '
                     'VALUES (?,?,?,?,?,?,?,?)',
                     (cid, title, desc, grade, order, status, n, n))
    # update core fields in case they changed (but keep created_at)
    await db.execute('UPDATE courses SET title=?, description=?, grade_range=?, '
                     '"order"=?, status=?, updated_at=? WHERE id=?',
                     (title, desc, grade, order, status, n, cid))


async def upsert_lesson(db, lid: str, cid: str, title: str, desc: str,
                        order: int, methods: list, default_anim: dict,
                        variants: list = None, status: str = "published"):
    n = now()
    variants = variants or []
    await db.execute('INSERT OR IGNORE INTO lessons '
                     '(id,course_id,title,description,"order",status,teaching_methods,'
                     'animation_data,animation_variants,created_at,updated_at) '
                     'VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                     (lid, cid, title, desc, order, status, JD(methods),
                      JD(default_anim), JD(variants), n, n))
    # Always refresh content (makes it easy to iterate on tutorials)
    await db.execute('UPDATE lessons SET title=?, description=?, "order"=?, '
                     'status=?, teaching_methods=?, animation_data=?, '
                     'animation_variants=?, updated_at=? WHERE id=?',
                     (title, desc, order, status, JD(methods),
                      JD(default_anim), JD(variants), n, lid))


async def insert_exercise(db, eid, lid, typ, question, expression, answer,
                          order, solutions, hints, options, difficulty):
    """UPSERT: insert or replace so reseeding always refreshes content."""
    await db.execute(
        'INSERT OR REPLACE INTO exercises '
        '(id,lesson_id,type,question,expression,correct_answer,"order",'
        'solutions,hints,options,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (eid, lid, typ, question, expression, str(answer), order,
         JD(solutions), JD(hints), JD(options), difficulty))


# ==========================================================
# Exercise builder (shared by seeders and generator)
# ==========================================================

def _options_for(ans: int, n: int = 4) -> list:
    """Build multiple-choice options including the correct answer."""
    return sorted(set([ans, max(0, ans - 1), ans + 1, ans + 2]))[:n]


def make_ex_addsub(eid, lid, a, b, op, diff=1, typ="fill_blank"):
    """Exercise for add/sub within 20. (Legacy _ex behavior, kept for course-01.)"""
    ans = a + b if op == "+" else a - b
    expr = f"{a}{op}{b}"; q = f"{a} {op} {b} = ?"

    if op == "+":
        if a + b > 10 and a < 10 and b < 10:
            big, small = (a, b) if a >= b else (b, a)
            need = 10 - big; rm = small - need
            h = [f"{big} 凑 10 还差 {need}", f"把 {small} 拆成 {need} 和 {rm}"]
            s = [{"method": "make_ten",
                  "steps": [f"{small}拆成{need}和{rm}", f"{big}+{need}=10", f"10+{rm}={ans}"]}]
        else:
            h = [f"从 {a} 开始往后数 {b} 个", "试试在数轴上跳一跳"]
            s = [{"method": "counting",
                  "steps": [f"从{a}开始数：{','.join(str(a+i) for i in range(1,b+1))}"]}]
    else:
        if a > 10 and b > a - 10:
            ones = a - 10
            h = [f"把 {a} 拆成 10 和 {ones}", f"先算 10 - {b} = {10 - b}"]
            s = [{"method": "break_ten",
                  "steps": [f"{a}=10+{ones}", f"10-{b}={10-b}", f"{10-b}+{ones}={ans}"]}]
        else:
            h = [f"从 {a} 个里拿走 {b} 个", f"在数轴上从 {a} 往左跳 {b} 步"]
            s = [{"method": "counting", "steps": [f"从{a}拿走{b}个，还剩{ans}个"]}]

    opts = _options_for(ans) if typ == "choice" else []
    return (eid, lid, typ, q, expr, str(ans), diff, s, h, opts, diff)


def make_ex_100(eid, lid, a, b, op, diff=1, typ="fill_blank"):
    """Exercise for 100以内加减."""
    ans = a + b if op == "+" else a - b
    assert 0 <= ans <= 100, f"{eid}: {a}{op}{b}={ans} 超出 [0,100]"
    expr = f"{a}{op}{b}"; q = f"{a} {op} {b} = ?"

    if op == "+":
        # 整十相加
        if a % 10 == 0 and b % 10 == 0:
            h = [f"{a//10} 个十 + {b//10} 个十 = {ans//10} 个十", f"所以 {a}+{b}={ans}"]
            s = [{"method": "place_value", "steps": [f"{a}={a//10}个十", f"{b}={b//10}个十",
                                                      f"合起来 {ans//10} 个十 = {ans}"]}]
        # 整十加一位
        elif a % 10 == 0 and b < 10:
            h = [f"{a} 是 {a//10} 个十", f"再加上 {b} 个一"]
            s = [{"method": "place_value", "steps": [f"{a}是{a//10}个十", f"加上{b}个一", f"= {ans}"]}]
        # 两位数加一位数（进位）
        elif b < 10 and (a % 10) + b >= 10:
            tens = (a // 10) * 10; ones = a % 10
            need = 10 - ones; rm = b - need
            h = [f"把 {a} 看成 {tens} + {ones}", f"{ones} 凑 10 还差 {need}"]
            s = [{"method": "column_add",
                  "steps": [f"个位：{ones}+{b}={ones+b}（进 1）",
                            f"十位：{a//10}+1={a//10+1}",
                            f"合起来 {ans}"]}]
        # 两位数加一位数（不进位）
        elif b < 10:
            h = [f"个位相加：{a%10}+{b}={a%10+b}", f"十位不变：{a//10}"]
            s = [{"method": "column_add",
                  "steps": [f"个位：{a%10}+{b}={a%10+b}", f"十位：{a//10}", f"= {ans}"]}]
        # 两位数加两位数
        else:
            a_o, a_t = a % 10, a // 10; b_o, b_t = b % 10, b // 10
            carry = 1 if a_o + b_o >= 10 else 0
            ones_sum = (a_o + b_o) % 10; tens_sum = a_t + b_t + carry
            carry_msg = "（进 1）" if carry else ""
            h = [f"先加个位：{a_o}+{b_o}={a_o+b_o}{'，进1' if carry else ''}",
                 f"再加十位：{a_t}+{b_t}{'+1' if carry else ''}={tens_sum}"]
            s = [{"method": "column_add",
                  "steps": [f"个位：{a_o}+{b_o}={a_o+b_o}{carry_msg}",
                            f"十位：{a_t}+{b_t}{'+1' if carry else ''}={tens_sum}",
                            f"= {ans}"]}]
    else:
        # 两位数减一位数（退位）
        if b < 10 and (a % 10) < b:
            h = [f"个位 {a%10} 不够减 {b}，向十位借 1",
                 f"借 1 当 10，{10+a%10}-{b}={10+a%10-b}"]
            s = [{"method": "column_sub",
                  "steps": [f"个位：{a%10}不够减{b}，借1",
                            f"个位变成 {10+a%10}-{b}={10+a%10-b}",
                            f"十位：{a//10}-1={a//10-1}",
                            f"= {ans}"]}]
        # 两位数减一位数（不退位）
        elif b < 10:
            h = [f"个位相减：{a%10}-{b}={a%10-b}", f"十位不变：{a//10}"]
            s = [{"method": "column_sub",
                  "steps": [f"个位：{a%10}-{b}={a%10-b}", f"十位：{a//10}", f"= {ans}"]}]
        # 两位数减两位数
        else:
            a_o, a_t = a % 10, a // 10; b_o, b_t = b % 10, b // 10
            borrow = 1 if a_o < b_o else 0
            ones_res = (10 + a_o - b_o) if borrow else (a_o - b_o)
            tens_res = a_t - b_t - borrow
            borrow_msg = "（借 1）" if borrow else ""
            h = [f"个位：{a_o}-{b_o}{'（不够借1）' if borrow else ''}={ones_res}",
                 f"十位：{a_t}{'-1' if borrow else ''}-{b_t}={tens_res}"]
            s = [{"method": "column_sub",
                  "steps": [f"个位：{a_o}-{b_o}={ones_res}{borrow_msg}",
                            f"十位：{a_t}{'-1' if borrow else ''}-{b_t}={tens_res}",
                            f"= {ans}"]}]

    opts = _options_for(ans) if typ == "choice" else []
    return (eid, lid, typ, q, expr, str(ans), diff, s, h, opts, diff)


def make_ex_mult(eid, lid, a, b, diff=1, typ="fill_blank"):
    """Multiplication: a × b."""
    assert 1 <= a <= 9 and 1 <= b <= 9, f"{eid}: {a}×{b} 超出九九表"
    ans = a * b; expr = f"{a}×{b}"; q = f"{a} × {b} = ?"
    h = [f"{a} 个 {b} 相加：{' + '.join([str(b)]*a)}",
         f"也可以说 {b} 个 {a} 相加"]
    s = [{"method": "multiply_array",
          "steps": [f"排成 {a} 行 {b} 列的方阵",
                    f"一共 {a}×{b}={ans} 个"]}]
    opts = sorted(set([ans, max(0, ans-1), ans+1, ans+b])) if typ == "choice" else []
    return (eid, lid, typ, q, expr, str(ans), diff,
            s, h, opts[:4], diff)


def make_ex_div(eid, lid, a, b, diff=1, typ="fill_blank"):
    """Division: a ÷ b (a must be divisible by b)."""
    assert b != 0 and a % b == 0, f"{eid}: {a}÷{b} 不整除"
    ans = a // b; expr = f"{a}÷{b}"; q = f"{a} ÷ {b} = ?"
    h = [f"把 {a} 平均分成 {b} 份", f"想：{b} × ? = {a}"]
    s = [{"method": "share_equally",
          "steps": [f"{a} 个东西分成 {b} 组",
                    f"每组 {ans} 个，因为 {b}×{ans}={a}"]}]
    opts = sorted(set([ans, max(0, ans-1), ans+1, ans+2])) if typ == "choice" else []
    return (eid, lid, typ, q, expr, str(ans), diff,
            s, h, opts[:4], diff)


# ==========================================================
# Animation builders — 20以内 (for course-01 back-compat)
# ==========================================================

def anim_counting_add(a, b):
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


def anim_counting_sub(a, b):
    r = a - b
    return {"expression": f"{a} - {b} = {r}", "methods": [
        {"type": "subtraction", "title": "拿走法", "steps": [
            {"action": "show_total", "total": a, "shape": "random",
             "narration": f"一共有 {a} 个"},
            {"action": "remove", "count": b, "narration": f"拿走 {b} 个..."},
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


def anim_nl_add(a, b, line_max=10):
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


def anim_make_ten(a, b):
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


def anim_break_ten(t, b):
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
             "narration": f"往左跳 {b} 步"},
            {"action": "mark_end", "position": r, "narration": f"到 {r}！"}
        ]}
    ]}


def anim_step_20_noc(a, b):
    """20以内不进位加法，分步法。"""
    s = a + b
    return {"expression": f"{a} + {b} = {s}", "methods": [
        {"type": "step_by_step", "title": "分步法", "steps": [
            {"action": "decompose", "number": a, "parts": [10, a-10],
             "narration": f"把 {a} 拆成 10 和 {a-10}"},
            {"action": "add_ones", "values": [a-10, b], "result": a-10+b,
             "narration": f"个位：{a-10} + {b} = {a-10+b}"},
            {"action": "combine", "values": [10, a-10+b], "result": s,
             "narration": f"10 + {a-10+b} = {s}！"}
        ]},
        {"type": "number_line", "title": "数轴法", "steps": [
            {"action": "draw_line", "from": 0, "to": 20, "narration": "看数轴"},
            {"action": "mark_start", "position": a, "narration": f"从 {a} 出发"},
            {"action": "jump", "count": b, "direction": "right",
             "narration": f"往右跳 {b} 步"},
            {"action": "mark_end", "position": s, "narration": f"到 {s}！"}
        ]}
    ]}


# ==========================================================
# Animation builders — 100 以内加减 (NEW)
# ==========================================================

def anim_tens_addsub(a, b, op):
    """整十数 ± 整十数."""
    r = a + b if op == "+" else a - b
    ta, tb, tr = a // 10, b // 10, r // 10
    return {"expression": f"{a} {op} {b} = {r}", "methods": [
        {"type": "place_value", "title": "数位盒", "steps": [
            {"action": "show_tens", "count": ta, "label": f"{a}",
             "narration": f"{a} 就是 {ta} 根小棒（每根 10）"},
            {"action": "show_tens", "count": tb, "label": f"{b}",
             "narration": f"{b} 就是 {tb} 根小棒"},
            {"action": "combine_tens", "a": ta, "b": tb, "op": op, "result": tr,
             "narration": f"{ta} {op} {tb} = {tr}，也就是 {tr} 个十 = {r}"}
        ]},
        {"type": "number_line", "title": "数轴法", "steps": [
            {"action": "draw_line", "from": 0, "to": 100, "narration": "大数轴出场！"},
            {"action": "mark_start", "position": a, "narration": f"从 {a} 出发"},
            {"action": "jump", "count": b // 10, "direction": "right" if op == "+" else "left",
             "step_size": 10,
             "narration": f"每次跳 10，跳 {b // 10} 次"},
            {"action": "mark_end", "position": r, "narration": f"到 {r}！"}
        ]}
    ]}


def anim_col_add_noc(a, b):
    """两位数 + 一位数 / 两位数，不进位."""
    r = a + b
    a_t, a_o = a // 10, a % 10
    b_t, b_o = (b // 10, b % 10) if b >= 10 else (0, b)
    return {"expression": f"{a} + {b} = {r}", "methods": [
        {"type": "column_add", "title": "竖式加法", "carry": False, "steps": [
            {"action": "setup", "top": a, "bottom": b,
             "narration": f"把 {a} 和 {b} 对齐写竖式，个位对个位"},
            {"action": "add_ones", "a": a_o, "b": b_o, "result": a_o + b_o, "carry": 0,
             "narration": f"先算个位：{a_o} + {b_o} = {a_o + b_o}"},
            {"action": "add_tens", "a": a_t, "b": b_t, "carry": 0, "result": a_t + b_t,
             "narration": f"再算十位：{a_t} + {b_t} = {a_t + b_t}"},
            {"action": "show_result", "result": r,
             "narration": f"合起来是 {r}！"}
        ]},
        {"type": "place_value", "title": "数位盒", "steps": [
            {"action": "show_num", "number": a, "tens": a_t, "ones": a_o,
             "narration": f"{a}：{a_t} 根十棒 + {a_o} 个一"},
            {"action": "show_num", "number": b, "tens": b_t, "ones": b_o,
             "narration": f"{b}：{b_t} 根十棒 + {b_o} 个一"},
            {"action": "merge", "tens": a_t + b_t, "ones": a_o + b_o, "result": r,
             "narration": f"个位合 {a_o + b_o}，十位合 {a_t + b_t}，一共 {r}"}
        ]}
    ]}


def anim_col_add_carry(a, b):
    """两位数 + 一位数 / 两位数，进位."""
    r = a + b
    a_t, a_o = a // 10, a % 10
    b_t, b_o = (b // 10, b % 10) if b >= 10 else (0, b)
    ones_sum = a_o + b_o
    ones_res = ones_sum % 10
    carry = 1
    tens_res = a_t + b_t + carry
    return {"expression": f"{a} + {b} = {r}", "methods": [
        {"type": "column_add", "title": "竖式加法（进位）", "carry": True, "steps": [
            {"action": "setup", "top": a, "bottom": b,
             "narration": f"{a} 和 {b} 对齐写，个位对齐"},
            {"action": "add_ones", "a": a_o, "b": b_o, "result": ones_sum, "carry": carry,
             "narration": f"个位：{a_o} + {b_o} = {ones_sum}，满 10 进 1！"},
            {"action": "write_ones", "digit": ones_res,
             "narration": f"个位写 {ones_res}，向十位进 1"},
            {"action": "add_tens", "a": a_t, "b": b_t, "carry": carry, "result": tens_res,
             "narration": f"十位：{a_t} + {b_t} + 1（进位） = {tens_res}"},
            {"action": "show_result", "result": r,
             "narration": f"答案是 {r}！"}
        ]},
        {"type": "place_value", "title": "数位盒（换十）", "steps": [
            {"action": "show_num", "number": a, "tens": a_t, "ones": a_o,
             "narration": f"{a}：{a_t} 十 {a_o} 一"},
            {"action": "show_num", "number": b, "tens": b_t, "ones": b_o,
             "narration": f"{b}：{b_t} 十 {b_o} 一"},
            {"action": "exchange", "from_ones": ones_sum, "to_tens": 1, "remain_ones": ones_res,
             "narration": f"{ones_sum} 个一！攒够 10 个换 1 根十棒！"},
            {"action": "merge", "tens": tens_res, "ones": ones_res, "result": r,
             "narration": f"一共 {tens_res} 十 {ones_res} 一 = {r}"}
        ]}
    ]}


def anim_col_sub_noc(a, b):
    """两位数 - 一位数 / 两位数，不退位."""
    r = a - b
    a_t, a_o = a // 10, a % 10
    b_t, b_o = (b // 10, b % 10) if b >= 10 else (0, b)
    return {"expression": f"{a} - {b} = {r}", "methods": [
        {"type": "column_sub", "title": "竖式减法", "borrow": False, "steps": [
            {"action": "setup", "top": a, "bottom": b,
             "narration": f"{a} - {b}，对齐写竖式"},
            {"action": "sub_ones", "a": a_o, "b": b_o, "result": a_o - b_o, "borrow": 0,
             "narration": f"个位：{a_o} - {b_o} = {a_o - b_o}"},
            {"action": "sub_tens", "a": a_t, "b": b_t, "borrow": 0, "result": a_t - b_t,
             "narration": f"十位：{a_t} - {b_t} = {a_t - b_t}"},
            {"action": "show_result", "result": r,
             "narration": f"答案：{r}"}
        ]}
    ]}


def anim_col_sub_borrow(a, b):
    """两位数 - 一位数 / 两位数，退位."""
    r = a - b
    a_t, a_o = a // 10, a % 10
    b_t, b_o = (b // 10, b % 10) if b >= 10 else (0, b)
    ones_res = 10 + a_o - b_o
    tens_after_borrow = a_t - 1
    tens_res = tens_after_borrow - b_t
    return {"expression": f"{a} - {b} = {r}", "methods": [
        {"type": "column_sub", "title": "竖式减法（退位）", "borrow": True, "steps": [
            {"action": "setup", "top": a, "bottom": b,
             "narration": f"{a} - {b}，对齐写竖式"},
            {"action": "check_ones", "a": a_o, "b": b_o,
             "narration": f"个位 {a_o} 不够减 {b_o}，要向十位借 1"},
            {"action": "borrow", "from_tens": a_t, "to_ones_add": 10,
             "new_tens": tens_after_borrow, "new_ones": a_o + 10,
             "narration": f"十位借走 1（变成 {tens_after_borrow}），个位变 {a_o + 10}"},
            {"action": "sub_ones", "a": a_o + 10, "b": b_o, "result": ones_res, "borrow": 1,
             "narration": f"个位：{a_o + 10} - {b_o} = {ones_res}"},
            {"action": "sub_tens", "a": tens_after_borrow, "b": b_t, "borrow": 1, "result": tens_res,
             "narration": f"十位：{tens_after_borrow} - {b_t} = {tens_res}"},
            {"action": "show_result", "result": r,
             "narration": f"答案：{r}！"}
        ]}
    ]}


# ==========================================================
# Animation builders — 乘法 (NEW)
# ==========================================================

def anim_multiply_array(a, b):
    """a × b as rectangular array."""
    r = a * b
    return {"expression": f"{a} × {b} = {r}", "methods": [
        {"type": "multiply_array", "title": "方阵图", "steps": [
            {"action": "show_groups", "groups": a, "per_group": b, "shape": "random",
             "narration": f"摆出 {a} 行，每行 {b} 个"},
            {"action": "count_row", "row": 0, "count": b,
             "narration": f"第一行有 {b} 个"},
            {"action": "count_all", "total": r,
             "narration": f"一共 {a} 行 × {b} 个 = {r} 个！"},
            {"action": "show_result", "expression": f"{a} × {b}", "result": r,
             "narration": f"{a} 乘 {b} 等于 {r}！"}
        ]},
        {"type": "repeated_add", "title": "相同加法", "steps": [
            {"action": "show_groups", "groups": a, "per_group": b, "shape": "random",
             "narration": f"{a} 个 {b} 相加"},
            {"action": "show_expression", "expression": " + ".join([str(b)] * a), "result": r,
             "narration": f"{' + '.join([str(b)]*a)} = {r}"},
            {"action": "conclude",
             "narration": f"加 {a} 次太累啦，所以写成 {a} × {b} = {r}"}
        ]}
    ]}


def anim_multiply_skip_count(a, b):
    """Skip counting on a number line for a × b."""
    r = a * b
    jumps = [b * (i + 1) for i in range(a)]
    line_max = max(20, r + 5)
    return {"expression": f"{a} × {b} = {r}", "methods": [
        {"type": "number_line", "title": "跳数法", "steps": [
            {"action": "draw_line", "from": 0, "to": line_max,
             "narration": f"数轴上每次跳 {b} 步"},
            {"action": "mark_start", "position": 0, "narration": "从 0 出发"},
            {"action": "skip_jump", "step_size": b, "times": a, "positions": jumps,
             "narration": f"跳 {a} 次，每次 {b} 步：{', '.join(str(x) for x in jumps)}"},
            {"action": "mark_end", "position": r,
             "narration": f"到 {r}！{a}×{b}={r}"}
        ]}
    ]}


# ==========================================================
# Animation builders — 除法 (NEW)
# ==========================================================

def anim_share_equally(a, b):
    """Division as equal sharing: a ÷ b."""
    q = a // b
    return {"expression": f"{a} ÷ {b} = {q}", "methods": [
        {"type": "share_equally", "title": "平均分", "steps": [
            {"action": "show_items", "total": a, "shape": "random",
             "narration": f"一共有 {a} 个，要平均分给 {b} 个小伙伴"},
            {"action": "make_groups", "groups": b,
             "narration": f"先准备好 {b} 个小篮子"},
            {"action": "deal_one_by_one", "per_group": q, "groups": b,
             "narration": f"一个一个发，每人最后拿到 {q} 个"},
            {"action": "show_result", "per_group": q,
             "narration": f"每人 {q} 个！{a} ÷ {b} = {q}"}
        ]},
        {"type": "repeated_sub", "title": "连减法", "steps": [
            {"action": "show_total", "total": a,
             "narration": f"一共 {a} 个"},
            {"action": "subtract_repeatedly", "step": b, "times": q,
             "narration": f"每次拿走 {b} 个，拿了 {q} 次"},
            {"action": "show_result", "times": q,
             "narration": f"所以 {a} ÷ {b} = {q}"}
        ]}
    ]}


# ==========================================================
# Animation builders — 几何 (NEW)
# ==========================================================

def anim_shape_show(shape, sides, corners, example_objects):
    """Tutorial for a single shape."""
    names = {"circle": "圆形", "square": "正方形", "triangle": "三角形",
             "rectangle": "长方形", "pentagon": "五边形", "hexagon": "六边形"}
    name = names.get(shape, shape)
    return {"expression": f"认识 {name}", "methods": [
        {"type": "shape_show", "title": name, "shape": shape, "steps": [
            {"action": "show_shape", "shape": shape,
             "narration": f"看，这就是 {name}"},
            {"action": "count_sides", "sides": sides,
             "narration": (f"{name} 有 {sides} 条边" if sides > 0
                           else "圆形没有边，是弯弯的一圈")},
            {"action": "count_corners", "corners": corners,
             "narration": (f"{name} 有 {corners} 个角" if corners > 0
                           else "圆形也没有角哦")},
            {"action": "show_examples", "examples": example_objects,
             "narration": f"生活中这些都是 {name}：{', '.join(example_objects)}"}
        ]}
    ]}


# ==========================================================
# Animation builders — 分数 (NEW)
# ==========================================================

def anim_fraction(num, den, theme="pie"):
    """Introduce a fraction num/den."""
    return {"expression": f"{num}/{den}", "methods": [
        {"type": "fraction_pie", "title": "分数饼", "steps": [
            {"action": "show_whole", "shape": theme,
             "narration": "先看一个完整的饼"},
            {"action": "divide", "parts": den,
             "narration": f"把它平均切成 {den} 份"},
            {"action": "highlight", "num": num, "den": den,
             "narration": (f"拿走其中 {num} 份" if num > 0 else "一份也不拿")},
            {"action": "show_fraction", "num": num, "den": den,
             "narration": f"这就是 {num}/{den}，读作 {den} 分之 {num}"}
        ]}
    ]}


# ==========================================================
# Animation builders — 时间 (NEW)
# ==========================================================

def anim_clock(h, m, title_suffix=""):
    """Show a clock face at h:m."""
    time_str = f"{h}:{m:02d}"
    desc = f"{h}点" if m == 0 else (f"{h}点半" if m == 30 else f"{h}点{m}分")
    return {"expression": time_str + (f" ({title_suffix})" if title_suffix else ""),
            "methods": [
        {"type": "clock", "title": "时钟", "h": h, "m": m, "steps": [
            {"action": "show_face",
             "narration": "看这个圆圆的钟面，有 12 个数字"},
            {"action": "point_hour_hand", "hour": h,
             "narration": f"短的是时针，指着 {h}"},
            {"action": "point_minute_hand", "minute": m,
             "narration": (f"长的是分针，指着 12（整点）" if m == 0
                           else (f"长的是分针，指着 6（半点）" if m == 30
                                 else f"长的是分针，指着 {m//5}，代表 {m} 分"))},
            {"action": "read_time", "h": h, "m": m,
             "narration": f"所以现在是 {desc}"}
        ]}
    ]}
