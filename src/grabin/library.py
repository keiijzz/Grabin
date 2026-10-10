"""Riwayat download (SQLite) — biar nggak download video yang sama dua kali.

DB-nya satu file: <output_dir>/.grabin_history.db
Isinya simpel: video_id + url + judul + platform + path file + waktu.
"""

from __future__ import annotations

import pathlib
import sqlite3
import time

_SCHEMA = """
CREATE TABLE IF NOT EXISTS history (
    video_id   TEXT PRIMARY KEY,
    url        TEXT NOT NULL,
    title      TEXT DEFAULT '',
    platform   TEXT DEFAULT '',
    file_path  TEXT DEFAULT '',
    created_at INTEGER NOT NULL
);
"""


def db_path(output_dir: str | pathlib.Path) -> pathlib.Path:
    return pathlib.Path(output_dir).expanduser().resolve() / ".grabin_history.db"


def _connect(output_dir: str | pathlib.Path) -> sqlite3.Connection:
    db = db_path(output_dir)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def already_downloaded(output_dir: str | pathlib.Path, video_id: str) -> bool:
    if not video_id:
        return False
    conn = _connect(output_dir)
    try:
        row = conn.execute("SELECT 1 FROM history WHERE video_id = ?", (video_id,)).fetchone()
        return row is not None
    finally:
        conn.close()


def save_record(
    output_dir: str | pathlib.Path,
    video_id: str,
    url: str,
    title: str = "",
    platform: str = "",
    file_path: str = "",
) -> None:
    if not video_id:
        return
    conn = _connect(output_dir)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO history (video_id, url, title, platform, file_path, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (video_id, url, title, platform, file_path, int(time.time())),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_all(output_dir: str | pathlib.Path, limit: int = 50) -> list[tuple]:
    conn = _connect(output_dir)
    try:
        return conn.execute(
            "SELECT video_id, title, platform, file_path, datetime(created_at,'unixepoch','localtime')"
            " FROM history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    finally:
        conn.close()


def clear(output_dir: str | pathlib.Path) -> int:
    conn = _connect(output_dir)
    try:
        cur = conn.execute("DELETE FROM history")
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()
