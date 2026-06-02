"""
BlastAdmin — registry I/O.
Reads and writes artists.json on the shared network drive.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from core import constants


# ── Resolve the active registry path ─────────────────────────────────────── #

def registry_path() -> Path:
    """Return the active Path to artists.json.

    Priority:
      1. constants.REGISTRY_PATH  (explicit path saved in config)
      2. constants.STUDIO_ROOT / artists.json  (studio root default)
    """
    if constants.REGISTRY_PATH:
        return Path(constants.REGISTRY_PATH)
    return Path(constants.STUDIO_ROOT) / "artists.json"


# ── Read ──────────────────────────────────────────────────────────────────── #

def load() -> dict:
    """Load the full registry dict.

    Returns a dict with at least ``{"artists": [], ...}``.
    If the file doesn't exist yet, returns a minimal skeleton.
    """
    path = registry_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "artists" not in data:
                data["artists"] = []
            return data
        except Exception:
            pass
    return {
        "studio_name": constants.STUDIO_NAME,
        "artists": [],
    }


def load_artists() -> list[dict]:
    return load().get("artists", [])


# ── Write ─────────────────────────────────────────────────────────────────── #

def save(data: dict) -> bool:
    """Write *data* to the registry file. Returns True on success."""
    path = registry_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except Exception as exc:
        print(f"[BlastAdmin] registry save failed: {exc}")
        return False


def save_artists(artists: list[dict], extra: Optional[dict] = None) -> bool:
    """Write *artists* back to the registry, preserving top-level metadata.

    *extra* can override top-level keys (e.g. ``{"studio_name": "..."}``).
    """
    data = load()
    data["artists"] = artists
    if extra:
        data.update(extra)
    return save(data)


# ── Config persistence ────────────────────────────────────────────────────── #

def load_config() -> None:
    """Load BlastAdmin's own config (studio root path, PIN hash, etc.)."""
    path = constants.CONFIG_PATH
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        constants.STUDIO_ROOT    = data.get("studio_root",    constants.STUDIO_ROOT)
        constants.REGISTRY_PATH  = data.get("registry_path",  "")
        constants.ADMIN_PIN_HASH = data.get("admin_pin_hash", "")
        constants.STUDIO_NAME    = data.get("studio_name",    "")
        constants.DEPARTMENTS    = data.get("departments",    constants.DEPARTMENTS)
        constants.REVIEW_TYPES   = data.get("review_types",   constants.REVIEW_TYPES)
    except Exception:
        pass


def save_config() -> None:
    """Persist BlastAdmin's own config."""
    data = {
        "studio_root":    constants.STUDIO_ROOT,
        "registry_path":  constants.REGISTRY_PATH,
        "admin_pin_hash": constants.ADMIN_PIN_HASH,
        "studio_name":    constants.STUDIO_NAME,
        "departments":    constants.DEPARTMENTS,
        "review_types":   constants.REVIEW_TYPES,
    }
    try:
        constants.CONFIG_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as exc:
        print(f"[BlastAdmin] config save failed: {exc}")
