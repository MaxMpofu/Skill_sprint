"""
SkillSprint database layer.

Uses SQLite for the hackathon MVP (swap DB_PATH for a Postgres connection
string + psycopg2/SQLAlchemy engine when you scale up - the schema below
maps directly).
"""

import sqlite3
import hashlib
import os
from contextlib import contextmanager
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "skillsprint.db")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Create tables if they don't exist, and seed one demo brief."""
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'lecturer')),
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS briefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                twist TEXT NOT NULL,
                source TEXT,
                week_start TEXT NOT NULL,
                deadline TEXT NOT NULL,
                is_active INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brief_id INTEGER NOT NULL REFERENCES briefs(id),
                student_id INTEGER NOT NULL REFERENCES users(id),
                repo_url TEXT NOT NULL,
                writeup TEXT NOT NULL,
                submitted_at TEXT NOT NULL,
                last_commit_at TEXT,
                UNIQUE(brief_id, student_id)
            );

            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL UNIQUE REFERENCES submissions(id),
                lecturer_id INTEGER NOT NULL REFERENCES users(id),
                creativity REAL NOT NULL,
                functionality REAL NOT NULL,
                code_quality REAL NOT NULL,
                scored_at TEXT NOT NULL
            );
            """
        )

        # Seed one active weekly brief if none exists yet.
        row = conn.execute("SELECT COUNT(*) AS c FROM briefs").fetchone()
        if row["c"] == 0:
            now = datetime.utcnow()
            conn.execute(
                """
                INSERT INTO briefs (title, description, twist, source, week_start, deadline, is_active)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    "Build a simple HTTP web server",
                    "Stand up a minimal HTTP server that handles at least GET and POST.",
                    "Your creative twist could add rate-limiting, a live analytics dashboard, or a chat relay.",
                    "GitHub Trending: lightweight server frameworks",
                    now.strftime("%Y-%m-%d"),
                    (now + timedelta(days=7)).strftime("%Y-%m-%d"),
                ),
            )


# ---------- password hashing (demo-grade; swap for bcrypt/argon2 in prod) ----------

def _hash_password(password: str, salt: str = "skillsprint") -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


# ---------- users ----------

def create_user(username: str, password: str, role: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, role, created_at) VALUES (?, ?, ?, ?)",
            (username, _hash_password(password), role, datetime.utcnow().isoformat()),
        )


def get_user_by_username(username: str):
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def verify_login(username: str, password: str):
    user = get_user_by_username(username)
    if user and user["password_hash"] == _hash_password(password):
        return user
    return None


def username_exists(username: str) -> bool:
    return get_user_by_username(username) is not None


# ---------- briefs ----------

def get_active_brief():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM briefs WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
        ).fetchone()


def publish_new_brief(title: str, description: str, twist: str, source: str, days_open: int = 7):
    now = datetime.utcnow()
    with get_conn() as conn:
        conn.execute("UPDATE briefs SET is_active = 0")
        conn.execute(
            """
            INSERT INTO briefs (title, description, twist, source, week_start, deadline, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
            """,
            (
                title, description, twist, source,
                now.strftime("%Y-%m-%d"),
                (now + timedelta(days=days_open)).strftime("%Y-%m-%d"),
            ),
        )


def all_briefs():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM briefs ORDER BY id DESC").fetchall()


# ---------- submissions ----------

def create_submission(brief_id: int, student_id: int, repo_url: str, writeup: str, last_commit_at=None):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO submissions (brief_id, student_id, repo_url, writeup, submitted_at, last_commit_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(brief_id, student_id) DO UPDATE SET
                repo_url = excluded.repo_url,
                writeup = excluded.writeup,
                submitted_at = excluded.submitted_at,
                last_commit_at = excluded.last_commit_at
            """,
            (brief_id, student_id, repo_url, writeup, datetime.utcnow().isoformat(), last_commit_at),
        )


def get_submission_for(brief_id: int, student_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM submissions WHERE brief_id = ? AND student_id = ?",
            (brief_id, student_id),
        ).fetchone()


def submissions_for_brief(brief_id: int):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT sub.*, u.username AS student_name,
                   sc.creativity, sc.functionality, sc.code_quality
            FROM submissions sub
            JOIN users u ON u.id = sub.student_id
            LEFT JOIN scores sc ON sc.submission_id = sub.id
            WHERE sub.brief_id = ?
            ORDER BY sub.submitted_at ASC
            """,
            (brief_id,),
        ).fetchall()


def pending_submissions_for_brief(brief_id: int):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT sub.*, u.username AS student_name
            FROM submissions sub
            JOIN users u ON u.id = sub.student_id
            LEFT JOIN scores sc ON sc.submission_id = sub.id
            WHERE sub.brief_id = ? AND sc.id IS NULL
            ORDER BY sub.submitted_at ASC
            """,
            (brief_id,),
        ).fetchall()


# ---------- scores / leaderboard ----------

def submit_score(submission_id: int, lecturer_id: int, creativity: float, functionality: float, code_quality: float):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO scores (submission_id, lecturer_id, creativity, functionality, code_quality, scored_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(submission_id) DO UPDATE SET
                creativity = excluded.creativity,
                functionality = excluded.functionality,
                code_quality = excluded.code_quality,
                scored_at = excluded.scored_at
            """,
            (submission_id, lecturer_id, creativity, functionality, code_quality, datetime.utcnow().isoformat()),
        )


def leaderboard_for_brief(brief_id: int):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT u.username AS student_name, sub.repo_url, sub.writeup,
                   sc.creativity, sc.functionality, sc.code_quality,
                   ROUND((sc.creativity + sc.functionality + sc.code_quality) / 3.0, 1) AS total
            FROM scores sc
            JOIN submissions sub ON sub.id = sc.submission_id
            JOIN users u ON u.id = sub.student_id
            WHERE sub.brief_id = ?
            ORDER BY total DESC
            """,
            (brief_id,),
        ).fetchall()

