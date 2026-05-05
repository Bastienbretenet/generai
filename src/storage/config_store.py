from sqlalchemy import create_engine, text
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "config.db"
DB_PATH.parent.mkdir(exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})

def init_db():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prompt TEXT NOT NULL,
                steps TEXT NOT NULL,
                sql TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """))

def add_history(prompt: str, steps: list[str], sql: str | None) -> int:
    import json
    with engine.begin() as conn:
        result = conn.execute(text("""
            INSERT INTO history (prompt, steps, sql) VALUES (:prompt, :steps, :sql)
        """), {"prompt": prompt, "steps": json.dumps(steps, ensure_ascii=False), "sql": sql})
        return result.lastrowid


def get_history(limit: int = 50) -> list[dict]:
    import json
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, prompt, steps, sql, created_at FROM history ORDER BY created_at DESC LIMIT :limit
        """), {"limit": limit}).fetchall()
        return [{"id": r[0], "prompt": r[1], "steps": json.loads(r[2]), "sql": r[3], "created_at": r[4]} for r in rows]


def get_history_item(item_id: int) -> dict | None:
    import json
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT id, prompt, steps, sql, created_at FROM history WHERE id = :id
        """), {"id": item_id}).fetchone()
        if not row:
            return None
        return {"id": row[0], "prompt": row[1], "steps": json.loads(row[2]), "sql": row[3], "created_at": row[4]}

def get_setting(key: str, default: str = None) -> str | None:
    with engine.connect() as conn:
        row = conn.execute(text("SELECT value FROM settings WHERE key = :key"), {"key": key}).fetchone()
        return row[0] if row else default

def set_setting(key: str, value: str):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO settings (key, value) VALUES (:key, :value)
            ON CONFLICT(key) DO UPDATE SET value = :value
        """), {"key": key, "value": value})
