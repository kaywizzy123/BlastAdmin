"""
BlastAdmin — core constants.
Shares the same dark colour palette as BlastVault for a unified suite feel.
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent

APP_NAME    = "BlastAdmin"
APP_VERSION = "1.0.0"

ICONS_DIR = _ROOT / "icons"
ICON      = str(ICONS_DIR / "bv.png")

# ── Per-user config ───────────────────────────────────────────────────────── #
_IS_FROZEN = getattr(sys, "frozen", False)

if _IS_FROZEN:
    if sys.platform == "win32":
        _APP_DATA = Path.home() / "AppData" / "Roaming" / "BlastAdmin"
    elif sys.platform == "darwin":
        _APP_DATA = Path.home() / "Library" / "Application Support" / "BlastAdmin"
    else:
        _APP_DATA = Path.home() / ".config" / "BlastAdmin"
else:
    _APP_DATA = _ROOT

_APP_DATA.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = _APP_DATA / "bladmin_config.json"

# ── Studio defaults ───────────────────────────────────────────────────────── #
if sys.platform == "win32":
    DEFAULT_ROOT = r"C:\SHOWS"
else:
    DEFAULT_ROOT = str(Path.home() / "Shows")

STUDIO_ROOT:    str       = DEFAULT_ROOT
REGISTRY_PATH:  str       = ""          # full path to artists.json
ADMIN_PIN_HASH: str       = ""

STUDIO_NAME:  str       = ""
DEPARTMENTS:  list[str] = [
    # Pre-production
    "Story",
    "Visual Development",
    # 3D Asset
    "Modeling",
    "Rigging",
    "Texturing",
    "Look Development",
    # Production
    "Layout",
    "Layout Finaling",
    "Animation",
    "Technical Animation",
    "Character FX",
    "FX / Simulation",
    "Lighting",
    "Compositing",
    "Matte Painting",
]
REVIEW_TYPES: list[str] = [
    "Director Dailies", "Head of Animation Rounds",
    "Supervisor Review", "CG Supervisor Review", "Final Review",
]

PERMISSION_OPTIONS = ["admin", "reviewer", "basic"]
ROLE_OPTIONS       = ["Admin", "Animation Supervisor", "Artist", "TD"]

# ── Palette (matches BlastVault) ──────────────────────────────────────────── #
BORDER        = "#0a0a0a"
BG            = "#1A1A1A"
ACCENT_HI     = "#1085d3"
ACCENT        = "#343434"
TEXT_PRI      = "#ededed"
TEXT_SEC      = "#a1a1a1"
FAIL          = "#ad0303"
SUCCESS       = "#03ad14"
SPLITTER_COLOR = "#292929"
