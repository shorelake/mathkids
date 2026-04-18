"""Database schema & connection. Content lives in tools/seeders/."""
import aiosqlite, os

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


async def is_empty() -> bool:
    """True if no courses exist yet."""
    db = await get_db()
    r = await db.execute("SELECT COUNT(*) as c FROM courses")
    row = await r.fetchone()
    await db.close()
    return row["c"] == 0
