#!/usr/bin/env bash
# Install grabin di Linux. Dijelasin per baris biar paham, bukan asal copy-paste.
set -euo pipefail

# 1. Pindah ke root project (folder yang ada file ini), biar script bisa
#    dijalankan dari mana aja tanpa path ngaco.
cd "$(dirname "$0")/.."

# 2. Cek python3 ada atau enggak. Kalau enggak ada, stop.
command -v python3 >/dev/null || { echo "python3 nggak ketemu, install dulu bro."; exit 1; }

# 3. Cek ffmpeg (wajib buat gabung video+audio & convert mp3).
if ! command -v ffmpeg >/dev/null; then
  echo "ffmpeg belum ada. Install dulu:"
  echo "  sudo pacman -S ffmpeg   # Arch/EndeavourOS/Omarchy"
  echo "  sudo apt install ffmpeg # Debian/Ubuntu"
  exit 1
fi

# 4. Bikin virtual env biar dependency nggak ngotorin system python.
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

# 5. Masuk venv + upgrade pip + install dependency.
# shellcheck disable=SC1091
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# 6. Tes cepat: CLI harusnya bisa nampilin daftar platform.
python -m grabin --platforms

echo ""
echo "Beres. Cara pakai:"
echo "  source .venv/bin/activate"
echo "  python -m grabin \"https://www.facebook.com/...\""
