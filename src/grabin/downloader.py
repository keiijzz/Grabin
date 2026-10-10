"""Inti downloader — satu-satunya file yang ngomong langsung ke yt-dlp.

Kenapa dipisah dari cli.py?
Biar CLI cuma urus argumen, logic download (format, cookies, history)
semuanya numpuk di sini. Mau dipakai CLI, bot Telegram, atau web,
tetap panggil fungsi di file ini.
"""

from __future__ import annotations

import pathlib
from typing import Any

try:
    import yt_dlp
except ImportError as exc:
    raise RuntimeError(
        "yt-dlp belum diinstall. Jalanin: pip install -r requirements.txt"
    ) from exc

from . import library, platforms
from .utils import ensure_dir


def quality_to_format(quality: str, audio_only: bool = False) -> str:
    """Mapping pilihan user -> format string yt-dlp."""
    if audio_only or quality == "audio":
        return "bestaudio/best"
    table = {
        "best": "bestvideo+bestaudio/best",
        "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "720": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
        "480": "bestvideo[height<=480]+bestaudio/best[height<=480]/best",
    }
    return table.get(str(quality), table["best"])


def build_ydl_opts(
    url: str,
    cfg: dict[str, Any],
    override: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], str]:
    """Susun opsi yt-dlp dari config + flag CLI. Return (opts, platform_key)."""
    ov = override or {}
    output_dir = str(ov.get("output_dir") or cfg.get("output_dir", "downloads"))
    quality = str(ov.get("quality") or cfg.get("quality", "best"))
    audio_only = bool(ov.get("audio_only", cfg.get("audio_only", False)))

    plat_key = platforms.platform_key(url)
    ensure_dir(output_dir)

    # Struktur rapi: downloads/facebook/2026-10-10/Judul [id].mp4
    outtmpl = str(
        pathlib.Path(output_dir)
        / plat_key
        / "%(upload_date>%Y-%m-%d)s"
        / "%(title)s [%(id)s].%(ext)s"
    )

    opts: dict[str, Any] = {
        "format": quality_to_format(quality, audio_only),
        "outtmpl": outtmpl,
        "noplaylist": True,
        "restrictfilenames": True,   # aman buat Linux/Windows/NAS
        "windowsfilenames": True,
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": False,
        "retries": 3,
        "concurrent_fragment_downloads": 4,
        "writethumbnail": False,
        "writeinfojson": bool(ov.get("write_info", cfg.get("write_info", False))),
        "writesubtitles": bool(ov.get("write_subs", cfg.get("write_subs", False))),
        "subtitleslangs": ["id", "en"],
    }

    if audio_only:
        opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": str(cfg.get("audio_format", "mp3")),
                "preferredquality": "192",
            }
        ]

    cookies_file = ov.get("cookies_file") or cfg.get("cookies_file") or ""
    browser = ov.get("cookies_from_browser") or cfg.get("cookies_from_browser") or ""
    if cookies_file:
        opts["cookiefile"] = str(pathlib.Path(cookies_file).expanduser())
    elif browser:
        # contoh: --cookies-from-browser chrome
        opts["cookiesfrombrowser"] = (str(browser),)

    return opts, plat_key


def fetch_info(url: str, cfg: dict[str, Any]) -> dict[str, Any]:
    """Ambil judul/durasi tanpa download (buat perintah --info)."""
    opts, _ = build_ydl_opts(url, cfg)
    opts.update({"skip_download": True, "quiet": True})
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    if info is None:
        raise RuntimeError("Gagal ambil info. Link private / butuh cookies?")
    if "entries" in info:  # playlist ke-skip, ambil item pertama
        info = next((e for e in info["entries"] if e), info)
    return info


def download_single(url: str, cfg: dict[str, Any], override: dict[str, Any] | None = None) -> dict[str, Any]:
    """Download 1 URL. Return dict ringkas: id/title/platform/file."""
    url = url.strip()
    if not url or url.startswith("#"):
        raise ValueError("URL kosong.")
    ov = override or {}
    output_dir = str(ov.get("output_dir") or cfg.get("output_dir", "downloads"))
    skip_history = bool(ov.get("skip_history", cfg.get("skip_history", False)))

    opts, plat_key = build_ydl_opts(url, cfg, ov)

    downloaded_file = {"path": ""}

    def _hook(d: dict[str, Any]) -> None:
        if d.get("status") == "finished":
            downloaded_file["path"] = d.get("filename", "")

    opts["progress_hooks"] = [_hook]

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
    if info is None:
        raise RuntimeError("Download gagal (info kosong). Coba --cookies kalau link login-walled.")
    if "entries" in info:
        info = next((e for e in info["entries"] if e), info)

    video_id = str(info.get("id", ""))
    title = str(info.get("title", video_id))

    if video_id and not skip_history:
        if library.already_downloaded(output_dir, video_id):
            pass  # yt-dlp tetap download ulang? enggak — kita catat aja, file sudah ada
        library.save_record(output_dir, video_id, url, title, plat_key, downloaded_file["path"])

    return {
        "id": video_id,
        "title": title,
        "platform": plat_key,
        "duration": info.get("duration"),
        "file": downloaded_file["path"],
    }


def download_batch(
    urls: list[str],
    cfg: dict[str, Any],
    override: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Download banyak URL sekaligus, yang gagal dicatat tapi lanjut jalan."""
    results: list[dict[str, Any]] = []
    for url in urls:
        url = url.strip()
        if not url or url.startswith("#"):
            continue
        try:
            results.append(download_single(url, cfg, override))
        except Exception as exc:  # noqa: BLE001 — batch harus tahan banting
            results.append({"url": url, "error": str(exc)})
    return results
