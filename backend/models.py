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


def _mt(a, b):
    """Make-ten animation variant for a+b."""
    s = a + b; need = 10 - a; rm = b - need
    return {"expression": f"{a} + {b} = {s}", "methods": [
        {"type":"make_ten","title":"凑十法","steps":[
            {"action":"show_objects","left":a,"right":b,"shape":"random","narration":f"左边 {a} 个，右边 {b} 个"},
            {"action":"think_split","target":"right","need":need,"narration":f"{a} 凑成 10 还差 {need}，把 {b} 拆成 {need} 和 {rm}"},
            {"action":"split","target":"right","parts":[need,rm],"narration":f"{b} = {need} + {rm}"},
            {"action":"move_to_left","count":need,"narration":f"移 {need} 个过去凑成 10"},
            {"action":"highlight_ten","value":10,"narration":f"{a} + {need} = 10"},
            {"action":"combine","values":[10,rm],"result":s,"narration":f"10 + {rm} = {s}，答对啦！"}]},
        {"type":"number_line","title":"数轴法","steps":[
            {"action":"draw_line","from":0,"to":20,"narration":"看这条数轴"},
            {"action":"mark_start","position":a,"narration":f"从 {a} 出发"},
            {"action":"jump_split","first_jump":need,"second_jump":rm,"via":10,"narration":f"先跳 {need} 步到 10，再跳 {rm} 步"},
            {"action":"mark_end","position":s,"narration":f"到达 {s}！"}]},
        {"type":"counting","title":"数数法","steps":[
            {"action":"show_objects","left":a,"right":b,"shape":"random","narration":f"左边 {a} 个，右边 {b} 个"},
            {"action":"count_on","start":a,"count":b,"sequence":list(range(a+1,s+1)),
             "narration":f"从 {a} 接着数：{', '.join(str(x) for x in range(a+1,s+1))}"},
            {"action":"show_result","result":s,"narration":f"数到 {s}！棒棒的！"}]}]}

def _bt(t, b):
    """Break-ten variant for t-b."""
    r = t - b; ones = t - 10
    return {"expression": f"{t} - {b} = {r}", "methods": [
        {"type":"break_ten","title":"破十法","steps":[
            {"action":"show_objects","total":t,"shape":"random","narration":f"一共 {t} 个"},
            {"action":"decompose","number":t,"parts":[10,ones],"narration":f"{t} 拆成 10 和 {ones}"},
            {"action":"subtract_from_ten","minuend":10,"subtrahend":b,"result":10-b,"narration":f"10 - {b} = {10-b}"},
            {"action":"combine","values":[10-b,ones],"result":r,"narration":f"{10-b} + {ones} = {r}！"}]},
        {"type":"number_line","title":"数轴法","steps":[
            {"action":"draw_line","from":0,"to":20,"narration":"看数轴"},
            {"action":"mark_start","position":t,"narration":f"从 {t} 出发"},
            {"action":"jump","count":b,"direction":"left","narration":f"往左跳 {b} 步"},
            {"action":"mark_end","position":r,"narration":f"到达 {r}！"}]}]}

