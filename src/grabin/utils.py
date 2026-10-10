"""Helper kecil-kecil: nama file aman, format ukuran, dsb."""

from __future__ import annotations

import pathlib
import re


_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_WS_RUN = re.compile(r"\s+")


def sanitize_filename(name: str, max_len: int = 120) -> str:
    """Bikin judul video aman jadi nama file.

    Contoh: 'Kastil 🏰 Skotlandia: Eilean Donan!!' -> 'Kastil Skotlandia - Eilean Donan!!'
    """
    cleaned = _INVALID_CHARS.sub("", name).strip()
    cleaned = _WS_RUN.sub(" ", cleaned)
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len].rstrip()
    return cleaned or "untitled"


def ensure_dir(path: str | pathlib.Path) -> pathlib.Path:
    p = pathlib.Path(path).expanduser().resolve()
    p.mkdir(parents=True, exist_ok=True)
    return p


def format_bytes(num: float | None) -> str:
    if num is None:
        return "?"
    step = 1024.0
    for unit in ("B", "KB", "MB", "GB"):
        if num < step:
            return f"{num:.1f} {unit}"
        num /= step
    return f"{num:.1f} TB"


def format_duration(seconds: int | float | None) -> str:
    if seconds is None:
        return "?"
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h:d}:{m:02d}:{s:02d}"
    return f"{m:d}:{s:02d}"
