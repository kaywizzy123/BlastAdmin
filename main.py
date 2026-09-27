"""
BlastAdmin — Pipeline TD administration tool for BlastVault studios.

Manages:
  • Studio name, departments, review types
  • Artist registry (add / edit / delete artists, set permissions)
  • Admin PIN (shared via artists.json — applies to all machines)

Completely independent of BlastVault — reads and writes artists.json directly.
"""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

from core import constants
from core import registry
from core.styles import stylesheet
from tabs.studio_tab      import StudioTab
from tabs.artists_tab     import ArtistsTab
from tabs.departments_tab import DepartmentsTab
from tabs.review_types_tab import ReviewTypesTab
from tabs.security_tab    import SecurityTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlastAdmin")
        self.setMinimumSize(860, 600)
        self.resize(1000, 660)
        self.setWindowIcon(QIcon(constants.ICON))
        self._build_ui()

    def _build_ui(self):
        # ── Header bar ────────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet(f"background: {constants.BORDER};")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(16, 0, 16, 0)
        h_layout.setSpacing(0)

        logo = QLabel()
        pix = QPixmap(str(constants.ICONS_DIR / "bv.png"))
        if not pix.isNull():
            logo.setPixmap(pix.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        title_lbl = QLabel("BlastAdmin")
        title_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: bold; color: {constants.ACCENT_HI}; "
            f"letter-spacing: 2px; background: transparent;"
        )

        subtitle_lbl = QLabel("Pipeline TD Tool")
        subtitle_lbl.setStyleSheet(
            f"font-size: 11px; color: {constants.TEXT_SEC}; background: transparent;"
        )

        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFixedWidth(1)
        sep.setStyleSheet(f"background: {constants.SPLITTER_COLOR}; margin: 12px 4px;")

        # Registry path label
        self._path_lbl = QLabel()
        self._path_lbl.setStyleSheet(
            f"font-size: 10px; color: {constants.TEXT_SEC}; background: transparent;"
        )
        self._refresh_path_label()

        h_layout.setSpacing(10)
        h_layout.addWidget(logo)
        h_layout.addWidget(title_lbl)
        h_layout.addWidget(subtitle_lbl)
        h_layout.addWidget(sep)
        h_layout.addWidget(self._path_lbl)
        h_layout.addStretch()

        # ── Tabs ──────────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._studio_tab      = StudioTab()
        self._artists_tab     = ArtistsTab()
        self._departments_tab = DepartmentsTab()
        self._review_types_tab = ReviewTypesTab()
        self._security_tab    = SecurityTab()

        self._tabs.addTab(self._studio_tab,      "  Studio  ")
        self._tabs.addTab(self._artists_tab,     "  Artists  ")
        self._tabs.addTab(self._departments_tab, "  Departments  ")
        self._tabs.addTab(self._review_types_tab, "  Review Types  ")
        self._tabs.addTab(self._security_tab,    "  Security  ")
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._studio_tab.registry_changed.connect(self._on_registry_changed)

        # ── Layout ────────────────────────────────────────────────────────
        central = QWidget()
        layout  = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header)
        layout.addWidget(self._tabs)
        self.setCentralWidget(central)

    def _refresh_path_label(self):
        path = registry.registry_path()
        exists = path.exists()
        color  = constants.TEXT_SEC if exists else constants.FAIL
        label  = str(path) + ("" if exists else "  ⚠ file not found")
        self._path_lbl.setText(f"Registry: {label}")
        self._path_lbl.setStyleSheet(
            f"font-size: 10px; color: {color}; background: transparent;"
        )

    def _on_registry_changed(self):
        """Studio tab saved a new path — refresh everything that reads the registry."""
        self._refresh_path_label()
        self._artists_tab.refresh()

    def _on_tab_changed(self, index: int):
        self._refresh_path_label()
        tab = self._tabs.widget(index)
        if tab in (self._artists_tab, self._departments_tab, self._review_types_tab):
            tab.refresh()


def main():
    from core.registry import load_config, save_config

    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(stylesheet())

    # ── Load BlastAdmin's own config ───────────────────────────────────── #
    is_first_run = not constants.CONFIG_PATH.exists()
    load_config()

    # ── Admin PIN — artists.json is authoritative when present ─────────── #
    # A PIN set, changed or removed on any TD machine is written to the
    # registry, so every machine follows it on its next launch. The local
    # config keeps the last-known hash for when the registry is unreachable.
    reg_path = registry.registry_path()
    if reg_path.exists():
        try:
            reg_data = json.loads(reg_path.read_text(encoding="utf-8"))
            if "admin_pin_hash" in reg_data:
                reg_hash = reg_data["admin_pin_hash"] or ""
                if reg_hash != constants.ADMIN_PIN_HASH:
                    constants.ADMIN_PIN_HASH = reg_hash
                    if not is_first_run:
                        save_config()
        except Exception:
            pass

    # ── First-run welcome — shown before PIN so TD can set things up ───── #
    if is_first_run:
        from dialogs.first_run_dialog import FirstRunDialog
        dlg = FirstRunDialog()
        dlg.exec_()   # Skip is allowed — TD can fill in Studio tab later

    # ── PIN authentication ─────────────────────────────────────────────── #
    if constants.ADMIN_PIN_HASH:
        from dialogs.auth_dialog import PinAuthDialog
        dlg = PinAuthDialog()
        if dlg.exec_() != dlg.Accepted:
            sys.exit(0)

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
