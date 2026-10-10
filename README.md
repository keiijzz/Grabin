# grabin — Universal Social Media Downloader

Satu CLI buat sedot video dari **Facebook, TikTok, Instagram, YouTube, X, Reddit, Vimeo**, dan 1000+ situs lain (via yt-dlp).

Dibikin karena kebiasaan scrolling Facebook nemu video kastil/medieval bagus, terus pengen nyimpen offline — bukan cuma di-save di app yang gampang hilang.

## Fitur

- 1 perintah buat semua sosmed: `python -m grabin "<url>"`
- Mode batch: ` --batch config/urls.txt` (1 URL per baris)
- Cek dulu tanpa download: `--info`
- Kualitas pilih: `best / 1080 / 720 / 480 / audio`
- Output rapi otomatis: `downloads/<platform>/<tanggal>/Judul [id].mp4`
- Riwayat SQLite: nggak download ulang yang sama (`--history`)
- Support cookies buat link private/login-walled (`--cookies cookies.txt`)
- Struktur modular, siap jadi porto GitHub: `platforms.py`, `downloader.py`, `library.py`, `cli.py` kepisah jelas

## Quickstart (3 menit)

```bash
# 1. Install (bikin venv + install dependency + self-test)
bash scripts/install.sh

# 2. Masuk venv tiap buka terminal baru
source .venv/bin/activate

# 3. Lihat platform yang didukung
python -m grabin --platforms

# 4. Gas download 1 video
python -m grabin "https://www.facebook.com/reel/xxxx"

# 5. Hasilnya ada di, misal:
#    downloads/facebook/2026-10-10/Judul Video [abc123].mp4
```

### Perintah yang sering dipakai

```bash
# Cek judul/durasi dulu (hemat kuota)
python -m grabin --info "https://www.tiktok.com/@user/video/123"

# Ambil audio aja (buat Nightwish / backsound kastil)
python -m grabin --audio-only "https://www.youtube.com/watch?v=xxxx"

# Kualitas 720p biar hemat (default: best)
python -m grabin -q 720 "https://www.instagram.com/reel/xxxx/"

# Batch 20 link sekaligus
python -m grabin --batch config/urls.txt

# Lihat riwayat
python -m grabin --history
```

### Kalau link private / kena login (IG, FB, TikTok)

1. Di Chrome install ekstensi **"Get cookies.txt LOCALLY"**
2. Buka sosmednya (pastiin udah login), klik ekstensi → Export → simpan sebagai `cookies.txt` di root project
3. Pakai begini:

```bash
python -m grabin --cookies cookies.txt "https://www.instagram.com/reel/private_xxxx/"
```

Atau tanpa file (Chrome/Firefox di laptop yang sama):

```bash
python -m grabin --cookies-from-browser chrome "https://..."
```

## Struktur project

```
Git-Porto/
├── src/grabin/
│   ├── __init__.py      # versi + identitas
│   ├── __main__.py      # entry `python -m grabin`
│   ├── cli.py           # urus argumen doang
│   ├── downloader.py    # satu-satunya yang ngomong ke yt-dlp
│   ├── platforms.py     # daftar sosmed — tambah baru cukup edit ini
│   ├── config.py        # load settings.yaml + defaults
│   ├── library.py       # riwayat SQLite
│   └── utils.py         # helper nama file, format ukuran
├── config/
│   ├── settings.yaml    # SATU file yang perlu lo edit (output, kualitas, cookies)
│   └── urls.txt         # contoh batch
├── tests/               # unittest stdlib, tanpa pytest
├── scripts/install.sh   # installer + penjelasan per baris
├── downloads/           # hasil (di-gitignore kecuali .gitkeep)
├── requirements.txt
├── pyproject.toml
├── Dockerfile           # opsional: jalanin via container
└── Makefile
```

## Config (`config/settings.yaml`)

Semua default ada di `src/grabin/config.py:DEFAULTS`. Yang di YAML menimpa default, yang di flag CLI menimpa YAML. Jadi urutan menang: **CLI > YAML > default**.

## Roadmap (ide lanjutan biar porto makin hidup)

- [ ] Bot Telegram: forward link dari HP → auto-download ke NAS/homelab
- [ ] Web UI mini (FastAPI) buat paste link dari tablet
- [ ] `--playlist` mode arsip channel kastil favorit
- [ ] GitHub Actions: auto `yt-dlp -U` check tiap minggu

## Disclaimer

Download hanya buat **koleksi pribadi / fair use**. Jangan re-upload karya orang tanpa izin. Kalau video private, pakai akun + cookies milik sendiri.

---

Built with Python + yt-dlp + ffmpeg. Owner: Enggar Irawan ([@keiijzz](https://github.com/keiijzz)).
