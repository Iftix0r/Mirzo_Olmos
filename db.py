import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = "orders.db"

_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
_conn.row_factory = sqlite3.Row


def init_db():
    _conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_number INTEGER PRIMARY KEY,
            group_id INTEGER,
            group_title TEXT,
            sender_id INTEGER,
            sender_name TEXT,
            sender_phone TEXT,
            text TEXT,
            msg_link TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL,
            closed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS groups (
            group_id INTEGER PRIMARY KEY,
            title TEXT,
            last_seen TEXT
        );

        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kw_type TEXT NOT NULL,
            word TEXT NOT NULL,
            UNIQUE(kw_type, word)
        );

        CREATE TABLE IF NOT EXISTS blocked_users (
            user_id INTEGER PRIMARY KEY,
            blocked_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            added_at TEXT NOT NULL
        );
        """
    )
    _conn.commit()


def create_order(order_number: int, group_id: Optional[int], group_title: str,
                  sender_id, sender_name: str, sender_phone: str, text: str, msg_link: str):
    _conn.execute(
        """INSERT OR REPLACE INTO orders
           (order_number, group_id, group_title, sender_id, sender_name, sender_phone, text, msg_link, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open', ?)""",
        (order_number, group_id, group_title, sender_id, sender_name, sender_phone, text, msg_link,
         datetime.now().isoformat(timespec="seconds")),
    )
    _conn.commit()


def close_order(order_number: int) -> bool:
    cur = _conn.execute(
        "UPDATE orders SET status='closed', closed_at=? WHERE order_number=? AND status='open'",
        (datetime.now().isoformat(timespec="seconds"), order_number),
    )
    _conn.commit()
    return cur.rowcount > 0


def get_last_order_number() -> Optional[int]:
    row = _conn.execute("SELECT MAX(order_number) FROM orders").fetchone()
    return row[0] if row and row[0] is not None else None


def get_order(order_number: int) -> Optional[sqlite3.Row]:
    return _conn.execute("SELECT * FROM orders WHERE order_number=?", (order_number,)).fetchone()


def get_recent_orders(limit: int = 10):
    return _conn.execute(
        "SELECT * FROM orders ORDER BY order_number DESC LIMIT ?", (limit,)
    ).fetchall()


def get_incomplete_orders(limit: int = 30):
    return _conn.execute(
        "SELECT * FROM orders WHERE status='open' ORDER BY order_number DESC LIMIT ?", (limit,)
    ).fetchall()


def get_stats() -> dict:
    total = _conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    open_count = _conn.execute("SELECT COUNT(*) FROM orders WHERE status='open'").fetchone()[0]
    closed_count = _conn.execute("SELECT COUNT(*) FROM orders WHERE status='closed'").fetchone()[0]
    today = datetime.now().date().isoformat()
    today_count = _conn.execute(
        "SELECT COUNT(*) FROM orders WHERE created_at LIKE ?", (f"{today}%",)
    ).fetchone()[0]
    return {"total": total, "open": open_count, "closed": closed_count, "today": today_count}


def upsert_group(group_id: int, title: str):
    _conn.execute(
        """INSERT INTO groups (group_id, title, last_seen) VALUES (?, ?, ?)
           ON CONFLICT(group_id) DO UPDATE SET title=excluded.title, last_seen=excluded.last_seen""",
        (group_id, title, datetime.now().isoformat(timespec="seconds")),
    )
    _conn.commit()


def get_group_stats():
    return _conn.execute(
        """SELECT g.group_id, g.title, COUNT(o.order_number) AS order_count
           FROM groups g LEFT JOIN orders o ON o.group_id = g.group_id
           GROUP BY g.group_id ORDER BY order_count DESC"""
    ).fetchall()


def search_orders(query: str, limit: int = 10):
    like = f"%{query}%"
    return _conn.execute(
        """SELECT * FROM orders
           WHERE CAST(order_number AS TEXT) LIKE ? OR sender_name LIKE ? OR sender_phone LIKE ? OR text LIKE ?
           ORDER BY order_number DESC LIMIT ?""",
        (like, like, like, like, limit),
    ).fetchall()


def add_keyword(kw_type: str, word: str) -> bool:
    try:
        _conn.execute("INSERT INTO keywords (kw_type, word) VALUES (?, ?)", (kw_type, word))
        _conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_keywords(kw_type: str):
    rows = _conn.execute("SELECT word FROM keywords WHERE kw_type=?", (kw_type,)).fetchall()
    return [r["word"] for r in rows]


def block_user(user_id: int):
    _conn.execute(
        "INSERT OR REPLACE INTO blocked_users (user_id, blocked_at) VALUES (?, ?)",
        (user_id, datetime.now().isoformat(timespec="seconds")),
    )
    _conn.commit()


def unblock_user(user_id: int):
    _conn.execute("DELETE FROM blocked_users WHERE user_id=?", (user_id,))
    _conn.commit()


def is_blocked(user_id) -> bool:
    row = _conn.execute("SELECT 1 FROM blocked_users WHERE user_id=?", (user_id,)).fetchone()
    return row is not None


def count_blocked() -> int:
    return _conn.execute("SELECT COUNT(*) FROM blocked_users").fetchone()[0]


def add_admin(user_id: int, name: str) -> bool:
    try:
        _conn.execute(
            "INSERT INTO admins (user_id, name, added_at) VALUES (?, ?, ?)",
            (user_id, name, datetime.now().isoformat(timespec="seconds")),
        )
        _conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def remove_admin(user_id: int) -> bool:
    cur = _conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
    _conn.commit()
    return cur.rowcount > 0


def is_admin_db(user_id) -> bool:
    row = _conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone()
    return row is not None


def list_admins():
    return _conn.execute("SELECT * FROM admins ORDER BY added_at").fetchall()
