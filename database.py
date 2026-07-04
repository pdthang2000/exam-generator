import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            chunk_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER,
            questions_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()


def insert_document(filename, file_type):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO documents (filename, file_type) VALUES (?, ?)",
        (filename, file_type),
    )
    doc_id = cur.lastrowid
    conn.commit()
    conn.close()
    return doc_id


def get_all_documents():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, filename, file_type, upload_time, chunk_count FROM documents ORDER BY upload_time DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_chunk_count(doc_id, count):
    conn = get_db()
    conn.execute("UPDATE documents SET chunk_count = ? WHERE id = ?", (count, doc_id))
    conn.commit()
    conn.close()


def delete_document(doc_id):
    conn = get_db()
    conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()


def insert_chat_message(role, content):
    conn = get_db()
    conn.execute(
        "INSERT INTO chat_history (role, content) VALUES (?, ?)",
        (role, content),
    )
    conn.commit()
    conn.close()


def get_chat_history(limit=20):
    conn = get_db()
    rows = conn.execute(
        "SELECT role, content FROM chat_history ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def clear_chat_history():
    conn = get_db()
    conn.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()
