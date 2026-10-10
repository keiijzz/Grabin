"""CLI: `python -m grabin <URL>` — argparse only, tanpa framework berat."""

from __future__ import annotations

import argparse
import pathlib
import sys

from . import __version__, downloader, library
from .config import DEFAULT_CONFIG_PATH, load_config
from .platforms import list_platforms
from .utils import ensure_dir, format_bytes, format_duration


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="grabin",
        description="grabin — sedot video sosmed (FB/TikTok/IG/YT/...) ke folder lokal.",
    )
    p.add_argument("url", nargs="?", help="Link video yang mau didownload.")
    p.add_argument("--batch", metavar="FILE", help="File .txt berisi daftar URL (1 per baris).")
    p.add_argument("--info", action="store_true", help="Cek judul/durasi doang, tanpa download.")
    p.add_argument("--platforms", action="store_true", help="Lihat daftar platform yang didukung.")
    p.add_argument("--history", action="store_true", help="Lihat riwayat download.")
    p.add_argument("--clear-history", action="store_true", help="Hapus riwayat download.")
    p.add_argument("-o", "--output-dir", default="", help="Folder output (default: downloads/).")
    p.add_argument("-q", "--quality", choices=["best", "1080", "720", "480", "audio"], default="",
                   help="Kualitas video.")
    p.add_argument("--audio-only", action="store_true", help="Ambil audio aja (mp3).")
    p.add_argument("--cookies", dest="cookies_file", default="", help="Path cookies.txt (buat IG/FB/TikTok login-walled).")
    p.add_argument("--cookies-from-browser", default="",
                   help="Ambil cookies dari browser: chrome / firefox / edge.")
    p.add_argument("--write-info", action="store_true", help="Simpan .info.json sebelah video.")
    p.add_argument("--skip-history", action="store_true", help="Download ulang walau pernah diunduh.")
    p.add_argument("--config", default="", help=f"Path settings.yaml (default: {DEFAULT_CONFIG_PATH}).")
    p.add_argument("--version", action="store_true", help="Tampilin versi.")
    return p


def _override_from_args(args: argparse.Namespace, cfg: dict) -> dict:
    ov: dict = {}
    if args.output_dir:
        ov["output_dir"] = args.output_dir
    if args.quality:
        ov["quality"] = args.quality
    if args.audio_only:
        ov["audio_only"] = True
    if args.cookies_file:
        ov["cookies_file"] = args.cookies_file
    if args.cookies_from_browser:
        ov["cookies_from_browser"] = args.cookies_from_browser
    if args.write_info:
        ov["write_info"] = True
    if args.skip_history:
        ov["skip_history"] = True
    return ov


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.version:
        print(f"grabin v{__version__}")
        return 0

    if args.platforms:
        print("Platform yang didukung (selain ini tetap dicoba via yt-dlp generic):\n")
        for plat in list_platforms():
            lock = " [butuh cookies kalau private]" if plat.needs_cookies else ""
            print(f"  - {plat.label:<14} {', '.join(plat.domains)}{lock}")
        print("\nCatatan: yt-dlp aslinya dukung 1000+ situs, jadi link random biasanya tetap jalan.")
        return 0

    cfg = load_config(args.config or None)
    ov = _override_from_args(args, cfg)
    output_dir = str(ov.get("output_dir") or cfg["output_dir"])
    ensure_dir(output_dir)

    if args.clear_history:
        n = library.clear(output_dir)
        print(f"Riwayat dihapus ({n} baris).")
        return 0

    if args.history:
        rows = library.fetch_all(output_dir)
        if not rows:
            print("Belum ada riwayat. Download dulu 1 video bro.")
            return 0
        for vid, title, plat, path, when in rows:
            print(f"[{when}] ({plat}) {title}\n  -> {path}\n")
        return 0

    if args.batch:
        batch_file = pathlib.Path(args.batch).expanduser()
        if not batch_file.exists():
            print(f"File batch nggak ketemu: {batch_file}", file=sys.stderr)
            return 1
        urls = batch_file.read_text(encoding="utf-8").splitlines()
        print(f"Ngesedot {len([u for u in urls if u.strip() and not u.startswith('#')])} URL...")
        results = downloader.download_batch(urls, cfg, ov)
        ok = sum(1 for r in results if "error" not in r)
        fail = len(results) - ok
        for r in results:
            if "error" in r:
                print(f"  GAGAL {r.get('url')}: {r['error']}")
            else:
                print(f"  OK [{r['platform']}] {r['title']}\n     -> {r['file']}")
        print(f"\nSelesai: {ok} sukses, {fail} gagal.")
        return 0 if fail == 0 else 2

    if not args.url:
        build_parser().print_help()
        print("\nContoh cepat:\n  python -m grabin \"https://www.facebook.com/...\"")
        return 1

    if args.info:
        try:
            info = downloader.fetch_info(args.url, cfg)
        except Exception as exc:  # noqa: BLE001
            print(f"Gagal ambil info: {exc}", file=sys.stderr)
            print("Hint: kalau IG/FB/TikTok private, pakai --cookies cookies.txt", file=sys.stderr)
            return 1
        size = info.get("filesize") or info.get("filesize_approx")
        print(f"Judul    : {info.get('title')}")
        print(f"Durasi   : {format_duration(info.get('duration'))}")
        print(f"Ukuran   : {format_bytes(size)} (estimasi)")
        print(f"Uploader : {info.get('uploader') or info.get('channel')}")
        return 0

    try:
        res = downloader.download_single(args.url, cfg, ov)
    except Exception as exc:  # noqa: BLE001
        print(f"\nGagal download: {exc}", file=sys.stderr)
        print("Hint umum:", file=sys.stderr)
        print("  1. Update yt-dlp: pip install -U yt-dlp", file=sys.stderr)
        print("  2. Kalau link private/login-walled: export cookies.txt lalu --cookies cookies.txt", file=sys.stderr)
        return 1

    print(f"\nOK [{res['platform']}] {res['title']}")
    print(f"  -> {res['file']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
