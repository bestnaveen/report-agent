"""Phase 2: SQLite chat history persistence across sessions."""
import sqlite3
import uuid
from datetime import datetime
from config import MEMORY_DB_PATH


def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(MEMORY_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with _get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                file_name TEXT,
                timestamp TEXT NOT NULL
            )
        """)
        conn.commit()


def save_message(session_id: str, role: str, content: str, file_name: str = None):
    """Persist a single message to SQLite."""
    init_db()
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (session_id, role, content, file_name, timestamp) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, file_name, datetime.now().isoformat()),
        )
        conn.commit()


def load_history(session_id: str, limit: int = 50) -> list[dict]:
    """Load recent messages for a session."""
    init_db()
    with _get_connection() as conn:
        rows = conn.execute(
            "SELECT role, content, file_name, timestamp FROM chat_history "
            "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def clear_history(session_id: str):
    """Delete all messages for a session."""
    init_db()
    with _get_connection() as conn:
        conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
        conn.commit()


def new_session_id() -> str:
    """Generate a new unique session ID."""
    return str(uuid.uuid4())
