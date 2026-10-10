"""Deteksi platform dari URL.

File ini yang jadi “daftar sosmed apa aja yang didukung”.
Kalau mau nambah platform baru, cukup tambah entry di SUPPORTED —
nggak perlu ubek-ubek downloader.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Platform:
    key: str          # dipakai buat nama folder output: downloads/facebook/
    label: str        # nama cantik buat ditampilin di CLI
    domains: tuple[str, ...]  # substring yang dicari di URL
    notes: str = ""
    needs_cookies: bool = False  # True kalau sering butuh login (IG/TikTok/FB private)


SUPPORTED: tuple[Platform, ...] = (
    Platform("youtube", "YouTube", ("youtube.com", "youtu.be",), "Shorts & full video OK."),
    Platform("tiktok", "TikTok", ("tiktok.com", "vt.tiktok.com", "vm.tiktok.com",), "Sering butuh cookies kalau kena captcha.", True),
    Platform("instagram", "Instagram", ("instagram.com", "instagr.am",), "Reels/post butuh login via cookies kalau akun private.", True),
    Platform("facebook", "Facebook", ("facebook.com", "fb.watch", "fb.com",), "Kasus utama lo: video kastil/medieval di FB.", True),
    Platform("twitter", "X (Twitter)", ("twitter.com", "x.com", "t.co",), ""),
    Platform("reddit", "Reddit", ("reddit.com", "redd.it",), "v.redd.it OK."),
    Platform("vimeo", "Vimeo", ("vimeo.com",), ""),
    Platform("dailymotion", "Dailymotion", ("dailymotion.com", "dai.ly",), ""),
    Platform("twitch", "Twitch", ("twitch.tv",), "VOD & clip."),
    Platform("pinterest", "Pinterest", ("pinterest.com", "pin.it",), "Video pin."),
    Platform("capcut", "CapCut", ("capcut.com",), "Template video."),
    Platform("soundcloud", "SoundCloud", ("soundcloud.com",), "Audio only paling cocok."),
)

# Fallback: selain yang di atas, yt-dlp sebenarnya dukung 1000+ situs.
# Jadi kalau nggak kedeteksi, tetap kita coba download sebagai "generic".
GENERIC_KEY = "generic"


def detect_platform(url: str) -> Platform | None:
    """Tebak platform dari URL. Return None kalau nggak dikenal (generic)."""
    lowered = url.lower()
    for plat in SUPPORTED:
        if any(dom in lowered for dom in plat.domains):
            return plat
    return None


def platform_key(url: str) -> str:
    """Return key folder output, misal 'facebook', 'tiktok', atau 'generic'."""
    plat = detect_platform(url)
    return plat.key if plat else GENERIC_KEY


def list_platforms() -> list[Platform]:
    return list(SUPPORTED)
