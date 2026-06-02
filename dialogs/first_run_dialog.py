"""
BlastAdmin — First-run welcome dialog.
Shown once on first launch to let the TD set the studio name and registry path.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon

from core import constants
from core import registry


class FirstRunDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Welcome to BlastAdmin")
        self.setFixedWidth(480)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(0)

        # ── Logo ─────────────────────────────────────────────────────────
        logo_lbl = QLabel()
        pix = QPixmap(str(constants.ICONS_DIR / "bv.png"))
        if not pix.isNull():
            logo_lbl.setPixmap(
                pix.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        logo_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_lbl)
        layout.addSpacing(12)

        # ── Title ─────────────────────────────────────────────────────────
        title = QLabel("Welcome to BlastAdmin")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {constants.TEXT_PRI};"
        )
        layout.addWidget(title)
        layout.addSpacing(6)

        # ── Subtitle ──────────────────────────────────────────────────────
        sub = QLabel(
            "Set up your studio registry before you get started.\n"
            "You can change these at any time in the Studio tab."
        )
        sub.setAlignment(Qt.AlignCenter)
        sub.setWordWrap(True)
        sub.setStyleSheet(f"font-size: 12px; color: {constants.TEXT_SEC};")
        layout.addWidget(sub)
        layout.addSpacing(24)

        # ── Form ──────────────────────────────────────────────────────────
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignRight)

        def _lbl(text):
            l = QLabel(text)
            l.setStyleSheet(f"color: {constants.TEXT_SEC}; font-size: 11px;")
            return l

        # Studio name
        self._studio_name = QLineEdit()
        self._studio_name.setFixedHeight(34)
        self._studio_name.setPlaceholderText("e.g. indie Animation Studio")
        form.addRow(_lbl("Studio Name *"), self._studio_name)

        # Registry path
        path_row = QHBoxLayout()
        path_row.setSpacing(8)
        self._registry_path = QLineEdit()
        self._registry_path.setFixedHeight(34)
        self._registry_path.setPlaceholderText(
            rf"Default: {constants.STUDIO_ROOT}\artists.json"
        )
        browse_btn = QPushButton()
        browse_btn.setIcon(QIcon(str(constants.ICONS_DIR / "folder.png")))
        browse_btn.setIconSize(QSize(14, 14))
        browse_btn.setFixedSize(34, 34)
        browse_btn.setToolTip("Browse for save location")
        browse_btn.clicked.connect(self._browse)
        path_row.addWidget(self._registry_path)
        path_row.addWidget(browse_btn)
        form.addRow(_lbl("Registry File"), path_row)

        layout.addLayout(form)
        layout.addSpacing(8)

        # ── Note ──────────────────────────────────────────────────────────
        note = QLabel(
            "Leave Registry File blank to use the default location.\n"
            "BlastVault will find it automatically from the Studio Root."
        )
        note.setWordWrap(True)
        note.setStyleSheet(f"font-size: 10px; color: {constants.TEXT_SEC};")
        layout.addWidget(note)

        # ── Error label ───────────────────────────────────────────────────
        self._error_lbl = QLabel()
        self._error_lbl.setStyleSheet(f"color: {constants.FAIL}; font-size: 11px;")
        self._error_lbl.setVisible(False)
        layout.addSpacing(8)
        layout.addWidget(self._error_lbl)

        layout.addSpacing(20)

        # ── Buttons ───────────────────────────────────────────────────────
        btn_row = QHBoxLayout()

        skip_btn = QPushButton("Skip for now")
        skip_btn.setStyleSheet(
            f"background: transparent; color: {constants.TEXT_SEC}; border: none;"
            f"padding: 8px 12px;"
        )
        skip_btn.clicked.connect(self.reject)

        get_started_btn = QPushButton("Get Started")
        get_started_btn.setFixedHeight(36)
        get_started_btn.setFixedWidth(140)
        get_started_btn.setProperty("primary", True)
        get_started_btn.setStyle(get_started_btn.style())
        get_started_btn.clicked.connect(self._on_confirm)

        btn_row.addWidget(skip_btn)
        btn_row.addStretch()
        btn_row.addWidget(get_started_btn)
        layout.addLayout(btn_row)

    def _browse(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Choose Registry File Location",
            self._registry_path.text() or constants.STUDIO_ROOT,
            "JSON files (*.json)",
            options=QFileDialog.Option.DontUseNativeDialog,
        )
        if path:
            self._registry_path.setText(path)

    def _on_confirm(self):
        name = self._studio_name.text().strip()
        if not name:
            self._error_lbl.setText("Studio name is required.")
            self._error_lbl.setVisible(True)
            return

        constants.STUDIO_NAME   = name
        constants.REGISTRY_PATH = self._registry_path.text().strip()

        from pathlib import Path
        path = registry.registry_path()

        if path.exists():
            # File already exists (e.g. pointing at a shared network registry).
            # Preserve all existing artists — only update studio_name.
            data = registry.load()
            data["studio_name"] = name
            registry.save(data)
        else:
            # New studio setup — create a fresh skeleton at the chosen path.
            data = {"studio_name": name, "artists": []}
            registry.save(data)

        registry.save_config()
        self.accept()
