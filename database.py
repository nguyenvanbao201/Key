import sqlite3

conn = sqlite3.connect("keys.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE,
    device_id TEXT DEFAULT '',
    key_type TEXT DEFAULT 'FREE',
    expire_time TEXT,
    telegraph_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()