def _ex(eid, lid, a, b, op, diff=1, typ="fill_blank"):
    ans = a+b if op=="+" else a-b
    expr = f"{a}{op}{b}"; q = f"{a} {op} {b} = ?"
    if op == "+":
        need = 10-a if a<10 else 10-b; rm = b-need if a<10 else a-need
        h = [f"{min(a,b)}凑10还差{10-min(a,b)}", f"试试凑十法"]
        s = [{"method":"make_ten","steps":[f"凑十：{min(a,b)}+{10-min(a,b)}=10","剩余加上去"]}]
    else:
        h = [f"把{a}拆成10和{a-10}", f"先从10里减"]
        s = [{"method":"break_ten","steps":[f"{a}=10+{a-10}",f"10-{b}={10-b}"]}]
    opts = sorted(set([ans, ans-1, ans+1, ans+2]))[:4] if typ == "choice" else []
    return (eid, lid, typ, q, expr, str(ans), diff,
            json.dumps(s, ensure_ascii=False), json.dumps(h, ensure_ascii=False),
            json.dumps(opts, ensure_ascii=False), diff)


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
        (cid,"20以内加减法","适合6-8岁儿童的20以内加减法启蒙课程","6-8",1,"published",now,now))

    v05 = [_mt(a,b) for a,b in [(8,5),(7,6),(9,4),(8,6),(7,5),(9,3),(6,7),(8,4),(5,8),(9,5),(6,8),(7,9),(8,7),(9,6),(6,9),(8,9),(9,7),(5,9),(6,6)]]
    v06 = [_bt(t,b) for t,b in [(13,8),(15,7),(12,9),(14,6),(11,8),(16,9),(13,5),(15,8),(12,7),(14,9),(17,8),(11,5),(16,7),(12,8),(18,9),(15,6),(14,8),(13,9)]]

    JD = lambda x: json.dumps(x, ensure_ascii=False)
    lessons = [
        ("lesson-01","认识加法","通过可爱小动物学习加法概念",1,"published",'["counting"]',
         JD({"expression":"2 + 3 = 5","methods":[{"type":"counting","title":"数数法","steps":[
             {"action":"show_objects","left":2,"right":3,"shape":"random","narration":"左边 2 个，右边 3 个"},
             {"action":"count_all","sequence":[1,2,3,4,5],"narration":"一起数：1, 2, 3, 4, 5"},
             {"action":"show_result","result":5,"narration":"一共 5 个！2 + 3 = 5"}]}]}),
         JD([{"expression":"1 + 4 = 5","methods":[{"type":"counting","title":"数数法","steps":[
             {"action":"show_objects","left":1,"right":4,"shape":"random","narration":"左边 1 个，右边 4 个"},
             {"action":"count_on","start":1,"count":4,"sequence":[2,3,4,5],"narration":"从 1 往后数：2, 3, 4, 5"},
             {"action":"show_result","result":5,"narration":"1 + 4 = 5！"}]}]},
             {"expression":"3 + 2 = 5","methods":[{"type":"counting","title":"数数法","steps":[
             {"action":"show_objects","left":3,"right":2,"shape":"random","narration":"左边 3 个，右边 2 个"},
             {"action":"count_on","start":3,"count":2,"sequence":[4,5],"narration":"从 3 往后数：4, 5"},
             {"action":"show_result","result":5,"narration":"3 + 2 = 5！"}]}]}])),
        ("lesson-02","10以内加法","数数法和数轴法双管齐下",2,"published",'["counting","number_line"]',
         JD({"expression":"4 + 3 = 7","methods":[
             {"type":"counting","title":"数数法","steps":[
                 {"action":"show_objects","left":4,"right":3,"shape":"random","narration":"左边 4 个，右边 3 个"},
                 {"action":"count_on","start":4,"count":3,"sequence":[5,6,7],"narration":"从 4 接着数：5, 6, 7"},
                 {"action":"show_result","result":7,"narration":"4 + 3 = 7！"}]},
             {"type":"number_line","title":"数轴法","steps":[
                 {"action":"draw_line","from":0,"to":10,"narration":"看数轴"},
                 {"action":"mark_start","position":4,"narration":"从 4 出发"},
                 {"action":"jump","count":3,"direction":"right","narration":"往右跳 3 步：5, 6, 7"},
                 {"action":"mark_end","position":7,"narration":"到 7！"}]}]}),'[]'),
        ("lesson-03","10以内减法","拿走法和数轴回跳",3,"published",'["counting","number_line"]',
         JD({"expression":"7 - 3 = 4","methods":[
             {"type":"counting","title":"拿走法","steps":[
                 {"action":"show_objects","left":7,"right":0,"shape":"random","narration":"一共 7 个"},
                 {"action":"remove","count":3,"narration":"拿走 3 个..."},
                 {"action":"show_result","result":4,"narration":"剩 4 个！7 - 3 = 4"}]},
             {"type":"number_line","title":"数轴法","steps":[
                 {"action":"draw_line","from":0,"to":10,"narration":"看数轴"},
                 {"action":"mark_start","position":7,"narration":"从 7 出发"},
                 {"action":"jump","count":3,"direction":"left","narration":"往左跳 3 步"},
                 {"action":"mark_end","position":4,"narration":"到 4！"}]}]}),'[]'),
        ("lesson-04","20以内不进位加法","个位直接加",4,"published",'["step_by_step","number_line"]',
         JD({"expression":"12 + 3 = 15","methods":[
             {"type":"step_by_step","title":"分步法","steps":[
                 {"action":"decompose","number":12,"parts":[10,2],"narration":"12 拆成 10 和 2"},
                 {"action":"add_ones","values":[2,3],"result":5,"narration":"个位：2 + 3 = 5"},
                 {"action":"combine","values":[10,5],"result":15,"narration":"10 + 5 = 15！"}]},
             {"type":"number_line","title":"数轴法","steps":[
                 {"action":"draw_line","from":0,"to":20,"narration":"数轴"},
                 {"action":"mark_start","position":12,"narration":"从 12 出发"},
                 {"action":"jump","count":3,"direction":"right","narration":"跳 3 步"},
                 {"action":"mark_end","position":15,"narration":"到 15！"}]}]}),'[]'),
        ("lesson-05","20以内进位加法（凑十法）","重点凑十法，一题三解",5,"published",
         '["make_ten","number_line","counting"]', JD(v05[0]), JD(v05[1:])),
        ("lesson-06","20以内退位减法（破十法）","破十法处理退位减法",6,"published",
         '["break_ten","number_line"]', JD(v06[0]), JD(v06[1:])),
        ("lesson-07","加减混合练习","综合运用多种方法",7,"published",
         '["make_ten","break_ten"]', JD(_mt(9,6)),
         JD([_mt(8,7),_bt(14,8),_mt(6,9),_bt(16,7)])),
        ("lesson-08","三个数连算","从左到右分步算",8,"draft",'["step_by_step"]',
         JD({"expression":"3 + 5 + 2 = 10","methods":[{"type":"step_by_step","title":"分步法","steps":[
             {"action":"highlight_first_pair","values":[3,5],"narration":"先算 3 + 5"},
             {"action":"compute","expression":"3 + 5","result":8,"narration":"3 + 5 = 8"},
             {"action":"compute","expression":"8 + 2","result":10,"narration":"8 + 2 = 10！"}]}]}),'[]'),
    ]
    for l in lessons:
        await db.execute('INSERT INTO lessons (id,course_id,title,description,"order",status,teaching_methods,animation_data,animation_variants,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
            (l[0],cid,l[1],l[2],l[3],l[4],l[5],l[6],l[7],now,now))

    # -- Exercises --
    INS = 'INSERT INTO exercises (id,lesson_id,type,question,expression,correct_answer,"order",solutions,hints,options,difficulty) VALUES (?,?,?,?,?,?,?,?,?,?,?)'
    for i,(a,b,ans) in enumerate([(1,1,2),(2,1,3),(1,3,4),(2,2,4),(3,1,4),(2,3,5),(1,4,5),(3,2,5),(4,1,5),(3,3,6)]):
        await db.execute(INS, _ex(f"ex-01-{i+1:02d}","lesson-01",a,b,"+",1))
    for i,(a,b,ans) in enumerate([(3,4,7),(5,5,10),(6,3,9),(4,5,9),(2,7,9),(8,2,10),(1,6,7),(5,4,9),(7,3,10),(6,4,10)]):
        await db.execute(INS, _ex(f"ex-02-{i+1:02d}","lesson-02",a,b,"+",(i%3)+1))
    for i,(a,b,ans) in enumerate([(5,2,3),(8,3,5),(10,4,6),(7,5,2),(9,3,6),(6,1,5),(8,5,3),(10,7,3),(9,6,3),(7,4,3)]):
        await db.execute(INS, _ex(f"ex-03-{i+1:02d}","lesson-03",a,b,"-",(i%3)+1))
    for i,(a,b) in enumerate([(12,3),(11,5),(14,2),(13,4),(10,6),(15,3),(11,7),(12,5),(14,5),(10,8)]):
        await db.execute(INS, _ex(f"ex-04-{i+1:02d}","lesson-04",a,b,"+",(i%3)+1))
    # Lesson 05: 25 exercises
    p05 = [(8,5),(7,6),(9,4),(8,6),(7,5),(9,3),(6,7),(8,4),(5,8),(9,5),(6,8),(7,9),(8,7),(9,6),(6,9),(8,9),(7,8),(9,7),(5,9),(6,6),(8,8),(9,9),(7,7),(5,7),(4,9)]
    for i,(a,b) in enumerate(p05):
        t = "choice" if i%5==0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-05-{i+1:02d}","lesson-05",a,b,"+",(i%3)+1,t))
    # Lesson 06: 20 exercises
    p06 = [(13,8),(15,7),(12,9),(14,6),(11,8),(16,9),(13,5),(15,8),(12,7),(14,9),(17,8),(11,5),(13,6),(16,7),(12,8),(18,9),(11,3),(15,6),(14,8),(13,9)]
    for i,(a,b) in enumerate(p06):
        t = "choice" if i%5==0 else "fill_blank"
        await db.execute(INS, _ex(f"ex-06-{i+1:02d}","lesson-06",a,b,"-",(i%3)+1,t))
    # Lesson 07: 15 mixed
    p07 = [(9,6,"+"),(13,7,"-"),(8,5,"+"),(15,9,"-"),(7,8,"+"),(12,5,"-"),(6,9,"+"),(14,6,"-"),(9,4,"+"),(11,8,"-"),(8,7,"+"),(16,8,"-"),(7,6,"+"),(13,4,"-"),(5,9,"+")]
    for i,(a,b,op) in enumerate(p07):
        await db.execute(INS, _ex(f"ex-07-{i+1:02d}","lesson-07",a,b,op,(i%3)+1))

    await db.commit()
    await db.close()
    print("✅ Seed data inserted (expanded)")
