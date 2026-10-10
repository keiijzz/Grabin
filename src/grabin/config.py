"""Load config YAML + default bawaan.

Prioritas nilai (yang paling menang paling atas):
  1. flag CLI   (misal --quality 720)
  2. config/settings.yaml
  3. DEFAULTS di bawah ini
"""

from __future__ import annotations

import pathlib
from typing import Any

try:
    import yaml
except ImportError:  # biar error-nya jelas, bukan traceback aneh
    yaml = None  # type: ignore

DEFAULTS: dict[str, Any] = {
    "output_dir": "downloads",
    "quality": "best",       # best | 1080 | 720 | 480 | audio
    "audio_only": False,
    "audio_format": "mp3",
    "write_info": False,     # simpan .info.json sebelah video (buat arsip)
    "write_subs": False,     # download subtitle kalau ada
    "cookies_file": "",      # path ke cookies.txt (cara ambil: lihat README)
    "cookies_from_browser": "",  # chrome | firefox | edge, kalau mau auto-ambil
    "skip_history": False,   # True = download ulang walaupun pernah diunduh
}

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def _project_relative(path_str: str) -> str:
    """'downloads' di settings.yaml selalu relatif ke root project, bukan cwd."""
    p = pathlib.Path(path_str).expanduser()
    if p.is_absolute():
        return str(p)
    return str((PROJECT_ROOT / p).resolve())


def load_config(path: str | pathlib.Path | None = None) -> dict[str, Any]:
    """Baca YAML, gabung sama DEFAULTS, return dict siap pakai."""
    cfg: dict[str, Any] = dict(DEFAULTS)
    cfg_path = pathlib.Path(path).expanduser() if path else DEFAULT_CONFIG_PATH
    if cfg_path.exists():
        if yaml is None:
            raise RuntimeError("PyYAML belum diinstall. Jalanin: pip install -r requirements.txt")
        with cfg_path.open("r", encoding="utf-8") as f:
            user_cfg = yaml.safe_load(f) or {}
        for key, val in user_cfg.items():
            if key in DEFAULTS:
                cfg[key] = val
    # normalisasi path output biar konsisten dari mana pun CLI dijalankan
    cfg["output_dir"] = _project_relative(str(cfg["output_dir"]))
    if cfg.get("cookies_file"):
        cfg["cookies_file"] = str(pathlib.Path(str(cfg["cookies_file"])).expanduser())
    return cfg
